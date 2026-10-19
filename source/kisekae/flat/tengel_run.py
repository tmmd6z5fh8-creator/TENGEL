"""マスター帯の壁紙（tengel_wall.py：テンゲルのアイコンの馬が いつも走る・数字が いつも動く・緑の雷が 枠じゅう ビリビリ）の絵と形
   元は flat/tengel_banner.py と同じ（説明書の上の絵 manual/banner.webp から 版の行を消して 切り出した絵 1036×425：clean_crop）。
   絵そのものは描きなおさない（アイコンの馬の 足と頭を 切りぬいて 動かす）
   - tengel_plate.webp（780×320）：馬の足（前足2本・後ろ足2本）と 頭を ぬいた絵。ぬいた所は まわりの紺で なめらかに うめる
     （まわりの 暗い紺だけから ぼかして ひろげる）。頭のうしろの 盾の金のふち（たての線）は 下の所を 写して つなぐ
   - tengel_<部品>.webp（すき通し）：足は 上と下の2つ（ひじ・ひざ／ももと すね）・頭・体と騎手（足が 体のうしろを 通るように 足の上に重ねる）
     どれも 元の絵の画素のまま（まわりの こい線ごと 少し大きめに 切りぬく）。止まった形で重ねると いまの絵と同じ
   - tengel_run.json：部品ごとの 置く場所（780×320）・回る中心、数字（0と1）の 場所・大きさ・色（数字の色と うしろの色）
   - tengel_icon.webp（312×312）：的中ボタン（gen_fx.py の tg_face_svg）に使う テンゲルのアイコン（アプリのアイコン icons/icon3-512.png を 小さくしただけ）
   python3 flat/tengel_run.py <出力フォルダ> [元の絵] [--check]（--check：止まった形で重ねて いまの絵と くらべる）"""
import sys, os, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
import tengel_banner as TB

W, Hh = TB.W, TB.Hh
ICON = os.path.join(HERE, '..', '..', 'icons', 'icon3-512.png')
ICON_PX = 312                       # 的中ボタン（156px）の 2倍

# 動かす部品（780×320 の座標）。足は 金の かたまり（その点を ふくむ）から 明るい所を ひろげて、まわりの こい線ごと 切りぬく
SEEDS = dict(FL1=[(240, 190), (225, 207)],                      # 手前の前足（「く」の字に たたんだ足）
             FL2=[(279, 195), (264, 193), (262, 176)],          # 向こうの前足（「7」の字）
             HL1=[(145, 200), (175, 228)],                      # 手前の後ろ足（「<」の字）
             HEAD=[(295, 100)])                                 # 頭と首の上
BOXES = dict(
    FL1=[(210, 168), (236, 168), (262, 195), (258, 206), (232, 218), (208, 214)],
    FL2=[(244, 165), (286, 168), (288, 190), (281, 226), (258, 226), (256, 186), (244, 186)],
    HL1=[(133, 166), (157, 166), (157, 192), (193, 238), (190, 248), (172, 248), (133, 200)],
    HEAD=[(243, 103.5), (262, 92), (275.5, 83.5), (277, 64), (283, 63), (283.5, 72.5), (292, 74), (330, 116), (322, 132), (292, 126),
          (283.5, 118), (266, 116.5), (246, 109)])
HL2 = [(156, 170), (173, 174), (171, 181), (167, 206), (162, 207), (157, 190)]            # 向こうの後ろ足（紺の細い足）
SPLIT = dict(FL1=((226, 198), (262, 201)), FL2=((268, 186), (285, 176)))                  # 上と下に分ける線（この線より上が 上の部品）
HL1_SPLIT_Y = 192
BODY = [(150, 150), (160, 110), (176, 95), (205, 90), (232, 104), (262, 112), (282, 118), (280, 170), (258, 172), (240, 175), (212, 182), (195, 182), (158, 178)]
PIVOT = dict(FL1u=(221, 177), FL1l=(253.5, 199), FL2u=(250, 180), FL2l=(279.5, 181.5), HL1u=(151, 171), HL1l=(141, 191), HL2=(164, 172), HEAD=(262, 111))
BAR = dict(x=(283, 292.5), gap=(72, 118.5), src=(121, 135))                             # 頭のうしろの 盾の金のふち
PARTS = ('HL2', 'FL2l', 'FL2u', 'HL1l', 'HL1u', 'FL1l', 'FL1u', 'BODY', 'HEAD')          # 重ねる順（下から）

