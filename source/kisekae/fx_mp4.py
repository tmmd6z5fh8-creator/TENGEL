# 的中演出を アプリの 画面の まま MP4（音つき）に する（まさちゃん 11/10 09:32「超神様的中と超プレミアム神様的中の演出の中身を少し変えたい！
#   とりあえずベースになるのは超神様的中演出だからMP4で出せる？」）
#   python3 kisekae/fx_mp4.py sgd <出す mp4> [PUSH を 見せる 秒（2.0）]
#   ・超神様的中（sgd）：PUSH の 画面（虹色の 超デカ PUSH・音 fz_push）→ タップ → 超神様の 動画（sgd_film・12.83秒〈第4.162版：球体の 場面なし。前は 14.23秒〉・音 sfx_sgd）→ 白い 光 → ボード（超神様的中！！！）
#   ・画面は アプリと 同じ（TARGET=app の ページ・390×844 を 3倍＝1170×2532・30コマ/秒）。動きは CSS と SVG（SMIL）だけ なので 1コマずつ 止めて 写す
#     動画の ところ（白い 光の 少し 前＝B_FROM 秒 まで）は 動画（アプリに 入る 超神様の 動画：assets_dir.adir('fx_assets')・名前は build_fx.py の FILMS）の コマ そのもの（その 間 幕の 上には 何も 出ない）。
#     B_FROM 秒 から は 幕を 動いた 形（go）に して、うしろに その 時刻の 動画の コマを しいて 白い 光と ボードを 写す
#   ・音：押す 前は fz_push（PUSH が 出た 時から）・押した 瞬間に 止めて sfx_sgd（動画と 同じ 0秒）。アプリの 動きと 同じ（fx.js の push・onPlaying）
#   ・ボードの 中身は 見本の レース（3連単 11→3→6：超大穴・大穴・1番人気）
#   ・PUSH は アプリと 同じ「いつもの」の 絵（ios/push_assets の pb_default.webp：第4.162版から 置く。ない ときは コードの PUSH）
import math, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(W)
sys.path.insert(0, os.path.join(W, 'kisekae'))
import kami_super as K
import build_fx as BF

