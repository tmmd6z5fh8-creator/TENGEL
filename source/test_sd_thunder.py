# 極ど的中（紫電）の 顔の 場面を まさちゃんの 3D「Violet Thunder」に（第4.195版）
#   まさちゃん 2026/11/18 12:02「極ど的中の演出、このファイルの3Dと入れ替えて！かなり顔をアップにして作成して！顔は、ゆっくり上下小さく、左右大きく顔を揺らすように、
#   とまってる画像ではなく、生きてる馬のように演出して！」（顔の 場面の 長さは「今の2秒のまま」）・12:22「スタートは一枚目くらいの顔の角度からスタートして、
#   カメラが移動して顔を上げると二枚目くらいの顔の角度にして！カメラのより具合は任せる！」・12:30「首から下ないからそこが映らないようにね！」・
#   13:29「スタートの顔の角度もっと下向いてて！光るのは左目で、目が光り始めてから今の角度になる。目は徐々に光りが強くなり、顔が見える頃には両目が光るようにして！
#   あと目の光りは紫で、もっとリアルに！」
#   ・道具：kisekae/flat/shiden_thunder.py（顔の 場面 54〜113コマ だけ。長さ 2.0秒・目が 光る／鼻息／雷／目の 光に つつまれる 時刻は 前の まま ＝ 音 sfx_sd と そろう）
#   ・動き：左右に 大きく ゆっくり（±8°・1.6秒で 1往復・目が 光りはじめて から 大きく）・上下は 小さく（±1.8° ＋ 鼻息で 少し 上げる）・耳が ぴくっ・鼻の 穴が ふくらむ・たてがみが おくれて ゆれる
#   ・角度：はじめ＝右前の 上から 見おろす（顔は 26° 下向き：頭から 見た カメラの 高さ 約47°）→ 目が 光りだして から 顔を 上げ、カメラが おりる → おわり＝右前の ほぼ 横の 高さ・かなり アップ
#   ・目：画面の 左の 目（カメラに 近い 目）だけ 0.10秒から だんだん 光る → もう 一つも 0.36秒から ともって、顔が 見える ころ（0.8秒）には 両目。光は 紫：3D の 瞳の 形 そのものが 光って
#     形の まま にじむ（十字の 筋は なし）・まぶたや 眉を 紫に 照らす。さいごは 近い 目の 光に つつまれて 前と 同じ 白へ
#   ・首：胸像の 首の 切れ目（モデルの 高さ −0.81）は 写らない（−0.40〜−0.60 で 闇に とかす）
#   ・アプリ：極ど的中の 動画は sd_film5.mp4（顔の あとの キーフレーム 138コマ目から うしろは sd_film4.mp4 と 1画素も 同じ）・さいごの 1まいは sd_last4.webp の まま・音も 前の まま
#   ・もとの ファイル（前の 動画・さいごの 1まい・音）は 消して いない・1バイトも かわって いない。3D（GLB）・コマ・動画は リポジトリに 入れない
#   python3 test_sd_thunder.py   （3D・ios/fx_assets が ある とき だけ その 確かめ。ない とき〈CI〉は コードの 確かめ だけ）
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae'); FLAT = os.path.join(K, 'flat')
sys.path.insert(0, W); sys.path.insert(0, K)
import assets_dir
import build_fx as BF
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
rd = lambda *p: open(os.path.join(W, *p), encoding='utf8').read()
OLD = {'sd_film4.mp4': '7cdf6947d5a60ffbe0e0fd565f1ee170', 'sd_last4.webp': 'f5b8cf903e27e03fbb02bfd6eb5679d4',
       'sfx_sd.m4a': 'cbad0b2e7dda2b998a5fca6df3490fce', 'sfx_sdp.m4a': 'e9372bfd95814329b0e5b8dfc0d0f8fc'}      # 前の 動画（新しい 動画の もと）・さいごの 1まい・音
NEW = 'sd_film5.mp4'
A0, A1, KEY, NF = 54, 114, 138, 315        # 顔の 場面（54〜113）・顔の あとの 最初の キーフレーム・コマの 数


