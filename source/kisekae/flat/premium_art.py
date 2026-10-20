"""プレミアムど的中（かわいいど的中）の 絵（WebP）：まさちゃんの指定
   「馬の絵だけヤバすぎる 全身写そうとするから変になるから、アップで、馬の顔も手、ハートだけ見えればいいから！ あとは黄金比とかだけ合ってれば大丈夫！
    背景もまだまだ、虹の感じが弱い！パチンコの大当たりのくらい派手な虹色にしないと！ この画像くらいリアルにして！」
   - ポニーは まさちゃんが 作った 絵の ポニーを モデルに した アップ（顔・前足・ハートだけ）。絵の 比（頭の はば：ハートの はば ≒ 0.54・目・ひづめ）を
     まさちゃんの 絵に あわせた（なぞっていない・まさちゃんの 絵も ここで 作った 絵も リポジトリに 入れない。絵は キャンバスの アセット）
   - 描き方：形は SVG（librsvg）で 3倍の 大きさに ぬって、ふくらみ（ふちからの きょり → 高さ → 光の 当たり方）・つや・ふちの 赤・まわりの かげ・
     キラキラを numpy で 重ねる（左上から 光）
   - 出す 絵（すき通しの ある WebP・画面の 座標の きまった 箱に ぴったり）：
       ポニーは 部品ごと（まさちゃん「馬もプルンプルン系で、全体的に動いて！…でも身体が歪んだりは変だから構造は身体の構造を考えて作成して！」：
         ページで 体の つくりどおりに 動かす。顔の 向き R＝右向き・T＝やや右・W＝やや右で 手前の 目を ウィンク・F＝正面。
         左向き・やや左は ページで 左右 うらがえす。箱は 画面の まん中で 左右 対称）：
         pm_legs：うしろ足（ハートの 下から 見える 関節の ある 短い 足・動かない）／ pm_neck_…：首 ／ pm_mane_…：たてがみ（頭の うしろ）／
         pm_earL_…・pm_earR_…：耳 ／ pm_face_…：頭と 顔・前髪（ウィンクの 顔は 小さな ハートも）／ pm_bow_…：リボン（左右の 耳の まん中）。
         動きの 中心（首の 上・たてがみの 上の はし・耳の つけね・リボンの むすびめ・ハートを 持つ 所）は premium_layers.json の rig。
         頭の 形は 3D の 形を 顔の 向きに 回して 描く（まさちゃん「顔もう少し細く！馬っぽく！目の位置ももっと自然にして！」：YAW・SKULL・CHEEK・SNOUT …）
         カメラ（まさちゃん「カメラだと思って、ど！は右正面からアップに、…う！は真正面からドアップに！カメラ目線で作成して！」）：
         R＝①右正面から・T／W＝③④右正面 斜め上から（PITCH：頭を 少し 上から・頭を 少し 大きく）・F＝⑤真正面 ドアップ。目は カメラ目線（GAZE）。
         絵は 世界の 座標の 箱で、その カメラの アップの 大きさで くっきり 描く（dens）
       pm_aura_…：オーラ（まさちゃん「光沢があるピンクと白のオーラが全体的に馬とハートから出るようにして！」：ポニーと、その カメラで かたむいた
         ハート・前足（・うしろ足）の 形の まわりの つやつやの ピンクの わと 白 → ピンクの 光。ページで 外へ 広がる）
       pm_heart：つやつやの 大きな ハート（こい ピンクの わく・虹色の 星空）／ pm_hoof：前足（首の 横の 肩から ハートの 山の 前を おりて、
         ひづめで ハートの 左右の ふちを 上から つかむ：肩・うで・ふわふわの 毛・ひづめ・ハートに 落ちる かげ）
       pm_t0〜pm_t4：ハートの 字（ど！・て！・き！・ちゅ！・う！）／ pm_fin：最後の 大きな ハートの「ど的中」（小さな ハートつき）
       pm_bg：パチンコの 大当たりのような 虹色の 背景 ／ pm_jelly：つやつやの ゼリーの ハート 6色（よこに ならべた 1まい）
   python3 flat/premium_art.py <出力フォルダ> [名前 …]   → <名前>.webp（名前を 書かなければ ぜんぶ）と、絵を おく 箱（画面の 座標）を
                                                           premium_layers.json に（絵を 作りなおしたら キャンバスに 入れて、id を premium_blobs.json に）
   python3 flat/premium_art.py --boxes                   → 描く 箱"""
import sys, os, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from cute_horse import svg_rgba
from art import f, smooth, ellipse_pts, sparkle
import premium_cute as PC

SC = int(os.environ.get('PM_SC', '3'))            # 画面の 1px を 3画素で 描く（iPhone の 3倍の 画面で くっきり。PM_SC＝ためしに 小さく）


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def nrm(v):
    v = np.array(v, np.float32)
    return v / np.linalg.norm(v)


LIGHT = nrm((-.52, -.68, .72))                    # 光の 向き（左上の 手前から）
HALF = nrm(LIGHT + np.array((0, 0, 1), np.float32))
OUT = hexc('#A11F3D')                             # ふち（こい 赤）
OUT_HI = hexc('#E0577A')                          # ふちの つや


def ramp(t, stops):
    """t（0〜1 の 配列）→ 色（stops＝[(位置, '#色'), …]）"""
    xs = [s[0] for s in stops]
    cs = [hexc(s[1]) for s in stops]
    return np.stack([np.interp(t, xs, [c[i] for c in cs]) for i in range(3)], -1).astype(np.float32)


class Cv:
    """絵の 板：画面の 座標（CSS の px）の 箱 (x, y, w, h)。中は SC 倍の 画素。色は かけた（premultiplied）RGBA"""

    def __init__(self, box, sc=SC):
        x, y, w, h = box
        self.box, self.sc = box, sc
        self.W, self.H = int(round(w * sc)), int(round(h * sc))
        self.img = np.zeros((self.H, self.W, 4), np.float32)
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        self.X = x + (xx + .5) / sc
        self.Y = y + (yy + .5) / sc

    def px(self, v):
        return v * self.sc

    def sub(self, x0, y0, x1, y1):
        """箱の 一部（画面の 座標）：同じ 絵の 中の 小さな 窓（そこだけ 計算する。書くと もとの 絵に 入る）"""
        bx, by = self.box[0], self.box[1]
        X0, Y0 = max(0, int(math.floor((x0 - bx) * self.sc))), max(0, int(math.floor((y0 - by) * self.sc)))
        X1, Y1 = min(self.W, int(math.ceil((x1 - bx) * self.sc))), min(self.H, int(math.ceil((y1 - by) * self.sc)))
        X1, Y1 = max(X1, X0 + 1), max(Y1, Y0 + 1)
        c = Cv.__new__(Cv)
        c.sc = self.sc
        c.box = (bx + X0 / self.sc, by + Y0 / self.sc, (X1 - X0) / self.sc, (Y1 - Y0) / self.sc)
        c.W, c.H = X1 - X0, Y1 - Y0
        c.img = self.img[Y0:Y1, X0:X1]
        c.X, c.Y = self.X[Y0:Y1, X0:X1], self.Y[Y0:Y1, X0:X1]
        return c

    def sub_mask(self, a, m=12.0):
        """不透明度 a（この 板の 大きさ）の ある 所の まわり m px の 窓と、その 窓の a"""
        ys, xs = np.nonzero(a > 1e-3)
        if len(xs) == 0:
            return self, a
        bx, by = self.box[0], self.box[1]
        c = self.sub(bx + xs.min() / self.sc - m, by + ys.min() / self.sc - m, bx + (xs.max() + 1) / self.sc + m, by + (ys.max() + 1) / self.sc + m)
        Y0 = int(round((c.box[1] - by) * self.sc))
        X0 = int(round((c.box[0] - bx) * self.sc))
        return c, a[Y0:Y0 + c.H, X0:X0 + c.W]

    def mask(self, inner):
        """SVG の 形（画面の 座標）→ 不透明度（白で ぬる。stroke を 使う 形は 自分で 書く）"""
        x, y, w, h = self.box
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" viewBox="{f(x)} {f(y)} {f(w)} {f(h)}">'
               f'<g fill="#fff">{inner}</g></svg>')
        return svg_rgba(svg, self.W, self.H)[..., 3].copy()

    def put(self, rgb, a):
        """上に 重ねる（rgb：(3,) か (H, W, 3)）"""
        a = np.clip(a, 0, 1)[..., None]
        rgb = np.broadcast_to(rgb, self.img[..., :3].shape)
        self.img[..., :3] = self.img[..., :3] * (1 - a) + rgb * a
        self.img[..., 3:] = self.img[..., 3:] * (1 - a) + a

    def tint(self, s, rgb, k=1.0):
        """もう 描いてある 所だけ 色を よせる（かげ・光）：s＝強さ（0〜1）"""
        s = np.clip(s * k, 0, 1)[..., None]
        al = self.img[..., 3:]
        self.img[..., :3] = self.img[..., :3] * (1 - s) + np.asarray(rgb, np.float32) * al * s

    def under(self, rgb, a):
        """うしろに 置く（すでに 描いてある 所の 下）"""
        a = np.clip(a, 0, 1)[..., None]
        k = (1 - self.img[..., 3:]) * a
        self.img[..., :3] += np.asarray(rgb, np.float32) * k
        self.img[..., 3:] += k

    def add(self, rgb, a):
        """光を たす（描いてある 所だけ。白い つやの にじみ）"""
        al = self.img[..., 3:]
        self.img[..., :3] = np.minimum(self.img[..., :3] + np.asarray(rgb, np.float32) * np.clip(a, 0, 1)[..., None] * al, al)

    def save(self, fn, q=92):
        a = np.clip(self.img[..., 3], 0, 1)
        rgb = np.where(a[..., None] > 1e-4, self.img[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
        u8 = (np.clip(np.dstack([rgb, a]), 0, 1) * 255 + .5).astype(np.uint8)
        bgra = cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA)
        if fn.endswith('.png'):
            cv2.imwrite(fn, bgra)
        else:
            cv2.imwrite(fn, bgra, [cv2.IMWRITE_WEBP_QUALITY, q])


# ---------------------------------------------------------------- 形の きょり・ふくらみ・光
def dist_in(a, thr=.5):
    return cv2.distanceTransform((a > thr).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)


def dist_out(a, thr=.5):
    return cv2.distanceTransform((a <= thr).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)


def grow(a, w):
    """形を w 画素 ふとらせた 不透明度（ふちの 外がわまで）"""
    if w <= 0:
        return a
    return np.maximum(a, np.clip(w - dist_out(a) + .5, 0, 1))


def blur(a, s):
    return cv2.GaussianBlur(a, (0, 0), max(.1, s))


def height(a, R, soft=.22):
    """ふくらみの 高さ（0〜1）：ふちから R 画素で まるく 上がる（soft：かどを まるめる）"""
    t = np.clip(dist_in(a) / R, 0, 1)
    h = np.sqrt(1 - (1 - t) ** 2).astype(np.float32)
    return blur(h, R * soft) if soft else h


def normals(h, k):
    """高さ h（0〜1）× k 画素 → 面の 向き"""
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8 * k
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8 * k
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    return n / np.linalg.norm(n, axis=2, keepdims=True)


def ell_normals(cv, cx, cy, rx, ry, rot=0.0, flat=0.0):
    """だ円の 玉の 面の 向き（rot：度・flat：0＝まんまる 1＝ひらたい）"""
    r = math.radians(rot)
    dx, dy = cv.X - cx, cv.Y - cy
    u = (dx * math.cos(r) + dy * math.sin(r)) / rx
    v = (-dx * math.sin(r) + dy * math.cos(r)) / ry
    q = np.clip(u * u + v * v, 0, 1)
    z = np.sqrt(1 - q) * (1 - flat) + flat
    nx = u * math.cos(r) - v * math.sin(r)
    ny = u * math.sin(r) + v * math.cos(r)
    n = np.dstack([nx, ny, z]).astype(np.float32)
    return n / np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-6)


