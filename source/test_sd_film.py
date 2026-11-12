# 極ど的中（紫電）と ノーマルど的中の 新しい 動画（第4.163版・まさちゃん 2026/11/13 00:15「極ど的中の演出の馬、文字をこのファイルと入れ替えて！」・
#   02:35「ノーマルど的中演出の文字このファイルと入れ替えて！」）
#   python3 test_sd_film.py   （ios/fx_assets/ が ある とき だけ ファイルの 確かめ・まさちゃんの 3D が ある とき だけ 3D の 確かめ。ない とき（CI）は コードの 確かめ だけ）
#   ・動画の 道具：字は まさちゃんの 3D（kisekae/flat/shiden_gtext.py：縦書きの 的中・ど！！！／極／的中・ど！／的中）・顔の 馬は Violet_Nightmane・
#     3D が ない とき／SD_TEXT=old／SD_HORSE_MODEL=nightmare は 前の 字と 前の 馬で 描ける・動きと 時刻（音・ボード）は 前と 同じ
#   ・字は 画面の 左右の まん中・カメラに ま正面（少し 右下から 見る カメラの ぶん だけ 回して 置く：右へ 曲がって 見えない）
#   ・点めつ（16.6）：3D の 字の ときは 大爆発の 火の粉を 5本に 1本 へらす（字が 欠けて とぶ かけらの 色は 前と 同じ）
#   ・アプリ：動画と さいごの 1まいは 新しい 名前（sd_film2.mp4・sd_last2.webp・nd_film2.mp4・nd_last2.webp）・音は 前と 同じ
#   ・もとの ファイル（マスター）：前の 動画・さいごの 1まい・音は 消して いない・1バイトも かわって いない
#   ・新しい 動画：780×1688・30コマ/秒・315コマ・音なし・ノーマルど的中は はじめの 170コマが 前の 動画と 1画素も 同じ（字が 出る 前は 描き直して いない）
#   ・軽い 版（アプリに 入る もの）：新しい 4つ だけ（前の 4つは ない）・動画は CRF 24（さいごの 30コマは 少しずつ きれいに）
#   ・3D（まさちゃんの Meshy の GLB）と コマは リポジトリに 入って いない
import hashlib, json, os, re, subprocess, sys
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae'); FLAT = os.path.join(K, 'flat')
sys.path.insert(0, W); sys.path.insert(0, K); sys.path.insert(0, FLAT)
import assets_dir
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
rd = lambda *p: open(os.path.join(W, *p), encoding='utf8').read()
# 前の ファイル（第4.162版まで）の md5：もとの フォルダ（ios/fx_assets）に のこす（消さない・上書きしない）
OLD = {'sd_film.mp4': '6b61c0feed45647f30a74a3355fbdf79', 'sd_last.webp': '3ba1bbd82213fd5de6f8c038bb8588d0',
       'nd_film.mp4': '72bad02ed44c616b8c27d6bcbb023b9b', 'nd_last.webp': '713a1be4c3716fca6e8f2d0eadadb3ae'}
NEW = ['sd_film2.mp4', 'sd_last2.webp', 'nd_film2.mp4', 'nd_last2.webp']
PAIR = {'sd_film2.mp4': 'sd_film.mp4', 'sd_last2.webp': 'sd_last.webp', 'nd_film2.mp4': 'nd_film.mp4', 'nd_last2.webp': 'nd_last.webp'}


def py(code, env=None, timeout=900):
    r = subprocess.run([sys.executable, '-c', 'import sys; sys.path[:0] = [%r, %r]\n' % (FLAT, K) + code], capture_output=True, text=True, env=dict(os.environ, **(env or {})), timeout=timeout)
    return r.returncode, (r.stdout.strip().split('\n') or [''])[-1], r.stderr.strip()[-200:]


