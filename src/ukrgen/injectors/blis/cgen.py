"""
C and assembly for blisgen's gemm kernels: each kernel's assembly, a wrapper
with BLIS's microkernel signature around it - BLIS's edge-case macros taking
partial tiles and storage the kernel doesn't take through a temporary tile -
and per data type a table of the kernels with a chooser by MR and NR.
"""

from __future__ import annotations

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


def vl_helper(gen) -> str:
    """
    The vector length in elements of a size, as the ISA reads it: the
    generator's SIMD size in bytes, divided
    """
    size = gen.c_simd_size_function.replace("inline size_t get_simd_size()",
                                            "static inline size_t ukrgen_simd_size( void )")
    return f"{size}\n\nstatic inline dim_t ukrgen_vl( size_t esize )\n" \
           f"{{\n\treturn ( dim_t )( ukrgen_simd_size() / esize );\n}}\n"


def c_expr(expr: str, ctype: str) -> str:
    """
    A blocksize - 8, 2*VL, VL - in C: VL read at run time
    """
    return str(expr).replace(" ", "").replace("VL", f"ukrgen_vl( sizeof( {ctype} ) )")


def asm_symbol(k: kernel) -> str:
    return f"{k.symbol}_asm"


def asm_source(k: kernel) -> str:
    """
    The kernel's assembly, as a function under its assembly symbol
    """
    return "\n".join(k.program.function(asm_symbol(k))) + "\n"


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
    return f"""\
void {asm_symbol(k)}( {proto} );

// {k.family}: {k.mr} x {k.nr}, C {k.c_layout}-major
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
             auxinfo_t* data,
       const cntx_t*    cntx
     )
{{
	( void )data; ( void )cntx;
	const dim_t mr = {c_expr(k.mr, ctype)};
	const dim_t nr = {c_expr(k.nr, ctype)};
	GEMM_UKR_SETUP_CT( {ch}, mr, nr, {row} );
	{asm_symbol(k)}( {args} );
	GEMM_UKR_FLUSH_CT( {ch} );
}}
"""


def split_size(expr: str) -> tuple[int, int]:
    """
    A blocksize as (count, vectors): 8 -> (8, 0), 2*VL -> (2, 1), VL -> (1, 1)
    """
    text = str(expr).replace(" ", "")
    if "VL" == text:
        return 1, 1
    if text.endswith("*VL"):
        return int(text[:-3]), 1
    return int(text), 0


def gemm_table(dtype: str, kernels: list[kernel], default: tuple | None) -> str:
    """
    The data type's kernels and a chooser: the kernel whose MR and NR -
    elements, the vector length read at run time - are the ones asked for,
    else the family's default size, else the first
    """
    ctype, ch = CTYPE[dtype], DT_CHAR[dtype]
    mine = [k for k in kernels if dtype == k.dtype]
    if not mine:
        return ""
    rows = []
    fallback = 0
    for i, k in enumerate(mine):
        mc, mv = split_size(k.mr)
        nc, nv = split_size(k.nr)
        rows.append(f"\t{{ {mc}, {mv}, {nc}, {nv}, {k.symbol}, {'true' if 'row' == k.c_layout else 'false'}, "
                    f"\"{k.family}_{k.symbol.rsplit('_', 1)[-1]}\" }},")
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
	const dim_t vl = ukrgen_vl( sizeof( {ctype} ) );
	const dim_t count = sizeof( ukrgen_{ch}gemm_kernels ) / sizeof( ukrgen_{ch}gemm_kernels[ 0 ] );
	for ( dim_t i = 0; i < count; ++i )
	{{
		const ukrgen_gemm_entry* e = &ukrgen_{ch}gemm_kernels[ i ];
		if ( ukrgen_size( e->mr_count, e->mr_vectors, vl ) == mr &&
		     ukrgen_size( e->nr_count, e->nr_vectors, vl ) == nr ) return e;
	}}
	return &ukrgen_{ch}gemm_kernels[ {fallback} ];
}}
"""


GEMM_TABLE_PRELUDE = """\
// a gemm kernel: MR and NR as count * (vectors ? the vector length : 1)
typedef struct
{
	dim_t       mr_count;
	int         mr_vectors;
	dim_t       nr_count;
	int         nr_vectors;
	gemm_ukr_ft ukr;
	bool        row_pref;
	const char* name;
} ukrgen_gemm_entry;

static inline dim_t ukrgen_size( dim_t count, int vectors, dim_t vl )
{
	return vectors ? count * vl : count;
}
"""