def py(code, env=None, timeout=1800):
    r = subprocess.run([sys.executable, '-c', 'import sys; sys.path[:0] = [%r, %r]\n' % (FLAT, K) + code], capture_output=True, text=True, cwd=FLAT,
                       env=dict(os.environ, **(env or {})), timeout=timeout)
    return r.returncode, (r.stdout.strip().split('\n') or [''])[-1], r.stderr.strip()[-300:]


print('■ 動画の 道具（kisekae/flat/shiden_thunder.py）')
st = rd('kisekae', 'flat', 'shiden_thunder.py'); bff = rd('kisekae', 'build_fx_films.py')
check('「極ど的中の演出、このファイルの3Dと入れ替えて！' in st and 'まさちゃん 12:30「首から下ないからそこが映らないようにね！」' in st
      and "GLB_PATH = os.environ.get('SD_THUNDER_GLB'," in st and 'def splice_keyed(old_mp4, work, out_mp4, W, H, a0, a1, n_all):' in st
      and "assert ok1 and np.array_equal(x, y), f'つないだ 動画の {n} コマ目が 前の 動画と ちがう'" in st and 'a0, a1 = int(round(BLACK * FPS)), int(round(FACE * FPS))' in st
      and "if film == 'sd_film5.mp4':" in bff and "T = os.path.join(FLAT, 'shiden_thunder.py')" in bff,
      '道具：顔の 場面（54〜113コマ）だけ 新しい 馬で 描いて、前の 動画（sd_film4.mp4）に つなぐ（顔の あとの キーフレームから うしろは 圧縮し直さず、1画素も 同じ ことを 確かめる）・'
      '3D の 場所は SD_THUNDER_GLB・作る 道具（build_fx_films.py の sd_film）も この 流れ')
rc, out, err = py('import math, numpy as np, shiden_thunder as T\n'
                  'ts = np.linspace(0, T.FACE_LEN, 241)\n'
                  'yaw = np.array([T.head_pose(t)[0] for t in ts]); pit = np.array([T.head_pose(t)[1] - T.base_pitch(t) for t in ts])\n'
                  'zc = int((np.sign(yaw[1:]) * np.sign(yaw[:-1]) < 0).sum())\n'
                  'print(repr(dict(a=(int(round(T.BLACK * T.FPS)), int(round(T.FACE * T.FPS))), yaw=(round(float(yaw.min()), 2), round(float(yaw.max()), 2)), pit=(round(float(pit.min()), 2), round(float(pit.max()), 2)), zc=zc,\n'
                  '    bp=(T.base_pitch(0.0), T.base_pitch(T.FACE_LEN)), cam0=[round(float(v), 2) for v in T.cam_params(0.0)], cam1=[round(float(v), 2) for v in T.cam_params(T.UP[1])],\n'
                  '    camE=round(float(T.cam_params(T.FACE_LEN)[2]), 2), neck=T.NECK, ear=round(max(T.ear_angle(t, "l") for t in ts), 1),\n'
                  '    fl=[round(max(T.flare(t) for t in ts if abs(t - p) < 0.3), 2) for p in T.PUFFS], lag=0.16, glb=T.GLB_PATH,\n'
                  '    first=T.FIRST_EYE, ge=[(round(float(t), 2), round(T.face_state(t)["ge"]["eye_r"], 3), round(T.face_state(t)["ge"]["eye_l"], 3)) for t in np.arange(0, 2.0001, 1 / 30)],\n'
                  '    col=[[round(float(c), 2) for c in T.EYE_COL], [round(float(c), 2) for c in T.EYE_HOT], [round(float(c), 3) for c in T.EYE_LIGHT]], up=T.HEAD_UP)))',
                  env=dict(SD_THUNDER_GLB='/nonexistent/thunder.glb'))
try:
    v = eval(out)
except Exception:
    v = {}
