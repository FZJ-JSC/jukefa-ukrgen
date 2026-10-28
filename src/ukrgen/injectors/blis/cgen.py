"""
C and assembly for blisgen's gemm kernels: each kernel's assembly, a wrapper
with BLIS's microkernel signature around it - BLIS's edge-case macros taking
partial tiles and storage the kernel doesn't take through a temporary tile -
and per data type a table of the kernels with a chooser by MR and NR.
"""

from __future__ import annotations
import re

from .families import kernel, DT_CHAR

CTYPE = {"FP32": "float", "FP64": "double"}

#: a gemm kernel's parameters as BLIS passes them: k, the panels, C, the
#: scalars; C's strides in bytes, as the kernels take them
GEMM_ARGS = {
    "k": ("dim_t", "k"),
    "base(A)": ("const void*", "a"),
    "base(B)": ("const void*", "b"),
    "base(C)": ("void*", "c"),
    "base(alpha)": ("const void*", "alpha"),
    "base(beta)": ("const void*", "beta"),
    "stride(C,n)": ("inc_t", "cs_c * (inc_t)sizeof({ctype})"),
    "stride(C,m)": ("inc_t", "rs_c * (inc_t)sizeof({ctype})"),
}


def vl_helper(gen, name: str = "ukrgen_vl") -> str:
    """
    The vector length in elements of a size, as the ISA reads it: the
    generator's SIMD size in bytes, divided
    """
    return vl_function(gen.c_simd_size_function, name)


def vl_function(simd_size_c: str, name: str) -> str:
    # asmgen's helper is inline, or static inline since its 0.6 (0048): static
    # once either way
    size = re.sub(r"(?:static\s+)?inline\s+size_t\s+get_simd_size\s*\(\s*\)",
                  f"static inline size_t {name}_bytes( void )", simd_size_c, count=1)
    return f"{size}\n\nstatic inline dim_t {name}( size_t esize )\n" \
           f"{{\n\treturn ( dim_t )( {name}_bytes() / esize );\n}}\n"


def vl_helpers(kernels: list, gen) -> str:
    """
    One vector-length function per way the kernels' generators read their
    vectors' size - RVV's grouped registers (LMUL) read otherwise than
    single ones - each kernel given its own (vl_fn); the first is
    ukrgen_vl
    """
    names = {}
    for k in kernels:
        text = k.simd_size_c or gen.c_simd_size_function
        if text not in names:
            names[text] = "ukrgen_vl" if not names else f"ukrgen_vl_{len(names)}"
        k.vl_fn = names[text]
    if not names:
        names[gen.c_simd_size_function] = "ukrgen_vl"
    return "\n".join(vl_function(text, name) for text, name in names.items())


def c_expr(expr: str, ctype: str, vl_fn: str = "ukrgen_vl") -> str:
    """
    A blocksize - 8, 2*VL, VL - in C: VL read at run time
    """
    return str(expr).replace(" ", "").replace("VL", f"{vl_fn}( sizeof( {ctype} ) )")


def asm_symbol(k: kernel) -> str:
    return f"{k.symbol}_asm"


def asm_source(k: kernel) -> str:
    """
    The kernel's assembly, as a function under its assembly symbol
    """
    if k.asm:
        return k.asm
    # the kernel offset bytes past a boundary, if it's to be (generate's align)
    boundary, offset = k.align or (None, 0)
    return "\n".join(k.program.function(asm_symbol(k), align=boundary, offset=offset)) + "\n"


