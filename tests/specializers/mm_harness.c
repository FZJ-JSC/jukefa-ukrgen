#include <stdio.h>
#include <math.h>
#ifndef WT
#define WT double
#endif
typedef WT w;
void ukr(long k, const w* A, const w* B, w* C, long sCn);
#ifndef LDC
#define LDC 71
#endif
/* C column-major by default; row-major with C_ROW_MAJOR: C[m*LDC + n] */
#ifdef C_ROW_MAJOR
#define CI(m, n) ((m) * LDC + (n))
#define MMAX 64
#define NMAX LDC
#else
#define CI(m, n) ((m) + (n) * LDC)
#define MMAX LDC
#define NMAX 64
#endif
static w A[8192], B[8192], Cbuf[LDC * 64 + 128];
static w *C = Cbuf + 16;
int main(void) {
    for (int i = 0; i < 8192; i++) { A[i] = 1; B[i] = 1; }
    for (int i = 0; i < LDC * 64 + 128; i++) Cbuf[i] = -7;
    ukr(1, A, B, C, LDC * sizeof(w));
    int M = 0, N = 0;
    while (M < MMAX && C[CI(M, 0)] == 1) M++;
    while (N < NMAX && C[CI(0, N)] == 1) N++;
    printf("tile %d x %d\n", M, N);
    int bad = 0, runs = 0;
    for (long K = 0; K <= 7; K++) {
        for (int i = 0; i < 8192; i++) { A[i] = (w)((i * 7) % 13 - 6); B[i] = (w)((i * 5) % 11 - 5); }
        for (int i = 0; i < LDC * 64 + 128; i++) Cbuf[i] = -7;
        ukr(K, A, B, C, LDC * sizeof(w));
        runs++;
        for (int n = 0; n < N; n++) for (int m = 0; m < M; m++) {
            w want = 0;
            for (long k = 0; k < K; k++) want = fma(A[m + k * M], B[n + k * N], want);
            if (C[CI(m, n)] != want) { if (bad < 5) printf("K=%ld C[%d,%d]=%g want %g\n", K, m, n, C[CI(m, n)], want); bad++; }
        }
        for (int i = -16; i < LDC * 64 + 112; i++) {
#ifdef C_ROW_MAJOR
            int on = i >= 0 && i / LDC < M && i % LDC < N;
#else
            int on = i >= 0 && i % LDC < M && i / LDC < N;
#endif
            if (!on && Cbuf[i + 16] != -7) { if (bad < 5) printf("written at %d\n", i); bad++; break; }
        }
    }
    printf("%d runs, %d wrong\n", runs, bad);
    return bad != 0;
}