yr = v.get('yaw', (0, 0)); pr = v.get('pit', (0, 9))
check(rc == 0 and v.get('a') == (A0, A1) and yr[0] <= -7.5 and yr[1] >= 7.5 and pr[1] - pr[0] <= 7.0 and (yr[1] - yr[0]) >= 2.2 * (pr[1] - pr[0]) and v.get('zc', 9) <= 3,
      f'動き：顔の 場面は {v.get("a")}コマ（前と 同じ）・左右に 大きく（{yr[0]}°〜{yr[1]}°）ゆっくり（2秒で 向きが かわるのは {v.get("zc")}回）・'
      f'上下は 小さく（{pr[0]}°〜{pr[1]}°：鼻息で 少し 上げる ぶんを 入れて）・3D が なくても 読める（{(err or "")[-80:]}）')
c0, c1 = v.get('cam0', [0, 0, 0]), v.get('cam1', [0, 0, 0])
check(v.get('bp', (0, 9))[0] <= -20 and v.get('bp', (0, 9))[1] == 0.0 and c0[:2] == [-16.0, 24.0] and c1[:2] == [-22.0, 6.0] and c0[2] > c1[2] > v.get('camE', 9) and 2.0 < v.get('camE', 0) < 2.8,
      f'角度：はじめは 頭を {v.get("bp", (0, 0))[0]}° 下げて、カメラは 右前（{c0[0]}°）の 上（{c0[1]}°）から 見おろす → 顔を 上げて（{v.get("bp", (0, 0))[1]}°）カメラは 右前（{c1[0]}°）の ほぼ 横（{c1[1]}°）へ おりる・'
      f'寄る（顔からの きょり {c0[2]} → {v.get("camE")}）')
check(v.get('ear', 0) >= 14 and all(f > 0.95 for f in v.get('fl', [0])) and len(v.get('fl', [])) == 2 and 'y_now, y_lag = head_pose(t)[0], head_pose(t - 0.16)[0]' in st
      and 'rot_part(ii, rot_w((0, 1, 0), (lag + math.radians(2.2) * wave) * w), PIVOT)' in st,
      f'生きて いる 動き：左耳が ぴくっと うしろへ（{v.get("ear")}°）・鼻息 2回の 前に 鼻の 穴が ふくらむ（{v.get("fl")}）・たてがみは 頭の 左右に 0.16秒 おくれて ついて くる ＋ 風で ゆらぐ')
ge_ = v.get('ge', []); gn = {round(t, 2): (a, b) for t, a, b in ge_}
jump = max((abs(ge_[i + 1][1] - ge_[i][1]) for i in range(len(ge_) - 1) if ge_[i][0] < 1.0), default=9)
avg = [sum(x[1] for x in ge_[i:i + 6]) / 6 for i in range(0, 31)]                 # 0.2秒の 平均（ゆらぎを ならす）：だんだん 強く
rise = all(avg[i + 1] >= avg[i] - 1e-6 for i in range(len(avg) - 1))
first_on = min((t for t, a, b in ge_ if a > 0.02), default=9); other_on = min((t for t, a, b in ge_ if b > 0.02), default=9)
both = gn.get(0.8, (0, 0))
check(v.get('first') == 'eye_r' and 0.08 <= first_on <= 0.2 and other_on - first_on >= 0.2 and rise and jump < 0.1 and both[1] > 0.6 and abs(both[0] - both[1]) < 0.06 and gn.get(0.3, (0, 9))[1] < 0.02,
      f'目：画面の 左の 目（カメラに 近い 目）が {first_on}秒から だんだん 光る（0.2秒の 平均は 1秒まで ずっと ふえる・1コマの ちがいは 小さな ゆらぎ {jump:.3f} まで）→ もう 一つは {other_on}秒から → 0.8秒（顔が 見える ころ）には 両目（{both}）')