def gemm_wrapper(k: kernel) -> str:
    """
    BLIS's gemm microkernel around the kernel: the edge-case macros with the
    kernel's C orientation, BLIS's arguments onto the kernel's parameters
    """
    ctype, ch = CTYPE[k.dtype], DT_CHAR[k.dtype]
    unknown = [p for p in k.params if p not in GEMM_ARGS]
    if unknown:
        raise ValueError(f"{k.symbol}: no BLIS argument for its parameters {unknown}")
    proto = ", ".join(GEMM_ARGS[p][0] for p in k.params)
    args = ", ".join(GEMM_ARGS[p][1].format(ctype=ctype) for p in k.params)
    row = "true" if "row" == k.c_layout else "false"
    # the temporary tile: for edge cases only where the kernel takes any C (a
    # storage branch 'any', or both strides at run time); where it branches
    # on row- and column-major C, also when neither stride is 1
    storages = set(k.c_storages or [k.c_layout])
    if "any" in storages:
        setup = "GEMM_UKR_SETUP_CT_ANY"
    elif {"row", "col"} <= storages:
        setup = "GEMM_UKR_SETUP_CT_AMBI"
    else:
        setup = "GEMM_UKR_SETUP_CT"
    return f"""\
void {asm_symbol(k)}( {proto} );

// {k.family}: {k.mr} x {k.nr}, C {" / ".join(k.c_storages or []) + " (branches)" if k.c_storages else ("of any storage" if "any" == k.c_layout else k.c_layout + "-major")}
void {k.symbol}
     (
             dim_t      m,
             dim_t      n,
             dim_t      k,
       const void*      alpha,
       const void*      a,
       const void*      b,
       const void*      beta,
             void*      c, inc_t rs_c, inc_t cs_c,
       const auxinfo_t* data,
       const cntx_t*    cntx
     )
{{
	( void )data; ( void )cntx;
	const dim_t mr = {c_expr(k.mr, ctype, k.vl_fn)};
	const dim_t nr = {c_expr(k.nr, ctype, k.vl_fn)};
	{setup}( {ch}, mr, nr, {row} );
	{asm_symbol(k)}( {args} );
	GEMM_UKR_FLUSH_CT( {ch} );
}}
"""


def split_size(expr: str) -> tuple[int, int]:
    """
    A blocksize as (vectors, elements): its value is vectors x VL + elements -
    8 -> (0, 8), 2*VL -> (2, 0), VL -> (1, 0), a split's 2*VL + 2 -> (2, 2)
    """
    vectors = elements = 0
    for term in str(expr).replace(" ", "").replace("-", "+-").split("+"):
        if not term:
            continue
        if term.endswith("VL"):
            count = term[:-2].rstrip("*")
            vectors += int(count) if count not in ("", "-") else (-1 if "-" == count else 1)
        else:
            elements += int(term)
    return vectors, elements

def gemm_table(dtype: str, kernels: list[kernel], default: tuple | None) -> str:
    """
    The data type's kernels and a chooser: the kernel whose MR and NR -
    elements, the vector length read at run time - are the ones asked for,
    else the family's default size, else the first
    """
    ctype, ch = CTYPE[dtype], DT_CHAR[dtype]
    mine = [k for k in kernels if dtype == k.dtype and not k.case]
    if not mine:
        return ""
    rows = []
    fallback = 0
    for i, k in enumerate(mine):
        mv, me = split_size(k.mr)
        nv, ne = split_size(k.nr)
        rows.append(f"\t{{ {mv}, {me}, {nv}, {ne}, {k.symbol}, {'true' if 'row' == k.c_layout else 'false'}, "
                    f"\"{k.family}_{k.symbol.rsplit('_', 1)[-1]}\", {k.vl_fn} }},")
        if default is not None and tuple(default) == tuple(k.size):
            fallback = i
    body = "\n".join(rows)
    return f"""\
static const ukrgen_gemm_entry ukrgen_{ch}gemm_kernels[] =
{{
{body}
}};

// the {ctype} kernel of MR x NR elements, or the default ({mine[fallback].symbol})
static const ukrgen_gemm_entry* ukrgen_{ch}gemm_choose( dim_t mr, dim_t nr )
{{
	const dim_t count = sizeof( ukrgen_{ch}gemm_kernels ) / sizeof( ukrgen_{ch}gemm_kernels[ 0 ] );
	for ( dim_t i = 0; i < count; ++i )
	{{
		const ukrgen_gemm_entry* e = &ukrgen_{ch}gemm_kernels[ i ];
		const dim_t vl = e->vl( sizeof( {ctype} ) );
		if ( ukrgen_size( e->mr_vectors, e->mr_elements, vl ) == mr &&
		     ukrgen_size( e->nr_vectors, e->nr_elements, vl ) == nr ) return e;
	}}
	return &ukrgen_{ch}gemm_kernels[ {fallback} ];
}}
"""