print('■ 動画の 道具')
gt = rd('kisekae', 'flat', 'shiden_gtext.py'); sf = rd('kisekae', 'flat', 'shiden_film.py'); nf = rd('kisekae', 'flat', 'normal_film.py')
sg = rd('kisekae', 'flat', 'shiden_glb.py'); f2 = rd('kisekae', 'flat', 'shiden_face2.py'); bf = rd('kisekae', 'build_fx_films.py')
check("FILES = dict(title='fortune.glb', logo='emblem.glb', nd='pop.glb')" in gt and 'import shiden_logo as SL' in gt and 'import kami_glb as KG' in gt
      and 'cam = SL.camera()' in gt and 'SL.env(' in gt and "def have(names=('title', 'logo')):" in gt and 'def render(name, W, H' in gt and 'def layer(g, W, H' in gt,
      '3D の 字を 描く 道具（kisekae/flat/shiden_gtext.py）：3つ（縦書きの 的中・ど！！！／極／的中・ど！／的中）・カメラと 映りこむ 光は 前の 字（shiden_logo.py）と 同じ・呼び方も 同じ（render → layer）')
check("FACE_YAW = math.degrees(math.atan2(SL.CAM_DIR[0], SL.CAM_DIR[2])) if os.environ.get('SD_TEXT_YAW', '1') != '0' else 0.0" in gt and 'Ry = SL.rot_xyz(0.0, FACE_YAW, 0.0)' in gt
      and 'q.pos = (((P - c) * sc + o) @ Ry.T).astype(np.float32)' in gt and '@ Ry.T' in gt.split('q.nrm = ')[1][:140],
      '3D の 字は 止まった 形で カメラに ま正面（カメラが 少し 右から 見る ぶん FACE_YAW だけ 回して 置く：右の 横の 面が 広く 見えて 右へ 曲がって 見えない）')
check("GTX = os.environ.get('SD_TEXT', 'glb') != 'old' and GT.have()" in sf and "GT.render('title', W, H, rot, pos)" in sf and "GT.render('logo', W, H, rot, pos) if GTX else SL.render(" in sf
      and 'lay = GT.layer(g, W, H, rot, pos, sweep=sweep_of(lam), flash=flash, heat=heat_of(lam))' in sf and 'return GT.layer(g, W, H, rot, pos, sweep=sw, flash=fl, heat=heat)' in sf
      and "GTN = os.environ.get('SD_TEXT', 'glb') != 'old' and GT.have(('nd',))" in nf and "GT.render('nd', W, H, rot, pos)" in nf,
      '極ど的中（shiden_film.py）の 縦書きの 的中と ロゴ・ノーマルど的中（normal_film.py）の ロゴは 3D が あれば 3D で 描く（向き・場所・光の 筋・雷の 光・白熱は 前と 同じ 流れ）')
check('BOOM_SKIP = 5 if GTX else 0' in sf and 'if not 0 < a < P[\'life\'] or (BOOM_SKIP and i_ % BOOM_SKIP == BOOM_SKIP - 1):' in sf
      and "col=SL.rainbow(np.array([np.clip((c[1] - ytop) / (ybot - ytop), 0, 1)]))[0] * .8 + .04," in sf and 'range(260)]' in sf.split('def boom_tex(')[1].split('\ndef ')[0],
      '点めつ（16.6）：3D の 字の ときは 大爆発の 火の粉を 5本に 1本 へらす（260 → 208本）・字が 欠けて とぶ かけらの 色は 前と 同じ（上 赤 → 下 むらさきの 虹）・前の 字の ときは 前の まま')
check('LOGO_BOX = ((.13, .2, .96, .375), (.05, .375, .97, .63), (.06, .63, .96, .786))' in sf and 'LOGO_FOOT = .8 if GTX else .757' in sf and 'yb = LOGO_FOOT * H' in sf,
      'ロゴの まわりの 火花・火花の 滝は 3D の ロゴの 形（上から ど！！！・極・的中 の 3段）に 合わせた 箱から 出る（字の 上は 通らない）')
