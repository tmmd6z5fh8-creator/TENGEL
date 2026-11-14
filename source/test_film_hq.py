# 的中の 演出の 動画を 3倍（1170×2532）に（第4.171版・まさちゃん 2026/11/14 16:18「①的中演出の画質上げる！」）
#   ・極ど的中（紫電）・ノーマルど的中：同じ 絵を 3倍の 大きさで 1コマずつ 描き直した（sd_film4.mp4・nd_film4.mp4）
#     神様極的中：もとの 絵を 描く 道具が そろわない ので、できた 動画を 3倍に のばした（gk_film2.mp4：Lanczos ＋ りんかくを 少し はっきり）／超神様は はじめから 3倍（sgd_film2.mp4）
#   ・コマの 数・時刻は 前と 同じ（音・ボードの 時刻は かえて いない）・絵は 前と 同じ 絵（小さく して くらべる）・前より くっきり（細かい 所の 量）
#   ・明るさの 流れ（点めつ）は 前の 動画と 同じ（前の 動画で 確かめた ものと 同じ 光り方）
#     極ど的中は 雷の 形が 描く たびに かわる（3倍で 描くと 雷の 線が 前と ちがう 所を 通る：出る 時刻は 同じ）→「同じ 絵」は 雷に 強い 見方（画素ごとの ちがいの まん中の 値・
#     大きく ちがう 画素の 割合）で 見る・点めつは 新しい 動画を じかに 数える（kisekae/flash_px.py：1秒に 4回 以上 光る 点が 画面の 10% を こえる 1秒が ない）
#   ・さいごの 1まいも 3倍・動画の さいごの コマと 同じ 絵
#   ・もとの ファイル（前の 動画・さいごの 1まい）は 消して いない・1バイトも かわって いない
#   ・軽い 版（アプリに 入る もの）：新しい もの だけ・CRF 24（さいごの 30コマは 少しずつ きれいに）・形は もとと 同じ
#   python3 test_film_hq.py   （ios/fx_assets/ が ある とき だけ ファイルの 確かめ。ない とき（CI）は コードの 確かめ だけ）
import hashlib, json, os, shutil, subprocess, sys, tempfile
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae'); sys.path.insert(0, W); sys.path.insert(0, K)
import assets_dir
import build_fx as BF
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
rd = lambda *p: open(os.path.join(W, *p), encoding='utf8').read()
# (名前, 新しい 動画, 新しい さいごの 1まい, 前の 動画, 前の さいごの 1まい, コマの 数, 描き直した か)
FILMS = (('sd', 'sd_film4.mp4', 'sd_last4.webp', 'sd_film3.mp4', 'sd_last3.webp', 315, True),
         ('nd', 'nd_film4.mp4', 'nd_last4.webp', 'nd_film3.mp4', 'nd_last3.webp', 315, True),
         ('gk', 'gk_film2.mp4', 'gk_last2.webp', 'gk_film.mp4', 'gk_last.webp', 361, False))
JP = dict(sd='極ど的中', nd='ノーマルど的中', gk='神様極的中')
# 前の ファイルの md5（もとの フォルダに のこす：消さない・上書きしない）
OLD = {'sd_film3.mp4': 'b3a39134056574606fb399a5d195183b', 'sd_last3.webp': 'f98df32869e9a84f3a85fdba84f072b0', 'nd_film3.mp4': 'b54073509e3e0acc6bdd2c6ce9f7b44d', 'nd_last3.webp': 'ff9e25768da640a1eb7ced3ab79b0a39',
       'gk_film.mp4': 'e0cbfa4408ca4092dd53550e50821c4a', 'gk_last.webp': '922c113414d599bfdc354a1fe1286e45', 'sgd_film2.mp4': '561c2d853e363119cd713e693d50b6f1', 'sgd_last2.webp': '657236f8c21d03874b2946d4291e8425'}