GEMM_TABLE_PRELUDE = """\
// a gemm kernel: MR and NR as vectors * the vector length + elements (a split
// microtile's parts: 2*VL + 2)
typedef struct
{
	dim_t       mr_vectors;
	dim_t       mr_elements;
	dim_t       nr_vectors;
	dim_t       nr_elements;
	gemm_ukr_ft ukr;
	bool        row_pref;
	const char* name;
	dim_t       ( *vl )( size_t esize );
} ukrgen_gemm_entry;

static inline dim_t ukrgen_size( dim_t vectors, dim_t elements, dim_t vl )
{
	return vectors * vl + elements;
}
"""


#: the cache blocksizes' defaults: MC and NC as multiples of MR and NR, KC -
#: BLIS_MR_IN_MC_<dt>, BLIS_NR_IN_NC_<dt>, BLIS_KC_<dt> override them
BLOCKSIZE_DEFAULTS = {"mr-in-mc": 16, "nr-in-nc": 200, "kc": 256}

#: BLIS's names of a data type
NUM = {"FP32": "BLIS_FLOAT", "FP64": "BLIS_DOUBLE"}


def gemm_prototype(symbol: str) -> str:
    return f"void {symbol}( dim_t m, dim_t n, dim_t k, const void* alpha, const void* a, " \
           f"const void* b, const void* beta, void* c, inc_t rs_c, inc_t cs_c, " \
           f"const auxinfo_t* data, const cntx_t* cntx );"