check("HORSE_KIND = os.environ.get('SD_HORSE_MODEL', 'nightmane')" in sg and "nightmane=float(os.environ.get('SD_TH0', '8.28'))" in sg and "'nightmane.glb' if HORSE_KIND == 'nightmane' else 'nightmare_old.glb'" in sg
      and "HORSE_KIND = os.environ.get('SD_HORSE_MODEL', 'nightmane')" in f2 and 'nightmane=dict(' in sg.split('LM_ALL = dict(')[1][:1600],
      '顔の 馬は Violet_Nightmane（SD_HORSE_MODEL＝nightmane：目・鼻・口・首の しるしは この 馬の 形で・はじめの 向きは 8.28°）・SD_HORSE_MODEL=nightmare で 前の 馬（前の 数の まま）')
rc, out, err = py('import shiden_film as F, normal_film as N, shiden_gtext as GT\nprint(F.GTX, N.GTN, F.BOOM_SKIP, F.NF, N.NF if hasattr(N, "NF") else 315, GT.have(), F.LOGO_FOOT)',
                  env=dict(SD_TEXT_DIR='/nonexistent', SD_GLB_DIR='/nonexistent'))
check(rc == 0 and out == 'False False 0 315 315 False 0.757', f'3D が ない とき（リポジトリ だけの 所）：前の 字で 描ける 形の まま・火の粉も へらさない（{(out or err)[-80:]}）')
rc, out, err = py('import shiden_glb as G, shiden_face2 as F2\nprint(G.HORSE_KIND, G.TH0_DEG, F2.HORSE_KIND, F2.NECK_A, [round(float(v), 3) for v in F2.PIV])', env=dict(SD_HORSE_MODEL='nightmare'))
check(rc == 0 and out == 'nightmare -5.37 nightmare 36.0 [0.0, 0.58, 0.16]', f'SD_HORSE_MODEL=nightmare：前の 馬の 数（はじめの 向き −5.37°・首 36°・回す 中心）に もどる（{(out or err)[-80:]}）')
import shiden as SDM
import normal_do as NDM
F_ = SDM.FILM
check((F_['BLACK'], F_['FACE'], F_['HOOF'], F_['END'], F_['FPS'], F_['W'], F_['H']) == (1.8, 3.8, 7.4, 10.5, 30, 780, 1688) and F_['T_FLY'] == (.1, 1.3) and F_['L_LAND'] == .5 and F_['H_BOOM'] == 3.22
      and SDM.SD_T['RES'] == 9.9 and NDM.ND_T['RES'] == 9.9 and round(NDM.FILM['END'] * NDM.FILM['FPS']) == 315 and NDM.SD_UP['AT'] == 5.34,
      '動きと 時刻は 前と 同じ（極ど的中：黒 1.8・顔 3.8・蹄 7.4・おわり 10.5秒・ドンッ 7.9秒・ボード 9.9秒／ノーマルど的中：315コマ・ボード 9.9秒／極ど的中の 入りは ノーマルの 5.34秒まで）＝音は 前の まま 合う')
check("film, last = BF.FILMS['sd_film'], BF.STILL['sd_last']" in bf and "film, last = BF.FILMS['nd_film'], BF.STILL['nd_last']" in bf and 'ND_CUT = 170' in bf
      and "splice = os.environ.get('ND_SPLICE', '1') != '0' and film != 'nd_film.mp4' and os.path.exists(old) and ND_CUT in key_frames(old)" in bf
      and "run([FF, '-y', '-loglevel', 'error', '-i', old, '-frames:v', str(ND_CUT), '-c', 'copy', a])" in bf and "assert ok1 and ok2 and np.array_equal(x, y)" in bf
      and 'if os.path.exists(os.path.join(out, name)) and not FORCE:' in bf,
      '動画を 作る 道具（build_fx_films.py）：新しい 名前で 書き出す（もう ある 動画は 上書きしない）・ノーマルど的中は 字が 出る 前の 170コマを 前の 動画から 圧縮し直さずに 使い、170コマ目から だけ 新しく 描いて つなぐ（同じ ことを 確かめてから）')
