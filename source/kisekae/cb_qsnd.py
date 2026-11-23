# 決戦調査の フィールドの 音（第4.210版・まさちゃん 2026/11/21〜22）：エリアごとの BGM（フィールドの 間 ずっと くり返す）と、タップ（セリフの 行）ごとの 効果音
#   音は まさちゃんが 送って くれた もの（姫は つなぎ目の プチ・くり返しの 所・音の 切れ目・大きさ だけ 整えた）。デモ（決戦調査の 音の デモ）で まさちゃんが 聞いて 決めた ファイルが もと
#   リポジトリには 入れない（ios/cb_assets/ に 置く：ほかの 絵と 音と 同じ。CI は 音なしで 作る）。形は MP3（44.1kHz・ステレオ〈Lv12 の a は モノラル〉）
#   第4.212版（まさちゃん 2026/11/23 10:12「音の質感、音が俺が聞いてる音と変わらないならやって欲しい！」）：アプリに 入れる ファイルは、もとの MP3 の「つめもの」だけを ぬいた もの（PACK）。
#     音の データは 1ビットも さわらない（kisekae/mp3_repack.py：もう 一度 MP3 に する のでは ない）→ ほどいた 音は もとと 同じ サンプル（長さ・くり返しの 所も 同じ）。
#     10,821,949 → 9,883,489 B（−938,460 B）。もとの ファイル（デモと 同じ バイト：256kbps／192kbps の 決まった 大きさの コマ）は ios/cb_assets/src/qsnd/ に のこす（上書きしない・消さない）。
#     音を 作り直す 方（VBR の V0 で −4.25MB）は 波形が 少し かわる（差 −22〜−62dB）ので、やって いない（まさちゃんが 聞いて 決めて から）。
#     もとに もどす ときは PACK = False に して 入れ直す（デモと 同じ バイトに なる）。
#   第4.213版（まさちゃん 2026/11/23 18:12「音の聞いてて変わらないから軽くして！」）：30こ を 軽い 音（もとの 音を ほどいて LAME の V0 で 包み直した もの：LIGHT）に 入れかえる。
#     まさちゃんが 聞きくらべの ページ（kisekae/qsnd_ab/）で 今の 音と 聞きくらべて 決めた ファイル その もの（同じ バイト：下の V0 の 表の SHA-256）。
#     ほどいた 長さ・位置は もとと 同じ（ずれ 0 サンプル・はじめの フレームの おくれの 数も 同じ）→ くり返しの 所（cb_app.js の QSND）は そのまま。大きさの 差は ±0.07dB の 中。
#     のこりの 7こ（軽く しても zip の 中で 10KB も へらない 6こ・軽い 音の 方が 大きく なる 1こ）は 第4.212版の まま（つめものを ぬいた だけ：音は もとと 同じ サンプル）。
#     37こ：9,883,489 → 6,595,878 B（−3,287,611 B）。軽い 音の ファイルは ios/cb_assets/src/qsnd_v0/ に のこす（まさちゃんが 聞いた バイト：上書きしない・消さない）。
#       そこに ない ときは もとの ファイルから ffmpeg（libmp3lame）で 作り直して、SHA-256 が 表と 同じ ときだけ 使う（ちがう ときは 止まる：聞いて いない 音を 入れない）。
#     第4.212版の 形に もどす ときは LIGHT = False に して 入れ直す（もとの ファイルは ios/cb_assets/src/qsnd/ に のこって いる）。
#   第4.214版（まさちゃん 2026/11/24 00:00「Lv11の3タップ目の音質だけ元々に戻せる？」）：Lv11 の 3タップ目（cb_q_se11b.mp3＝もとの 11_se2.mp3）だけ 軽い 音を やめて、
#     第4.212版の 形（つめものを ぬいた だけ：ほどいた 音は まさちゃんの もとの ファイルと 同じ サンプル）に もどす（下の ORIG）。100,079 → 151,309 B（＋51,230 B）。
#     軽い 音は 29こ・つめものを ぬいた だけ が 8こ。37こ：6,595,878 → 6,647,108 B。ほかの 音を もどす ときは ORIG に 名前を 足して 入れ直す。
#   python3 kisekae/cb_qsnd.py [<もとの snd フォルダ>]  … ios/cb_assets/ に アプリの 名前（cb_q_bgm01.mp3・cb_q_se01a.mp3 …）で 入れる（もと・できた ものを SHA-256 で 確かめる）。
#                                                        フォルダを 書かない ときは ios/cb_assets/src/qsnd/（もとの ファイルは ここにも 写して おく）
#   python3 kisekae/cb_qsnd.py --check                … ios/cb_assets/ の 音が 決めた もの と 同じか
#   python3 kisekae/cb_qsnd.py --light-check          … この パソコンの ffmpeg で もとの ファイルから 軽い 音を 作り直すと、表と 同じ バイトに なるか（何も 入れかえない）
#   鳴らし方（くり返しの 所・何タップ目に どの 音・遅らせる 秒・タップで 止まらない 音）は cb/cb_app.js の QSND（この 表と 同じ 並び：効果音 a・b・c ＝ 0・1・2）
import hashlib, os, shutil, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
OUT = os.path.join(W, 'ios', 'cb_assets')
KEEP = os.path.join(OUT, 'src', 'qsnd')      # もとの ファイル（まさちゃんが デモで 聞いて 決めた バイト）を のこす 所
PACK = True                                  # アプリには つめものを ぬいた ものを 入れる（False：もとの バイトの まま）
LITE = os.path.join(OUT, 'src', 'qsnd_v0')   # 軽い 音（まさちゃんが 聞きくらべて 決めた バイト）を のこす 所（アプリの 名前で）
LIGHT = True                                 # 下の V0 の 表の 音は 軽い 音を 入れる（False：第4.212版の 形＝ぜんぶ つめものを ぬいた だけ）
ORIG = {'cb_q_se11b.mp3'}                    # 第4.214版：軽い 音に しない 音（V0 の 表に あっても 第4.212版の 形＝つめものを ぬいた だけ：音は もとと 同じ サンプル）
# レベル ごと：[BGM の もと, [効果音の もと（a・b・c の 順）]]。もと＝デモの ファイルの 名前・(大きさ, SHA-256 の はじめ 16字)・つめものを ぬいた あとの (大きさ, SHA-256 の はじめ 16字)
SRC = [
    (('1_bgm.mp3', 336919, 'a4d409556d34e92f', 334038, '59413ef0e06c5126'), [('1_se1.mp3', 21986, '15c91f841b5d9e29', 21435, '28c6a67f79af7c26')]),
    (('2_bgm.mp3', 403792, '07e13132ba6dc68c', 395560, '7d6e73e99098751c'), [('2_se1b.mp3', 230757, 'd2e4288092771376', 227194, '77cb2af35f363a86'), ('2_se2c.mp3', 59603, 'bc28bdce558f4da9', 56397, 'f831299a193248ec')]),
    (('3_bgm.mp3', 290107, '9087aa8810a2041a', 284277, 'b51462d0440fc372'), [('3_se1b.mp3', 242042, '8dc89790b4d7a7ba', 231246, '6d1761e865137691'), ('3_se2b.mp3', 62111, '0c3d85325bc63b8b', 61346, '82315a40ef365b14'), ('3_se3.mp3', 131701, '21b89585172a4788', 128685, '15230f5cafaa08d6')]),
    (('4_bgm.mp3', 535031, 'd55bb0278c3fa4c2', 473294, 'f4e533df968cb6d7'), [('4_se1d.mp3', 67753, '05f6a3e13cb93551', 64961, '2e1cac6b213a44bb'), ('4_se2d.mp3', 143613, 'bb284e2206e8255d', 126733, '2018b396e8a84db5'), ('4_se3.mp3', 206933, 'f0c576ab873d2987', 178295, '8a2e427f87378792')]),
    (('5_bgm.mp3', 290943, '7fe4868afab6871a', 285789, 'ff912dee5904ebe2'), [('5_se1.mp3', 118535, '091230a863cef719', 91484, 'a3e5bdcb0d25755c'), ('5_se2.mp3', 64618, 'ef9b7abc07a1a2e9', 54347, 'b7e5606fae0ad043')]),
    (('6_bgm.mp3', 290107, '49f650ba630df3a0', 213486, 'f23e12030d40628a'), [('6_se1b.mp3', 173706, '4e7833aa85f3f936', 170904, '8ba66609c4b35689'), ('6_se2b.mp3', 141105, 'c60ebc6cc2b88bf6', 135700, 'c65e031eeb030c2e')]),
    (('7_bgm.mp3', 290107, 'e7fb4b231aca58a1', 272293, 'adaf33673175e456'), [('7_se2.mp3', 343606, '319ad2ed1322d826', 280193, 'cdaa577bc681853d')]),
    (('8_bgm.mp3', 289271, '224ee9d4199a5656', 282509, '1cbdea701a3554d4'), [('8_se12.mp3', 265239, 'f9714055598bb091', 203470, 'ea4c3327d68bc276'), ('8_se3.mp3', 198156, 'ef00467661861a6d', 187812, '924dba11bdf60df1')]),
    (('9_bgm.mp3', 323544, 'f3dbb7b1886ab230', 306588, '9181968d9a019bb9'), [('9_se1b.mp3', 242669, '04ca0b5415e99c31', 191251, '1bd2105ce231835a'), ('9_se2b.mp3', 181856, 'ffdabdfa41c4ad4f', 155910, '24116036e933c36f')]),
    (('10_bgm.mp3', 444752, '521049f2c705a04d', 263861, '1f0d31bfd72fedac'), [('10_se1.mp3', 184991, 'dd1f78d698314d8a', 170851, '79f99dee695057ba'), ('10_se2.mp3', 242669, '2cdce824924f07b9', 198380, '51c2e7b758116d91')]),
    (('11_bgm.mp3', 1416089, '0d9f30076cbe5bea', 1412023, 'e60fe73c2271972a'), [('11_se1b.mp3', 239534, 'ea364057fb892d3f', 192602, '28be1c7c38bdc7c4'), ('11_se2.mp3', 215084, 'e0bdc7c11a03d034', 151309, '43c1874e2baa9102')]),
    (('12_bgm.mp3', 1369278, 'fb8519813e016357', 1358744, '2f3b2331a36d3968'), [('12_1.mp3', 242669, 'ca25f710f65e0240', 233827, 'fc2d49bef144f6bf'), ('12_2.mp3', 62737, '83c5f65db22dd38a', 61862, '429c679325d175b2'), ('12_3.mp3', 458336, 'ad33917594225463', 424833, '97ddd5e5ee5bf4d4')]),
]
# 軽い 音（第4.213版）：アプリの 名前 → (大きさ, SHA-256 の はじめ 16字)。聞きくらべの ページで まさちゃんが 聞いた ファイルと 同じ。ここに ない 7こ は 今の まま
V0 = {
    'cb_q_bgm01.mp3': (183843, '2c68dedd7bdcb3b9'), 'cb_q_bgm02.mp3': (222933, '57c0ff4409ec894e'), 'cb_q_bgm03.mp3': (154405, 'b5e1707412cf97e7'), 'cb_q_bgm04.mp3': (265333, 'f246147e566fdcec'),
    'cb_q_bgm05.mp3': (164163, 'ef723f46d0276db0'), 'cb_q_bgm06.mp3': (174553, '9d42bb873d7b89c6'), 'cb_q_bgm07.mp3': (148455, '35ba67e2166f3699'), 'cb_q_bgm08.mp3': (155929, '2a0eaf8a9bdb40ec'),
    'cb_q_bgm09.mp3': (144243, '1efe98684058d2fa'), 'cb_q_bgm10.mp3': (169217, '10a38a4b7ed03307'), 'cb_q_bgm11.mp3': (839189, '974e89a6d449c033'), 'cb_q_bgm12.mp3': (777241, 'ee69851231586f31'),
    'cb_q_se02a.mp3': (175635, '06b5f8cd64a825d8'), 'cb_q_se03c.mp3': (96671, 'd011d04f99f6c37d'), 'cb_q_se04b.mp3': (106287, '455b3199790f1b7b'), 'cb_q_se04c.mp3': (132802, '8b03f93d22ec3157'),
    'cb_q_se05a.mp3': (72930, 'db8c79b7eb08cb46'), 'cb_q_se05b.mp3': (41526, '654b0ad26f4a3782'), 'cb_q_se06a.mp3': (132970, '6ff9442a7f241636'), 'cb_q_se07a.mp3': (210901, 'd456bd8778ce8dc2'),
    'cb_q_se08a.mp3': (164349, 'e0d46b2cc23fae57'), 'cb_q_se09a.mp3': (160440, '38e0c285165d40a7'), 'cb_q_se09b.mp3': (109767, 'fa6b5373030519c9'), 'cb_q_se10a.mp3': (104582, '1bea0816d0e4759a'),
    'cb_q_se10b.mp3': (159411, '4895b6bc4100da7c'), 'cb_q_se11a.mp3': (126079, 'db8afd9036091f86'), 'cb_q_se11b.mp3': (100079, 'b58a81fdc42e93a6'), 'cb_q_se12a.mp3': (157417, '04be3f5cd52524ea'),
    'cb_q_se12b.mp3': (44637, '6f29fb1ab34b10ed'), 'cb_q_se12c.mp3': (340994, 'ce4615b08b2ccd72'),
}


