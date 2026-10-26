"""3Dの場面を組み立てて sdfr で描くための道具（カメラ・形・素材・読み込み）"""
import os, subprocess, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, 'sdfr')


def nrm(a):
    a = np.asarray(a, float)
    n = np.linalg.norm(a)
    return a / n if n > 1e-12 else a


def basis(ax, up=(0, 1, 0)):
    """ローカルx軸を ax、yをできるだけ up に向けた 世界→ローカル の行列（行）"""
    ex = nrm(ax)
    up = np.asarray(up, float)
    ez = np.cross(ex, up)
    if np.linalg.norm(ez) < 1e-6:
        ez = np.cross(ex, (0, 0, 1) if abs(ex[2]) < 0.9 else (1, 0, 0))
    ez = nrm(ez)
    ey = np.cross(ez, ex)
    return np.array([ex, ey, ez])


def basis_y(ay, side=(1, 0, 0)):
    """ローカルy軸を ay、xをできるだけ side に向けた行列"""
    ey = nrm(ay)
    ex = np.asarray(side, float) - ey * np.dot(side, ey)
    if np.linalg.norm(ex) < 1e-6:
        ex = np.cross(ey, (0, 0, 1))
    ex = nrm(ex)
    ez = np.cross(ex, ey)
    return np.array([ex, ey, ez])


