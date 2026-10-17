#include <stdio.h>
#include <math.h>
typedef _Float16 h;
void ukr(long k, const h* A, const h* B, float* C, long ldc_bytes);
#define LDC 37
static h A[4096], B[4096];
static float Cbuf[LDC * 32 + 64];
static float *C = Cbuf + 16;
int main(void) {
    for (int i = 0; i < 4096; i++) { A[i] = 1; B[i] = 1; }
    for (int i = 0; i < LDC * 32 + 64; i++) Cbuf[i] = -7;
    ukr(1, A, B, C, LDC * 4);
    int M = 0, N = 0;
    while (M < LDC && C[M] == 1) M++;
    while (N < 32 && C[N * LDC] == 1) N++;
    printf("tile %d x %d\n", M, N);
    int bad = 0, runs = 0;
    for (long K = 0; K <= 7; K++) {
        for (int i = 0; i < 4096; i++) { A[i] = (h)((i * 7) % 13 - 6); B[i] = (h)((i * 5) % 11 - 5); }
        for (int i = 0; i < LDC * 32 + 64; i++) Cbuf[i] = -7;
        ukr(K, A, B, C, LDC * 4);
        runs++;
        for (int n = 0; n < N; n++) for (int m = 0; m < M; m++) {
            float want = 0;
            for (long k = 0; k < K; k++) want = fmaf((float)A[m + k * M], (float)B[n + k * N], want);
            if (C[m + n * LDC] != want) { if (bad < 5) printf("K=%ld C[%d,%d]=%g want %g\n", K, m, n, C[m + n * LDC], want); bad++; }
        }
        for (int n = 0; n < N; n++) for (int m = M; m < LDC; m++)
            if (C[m + n * LDC] != -7) { if (bad < 5) printf("outside C[%d,%d]\n", m, n); bad++; }
    }
    printf("%d runs, %d wrong\n", runs, bad);
    return bad != 0;
}