def cntx_init(config_name: str, gen, kernels: list[kernel], defaults: dict, blocksizes: dict) -> str:
    """
    The configuration's context initialization: the reference first, then
    per data type with kernels the one BLIS_MR_<dt> x BLIS_NR_<dt> names -
    the family's default where unset or not made - registered with its
    orientation, MR and NR from it, MC, NC and KC from the configuration's
    defaults (PR 960 overriding them afterwards); a data type without
    kernels keeps the reference's kernel and blocksizes
    """
    dts = [dt for dt in ("FP32", "FP64") if any(dt == k.dtype and not k.case for k in kernels)]
    packs = [dt for dt in ("FP32", "FP64") if any(dt == k.dtype and k.case for k in kernels)]
    protos = "\n".join([gemm_prototype(k.symbol) for k in kernels if not k.case] +
                       [packm_prototype(config_name, dt) for dt in packs] +
                       # defined below, called by the init: C99 wants it declared first
                       [f"void bli_cntx_init_{config_name}_ref( cntx_t* cntx );"])
    lines = []
    for dt in ("FP32", "FP64"):
        ch, ctype = DT_CHAR[dt], CTYPE[dt]
        bs = dict(BLOCKSIZE_DEFAULTS)
        bs.update(blocksizes.get(dt, {}))
        if dt in dts:
            lines.append(f"""\
	const ukrgen_gemm_entry* k_{ch} = ukrgen_{ch}gemm_choose( ukrgen_env( "BLIS_MR_{ch.upper()}" ),
	                                                    ukrgen_env( "BLIS_NR_{ch.upper()}" ) );
	const dim_t vl_{ch} = k_{ch}->vl( sizeof( {ctype} ) );
	const dim_t mr_{ch} = ukrgen_size( k_{ch}->mr_vectors, k_{ch}->mr_elements, vl_{ch} );
	const dim_t nr_{ch} = ukrgen_size( k_{ch}->nr_vectors, k_{ch}->nr_elements, vl_{ch} );
	const dim_t mc_{ch} = {int(bs["mr-in-mc"])} * mr_{ch};
	const dim_t nc_{ch} = {int(bs["nr-in-nc"])} * nr_{ch};
	const dim_t kc_{ch} = {int(bs["kc"])};""")
        else:
            lines.append("\n".join(
                f"\tconst dim_t {b}_{ch} = bli_cntx_get_blksz_def_dt( {NUM[dt]}, BLIS_{b.upper()}, cntx );"
                for b in ("mr", "nr", "mc", "nc", "kc")))
    ukrs = "".join(f"\t                   BLIS_GEMM_UKR, {NUM[dt]}, k_{DT_CHAR[dt]}->ukr,\n" for dt in dts) + \
           "".join(f"\t                   BLIS_PACKM_KER, {NUM[dt]}, bli_{DT_CHAR[dt]}packm_{config_name},\n"
                   for dt in packs)
    prefs = "".join(f"\t                        BLIS_GEMM_UKR_ROW_PREF, {NUM[dt]}, k_{DT_CHAR[dt]}->row_pref,\n"
                    for dt in dts)
    choose = "\n".join(lines)
    register = (f"""\
	bli_cntx_set_ukrs( cntx,
{ukrs}	                   BLIS_VA_END );
""" if dts or packs else "") + (f"""\
	bli_cntx_set_ukr_prefs( cntx,
{prefs}	                        BLIS_VA_END );
""" if dts else "")
    helpers = vl_helpers(kernels, gen)
    tables = "".join(gemm_table(dt, kernels, defaults.get(dt)) for dt in dts)
    return f"""\
#include "blis.h"

{helpers}
{protos}

{GEMM_TABLE_PRELUDE}
{tables}
static dim_t ukrgen_env( const char* name )
{{
	return ( dim_t )bli_env_get_var( name, 0 );
}}

void bli_cntx_init_{config_name}( cntx_t* cntx )
{{
	blksz_t blkszs[ BLIS_NUM_BLKSZS ];

	bli_cntx_init_{config_name}_ref( cntx );

	// the microkernels: BLIS_MR_<dt> x BLIS_NR_<dt> (elements) where such a
	// kernel was made, the default otherwise
{choose}

{register}
	// MC, NC and KC are defaults: BLIS_MR_IN_MC_<dt>, BLIS_NR_IN_NC_<dt> and
	// BLIS_KC_<dt> override them once the context is made (bli_gks.c)
	bli_blksz_init_easy( &blkszs[ BLIS_MR ], mr_s, mr_d, -1, -1 );
	bli_blksz_init_easy( &blkszs[ BLIS_NR ], nr_s, nr_d, -1, -1 );
	bli_blksz_init_easy( &blkszs[ BLIS_MC ], mc_s, mc_d, -1, -1 );
	bli_blksz_init_easy( &blkszs[ BLIS_KC ], kc_s, kc_d, -1, -1 );
	bli_blksz_init_easy( &blkszs[ BLIS_NC ], nc_s, nc_d, -1, -1 );

	bli_cntx_set_blkszs
	(
	  cntx,
	  BLIS_NC, &blkszs[ BLIS_NC ], BLIS_NR,
	  BLIS_KC, &blkszs[ BLIS_KC ], BLIS_KR,
	  BLIS_MC, &blkszs[ BLIS_MC ], BLIS_MR,
	  BLIS_NR, &blkszs[ BLIS_NR ], BLIS_NR,
	  BLIS_MR, &blkszs[ BLIS_MR ], BLIS_MR,
	  BLIS_VA_END
	);
}}
"""


