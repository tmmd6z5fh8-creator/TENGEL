// raster.c — software triangle rasterizer producing a visibility buffer.
// Build: gcc -O3 -march=native -shared -fPIC -o libraster.so raster.c -lm
//
// rasterize(nv, xyzw, uv, nt, tri, tflag, tmat, nmat, atex, aw, ah, acut, W, H, depth, tid, bary, facing)
//   xyzw[nv*4]: screen x (px), screen y (px, down), z_ndc (smaller = nearer), inv_w (1/clip.w; 1 for ortho)
//   uv[nv*2]:   texcoords (only used for alpha-cutout materials; may be NULL if no alpha tex)
//   tri[nt*3], tflag[nt] (bit0: double sided), tmat[nt] (material id)
//   atex[nmat]: pointer to alpha texture (float, ah*aw, row-major, v down) or NULL; acut[nmat] cutoff
//   outputs (W*H): depth (init +inf), tid (init -1), bary[2] (persp-correct b1,b2), facing (1 front / -1 back)
// Front faces are counter-clockwise in NDC (glTF); with y flipped to screen they are clockwise, i.e. area < 0.
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

static inline float samp_alpha(const float *tex, int w, int h, float u, float v) {
    u = u - floorf(u); v = v - floorf(v);
    int x = (int)(u * w); int y = (int)(v * h);
    if (x >= w) x = w - 1; if (y >= h) y = h - 1; if (x < 0) x = 0; if (y < 0) y = 0;
    return tex[y * w + x];
}

void rasterize(int nv, const float *xyzw, const float *uv,
               int nt, const int32_t *tri, const int32_t *tflag, const int32_t *tmat,
               int nmat, const float **atex, const int32_t *aw, const int32_t *ah, const float *acut,
               int W, int H, float *depth, int32_t *tid, float *bary, int8_t *facing) {
    (void)nv; (void)nmat;
    for (int t = 0; t < nt; t++) {
        int i0 = tri[t * 3], i1 = tri[t * 3 + 1], i2 = tri[t * 3 + 2];
        const float *p0 = xyzw + i0 * 4, *p1 = xyzw + i1 * 4, *p2 = xyzw + i2 * 4;
        if (p0[3] <= 0 || p1[3] <= 0 || p2[3] <= 0) continue;      // behind camera (clip first in python)
        float x0 = p0[0], y0 = p0[1], x1 = p1[0], y1 = p1[1], x2 = p2[0], y2 = p2[1];
        float area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
        if (area == 0.f || !isfinite(area)) continue;
        int front = area < 0.f;
        int ds = tflag[t] & 1;
        if (!front && !ds) continue;
        int m = tmat[t];
        const float *at = (m >= 0 && atex) ? atex[m] : 0;
        float cut = at ? acut[m] : 0.f;
        int tw = at ? aw[m] : 0, th = at ? ah[m] : 0;
        float minx = fminf(x0, fminf(x1, x2)), maxx = fmaxf(x0, fmaxf(x1, x2));
        float miny = fminf(y0, fminf(y1, y2)), maxy = fmaxf(y0, fmaxf(y1, y2));
        int bx0 = (int)floorf(minx), bx1 = (int)ceilf(maxx), by0 = (int)floorf(miny), by1 = (int)ceilf(maxy);
        if (bx0 < 0) bx0 = 0; if (by0 < 0) by0 = 0; if (bx1 > W - 1) bx1 = W - 1; if (by1 > H - 1) by1 = H - 1;
        if (bx0 > bx1 || by0 > by1) continue;
        float inv = 1.f / area;
        float z0 = p0[2], z1 = p1[2], z2 = p2[2];
        float q0 = p0[3], q1 = p1[3], q2 = p2[3];
        // edge function increments: w0 = edge(p1,p2,p), w1 = edge(p2,p0,p), w2 = edge(p0,p1,p)
        float A0 = (y1 - y2), B0 = (x2 - x1);
        float A1 = (y2 - y0), B1 = (x0 - x2);
        float A2 = (y0 - y1), B2 = (x1 - x0);
        float sgn = area > 0 ? 1.f : -1.f;
        for (int py = by0; py <= by1; py++) {
            float fy = py + 0.5f;
            float fx = bx0 + 0.5f;
            float w0 = (x2 - x1) * (fy - y1) - (y2 - y1) * (fx - x1);
            float w1 = (x0 - x2) * (fy - y2) - (y0 - y2) * (fx - x2);
            float w2 = (x1 - x0) * (fy - y0) - (y1 - y0) * (fx - x0);
            // d/dx of edge(a,b,p) = -(b.y - a.y)
            float dw0 = -(y2 - y1), dw1 = -(y0 - y2), dw2 = -(y1 - y0);
            (void)A0; (void)B0; (void)A1; (void)B1; (void)A2; (void)B2;
            for (int px = bx0; px <= bx1; px++, w0 += dw0, w1 += dw1, w2 += dw2) {
                if (w0 * sgn < 0 || w1 * sgn < 0 || w2 * sgn < 0) continue;
                float l0 = w0 * inv, l1 = w1 * inv, l2 = w2 * inv;
                float z = l0 * z0 + l1 * z1 + l2 * z2;
                int idx = py * W + px;
                if (z >= depth[idx]) continue;
                float c0 = l0 * q0, c1 = l1 * q1, c2 = l2 * q2;
                float s = c0 + c1 + c2;
                if (s <= 0) continue;
                float b1 = c1 / s, b2 = c2 / s, b0 = 1.f - b1 - b2;
                if (at) {
                    float u = b0 * uv[i0 * 2] + b1 * uv[i1 * 2] + b2 * uv[i2 * 2];
                    float v = b0 * uv[i0 * 2 + 1] + b1 * uv[i1 * 2 + 1] + b2 * uv[i2 * 2 + 1];
                    if (samp_alpha(at, tw, th, u, v) < cut) continue;
                }
                depth[idx] = z;
                tid[idx] = t;
                bary[idx * 2] = b1; bary[idx * 2 + 1] = b2;
                facing[idx] = front ? 1 : -1;
            }
        }
    }
}

