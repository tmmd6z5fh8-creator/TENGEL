# 決戦調査（第4.196版・まさちゃん 2026/11/18 15:09「テンゲルカードバトルにクエストを追加する 名前:決戦調査」）の 絵
#   まさちゃんの 絵（ios/cb_assets/src/：リポジトリには 入れない）から アプリ用の 絵を 作る。kisekae/cb_art.py の plan() に 入る（台帳・古いかの たしかめも cb_art.py と 同じ）
#     cb_quest_map.png（エリア 1〜12 の 全体マップ 1024×1536）       → cb_q_map.webp（そのまま）
#     cb_quest_field_01〜12.png（フィールド 941×1672）              → cb_q_f01〜12.webp（そのまま）
#       ※ まさちゃんの 7まい目・8まい目の フィールドは マップの 名前と 入れ替えて 使う（7 雷鳴峡 ＝ 雷の 絵〈field_08〉・8 氷晶砦 ＝ 氷の 城の 絵〈field_07〉：敵の 絵 7＝雷の 馬・8＝氷の 鎧の 馬 とも 合う）
#     cb_quest_enemy_01〜12.png（敵 1254×1254・すき通し）           → cb_q_e01〜12.webp（下の「敵の 絵」）
#     cb_quest_hp.png（敵HP ゲージ 2172×724・すき通し）             → cb_q_hl01〜12.webp（左：盾の 中に 敵の 顔）・cb_q_hm.webp（まん中：のばす）・cb_q_hr.webp（右）
#   敵の 絵：フィールドに 立って いる ように（まさちゃん「敵は背景にセットされるから、足元とか違和感がないように」）
#     ・すき通しの ふち（不透明度 40 より 下の もや）を 消す・まん中は ぴったり 不透明に
#     ・フィールドの 光の 色を 少し うつす（TINT：フィールドの 立つ 所の 平均の 色）・足もとを 少し 暗く（地面の 影）
#     ・足もとの 影（蹄の 下に だけ こい 影 ＋ 体の 下の うすい 影）を 絵の 中に 入れる（敵と いっしょに 動く）
#     ・つるつるの 床・水の 上（5 霧鏡の湖・8 氷晶砦・10 星月の回廊・11 黒曜の天文台・12 日蝕の玉座）は うすい うつりこみ（上下を 返して 下へ うすれる・水は 少し ゆらぐ）
#     ・絵の 下の はし（FOOT）＝ 蹄の 線（いちばん 下の 蹄）。アプリ（cb/cb_app.js の QUEST の g）は この 線を 地面の 高さに 置く
#   HP ゲージ：盾の 中（暗い 所：明るさ 60 より 下で つながった 所）に 敵の 顔（HEAD：頭 ぜんぶの 四角 ＋ よゆう FACE_FIT：耳も 鼻先も 切れない）＋ うしろに その フィールドの ぼかした 絵
#   python3 kisekae/cb_quest_art.py preview <フォルダ>   … 見る 用の 絵（フィールドに 立った 敵・ゲージ）を 作る（アプリには 入れない）
import os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
SRC = os.path.join(W, 'ios', 'cb_assets', 'src')
LV = 12
MAP = 'cb_quest_map.png'; HP = 'cb_quest_hp.png'
FIELD = {lv: f'cb_quest_field_{({7: 8, 8: 7}.get(lv, lv)):02d}.png' for lv in range(1, LV + 1)}      # 7・8 は 入れ替え（上の ※）
ENEMY = {lv: f'cb_quest_enemy_{lv:02d}.png' for lv in range(1, LV + 1)}
# 盾の 中に 入れる 顔：敵の 絵（1254×1254）の 中の 頭の 四角（耳・たてがみ・冠の 先 〜 鼻先・あご：x0, y0, x1, y1）。
#   第4.196版（まさちゃん 15:53「HPゲージの敵の顔だけ顔が途中で切れちゃってるの多いから、顔がしっかり入るようにして！」）：前は 顔の まん中と 幅で 決めて いて 耳・鼻先が 切れて いた →
#   頭 ぜんぶ ＋ よゆう（FACE_FIT：たて 1.31倍・よこ 1.20倍・頭を 少し 上へ＝盾の 下は とがって いる）が 盾の 中（たて横 227/193）に 入る 大きさで 切る
HEAD = {1: (140, 5, 495, 425), 2: (100, 35, 420, 360), 3: (30, 140, 360, 560), 4: (250, 15, 460, 345), 5: (50, 60, 310, 460), 6: (105, 15, 310, 400),
        7: (30, 290, 370, 615), 8: (140, 5, 360, 405), 9: (40, 200, 330, 610), 10: (250, 290, 420, 510), 11: (200, 20, 410, 295), 12: (215, 145, 400, 530)}
