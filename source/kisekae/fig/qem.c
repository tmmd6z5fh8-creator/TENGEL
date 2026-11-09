// 形を へらす（QEM・辺を 片方の 頂点へ たたむ）と UV の 上での 塗り（思い出フィギュア：kisekae/fig/fig_prep.py が ctypes で 使う）
//   qem_decimate：lock の 頂点（UV の 継ぎ目・ふち）は 動かさない → 元の UV と 絵が そのまま 使える
//   uv_raster：三角を UV の 上に 塗って、頂点の 値（3つ）を まぜて 絵に する（物の 向きの 法線を 焼く）
//   gcc -O2 -shared -fPIC -o libqem.so qem.c -lm
#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef struct { double c; int u, v, su, sv; } Ent;
typedef struct { Ent *a; int n, cap; } Heap;
static void hpush(Heap *h, Ent e) {
  if (h->n == h->cap) { h->cap = h->cap ? h->cap * 2 : 1024; h->a = (Ent *)realloc(h->a, sizeof(Ent) * h->cap); }
  int i = h->n++; while (i > 0) { int p = (i - 1) / 2; if (h->a[p].c <= e.c) break; h->a[i] = h->a[p]; i = p; } h->a[i] = e;
}
static Ent hpop(Heap *h) {
  Ent top = h->a[0], last = h->a[--h->n]; int i = 0;
  for (;;) { int l = 2 * i + 1, r = l + 1, m = i; double mc = last.c;
    if (l < h->n && h->a[l].c < mc) { m = l; mc = h->a[l].c; }
    if (r < h->n && h->a[r].c < mc) { m = r; }
    if (m == i) break; h->a[i] = h->a[m]; i = m; }
  if (h->n) h->a[i] = last; return top;
}
typedef struct { int *f; int n, cap; } List;
static void ladd(List *l, int x) { if (l->n == l->cap) { l->cap = l->cap ? l->cap * 2 : 8; l->f = (int *)realloc(l->f, sizeof(int) * l->cap); } l->f[l->n++] = x; }

static void fnormal(const double *V, int a, int b, int c, double *n, double *area) {
  const double *p = V + 3 * a, *q = V + 3 * b, *r = V + 3 * c;
  double e1[3] = {q[0] - p[0], q[1] - p[1], q[2] - p[2]}, e2[3] = {r[0] - p[0], r[1] - p[1], r[2] - p[2]};
  n[0] = e1[1] * e2[2] - e1[2] * e2[1]; n[1] = e1[2] * e2[0] - e1[0] * e2[2]; n[2] = e1[0] * e2[1] - e1[1] * e2[0];
  double l = sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]); *area = l * 0.5;
  if (l > 1e-300) { n[0] /= l; n[1] /= l; n[2] /= l; } else { n[0] = n[1] = 0; n[2] = 1; }
}
static double qcost(const double *Q, const double *p) {      // Q：10こ（対称 4×4 の 上半分）
  double x = p[0], y = p[1], z = p[2];
  return Q[0] * x * x + 2 * Q[1] * x * y + 2 * Q[2] * x * z + 2 * Q[3] * x + Q[4] * y * y + 2 * Q[5] * y * z + 2 * Q[6] * y + Q[7] * z * z + 2 * Q[8] * z + Q[9];
}

