/* sdfr.c — 着せ替えの絵用の小さなSDFレイマーチャ（オリジナルの3D彫刻を描く）
   使い方: ./sdfr scene.txt
   scene.txt の行:
     img W H ss [x0 y0 x1 y1]          画像サイズ・スーパーサンプル・描く範囲
     cam ex ey ez tx ty tz fov          カメラ（縦の画角°）
     out prefix                          出力（prefix_rgb.f32 / _a / _d / _n / _m / _ao）
     amb r g b                           環境の底
     grad tr tg tb hr hg hb br bg bb     環境の上・地平・下の色
     lobe dx dy dz r g b sharp           環境の光のかたまり
     light dx dy dz r g b k shadow       平行光（k=影のやわらかさ）
     plight x y z r g b k shadow         点光源
     mat id type r g b rough a1 a2 a3    素材（type 0金属 1誘電体 2宝石）a1..a3は素材ごと
     bump id pattern scale amp [ox oy oz ax ay az rx ry rz rad]
     bounce n                            金属の映り込み回数（0/1）
     begin OP k mat / end                グループ
     sph OP k mat shell cx cy cz r
     ell OP k mat shell cx cy cz hx hy hz R9
     rcone OP k mat shell ax ay az bx by bz ra rb
     rbox OP k mat shell cx cy cz hx hy hz rnd R9
     torus OP k mat shell cx cy cz Rb rs R9
     ctorus OP k mat shell cx cy cz Rb rs half R9
     ccone OP k mat shell cx cy cz h r1 r2 rnd R9
     tex id W H path                     2Dの 距離の 絵（float32・W×H・単位は 画素・中が マイナス）：字の 形など
     glyph OP k mat shell cx cy cz sx hz bev texid R9 [dome domew]   2Dの 距離の 絵を 厚み 2hz で のばした 形（sx＝1画素の 長さ・bev＝ふちの 面取り 45°・
                                         dome＝ふちから domew の 間で 前の 面が ふくらむ 高さ）
   OP: U（なめらか結合）/ S（引く）/ I（交わり）  R9 = 世界→ローカルの回転（行）
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef struct { float x, y, z; } v3;
static inline v3 v(float x, float y, float z) { v3 r = {x, y, z}; return r; }
static inline v3 vadd(v3 a, v3 b) { return v(a.x + b.x, a.y + b.y, a.z + b.z); }
static inline v3 vsub(v3 a, v3 b) { return v(a.x - b.x, a.y - b.y, a.z - b.z); }
static inline v3 vmul(v3 a, float s) { return v(a.x * s, a.y * s, a.z * s); }
static inline v3 vmulv(v3 a, v3 b) { return v(a.x * b.x, a.y * b.y, a.z * b.z); }
static inline float dot(v3 a, v3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline float len(v3 a) { return sqrtf(dot(a, a)); }
static inline v3 norm(v3 a) { float l = len(a); return l > 1e-20f ? vmul(a, 1.0f / l) : a; }
static inline v3 cross(v3 a, v3 b) { return v(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x); }
static inline float clampf(float x, float a, float b) { return x < a ? a : (x > b ? b : x); }
static inline float mixf(float a, float b, float t) { return a + (b - a) * t; }
static inline v3 vmix(v3 a, v3 b, float t) { return v(mixf(a.x, b.x, t), mixf(a.y, b.y, t), mixf(a.z, b.z, t)); }
static inline float sminf(float a, float b, float k) {
    if (k <= 0.f) return a < b ? a : b;
    float h = fmaxf(k - fabsf(a - b), 0.0f) / k;
    return fminf(a, b) - h * h * k * 0.25f;
}
static inline float smaxf(float a, float b, float k) { return -sminf(-a, -b, k); }
static inline float smoothstepf(float a, float b, float x) { float t = clampf((x - a) / (b - a), 0.f, 1.f); return t * t * (3.f - 2.f * t); }

enum { T_SPH, T_ELL, T_RCONE, T_RBOX, T_TORUS, T_CTORUS, T_CCONE, T_GLYPH };
typedef struct { int W, H; float *d; } Tex;
static Tex texs[32];
enum { O_U, O_S, O_I };

typedef struct {
    int type, op, mat;
    float k, shell;
    v3 c, b, h;
    float r1, r2, rnd, half;
    float R[9];
    v3 bc; float br;
} Prim;

typedef struct { int first, count, op, mat; float k; v3 bc; float br; } Group;
typedef struct { int is_group, idx; } Item;

#define MAXP 20000
static Prim prims[MAXP]; static int nprims = 0;
static Group groups[4000]; static int ngroups = 0;
static Item items[MAXP]; static int nitems = 0;

typedef struct { int type; v3 col; float rough, a1, a2, a3; int bump; float bscale, bamp; v3 bo, ba, br; float brad; } Mat;
static Mat mats[64];

typedef struct { int point; v3 d; v3 col; float k; int shadow; } Light;
static Light lights[16]; static int nlights = 0;
typedef struct { v3 d, col; float sharp; } Lobe;
static Lobe lobes[64]; static int nlobes = 0;
static v3 amb = {0, 0, 0}, gtop = {0, 0, 0}, ghor = {0, 0, 0}, gbot = {0, 0, 0};
static int bounce = 1;
static float cullm = 0.f; static int nocull = 0;

static inline v3 rot(const float *R, v3 p) {
    return v(R[0] * p.x + R[1] * p.y + R[2] * p.z, R[3] * p.x + R[4] * p.y + R[5] * p.z, R[6] * p.x + R[7] * p.y + R[8] * p.z);
}
static inline float dot2(v3 a) { return dot(a, a); }

static float sdRoundCone(v3 p, v3 a, v3 b, float r1, float r2) {
    v3 ba = vsub(b, a);
    float l2 = dot(ba, ba);
    float rr = r1 - r2;
    float a2 = l2 - rr * rr;
    float il2 = 1.0f / l2;
    v3 pa = vsub(p, a);
    float y = dot(pa, ba);
    float z = y - l2;
    float x2 = dot2(vsub(vmul(pa, l2), vmul(ba, y)));
    float y2 = y * y * l2;
    float z2 = z * z * l2;
    float k = (rr > 0 ? 1.f : (rr < 0 ? -1.f : 0.f)) * rr * rr * x2;
    if ((z > 0 ? 1.f : -1.f) * a2 * z2 > k) return sqrtf(x2 + z2) * il2 - r2;
    if ((y > 0 ? 1.f : -1.f) * a2 * y2 < k) return sqrtf(x2 + y2) * il2 - r1;
    return (sqrtf(fmaxf(x2 * a2 * il2, 0.f)) + y * rr) * il2 - r1;
}

static inline float prim_d(const Prim *P, v3 p) {
    float d;
    switch (P->type) {
    case T_SPH: d = len(vsub(p, P->c)) - P->r1; break;
    case T_ELL: {
        v3 q = rot(P->R, vsub(p, P->c));
        float k0 = len(v(q.x / P->h.x, q.y / P->h.y, q.z / P->h.z));
        float k1 = len(v(q.x / (P->h.x * P->h.x), q.y / (P->h.y * P->h.y), q.z / (P->h.z * P->h.z)));
        d = k1 > 1e-12f ? k0 * (k0 - 1.0f) / k1 : -fminf(P->h.x, fminf(P->h.y, P->h.z));
        /* 外接球までの距離より小さくしない（近似のずれで影の線が出るのを防ぐ） */
        d = fmaxf(d, len(vsub(p, P->c)) - (P->br - P->shell));
    } break;
    case T_RCONE: d = sdRoundCone(p, P->c, P->b, P->r1, P->r2); break;
    case T_RBOX: {
        v3 q = rot(P->R, vsub(p, P->c));
        v3 e = v(fabsf(q.x) - (P->h.x - P->rnd), fabsf(q.y) - (P->h.y - P->rnd), fabsf(q.z) - (P->h.z - P->rnd));
        v3 m = v(fmaxf(e.x, 0), fmaxf(e.y, 0), fmaxf(e.z, 0));
        d = len(m) + fminf(fmaxf(e.x, fmaxf(e.y, e.z)), 0.f) - P->rnd;
    } break;
    case T_TORUS: {
        v3 q = rot(P->R, vsub(p, P->c));
        float qx = sqrtf(q.x * q.x + q.z * q.z) - P->r1;
        d = sqrtf(qx * qx + q.y * q.y) - P->r2;
    } break;
    case T_CTORUS: {
        v3 q = rot(P->R, vsub(p, P->c));
        float sx = sinf(P->half), sy = cosf(P->half);
        q.x = fabsf(q.x);
        float kk = (sy * q.x > sx * q.y) ? (q.x * sx + q.y * sy) : sqrtf(q.x * q.x + q.y * q.y);
        d = sqrtf(fmaxf(dot(q, q) + P->r1 * P->r1 - 2.0f * P->r1 * kk, 0.f)) - P->r2;
    } break;
    case T_CCONE: {
        v3 q3 = rot(P->R, vsub(p, P->c));
        float h = P->h.x, r1 = P->r1 - P->rnd, r2 = P->r2 - P->rnd;
        float qx = sqrtf(q3.x * q3.x + q3.z * q3.z), qy = q3.y;
        float k1x = r2, k1y = h, k2x = r2 - r1, k2y = 2.0f * h;
        float cax = qx - ((qy < 0.0f) ? r1 : r2), cay = fabsf(qy) - h;
        float tt = clampf(((k1x - qx) * k2x + (k1y - qy) * k2y) / (k2x * k2x + k2y * k2y), 0.f, 1.f);
        float cbx = qx - k1x + k2x * tt, cby = qy - k1y + k2y * tt;
        float s = (cbx < 0.0f && cay < 0.0f) ? -1.0f : 1.0f;
        d = s * sqrtf(fminf(cax * cax + cay * cay, cbx * cbx + cby * cby)) - P->rnd;
    } break;
    case T_GLYPH: {
        /* 2Dの 距離の 絵（字）を のばして 面取り：ローカルの x・y が 絵の 面（y は 上向き）、z が 厚み */
        v3 q = rot(P->R, vsub(p, P->c));
        const Tex *T = &texs[(int)P->r1];
        float sx = P->h.x, hz = P->h.y, bev = P->h.z;
        float u = q.x / sx + T->W * 0.5f, vv = -q.y / sx + T->H * 0.5f;
        float cu = clampf(u, 0.5f, T->W - 0.5f), cv = clampf(vv, 0.5f, T->H - 0.5f);
        float outd = sqrtf((u - cu) * (u - cu) + (vv - cv) * (vv - cv));
        float fu = cu - 0.5f, fv = cv - 0.5f;
        int iu = (int)fu, iv = (int)fv;
        if (iu > T->W - 2) iu = T->W - 2; if (iv > T->H - 2) iv = T->H - 2;
        if (iu < 0) iu = 0; if (iv < 0) iv = 0;
        float tu = fu - iu, tv = fv - iv;
        const float *r0 = T->d + (size_t)iv * T->W + iu, *r1 = r0 + T->W;
        float sd = mixf(mixf(r0[0], r0[1], tu), mixf(r1[0], r1[1], tu), tv);
        float d2 = (sd + outd) * sx;
        float hze = hz;
        if (P->b.x > 0.f && d2 < 0.f) { float tt = clampf(-d2 / P->b.y, 0.f, 1.f); hze += P->b.x * tt * (2.f - tt); }   /* ふちから 中へ ふくらむ */
        float dz = fabsf(q.z) - hze;
        d = fmaxf(fmaxf(d2, dz), (d2 + dz + bev) * 0.70710678f);
        if (P->b.x > 0.f) d *= 0.85f;
    } break;
    default: d = 1e9f;
    }
    if (P->shell > 0.f) d = fabsf(d) - P->shell;
    return d;
}

