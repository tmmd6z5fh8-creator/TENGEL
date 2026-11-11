"""大理石の 壁紙（marble_wall.py）の 像を まさちゃんの 3D（Meshy の GLB「Marble Majesty」：金の 帯の 白い 大理石の 台の 上で、後ろ足で 立ち上がる 白い 大理石の 馬・骨なし）で 描く（第4.155版）
   - まさちゃん 2026/11/11：シルバー帯・ゴールド帯・マスター帯（flat/metal_glb.py）に つづいて、大理石の 馬も 3D に。動きの 見本（動画）を 見て「大理石OK！」
   - 3D は アプリに 入れない（約26MB）。ここで コマ（すき通った 絵）に して、flat/marble_glb_run.py が シートに まとめる。壁紙の 動き（marble_wall.py）は 前と 同じ
   - 骨の ない 形を 動かす：形の 上の なだらかな 場（となりの 点の 平均＝調和関数：Mesh.harmonic）を 重みに して、点を 軸の まわりに 回す。
     場は 面の つながりに そって 決まる ＝ たてがみの 房（行き止まりの 枝）は 生えぎわと 同じ 値に なって、生えぎわと いっしょに 動く
       ふり向き look（度）    ：首と 頭を、首の まん中を 通る たての 軸の まわりに（頭は ぜんぶ・首は 根元から うなじへ だんだん）。＋＝こちら（カメラ）がわへ
       くるっと psi（度）     ：馬 だけを、台の まん中の たての 軸の まわりに（台は 動かさない：台と 馬は 台の 上の 面の すぐ 上で 切り分ける）
       ヒヒィーン（neigh_pose）：体を 少し 起こす・首を そらす・頭を ふり上げる・前足 2本を かわるがわる 前へ（ひじと ひざ）・頭を 少し ふる
   - カメラ：台の 下の まん中が 壁紙の 絵（780×320）の FOOT に、像の 高さが 絵の 高さの 9割に なる ように 合わせる（Stage.calibrate）
   - **馬（主役）だけ 高画質**：コマは 壁紙の 絵（780×320＝画面の 2倍）の K＝1.5倍（画面の 3倍）の 細かさ。描く ときは さらに SS＝3倍に して 小さく する（ふちが なめらか）
   - もとの 3D（MARBLE_HORSE_GLB：リポジトリに 入れない）は 読む だけ。場（重み）は <rig の フォルダ>/*.npy に のこして 2回目は 計算しない（3D から 作った もの ＝ リポジトリに 入れない）
   python3 flat/marble_glb.py <出力フォルダ> [psi,look,ヒヒィーンの秒（ない ときは x） …]  → 見る 用の コマ（<出力フォルダ>/<名前>.png・すき通り）。何も 書かなければ 止まった 形（0,0,x）"""
import sys, os, math, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))

GLB = os.environ.get('MARBLE_HORSE_GLB') or '/home/claude/work/band3d/orig/marble_majesty.glb'
W, Hh = 780, 320                                 # 壁紙の 絵（画面の 2倍）
K = 1.5                                          # コマの 細かさ（壁紙の 絵の 何倍か）：1.5 ＝ 画面の 3倍
SS = 3                                           # 描く ときの 細かさ（コマの 何倍か）
WIN = (286, 0, 582, 320)                         # 描く 窓（壁紙の 絵の 画素）：像が 動く はんい。シートの コマは この 中から 切りぬく（marble_glb_run.py）
FW, FH = int((WIN[2] - WIN[0]) * K), int((WIN[3] - WIN[1]) * K)      # 窓の 絵の 大きさ（444×480）
FOOT = (431.83, 305.0)                           # 台の 下の まん中（壁紙の 絵の 画素）。横は 前の 像（flat/marble_banner.py）と 同じ 所
TALL = 0.90                                      # 像の 高さ（絵の 高さの 何割か）
MODEL_H = 1.902                                  # 3D の 像の 高さ（3D の 長さ）
PXU = TALL * Hh / MODEL_H                        # 壁紙の 絵の 画素／3D の 長さ 1
LOOK, LOOK_OVER, PSI_R = 130.0, 140.0, 140.0     # ふり向く 角度・2度見で 少し 行きすぎる 角度・右向きの psi
N_LOOK, N_TURN = 12, 30                          # ふり向き（0 → LOOK）・体が 回る（2秒で 15コマ/秒）の きざみ
NEIGH_S, NEIGH_FPS = 2.6, 15                     # ヒヒィーンの 秒・コマ/秒
EXPO = 0.85                                      # 明るさ