#: the longest vector, in bytes, a VLA ISA allows - for sizing BLIS's stack
#: temporary tile when the configuration doesn't give it
LONGEST_VECTOR = {"sve": 256, "sme": 256, "rvv": 256, "rvv071": 256}


#: the element size BLIS checks the stack buffer by: a double complex's
DCOMPLEX_SIZE = 16


def stack_buf_size(isa: str, gen, kernels: list[kernel], given: int | None = None) -> int:
    """
    BLIS_STACK_BUF_MAX_SIZE: given, or what BLIS checks it against
    (bli_check_sufficient_stack_buf_size) - every kernel's MR x NR at the
    ISA's longest vector, in double complex elements whatever the kernel's
    type (mixed-domain and induced methods use the microtile so) - at least
    BLIS's 2048, rounded up to 64 bytes
    """
    if given:
        return int(given)
    largest = 2048
    for k in kernels:
        # the vector length in the kernel's own elements
        vl = LONGEST_VECTOR.get(isa, 0) // (4 if "FP32" == k.dtype else 8)
        mv, me = split_size(k.mr)
        nv, ne = split_size(k.nr)
        mr = mv * vl + me
        nr = nv * vl + ne
        largest = max(largest, mr * nr * DCOMPLEX_SIZE)
    return (largest + 63) // 64 * 64


def family_header(config_name: str, stack_size: int) -> str:
    """
    bli_family_<config>.h: the stack temporary tile sized for the
    configuration's kernels, BLIS's MC/NR and NC/MR constraints relaxed (as
    nearly every configuration does) - MR x NR pairs are any the families make
    """
    guard = f"BLIS_FAMILY_{config_name.upper()}_H"
    return f"""\
#ifndef {guard}
#define {guard}

// the temporary microtile of partial tiles and storage a kernel doesn't take
#define BLIS_STACK_BUF_MAX_SIZE {int(stack_size)}

#define BLIS_RELAX_MCNR_NCMR_CONSTRAINTS

#endif
"""


#: a packm case's parameters as BLIS passes them: the panel's length, A and
#: its strides (bytes), P, kappa
PACKM_ARGS = {
    "n": ("dim_t", "n"),
    "base(X)": ("const void*", "a"),
    "base(Y)": ("void*", "p"),
    "base(kappa)": ("const void*", "kappa"),
    "stride(X,n)": ("inc_t", "lda * (inc_t)sizeof({ctype})"),
    "stride(X,m)": ("inc_t", "inca * (inc_t)sizeof({ctype})"),
    "stride(Y,n)": ("inc_t", "ldp * (inc_t)sizeof({ctype})"),
    # a masked vec case's rows past its whole vectors (its row() computes it)
    "tail(m)": ("dim_t", "tail"),
}

#: rows a vec case's kernel leaves to the reference at most - cdim of the
#: vectors plus a few: a split microtile's 2*VL + 2
PACKM_REST = 16

PACKM_SIGNATURE = """\
     (
             conj_t  conja,
             pack_t  schema,
             dim_t   cdim,
             dim_t   cdim_max,
             dim_t   cdim_bcast,
             dim_t   n,
             dim_t   n_max,
       const void*   kappa,
       const void*   a, inc_t inca, inc_t lda,
             void*   p,             inc_t ldp,
       const void*   params,
       const cntx_t* cntx
     )"""


def packm_prototype(config_name: str, dtype: str) -> str:
    return f"void bli_{DT_CHAR[dtype]}packm_{config_name}\n{PACKM_SIGNATURE};"


