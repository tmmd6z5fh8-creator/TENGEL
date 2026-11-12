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
SET = {'news': dict(jp='競馬新聞', key='run', pre='', sub=None, old='90c9d3f81a75c530c5dcaf297f8bfafb', cell=[208, 76, 360, 200], mode='RGB', el='.nsw .nsr', win='.nsw .nsh', anim='nsRun', kb=(70, 140), dmin=1.3, smin=1.12),
       'silks': dict(jp='勝負服', key='run', pre='', sub=None, old='a6f4674ee0a8a396c3f9df8527b92f77', cell=[70, 24, 612, 292], mode='RGBA', el='.sbw .sbr', win='.sbw .sbh', anim='sbRun', kb=(280, 480), dmin=1.3, smin=1.12),
       'sunset': dict(jp='夕焼け', key='horse', pre='/_blob/', sub='horse', old='3f932ad749f07e3a3d47e32e8004914e', cell=[204, 26, 430, 228], mode='RGBA', el='.ssw .sxr', win='.ssw .sxh', anim='sxRun', kb=(130, 250), dmin=1.3, smin=1.12),
       'ink': dict(jp='水墨画', key='run', pre='', sub=None, old='2a2aa8796320a888283cdacb060f4be1', cell=[112, 32, 596, 266], mode='RGB', el='.ikw .ikr', win='.ikw .ikh', anim='ikRun', kb=(220, 400), dmin=1.3, smin=1.12),
       'neon': dict(jp='ネオン', key='run', pre='', sub=None, old='0417b8e6f0ca61b59a999f45f38744bd', cell=[170, 0, 284, 320], mode='RGBA', el='.nqw .nqr', win='.nqw .nqh', anim='nqRun', kb=(220, 400), dmin=1.04, smin=1.02)}
