"""マスター帯の壁紙（tengel_wall.py：おしりから 後ろ足の まわりの 数字が いつも動く・緑の雷が 枠じゅう ビリビリ）の形
   エンブレムの 馬は 動かさない（まさちゃんの指定「やっぱりテンゲルのアイコンは動かさなくていいや・アイコン、元のように戻して」）。
   上の絵は いまの絵（flat/tengel_banner.py：説明書の上の絵 manual/banner.webp から 版の行を消して 切り出した絵）の まま
   - tengel_run.json：数字（0と1）の 場所・大きさ・0か1か・色（数字の色と うしろの色）。元の大きさの 切り出し（clean_crop）から さがす
   - tengel_push.webp（900×491）：的中ボタン（gen_fx.py の tg_face_svg：説明書の上の絵と 同じ 長方形の PUSH）の 面。
     説明書の上の絵（manual/banner.webp・外の すじの わくも ふくむ）から 版の行を 消した絵（clean_full）を 小さくしただけ（ボタン 300px の 3倍）
   python3 flat/tengel_run.py <出力フォルダ> [元の絵]"""
import sys, os, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
import tengel_banner as TB

W, Hh = TB.W, TB.Hh
PUSH_PX = (900, 491)                # 的中ボタン（300×164）の 3倍（元の絵 1200×655 と 同じ 横長）

# 数字（0と1）：ある所（ドームの中・左の行・後ろ足の下の行：780×320 の 座標）と 字の間の目安
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
    """元の大きさの 切り出し（1036×425・BGR）と 色（HSV）"""
    def __init__(self, src=TB.SRC):
        self.crop, _ = TB.clean_crop(src)
        self.Hs, self.Ws = self.crop.shape[:2]
        self.s = self.Ws / W
        hsv = cv2.cvtColor(self.crop, cv2.COLOR_BGR2HSV)
        self.H, self.Sa, self.V = (hsv[..., k].astype(int) for k in range(3))

    def poly(self, pts):
        m = np.zeros((self.Hs, self.Ws), np.uint8)
        cv2.fillPoly(m, [np.array([(x * self.s, y * self.s) for x, y in pts], np.int32)], 1)
        return m


def to_banner(img):
    return cv2.resize(img, (W, Hh), interpolation=cv2.INTER_AREA)


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


def build(outdir, src=TB.SRC):
    os.makedirs(outdir, exist_ok=True)
    S = Src(src)
    run = dict(size=[W, Hh], digits=digits(S))
    full, _ = TB.clean_full(src)
    cv2.imwrite(os.path.join(outdir, 'tengel_push.webp'), cv2.resize(full, PUSH_PX, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_WEBP_QUALITY, 90])
    json.dump(run, open(os.path.join(outdir, 'tengel_run.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('数字', len(run['digits']), {r: sum(d['r'] == r for d in run['digits']) for r in DIGIT_REG})
    return run


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    build(args[0], args[1] if len(args) > 1 else TB.SRC)
