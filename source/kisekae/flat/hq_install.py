"""走る コマの 高画質の シート（1.5倍＝iPhone の 画面の 3倍）を、手元の 絵の フォルダと 台帳に 入れる
   （第4.156版・まさちゃん 2026/11/12 04:20「Aにして！」：夕焼け・花火・ナイター・競馬新聞・勝負服・水墨画・ネオンの 走る コマを 画面の 3倍に。この 版は 競馬新聞・勝負服・夕焼け）
   python3 flat/hq_install.py news   <hq_news.py の 出した フォルダ>
   python3 flat/hq_install.py silks  <hq_silks.py の 出した フォルダ>
   python3 flat/hq_install.py sunset <hq_sunset.py の 出した フォルダ>
   python3 flat/hq_install.py ink    <hq_ink.py の 出した フォルダ>   （第4.157版：水墨画・ネオン）
   python3 flat/hq_install.py neon   <hq_neon.py の 出した フォルダ>
   python3 flat/hq_install.py fireworks <hq_fireworks.py の 出した フォルダ>   （第4.157版：花火＝馬の 足す光 だけ 別の 絵に。下の「花火」）
   python3 flat/hq_install.py night  <hq_night.py の 出した フォルダ>   （第4.157版：ナイター＝3頭の 走る コマ・止まる／走りだす コマ・表彰の 絵の 9まい。下の「ナイター」）
   ・絵は ios/kisekae_blobs/<中身の md5>.webp に 置く（リポジトリには 入れない）。**前の 絵（2倍）は 消さない・上書きしない**（同じ 名前＝同じ 中身）
   ・台帳（<名前>_blobs.json）の 走る コマの id を 書きかえる。切りぬく 場所の 台帳（<名前>_run.json）に scale＝1.5（絵の 細かさ：cell は 今までどおり 2倍の 画素の 単位）を 足す
   ・ページ（news_wall.py・silks_wall.py・sunset_wall.py）は かえない：シートの 大きさは pt（background-size）で 書いて ある ので、同じ 場所に 1.5倍 細かい 絵が 出る
   ・シートの 大きさ（コマの 数 × cell × 1.5）を 確かめて から 入れる
   花火（走る コマでは なく、光の 粒 8組に 分けた「足す光」）：台帳 fireworks_blobs.json の scatter を「花火 4つ だけ」（前の 絵から 馬の 段を 切り落とした もの：
   画素が 1つも ちがわない のを 確かめる）に、scatter_h（馬 だけ・8組を 横に・1.5倍）を 足す。置く 場所の 台帳（fireworks_layers.json）は かえない。
   ページ（fireworks_wall.py）は scatter_h が あれば 馬の 段 だけ その 絵から 出す
   ナイター：台帳 night_blobs.json の h5・h3・h7（走る）・t5・t3・t7（止まる／立つ／走りだす）・a5・a3・a7（表彰）の id を 書きかえる（コースの 絵 far・track・rail は そのまま）。
   切りぬく 場所の 台帳（night_run.json）は scale＝1.5 を 足す だけ（cell・at・dy は かえない）。ページ（night_wall.py）は かえない（大きさは pt）
   第4.167版（コマを 1/30秒に）の ナイター：flat/hq_night.py が 出した 台帳の かけら（night_new<番号>.json：horses・trans）を night_run.json に 入れて、
   h<番号>＝走る 15コマ（night_h<番号>_hq.webp・1.5倍・ロスなし）・t<番号>＝止まる／走りだす コマ（night_t<番号>_m.webp・1倍・ロスあり）・
   s<番号>＝立つ 絵（night_s<番号>_hq.webp・1.5倍・ロスなし：新しい キー）の id を 書く。表彰の 絵（a<番号>）は 出した フォルダに ある とき だけ 入れかえる"""