def available():
    return os.path.isfile(GLB)


def sm(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


class Mesh:
    """3D の 形（1つの かたまり）と、同じ 場所の 点を まとめた つながり"""
    def __init__(self, path=GLB):
        import glb
        from scipy import sparse
        from scipy.sparse import csgraph
        t0 = time.time()
        self.model = glb.load(path)
        self.prims = self.model.flatten()
        assert len(self.prims) == 1
        pr = self.pr = self.prims[0]
        self.pos0 = pr.pos.astype(np.float64).copy()
        self.nrm0 = pr.nrm.astype(np.float64).copy()
        self.tri = np.asarray(pr.idx).reshape(-1, 3)
        key = np.round(self.pos0 * 2e4).astype(np.int64)               # 絵の 切れ目で 2つに 分かれた 点を 1つに
        _u, inv = np.unique(key, axis=0, return_inverse=True)
        self.w_of = inv.reshape(-1)
        self.nw = int(self.w_of.max()) + 1
        self.wpos = np.zeros((self.nw, 3))
        self.wpos[self.w_of] = self.pos0
        wt = self.w_of[self.tri]
        e = np.concatenate([wt[:, [0, 1]], wt[:, [1, 2]], wt[:, [2, 0]]], 0)
        e = e[e[:, 0] != e[:, 1]]
        A = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(self.nw, self.nw)).tocsr()
        A = A + A.T
        A.data[:] = 1.0
        self.adj = A
        self.ncomp, self.comp = csgraph.connected_components(A, directed=False)
        sizes = np.bincount(self.comp)
        print(f'mesh: 点 {len(self.pos0):,} → まとめて {self.nw:,}・三角 {len(self.tri):,}・つながりの かたまり {self.ncomp}（大きい 順 {sorted(sizes.tolist(), reverse=True)[:6]}）（{time.time() - t0:.1f}秒）', flush=True)

    def harmonic(self, one, zero, name=''):
        """one（True の 所＝1）・zero（＝0）を 決めて、ほかは となりの 平均（調和）。どちらの 印も ない かたまりは 0"""
        from scipy import sparse
        from scipy.sparse.linalg import splu
        t0 = time.time()
        fixed = one | zero
        has = np.zeros(self.ncomp, bool)
        has[np.unique(self.comp[fixed])] = True
        lost = ~has[self.comp]                                         # 印の ない かたまり
        fixed = fixed | lost
        val = np.where(one, 1.0, 0.0)
        free = np.nonzero(~fixed)[0]
        fx = np.nonzero(fixed)[0]
        deg = np.asarray(self.adj.sum(1)).reshape(-1)
        L = sparse.diags(deg) - self.adj
        Lff = L[free][:, free].tocsc()
        rhs = -(L[free][:, fx] @ val[fx])
        lu = splu(Lff, permc_spec='MMD_AT_PLUS_A', diag_pivot_thresh=0.0, options=dict(SymmetricMode=True))
        x = lu.solve(rhs)
        out = val.copy()
        out[free] = x
        print(f'harmonic {name}: 1 の 点 {int(one.sum()):,}・0 の 点 {int(zero.sum()):,}・自由 {len(free):,}・印なしの かたまりの 点 {int(lost.sum()):,}（{time.time() - t0:.1f}秒）', flush=True)
        return out


def _rod(v, k, ang):
    c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
    return v * c + np.cross(k[None, :], v) * s + k[None, :] * (v @ k)[:, None] * (1 - c)


