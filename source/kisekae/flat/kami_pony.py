"""超神様的中の 昇格：バグ → 1秒 まっ暗 → 超プレミアムど的中の ポニーに 隕石が 向かって くる（1.6秒・48コマ・1170×2532）→ 宇宙の カットイン
   まさちゃん「ブラックアウトした後に、超プレミアムど的中の馬に目掛けて、隕石が向かっている演出追加して！」
   絵：超プレミアムど的中（super_premium.py）の ピンクの 画面（水玉・光の 筋・まん中の 光・キラキラ）と 鉛筆の 線の ポニーを そのまま 使い、
       字の ない ハートを だいて びっくり した 顔（目を 見ひらいて 右上の 隕石を 見る・口を あける・あせ・ガーンの 線）。紙の ざらざらも 同じ。
       右上の 空から 燃える 隕石が ポニーに 向かって 近づいて くる（だんだん 大きく・空が だんだん 赤く・ポニーは ぶるぶる・少しずつ よる）
   点めつ：まっ暗から ふっと 明るく（5コマ）・ぶるぶるは 2画素・空の 赤は ゆっくり。隕石は 小さい 所だけ
   絵の 層は ブラウザ（Playwright の Chromium）で 1回だけ 写す（背景・ポニー・紙の ざらざら：<出力>/layers）→ コマは numpy で 重ねる
   python3 flat/kami_pony.py <出力フォルダ> [コマ番号（1〜）…] → p001.png …（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, K)

W, H = 1170, 2532
S = 3.0                                 # 画面の px（390×844）→ 絵の 画素
FPS, N = 30, 48
FADE = 5                                # まっ暗から ふっと 明るく（コマ）
FACE = (195.0, 262.0)                   # ポニーの 顔（画面の px）
SHIVER = (2.0, 5.0)                     # ぶるぶる（絵の 画素・回/秒）
PUSH = 1.07                             # だんだん よる（さいごの 大きさ）


# ---------------------------------------------------------------- 絵の 層（超プレミアムの 絵の しくみで 作って ブラウザで 写す）
def head_shock():
    """びっくり した 顔（正面）：目を 見ひらいて 右上を 見る・まゆが 上がる・口を あける・ほっぺ"""
    import super_premium as SP
    import cute as C
    from art import smooth, ellipse_pts, f
    path, outlined, LINE = SP.path, SP.outlined, SP.LINE
    head = smooth(ellipse_pts(80, 47, 30, 27, 14))
    muzzle = smooth(ellipse_pts(80, 64, 16, 12.5, 12))
    out = outlined([head, muzzle], '#FFFFFF', LINE, 2.2)
    out += path(smooth(ellipse_pts(80, 65, 12.5, 9.4, 12)), fill='#FFE4EE')
    out += '<ellipse cx="75.6" cy="61.6" rx="1.7" ry="2.3" fill="#C0607F"/><ellipse cx="84.4" cy="61.6" rx="1.7" ry="2.3" fill="#C0607F"/>'
    out += path(smooth(ellipse_pts(80, 70.2, 4.0, 4.9, 10)), fill='#8A2B4F', stroke=LINE, stroke_width='1.3')     # あいた 口
    out += '<ellipse cx="80" cy="72.6" rx="2.5" ry="1.5" fill="#FF7FA8"/>'
    out += '<ellipse cx="62" cy="58" rx="5.4" ry="3.2" fill="#FF9FC4" opacity=".7"/><ellipse cx="98" cy="58" rx="5.4" ry="3.2" fill="#FF9FC4" opacity=".7"/>'
    for ex, side in ((68.5, -1), (91.5, 1)):                                                                   # 見ひらいた 目（白目に 小さな 黒目：右上を 見る）
        out += path(smooth(ellipse_pts(ex, 44.5, 8.2, 9.6, 14)), fill='#FFFFFF', stroke='#3A1F2B', stroke_width='1.6')
        out += f'<ellipse cx="{f(ex + 1.9)}" cy="{f(42.0)}" rx="3.6" ry="4.3" fill="#3A1F2B"/>'
        out += f'<circle cx="{f(ex + 2.9)}" cy="{f(40.4)}" r="1.25" fill="#fff"/>'
        lash = f'M{f(ex + side * 7.2)} {f(37.6)} l{f(side * 3.6)} -3.4 M{f(ex + side * 8.4)} {f(41.2)} l{f(side * 4.2)} -1.8'
        out += path(lash, fill='none', stroke='#3A1F2B', stroke_width='1.6', stroke_linecap='round')
        out += path(f'M{f(ex - 6)} {f(29.4)} Q{f(ex)} {f(25.2)} {f(ex + 6)} {f(29.0)}', fill='none', stroke='#A8416F', stroke_width='1.8', stroke_linecap='round')
    out += C.pony_mane(SP.FRONT_CURLS, ((54, 28, 4.6), (49, 40, 4.8), (49, 52, 4.5), (72, 18, 3.8))) + SP.gloss_curls(SP.FRONT_CURLS[:5])
    out += C.pony_ears((((59, 27), (55, 5), (70, 19)), ((101, 27), (105, 5), (90, 19))),
                       (((61, 22), (58, 10), (67, 18)), ((99, 22), (102, 10), (93, 18))), bow_at=(64, 14))
    out += path('M112 33 Q116.5 41.5 112.8 45.2 Q107.6 46 108.4 39.6 Q109.6 36 112 33 Z', fill='#BFE6FF', stroke='#5AA9E6', stroke_width='1.3')   # あせ
    out += path('M110 37.5 Q110.6 40.5 112 41.5', fill='none', stroke='#FFFFFF', stroke_width='1.1', stroke_linecap='round')
    return out


def shock_lines():
    """ガーンの 線（頭の 左上：鉛筆）"""
    import super_premium as SP
    o = ''
    for k, (x, y, a) in enumerate(((92, 168, -112), (108, 150, -124), (128, 138, -138))):
        r0, r1 = 0, 30 - k * 3
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        o += SP.path(f'M{x + ca * r0:.1f} {y + sa * r0:.1f} L{x + ca * r1:.1f} {y + sa * r1:.1f}', fill='none', stroke='#A8416F', stroke_width='3', stroke_linecap='round')
    return o


def layers_html():
    import super_premium as SP
    import rough as R
    cx, cy = SP.HEART_C
    with SP.hand(SP.S_HEAD, 4):
        hs = R.ellipses(head_shock())
    with SP.hand(1.0, 31):
        torso = R.ellipses(SP.pony_torso('F'))
        sl = shock_lines()
    hx, hy = FACE
    head = (f'<g transform="rotate(-4 {hx:.0f} {hy + 40:.0f})"><g transform="translate({hx:.1f} {hy:.1f}) scale({SP.S_HEAD} {SP.S_HEAD}) translate(-80 -47)">'
            f'{hs}</g></g>')
    pony = (f'<svg viewBox="0 0 390 844" width="390" height="844"><use href="#zpTl"/><use href="#zpLg"/>{torso}<use href="#zpHt"/><use href="#zpHv"/>{head}{sl}</svg>')
    css = f'''html,body{{margin:0;background:transparent}}
.L{{position:absolute;left:0;top:0;width:390px;height:844px;overflow:hidden;display:none}}
.zpdefs{{position:absolute;width:0;height:0;overflow:hidden}}
#bg{{background:{SP.uri(SP.dots_svg())} 0 0/88px 88px,linear-gradient(180deg,#FFC9DF,#FFE6F1 55%,#FFD3E5)}}
#bg .rays{{position:absolute;left:50%;top:{cy:.0f}px;width:{SP.RAYS:.0f}px;height:{SP.RAYS:.0f}px;margin:-{SP.RAYS / 2:.0f}px 0 0 -{SP.RAYS / 2:.0f}px;opacity:.55;
  -webkit-mask-image:radial-gradient(circle 778px,#000 0 10%,transparent 58%);mask-image:radial-gradient(circle 778px,#000 0 10%,transparent 58%)}}
#bg .rays svg{{position:absolute;inset:0;width:100%;height:100%}}
#bg .glow{{position:absolute;left:50%;top:{cy:.0f}px;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.95),rgba(255,255,255,.5) 38%,rgba(255,255,255,0) 70%)}}
#bg .zpk{{position:absolute;inset:0;width:390px;height:844px;opacity:.75}}
#gr{{background:{SP.uri(SP.grain_svg())} 0 0/{SP.GRAIN['tile']}px {SP.GRAIN['tile']}px;opacity:{SP.GRAIN['op']}}}'''
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{SP.shared_defs()}
<div class="L" id="bg"><i class="rays">{SP.rays_svg()}</i><i class="glow"></i><svg class="zpk" viewBox="0 0 390 844">{SP.twinkles(22, 5)}</svg></div>
<div class="L" id="po">{pony}</div>
<div class="L" id="gr"></div></body></html>'''


def make_layers(d):
    """背景（不透明）・ポニー（すきとおり）・紙の ざらざら（すきとおり）を 写す"""
    os.makedirs(d, exist_ok=True)
    want = [os.path.join(d, n) for n in ('bg.png', 'pony.png', 'grain.png')]
    if all(os.path.exists(p) for p in want):
        return want
    from playwright.sync_api import sync_playwright
    html = layers_html()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=3)
        pg.set_content(html)
        pg.wait_for_timeout(300)
        for lid, name, omit in (('bg', 'bg.png', False), ('po', 'pony.png', True), ('gr', 'grain.png', True)):
            pg.evaluate("(id) => { document.querySelectorAll('.L').forEach(function (e) { e.style.display = e.id === id ? 'block' : 'none'; }); }", lid)
            pg.wait_for_timeout(120)
            pg.screenshot(path=os.path.join(d, name), omit_background=omit)
        b.close()
    return want


_L = {}


def layers(d):
    if 'L' not in _L:
        pb, pp, pgr = make_layers(d)
        bg = cv2.cvtColor(cv2.imread(pb), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        po = cv2.cvtColor(cv2.imread(pp, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255
        gr = cv2.cvtColor(cv2.imread(pgr, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255
        assert bg.shape[:2] == (H, W) and po.shape[:2] == (H, W), (bg.shape, po.shape)
        _L['L'] = (bg, po, gr)
    return _L['L']


# ---------------------------------------------------------------- 隕石（ポニーに 向かって くる：右上の 空から だんだん 大きく）
METEORS = (  # (はじまる 秒, 出る 所（絵の 画素）, ねらう 所, とどく 秒（場面の あと：とどく 前に 宇宙へ）, 頭の 大きさ（はじめ・さいご）, 明るさ)
    (0.00, (1450.0, -250.0), (640.0, 820.0), 1.78, (12.0, 80.0), 1.0),     # いちばん 大きい：顔へ
    (0.10, (1350.0, 300.0), (470.0, 1420.0), 2.1, (8.0, 46.0), .9),        # ハートへ
    (0.25, (900.0, -300.0), (260.0, 980.0), 2.3, (7.0, 34.0), .85),
    (0.40, (1350.0, 900.0), (760.0, 1700.0), 2.4, (6.0, 30.0), .8),
    (0.55, (1150.0, -250.0), (900.0, 640.0), 2.5, (5.0, 24.0), .75))


def met_state(m, t):
    t0, p0, p1, ta, (s0, s1), b = m
    if t < t0:
        return None
    u = (t - t0) / (ta - t0)
    ue = u * u * (3 - 2 * u) * .35 + u * .65                    # 近づくほど 速く 見える
    x = p0[0] + (p1[0] - p0[0]) * ue
    y = p0[1] + (p1[1] - p0[1]) * ue
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    dv = ((p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L)
    s = s0 + (s1 - s0) * u ** 2
    return (x, y), dv, s, b * min(1.0, (t - t0) / .08), u


def P8(p):
    return (int(round(p[0] * 8)), int(round(p[1] * 8)))


def fblur(img, sig):
    if sig <= 6:
        return cv2.GaussianBlur(img, (0, 0), sig)
    f = int(min(16, max(2, sig // 4)))
    h, w = img.shape[:2]
    sm = cv2.resize(img, (max(1, w // f), max(1, h // f)), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), sig / f)
    return cv2.resize(sm, (w, h), interpolation=cv2.INTER_LINEAR)


def meteors(img, t):
    """ピンクの 空の 上でも 見える ように 色を かさねる：けむり（こげ茶）→ 炎（赤 → だいだい → 黄色）→ 白い 頭・光（スクリーン）"""
    smoke = np.zeros((H, W), np.float32)
    flame = np.zeros((H, W), np.float32)
    core = np.zeros((H, W), np.float32)
    for m in METEORS:
        st = met_state(m, t)
        if st is None:
            continue
        (x, y), dv, s, b, u = st
        tr = s * (9 + 10 * u) + 120
        n = 22
        for i in range(n, 0, -1):
            u0, u1 = i / n, (i - 1) / n
            p0 = (x - dv[0] * tr * u0, y - dv[1] * tr * u0)
            p1 = (x - dv[0] * tr * u1, y - dv[1] * tr * u1)
            w = s * (1 - .7 * u0) * 2
            cv2.line(smoke, P8((x - dv[0] * tr * 1.5 * u0, y - dv[1] * tr * 1.5 * u0)), P8((x - dv[0] * tr * 1.5 * u1, y - dv[1] * tr * 1.5 * u1)),
                     float(b * (1 - u0) ** .8 * .9), max(1, int(round(w * 1.9))), cv2.LINE_AA, shift=3)
            cv2.line(flame, P8(p0), P8(p1), float(b * (1 - u0) ** 1.3), max(1, int(round(w * 1.25))), cv2.LINE_AA, shift=3)
            cv2.line(core, P8(p0), P8(p1), float(b * (1 - u0) ** 2.2), max(1, int(round(w * .45))), cv2.LINE_AA, shift=3)
        cv2.circle(core, P8((x, y)), int(s * .85 * 8), float(b), -1, cv2.LINE_AA, shift=3)
        cv2.circle(flame, P8((x, y)), int(s * 1.35 * 8), float(b), -1, cv2.LINE_AA, shift=3)
    a_s = np.clip(fblur(smoke, 14) * .55, 0, .55)[..., None]
    img = img * (1 - a_s) + np.float32((.33, .2, .17)) * a_s
    f1 = fblur(flame, 5)
    a_r = np.clip(fblur(flame, 16) * 1.1, 0, .9)[..., None]
    img = img * (1 - a_r) + np.float32((.92, .24, .08)) * a_r
    a_o = np.clip(f1 * 1.2, 0, 1)[..., None]
    img = img * (1 - a_o) + np.float32((1.0, .55, .12)) * a_o
    c1 = fblur(core, 2.5)
    a_y = np.clip(fblur(core, 7) * 1.5, 0, 1)[..., None]
    img = img * (1 - a_y) + np.float32((1.0, .86, .35)) * a_y
    a_c = np.clip(c1 * 1.4, 0, 1)[..., None]
    img = img * (1 - a_c) + np.float32((1.0, .98, .9)) * a_c
    glow = fblur(core + flame * .5, 40)[..., None] * np.float32((1.0, .55, .2)) * .55       # まわりを 照らす 光（スクリーン）
    return 1 - (1 - img) * (1 - np.clip(glow, 0, 1))


# ---------------------------------------------------------------- 1コマ
_G = {}


def grid():
    if 'g' not in _G:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _G['g'] = (xx, yy)
    return _G['g']


def frame(fi, d):
    bg, po, gr = layers(d)
    t = fi / FPS
    u = fi / (N - 1)
    xx, yy = grid()
    # 空が だんだん 赤く（右上から：隕石の 火の 光）＋少し 暗く
    k = (.08 + .5 * u ** 1.4)
    r = np.hypot(xx - W * 1.05, yy + H * .08) / (H * .95)
    sky = (np.clip(1.15 - r, 0, 1) ** 1.3 * k)[..., None]
    img = bg * (1 - sky) + np.float32((.95, .36, .2)) * sky
    img *= (1 - .1 * u)
    # ポニー（ぶるぶる・右上から 赤い 光が 当たる）＋紙の ざらざら
    sx = SHIVER[0] * math.sin(2 * math.pi * SHIVER[1] * t)
    M = np.float32([[1, 0, sx], [0, 1, 0]])
    pw = cv2.warpAffine(po, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = pw[..., 3:4]
    lit = (np.clip(1.1 - np.hypot(xx - W * 1.0, yy - H * .05) / (H * .9), 0, 1) * (.06 + .32 * u ** 1.5))[..., None]
    pcol = pw[..., :3] * (1 - lit) + np.float32((1.0, .5, .25)) * lit
    img = img * (1 - a) + pcol * a
    img = img * (1 - gr[..., 3:4]) + gr[..., :3] * gr[..., 3:4]
    img = meteors(img, t)
    # だんだん よる（顔の 少し 下を 中心に）
    z = 1 + (PUSH - 1) * u * u * (3 - 2 * u)
    c = (FACE[0] * S, FACE[1] * S + 260)
    Mz = np.float32([[z, 0, c[0] * (1 - z)], [0, z, c[1] * (1 - z)]])
    img = cv2.warpAffine(img, Mz, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if fi < FADE:                                             # まっ暗から ふっと
        img = img * ((fi + 1) / (FADE + 1))
    return (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)


def main(out, which=None):
    os.makedirs(out, exist_ok=True)
    d = os.path.join(out, 'layers')
    for fi in (which or range(N)):
        im = frame(fi, d)
        cv2.imwrite(os.path.join(out, f'p{fi + 1:03d}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        print('p', fi + 1, flush=True)


if __name__ == '__main__':
    main(sys.argv[1], [int(a) - 1 for a in sys.argv[2:]] or None)