import hashlib, json, os, re, sys
from PIL import Image
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOB_DIR = os.environ.get('KISEKAE_ASSETS') or os.path.join(os.path.dirname(K), 'ios', 'kisekae_blobs')
SCALE = 1.5
#        名前      できた 絵                 台帳の キー・id の 前に つく もの・run.json の どこ・絵の 形
SET = {'news': ('news_run_hq.webp', 'run', '', None, 'RGB'),
       'silks': ('silks_run_hq.webp', 'run', '', None, 'RGBA'),
       'sunset': ('sunset_horse_hq.webp', 'horse', '/_blob/', 'horse', 'RGBA'),
       'ink': ('ink_run_hq.webp', 'run', '', None, 'RGB'),                         # 第4.157版：水墨画（flat/hq_ink.py）
       'neon': ('neon_run_hq.webp', 'run', '', None, 'RGBA')}                      # 第4.157版：ネオン（flat/hq_neon.py）


def install(name, out):
    fn, key, pre, sub, mode = SET[name]
    data = open(os.path.join(out, fn), 'rb').read(); bid = hashlib.md5(data).hexdigest()
    bp, rp = os.path.join(K, name + '_blobs.json'), os.path.join(K, name + '_run.json')
    btxt = open(bp, encoding='utf8').read(); blobs = json.loads(btxt); run = json.load(open(rp, encoding='utf8'))
    info = run[sub] if sub else run
    x0, y0, cw, ch = info['cell']; n = info['frames']
    im = Image.open(os.path.join(out, fn))
    assert im.format == 'WEBP' and im.mode == mode and im.size == (int(cw * SCALE) * n, int(ch * SCALE)), (name, im.mode, im.size, (cw, ch, n))
    old = blobs[key]; assert old.startswith(pre) and re.fullmatch(r'[0-9a-f]{32}', old[len(pre):]), old
    dst = os.path.join(BLOB_DIR, bid + '.webp')
    if os.path.exists(dst):
        assert open(dst, 'rb').read() == data, dst
    else:
        open(dst, 'wb').write(data)
    if old[len(pre):] != bid:
        assert btxt.count(old) == 1, (name, old)
        open(bp, 'w', encoding='utf8').write(btxt.replace(old, pre + bid))            # 書き方（字下げ・改行）は そのまま
    if info.get('scale') != SCALE:
        info['scale'] = SCALE
        rtxt = open(rp, encoding='utf8').read()
        open(rp, 'w', encoding='utf8').write(json.dumps(run, ensure_ascii=False, indent=1 if rtxt.startswith('{\n') else None) + ('\n' if rtxt.endswith('\n') else ''))
    print(name, key, old[len(pre):], '→', bid, im.size, len(data), 'bytes', '（前の 絵は のこる：', os.path.exists(os.path.join(BLOB_DIR, old[len(pre):] + '.webp')), '）')
    return bid


def put(data):
    """絵を 手元の フォルダへ（同じ 名前＝同じ 中身。上書きしない）→ id"""
    bid = hashlib.md5(data).hexdigest(); dst = os.path.join(BLOB_DIR, bid + '.webp')
    if os.path.exists(dst):
        assert open(dst, 'rb').read() == data, dst
    else:
        open(dst, 'wb').write(data)
    return bid


def install_fireworks(out, ncls=8):
    import numpy as np
    bp = os.path.join(K, 'fireworks_blobs.json'); blobs = json.load(open(bp, encoding='utf8'))
    lay = json.load(open(os.path.join(K, 'fireworks_layers.json'), encoding='utf8')); sw, sh = lay['sheet']
    hs = [e for e in lay['layers'] if e['kind'] == 'horse']; assert len(hs) == 1 and lay['layers'][-1] is hs[0]
    x, y, w, h = hs[0]['rect']; hy = hs[0]['sheet_y']; assert hy + h == sh
    fh, fb = os.path.join(out, 'fireworks_horse_hq.webp'), os.path.join(out, 'fireworks_bursts.webp')
    dh, db = open(fh, 'rb').read(), open(fb, 'rb').read()
    ih, ib = Image.open(fh), Image.open(fb)
    assert ih.format == 'WEBP' and ih.mode == 'RGB' and ih.size == (int(w * SCALE) * ncls, int(h * SCALE)), (ih.mode, ih.size)
    assert ib.format == 'WEBP' and ib.mode == 'RGB' and ib.size == (sw * ncls, hy), (ib.mode, ib.size)
    assert dh[12:16] == b'VP8L' and db[12:16] == b'VP8L', 'must be lossless（8まい 足す ので）'
    old = blobs['scatter']; assert re.fullmatch(r'[0-9a-f]{32}', old), old
    oldp = os.path.join(BLOB_DIR, old + '.webp')
    if 'scatter_h' not in blobs:                  # はじめて：前の 絵（花火 4つ ＋ 馬）の 上の 段と 1画素も ちがわない
        prev = np.asarray(Image.open(oldp).convert('RGB')); assert prev.shape == (sh, sw * ncls, 3), prev.shape
        assert (np.asarray(ib.convert('RGB')) == prev[:hy]).all(), 'bursts differ from the current sheet'
    blobs['scatter'], blobs['scatter_h'] = put(db), put(dh)
    open(bp, 'w', encoding='utf8').write(json.dumps(blobs, ensure_ascii=False))
    print('fireworks scatter', old, '→', blobs['scatter'], ib.size, len(db), 'bytes ／ scatter_h', blobs['scatter_h'], ih.size, len(dh), 'bytes（前の 絵は のこる：', os.path.exists(oldp), '）')
    return blobs


