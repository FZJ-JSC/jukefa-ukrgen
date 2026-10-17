#include <stdio.h>
#include <math.h>
#include <string.h>
#include KERNEL_H
#define LDA 37
#define LDB 41
#define LDC 43
#define KMAX 8
#define GUARD 8
static double A[LDA * KMAX + 64], B[LDB * KMAX + 64], Cbuf[LDC * 16 + 2 * GUARD], C0[LDC * 16];
static double *C = Cbuf + GUARD;

static void call(long k, double alpha, double beta) {
    ukr(k, A, B, C, &alpha, &beta, LDA * 8, LDB * 8, LDC * 8);
}

int main(void) {
    /* footprint: A = B = 1, alpha 1, beta 0, k 1: the tile becomes 1 */
    for (int i = 0; i < LDA * KMAX; i++) A[i] = 1;
    for (int i = 0; i < LDB * KMAX; i++) B[i] = 1;
    for (int i = 0; i < LDC * 16 + 2 * GUARD; i++) Cbuf[i] = -7;
    call(1, 1.0, 0.0);
    int M = 0, N = 0;
    while (M < LDC && C[M] == 1) M++;
    while (N < 16 && C[N * LDC] == 1) N++;
    printf("tile %d x %d\n", M, N);
    int bad = 0, tests = 0;
    double alphas[] = {1.0, 2.5}, betas[] = {0.0, -0.0, 1.0, -1.5};
    long ks[] = {0, 1, 2, 3, 4, 5, 7};
    for (int ki = 0; ki < 7; ki++) for (int ai = 0; ai < 2; ai++) for (int bi = 0; bi < 4; bi++) {
        long K = ks[ki]; double alpha = alphas[ai], beta = betas[bi];
        for (int i = 0; i < LDA * KMAX; i++) A[i] = (double)((i * 7) % 13) - 6;
        for (int i = 0; i < LDB * KMAX; i++) B[i] = (double)((i * 5) % 11) - 5;
        for (int i = 0; i < LDC * 16 + 2 * GUARD; i++) Cbuf[i] = -7;
        for (int n = 0; n < N; n++) for (int m = 0; m < M; m++)
            C[m + n * LDC] = beta == 0 ? NAN : (double)((m * 3 + n * 5) % 7) - 3;
        memcpy(C0, C, sizeof(C0));
        call(K, alpha, beta);
        tests++;
        for (int n = 0; n < N; n++) for (int m = 0; m < M; m++) {
            double ab = 0;
            for (long k = 0; k < K; k++) ab += A[m + k * LDA] * B[n + k * LDB];
            double want = (beta == 0 ? 0 : beta * C0[m + n * LDC]) + alpha * ab;
            double got = C[m + n * LDC];
            if (!(fabs(got - want) <= 1e-12 * (1 + fabs(want)))) {
                if (bad < 6) printf("K=%ld alpha=%g beta=%g C[%d,%d] = %g, want %g\n", K, alpha, beta, m, n, got, want);
                bad++;
            }
        }
        for (int g = 0; g < GUARD; g++)
            if (Cbuf[g] != -7 || C[LDC * 16 + g] != -7) { if (bad < 6) printf("guard written\n"); bad++; }
        for (int n = 0; n < N; n++) for (int m = M; m < LDC; m++)
            if (C[m + n * LDC] != -7) { if (bad < 6) printf("outside tile written C[%d,%d]\n", m, n); bad++; }
    }
    printf("%d runs, %d wrong\n", tests, bad);
    return bad != 0;
}
