# 軽い 版の 絵と 動画を 作る（第4.146版・まさちゃん 2026/11/10 21:26「圧縮少しやわらか−45Mbの方でやって！」）
#   python3 kisekae/lite_assets.py            … ios/lite/<フォルダ>/ を 作る・直す（もとが かわった もの だけ 作り直す）
#   python3 kisekae/lite_assets.py --check    … 古く なって いないか だけ 見る（古ければ 1 で おわる）
#   もと（マスター）＝ios/fx_assets・ios/bcp_assets・ios/tc_assets・ios/fig_assets は **読む だけ**（上書きしない・消さない）。
#   軽い 版＝ios/lite/<同じ 名前>/：もとと 同じ 名前の ファイルを 置く（軽く する もの は 作り直した もの・ほかは そのままの 写し）＋ 台帳 lite.info。
#     どの フォルダを アプリに 入れるかは assets_dir.py の adir()（軽い 版が あれば そちら・LITE=0 で もと）
#   軽く する もの（まさちゃんに 見せた「少し やわらか」と 同じ 強さ）：
#     ・動画（fx_assets の *.mp4）：H.264 CRF 29・preset slow。大きさ・コマ数・30コマ／秒・yuv420p・faststart・音なし は もとと 同じ（作った あとに 確かめる）
#         「さいごの 1まい」（<名前>_last.webp）に つながる 動画（gk・sd・nd・sgd）は、さいごの 30コマ だけ 少しずつ きれいに する（CRF 27 → 25 → 22：x264 の zones）。
#         動画が おわった 瞬間に きれいな 1まい絵に かわる ので、さいごまで やわらかい ままだと そこで 絵が パッと はっきり して 見える（ためした 数：さいごの コマが 36dB → 41dB・1本 ＋約0.25MB）
#     ・絵（WebP quality 75・method 6。すき通し（アルファ）は もとと 1点も かえない）：
#         結果ボードの 絵（bcp_assets：見本・背景・前の 絵・キャラ・動かない 物）／馬の 色（tc_assets の tc_c_*）／フィギュアと 棚の 色（fig_assets の fgN_c・fgN_cs・fg_shelf_c*）
#   さわらない もの（そのままの 写し）：
#     ・でこぼこ（法線：tc_n_*・fgN_n・fgN_ns）＝光り方に ひびく
#     ・つや（金属／あらさ：fgN_m・fgN_ms）＝WebP の 圧縮は 色を 2×2 で まとめて ブロックの まだらに なる（kisekae/fig/collect_assets.py）ので 劣化なしの まま
#     ・光と 雲の 地図と うめる 絵（bcp_*a_m1〜3・bcp_*a_f）＝数（向き・強さ）として 使う 絵
#     ・フィールド・ルーレット・チケット・小物・的中の 絵（pm_*・*_last）・見本の 小さい 絵（fgN_t）・音・形（bin）・json
#   作り直した ものが もとの 97% より 大きい ときは もとを そのまま 使う（how＝keep）
#   台帳 lite.info（JSON）：{ v, params, files: { 名前: { how（webp・film・copy・keep）, p（作る ときの 決めごと：かわったら 作り直す）, src: [大きさ, 更新の 時刻, sha1], size } } }
import hashlib, json, os, re, shutil, subprocess, sys, time
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
sys.path.insert(0, W); import assets_dir as AD
sys.path.insert(0, os.path.join(H, 'bcp')); import bcp_app as B
PARAMS = {'crf': 29, 'preset': 'slow', 'tail': [[30, 27], [20, 25], [10, 22]], 'q': 75, 'method': 6, 'keep': 0.97}      # tail＝[さいごから 何コマ, CRF]（さいごの 1まいに つながる 動画 だけ）
V = 1
_M = B.MOTION
BCP_KEEP = {_M[n]['amb'][k] for n in _M if _M[n].get('amb') for k in ('m1', 'm2', 'm3', 'f')}      # 光と 雲の 地図・うめる 絵


def rule(name, f):
    """その ファイルを どう するか：film・webp・copy"""
    if name == 'fx_assets':
        return 'film' if f.endswith('.mp4') else 'copy'
    if name == 'bcp_assets':
        return 'webp' if f.endswith('.webp') and f not in BCP_KEEP else 'copy'
    if name == 'tc_assets':
        return 'webp' if re.fullmatch(r'tc_c_.+\.webp', f) else 'copy'
    if name == 'fig_assets':
        return 'webp' if re.fullmatch(r'fg(\d+_cs?|_shelf_c\d+)\.webp', f) else 'copy'
    raise ValueError(name)


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def probe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_frames,duration', '-of', 'json', p], capture_output=True, text=True, check=True)
    st = json.loads(r.stdout)['streams']
    v = [s for s in st if s['codec_type'] == 'video']
    b = open(p, 'rb').read(1 << 16)
    return {'n': len(st), 'v': v[0] if v else None, 'fast': 0 <= b.find(b'moov') < (b.find(b'mdat') if b.find(b'mdat') >= 0 else 1 << 30)}