import shiden_gtext as GT
if GT.have(('title', 'logo', 'nd')):
    code = ('import numpy as np, shiden_gtext as GT, shiden_film as F\nout = {}\n'
            'for name in ("title", "logo", "nd"):\n'
            '    Rb, rect = GT.render(name, 390, 844); ys, xs = np.nonzero(Rb["a"] > .5); K = GT.K_SS\n'
            '    out[name] = [round(float((rect[0] + xs.min()) / K), 1), round(float((rect[0] + xs.max() + 1) / K), 1), round(float((rect[1] + ys.min()) / K), 1), round(float((rect[1] + ys.max() + 1) / K), 1)]\n'
            'lam = round((F.NF - 1) / F.FPS - F.HOOF, 6); rot, pos, s = F.logo_pose(lam)\n'
            'Rb, rect = GT.render("logo", 390, 844, rot, pos); ys, xs = np.nonzero(Rb["a"] > .5); K = GT.K_SS\n'
            'last = [round(float((rect[0] + xs.min()) / K), 1), round(float((rect[0] + xs.max() + 1) / K), 1)]\n'
            'Rb, rect = GT.render("nd", 390, 844); a = Rb["a"] > .5; ys, xs = np.nonzero(a); y0, y1 = ys.min(), ys.max(); low = np.nonzero(a[int(y0 + (y1 - y0) * .65):].any(0))[0]\n'
            'foot = [round(float((rect[0] + low.min()) / K), 1), round(float((rect[0] + low.max() + 1) / K), 1)]\n'
            'print(repr((out, round(GT.FACE_YAW, 2), [round(float(v), 2) for v in rot], round(float(s), 3), last, foot)))')
    rc, out, err = py(code)
    try:
        box, yaw, rot, sc, last, foot = eval(out)
    except Exception:
        box, yaw, rot, sc, last, foot = {}, 0, [9, 9, 9], 0, [0, 0], [0, 0]
    cx = {k: round((v[0] + v[1]) / 2 - 195, 2) for k, v in box.items()}
    cl, cf = round((last[0] + last[1]) / 2 - 195, 2), round((foot[0] + foot[1]) / 2 - 195, 2)
    check(rc == 0 and len(box) == 3 and all(abs(v) < 2.0 for v in cx.values()) and abs(cx.get('title', 9)) < .6 and abs(cx.get('nd', 9)) < .6 and all(v[0] > 8 and v[1] < 382 for v in box.values())
          and abs(yaw - 11.31) < .01 and abs(rot[1]) < .5 and abs(rot[2]) < .2 and 1.02 < sc < 1.04 and abs(cl) < 2.5 and last[0] > 8 and last[1] < 382 and abs(cf) < .6,
          f'手元の 3D で：止まった 字の 左右の まん中は 画面（390）の まん中から {cx}px・左右の はし {dict((k, v[:2]) for k, v in box.items())}・置く 向き {yaw}°（カメラに ま正面）・'
          f'極ど的中の さいごの コマの ロゴは 向き {rot}°（左右は ほぼ 0°）・まん中から {cl}px（はし {last}）・ノーマルど的中の「的中」の 段は まん中から {cf}px（{err[-100:]}）')
else:
    print('  ※ まさちゃんの 3D が ない ので、3D の 確かめは しない（CI）')

print('■ アプリ（新しい 動画の 名前）')
import build_fx as BF
check([BF.FILMS['sd_film'], BF.STILL['sd_last'], BF.FILMS['nd_film'], BF.STILL['nd_last']] == NEW and BF.SFX['sd'] == 'sfx_sd.m4a' and BF.SFX['nd'] == 'sfx_nd.m4a' and BF.SFX['sdp'] == 'sfx_sdp.m4a' and BF.SFX['ndt'] == 'sfx_ndt.m4a'
      and BF.ART['sd'] == ['sd_last2.webp'] and BF.ART['nd'] == ['nd_last2.webp'] and len(BF.ASSET_FILES) == 24 and all(f in BF.ASSET_FILES for f in NEW) and not [f for f in BF.ASSET_FILES if f in OLD],
      f'アプリに 入れる ファイル（{len(BF.ASSET_FILES)}こ）：極ど的中と ノーマルど的中は 新しい 動画と さいごの 1まい（{"・".join(NEW)}）・音は 前と 同じ・前の 4つは 入れない')