# 第4.160版（まさちゃん 2026/11/12 14:31「壁紙のネオン消して！」）：ネオンは アプリから 外した。絵と 作る 道具・台帳は 手元／リポジトリに のこす ので、台帳・ページ・絵の 確かめは そのまま。
#   アプリの 中身と 画面の 確かめ（IN_APP）からは 外して、「アプリに 入って いない」ことを 見る
IN_APP = [nm for nm in SET if nm != 'neon']
N = 10; SC = 1.5
sys.path.insert(0, K)
import news_wall, silks_wall, sunset_wall, ink_wall, neon_wall, fireworks_wall, night_wall
MOD = dict(news=news_wall, silks=silks_wall, sunset=sunset_wall, ink=ink_wall, neon=neon_wall)
ID = {}; RUN = {}
for nm, s in SET.items():
    blobs = json.load(open(os.path.join(K, nm + '_blobs.json'), encoding='utf8')); run = json.load(open(os.path.join(K, nm + '_run.json'), encoding='utf8'))
    info = run[s['sub']] if s['sub'] else run
    v = blobs[s['key']]; ID[nm] = v[len(s['pre']):]; RUN[nm] = run
    check(v.startswith(s['pre']) and HEX(ID[nm]) and ID[nm] != s['old'] and info['cell'] == s['cell'] and info['frames'] == N and info.get('scale') == SC
          and s['old'] not in json.dumps(blobs),
          f'台帳（{s["jp"]}）：走る コマは 新しい 絵・切りぬく 場所 {s["cell"]} と コマの 数 {N} は 前と 同じ・絵の 細かさ {info.get("scale")}倍（＝画面の 3倍）')
    x0, y0, cw, ch = (v // 2 for v in s['cell'])
    html, css = MOD[nm].inline(MOD[nm].load_blobs(os.path.join(K, nm + '_blobs.json')), run)
    check(f'{s["el"]}{{width:{N * cw}px;height:{ch}px;background:url(/_blob/{ID[nm]}) 0 0/{N * cw}px {ch}px no-repeat;' in css and f'steps({N})' in css and f'translateX(-{N * cw}px)' in css
          and f'left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden' in css and s['old'] not in css + html,
          f'ページ（{s["jp"]}）：窓は 左 {x0}・上 {y0}・{cw}×{ch}pt・シートは {N * cw}×{ch}pt（pt の まま＝場所と 動きは 前と 同じ）・絵は 新しい id')

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
check(sorted(NTB) == sorted(list(NT_OLD) + list(NT_KEEP)) and all(HEX(v) for v in NTB.values()) and all(NTB[k] != o and o not in json.dumps(NTB) for k, o in NT_OLD.items())
      and all(NTB[k] == o for k, o in NT_KEEP.items()) and NTR.get('scale') == SC and NTR['size'] == [780, 320]
      and all(NTR['horses'][n]['cell'] == c[0] and NTR['horses'][n]['at'] == c[1] and NTR['horses'][n]['frames'] == N and NTR['trans'][n]['cell'] == c[2] and NTR['trans'][n]['at'] == c[3]
              and [NTR['trans'][n]['cols'], NTR['trans'][n]['rows'], len(NTR['trans'][n]['frames'])] == [6, 3, 18] for n, c in NT_CELL.items()),
      f'台帳（ナイター）：3頭の 走る コマ・止まる／走りだす コマ・表彰の 絵（9まい）は 新しい 絵・コースの 絵 3まいは そのまま・切りぬく 場所と コマの 数は 前と 同じ・絵の 細かさ {NTR.get("scale")}倍')
nhtml, ncss = night_wall.inline(night_wall.load_blobs(os.path.join(K, 'night_blobs.json')), NTR)
okp = all(o not in ncss + nhtml for o in NT_OLD.values())
for n, c in NT_CELL.items():
    cw, ch, tw, th = c[0][0] / 2, c[0][1] / 2, c[2][0] / 2, c[2][1] / 2
    okp = (okp and f'.nts{n},.ntv{n}{{width:{N * cw:g}px;height:{ch:g}px;background:url(/_blob/{NTB["h" + n]}) 0 0/{N * cw:g}px {ch:g}px no-repeat;' in ncss
           and f'.ntq{n}{{width:{6 * tw:g}px;height:{3 * th:g}px;background:url(/_blob/{NTB["t" + n]}) 0 0/{6 * tw:g}px {3 * th:g}px no-repeat;' in ncss
           and f'.ntz{n}{{background:url(/_blob/{NTB["a" + n]}) 0 0/390px 160px no-repeat}}' in ncss
           and f'.ntc{n},.ntu{n}{{position:absolute;left:{c[1][0] / 2:g}px;top:{c[1][1] / 2:g}px;width:{cw:g}px;height:{ch:g}px;overflow:hidden}}' in ncss)
check(okp, 'ページ（ナイター）：3頭の 窓・走る シート・止まる／走りだす シート・表彰の 絵の 大きさは pt の まま（場所と 動きは 前と 同じ）・絵は 新しい id')

gi = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
tools = ['hq_news.py', 'hq_silks.py', 'hq_sunset.py', 'hq_ink.py', 'hq_neon.py', 'hq_fireworks.py', 'hq_night.py', 'hq_install.py']
check(not any(f.startswith('ios/kisekae_blobs/') for f in gi) and all(os.path.exists(os.path.join(K, 'flat', f)) and ('kisekae/flat/' + f) in gi for f in tools)
      and all('/home/claude' not in open(os.path.join(K, 'flat', f), encoding='utf8').read() for f in tools),
      '壁紙の 絵は リポジトリに 入って いない・作る 道具（flat/hq_news.py・hq_silks.py・hq_sunset.py・hq_ink.py・hq_neon.py・hq_fireworks.py・hq_night.py）と 入れる 道具（flat/hq_install.py）が ある')
ALL_NEW = list(ID.values()) + [FWB['scatter'], FWB['scatter_h']] + [NTB[k] for k in NT_OLD]
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


tot_new = tot_old = 0
for nm, s in SET.items():
    x0, y0, cw, ch = s['cell']; pn, po = P(ID[nm]), P(s['old'])
    im = Image.open(pn); szn = os.path.getsize(pn)
    okf = MD5(ID[nm]) and im.format == 'WEBP' and im.mode == s['mode'] and im.size == (int(cw * SC) * N, int(ch * SC)) == (3 * (cw // 2) * N, 3 * (ch // 2))
    oko = os.path.exists(po) and Image.open(po).size == (cw * N, ch)          # 前の 絵（キャンバスの id の まま：名前は md5 では ない）
    tot_new += szn; tot_old += os.path.getsize(po) if oko else 0
    check(okf and oko and s['kb'][0] * 1000 < szn < s['kb'][1] * 1000,
          f'絵（{s["jp"]}）：名前は 中身の md5・1コマ {int(cw * SC)}×{int(ch * SC)}px（{cw // 2}×{ch // 2}pt の 3倍）・{szn / 1e3:.0f}KB（前 {os.path.getsize(po) / 1e3 if oko else 0:.0f}KB）・前の 絵（2倍）も 手元に のこって いる')
    if not (okf and oko):
        continue
    ps, dr, off = same_pic(load(pn), load(po), N)
    check(ps > 25 and dr > s['dmin'] and off < 0.3,
          f'絵（{s["jp"]}）：同じ 絵（2/3 に 小さく すると 前の 絵と 同じ：PSNR {ps:.1f}dB' + (f'・馬の 場所の ずれ {off:.2f}pt' if s['mode'] == 'RGBA' else '') + f'）・前の 絵を のばした ものより 細かい（細かさ {dr:.2f}倍）')
check(350_000 < tot_new - tot_old < 650_000, f'走る コマ 5まい（競馬新聞・勝負服・夕焼け・水墨画・ネオン）で ＋{(tot_new - tot_old) / 1e3:.0f}KB（{tot_old / 1e3:.0f}KB → {tot_new / 1e3:.0f}KB）')

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

# ナイターの 絵
nt_new = nt_old = 0; rows_ = []
for n, c in NT_CELL.items():
    for key, cols, rws, cell in (('h' + n, N, 1, c[0]), ('t' + n, 6, 3, c[2]), ('a' + n, 1, 1, [780, 320])):
        pn, po = P(NTB[key]), P(NT_OLD[key]); im = Image.open(pn); mode = 'RGB' if key[0] == 'a' else 'RGBA'
        okf = (MD5(NTB[key]) and im.format == 'WEBP' and im.mode == mode and im.size == (int(cell[0] * SC) * cols, int(cell[1] * SC) * rws) == (3 * (cell[0] // 2) * cols, 3 * (cell[1] // 2) * rws)
               and os.path.exists(po) and Image.open(po).size == (cell[0] * cols, cell[1] * rws))
        nt_new += os.path.getsize(pn); nt_old += os.path.getsize(po) if os.path.exists(po) else 0
        ps, dr, off = same_pic(load(pn), load(po), cols, rws) if okf else (0, 0, 9)
        rows_.append((key, okf, ps, dr, off, im.size, os.path.getsize(pn)))
for kind, jp, pmin, dmin in (('h', '走る コマ', 28, 1.25), ('t', '止まる／立つ／走りだす コマ', 28, 1.25), ('a', '表彰の 絵', 30, 1.1)):
    rr = [r for r in rows_ if r[0][0] == kind]
    check(all(r[1] and r[2] > pmin and r[3] > dmin and r[4] < 0.3 for r in rr),
          f'絵（ナイターの {jp} 3まい）：名前は 中身の md5・pt の 3倍（' + '・'.join(f'{r[0]} {r[5][0]}×{r[5][1]}px {r[6] / 1e3:.0f}KB' for r in rr) + '）・同じ 絵（PSNR '
          + '・'.join(f'{r[2]:.1f}' for r in rr) + 'dB' + ('' if kind == 'a' else '・馬の 場所の ずれ ' + '・'.join(f'{r[4]:.2f}' for r in rr) + 'pt') + '）・前より 細かい（'
          + '・'.join(f'{r[3]:.2f}' for r in rr) + '倍）・前の 絵も 手元に のこって いる')
check(-900_000 < nt_new - nt_old < 2_600_000, f'ナイターの 9まいで {"＋" if nt_new >= nt_old else "−"}{abs(nt_new - nt_old) / 1e3:.0f}KB（{nt_old / 1e3:.0f}KB → {nt_new / 1e3:.0f}KB）')

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
for nm, jp, new, old in ([(nm, SET[nm]['jp'], [ID[nm]], [SET[nm]['old']]) for nm in IN_APP] + [('fireworks', '花火', [FWB['scatter'], FWB['scatter_h']], [FW_OLD]), ('night', 'ナイター', [NTB[k] for k in NT_OLD], list(NT_OLD.values()))]):
    kj = json.load(open(os.path.join(SRV, 'APP', f'ks_{nm}.json'), encoding='utf8')); txt = kj['bnr']['html'] + kj['bnr']['css']
    check(all(f'ks_{i}.webp' in txt for i in new) and not any(o in json.dumps(kj) for o in old), f'{jp}の ファイル（ks_{nm}.json）：新しい 絵（{len(new)}まい）・前の 絵は 入って いない')
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
            x0, y0, cw, ch = (v // 2 for v in s['cell'])
            q = pg.evaluate(ST, [s['el'], s['win']])
            okq = (bool(q) and q['bn'] == [390, 160] and q['win'] == [x0, y0, cw, ch] and [q['w'], q['h']] == [N * cw, ch] and q['bs'] == f'{N * cw}px {ch}px' and q['url'] == f'ks_{ID[nm]}.webp'
                   and q['nat'] == [3 * N * cw, 3 * ch] and q['nat'][0] / q['w'] == 3.0 and any(a[0].endswith(s['anim']) and a[1] == 'running' for a in q['an']) and q['tf'].replace(' ', '') in (f'steps({N})', f'steps({N},end)') and q['sw'] <= 390)
            if not okq: print('    ', json.dumps(q, ensure_ascii=False)[:900])
            check(okq, f'アプリ（{s["jp"]}・iPhone の 3倍の 画面）：窓 {[x0, y0, cw, ch]}pt・シート {q and q["nat"]}px＝**絵の 3px を 1pt に**・走る 動き（{N}コマ）・横に はみ出さない' + ('' if okq else f'（{q}）'))
            # くっきり：いまの 絵 と、同じ 所に 前の 絵（2倍）を さしかえた とき を くらべる（動きは 同じ コマで 止める）
            dur = next((a[2] for a in (q or {}).get('an', []) if a[0].endswith(s['anim'])), 500) / 1000
            a1 = shot(pg, s['win'], 0.45 * dur)
            same, dr, a0 = versus(pg, s['win'], 0.05 * dur, f'#ksBnr {s["el"]}{{background-image:url(ks_{s["old"]}.webp) !important}}'); mv = float(np.abs(a0 - a1).mean())
            check(a0.shape == (3 * ch, 3 * cw, 3) and same > 22 and dr > s['smin'] and mv > 0.004,
                  f'アプリ（{s["jp"]}）：前の 絵（2倍）に さしかえた ときと 同じ 絵（PSNR {same:.1f}dB）で、画面の 上でも くっきり（細かさ {dr:.2f}倍）・コマが 進む')

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
        sels = [[k + n, sel + n] for n in NT_CELL for k, sel in (('s', '.nts'), ('v', '.ntv'), ('q', '.ntq'), ('z', '.ntz'), ('c', '.ntc'), ('k', '.ntk'))]
        q = pg.evaluate(PIC, sels)
        okq = bool(q) and q['bn'] == [390, 160] and q['sw'] <= 390
        for n, c in NT_CELL.items():
            cw, ch, tw, th = c[0][0] // 2, c[0][1] // 2, c[2][0] // 2, c[2][1] // 2
            okq = (okq and all(q[k + n] for k in 'svqzck') and q['s' + n]['url'] == q['v' + n]['url'] == f'ks_{NTB["h" + n]}.webp' and q['s' + n]['nat'] == [3 * N * cw, 3 * ch] and q['s' + n]['bs'] == f'{N * cw}px {ch}px'
                   and q['s' + n]['nat'][0] / q['s' + n]['w'] == 3.0 and q['q' + n]['url'] == f'ks_{NTB["t" + n]}.webp' and q['q' + n]['nat'] == [3 * 6 * tw, 3 * 3 * th] and q['q' + n]['bs'] == f'{6 * tw}px {3 * th}px'
                   and q['z' + n]['url'] == f'ks_{NTB["a" + n]}.webp' and q['z' + n]['nat'] == [1170, 480] and q['z' + n]['bs'] == '390px 160px'
                   and q['c' + n]['box'][2:] == [cw, ch] and q['k' + n]['box'][2:] == [tw, th])
        if not okq: print('    ', json.dumps(q, ensure_ascii=False)[:2500])
        check(okq, 'アプリ（ナイター・iPhone の 3倍の 画面）：3頭の 走る シート ' + '・'.join(f'{q["s" + n]["nat"][0]}×{q["s" + n]["nat"][1]}' for n in NT_CELL if q.get('s' + n) and q['s' + n]['nat'])
              + 'px・止まる／走りだす シート・表彰の 絵 1170×480px＝**絵の 3px を 1pt に**・窓の 大きさは 前と 同じ')
        old_css = ''.join(f'#ksBnr .nts{n},#ksBnr .ntv{n}{{background-image:url(ks_{NT_OLD["h" + n]}.webp) !important}}#ksBnr .ntq{n}{{background-image:url(ks_{NT_OLD["t" + n]}.webp) !important}}'
                          f'#ksBnr .ntz{n}{{background-image:url(ks_{NT_OLD["a" + n]}.webp) !important}}' for n in NT_CELL)
        OPEN_U, T_GOAL, T_AWARD = night_wall.OPEN_U, night_wall.T_GOAL, night_wall.T_AWARD
        res = []
        for jp, sel, t, vis in (('走って いる 7番', '.ntc7', 1.0, 'c7'), ('走って いる 3番', '.ntc3', 1.0, 'c3'), ('走って いる 5番', '.ntc5', 1.0, 'c5'),
                                ('ゴールの あと 止まる 7番', '.ntk7', T_GOAL - OPEN_U + 1.0, 'k7'), ('表彰の 馬と 騎手', [113, 20, 143, 126], T_AWARD - OPEN_U + 3.0, None)):
            same, dr, a0 = versus(pg, sel, t, old_css)
            v = pg.evaluate(PIC, [[vis, sel]])[vis]['vis'] if vis else pg.evaluate("() => { const a = document.querySelector('#ksBnr .ntaw'); return +getComputedStyle(a).opacity > 0.9 && [...document.querySelectorAll('#ksBnr .nta')].filter(e => getComputedStyle(e).visibility === 'visible').length === 1 ? 'visible' : 'hidden'; }")
            res.append((jp, same, dr, v, a0.shape, float(a0.mean())))
        gal = pg.evaluate("() => document.querySelector('#ksBnr').getAnimations({ subtree: true }).length")
        check(all(r[1] > 24 and r[2] > 1.15 and r[3] == 'visible' and r[5] > 0.03 for r in res) and gal > 30,
              'アプリ（ナイター）：前の 絵（2倍）に さしかえた ときと 同じ 絵で、画面の 上でも くっきり（' + '／'.join(f'{r[0]}：PSNR {r[1]:.1f}dB・細かさ {r[2]:.2f}倍' for r in res) + '）')
        check(not errs and not bad, f'エラー なし・読めない 絵 なし {errs[:2]} {bad[:3]}')
        ctx.close()
        # iPad の「iPhone の 大きさ」（390×844・2倍の 画面）：同じ 場所に 出る（絵は 3倍の まま 小さく 出す）
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg2, errs2, bad2 = open_app(ctx2, 'silks')
        s = SET['silks']; x0, y0, cw, ch = (v // 2 for v in s['cell'])
        q = pg2.evaluate(ST, [s['el'], s['win']])
        check(bool(q) and q['bn'] == [390, 160] and q['win'] == [x0, y0, cw, ch] and q['nat'] == [3 * N * cw, 3 * ch] and (q['k'] or '1') in ('1', '1.0000') and not errs2 and not bad2,
              f'iPad の「iPhone の 大きさ」（390×844・2倍の 画面）：壁紙は 引きのばさない（--ksk {q and q["k"]}）・走る コマは 同じ 場所 {q and q["win"]}')
        use(pg2, 'night'); q = pg2.evaluate(PIC, [['s7', '.nts7'], ['z7', '.ntz7']])
        use(pg2, 'fireworks'); q2 = pg2.evaluate(PIC, [['k', '.hqw .hq4'], ['h', '.hqw .hq4 .hqc i']])
        check(bool(q) and q['bn'] == [390, 160] and q['s7']['nat'] == [3 * N * 210, 324] and q['s7']['bs'] == '2100px 108px' and q['z7']['nat'] == [1170, 480]
              and bool(q2) and q2['k']['box'] == [fx // 2, fy // 2, fw // 2, fhh // 2] and q2['h']['nat'] == [3 * NG * (fw // 2), 3 * (fhh // 2)] and not errs2 and not bad2,
              'iPad の「iPhone の 大きさ」：ナイターと 花火も 同じ 場所・同じ 大きさ（絵は 3倍の まま 小さく 出す）')
        ctx2.close(); b.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