# 数字（0と1）：ある所（ドームの中・左の行・下の行）と 字の間の目安
DIGIT_REG = dict(D=[(110, 118), (119, 114), (151, 114), (155, 116), (155, 150), (149, 159), (124, 167), (110, 167)],
                 L=[(15, 143), (60, 143), (75, 146.5), (110, 146.5), (112, 153.5), (158, 153.5), (158, 186.5), (110, 186.5), (110, 193), (15, 193)],
                 B=[(100, 210), (136, 210), (136, 222), (145, 240), (142, 264), (110, 264), (100, 245)])
DIGIT_EXCL = [[(58, 145.5), (112, 145.5), (112, 154), (58, 154)], [(80, 187.5), (160, 187.5), (160, 196), (80, 196)]]
DIGIT_PITCH = dict(D=5.5, L=5.4, B=6.2)
DIGIT_THR = dict(D=16, L=14, B=16)


def hexc(c):
    b, g, r = (int(round(float(v))) for v in c)
    return f'#{r:02X}{g:02X}{b:02X}'


class Src:
    def __init__(self, src=TB.SRC):
        self.crop, _ = TB.clean_crop(src)
        self.Hs, self.Ws = self.crop.shape[:2]
        self.s = self.Ws / W
        hsv = cv2.cvtColor(self.crop, cv2.COLOR_BGR2HSV)
        self.H, self.Sa, self.V = (hsv[..., k].astype(int) for k in range(3))
        self.yy, self.xx = np.mgrid[0:self.Hs, 0:self.Ws]

    def poly(self, pts):
        m = np.zeros((self.Hs, self.Ws), np.uint8)
        cv2.fillPoly(m, [np.array([(x * self.s, y * self.s) for x, y in pts], np.int32)], 1)
        return m

    def side(self, a, b):
        s = self.s
        ax, ay, bx, by = a[0] * s, a[1] * s, b[0] * s, b[1] * s
        return ((bx - ax) * (self.yy - ay) - (by - ay) * (self.xx - ax) < 0).astype(np.uint8)


def part_masks(S):
    """部品ごとの マスク（元の大きさ）"""
    gold = ((S.H >= 12) & (S.H <= 32) & (S.Sa > 70) & (S.V > 110)).astype(np.uint8)
    fg = (S.V > 85).astype(np.uint8)
    _, glab = cv2.connectedComponents(gold, connectivity=8)
    _, flab = cv2.connectedComponents(fg, connectivity=8)

    def grow(pts, box):
        seed = np.zeros((S.Hs, S.Ws), np.uint8)
        for bx, by in pts:
            seed |= (glab == glab[int(by * S.s), int(bx * S.s)]).astype(np.uint8)
        seed &= box
        ids = np.unique(flab[(seed > 0) & (fg > 0)])
        return (np.isin(flab, ids[ids > 0]).astype(np.uint8) & box) | seed
    raw = {}
    for k in ('FL1', 'FL2', 'HL1', 'HEAD'):
        raw[k] = grow(SEEDS[k], S.poly(BOXES[k]))
    up = S.side(*SPLIT['FL1'])
    raw['FL1u'], raw['FL1l'] = raw['FL1'] & up, raw['FL1'] & (1 - up)
    up = S.side(*SPLIT['FL2'])
    raw['FL2u'], raw['FL2l'] = raw['FL2'] & up, raw['FL2'] & (1 - up)
    up = (S.yy < HL1_SPLIT_Y * S.s).astype(np.uint8)
    raw['HL1u'], raw['HL1l'] = raw['HL1'] & up, raw['HL1'] & (1 - up)
    raw['HL2'] = S.poly(HL2)
    for k in ('FL1', 'FL2', 'HL1'):
        del raw[k]
    allraw = np.zeros((S.Hs, S.Ws), np.uint8)
    for m in raw.values():
        allraw |= m
    other = (fg & (1 - cv2.dilate(allraw, np.ones((3, 3), np.uint8)))).astype(np.uint8)       # ほかの明るい物は ふくめない
    ell = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    M = {k: ((cv2.dilate(m, ell) & (1 - other)) | m) for k, m in raw.items()}
    legs = np.zeros((S.Hs, S.Ws), np.uint8)
    for k in ('FL1u', 'FL1l', 'FL2u', 'FL2l', 'HL1u', 'HL1l', 'HL2'):
        legs |= M[k]
    M['BODY'] = (S.poly(BODY) & (S.V > 60).astype(np.uint8) & (1 - legs)).astype(np.uint8)
    return M