B = BF.bundle()
check(B['films']['sd_film'] == 'sd_film2.mp4' and B['films']['nd_film'] == 'nd_film2.mp4' and B['art']['sd'] == ['sd_last2.webp'] and B['art']['nd'] == ['nd_last2.webp']
      and 'sd_last2.webp' in B['reveal']['sd'] and 'sd_last.webp' not in B['reveal']['sd'] and 'nd_last2.webp' in B['reveal']['nd'] and 'nd_last.webp' not in B['reveal']['nd']
      and B['t']['SD'] == 9.9 and B['t']['ND'] == 9.9 and B['t']['SDS'] == {'FROM': 9.8, 'WAIT': 1.0} and B['t']['SDUP']['AT'] == 5.34,
      '演出の 束（window.__FX）：極ど的中・ノーマルど的中の 動画と さいごの 1まいは 新しい 名前・ボードが 出る 時刻・さいごの 1まいに かわる 時刻・極ど的中の 入りは 前と 同じ')
fx = rd('fx.js')
check("video('sd_film')" in fx and "video('nd_film')" in fx and 'sd_film2' not in fx and 'nd_film2' not in fx and 'sd_film.mp4' not in fx and 'nd_film.mp4' not in fx,
      'fx.js は 動画を 名前の 表（A.films）で 引く（ファイルの 名前は 書いて いない ＝ かえて いない）')
S = assets_dir.superseded
allf = set(OLD) | set(NEW) | {'sfx_sd.m4a', 'sfx_nd.m4a', 'gk_film.mp4', 'gk_last.webp', 'sgd_film2.mp4'}
check(S('fx_assets', allf) == set(OLD) and S('fx_assets', allf - {'sd_last2.webp'}) == {'nd_film.mp4', 'nd_last.webp'} and S('fx_assets', allf - {'nd_film2.mp4'}) == {'sd_film.mp4', 'sd_last.webp'}
      and S('fx_assets', set(OLD) | {'sfx_sd.m4a'}) == set() and len(assets_dir.FX_NEW) == 3,
      'アプリに 入れない もの（assets_dir.superseded）：前の 動画と さいごの 1まいは、新しい 2つが そろって いる 組 だけ（極ど的中・ノーマルど的中 べつべつ。そろう までは 前の ものを 使う）')

