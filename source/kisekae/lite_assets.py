# 軽い 版の 絵と 動画を 作る（第4.146版・まさちゃん 2026/11/10 21:26「圧縮少しやわらか−45Mbの方でやって！」）
#   python3 kisekae/lite_assets.py            … ios/lite/<フォルダ>/ を 作る・直す（もとが かわった もの だけ 作り直す）
#   python3 kisekae/lite_assets.py --check    … 古く なって いないか だけ 見る（古ければ 1 で おわる）
#   もと（マスター）＝ios/fx_assets・ios/bcp_assets・ios/tc_assets・ios/fig_assets は **読む だけ**（上書きしない・消さない）。
#   軽い 版＝ios/lite/<同じ 名前>/：もとと 同じ 名前の ファイルを 置く（軽く する もの は 作り直した もの・ほかは そのままの 写し）＋ 台帳 lite.info。
#     どの フォルダを アプリに 入れるかは assets_dir.py の adir()（軽い 版が あれば そちら・LITE=0 で もと）
#   軽く する もの（まさちゃんに 見せた「少し やわらか」と 同じ 強さ）：
#     ・動画（fx_assets の *.mp4）：H.264 CRF 24・preset slow。大きさ・コマ数・30コマ／秒・yuv420p・faststart・音なし は もとと 同じ（作った あとに 確かめる）
#         「さいごの 1まい」（<名前>_last.webp）に つながる 動画（gk・sd・nd・sgd）は、さいごの 30コマ だけ 少しずつ きれいに する（CRF 23 → 22 → 21：x264 の zones）。
#         動画が おわった 瞬間に きれいな 1まい絵に かわる ので、さいごまで やわらかい ままだと そこで 絵が パッと はっきり して 見える
#         第4.156版（まさちゃん 2026/11/12 04:20「的中の演出も大分画質落ちているから綺麗な状態にしてほしい！」・04:41「ほぼ見た目同じより、少し綺麗にしてみるのはどう？
#           そしたら綺麗だけど、＋21.0MBまでは増えないんじゃない！」）：CRF 29（第4.146版）→ **CRF 24**。
#           もと（マスター：nd・sd＝CRF 20／gk＝CRF 23／spg・sgd＝CRF 24）と くらべた 近さ（PSNR・5本）：CRF 29＝38.7〜42.7dB → 26＝40.9〜45.7 → 25＝41.9〜47.1 → **24＝43.1〜48.7** → 23＝44.0〜49.2。
#           大きさ（5本・さいごの コマの 分は 別）：29＝18.5MB・26＝25.0・25＝27.9・**24＝31.0**・23＝34.0・もと＝39.5MB（＋21.0MB）。
#           いちばん 差の 出る コマ（金の かざりの 細かい もよう）を 2倍に のばして 見くらべて、もとに 近く 戻る 24 に 決めた（26＝「ほぼ 同じ」は もようが まだ とける）
#     ・絵（WebP quality 75・method 6。すき通し（アルファ）は もとと 1点も かえない）：
#         馬の 色（tc_assets の tc_c_*）／フィギュアの 色（fig_assets の fgN_c・fgN_cs）
#         第4.150版：結果ボードの 絵（bcp_assets）は 軽く しない（そのままの 写し：まさちゃん 2026/11/11 02:36「結果カスタムボードの動き全部無くして！…その代わり、画質あげて！」。
#           動く 絵の 部品を やめて 止まった 絵 だけに なった ので、もとの 画質＝WebP quality 88・前の 絵 90 の まま 入れる）
#   さわらない もの（そのままの 写し）：
#     ・でこぼこ（法線：tc_n_*・fgN_n・fgN_ns）＝光り方に ひびく
#     ・つや（金属／あらさ：fgN_m・fgN_ms）＝WebP の 圧縮は 色を 2×2 で まとめて ブロックの まだらに なる（kisekae/fig/collect_assets.py）ので 劣化なしの まま
#     ・結果ボードの 絵（bcp_assets：見本・背景・前の 絵）＝第4.150版から もとの 画質の まま
#     ・フィールド・ルーレット・チケット・小物・的中の 絵（pm_*・*_last）・見本の 小さい 絵（fgN_t）・音・形（bin）・json
#   作り直した ものが もとの 97% より 大きい ときは もとを そのまま 使う（how＝keep）
#   第4.151版（まさちゃん 2026/11/11 09:07）：
#     ・形（bin）の 三角の 番号を 詰め直す（how＝idxz・「ア、をお願い！」）：番号が 32bit の 形（フィギュア 8体・神様馬・幻の馬）だけ。
#         番号を「前の 番号との 差」に して 小さい 数は 1バイトで 書く（劣化なし：作った あと もとに もどして 1バイトも ちがわない ことを 確かめる）。
#         入れものの 形（24バイトの 頭＋番号より 前＋番号より 後ろ＋詰めた 番号）は pack_idx・読む 側は tc/tc_horse.js と fig/fig_render.js の unz（もとの 形に もどして から 使う）
#     ・棚の 絵 7まい（how＝shelf・「思い出フィギュアの棚の7個とも画質がかなり悪くなってるから、改善して！」）：
#         棚の 絵は 小さな 島が びっしり ならんだ 絵（UV）なので、ふつうの 圧縮（quality 75・もとの 90 でも）だと 島の さかいで となりの 島の 色が にじんで、
#         暗い 板に 茶色の すじ・柱の ふちの ギザギザが 出る。→ 劣化なしの もと（ios/fig_src/shelf_cN.webp：kisekae/fig/shelf_proj.py が 作る・リポジトリに 入れない）から
#         色を 6bit（64段）に そろえて **劣化なしの WebP** に する（色の 差は 2／255 まで・島の さかいは にじまない）。ios/fig_src が ない ときは もとの 絵（quality 90）の 写し
#   台帳 lite.info（JSON）：{ v, params, files: { 名前: { how（webp・film・copy・keep・idxz・shelf）, p（作る ときの 決めごと：かわったら 作り直す）, src: [大きさ, 更新の 時刻, sha1], size } } }
import hashlib, json, os, re, shutil, subprocess, sys, time
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
sys.path.insert(0, W); import assets_dir as AD
sys.path.insert(0, os.path.join(H, 'bcp')); import bcp_app as B
PARAMS = {'crf': 24, 'preset': 'slow', 'tail': [[30, 23], [20, 22], [10, 21]], 'q': 75, 'method': 6, 'keep': 0.97}      # tail＝[さいごから 何コマ, CRF]（さいごの 1まいに つながる 動画 だけ）
V = 1