def make_plate(S, M):
    """足と頭を ぬいた絵（元の大きさ・BGR）"""
    union = np.zeros((S.Hs, S.Ws), np.uint8)
    for k, m in M.items():
        if k != 'BODY':
            union |= m
    near = cv2.dilate(union, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    cf = S.crop.astype(np.float32)
    valid = ((S.V >= 38) & (S.V <= 85) & (near == 0)).astype(np.float32)         # まわりの 暗い紺だけ（部品の ふちの こい線は つかわない）
    fill = None
    for sig in (7, 18):
        num = cv2.GaussianBlur(cf * valid[..., None], (0, 0), sig)
        den = cv2.GaussianBlur(valid, (0, 0), sig)[..., None]
        f = num / np.maximum(den, 1e-4)
        if fill is None:
            fill, wgt = f, np.clip(den / 0.25, 0, 1)
        else:
            fill = fill * wgt + f * (1 - wgt)
    soft = union[..., None].astype(np.float32)                                    # うめるのは 部品の中だけ（外は いまの絵のまま）
    plate = np.clip(cf * (1 - soft) + fill * soft, 0, 255).astype(np.uint8)
    s = S.s
    x0, x1 = int(BAR['x'][0] * s), int(BAR['x'][1] * s) + 1
    ya, yb = int(BAR['gap'][0] * s), int(BAR['gap'][1] * s)
    src = S.crop[int(BAR['src'][0] * s):int(BAR['src'][1] * s), x0:x1]
    for y in range(ya, yb):
        row = src[(y - ya) % src.shape[0]]
        plate[y, x0:x1] = np.where(M['HEAD'][y, x0:x1, None] > 0, row, plate[y, x0:x1])
    return plate


def to_banner(img):
    return cv2.resize(img, (W, Hh), interpolation=cv2.INTER_AREA)


def rgba_part(S, m):
    """部品の 切りぬき（780×320 の大きさで・すき通し・色は 元の画素）：(BGRA, (x0, y0, w, h))"""
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6)
    a = np.clip(a * 1.25, 0, 1) * (cv2.dilate(m, np.ones((3, 3), np.uint8)) > 0)
    pa = to_banner(S.crop.astype(np.float32) * a[..., None])
    ab = to_banner(a)
    col = pa / np.maximum(ab, 1e-4)[..., None]
    ys, xs = np.nonzero(ab > 1 / 255)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    out = np.dstack([np.clip(col, 0, 255), np.clip(ab * 255, 0, 255)])[y0:y1, x0:x1]
    return (out + .5).astype(np.uint8), (int(x0), int(y0), int(x1 - x0), int(y1 - y0))