fxd = assets_dir.master('fx_assets')
if os.path.isdir(fxd) and all(os.path.isfile(os.path.join(fxd, f)) for f in NEW):
    print('■ もとの ファイル（ios/fx_assets）')
    check(all(os.path.isfile(os.path.join(fxd, f)) and md5(os.path.join(fxd, f)) == h for f, h in OLD.items())
          and md5(os.path.join(fxd, 'sfx_sd.m4a')).startswith('cbad0b2e') and md5(os.path.join(fxd, 'sfx_nd.m4a')).startswith('bd829663'),
          '前の 動画・さいごの 1まい（4つ）と 音（極ど的中・ノーマルど的中）は もとの フォルダに ある・1バイトも かわって いない（上書きして いない）')
    import cv2
    import numpy as np

    def probe(p):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_frames', '-of', 'json', p], capture_output=True, text=True, check=True)
        st = json.loads(r.stdout)['streams']; v = [s for s in st if s['codec_type'] == 'video'][0]; b = open(p, 'rb').read(1 << 16)
        return (len(st), v['codec_name'], v['profile'], v['width'], v['height'], v['pix_fmt'], v['r_frame_rate'], int(v['nb_frames']), 0 <= b.find(b'moov') < (b.find(b'mdat') if b.find(b'mdat') >= 0 else 1 << 30))

    def frame(p, i):
        c = cv2.VideoCapture(p); c.set(cv2.CAP_PROP_POS_FRAMES, i); ok, x = c.read(); c.release()
        return x if ok else None

    def psnr(a, b):
        return float(10 * np.log10(255.0 ** 2 / max(1e-9, float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)))))
    want = (1, 'h264', 'High', 780, 1688, 'yuv420p', '30/1', 315, True)
    ps, pn = probe(os.path.join(fxd, 'sd_film2.mp4')), probe(os.path.join(fxd, 'nd_film2.mp4'))
    check(ps == want and pn == want and probe(os.path.join(fxd, 'sd_film.mp4')) == want and probe(os.path.join(fxd, 'nd_film.mp4')) == want,
          f'新しい 動画（もと）：2本とも H.264 High・780×1688・30コマ/秒・315コマ・音なし・先読みできる 形（前の 動画と 同じ）（{ps[1:8]}）')
    so, sn = os.path.join(fxd, 'nd_film.mp4'), os.path.join(fxd, 'nd_film2.mp4')
    co, cn = cv2.VideoCapture(so), cv2.VideoCapture(sn); same = 0; dif = None
    for i in range(315):
        ok1, x = co.read(); ok2, y = cn.read()
        if not (ok1 and ok2):
            break
        if i < 170:
            same += int(np.array_equal(x, y))
        elif i in (200, 260, 314):
            dif = min(dif, psnr(x, y)) if dif is not None else psnr(x, y)
    co.release(); cn.release()
    check(same == 170 and dif is not None and dif < 30, f'ノーマルど的中の 新しい 動画：はじめの 170コマ（字が 出る 前）は 前の 動画と 1画素も 同じ（{same}コマ）・字が 出た あとは 新しい 絵（前との 近さ {dif:.1f}dB）')
    b0, b53, f60, f150, f240 = (frame(os.path.join(fxd, 'sd_film2.mp4'), i) for i in (0, 53, 60, 150, 240))
    o60, o150, o240 = (frame(os.path.join(fxd, 'sd_film.mp4'), i) for i in (60, 150, 240))
    check(b0 is not None and b0.max() < 8 and b53.max() < 8 and f60.mean() > 1 and psnr(f150, o150) < 30 and psnr(f240, o240) < 30 and psnr(f60, o60) < 45,
          f'極ど的中の 新しい 動画：はじめの 54コマは 黒（前と 同じ）・顔（馬）・蹄の 場面（縦書きの 的中）・ロゴの 場面は 新しい 絵（前との 近さ：顔 {psnr(f60, o60):.1f}・的中 {psnr(f150, o150):.1f}・ロゴ {psnr(f240, o240):.1f}dB）')
    for film, last in (('sd_film2.mp4', 'sd_last2.webp'), ('nd_film2.mp4', 'nd_last2.webp')):
        a = frame(os.path.join(fxd, film), 314); b = cv2.imread(os.path.join(fxd, last))
        check(a is not None and b is not None and b.shape[:2] == (1688, 780) and psnr(a, b) > 33, f'{last}：780×1688・動画の さいごの コマと 同じ 絵（近さ {psnr(a, b) if a is not None and b is not None else 0:.1f}dB）')

    def edge_free(pth):
        """さいごの 1まい：字（色が こくて 明るい 所）が 画面の 左右の はし（1%）に かかって いない"""
        img = cv2.imread(pth); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); H_, W_ = img.shape[:2]; e = max(2, int(.01 * W_))
        m = ((hsv[..., 1] > 150) & (hsv[..., 2] > 170))[int(.2 * H_):int(.8 * H_)]
        return float(m[:, :e].mean()), float(m[:, -e:].mean()), float(m.mean())
    es, en = edge_free(os.path.join(fxd, 'sd_last2.webp')), edge_free(os.path.join(fxd, 'nd_last2.webp'))
    check(max(es[:2]) < .03 and max(en[:2]) < .03 and es[2] > .15 and en[2] > .1,
          f'さいごの 1まい：字は 画面の 中に おさまって いる（左右の はし 1% に かかる 割合：極ど的中 {es[0] * 100:.1f}%・{es[1] * 100:.1f}%／ノーマルど的中 {en[0] * 100:.1f}%・{en[1] * 100:.1f}%）')
    print('■ 軽い 版（アプリに 入る もの）')
    if assets_dir.is_lite('fx_assets'):
        man = assets_dir.manifest('fx_assets'); lt = assets_dir.lite('fx_assets'); fl = man['files']
        check(all(f in fl and os.path.isfile(os.path.join(lt, f)) for f in NEW) and not any(f in fl or os.path.exists(os.path.join(lt, f)) for f in OLD) and assets_dir.stale('fx_assets') == ''
              and all(fl[f]['p'] == 'crf24-slow-tail30:23/20:22/10:21' for f in ('sd_film2.mp4', 'nd_film2.mp4')) and all(fl[f]['how'] == 'film' for f in ('sd_film2.mp4', 'nd_film2.mp4'))
              and probe(os.path.join(lt, 'sd_film2.mp4')) == want and probe(os.path.join(lt, 'nd_film2.mp4')) == want
              and all(os.path.getsize(os.path.join(lt, f)) < os.path.getsize(os.path.join(fxd, f)) * .7 for f in ('sd_film2.mp4', 'nd_film2.mp4'))
              and all(md5(os.path.join(lt, f)) == md5(os.path.join(fxd, f)) for f in ('sd_last2.webp', 'nd_last2.webp')),
              f'軽い 版：新しい 4つ だけ（前の 4つは ない）・動画は CRF 24（さいごの 30コマは 少しずつ きれいに）・形は もとと 同じ（極ど的中 {os.path.getsize(os.path.join(lt, "sd_film2.mp4")) / 1e6:.2f}MB・'
              f'ノーマルど的中 {os.path.getsize(os.path.join(lt, "nd_film2.mp4")) / 1e6:.2f}MB・さいごの 1まい {os.path.getsize(os.path.join(lt, "sd_last2.webp")) / 1e3:.0f}KB・{os.path.getsize(os.path.join(lt, "nd_last2.webp")) / 1e3:.0f}KB）')
    else:
        print('  ※ 軽い 版（ios/lite/fx_assets）が ない ので、その 確かめは しない')