static float group_d(const Group *G, v3 p) {
    float acc = 1e9f;
    for (int i = 0; i < G->count; i++) {
        const Prim *P = &prims[G->first + i];
        if (!nocull && i > 0 && P->op == O_U) {
            float bd = len(vsub(p, P->bc)) - P->br - cullm * P->br;
            if (bd > acc + P->k) continue;
        }
        if (!nocull && i > 0 && P->op == O_S) {
            float bd = len(vsub(p, P->bc)) - P->br - cullm * P->br;
            if (bd >= P->k - acc) continue;
        }
        float d = prim_d(P, p);
        if (i == 0) { acc = d; continue; }
        if (P->op == O_U) acc = sminf(acc, d, P->k);
        else if (P->op == O_S) acc = smaxf(acc, -d, P->k);
        else acc = smaxf(acc, d, P->k);
    }
    return acc;
}

static float map(v3 p, int *mat) {
    float acc = 1e9f; int m = -1;
    for (int i = 0; i < nitems; i++) {
        int op, imat; float k; v3 bc; float br;
        if (items[i].is_group) { Group *G = &groups[items[i].idx]; op = G->op; k = G->k; bc = G->bc; br = G->br; imat = G->mat; }
        else { Prim *P = &prims[items[i].idx]; op = P->op; k = P->k; bc = P->bc; br = P->br; imat = P->mat; }
        float bd = len(vsub(p, bc)) - br - cullm * br;
        if (!nocull) {
            if (op == O_U) { if (bd > acc + k) continue; }
            else if (op == O_S) { if (bd >= k - acc) continue; }
        }
        float d = items[i].is_group ? group_d(&groups[items[i].idx], p) : prim_d(&prims[items[i].idx], p);
        if (op == O_U) { if (d < acc) m = imat; acc = sminf(acc, d, k); }
        else if (op == O_S) acc = smaxf(acc, -d, k);
        else acc = smaxf(acc, d, k);
    }
    if (mat) *mat = m;
    return acc;
}