def bgm(lv):
    return f'cb_q_bgm{lv:02d}.mp3'


def se(lv, k):
    return f'cb_q_se{lv:02d}{"abc"[k]}.mp3'


def table():
    """[(アプリの 名前, もとの 名前, もとの 大きさ, もとの SHA, つめものを ぬいた 大きさ, その SHA)]"""
    out = []
    for i, (b, ss) in enumerate(SRC):
        out.append((bgm(i + 1),) + b)
        out += [(se(i + 1, k),) + s for k, s in enumerate(ss)]
    return out


def light(name):
    """その 音を 軽い 音で 入れるか"""
    return LIGHT and name in V0 and name not in ORIG


def plan():
    """[(アプリの 名前, もとの 名前, アプリに 入る 大きさ, アプリに 入る SHA-256 の はじめ 16字)]（LIGHT：表の 音は 軽い 音／PACK：ほかは つめものを ぬいた もの）"""
    return [(t[0], t[1]) + (V0[t[0]] if light(t[0]) else t[4:6] if PACK else t[2:4]) for t in table()]


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


def remake(src, dst):
    """もとの MP3 を ほどいて V0 で 包み直す（聞きくらべの ページの 軽い 音と 同じ 作り方：同じ チャンネルの 数・44.1kHz・頭の しるし〈Xing〉つき）"""
    ch = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=channels', '-of', 'csv=p=0', src], check=True, stdout=subprocess.PIPE).stdout.decode().strip()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-map', '0:a:0', '-map_metadata', '-1', '-c:a', 'libmp3lame', '-q:a', '0', '-ac', ch, '-ar', '44100', '-write_xing', '1', dst], check=True)