def lit(n, shin=40.0):
    """(光の 当たり ぐあい 0〜1, つや 0〜1)"""
    d = np.clip(n @ LIGHT, 0, 1)
    s = np.clip(n @ HALF, 0, 1) ** shin
    return d, s


def edge_dir(a, s=2.0):
    """形の ふちの 外向きの 向き（xy）"""
    b = blur(a, s)
    gx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3)
    L = np.sqrt(gx * gx + gy * gy) + 1e-6
    return -gx / L, -gy / L


def outline(cv, a, w, col=OUT, hi=OUT_HI, gloss=.55):
    """こい 赤の ふち（外がわに w 画面px）。左上の ふちに 少し つや（ルビーの ような ふち）"""
    W = cv.px(w)
    sil = grow(a, W)
    band = np.clip(sil - a, 0, 1)
    ex, ey = edge_dir(sil, W * .6)
    face = np.clip(-(ex * LIGHT[0] + ey * LIGHT[1]) / .85, 0, 1)          # 光の 方を むいた ふち
    d = dist_out(a)
    mid = np.clip(1 - np.abs(d - W * .45) / (W * .32), 0, 1)              # ふちの まん中の すじ
    rgb = col[None, None, :] + (hi - col)[None, None, :] * (face * mid * gloss)[..., None]
    cv.put(rgb, sil)
    return sil, band


def drop(cv, sil, dx=1.5, dy=2.5, s=3.0, col='#7A1235', k=.35):
    """下の 絵に 落ちる かげ（描く 前に 呼ぶ）"""
    sh = blur(np.roll(np.roll(sil, int(cv.px(dy)), 0), int(cv.px(dx)), 1), cv.px(s))
    cv.tint(sh, hexc(col), k)


def glitter(cv, a, n, seed, r=(.5, 1.6), col='#FFFFFF', op=(.5, 1.0), star=0.0):
    """キラキラの 点（a の 中だけ）"""
    rnd = np.random.default_rng(seed)
    H, W = a.shape
    ys, xs = np.nonzero(a > .6)
    if len(xs) == 0:
        return
    idx = rnd.integers(0, len(xs), n)
    acc = np.zeros((H, W), np.float32)
    for i in idx:
        x, y = xs[i], ys[i]
        rr = cv.px(rnd.uniform(*r))
        o = rnd.uniform(*op)
        R = int(rr * (5 if star else 2.5)) + 2
        x0, x1, y0, y1 = max(0, x - R), min(W, x + R + 1), max(0, y - R), min(H, y + R + 1)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d2 = (xx - x) ** 2 + (yy - y) ** 2
        dot = np.exp(-d2 / (2 * (rr * .55) ** 2))
        if star and rnd.random() < star:
            ax = np.exp(-np.abs(yy - y) / (rr * .18)) * np.exp(-np.abs(xx - x) / (rr * 1.9))
            ay = np.exp(-np.abs(xx - x) / (rr * .18)) * np.exp(-np.abs(yy - y) / (rr * 1.9))
            dot = np.maximum(dot, np.maximum(ax, ay))
        acc[y0:y1, x0:x1] = np.maximum(acc[y0:y1, x0:x1], dot * o)
    cv.put(hexc(col), acc * np.clip(a, 0, 1))


def soft_ell(cv, cx, cy, rx, ry, rot=0.0, feather=.5):
    """やわらかい だ円（0〜1）"""
    r = math.radians(rot)
    dx, dy = cv.X - cx, cv.Y - cy
    u = (dx * math.cos(r) + dy * math.sin(r)) / rx
    v = (-dx * math.sin(r) + dy * math.cos(r)) / ry
    q = np.sqrt(u * u + v * v)
    return np.clip((1 - q) / max(1e-3, feather), 0, 1).astype(np.float32)


# ---------------------------------------------------------------- 部品
def circ(cx, cy, r, n=20):
    return smooth(ellipse_pts(cx, cy, r, r, n))


def oval(cx, cy, rx, ry, rot=0.0, n=18):
    return smooth(ellipse_pts(cx, cy, rx, ry, n, rot=rot))


def P(d):
    return f'<path d="{d}"/>'


PINK = [(0, '#CF4A8C'), (.3, '#E5649F'), (.55, '#F189BC'), (.8, '#FAB6D6'), (1, '#FFDDEE')]      # くるくる・リボン（かげ → 光）
WHITE = [(0, '#E0BCD6'), (.35, '#F4DDEB'), (.64, '#FFFFFF'), (1, '#FFFFFF')]                    # 白い 毛（かげは うすい ラベンダー ピンク）


def gloss_ball(cv, cx, cy, rx, ry, rot=0.0, cols=PINK, lw=2.4, shin=30, hi=1.0, rim=.55, sh=.3):
    """つやつやの 玉（リボンの まん中・濁点・ひづめ）：ふち・まるい かげ・左上の 白い つや・右下の 光。sh：下の 絵に 落ちる かげ"""
    R = max(rx, ry) + lw + 10
    cv = cv.sub(cx - R, cy - R, cx + R, cy + R)
    a = cv.mask(P(oval(cx, cy, rx, ry, rot)))
    if sh:
        drop(cv, grow(a, cv.px(lw)), k=sh)
    outline(cv, a, lw)
    n = ell_normals(cv, cx, cy, rx, ry, rot)
    d, s = lit(n, shin)
    t = np.clip(.18 + .9 * d, 0, 1)
    cv.put(ramp(t, cols), a)
    # 右下の 光（はねかえり）
    rimv = np.clip(1 - n[..., 2], 0, 1) ** 2 * np.clip(n[..., 0] * .5 + n[..., 1] * .8, 0, 1)
    cv.add(hexc('#FFE3F1'), rimv * rim * a)
    # 左上の 白い つや（くっきり）と 小さな 点
    hx, hy = cx - rx * .38, cy - ry * .42
    hl = soft_ell(cv, hx, hy, rx * .34, ry * .2, -38 + rot * .3, .45)
    cv.put(hexc('#FFFFFF'), np.clip(hl * 1.6, 0, 1) * .92 * hi * a)
    cv.put(hexc('#FFFFFF'), np.clip(s * 1.2, 0, 1) * .6 * a)
    dot = soft_ell(cv, cx + rx * .32, cy + ry * .38, rx * .09, ry * .09, 0, .6)
    cv.put(hexc('#FFFFFF'), dot * .75 * hi * a)
    return a


def rot_pt(cx, cy, ox, oy, rot):
    r = math.radians(rot)
    return cx + ox * math.cos(r) - oy * math.sin(r), cy + ox * math.sin(r) + oy * math.cos(r)


def ell_q(cv, cx, cy, rx, ry, rot=0.0):
    """だ円の 中の 位置（1＝ふち・0＝まん中）"""
    r = math.radians(rot)
    dx, dy = cv.X - cx, cv.Y - cy
    u = (dx * math.cos(r) + dy * math.sin(r)) / rx
    v = (-dx * math.sin(r) + dy * math.cos(r)) / ry
    return np.sqrt(u * u + v * v).astype(np.float32)


def tube_normals(cv, outer, inner, k):
    """2つの だ円（outer・inner＝(cx, cy, rx, ry, rot)）の あいだの わ（ドーナツ）の 面の 向き：外の ふちと 中の ふちで 下がる"""
    qo = ell_q(cv, *outer)
    qi = ell_q(cv, *inner)
    a = np.clip(1 - qo, 0, None) * min(outer[2], outer[3])
    b = np.clip(qi - 1, 0, None) * min(inner[2], inner[3])
    u = np.clip(a / np.maximum(a + b, 1e-4), 0, 1)
    h = np.sin(np.pi * np.clip(u * .94 + .03, 0, 1)) ** .6
    return normals(h.astype(np.float32), k)


CURL = [(0, '#B92F72'), (.3, '#D9579A'), (.55, '#E979B0'), (.8, '#F5A2CA'), (1, '#FDD0E5')]       # くるくる（かげ → 光：まさちゃんの 絵の こい ピンク）


def curl(cv, cx, cy, rx, ry, rot=0.0, spin=1, lw=2.6, sh=.3):
    """つやつやの くるくる（まいた ロールを 横から）：外の まき（ドーナツの ような わ）・中の まき（右に ずれた 小さな 玉・少し へこむ）・
       中の まきの 中の うず・左上の 白い つや・右下の 光。spin：中の まきの ずれる 向き（1＝右・-1＝左）"""
    R = max(rx, ry) + lw + 10
    cv = cv.sub(cx - R, cy - R, cx + R, cy + R)
    a = cv.mask(P(oval(cx, cy, rx, ry, rot)))
    if sh:
        drop(cv, grow(a, cv.px(lw)), k=sh)
    sil, _ = outline(cv, a, lw)
    icx, icy = rot_pt(cx, cy, rx * .24 * spin, ry * .08, rot)
    irx, iry = rx * .55, ry * .6
    ia = cv.mask(P(oval(icx, icy, irx, iry, rot))) * a
    # 外の まき（わ）
    n = tube_normals(cv, (cx, cy, rx, ry, rot), (icx, icy, irx, iry, rot), cv.px(min(rx, ry)) * .32)
    d, s = lit(n, 26)
    cv.put(ramp(np.clip(.22 + .78 * d, 0, 1), CURL), a)
    rimv = np.clip(n[..., 0] * .5 + n[..., 1] * .85, 0, 1) ** 1.5 * np.clip(1 - n[..., 2], 0, 1)
    cv.add(hexc('#FFD9EC'), rimv * .45 * a * (1 - ia))
    cv.put(hexc('#FFFFFF'), np.clip(s * 1.2, 0, 1) * .4 * a * (1 - ia))
    # 中の まき：まわりの みぞ（こい ピンク）→ 玉（左上は 外の まきの かげ）→ 中の うず
    crease = np.clip(grow(ia, cv.px(rx * .07 + .8)) - ia, 0, 1) * a
    cv.tint(blur(crease, cv.px(.8)), hexc('#A3205F'), .7)
    n2 = ell_normals(cv, icx, icy, irx, iry, rot, flat=.3)
    d2, s2 = lit(n2, 34)
    cv.put(ramp(np.clip(.2 + .8 * d2, 0, 1), CURL), ia)
    sh2 = blur(np.roll(np.roll(a * (1 - ia), int(cv.px(ry * .12)), 0), int(cv.px(rx * .08)), 1), cv.px(ry * .08))
    cv.tint(sh2 * ia, hexc('#9E2463'), .7)
    ring = np.clip(ia - np.clip(dist_in(ia) / cv.px(.8), 0, 1), 0, 1) * a
    cv.tint(ring, hexc('#8E1E57'), .75)
    jcx, jcy = rot_pt(icx, icy, irx * .18 * spin, iry * .1, rot)
    ja = cv.mask(P(oval(jcx, jcy, irx * .52, iry * .52, rot))) * ia
    jring = np.clip(grow(ja, cv.px(.8)) - ja, 0, 1) * ia
    cv.tint(blur(jring, cv.px(.5)), hexc('#A3286A'), .55)
    cv.tint(blur(np.roll(np.roll(jring, int(cv.px(1.0)), 0), int(cv.px(.6)), 1), cv.px(.9)) * ja, hexc('#B23778'), .35)
    # つや：外の まきの 左上の 三日月・中の まきの 左上・小さな 点
    hx, hy = rot_pt(cx, cy, -rx * .48, -ry * .5, rot)
    hl = soft_ell(cv, hx, hy, rx * .32, ry * .13, rot - 26, .4) * (1 - ia)
    cv.put(hexc('#FFFFFF'), np.clip(hl * 1.5, 0, 1) * .8 * a)
    hx2, hy2 = rot_pt(icx, icy, -irx * .3, -iry * .38, rot)
    hl2 = soft_ell(cv, hx2, hy2, irx * .28, iry * .14, rot - 24, .5)
    cv.put(hexc('#FFFFFF'), np.clip(hl2 * 1.4, 0, 1) * .7 * ia)
    px_, py_ = rot_pt(cx, cy, rx * .02, -ry * .72, rot)
    cv.put(hexc('#FFFFFF'), soft_ell(cv, px_, py_, rx * .05, rx * .05, 0, .6) * .85 * a)
    return sil