def rule(name, f):
    """その ファイルを どう するか：film・webp・copy"""
    if name == 'fx_assets':
        return 'film' if f.endswith('.mp4') else 'copy'
    if name == 'bcp_assets':
        return 'copy'      # 第4.150版（まさちゃん 2026/11/11 02:36「…その代わり、画質あげて！」）：結果ボードの 絵（止まった 絵 だけに なった）は 軽く しない＝もとの 画質（WebP quality 88・前の 絵 90）の まま
    if name == 'tc_assets':
        return 'webp' if re.fullmatch(r'tc_c_.+\.webp', f) else 'idxz' if idx32(name, f) else 'copy'
    if name == 'fig_assets':
        if re.fullmatch(r'fg_shelf_c\d+\.webp', f):
            return 'shelf' if os.path.isfile(shelf_src(f)) else 'copy'
        return 'webp' if re.fullmatch(r'fg\d+_cs?\.webp', f) else 'idxz' if idx32(name, f) else 'copy'
    raise ValueError(name)


def idx32(name, f):
    """三角の 番号が 32bit の 形（bin）か：となりの json（<名前>.json・"bin" で 名前を 指す ものも）を 見る"""
    if not f.endswith('.bin'):
        return False
    m = AD.master(name)
    for j in sorted(os.listdir(m)):
        if j.endswith('.json'):
            try:
                d = json.load(open(os.path.join(m, j), encoding='utf8'))
            except Exception:
                continue
            if isinstance(d, dict) and d.get('idx32') and (d.get('bin') or j[:-5] + '.bin') == f and isinstance(d.get('layout'), dict) and 'idx' in d['layout']:
                return True
    return False