/* ---------- ノイズ ---------- */
static inline float hash3i(int x, int y, int z) {
    unsigned h = (unsigned)x * 374761393u + (unsigned)y * 668265263u + (unsigned)z * 2246822519u;
    h = (h ^ (h >> 13)) * 1274126177u; h ^= h >> 16;
    return (h & 0xffffff) / 16777215.0f;
}
static float vnoise(v3 p) {
    float fx = floorf(p.x), fy = floorf(p.y), fz = floorf(p.z);
    int ix = (int)fx, iy = (int)fy, iz = (int)fz;
    float ux = p.x - fx, uy = p.y - fy, uz = p.z - fz;
    ux = ux * ux * (3 - 2 * ux); uy = uy * uy * (3 - 2 * uy); uz = uz * uz * (3 - 2 * uz);
    float a = hash3i(ix, iy, iz), b = hash3i(ix + 1, iy, iz), c = hash3i(ix, iy + 1, iz), d = hash3i(ix + 1, iy + 1, iz);
    float e = hash3i(ix, iy, iz + 1), f = hash3i(ix + 1, iy, iz + 1), g = hash3i(ix, iy + 1, iz + 1), h = hash3i(ix + 1, iy + 1, iz + 1);
    float x1 = mixf(mixf(a, b, ux), mixf(c, d, ux), uy);
    float x2 = mixf(mixf(e, f, ux), mixf(g, h, ux), uy);
    return mixf(x1, x2, uz);
}
static float fbm3(v3 p, int oct) {
    float s = 0, a = 0.5f, n = 0;
    for (int i = 0; i < oct; i++) { s += a * vnoise(p); n += a; a *= 0.5f; p = vmul(v(p.y * 1.7f + 3.1f, p.z * 1.7f - 1.3f, p.x * 1.7f + 7.7f), 1.18f); }
    return s / n;
}

/* 凸凹の高さ（模様） */
static float bump_h(const Mat *M, v3 p) {
    switch (M->bump) {
    case 1: return fbm3(vmul(p, M->bscale), 4);
    case 2: { /* うろこ：軸にそった円筒座標 */
        v3 q = vsub(p, M->bo);
        float u = dot(q, M->ba);
        v3 qp = vsub(q, vmul(M->ba, u));
        v3 bb = cross(M->ba, M->br);
        float ang = atan2f(dot(qp, bb), dot(qp, M->br));
        float vv = ang * M->brad;
        float s = M->bscale;
        int j0 = (int)floorf(u / s);
        float best = 0.f; int bestj = -100000;
        for (int j = j0 - 1; j <= j0 + 1; j++) {
            float off = (j & 1) ? 0.5f : 0.f;
            int i0 = (int)floorf(vv / s - off);
            for (int i = i0 - 1; i <= i0 + 1; i++) {
                float cu = (j + 0.5f) * s, cv = (i + 0.5f + off) * s;
                float du = (u - cu) / (0.78f * s), dv = (vv - cv) / (0.62f * s);
                float dd = du * du + dv * dv;
                if (dd < 1.f && j > bestj) { bestj = j; best = sqrtf(1.f - dd) * (0.55f + 0.45f * clampf(du + 1.f, 0.f, 1.f)); }
                else if (dd < 1.f && j == bestj) { float hh = sqrtf(1.f - dd) * (0.55f + 0.45f * clampf(du + 1.f, 0.f, 1.f)); if (hh > best) best = hh; }
            }
        }
        return best;
    }
    case 3: { /* 彫り模様：うねる線 */
        float n = fbm3(vmul(p, M->bscale), 3);
        float l = 1.f - smoothstepf(0.f, 0.035f, fabsf(n - 0.5f));
        float n2 = fbm3(vadd(vmul(p, M->bscale * 1.9f), v(5.2f, 1.3f, 2.8f)), 3);
        float l2 = 1.f - smoothstepf(0.f, 0.03f, fabsf(n2 - 0.5f));
        return fmaxf(l, l2 * 0.7f) + fbm3(vmul(p, M->bscale * 6.f), 2) * 0.15f;
    }
    case 4: { /* 毛並み：体にそった細い筋＋ゆるい凹凸 */
        v3 q = vmul(p, M->bscale);
        float s1 = sinf(dot(q, M->ba) * 9.0f + fbm3(vmul(q, 0.6f), 3) * 9.f) * 0.5f + 0.5f;
        return s1 * 0.25f + fbm3(vmul(q, 0.35f), 3);
    }
    }
    return 0.f;
}