def install_night(out):
    bp, rp = os.path.join(K, 'night_blobs.json'), os.path.join(K, 'night_run.json')
    blobs = json.load(open(bp, encoding='utf8')); run = json.load(open(rp, encoding='utf8'))
    w, h = run['size']; todo = []
    for n in ('5', '3', '7'):
        new = json.load(open(os.path.join(out, f'night_new{n}.json'), encoding='utf8'))       # hq_night.py が 書いた 台帳の かけら
        run['horses'][n], run['trans'][n] = new['horses'][n], new['trans'][n]
        e, t = run['horses'][n], run['trans'][n]
        assert e['frames'] == 15 and len(e['dy']) == 15 and len(t['frames']) == t['cols'] * t['rows'] and t['stand']['kind'] == 'stand', n
        for key, fn, mode, size, lossless in (
                (f'h{n}', f'night_h{n}_hq.webp', 'RGBA', (int(e['cell'][0] * SCALE) * e['frames'], int(e['cell'][1] * SCALE)), True),
                (f't{n}', f'night_t{n}_m.webp', 'RGBA', (t['cell'][0] * t['cols'], t['cell'][1] * t['rows']), False),
                (f's{n}', f'night_s{n}_hq.webp', 'RGBA', (int(t['cell'][0] * SCALE), int(t['cell'][1] * SCALE)), True),
                (f'a{n}', f'night_award{n}_hq.webp', 'RGB', (int(w * SCALE), int(h * SCALE)), None)):
            if key[0] == 'a' and not os.path.exists(os.path.join(out, fn)):
                continue                                                              # 表彰の 絵は 作り直した とき だけ
            data = open(os.path.join(out, fn), 'rb').read(); im = Image.open(os.path.join(out, fn))
            assert im.format == 'WEBP' and im.mode == mode and im.size == size, (key, im.mode, im.size, size)
            assert lossless is None or (data[12:16] == b'VP8L') == lossless, (key, '走る コマ・立つ 絵は ロスなし／止まる・走りだす コマは ロスあり')
            old = blobs.get(key); assert old is None or re.fullmatch(r'[0-9a-f]{32}', old), old
            todo.append((key, data, old, im.size))
    out_b = {}
    for key, data, old, size in todo:
        out_b[key] = put(data)
        print('night', key, old, '→', out_b[key], size, len(data), 'bytes（前の 絵は のこる：', old is None or os.path.exists(os.path.join(BLOB_DIR, old + '.webp')), '）')
    order = ['far', 'track', 'rail', 'h5', 'h3', 'h7', 't5', 't3', 't7', 's5', 's3', 's7', 'a5', 'a3', 'a7']
    blobs.update(out_b)
    assert set(blobs) == set(order), sorted(blobs)
    open(bp, 'w', encoding='utf8').write('{\n' + ',\n'.join(f' "{k}": "{blobs[k]}"' for k in order) + '\n}\n')      # 書き方（字下げ・改行）は 今までと 同じ
    run['scale'] = SCALE
    json.dump(run, open(rp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return blobs


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'fireworks':
        install_fireworks(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'night':
        install_night(sys.argv[2])
    elif len(sys.argv) != 3 or sys.argv[1] not in SET:
        raise SystemExit(__doc__)
    else:
        install(sys.argv[1], sys.argv[2])