FACE_FIT = (1.31, 1.20, 0.06)      # たての よゆう・よこの よゆう・頭を 上へ（切る 四角の 高さに 対して）


def face_box(lv):
    """盾の 中に 入れる 四角：(まん中 x, まん中 y, 幅)（高さ＝幅 × 227/193）"""
    (x0, y0, x1, y1), (mh, mw, dy) = HEAD[lv], FACE_FIT
    hw, hh = x1 - x0, y1 - y0
    h = max(hh * mh, hw * mw * 227 / 193); w = h * 193 / 227
    return (round((x0 + x1) / 2), round((y0 + y1) / 2 + dy * h), round(w))


# うつりこみの こさ（0＝なし）・水の ゆらぎ
REFL = {5: (0.46, True), 8: (0.18, False), 10: (0.34, False), 11: (0.28, False), 12: (0.28, False)}
E_MAX = 1000                  # 敵の 絵の 幅の 上限（px）
REFL_H = 0.40                 # うつりこみの 長さ（敵の 高さに 対して）
EXT = 0.42                    # 絵の 下に たす 高さ（敵の 高さに 対して：影・うつりこみ。どの 敵も 同じ → 蹄の 線は 絵の 上から 1/1.42：cb/cb_app.js の QFOOT）
AIR = {7: 0.13}               # とんで いる 敵（7 雷鳴峡の 迅雷）：蹄から 地面の 影までの すきま（敵の 高さに 対して）
SHADOW = dict(band=0.10, foot=0.62, body=0.40)      # 影：蹄を さがす 下の はば（敵の 高さに 対して）・蹄の 下の 影の こさ・体の 下の うすい 影の こさ
TINT = 0.20                   # フィールドの 光の 色を うつす 強さ
HP_Y = (206, 500)             # ゲージを 切る 高さ（もとの 絵の 中：絵の ある 所 208〜497 ＋ すこし）
HP_L, HP_M, HP_R = (34, 560), (1100, 1140), (1990, 2146)      # 左（盾・敵HP・バーの はじめ）・まん中（のばす）・右（バーの おわり・赤い 石）
SHIELD_AT = (155, 353)        # 盾の 中の 1点（ここから 暗い 所を たどる）
Q = dict(quality=84, method=6)
QF = dict(quality=82, method=6)


def PARAMS():
    """決めごと（cb_art.py の 台帳に 書く：かわったら 作り直す）"""
    return [sorted([k, v] for k, v in FIELD.items()), sorted([k, list(v)] for k, v in HEAD.items()), list(FACE_FIT), sorted([k, list(v)] for k, v in REFL.items()),
            E_MAX, REFL_H, EXT, sorted([k, v] for k, v in AIR.items()), SHADOW, TINT, list(HP_Y), list(HP_L), list(HP_M), list(HP_R), list(SHIELD_AT), Q, QF]


def rgba(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.float32)


def soft_alpha(al):
    """もとの 不透明度（0〜255）→ 0〜1：40 より 下の もやは 消す・236 より 上は 1"""
    return np.clip((al - 40.0) / (236.0 - 40.0), 0, 1)


def field_light(fp):
    """フィールドの 立つ 所（下の まん中）の 平均の 色（0〜1）と 明るさ"""
    f = np.asarray(Image.open(fp).convert('RGB')).astype(np.float32) / 255
    h, w = f.shape[:2]; reg = f[int(h * 0.45):int(h * 0.9), int(w * 0.15):int(w * 0.85)]
    c = reg.reshape(-1, 3).mean(0); lum = float(c @ [0.299, 0.587, 0.114])
    return c, lum