def has_tail(src):
    """さいごの 1まい（<名前>_last.webp）に つながる 動画か（gk_film.mp4 → gk_last.webp）"""
    m = re.fullmatch(r'(.+)_film\.mp4', os.path.basename(src))
    return bool(m) and os.path.isfile(os.path.join(os.path.dirname(src), m.group(1) + '_last.webp'))


def sig(name, f, how):
    """その ファイルを 作る ときの 決めごと（かわったら 作り直す）"""
    if how == 'film':
        return f"crf{PARAMS['crf']}-{PARAMS['preset']}" + ('-tail' + '/'.join(f'{a}:{b}' for a, b in PARAMS['tail']) if has_tail(os.path.join(AD.master(name), f)) else '')
    if how == 'webp':
        return f"q{PARAMS['q']}-m{PARAMS['method']}"
    return ''


def enc_film(src, dst):
    tmp = dst + '.tmp.mp4'; a = probe(src); n = int(a['v']['nb_frames']); zones = []
    if has_tail(src):
        edges = [n - k for k, _c in PARAMS['tail']] + [n]
        zones = ['-x264-params', 'zones=' + '/'.join(f'{edges[i]},{edges[i + 1] - 1},crf={c}' for i, (_k, c) in enumerate(PARAMS['tail']))]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-map', '0:v:0', '-c:v', 'libx264', '-profile:v', 'high', '-preset', PARAMS['preset'], '-crf', str(PARAMS['crf']), *zones,
                    '-pix_fmt', 'yuv420p', '-an', '-threads', '2', '-movflags', '+faststart', '-map_metadata', '-1', tmp], check=True)
    b = probe(tmp)
    for k in ('codec_name', 'profile', 'width', 'height', 'pix_fmt', 'r_frame_rate', 'nb_frames'):
        assert a['v'][k] == b['v'][k], (os.path.basename(src), k, a['v'][k], b['v'][k])
    assert abs(float(a['v']['duration']) - float(b['v']['duration'])) < 1e-3, (src, a['v']['duration'], b['v']['duration'])
    assert b['n'] == 1 and a['n'] == 1 and b['fast'], (src, a['n'], b['n'], b['fast'])        # 絵だけ（音なし）・faststart
    os.replace(tmp, dst)


def enc_webp(src, dst):
    import numpy as np
    from PIL import Image
    im = Image.open(src); im.load()
    assert im.mode in ('RGB', 'RGBA'), (src, im.mode)
    tmp = dst + '.tmp.webp'
    im.save(tmp, 'WEBP', quality=PARAMS['q'], method=PARAMS['method'])
    out = Image.open(tmp); out.load()
    assert out.mode == im.mode and out.size == im.size, (src, im.mode, out.mode, im.size, out.size)
    if im.mode == 'RGBA':
        assert np.array_equal(np.asarray(im)[..., 3], np.asarray(out)[..., 3]), src + '：すき通しが かわった'
    os.replace(tmp, dst)


def one(job):
    name, f, how = job
    src = os.path.join(AD.master(name), f); dst = os.path.join(AD.lite(name), f)
    t0 = time.time()
    if how == 'film':
        enc_film(src, dst)
    elif how == 'webp':
        enc_webp(src, dst)
    else:
        shutil.copy2(src, dst)
    if how in ('film', 'webp') and os.path.getsize(dst) > PARAMS['keep'] * os.path.getsize(src):
        shutil.copy2(src, dst); how = 'keep'                      # 小さく ならない → もとを そのまま
    return name, f, how, os.path.getsize(dst), time.time() - t0


