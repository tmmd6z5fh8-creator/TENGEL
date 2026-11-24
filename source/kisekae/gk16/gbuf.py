"""神様極的中 第16稿：神様馬（まさちゃんの 3D・Solar_Sovereign）の G バッファ（色・金属・ざらつき・向き・場所・すけ・AO）を 描く
   kisekae/r3d/glb の ラスタライザを そのまま 使い、光は つけない（光は face3d.py が あとで つける）。
   ・向きは 法線の 地図（normal map）を 入れた もの。金属・ざらつきは metallicRoughness の 地図（B＝金属・G＝ざらつき）
   ・たて BANDS に 分けて 描く（メモリ）。SS 倍の 細かさで 描いて 平均（すけ で 重みづけ）
   ・AO は 描いた 深さから（raster._ssao：SS 倍の 半分の 細かさ）"""
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
import glb as GL                                                               # noqa: E402
import raster as RA                                                            # noqa: E402
from raster import Camera, Scene                                               # noqa: E402

GLB_PATH = os.environ.get('GK16_GLB', '/mnt/user-data/uploads/Solar_Sovereign_Meshy_AI_2026-11-01_5254ac_3.glb')
_MD = {}


def scene():
    """3D を 1回だけ 読む（約 20秒・三角 758万）"""
    if 'sc' not in _MD:
        t0 = time.time()
        m = GL.load(GLB_PATH)
        prims = m.flatten()
        _MD['sc'] = Scene(prims)
        _MD['prims'] = prims
        print('gk16: 3D', len(_MD['sc'].tri), 'tris', round(time.time() - t0, 1), 's', flush=True)
    return _MD['sc']


def band_cam(cam, r0, r1):
    """画面の 行 r0〜r1 だけを 写す カメラ（同じ 目・同じ 向き）"""
    H = cam.H
    c = 1 - (r0 + r1) / H; h = (r1 - r0) / H
    T = np.eye(4); T[1, 1] = 1 / h; T[1, 3] = -c / h
    bc = Camera(cam.view, T @ cam.proj, cam.W, r1 - r0)
    bc.near, bc.far, bc.fov_y = cam.near, cam.far, cam.fov_y
    return bc


