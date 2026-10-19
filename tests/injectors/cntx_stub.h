/* The context calls a generated bli_cntx_init makes - recorded, for testing
   the initialization without BLIS (with blis_stub.h for the types) */
#ifndef CNTX_STUB_H
#define CNTX_STUB_H
#include <stdarg.h>
#include <stdlib.h>
#include "blis_stub.h"
typedef enum { BLIS_FLOAT = 0, BLIS_DOUBLE = 1 } num_t;
enum { BLIS_KR = 0, BLIS_MR, BLIS_NR, BLIS_KC, BLIS_MC, BLIS_NC, BLIS_NUM_BLKSZS };
enum { BLIS_GEMM_UKR = 100, BLIS_GEMM_UKR_ROW_PREF = 200, BLIS_VA_END = -1 };
typedef struct { dim_t v[ 2 ]; } blksz_t;
typedef void ( *gemm_ukr_ft )( dim_t, dim_t, dim_t, const void*, const void*, const void*, const void*,
                               void*, inc_t, inc_t, const auxinfo_t*, const cntx_t* );
static gemm_ukr_ft stub_ukr[ 2 ];
static int stub_pref[ 2 ] = { -1, -1 };
static dim_t stub_bs[ BLIS_NUM_BLKSZS ][ 2 ];
static long bli_env_get_var( const char* name, long def )
{
	const char* v = getenv( name );
	return v ? atol( v ) : def;
}
static void bli_cntx_set_ukrs( cntx_t* cntx, ... )
{
	va_list ap; va_start( ap, cntx );
	for ( int id; ( id = va_arg( ap, int ) ) != BLIS_VA_END; )
	{ int dt = va_arg( ap, int ); stub_ukr[ dt ] = va_arg( ap, gemm_ukr_ft ); }
	va_end( ap );
}
static void bli_cntx_set_ukr_prefs( cntx_t* cntx, ... )
{
	va_list ap; va_start( ap, cntx );
	for ( int id; ( id = va_arg( ap, int ) ) != BLIS_VA_END; )
	{ int dt = va_arg( ap, int ); stub_pref[ dt ] = va_arg( ap, int ); }
	va_end( ap );
}
static void bli_blksz_init_easy( blksz_t* b, dim_t s, dim_t d, dim_t se, dim_t de )
{ b->v[ 0 ] = s; b->v[ 1 ] = d; }
static void bli_cntx_set_blkszs( cntx_t* cntx, ... )
{
	va_list ap; va_start( ap, cntx );
	for ( int id; ( id = va_arg( ap, int ) ) != BLIS_VA_END; )
	{ blksz_t* b = va_arg( ap, blksz_t* ); ( void )va_arg( ap, int );
	  stub_bs[ id ][ 0 ] = b->v[ 0 ]; stub_bs[ id ][ 1 ] = b->v[ 1 ]; }
	va_end( ap );
}
static dim_t bli_cntx_get_blksz_def_dt( num_t dt, int id, const cntx_t* cntx )
{ return stub_bs[ id ][ dt ]; }
#endif