def build(only=None):
    jobs = []; mans = {}
    for name in AD.NAMES:
        if only and name not in only:
            continue
        m, p = AD.master(name), AD.lite(name)
        if not os.path.isdir(m):
            print('※ もとが ない：', m); continue
        os.makedirs(p, exist_ok=True)
        try:
            old = AD.manifest(name) or {}
        except Exception:
            old = {}
        same = old.get('v') == V
        want = AD.expected(name); man = {'v': V, 'params': PARAMS, 'files': {}}; mans[name] = man
        for f in want:
            sp = os.path.join(m, f); st = os.stat(sp); how = rule(name, f); e = (old.get('files') or {}).get(f) if same else None
            pp = os.path.join(p, f)
            sg = sig(name, f, how)
            if e and os.path.isfile(pp) and os.path.getsize(pp) == e['size'] and e['how'] in ((how, 'keep') if how != 'copy' else ('copy',)) \
                    and e.get('p', {'webp': 'q75-m6', 'film': 'crf29-slow'}.get(how, '')) == sg:
                if e['src'][:2] == [st.st_size, st.st_mtime_ns] or (e['src'][0] == st.st_size and e['src'][2] == sha1(sp)):
                    man['files'][f] = {'how': e['how'], 'p': sg, 'src': [st.st_size, st.st_mtime_ns, e['src'][2]], 'size': e['size']}      # かわって いない
                    continue
            man['files'][f] = {'how': how, 'p': sg, 'src': [st.st_size, st.st_mtime_ns, sha1(sp)], 'size': -1}
            jobs.append((name, f, how))
        for f in sorted(os.listdir(p)):                               # 軽い 版の フォルダに 残った いらない もの（軽い 版の 中 だけ 消す）
            if f != AD.INFO and f not in want:
                q = os.path.join(p, f); assert os.path.dirname(os.path.abspath(q)) == os.path.abspath(p) and os.sep + os.path.join('ios', 'lite') + os.sep in os.path.abspath(q), q
                os.remove(q)
    films = [j for j in jobs if j[2] == 'film']; rest = [j for j in jobs if j[2] != 'film']
    print('作る もの：動画', len(films), '・絵', sum(1 for j in rest if j[2] == 'webp'), '・写し', sum(1 for j in rest if j[2] == 'copy'), flush=True)
    done = 0; t0 = time.time()
    for j in films:
        name, f, how, size, sec = one(j); mans[name]['files'][f].update(how=how, size=size); done += 1
        print(f'  {f}：{mans[name]["files"][f]["src"][0] / 1e6:.2f}MB → {size / 1e6:.2f}MB（{how}・{sec:.0f}秒）', flush=True)
    if rest:
        with Pool(int(os.environ.get('LITE_J', str(os.cpu_count() or 1)))) as P:
            for name, f, how, size, sec in P.imap_unordered(one, rest, chunksize=1):
                mans[name]['files'][f].update(how=how, size=size); done += 1
                if done % 50 == 0:
                    print(f'  {done}／{len(jobs)}（{time.time() - t0:.0f}秒）', flush=True)
    for name, man in mans.items():
        assert all(e['size'] >= 0 for e in man['files'].values()), name
        tmp = os.path.join(AD.lite(name), AD.INFO + '.tmp')
        json.dump(man, open(tmp, 'w', encoding='utf8'), ensure_ascii=False, indent=0, sort_keys=True); os.replace(tmp, os.path.join(AD.lite(name), AD.INFO))
    return mans


def report():
    tot0 = tot1 = 0
    for name in AD.NAMES:
        man = AD.manifest(name)
        if not man:
            continue
        by = {}
        for f, e in man['files'].items():
            b = by.setdefault(e['how'], [0, 0, 0]); b[0] += 1; b[1] += e['src'][0]; b[2] += e['size']
        s0 = sum(b[1] for b in by.values()); s1 = sum(b[2] for b in by.values()); tot0 += s0; tot1 += s1
        print(f'{name}：{len(man["files"])}こ {s0 / 1e6:.2f}MB → {s1 / 1e6:.2f}MB（{(s1 - s0) / 1e6:+.2f}MB）  ' +
              '・'.join(f'{k} {b[0]}こ {b[1] / 1e6:.2f}→{b[2] / 1e6:.2f}MB' for k, b in sorted(by.items())) + f'  ［{AD.stale(name) or "新しい"}］')
    print(f'合わせて：{tot0 / 1e6:.2f}MB → {tot1 / 1e6:.2f}MB（{(tot1 - tot0) / 1e6:+.2f}MB）')


if __name__ == '__main__':
    if '--check' in sys.argv:
        bad = {n: AD.stale(n) for n in AD.NAMES}
        for n, w in bad.items():
            print(n, '：', 'ない' if w is None else (w or '新しい'))
        sys.exit(1 if any(w for w in bad.values()) or all(w is None for w in bad.values()) else 0)
    if '--report' not in sys.argv:
        build([a for a in sys.argv[1:] if a in AD.NAMES] or None)
    report()
