#include <stdio.h>
#include <math.h>
#include <string.h>
#ifndef WT
#define WT double
#define NT double
#define TOL 1e-12
#endif
typedef WT w;
typedef NT h;
#include KERNEL_H
#define LDA 37
#define LDB 41
#ifndef LDC
#define LDC 43
#endif
#define KMAX 8
#define GUARD 8
/* columns of C the buffer holds (rows, row-major) */
#ifndef NCOLS
#define NCOLS 16
#endif
/* C column-major by default; row-major with C_ROW_MAJOR: C[m*LDC + n] */
#ifdef C_ROW_MAJOR
#define CI(m, n) ((m) * LDC + (n))
#define MMAX NCOLS
#define NMAX LDC
#else
#define CI(m, n) ((m) + (n) * LDC)
#define MMAX LDC
#define NMAX NCOLS
#endif
static h A[LDA * KMAX + 64], B[LDB * KMAX + 64];
static w Cbuf[LDC * NCOLS + 2 * GUARD], C0[LDC * NCOLS];
static w *C = Cbuf + GUARD;

static void call(long k, w alpha, w beta) {
    ukr(k, A, B, C, &alpha, &beta, LDA * sizeof(h), LDB * sizeof(h), LDC * sizeof(w));
}

int main(void) {
    /* footprint: A = B = 1, alpha 1, beta 0, k 1: the tile becomes 1 */
    for (int i = 0; i < LDA * KMAX; i++) A[i] = 1;
    for (int i = 0; i < LDB * KMAX; i++) B[i] = 1;
    for (int i = 0; i < LDC * NCOLS + 2 * GUARD; i++) Cbuf[i] = -7;
    call(1, 1.0, 0.0);
    int M = 0, N = 0;
    while (M < MMAX && C[CI(M, 0)] == 1) M++;
    while (N < NMAX && C[CI(0, N)] == 1) N++;
    printf("tile %d x %d\n", M, N);
    int bad = 0, tests = 0;
    w alphas[] = {1.0, 2.5}, betas[] = {0.0, -0.0, 1.0, -1.5};
    long ks[] = {0, 1, 2, 3, 4, 5, 7};
    for (int ki = 0; ki < 7; ki++) for (int ai = 0; ai < 2; ai++) for (int bi = 0; bi < 4; bi++) {
        long K = ks[ki]; w alpha = alphas[ai], beta = betas[bi];
        for (int i = 0; i < LDA * KMAX; i++) A[i] = (h)((i * 7) % 13 - 6);
        for (int i = 0; i < LDB * KMAX; i++) B[i] = (h)((i * 5) % 11 - 5);
        for (int i = 0; i < LDC * NCOLS + 2 * GUARD; i++) Cbuf[i] = -7;
        for (int n = 0; n < N; n++) for (int m = 0; m < M; m++)
            C[CI(m, n)] = beta == 0 ? NAN : (w)((m * 3 + n * 5) % 7 - 3);
        memcpy(C0, C, sizeof(C0));
        call(K, alpha, beta);
        tests++;
        for (int n = 0; n < N; n++) for (int m = 0; m < M; m++) {
            double ab = 0;
            for (long k = 0; k < K; k++) ab += (double)A[m + k * LDA] * (double)B[n + k * LDB];
            double want = (beta == 0 ? 0 : beta * C0[CI(m, n)]) + alpha * ab;
            double got = C[CI(m, n)];
            if (!(fabs(got - want) <= TOL * (1 + fabs(want)))) {
                if (bad < 6) printf("K=%ld alpha=%g beta=%g C[%d,%d] = %g, want %g\n", K, alpha, beta, m, n, got, want);
                bad++;
            }
        }
        for (int g = 0; g < GUARD; g++)
            if (Cbuf[g] != -7 || C[LDC * NCOLS + g] != -7) { if (bad < 6) printf("guard written\n"); bad++; }
        for (int n = 0; n < NMAX; n++) for (int m = 0; m < MMAX; m++)
            if ((m >= M || n >= N) && C[CI(m, n)] != -7) { if (bad < 6) printf("outside tile written C[%d,%d]\n", m, n); bad++; }
    }
    printf("%d runs, %d wrong\n", tests, bad);
    return bad != 0;
}
