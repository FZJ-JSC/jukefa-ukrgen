/* The parts of blis.h a generated gemm wrapper uses - types and the gemm
   edge-case macros as BLIS defines them - for testing wrappers without BLIS */
#ifndef BLIS_STUB_H
#define BLIS_STUB_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef long dim_t;
typedef long inc_t;
typedef struct { int unused; } auxinfo_t;
typedef struct { int unused; } cntx_t;
typedef double d_ctype;
typedef float  s_ctype;
#define PASTEMAC(ch,op) ch##_##op
#define bli_tset0s(ch,x) ((x) = 0)
#define BLIS_STACK_BUF_MAX_SIZE 16384
#define bli_txpbys_mxn(chx,chb,chy,chc,m,n,x,rsx,csx,beta,y,rsy,csy) \
	for ( dim_t _j = 0; _j < (n); ++_j ) for ( dim_t _i = 0; _i < (m); ++_i ) \
		(y)[_i*(rsy) + _j*(csy)] = (x)[_i*(rsx) + _j*(csx)] + *(beta) * (y)[_i*(rsy) + _j*(csy)];
#define GEMM_UKR_SETUP_CT_PRE(ch,mr,nr,row_major,alignment) \
	const PASTEMAC(ch,ctype)* _beta = beta; \
	      PASTEMAC(ch,ctype)* _c = c; \
	const inc_t _rs_c = rs_c; \
	const inc_t _cs_c = cs_c; \
	      PASTEMAC(ch,ctype) _ct[ BLIS_STACK_BUF_MAX_SIZE / sizeof( PASTEMAC(ch,ctype) ) ] __attribute__((aligned(alignment))); \
	const inc_t _rs_ct = row_major ? nr : 1; \
	const inc_t _cs_ct = row_major ? 1 : mr;
#define GEMM_UKR_SETUP_CT_POST(ch) \
	PASTEMAC(ch,ctype) _zero; \
	bli_tset0s( ch, _zero ); \
	if ( _use_ct ) { c = _ct; rs_c = _rs_ct; cs_c = _cs_ct; beta = &_zero; }
#define GEMM_UKR_SETUP_CT(ch,mr,nr,row_major) \
	GEMM_UKR_SETUP_CT_PRE(ch,mr,nr,row_major,64); \
	const bool _use_ct = ( row_major ? cs_c != 1 : rs_c != 1 ) || m != mr || n != nr; \
	GEMM_UKR_SETUP_CT_POST(ch);
/* a kernel for both orientations: the temporary where neither stride is 1 */
#define GEMM_UKR_SETUP_CT_AMBI(ch,mr,nr,row_major) \
	GEMM_UKR_SETUP_CT_PRE(ch,mr,nr,row_major,64); \
	const bool _use_ct = ( cs_c != 1 && rs_c != 1 ) || m != mr || n != nr; \
	GEMM_UKR_SETUP_CT_POST(ch);
/* a kernel taking C of any storage: the temporary for edge cases only */
#define GEMM_UKR_SETUP_CT_ANY(ch,mr,nr,row_major) \
	GEMM_UKR_SETUP_CT_PRE(ch,mr,nr,row_major,64); \
	const bool _use_ct = ( m != mr || n != nr ); \
	GEMM_UKR_SETUP_CT_POST(ch);
#define GEMM_UKR_FLUSH_CT(ch) \
	if ( _use_ct ) { bli_txpbys_mxn( ch,ch,ch,ch, m, n, _ct, _rs_ct, _cs_ct, _beta, _c, _rs_c, _cs_c ); }
#endif