print('■ アプリ（動画の 名前）')
check(BF.FILMS == {'sgd_film': 'sgd_film2.mp4', 'sd_film': 'sd_film4.mp4', 'nd_film': 'nd_film4.mp4', 'gk_film': 'gk_film2.mp4'}
      and BF.STILL == {'sgd_last': 'sgd_last2.webp', 'sd_last': 'sd_last4.webp', 'nd_last': 'nd_last4.webp', 'gk_last': 'gk_last2.webp'}
      and BF.ART == {'sd': ['sd_last4.webp'], 'nd': ['nd_last4.webp'], 'sgd': ['sgd_last2.webp'], 'gk': ['gk_last2.webp']} and len(BF.ASSET_FILES) == 24,
      f'アプリに 入れる 動画と さいごの 1まい：極ど的中・ノーマルど的中は …4・神様極的中は …2（3倍の もの）・超神様は いままで どおり（ぜんぶで {len(BF.ASSET_FILES)}こ：数は 同じ）')
B = BF.bundle()
check(B['films'] == BF.FILMS and all(BF.STILL[k + '_last'] in B['reveal'][k] for k in ('sd', 'nd', 'gk', 'sgd')) and not any(o in json.dumps(B['reveal']) for o in ('sd_last3.webp', 'nd_last3.webp', 'gk_last.webp'))
      and B['t']['SD'] == 9.9 and B['t']['ND'] == 9.9 and B['t']['GKB'] == 12.0 and B['t']['SDS'] == {'FROM': 9.8, 'WAIT': 1.0},
      '演出の 束（window.__FX）：動画と さいごの 1まいは 新しい 名前・ボードが 出る 時刻は 前と 同じ（音と ずれない）')
fx = rd('fx.js')
check("video('sd_film')" in fx and "video('nd_film')" in fx and "video('gk_film')" in fx and 'film4' not in fx and 'gk_film2' not in fx, 'fx.js は 動画を 名前の 表（A.films）で 引く（ファイルの 名前は 書いて いない ＝ かえて いない）')
S = assets_dir.superseded
allf = set(OLD) | {f for _n, a, b, _o, _p, _c, _r in FILMS for f in (a, b)} | {'sfx_sd.m4a', 'sfx_gk.m4a'}
check(S('fx_assets', allf) == {'sd_film3.mp4', 'sd_last3.webp', 'nd_film3.mp4', 'nd_last3.webp', 'gk_film.mp4', 'gk_last.webp'} and S('fx_assets', allf - {'sd_last4.webp'}) == {'nd_film3.mp4', 'nd_last3.webp', 'gk_film.mp4', 'gk_last.webp'}
      and S('fx_assets', allf - {'gk_film2.mp4'}) == {'sd_film3.mp4', 'sd_last3.webp', 'nd_film3.mp4', 'nd_last3.webp'} and S('fx_assets', set(OLD)) == set() and len(assets_dir.FX_NEW) == 8,
      'アプリに 入れない もの（assets_dir.superseded）：3倍の 動画と さいごの 1まいが そろって いる 組 だけ、前の もの（…3・神様極的中の はじめの もの）を 入れない（そろって いない 組は 前の ものを 使う）')
bf = rd('kisekae', 'build_fx_films.py'); nf = rd('kisekae', 'flat', 'normal_film.py'); sf = rd('kisekae', 'flat', 'shiden_film.py')
check("GK_UP = 'scale=1170:2532:flags=lanczos+accurate_rnd+full_chroma_int,cas=0.5'" in bf and 'def gk_film_up():' in bf and "if float(os.environ.get('SCALE', '1')) != 1:\n        splice = False" in bf
      and "assert im is not None and im.shape[:2] == (H, W), 'さいごの コマが 読めない'" in nf and "assert im is not None and im.shape[:2] == (H, W), 'さいごの コマが 読めない'" in sf
      and "SC = float(os.environ.get('SCALE', '1'))" in sf,
      '動画の 道具：SCALE=1.5 で 3倍の コマを 描く（さいごの 1まいも その 大きさ・ノーマルど的中は 前の 動画と つながずに ぜんぶ 描く）・神様極的中は できた 動画を 3倍に のばす（gk_film_up）')