cl = v.get('col', [[0, 0, 0]] * 3)
check(all(c[2] > c[0] > c[1] for c in cl) and 'stx = ' not in st and '十字の 筋は なし' in st and 'B[\'eyem\'] = eye_masks(B, B[\'alb\'])' in st
      and "wcol = np.array([0.80, 0.55, 1.0]) * (1 - fl) + np.array([1.0, .95, .88]) * fl" in st,
      f'目の 光は 紫（光 {cl[0]}・まん中 {cl[1]}・まわりを 照らす 光 {cl[2]}：青 ＞ 赤 ＞ 緑）・3D の 瞳の 形 そのものが 光って にじむ（十字の 筋は なし）・さいごは 紫 → 前と 同じ 白へ（つぎの 場面と つながる）')
gl = v.get('glb', '')
check(v.get('neck') == (-0.4, -0.6) and 'def neck_fade(B):' in st and 'BUF[f] = neck_fade(B)' in st and gl == '/nonexistent/thunder.glb'
      and '/home/claude/work/v195/glb/thunder.glb' in st and not os.path.abspath('/home/claude/work/v195/glb/thunder.glb').startswith(W + os.sep),
      '首：モデルの 高さ −0.40 から −0.60 で 首と たてがみを 闇に とかす（胸像の 切れ目 −0.81 は 写らない）・3D の 場所は リポジトリの 外（SD_THUNDER_GLB で かえられる）')

GLB = os.environ.get('SD_THUNDER_GLB', '/home/claude/work/v195/glb/thunder.glb')
if os.path.isfile(GLB):
    print('■ 手元の 3D で（小さく 描いて はかる）')
    rc, out, err = py('import math, numpy as np, shiden_thunder as T\n'
                      'D = T.horse(); ymin = float(D["p"].pos[:, 1].min()); W_, H_ = 234, 506; fr = {}\n'
                      'for f in (58, 66, 84, 98, 108):\n'
                      '    B = T.buffers(f, W_, H_); Mi = np.linalg.inv(B["Mm"])\n'
                      '    e = Mi[:3, :3] @ B["cam"].eye + Mi[:3, 3]; d = T.nrm(e - T.FACE_C)\n'
                      '    y = (B["P"] @ Mi[:3, :3].T + Mi[:3, 3])[..., 1]; A0 = B["A"] > 0.02\n'
                      '    B2 = T.neck_fade(dict(A=B["A"], col=B["col"], mane=B["mane"], P=B["P"], Mm=B["Mm"])); vis = B2["A"] > 0.02\n'
                      '    M = B["M"]; el = [[round(M[k][0] / W_, 3), round(M[k][1] / H_, 3)] for k in ("eye_l", "eye_r")]; em = T.eye_masks(B, B["alb"])\n'
                      '    fr[f] = dict(el=round(math.degrees(math.asin(d[1])), 1), az=round(math.degrees(math.atan2(d[0], d[2])), 1), eyes=el, ed=round(abs(el[0][0] - el[1][0]), 3),\n'
                      '                 low=round(float(y[vis].min()), 3) if vis.any() else 9.0, neck=int((A0 & (y < T.NECK[1])).sum()), cover=round(float(vis.mean()), 3),\n'
                      '                 ve=[int((em[k][0] > .5).sum()) for k in ("eye_r", "eye_l")])\n'
                      'print(repr(dict(ymin=round(ymin, 3), fr=fr)))', env=dict(SD_THUNDER_SS='1', SD_THUNDER_BANDS='1', SD_THUNDER_GLB=GLB))
    try:
        g = eval(out)
    except Exception:
        g = {'ymin': 0, 'fr': {}}
    fr = g.get('fr', {})
    a, b = fr.get(58, {}), fr.get(98, {})
    check(rc == 0 and a.get('el', 0) >= 40 and b.get('el', 99) <= 12 and a.get('el', 0) - b.get('el', 99) >= 30 and all(-40 < fr[f]['az'] < -8 for f in (58, 66, 84, 98) if f in fr) and len(fr) == 5,
          f'角度（頭から 見た カメラの 高さ・方角）：はじめ（58コマ）は 上から {a.get("el")}°・右前 {a.get("az")}° → 顔を 上げた あと（98コマ）は {b.get("el")}°・右前 {b.get("az")}°'
          f'（高さ {" ".join(str(fr[f]["el"]) for f in sorted(fr))}°・方角 {" ".join(str(fr[f]["az"]) for f in sorted(fr))}°：108コマは 目へ 寄る ところ）（{(err or "")[-80:]}）')
    inside = [f for f in (58, 66, 84, 98) if f in fr and all(0.03 < x < 0.97 and 0.03 < y < 0.97 for x, y in fr[f]['eyes'])]
    check(len(inside) == 4 and all(fr[f]['ed'] >= 0.3 and fr[f]['cover'] >= 0.45 for f in inside),
          f'かなり アップ：目 2つが 画面の 中（目と 目の あいだは 画面の はばの {"・".join(str(fr[f]["ed"]) for f in inside)}）・馬が 画面の {"・".join(str(fr[f]["cover"]) for f in inside)} を うめる')
    check(g.get('ymin', 0) < -0.75 and all(fr[f]['low'] >= -0.6 for f in fr) and sum(fr[f]['neck'] for f in fr) > 0,
          f'首：胸像の 切れ目（モデルの 高さ {g.get("ymin")}）は 画面に 写らない（見える 所の いちばん 下は {min((fr[f]["low"] for f in fr), default=0)}：−0.60 より 下は すき通す）・'
          f'消さ なければ 写る 首の 点 {[fr[f]["neck"] for f in sorted(fr)]}')
    ve = {f: fr[f].get('ve', [0, 0]) for f in fr}
    check(ve.get(58, [0, 9])[0] > 0 and ve.get(58, [0, 9])[1] == 0 and ve.get(84, [0, 0])[0] > 0 and ve.get(84, [0, 0])[1] > 0 and ve.get(98, [0, 0])[1] > 0,
          f'光る 目の 形（3D の 紫の 瞳：画面の 左の 目・右の 目の 点の 数）：はじめ（58コマ）は 左の 目 だけ 見える {ve.get(58)} → 顔を 上げると 両目 {ve.get(84)}・{ve.get(98)}'
          f'（{" ".join(f"{f}:{ve[f]}" for f in sorted(ve))}）')
