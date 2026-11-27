"""競馬新聞の 壁紙の 馬券（第4.234版・まさちゃん 2026/11/28 02:44「壁紙の競馬新聞は、馬の絵を消して、2枚目みたいなデザインで、三枚目の馬券入れて！
   馬券の中の数字を15秒起きにランダムに変えて！合計25種類の組み合わせが欲しい」・02:49「数字の前に0を入れないでってこと！」）
   python3 kisekae/flat/news_ticket.py <出す フォルダ>             … 絵 2まい と 置く 場所（news_tk.json）を 作る（見る だけ：台帳は かえない）
   python3 kisekae/flat/news_ticket.py <出す フォルダ> --install   … 作って、ios/kisekae_blobs/<中身の md5>.webp に 置き、台帳（news_blobs.json の paper・tickets）と
                                                                    置く 場所（kisekae/news_tk.json）を 書く。そのあと 止まった 絵（選ぶ 画面の 小さな 絵）を 写して blobs20.json の news に
   もと：ios/wall_src/news_tickets.png（まさちゃんの 絵：馬単と 3連単の 馬券 2まい・すき通し つき 1536×1024）。**読む だけ**（上書きしない・消さない）。
         もとの 絵と できた 絵は リポジトリに 入れない（.gitignore：ios/wall_src/・ios/kisekae_blobs/）。リポジトリに 入るのは 置く 場所（news_tk.json：数 だけ）
   作る もの
     news_paper.webp   … 新聞の 紙と 字（馬なし）＝ flat/news_banner.py の render に 墨なし（いままでの 止まった 絵と 同じ 作り方・同じ 780×320・同じ q88）
     news_tickets.webp … 馬券 2まい：もとの 絵の 中身（すき通しの かげ まで）を CROP で 切りぬいて、置く 大きさ（BOX の pt）の 3倍（＝iPhone の 画面）に
     news_tk.json      … 置く 場所 BOX（壁紙 390×160pt の 中の pt）・数字の 枠 5つ（馬単 1着・2着／3連単 1着・2着・3着：枠の 内がわの 4すみ・BOX の 中の pt）
                         ＝ 黒い 枠の 中の 白い 所を 絵から 見つける（ぴったり 5つ で なければ 止まる）
     news_thumb.webp   … 止まった 絵（選ぶ 画面の タイル・見本の 下の 絵）：本物の ページ（news_wall.inline）を 1組目の 数字で 写した もの（780×320・q88）
   数字は 絵に 描かない：アプリが 字（Kaisei Tokumin 800：競馬新聞の 見出しの 字）で 枠に 書いて、15秒ごとに かえる（news_wall.py・kisekae.js）"""
import hashlib, io, json, os, shutil, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); K = os.path.dirname(HERE); W = os.path.dirname(K)
sys.path.insert(0, HERE); sys.path.insert(0, K)
SRC = os.path.join(W, 'ios', 'wall_src', 'news_tickets.png')
SRC_SHA1, SRC_SIZE = '77c97a1369d4de6928501761d2b87346364c2504', (1536, 1024)
BLOB_DIR = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
FONT = os.path.join(W, 'ios', 'fonts', 'ks', 'KaiseiTokumin-800.woff2')
CROP = (133, 14, 1388, 1018)          # もとの 絵から 切りぬく 所（左・上・右・下）：馬券と かげ（濃さ 8 より 上）が ぜんぶ 入る・1255×1004＝5:4
BOX = (117, 18, 175, 140)             # 壁紙（390×160pt）の 中に 置く 所（左・上・幅・高さ pt）：左の 記事の 行と 右の 印の 表の あいだ（まさちゃんの 見本と 同じ くらいの 大きさ・場所）
SC = 3                                # 絵の 細かさ（pt の 3倍）
FONT_K = 0.92                         # 数字の 大きさ（枠の 高さに 対して：見本と 同じ くらい 枠を うめる・2けたでも 枠に さわらない）


def sha1(p):
    return hashlib.sha1(open(p, 'rb').read()).hexdigest()


def source():
    if not os.path.isfile(SRC): sys.exit('※ もとの 絵が ない：' + SRC)
    if sha1(SRC) != SRC_SHA1: sys.exit('※ もとの 絵が かわって いる（切りぬく 所・枠の 場所を 見直してね）：' + SRC)
    im = Image.open(SRC).convert('RGBA'); assert im.size == SRC_SIZE, im.size
    return im


