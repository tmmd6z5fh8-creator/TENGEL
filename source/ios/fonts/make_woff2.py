"""アプリに入れる 基本の フォントを 字は そのままで WOFF2 に する（第4.109版・まさちゃん「今いらないデータでアプリに影響が出るレベルのもの、消しておいた方がいいデータがあったら教えて！」）。
   python3 ios/fonts/make_woff2.py           → ios/fonts/<名前>.woff2（3こ）を 作って、もとの TTF と 字の 形が 同じ ことを 確かめる
   python3 ios/fonts/make_woff2.py --check   → 作らずに 確かめる だけ
   - しぼらない（ぜんぶの 字を 残す：お客さんが 打つ 開催場や レースの 名前にも 使う）。WOFF2 の 圧縮は 字の 形が かわらない（もどすと 同じ 形）
   - Reserved Font Name が 無い フォントだけ（BIZ UDPGothic・Dela Gothic One）。SIL OFL 1.1 では 形式を かえるのは 改変 → 予約名「Plex」の ある
     IBM Plex Mono は もとの TTF の まま（小さい：2つで 約0.28MB）
   - name の 表（著作権・ライセンス）は そのまま 残る（DSIG＝電子署名の 表だけは WOFF2 の きまりで 入らない）。ライセンスの 全文は OFL-<Family>.txt と アプリの「このアプリについて」
   - 作った WOFF2 は リポジトリに 入れる（build_pwa.py が アプリの fonts/ に 入れる：manual/build_manual.py の APP_FONT_FILES）
   - brotli が 入って いなければ kisekae/brotli_node.py（node の zlib）を 使う（何回 作っても 同じ ファイル）"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'kisekae'))
try:
    import brotli  # noqa: F401
except ImportError:
    import brotli_node as brotli
    sys.modules['brotli'] = brotli
from fontTools.ttLib import TTFont  # noqa: E402

NAMES = ['BIZUDPGothic-Regular', 'BIZUDPGothic-Bold', 'DelaGothicOne-Regular']


def make(name):
    f = TTFont(os.path.join(HERE, name + '.ttf'), recalcBBoxes=False, recalcTimestamp=False)
    f.flavor = 'woff2'
    f.save(os.path.join(HERE, name + '.woff2'))


def same(name):
    """もとの TTF と WOFF2 を もどした ものが 同じ か（字の 並び・cmap・字の 幅・字の 形・name の 表）"""
    a = TTFont(os.path.join(HERE, name + '.ttf'))
    b = TTFont(os.path.join(HERE, name + '.woff2'))
    assert b.flavor == 'woff2', name
    assert a.getGlyphOrder() == b.getGlyphOrder(), name + '：字の 並び'
    assert a.getBestCmap() == b.getBestCmap(), name + '：cmap'
    assert a['hmtx'].metrics == b['hmtx'].metrics, name + '：字の 幅'
    assert [(r.nameID, r.platformID, r.langID, r.toUnicode()) for r in a['name'].names] == [(r.nameID, r.platformID, r.langID, r.toUnicode()) for r in b['name'].names], name + '：name'
    assert sorted(k for k in a.keys() if k != 'DSIG') == sorted(b.keys()), name + '：表'   # DSIG（電子署名）は WOFF2 の きまりで 入れない（形を かえると 合わなく なる）
    ga, gb = a['glyf'], b['glyf']
    for g in a.getGlyphOrder():
        x, y = ga[g], gb[g]
        if x.isComposite():
            assert y.isComposite() and [(c.glyphName, c.x, c.y) for c in x.components] == [(c.glyphName, c.x, c.y) for c in y.components], name + '：' + g
        else:
            cx, ex, fx = x.getCoordinates(ga)
            cy, ey, fy = y.getCoordinates(gb)
            assert list(cx) == list(cy) and list(ex) == list(ey) and [f & 1 for f in fx] == [f & 1 for f in fy], name + '：' + g
    return len(a.getGlyphOrder())


if __name__ == '__main__':
    for n in NAMES:
        if '--check' not in sys.argv:
            make(n)
        g = same(n)
        t, w = os.path.getsize(os.path.join(HERE, n + '.ttf')), os.path.getsize(os.path.join(HERE, n + '.woff2'))
        print(f'{n}: {g} 字・TTF {t / 1e6:.2f}MB → WOFF2 {w / 1e6:.2f}MB（字の 形は 同じ）', flush=True)
