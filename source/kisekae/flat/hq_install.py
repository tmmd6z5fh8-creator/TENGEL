"""走る コマの 高画質の シート（1.5倍＝iPhone の 画面の 3倍）を、手元の 絵の フォルダと 台帳に 入れる
   （第4.156版・まさちゃん 2026/11/12 04:20「Aにして！」：夕焼け・花火・ナイター・競馬新聞・勝負服・水墨画・ネオンの 走る コマを 画面の 3倍に。この 版は 競馬新聞・勝負服・夕焼け）
   python3 flat/hq_install.py news   <hq_news.py の 出した フォルダ>
   python3 flat/hq_install.py silks  <hq_silks.py の 出した フォルダ>
   python3 flat/hq_install.py sunset <hq_sunset.py の 出した フォルダ>
   ・絵は ios/kisekae_blobs/<中身の md5>.webp に 置く（リポジトリには 入れない）。**前の 絵（2倍）は 消さない・上書きしない**（同じ 名前＝同じ 中身）
   ・台帳（<名前>_blobs.json）の 走る コマの id を 書きかえる。切りぬく 場所の 台帳（<名前>_run.json）に scale＝1.5（絵の 細かさ：cell は 今までどおり 2倍の 画素の 単位）を 足す
   ・ページ（news_wall.py・silks_wall.py・sunset_wall.py）は かえない：シートの 大きさは pt（background-size）で 書いて ある ので、同じ 場所に 1.5倍 細かい 絵が 出る
   ・シートの 大きさ（コマの 数 × cell × 1.5）を 確かめて から 入れる"""
import hashlib, json, os, re, sys
from PIL import Image
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOB_DIR = os.environ.get('KISEKAE_ASSETS') or os.path.join(os.path.dirname(K), 'ios', 'kisekae_blobs')
SCALE = 1.5
#        名前      できた 絵                 台帳の キー・id の 前に つく もの・run.json の どこ・絵の 形
SET = {'news': ('news_run_hq.webp', 'run', '', None, 'RGB'),
       'silks': ('silks_run_hq.webp', 'run', '', None, 'RGBA'),
       'sunset': ('sunset_horse_hq.webp', 'horse', '/_blob/', 'horse', 'RGBA')}


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


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in SET:
        raise SystemExit(__doc__)
    install(sys.argv[1], sys.argv[2])