class State:
    """動かして いる 途中の 形：点・法線・接線（向き だけ）"""
    def __init__(self, pos, nrm, tan):
        self.pos, self.nrm, self.tan = pos.copy(), nrm.copy(), (None if tan is None else tan.copy())

    def rot(self, origin, axis, deg, w):
        """origin を 通る 軸 axis の まわりに deg×w（点ごとの 重み）だけ 回す"""
        if not deg:
            return self
        k = np.asarray(axis, np.float64)
        k = k / np.linalg.norm(k)
        a = math.radians(deg) * w
        m = a != 0
        self.pos[m] = _rod(self.pos[m] - origin, k, a[m]) + origin
        self.nrm[m] = _rod(self.nrm[m], k, a[m])
        if self.tan is not None:
            self.tan[m, :3] = _rod(self.tan[m, :3], k, a[m])
        return self


FWD = math.radians(20.0)                                   # 馬の 体は 真横より 20° こちら（＋z）を 向いて いる
LAT = np.array([math.sin(FWD), 0.0, math.cos(FWD)])        # 馬の 左右の 軸（こちらがわ へ）。この 軸の まわりに −で 回す ＝ 上へ・前へ（起こす・ふり上げる・打ち出す）
UP = np.array([0.0, 1.0, 0.0])
# ヒヒィーン（秒, 体, 首, 頭, 手前の ひじ, 手前の ひざ, 奥の ひじ, 奥の ひざ, 頭を ふる look）：度。いまの 形＝ぜんぶ 0
_TUCK, _STRIKE, _STRIKE_F = (6.0, 24.0), (-14.0, -42.0), (-9.0, -27.0)       # たたむ／打ち出す（ひじ・ひざ）。奥の 足は ひざを のばしきらない
NEIGH_KEYS = (
    (0.00, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    (0.30, 1.0, 4.0, 8.0, 5.0, 14.0, 4.0, 12.0, 0.0),                       # ためる（首を 少し 引いて 前足を たたむ）
    (0.75, -3.5, -10.0, -24.0, *_STRIKE, *_TUCK, 0.0),                      # 体を 起こして 首を 上げ 頭を ふり上げる・手前を 打ち出す
    (1.07, -4.0, -12.0, -28.0, *_TUCK, *_STRIKE_F, 6.0),                    # いちばん 高く・奥を 打ち出す
    (1.40, -3.5, -11.0, -25.0, *_STRIKE, *_TUCK, -10.0),                    # 頭を ふる
    (1.72, -3.0, -9.0, -20.0, *_TUCK, *_STRIKE_F, 8.0),
    (2.10, -1.0, -3.0, -6.0, 3.0, 8.0, 2.0, 6.0, 0.0),                      # おりて くる
    (2.60, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
)


def _cat(p0, p1, p2, p3, u):
    """なめらかな つなぎ（Catmull-Rom）"""
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


def neigh_pose(t):
    """ヒヒィーンの 時刻 t（秒）の 角度（体・首・頭・前足）と 頭を ふる 角度（look）"""
    Kk = NEIGH_KEYS
    vec = [np.array(k[1:], float) for k in Kk]
    ts = [k[0] for k in Kk]
    t = min(max(t, 0.0), ts[-1])
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    v = _cat(vec[max(i - 1, 0)], vec[i], vec[i + 1], vec[min(i + 2, len(Kk) - 1)], u)
    return dict(body=float(v[0]), neck=float(v[1]), head=float(v[2]), eN=float(v[3]), kN=float(v[4]), eF=float(v[5]), kF=float(v[6])), float(v[7])


class Horse:
    PED_TOP = -0.546                               # 台の 上の 面
    CUT = PED_TOP + 0.006                          # ここより 上の 三角 ＝ 馬
    NECK_O = np.array([-0.06, 0.55, 0.03])         # 首の 軸（たて）が 通る 点
    NECK_B = np.array([-0.04, 0.50, 0.03])         # 首の 根元（首を そらす 軸が 通る 点）
    POLL = np.array([-0.055, 0.845, 0.03])         # うなじ（頭を ふり上げる 軸が 通る 点）
    BODY_O = np.array([0.0, -0.50, 0.0])           # 後ろ足の ひづめの 間（体を 起こす 軸が 通る 点）
    SPIN_O = np.array([0.05, 0.0, -0.015])         # 台の まん中
    H_NECK = (0.33, 0.72)                          # 場 h：首の 根元 → うなじ（ここで 0 → 1）
    E_N, K_N = np.array([-0.215, 0.28, 0.23]), np.array([-0.392, 0.275, 0.302])      # 手前の 前足：ひじ・ひざ
    E_F, K_F = np.array([-0.27, 0.315, -0.045]), np.array([-0.465, 0.392, 0.02])     # 奥の 前足：ひじ・ひざ
    G_E, G_KN, G_KF = (0.04, 0.16), (0.30, 0.46), (0.34, 0.50)                        # 足の 場：ひじ・ひざの 所で 0 → 1

    def __init__(self, rig_dir):
        """rig_dir：場（重み）を のこす フォルダ（h・gN・gF・gH2 の .npy：32bit。もう あれば 計算しない）"""
        os.makedirs(rig_dir, exist_ok=True)
        self.M = M = Mesh()
        P = M.wpos

        def field(nm, make):
            fp = os.path.join(rig_dir, nm + '.npy')
            if not os.path.exists(fp):
                for k, v in make().items():
                    np.save(os.path.join(rig_dir, k + '.npy'), v.astype(np.float32))
            f = np.load(fp).astype(np.float64)                  # いつも 32bit に した ものを 使う（1回目と 2回目で 同じ 絵に なる ように）
            assert f.shape == (M.nw,), (fp, f.shape, M.nw, 'ちがう 3D の 場：フォルダを 空に して やり直す')
            return f

        h = field('h', lambda: dict(h=M.harmonic(P[:, 1] > 0.87, P[:, 1] < 0.15, 'h（体 → 頭）')))

        def legs():
            oneN = (P[:, 2] > 0.18) & (P[:, 0] < -0.2) & (P[:, 1] < 0.02) & (P[:, 1] > -0.07)
            oneF = (P[:, 2] < 0.2) & (P[:, 0] < -0.46) & (P[:, 1] < 0.12)
            zero = P[:, 0] > -0.15
            return dict(gN=M.harmonic(oneN, zero | oneF, '手前の 前足'), gF=M.harmonic(oneF, zero | oneN, '奥の 前足'))

        def head():
            one = ((P[:, 0] < -0.075) & (P[:, 1] > 0.60) & (h > 0.70)) | ((P[:, 1] > 0.885) & (P[:, 0] < -0.06) & (P[:, 0] > -0.2))
            return dict(gH2=M.harmonic(one, h < 0.60, '頭'))

        F = dict(h=h, gN=field('gN', legs), gF=field('gF', legs), gH2=field('gH2', head))
        self.F = F
        # 台と 馬を 切り分ける：馬の 三角＝3つの 点が ぜんぶ CUT より 上。両方に 使われる 点は 馬の 分を 写して 分ける
        pos, nrm, tri = M.pos0, M.nrm0, M.tri
        pr = M.pr
        uv = np.asarray(pr.uv)
        tan = None if pr.tangent is None else np.asarray(pr.tangent, np.float64)
        th = (pos[tri][:, :, 1] > self.CUT).all(1)
        used_h = np.zeros(len(pos), bool)
        used_h[tri[th].reshape(-1)] = True
        used_p = np.zeros(len(pos), bool)
        used_p[tri[~th].reshape(-1)] = True
        both = np.nonzero(used_h & used_p)[0]
        remap = np.arange(len(pos))
        remap[both] = len(pos) + np.arange(len(both))
        tri2 = tri.copy()
        tri2[th] = remap[tri[th]]
        src = np.concatenate([np.arange(len(pos)), both])               # 新しい 点 → もとの 点
        self.pos0, self.nrm0 = pos[src], nrm[src]
        self.tan0 = None if tan is None else tan[src]
        pr.uv = uv[src]
        pr.idx = tri2
        if pr.uv1 is not None:
            pr.uv1 = np.asarray(pr.uv1)[src]
        if pr.color is not None:
            pr.color = np.asarray(pr.color)[src]
        self.is_horse = np.zeros(len(src), np.float64)
        self.is_horse[tri2[th].reshape(-1)] = 1.0
        w_of = M.w_of[src]
        f = lambda nm: F[nm][w_of]
        hh = f('h')
        self.w_neck = sm(self.H_NECK[0], self.H_NECK[1], hh) * self.is_horse
        self.w_head = sm(0.15, 0.85, f('gH2')) * self.is_horse
        self.w_body = sm(-0.50, -0.28, self.pos0[:, 1]) * self.is_horse
        gN, gF = f('gN'), f('gF')
        self.w_eN, self.w_kN = sm(*self.G_E, gN) * self.is_horse, sm(*self.G_KN, gN) * self.is_horse
        self.w_eF, self.w_kF = sm(*self.G_E, gF) * self.is_horse, sm(*self.G_KF, gF) * self.is_horse
        print(f'horse: 馬の 三角 {int(th.sum()):,}・台の 三角 {int((~th).sum()):,}・分けた 点 {len(both):,}', flush=True)

    def pose(self, look=0.0, psi=0.0, neigh=None):
        """look・psi は 度。neigh＝ヒヒィーンの 時刻（秒）か None"""
        S = State(self.pos0, self.nrm0, self.tan0)
        if neigh is not None:
            p, shake = neigh_pose(neigh)
            S.rot(self.K_N, LAT, p['kN'], self.w_kN).rot(self.E_N, LAT, p['eN'], self.w_eN)
            S.rot(self.K_F, LAT, p['kF'], self.w_kF).rot(self.E_F, LAT, p['eF'], self.w_eF)
            S.rot(self.POLL, LAT, p['head'], self.w_head).rot(self.NECK_B, LAT, p['neck'], self.w_neck)
            look = look + shake
        S.rot(self.NECK_O, UP, look, self.w_neck)
        if neigh is not None:
            S.rot(self.BODY_O, LAT, p['body'], self.w_body)
        S.rot(self.SPIN_O, UP, psi, self.is_horse)
        pr = self.M.pr
        pr.pos = S.pos.astype(np.float32)
        pr.nrm = (S.nrm / np.maximum(np.linalg.norm(S.nrm, axis=1, keepdims=True), 1e-9)).astype(np.float32)
        if S.tan is not None:
            pr.tangent = S.tan.astype(np.float32)
        return self.M.prims


def lights(yaw=0.0):
    from raster import Light
    Ld = lambda a, e: (math.sin(math.radians(yaw + a)) * math.cos(math.radians(e)), math.sin(math.radians(e)), math.cos(math.radians(yaw + a)) * math.cos(math.radians(e)))
    return [Light.key(direction=Ld(-38, 48), color=(1.0, 0.97, 0.92), intensity=2.5), Light.fill(direction=Ld(60, 12), color=(0.86, 0.9, 1.0), intensity=0.75),
            Light.rim(direction=Ld(170, 30), color=(1.0, 0.96, 0.88), intensity=1.1)]


def camera(Hpx=600, aspect=0.9, yaw=0.0, pit=5.0, fov=14.0, dist=9.0, center=(0.0, 0.0, 0.0)):
    from raster import Camera
    c = np.asarray(center, np.float64)
    y, p = math.radians(yaw), math.radians(pit)
    eye = c + dist * np.array([math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)])
    return Camera.look_at(eye, c, fov_y=fov, W=int(Hpx * aspect) // 2 * 2, H=Hpx)


def shot(prims, cam, ss=2, expo=1.0):
    """1コマ（すき通り：色は まっすぐな α）。光：上・手前・少し 左の 大きな 光＋右の 弱い 光＋うしろの ふちの 光"""
    from raster import render, tonemap
    from PIL import Image
    fr = render(prims, cam, ss=ss, want=('rgb', 'alpha'), lights=lights(), ambient=((0.80, 0.78, 0.74), (0.42, 0.38, 0.33)), env_spec=(0.95, 0.93, 0.9), rim=((1.0, 0.98, 0.94), 0.22, 3.0))
    rgb = np.clip(tonemap(fr['rgb'], expo), 0, 1)
    a = np.clip(fr['alpha'], 0, 1)
    return Image.fromarray((np.dstack([rgb, a]) * 255 + .5).astype(np.uint8), 'RGBA')


def key(psi, look, tn):
    """形 → コマの ファイルの 名前"""
    return f'p{psi + 0.0:07.3f}_l{look + 0.0:+08.3f}_n{"x" if tn is None else f"{tn:.4f}"}'          # ＋0.0：−0.0 を 0.0 に（同じ 形に 2つの 名前を つけない）


class Stage:
    """カメラを 合わせて、形（psi・look・ヒヒィーンの 時刻）ごとの コマ（窓 WIN の 絵：FW×FH・すき通り）を 描く"""
    def __init__(self, rig_dir):
        self.H = Horse(rig_dir)
        self.dist, self.pit = 9.0, 5.0
        self.fov = math.degrees(2 * math.atan((FH / 2) / (PXU * K * self.dist)))
        self.tgt = np.array([Horse.SPIN_O[0] + ((WIN[0] + WIN[2]) / 2 - FOOT[0]) / PXU, -0.952 + (FOOT[1] - (WIN[1] + WIN[3]) / 2) / PXU, Horse.SPIN_O[2]])
        self.calibrate()

    def cam(self):
        return camera(Hpx=FH, aspect=FW / FH, pit=self.pit, fov=self.fov, dist=self.dist, center=self.tgt)

    def calibrate(self):
        """台の 下の まん中が FOOT に、像の 高さが 絵の 9割に なる ように カメラを 合わせる（止まった 形で 3回まで）"""
        for it in range(3):
            im = shot(self.H.pose(), self.cam(), ss=1, expo=EXPO)
            a = np.asarray(im)[..., 3] > 128
            ys, xs = np.nonzero(a)
            y1, y0 = ys.max() + 1, ys.min()
            row = np.nonzero(a[y1 - 4])[0]
            cx = (row.min() + row.max() + 1) / 2
            want_cx, want_y1, want_h = (FOOT[0] - WIN[0]) * K, (FOOT[1] - WIN[1]) * K, TALL * Hh * K
            hgt = y1 - y0
            print(f'calibrate {it}: 台の 下 y={y1}（ねらい {want_y1:.1f}）・台の まん中 x={cx:.1f}（ねらい {want_cx:.1f}）・高さ {hgt}（ねらい {want_h:.1f}）・fov {self.fov:.3f}', flush=True)
            if abs(y1 - want_y1) < 0.8 and abs(cx - want_cx) < 0.8 and abs(hgt - want_h) < 1.5:
                break
            self.fov *= hgt / want_h
            ppu = hgt / MODEL_H
            self.tgt = self.tgt + np.array([(cx - want_cx) / ppu, -(y1 - want_y1) / ppu, 0.0])

    def frame(self, psi, look, tn):
        return shot(self.H.pose(look=look, psi=psi, neigh=tn), self.cam(), ss=SS, expo=EXPO)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    st = Stage(os.path.join(out, 'rig'))
    for spec in sys.argv[2:] or ['0,0,x']:
        a, b, c = spec.split(',')
        psi, look, tn = float(a), float(b), (None if c == 'x' else float(c))
        t0 = time.time()
        fp = os.path.join(out, key(psi, look, tn) + '.png')
        st.frame(psi, look, tn).save(fp)
        print(fp, f'{time.time() - t0:.1f}秒', flush=True)