// depth-only pass (shadow maps): same inputs, no alpha test, no outputs but depth
void rasterize_depth(int nv, const float *xyzw, int nt, const int32_t *tri, int W, int H, float *depth) {
    (void)nv;
    for (int t = 0; t < nt; t++) {
        int i0 = tri[t * 3], i1 = tri[t * 3 + 1], i2 = tri[t * 3 + 2];
        const float *p0 = xyzw + i0 * 4, *p1 = xyzw + i1 * 4, *p2 = xyzw + i2 * 4;
        float x0 = p0[0], y0 = p0[1], x1 = p1[0], y1 = p1[1], x2 = p2[0], y2 = p2[1];
        float area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
        if (area == 0.f || !isfinite(area)) continue;
        float minx = fminf(x0, fminf(x1, x2)), maxx = fmaxf(x0, fmaxf(x1, x2));
        float miny = fminf(y0, fminf(y1, y2)), maxy = fmaxf(y0, fmaxf(y1, y2));
        int bx0 = (int)floorf(minx), bx1 = (int)ceilf(maxx), by0 = (int)floorf(miny), by1 = (int)ceilf(maxy);
        if (bx0 < 0) bx0 = 0; if (by0 < 0) by0 = 0; if (bx1 > W - 1) bx1 = W - 1; if (by1 > H - 1) by1 = H - 1;
        if (bx0 > bx1 || by0 > by1) continue;
        float inv = 1.f / area, sgn = area > 0 ? 1.f : -1.f;
        float z0 = p0[2], z1 = p1[2], z2 = p2[2];
        for (int py = by0; py <= by1; py++) {
            float fy = py + 0.5f, fx = bx0 + 0.5f;
            float w0 = (x2 - x1) * (fy - y1) - (y2 - y1) * (fx - x1);
            float w1 = (x0 - x2) * (fy - y2) - (y0 - y2) * (fx - x2);
            float w2 = (x1 - x0) * (fy - y0) - (y1 - y0) * (fx - x0);
            float dw0 = -(y2 - y1), dw1 = -(y0 - y2), dw2 = -(y1 - y0);
            for (int px = bx0; px <= bx1; px++, w0 += dw0, w1 += dw1, w2 += dw2) {
                if (w0 * sgn < 0 || w1 * sgn < 0 || w2 * sgn < 0) continue;
                float z = (w0 * z0 + w1 * z1 + w2 * z2) * inv;
                int idx = py * W + px;
                if (z < depth[idx]) depth[idx] = z;
            }
        }
    }
}