def idx_meta(name, f):
    m = AD.master(name)
    for j in sorted(os.listdir(m)):
        if j.endswith('.json'):
            try:
                d = json.load(open(os.path.join(m, j), encoding='utf8'))
            except Exception:
                continue
            if isinstance(d, dict) and d.get('idx32') and (d.get('bin') or j[:-5] + '.bin') == f:
                return d
    raise ValueError(f)


SHELF_SRC = os.path.join(W, 'ios', 'fig_src')          # 棚の 絵の 劣化なしの もと（shelf_c1〜7.webp）。リポジトリに 入れない（.gitignore）
SHELF_BITS = 6


def shelf_src(f):
    return os.path.join(SHELF_SRC, f[3:])               # fg_shelf_c3.webp → shelf_c3.webp


MAGIC = b'TGIZ'


def pack_idx(raw, off, nb, n):
    """形（bin）の 番号（32bit・n こ・off から nb バイト）を 詰める → 頭（TGIZ・もとの 長さ・番号の 場所・番号の バイト数・番号の 数・詰めた 長さ：どれも 32bit）＋番号より 前＋番号より 後ろ＋詰めた 番号
       詰め方：前の 番号との 差を ジグザグ（0, -1, 1, -2, …）に して、7bit ずつ（小さい 数は 1バイト）"""
    import struct
    import numpy as np
    assert nb == n * 4 and off % 4 == 0 and off + nb <= len(raw), (off, nb, n, len(raw))
    idx = np.frombuffer(raw, np.uint32, n, off).astype(np.int64)
    d = np.diff(idx, prepend=0); z = ((d << 1) ^ (d >> 63)).astype(np.uint64)
    parts = []; zz = z.copy()
    while True:
        b = (zz & 0x7F).astype(np.uint8); zz >>= np.uint64(7); more = zz > 0
        parts.append((b | (more.astype(np.uint8) << 7), more))
        if not more.any():
            break
    lens = np.ones(len(z), np.int64)
    for _b, more in parts[:-1]:
        lens += more
    offs = np.concatenate([[0], np.cumsum(lens)[:-1]]); buf = np.zeros(int(lens.sum()), np.uint8); alive = np.ones(len(z), bool)
    for k, (b, more) in enumerate(parts):
        buf[offs[alive] + k] = b[alive]; alive &= more
    return MAGIC + struct.pack('<5I', len(raw), off, nb, n, len(buf)) + raw[:off] + raw[off + nb:] + buf.tobytes()


def unpack_idx(pk):
    """pack_idx の 逆（読む 側の JS と 同じ 手順）"""
    import struct
    import numpy as np
    if pk[:4] != MAGIC:
        return pk
    L, off, nb, n, pl = struct.unpack('<5I', pk[4:24]); tail = L - off - nb
    assert 24 + off + tail + pl == len(pk) and nb == n * 4, (L, off, nb, n, pl, len(pk))
    st = np.frombuffer(pk, np.uint8, pl, 24 + off + tail)
    ends = np.nonzero(st < 128)[0]; assert len(ends) == n, (len(ends), n)
    starts = np.concatenate([[0], ends[:-1] + 1]); v = np.zeros(n, np.uint64)
    for k in range(int((ends - starts).max()) + 1):
        m = starts + k <= ends
        v[m] |= (st[starts[m] + k].astype(np.uint64) & np.uint64(0x7F)) << np.uint64(7 * k)
    d = (v >> np.uint64(1)).astype(np.int64) ^ -(v & np.uint64(1)).astype(np.int64)
    idx = np.cumsum(d).astype(np.uint32)
    return pk[24:24 + off] + idx.tobytes() + pk[24 + off:24 + off + tail]


def enc_idxz(name, f, src, dst):
    meta = idx_meta(name, f); off, nb = meta['layout']['idx']
    raw = open(src, 'rb').read(); pk = pack_idx(raw, off, nb, meta['i'])
    assert unpack_idx(pk) == raw, f + '：もとに もどらない'
    assert len(pk) < len(raw), (f, len(pk), len(raw))
    tmp = dst + '.tmp'; open(tmp, 'wb').write(pk); os.replace(tmp, dst)


