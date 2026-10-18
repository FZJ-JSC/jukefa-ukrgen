#include <stdio.h>
typedef double w;
void ukr(long n, const w* X, w* Y, const w* kappa, long ldx_bytes);
#define LDX 37
#define NMAX 9
static w X[LDX * NMAX + 64], Ybuf[64 * NMAX + 64];
static w *Y = Ybuf + 16;
int main(void) {
    for (int i = 0; i < LDX * NMAX + 64; i++) X[i] = 1;
    for (int i = 0; i < 64 * NMAX + 64; i++) Ybuf[i] = -7;
    w one = 1;
    ukr(1, X, Y, &one, LDX * sizeof(w));
    int M = 0;
    while (M < 64 && Y[M] == 1) M++;
    printf("panel %d\n", M);
    int bad = 0, runs = 0;
    w kappas[] = {1.0, -2.5};
    for (long N = 0; N <= 7; N++) for (int ki = 0; ki < 2; ki++) {
        for (int i = 0; i < LDX * NMAX + 64; i++) X[i] = (w)((i * 7) % 13) - 6;
        for (int i = 0; i < 64 * NMAX + 64; i++) Ybuf[i] = -7;
        ukr(N, X, Y, &kappas[ki], LDX * sizeof(w));
        runs++;
        for (long n = 0; n < N; n++) for (int m = 0; m < M; m++)
            if (Y[m + n * M] != kappas[ki] * X[m + n * LDX]) {
                if (bad < 5) printf("N=%ld Y[%d,%ld]=%g want %g\n", N, m, n, Y[m + n * M], kappas[ki] * X[m + n * LDX]);
                bad++;
            }
        for (int i = -16; i < 0; i++) if (Y[i] != -7) bad++;
        for (long i = N * M; i < 64 * NMAX + 48; i++) if (Y[i] != -7) { if (bad < 5) printf("written past Y[%ld]\n", i); bad++; break; }
    }
    printf("%d runs, %d wrong\n", runs, bad);
    return bad != 0;
}
