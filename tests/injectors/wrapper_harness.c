/* A generated gemm wrapper against a reference: full and partial tiles,
   C column-major, row-major and general strided, nothing written beside */
#include <stdio.h>
#include <stdlib.h>
#include "blis_stub.h"
#ifndef WT
#define WT double
#endif
void UKR( dim_t m, dim_t n, dim_t k, const void* alpha, const void* a, const void* b,
          const void* beta, void* c, inc_t rs_c, inc_t cs_c, const auxinfo_t* data, const cntx_t* cntx );
dim_t MR_OF( void );
dim_t NR_OF( void );
#define LD 97
static WT A[64 * 1024], B[64 * 1024], C[LD * 2 * 160 + 64], R[LD * 2 * 160 + 64];
int main( void )
{
	const dim_t mr = MR_OF(), nr = NR_OF();
	int bad = 0, runs = 0;
	srand( 7 );
	for ( int i = 0; i < 64 * 1024; i++ ) { A[i] = rand() % 7 - 3; B[i] = rand() % 5 - 2; }
	const dim_t ms[] = { mr, mr - 1, 1 }, ns[] = { nr, nr > 1 ? nr - 1 : 1, 1 };
	for ( int st = 0; st < 3; st++ )
	for ( int mi = 0; mi < 3; mi++ ) for ( int ni = 0; ni < 3; ni++ ) for ( dim_t k = 1; k <= 3; k++ )
	{
		const dim_t m = ms[mi], n = ns[ni];
		if ( m < 1 || n < 1 ) continue;
		/* column-major, row-major, general */
		const inc_t rs = st == 0 ? 1 : st == 1 ? LD : 2, cs = st == 0 ? LD : st == 1 ? 1 : 2 * LD;
		const WT alpha = 2, beta = st == 2 ? 0 : 3;
		for ( int i = 0; i < LD * 2 * 160 + 64; i++ ) C[i] = R[i] = ( i % 11 ) - 5;
		for ( dim_t i = 0; i < m; i++ ) for ( dim_t j = 0; j < n; j++ )
		{
			WT s = 0;
			for ( dim_t p = 0; p < k; p++ ) s += A[i + p * mr] * B[j + p * nr];
			R[i * rs + j * cs] = alpha * s + beta * R[i * rs + j * cs];
		}
		UKR( m, n, k, &alpha, A, B, &beta, C, rs, cs, NULL, NULL );
		runs++;
		for ( int i = 0; i < LD * 2 * 160 + 64; i++ )
			if ( C[i] != R[i] ) { if ( bad < 4 ) printf( "st %d m %ld n %ld k %ld: C[%d]=%g want %g\n", st, m, n, k, i, (double)C[i], (double)R[i] ); bad++; break; }
	}
	printf( "mr %ld nr %ld: %d runs, %d wrong\n", mr, nr, runs, bad );
	return bad != 0;
}
