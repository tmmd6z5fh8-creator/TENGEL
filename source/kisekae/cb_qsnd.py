# 決戦調査の フィールドの 音（第4.210版・まさちゃん 2026/11/21〜22）：エリアごとの BGM（フィールドの 間 ずっと くり返す）と、タップ（セリフの 行）ごとの 効果音
#   音は まさちゃんが 送って くれた もの（姫は つなぎ目の プチ・くり返しの 所・音の 切れ目・大きさ だけ 整えた）。デモ（決戦調査の 音の デモ）で まさちゃんが 聞いて 決めた ファイルを そのまま 使う
#   リポジトリには 入れない（ios/cb_assets/ に 置く：ほかの 絵と 音と 同じ。CI は 音なしで 作る）。形は MP3（44.1kHz・ステレオ〈Lv12 の a は モノラル〉・BGM 256kbps・効果音 192kbps：デモと 同じ バイト）
#   python3 kisekae/cb_qsnd.py <デモの snd フォルダ>   … ios/cb_assets/ に アプリの 名前（cb_q_bgm01.mp3・cb_q_se01a.mp3 …）で 入れる（中身が 決めた もの と 同じか SHA-256 で 確かめる）
#   python3 kisekae/cb_qsnd.py --check                … ios/cb_assets/ の 音が 決めた もの と 同じか
#   鳴らし方（くり返しの 所・何タップ目に どの 音・遅らせる 秒・タップで 止まらない 音）は cb/cb_app.js の QSND（この 表と 同じ 並び：効果音 a・b・c ＝ 0・1・2）
import hashlib, os, shutil, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
OUT = os.path.join(W, 'ios', 'cb_assets')
# レベル ごと：[BGM の もと, [効果音の もと（a・b・c の 順）]]。もと＝デモの ファイルの 名前・(大きさ, SHA-256 の はじめ 16字)
SRC = [
    (('1_bgm.mp3', 336919, 'a4d409556d34e92f'), [('1_se1.mp3', 21986, '15c91f841b5d9e29')]),
    (('2_bgm.mp3', 403792, '07e13132ba6dc68c'), [('2_se1b.mp3', 230757, 'd2e4288092771376'), ('2_se2c.mp3', 59603, 'bc28bdce558f4da9')]),
    (('3_bgm.mp3', 290107, '9087aa8810a2041a'), [('3_se1b.mp3', 242042, '8dc89790b4d7a7ba'), ('3_se2b.mp3', 62111, '0c3d85325bc63b8b'), ('3_se3.mp3', 131701, '21b89585172a4788')]),
    (('4_bgm.mp3', 535031, 'd55bb0278c3fa4c2'), [('4_se1d.mp3', 67753, '05f6a3e13cb93551'), ('4_se2d.mp3', 143613, 'bb284e2206e8255d'), ('4_se3.mp3', 206933, 'f0c576ab873d2987')]),
    (('5_bgm.mp3', 290943, '7fe4868afab6871a'), [('5_se1.mp3', 118535, '091230a863cef719'), ('5_se2.mp3', 64618, 'ef9b7abc07a1a2e9')]),
    (('6_bgm.mp3', 290107, '49f650ba630df3a0'), [('6_se1b.mp3', 173706, '4e7833aa85f3f936'), ('6_se2b.mp3', 141105, 'c60ebc6cc2b88bf6')]),
    (('7_bgm.mp3', 290107, 'e7fb4b231aca58a1'), [('7_se2.mp3', 343606, '319ad2ed1322d826')]),
    (('8_bgm.mp3', 289271, '224ee9d4199a5656'), [('8_se12.mp3', 265239, 'f9714055598bb091'), ('8_se3.mp3', 198156, 'ef00467661861a6d')]),
    (('9_bgm.mp3', 323544, 'f3dbb7b1886ab230'), [('9_se1b.mp3', 242669, '04ca0b5415e99c31'), ('9_se2b.mp3', 181856, 'ffdabdfa41c4ad4f')]),
    (('10_bgm.mp3', 444752, '521049f2c705a04d'), [('10_se1.mp3', 184991, 'dd1f78d698314d8a'), ('10_se2.mp3', 242669, '2cdce824924f07b9')]),
    (('11_bgm.mp3', 1416089, '0d9f30076cbe5bea'), [('11_se1b.mp3', 239534, 'ea364057fb892d3f'), ('11_se2.mp3', 215084, 'e0bdc7c11a03d034')]),
    (('12_bgm.mp3', 1369278, 'fb8519813e016357'), [('12_1.mp3', 242669, 'ca25f710f65e0240'), ('12_2.mp3', 62737, '83c5f65db22dd38a'), ('12_3.mp3', 458336, 'ad33917594225463')]),
]


def bgm(lv):
    return f'cb_q_bgm{lv:02d}.mp3'


def se(lv, k):
    return f'cb_q_se{lv:02d}{"abc"[k]}.mp3'


def plan():
    """[(アプリの 名前, もとの 名前, 大きさ, SHA-256 の はじめ 16字)]"""
    out = []
    for i, (b, ss) in enumerate(SRC):
        out.append((bgm(i + 1),) + b)
        out += [(se(i + 1, k),) + s for k, s in enumerate(ss)]
    return out


def files():
    """アプリに 入れる 名前（cb_sfx.files() が 足す：build_ios.py・テストが 使う）：BGM 12こ ＋ 効果音 25こ"""
    return [p[0] for p in plan()]


def sig(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def stale():
    """ios/cb_assets/ に ある 音が 決めた もの と ちがう わけ（同じ・ない ときは ''：ない ときは build_ios.py が 数を 知らせる）"""
    for name, _src, size, h in plan():
        p = os.path.join(OUT, name)
        if os.path.isfile(p) and (os.path.getsize(p) != size or sig(p) != h):
            return '決戦調査の フィールドの 音が ちがう：' + name
    return ''


def main():
    if '--check' in sys.argv:
        w = stale(); n = sum(os.path.isfile(os.path.join(OUT, p[0])) for p in plan())
        print('cb_assets の フィールドの 音 →', f'{n}／{len(plan())}こ', '・ちがう：' + w if w else '・決めた もの と 同じ'); sys.exit(1 if w or n != len(plan()) else 0)
    if len(sys.argv) < 2:
        sys.exit('使い方：python3 kisekae/cb_qsnd.py <デモの snd フォルダ>')
    d = sys.argv[1]; os.makedirs(OUT, exist_ok=True); tot = 0
    for name, src, size, h in plan():
        p = os.path.join(d, src)
        if not os.path.isfile(p) or os.path.getsize(p) != size or sig(p) != h:
            sys.exit(f'※ {src} が 決めた もの と ちがう（まさちゃんが デモで 聞いた もの を 使う）')
        shutil.copyfile(p, os.path.join(OUT, name)); tot += size
    print(f'入れた：{len(plan())}こ・{tot / 1e6:.2f}MB → {OUT}')


if __name__ == '__main__':
    main()