static v3 apply_bump(const Mat *M, v3 p, v3 n) {
    if (!M->bump || M->bamp == 0.f) return n;
    float e = 0.0015f;
    if (M->bump == 1 || M->bump == 3 || M->bump == 4) e = 0.15f / M->bscale;
    if (M->bump == 2) e = M->bscale * 0.04f;
    float h0 = bump_h(M, p);
    v3 g = v((bump_h(M, vadd(p, v(e, 0, 0))) - h0) / e, (bump_h(M, vadd(p, v(0, e, 0))) - h0) / e, (bump_h(M, vadd(p, v(0, 0, e))) - h0) / e);
    g = vsub(g, vmul(n, dot(g, n)));
    return norm(vsub(n, vmul(g, M->bamp)));
}

/* ---------- 環境・光 ---------- */
static v3 env(v3 d) {
    v3 c;
    if (d.y >= 0) c = vmix(ghor, gtop, powf(d.y, 0.6f));
    else c = vmix(ghor, gbot, powf(-d.y, 0.6f));
    c = vadd(c, amb);
    for (int i = 0; i < nlobes; i++) {
        float t = dot(d, lobes[i].d);
        if (t > 0) c = vadd(c, vmul(lobes[i].col, powf(t, lobes[i].sharp)));
    }
    return c;
}

static float softshadow(v3 ro, v3 rd, float mint, float maxt, float k) {
    float res = 1.0f, t = mint, ph = 1e10f;
    for (int i = 0; i < 96 && t < maxt; i++) {
        float h = map(vadd(ro, vmul(rd, t)), 0);
        if (h < 0.0004f) return 0.f;
        float y = h * h / (2.0f * ph);
        float d = sqrtf(fmaxf(h * h - y * y, 0.f));
        res = fminf(res, k * d / fmaxf(0.0f, t - y));
        ph = h;
        t += clampf(h, 0.004f, 0.25f);
    }
    return clampf(res, 0.f, 1.f);
}

static float calcAO(v3 p, v3 n) {
    float occ = 0.f, sca = 1.f;
    for (int i = 0; i < 6; i++) {
        float h = 0.006f + 0.16f * i / 5.0f;
        float d = map(vadd(p, vmul(n, h)), 0);
        occ += (h - d) * sca;
        sca *= 0.9f;
    }
    return clampf(1.0f - 2.6f * occ, 0.f, 1.f);
}

static v3 calcNormal(v3 p, float eps) {
    v3 k1 = v(1, -1, -1), k2 = v(-1, -1, 1), k3 = v(-1, 1, -1), k4 = v(1, 1, 1);
    v3 n = vadd(vadd(vmul(k1, map(vadd(p, vmul(k1, eps)), 0)), vmul(k2, map(vadd(p, vmul(k2, eps)), 0))),
                vadd(vmul(k3, map(vadd(p, vmul(k3, eps)), 0)), vmul(k4, map(vadd(p, vmul(k4, eps)), 0))));
    return norm(n);
}

static v3 sceneC; static float sceneR;

static float march(v3 ro, v3 rd, float tmin, float tmax, int *mat) {
    /* シーン全体の球との交差 */
    v3 oc = vsub(ro, sceneC);
    float b = dot(oc, rd), c = dot(oc, oc) - sceneR * sceneR, h = b * b - c;
    if (h < 0) return -1.f;
    h = sqrtf(h);
    float t0 = -b - h, t1 = -b + h;
    float t = fmaxf(tmin, t0);
    tmax = fminf(tmax, t1);
    for (int i = 0; i < 400; i++) {
        if (t > tmax) break;
        v3 p = vadd(ro, vmul(rd, t));
        float d = map(p, mat);
        if (d < 0.00035f * t) return t;
        t += d * 0.8f;
    }
    return -1.f;
}

static inline v3 schlick(v3 F0, float c) {
    float f = powf(1.0f - clampf(c, 0.f, 1.f), 5.0f);
    return v(F0.x + (1 - F0.x) * f, F0.y + (1 - F0.y) * f, F0.z + (1 - F0.z) * f);
}
static inline float ggx(float NdotH, float NdotV, float NdotL, float rough) {
    float a = rough * rough, a2 = a * a;
    float dn = NdotH * NdotH * (a2 - 1.0f) + 1.0f;
    float D = a2 / (3.14159f * dn * dn);
    float gv = 2.f * NdotV / (NdotV + sqrtf(a2 + (1 - a2) * NdotV * NdotV));
    float gl = 2.f * NdotL / (NdotL + sqrtf(a2 + (1 - a2) * NdotL * NdotL));
    return D * gv * gl / (4.f * fmaxf(NdotV, 1e-3f));
}

static v3 refl(v3 i, v3 n) { return vsub(i, vmul(n, 2.f * dot(i, n))); }

static unsigned rng_state_dummy;
static inline float frand(unsigned *s) { *s = *s * 1664525u + 1013904223u; return ((*s >> 8) & 0xffffff) / 16777216.0f; }