def _gb(sc, cam, ss):
    """1つの 帯：raster.render の 前半（ラスタ・色の 地図 読み）だけ → SS 倍の 点ごとの 値を 平均"""
    hc = cam.scaled(ss)
    W, H = hc.W, hc.H
    clip = RA._project(hc, sc.pos)
    xyzw, tri, src, lerp = RA._clip_and_screen(hc, clip, sc.tri, None)
    del clip
    tmat = sc.tmat[src]; tflag = np.ones(len(src), np.int32)
    uvs = RA._lerp_attr(sc.uv, lerp)
    nmat = len(sc.mats)
    atex = (RA._fp * nmat)()
    for i in range(nmat):
        atex[i] = RA.ctypes.cast(None, RA._fp)
    aw = np.zeros(nmat, np.int32); ah = np.zeros(nmat, np.int32); acut = np.zeros(nmat, np.float32)
    depth = np.full(W * H, np.inf, np.float32); tid = np.full(W * H, -1, np.int32)
    bary = np.zeros(W * H * 2, np.float32); facing = np.zeros(W * H, np.int8)
    RA._lib.rasterize(len(xyzw), RA._f32(xyzw).ctypes.data_as(RA._fp), RA._f32(uvs).ctypes.data_as(RA._fp), len(tri), RA._i32(tri).ctypes.data_as(RA._ip),
                      RA._i32(tflag).ctypes.data_as(RA._ip), RA._i32(tmat).ctypes.data_as(RA._ip), nmat, atex, aw.ctypes.data_as(RA._ip), ah.ctypes.data_as(RA._ip),
                      acut.ctypes.data_as(RA._fp), W, H, depth.ctypes.data_as(RA._fp), tid.ctypes.data_as(RA._ip), bary.ctypes.data_as(RA._fp),
                      facing.ctypes.data_as(RA.ctypes.POINTER(RA.ctypes.c_int8)))
    cov = tid >= 0
    pix = np.nonzero(cov)[0]
    n = len(pix)
    out = {k: np.zeros((W * H, c), np.float32) for k, c in (('alb', 3), ('mr', 2), ('nrm', 3), ('pos', 3))}
    if n:
        t = tid[pix]
        b1 = bary[pix * 2]; b2 = bary[pix * 2 + 1]; b0 = 1 - b1 - b2
        vi = tri[t]
        pos_all = RA._lerp_attr(sc.pos, lerp); nrm_all = RA._lerp_attr(sc.nrm, lerp); tan_all = RA._lerp_attr(sc.tan, lerp)

        def interp(arr):
            return arr[vi[:, 0]] * b0[:, None] + arr[vi[:, 1]] * b1[:, None] + arr[vi[:, 2]] * b2[:, None]
        P = interp(pos_all); N = RA.normalize(interp(nrm_all)); UV = interp(uvs); T = interp(tan_all)
        eye = hc.eye.astype(np.float32)
        V = RA.normalize(eye[None, :] - P)
        fc = np.where(np.sum(N * V, -1) < 0, -1.0, 1.0).astype(np.float32)
        N = N * fc[:, None]
        mid = tmat[t]
        xy = xyzw[:, :2]
        sa = 0.5 * np.abs((xy[vi[:, 1], 0] - xy[vi[:, 0], 0]) * (xy[vi[:, 2], 1] - xy[vi[:, 0], 1]) - (xy[vi[:, 2], 0] - xy[vi[:, 0], 0]) * (xy[vi[:, 1], 1] - xy[vi[:, 0], 1]))
        ua = 0.5 * np.abs((uvs[vi[:, 1], 0] - uvs[vi[:, 0], 0]) * (uvs[vi[:, 2], 1] - uvs[vi[:, 0], 1]) - (uvs[vi[:, 2], 0] - uvs[vi[:, 0], 0]) * (uvs[vi[:, 1], 1] - uvs[vi[:, 0], 1]))
        base = np.zeros((n, 3), np.float32); mr = np.zeros((n, 2), np.float32); Nn = N.copy()
        for i, m in enumerate(sc.mats):
            sel = np.nonzero(mid == i)[0]
            if not len(sel):
                continue
            uv = UV[sel]
            bc = np.tile(m.base_color[:3], (len(sel), 1))
            if m.base_tex is not None:
                tx = m.base_tex.tex; th, tw = tx.img.shape[:2]
                lod = 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
                s = RA.sample(tx, m.base_tex.uv(uv), lod)
                bc = bc * RA.srgb_to_linear(s[:, :3])
            base[sel] = bc
            m_r = np.tile([m.metallic, m.roughness], (len(sel), 1)).astype(np.float32)
            if m.mr_tex is not None:
                tx = m.mr_tex.tex; th, tw = tx.img.shape[:2]
                lod = 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
                s = RA.sample(tx, m.mr_tex.uv(uv), lod)
                m_r = m_r * np.stack([s[:, 2], s[:, 1]], 1)
            mr[sel] = m_r
            if m.normal_tex is not None and np.any(np.abs(T[sel, :3]).sum(1) > 0):
                tx = m.normal_tex.tex; th, tw = tx.img.shape[:2]
                lod = 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
                s = RA.sample(tx, m.normal_tex.uv(uv), lod)
                tn = s[:, :3] * 2 - 1
                tn[:, :2] *= m.normal_tex.scale
                tn = RA.normalize(tn)
                Ns = N[sel]; Ts = T[sel, :3] * fc[sel][:, None]; Ts = RA.normalize(Ts - Ns * np.sum(Ns * Ts, 1, keepdims=True))
                Bs = np.cross(Ns, Ts) * T[sel, 3:4]
                Nn[sel] = RA.normalize(Ts * tn[:, 0:1] + Bs * tn[:, 1:2] + Ns * tn[:, 2:3])
        out['alb'][pix] = base; out['mr'][pix] = mr; out['nrm'][pix] = Nn; out['pos'][pix] = P
        # AO（法線の 地図を 入れない 向き・半分の 細かさ）
        Pv = (P - eye[None, :]) @ hc.inv_view[:3, :3].astype(np.float32)
        Dfull = np.full(W * H, np.inf, np.float32); Dfull[pix] = -Pv[:, 2]
        Nfull = np.zeros((W * H, 3), np.float32); Nfull[pix] = N @ hc.inv_view[:3, :3].astype(np.float32)
        k = 2
        Dh = Dfull.reshape(H, W)[::k, ::k]; Nh = Nfull.reshape(H, W, 3)[::k, ::k]
        r = np.linalg.norm(sc.hi - sc.lo) * 0.03
        aoh = RA._ssao(Dh, Nh, hc, r)
        ao = np.repeat(np.repeat(aoh, k, 0), k, 1)[:H, :W].reshape(-1)
    else:
        ao = np.ones(W * H, np.float32)

    def ds(a):
        a = a.reshape(H, W, -1)
        return a.reshape(H // ss, ss, W // ss, ss, a.shape[-1]).mean((1, 3))
    A = ds(cov.astype(np.float32))[..., 0]
    safe = np.maximum(A, 1e-6)[..., None]
    G = dict(alpha=A)
    for k_ in ('alb', 'mr', 'pos'):
        G[k_] = ds(out[k_]) / safe * (A[..., None] > 0)
    G['nrm'] = RA.normalize(ds(out['nrm']))
    G['ao'] = (ds((ao * cov).astype(np.float32)) / safe)[..., 0] * (A > 0) + (A <= 0)
    dv = np.where(cov, np.linalg.norm(out['pos'] - hc.eye.astype(np.float32)[None, :], axis=1), np.inf).astype(np.float32).reshape(H, W)
    G['depth'] = dv.reshape(H // ss, ss, W // ss, ss).min((1, 3))
    return G


def gbuffer(cam, ss=2, bands=2):
    """カメラ → G バッファ（alpha・alb〈線形〉・mr〈金属, ざらつき〉・nrm・pos・ao・depth）"""
    sc = scene()
    edges = np.linspace(0, cam.H, bands + 1).round().astype(int)
    parts = [_gb(sc, band_cam(cam, r0, r1), ss) for r0, r1 in zip(edges[:-1], edges[1:])]
    return {k: np.concatenate([p[k] for p in parts], 0) for k in parts[0]}
