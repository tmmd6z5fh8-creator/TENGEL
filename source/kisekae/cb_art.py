# 馬カードバトルの 絵を アプリに 入れる 形に する（第4.176版・まさちゃん 2026/11/15 21:41「TENGER馬カードバトル …デザイン…これは、俺が作成する」・21:58「これ背面！」）
#   python3 kisekae/cb_art.py            … ios/cb_assets/src/（まさちゃんの 絵 13まい・PNG）→ ios/cb_assets/cb_*.webp（アプリに 入れる 形）
#   python3 kisekae/cb_art.py --check    … できて いる ものが 今の もと・今の 決めごとで 作った ものか だけ 見る（ちがえば 1 で おわる）
#   もと（ios/cb_assets/src/）は **読む だけ**（上書きしない・消さない）。どちらの フォルダも リポジトリには 入れない（.gitignore）
#
#   もとの 絵（名前は 姫が つけた）：
#     cb_1.png 〜 cb_7.png（数字の カード）・cb_k.png（神様馬）・cb_m.png（幻の馬）・cb_back.png（カードの うら）：1024×1536・すき通し あり（角が 丸い）
#     cb_board.png（プレイボード：1672×941・すき通し なし）・cb_deck.png（山札：1254×1254）・cb_icon.png（アイコン：1254×1254）
#   作る もの：
#     カード 10種 × 2つの 大きさ：cb_c<名前>.webp（800×1200：大きく 見る・めくった とき）・cb_s<名前>.webp（300×450：手札・台の 上）。名前＝1〜7・k・m・b（うら）
#       ・カードは もとの 絵ごとに 大きさと たて横が 少し ちがう（おもて 986〜1007×1510〜1521・うら 938×1338）→ 絵の ある 所（すき通しで ない 所）を 切り出して、
#         どれも 同じ たて横（2:3）・同じ 角の 丸み に そろえる（めくった ときに 形が かわらない ように）。うらは たてに 5% ほど のびる（もようは ほぼ そのまま）
#       ・もとの 絵は まん中も 少し すき通って いる（不透明度 242〜254／255）→ まん中は ぴったり 不透明に する。ふちは 4px 内がわで 切る（もとの ふちの にじみを 出さない）
#     cb_board.webp（1254×706）・cb_deck.webp（360×426）・cb_icon.webp（240×240：右下の 丸い ボタン）・cb_logo.webp（720×720：メニューの 絵）
#   台帳 cb_art.json：{ v, files: { 名前: { src: [もとの 名前, 大きさ, sha1], size } } }（アプリには 入れない）
import hashlib, json, os, sys
import numpy as np
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
SRC = os.path.join(W, 'ios', 'cb_assets', 'src'); OUT = os.path.join(W, 'ios', 'cb_assets')
V = 1
CARDS = [('1', 'cb_1.png'), ('2', 'cb_2.png'), ('3', 'cb_3.png'), ('4', 'cb_4.png'), ('5', 'cb_5.png'), ('6', 'cb_6.png'), ('7', 'cb_7.png'), ('k', 'cb_k.png'), ('m', 'cb_m.png'), ('b', 'cb_back.png')]
BASE = (1000, 1500)          # そろえる 大きさ（たて横 2:3）
INSET, RADIUS = 4, 62        # ふちを 内がわへ 4px・角の 丸み 62px（1000×1500 の とき。どの もとの 絵の 角 よりも 内がわ）
BIG, SMALL = (800, 1200), (300, 450)
Q = dict(quality=84, method=6)
INFO = 'cb_art.json'         # 台帳（アプリには 入れない：build_ios.py は cb_*.webp と cb_se_*.m4a だけ 入れる）


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


def card(src):
    """カード 1まい → 1000×1500 の RGBA（float 0〜255）と、マスクの 中で もとが うすかった 所の 数"""
    a = np.asarray(Image.open(src).convert('RGBA'))
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


def plan():
    """作る もの：[(できる 名前, もとの 名前, 作る 関数)]"""
    jobs = []
    for cid, src in CARDS:
        jobs.append((f'cb_c{cid}.webp', src, lambda p, o: save(card(p)[0], BIG, o)))
        jobs.append((f'cb_s{cid}.webp', src, lambda p, o: save(card(p)[0], SMALL, o)))
    def board(p, o):
        im = Image.open(p).convert('RGB').resize((1254, 706), Image.LANCZOS); im.save(o, 'WEBP', quality=86, method=6); return os.path.getsize(o)
    jobs.append(('cb_board.webp', 'cb_board.png', board))
    jobs.append(('cb_deck.webp', 'cb_deck.png', lambda p, o: save(cut(p), (360, 426), o)))
    jobs.append(('cb_icon.webp', 'cb_icon.png', lambda p, o: save(square(cut(p)), (240, 240), o)))
    jobs.append(('cb_logo.webp', 'cb_icon.png', lambda p, o: save(square(cut(p)), (720, 720), o)))
    return jobs


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
    if man.get('v') != V or man.get('p') != [list(BASE), INSET, RADIUS, list(BIG), list(SMALL), Q]:
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
    man = {'v': V, 'p': [list(BASE), INSET, RADIUS, list(BIG), list(SMALL), Q], 'files': {}}; tot = 0
    for cid, src in CARDS:
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