static v3 env_rough(v3 R, float rough, unsigned *seed) {
    if (rough < 0.06f) return env(R);
    v3 up = fabsf(R.y) < 0.9f ? v(0, 1, 0) : v(1, 0, 0);
    v3 t1 = norm(cross(up, R)), t2 = cross(R, t1);
    v3 acc = v(0, 0, 0);
    int S = 16;
    /* 決まった並び（黄金角のうずまき）でむらのない ぼかし */
    for (int i = 0; i < S; i++) {
        float a = i * 2.39996f, r = sqrtf((i + 0.5f) / S) * rough * rough * 1.6f;
        v3 d = norm(vadd(R, vadd(vmul(t1, cosf(a) * r), vmul(t2, sinf(a) * r))));
        acc = vadd(acc, env(d));
    }
    (void)seed;
    return vmul(acc, 1.0f / S);
}

static v3 shade(v3 p, v3 rd, v3 n, int mid, int depth, unsigned *seed, float *ao_out);

static v3 trace_refl(v3 p, v3 n, v3 R, float rough, int depth, unsigned *seed) {
    if (depth >= bounce) return env_rough(R, rough, seed);
    int m;
    float t = march(vadd(p, vmul(n, 0.003f)), R, 0.002f, 4.0f, &m);
    if (t < 0) return env_rough(R, rough, seed);
    v3 q = vadd(vadd(p, vmul(n, 0.003f)), vmul(R, t));
    v3 nq = calcNormal(q, 0.0012f);
    float dummy;
    return shade(q, R, nq, m, depth + 1, seed, &dummy);
}