else:
    print('  ※ まさちゃんの 3D（SD_THUNDER_GLB）が ない ので、3D の 確かめは しない（CI）')

print('■ アプリ（極ど的中の 動画の 名前）')
check(BF.FILMS['sd_film'] == NEW and BF.STILL['sd_last'] == 'sd_last4.webp' and BF.ART['sd'] == ['sd_last4.webp'] and BF.SFX['sd'] == 'sfx_sd.m4a' and BF.SFX['sdp'] == 'sfx_sdp.m4a'
      and NEW in BF.ASSET_FILES and 'sd_film4.mp4' not in BF.ASSET_FILES and len(BF.ASSET_FILES) == 23,
      f'アプリに 入れる：極ど的中の 動画は {NEW}（顔の 場面だけ 新しい 馬）・さいごの 1まいと 音は 前の まま（sd_last4.webp・sfx_sd.m4a・sfx_sdp.m4a）・ファイルの 数は 前と 同じ（{len(BF.ASSET_FILES)}こ）')
B = BF.bundle()
fx = rd('fx.js')
check(B['films']['sd_film'] == NEW and 'sd_last4.webp' in B['reveal']['sd'] and B['t']['SD'] == 9.9 and B['t']['SDS'] == {'FROM': 9.8, 'WAIT': 1.0} and B['t']['SDUP']['AT'] == 5.34
      and "video('sd_film')" in fx and not re.search(r'sd_(film|last)\d*\.(mp4|webp)', fx),
      '演出の 束（window.__FX）：極ど的中の 動画は 新しい 名前・ボードが 出る 時刻・さいごの 1まいに かわる 時刻は 前と 同じ（fx.js は 名前の 表で 引く ＝ かえて いない）')