KIND = sys.argv[1]; OUT = os.path.abspath(sys.argv[2]); PUSH_T = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
assert KIND == 'sgd', '今は 超神様的中（sgd）だけ'
FPS, DPR = 30, 3
sys.path.insert(0, W)
import assets_dir
FX = assets_dir.adir('fx_assets')      # 第4.162版：アプリに 入る もの（軽い 版 ios/lite/fx_assets が あれば そちら）で 作る ＝ 見本の 動画の 画質は アプリと 同じ
FILM = os.path.join(FX, BF.FILMS['sgd_film']); SND = os.path.join(FX, BF.SFX['sgd'])
WORK = os.path.join(os.path.dirname(OUT), '_fxmp4_' + KIND); SRV = os.path.join(WORK, 'srv'); PORT = 8807
B_FROM = math.floor((K.RES - .15) * 10) / 10      # ここから ブラウザで 写す（白い 光は RES−0.15 秒から：第4.162版 12.78秒 → 12.7・前は 14.18秒 → 14.1）
END = K.RES + 4.2                    # 押してから ここまで（音は ボードの 買い目の 2秒 あとで おわる・ボードを 少し 見せる）
NF = int(round(K.FILM * FPS))        # 動画の コマ数（第4.162版 385・前は 427）
SPEC = {'r': 9, 'n': 12, 'ranks': {'6': 1, '2': 2, '10': 3, '4': 5, '7': 4, '11': 11, '1': 9, '3': 8, '5': 7, '9': 6, '8': 12, '12': 10},
        'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 3, 6]], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 3]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 9}]}
STEP = """(t) => { const ov = document.getElementById('fxOv'); if (!ov) return -1;
  const as = ov.getAnimations({ subtree: true }); as.forEach(a => { try { a.pause(); a.currentTime = t * 1000; } catch (e) {} });
  ov.querySelectorAll('svg').forEach(s => { try { s.pauseAnimations(); s.setCurrentTime(t); } catch (e) {} });
  return as.length; }"""
BG = "([u]) => new Promise(ok => { const im = new Image(); im.onload = im.onerror = () => { const o = document.querySelector('#fxOv .ov.sgd'); if (o) o.style.background = '#000 url(' + u + ') center / cover no-repeat'; requestAnimationFrame(() => requestAnimationFrame(() => ok(1))); }; im.src = u; })"


def main():
    shutil.rmtree(WORK, ignore_errors=True); os.makedirs(SRV)
    fp = os.path.join(WORK, 'push'); fb = os.path.join(WORK, 'board'); os.makedirs(fp); os.makedirs(fb)
    subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
    pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in html
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
    for f in os.listdir(FX):
        if f.endswith('.webp'): shutil.copy(os.path.join(FX, f), os.path.join(SRV, 'APP', f))
    # 第4.162版（まさちゃん 2026/11/13 00:18「さっきの試しの動画だと昔のpushボタンだったから確認！」）：PUSHボタンの 絵（ios/push_assets の pb_<テーマ>.webp：アプリには 入って いる）も 置く。
    #   前は 置いて いなかった ので、動画の 中の PUSH が コードの PUSH（絵が 読めない ときの 形）に なって いた。ない とき（リポジトリ だけの 所）は コードの PUSH の まま
    import push_art as _pa
    pb = _pa.files()
    for e in pb.values():
        shutil.copy(os.path.join(_pa.ROOT, e['f']), os.path.join(SRV, 'APP', e['f']))
    # 白い 光と ボードの うしろに しく 動画の コマ（14.1秒〜さいご）
    fd = os.path.join(SRV, 'APP', '_f'); os.makedirs(fd)
    first = int(round(B_FROM * FPS))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', FILM, '-vf', f'select=gte(n\\,{first})', '-vsync', '0', '-start_number', str(first), os.path.join(fd, 'f%04d.png')], check=True)
    srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(.8)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DPR, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='no-preference')
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500)
            if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(800)
            if pb:                                                        # PUSH の 絵が 読める まで 待つ（読めて いない 間は コードの PUSH に なる）
                pg.wait_for_function("() => { try { return !!(window.TengelKisekae && TengelKisekae.pushArt && TengelKisekae.pushArt()); } catch (e) { return false; } }", timeout=8000)
            pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sgd' }, s))", SPEC); pg.wait_for_timeout(500)
            assert pg.evaluate('TengelFx.current().kind') == 'sgd'
            art = pg.evaluate('TengelFx.current().art')
            assert not pb or art == 'pb_default.webp', art                # 絵が ある ときは「いつもの」の PUSH の 絵で 出て いる
            print('PUSH の 絵：', art or 'なし（コードの PUSH）', flush=True)
            t0 = time.time()
            for i in range(int(round(PUSH_T * FPS))):
                pg.evaluate(STEP, i / FPS); pg.screenshot(path=os.path.join(fp, f'p{i:04d}.png'))
            print(f'PUSH {int(round(PUSH_T * FPS))}コマ（{time.time() - t0:.0f}秒）', flush=True)
            pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(400)
            # 動いた 形（go）に する（ここの ブラウザでは 動画が 動かない ことが ある → さいごの 1まいの 形（still）に なって いたら もどす）
            pg.evaluate("() => { const o = document.querySelector('#fxOv .ov.sgd'); o.classList.remove('still'); o.classList.add('go'); }"); pg.wait_for_timeout(300)
            t0 = time.time(); k = 0
            for i in range(first, int(round(END * FPS))):
                t = i / FPS; fi = min(i, NF - 1)
                pg.evaluate(BG, [f'_f/f{fi:04d}.png'])
                pg.evaluate(STEP, t); pg.screenshot(path=os.path.join(fb, f'b{k:04d}.png')); k += 1
            print(f'白い 光と ボード {k}コマ（{time.time() - t0:.0f}秒）', flush=True)
            if errs: print('ページの エラー', errs[:3])
            b.close()
    finally:
        srv.terminate()
    # つなぐ：PUSH（PNG）＋ 動画（0〜14.1秒）＋ 白い 光と ボード（PNG）。音：fz_push（PUSH の 間）→ sfx_sgd（押した 瞬間 から）
    dur = PUSH_T + END
    fc = (f'[0:v]format=yuv420p,setsar=1[a];[1:v]trim=end_frame={first},setpts=PTS-STARTPTS,format=yuv420p,setsar=1[b];[2:v]format=yuv420p,setsar=1[c];'
          f'[a][b][c]concat=n=3:v=1:a=0[v];'
          f'[3:a]atrim=0:{PUSH_T},asetpts=PTS-STARTPTS[pa];[4:a]asetpts=PTS-STARTPTS[sa];[pa][sa]concat=n=2:v=0:a=1,apad,atrim=0:{dur:.3f}[au]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(fp, 'p%04d.png'), '-i', FILM, '-framerate', str(FPS), '-i', os.path.join(fb, 'b%04d.png'),
                    '-i', os.path.join(FX, 'sfx_fz_push.m4a'), '-i', SND,
                    '-filter_complex', fc, '-map', '[v]', '-map', '[au]', '-r', str(FPS),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], check=True)
    print('できた', OUT, flush=True)


if __name__ == '__main__':
    main()
