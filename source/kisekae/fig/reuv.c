// 棚の 貼り直し（shelf_reuv.py）の 手伝い
#include <math.h>
#include <stddef.h>
// 三角 ごとに「写真の カメラから 見える 点の 数」を 数える。S：nv×3（画面の x・y・深さ）・F：nf×3・zb：H×W（いちばん 手前の 深さ）→ tot・vis：nf
void vis_count(int nf, const double *S, const int *F, int W, int H, const float *zb, double eps, int *tot, int *vis) {
  for (int f = 0; f < nf; f++) {
    const double *p0 = S + 3 * F[3 * f], *p1 = S + 3 * F[3 * f + 1], *p2 = S + 3 * F[3 * f + 2];
    tot[f] = 0; vis[f] = 0;
    double den = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1]); if (fabs(den) < 1e-12) continue;
    int x0 = (int)floor(fmin(p0[0], fmin(p1[0], p2[0]))), x1 = (int)ceil(fmax(p0[0], fmax(p1[0], p2[0])));
    int y0 = (int)floor(fmin(p0[1], fmin(p1[1], p2[1]))), y1 = (int)ceil(fmax(p0[1], fmax(p1[1], p2[1])));
    if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > W - 1) x1 = W - 1; if (y1 > H - 1) y1 = H - 1;
    for (int py = y0; py <= y1; py++) for (int px = x0; px <= x1; px++) {
      double cx = px + 0.5, cy = py + 0.5;
      double w0 = ((p1[1] - p2[1]) * (cx - p2[0]) + (p2[0] - p1[0]) * (cy - p2[1])) / den, w1 = ((p2[1] - p0[1]) * (cx - p2[0]) + (p0[0] - p2[0]) * (cy - p2[1])) / den, w2 = 1 - w0 - w1;
      if (w0 < 0 || w1 < 0 || w2 < 0) continue;
      double z = w0 * p0[2] + w1 * p1[2] + w2 * p2[2]; tot[f]++;
      if (z <= zb[(size_t)py * W + px] + eps) vis[f]++;
    }
  }
}
// 画面に 三角を 塗る（いちばん 手前の 三角の 番号と 深さ）：zb は 大きい 数・id は −1 で はじめる
void idbuffer(int nf, const double *S, const int *F, int W, int H, float *zb, int *id) {
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
      if (z < zb[o]) { zb[o] = z; id[o] = f; }
    }
  }
}
// 絵の 上で 三角が 重なる 数：UV は 点の 単位（角ごと nf×3×2）・cnt：H×W（三角の 中に ある 点の 中心 ごとに ＋1・ふちは 数えない）
void cover_count(int nf, const double *UV, int W, int H, unsigned char *cnt) {
  for (int f = 0; f < nf; f++) {
    const double *q = UV + (size_t)f * 6; double x[3] = { q[0] - 0.5, q[2] - 0.5, q[4] - 0.5 }, y[3] = { q[1] - 0.5, q[3] - 0.5, q[5] - 0.5 };
    double den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2]); if (fabs(den) < 1e-9) continue;
    int x0 = (int)floor(fmin(x[0], fmin(x[1], x[2]))), x1 = (int)ceil(fmax(x[0], fmax(x[1], x[2])));
    int y0 = (int)floor(fmin(y[0], fmin(y[1], y[2]))), y1 = (int)ceil(fmax(y[0], fmax(y[1], y[2])));
    if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0; if (x1 > W - 1) x1 = W - 1; if (y1 > H - 1) y1 = H - 1;
    for (int py = y0; py <= y1; py++) for (int px = x0; px <= x1; px++) {
      double w0 = ((y[1] - y[2]) * (px - x[2]) + (x[2] - x[1]) * (py - y[2])) / den, w1 = ((y[2] - y[0]) * (px - x[2]) + (x[0] - x[2]) * (py - y[2])) / den, w2 = 1 - w0 - w1;
      const double e = 0.02; if (w0 < e || w1 < e || w2 < e) continue;
      size_t o = (size_t)py * W + px; if (cnt[o] < 255) cnt[o]++;
    }
  }
}