def digits(S):
    """数字（0と1）の 字ごとの 場所（780×320 の座標）・0か1か・色（字・うしろ）"""
    lum = S.crop.astype(np.float32).mean(2)
    bg = cv2.morphologyEx(lum, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    d = lum - bg
    gold = (S.H >= 12) & (S.H <= 34) & (S.Sa > 60)
    line = (S.H >= 16) & (S.H <= 34) & (S.Sa >= 38)
    near_gold = cv2.dilate(gold.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    excl = np.zeros((S.Hs, S.Ws), np.uint8)
    for p in DIGIT_EXCL:
        excl |= S.poly(p)
    ban = to_banner(S.crop).astype(np.float32)
    blum = ban.mean(2)
    out = []
    for r, pts in DIGIT_REG.items():
        R = S.poly(pts)
        m = ((d > DIGIT_THR[r]) & ~gold & ~line & ~near_gold).astype(np.uint8) & R & (1 - excl)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
        for i in range(1, n):
            x, y, w, h, a = st[i]
            bw, bh = w / S.s, h / S.s
            if a < 3 or bh < 2.5 or bh > 7.8:
                continue
            k = max(1, int(round(bw / DIGIT_PITCH[r])))
            if bw / k > 6.2 or bw / k < 0.9:
                continue
            for j in range(k):
                gx0 = x + w * j / k
                gx1 = x + w * (j + 1) / k
                sub = lab[y:y + h, int(gx0):int(np.ceil(gx1))] == i
                if sub.sum() < 2:
                    continue
                cols = np.nonzero(sub.any(0))[0]
                ax0 = (int(gx0) + cols.min()) / S.s
                ax1 = (int(gx0) + cols.max() + 1) / S.s
                by0, by1 = y / S.s, (y + h) / S.s
                kind = '0' if (ax1 - ax0) / bh > .5 else '1'
                # 色：字＝四角の中の 明るい所・うしろ＝四角のまわり（1.5px 外）の まん中の明るさ
                X0, Y0, X1, Y1 = int(np.floor(ax0)), int(np.floor(by0)), int(np.ceil(ax1)), int(np.ceil(by1))
                box = ban[Y0:Y1, X0:X1].reshape(-1, 3)
                bl = blum[Y0:Y1, X0:X1].ravel()
                glyph = box[bl >= np.percentile(bl, 75)].mean(0)
                ring = ban[max(0, Y0 - 2):Y1 + 2, max(0, X0 - 2):X1 + 2].reshape(-1, 3)
                rl = ring.mean(1)
                back = ring[rl <= np.percentile(rl, 50)].mean(0)
                out.append(dict(r=r, x=round(ax0, 2), y=round(by0, 2), w=round(ax1 - ax0, 2), h=round(by1 - by0, 2), k=kind,
                                c=hexc(glyph), b=hexc(back)))
    return out


def build(outdir, src=TB.SRC, check=False):
    os.makedirs(outdir, exist_ok=True)
    S = Src(src)
    M = part_masks(S)
    plate = make_plate(S, M)
    pb = to_banner(plate)
    cv2.imwrite(os.path.join(outdir, 'tengel_plate.webp'), pb, [cv2.IMWRITE_WEBP_QUALITY, 88])
    run = dict(size=[W, Hh], parts={}, order=list(PARTS))
    layers = {}
    for k in PARTS:
        im, (x, y, w, h) = rgba_part(S, M[k])
        cv2.imwrite(os.path.join(outdir, f'tengel_{k.lower()}.webp'), im, [cv2.IMWRITE_WEBP_QUALITY, 92])
        run['parts'][k] = dict(box=[x, y, w, h], pivot=list(PIVOT.get(k, (0, 0))))
        layers[k] = (im, x, y)
    run['digits'] = digits(S)
    ic = cv2.imread(ICON, cv2.IMREAD_COLOR)
    assert ic is not None and ic.shape[:2] == (512, 512), ICON
    cv2.imwrite(os.path.join(outdir, 'tengel_icon.webp'), cv2.resize(ic, (ICON_PX, ICON_PX), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_WEBP_QUALITY, 90])
    json.dump(run, open(os.path.join(outdir, 'tengel_run.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('部品', {k: v['box'] for k, v in run['parts'].items()}, '数字', len(run['digits']))
    if check:
        ref = to_banner(S.crop).astype(np.float32)
        comp = cv2.imread(os.path.join(outdir, 'tengel_plate.webp')).astype(np.float32)
        for k in PARTS:
            im = cv2.imread(os.path.join(outdir, f'tengel_{k.lower()}.webp'), cv2.IMREAD_UNCHANGED).astype(np.float32)
            x, y = layers[k][1], layers[k][2]
            h, w = im.shape[:2]
            a = im[..., 3:] / 255
            comp[y:y + h, x:x + w] = comp[y:y + h, x:x + w] * (1 - a) + im[..., :3] * a
        d = np.abs(comp - ref).max(2)
        print('止まった形と いまの絵（切り出し・webp まえ）：ちがい 平均', round(float(d.mean()), 2), '最大', int(d.max()),
              ' 8段より大きい画素', int((d > 8).sum()))
        cv2.imwrite(os.path.join(outdir, 'check_rest.png'), np.clip(comp, 0, 255).astype(np.uint8))
    return run


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    build(args[0], args[1] if len(args) > 1 else TB.SRC, check='--check' in sys.argv)
