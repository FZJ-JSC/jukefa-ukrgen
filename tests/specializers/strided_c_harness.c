#include <stdio.h>
#include <math.h>
typedef double w;
void ukr(long k, const w* A, const w* B, w* C, long sCm, long sCn);
#define LDM 3
#define LDN 101
static w A[4096], B[4096], Cbuf[LDN * 40 + 256];
static w *C = Cbuf + 16;
int main(void) {
    for (int i = 0; i < 4096; i++) { A[i] = 1; B[i] = 1; }
    for (int i = 0; i < LDN * 40 + 256; i++) Cbuf[i] = -7;
    ukr(1, A, B, C, LDM * sizeof(w), LDN * sizeof(w));
    int M = 0, N = 0;
    while (M < 33 && C[M * LDM] == 1) M++;
    while (N < 32 && C[N * LDN] == 1) N++;
    printf("tile %d x %d\n", M, N);
    int bad = 0, runs = 0;
    for (long K = 0; K <= 7; K++) {
        for (int i = 0; i < 4096; i++) { A[i] = (w)((i * 7) % 13 - 6); B[i] = (w)((i * 5) % 11 - 5); }
        for (int i = 0; i < LDN * 40 + 256; i++) Cbuf[i] = -7;
        ukr(K, A, B, C, LDM * sizeof(w), LDN * sizeof(w));
        runs++;
        for (int n = 0; n < N; n++) for (int m = 0; m < M; m++) {
            w want = 0;
            for (long k = 0; k < K; k++) want = fma(A[m + k * M], B[n + k * N], want);
            if (C[m * LDM + n * LDN] != want) { if (bad < 5) printf("K=%ld C[%d,%d]=%g want %g\n", K, m, n, C[m * LDM + n * LDN], want); bad++; }
        }
        /* nothing between the strided elements, nothing past the tile */
        for (int i = -16; i < LDN * 40 + 200; i++) {
            int on = i >= 0 && i % LDN < M * LDM && (i % LDN) % LDM == 0 && i / LDN < N;
            if (!on && Cbuf[i + 16] != -7) { if (bad < 5) printf("written at %d\n", i); bad++; break; }
        }
    }
    printf("%d runs, %d wrong\n", runs, bad);
    return bad != 0;
}