fxd = assets_dir.master('fx_assets')
NEWF = [f for _n, a, b, _o, _p, _c, _r in FILMS for f in (a, b)]
if os.path.isdir(fxd) and all(os.path.isfile(os.path.join(fxd, f)) for f in NEWF):
    import cv2
    import numpy as np
    print('■ もとの ファイル（ios/fx_assets）')
    check(all(os.path.isfile(os.path.join(fxd, f)) and md5(os.path.join(fxd, f)) == h for f, h in OLD.items()),
          f'前の 動画・さいごの 1まい（{len(OLD)}つ：極ど的中・ノーマルど的中の …3・神様極的中・超神様）は もとの フォルダに ある・1バイトも かわって いない（上書きして いない）')

    def probe(p):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_frames', '-of', 'json', p], capture_output=True, text=True, check=True)
        st = json.loads(r.stdout)['streams']; v = [s for s in st if s['codec_type'] == 'video'][0]; b = open(p, 'rb').read(1 << 16)
        return (len(st), v['codec_name'], v['profile'], v['width'], v['height'], v['pix_fmt'], v['r_frame_rate'], int(v['nb_frames']), 0 <= b.find(b'moov') < (b.find(b'mdat') if b.find(b'mdat') >= 0 else 1 << 30))

    def small(p, w=65, h=140):
        """動画の ぜんぶの コマを 小さく（明るさの 流れを 見る）→ (コマ, h, w, 3)"""
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'scale={w}:{h}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
        return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w, 3)

    def frame(p, i):
        c = cv2.VideoCapture(p); c.set(cv2.CAP_PROP_POS_FRAMES, i); ok, x = c.read(); c.release()
        return x if ok else None

    def psnr(a, b):
        return float(10 * np.log10(255.0 ** 2 / max(1e-9, float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)))))

    def lum(a):
        c = a.astype(np.float64) / 255; c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

    def detail(im):
        """細かい 所の 量（りんかくの 強さの 平均：大きい ほど くっきり）"""
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
        return float(np.mean(np.abs(cv2.Laplacian(g, cv2.CV_32F, ksize=3))))
    tot_new = tot_old = 0
    for nm, film, last, ofilm, olast, n, redraw in FILMS:
        pn, po = os.path.join(fxd, film), os.path.join(fxd, ofilm); a, b_ = probe(pn), probe(po)
        check(a == (1, 'h264', 'High', 1170, 2532, 'yuv420p', '30/1', n, True) and b_[3:5] == (780, 1688) and b_[7] == n,
              f'{JP[nm]}の 新しい 動画（{film}）：H.264 High・1170×2532（前は 780×1688 ＝ たて よこ 1.5倍）・30コマ/秒・{n}コマ（前と 同じ）・音なし・先読みできる 形（{os.path.getsize(pn) / 1e6:.1f}MB・前は {os.path.getsize(po) / 1e6:.1f}MB）')
        tot_new += os.path.getsize(pn); tot_old += os.path.getsize(po)
        # 同じ 絵：新しい 動画の コマを 前の 大きさに 小さく して 前の 動画と くらべる（6コマ）／くっきり：前の コマを 3倍に のばした ものと 細かい 所の 量を くらべる
        ks = [int(n * q) for q in (0.2, 0.36, 0.5, 0.68, 0.84, 0.97)]; ps, dr = [], []
        for k in ks:
            x, y = frame(pn, k), frame(po, k)
            if x is None or y is None: ps.append(0); continue
            ps.append(psnr(cv2.resize(x, (780, 1688), interpolation=cv2.INTER_AREA), y))
            d0 = detail(cv2.resize(y, (1170, 2532), interpolation=cv2.INTER_LINEAR)); dr.append(detail(x) / max(1e-6, d0))
        if not redraw: check(min(ps) > 30 and np.median(ps) > 33, f'{JP[nm]}：前の 動画と 同じ 絵（小さく して くらべた 近さ：{" ".join("%.1f" % v for v in ps)} dB）')
        check(np.median(dr) > (1.25 if redraw else 1.08) and min(dr) > 0.95, f'{JP[nm]}：前の 動画を 画面の 大きさに のばした ものより くっきり（細かい 所の 量 {" ".join("%.2f" % v for v in dr)} 倍）')
        # 明るさの 流れ（点めつ）：1コマごとの 画面 ぜんぶの 明るさ・大きい ます（3×4）の 明るさが 前の 動画と 同じ
        sa, sb = small(pn), small(po)
        if redraw:
            # 描き直した 動画：ぜんぶの コマで、画素ごとの ちがい（0〜1）の まん中の 値 と 大きく（0.25 より）ちがう 画素の 割合 ＝ 雷・火花の ような 細い ものの 形が ちがっても、絵が 同じ なら 小さい
            dd = np.abs(sa.astype(np.float32) - sb.astype(np.float32)).mean(3) / 255 if len(sa) == len(sb) else np.ones((1, 1, 1), np.float32)
            med = np.median(dd.reshape(len(dd), -1), 1); frc = (dd > 0.25).reshape(len(dd), -1).mean(1)
            check(len(sa) == n and len(sb) == n and float(med.max()) < 0.035 and float(frc.max()) < 0.12 and np.median(ps) > 27,
                  f'{JP[nm]}：前の 動画と 同じ 絵（ぜんぶの コマで：画素ごとの ちがいの まん中の 値 {med.max():.3f} まで・大きく ちがう 画素 {frc.max() * 100:.1f}% まで〈雷・火花の 形は 描く たびに かわる〉・6コマの 近さ {" ".join("%.1f" % v for v in ps)} dB）')
        A_, B2 = lum(sa), lum(sb); ga, gb = A_.mean((1, 2)), B2.mean((1, 2))
        ca = np.stack([A_[:, int(i * 35):int((i + 1) * 35), int(j * 21.67):int((j + 1) * 21.67)].mean((1, 2)) for i in range(4) for j in range(3)], 1)
        cb = np.stack([B2[:, int(i * 35):int((i + 1) * 35), int(j * 21.67):int((j + 1) * 21.67)].mean((1, 2)) for i in range(4) for j in range(3)], 1)
        check(len(A_) == n and len(B2) == n and float(np.abs(ga - gb).max()) < 0.03 and float(np.abs(ca - cb).max()) < (0.12 if redraw else 0.08),
              f'{JP[nm]}：明るさの 流れは 前の 動画と 同じ（1コマごとの 差：画面 ぜんぶ {np.abs(ga - gb).max():.3f} まで・大きい ます〈画面の 1/12〉 {np.abs(ca - cb).max():.3f} まで' + ('：雷の 通る 所が ちがう ぶん' if redraw else '') + '）')
        # 点めつ：新しい 動画（アプリに 入る もの）を じかに 数える（60コマ/秒の 絵に して kisekae/flash_px.py：test_fx_flash.py の film と 同じ 数え方）
        ship = os.path.join(assets_dir.adir('fx_assets'), film); ship = ship if os.path.isfile(ship) else pn; td = tempfile.mkdtemp(prefix='fhq_')
        try:
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', ship, '-vf', 'scale=390:844,fps=60', '-start_number', '0', os.path.join(td, 'f%04d.png')], check=True)
            r = subprocess.run(['python3', os.path.join(K, 'flash_px.py'), td, '0'], capture_output=True, text=True, env=dict(os.environ, AREA='.1')); out = r.stdout.strip().split('\n')
        finally: shutil.rmtree(td, ignore_errors=True)
        check(r.returncode == 0 and '窓 0個' in out[0], f'{JP[nm]}：点めつ（新しい 動画を じかに 数えた）：{out[0]}／{out[-1]}')
        st = cv2.imread(os.path.join(fxd, last)); lf = frame(pn, n - 1); ost = cv2.imread(os.path.join(fxd, olast))
        if st is not None and ost is not None:
            dl = np.abs(cv2.resize(st, (780, 1688), interpolation=cv2.INTER_AREA).astype(np.float32) - ost.astype(np.float32)).mean(2) / 255; lmed, lfr = float(np.median(dl)), float((dl > 0.25).mean())
        else: lmed = lfr = 1.0
        check(st is not None and st.shape[:2] == (2532, 1170) and lf is not None and psnr(st, lf) > 30 and ((lmed < 0.035 and lfr < 0.12) if redraw else psnr(cv2.resize(st, (780, 1688), interpolation=cv2.INTER_AREA), ost) > 32),
              f'{last}：1170×2532・動画の さいごの コマと 同じ 絵（近さ {psnr(st, lf) if st is not None and lf is not None else 0:.1f}dB）・前の さいごの 1まいと 同じ 絵（ちがいの まん中の 値 {lmed:.3f}・大きく ちがう 画素 {lfr * 100:.1f}%）')
    print(f'  もとの 動画 3本の 大きさ：{tot_old / 1e6:.1f}MB → {tot_new / 1e6:.1f}MB')
    print('■ 軽い 版（アプリに 入る もの）')
    if assets_dir.is_lite('fx_assets'):
        man = assets_dir.manifest('fx_assets'); lt = assets_dir.lite('fx_assets'); fl = man['files']; lsz = osz = 0
        ok = assets_dir.stale('fx_assets') == '' and all(f in fl and os.path.isfile(os.path.join(lt, f)) for f in NEWF) and not any(f in fl or os.path.exists(os.path.join(lt, f)) for f in OLD if not f.startswith('sgd'))
        for nm, film, last, ofilm, olast, n, redraw in FILMS:
            ok = ok and fl[film]['how'] == 'film' and fl[film]['p'] == ('crf24-slow-tail30:23/20:22/10:21' if redraw else 'crf27-slow-tail30:25/20:23/10:21') and probe(os.path.join(lt, film)) == (1, 'h264', 'High', 1170, 2532, 'yuv420p', '30/1', n, True)
            ok = ok and os.path.getsize(os.path.join(lt, film)) < os.path.getsize(os.path.join(fxd, film)) * 0.85 and md5(os.path.join(lt, last)) == md5(os.path.join(fxd, last))
            lsz += os.path.getsize(os.path.join(lt, film)) + os.path.getsize(os.path.join(lt, last))
        check(ok, f'軽い 版：新しい 6つ（動画 3本・さいごの 1まい 3まい）だけ（前の ものは ない）・描き直した 2本は CRF 24・のばして 作った 神様極的中は CRF 27（どれも さいごの 30コマは 少しずつ きれいに）・形は もとと 同じ・さいごの 1まいは もとの まま（6つで {lsz / 1e6:.1f}MB）')
        print('  軽い 版の 大きさ：' + '・'.join(f'{JP[nm]} {os.path.getsize(os.path.join(lt, film)) / 1e6:.2f}MB' for nm, film, *_ in FILMS))
    else:
        print('  ※ 軽い 版（ios/lite/fx_assets）が ない ので、その 確かめは しない')
else:
    print('  ※ ios/fx_assets に 新しい 動画が ない ので、ファイルの 確かめは しない（CI）')

print('■ リポジトリに 入れない もの')
gi = rd('.gitignore')
tracked = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
bad_t = [f for f in tracked if (f.endswith(('.mp4', '.mov', '.glb')) and not f.startswith('cm_media/')) or '/fx_assets/' in f or '/lite/' in f]      # cm_media/ の CM の 動画（前から ある）は べつ
check('ios/fx_assets/' in gi and 'ios/lite/' in gi and not bad_t, f'的中の 演出の 動画・さいごの 1まい・まさちゃんの 3D・軽い 版は リポジトリに 入って いない{bad_t[:3] if bad_t else ""}')
print()
print('結果：', 'ぜんぶ OK' if not fails else f'{len(fails)} こ ❌')
for f in fails: print('  ❌', f)
sys.exit(1 if fails else 0)