class Scene:
    def __init__(self):
        self.lines = []
        self.cam = None
        self.size = None

    def raw(self, s):
        self.lines.append(s)

    def _f(self, *vals):
        out = []
        for x in vals:
            if isinstance(x, (list, tuple, np.ndarray)):
                out += [f'{float(y):.5f}' for y in np.ravel(x)]
            else:
                out.append(f'{float(x):.5f}')
        return ' '.join(out)

    # 画像・カメラ
    def image(self, W, H, ss=1, rect=None):
        self.size = (W, H)
        r = rect or (0, 0, W, H)
        self.raw(f'img {W} {H} {ss} {r[0]} {r[1]} {r[2]} {r[3]}')

    def camera(self, eye, tgt, fov):
        self.cam = (np.asarray(eye, float), np.asarray(tgt, float), float(fov))
        self.raw('cam ' + self._f(eye, tgt, fov))

    def project(self, P):
        """世界の点 → 画素（x, y）と奥行き"""
        eye, tgt, fov = self.cam
        W, H = self.size
        fw = nrm(tgt - eye)
        rt = nrm(np.cross(fw, (0, 1, 0)))
        up = np.cross(rt, fw)
        th = math.tan(math.radians(fov) * .5)
        asp = W / H
        P = np.atleast_2d(np.asarray(P, float))
        d = P - eye
        xc, yc, zc = d @ rt, d @ up, d @ fw
        nx = xc / zc / (th * asp)
        ny = yc / zc / th
        px = (nx + 1) * .5 * W
        py = (1 - ny) * .5 * H
        return np.stack([px, py], -1), zc

    # 光・環境・素材
    def env(self, top, hor, bot, amb=(0, 0, 0)):
        self.raw('grad ' + self._f(top, hor, bot))
        self.raw('amb ' + self._f(amb))

    def lobe(self, d, col, sharp):
        self.raw('lobe ' + self._f(d, col, sharp))

    def light(self, d, col, k=8, shadow=1):
        self.raw('light ' + self._f(d, col, k) + f' {int(shadow)}')

    def plight(self, p, col, k=8, shadow=0):
        self.raw('plight ' + self._f(p, col, k) + f' {int(shadow)}')

    def mat(self, mid, typ, col, rough, a1=0, a2=0, a3=0):
        self.raw(f'mat {mid} {typ} ' + self._f(col, rough, a1, a2, a3))

    def bump(self, mid, pat, scale, amp, o=(0, 0, 0), ax=(0, 1, 0), rx=(1, 0, 0), rad=0.2):
        self.raw(f'bump {mid} {pat} ' + self._f(scale, amp, o, ax, rx, rad))

    def bounce(self, n):
        self.raw(f'bounce {int(n)}')

    # グループ
    def begin(self, op='U', k=0.0, mat=0):
        self.raw(f'begin {op} {k:.5f} {mat}')

    def end(self):
        self.raw('end')

    # 形
    def sph(self, c, r, op='U', k=0.0, mat=0, shell=0.0):
        self.raw(f'sph {op} ' + self._f(k, mat, shell, c, r))

    def ell(self, c, radii, R=None, op='U', k=0.0, mat=0, shell=0.0):
        R = np.eye(3) if R is None else R
        self.raw(f'ell {op} ' + self._f(k, mat, shell, c, radii, R))

    def ell_ax(self, c, ax, radii, up=(0, 1, 0), **kw):
        """x半径を ax の向きに"""
        self.ell(c, radii, basis(ax, up), **kw)

    def rcone(self, a, b, ra, rb, op='U', k=0.0, mat=0, shell=0.0):
        a = np.asarray(a, float); b = np.asarray(b, float)
        L = np.linalg.norm(b - a)
        if abs(ra - rb) >= L * 0.98:
            # 片方の球がもう片方を含む → 小さい方を少し縮める
            if ra > rb: rb = ra - L * 0.98
            else: ra = rb - L * 0.98
        self.raw(f'rcone {op} ' + self._f(k, mat, shell, a, b, ra, rb))

    def rbox(self, c, half, rnd, R=None, op='U', k=0.0, mat=0, shell=0.0):
        R = np.eye(3) if R is None else R
        self.raw(f'rbox {op} ' + self._f(k, mat, shell, c, half, rnd, R))

    def torus(self, c, axis, Rb, rs, op='U', k=0.0, mat=0, shell=0.0):
        self.raw(f'torus {op} ' + self._f(k, mat, shell, c, Rb, rs, basis_y(axis)))

    def ctorus(self, c, normal, mid, Rb, rs, half, op='U', k=0.0, mat=0, shell=0.0):
        """円弧：中心 c・面の向き normal・弧のまん中の向き mid・半開角 half(rad)"""
        ey = nrm(mid); ez = nrm(normal); ex = nrm(np.cross(ey, ez))
        ez = np.cross(ex, ey)
        self.raw(f'ctorus {op} ' + self._f(k, mat, shell, c, Rb, rs, half, np.array([ex, ey, ez])))

    def ccone(self, a, b, ra, rb, rnd=0.0, side=(1, 0, 0), op='U', k=0.0, mat=0, shell=0.0):
        a = np.asarray(a, float); b = np.asarray(b, float)
        c = (a + b) / 2
        h = np.linalg.norm(b - a) / 2
        self.raw(f'ccone {op} ' + self._f(k, mat, shell, c, h, ra, rb, rnd, basis_y(b - a, side)))

    def tex(self, tid, arr, path):
        """2Dの 距離の 絵（単位は 画素・中が マイナス）を ファイルに 書いて 読ませる（glyph で 使う）"""
        a = np.ascontiguousarray(arr, np.float32)
        a.tofile(path)
        self.raw(f'tex {int(tid)} {a.shape[1]} {a.shape[0]} {path}')

    def glyph(self, c, sx, hz, bev, tid, R=None, op='U', k=0.0, mat=0, shell=0.0, dome=0.0, domew=0.1):
        """2Dの 距離の 絵（tex）を 厚み 2hz で のばした 形（面取り bev・前の 面は ふちから domew の 間で dome だけ ふくらむ）。
           R＝世界→ローカル（ローカルの z が 厚みの 向き）"""
        R = np.eye(3) if R is None else np.asarray(R, float)
        self.raw(f'glyph {op} ' + self._f(k, mat, shell, c, sx, hz, bev, tid, R, dome, domew))

    def render(self, path_prefix, txt=None, quiet=True):
        txt = txt or path_prefix + '.txt'
        with open(txt, 'w') as f:
            f.write('\n'.join(self.lines + [f'out {path_prefix}']) + '\n')
        r = subprocess.run([EXE, txt], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr)
        if not quiet:
            print(r.stderr.strip())
        return load(path_prefix, *self.size)


def load(prefix, W, H):
    g = lambda s, c: np.fromfile(f'{prefix}_{s}.f32', np.float32).reshape(H, W, c) if c > 1 else np.fromfile(f'{prefix}_{s}.f32', np.float32).reshape(H, W)
    return dict(rgb=g('rgb', 3), a=g('a', 1), d=g('d', 1), n=g('n', 3), m=g('m', 1), ao=g('ao', 1))


def tonemap(x, exposure=1.0):
    """ACES風のなめらかな明るさ合わせ（線形 → 0〜1）"""
    x = np.maximum(x * exposure, 0)
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    y = (x * (a * x + b)) / (x * (c * x + d) + e)
    return np.clip(y, 0, 1) ** (1 / 2.2)
