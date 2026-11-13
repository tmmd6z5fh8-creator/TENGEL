# 壁紙の 馬の 絵を 画面の 3倍に（第4.156版・第4.157版：まさちゃん 2026/11/12 04:20「Aにして！あと、課金の壁紙は全部馬の画質が悪いから同じように画質を上げてほしい！」）
#   python3 test_wall_hq.py   （壁紙の 絵 ios/kisekae_blobs/ が 手元に ある とき だけ 絵と 画面も。ない とき（CI）は 台帳と ページの 形 だけ）
#   第4.156版：競馬新聞・勝負服・夕焼け ／ 第4.157版：水墨画・ネオン（走る コマ）・花火（馬の 足す光）・ナイター（走る コマ・止まる／走りだす コマ・表彰の 絵）＝ 7つ ぜんぶ
#   ・台帳：馬の 絵の id は 新しい 絵・切りぬく 場所と コマの 数は 前と 同じ・絵の 細かさ scale＝1.5（＝画面の 3倍）
#   ・ページ（news_wall.py など）：シートの 大きさは pt の まま（前と 同じ 場所・同じ 動き）。花火は 馬の 段 だけ 別の 絵から 出す（fireworks_wall.py）
#   ・絵は リポジトリに 入って いない・作る 道具（flat/hq_*.py）と 入れる 道具（flat/hq_install.py）は ある
#   ・絵：名前は 中身の md5・1コマは pt の 3倍・前の 絵（2倍）も 手元に のこって いる（消して いない）・同じ 絵（小さく すると 前の 絵と 同じ・馬の 場所も 同じ）・前より 細かい
#     花火：花火 4つは 前の 絵と 1画素も ちがわない・馬の 8組を 足すと 前と 同じ 絵・組ごとの 光の 割合も 前と 同じ（散り方は かわらない）
#   ・アプリの 画面（iPhone と 同じ 3倍）：絵の 3px を 1pt に 出す・動く・前の 絵（2倍）に さしかえた ときより くっきり・エラー なし
#     iPad の「iPhone の 大きさ」（2倍の 画面）でも 同じ 場所に 出る
#   第4.166版（まさちゃん 2026/11/13 15:21「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）：
#     競馬新聞・勝負服・夕焼け・水墨画の 走る コマは 10 → **15コマ**（0.5秒で 1回り＝1コマ 1/30秒 ちょうど）。絵の 細かさ（画面の 3倍）は そのまま。
#     ・台帳：コマの 数 15・切りぬく 場所は コマが ふえた 分 だけ 少し かわる（前の 場所から 12画素 まで）
#     ・絵：同じ 位相の コマ（新しい 0・3・6・9・12 ＝ 前の 0・2・4・6・8）は 前の 絵（2倍）と 同じ 絵・同じ 場所（上下の 動きは 前の 動きの まま）
#     ・アプリの 画面：1コマめ（前と 同じ 形）で 前の 絵（2倍）に さしかえて くらべる・1回り 0.5秒・15コマ
#     ネオン（アプリに 入れて いない）と ナイターは 10コマの まま
import hashlib, io, json, os, re, shutil, subprocess, sys, time
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae')
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


HEX = lambda v: bool(re.fullmatch(r'[0-9a-f]{32}', v))
#           台帳の キー・id の 前に つく もの・run.json の どこ・前の 絵（2倍）・切りぬく 場所・絵の 形・ページの 動く 所／その 窓・絵の 大きさ（バイト）の はんい・
#           dmin＝前の 絵を のばした ものより どれだけ 細かいか（絵）・smin＝同じ（アプリの 画面）。ネオンは 光の にじみが 多い 絵なので 差は 小さい
SET = {'news': dict(jp='競馬新聞', key='run', pre='', sub=None, old='90c9d3f81a75c530c5dcaf297f8bfafb', cell=[208, 76, 360, 200], mode='RGB', el='.nsw .nsr', win='.nsw .nsh', anim='nsRun', kb=(110, 200), hq165='0352aceb759e1da7dfc1dc208c08876b', dmin=1.3, smin=1.12),
       'silks': dict(jp='勝負服', key='run', pre='', sub=None, old='a6f4674ee0a8a396c3f9df8527b92f77', cell=[70, 24, 612, 292], mode='RGBA', el='.sbw .sbr', win='.sbw .sbh', anim='sbRun', kb=(430, 720), hq165='2d4d141890936b1c4d001b4923332ad3', dmin=1.3, smin=1.12),
       'sunset': dict(jp='夕焼け', key='horse', pre='/_blob/', sub='horse', old='3f932ad749f07e3a3d47e32e8004914e', cell=[204, 26, 430, 228], mode='RGBA', el='.ssw .sxr', win='.ssw .sxh', anim='sxRun', kb=(210, 360), hq165='00fe98049715d46ecfdac7210aada1f9', dmin=1.3, smin=1.12),
       'ink': dict(jp='水墨画', key='run', pre='', sub=None, old='2a2aa8796320a888283cdacb060f4be1', cell=[112, 32, 596, 266], mode='RGB', el='.ikw .ikr', win='.ikw .ikh', anim='ikRun', kb=(340, 580), hq165='4115d8c9d46de3bca33d03f72088d265', dmin=1.3, smin=1.12),
       'neon': dict(jp='ネオン', key='run', pre='', sub=None, old='0417b8e6f0ca61b59a999f45f38744bd', cell=[170, 0, 284, 320], mode='RGBA', el='.nqw .nqr', win='.nqw .nqh', anim='nqRun', kb=(220, 400), dmin=1.04, smin=1.02)}