def enemy_sprite(lv, ep, fp):
    """敵の 絵（RGBA float 0〜255）と 蹄の 線の 高さ（絵の 上から：0〜1）"""
    a = rgba(ep); al = soft_alpha(a[..., 3])
    ys, xs = np.nonzero(al > 0.02); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    m = 6; x0 = max(0, x0 - m); y0 = max(0, y0 - m); x1 = min(a.shape[1], x1 + m)
    foot = int(np.nonzero(al.max(axis=1) > 0.5)[0].max()) + 1       # いちばん 下の 蹄（不透明な 所の いちばん 下）
    y1 = foot
    rgb = a[y0:y1, x0:x1, :3]; A = al[y0:y1, x0:x1]
    hh, ww = A.shape
    # 光の 色：フィールドの 色を 少し（明るさは かえない 色だけ）＋ 明るさを 少し 合わせる ＋ 足もとを 少し 暗く
    c, lum = field_light(fp)
    tint = np.clip(c / max(1e-3, float(c @ [0.299, 0.587, 0.114])), 0.7, 1.35)
    expo = float(np.clip(0.93 + 0.30 * (lum - 0.42), 0.84, 1.04))
    yy = np.linspace(0, 1, hh)[:, None]
    ao = 1 - 0.16 * np.clip((yy - 0.72) / 0.28, 0, 1) ** 1.5
    rgb = rgb * ((1 - TINT) + TINT * tint)[None, None, :] * expo * ao[..., None]
    # 下に 影と うつりこみの 場所を たす（どの 敵も 同じ 割合：蹄の 線は 絵の 上から FOOT）
    ext = int(round(hh * EXT)); N = hh + ext
    # 蹄の 線（列ごと）：下の はば band の 中で いちばん 下の 不透明な 所。手前の 蹄と おくの 蹄で 高さが ちがう ので 列ごとに
    band = int(hh * SHADOW['band']); sub = A[hh - band:] > 0.5; has = sub.any(axis=0)
    yb = (hh - 1 - np.argmax(sub[::-1], axis=0)).astype(np.float32)
    xs_ = np.arange(ww)
    yf = np.interp(xs_, xs_[has], yb[has]) if has.any() else np.full(ww, hh - 1.0)
    yf = np.minimum(ndimage.gaussian_filter1d(yf, max(2.0, 0.03 * ww), mode='nearest'), hh - 1.0)
    air = AIR.get(lv, 0.0)
    out = np.zeros((N, ww, 4), np.float32)
    yy2 = np.arange(N, dtype=np.float32)[:, None]
    # うつりこみ（列ごとの 蹄の 線で 上下を 返す・下へ うすれる・少し ぼかして 暗く・水は ゆらぐ）
    rl = REFL.get(lv)
    if rl:
        k, water = rl
        d = yy2 - yf[None, :]                                  # 蹄の 線からの きょり（下へ ＋）
        sy = yf[None, :] - d                                   # 返した 所
        sx = np.broadcast_to(xs_[None, :].astype(np.float32), d.shape).copy()
        if water:
            sx = sx + (np.sin(d / 7.0) * 3.5 + np.sin(d / 2.3) * 1.2) * np.clip(d / (0.15 * hh), 0, 1)
        ok = (d > 0) & (sy >= 0)
        crd = [np.clip(sy, 0, hh - 1), np.clip(sx, 0, ww - 1)]
        fa = ndimage.map_coordinates(A, crd, order=1) * ok
        fr = np.stack([ndimage.map_coordinates(rgb[..., c], crd, order=1) for c in range(3)], -1)
        fade = np.clip(1 - d / (REFL_H * hh), 0, 1) ** 1.6
        fa = ndimage.gaussian_filter(fa * fade, 1.2) * k
        fr = ndimage.gaussian_filter(fr, (1.2, 1.2, 0)) * 0.72
        out[..., :3] = fr; out[..., 3] = fa
    # 影：蹄の 下（列ごとの 蹄の 線）＋ 体の 下の うすい 影。とんで いる 敵（AIR）は 蹄の 下に すきまを あけて うすく 広く
    col = has.astype(np.float32)
    if air:
        s1 = np.zeros((N, ww), np.float32)
    else:
        s1 = np.exp(-0.5 * ((yy2 - (yb[None, :] + 0.004 * hh)) / max(2.0, 0.012 * hh)) ** 2) * col[None, :]
        s1 = ndimage.gaussian_filter(s1, (0, max(1.0, 0.006 * ww)))
    cols = np.nonzero(has)[0]; s2 = np.zeros((N, ww), np.float32)
    if len(cols):
        cx, half = (cols.min() + cols.max()) / 2, max(10, (cols.max() - cols.min()) / 2 * 1.08)
        gy = hh + air * hh; sg = max(3.0, (0.022 + 0.03 * (air > 0)) * hh)
        xx = xs_[None, :]
        s2 = np.exp(-0.5 * ((xx - cx) / (half * (0.62 if not air else 0.5))) ** 2 - 0.5 * ((yy2 - gy) / sg) ** 2) * (1.0 if not air else 0.8)
    sh_a = np.clip(SHADOW['foot'] * s1 + SHADOW['body'] * s2, 0, 0.75)
    # 重ねる：影 → うつりこみ → 敵（すき通しを かけた 色で）
    base_a = out[..., 3]; base_rgb = out[..., :3]
    a2 = base_a + sh_a * (1 - base_a); rgb2 = np.where(a2[..., None] > 1e-5, (base_rgb * base_a[..., None]) / np.maximum(a2[..., None], 1e-5), 0)
    top = np.zeros_like(out); top[:hh, :, :3] = rgb; top[:hh, :, 3] = A
    ta = top[..., 3]; fa2 = ta + a2 * (1 - ta)
    frgb = np.where(fa2[..., None] > 1e-5, (top[..., :3] * ta[..., None] + rgb2 * a2[..., None] * (1 - ta[..., None])) / np.maximum(fa2[..., None], 1e-5), 0)
    img = np.concatenate([frgb, fa2[..., None] * 255], 2)
    return img, hh / N