// V：nv×3・F：nf×3・lock：nv（1＝動かさない）・target：残す 三角の 数・outF：残った 三角（元の 頂点の 番号）。返り値＝残った 三角の 数
int qem_decimate(int nv, const double *V, int nf, const int *F0, const unsigned char *lock, int target, double maxcos, int *outF) {
  int *F = (int *)malloc(sizeof(int) * 3 * nf); memcpy(F, F0, sizeof(int) * 3 * nf);
  unsigned char *fdead = (unsigned char *)calloc(nf, 1), *vdead = (unsigned char *)calloc(nv, 1);
  int *stamp = (int *)calloc(nv, sizeof(int)), *mark = (int *)calloc(nv, sizeof(int)); int mk = 0;
  double *Q = (double *)calloc((size_t)nv * 10, sizeof(double));
  List *vf = (List *)calloc(nv, sizeof(List));
  for (int f = 0; f < nf; f++) {
    int a = F[3 * f], b = F[3 * f + 1], c = F[3 * f + 2]; double n[3], ar; fnormal(V, a, b, c, n, &ar);
    double d = -(n[0] * V[3 * a] + n[1] * V[3 * a + 1] + n[2] * V[3 * a + 2]);
    double q[10] = {n[0] * n[0], n[0] * n[1], n[0] * n[2], n[0] * d, n[1] * n[1], n[1] * n[2], n[1] * d, n[2] * n[2], n[2] * d, d * d};
    for (int k = 0; k < 3; k++) { int v = F[3 * f + k]; for (int j = 0; j < 10; j++) Q[10 * v + j] += q[j] * ar; ladd(&vf[v], f); }
  }
  Heap H = {0};
  #define PUSH(u_, v_) do { if (!lock[u_]) { double qq[10]; for (int j = 0; j < 10; j++) qq[j] = Q[10 * (u_) + j] + Q[10 * (v_) + j]; \
    Ent e = {qcost(qq, V + 3 * (v_)), (u_), (v_), stamp[u_], stamp[v_]}; hpush(&H, e); } } while (0)
  for (int f = 0; f < nf; f++) for (int k = 0; k < 3; k++) { int a = F[3 * f + k], b = F[3 * f + (k + 1) % 3]; PUSH(a, b); PUSH(b, a); }
  int alive = nf;
  while (alive > target && H.n) {
    Ent e = hpop(&H); int u = e.u, v = e.v;
    if (vdead[u] || vdead[v] || stamp[u] != e.su || stamp[v] != e.sv) continue;
    // 共通の 隣り（2つより 多いと ねじれる）
    mk++; int common = 0;
    for (int i = 0; i < vf[u].n; i++) { int f = vf[u].f[i]; if (fdead[f]) continue; for (int k = 0; k < 3; k++) mark[F[3 * f + k]] = mk; }
    for (int i = 0; i < vf[v].n; i++) { int f = vf[v].f[i]; if (fdead[f]) continue; for (int k = 0; k < 3; k++) { int w = F[3 * f + k]; if (w != u && w != v && mark[w] == mk) { mark[w] = -mk; common++; } } }
    if (common > 2) continue;
    // 面が うら返らないか
    int ok = 1;
    for (int i = 0; i < vf[u].n && ok; i++) {
      int f = vf[u].f[i]; if (fdead[f]) continue; int a = F[3 * f], b = F[3 * f + 1], c = F[3 * f + 2];
      if (a == v || b == v || c == v) continue;
      double n0[3], n1[3], ar0, ar1; fnormal(V, a, b, c, n0, &ar0);
      int a2 = a == u ? v : a, b2 = b == u ? v : b, c2 = c == u ? v : c; fnormal(V, a2, b2, c2, n1, &ar1);
      if (ar1 < ar0 * 1e-3 || n0[0] * n1[0] + n0[1] * n1[1] + n0[2] * n1[2] < maxcos) ok = 0;
    }
    if (!ok) continue;
    for (int i = 0; i < vf[u].n; i++) {
      int f = vf[u].f[i]; if (fdead[f]) continue; int *t = F + 3 * f;
      if (t[0] == v || t[1] == v || t[2] == v) { fdead[f] = 1; alive--; continue; }
      for (int k = 0; k < 3; k++) if (t[k] == u) t[k] = v;
      ladd(&vf[v], f);
    }
    vdead[u] = 1; stamp[u]++; stamp[v]++;
    for (int j = 0; j < 10; j++) Q[10 * v + j] += Q[10 * u + j];
    // v の まわりの 辺を 入れ直す
    for (int i = 0; i < vf[v].n; i++) { int f = vf[v].f[i]; if (fdead[f]) continue; for (int k = 0; k < 3; k++) { int w = F[3 * f + k]; if (w != v) { PUSH(v, w); PUSH(w, v); } } }
  }
  int n = 0; for (int f = 0; f < nf; f++) if (!fdead[f]) { memcpy(outF + 3 * n, F + 3 * f, sizeof(int) * 3); n++; }
  for (int i = 0; i < nv; i++) free(vf[i].f);
  free(vf); free(Q); free(F); free(fdead); free(vdead); free(stamp); free(mark); free(H.a);
  return n;
}

