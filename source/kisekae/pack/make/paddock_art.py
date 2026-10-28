"""パドックの 壁紙（壁紙パック・第4.92版）の 馬：いままでの 壁紙と 同じ 馬（horse_flat）が パドックを 歩く（常歩＝4拍子）。
   - 足の 動き：左うしろ → 左前 → 右うしろ → 右前（手前＝左）の じゅんに 地面に つく 4拍子。1本の 足は 1回りの 62% 地面に ついて うしろへ 動き、
     のこりで 持ち上げて 前へ（前足は ひざを まげて、うしろ足は 少しだけ 上げる）。キーは F_KEYS・H_KEYS（位相, 4つの 骨の 向き°：sea_run の pose_at と 同じ 形）
   - 体は 前足が つく たびに 少し 上下し、首と 頭が うなずく（1回りに 2回）。しっぽは ゆっくり ゆれる
   - 地面に ついて いる ひづめが 地面に くる ように 上下を そろえる（sheets.ground_dy）。前足は うしろ足より 少し 短いので 管を のばす（ext）
   - 手前の 3頭（右向き・2・5・7）と おくの 3頭（左向き・小さく・1・4・8）。毛色と 布の 色は 馬ごと
   - ページは シートを めくりながら 横へ 動かす：歩く はやさ（CSS の px／秒）は、地面に ついた ひづめが すべらない はやさ（コマの ひづめの 動きから 出す：speed）
   python3 kisekae/pack/make/paddock_art.py [名前…]   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の paddock.<名前>（シートと speed）"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import render, make_sheet, ground_dy, save_webp, record, preview_png, HOOF_ORDER  # noqa: E402

N = 12             # 1回りの コマ
CYCLE = 1.25       # 1回りの 秒（ページと 同じ）
ST = 0.62          # 足が 地面に ついて いる 長さ（1回りの 割合）
F_KEYS = [(0.00, [-114, -80, -80, -56]), (0.31, [-126, -92, -92, -62]), (0.60, [-136, -106, -106, -78]),
          (0.74, [-128, -78, -150, -150]), (0.88, [-110, -62, -92, -82])]
H_KEYS = [(0.00, [-52, -110, -82, -56]), (0.31, [-62, -118, -94, -64]), (0.60, [-73, -127, -109, -81]),
          (0.74, [-58, -128, -66, -40]), (0.88, [-50, -114, -72, -50])]
OFF = dict(HL=0.00, FL=0.25, HR=0.50, FR=0.75)


def ease(t):
    return t * t * (3 - 2 * t)


def leg_at(keys, p):
    p %= 1.0
    ks = keys + [(keys[0][0] + 1.0, keys[0][1])]
    for (p0, a0), (p1, a1) in zip(ks, ks[1:]):
        if p0 <= p <= p1:
            t = (p - p0) / (p1 - p0)
            if p1 > ST:                     # 地面に ついて いる 間は まっすぐ（すべらない）・持ち上げて から は なめらかに
                t = ease(t)
            return [round(x0 + (x1 - x0) * t, 2) for x0, x1 in zip(a0, a1)]
    return keys[0][1]


def pose_at(g):
    from horse_flat import TAILS
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - OFF[k])
    w = 2 * math.pi
    wave = math.sin(w * g)
    tufts = [((a[0], a[1] + .015 * wave * (i + 1) / 3), (b[0] + .02 * wave * (i + 1) / 3, b[1]), (c[0] + .05 * math.sin(w * g - .9) * (i + 1) / 3, c[1]), wm)
             for i, (a, b, c, wm) in enumerate(TAILS['sway'])]
    return dict(theta=round(0.6 * math.sin(w * 2 * g), 2), neck_rot=round(-7 + 2.4 * math.cos(w * 2 * (g - 0.1)), 2), head_ang=round(-55 + 1.6 * math.sin(w * 2 * g), 2),
                tail=[-118, -100], tail_kind='sway', tail_tufts=tufts,
                fore_near=leg('FL'), fore_far=leg('FR'), hind_near=leg('HL'), hind_far=leg('HR'))


def stance(g):
    return [k for k in HOOF_ORDER if ((g - OFF[k]) % 1.0) < ST]


# 毛色（馬ごと）
def coat(kind):
    if kind == 'bay':
        return dict(body='#9A552C', shade='#6E3818', muzzle='#C9906A', mane='#231612', maneD='#120A08', hoof='#2E2420', eye='#1A100A', blush='#EE9070', bodyShade='#8A4A24')
    if kind == 'chestnut':
        return dict(body='#C8763C', shade='#9A5426', muzzle='#E8AE80', mane='#B85A26', maneD='#8A3E16', hoof='#3A2A20', eye='#1E120A', blush='#F09A78', bodyShade='#B86A34')
    if kind == 'black':
        return dict(body='#3A2C28', shade='#251C1A', muzzle='#6A5246', mane='#141010', maneD='#0A0808', hoof='#262020', eye='#0E0A08', blush='#C98070', bodyShade='#33261F')
    if kind == 'gray':
        return dict(body='#E2DED8', shade='#B3ABA0', muzzle='#F2EFEA', mane='#6A6460', maneD='#4A4542', hoof='#4A4440', eye='#1A1414', blush='#E8A898', bodyShade='#D2CBC1')
    if kind == 'darkbay':
        return dict(body='#6E3A22', shade='#4A2412', muzzle='#A07058', mane='#1A100C', maneD='#0C0806', hoof='#2A201C', eye='#140C08', blush='#D88870', bodyShade='#62331E')
    raise KeyError(kind)


def pal(kind, cloth, num_col, trim='#FFFFFF'):
    p = coat(kind)
    p.update(tack='#2A1A12', ring='#E8E4DC', cloth=cloth, clothTrim=trim, num=num_col, saddle='#2A1C14')
    return p


# 名前 → (毛色, 布の 色, 番号の 色, 番号, 向き)
HORSES = dict(
    n2=('bay', '#D23A3A', '#FFFFFF', '2', 'right'),
    n5=('chestnut', '#2456B8', '#FFFFFF', '5', 'right'),
    n7=('black', '#2E8A4A', '#FFFFFF', '7', 'right'),
    f1=('gray', '#FFFFFF', '#1A1A1A', '1', 'left'),
    f4=('chestnut', '#F2C230', '#1A1A1A', '4', 'left'),
    f8=('darkbay', '#E86A9A', '#FFFFFF', '8', 'left'),
)
BOX_NEAR = (230, 92, 452, 300)          # 手前の 馬（右向き）
BOX_FAR = (300, 70, 432, 196)           # おくの 馬（左向き・小さく）


def speed(frames, legs, dys):
    """地面に ついて いる ひづめが すべらない 横の はやさ（2倍の 画素／コマ）：コマから つぎの コマへ、どちらでも 地面に ついて いる 足の ひづめの 動きの 平均"""
    n = len(frames)
    vals = []
    for i in range(n):
        j = (i + 1) % n
        for k in legs[i]:
            if k in legs[j]:
                x0 = frames[i][2][HOOF_ORDER.index(k)][0]
                x1 = frames[j][2][HOOF_ORDER.index(k)][0]
                vals.append(x0 - x1)
    return sum(vals) / len(vals) if vals else 0.0


def build(name, out=None):
    kind, cloth, numc, num, facing = HORSES[name]
    box = BOX_NEAR if facing == 'right' else BOX_FAR
    spot = dict(pose='stand', facing=facing, box=box, azim=6 if facing == 'right' else -6, shadow=('#3A2A10', 0.0), ext=(0.05, 0.05))
    poses = [pose_at(i / N) for i in range(N)]
    frames, cam = render(pal(kind, cloth, numc, '#F2C14E' if cloth != '#FFFFFF' else '#1A1A1A'), spot, poses, acc=None, number=num, tag='pkpd' + name, workers=1)
    legs = [stance(i / N) for i in range(N)]
    if facing == 'left':                                                 # 左向きは 手前の 足が 骨の R（make_pose）→ ひづめの 目印も 入れかえる
        sw = {'FL': 'FR', 'FR': 'FL', 'HL': 'HR', 'HR': 'HL'}
        legs = [[sw[k] for k in st] for st in legs]
    dys = ground_dy(frames, legs, box[3] - 4, lift=0.0)
    v = speed(frames, legs, dys)                                         # 2倍の 画素／コマ（右向きは ＋）
    xs = [h[0] for fr in frames for h in fr[2]]
    g = box[3] - 4
    sh = ('#3A2A10', (min(xs) + max(xs)) / 2, g + 3, (max(xs) - min(xs)) * 0.52, 5.0, 0.22)
    u8, meta = make_sheet(frames, dys, shadow=sh)
    meta['dy'] = [round(float(d), 2) for d in dys]
    meta['speed'] = round(abs(v) / 2 * N / CYCLE, 2)                     # CSS の px／秒
    meta['facing'] = facing
    if out:
        preview_png(u8, os.path.join(out, f'paddock_{name}.png'), bg=(196, 170, 120))
    bid = save_webp(u8, quality=90)
    record('paddock', name, bid, meta)
    print(name, bid, meta, flush=True)


if __name__ == '__main__':
    names = sys.argv[1:] or list(HORSES)
    for nm in names:
        build(nm, os.environ.get('OUT'))
