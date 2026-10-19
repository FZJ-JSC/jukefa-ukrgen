/* A generated packm dispatch against what BLIS's packm does: full panels a
   case packs go to it, everything else to the reference (counted here) */
#include <stdio.h>
#include <stdlib.h>
#include "blis_stub.h"
typedef int conj_t;
typedef int pack_t;
#ifndef WT
#define WT double
#endif
static int ref_calls = 0;
void REF( conj_t conja, pack_t schema, dim_t cdim, dim_t cdim_max, dim_t cdim_bcast, dim_t n,
          dim_t n_max, const void* kappa, const void* a, inc_t inca, inc_t lda, void* p, inc_t ldp,
          const void* params, const cntx_t* cntx )
{
	const WT k = *( const WT* )kappa; const WT* A = a; WT* P = p;
	ref_calls++;
	for ( dim_t j = 0; j < n_max; j++ ) for ( dim_t i = 0; i < cdim_max; i++ )
		P[ i + j * ldp ] = ( i < cdim && j < n ) ? k * A[ i * inca + j * lda ] : 0;
}
#include KERNEL_C
static WT A[ 64 * 1024 ], P[ 64 * 1024 ];
int main( void )
{
	const dim_t vl = VL_OF();
	const WT kappa = 2;
	int bad = 0, runs = 0, fast = 0;
	for ( int i = 0; i < 64 * 1024; i++ ) A[ i ] = ( i % 13 ) - 6;
	/* cdim, cdim_max, n, inca, lda, the reference calls expected */
#ifndef CASES
#define CASES { vl, vl, 5, 1, vl + 3, 0 }, { 2 * vl, 2 * vl, 7, 1, 2 * vl + 1, 0 }, \
              { 2 * vl, 2 * vl, 1, 1, 2 * vl, 0 }, { vl + 1, vl + 1, 5, 1, vl + 4, 1 }, \
              { vl - 1, vl, 5, 1, vl + 3, 1 }, { vl, vl, 5, 3, 1, 1 }
#endif
	const dim_t cases[][6] = { CASES };
	const int count = sizeof( cases ) / sizeof( cases[ 0 ] );
	for ( int c = 0; c < count; c++ )
	{
		const dim_t cdim = cases[c][0], cdim_max = cases[c][1], n = cases[c][2];
		const inc_t inca = cases[c][3], lda = cases[c][4];
		for ( int i = 0; i < 64 * 1024; i++ ) P[ i ] = -99;
		const int before = ref_calls;
		PACKM( 0, 0, cdim, cdim_max, 1, n, n, &kappa, A, inca, lda, P, cdim_max, NULL, NULL );
		runs++;
		if ( ref_calls - before != ( int )cases[c][5] ) { printf( "case %d: %d reference calls, %ld expected\n", c, ref_calls - before, cases[c][5] ); bad++; }
		fast += ref_calls == before;
		for ( dim_t j = 0; j < n; j++ ) for ( dim_t i = 0; i < cdim_max; i++ )
		{
			const WT want = i < cdim ? kappa * A[ i * inca + j * lda ] : 0;
			if ( P[ i + j * cdim_max ] != want ) { if ( bad < 4 ) printf( "case %d P[%ld,%ld]=%g want %g\n", c, i, j, ( double )P[ i + j * cdim_max ], ( double )want ); bad++; break; }
		}
	}
	printf( "vl %ld: %d runs, %d by generated cases, %d wrong\n", vl, runs, fast, bad );
	return bad != 0;
}