def same(p, size, h):
    return os.path.isfile(p) and os.path.getsize(p) == size and sig(p) == h


def kind():
    n = sum(1 for t in table() if light(t[0]))
    return f'（軽い 音 {n}こ ＋ つめものを ぬいた {len(table()) - n}こ）' if n else '（つめものを ぬいた 形）' if PACK else '（もとの バイト）'


def main():
    if '--check' in sys.argv:
        w = stale(); n = sum(os.path.isfile(os.path.join(OUT, p[0])) for p in plan())
        print('cb_assets の フィールドの 音 →', f'{n}／{len(plan())}こ', '・ちがう：' + w if w else '・決めた もの と 同じ' + kind()); sys.exit(1 if w or n != len(plan()) else 0)
    if '--light-check' in sys.argv:
        bad = []
        with tempfile.TemporaryDirectory() as tmp:
            for name, src, size, h, _ps, _ph in table():
                if name not in V0: continue
                p = os.path.join(KEEP, src)
                if not same(p, size, h): sys.exit(f'※ もとの {src} が ない か ちがう（{KEEP}）')
                q = os.path.join(tmp, name); remake(p, q)
                if not same(q, *V0[name]): bad.append(name)
        print(f'軽い 音を 作り直した：{len(V0)}こ →', '表と 同じ バイト' if not bad else 'ちがう：' + ' '.join(bad)); sys.exit(1 if bad else 0)
    d = sys.argv[1] if len(sys.argv) > 1 else KEEP
    if not os.path.isdir(d):
        sys.exit('使い方：python3 kisekae/cb_qsnd.py <もとの snd フォルダ>（書かない ときは ios/cb_assets/src/qsnd/）')
    import mp3_repack
    os.makedirs(OUT, exist_ok=True); os.makedirs(KEEP, exist_ok=True); tot = 0; tot0 = 0; made = 0
    for name, src, size, h, psize, ph in table():
        p = os.path.join(d, src)
        if not os.path.isfile(p) or os.path.getsize(p) != size or sig(p) != h:
            sys.exit(f'※ {src} が 決めた もの と ちがう（まさちゃんが デモで 聞いた もの を 使う）')
        k = os.path.join(KEEP, src)
        if os.path.abspath(k) != os.path.abspath(p) and not os.path.isfile(k):
            shutil.copyfile(p, k)                                   # もとの ファイルを のこす（もう ある ときは さわらない）
        a = open(p, 'rb').read(); tot0 += size
        if PACK:
            b, _r = mp3_repack.repack(a); w = mp3_repack.verify(a, b)
            if w or len(b) != psize or hashlib.sha256(b).hexdigest()[:16] != ph:
                sys.exit(f'※ {src} の つめものを ぬいた ものが 決めた もの と ちがう（{w or "大きさ・SHA-256"}）')
        else:
            b = a
        if light(name):                                             # 軽い 音：のこして ある ファイル（まさちゃんが 聞いた バイト）。ない ときは 作り直して、表と 同じ ときだけ 使う
            os.makedirs(LITE, exist_ok=True); lp = os.path.join(LITE, name)
            if not same(lp, *V0[name]):
                if os.path.isfile(lp):
                    sys.exit(f'※ {lp} が 決めた もの と ちがう（まさちゃんが 聞いた 軽い 音を 置いてね。上書きは しない）')
                with tempfile.TemporaryDirectory() as tmp:
                    q = os.path.join(tmp, name); remake(p, q)
                    if not same(q, *V0[name]):
                        sys.exit(f'※ {name} の 軽い 音を 作り直したら 決めた もの と ちがった（ffmpeg の 版が ちがう？ まさちゃんが 聞いた ファイルを {LITE} に 置いてね）')
                    shutil.copyfile(q, lp); made += 1
            b = open(lp, 'rb').read()
        open(os.path.join(OUT, name), 'wb').write(b); tot += len(b)
    print(f'入れた：{len(table())}こ・{tot / 1e6:.2f}MB' + kind() + f'・もと {tot0 / 1e6:.2f}MB' + (f'・軽い 音を 作り直した {made}こ' if made else '') + f' → {OUT}')


if __name__ == '__main__':
    main()