def fur(cv, a, R=26.0, lw=2.4, cols=WHITE, rim=.0, line=True):
    """白い 毛（頭・首・前足）：ふち・やわらかい かげ（うすい ラベンダー ピンク）"""
    cv, a = cv.sub_mask(a, lw + 4)
    sil = None
    if line:
        sil, _ = outline(cv, a, lw)
    h = height(a, cv.px(R), soft=.3)
    n = normals(h, cv.px(R) * .55)
    d, s = lit(n, 12)
    cv.put(ramp(np.clip(.2 + .95 * d, 0, 1), cols), a)
    if rim:
        rimv = np.clip(n[..., 0] * .4 + n[..., 1] * .8, 0, 1) * np.clip(1 - n[..., 2], 0, 1)
        cv.add(hexc('#FFF4FA'), rimv * rim * a)
    return sil


def stroke_mask(cv, d, w, cap='round'):
    x, y, ww, hh = cv.box
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{cv.W}" height="{cv.H}" viewBox="{f(x)} {f(y)} {f(ww)} {f(hh)}">'
           f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{f(w)}" stroke-linecap="{cap}" stroke-linejoin="round"/></svg>')
    return svg_rgba(svg, cv.W, cv.H)[..., 3].copy()


EYE_D = hexc('#22041A')


def eye(cv, ex, ey, rx, ry, side=1, rot=0.0, lashes=True, clip=None, gaze=(0.0, 0.0)):
    """大きな キラキラの 目（まさちゃんの 絵の 目）：上が こい 紫 → 下が マゼンタ・まん中の ひとみ・大きな 白い 光・下の やわらかい 光・
       上の まぶたの 線・まつげ 3本（side：まつげの 向き 1＝右・-1＝左）。clip：目を この 形（SVG）の 中だけに（ななめの 顔の 向こうの 目）。
       gaze：目線（ひとみと 光を 目の はば・高さの 何倍 ずらすか：カメラ目線）"""
    R = max(rx, ry) * 1.9
    cv = cv.sub(ex - R, ey - R, ex + R, ey + R)
    a = cv.mask(P(oval(ex, ey, rx, ry, rot)))
    if clip:
        a = a * cv.mask(clip)
    gx, gy = gaze[0] * rx, gaze[1] * ry
    t = np.clip((cv.Y - (ey - ry)) / (2 * ry), 0, 1)
    col = ramp(t, [(0, '#24051A'), (.3, '#3A0A2C'), (.55, '#701A5A'), (.78, '#B8357F'), (1, '#E66AAE')])
    cv.put(col, a)
    # 下の やわらかい 光（ピンク）
    cv.put(hexc('#F59ACB'), soft_ell(cv, ex - rx * .15 * side + gx * .5, ey + ry * .62 + gy * .5, rx * .75, ry * .35, 0, 1.0) * .55 * a)
    # ひとみ（まん中 少し 下・目線の 方へ）と その まわりの 輪
    px0, py0 = ex + gx, ey + ry * .12 + gy
    ir = soft_ell(cv, px0, py0 - ry * .02, rx * .6, ry * .52, rot, .08)
    cv.tint(ir * a, hexc('#5A1046'), .35)
    pu = soft_ell(cv, px0, py0, rx * .38, ry * .34, rot, .12)
    cv.put(hexc('#2A0420'), pu * .92 * a)
    pr = np.clip(soft_ell(cv, px0, py0, rx * .46, ry * .42, rot, .05) - soft_ell(cv, px0, py0, rx * .38, ry * .34, rot, .05), 0, 1)
    cv.put(hexc('#C0488F'), pr * .5 * a)
    # 下の ふちの 光の 玉（ボケ）
    for bx, by, br, op in ((-.42, .58, .2, .75), (-.12, .7, .14, .6), (.22, .66, .1, .45)):
        cv.put(hexc('#FFE2F2'), soft_ell(cv, ex + rx * bx * side + gx * .6, ey + ry * by + gy * .6, rx * br, rx * br, 0, .35) * op * a)
    # 大きな 白い 光（上・ひとみの 左）と 小さな 光（ひとみと いっしょに 動く）
    hx0, hy0 = gx, gy * .45
    hl = cv.mask(P(oval(ex - rx * .18 * side + hx0, ey - ry * .42 + hy0, rx * .36, ry * .28, 0)))
    cv.put(hexc('#FFFFFF'), hl * a)
    cv.put(hexc('#FFFFFF'), cv.mask(P(circ(ex + rx * .06 * side + gx, ey + ry * .04 + gy, rx * .1))) * a)
    cv.put(hexc('#FFFFFF'), cv.mask(P(sparkle(ex + rx * .45 * side + gx, ey + ry * .02 + gy, rx * .16, .2))) * .95 * a)
    cv.put(hexc('#FFFFFF'), cv.mask(P(circ(ex - rx * .02 * side + gx, ey + ry * .34 + gy, rx * .05))) * .8 * a)
    # ふち（こい むらさき・上を 太く）
    W = cv.px(rx * .1)
    ring = np.clip(grow(a, W) - a, 0, 1)
    cv.put(EYE_D, ring)
    lid = stroke_mask(cv, f'M{f(ex - rx * 1.02)} {f(ey - ry * .1)} C{f(ex - rx * .9)} {f(ey - ry * 1.1)} {f(ex + rx * .9)} {f(ey - ry * 1.12)} {f(ex + rx * 1.06)} {f(ey - ry * .2)}',
                      rx * .2)
    cv.put(EYE_D, lid)
    if lashes:
        for th, L in ((28, .62), (50, .6), (72, .5)):          # まぶたの 上の 外がわ（だ円の 角度）から 外の 上へ はねる
            t = math.radians(th)
            bx, by = ex + side * rx * 1.04 * math.cos(t), ey - ry * 1.04 * math.sin(t)
            dx, dy = side * math.cos(t - .25), -math.sin(t + .1)
            L2 = L * rx
            tx, ty = bx + dx * L2, by + dy * L2 - L2 * .12
            mx, my = bx + dx * L2 * .55 + side * L2 * .1, by + dy * L2 * .55 + L2 * .06
            m = stroke_mask(cv, f'M{f(bx)} {f(by)} Q{f(mx)} {f(my)} {f(tx)} {f(ty)}', rx * .15)
            cv.put(EYE_D, m)
    return a


def wink(cv, ex, ey, rx, ry, side=1):
    """ウィンク（とじて にっこり：上へ まるい 太い 線・外がわに まつげ 2本）"""
    R = max(rx, ry) * 2
    cv = cv.sub(ex - R, ey - R, ex + R, ey + R)
    m = stroke_mask(cv, f'M{f(ex - rx * 1.0)} {f(ey + ry * .22)} C{f(ex - rx * .7)} {f(ey - ry * .55)} {f(ex + rx * .7)} {f(ey - ry * .55)} {f(ex + rx * 1.0)} {f(ey + ry * .22)}',
                    rx * .26)
    cv.put(EYE_D, m)
    ox, oy = ex + side * rx * .98, ey + ry * .14
    for dx, dy in ((.5, -.08), (.42, -.4)):
        mm = stroke_mask(cv, f'M{f(ox - side * rx * .05)} {f(oy - ry * .02)} Q{f(ox + side * rx * dx * .5)} {f(oy + ry * dy * .3)} {f(ox + side * rx * dx)} {f(oy + ry * dy)}', rx * .15)
        cv.put(EYE_D, mm)


