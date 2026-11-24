# 結果ボードカスタム（絵の ボード）：アプリに 入れる 絵を 作り直す（第4.215版・まさちゃん 2026/11/24 01:31 の ①〜④）
#   python3 kisekae/bcp/bcp_remake.py <絵の フォルダ（ios/bcp_assets）> <出す フォルダ> [デザイン…]
#   デザインごとに：
#     1. bcp_ext.make   ：絵の 上・下に 足す 所を 作り直す（光の すじ・やわらかい うつりこみ・iPad の 画面の あとを 消す）
#     2. bcp_fg2.make   ：ボードの 前の 絵を 絵の ぎりぎりで 切りぬき直す → bcp_<デザイン>_f2.webp（前の 絵が ある デザイン だけ）
#     3. bcp_blank.clean：板の 中を ぬり直す（新しい 前の 絵に 合わせて・絵の ぎりぎり まで）→ bcp_<デザイン>_b2.webp
#   もとの 絵（bcp_<デザイン>.webp・_fg.webp・_bl.webp）は 読む だけ（消さない・上書きしない）。できた 絵を 絵の フォルダへ 写す ときも 新しい 名前 なので 上書きに ならない
#   第4.216版（まさちゃん 2026/11/24 11:39「赤丸のところ、枠がガタガタしてたり書き直しが甘かったりするところあるから、確認して描き直して！」）：--v3
#     4. bcp_rays2.fix ：花束の 上下・自撮りの 上の 光の すじを 描き直す（物＝花びら・紙ふぶき・星は もとの 絵から のせなおす）
#     5. bcp_rim.fix   ：乾杯の 板の ふち（わくの 内がわの 段）の 四角い 出っぱり・へこみを なおす（虹色の 乾杯④は 色が かわる ので しない）
#     6. bcp_rim.paste_orig：花束①・④の 板の 右上の 四角い 紺の かたまり（11/03 に 紙ふぶきを 消す とき 四角く ぬった あと）→
#        まさちゃんの もとの 絵（<BCPIC>/<デザイン>/src.png・リポジトリに 入れない）から その 所だけ くりぬいて かぶせる（前の 絵も 直す）
#        （まさちゃん 12:47「元のデータからここだけくり抜いて上から被せちゃえば？」・13:24「花束ボードの元のデータある？」。はじめの 直し fix_tab は 使わない）
#     → bcp_<デザイン>_b3.webp（前の 絵を 直した ときは _f3.webp も）。前の _b2・_f2 は 消さない・上書きしない
import sys, os, io, time, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import bcp_app, bcp_blank, bcp_ext, bcp_fg2
BG, FG = '_b2', '_f2'
BG3, FG3 = '_b3', '_f3'
RIM = ('toast1', 'toast2', 'toast3')