S = assets_dir.superseded
allf = {'sd_film.mp4', 'sd_last.webp', 'sd_film2.mp4', 'sd_last2.webp', 'sd_film3.mp4', 'sd_last3.webp', 'sd_film4.mp4', 'sd_last4.webp', 'sfx_sd.m4a'}
olds = allf - {'sd_film4.mp4', 'sd_last4.webp', 'sfx_sd.m4a'}
check(S('fx_assets', allf | {NEW}) == olds | {'sd_film4.mp4'} and S('fx_assets', allf) == olds and S('fx_assets', (allf | {NEW}) - {'sd_last4.webp'}) == olds - {'sd_film3.mp4', 'sd_last3.webp'}
      and len(assets_dir.FX_NEW) == 11,      # 第4.216版：神様極的中の 第16稿（gk_film4.mp4・sfx_gk3.m4a）で 1つ ふえた
      f'アプリに 入れない もの（assets_dir.superseded）：{NEW} と sd_last4.webp が そろって いる とき、前の 動画（…4 まで）と 前の さいごの 1まい（…3 まで）を 入れない（もとの フォルダには 残す）')
import lite_assets as LA
# 第4.216版：神様極的中の 第16稿（gk_film4.mp4）も さいごの 1まいは 前の まま（gk_last3.webp）
check(LA.TAIL_LAST == {NEW: 'sd_last4.webp', 'gk_film4.mp4': 'gk_last3.webp'} and LA.has_tail(os.path.join(assets_dir.master('fx_assets'), NEW)) == os.path.isfile(os.path.join(assets_dir.master('fx_assets'), 'sd_last4.webp')),
      '軽い 版の 決めごと：新しい 動画も さいごの 1まい（sd_last4.webp）に つながる 動画 ＝ さいごの 30コマを 少しずつ きれいに（tail）')