def enc_shelf(f, dst):
    import numpy as np
    from PIL import Image
    im = Image.open(shelf_src(f)); im.load(); assert im.mode == 'RGB' and im.size == (2048, 2048), (f, im.mode, im.size)
    a = np.asarray(im); sh = 8 - SHELF_BITS
    q = np.clip(((a >> sh) << sh) + (1 << sh >> 1), 0, 255).astype(np.uint8)
    assert int(np.abs(q.astype(int) - a).max()) <= (1 << sh) // 2, f
    tmp = dst + '.tmp.webp'; Image.fromarray(q, 'RGB').save(tmp, 'WEBP', lossless=True, quality=100, method=6)
    out = Image.open(tmp); out.load(); assert out.size == im.size and np.array_equal(np.asarray(out.convert('RGB')), q), f + '：劣化なしで ない'
    os.replace(tmp, dst)


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
    """さいごの 1まい（<名前>_last.webp）に つながる 動画か（gk_film.mp4 → gk_last.webp。作り直した 版は 数字つき：sgd_film2.mp4 → sgd_last2.webp〈第4.162版〉）"""
    m = re.fullmatch(r'(.+)_film(\d*)\.mp4', os.path.basename(src))
    return bool(m) and os.path.isfile(os.path.join(os.path.dirname(src), m.group(1) + '_last' + m.group(2) + '.webp'))


# 第4.171版（まさちゃん 2026/11/14 16:18「①的中演出の画質上げる！」）：神様極的中の 3倍の 動画（gk_film2.mp4）は、できた 動画（780×1688）を のばして 作った もの
#   ＝ 新しい 細かさは ない ので、ほかの 動画（CRF 24）より 強めに 圧縮しても 見た目は かわらない（CRF 24＝15.4MB と CRF 27＝10.6MB を 同じ コマで 見くらべて 決めた。
#   前の 2倍の 動画は 7.8MB：りんかくは 前より くっきり）。さいごの 30コマは ほかと 同じく 少しずつ きれいに（さいごは CRF 21：きれいな 1まい絵に つながる）
FILM_P = {'gk_film2.mp4': (27, [[30, 25], [20, 23], [10, 21]])}


def film_p(f):
    """その 動画の 圧縮の 強さ（CRF）と さいごの コマの 決めごと"""
    return FILM_P.get(os.path.basename(f), (PARAMS['crf'], PARAMS['tail']))


def sig(name, f, how):
    """その ファイルを 作る ときの 決めごと（かわったら 作り直す）"""
    if how == 'film':
        crf, tail = film_p(f)
        return f"crf{crf}-{PARAMS['preset']}" + ('-tail' + '/'.join(f'{a}:{b}' for a, b in tail) if has_tail(os.path.join(AD.master(name), f)) else '')
    if how == 'webp':
        return f"q{PARAMS['q']}-m{PARAMS['method']}"
    if how == 'idxz':
        return 'z1'
    if how == 'shelf':
        return f'b{SHELF_BITS}-' + sha1(shelf_src(f))[:12]
    return ''


def enc_film(src, dst):
    tmp = dst + '.tmp.mp4'; a = probe(src); n = int(a['v']['nb_frames']); zones = []; crf, tail = film_p(src)
    if has_tail(src):
        edges = [n - k for k, _c in tail] + [n]
        zones = ['-x264-params', 'zones=' + '/'.join(f'{edges[i]},{edges[i + 1] - 1},crf={c}' for i, (_k, c) in enumerate(tail))]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-map', '0:v:0', '-c:v', 'libx264', '-profile:v', 'high', '-preset', PARAMS['preset'], '-crf', str(crf), *zones,
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
    elif how == 'idxz':
        enc_idxz(name, f, src, dst)
    elif how == 'shelf':
        enc_shelf(f, dst)
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
    print('作る もの：動画', len(films), '・絵', sum(1 for j in rest if j[2] == 'webp'), '・形（番号を 詰める）', sum(1 for j in rest if j[2] == 'idxz'), '・棚の 絵', sum(1 for j in rest if j[2] == 'shelf'), '・写し', sum(1 for j in rest if j[2] == 'copy'), flush=True)
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