// UV の 上に 三角を 塗る：UV：nv×2（0〜1・上が v=0）・F：nf×3・A：nf×3×K（角ごとの 値）→ out：H×W×K・cov：H×W（塗れた ところ 1）
void uv_raster(int nf, const double *UV, const int *F, const double *A, int K, int W, int H, float *out, unsigned char *cov) {
  for (int f = 0; f < nf; f++) {
    double x[3], y[3];
    for (int k = 0; k < 3; k++) { x[k] = UV[2 * F[3 * f + k]] * W - 0.5; y[k] = UV[2 * F[3 * f + k] + 1] * H - 0.5; }
    double den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2]); if (fabs(den) < 1e-12) continue;
    int x0 = (int)floor(fmin(x[0], fmin(x[1], x[2]))), x1 = (int)ceil(fmax(x[0], fmax(x[1], x[2])));
    int y0 = (int)floor(fmin(y[0], fmin(y[1], y[2]))), y1 = (int)ceil(fmax(y[0], fmax(y[1], y[2])));
    if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > W - 1) x1 = W - 1; if (y1 > H - 1) y1 = H - 1;
    const double *a = A + (size_t)f * 3 * K;
    for (int py = y0; py <= y1; py++) for (int px = x0; px <= x1; px++) {
      double w0 = ((y[1] - y[2]) * (px - x[2]) + (x[2] - x[1]) * (py - y[2])) / den, w1 = ((y[2] - y[0]) * (px - x[2]) + (x[0] - x[2]) * (py - y[2])) / den, w2 = 1 - w0 - w1;
      const double e = -1e-4; if (w0 < e || w1 < e || w2 < e) continue;
      size_t o = (size_t)py * W + px;
      for (int k = 0; k < K; k++) out[o * K + k] = (float)(w0 * a[k] + w1 * a[K + k] + w2 * a[2 * K + k]);
      cov[o] = 1;
    }
  }
}

// 画面に 三角を 塗って いちばん 手前の 深さを 残す（棚の 写真の 見える／見えない）：S：nv×3（画面の x・y〈下向き〉・深さ）・F：nf×3 → zb：H×W（はじめに 大きい 数を 入れて おく）
void zbuffer(int nf, const double *S, const int *F, int W, int H, float *zb) {
  for (int f = 0; f < nf; f++) {
    const double *p0 = S + 3 * F[3 * f], *p1 = S + 3 * F[3 * f + 1], *p2 = S + 3 * F[3 * f + 2];
    double den = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1]); if (fabs(den) < 1e-12) continue;
    int x0 = (int)floor(fmin(p0[0], fmin(p1[0], p2[0]))), x1 = (int)ceil(fmax(p0[0], fmax(p1[0], p2[0])));
    int y0 = (int)floor(fmin(p0[1], fmin(p1[1], p2[1]))), y1 = (int)ceil(fmax(p0[1], fmax(p1[1], p2[1])));
    if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > W - 1) x1 = W - 1; if (y1 > H - 1) y1 = H - 1;
    for (int py = y0; py <= y1; py++) for (int px = x0; px <= x1; px++) {
      double cx = px + 0.5, cy = py + 0.5;
      double w0 = ((p1[1] - p2[1]) * (cx - p2[0]) + (p2[0] - p1[0]) * (cy - p2[1])) / den, w1 = ((p2[1] - p0[1]) * (cx - p2[0]) + (p0[0] - p2[0]) * (cy - p2[1])) / den, w2 = 1 - w0 - w1;
      if (w0 < 0 || w1 < 0 || w2 < 0) continue;
      float z = (float)(w0 * p0[2] + w1 * p1[2] + w2 * p2[2]); size_t o = (size_t)py * W + px;
      if (z < zb[o]) zb[o] = z;
    }
  }
}