def remake(src, out, name, keep_ext=None):
    t = time.time(); E = bcp_ext.make(src, name)
    if keep_ext: Image.fromarray(np.clip(E + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(keep_ext, f'bcp_{name}.png'))
    has_fg = bool(bcp_app.cfg(name).get('fg')); fgm = None; info = ''
    if has_fg:
        f2 = bcp_fg2.make(src, name, P=E); fp = os.path.join(out, f'bcp_{name}{FG}.webp'); Image.fromarray(f2, 'RGBA').save(fp, 'WEBP', quality=90, method=6)
        f2 = np.asarray(Image.open(fp).convert('RGBA')); fgm = f2[..., 3] > 8; info = f' 前の絵 {int(fgm.sum())}px {os.path.getsize(fp)}B'
    o, M = bcp_blank.clean(src, name, bcp_blank.cfg_of(name, v2=True), P=E, fg=fgm if has_fg else np.zeros(E.shape[:2], bool))
    bp = os.path.join(out, f'bcp_{name}{BG}.webp'); Image.fromarray(o).save(bp, 'WEBP', quality=90, method=6)
    print(name, bcp_ext.fam_of(name) or '-', 'ぬり直した 点', int(M.sum()), os.path.getsize(bp), 'B' + info, round(time.time() - t, 1), 's', flush=True)


def _webp_rgba(a):
    """RGBA を WebP（quality 90）に して 読みもどす（アプリに 入る 前の 絵と 同じ 画素）"""
    b = io.BytesIO(); Image.fromarray(a, 'RGBA').save(b, 'WEBP', quality=90, method=6); return np.asarray(Image.open(io.BytesIO(b.getvalue())).convert('RGBA')), b.getvalue()


def remake3(src, out, name):
    """第4.216版：すじ・板の ふち・右上の 四角を 描き直した 絵（_b3・前の 絵を 直した ときは _f3）。→ 前の 絵を 新しく した か"""
    import bcp_rays2, bcp_rim
    t = time.time(); E0 = bcp_ext.make(src, name)
    S = np.asarray(Image.open(os.path.join(src, f'bcp_{name}.webp')).convert('RGB')).astype(np.float32)
    q = np.array(bcp_app.design(name)['q'], np.float64) * 3
    has_fg = bool(bcp_app.cfg(name).get('fg'))
    F2 = np.asarray(Image.open(os.path.join(src, f'bcp_{name}{FG}.webp')).convert('RGBA')) if has_fg else None
    E = bcp_rays2.fix(E0, S, name, q, None if F2 is None else F2[..., 3] > 8)
    new_fg = False; F = F2
    if has_fg and name in bcp_rays2.RAYS:                                         # すじを かえた：前の 絵（すじの 上の 物）が かわる なら 新しく
        fo, fn = bcp_fg2.make(src, name, P=E0), bcp_fg2.make(src, name, P=E)
        if not np.array_equal(fo, fn): F, _b = _webp_rgba(fn); new_fg = True
    fgm = F[..., 3] > 8 if has_fg else np.zeros(E.shape[:2], bool)
    model = {}
    o, M = bcp_blank.clean(src, name, bcp_blank.cfg_of(name, v2=True), P=E, fg=fgm, model=model)
    info = ''
    if name in RIM:
        o, ch = bcp_rim.fix(o, model['geo'], fgm); info += f' ふち {int(ch.sum())}px'
    if name in bcp_rim.ORIG:                                                       # 花束①・④の 右上：まさちゃんの もとの 絵から かぶせる
        o, F, ch = bcp_rim.paste_orig(o, F, bcp_app.cfg(name), name); new_fg = new_fg or F is not None; info += f' 右上（もとの 絵） {int(ch.sum())}px'
    bp = os.path.join(out, f'bcp_{name}{BG3}.webp'); assert not os.path.exists(bp), f'もう ある（上書きしない）：{bp}'
    Image.fromarray(o).save(bp, 'WEBP', quality=90, method=6); info += f' {os.path.getsize(bp)}B'
    if new_fg:
        fp = os.path.join(out, f'bcp_{name}{FG3}.webp'); assert not os.path.exists(fp), f'もう ある（上書きしない）：{fp}'
        Image.fromarray(F, 'RGBA').save(fp, 'WEBP', quality=90, method=6); info += f' 前の絵 {os.path.getsize(fp)}B'
    print(name, 'v3', info, '前の絵', '新' if new_fg else 'そのまま', round(time.time() - t, 1), 's', flush=True)
    return new_fg


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--v3':
        src, out = sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
        for n in sys.argv[4:]:
            remake3(src, out, n)
        sys.exit(0)
    if len(sys.argv) < 3:
        print('使い方：bcp_remake.py <絵の フォルダ> <出す フォルダ> [デザイン…]'); sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); ke = os.environ.get('KEEP_EXT')
    if ke: os.makedirs(ke, exist_ok=True)
    for n in (sys.argv[3:] or [n for _i, _k, st in bcp_app.ITEMS for _d, n in st]):
        remake(src, out, n, ke)
