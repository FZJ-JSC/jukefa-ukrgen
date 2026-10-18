#include <stdio.h>
#include <math.h>
typedef double w;
void ukr(long k, const w* A, const w* B, w* C, long sCn);
#define LDC 71
static w A[8192], B[8192], Cbuf[LDC * 64 + 128];
static w *C = Cbuf + 16;
int main(void) {
    for (int i = 0; i < 8192; i++) { A[i] = 1; B[i] = 1; }
    for (int i = 0; i < LDC * 64 + 128; i++) Cbuf[i] = -7;
    ukr(1, A, B, C, LDC * sizeof(w));
    int M = 0, N = 0;
    while (M < LDC && C[M] == 1) M++;
    while (N < 64 && C[N * LDC] == 1) N++;
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
            if (C[m + n * LDC] != want) { if (bad < 5) printf("K=%ld C[%d,%d]=%g want %g\n", K, m, n, C[m + n * LDC], want); bad++; }
        }
        for (int i = -16; i < LDC * 64 + 112; i++) {
            int on = i >= 0 && i % LDC < M && i / LDC < N;
            if (!on && Cbuf[i + 16] != -7) { if (bad < 5) printf("written at %d\n", i); bad++; break; }
        }
    }
    printf("%d runs, %d wrong\n", runs, bad);
    return bad != 0;
}