else:
    print('  ※ ios/fx_assets に 新しい 動画が ない ので、ファイルの 確かめは しない（CI）')

print('■ リポジトリに 入れない もの')
ls = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
ig = lambda p: subprocess.run(['git', 'check-ignore', '-q', p], cwd=os.path.dirname(W)).returncode == 0
check(not [f for f in ls if f.lower().endswith(('.glb', '.npz', '.f32'))] and not [f for f in ls if f.lower().endswith('.mp4') and not f.startswith('cm_media/')]
      and not [f for f in ls if re.search(r'(sd|nd)_(film|last)\d*\.(mp4|webp|webm)$', f)]
      and all(ig('source/ios/fx_assets/' + f) for f in NEW) and all(ig('source/ios/lite/fx_assets/' + f) for f in NEW)
      and '/home/claude/work/sd163/orig' in gt and os.path.isfile(os.path.join(FLAT, 'shiden_gtext.py')) and not ig('source/kisekae/flat/shiden_gtext.py'),
      'まさちゃんの 3D（GLB）・動画・さいごの 1まい・コマは リポジトリに 入って いない（3D の 場所は リポジトリの 外：SD_TEXT_DIR・SD_GLB_DIR）・道具（shiden_gtext.py）は 入って いる')

print('\n' + ('✅ ぜんぶ OK' if not fails else f'❌ {len(fails)}こ だめ'))
sys.exit(1 if fails else 0)