# 第4.160版（まさちゃん 2026/11/12 14:31「壁紙のネオン消して！」）：ネオンは アプリから 外した。絵と 作る 道具・台帳は 手元／リポジトリに のこす ので、台帳・ページ・絵の 確かめは そのまま。
#   アプリの 中身と 画面の 確かめ（IN_APP）からは 外して、「アプリに 入って いない」ことを 見る
IN_APP = [nm for nm in SET if nm != 'neon']
N = 10; SC = 1.5
N15 = ('news', 'silks', 'sunset', 'ink')                     # 第4.166版：15コマ（1コマ 1/30秒）。ネオンは 10コマの まま（アプリには 入って いない）。ナイターは 第4.167版で 15コマ
NF = {nm: (15 if nm in N15 else N) for nm in SET}
CELL = {}                                                     # いまの 切りぬく 場所（台帳から）。SET の cell は 前の 絵（2倍・10コマ）の 場所
sys.path.insert(0, K)
import news_wall, silks_wall, sunset_wall, ink_wall, neon_wall, fireworks_wall, night_wall
MOD = dict(news=news_wall, silks=silks_wall, sunset=sunset_wall, ink=ink_wall, neon=neon_wall)
ID = {}; RUN = {}
for nm, s in SET.items():
    blobs = json.load(open(os.path.join(K, nm + '_blobs.json'), encoding='utf8')); run = json.load(open(os.path.join(K, nm + '_run.json'), encoding='utf8'))
    info = run[s['sub']] if s['sub'] else run
    v = blobs[s['key']]; ID[nm] = v[len(s['pre']):]; RUN[nm] = run; n = NF[nm]; CELL[nm] = info['cell']
    if nm in N15:
        near = all(abs(a - b) <= 12 and a % 2 == 0 for a, b in zip(info['cell'], s['cell']))
        check(v.startswith(s['pre']) and HEX(ID[nm]) and ID[nm] not in (s['old'], s['hq165']) and near and info['frames'] == n and info.get('scale') == SC
              and s['old'] not in json.dumps(blobs) and s['hq165'] not in json.dumps(blobs),
              f'台帳（{s["jp"]}）：走る コマは 新しい 絵（第4.166版）・コマの 数 {info["frames"]}・切りぬく 場所 {info["cell"]}（前は {s["cell"]}）・絵の 細かさ {info.get("scale")}倍（＝画面の 3倍）')
    else:
        check(v.startswith(s['pre']) and HEX(ID[nm]) and ID[nm] != s['old'] and info['cell'] == s['cell'] and info['frames'] == n and info.get('scale') == SC
              and s['old'] not in json.dumps(blobs),
              f'台帳（{s["jp"]}）：走る コマは 新しい 絵・切りぬく 場所 {s["cell"]} と コマの 数 {n} は 前と 同じ・絵の 細かさ {info.get("scale")}倍（＝画面の 3倍）')
    x0, y0, cw, ch = (v // 2 for v in info['cell'])
    html, css = MOD[nm].inline(MOD[nm].load_blobs(os.path.join(K, nm + '_blobs.json')), run)
    check(f'{s["el"]}{{width:{n * cw}px;height:{ch}px;background:url(/_blob/{ID[nm]}) 0 0/{n * cw}px {ch}px no-repeat;' in css and f'steps({n})' in css and f'translateX(-{n * cw}px)' in css
          and f'left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden' in css and s['old'] not in css + html
          and (nm not in N15 or bool(re.search(r'animation:%s 0?\.5s steps\(15\) infinite' % s['anim'], css))),
          f'ページ（{s["jp"]}）：窓は 左 {x0}・上 {y0}・{cw}×{ch}pt・シートは {n * cw}×{ch}pt（pt の まま）・絵は 新しい id' + ('・0.5秒で 15コマ（1コマ 1/30秒）' if nm in N15 else ''))

# ---- 花火（第4.157版）：馬の 足す光 だけ 別の 絵（8組を 横に・画面の 3倍）。花火 4つの 絵は 前の 絵から 馬の 段を 切り落とした もの
FW_OLD = '64be0e0e3c35a9c3c4f2656f72b1144a'; NG = 8
FWB = json.load(open(os.path.join(K, 'fireworks_blobs.json'), encoding='utf8')); FWL = json.load(open(os.path.join(K, 'fireworks_layers.json'), encoding='utf8'))
fsw, fsh = FWL['sheet']; fh = FWL['layers'][-1]; fx, fy, fw, fhh = fh['rect']; fsy = fh['sheet_y']
check(sorted(FWB) == ['base', 'scatter', 'scatter_h'] and all(HEX(v) for v in FWB.values()) and FW_OLD not in json.dumps(FWB) and FWB['base'] == 'b9925a44f1d90cc6e3adf5d8ca09f76b'
      and [fsw, fsh] == [362, 862] and len(FWL['layers']) == 5 and fh['kind'] == 'horse' and fh['rect'] == [206, 50, 362, 206] and fsy == 656 and [e['kind'] for e in FWL['layers'][:4]] == ['burst'] * 4,
      f'台帳（花火）：馬の 足す光は 新しい 絵（scatter_h）・花火 4つは 馬の 段を 切り落とした 絵（scatter）・下の 絵と 置く 場所（fireworks_layers.json：馬 {fh["rect"]}）は 前と 同じ')
fhtml, fcss = fireworks_wall.inline(fireworks_wall.load_blobs(os.path.join(K, 'fireworks_blobs.json')), FWL)
check(f'.hqw .hqc i{{display:block;background:url(/_blob/{FWB["scatter"]}) 0 0/{NG * fsw / 2:g}px {fsy / 2:g}px no-repeat;' in fcss
      and f'.hqw .hq4 .hqc i{{background-image:url(/_blob/{FWB["scatter_h"]});background-size:{NG * fw / 2:g}px {fhh / 2:g}px}}' in fcss
      and f'.hqw .hq4{{left:{fx // 2}px;top:{fy // 2}px;width:{fw // 2}px;height:{fhh // 2}px}}' in fcss
      and all(f'<i style="background-position:-{g * fw // 2}px 0;' in fhtml for g in range(NG)) and fhtml.count('px 0;animation-duration') == NG
      and all(f'<i style="background-position:-{g * fsw // 2}px -{e["sheet_y"] // 2}px;' in fhtml for e in FWL['layers'][:4] for g in range(NG)) and FW_OLD not in fcss + fhtml,
      f'ページ（花火）：馬は 左 {fx // 2}・上 {fy // 2}・{fw // 2}×{fhh // 2}pt の まま・馬の 8組は 馬 だけの 絵（{NG * fw // 2}×{fhh // 2}pt）から・花火 4つは {NG * fsw // 2}×{fsy // 2}pt の 絵から（場所は 前と 同じ）')
h0, c0 = fireworks_wall.inline({'base': '/_blob/' + 'a' * 32, 'scatter': '/_blob/' + 'b' * 32}, FWL)
check(f') 0 0/{NG * fsw / 2:g}px {fsh / 2:g}px no-repeat;' in c0 and '.hq4 .hqc i{' not in c0 and f'<i style="background-position:-{7 * fsw // 2}px -{fsy // 2}px;' in h0 and fhtml.count('<i style=') == h0.count('<i style=')
      and re.sub(r'background-position:[^;]*;', '', fhtml.replace(FWB['scatter'], 'b' * 32).replace(FWB['base'], 'a' * 32)) == re.sub(r'background-position:[^;]*;', '', h0),
      'ページ（花火）：馬の 絵が 別で ない 台帳（前の 形）でも 今までどおり 出せる・ちがいは 馬の 段の 絵の 場所 だけ（動き・きらめき・火の粉は 1字も かわらない）')

# ---- ナイター（第4.157版）：3頭の 走る コマ（h）・止まる／立つ／走りだす コマ（t）・表彰の 絵（a）＝ 9まい。コースの 絵 3まい（far・track・rail）は そのまま
NT_OLD = dict(h5='d9208aa63d454494f1d3ddbe65515aef', h3='425479ad8bee8af3244ae5c846a45827', h7='396981d8625d3649c7e5a195529a1699',
              t5='cd33141a32744cb8b094d9bc5d9b2fcf', t3='6954a38b26ed8edbd0e42cd0391b8766', t7='395e647ee206dad5b4786b39921769e3',
              a5='6e7e653b8aa554da8140dace813b0390', a3='7be1e8a6dbc41e71235880baafbd0115', a7='bd07184da2c173a49c5ee233e4b87751')
NT_KEEP = dict(far='d42c84d00c06bbc5dbda2ac042481eeb', track='e5b85de4f796815ad8f92a07b14c074e', rail='c7fe0d55b5c05b3338b9561c3979d3e9')
NT_CELL = {'5': ([234, 120], [424, 110], [236, 118], [422, 112]), '3': ([326, 178], [-50, 100], [324, 178], [-50, 100]), '7': ([420, 216], [144, 78], [416, 216], [146, 78])}
NTB = json.load(open(os.path.join(K, 'night_blobs.json'), encoding='utf8')); NTR = json.load(open(os.path.join(K, 'night_run.json'), encoding='utf8'))
# 第4.167版：走る コマは 15（1コマ 1/30秒）・止まる／走りだすは 時刻で 決めた コマ（72コマ・12×6・1倍・ロスあり：動いて いる 間 だけ 見える）・立つ 絵（s：1.5倍・ロスなし）は べつの 1まい
NT_165 = dict(h5='8edbf16f7bf2d3ba9a951373614bc6a0', h3='c8ddf7dde0c9c54f1283130f667d7ac2', h7='28aabf8f3c948aa11be5cdc994b41bfd',
              t5='bea400d33650a1f2ec4883509e122ecc', t3='bcae27477a2a8b2213ded5fb74d847d5', t7='ab2f74677fb738915dcdd60dc0c35163')      # 第4.157〜4.166版の 走る 10コマ・止まる／立つ／走りだす 18コマ（1.5倍）
NT_AW = dict(a5='88c59aad22f3a012cd1264e2d4f7fa77', a3='09304cce3330dec0846b518d4609b380', a7='33cc560b6158d1fde6c5b1dfaf889ce2')        # 表彰の 絵は 第4.157版の まま
NTN = 15; NT_COLS, NT_ROWS = 12, 6
NTC = {n: (NTR['horses'][n]['cell'], NTR['horses'][n]['at'], NTR['trans'][n]['cell'], NTR['trans'][n]['at']) for n in NT_CELL}                # いまの 切りぬく 場所（台帳から）
inside_ = lambda new, old: new[1][0] <= old[1][0] and new[1][1] <= old[1][1] and new[1][0] + new[0][0] >= old[1][0] + old[0][0] and new[1][1] + new[0][1] >= old[1][1] + old[0][1]
check(sorted(NTB) == sorted(list(NT_OLD) + ['s5', 's3', 's7'] + list(NT_KEEP)) and all(HEX(v) for v in NTB.values()) and len(set(NTB.values())) == 15
      and all(NTB[k] != o and o not in json.dumps(NTB) for k, o in NT_OLD.items()) and all(NTB[k] != o and o not in json.dumps(NTB) for k, o in NT_165.items())
      and all(NTB[k] == o for k, o in NT_AW.items()) and all(NTB[k] == o for k, o in NT_KEEP.items()) and NTR.get('scale') == SC and NTR['size'] == [780, 320]
      and all(NTR['horses'][n]['frames'] == NTN and inside_((NTC[n][0], NTC[n][1]), (c[0], c[1])) and all(v % 2 == 0 for v in NTC[n][0] + NTC[n][2])
              and [NTR['trans'][n]['cols'], NTR['trans'][n]['rows'], len(NTR['trans'][n]['frames'])] == [NT_COLS, NT_ROWS, NT_COLS * NT_ROWS] and NTR['trans'][n]['stand']['kind'] == 'stand'
              for n, c in NT_CELL.items()),
      f'台帳（ナイター）：3頭の 走る コマ（15コマ）・止まる／走りだす コマ（72コマ）・立つ 絵（新しい キー s5・s3・s7）は 新しい 絵・表彰の 絵 3まいと コースの 絵 3まいは そのまま・'
      f'走る コマの 切りぬく 場所は 前の 場所を ふくむ・絵の 細かさ {NTR.get("scale")}倍')
nhtml, ncss = night_wall.inline(night_wall.load_blobs(os.path.join(K, 'night_blobs.json')), NTR)
okp = all(o not in ncss + nhtml for o in list(NT_OLD.values()) + list(NT_165.values())) and '.ntv' not in ncss + nhtml and 'ntu' not in nhtml
for n in NT_CELL:
    (cw, ch), (ax, ay), (tw, th), (tx, ty) = [[v / 2 for v in x] for x in NTC[n]]
    okp = (okp and f'.nts{n}{{width:{NTN * cw:g}px;height:{ch:g}px;background:url(/_blob/{NTB["h" + n]}) 0 0/{NTN * cw:g}px {ch:g}px no-repeat;will-change:transform;animation:ntS{n} 0.5s steps({NTN}) infinite}}' in ncss
           and f'.ntq{n}{{width:{tw:g}px;height:{th:g}px;background:url(/_blob/{NTB["t" + n]}) 0 0/{NT_COLS * tw:g}px {NT_ROWS * th:g}px no-repeat;' in ncss
           and f'.nto{n}{{background:url(/_blob/{NTB["s" + n]}) 0 0/{tw:g}px {th:g}px no-repeat;' in ncss
           and f'.ntz{n}{{background:url(/_blob/{NTB["a" + n]}) 0 0/390px 160px no-repeat}}' in ncss
           and f'.ntc{n}{{position:absolute;left:{ax:g}px;top:{ay:g}px;width:{cw:g}px;height:{ch:g}px;overflow:hidden;' in ncss
           and f'.ntk{n},.nto{n}{{position:absolute;left:{tx:g}px;top:{ty:g}px;width:{tw:g}px;height:{th:g}px}}' in ncss)
check(okp, 'ページ（ナイター）：3頭の 窓・走る シート（15コマを 0.5秒）・止まる／走りだす シート（窓と 同じ 大きさの 所で めくる）・立つ 絵・表彰の 絵の 大きさは pt・絵は 新しい id・'
      'ギャロップの コマを 借りる 重ね（.ntu・.ntv）は ない')

gi = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
tools = ['hq_news.py', 'hq_silks.py', 'hq_sunset.py', 'hq_ink.py', 'hq_neon.py', 'hq_fireworks.py', 'hq_night.py', 'hq_install.py']
check(not any(f.startswith('ios/kisekae_blobs/') for f in gi) and all(os.path.exists(os.path.join(K, 'flat', f)) and ('kisekae/flat/' + f) in gi for f in tools)
      and all('/home/claude' not in open(os.path.join(K, 'flat', f), encoding='utf8').read() for f in tools),
      '壁紙の 絵は リポジトリに 入って いない・作る 道具（flat/hq_news.py・hq_silks.py・hq_sunset.py・hq_ink.py・hq_neon.py・hq_fireworks.py・hq_night.py）と 入れる 道具（flat/hq_install.py）が ある')
ALL_NEW = list(ID.values()) + [FWB['scatter'], FWB['scatter_h']] + [NTB[k] for k in NTB if k not in NT_KEEP]
have = os.path.isdir(BL) and all(os.path.exists(os.path.join(BL, i + '.webp')) for i in ALL_NEW)
if not have:
    print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、絵と アプリの 画面の 確かめは しない')
    print('結果：', 'NG ' + str(len(fails)) if fails else 'OK'); sys.exit(1 if fails else 0)
import numpy as np
from PIL import Image
P = lambda i: os.path.join(BL, i + '.webp')
MD5 = lambda i: hashlib.md5(open(P(i), 'rb').read()).hexdigest() == i
LOSSLESS = lambda i: open(P(i), 'rb').read()[12:16] == b'VP8L'


def load(p):
    """0〜1 の 数。すき通しの ある 絵は 色×濃さ（＋濃さ）で くらべる"""
    im = Image.open(p); im = im.convert('RGBA') if im.mode == 'RGBA' else im.convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255
    return np.dstack([a[..., :3] * a[..., 3:], a[..., 3]]) if a.shape[2] == 4 else a


def psnr(x, y):
    m = float(((x - y) ** 2).mean()); return 99.0 if m < 1e-12 else 10 * np.log10(1 / m)


def detail(a):
    """絵の 細かさ（となりの 点との 差の 大きさ：ぼやけた 絵ほど 小さい）"""
    g = a[..., :3].mean(2)
    return float(np.abs(4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).mean())


def resize(a, size, how):
    """大きさを かえる（色ごとに 小数の まま：すき通しつきの 絵は 色×濃さの 数を そのまま 使う。第4.157版：8bit の RGBA として 渡すと 濃さを もう 1回 かけて しまう のを 直した）"""
    return np.clip(np.dstack([np.asarray(Image.fromarray(np.ascontiguousarray(a[..., c], np.float32), 'F').resize(size, how)) for c in range(a.shape[2])]), 0, 1)


def same_pic(A, O, cols=1, rows=1, alpha=True):
    """新しい 絵 A（1.5倍）と 前の 絵 O：(2/3 に 小さく した ときの PSNR, 前の 絵を のばした ものより どれだけ 細かいか, コマごとの 重心の ずれ pt)"""
    small = resize(A, (O.shape[1], O.shape[0]), Image.LANCZOS); up = resize(O, (A.shape[1], A.shape[0]), Image.BILINEAR)
    off = 0.0
    if alpha and A.shape[2] == 4:          # 馬の 場所（コマごとの 濃さの 重心：pt）
        for r in range(rows):
            for i in range(cols):
                c = []
                for a, k in ((A, 3.0), (O, 2.0)):
                    w, h = a.shape[1] // cols, a.shape[0] // rows; al = a[r * h:(r + 1) * h, i * w:(i + 1) * w, 3]; ys, xs = np.mgrid[0:al.shape[0], 0:al.shape[1]]; m = al.sum()
                    c.append(((xs * al).sum() / m / k, (ys * al).sum() / m / k))
                off = max(off, abs(c[0][0] - c[1][0]), abs(c[0][1] - c[1][1]))
    return psnr(O, small), detail(A) / max(detail(up), 1e-9), off


def common(A, O, cn, co, k=5):
    """第4.166版：同じ 位相の コマ（新しい 15コマの 0・3・6・9・12 と 前の 10コマの 0・2・4・6・8）を、2つの 切りぬきが 重なる 所 だけ ならべる → (新しい 絵, 前の 絵)。
       cn・co：新しい・前の 切りぬく 場所 [左, 上, 幅, 高さ]（壁紙の 絵 780×320 の 画素）。A は その 1.5倍・O は 1倍"""
    X0, Y0 = max(cn[0], co[0]), max(cn[1], co[1]); X1, Y1 = min(cn[0] + cn[2], co[0] + co[2]), min(cn[1] + cn[3], co[1] + co[3])
    wa, wo = int(cn[2] * SC), co[2]
    pa = [A[int((Y0 - cn[1]) * SC):int((Y1 - cn[1]) * SC), 3 * i * wa + int((X0 - cn[0]) * SC):3 * i * wa + int((X1 - cn[0]) * SC)] for i in range(k)]
    po_ = [O[Y0 - co[1]:Y1 - co[1], 2 * i * wo + X0 - co[0]:2 * i * wo + X1 - co[0]] for i in range(k)]
    return np.concatenate(pa, 1), np.concatenate(po_, 1)


tot_new = tot_old = 0
for nm, s in SET.items():
    x0, y0, cw, ch = CELL[nm]; ox0, oy0, ocw, och = s['cell']; n = NF[nm]; pn, po = P(ID[nm]), P(s['old'])
    im = Image.open(pn); szn = os.path.getsize(pn)
    okf = MD5(ID[nm]) and im.format == 'WEBP' and im.mode == s['mode'] and im.size == (int(cw * SC) * n, int(ch * SC)) == (3 * (cw // 2) * n, 3 * (ch // 2))
    oko = os.path.exists(po) and Image.open(po).size == (ocw * N, och)        # 前の 絵（キャンバスの id の まま：名前は md5 では ない・10コマ）
    tot_new += szn; tot_old += os.path.getsize(po) if oko else 0
    check(okf and oko and s['kb'][0] * 1000 < szn < s['kb'][1] * 1000,
          f'絵（{s["jp"]}）：名前は 中身の md5・1コマ {int(cw * SC)}×{int(ch * SC)}px（{cw // 2}×{ch // 2}pt の 3倍）・{szn / 1e3:.0f}KB（前 {os.path.getsize(po) / 1e3 if oko else 0:.0f}KB）・前の 絵（2倍）も 手元に のこって いる')
    if not (okf and oko):
        continue
    if nm in N15:                                                             # 同じ 位相の 5コマ（重なる 所）で くらべる
        ps, dr, off = same_pic(*common(load(pn), load(po), CELL[nm], s['cell']), 5)
        check(ps > 25 and dr > s['dmin'] and off < 0.3,
              f'絵（{s["jp"]}）：同じ 位相の 5コマ（新しい 0・3・6・9・12 ＝ 前の 0・2・4・6・8）は 同じ 絵（2/3 に 小さく すると 前の 絵と 同じ：PSNR {ps:.1f}dB'
              + (f'・馬の 場所の ずれ {off:.2f}pt' if s['mode'] == 'RGBA' else '') + f'）＝上下の 動きは 前の まま・前の 絵を のばした ものより 細かい（細かさ {dr:.2f}倍）')
        continue
    ps, dr, off = same_pic(load(pn), load(po), N)
    check(ps > 25 and dr > s['dmin'] and off < 0.3,
          f'絵（{s["jp"]}）：同じ 絵（2/3 に 小さく すると 前の 絵と 同じ：PSNR {ps:.1f}dB' + (f'・馬の 場所の ずれ {off:.2f}pt' if s['mode'] == 'RGBA' else '') + f'）・前の 絵を のばした ものより 細かい（細かさ {dr:.2f}倍）')
check(750000 < tot_new - tot_old < 1250000, f'走る コマ 5まい（競馬新聞・勝負服・夕焼け・水墨画〈15コマ〉・ネオン〈10コマ〉）で ＋{(tot_new - tot_old) / 1e3:.0f}KB（前の 2倍・10コマの 絵 {tot_old / 1e3:.0f}KB → {tot_new / 1e3:.0f}KB）')

# 花火の 絵
fB, fH, fO = (np.asarray(Image.open(P(i)).convert('RGB')) for i in (FWB['scatter'], FWB['scatter_h'], FW_OLD))
w15, h15 = int(fw * SC), int(fhh * SC)
okf = (MD5(FWB['scatter']) and MD5(FWB['scatter_h']) and LOSSLESS(FWB['scatter']) and LOSSLESS(FWB['scatter_h']) and fO.shape == (fsh, fsw * NG, 3)
       and fB.shape == (fsy, fsw * NG, 3) and bool((fB == fO[:fsy]).all()) and fH.shape == (h15, w15 * NG, 3) and (w15, h15) == (3 * (fw // 2), 3 * (fhh // 2)))
fsz = os.path.getsize(P(FWB['scatter'])) + os.path.getsize(P(FWB['scatter_h'])); fso = os.path.getsize(P(FW_OLD))
check(okf and 60_000 < fsz - fso < 140_000,
      f'絵（花火）：花火 4つは 前の 絵と 1画素も ちがわない（馬の 段を 切り落とした だけ）・馬は {NG}組 × {w15}×{h15}px（{fw // 2}×{fhh // 2}pt の 3倍）・どちらも ロスなし・'
      f'2まいで {fsz / 1e3:.0f}KB（前 {fso / 1e3:.0f}KB＝＋{(fsz - fso) / 1e3:.0f}KB）・前の 絵も 手元に のこって いる')
if okf:
    gn = [fH[:, g * w15:(g + 1) * w15].astype(np.float32) / 255 for g in range(NG)]; go = [fO[fsy:fsy + fhh, g * fsw:g * fsw + fw].astype(np.float32) / 255 for g in range(NG)]
    sn, so = np.clip(sum(gn), 0, 1), np.clip(sum(go), 0, 1)
    ps, dr, _ = same_pic(sn, so, alpha=False)
    shn, sho = np.array([g.sum() for g in gn]), np.array([g.sum() for g in go]); shd = float(np.abs(shn / shn.sum() - sho / sho.sum()).max())
    lit = float(np.abs(sn.mean() - so.mean()) / so.mean())
    check(ps > 30 and dr > 1.3 and shd < 0.01 and lit < 0.03,
          f'絵（花火の 馬）：{NG}組を 足すと 前と 同じ 絵（2/3 に 小さく して PSNR {ps:.1f}dB・明るさの ちがい {lit * 100:.1f}%）・前の 絵を のばした ものより 細かい（{dr:.2f}倍）・'
          f'組ごとの 光の 割合は 前と 同じ（ずれ {shd * 100:.2f}%＝散り方は かわらない）')

# ナイターの 絵（第4.167版）
VP8L = lambda p: open(p, 'rb').read()[12:16] == b'VP8L'
nt_new = nt_165 = 0; rows_ = []
for n, c in NT_CELL.items():
    (cw, ch), (ax, ay), (tw, th), (tx, ty) = NTC[n]
    # 走る 15コマ（1.5倍・ロスなし）：同じ 位相の 5コマ（新しい 0・3・6・9・12 ＝ 前の 0・2・4・6・8）を 第4.156版までの 絵（2倍・10コマ）と くらべる
    pn, po = P(NTB['h' + n]), P(NT_OLD['h' + n]); im = Image.open(pn)
    okf = (MD5(NTB['h' + n]) and im.format == 'WEBP' and im.mode == 'RGBA' and VP8L(pn) and im.size == (int(cw * SC) * NTN, int(ch * SC)) == (3 * (cw // 2) * NTN, 3 * (ch // 2))
           and os.path.exists(po) and Image.open(po).size == (c[0][0] * N, c[0][1]) and os.path.exists(P(NT_165['h' + n])))
    ps, dr, off = same_pic(*common(load(pn), load(po), [ax, ay, cw, ch], [c[1][0], c[1][1], c[0][0], c[0][1]]), 5) if okf else (0, 0, 9)
    rows_.append(('h' + n, okf, ps, dr, off, im.size, os.path.getsize(pn)))
    # 止まる／走りだす 72コマ（1倍・ロスあり）：さいしょの コマ（ゴールの しゅんかん）は 走る コマの 0番・さいごの コマ（走りだして 29/30秒）は 走る コマの 14番と 同じ 形
    pt = P(NTB['t' + n]); it = Image.open(pt)
    okt = (MD5(NTB['t' + n]) and it.format == 'WEBP' and it.mode == 'RGBA' and not VP8L(pt) and it.size == (tw * NT_COLS, th * NT_ROWS) and os.path.exists(P(NT_165['t' + n])))
    T_ = load(pt); H_ = load(pn); fr = NTR['trans'][n]['frames']
    X0, Y0, X1, Y1 = max(ax, tx), max(ay, ty), min(ax + cw, tx + tw), min(ay + ch, ty + th)
    def tcell(i):
        r_, c_ = divmod(i, NT_COLS)
        return T_[r_ * th + Y0 - ty:r_ * th + Y1 - ty, c_ * tw + X0 - tx:c_ * tw + X1 - tx]
    def hcell(f):
        hw = int(cw * SC)
        return resize(H_[int((Y0 - ay) * SC):int((Y1 - ay) * SC), f * hw + int((X0 - ax) * SC):f * hw + int((X1 - ax) * SC)], (X1 - X0, Y1 - Y0), Image.LANCZOS)
    i_dec0 = [i for i, f in enumerate(fr) if f['kind'] == 'dec' and f['k'] == 0][0]; i_acc = [i for i, f in enumerate(fr) if f['kind'] == 'acc'][-1]
    j0, j1 = psnr(tcell(i_dec0), hcell(0)) if okt else 0, psnr(tcell(i_acc), hcell(NTN - 1)) if okt else 0
    rows_.append(('t' + n, okt, j0, j1, 0, it.size, os.path.getsize(pt)))
    # 立つ 絵（1.5倍・ロスなし）：第4.166版までの 止まる／立つ／走りだす シート（6×3）の 立つ コマ（12番目）と 同じ 絵
    ps_, p165 = P(NTB['s' + n]), P(NT_165['t' + n]); is_ = Image.open(ps_)
    oks = MD5(NTB['s' + n]) and is_.format == 'WEBP' and is_.mode == 'RGBA' and VP8L(ps_) and is_.size == (int(tw * SC), int(th * SC)) == (3 * (tw // 2), 3 * (th // 2))
    if oks and os.path.exists(p165):
        O_ = load(p165); ow, oh = int(c[2][0] * SC), int(c[2][1] * SC); S_ = load(ps_)
        ox, oy = 5 * ow, 1 * oh                                                    # 12番目（0から 数えて 11）＝2段目の 6つめ
        SX0, SY0, SX1, SY1 = max(tx, c[3][0]), max(ty, c[3][1]), min(tx + tw, c[3][0] + c[2][0]), min(ty + th, c[3][1] + c[2][1])
        ps = psnr(S_[int((SY0 - ty) * SC):int((SY1 - ty) * SC), int((SX0 - tx) * SC):int((SX1 - tx) * SC)],
                  O_[oy + int((SY0 - c[3][1]) * SC):oy + int((SY1 - c[3][1]) * SC), ox + int((SX0 - c[3][0]) * SC):ox + int((SX1 - c[3][0]) * SC)])
    else:
        ps = 0
    rows_.append(('s' + n, oks, ps, 0, 0, is_.size, os.path.getsize(ps_)))
    # 表彰の 絵（第4.157版の まま）
    pa, pao = P(NTB['a' + n]), P(NT_OLD['a' + n]); ia = Image.open(pa)
    oka = MD5(NTB['a' + n]) and ia.mode == 'RGB' and ia.size == (1170, 480) and os.path.exists(pao)
    psa, dra, _o = same_pic(load(pa), load(pao), 1, 1) if oka else (0, 0, 9)
    rows_.append(('a' + n, oka, psa, dra, 0, ia.size, os.path.getsize(pa)))
    nt_new += sum(os.path.getsize(P(NTB[k + n])) for k in 'htsa'); nt_165 += sum(os.path.getsize(P(i)) for i in (NT_165['h' + n], NT_165['t' + n], NT_AW['a' + n]))
rr = [r for r in rows_ if r[0][0] == 'h']
check(all(r[1] and r[2] > 28 and r[3] > 1.25 and r[4] < 0.3 for r in rr),
      '絵（ナイターの 走る コマ 3まい・15コマ）：名前は 中身の md5・ロスなし・pt の 3倍（' + '・'.join(f'{r[0]} {r[5][0]}×{r[5][1]}px {r[6] / 1e3:.0f}KB' for r in rr)
      + '）・同じ 位相の 5コマは 前の 絵と 同じ（PSNR ' + '・'.join(f'{r[2]:.1f}' for r in rr) + 'dB・馬の 場所の ずれ ' + '・'.join(f'{r[4]:.2f}' for r in rr) + 'pt）＝上下の 動きは 前の まま・前より 細かい（'
      + '・'.join(f'{r[3]:.2f}' for r in rr) + '倍）')
rr = [r for r in rows_ if r[0][0] == 't']
check(all(r[1] and r[2] > 27 and r[3] > 27 for r in rr),
      '絵（ナイターの 止まる／走りだす コマ 3まい・72コマ）：pt の 2倍・ロスあり（' + '・'.join(f'{r[0]} {r[5][0]}×{r[5][1]}px {r[6] / 1e3:.0f}KB' for r in rr)
      + '）・つなぎ目：ゴールの しゅんかんの コマは 走る コマの 0番と 同じ 形（PSNR ' + '・'.join(f'{r[2]:.1f}' for r in rr) + 'dB）・走りだしの さいごの コマは 走る コマの 14番と 同じ 形（'
      + '・'.join(f'{r[3]:.1f}' for r in rr) + 'dB）')
rr = [r for r in rows_ if r[0][0] == 's']
check(all(r[1] and r[2] > 40 for r in rr),
      '絵（ナイターの 立つ 絵 3まい）：pt の 3倍・ロスなし（' + '・'.join(f'{r[0]} {r[5][0]}×{r[5][1]}px {r[6] / 1e3:.0f}KB' for r in rr) + '）・前の シートの 立つ コマと 同じ 絵（PSNR '
      + '・'.join(f'{r[2]:.1f}' for r in rr) + 'dB）＝止まって いる 間は 前と 同じ 細かさ')
rr = [r for r in rows_ if r[0][0] == 'a']
check(all(r[1] and r[2] > 30 and r[3] > 1.1 for r in rr), '絵（ナイターの 表彰の 絵 3まい）：第4.157版の まま（1170×480px・PSNR ' + '・'.join(f'{r[2]:.1f}' for r in rr) + 'dB）')
check(0 < nt_new - nt_165 < 2_500_000, f'ナイターの 馬の 絵（走る・止まる／走りだす・立つ・表彰）で ＋{(nt_new - nt_165) / 1e3:.0f}KB（第4.166版 {nt_165 / 1e3:.0f}KB → {nt_new / 1e3:.0f}KB：コマは 1頭 28 → 88コマ）')

from playwright.sync_api import sync_playwright
SRV = os.path.join(W, 'srv_wallhq'); PORT = 8800; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
for f in os.listdir(BL):
    shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
check(not os.path.exists(os.path.join(SRV, 'APP', 'ks_neon.json')) and all(os.path.exists(os.path.join(SRV, 'APP', f'ks_{nm}.json')) for nm in IN_APP) and os.path.exists(os.path.join(BL, ID['neon'] + '.webp')),
      '第4.160版：ネオンの ファイル（ks_neon.json）は アプリに 入って いない（ほかの 4つは ある）・ネオンの 絵は 手元に のこって いる')
for nm, jp, new, old in ([(nm, SET[nm]['jp'], [ID[nm]], [SET[nm]['old']]) for nm in IN_APP] + [('fireworks', '花火', [FWB['scatter'], FWB['scatter_h']], [FW_OLD]), ('night', 'ナイター', [NTB[k] for k in NTB if k not in NT_KEEP], list(NT_OLD.values()) + list(NT_165.values()))]):
    kj = json.load(open(os.path.join(SRV, 'APP', f'ks_{nm}.json'), encoding='utf8')); txt = kj['bnr']['html'] + kj['bnr']['css']
    check(all(f'ks_{i}.webp' in txt for i in new) and not any(o in json.dumps(kj) for o in old), f'{jp}の ファイル（ks_{nm}.json）：新しい 絵（{len(new)}まい）・前の 絵は 入って いない')
# 第4.168版（まさちゃん 2026/11/14 01:26「勝負服の馬の動く黒い線おかしいから消して！」）：勝負服の 壁紙の 走る 絵は 馬の 腹帯（鞍を とめる 黒い 帯：コマごとに 少し 動いて 見えた）を 描かない。
#   道具：flat/comic_rider.py は look の girth が False なら 腹帯を 描かない・勝負服（flat/silks_banner.py・flat/hq_silks.py）だけ girth=False を わたす（ほかの 壁紙は 今までどおり）
#   絵：前の 絵（第4.166〜4.167版：a1fc4438…）と くらべて、形（すき通し）は 1点も ちがわない・大きく かわった 点は どの コマも おなかの 細い たての 帯の 中 だけ（前は 暗い → いまは 馬の 体の 色）
_cr = open(os.path.join(K, 'flat', 'comic_rider.py'), encoding='utf8').read(); _sbn = open(os.path.join(K, 'flat', 'silks_banner.py'), encoding='utf8').read(); _hqs = open(os.path.join(K, 'flat', 'hq_silks.py'), encoding='utf8').read()
G167 = 'a1fc44386dd7e4989af9150869ab10a6'
check("if look.get('girth', True):" in _cr and 'girth=False' in _sbn and 'girth=False' in _hqs and ID['silks'] != G167 and G167 not in json.dumps(json.load(open(os.path.join(K, 'silks_blobs.json'), encoding='utf8'))),
      '第4.168版：勝負服の 走る 絵は 腹帯を 描かない（comic_rider.py の girth・勝負服 だけ girth=False）・台帳は 新しい 絵を さす（前の 絵 a1fc4438… は さして いない）')
if os.path.exists(P(G167)):
    _ga = np.asarray(Image.open(P(G167)).convert('RGBA')).astype(int); _gb = np.asarray(Image.open(P(ID['silks'])).convert('RGBA')).astype(int)
    _ok = _ga.shape == _gb.shape == (441, 13860, 4) and bool((_ga[..., 3] == _gb[..., 3]).all())
    if _ok:
        _d = np.abs(_ga[..., :3] - _gb[..., :3]).max(2); _big = (_d > 40) & (_ga[..., 3] > 0); _fw = _ga.shape[1] // 15; _per = []; _in = 0
        for _i in range(15):
            _ys, _xs = np.where(_big[:, _i * _fw:(_i + 1) * _fw]); _per.append(len(_xs)); _in += int(((_xs >= 470) & (_xs <= 520) & (_ys >= 190) & (_ys <= 320)).sum())
        _vo = float(_ga[..., :3].max(2)[_big].mean()); _vn = float(_gb[..., :3].max(2)[_big].mean())
        check(all(700 <= v <= 1400 for v in _per) and _in >= 0.97 * sum(_per) and _vo < 90 and _vn > 160,
              f'勝負服の 走る 絵（15コマ）：形（すき通し）は 前と 1点も ちがわない・大きく かわった 点は どの コマも おなかの 細い 帯の 中 だけ（1コマ {min(_per)}〜{max(_per)}点・その {_in / max(1, sum(_per)) * 100:.1f}% が 帯の 中）・'
              f'そこは 前は 暗い（明るさ {_vo:.0f}）→ いまは 馬の 体の 色（{_vn:.0f}）＝黒い 線は ない')
    else:
        check(False, f'勝負服の 走る 絵：前の 絵と 大きさ・形（すき通し）が ちがう（{_ga.shape}・{_gb.shape}）')
else:
    print('  （前の 絵 a1fc4438… が 手元に ない ので、前の 絵との くらべは しない）')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
ST = """async ([el, win]) => { const bn = document.querySelector('#ksBnr'), e = bn && bn.querySelector(el), w = bn && bn.querySelector(win); if (!e || !w) return null;
  const b = bn.getBoundingClientRect(), r = w.getBoundingClientRect(), c = getComputedStyle(e), u = (c.backgroundImage.match(/url\\("?([^")]+)"?\\)/) || [])[1];
  const nat = u ? await new Promise(res => { const im = new Image(); im.onload = () => res([im.naturalWidth, im.naturalHeight]); im.onerror = () => res(null); im.src = u; }) : null;
  const an = e.getAnimations();
  return { bn: [b.width, b.height], win: [r.left - b.left, r.top - b.top, r.width, r.height].map(v => +v.toFixed(2)), w: parseFloat(c.width), h: parseFloat(c.height), bs: c.backgroundSize, url: u ? u.split('/').pop() : null, nat: nat,
    an: an.map(a => [a.animationName, a.playState, a.effect.getTiming().duration]), tf: c.animationTimingFunction, k: bn.style.getPropertyValue('--ksk'), sw: document.documentElement.scrollWidth }; }"""
# いくつかの 部品の 絵（名前・もとの 大きさ・出す 大きさ pt）と 場所
PIC = """async (sels) => { const bn = document.querySelector('#ksBnr'), b = bn.getBoundingClientRect(), out = { bn: [b.width, b.height], sw: document.documentElement.scrollWidth };
  for (const [k, sel] of sels) { const e = bn.querySelector(sel); if (!e) { out[k] = null; continue; }
    const c = getComputedStyle(e), u = (c.backgroundImage.match(/url\\("?([^")]+)"?\\)/) || [])[1], r = e.getBoundingClientRect();
    const nat = u ? await new Promise(res => { const im = new Image(); im.onload = () => res([im.naturalWidth, im.naturalHeight]); im.onerror = () => res(null); im.src = u; }) : null;
    out[k] = { url: u ? u.split('/').pop() : null, nat: nat, w: parseFloat(c.width), h: parseFloat(c.height), bs: c.backgroundSize, bp: c.backgroundPosition, box: [r.left - b.left, r.top - b.top, r.width, r.height].map(v => +v.toFixed(2)), vis: c.visibility }; }
  return out; }"""
SEEK = "(T) => { for (const a of document.querySelector('#ksBnr').getAnimations({ subtree: true })) { a.pause(); a.currentTime = T * 1000; } }"
BOX = """(sel) => { const bn = document.querySelector('#ksBnr').getBoundingClientRect();
  const r = !sel ? bn : Array.isArray(sel) ? { left: bn.left + sel[0], top: bn.top + sel[1], right: bn.left + sel[0] + sel[2], bottom: bn.top + sel[1] + sel[3] } : document.querySelector('#ksBnr ' + sel).getBoundingClientRect();
  const x0 = Math.max(bn.left, r.left), y0 = Math.max(bn.top, r.top), x1 = Math.min(bn.right, r.right), y1 = Math.min(bn.bottom, r.bottom); return [x0, y0, x1 - x0, y1 - y0]; }"""


def open_app(ctx, tid):
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/ks_' in r.url else None)
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=10000)
    use(pg, tid)
    return pg, errs, bad


def use(pg, tid):
    pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
    pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); pg.wait_for_timeout(1200)
    pg.evaluate("window.scrollTo(0, 0)")


def shot(pg, win, t):
    """壁紙の 中の 1つの 所 だけ（動きを t 秒で 止めて）。win＝部品の 名前／[左, 上, 幅, 高さ]（壁紙の 中の pt）／None なら 壁紙 ぜんぶ。壁紙の 外に 出た 所は 写さない"""
    pg.evaluate(SEEK, t); pg.wait_for_timeout(250)
    r = pg.evaluate(BOX, win)
    return np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=dict(x=r[0], y=r[1], width=r[2], height=r[3])))).convert('RGB')).astype(np.float32) / 255


def versus(pg, win, t, css):
    """いまの 絵 と、同じ 所に 前の 絵（2倍）を さしかえた とき（css）を 同じ 時刻で 写す → (同じ 絵か PSNR, 細かさの 比, 写した 大きさ)"""
    a0 = shot(pg, win, t)
    tag = pg.add_style_tag(content=css); pg.wait_for_timeout(500)
    o0 = shot(pg, win, t)
    tag.evaluate("e => e.remove()"); pg.wait_for_timeout(300)
    return psnr(a0, o0), detail(a0) / max(detail(o0), 1e-9), a0


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg, errs, bad = open_app(ctx, 'news')
        for nm in IN_APP:
            s = SET[nm]
            if nm != 'news':
                use(pg, nm)
            x0, y0, cw, ch = (v // 2 for v in CELL[nm]); n = NF[nm]
            q = pg.evaluate(ST, [s['el'], s['win']])
            dur = next((a[2] for a in (q or {}).get('an', []) if a[0].endswith(s['anim'])), 0) / 1000
            okq = (bool(q) and q['bn'] == [390, 160] and q['win'] == [x0, y0, cw, ch] and [q['w'], q['h']] == [n * cw, ch] and q['bs'] == f'{n * cw}px {ch}px' and q['url'] == f'ks_{ID[nm]}.webp'
                   and q['nat'] == [3 * n * cw, 3 * ch] and q['nat'][0] / q['w'] == 3.0 and any(a[0].endswith(s['anim']) and a[1] == 'running' for a in q['an']) and q['tf'].replace(' ', '') in (f'steps({n})', f'steps({n},end)') and q['sw'] <= 390
                   and abs(dur - n / 30) < 1e-6)
            if not okq: print('    ', json.dumps(q, ensure_ascii=False)[:900])
            check(okq, f'アプリ（{s["jp"]}・iPhone の 3倍の 画面）：窓 {[x0, y0, cw, ch]}pt・シート {q and q["nat"]}px＝**絵の 3px を 1pt に**・走る 動き（{n}コマ・1回り {dur:g}秒＝1コマ 1/30秒）・横に はみ出さない' + ('' if okq else f'（{q}）'))
            # くっきり：いまの 絵 と、同じ 所に 前の 絵（2倍・10コマ）を さしかえた とき を くらべる。1コマめ（どちらも 同じ 形）で 止めて、2つの 切りぬきが 重なる 所 だけ 写す
            ox0, oy0, ocw, och = (v // 2 for v in s['cell'])
            X0, Y0, X1, Y1 = max(x0, ox0), max(y0, oy0), min(x0 + cw, ox0 + ocw), min(y0 + ch, oy0 + och); box = [X0, Y0, X1 - X0, Y1 - Y0]
            a1 = shot(pg, box, 0.45 * dur)
            same, dr, a0 = versus(pg, box, 0.0, f'#ksBnr {s["el"]}{{background-image:url(ks_{s["old"]}.webp) !important;background-size:{N * ocw}px {och}px !important;background-position:{ox0 - x0}px {oy0 - y0}px !important}}'); mv = float(np.abs(a0 - a1).mean())
            check(a0.shape == (3 * box[3], 3 * box[2], 3) and same > 22 and dr > s['smin'] and mv > 0.004,
                  f'アプリ（{s["jp"]}）：1コマめで 前の 絵（2倍）に さしかえた ときと 同じ 絵（PSNR {same:.1f}dB）で、画面の 上でも くっきり（細かさ {dr:.2f}倍）・コマが 進む')

        # 花火：馬の 段は 馬 だけの 絵（3倍）・花火 4つは 前と 同じ 絵（2倍）
        use(pg, 'fireworks')
        q = pg.evaluate(PIC, [['k', '.hqw .hq4'], ['h', '.hqw .hq4 .hqc i'], ['b', '.hqw .hq0 .hqc i']] + [[f'g{g}', f'.hqw .hq4 .hqc:nth-child({g + 1}) i'] for g in range(NG)])
        okq = (bool(q) and q['bn'] == [390, 160] and q['k'] and q['k']['box'] == [fx // 2, fy // 2, fw // 2, fhh // 2] and q['h']['url'] == f'ks_{FWB["scatter_h"]}.webp'
               and q['h']['nat'] == [3 * NG * (fw // 2), 3 * (fhh // 2)] and q['h']['bs'] == f'{NG * fw // 2}px {fhh // 2}px' and q['h']['nat'][0] / (NG * fw // 2) == 3.0
               and q['b']['url'] == f'ks_{FWB["scatter"]}.webp' and q['b']['nat'] == [NG * fsw, fsy] and q['b']['bs'] == f'{NG * fsw // 2}px {fsy // 2}px'
               and all(q[f'g{g}'] and q[f'g{g}']['bp'] == f'{-g * (fw // 2)}px 0px' and q[f'g{g}']['url'] == q['h']['url'] for g in range(NG)) and q['sw'] <= 390)
        if not okq: print('    ', json.dumps(q, ensure_ascii=False)[:1500])
        check(okq, f'アプリ（花火・iPhone の 3倍の 画面）：馬は {[fx // 2, fy // 2, fw // 2, fhh // 2]}pt の まま・馬の {NG}組は 馬 だけの 絵 {q and q["h"] and q["h"]["nat"]}px＝**絵の 3px を 1pt に**・花火 4つは 前と 同じ 絵（{NG * fsw}×{fsy}px）')
        an = pg.evaluate("() => document.querySelector('#ksBnr').getAnimations({ subtree: true }).filter(a => a.playState === 'running').length")
        same, dr, a0 = versus(pg, '.hqw .hq4', 0.0, f'#ksBnr .hqw .hq4 .hqc i{{background-image:url(ks_{FW_OLD}.webp) !important;background-size:{NG * fsw // 2}px {fsh // 2}px !important;background-position-y:-{fsy // 2}px !important}}')
        check(a0.shape == (3 * (fhh // 2), 3 * (fw // 2), 3) and same > 26 and dr > 1.1 and an > 40 and float(a0.mean()) > 0.05,
              f'アプリ（花火）：咲ききった ところで、前の 絵（2倍）に さしかえた ときと 同じ 絵（PSNR {same:.1f}dB）・画面の 上でも 馬が くっきり（細かさ {dr:.2f}倍）・動いて いる（{an}こ）')

        # ナイター：走る コマ・止まる／走りだす コマ・表彰の 絵
        use(pg, 'night')
        sels = [[k + n, sel + n] for n in NT_CELL for k, sel in (('s', '.nts'), ('q', '.ntq'), ('o', '.nto'), ('z', '.ntz'), ('c', '.ntc'), ('k', '.ntk'))]
        q = pg.evaluate(PIC, sels)
        okq = bool(q) and q['bn'] == [390, 160] and q['sw'] <= 390
        for n in NT_CELL:
            cw, ch, tw, th = NTC[n][0][0] // 2, NTC[n][0][1] // 2, NTC[n][2][0] // 2, NTC[n][2][1] // 2
            okq = (okq and all(q[k + n] for k in 'sqozck') and q['s' + n]['url'] == f'ks_{NTB["h" + n]}.webp' and q['s' + n]['nat'] == [3 * NTN * cw, 3 * ch] and q['s' + n]['bs'] == f'{NTN * cw}px {ch}px'
                   and q['s' + n]['nat'][0] / q['s' + n]['w'] == 3.0 and q['q' + n]['url'] == f'ks_{NTB["t" + n]}.webp' and q['q' + n]['nat'] == [2 * NT_COLS * tw, 2 * NT_ROWS * th]
                   and q['q' + n]['bs'] == f'{NT_COLS * tw}px {NT_ROWS * th}px' and [q['q' + n]['w'], q['q' + n]['h']] == [tw, th]
                   and q['o' + n]['url'] == f'ks_{NTB["s" + n]}.webp' and q['o' + n]['nat'] == [3 * tw, 3 * th] and q['o' + n]['bs'] == f'{tw}px {th}px'
                   and q['z' + n]['url'] == f'ks_{NTB["a" + n]}.webp' and q['z' + n]['nat'] == [1170, 480] and q['z' + n]['bs'] == '390px 160px'
                   and q['c' + n]['box'][2:] == [cw, ch] and q['k' + n]['box'][2:] == [tw, th] and q['o' + n]['box'][2:] == [tw, th])
        if not okq: print('    ', json.dumps(q, ensure_ascii=False)[:2500])
        check(okq, 'アプリ（ナイター・iPhone の 3倍の 画面）：3頭の 走る シート ' + '・'.join(f'{q["s" + n]["nat"][0]}×{q["s" + n]["nat"][1]}' for n in NT_CELL if q.get('s' + n) and q['s' + n]['nat'])
              + 'px と 立つ 絵・表彰の 絵 1170×480px＝**絵の 3px を 1pt に**・止まる／走りだす シートは 絵の 2px を 1pt に（動いて いる 間 だけ）・窓の 大きさは pt')
        OPEN_U, T_GOAL, T_AWARD, T_START, BLOCK = night_wall.OPEN_U, night_wall.T_GOAL, night_wall.T_AWARD, night_wall.T_START, night_wall.BLOCK
        # 時刻ごとに どの 重ねが 見えるか：走って いる（走る シート）→ ゴールの あと（止まる コマ）→ 立つ 絵 → つぎの レースの 走りだし（走りだす コマ）→ 走る シート
        VIS = "(n) => ['.ntc', '.ntk', '.nto'].map(s => getComputedStyle(document.querySelector('#ksBnr ' + s + n)).visibility === 'visible' ? 1 : 0).join('')"
        seq = []
        for jp, t, want in (('走って いる', 1.01, '100'), ('ゴールの すぐ あと', T_GOAL - OPEN_U + 0.51, '010'), ('止まる とちゅう', T_GOAL - OPEN_U + 1.81, '010'), ('止まった あと', T_GOAL - OPEN_U + 2.51, '001'),
                            ('つぎの レースの 走りだす 前', BLOCK - OPEN_U + T_START - 0.2, '001'), ('走りだし', BLOCK - OPEN_U + T_START + 0.51, '010'), ('走りだして 1秒', BLOCK - OPEN_U + T_START + 1.01, '100')):
            pg.evaluate(SEEK, t); pg.wait_for_timeout(120)
            v = [pg.evaluate(VIS, n) for n in NT_CELL]
            a0 = shot(pg, '.nth7', t)
            seq.append((jp, v, want, float(a0.std())))
        if not all(all(x == want for x in v) and sd > 0.02 for jp, v, want, sd in seq): print('    ', seq)
        check(all(all(x == want for x in v) and sd > 0.02 for jp, v, want, sd in seq),
              'アプリ（ナイター）：重ねの 入れかわり（走る シート／止まる・走りだす コマ／立つ 絵 の どれか 1つ だけ 見える）：' + ' → '.join(f'{jp}＝{"走る" if want == "100" else "止まる・走りだす コマ" if want == "010" else "立つ 絵"}' for jp, v, want, sd in seq))
        old_css = ''.join(f'#ksBnr .ntz{n}{{background-image:url(ks_{NT_OLD["a" + n]}.webp) !important}}' for n in NT_CELL)
        same, dr, a0 = versus(pg, [113, 20, 143, 126], T_AWARD - OPEN_U + 3.0, old_css)
        v = pg.evaluate("() => { const a = document.querySelector('#ksBnr .ntaw'); return +getComputedStyle(a).opacity > 0.9 && [...document.querySelectorAll('#ksBnr .nta')].filter(e => getComputedStyle(e).visibility === 'visible').length === 1 ? 'visible' : 'hidden'; }")
        gal = pg.evaluate("() => document.querySelector('#ksBnr').getAnimations({ subtree: true }).length")
        check(same > 24 and dr > 1.15 and v == 'visible' and float(a0.mean()) > 0.03 and gal > 30,
              f'アプリ（ナイター）：表彰の 馬と 騎手は 前の 絵（2倍）に さしかえた ときと 同じ 絵で くっきり（PSNR {same:.1f}dB・細かさ {dr:.2f}倍）')
        check(not errs and not bad, f'エラー なし・読めない 絵 なし {errs[:2]} {bad[:3]}')
        ctx.close()
        # iPad の「iPhone の 大きさ」（390×844・2倍の 画面）：同じ 場所に 出る（絵は 3倍の まま 小さく 出す）
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg2, errs2, bad2 = open_app(ctx2, 'silks')
        s = SET['silks']; x0, y0, cw, ch = (v // 2 for v in CELL['silks'])
        q = pg2.evaluate(ST, [s['el'], s['win']])
        check(bool(q) and q['bn'] == [390, 160] and q['win'] == [x0, y0, cw, ch] and q['nat'] == [3 * NF['silks'] * cw, 3 * ch] and (q['k'] or '1') in ('1', '1.0000') and not errs2 and not bad2,
              f'iPad の「iPhone の 大きさ」（390×844・2倍の 画面）：壁紙は 引きのばさない（--ksk {q and q["k"]}）・走る コマは 同じ 場所 {q and q["win"]}')
        use(pg2, 'night'); q = pg2.evaluate(PIC, [['s7', '.nts7'], ['z7', '.ntz7']])
        use(pg2, 'fireworks'); q2 = pg2.evaluate(PIC, [['k', '.hqw .hq4'], ['h', '.hqw .hq4 .hqc i']])
        c7w, c7h = NTC['7'][0][0] // 2, NTC['7'][0][1] // 2
        check(bool(q) and q['bn'] == [390, 160] and q['s7']['nat'] == [3 * NTN * c7w, 3 * c7h] and q['s7']['bs'] == f'{NTN * c7w}px {c7h}px' and q['z7']['nat'] == [1170, 480]
              and bool(q2) and q2['k']['box'] == [fx // 2, fy // 2, fw // 2, fhh // 2] and q2['h']['nat'] == [3 * NG * (fw // 2), 3 * (fhh // 2)] and not errs2 and not bad2,
              'iPad の「iPhone の 大きさ」：ナイターと 花火も 同じ 場所・同じ 大きさ（絵は 3倍の まま 小さく 出す）')
        ctx2.close(); b.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