static v3 shade(v3 p, v3 rd, v3 n0, int mid, int depth, unsigned *seed, float *ao_out) {
    Mat *M = &mats[mid < 0 ? 0 : mid];
    v3 n = apply_bump(M, p, n0);
    v3 V = vmul(rd, -1.f);
    float NdotV = fmaxf(dot(n, V), 1e-3f);
    float ao = calcAO(p, n0);
    *ao_out = ao;
    v3 col = v(0, 0, 0);
    float rough = M->rough;
    if (M->type == 0 && M->a3 > 0.f) rough = clampf(rough + (fbm3(vmul(p, M->a3), 3) - 0.5f) * 0.18f, 0.04f, 1.f);
    v3 F0 = M->col;
    if (M->type != 0) F0 = v(0.04f, 0.04f, 0.04f);
    if (M->type == 2) F0 = v(0.08f, 0.08f, 0.08f);
    for (int i = 0; i < nlights; i++) {
        Light *L = &lights[i];
        v3 Ld; v3 lc = L->col;
        float maxt = 6.f;
        if (L->point) {
            v3 dl = vsub(L->d, p); float dd = len(dl); Ld = vmul(dl, 1.f / dd); maxt = dd;
            lc = vmul(lc, 1.0f / (dd * dd));
        } else Ld = L->d;
        float NdotL = dot(n, Ld);
        if (NdotL <= 0.f && M->type != 1) continue;
        float sh = 1.f;
        if (L->shadow && depth == 0 && dot(n0, Ld) > -0.1f) sh = softshadow(vadd(p, vmul(n0, 0.002f)), Ld, 0.004f, maxt, L->k);
        if (sh <= 0.f) continue;
        v3 H = norm(vadd(Ld, V));
        float NdotH = fmaxf(dot(n, H), 0.f), VdotH = fmaxf(dot(V, H), 0.f);
        float nl = fmaxf(NdotL, 0.f);
        if (nl > 0.f) {
            float rr = M->type == 2 ? 0.05f : rough;
            float s = ggx(NdotH, NdotV, nl, rr) * nl;
            v3 F = schlick(F0, VdotH);
            col = vadd(col, vmulv(vmul(F, s * sh), lc));
        }
        if (M->type == 1) {
            /* 拡散（毛の黒）＋ うしろからの光の縁（シーン） */
            col = vadd(col, vmul(vmulv(M->col, lc), nl * sh * 0.318f));
            float rim = powf(1.f - NdotV, M->a3 > 0.f ? M->a3 : 3.0f) * fmaxf(dot(Ld, rd), 0.f) * smoothstepf(-0.25f, 0.55f, dot(n, Ld));
            col = vadd(col, vmul(lc, rim * M->a1 * sh));
        }
    }
    v3 R = refl(rd, n);
    if (M->type == 0) {
        v3 F = schlick(F0, NdotV);
        v3 rc = trace_refl(p, n0, R, rough, depth, seed);
        float so = clampf(ao * 1.2f, 0.f, 1.f);
        col = vadd(col, vmul(vmulv(F, rc), so));
    } else if (M->type == 1) {
        v3 F = schlick(F0, NdotV);
        v3 rc = (depth == 0 && M->rough < 0.25f) ? trace_refl(p, n0, R, M->rough, depth, seed) : env_rough(R, fmaxf(M->rough, 0.1f), seed);
        col = vadd(col, vmul(vmulv(F, rc), ao));
        /* 拡散の環境光 */
        v3 irr = vmul(vadd(vadd(env(n), env(norm(vadd(n, v(0, 0.6f, 0))))), env(norm(vadd(n, v(0, -0.6f, 0))))), 1.f / 3.f);
        col = vadd(col, vmul(vmulv(M->col, irr), ao));
        /* 布のような縁の光（環境から） */
        if (M->a2 > 0.f) {
            v3 back = env(norm(vadd(rd, vmul(n, -0.35f))));
            col = vadd(col, vmul(back, powf(1.f - NdotV, M->a3 > 0.f ? M->a3 + 1.f : 4.f) * M->a2 * ao));
        }
    } else if (M->type == 3) {
        /* 大理石：白い地に灰色のすじ（a1=すじの細かさ a2=うねり） */
        v3 q = vmul(p, M->a1 > 0 ? M->a1 : 3.0f);
        float w = sinf(q.x * 1.3f + q.y * 0.7f + q.z * 0.9f + fbm3(vmul(q, 0.9f), 5) * (M->a2 > 0 ? M->a2 : 9.0f));
        float vein = powf(1.f - fabsf(w), 7.0f) * 0.75f + powf(1.f - fabsf(w), 40.0f) * 0.25f;
        float mott = fbm3(vmul(q, 2.5f), 3);
        v3 alb = vmul(M->col, 0.92f + 0.10f * mott);
        alb = vmix(alb, vmul(M->col, 0.62f), clampf(vein, 0.f, 1.f));
        v3 F = schlick(v(0.04f, 0.04f, 0.04f), NdotV);
        v3 rc = (depth == 0) ? trace_refl(p, n0, R, M->rough, depth, seed) : env_rough(R, fmaxf(M->rough, 0.1f), seed);
        col = vadd(col, vmul(vmulv(F, rc), ao));
        v3 irr = vmul(vadd(vadd(env(n), env(norm(vadd(n, v(0, 0.6f, 0))))), env(norm(vadd(n, v(0, -0.6f, 0))))), 1.f / 3.f);
        col = vadd(col, vmul(vmulv(alb, irr), ao));
        for (int i = 0; i < nlights; i++) {
            Light *L = &lights[i];
            v3 Ld = L->point ? norm(vsub(L->d, p)) : L->d;
            float nl = fmaxf(dot(n, Ld), 0.f);
            if (nl <= 0.f) continue;
            float sh = 1.f;
            if (L->shadow && depth == 0) sh = softshadow(vadd(p, vmul(n0, 0.002f)), Ld, 0.004f, 6.f, L->k);
            /* うすい光のにじみ（大理石の中を通る光） */
            float wrap = clampf((dot(n, Ld) + 0.35f) / 1.35f, 0.f, 1.f);
            col = vadd(col, vmul(vmulv(alb, L->col), (nl * 0.85f + wrap * 0.15f) * sh * 0.318f));
        }
    } else if (M->type == 2) {
        /* カットした宝石：法線を面ごとにそろえる */
        v3 nq = norm(v(floorf(n.x * 2.2f + 0.5f), floorf(n.y * 2.2f + 0.5f), floorf(n.z * 2.2f + 0.5f)));
        if (dot(nq, n) < 0.5f) nq = n;
        n = nq; NdotV = fmaxf(dot(n, V), 1e-3f); R = refl(rd, n);
        v3 F = schlick(F0, NdotV);
        col = vadd(col, vmul(vmulv(F, env(R)), 1.6f));
        /* 中の光：屈折した方向の環境を色で染める＋芯の光 */
        float eta = 1.0f / 1.77f;
        float cosi = -dot(rd, n);
        float k = 1.f - eta * eta * (1.f - cosi * cosi);
        v3 T = k < 0 ? R : norm(vadd(vmul(rd, eta), vmul(n, eta * cosi - sqrtf(k))));
        v3 inner = env(vmul(T, -1.f));
        float tint = 0.35f + 0.65f * powf(NdotV, 1.5f);
        v3 g = vmulv(M->col, vadd(vmul(inner, 0.55f), v(M->a1, M->a1, M->a1)));
        col = vadd(col, vmul(g, tint * (1.f - F.x)));
        /* きらめき：面ごとに明るさを変える */
        float fac = hash3i((int)(nq.x * 7.f), (int)(nq.y * 7.f), (int)(nq.z * 7.f));
        col = vmul(col, 0.6f + 0.8f * fac * M->a2);
    }
    return col;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: sdfr scene.txt\n"); return 1; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror("scene"); return 1; }
    int W = 400, H = 800, ss = 1, x0 = 0, y0 = 0, x1 = -1, y1 = -1;
    v3 eye = v(0, 1, 5), tgt = v(0, 1, 0); float fov = 30.f;
    char outp[512] = "out";
    char line[4096];
    int cur_group = -1;
    for (int i = 0; i < 64; i++) { mats[i].type = 0; mats[i].col = v(1, 0.8f, 0.4f); mats[i].rough = 0.3f; mats[i].bump = 0; }
    while (fgets(line, sizeof line, f)) {
        char kw[32]; if (sscanf(line, "%31s", kw) != 1 || kw[0] == '#') continue;
        char *rest = line + strlen(kw);
        if (!strcmp(kw, "img")) { int n = sscanf(rest, "%d %d %d %d %d %d %d", &W, &H, &ss, &x0, &y0, &x1, &y1); if (n < 7) { x0 = 0; y0 = 0; x1 = W; y1 = H; } }
        else if (!strcmp(kw, "cam")) sscanf(rest, "%f %f %f %f %f %f %f", &eye.x, &eye.y, &eye.z, &tgt.x, &tgt.y, &tgt.z, &fov);
        else if (!strcmp(kw, "out")) sscanf(rest, "%511s", outp);
        else if (!strcmp(kw, "amb")) sscanf(rest, "%f %f %f", &amb.x, &amb.y, &amb.z);
        else if (!strcmp(kw, "grad")) sscanf(rest, "%f %f %f %f %f %f %f %f %f", &gtop.x, &gtop.y, &gtop.z, &ghor.x, &ghor.y, &ghor.z, &gbot.x, &gbot.y, &gbot.z);
        else if (!strcmp(kw, "bounce")) sscanf(rest, "%d", &bounce);
        else if (!strcmp(kw, "tex")) {
            int id, tw, th; char path[512];
            if (sscanf(rest, "%d %d %d %511s", &id, &tw, &th, path) == 4 && id >= 0 && id < 32) {
                FILE *tf = fopen(path, "rb");
                if (!tf) { fprintf(stderr, "tex: cannot open %s\n", path); continue; }
                texs[id].W = tw; texs[id].H = th; texs[id].d = malloc((size_t)tw * th * 4);
                if (fread(texs[id].d, 4, (size_t)tw * th, tf) != (size_t)tw * th) fprintf(stderr, "tex: short read %s\n", path);
                fclose(tf);
            }
        }
        else if (!strcmp(kw, "nocull")) sscanf(rest, "%d", &nocull);
        else if (!strcmp(kw, "cullm")) sscanf(rest, "%f", &cullm);
        else if (!strcmp(kw, "lobe")) { Lobe *L = &lobes[nlobes++]; sscanf(rest, "%f %f %f %f %f %f %f", &L->d.x, &L->d.y, &L->d.z, &L->col.x, &L->col.y, &L->col.z, &L->sharp); L->d = norm(L->d); }
        else if (!strcmp(kw, "light") || !strcmp(kw, "plight")) {
            Light *L = &lights[nlights++]; L->point = !strcmp(kw, "plight");
            sscanf(rest, "%f %f %f %f %f %f %f %d", &L->d.x, &L->d.y, &L->d.z, &L->col.x, &L->col.y, &L->col.z, &L->k, &L->shadow);
            if (!L->point) L->d = norm(L->d);
        }
        else if (!strcmp(kw, "mat")) {
            int id; Mat m = mats[0]; sscanf(rest, "%d %d %f %f %f %f %f %f %f", &id, &m.type, &m.col.x, &m.col.y, &m.col.z, &m.rough, &m.a1, &m.a2, &m.a3);
            m.bump = mats[id].bump; m.bscale = mats[id].bscale; m.bamp = mats[id].bamp; m.bo = mats[id].bo; m.ba = mats[id].ba; m.br = mats[id].br; m.brad = mats[id].brad;
            mats[id] = m;
        }
        else if (!strcmp(kw, "bump")) {
            int id, pat; float sc, am; float ox = 0, oy = 0, oz = 0, ax = 0, ay = 1, az = 0, rx = 1, ry = 0, rz = 0, rad = 0.2f;
            sscanf(rest, "%d %d %f %f %f %f %f %f %f %f %f %f %f %f", &id, &pat, &sc, &am, &ox, &oy, &oz, &ax, &ay, &az, &rx, &ry, &rz, &rad);
            mats[id].bump = pat; mats[id].bscale = sc; mats[id].bamp = am; mats[id].bo = v(ox, oy, oz); mats[id].ba = norm(v(ax, ay, az)); mats[id].br = norm(v(rx, ry, rz)); mats[id].brad = rad;
        }
        else if (!strcmp(kw, "begin")) {
            char op[4]; Group *G = &groups[ngroups]; sscanf(rest, "%3s %f %d", op, &G->k, &G->mat);
            G->op = op[0] == 'U' ? O_U : (op[0] == 'S' ? O_S : O_I);
            G->first = nprims; G->count = 0; cur_group = ngroups++;
            items[nitems].is_group = 1; items[nitems].idx = cur_group; nitems++;
        }
        else if (!strcmp(kw, "end")) {
            Group *G = &groups[cur_group];
            /* グループの外接球（最初の形と結合の形） */
            v3 c = v(0, 0, 0); float wsum = 0;
            for (int i = 0; i < G->count; i++) { Prim *P = &prims[G->first + i]; if (i == 0 || P->op == O_U) { c = vadd(c, P->bc); wsum += 1; } }
            c = vmul(c, 1.f / wsum);
            float r = 0;
            for (int i = 0; i < G->count; i++) { Prim *P = &prims[G->first + i]; if (i == 0 || P->op == O_U) { float rr = len(vsub(P->bc, c)) + P->br + P->k; if (rr > r) r = rr; } }
            G->bc = c; G->br = r;
            cur_group = -1;
        }
        else {
            Prim P; memset(&P, 0, sizeof P);
            char op[4];
            int t = -1;
            if (!strcmp(kw, "sph")) t = T_SPH; else if (!strcmp(kw, "ell")) t = T_ELL; else if (!strcmp(kw, "rcone")) t = T_RCONE;
            else if (!strcmp(kw, "rbox")) t = T_RBOX; else if (!strcmp(kw, "torus")) t = T_TORUS; else if (!strcmp(kw, "ctorus")) t = T_CTORUS;
            else if (!strcmp(kw, "ccone")) t = T_CCONE; else if (!strcmp(kw, "glyph")) t = T_GLYPH;
            if (t < 0) { fprintf(stderr, "unknown: %s\n", kw); continue; }
            P.type = t;
            float a[40]; int na = 0; char *s = rest;
            if (sscanf(s, "%3s", op) != 1) continue;
            s = strstr(s, op) + strlen(op);
            while (na < 40) { char *e; float x = strtof(s, &e); if (e == s) break; a[na++] = x; s = e; }
            P.op = op[0] == 'U' ? O_U : (op[0] == 'S' ? O_S : O_I);
            P.k = a[0]; P.mat = (int)a[1]; P.shell = a[2];
            float *q = a + 3;
            for (int i = 0; i < 9; i++) P.R[i] = (i % 4 == 0) ? 1.f : 0.f;
            switch (t) {
            case T_SPH: P.c = v(q[0], q[1], q[2]); P.r1 = q[3]; P.bc = P.c; P.br = q[3]; break;
            case T_ELL: P.c = v(q[0], q[1], q[2]); P.h = v(q[3], q[4], q[5]); memcpy(P.R, q + 6, 9 * sizeof(float)); P.bc = P.c; P.br = 1.5f * fmaxf(q[3], fmaxf(q[4], q[5])); break;
            case T_RCONE: P.c = v(q[0], q[1], q[2]); P.b = v(q[3], q[4], q[5]); P.r1 = q[6]; P.r2 = q[7];
                P.bc = vmul(vadd(P.c, P.b), 0.5f); P.br = len(vsub(P.b, P.c)) * 0.5f + fmaxf(P.r1, P.r2); break;
            case T_RBOX: P.c = v(q[0], q[1], q[2]); P.h = v(q[3], q[4], q[5]); P.rnd = q[6]; memcpy(P.R, q + 7, 9 * sizeof(float)); P.bc = P.c; P.br = len(P.h); break;
            case T_TORUS: P.c = v(q[0], q[1], q[2]); P.r1 = q[3]; P.r2 = q[4]; memcpy(P.R, q + 5, 9 * sizeof(float)); P.bc = P.c; P.br = q[3] + q[4]; break;
            case T_CTORUS: P.c = v(q[0], q[1], q[2]); P.r1 = q[3]; P.r2 = q[4]; P.half = q[5]; memcpy(P.R, q + 6, 9 * sizeof(float)); P.bc = P.c; P.br = q[3] + q[4]; break;
            case T_CCONE: P.c = v(q[0], q[1], q[2]); P.h = v(q[3], 0, 0); P.r1 = q[4]; P.r2 = q[5]; P.rnd = q[6]; memcpy(P.R, q + 7, 9 * sizeof(float)); P.bc = P.c; P.br = sqrtf(q[3] * q[3] + fmaxf(q[4], q[5]) * fmaxf(q[4], q[5])) + q[6]; break;
            case T_GLYPH: {
                P.c = v(q[0], q[1], q[2]); P.h = v(q[3], q[4], q[5]); P.r1 = q[6]; memcpy(P.R, q + 7, 9 * sizeof(float)); P.bc = P.c;
                if (na >= 3 + 16 + 2) { P.b = v(q[16], fmaxf(q[17], 1e-4f), 0); }
                const Tex *T = &texs[(int)q[6]];
                float hw = T->W * 0.5f * q[3], hh = T->H * 0.5f * q[3];
                P.br = sqrtf(hw * hw + hh * hh + q[4] * q[4]);
            } break;
            }
            P.br += P.shell;
            prims[nprims] = P;
            if (cur_group >= 0) groups[cur_group].count++;
            else { items[nitems].is_group = 0; items[nitems].idx = nprims; nitems++; }
            nprims++;
        }
    }
    fclose(f);
    if (x1 < 0) { x1 = W; y1 = H; }
    /* シーンの外接球 */
    {
        v3 c = v(0, 0, 0); int n = 0;
        for (int i = 0; i < nitems; i++) { int op = items[i].is_group ? groups[items[i].idx].op : prims[items[i].idx].op; if (op != O_U) continue; c = vadd(c, items[i].is_group ? groups[items[i].idx].bc : prims[items[i].idx].bc); n++; }
        c = vmul(c, 1.f / (n ? n : 1)); float r = 0;
        for (int i = 0; i < nitems; i++) {
            int op = items[i].is_group ? groups[items[i].idx].op : prims[items[i].idx].op; if (op != O_U) continue;
            v3 bc = items[i].is_group ? groups[items[i].idx].bc : prims[items[i].idx].bc; float br = items[i].is_group ? groups[items[i].idx].br : prims[items[i].idx].br;
            float rr = len(vsub(bc, c)) + br + 0.05f; if (rr > r) r = rr;
        }
        sceneC = c; sceneR = r;
    }
    fprintf(stderr, "prims %d items %d groups %d  scene r=%.2f\n", nprims, nitems, ngroups, sceneR);
    v3 fw = norm(vsub(tgt, eye)), rt = norm(cross(fw, v(0, 1, 0))), up = cross(rt, fw);
    float th = tanf(fov * 0.5f * 3.14159265f / 180.f), asp = (float)W / H;
    size_t NP = (size_t)W * H;
    float *rgb = calloc(NP * 3, 4), *al = calloc(NP, 4), *dep = calloc(NP, 4), *nor = calloc(NP * 3, 4), *mm = calloc(NP, 4), *aob = calloc(NP, 4);
    for (size_t i = 0; i < NP; i++) { dep[i] = -1.f; mm[i] = -1.f; }
    int rows_done = 0;
#pragma omp parallel for schedule(dynamic, 1)
    for (int py = y0; py < y1; py++) {
        unsigned seed = 1234567u + py * 7919u;
        for (int px = x0; px < x1; px++) {
            v3 acc = v(0, 0, 0); float a = 0; int got = 0;
            for (int sy = 0; sy < ss; sy++) for (int sx = 0; sx < ss; sx++) {
                float jx = (sx + 0.5f) / ss, jy = (sy + 0.5f) / ss;
                float nx = (2.f * (px + jx) / W - 1.f) * th * asp;
                float ny = (1.f - 2.f * (py + jy) / H) * th;
                v3 rd = norm(vadd(fw, vadd(vmul(rt, nx), vmul(up, ny))));
                int m;
                float t = march(eye, rd, 0.05f, 60.f, &m);
                if (t > 0) {
                    v3 p = vadd(eye, vmul(rd, t));
                    v3 n = calcNormal(p, 0.0006f + 0.0002f * t);
                    float ao;
                    v3 c = shade(p, rd, n, m, 0, &seed, &ao);
                    acc = vadd(acc, c); a += 1;
                    if (!got || (sx == ss / 2 && sy == ss / 2)) {
                        size_t id = (size_t)py * W + px;
                        dep[id] = t; mm[id] = m; aob[id] = ao; nor[id * 3] = n.x; nor[id * 3 + 1] = n.y; nor[id * 3 + 2] = n.z; got = 1;
                    }
                }
            }
            size_t id = (size_t)py * W + px;
            float inv = 1.f / (ss * ss);
            rgb[id * 3] = acc.x * inv; rgb[id * 3 + 1] = acc.y * inv; rgb[id * 3 + 2] = acc.z * inv; al[id] = a * inv;
        }
#pragma omp atomic
        rows_done++;
    }
    char fn[600]; FILE *o;
#define DUMP(suffix, buf, cnt) snprintf(fn, sizeof fn, "%s_%s.f32", outp, suffix); o = fopen(fn, "wb"); fwrite(buf, 4, cnt, o); fclose(o);
    DUMP("rgb", rgb, NP * 3); DUMP("a", al, NP); DUMP("d", dep, NP); DUMP("n", nor, NP * 3); DUMP("m", mm, NP); DUMP("ao", aob, NP);
    fprintf(stderr, "done %dx%d\n", W, H);
    return 0;
}