def ear(cv, b1, tip, b2, k=.32, inner=True):
    """耳（白・中は ピンク）：b1・b2＝つけね・tip＝先（ふくらみ k）"""
    cen = ((b1[0] + tip[0] + b2[0]) / 3, (b1[1] + tip[1] + b2[1]) / 3)

    def bulge(p, q, kk):
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        vx, vy = mx - cen[0], my - cen[1]
        L = math.hypot(vx, vy) or 1
        dd = math.hypot(q[0] - p[0], q[1] - p[1])
        return mx + vx / L * dd * kk, my + vy / L * dd * kk

    def shape(p1, t, p2, kk):
        c1, c2 = bulge(p1, t, kk), bulge(t, p2, kk)
        return f'M{f(p1[0])} {f(p1[1])} Q{f(c1[0])} {f(c1[1])} {f(t[0])} {f(t[1])} Q{f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])} Z'

    lerp = lambda p, q, u: (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
    xs, ys = [b1[0], tip[0], b2[0]], [b1[1], tip[1], b2[1]]
    cv = cv.sub(min(xs) - 24, min(ys) - 24, max(xs) + 24, max(ys) + 24)
    a = cv.mask(P(shape(b1, tip, b2, k)))
    sil = fur(cv, a, R=10, lw=2.4)
    if inner:
        bm = lerp(b1, b2, .5)
        i1, i2, it = lerp(lerp(b1, bm, .3), tip, .1), lerp(lerp(b2, bm, .3), tip, .1), lerp(tip, bm, .2)
        ia = cv.mask(P(shape(i1, it, i2, k * .75))) * a
        t = np.clip(((cv.X - tip[0]) * (bm[0] - tip[0]) + (cv.Y - tip[1]) * (bm[1] - tip[1])) / max(1e-3, (bm[0] - tip[0]) ** 2 + (bm[1] - tip[1]) ** 2), 0, 1)
        cv.put(ramp(t, [(0, '#FBC6DD'), (.6, '#F4A3C8'), (1, '#E784B4')]), ia)
        cv.tint(blur(np.clip(grow(ia, cv.px(1.2)) - ia, 0, 1), cv.px(.8)) * a, hexc('#E9A2C6'), .5)
    return sil


def tf(pts, cx, cy, s=1.0, rot=0.0, mx=1):
    """点を 回して（度）・大きさ s・左右（mx＝-1 で うらがえし）・(cx, cy) へ"""
    r = math.radians(rot)
    c, si = math.cos(r), math.sin(r)
    return [(cx + (x * mx * c - y * si) * s, cy + (x * mx * si + y * c) * s) for x, y in pts]


def shaded(cv, a, cols=PINK, R=7.0, lw=2.4, shin=24, hl=None, gloss=.5, line=True):
    """ふち＋ふくらみの かげ＋つや（リボン・ひだ など）。hl：白い つやの だ円 [(x, y, rx, ry, rot, 強さ)]"""
    cv, a = cv.sub_mask(a, lw + 4)
    sil = outline(cv, a, lw)[0] if line else a
    h = height(a, cv.px(R), soft=.28)
    n = normals(h, cv.px(R) * .7)
    d, s = lit(n, shin)
    cv.put(ramp(np.clip(.12 + .95 * d, 0, 1), cols), a)
    cv.put(hexc('#FFFFFF'), np.clip(s * 1.3, 0, 1) * gloss * a)
    for x, y, rx, ry, rot, k in (hl or ()):
        cv.put(hexc('#FFFFFF'), np.clip(soft_ell(cv, x, y, rx, ry, rot, .5) * 1.6, 0, 1) * k * a)
    return sil


def bow(cv, cx, cy, s=1.0, rot=0.0, mx=1):
    """大きな つやつやの リボン（まさちゃんの 絵の リボン）：下へ 広がる ひだの リボン 5まい・左右の ふくらんだ わ（中に おりめ）・まん中の 玉"""
    cv = cv.sub(cx - 80 * s, cy - 80 * s, cx + 80 * s, cy + 80 * s)
    # ひだ（うしろ）
    for i in range(5):
        a0, a1 = math.radians(60 + i * 12), math.radians(60 + (i + 1) * 12)
        L = 50 - abs(i - 2) * 4.5
        am = (a0 + a1) / 2
        pts = [(math.cos(a0) * 8, math.sin(a0) * 8), (math.cos(a0) * L, math.sin(a0) * L),
               (math.cos(am) * (L - 5), math.sin(am) * (L - 5)), (math.cos(a1) * L, math.sin(a1) * L), (math.cos(a1) * 8, math.sin(a1) * 8)]
        q = tf(pts, cx, cy, s, rot, mx)
        d = f'M{f(q[0][0])} {f(q[0][1])} L{f(q[1][0])} {f(q[1][1])} L{f(q[2][0])} {f(q[2][1])} L{f(q[3][0])} {f(q[3][1])} L{f(q[4][0])} {f(q[4][1])} Z'
        a = cv.mask(P(d))
        cols = PINK if i % 2 else [(0, '#D9579A'), (.4, '#EC7DB5'), (.75, '#F8AED2'), (1, '#FFD9EC')]
        shaded(cv, a, cols, R=4.5 * s, lw=1.8, gloss=.35)
    # 左右の わ（右の わは 少し 小さい：ななめ）
    for side, k in ((-1, 1.0), (1, .9)):
        side_pts = lambda pts: [(x * k * side, y * k) for x, y in pts]        # わの 点（x が 正）→ side の がわ
        loop = [(6, -5), (22, -27), (44, -33), (57, -18), (56, 6), (44, 21), (23, 18), (7, 7)]
        q = tf(side_pts(loop), cx, cy, s, rot, mx)
        a = cv.mask(P(smooth(q)))
        hx, hy = tf([(side * 36 * k, -18 * k)], cx, cy, s, rot, mx)[0]
        shaded(cv, a, PINK, R=11 * s, lw=2.6, hl=[(hx, hy, 9 * s, 5 * s, rot - 20 * side * mx, .85)])
        inner = [(8, -2), (20, -15), (33, -13), (36, -1), (28, 8), (13, 6)]
        q2 = tf(side_pts(inner), cx, cy, s, rot, mx)
        ia = cv.mask(P(smooth(q2))) * a
        cv.tint(blur(np.clip(grow(ia, cv.px(1.4)) - ia, 0, 1), cv.px(.7)) * a, hexc('#B8337A'), .6)
        hh = height(ia, cv.px(5 * s), soft=.3)
        dd, ss = lit(normals(hh, cv.px(4 * s)), 20)
        cv.put(ramp(np.clip(.05 + .8 * dd, 0, 1), [(0, '#C9407F'), (.5, '#E46CA6'), (1, '#F6A8CE')]), ia)
        for dx, dy, r_, op in ((24, -2, 3.2, .9), (40, 8, 2.2, .75)):
            px_, py_ = tf([(side * dx * k, dy * k)], cx, cy, s, rot, mx)[0]
            cv.put(hexc('#FFFFFF'), soft_ell(cv, px_, py_, r_ * s, r_ * s, 0, .5) * op * a)
    gloss_ball(cv, cx, cy, 11.5 * s, 11.5 * s, 0, lw=2.4)


# ---------------------------------------------------------------- ならべ方（390×844 の 画面。まさちゃんの 絵の 比：頭の 白い はば ≒ ハートの はば × 0.54）
HC = PC.HEART_C                                   # ハートの まん中
HS = PC.HEART_S                                   # ハートの はばの 半分
HEAD_BOX = PC.HEAD_BOX                            # 頭の 絵の 箱（画面の まん中で 左右 対称：左向きは ページで うらがえす）
HEART_BOX = PC.HEART_BOX
HOOF_BOX = PC.HOOF_BOX
WU = 2 * HS / 350                                 # 頭の 部品の 数字は ハートの はば 350px の 時の 大きさ
HEAD_K = 1.1 * WU                                 # 頭の 大きさ（まさちゃんの 絵より 1割 大きく：アップ）
# カメラ（まさちゃん「カメラだと思って、ど！は右正面からアップに、て！は左正面からアップに、き！は右正面斜め上からアップに、
#  ちゅ！は左正面斜め上からアップに、う！は真正面からドアップに！カメラ目線で作成して！」）：顔の 向きごとの カメラ（PC.CAMS の 番号）。
#  R＝①右正面から（②は 左右 うらがえし）・T＝③右正面 斜め上から・W＝T で ウィンク（④は ③の カメラを 左右 うらがえし）・F＝⑤真正面 ドアップ
CAM_OF = dict(R=0, T=2, W=2, F=4)
HEAD_SC = dict(R=1.0, T=1.08, W=1.08, F=1.03)     # カメラに 近い 頭は 少し 大きく（斜め上から・ドアップ）
HEAD_C = dict(R=(HC[0] - .1 * 2 * HS, HC[1] - .75 * 2 * HS), T=(HC[0] - .06 * 2 * HS, HC[1] - .75 * 2 * HS + 6),
              F=(HC[0], HC[1] - .75 * 2 * HS))                  # 頭の まん中（顔の 向きごと。斜め上からは 首が 短く 見えて 少し 下）
HEAD_C['W'] = HEAD_C['T']
ZMAX = max(c['z'] for c in PC.CAMS)


def dens(z):
    """画面で z 倍に して 見せる 絵の 画素の こさ（iPhone の 3倍の 画面で くっきり）"""
    return SC * z


def head_k(v):
    return HEAD_K * HEAD_SC[v]
HOOF_R = .072 * 2 * HS                            # ひづめの 大きさ（場所は 前足の HOOF_AT）
HEART_KY = .94                                    # ハートの 高さ（はばに 対して 少し ひくく：まさちゃんの 絵の ハート）


LEG_X, LEG_Y0, LEG_KNEE, LEG_Y1 = .19 * 2 * HS, HC[1] + 70, HC[1] + 132, HC[1] + 180   # うしろ足：左右・上の はし（ハートの うしろ）・関節・ひづめの 下


def legs(cv):
    """うしろ足（ハートの 下から 見える 短い 足：関節（ひざ）で 少し 曲がる・白い 毛・ひづめに かぶさる ふわふわの 毛・ピンクの ひづめ）。
       まさちゃん「後ろ脚もいいサイズ感で入れて！この感じなら短い方がいいと思う！」「脚は、せめて関節入れて！」（まさちゃんの 絵の うしろ足）"""
    from art import limb
    cuff = [(0, '#E7B3D2'), (.4, '#F7D9EA'), (.7, '#FFFFFF'), (1, '#FFFFFF')]
    for sd in (-1, 1):
        x = HC[0] + sd * LEG_X
        top, knee, ank = (x - sd * 4, LEG_Y0), (x + sd * 10, LEG_KNEE), (x + sd * 2, LEG_Y1 - 26)
        a = cv.mask(P(limb([top, knee], [36, 32], cap=False)) + P(limb([knee, ank], [26, 25], cap=False)) + P(oval(knee[0] + sd * 3, knee[1], 19, 17)))
        drop(cv, grow(a, cv.px(2.4)), k=.25)
        fur(cv, a, R=12, lw=2.4)
        # 関節（ひざ）：ふくらみの かげ・内がわの しわ・上の 光
        cv.tint(np.clip(soft_ell(cv, knee[0] + sd * 3, knee[1] + 8, 18, 9, 0, 1.0) - soft_ell(cv, knee[0] + sd * 3, knee[1] + 2, 16, 10, 0, 1.0), 0, 1) * a,
                hexc('#E2B4CF'), .9)
        cr = stroke_mask(cv, f'M{f(knee[0] - sd * 14)} {f(knee[1] - 9)} Q{f(knee[0] - sd * 5)} {f(knee[1] + 1)} {f(knee[0] - sd * 12)} {f(knee[1] + 11)}', 2.4)
        cv.put(hexc('#B97A9F'), cr * .9)
        cv.put(hexc('#FFFFFF'), soft_ell(cv, knee[0] + sd * 6, knee[1] - 6, 7, 4, 0, .6) * .85 * a)
        # ひづめ（うすい ピンク・つや）→ ひづめに かぶさる ふわふわの 毛
        y = LEG_Y1 - 30
        hf = cv.mask(P(smooth([(x - 21, y + 12), (x + 21, y + 12), (x + 24, LEG_Y1 - 6), (x + 19, LEG_Y1), (x - 19, LEG_Y1), (x - 24, LEG_Y1 - 6)])))
        shaded(cv, hf, cols=[(0, '#D66A9C'), (.35, '#EC98C0'), (.7, '#F8C6DD'), (1, '#FFEAF4')], R=6, lw=2.4, gloss=.6,
               hl=[(x - 9, LEG_Y1 - 10, 6.5, 3, -8, .8)])
        sc = [(x - 24, y + 4), (x - 18, y - 5), (x - 10, y - 1), (x - 3, y - 7), (x + 4, y - 1), (x + 12, y - 6), (x + 19, y - 1), (x + 24, y + 4),
              (x + 25, y + 13), (x + 19, y + 19), (x + 11, y + 15), (x + 3, y + 20), (x - 4, y + 15), (x - 12, y + 20), (x - 19, y + 15), (x - 25, y + 13)]
        m = cv.mask(P(smooth(sc)))
        drop(cv, grow(m, cv.px(2.2)), k=.25)
        fur(cv, m, R=8, lw=2.2, cols=cuff)


def neck(cv, v, th, ph=0.0):
    """首（白・頭の うしろから むねへ。下ほど 太く、肩の あいだに 入る）。まさちゃん「全体的に、首がなく」「首から手の位置まで、肩を入れたり自然にして！」"""
    from art import limb
    hx, hy = HEAD_C[v]
    K = head_k(v)
    (nx, ny), _ = pr((0, 40, -18), th, ph)
    top = (hx + nx * K, hy + ny * K)
    bot = (HC[0], HC[1] - 100)                                      # むねの まん中（ハートの うしろ）
    mid = (top[0] * .55 + bot[0] * .45, top[1] * .55 + bot[1] * .45)
    a = cv.mask(P(limb([top, mid, bot], [92 * K, 100 * HEAD_K, 118 * HEAD_K])))
    fur(cv, a, R=30, lw=2.6)


# 前足（まさちゃん「ハートの持ち方が手が下から入ってるから変！上から持って！首から手の位置まで、肩を入れたり自然にして！」）：
# 首の 横の 肩から、ハートの 山の 前を ななめに おりて、ハートの 左右の ふちを 上から つかむ。点は (ハートの まん中から 左右へ, 上下)
ARM = ((64, -135), (93, -119), (101, -111))                     # 肩 → ハートの 山の 前 → 手首（まさちゃん「もっと腕の長さ短くして！鉤爪で、支えてるくらいが丁度いい！」）
ARM_W = (44, 38, 35)
HOOF_TILT = 28.0                                                  # ひづめの かたむき（度：うでより 少し 下へ 曲げて、ハートの 上の 方に ひっかける）
HOOF_AT = (ARM[-1][0] + 30 * math.sin(math.radians(HOOF_TILT)), ARM[-1][1] + 30 * math.cos(math.radians(HOOF_TILT)))   # ひづめの まん中


HOOF_X, HOOF_Y = HOOF_AT[0], HC[1] + HOOF_AT[1]                  # ひづめの まん中（ハートの まん中から 左右へ・画面の 高さ）


def arm_d(sd):
    """前足（肩から 手首まで）の 形"""
    from art import limb
    return limb([(HC[0] + sd * dx, HC[1] + dy) for dx, dy in ARM], list(ARM_W))


def hoof_rot(sd):
    """ひづめの かたむき（上が 内がわ）"""
    return -sd * HOOF_TILT


# ---------------------------------------------------------------- 頭（3D の 形を 顔の 向きに 回して 描く：どの 向きでも 目・耳・鼻の 場所が 自然に そろう）
# まさちゃん「顔もう少し細く！馬っぽく！目の位置ももっと自然にして！」「ここ耳がおかしい！二枚目に合わせて！」（耳は まっすぐ 上へ のびる 長い 耳）
# 座標：x＝右・y＝下・z＝手前（ハートの はば 350px の 時の 大きさ）。向き：右へ 回す 角度・上から 見る 角度
YAW = dict(R=30.0, T=16.0, W=16.0, F=0.0)          # R＝右正面から（①）・T＝右正面 斜め上から（③。W は ウィンク）・F＝真正面（⑤）。左は ページで 左右 うらがえす
PITCH = dict(R=0.0, T=12.0, W=12.0, F=0.0)          # 斜め上から：頭を 少し 上から 見る（顔は カメラへ 上げているので 少しだけ）
GAZE = dict(R=(-.3, 0.0), T=(-.16, -.3), W=(-.16, -.3), F=(0.0, 0.0))   # カメラ目線：ひとみを カメラの 方へ（目の はば・高さの 何倍）
SKULL = ((0, -18, 0), (68, 66, 62))                # 頭の まるい 所（まん中・半径 x, y, z）
CHEEK = ((0, 16, 18), (57, 48, 56))                # ほお（頭と 鼻先の あいだ）
SNOUT = ((0, 50, 56), (40, 30, 54))                # 鼻先（前と 下へ のびる＝馬の 顔）
EYE = ((40, -20, 50), 20, 27, (.55, 0, .83))       # 右目（左目は x を 反対）：まん中・はば・高さ・向き
EAR = ((37, -74, -8), (44, -150, -16), 19.5)       # 右耳：つけねの まん中・先・つけねの はばの 半分（外がわの つけねは EAR_OUT まで 下げて 頭の 中に）
EAR_OUT = (-4, 24)                                 # 外がわの つけねを 内へ・下へ（まさちゃん「耳が散れちゃってる」：つけねの 線が 頭の 外に 出ていた）
NOSTRIL = ((15, 58, 102), 3.8, 5.4, (.35, .1, .93))
BLUSH = ((50, 20, 44), 14, 10, (.7, 0, .7))
BOW = ((0, -96, 10), .8, -.18)                     # リボン：左右の 耳の まん中（まさちゃん「赤丸の位置にリボンの位置合わせて！左右の耳の中央にくるように！」）・大きさ・かたむき（顔の 向きの 何倍）
FORE = [((-44, -80, 30), 23, 17, -18, 1), ((-8, -90, 40), 21, 16, -4, -1), ((28, -84, 34), 20, 15, 14, -1)]   # 前髪の くるくる
MANE = [((-68, -56, -24), 31, 22, -26, 1), ((-82, -16, -30), 39, 27, -14, 1), ((-84, 28, -30), 39, 26, -6, 1),
        ((-78, 70, -26), 37, 24, 0, 1), ((-64, 106, -20), 34, 22, 6, 1)]                 # たてがみ（首の 左がわ だけ。正面の 顔では 頭の うしろ）


def pr(p, th, ph=0.0):
    """3D の 点 → (画面の x, y)・手前への 深さ（th：右へ 回す・ph：上から 見る 角度）"""
    x, y, z = p
    x1, z1 = x * math.cos(th) + z * math.sin(th), -x * math.sin(th) + z * math.cos(th)
    return (x1, y * math.cos(ph) + z1 * math.sin(ph)), -y * math.sin(ph) + z1 * math.cos(ph)


def pr_ell(c, r, th, ph=0.0):
    """だ円の 玉 → 画面の だ円 (x, y, はば, 高さ)"""
    (x, y), _ = pr(c, th, ph)
    rz = math.hypot(r[0] * math.sin(th), r[2] * math.cos(th))
    return x, y, math.hypot(r[0] * math.cos(th), r[2] * math.sin(th)), math.hypot(r[1] * math.cos(ph), rz * math.sin(ph))


def facing(n, th, ph=0.0):
    """向き n の 面が どれだけ こちらを 向くか（1＝まっすぐ こちら）"""
    return -n[1] * math.sin(ph) + (-n[0] * math.sin(th) + n[2] * math.cos(th)) * math.cos(ph)


def flip(p, sd):
    return (p[0] * sd, p[1], p[2])


def cast(cv, sil, under, k=.3, dx=1.5, dy=2.5, sd=3.0, col='#7A1235'):
    """この 部品が 下の 部品（under：同じ 板の 大きさの 不透明度）に 落とす かげを、この 部品の 板の うしろに 入れる（右下へ）"""
    sh = blur(np.roll(np.roll(sil, int(cv.px(dy)), 0), int(cv.px(dx)), 1), cv.px(sd)) * k * np.clip(under, 0, 1)
    cv.under(hexc(col), sh)


def rig(v):
    """動きの 中心（画面の 座標・左右 うらがえす 前）：head＝首の 上（頭が かたむく）・mane＝たてがみの 上の はし・
       earL・earR＝耳の つけね・bow＝リボンの むすびめ"""
    hx, hy = HEAD_C[v]
    K = head_k(v)
    th, ph = math.radians(YAW[v]), math.radians(PITCH[v])
    S = lambda p: (hx + p[0] * K, hy + p[1] * K)
    P3 = lambda p: S(pr(p, th, ph)[0])
    (bx, by, bz), tip, w = EAR
    r = dict(head=P3((0, 40, -18)), mane=P3(MANE[0][0]),
             earL=P3((-(bx + EAR_OUT[0] / 2), by + EAR_OUT[1] / 2, bz)), earR=P3((bx + EAR_OUT[0] / 2, by + EAR_OUT[1] / 2, bz)),
             bow=P3(BOW[0]), hc=(hx, hy))
    return {k: [round(x, 2), round(y, 2)] for k, (x, y) in r.items()}


def legs_layer():
    """うしろ足（顔の 向きに よらない・動かない：ハートの 下から 見える。見えるのは ①②の カメラだけ）"""
    cv = Cv(HEAD_BOX, sc=dens(PC.CAMS[CAM_OF['R']]['z']))
    legs(cv)
    return cv


_PARTS = {}


def pony_parts(v):
    """ポニーの 部品（どれも HEAD_BOX の 板）：neck（首）・mane（たてがみ）・earL・earR（耳）・face（頭と 顔・前髪・ウィンクの ハート）・bow（リボン）。
       まさちゃん「馬もプルンプルン系で、全体的に動いて！…でも身体が歪んだりは変だから構造は身体の構造を考えて作成して！」：
       部品ごとに 別の 絵に して、ページで 体の つくりどおりに 動かす（首の 上を 中心に 頭が かたむく・耳は つけねを 中心に ゆれる…）。
       上の 部品の かげは、下の 部品の 上だけに 落とす（cast）"""
    if v in _PARTS:
        return _PARTS[v]
    hx, hy = HEAD_C[v]
    K = head_k(v)
    th, ph = math.radians(YAW[v]), math.radians(PITCH[v])
    sc = dens(PC.CAMS[CAM_OF[v]]['z'])
    S = lambda p: (hx + p[0] * K, hy + p[1] * K)
    P3 = lambda p: S(pr(p, th, ph)[0])
    out = {}
    nk = Cv(HEAD_BOX, sc=sc)
    neck(nk, v, th, ph)
    out['neck'] = nk
    # たてがみ（首の 左がわ・頭の うしろ）
    mn = Cv(HEAD_BOX, sc=sc)
    for c, rx, ry, rot, sp in MANE:
        curl(mn, *P3(c), rx * K, ry * K, rot, sp)
    cast(mn, grow(mn.img[..., 3].copy(), mn.px(1)), nk.img[..., 3])
    out['mane'] = mn
    # 耳：まっすぐ 上へ のびる 長い 耳（頭の うしろから）
    (bx, by, bz), tip, w = EAR
    for sd, name in ((-1, 'earL'), (1, 'earR')):
        e = Cv(HEAD_BOX, sc=sc)
        ear(e, P3((sd * (bx - w), by, bz)), P3(flip(tip, sd)), P3((sd * (bx + w + EAR_OUT[0]), by + EAR_OUT[1], bz)))
        out[name] = e
    # 頭：まるい 頭・ほお・鼻先（馬の 長い 顔）
    cv = Cv(HEAD_BOX, sc=sc)
    sk, ch, sn = pr_ell(*SKULL, th, ph), pr_ell(*CHEEK, th, ph), pr_ell(*SNOUT, th, ph)
    rot_sn = -14 * math.sin(th) / math.sin(math.radians(35))
    head_svg = (P(oval(*S(sk[:2]), sk[2] * K, sk[3] * K)) + P(oval(*S(ch[:2]), ch[2] * K, ch[3] * K))
                + P(oval(*S(sn[:2]), sn[2] * K, sn[3] * K, rot_sn)))
    a = cv.mask(head_svg)
    fur(cv, a, R=30 * K, lw=2.6)
    # 鼻先の うすい ピンク
    (nx, ny), _ = pr((0, 56, 80), th, ph)
    cv.tint(soft_ell(cv, *S((nx, ny)), sn[2] * .82 * K, sn[3] * .7 * K, rot_sn, 1.0) * a, hexc('#FFD3E7'), .6)
    # ほお
    for sd in (-1, 1):
        f_ = facing(flip(BLUSH[3], sd), th, ph)
        if f_ < .15:
            continue
        x, y = P3(flip(BLUSH[0], sd))
        rx, ry = BLUSH[1] * max(.5, f_) * K, BLUSH[2] * K
        cv.put(hexc('#FF8FC0'), soft_ell(cv, x, y, rx, ry, 0, .9) * .72 * a)
        cv.put(hexc('#FFFFFF'), soft_ell(cv, x - rx * .35, y - ry * .2, rx * .16, rx * .16, 0, .5) * .85 * a)
    # 鼻の あな
    for sd in (-1, 1):
        f_ = facing(flip(NOSTRIL[3], sd), th, ph)
        if f_ < .2:
            continue
        x, y = P3(flip(NOSTRIL[0], sd))
        rx, ry = NOSTRIL[1] * max(.55, f_) * K, NOSTRIL[2] * K
        ring = stroke_mask(cv, oval(x, y, rx, ry, sd * 10, n=12), 2.0)
        cv.put(hexc('#E2729F'), ring * a)
        cv.put(hexc('#F7A6C8'), cv.mask(P(oval(x, y, rx * .7, ry * .7, sd * 10))) * .6 * a)
    # 目（向こうの 目は 細く・頭の 形の 中だけ）：カメラ目線（GAZE）
    eyes = []
    for sd in (-1, 1):
        f_ = facing(flip(EYE[3], sd), th, ph)
        if f_ < .2:
            continue
        x, y = P3(flip(EYE[0], sd))
        eyes.append((sd, x, y, max(.42, min(1.0, f_ * 1.02))))
    near = min(eyes, key=lambda e: abs(e[1] - hx))
    for sd, x, y, kx in eyes:
        if v == 'W' and (sd, x) == near[:2]:
            wink(cv, x, y, EYE[1] * K, EYE[2] * K, sd)
        else:
            eye(cv, x, y, EYE[1] * kx * K, EYE[2] * K, sd, clip=head_svg, gaze=GAZE[v])
    # 前髪
    for c, rx, ry, rot, sp in FORE:
        if pr(c, th, ph)[1] > -12:
            curl(cv, *P3(c), rx * K, ry * K, rot, sp)
    if v == 'W':                                  # 「ちゅ！❤️」：ウィンクの 目の 外に 小さな ハート
        sd, x, y, kx = near
        jx, jy = x + sd * EYE[1] * K * 1.9, y + EYE[2] * K * .1
        jelly_heart(cv.sub(jx - 30, jy - 30, jx + 30, jy + 30), jx, jy, 12 * K, '#FF5FA6', '#FFC2DE', '#DD3484', rot=-16)
    below = np.maximum.reduce([out[k].img[..., 3] for k in ('neck', 'mane', 'earL', 'earR')])
    cast(cv, grow(a, cv.px(2.4)), below)
    out['face'] = cv
    # リボン（左右の 耳の まん中）
    bw = Cv(HEAD_BOX, sc=sc)
    c, bs, br = BOW
    bow(bw, *P3(c), bs * K, br * YAW[v])
    cast(bw, grow(bw.img[..., 3].copy(), bw.px(1)), np.maximum.reduce([out[k].img[..., 3] for k in ('face', 'earL', 'earR')]))
    out['bow'] = bw
    _PARTS.clear()
    _PARTS[v] = out
    return out


def glow(cv, a, w=2.0, s=7.0, k=.85):
    """形の まわりの 白い 光（うしろに 置く）"""
    g = blur(grow(a, cv.px(w)), cv.px(s))
    cv.under(hexc('#FFFFFF'), np.clip(g * 1.25, 0, 1) * k)


# ---------------------------------------------------------------- ハート（まさちゃんの 絵の ハート：ふくらんだ 形・くぼみは 浅い）
HEART_K = ((0, -.5), (-.2, -.94), (-1.0, -1.0), (-1.02, -.4), (-1.04, .12), (-.44, .52), (0, .88))   # 左半分の 3次ベジェ（くぼみ → 左の 山 → とがった 先）


def heart_d(cx, cy, s, ky=1.0):
    """ハートの 形（はばの 半分 s・高さは ky 倍）"""
    p = [(cx + x * s, cy + y * s * ky) for x, y in HEART_K]
    q = [(2 * cx - x, y) for x, y in p]
    return (f'M{f(p[0][0])} {f(p[0][1])} C{f(p[1][0])} {f(p[1][1])} {f(p[2][0])} {f(p[2][1])} {f(p[3][0])} {f(p[3][1])} '
            f'C{f(p[4][0])} {f(p[4][1])} {f(p[5][0])} {f(p[5][1])} {f(p[6][0])} {f(p[6][1])} '
            f'C{f(q[5][0])} {f(q[5][1])} {f(q[4][0])} {f(q[4][1])} {f(q[3][0])} {f(q[3][1])} '
            f'C{f(q[2][0])} {f(q[2][1])} {f(q[1][0])} {f(q[1][1])} {f(q[0][0])} {f(q[0][1])} Z')


FRAME = [(0, '#B51A63'), (.25, '#D9307F'), (.5, '#F2559F'), (.75, '#FF8DC3'), (1, '#FFD3E8')]


def nebula(cv, a, seed, cx, cy, s):
    """虹色の 星空（まさちゃんの 絵の ハートの 中）：右上の 明るい 光の まわりを 虹が 回る・ふちは こい マゼンタ と むらさき・白い 光の くも"""
    gx, gy = cx + s * .12, cy - s * .18                 # 光の まん中
    ang = (np.arctan2(cv.Y - gy, cv.X - gx) / (2 * np.pi) + .5 + .08) % 1.0
    col = ramp(ang, [(0, '#FF2FA8'), (.12, '#FF6A3A'), (.24, '#FFC21F'), (.36, '#FFF04A'), (.48, '#6CF05A'), (.6, '#22D8E8'), (.72, '#3A6BFF'),
                     (.84, '#9A3CFF'), (1, '#FF2FA8')])
    r = np.sqrt(((cv.X - gx) / (s * .95)) ** 2 + ((cv.Y - gy) / (s * .85)) ** 2)
    sat = np.clip(r * 1.6, 0, 1)[..., None]
    col = hexc('#FFFBEA') * (1 - sat) + col * sat                                 # まん中は 白く 明るい
    rnd = np.random.default_rng(seed)
    H, W = a.shape
    for c, amp, sc_ in (('#FFFFFF', .32, 26), ('#FF8BE0', .22, 18), ('#FFFFFF', .2, 10)):
        nz = rnd.random((max(6, H // sc_), max(6, W // sc_))).astype(np.float32)
        nz = blur(cv2.resize(nz, (W, H), interpolation=cv2.INTER_CUBIC), cv.px(3))
        m = (np.clip((nz - .52) * 4, 0, 1) * amp * np.clip(r * 1.2, 0, 1))[..., None]
        col = col * (1 - m) + hexc(c) * m
    vig = np.clip((r - .75) / .6, 0, 1)[..., None]
    col = col * (1 - vig * .5) + hexc('#7A1690') * vig * .5
    cv.put(col, a)


def big_heart(cv, cx, cy, s, seed=7):
    """つやつやの 大きな ハート：こい 赤の ふち・ふくらんだ こい ピンクの わく（つや）・中に 白い 線・虹色の 星空と キラキラ・ガラスの つや"""
    outer = cv.mask(P(heart_d(cx, cy, s, HEART_KY)))
    ic = (cx, cy + s * .03)
    si = s * .84
    inner = cv.mask(P(heart_d(ic[0], ic[1], si, HEART_KY)))
    drop(cv, grow(outer, cv.px(3.4)), dx=0, dy=5, s=6, k=.5)
    outline(cv, outer, 3.4)
    # わく：外の ふちと 中の ふちの あいだの ふくらみ
    do, di = dist_in(outer), dist_out(inner)
    u = np.clip(do / np.maximum(do + di, 1e-3), 0, 1)
    h = blur((np.sin(np.pi * np.clip(u * .9 + .05, 0, 1)) ** .55).astype(np.float32), cv.px(1.6))
    n = normals(h, cv.px(s * .09))
    d, sp = lit(n, 30)
    frame = np.clip(outer - inner, 0, 1)
    cv.put(ramp(np.clip(.06 + 1.0 * d, 0, 1), FRAME), outer)
    rimv = np.clip(n[..., 0] * .45 + n[..., 1] * .85, 0, 1) * np.clip(1 - n[..., 2], 0, 1)
    cv.add(hexc('#FFC2E0'), rimv * .6 * frame)
    cv.put(hexc('#FFFFFF'), np.clip(sp * 1.4, 0, 1) * .7 * frame)
    # 中の 星空
    nebula(cv, inner, seed, ic[0], ic[1], si)
    glitter(cv, inner, 320, seed + 1, r=(.35, 1.1), op=(.45, 1.0))
    glitter(cv, inner, 26, seed + 2, r=(1.6, 3.4), op=(.7, 1.0), star=1.0)
    for bx, by, br, op in ((-.45, -.35, .1, .35), (.42, -.42, .08, .3), (.3, .25, .12, .25), (-.25, .3, .07, .3), (.05, -.6, .06, .35)):
        cv.put(hexc('#FFFFFF'), soft_ell(cv, cx + bx * s, cy + by * s, br * s, br * s, 0, .25) * op * inner)
    # 中の ふち：こい 赤の 線と 白い 線
    ring = np.clip(grow(inner, cv.px(2.2)) - inner, 0, 1)
    cv.put(OUT, ring)
    wl = np.clip(inner - np.clip((dist_in(inner) - cv.px(1.6)) / cv.px(1.2), 0, 1), 0, 1) * inner
    cv.put(hexc('#FFFFFF'), np.clip(dist_in(inner) / cv.px(.8), 0, 1) * wl * .85)
    # わくの つや：左上の 大きな 光（わくの まん中の すじ）・右の 山の 光・下の 小さな 光・点
    mid = stroke_mask(cv, heart_d(cx, cy + s * .015, s * .92, HEART_KY), s * .05)
    cv.put(hexc('#FFFFFF'), np.clip(soft_ell(cv, cx - s * .62, cy - s * .55, s * .5, s * .32, -38, .7) * 1.4, 0, 1) * blur(mid, cv.px(.6)) * .95)
    mid2 = stroke_mask(cv, heart_d(cx, cy + s * .015, s * .92, HEART_KY), s * .032)
    cv.put(hexc('#FFFFFF'), np.clip(soft_ell(cv, cx + s * .55, cy - s * .72, s * .3, s * .18, 20, .7) * 1.4, 0, 1) * blur(mid2, cv.px(.5)) * .85)
    cv.put(hexc('#FFFFFF'), np.clip(soft_ell(cv, cx + s * .62, cy + s * .2, s * .22, s * .14, -48, .8) * 1.3, 0, 1) * blur(mid2, cv.px(.5)) * .5)
    for px_, py_, r_ in ((-.93, -.12, .03), (.14, -.83, .026), (-.2, .72, .02)):
        cv.put(hexc('#FFFFFF'), soft_ell(cv, cx + px_ * s, cy + py_ * s * HEART_KY, s * r_, s * r_, 0, .4) * .95)
    # 星空の 上の うすい ガラスの 光（左上）
    cv.put(hexc('#FFFFFF'), soft_ell(cv, cx - s * .42, cy - s * .42, s * .3, s * .12, -40, 1.0) * .35 * inner)
    return outer


def heart_layer():
    """ハート（①〜⑤で 同じ 絵：いちばん アップの カメラで くっきり）"""
    cv = Cv(HEART_BOX, sc=dens(ZMAX))
    big_heart(cv, HC[0], HC[1], HS)
    return cv


def hooves():
    """前足（ハートの 前）：首の 横の 肩から ハートの 山の 前を ななめに おりて、ひづめで ハートの 左右の ふちを 上から つかむ
       （肩・うで・手首の ふわふわの 毛・うすい ピンクの つやつやの ひづめ・ハートに 落ちる かげ）。
       まさちゃん「ハートの持ち方が手が下から入ってるから変！上から持って！首から手の位置まで、肩を入れたり自然にして！」"""
    cv = Cv(HOOF_BOX, sc=dens(ZMAX))
    cuff = [(0, '#E7B3D2'), (.4, '#F7D9EA'), (.7, '#FFFFFF'), (1, '#FFFFFF')]
    on_heart = grow(cv.mask(P(heart_d(HC[0], HC[1], HS, HEART_KY))), cv.px(4))
    for side in (-1, 1):
        x, y = HC[0] + side * HOOF_X, HOOF_Y
        rot = hoof_rot(side)
        hm = cv.mask(P(oval(x, y, HOOF_R * .9, HOOF_R * 1.08, rot)))
        am = cv.mask(P(arm_d(side)))
        # ふわふわの 毛（ひづめの すぐ 上・うでの 向き：下の ふちが ぎざぎざ）
        R0 = HOOF_R
        pts = [(-.78, .1), (-.82, -.32), (-.5, -.62), (0, -.7), (.5, -.62), (.82, -.32), (.78, .1),
               (.6, .3), (.4, .16), (.2, .34), (0, .2), (-.2, .34), (-.4, .16), (-.6, .3)]
        cx, cy = rot_pt(x, y, 0, -R0 * .78, rot)
        cm = cv.mask(P(smooth(tf([(px * R0, py * R0) for px, py in pts], cx, cy, 1.0, rot))))
        # ハートに 落ちる かげ（右下へ）
        sh = blur(np.roll(np.roll(grow(np.maximum(np.maximum(hm, cm), am), cv.px(2.6)), int(cv.px(3.5)), 0), int(cv.px(2)), 1), cv.px(3))
        cv.put(hexc('#6E1030'), sh * on_heart * .3)
        fur(cv, am, R=14, lw=2.4)
        gloss_ball(cv, x, y, HOOF_R * .9, HOOF_R * 1.08, rot, cols=[(0, '#D66A9C'), (.35, '#EC98C0'), (.7, '#F8C6DD'), (1, '#FFEAF4')],
                   lw=2.6, sh=0)
        drop(cv, grow(cm, cv.px(2.2)), k=.3)
        fur(cv, cm, R=7, lw=2.2, cols=cuff)
    return cv


# ---------------------------------------------------------------- オーラ（まさちゃん「馬とハートが登場してプルルンと揺れる時に、光沢があるピンクと白のオーラが
# 全体的に馬とハートから出るようにして！」）：ポニーと ハートの 形の まわりの つやつやの ピンクの わ（ゼリー）と、白 → ピンクの やわらかい 光。
# ページで 着地の 時に 外へ 広がりながら 消える（pm_aura_…：顔の 向きごと。ハートは その カメラの かたむきで 入れる）
AURA_BOX = (-80.0, -10.0, 550.0, 830.0)
_LEGS = {}


def tilt_pt(x, y, ry, rx, fs=1.0, P=PC.PERSP):
    """ハートの 面の 点（ハートの まん中から の ずれ）→ 世界の 点。ページの transform:perspective(P) rotateX(rx) rotateY(ry) scale(fs)
       （ハートの まん中が 中心）と 同じ"""
    b, a = math.radians(ry), math.radians(rx)
    x, y = x * fs, y * fs
    x1, z1 = x * math.cos(b), -x * math.sin(b)
    y2, z2 = y * math.cos(a) - z1 * math.sin(a), y * math.sin(a) + z1 * math.cos(a)
    w = 1 - z2 / P
    return HC[0] + x1 / w, HC[1] + y2 / w


def resample(alpha, src_box, src_sc, cv):
    """ほかの 板（src_box・src_sc）の 不透明度を この 板の 画素に"""
    s = src_sc / cv.sc
    tx = (cv.box[0] - src_box[0]) * src_sc + .5 * s - .5
    ty = (cv.box[1] - src_box[1]) * src_sc + .5 * s - .5
    M = np.float32([[s, 0, tx], [0, s, ty]])
    return cv2.warpAffine(alpha, M, (cv.W, cv.H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderValue=0)


def front_mask(cv):
    """ハートと 前足の 形（ふちまで）"""
    a = grow(cv.mask(P(heart_d(HC[0], HC[1], HS, HEART_KY))), cv.px(3.4))
    for side in (-1, 1):
        x, y = HC[0] + side * HOOF_X, HOOF_Y
        hm = cv.mask(P(oval(x, y, HOOF_R * .9, HOOF_R * 1.08, hoof_rot(side))))
        am = cv.mask(P(arm_d(side)))
        a = np.maximum(a, grow(np.maximum(hm, am), cv.px(2.6)))
    return a


def front_tilted(cv, ry, rx, fs=1.0):
    """ハートと 前足の 形を カメラの かたむきで（この 板の 上に）"""
    pl = Cv(HEART_BOX, sc=cv.sc)
    m = front_mask(pl)
    bx, by = pl.box[0], pl.box[1]
    src, dst = [], []
    for u, v in ((0, 0), (pl.W - 1, 0), (pl.W - 1, pl.H - 1), (0, pl.H - 1)):
        X, Y = bx + (u + .5) / pl.sc, by + (v + .5) / pl.sc
        x2, y2 = tilt_pt(X - HC[0], Y - HC[1], ry, rx, fs)
        src.append((u, v))
        dst.append(((x2 - cv.box[0]) * cv.sc - .5, (y2 - cv.box[1]) * cv.sc - .5))
    H = cv2.getPerspectiveTransform(np.float32(src), np.float32(dst))
    return cv2.warpPerspective(m, H, (cv.W, cv.H), flags=cv2.INTER_LINEAR, borderValue=0)


def aura_layer(v):
    """オーラ（顔の 向き v の ポニー（とその カメラで かたむいた ハート・前足・見えれば うしろ足）の まわり）"""
    cam = PC.CAMS[CAM_OF[v]]
    cv = Cv(AURA_BOX, sc=dens(cam['z']) * .6)
    parts = pony_parts(v)
    sc_v = parts['face'].sc
    U = resample(np.maximum.reduce([parts[k].img[..., 3] for k in PART_NAMES]), HEAD_BOX, sc_v, cv)
    if cam['legs']:
        if 'cv' not in _LEGS:
            _LEGS['cv'] = legs_layer()
        lg = _LEGS['cv']
        U = np.maximum(U, resample(lg.img[..., 3], HEAD_BOX, lg.sc, cv))
    U = np.maximum(U, front_tilted(cv, cam['ry'], cam['rx'], cam['fs']))
    # 外の ふちだけの 形（まつげ・すきまの 穴は うめる：広がる 時に 黒い すじや 中の わが 見えないように）
    m = (blur(np.clip(U, 0, 1).astype(np.float32), cv.px(1.5)) > .35).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    fill = np.zeros_like(m)
    cv2.drawContours(fill, cs, -1, 1, -1)
    U = blur(fill.astype(np.float32), cv.px(.6))
    d = dist_out(U) / cv.sc                                             # 形の 外への きょり（世界の px）
    out = np.clip(1 - U, 0, 1)
    # つやつやの ピンクの わ（ゼリー：ふくらみ・左上の 白い つや・右下の 光）と、わの まわりの 白 → ピンクの やわらかい 光
    # （形の すぐ まわりの 光は ページの drop-shadow：ここで 広く 光らせると、広がる 時に 点めつが ふえる）
    d0, W = 5.0, 12.0
    g = np.exp(-np.abs(d - (d0 + W * .5)) / 5.0) * out
    cv.put(ramp(np.clip((d - d0) / W, 0, 1), [(0, '#FFFFFF'), (.4, '#FFD2E8'), (1, '#FF8CC6')]), g * .45)
    u = np.clip((d - d0) / W, 0, 1).astype(np.float32)
    band = np.clip(np.minimum(d - d0, d0 + W - d) / 1.3, 0, 1).astype(np.float32)
    h = (np.clip(np.sin(np.pi * u), 0, 1) ** .65).astype(np.float32)
    n = normals(blur(h, cv.px(.6)), cv.px(W) * .5)
    dd, sp = lit(n, 26)
    cv.put(ramp(np.clip(.1 + .95 * dd, 0, 1), [(0, '#E23A8A'), (.45, '#FF7FBF'), (.8, '#FFC6E2'), (1, '#FFF1F8')]), band * .92)
    rimv = np.clip(n[..., 0] * .45 + n[..., 1] * .85, 0, 1) * np.clip(1 - n[..., 2], 0, 1)
    cv.add(hexc('#FFE3F1'), rimv * .5 * band)
    cv.put(hexc('#FFFFFF'), np.clip(sp * 1.6, 0, 1) * .95 * band)
    # わの まん中の 白い すじ（光沢）
    mid = np.clip(1 - np.abs(d - (d0 + W * .38)) / 1.4, 0, 1)
    ex, ey = edge_dir(U, cv.px(4))
    face_l = np.clip(-(ex * LIGHT[0] + ey * LIGHT[1]) * 1.2, 0, 1)
    cv.put(hexc('#FFFFFF'), mid * face_l * .8 * band)
    glitter(cv, band, 70, 40 + FACES.index(v), r=(.7, 2.0), op=(.7, 1.0), star=.6)
    glitter(cv, np.clip(g * 1.6, 0, 1) * out, 50, 50 + FACES.index(v), r=(1.2, 3.0), op=(.6, 1.0), star=1.0)
    ys, xs = np.nonzero(U > .5)
    _AURA_C[v] = (round(float(cv.box[0] + (xs.min() + xs.max() + 1) / 2 / cv.sc), 2),
                  round(float(cv.box[1] + (ys.min() + ys.max() + 1) / 2 / cv.sc), 2))
    return cv


_AURA_C = {}


def aura_center(v):
    """オーラが 広がる 中心（ポニーと ハートの 形の 箱の まん中・世界の 座標）"""
    if v not in _AURA_C:
        aura_layer(v)
    return list(_AURA_C[v])


# ---------------------------------------------------------------- 字（ど！ など：PC.GLYPHS の 線を 太く・虹色・つや）
def word(cv, text, cx, cy, s, w=17.0, gap=-4, seed=3):
    d, total, balls = PC.word_d(text, cx, cy, s, gap)
    W = w * s
    sh = stroke_mask(cv, d, W + 18 * s)
    cv.tint(blur(np.roll(sh, int(cv.px(4 * s)), 0), cv.px(2.5 * s)), hexc('#6E1030'), .55)
    cv.put(hexc('#6E1030'), blur(np.roll(sh, int(cv.px(3 * s)), 0), cv.px(1.2 * s)) * .5)
    o = stroke_mask(cv, d, W + 17 * s)
    ex, ey = edge_dir(o, cv.px(1.5 * s))
    face = np.clip(-(ex * LIGHT[0] + ey * LIGHT[1]), 0, 1)
    cv.put(OUT[None, None, :] + (OUT_HI - OUT)[None, None, :] * (face * .45)[..., None], o)
    m1 = stroke_mask(cv, d, W + 11 * s)
    h1 = height(m1, cv.px(3 * s), soft=.3)
    d1, _ = lit(normals(h1, cv.px(3 * s)), 20)
    cv.put(ramp(np.clip(.1 + .95 * d1, 0, 1), [(0, '#C42A72'), (.5, '#EE4C97'), (1, '#FF9CCB')]), m1)
    m2 = stroke_mask(cv, d, W + 5 * s)
    cv.put(hexc('#FFE0EF'), m2)
    m3 = stroke_mask(cv, d, W)
    t = np.clip((cv.Y - (cy - 50 * s)) / (100 * s), 0, 1)
    col = ramp(t, [(0, '#FF3D7A'), (.18, '#FF8A2E'), (.34, '#FFE03A'), (.5, '#5FE07A'), (.66, '#2FCBFF'), (.84, '#4F6BFF'), (1, '#A04CFF')])
    h3 = height(m3, cv.px(W * .5), soft=.3)
    n3 = normals(h3, cv.px(W * .35))
    d3, s3 = lit(n3, 30)
    shade = np.clip(.55 + .6 * d3, 0, 1.1)[..., None]
    cv.put(np.clip(col * shade, 0, 1), m3)
    glitter(cv, m3, int(total * 1.2), seed, r=(.3, .9), op=(.5, 1.0))
    cv.put(hexc('#FFFFFF'), np.clip(s3 * 1.6, 0, 1) * .8 * m3)
    hl = stroke_mask(cv, d, W * .28)
    hl = np.roll(np.roll(hl, -int(cv.px(2.4 * s)), 0), -int(cv.px(1.6 * s)), 1) * m3
    cv.put(hexc('#FFFFFF'), blur(hl, cv.px(.5)) * .7)
    for bx, by, br in balls:
        gloss_ball(cv, bx, by, br * 1.05, br * 1.05, 0, lw=2.4 * s / 1.3 + 1, sh=.45)
    return cv


def text_layer(i):
    text, _, _, s_txt = PC.SCREENS[i]
    cv = Cv(HEART_BOX, sc=dens(PC.CAMS[i]['z'] * 1.05))      # その 画面の カメラで くっきり（かたむけて 手前が 少し 大きくなる 分も）
    word(cv, text, HC[0], HC[1] - 6, s_txt * HS / 150, w=17, gap=2, seed=10 + i)
    return cv


# ---------------------------------------------------------------- 背景（パチンコの 大当たりのような 派手な 虹色）
BG_C = PC.BG_C                                    # 光の まん中（顔と ハートの あいだ）


def hsv_rainbow(h):
    """色相 h（0〜1）→ あざやかな 虹（赤 → だいだい → 黄 → 緑 → 水色 → 青 → むらさき → ピンク）"""
    return ramp(h % 1.0, [(0, '#FF1F5A'), (.1, '#FF6A1F'), (.2, '#FFD21F'), (.32, '#7BEA1F'), (.44, '#1FE07A'), (.54, '#1FD8F0'),
                          (.66, '#2F6BFF'), (.78, '#8A2FFF'), (.9, '#FF2FD0'), (1, '#FF1F5A')])


def sakura_d(cx, cy, r, rot=0.0):
    """さくら（5まいの 花びら）"""
    out = ''
    for i in range(5):
        a = rot + i * 72
        pts = tf([(0, 0), (-r * .55, -r * .22), (-r * .62, -r * .86), (-r * .2, -r * .98), (0, -r * .84), (r * .2, -r * .98), (r * .62, -r * .86), (r * .55, -r * .22)],
                 cx, cy, 1, a)
        out += f'<path d="M{f(pts[0][0])} {f(pts[0][1])} C{f(pts[1][0])} {f(pts[1][1])} {f(pts[2][0])} {f(pts[2][1])} {f(pts[3][0])} {f(pts[3][1])} ' \
               f'L{f(pts[4][0])} {f(pts[4][1])} L{f(pts[5][0])} {f(pts[5][1])} C{f(pts[6][0])} {f(pts[6][1])} {f(pts[7][0])} {f(pts[7][1])} {f(pts[0][0])} {f(pts[0][1])}Z"/>'
    return out


def background():
    """虹色の 大当たり：まん中の 白い 光から あざやかな 虹の 光線（太い 光線と 明るい 光線）・虹の 輪・ふちは こい むらさき・
       さくら・花びら・光の 玉・キラキラ（止まった 絵。動く 光線と キラキラは ページの CSS）"""
    cv = Cv((0, 0, 390, 844), sc=2)
    cx, cy = BG_C
    dx, dy = cv.X - cx, cv.Y - cy
    r = np.sqrt(dx * dx + dy * dy)
    th = (np.arctan2(dy, dx) / (2 * np.pi)) % 1.0
    N = 20                                         # 光線の 数
    ray = (th * N) % 1.0
    band = np.clip(np.abs(ray - .5) * 2, 0, 1)    # 0＝光線の まん中・1＝光線の あいだ
    hue = (th * 2 + r / 900) % 1.0                 # 色は 2回 回る＋外へ 少し ずれる
    col = hsv_rainbow(hue)
    light = np.clip((.5 - band) / .05 + .5, 0, 1)[..., None]                  # 明るい 光線（くっきり）
    col = col * (1 - light * .5) + hexc('#FFFFFF') * light * .5
    deep = np.clip((band - .55) / .3, 0, 1)[..., None]                        # 光線の あいだは こい 色
    col = col * (1 - deep * .28)
    # まん中の 白い 光（白 → 金色 → 虹）
    core = np.exp(-(r / 120) ** 2)[..., None]
    halo = np.exp(-(r / 230) ** 2)[..., None]
    col = col * (1 - halo * .5) + hexc('#FFF4C2') * halo * .5
    col = col * (1 - core) + hexc('#FFFFFF') * core
    # 虹の 輪（光る 細い 輪 2つ）
    for R0, w, k in ((262, 9, .75), (372, 7, .55)):
        ring = np.exp(-((r - R0) / w) ** 2)[..., None]
        col = col * (1 - ring * k) + (hsv_rainbow(th + .15) * .45 + .55) * ring * k
    # ふちの こい むらさき（画面の 外がわ）
    ex = np.sqrt(((cv.X - 195) / 230) ** 2 + ((cv.Y - 430) / 470) ** 2)
    vig = np.clip((ex - .78) / .55, 0, 1)[..., None]
    col = col * (1 - vig * .45) + hexc('#4A0C6E') * vig * .45
    cv.img[..., :3] = col
    cv.img[..., 3] = 1
    # さくら・花びら（白と ピンク）・光の 玉・キラキラ
    rnd = random.Random(31)
    for x, y, rr, c, op in ((34, 92, 34, '#FFFFFF', .85), (352, 128, 40, '#FFE3F1', .85), (22, 760, 38, '#FFFFFF', .8), (366, 742, 44, '#FFD0E8', .85),
                            (300, 36, 24, '#FFFFFF', .75), (80, 818, 26, '#FFE3F1', .8), (376, 430, 22, '#FFFFFF', .7), (12, 420, 20, '#FFE3F1', .7),
                            (196, 820, 22, '#FFFFFF', .7), (120, 30, 18, '#FFE3F1', .75)):
        m = cv.mask(sakura_d(x, y, rr, rnd.uniform(0, 72)))
        cv.put(hexc('#D94C93'), blur(grow(m, cv.px(1.2)), cv.px(.6)) * .55 * op)
        sh = blur(m, cv.px(rr * .2))
        cv.put(hexc(c), m * op)
        cv.tint(soft_ell(cv, x, y, rr * .55, rr * .55, 0, 1.0) * m, hexc('#FF9CC9'), .5)
        cv.put(hexc('#FFF06A'), soft_ell(cv, x, y, rr * .16, rr * .16, 0, .5) * op)
    for i in range(26):
        x, y, rr = rnd.uniform(0, 390), rnd.uniform(0, 844), rnd.uniform(4, 8)
        m = cv.mask(f'<path d="M0 {f(rr)} C{f(-rr * .8)} {f(rr * .3)} {f(-rr * .6)} {f(-rr * .7)} {f(-rr * .15)} {f(-rr)} L0 {f(-rr * .78)} L{f(rr * .15)} {f(-rr)} '
                    f'C{f(rr * .6)} {f(-rr * .7)} {f(rr * .8)} {f(rr * .3)} 0 {f(rr)}Z" transform="translate({f(x)} {f(y)}) rotate({rnd.uniform(0, 360):.0f})"/>')
        cv.put(hexc(rnd.choice(('#FFFFFF', '#FFD6EA', '#FFC0DC'))), m * .9)
    for i in range(40):                           # 光の 玉（ボケ）
        x, y, rr = rnd.uniform(0, 390), rnd.uniform(0, 844), rnd.uniform(5, 22)
        c = hsv_rainbow(np.array([rnd.random()]))[0] * .4 + .6
        cv.put(c, soft_ell(cv, x, y, rr, rr, 0, .35) * rnd.uniform(.25, .5))
    full = np.ones((cv.H, cv.W), np.float32)
    glitter(cv, full, 900, 5, r=(.4, 1.1), op=(.4, 1.0))
    glitter(cv, full, 70, 6, r=(2.0, 4.6), op=(.7, 1.0), star=1.0)
    return cv



# ---------------------------------------------------------------- つやつやの ゼリーの ハート（つもる・とぶ・のぼる 小さな ハート）と 最後の「ど的中」
JELLY_PX = 192                                    # 1つの ハートの 大きさ（画素）


def jelly_heart(cv, cx, cy, s, fill, light, deep, rot=0.0, lw=None):
    """つやつやの ゼリーの ハート：こい 赤の ふち・ふくらみ・左上の 大きな 白い つや・右下の 光"""
    from art import heart as heart0
    d = heart0(0, 0, s)
    a = cv.mask(f'<path d="{d}" transform="translate({f(cx)} {f(cy)}) rotate({f(rot)})"/>')
    outline(cv, a, lw or max(1.2, s * .085))
    h = height(a, cv.px(s * .55), soft=.3)
    n = normals(h, cv.px(s * .5))
    dd, sp = lit(n, 30)
    cv.put(ramp(np.clip(.08 + .95 * dd, 0, 1), [(0, deep), (.55, fill), (1, light)]), a)
    rimv = np.clip(n[..., 0] * .45 + n[..., 1] * .85, 0, 1) * np.clip(1 - n[..., 2], 0, 1)
    cv.add(hexc('#FFE6F3'), rimv * .55 * a)
    cv.put(hexc('#FFFFFF'), np.clip(sp * 1.4, 0, 1) * .7 * a)
    hx, hy = rot_pt(cx, cy, -.48 * s, -.5 * s, rot)
    cv.put(hexc('#FFFFFF'), np.clip(soft_ell(cv, hx, hy, .27 * s, .15 * s, -38 + rot, .45) * 1.6, 0, 1) * .92 * a)
    px_, py_ = rot_pt(cx, cy, -.16 * s, -.68 * s, rot)
    cv.put(hexc('#FFFFFF'), soft_ell(cv, px_, py_, .07 * s, .07 * s, 0, .5) * .9 * a)
    return a


def jelly_sheet():
    """6色の ゼリーの ハート（よこに ならべた 1まい：1つ JELLY_PX 画素の ます）"""
    n = len(PC.PILE_COLS)
    cv = Cv((0, 0, n * 2.24, 2.24), sc=JELLY_PX / 2.24)
    for k, (fill, light, deep) in enumerate(PC.PILE_COLS):
        jelly_heart(cv, k * 2.24 + 1.12, 1.16, .96, fill, light, deep, lw=.07)
    return cv


def final_layer():
    """最後の 大きな ハート：つやつやの ハートに 虹色の「ど的中」・右上に 小さな ゼリーの ハート・まわりの 白い 光"""
    cv = Cv(PC.FIN_BOX)
    cx, cy = PC.FIN_C
    s = PC.FIN_S
    big_heart(cv, cx, cy, s, seed=17)
    word(cv, 'ど的中', cx - 4, cy - 6, .98 * s / 165, w=14, gap=-4, seed=19)
    jelly_heart(cv, cx + s * .76, cy - s * .55, 23, '#FF5FA6', '#FFC2DE', '#DD3484', rot=14)
    glow(cv, np.maximum(cv.img[..., 3], cv.mask(P(heart_d(cx, cy, s, HEART_KY)))))
    return cv



# ---------------------------------------------------------------- 書き出し
FACES = ('R', 'T', 'W', 'F')                                       # 顔の 向き（左向き・やや左は ページで 左右 うらがえす）
PART_NAMES = ('neck', 'mane', 'earL', 'earR', 'face', 'bow')


def legs_cached():
    if 'cv' not in _LEGS:
        _LEGS['cv'] = legs_layer()
    return _LEGS['cv']


def _layers():
    """書き出す 絵の 名前 → 作る 関数（顔の 向きごとに 部品 → オーラ の 順：同じ 顔の 部品を 1回で 作る）"""
    L = dict(pm_legs=legs_cached)
    for v in FACES:
        for p in PART_NAMES:
            L[f'pm_{p}_{v}'] = lambda p=p, v=v: pony_parts(v)[p]
        L[f'pm_aura_{v}'] = lambda v=v: aura_layer(v)
    L.update(pm_heart=heart_layer, pm_hoof=hooves, **{f'pm_t{i}': (lambda i=i: text_layer(i)) for i in range(5)},
             pm_fin=final_layer, pm_bg=background, pm_jelly=jelly_sheet)
    return L


LAYERS = _layers()
NO_CROP = ('pm_bg', 'pm_jelly')


def crop(cv):
    """すき通しで ない 所だけに 切る → (板, 箱)"""
    ys, xs = np.nonzero(cv.img[..., 3] > 1 / 255)
    Y0, Y1, X0, X1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    c = cv.sub(cv.box[0] + X0 / cv.sc, cv.box[1] + Y0 / cv.sc, cv.box[0] + X1 / cv.sc, cv.box[1] + Y1 / cv.sc)
    return c, [round(v, 3) for v in c.box]


def main(out, names):
    """絵を out に 書き出して、箱（と 動きの 中心 rig）を premium_layers.json（premium_cute.py の となり）に 書く（ほかの 名前の 箱は そのまま）"""
    import json
    fn_json = os.path.join(HERE, '..', 'premium_layers.json')
    boxes = json.load(open(fn_json)) if os.path.exists(fn_json) else {}
    for name in names:
        cv = LAYERS[name]()
        if name in NO_CROP:
            box = [round(v, 3) for v in cv.box]
        else:
            cv, box = crop(cv)
        cv.save(os.path.join(out, name + '.webp'), q=90)
        boxes[name] = box
        print(name, box, os.path.getsize(os.path.join(out, name + '.webp')))
    rigs = {v: dict(rig(v), aura=aura_center(v)) for v in FACES}
    rigs['heart'] = [round(HC[0], 2), round(HC[1] + HOOF_AT[1], 2)]                 # ハートが ぷるんっと する 中心（前足で 持っている 所）
    with open(fn_json, 'w', encoding='utf-8') as fh:
        fh.write('{' + ',\n '.join(f'"{k}": [{", ".join(repr(v) for v in boxes[k])}]' for k in LAYERS if k in boxes)
                 + ',\n "rig": ' + json.dumps(rigs, ensure_ascii=False) + '}\n')


if __name__ == '__main__':
    if sys.argv[1] == '--boxes':
        print(dict(HEAD_BOX=HEAD_BOX, HEART_BOX=HEART_BOX, HOOF_BOX=HOOF_BOX, FIN_BOX=PC.FIN_BOX))
    else:
        main(sys.argv[1], sys.argv[2:] or list(LAYERS))