def packm_dispatch(config_name: str, dtype: str, kernels: list[kernel], order: list | None = None,
                   rest: int | None = None, tail: str = "overlap") -> str:
    """
    The data type's packm: each case a block of its own, tried in order -
    the family's dispatch (by case name), else vec, gather, trans as the
    config has them - and everything else the reference's, which also fills
    the edges. vec, gather cases taking P's leading dimension pack the
    vectors of any cdim from theirs to theirs plus rest - the family's
    vec-rest, else PACKM_REST - (inca 1 for vec, lda 1 for gather), the
    reference the rows left; a full panel - cdim
    of cdim_max rows, n of n_max, no broadcast, P's rows cdim apart - of a
    size a case packs goes to that case: vec where A is contiguous along
    cdim (inca 1), trans where along the panel (lda 1)
    """
    ctype, ch = CTYPE[dtype], DT_CHAR[dtype]
    mine = [k for k in kernels if dtype == k.dtype and k.case]
    kind_of = lambda k: k.kind or k.case
    bad = [k.symbol for k in mine if "gather" == kind_of(k) and "stride(Y,n)" not in k.params]
    if bad:
        raise ValueError(f"gather cases take P's leading dimension (Y-layout [m:c, n:s]): {bad}")
    for k in mine:
        unknown = [p for p in k.params if p not in PACKM_ARGS]
        if unknown:
            raise ValueError(f"{k.symbol}: no BLIS argument for its parameters {unknown}")
    names = list(dict.fromkeys(k.case for k in mine))
    if order is None:
        # masked vec cases first: one pass, where a vec case and the
        # reference take two
        rank = {"vec": 1, "gather": 2, "trans": 3}
        first = lambda n: next(k for k in mine if n == k.case)
        # a trans case's blocks after its full panels: exact ones first
        blockwise = lambda n: "trans" == kind_of(first(n)) and "stride(Y,n)" in first(n).params
        names.sort(key=lambda n: 0 if first(n).tail else rank.get(kind_of(first(n)), 4) + (0.5 if blockwise(n) else 0))
    else:
        names = [n for n in order if n in names]
    decls = [f"void {asm_symbol(k)}( {', '.join(PACKM_ARGS[p][0] for p in k.params)} );"
             for n in names for k in mine if n == k.case]

    def at(q, start):
        """a kernel's arguments, A's and P's rows from start"""
        return ", ".join({"base(X)": f"( const {ctype}* )a + {start} * inca",
                          "base(Y)": f"( {ctype}* )p + {start}"}.get(p) or PACKM_ARGS[p][1].format(ctype=ctype)
                         for p in q.params)

    def row(k, peers=()):
        args = ", ".join(PACKM_ARGS[p][1].format(ctype=ctype) for p in k.params)
        if k.tail:
            # its whole vectors, then the last one masked to the rows left -
            # any cdim between, in one pass; the reference zeroes the rows
            # past cdim, where cdim_max has more
            vl = c_expr("VL", ctype, k.vl_fn)
            # its rows less one vector length: whole vectors before the masked
            # one - k*VL or a number of elements (AVX-512's 16), alike
            rows = c_expr(k.mr, ctype, k.vl_fn)
            return f"""\
\t\t{{
\t\t\tconst dim_t full = {rows} - {vl};
\t\t\tif ( full < cdim && cdim - full < {vl} )
\t\t\t{{
\t\t\t\tconst dim_t tail = cdim - full;
\t\t\t\t{asm_symbol(k)}( {args} );
\t\t\t\tif ( cdim < cdim_max )
\t\t\t\t\tbli_{ch}{ch}packm_{config_name}_ref( conja, schema, 0, cdim_max - cdim,
\t\t\t\t\t    cdim_bcast, n, n_max, kappa, ( const {ctype}* )a + cdim * inca, inca, lda,
\t\t\t\t\t    ( {ctype}* )p + cdim, ldp, params, cntx );
\t\t\t\treturn;
\t\t\t}}
\t\t}}"""
        return f"""\
\t\t{{
\t\t\tconst dim_t done = {c_expr(k.mr, ctype, k.vl_fn)};
\t\t\tif ( done <= cdim && cdim - done <= {PACKM_REST if rest is None else rest} )
\t\t\t{{
\t\t\t\t{asm_symbol(k)}( {args} );
\t\t\t\tif ( done < cdim )
\t\t\t\t{{
{overlap(k, peers)}\t\t\t\t}}
\t\t\t\tif ( cdim < cdim_max )
\t\t\t\t\tbli_{ch}{ch}packm_{config_name}_ref( conja, schema, 0, cdim_max - cdim,
\t\t\t\t\t    cdim_bcast, n, n_max, kappa, ( const {ctype}* )a + cdim * inca, inca, lda,
\t\t\t\t\t    ( {ctype}* )p + cdim, ldp, params, cntx );
\t\t\t\treturn;
\t\t\t}}
\t\t}}"""

    def overlap(k, peers):
        """
        The rows left past a vec kernel's: a kernel of the case ending at
        cdim - the smallest that covers them and fits in cdim - its first
        rows packed again, the same values (vec-tail overlap); else, or
        where the family says reference, the reference
        """
        lines = []
        if "overlap" == tail:
            for q in sorted((q for q in peers if not q.tail),
                            key=lambda q: (split_size(q.mr)[0] * q.lmul, split_size(q.mr)[1])):
                rows = c_expr(q.mr, ctype, q.vl_fn)
                lines.append(f"\t\t\t\t\t{'else ' if lines else ''}if ( cdim - done <= {rows} && {rows} <= cdim )\n"
                             f"\t\t\t\t\t\t{asm_symbol(q)}( {at(q, f'( cdim - {rows} )')} );\n")
        lines.append(f"\t\t\t\t\t{'else' if lines else ''}\n"
                     f"\t\t\t\t\t\tbli_{ch}{ch}packm_{config_name}_ref( conja, schema, cdim - done, cdim - done,\n"
                     f"\t\t\t\t\t\t    cdim_bcast, n, n_max, kappa, ( const {ctype}* )a + done * inca, inca, lda,\n"
                     f"\t\t\t\t\t\t    ( {ctype}* )p + done, ldp, params, cntx );\n")
        return "".join(lines)

    def branch(k):
        if "VL" == k.loop_unit:
            # chunks of a vector length along the panel; the reference takes
            # what's left of one - A and P from the first column it packs
            vl = f"{k.vl_fn}( sizeof( {ctype} ) )"
            args = ", ".join("chunks" if "n" == p else PACKM_ARGS[p][1].format(ctype=ctype)
                             for p in k.params)
            return f"""\
\t\tif ( cdim == {c_expr(k.mr, ctype, k.vl_fn)} )
\t\t{{
\t\t\tconst dim_t chunks = n / {vl}, done = chunks * {vl};
\t\t\tif ( chunks ) {asm_symbol(k)}( {args} );
\t\t\tif ( done < n )
\t\t\t\tbli_{ch}{ch}packm_{config_name}_ref( conja, schema, cdim, cdim_max, cdim_bcast,
\t\t\t\t    n - done, n_max - done, kappa, ( const {ctype}* )a + done * lda, inca, lda,
\t\t\t\t    ( {ctype}* )p + done * ldp, ldp, params, cntx );
\t\t\treturn;
\t\t}}"""
        args = ", ".join(PACKM_ARGS[p][1].format(ctype=ctype) for p in k.params)
        return f"\t\tif ( cdim == {c_expr(k.mr, ctype, k.vl_fn)} ) {{ {asm_symbol(k)}( {args} ); return; }}"

    def trans_blocks(name, ks):
        """
        A trans case taking P's leading dimension: its kernels on blocks of
        rows - each as many times as fit, the widest first, at A's and P's
        rows done - the reference for what's left of each block's last
        vector-length chunk, the rows no kernel fits, and the zero padding
        """
        calls = []
        for k in sorted(ks, key=lambda k: -split_size(k.mr)[1] - split_size(k.mr)[0] * 1000):
            rows = c_expr(k.mr, ctype, k.vl_fn)
            vl = f"{k.vl_fn}( sizeof( {ctype} ) )" if "VL" == k.loop_unit else "1"
            args = ", ".join({"n": "chunks", "base(X)": f"( const {ctype}* )a + done * inca",
                              "base(Y)": f"( {ctype}* )p + done"}.get(p) or
                             PACKM_ARGS[p][1].format(ctype=ctype) for p in k.params)
            calls.append(f"""\
\t\twhile ( cdim - done >= {rows} )
\t\t{{
\t\t\tconst dim_t chunks = n / {vl}, packed = chunks * {vl};
\t\t\tif ( chunks ) {asm_symbol(k)}( {args} );
\t\t\tif ( packed < n )
\t\t\t\tbli_{ch}{ch}packm_{config_name}_ref( conja, schema, {rows}, {rows}, cdim_bcast,
\t\t\t\t    n - packed, n_max - packed, kappa, ( const {ctype}* )a + done * inca + packed * lda, inca, lda,
\t\t\t\t    ( {ctype}* )p + done + packed * ldp, ldp, params, cntx );
\t\t\tdone += {rows};
\t\t}}""")
        return (f"\t// {name}: A's rows contiguous, in blocks of rows - any cdim\n"
                f"\tif ( cdim_bcast == 1 && n == n_max && lda == 1 )\n\t{{\n\t\tdim_t done = 0;\n"
                + "\n".join(calls) + f"""
\t\t// the rows no block takes, and the padding to cdim_max
\t\tif ( done < cdim_max )
\t\t\tbli_{ch}{ch}packm_{config_name}_ref( conja, schema, cdim - done, cdim_max - done, cdim_bcast,
\t\t\t    n, n_max, kappa, ( const {ctype}* )a + done * inca, inca, lda,
\t\t\t    ( {ctype}* )p + done, ldp, params, cntx );
\t\treturn;
\t}}""")

    blocks = []
    for name in names:
        ks = [k for k in mine if name == k.case]
        kind = kind_of(ks[0])
        along = "inca == 1" if "vec" == kind else "lda == 1"
        # taking P's leading dimension: any cdim from theirs, the most vectors first
        # by rows: a kernel's vectors its LMUL's groups (k.lmul)
        strided = sorted([k for k in ks if "stride(Y,n)" in k.params],
                         key=lambda k: (-split_size(k.mr)[0] * k.lmul, -split_size(k.mr)[1]))
        full = [k for k in ks if k not in strided]
        if strided and "trans" == kind:
            # blocks of rows: A's rows contiguous, any cdim - B rows a call,
            # the widest blocks first, P's rows ldp apart (large vectors'
            # cdims, 2*VL rows and more, past any one kernel's rows)
            blocks.append(trans_blocks(name, strided))
            strided = []
        if strided:
            note = "A's rows inca apart, gathered into vectors along cdim" if "gather" == kind else name
            blocks.append(f"\t// {note}\n\tif ( cdim_bcast == 1 && n == n_max && {along} )\n\t{{\n"
                          + "\n".join(row(k, strided) for k in strided) + "\n\t}")
        if full:
            blocks.append(f"\t// {name}: a full panel\n\tif ( cdim_bcast == 1 && cdim == cdim_max && n == n_max "
                          f"&& ldp == cdim && {along} )\n\t{{\n" + "\n".join(branch(k) for k in full)
                          + "\n\t}")
    body = "\n".join(blocks)
    return f"""\
{chr(10).join(decls)}

// the reference, for everything the cases don't pack
void bli_{ch}{ch}packm_{config_name}_ref
{PACKM_SIGNATURE};

void bli_{ch}packm_{config_name}
{PACKM_SIGNATURE}
{{
{body}
\tbli_{ch}{ch}packm_{config_name}_ref( conja, schema, cdim, cdim_max, cdim_bcast, n, n_max,
\t                              kappa, a, inca, lda, p, ldp, params, cntx );
}}
"""