def cells(im):
    """数字の 枠 5つ：黒い 線（濃い 色・すき通さない 所）の 中の 穴で、4すみの 形・大きさが 枠 くらいの もの。
       もどす：[(左上, 右上, 右下, 左下) …]（もとの 絵の 画素）＝ 馬単の 2つ（上の 馬券）→ 3連単の 3つ（下の 馬券）・それぞれ 左から"""
    a = np.asarray(im).astype(np.float32)
    dark = ((a[..., :3].mean(-1) < 70) & (a[..., 3] > 200)).astype(np.uint8) * 255
    cnts, hier = cv2.findContours(dark, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for i, c in enumerate(cnts):
        if hier[0][i][3] < 0: continue                                   # 穴（線の 内がわ）だけ
        ar = cv2.contourArea(c)
        if not 8000 < ar < 40000: continue
        ap = cv2.approxPolyDP(c, 0.03 * cv2.arcLength(c, True), True).reshape(-1, 2).astype(np.float64)
        if len(ap) != 4: continue
        s = ap.sum(1); d = ap[:, 0] - ap[:, 1]
        tl, br = ap[np.argmin(s)], ap[np.argmax(s)]; tr, bl = ap[np.argmax(d)], ap[np.argmin(d)]
        out.append((tl, tr, br, bl))
    assert len(out) == 5, f'数字の 枠が 5つ で ない：{len(out)}'
    top = sorted([q for q in out if q[0][1] < 500], key=lambda q: q[0][0]); low = sorted([q for q in out if q[0][1] >= 500], key=lambda q: q[0][0])
    assert len(top) == 2 and len(low) == 3, (len(top), len(low))
    return top + low


def layout(im):
    """news_tk.json の 中身：BOX と 枠 5つ（BOX の 中の pt）"""
    x0, y0, x1, y1 = CROP; k = BOX[2] / (x1 - x0)
    assert abs(BOX[3] - (y1 - y0) * k) < 1e-6, '切りぬく 所と 置く 所の 形が ちがう'
    pt = lambda p: [round(float(p[0] - x0) * k, 2), round(float(p[1] - y0) * k, 2)]
    cs = [dict(t='umatan' if n < 2 else 'sanrentan', i=(n if n < 2 else n - 2), quad=[pt(p) for p in q]) for n, q in enumerate(cells(im))]
    return dict(v=1, src=dict(file='ios/wall_src/news_tickets.png', sha1=SRC_SHA1, size=list(SRC_SIZE), crop=list(CROP)), box=list(BOX), scale=SC, font=FONT_K, cells=cs)


def tickets_webp(im):
    x0, y0, x1, y1 = CROP
    c = im.crop(CROP).resize((BOX[2] * SC, BOX[3] * SC), Image.LANCZOS)
    buf = io.BytesIO(); c.save(buf, 'WEBP', quality=90, alpha_quality=100, method=6)
    return buf.getvalue()


def paper_webp():
    import news_banner as NB
    from style2d import save_webp
    p = NB.render(np.zeros((NB.Hh, NB.W), np.float32))
    fd, tmp = tempfile.mkstemp(suffix='.webp'); os.close(fd)
    try:
        save_webp(p, tmp); return open(tmp, 'rb').read()
    finally:
        os.remove(tmp)


def thumb_webp(paper, tickets, tk):
    """本物の ページ（news_wall.inline）を 1組目の 数字で 写す（Chromium・2倍＝780×320）→ WebP q88（いままでの 止まった 絵と 同じ 形）"""
    import news_wall
    from playwright.sync_api import sync_playwright
    d = tempfile.mkdtemp()
    try:
        open(os.path.join(d, 'p.webp'), 'wb').write(paper); open(os.path.join(d, 't.webp'), 'wb').write(tickets); shutil.copy(FONT, os.path.join(d, 'f.woff2'))
        html, css = news_wall.inline({'paper': 'p.webp', 'tickets': 't.webp'}, tk)
        page = ('<!doctype html><meta charset="utf-8"><style>@font-face{font-family:"Kaisei Tokumin";font-weight:800;src:url(f.woff2) format("woff2")}'
                'html,body{margin:0;background:#fff}' + css + '.nsw .nsq{animation:none!important}</style>' + html)
        open(os.path.join(d, 'i.html'), 'w', encoding='utf-8').write(page)
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 160}, device_scale_factor=2)
            pg.goto('file://' + os.path.join(d, 'i.html'))
            pg.wait_for_function("() => document.fonts.status === 'loaded' && [...document.images].every(i => i.complete && i.naturalWidth > 0)")
            assert pg.evaluate("() => document.fonts.check('800 12px \"Kaisei Tokumin\"', '1234567890')")
            png = pg.locator('.nsw').screenshot(); b.close()
        a = np.asarray(Image.open(io.BytesIO(png)).convert('RGB'))
        assert a.shape == (320, 780, 3), a.shape
        ok, buf = cv2.imencode('.webp', cv2.cvtColor(a, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_WEBP_QUALITY, 88]); assert ok
        return buf.tobytes()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def put(data):
    """ios/kisekae_blobs/<中身の md5>.webp（同じ 名前＝同じ 中身が もう あれば 書かない・前の 絵は 消さない）→ id"""
    bid = hashlib.md5(data).hexdigest(); p = os.path.join(BLOB_DIR, bid + '.webp')
    if not os.path.exists(p): open(p, 'wb').write(data)
    assert open(p, 'rb').read() == data
    return bid


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    im = source(); tk = layout(im)
    paper, tickets = paper_webp(), tickets_webp(im)
    thumb = thumb_webp(paper, tickets, tk)
    for fn, data in (('news_paper.webp', paper), ('news_tickets.webp', tickets), ('news_thumb.webp', thumb)):
        open(os.path.join(out, fn), 'wb').write(data)
    json.dump(tk, open(os.path.join(out, 'news_tk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('紙', len(paper), 'B・馬券', len(tickets), 'B・止まった 絵', len(thumb), 'B・枠', [c['quad'][0] for c in tk['cells']])
    if '--install' in sys.argv:
        ids = dict(paper=put(paper), tickets=put(tickets), thumb=put(thumb))
        bp = os.path.join(K, 'news_blobs.json'); nb = json.load(open(bp, encoding='utf-8'))
        nb['paper'], nb['tickets'] = ids['paper'], ids['tickets']
        open(bp, 'w', encoding='utf-8').write(json.dumps(nb, ensure_ascii=False) + '\n')
        json.dump(tk, open(os.path.join(K, 'news_tk.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open(os.path.join(K, 'news_tk.json'), 'a').write('\n')
        p20 = os.path.join(K, 'blobs20.json'); t20 = open(p20, encoding='utf-8').read(); old = json.loads(t20)['news']
        if old != ids['thumb']:
            assert t20.count(f'"news": "{old}"') == 1
            open(p20, 'w', encoding='utf-8').write(t20.replace(f'"news": "{old}"', f'"news": "{ids["thumb"]}"'))
        print('入れた：', ids)
