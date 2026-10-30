/* The context calls a generated bli_cntx_init makes - recorded, for testing
   the initialization without BLIS (with blis_stub.h for the types). A
   blksz_t holds a value per data type and a maximum beside it (BLIS's v and
   e); both are recorded, the defaults in stub_bs and the maxima in
   stub_bs_max */
#ifndef CNTX_STUB_H
#define CNTX_STUB_H
#include <stdarg.h>
#include <stdlib.h>
#include "blis_stub.h"
typedef enum { BLIS_FLOAT = 0, BLIS_DOUBLE = 1 } num_t;
enum { BLIS_KR = 0, BLIS_MR, BLIS_NR, BLIS_KC, BLIS_MC, BLIS_NC, BLIS_NUM_BLKSZS };
enum { BLIS_GEMM_UKR = 100, BLIS_GEMM_UKR_ROW_PREF = 200, BLIS_VA_END = -1 };
typedef struct { dim_t v[ 2 ]; dim_t e[ 2 ]; } blksz_t;
typedef void ( *gemm_ukr_ft )( dim_t, dim_t, dim_t, const void*, const void*, const void*, const void*,
                               void*, inc_t, inc_t, const auxinfo_t*, const cntx_t* );
static gemm_ukr_ft stub_ukr[ 2 ];
static int stub_pref[ 2 ] = { -1, -1 };
static dim_t stub_bs[ BLIS_NUM_BLKSZS ][ 2 ];
static dim_t stub_bs_max[ BLIS_NUM_BLKSZS ][ 2 ];
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
/* BLIS's: a value for each data type, the maximum the same */
static void bli_blksz_init_easy( blksz_t* b, dim_t s, dim_t d, dim_t sc, dim_t dc )
{
	b->v[ 0 ] = b->e[ 0 ] = s; b->v[ 1 ] = b->e[ 1 ] = d;
	( void )sc; ( void )dc;
}
/* the defaults first, then the maxima, as BLIS takes them */
static void bli_blksz_init( blksz_t* b, dim_t s, dim_t d, dim_t sc, dim_t dc,
                            dim_t se, dim_t de, dim_t sec, dim_t dec )
{
	( void )sc; ( void )dc; ( void )sec; ( void )dec;
	b->v[ 0 ] = s; b->v[ 1 ] = d; b->e[ 0 ] = se; b->e[ 1 ] = de;
}
static void bli_cntx_set_blkszs( cntx_t* cntx, ... )
{
	va_list ap; va_start( ap, cntx );
	for ( int id; ( id = va_arg( ap, int ) ) != BLIS_VA_END; )
	{ blksz_t* b = va_arg( ap, blksz_t* ); ( void )va_arg( ap, int );
	  stub_bs[ id ][ 0 ] = b->v[ 0 ]; stub_bs[ id ][ 1 ] = b->v[ 1 ];
	  stub_bs_max[ id ][ 0 ] = b->e[ 0 ]; stub_bs_max[ id ][ 1 ] = b->e[ 1 ]; }
	va_end( ap );
}
static dim_t bli_cntx_get_blksz_def_dt( num_t dt, int id, const cntx_t* cntx )
{ return stub_bs[ id ][ dt ]; }
static dim_t bli_cntx_get_blksz_max_dt( num_t dt, int id, const cntx_t* cntx )
{ return stub_bs_max[ id ][ dt ]; }
#endif