fxd = assets_dir.master('fx_assets')
if os.path.isfile(os.path.join(fxd, NEW)) and all(os.path.isfile(os.path.join(fxd, f)) for f in OLD):
    import cv2
    import numpy as np
    print('■ もとの ファイル（ios/fx_assets）')
    check(all(md5(os.path.join(fxd, f)) == h for f, h in OLD.items()),
          '前の 動画（sd_film4.mp4）・さいごの 1まい（sd_last4.webp）・音（sfx_sd.m4a・sfx_sdp.m4a）は もとの フォルダに ある・1バイトも かわって いない（上書きして いない）')

    def probe(p):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_frames', '-of', 'json', p], capture_output=True, text=True, check=True)
        s_ = json.loads(r.stdout)['streams']; vv = [x for x in s_ if x['codec_type'] == 'video'][0]; b = open(p, 'rb').read(1 << 16)
        return (len(s_), vv['codec_name'], vv['profile'], vv['width'], vv['height'], vv['pix_fmt'], vv['r_frame_rate'], int(vv['nb_frames']), 0 <= b.find(b'moov') < (b.find(b'mdat') if b.find(b'mdat') >= 0 else 1 << 30))

    def fmd5(p):
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-an', '-f', 'framemd5', '-'], capture_output=True, text=True, check=True)
        return [ln.split(',')[-1].strip() for ln in r.stdout.split('\n') if ln and not ln.startswith('#')]

    def small(p, w=65, h=140):
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'scale={w}:{h}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
        return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w, 3).astype(np.float32) / 255

    def frame(p, i):
        c = cv2.VideoCapture(p); c.set(cv2.CAP_PROP_POS_FRAMES, i); ok, x = c.read(); c.release()
        return x if ok else None

    def psnr(a, b):
        return float(10 * np.log10(255.0 ** 2 / max(1e-9, float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)))))
    pn, po = os.path.join(fxd, NEW), os.path.join(fxd, 'sd_film4.mp4')
    a = probe(pn)
    check(a == (1, 'h264', 'High', 1170, 2532, 'yuv420p', '30/1', NF, True) and probe(po)[3:8] == (1170, 2532, 'yuv420p', '30/1', NF),
          f'新しい 動画（もと）：H.264 High・1170×2532・30コマ/秒・{NF}コマ（前と 同じ）・音なし・先読みできる 形（{os.path.getsize(pn) / 1e6:.1f}MB・前は {os.path.getsize(po) / 1e6:.1f}MB）')
    hn, ho = fmd5(pn), fmd5(po)
    same_tail = len(hn) == len(ho) == NF and hn[KEY:] == ho[KEY:]
    sa, sb = small(pn), small(po)
    dd = np.abs(sa - sb).mean((1, 2, 3)) if len(sa) == len(sb) == NF else np.ones(NF)
    face = dd[A0:A1]; pre, post = dd[:A0], dd[A1:KEY]
    check(same_tail and float(pre.max()) < 0.01 and float(post.max()) < 0.01 and float(np.median(face[6:])) > 0.03,
          f'つなぎ：{KEY}コマ目（顔の あとの キーフレーム）から うしろの {NF - KEY}コマは 前の 動画と 1画素も 同じ・はじめの 黒（{A0}コマ）と 蹄の はじめ（{A1}〜{KEY - 1}）は 前と 同じ 絵'
          f'（ちがい {pre.max():.4f}・{post.max():.4f}）・顔の 場面（{A0}〜{A1 - 1}）は 新しい 絵（ちがいの まん中の 値 {np.median(face[6:]):.3f}）')
    lum = lambda x: (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]).mean((1, 2))
    ln_, lo_ = lum(sa), lum(sb)
    check(float(ln_[A0:A0 + 3].max()) < 0.03 and float(ln_[A0 + 15:A0 + 42].min()) > 0.08 and float(ln_[A1 - 3:A1].min()) > 0.75 and abs(float(ln_[A1 - 1]) - float(lo_[A1 - 1])) < 0.08,
          f'明るさの 流れ：はじめは 闇（{ln_[A0:A0 + 3].max():.3f}）→ 顔が 見える（{ln_[A0 + 15:A0 + 42].min():.3f} 以上）→ さいごは 目の 光に つつまれて 白（{ln_[A1 - 3:A1].min():.3f}：前の 動画 {lo_[A1 - 1]:.3f}）→ 蹄の 場面へ（前と 同じ）')
    def eye_px(x8):
        """あざやかな 紫の 明るい 点（目の 光の 色：色相 250〜300°）の 数と 場所（画面の はばの 割合）・だいだい色に 光る 点（前の 目の 火の 色）の 数"""
        hsv = cv2.cvtColor(x8, cv2.COLOR_BGR2HSV); h = hsv[..., 0].astype(int) * 2; s_ = hsv[..., 1] / 255; v_ = hsv[..., 2] / 255
        pur = (s_ > 0.45) & (v_ > 0.55) & (h >= 250) & (h <= 300); ora = (s_ > 0.5) & (v_ > 0.6) & (h >= 15) & (h <= 50)
        xs = np.nonzero(pur)[1]
        return int(pur.sum()), (float(xs.mean() / x8.shape[1]) if len(xs) else 1.0), int(ora.sum())
    capn = cv2.VideoCapture(pn); ep = {}
    for i in range(A1):
        ok, x8 = capn.read()
        if ok and i >= A0:
            ep[i] = eye_px(x8)
    capn.release()
    early = [ep.get(i, (0, 1, 0)) for i in (60, 62, 64)]
    check(len(ep) == A1 - A0 and all(n > 500 and cx < 0.4 for n, cx, _o in early) and all(o == 0 for _n, _c, o in ep.values()) and ep[A0][0] == 0,
          f'目の 光：はじめは 闇（{A0}コマ：紫の 点 {ep.get(A0, (0,))[0]}）→ 画面の 左の 目 だけ 紫に 光る（60・62・64コマ：紫の 点 {[e[0] for e in early]}・場所 {[round(e[1], 2) for e in early]}〈画面の はばの 割合〉）・'
          f'顔の 場面に だいだい色に 光る 点は ない（前の 目の 火の 色：{sum(e[2] for e in ep.values())}）')
    ship = os.path.join(assets_dir.adir('fx_assets'), NEW); ship = ship if os.path.isfile(ship) else pn; td = tempfile.mkdtemp(prefix='sdt_')
    try:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', ship, '-vf', 'scale=390:844,fps=60', '-start_number', '0', os.path.join(td, 'f%04d.png')], check=True)
        r = subprocess.run(['python3', os.path.join(K, 'flash_px.py'), td, '0'], capture_output=True, text=True, env=dict(os.environ, AREA='.1')); fo = r.stdout.strip().split('\n')
    finally:
        shutil.rmtree(td, ignore_errors=True)
    check(r.returncode == 0 and '窓 0個' in fo[0], f'点めつ（アプリに 入る 動画を じかに 数えた：1秒に 4回 以上 光る 点が 画面の 10% を こえる 1秒が ない）：{fo[0]}／{fo[-1]}')
    stl = cv2.imread(os.path.join(fxd, 'sd_last4.webp')); lf = frame(pn, NF - 1)
    check(stl is not None and lf is not None and psnr(stl, lf) > 30, f'さいごの コマは さいごの 1まい（sd_last4.webp）と 同じ 絵（近さ {psnr(stl, lf) if stl is not None and lf is not None else 0:.1f}dB）')
    print('■ 軽い 版（アプリに 入る もの）')
    if assets_dir.is_lite('fx_assets'):
        man = assets_dir.manifest('fx_assets'); lt = assets_dir.lite('fx_assets'); fl = man['files']; lp = os.path.join(lt, NEW)
        ok = (assets_dir.stale('fx_assets') == '' and NEW in fl and os.path.isfile(lp) and 'sd_film4.mp4' not in fl and not os.path.exists(os.path.join(lt, 'sd_film4.mp4'))
              and fl[NEW]['how'] == 'film' and fl[NEW]['p'] == 'crf24-slow-tail30:23/20:22/10:21' and probe(lp) == (1, 'h264', 'High', 1170, 2532, 'yuv420p', '30/1', NF, True)
              and os.path.getsize(lp) < os.path.getsize(pn) * 0.85 and md5(os.path.join(lt, 'sd_last4.webp')) == OLD['sd_last4.webp'])
        lq = [psnr(frame(lp, k), frame(pn, k)) for k in (60, 75, 90, 105, 200, NF - 1)] if ok else [0]
        check(ok and min(lq) > 33, f'軽い 版：{NEW} だけ（sd_film4.mp4 は ない）・CRF 24（さいごの 30コマは 少しずつ きれいに）・形は もとと 同じ（{os.path.getsize(lp) / 1e6 if os.path.isfile(lp) else 0:.2f}MB・'
                               f'もとは {os.path.getsize(pn) / 1e6:.2f}MB）・もとと 同じ 絵（顔・蹄・さいごの コマの 近さ {" ".join("%.1f" % q for q in lq)} dB）')
    else:
        print('  ※ 軽い 版（ios/lite/fx_assets）が ない ので、その 確かめは しない')
else:
    print('  ※ ios/fx_assets に 新しい 動画が ない ので、ファイルの 確かめは しない（CI）')

print('■ リポジトリに 入れない もの')
gi = rd('.gitignore')
tracked = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
bad = [f for f in tracked if f.lower().endswith(('.glb', '.npz')) or re.search(r'sd_(film|last)\d*\.(mp4|webp)$', f) or '/fx_assets/' in f or '/lite/' in f]
ig = lambda p: subprocess.run(['git', 'check-ignore', '-q', p], cwd=os.path.dirname(W)).returncode == 0
check('ios/fx_assets/' in gi and not bad and ig('source/ios/fx_assets/' + NEW) and ig('source/ios/lite/fx_assets/' + NEW) and not ig('source/kisekae/flat/shiden_thunder.py'),
      f'まさちゃんの 3D（GLB）・G バッファ・動画は リポジトリに 入って いない・道具（shiden_thunder.py）は 入る{bad[:3] if bad else ""}')
print()
print('結果：', 'ぜんぶ OK' if not fails else f'{len(fails)} こ ❌')
for f in fails:
    print('  ❌', f)
sys.exit(1 if fails else 0)
