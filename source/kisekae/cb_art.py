# 馬カードバトルの 絵を アプリに 入れる 形に する（第4.176版・まさちゃん 2026/11/15 21:41「TENGER馬カードバトル …デザイン…これは、俺が作成する」・21:58「これ背面！」）
#   python3 kisekae/cb_art.py            … ios/cb_assets/src/（まさちゃんの 絵 13まい・PNG）→ ios/cb_assets/cb_*.webp（アプリに 入れる 形）
#   python3 kisekae/cb_art.py --check    … できて いる ものが 今の もと・今の 決めごとで 作った ものか だけ 見る（ちがえば 1 で おわる）
#   もと（ios/cb_assets/src/）は **読む だけ**（上書きしない・消さない）。どちらの フォルダも リポジトリには 入れない（.gitignore）
#
#   もとの 絵（名前は 姫が つけた）：
#     cb_1.png 〜 cb_7.png（数字の カード）・cb_k.png（神様馬）・cb_m.png（幻の馬）・cb_back.png（カードの うら）：1024×1536・すき通し あり（角が 丸い）
#     cb_board.png（プレイボード：1672×941・すき通し なし）・cb_deck.png（山札：1254×1254）・cb_icon.png（アイコン：1254×1254）
#     第4.177版（まさちゃん 2026/11/16 10:40「3.に効果追加…」・10:54「5.の効果変更した画像！」）：3 と 5 は 新しい 絵 cb_3_v2.png・cb_5_v2.png（1024×1536・すき通し なし＝白い 紙の 上に カード）。
#       前の 絵 cb_3.png・cb_5.png は のこす（上書きしない・消さない）。白い 紙の 絵は「白で ない 所の 四角」を カードと して 切り出す（下の alpha_of：カードの 場所と 角の 丸みは 前の 絵と 同じ）
#     第4.178版（まさちゃん 2026/11/16 15:33「テンゲルカードバトルに追加 1は…2は…」と 新しい 絵 2まい「3枚公開：逆転勝利」）：1 と 2 も 新しい 絵 cb_1_v2.png・cb_2_v2.png（1024×1536・白い 紙の 上）。
#       前の 絵 cb_1.png・cb_2.png は のこす（上書きしない・消さない）
#     第4.179版（まさちゃん 2026/11/16 16:18「一枚目、コインのデザイン」）：バトルコインの 絵 cb_coin.png（1254×1254・すき通し あり）→ cb_coin.webp（240×240：メニュー・部屋・結果の 画面の 小さい しるし）
#     第4.182版（まさちゃん 2026/11/16 20:00「バトルコインで購入するカード背面のデザイン送る！ ・背面カスタム1枚 バトルコイン300枚」と 絵 7まい）：
#       カードの うら 7種 cb_back_<名前>.png（1024×1536・白い 紙の 上に カード：名前は 姫が つけた）＝ sky（天馬の光）・star（星座の馬）・ice（氷の結晶）・wa（和の墨絵）・
#       ori（折り紙の馬）・crown（王冠の紋章）・heart（ハートの2頭）→ 下の BACKS
#     第4.182版（まさちゃん 20:09「カードバトルデザインカスタム デザイン一枚解放、バトルコイン300枚 神様馬カードと幻の馬カード500枚」と 絵 16まい）：
#       カードの おもての べつの デザイン cb_face_<名前>.png（1024×1536・白い 紙の 上に カード：名前は 姫が つけた。<カード><a・b>）→ 下の FACES
#       ka・kb（神様馬）・ma・mb（幻の馬）・1a・1b・2a・2b・3a・3b・4a・4b・5a・5b・6a・7a ／ 20:22「6.71枚づつ追加して！」＋ 絵 2まい：6b・7b（あわせて 18種）
#     第4.185版（まさちゃん 2026/11/16 22:39「7.の効果変わる！…」＋ 7 の 新しい 絵 3まい「デザインベースが一枚目！カスタムが二枚目！、3枚目！」・
#       22:45「2.元々のは消して！ルールが追加されてないから！」）：7 の いつもの 絵は cb_7_v2.png・カスタム 7a・7b は cb_face_7a_v2.png・cb_face_7b_v2.png
#       （1024×1536・白い 紙の 上：「3枚交換・4枚公開で逆転」の 文）。前の 絵 cb_7.png・cb_face_7a.png・cb_face_7b.png は のこす（上書きしない・消さない：アプリには 入れない）
#     第4.185版（まさちゃん 2026/11/16 23:20「バトルコインで、プレイボード7種類購入できるようにして！ 1個バトルコイン300枚で解放できるようにして！」と 絵 7まい）：
#       プレイボード 7種 cb_board_<名前>.png（1672×941・すき通し なし：いつもの ボードと 同じ 形〈台・捨て札・山札・VS の 2つの わく・歯車〉の 場所は 1画素も ずれて いない）＝
#       marble（白亜の宮殿）・frost（蒼氷の宮）・sakura（桜の舞踏会）・violet（紫月の夜）・crimson（紅蓮の闘技場）・starry（黄金の星空）・steam（歯車の工房）→ 下の BOARDS（名前は 姫が つけた）
#   作る もの：
#     カード 10種 × 2つの 大きさ：cb_c<名前>.webp（800×1200：大きく 見る・めくった とき）・cb_s<名前>.webp（300×450：手札・台の 上）。名前＝1〜7・k・m・b（うら）
#       ・カードは もとの 絵ごとに 大きさと たて横が 少し ちがう（おもて 986〜1007×1510〜1521・うら 938×1338）→ 絵の ある 所（すき通しで ない 所）を 切り出して、
#         どれも 同じ たて横（2:3）・同じ 角の 丸み に そろえる（めくった ときに 形が かわらない ように）。うらは たてに 5% ほど のびる（もようは ほぼ そのまま）
#       ・もとの 絵は まん中も 少し すき通って いる（不透明度 242〜254／255）→ まん中は ぴったり 不透明に する。ふちは 4px 内がわで 切る（もとの ふちの にじみを 出さない）
#     第4.182版：おもての べつの デザイン 18種 × 2つ：cb_fc_<名前>_c.webp（800×1200）・cb_fc_<名前>_s.webp（300×450）：いつもの おもてと 同じ 切り方（card）
#     第4.182版：背面カスタム 7種 × 3つ：cb_bk_<名前>_c.webp（800×1200）・cb_bk_<名前>_s.webp（300×450）・cb_bk_<名前>_d.webp（山札 360×426：下の deck_with）
#       ・おもてと 同じ 切り方（card：白い 紙の 外を 切って 2:3・同じ 角の 丸み）
#       ・山札は cb_deck.png（いつもの 山札の 絵：少し ななめから 見た 形）の いちばん 上の カードの 面 だけを、その うらの 絵に はりかえる（DECK_FACE の 4つの 角へ ななめに うつす）。
#         下に かさなった カードの ふち（金の 線）と 外の 形（すき通し）は いつもの まま ＝ 切り方・大きさは cb_deck.webp と 同じ
#     第4.185版：プレイボード 7種 × 2つ：cb_bd_<名前>.webp（1254×706：対戦の ボード）・cb_bd_<名前>_s.webp（480×270：デザインカスタムの タイル）。
#     第4.186版（まさちゃん 2026/11/17 00:52「この4つ、この画像と入れ替えて！」と 絵 4まい）：crimson・sakura・marble・frost は 新しい 絵 cb_board_<名前>_v2.png
#       （1672×941：右の 馬が 大きく なって「山札」の 札が 左へ 98px。ほかの 形〈台・捨て札・VS の わく・歯車〉は 同じ 場所）。前の 絵は のこす（上書きしない・消さない：アプリには 入れない）
#       絵は そのまま（夜の 色〈night〉に しない：まさちゃんの デザインの まま）。大きさを かえる だけ
#     第4.189版（まさちゃん 2026/11/17 15:00「カードバトル 1パックコイン112枚 カード購入ではなく、パック式にする…」と 絵 18まい：どれも「SECRET RARE」）：
#       カードパックの レア 9種・超レア 9種（1〜7・神様馬・幻の馬：名前は 姫が つけた。どちらが レアかは 姫が 決めた）＝ cb_face_<名前>.png（1024×1536・白い 紙の 上に カード）
#       ・レア（キラキラの 水晶の 枠・角ばった 大きい 数字）：kr・mr・1r〜7r（2r だけ cb_face_2r.jpg：もらった 形の まま）
#       ・超レア（宮殿の 柱と ダイヤの 枠・丸い 数字）：ksr・msr・1sr〜7sr
#       kr・ksr は 紙の ふちが ない（絵が 画面いっぱい）→ そのまま 2:3 で 同じ 角の 丸みに 切る。作り方は ほかの おもてと 同じ（cb_fc_<名前>_c／_s.webp）
#     cb_board.webp（1254×706）・cb_deck.webp（360×426）・cb_icon.webp（240×240：右下の 丸い ボタン）・cb_logo.webp（720×720：メニューの 絵）・cb_coin.webp（240×240：バトルコイン：第4.179版）
#     第4.189版（まさちゃん 2026/11/17 15:39「パックの画像これ使える？」と 絵 1まい）：カードパックの 絵 cb_pack.png（1024×1536・すき通し あり：TENGER 馬カードバトル・BOOSTER PACK・5枚入り）
#       → cb_pack.webp（600×1110：絵の ある 所〈109〜914 × 6〜1509〉に すこし よゆうを つけて 切り出す・まん中は ぴったり 不透明に・まわりの うすい もや〈不透明度 64 未満〉は 消す）
#     第4.178版（まさちゃん 2026/11/16 14:43「フィールドの雰囲気を夜の月あかりと火のライトに照らされてるイメージにして！(デザインは変えないで、差し込んでる光りの色を変えてみて)」）：
#       cb_board.webp は、もとの 絵（cb_board.png：そのまま のこす）の **光の 色 だけ** を かえて 作る（下の night）：形・もよう・字は 1画素も 動かさない。
#       ・ぜんたいを 夜の 暗さ・青みへ ／ 光って いる 所（床に 差しこむ 光・金の ふちの てり）の 色を、左上から 月あかり（青白）・右下から 火の あかり（だいだい）に 入れかえる ／
#         緑の フェルト・緑の 馬と 葉は ほぼ そのまま（あそぶ 所が 見にくく ならない ように）
#   台帳 cb_art.json：{ v, p（決めごと：大きさ・夜の 色の 数字）, files: { 名前: { src: [もとの 名前, 大きさ, sha1], size } } }（アプリには 入れない）
import hashlib, json, os, sys
import numpy as np
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
SRC = os.path.join(W, 'ios', 'cb_assets', 'src'); OUT = os.path.join(W, 'ios', 'cb_assets')
V = 1
CARDS = [('1', 'cb_1_v2.png'), ('2', 'cb_2_v2.png'), ('3', 'cb_3_v2.png'), ('4', 'cb_4.png'), ('5', 'cb_5_v2.png'), ('6', 'cb_6.png'), ('7', 'cb_7_v2.png'), ('k', 'cb_k.png'), ('m', 'cb_m.png'), ('b', 'cb_back.png')]
BACKS = [('sky', 'cb_back_sky.png'), ('star', 'cb_back_star.png'), ('ice', 'cb_back_ice.png'), ('wa', 'cb_back_wa.png'), ('ori', 'cb_back_ori.png'), ('crown', 'cb_back_crown.png'), ('heart', 'cb_back_heart.png')]      # 第4.182版：背面カスタム
BOARDS = [(b, f'cb_board_{b}' + ('_v2' if b in ('crimson', 'sakura', 'marble', 'frost') else '') + '.png') for b in ('marble', 'frost', 'sakura', 'violet', 'crimson', 'starry', 'steam')]      # 第4.185版：プレイボード（第4.186版：4つは 新しい 絵）
BD, BD_S = (1254, 706), (480, 270)      # 第4.185版：プレイボードの 大きさ（いつもの cb_board.webp と 同じ）・タイル
FACES = [(f, f'cb_face_{f}' + ('_v2' if f in ('7a', '7b') else '') + '.png') for f in ('ka', 'kb', 'ma', 'mb', '1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '5a', '5b', '6a', '6b', '7a', '7b')]
FACES += [(f, f'cb_face_{f}' + ('.jpg' if f == '2r' else '.png')) for f in ('kr', 'mr', '1r', '2r', '3r', '4r', '5r', '6r', '7r', 'ksr', 'msr', '1sr', '2sr', '3sr', '4sr', '5sr', '6sr', '7sr')]      # 第4.189版：カードパックの レア・超レア      # 第4.182版：おもての べつの デザイン（第4.185版：7a・7b は 新しい 絵）
DECK_FACE = ((268.4, 104.0), (963.2, 104.0), (1060.7, 948.0), (198.0, 948.0))      # cb_deck.png（1254×1254）の いちばん 上の カードの 面の 角（左上・右上・右下・左下：外の 形の 左右の 線と 金の ふちの 上下で 測った）
BASE = (1000, 1500)          # そろえる 大きさ（たて横 2:3）
INSET, RADIUS = 4, 62        # ふちを 内がわへ 4px・角の 丸み 62px（1000×1500 の とき。どの もとの 絵の 角 よりも 内がわ）
BIG, SMALL = (800, 1200), (300, 450)
PACK_BOX, PACK_SIZE = (104, 4, 920, 1514), (600, 1110)      # 第4.189版：カードパックの 絵の 切り出し（cb_pack.png の 中）と 大きさ
Q = dict(quality=84, method=6)
INFO = 'cb_art.json'         # 台帳（アプリには 入れない：build_ios.py は cb_*.webp と cb_se_*.m4a・cb_bgm.m4a だけ 入れる）
# 夜の 光（第4.178版）：月＝左上から・火＝右下から。数字を かえたら 台帳の p が かわる（--check で 古いと 出る）
#   mkeep＝月の 側で もとの 色（金）を どれだけ のこすか（0.70：金の ふちは 金の まま、てりが 青白く なる。0.4 に すると 銀色に 見えて「デザインが かわった」ように 見えた）
NIGHT = dict(lit0=0.06, lit1=0.40, mx=0.0, my=-0.08, mrx=1.0, mry=1.3, fx=1.03, fy=1.0, frx=0.95, fry=1.25, floor=0.3,
             amb=(0.40, 0.50, 0.76), moon=(0.52, 0.73, 1.0), fire=(1.0, 0.53, 0.17), mkeep=0.70, mcool=(0.78, 0.96, 1.10), mgain=1.10,
             fwarm=(1.30, 0.80, 0.33), fgain=1.16, recolor=0.92, mpool=0.065, fpool=0.10, felt=0.12)


def sha(p):
    return hashlib.sha1(open(p, 'rb').read()).hexdigest()


def bbox(al, th=128):
    ys, xs = np.nonzero(al > th)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def round_mask(size, inset, radius, ss=4):
    """角の 丸い 四角（0〜1）：ss 倍で 描いて 小さく する（ふちを なめらかに）"""
    w, h = size; m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([inset * ss, inset * ss, (w - inset) * ss - 1, (h - inset) * ss - 1], radius=radius * ss, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS), np.float32) / 255


def solid(al):
    """もとの 不透明度（0〜255）→ 0〜1：まん中（242〜254）は 1 に・ふちの うすい 所は そのまま"""
    return np.clip((al.astype(np.float32) - 64) / (236 - 64), 0, 1)


def alpha_of(a):
    """もとの 絵の すき通し（0〜255）。すき通しの ない 絵（白い 紙の 上の カード）は、白で ない 点が 5% より 多い 行と 列の 四角を カード（255）・その 外を すき通し（0）に する
       （カードの 上下の はしの 行は 角が 丸い ぶん 短い・金の ふちに 白く 光る 所も ある ので、半分では なく 5%。紙の 上の 小さな ごみでは 広がらない）。
       角の 白い 所は あとの 丸い マスク（INSET・RADIUS：カードの 角より 内がわ）で 切れる。カードの 中の 白い 所（字・光）は そのまま のこる"""
    al = a[..., 3]
    if int(al.min()) >= 250:
        ink = a[..., :3].min(axis=2) < 236
        cols = np.nonzero(ink.mean(axis=0) > 0.05)[0]; rows = np.nonzero(ink.mean(axis=1) > 0.05)[0]
        al = np.zeros(al.shape, np.uint8); al[rows.min():rows.max() + 1, cols.min():cols.max() + 1] = 255
    return al


def card(src):
    """カード 1まい → 1000×1500 の RGBA（float 0〜255）と、マスクの 中で もとが うすかった 所の 数"""
    a = np.asarray(Image.open(src).convert('RGBA')).copy()
    a[..., 3] = alpha_of(a)
    x0, y0, x1, y1 = bbox(a[..., 3])
    im = Image.fromarray(a[y0:y1, x0:x1]).resize(BASE, Image.LANCZOS)
    b = np.asarray(im, np.float32)
    mask = round_mask(BASE, INSET, RADIUS); own = solid(b[..., 3])
    thin = int(((mask > 0.99) & (own < 0.95)).sum())
    out = b.copy(); out[..., 3] = np.clip(mask * own, 0, 1) * 255
    return out, (x1 - x0, y1 - y0), thin


def save(rgba, size, path):
    im = Image.fromarray(np.clip(rgba + 0.5, 0, 255).astype(np.uint8), 'RGBA')
    if im.size != size:
        # すき通しを かけた 色で 小さく する（ふちに 外の 色が にじまない ように）
        f = np.asarray(im, np.float32); al = f[..., 3:4] / 255
        pm = np.concatenate([f[..., :3] * al, f[..., 3:4]], 2)
        r = np.asarray(Image.fromarray(np.clip(pm + 0.5, 0, 255).astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS), np.float32)
        a2 = r[..., 3:4] / 255
        rgb = np.where(a2 > 1e-4, r[..., :3] / np.maximum(a2, 1e-4), 0)
        im = Image.fromarray(np.clip(np.concatenate([rgb, r[..., 3:4]], 2) + 0.5, 0, 255).astype(np.uint8), 'RGBA')
    im.save(path, 'WEBP', **Q)
    return os.path.getsize(path)


def cut(src, th=128):
    """すき通しの ある 絵（山札・アイコン）：絵の ある 所を 切り出す・まん中は ぴったり 不透明に"""
    a = np.asarray(Image.open(src).convert('RGBA')).astype(np.float32)
    x0, y0, x1, y1 = bbox(a[..., 3], th)
    b = a[y0:y1, x0:x1].copy(); b[..., 3] = solid(b[..., 3]) * 255
    return b


def square(b):
    """まん中に 置いた 正方形に する（まわりは すき通し）"""
    h, w = b.shape[:2]; n = max(h, w); o = np.zeros((n, n, 4), np.float32)
    y, x = (n - h) // 2, (n - w) // 2; o[y:y + h, x:x + w] = b
    return o


def night(im, P=None):
    """ボードの 絵（RGB）の 光の 色 だけを 夜（月あかり＋火の あかり）に かえた 絵を 返す。形・もようは 動かさない（1画素ごとに 色を 計算する だけ）
         1) ぜんたい：夜の 暗さ・青み（amb）  2) 光って いる 所（明るい・緑で ない 所）：月の 側（左上）は 青白い てり・火の 側（右下）は だいだいの てりに 入れかえる
         3) 月と 火の うすい 光を 足す（mpool・fpool：緑の フェルトの 上は felt 倍 だけ）"""
    P = P or NIGHT
    a = np.asarray(im.convert('RGB'), np.float32) / 255
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); u = xx / (w - 1); v = yy / (h - 1)
    sm = lambda x, lo, hi: (lambda t: t * t * (3 - 2 * t))(np.clip((x - lo) / (hi - lo), 0, 1))
    lin = a ** 2.2                                               # 光の 足し引きは 明るさに 比例する 形で
    L = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    green = sm(lin[..., 1] - np.maximum(lin[..., 0], lin[..., 2]), 0.004, 0.05)
    lit = sm(L, P['lit0'], P['lit1']) * (1 - green)
    moon = np.clip(1 - np.hypot((u - P['mx']) / P['mrx'], (v - P['my']) / P['mry']), 0, 1)
    fire = np.clip(1 - np.hypot((u - P['fx']) / P['frx'], (v - P['fy']) / P['fry']), 0, 1)
    tot = np.maximum(moon + fire, P['floor']); wm = (moon / tot)[..., None]; wf = (fire / tot)[..., None]
    mc = np.array(P['moon'], np.float32)[None, None, :]; fc = np.array(P['fire'], np.float32)[None, None, :]
    out = lin * np.array(P['amb'], np.float32)[None, None, :]
    moonlit = (P['mkeep'] * lin * np.array(P['mcool'], np.float32)[None, None, :] + (1 - P['mkeep']) * L[..., None] * mc) * P['mgain']
    firelit = lin * np.array(P['fwarm'], np.float32)[None, None, :] * P['fgain']
    k = (lit * P['recolor'])[..., None]
    out = out * (1 - k * (wm + wf)) + k * (wm * moonlit + wf * firelit)
    soft = (P['felt'] + (1 - P['felt']) * (1 - green))[..., None]
    out = out + (P['mpool'] * (moon ** 2)[..., None] * mc + P['fpool'] * (fire ** 2)[..., None] * fc) * soft
    return Image.fromarray((np.clip(out, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8))


def persp(dst, src):
    """ななめに うつす 数（PIL の PERSPECTIVE：できる 絵の 点 → もとの 絵の 点）。dst・src＝4つの 角"""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return [float(c) for c in np.linalg.solve(np.array(A, np.float64), np.array(B, np.float64))]


def deck_with(back_src):
    """山札の 絵（cb_deck.png）の いちばん 上の 面を back_src の うらに はりかえた RGBA（float）を、cut と 同じ 形で 返す（外の 形・下の ふちは いつもの まま）"""
    d = np.asarray(Image.open(os.path.join(SRC, 'cb_deck.png')).convert('RGBA')).astype(np.float32)
    f = card(back_src)[0]; al = f[..., 3:4] / 255
    pm = np.concatenate([f[..., :3] * al, f[..., 3:4]], 2)      # すき通しを かけた 色で うつす（ふちに 外の 色が にじまない ように）
    h, w = d.shape[:2]; ss = 2                                  # 2倍で うつして 小さく する（ふちを なめらかに）
    co = persp([(x * ss, y * ss) for x, y in DECK_FACE], [(0, 0), (BASE[0], 0), (BASE[0], BASE[1]), (0, BASE[1])])
    wp = Image.fromarray(np.clip(pm + 0.5, 0, 255).astype(np.uint8), 'RGBA').transform((w * ss, h * ss), Image.PERSPECTIVE, co, Image.BICUBIC)
    wp = np.asarray(wp.resize((w, h), Image.LANCZOS), np.float32)
    a2 = wp[..., 3:4] / 255
    out = d.copy(); out[..., :3] = d[..., :3] * (1 - a2) + wp[..., :3]      # 面の 上に かさねる（色は すき通しを かけて ある）
    x0, y0, x1, y1 = bbox(d[..., 3], 128)                      # 切り方は cut（いつもの 山札）と 同じ
    b = out[y0:y1, x0:x1].copy(); b[..., 3] = solid(d[y0:y1, x0:x1, 3]) * 255
    return b


def plan():
    """作る もの：[(できる 名前, もとの 名前, 作る 関数)]"""
    jobs = []
    for cid, src in CARDS:
        jobs.append((f'cb_c{cid}.webp', src, lambda p, o: save(card(p)[0], BIG, o)))
        jobs.append((f'cb_s{cid}.webp', src, lambda p, o: save(card(p)[0], SMALL, o)))
    def board(p, o):
        im = night(Image.open(p).convert('RGB')).resize((1254, 706), Image.LANCZOS); im.save(o, 'WEBP', quality=86, method=6); return os.path.getsize(o)      # 第4.178版：光の 色を 夜に（night）
    jobs.append(('cb_board.webp', 'cb_board.png', board))
    jobs.append(('cb_deck.webp', 'cb_deck.png', lambda p, o: save(cut(p), (360, 426), o)))
    jobs.append(('cb_icon.webp', 'cb_icon.png', lambda p, o: save(square(cut(p)), (240, 240), o)))
    jobs.append(('cb_logo.webp', 'cb_icon.png', lambda p, o: save(square(cut(p)), (720, 720), o)))
    jobs.append(('cb_coin.webp', 'cb_coin.png', lambda p, o: save(square(cut(p)), (240, 240), o)))      # 第4.179版：バトルコイン
    def pack(p, o):                                             # 第4.189版：カードパックの 絵
        a = np.asarray(Image.open(p).convert('RGBA')).astype(np.float32)
        x0, y0, x1, y1 = PACK_BOX; b = a[y0:y1, x0:x1].copy(); b[..., 3] = solid(b[..., 3]) * 255
        return save(b, PACK_SIZE, o)
    jobs.append(('cb_pack.webp', 'cb_pack.png', pack))
    for fid, src in FACES:                                      # 第4.182版：おもての べつの デザイン（大きい・小さい）
        jobs.append((f'cb_fc_{fid}_c.webp', src, lambda p, o: save(card(p)[0], BIG, o)))
        jobs.append((f'cb_fc_{fid}_s.webp', src, lambda p, o: save(card(p)[0], SMALL, o)))
    for bid, src in BACKS:                                      # 第4.182版：背面カスタム（大きい・小さい・山札）
        jobs.append((f'cb_bk_{bid}_c.webp', src, lambda p, o: save(card(p)[0], BIG, o)))
        jobs.append((f'cb_bk_{bid}_s.webp', src, lambda p, o: save(card(p)[0], SMALL, o)))
        jobs.append((f'cb_bk_{bid}_d.webp', src, lambda p, o: save(deck_with(p), (360, 426), o)))
    def plain(size):                                            # 第4.185版：プレイボード（絵は そのまま・大きさ だけ）
        def f(p, o):
            Image.open(p).convert('RGB').resize(size, Image.LANCZOS).save(o, 'WEBP', quality=86, method=6); return os.path.getsize(o)
        return f
    for did, src in BOARDS:
        jobs.append((f'cb_bd_{did}.webp', src, plain(BD)))
        jobs.append((f'cb_bd_{did}_s.webp', src, plain(BD_S)))
    return jobs


def PARAMS():
    """決めごと（台帳に 書く：かわったら 作り直す）"""
    return json.loads(json.dumps([list(BASE), INSET, RADIUS, list(BIG), list(SMALL), Q, NIGHT, [list(c) for c in DECK_FACE], [list(BD), list(BD_S)], [list(PACK_BOX), list(PACK_SIZE)]]))      # 第4.185版：プレイボードの 大きさ・第4.189版：パックの 絵


def files():
    """アプリに 入れる 絵の 名前（build_ios.py・テストが 使う）"""
    return [n for n, _s, _f in plan()]


def stale():
    """できて いる ものが 古い わけ（新しければ ''）。もとが ない ときは None"""
    if not os.path.isdir(SRC):
        return None
    mf = os.path.join(OUT, INFO)
    if not os.path.isfile(mf):
        return '台帳（cb_art.json）が ない'
    man = json.load(open(mf, encoding='utf8'))
    if man.get('v') != V or man.get('p') != PARAMS():
        return '決めごとが かわった'
    for name, src, _f in plan():
        e = man['files'].get(name); sp = os.path.join(SRC, src); op = os.path.join(OUT, name)
        if not e or not os.path.isfile(op) or os.path.getsize(op) != e['size']:
            return 'ない・大きさが ちがう：' + name
        if not os.path.isfile(sp) or e['src'] != [src, os.path.getsize(sp), sha(sp)]:
            return 'もとが かわった：' + src
    return ''


def main():
    if '--check' in sys.argv:
        w = stale(); print('cb_assets →', 'もとの 絵が ない' if w is None else ('新しい' if w == '' else '古い：' + w)); sys.exit(1 if w else 0)
    man = {'v': V, 'p': PARAMS(), 'files': {}}; tot = 0
    for cid, src in CARDS + [('fc_' + f, s_) for f, s_ in FACES] + [('bk_' + b, s_) for b, s_ in BACKS]:
        _o, sz, thin = card(os.path.join(SRC, src))
        print(f'  カード {cid}：もとの 絵の 大きさ {sz[0]}×{sz[1]}（たて横 {sz[0] / sz[1]:.4f}）→ {BASE[0]}×{BASE[1]}・マスクの 中で もとが うすかった 点 {thin}')
    for name, src, fn in plan():
        sp = os.path.join(SRC, src); n = fn(sp, os.path.join(OUT, name)); tot += n
        man['files'][name] = {'src': [src, os.path.getsize(sp), sha(sp)], 'size': n}
        print(f'  {name}  {n / 1000:.1f}KB')
    json.dump(man, open(os.path.join(OUT, INFO), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'できた：{len(man["files"])}こ・{tot / 1e6:.2f}MB → {OUT}')


if __name__ == '__main__':
    main()