def save_rgba(img, size, path, q=Q):
    """すき通しを かけた 色で 小さく して 保存（cb_art.save と 同じ やり方）"""
    import cb_art
    return cb_art.save(img, size, path) if q is Q else _save_q(img, size, path, q)


def _save_q(img, size, path, q):
    im = Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8), 'RGBA')
    if im.size != size: im = im.resize(size, Image.LANCZOS)
    im.save(path, 'WEBP', **q); return os.path.getsize(path)


def enemy(lv):
    def f(srcs, o):
        img, foot = enemy_sprite(lv, srcs[0], srcs[1])
        h, w = img.shape[:2]; s = min(1.0, E_MAX / w)
        return save_rgba(img, (int(round(w * s)), int(round(h * s))), o)
    return f


def shield_mask(g):
    """盾の 中（暗い 所）：0〜1（ふちは なめらかに）"""
    L = g[..., 0] * 0.3 + g[..., 1] * 0.59 + g[..., 2] * 0.11
    lab, _n = ndimage.label(L < 60)
    m = lab == lab[SHIELD_AT[1], SHIELD_AT[0]]
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_erosion(m, iterations=1)
    return np.clip(ndimage.gaussian_filter(m.astype(np.float32), 0.8), 0, 1)


def portrait(lv, ep, fp, box):
    """盾の 中に 入れる 絵（box＝(x0, y0, x1, y1)：その 大きさの RGB float）：うしろは フィールドの ぼかした 絵 ＋ 敵の 顔"""
    bw, bh = box[2] - box[0], box[3] - box[1]
    f = Image.open(fp).convert('RGB'); fw, fh = f.size
    cw = fw * 0.62; ch = cw * bh / bw; cy = fh * 0.40
    bg = f.crop((int((fw - cw) / 2), int(cy - ch / 2), int((fw + cw) / 2), int(cy + ch / 2))).resize((bw, bh), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
    bg = np.asarray(bg).astype(np.float32) * 0.62
    cx, cy2, w = face_box(lv); h = w * bh / bw
    e = Image.open(ep).convert('RGBA').crop((int(cx - w / 2), int(cy2 - h / 2), int(cx + w / 2), int(cy2 + h / 2))).resize((bw, bh), Image.LANCZOS)
    e = np.asarray(e).astype(np.float32); ea = soft_alpha(e[..., 3])[..., None]
    out = bg * (1 - ea) + e[..., :3] * ea
    yy, xx = np.mgrid[0:bh, 0:bw]; r = np.sqrt(((xx - bw / 2) / (bw * 0.62)) ** 2 + ((yy - bh * 0.46) / (bh * 0.62)) ** 2)
    return out * (1 - 0.32 * np.clip(r - 0.55, 0, 1))[..., None]


def gauge_left(lv):
    def f(srcs, o):
        g = rgba(srcs[0]); m = shield_mask(g)
        ys, xs = np.nonzero(m > 0.01); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        p = portrait(lv, srcs[1], srcs[2], box)
        out = g.copy(); mm = m[box[1]:box[3], box[0]:box[2]][..., None]
        # 盾の ふちの 内がわに うすい 影（はめこんだ ように）
        d = ndimage.distance_transform_edt(m > 0.5)[box[1]:box[3], box[0]:box[2]][..., None]
        p = p * (1 - 0.45 * np.exp(-d / 5.0))
        out[box[1]:box[3], box[0]:box[2], :3] = g[box[1]:box[3], box[0]:box[2], :3] * (1 - mm) + p * mm
        out[..., 3] = np.where(m > 0.01, np.maximum(out[..., 3], 255 * m), out[..., 3])
        c = out[HP_Y[0]:HP_Y[1], HP_L[0]:HP_L[1]]
        return _save_q(c, (c.shape[1], c.shape[0]), o, Q)
    return f


def gauge_part(x0x1):
    def f(srcs, o):
        g = rgba(srcs if isinstance(srcs, str) else srcs[0]); c = g[HP_Y[0]:HP_Y[1], x0x1[0]:x0x1[1]]
        return _save_q(c, (c.shape[1], c.shape[0]), o, Q)
    return f


def plain(q):
    def f(p, o):
        im = Image.open(p).convert('RGB'); im.save(o, 'WEBP', **q); return os.path.getsize(o)
    return f


def jobs():
    """作る もの（cb_art.plan() が 使う）：[(できる 名前, もとの 名前〈いくつか ある ときは tuple〉, 作る 関数)]"""
    j = [('cb_q_map.webp', MAP, plain(QF))]
    for lv in range(1, LV + 1):
        j.append((f'cb_q_f{lv:02d}.webp', FIELD[lv], plain(QF)))
        j.append((f'cb_q_e{lv:02d}.webp', (ENEMY[lv], FIELD[lv]), enemy(lv)))
        j.append((f'cb_q_hl{lv:02d}.webp', (HP, ENEMY[lv], FIELD[lv]), gauge_left(lv)))
    j.append(('cb_q_hm.webp', HP, gauge_part(HP_M)))
    j.append(('cb_q_hr.webp', HP, gauge_part(HP_R)))
    return j


def preview(outdir, src_dir=None, levels=None):
    """見る 用：390×844 の 画面（3倍）で、フィールド（画面いっぱい）に 敵を 置いた 形・ゲージ（顔）"""
    sys.path.insert(0, H); import re
    os.makedirs(outdir, exist_ok=True)
    js = open(os.path.join(W, 'cb', 'cb_app.js'), encoding='utf8').read()
    m = re.search(r"const QG = \[(.*?)\];", js, re.S)
    G = [tuple(float(v) for v in t.split(',')) for t in re.findall(r'\[([0-9., ]+)\]', m.group(1))] if m else [(0.5, 0.80, 0.74)] * LV
    OUT = src_dir or os.path.join(W, 'ios', 'cb_assets')
    sw, sh, k = 390, 844, 2
    levels = levels or list(range(1, LV + 1))
    tiles = []
    for lv in levels:
        f = Image.open(os.path.join(OUT, f'cb_q_f{lv:02d}.webp')).convert('RGBA'); fw, fh = f.size
        e = Image.open(os.path.join(OUT, f'cb_q_e{lv:02d}.webp')).convert('RGBA')
        gx, gy, gw = G[lv - 1][:3]
        img, foot = None, None
        # 蹄の 線：絵の 中の 高さ（うつりこみ・影の 分を のぞく）
        foot = 1 / (1 + EXT)
        W2 = gw * fw; H2 = W2 * e.size[1] / e.size[0]
        x = gx * fw - W2 / 2; y = gy * fh - foot * H2
        f.alpha_composite(e.resize((int(W2), int(H2)), Image.LANCZOS), (int(x), int(y)))
        s = max(sw * k / fw, sh * k / fh); f2 = f.resize((int(fw * s), int(fh * s)), Image.LANCZOS)
        l = (f2.size[0] - sw * k) // 2; t = (f2.size[1] - sh * k) // 2
        tiles.append(f2.crop((l, t, l + sw * k, t + sh * k)).convert('RGB'))
    for i in range(0, len(tiles), 4):
        sheet = Image.new('RGB', (sw * k * 4, sh * k))
        for j, tl in enumerate(tiles[i:i + 4]): sheet.paste(tl, (j * sw * k, 0))
        sheet.resize((sw * 4, sh)).save(os.path.join(outdir, f'scene_{i // 4 + 1}.jpg'), quality=88)
    gs = Image.new('RGBA', (1600, 110 * len(levels)), (24, 20, 30, 255))
    hm = Image.open(os.path.join(OUT, 'cb_q_hm.webp')).convert('RGBA'); hr = Image.open(os.path.join(OUT, 'cb_q_hr.webp')).convert('RGBA')
    for r_, lv in enumerate(levels):
        hl = Image.open(os.path.join(OUT, f'cb_q_hl{lv:02d}.webp')).convert('RGBA')
        row = Image.new('RGBA', (hl.size[0] + 900 + hr.size[0], hl.size[1]), (0, 0, 0, 0))
        row.alpha_composite(hl, (0, 0)); row.alpha_composite(hm.resize((900, hm.size[1])), (hl.size[0], 0)); row.alpha_composite(hr, (hl.size[0] + 900, 0))
        row = row.resize((int(row.size[0] * 100 / row.size[1]), 100), Image.LANCZOS)
        gs.alpha_composite(row, (10, 5 + 110 * r_))
    gs.convert('RGB').save(os.path.join(outdir, 'gauges.jpg'), quality=90)
    print('preview →', outdir)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'preview':
        preview(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, [int(x) for x in sys.argv[4:]] or None)
