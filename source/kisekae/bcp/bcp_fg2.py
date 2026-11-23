# 結果ボードカスタム（絵の ボード）：ボードの 前の 絵（キャラ・前の 紙ふぶき）を「絵の ぎりぎり」で 切りぬき直す（第4.215版）
#   まさちゃん 2026/11/24 01:31「ボードに重なるところの影みたいなのは、絵のぎりぎりまで合わせてあまり、影がボードに入りすぎないようにして！」
#   前の 切りぬき（bcp_<デザイン>_fg.webp）は、キャラの まわりの かげ・光の にじみ・わくの 内がわの 光（板の 上の うすい 帯）まで 入って いて、
#   それが ボードの 行（アプリが 書く 字）の 上に かぶって いた。
#   新しい 切りぬき（bcp_<デザイン>_f2.webp）＝
#     1. キャラ：動く 絵の ために 作った キャラの 部品（chr/motion.json の layers の f＝ボードの 前に 出る 所）の 形（絵の ふち どおり）
#     2. そのほか（前の 絵 fgx：前の 紙ふぶき・びっくりマーク・わくの かざり）：板の 中では「板と 同じ 色（板の 形 ＝ 面＋ふちの 光）」「板の 色が 暗く なった だけ（かげ）」の 所を はぶく
#     3. 板の 外は 前の 切りぬきの まま（ボードの 行に かぶらない）
#   色は 絵（bcp_<デザイン>.webp）の 色の まま。前の 切りぬき より 広くは ならない（すき通しは 前の 切りぬきの 値まで）。前の ファイルは 消さない・上書きしない
#   python3 kisekae/bcp/bcp_fg2.py <絵の フォルダ（ios/bcp_assets）> <出す フォルダ> [デザイン…]
import sys, os, json, numpy as np, cv2
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import bcp_app, bcp_blank
SUF = '_f2'
MOTION = json.load(open(os.path.join(HERE, 'chr', 'motion.json'), encoding='utf8'))
W_, H_ = 1170, 2532
# デザインごとの きまり：tau（板と 同じ 色と みなす はば）・keep_fgx（そのほか の 物を はぶかない）・chars（キャラの 部品を 使う）
RULES = {}


def place(src, f, box):
    """部品（舞台の pt の 箱）を 絵の 大きさ（1170×2532）に 置いた すき通し（0〜1）"""
    im = Image.open(os.path.join(src, f)).convert('RGBA'); x, y, w, h = [int(round(v * 3)) for v in box]
    if im.size != (w, h): im = im.resize((w, h), Image.LANCZOS)
    a = np.asarray(im)[..., 3].astype(np.float32) / 255; cv = np.zeros((H_, W_), np.float32)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W_), min(y + h, H_)
    cv[y0:y1, x0:x1] = a[y0 - y:y1 - y, x0 - x:x1 - x]; return cv


def chars(src, name):
    """キャラの 部品の「ボードの 前に 出る 所」を 合わせた 形"""
    a = np.zeros((H_, W_), np.float32)
    for l in MOTION.get(name, {}).get('layers', []):
        if l.get('f') and os.path.exists(os.path.join(src, l['f'])): a = np.maximum(a, place(src, l['f'], l['box']))
    return a


def tight(P, a0, ch, board, quad, tau=(34.0, 70.0), sh_res=18.0, grow=30, min_px=400, near=3):
    """P＝絵（float32）・a0＝前の 切りぬきの すき通し（0〜1）・ch＝キャラの 形（0〜1）・board＝板の 形（もの が ない ときの 板の 色）・quad＝板の 中。→ 新しい すき通し（0〜1）
       板の 中（と まわり grow px）で のこす もの：
         ・キャラ（ch：絵の ふち どおり）
         ・そのほか の 物（紙ふぶき・びっくりマーク・花・わくの かざり）：板の 形（面＋ふちの 光）と 色が はなれて いて（tau）、明るい か あざやかな 所。
           暗い 所は、その 物の 明るい 所の すぐ そば（near px）だけ のこす（物の ふち線・かげ）＝ キャラの まわりの かげ・光の にじみ・板の 上の うすい 帯は のこらない"""
    zone = cv2.dilate(quad.astype(np.uint8), bcp_blank.disk(grow)) > 0
    dev = np.abs(P - board).max(2)
    k = (P * board).sum(2) / np.maximum((board * board).sum(2), 1.0); res = np.abs(P - k[..., None] * board).max(2)
    shadow = (k > 0.25) & (k < 1.12) & (res < sh_res)                                 # かげ：板の 色が 暗く（少し 明るく）なった だけ
    obj = (dev > (tau[0] + tau[1]) / 2) & ~shadow & (a0 > 0.03)
    mx, mn = P.max(2), P.min(2); vivid = (mx >= 150) | ((mx - mn >= 80) & (mx >= 110))
    seed = obj & vivid & (ch < 0.5)
    lab, n = ndimage.label(seed); cnt = np.bincount(lab.ravel(), minlength=n + 1); seed = np.isin(lab, [i for i in range(1, n + 1) if cnt[i] >= min_px])      # 小さな 点（400px より 小さい：消した 字の のこり・きらきら）は はぶく
    m = obj & (cv2.dilate(seed.astype(np.uint8), bcp_blank.disk(near)) > 0)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, bcp_blank.disk(1)) > 0
    m = (cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, bcp_blank.disk(1)) > 0) | seed                          # 細い すじは はぶく
    soft = np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8) * 1.6 - 0.25, 0, 1)
    other = np.where(zone, soft, 1.0)                                  # 板の 外は 前の 切りぬきの まま
    return np.minimum(a0, np.maximum(ch, other * a0))


def make(src, name, P=None, dbg=None):
    """→ 新しい 前の 絵（RGBA uint8）。P＝絵（わたさなければ bcp_<name>.webp）"""
    if P is None: P = np.asarray(Image.open(os.path.join(src, f'bcp_{name}.webp')).convert('RGB')).astype(np.float32)
    old = np.asarray(Image.open(os.path.join(src, f'bcp_{name}_fg.webp')).convert('RGBA')); a0 = old[..., 3].astype(np.float32) / 255
    mdl = {}; bcp_blank.clean(src, name, bcp_blank.cfg_of(name), P=P, model=mdl)
    r = RULES.get(name, {}); ch = chars(src, name) if r.get('chars', True) else np.zeros_like(a0)
    a = a0 if r.get('keep') else tight(P, a0, ch, mdl['board'], mdl['quad'], tau=r.get('tau', (34.0, 70.0)))
    rgb = np.clip(P + 0.5, 0, 255).astype(np.uint8); rgb[a <= 0] = 0
    if dbg is not None: dbg.update(a0=a0, ch=ch, board=mdl['board'], quad=mdl['quad'])
    return np.dstack([rgb, np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8)])


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('使い方：bcp_fg2.py <絵の フォルダ> <出す フォルダ> [デザイン…]'); sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    names = sys.argv[3:] or [n for _i, _k, st in bcp_app.ITEMS for _d, n in st if bcp_app.cfg(n).get('fg')]
    for n in names:
        o = make(src, n); f = os.path.join(out, f'bcp_{n}{SUF}.webp'); Image.fromarray(o, 'RGBA').save(f, 'WEBP', quality=90, method=6)
        a0 = np.asarray(Image.open(os.path.join(src, f'bcp_{n}_fg.webp')).convert('RGBA'))[..., 3]
        print(n, '前', int((a0 > 8).sum()), '→ 新', int((o[..., 3] > 8).sum()), f, os.path.getsize(f), flush=True)
