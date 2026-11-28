# 画像の読み取り（アプリ版・端末の中の文字認識）のテスト用：架空のオッズ画面（いろいろな並び）を作って、写真（JPEG）と「読めた文字と位置」（DOMから。Visionの代わり）を出す
# 出したものは testdata/ocr/ に入れておく（test_ocr_local.js・test_native.py が使う。JPEG は ios/ci/ocr/ にもコピーして、GitHubのMacで本物のVisionで読む）
#   python3 make_mock.py <出力フォルダ> [画面の 名前 …]
import json, os, sys
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
W, H = 390, 844   # iPhone の点（撮るときは3倍）

HORSES = [(1, 'サンライズゴールド', 12.4, '3.0-4.6'), (2, 'テンゲルクイーン', 4.1, '1.6-2.2'), (3, 'ナイトレイン', 31.5, '6.1-9.8'), (4, 'ブルーハーバー', 9.8, '2.6-3.9'),
          (5, 'コスモスカイ', 18.2, '4.0-6.2'), (6, 'ミラクルアロー', 2.4, '1.1-1.3'), (7, 'ハッピーデイズ', 7.6, '2.1-3.1'), (8, 'シルバーウィンド', 54.0, '9.4-15.0'),
          (9, 'ドリームキャッチャー', 25.9, '5.2-8.1'), (10, 'ロイヤルステップ', 6.3, '1.9-2.7'), (11, 'スターダストメモリー', 14.7, '3.3-5.1'), (12, 'ラストサムライ', 88.6, '13.2-21.1')]
WAKU = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 7, 9: 8, 10: 8, 11: 6, 12: 5}
TRI = [('6-2-10', 18.5), ('6-10-2', 24.1), ('2-6-10', 29.0), ('6-2-7', 33.6), ('2-10-6', 41.3), ('6-7-2', 45.8), ('10-6-2', 52.0), ('6-2-4', 55.2), ('2-6-7', 61.9), ('6-10-7', 84.0),
       ('7-6-2', 92.5), ('6-4-2', 101.3), ('2-7-6', 118.0), ('10-2-6', 125.4), ('6-2-1', 140.2)]
CSS = '''<style>*{box-sizing:border-box}body{margin:0;font-family:-apple-system,"Hiragino Sans",sans-serif;background:#fff;color:#111}
.a{font-size:15px}.a .hd{background:#1a3a6e;color:#fff;padding:14px 12px;font-weight:700;font-size:17px}.a .sub{padding:8px 12px;background:#eef2f8;font-size:13px;color:#333}
.a table{width:100%;border-collapse:collapse}.a th{background:#dfe6f0;font-size:12px;padding:8px 4px;text-align:center}.a td{padding:10px 4px;border-bottom:1px solid #ddd;text-align:center;white-space:nowrap}
.a td.n{text-align:left;font-size:13px}.wk{display:inline-block;width:22px;height:22px;line-height:22px;color:#fff;border-radius:3px;font-weight:700}
.w1{background:#fff;color:#000;border:1px solid #999}.w2{background:#000}.w3{background:#d00}.w4{background:#06c}.w5{background:#e6b800;color:#000}.w6{background:#0a0}.w7{background:#f80}.w8{background:#f6a}
.b{font-size:14px}.b .hd{display:flex;justify-content:space-between;padding:12px;background:#222;color:#fff;font-weight:700}.b .meta{padding:8px 12px;font-size:12px;color:#444;background:#f3f3f3}
.b .row{display:grid;grid-template-columns:28px 26px 30px 1fr 52px 76px;align-items:center;padding:9px 8px;border-bottom:1px solid #e3e3e3;font-size:13px}.b .row.h{background:#eee;font-size:11px;color:#555}
.b .row .nm{font-size:12px;overflow:hidden;white-space:nowrap}.b .pop{color:#c00;font-weight:700}
.c{font-size:15px}.c .hd{background:#0d6b3a;color:#fff;padding:14px 12px;font-weight:700}.c .ttl{padding:10px 12px;font-weight:700;border-bottom:2px solid #0d6b3a}
.c .row{display:grid;grid-template-columns:44px 1fr 90px;padding:10px 12px;border-bottom:1px solid #ddd;align-items:center}.c .row.h{font-size:12px;color:#666;background:#f5f5f5}.c .odds{text-align:right;font-weight:700}
.c .cb{letter-spacing:1px}.c.arrow .cb{letter-spacing:0}
.e{font-size:14px}.e .sb{display:flex;justify-content:space-between;align-items:center;height:47px;padding:0 26px 0 34px;font-weight:700;font-size:17px}.e .sb i{font-style:normal;font-size:13px}
.e .hd{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;background:#1a3a6e;color:#fff;font-weight:700;font-size:17px}
.e .soon{background:#d00;color:#fff;font-size:12px;line-height:15px;padding:3px 8px;border-radius:4px;text-align:center}.e .meta{padding:8px 12px;font-size:13px;color:#333;background:#eef2f8}
.e .row{display:grid;grid-template-columns:34px 1fr 60px 84px;align-items:center;padding:9px 10px;border-bottom:1px solid #e3e3e3;font-size:13px}.e .row.h{background:#eee;font-size:11px;color:#555}
.f{font-size:14px}.f .sb{display:flex;justify-content:space-between;align-items:center;height:47px;padding:0 26px 0 34px;font-weight:700;font-size:17px;background:#1d4f9c;color:#fff}.f .sb i{font-style:normal;font-size:13px}
.f .nav{display:flex;align-items:center;gap:14px;padding:12px 10px;border-bottom:1px solid #ccc}.f .pill{border:1px solid #888;border-radius:18px;padding:5px 12px;font-weight:700;font-size:15px}.f .pill s{text-decoration:none;color:#666}
.f .tb{color:#1d4f9c;font-weight:700;font-size:15px;padding:4px 6px}.f .tb.on{border-bottom:3px solid #1d4f9c}
.f .hd{display:flex;gap:14px;padding:14px 12px}.f .big{color:#1d4f9c;font-size:22px;font-weight:700;border-right:3px solid #1d4f9c;padding-right:12px;display:flex;align-items:center}
.f .tx{display:flex;flex-direction:column;gap:4px;font-size:13px}.f .tx b{font-size:15px}.f .meta{padding:8px 12px;font-size:13px;color:#333;background:#eef2f8}.f .ttl{padding:10px 12px;font-weight:700;font-size:16px}
.f .row{display:grid;grid-template-columns:34px 40px 1fr 70px;align-items:center;padding:9px 10px;border-bottom:1px solid #e3e3e3;font-size:13px}.f .row.h{background:#eee;font-size:11px;color:#555}.f .od{text-align:right}
.g{font-size:14px;background:#fff}.g .sb{display:flex;justify-content:space-between;align-items:center;height:47px;padding:0 26px 0 34px;font-weight:700;font-size:17px;background:#0b6b55;color:#fff}.g .sb i{font-style:normal;font-size:13px}
.g .top{display:flex;align-items:center;gap:16px;height:60px;padding:0 14px;background:#0b6b55;color:#fff;font-size:24px}.g .tt{background:linear-gradient(#5bb33a,#2c7a12);color:#fff;text-align:center;font-weight:700;font-size:19px;padding:6px 0}
.g .day{text-align:center;font-size:18px;margin:6px 0 4px}.g .vs{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;padding:0 6px}.g .vs span{border:1px solid #bbb;border-radius:4px;background:#f1f1f1;text-align:center;font-weight:700;font-size:18px;padding:7px 0}
.g .vs span.on{background:#444;color:#fff}.g .lk{text-align:right;color:#2233cc;font-size:15px;padding:8px 6px;word-spacing:14px}
.g .rt{display:grid;grid-template-columns:repeat(6,1fr);gap:3px;padding:0 3px}.g .rt span{border:1px solid #ccc;background:#f1f1f1;text-align:center;font-size:19px;padding:8px 0}.g .rt span.on{background:#333;color:#fff}
.g .kd{border-left:6px solid #3a8a1a;margin:8px 0;padding:6px 10px;font-weight:700;font-size:19px;border-bottom:1px solid #3a8a1a}
.g .rn{background:#f6f3dc;padding:10px 12px;display:flex;align-items:baseline;gap:10px}.g .rn b{font-size:24px}.g .rn span{font-weight:700;font-size:15px}
.g .cd{padding:6px 8px;font-size:15px;line-height:1.45}.g .bt{display:flex;justify-content:flex-end;gap:8px;padding:8px}.g .bt span{background:#2233aa;color:#fff;font-weight:700;padding:6px 18px;border-radius:4px}
.g .row{display:grid;grid-template-columns:30px 30px 1fr;border:1px solid #bbb;font-size:13px}.g .row.h{background:#dcdcb0;font-weight:700;font-size:12px}.g .row div{padding:4px}.g .nm{color:#2233cc;font-size:17px}.g .od{float:right}
.g .nv{display:grid;grid-template-columns:repeat(5,1fr);background:#0b6b55;color:#fff;text-align:center;font-size:12px;font-weight:700;padding:14px 0 26px}
</style>'''


def page_a():
    rows = ''.join(f'<tr><td><span class="wk w{WAKU[n]}">{WAKU[n]}</span></td><td><b>{n}</b></td><td class="n">{nm}</td><td>{t}</td><td>{f}</td></tr>' for n, nm, t, f in HORSES)
    return f'<div class="a"><div class="hd">大井競馬 第9競走</div><div class="sub">ダ1400m　12頭　馬場:良　発走 18:05　10月14日(水)</div>' \
           f'<table><tr><th>枠</th><th>馬番</th><th>馬名</th><th>単勝</th><th>複勝</th></tr>{rows}</table><div class="sub">オッズは締切前のものです</div></div>'


def page_b():
    hs = sorted(HORSES, key=lambda x: x[2])
    rows = ''.join(f'<div class="row"><span class="pop">{i + 1}</span><span class="wk w{WAKU[n]}">{WAKU[n]}</span><span><b>{n}</b></span><span class="nm">{nm}</span><span>{t}</span><span>{f.replace("-", " - ")}</span></div>'
                   for i, (n, nm, t, f) in enumerate(hs))
    rows += '<div class="row"><span class="pop"></span><span class="wk w8">8</span><span><b>13</b></span><span class="nm">ゴールデンメテオ</span><span>取消</span><span>---</span></div>'
    return f'<div class="b"><div class="hd"><span>大井 9R</span><span>単勝・複勝</span></div><div class="meta">2026/10/14　ダート 1,400m　良　13頭（取消1）</div>' \
           f'<div class="row h"><span>人気</span><span>枠</span><span>馬番</span><span>馬名</span><span>単勝</span><span>複勝</span></div>{rows}</div>'


def page_c(arrow=False, rank=True):
    rows = ''.join(f'<div class="row"><span>{(str(i + 1) + "位") if rank else ""}</span><span class="cb">{c.replace("-", "→") if arrow else c}</span><span class="odds">{o}</span></div>' for i, (c, o) in enumerate(TRI))
    return f'<div class="c{" arrow" if arrow else ""}"><div class="hd">大井競馬場 9R　3連単</div><div class="ttl">人気順（オッズの低い順）</div>' \
           f'<div class="row h"><span>順位</span><span>組番</span><span>オッズ</span></div>{rows}</div>'


# 第4.227版：まもなく 締切の 画面（いちばん 上に iPhone の 時計と 電池・見出しの 右に 2段の 札「まもなく／締切」・発走の 時刻と 日付は ない）
#   読めた 文字では：締切済みに しない（soon）・時計を 発走に しない（start は null）。JPEG は GitHubのMacの 本物の Vision でも 読む（ios/ci/selftest.js の ocrsoon）
def page_e():
    rows = ''.join(f'<div class="row"><span><b>{n}</b></span><span class="nm">{nm}</span><span>{t}</span><span>{f}</span></div>' for n, nm, t, f in HORSES)
    return f'<div class="e"><div class="sb"><span>17:58</span><i>5G 87</i></div><div class="hd"><span>大井 9R</span><span class="soon">まもなく<br>締切</span></div>' \
           f'<div class="meta">ダート 1,400m　良　12頭</div><div class="row h"><span>馬番</span><span>馬名</span><span>単勝</span><span>複勝</span></div>{rows}</div>'


# 第4.233版（まさちゃん 11/27 20:20：11R の 画面が 9R に なった）：いちばん 上に 開催場の 札「大井 ⌄」と レースの 切りかえ「8R 9R 10R 11R 12R」（選んで いる 11R は 下線 だけ）・
#   その 下の 見出しに 大きく「11R」と 日付・レース名・発走・距離・頭数。読めた 文字では：11R（切りかえの 並びの 8R・9R に しない）・大井。JPEG は GitHubのMacの 本物の Vision でも 読む（ios/ci/selftest.js の ocrtabs）
def page_f():
    hs = sorted(HORSES, key=lambda x: x[2])
    tabs = ''.join(f'<span class="tb{" on" if r == 11 else ""}">{r}R</span>' for r in range(8, 13))
    rows = ''.join(f'<div class="row"><span>{i + 1}</span><span><b>{n}</b></span><span class="nm">{nm}</span><span class="od">{t}</span></div>' for i, (n, nm, t, f) in enumerate(hs))
    return f'<div class="f"><div class="sb"><span>20:10</span><i>5G 87</i></div><div class="nav"><span class="pill">大井 <s>⌄</s></span>{tabs}</div>' \
           f'<div class="hd"><span class="big">11R</span><span class="tx"><span>2026年10月14日(水)</span><b>テンゲル特別 A1</b><span>発走予定時刻：20:15　ダート1400m　12頭</span></span></div>' \
           f'<div class="meta">天候：晴　馬場状態：良</div><div class="ttl">単勝オッズ</div><div class="row h"><span>人気</span><span>馬番</span><span>馬名</span><span>オッズ</span></div>{rows}</div>'


# 第4.239版（まさちゃん 11/28 15:40：作戦会議で 出馬表の 画面〈日付ごとの 開催場の ボタン・1R〜12R の 切りかえ・「2026年11月28日(土曜) 5回京都7日」・
#   大きく「12R」と「3歳以上 2勝クラス」〉から 開催場と R が 読めない）：その 形の 架空の 画面（馬の 名前は 架空）。
#   g_card＝特別で ない レース（名前は クラス「3歳以上2勝クラス」）・g_card_t＝ほかの 開催場が 選ばれて いる 日（東京）・h_card＝特別の レース（名前「テンゲルステークス」）
def page_g(venue='京都', r=12, band='3歳以上 2勝クラス', cond='(混合)(特指) 定量', course='コース 1200m 芝・右 発走16:15', prize='本賞金(万円):1190、480、300、180、119'):
    btn = lambda vs, on: '<div class="vs">' + ''.join(f'<span class="{"on" if v == on else ""}">{v}</span>' for v in vs) + '</div>'
    tabs = ''.join(f'<span class="{"on" if k == r else ""}">{k}R</span>' for k in range(1, 13))
    hs = [(1, 1, 'サンライズゴールド', '38.7 (15番人気)', '牝4 / 鹿 434kg(0)', '(2,2,3,8)', 'テンゲル太郎(56.0) 星野一郎(栗東)'),
          (1, 2, 'テンゲルクイーン', '2.6 (1番人気)', '牡3 / 鹿 534kg(-2)', '(2,1,1,4)', '月夜次郎(57.0) 花田三郎(栗東)')]
    rows = ''.join(f'<div class="row"><div>{w}</div><div>{n}</div><div><span class="nm">{nm}</span><span class="od">{od}</span><br>{sx}<br>{rc}<br>{jk}</div></div>' for w, n, nm, od, sx, rc, jk in hs)
    return f'<div class="g"><div class="sb"><span>15:34</span><i>4G</i></div><div class="top"><span>←</span><span>出馬表</span></div>' \
           f'<div class="day">11月28日(土曜)</div>{btn(["東京", "京都"], venue)}<div class="day">11月29日(日曜)</div>{btn(["東京", "京都"], None)}' \
           f'<div class="day">11月30日(月曜)</div>{btn(["東京"], None)}<div class="lk">開催選択へ レース選択へ</div><div class="rt">{tabs}</div>' \
           f'<div class="kd">2026年11月28日(土曜) 5回{venue}7日</div><div class="rn"><b>{r}R</b><span>{band}</span></div>' \
           f'<div class="cd">{cond}<br>{course}<br>天候:晴 芝:良<br>{prize}</div><div class="bt"><span>オッズ</span><span>詳細出馬表</span></div>' \
           f'<div class="row h"><div>枠</div><div>馬番</div><div>馬名 / 単勝オッズ(人気)<br>性齢 / 毛色 / 馬体重<br>戦績(1着, 2着, 3着, 4着以下)<br>騎手名(負担重量) / 調教師名</div></div>{rows}' \
           f'<div class="nv"><span>ホーム</span><span>調教・レース</span><span>馬券購入</span><span>レースライブ</span><span>アプリ設定</span></div></div>'


PAGES = {'a_tanfuku_waku': page_a(), 'b_tanfuku_ninki': page_b(), 'c_sanrentan': page_c(), 'd_sanrentan_arrow': page_c(arrow=True, rank=False), 'e_soon': page_e(), 'f_tabs': page_f(),
         'g_card': page_g(), 'g_card_t': page_g('東京', 12, '3歳以上 1勝クラス', '(混合)[指定] 定量', 'コース 2400m 芝・左 発走16:01', '本賞金(万円):820、330、210、120、82'),
         'h_card': page_g('京都', 11, 'テンゲルステークス', '3歳以上 オープン (混合)(特指) 別定', 'コース 1600m 芝・右 発走15:35', '本賞金(万円):2300、920、580、350、230')}
ONLY = sys.argv[2:]      # 第4.227版：作る 画面を しぼる（python3 make_mock.py <出力フォルダ> e_soon）。前の 画面の 見本は 作り直さない
LEAF_JS = '''() => {
  const out = []; const H = document.documentElement.scrollHeight, W = document.documentElement.scrollWidth;
  const walk = n => { for (const c of n.childNodes) { if (c.nodeType === 3) { const t = c.textContent.trim(); if (!t) continue; const r = document.createRange(); r.selectNodeContents(c); const b = r.getBoundingClientRect();
      if (b.width > 0 && b.height > 0) out.push({ text: t, x: (b.left + scrollX) / W, y: (b.top + scrollY) / H, w: b.width / W, h: b.height / H }); } else walk(c); } };
  walk(document.body); return { lines: out, W, H };
}'''
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=3, locale='ja-JP')
    pg = ctx.new_page()
    for name, body in PAGES.items():
        if ONLY and name not in ONLY: continue
        pg.set_content('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">' + CSS + '</head><body>' + body + '</body></html>')
        pg.wait_for_timeout(300)
        d = pg.evaluate(LEAF_JS)
        json.dump(d, open(f'{OUT}/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        pg.screenshot(path=f'{OUT}/{name}.jpg', full_page=True, type='jpeg', quality=85)
        print(name, len(d['lines']), d['W'], d['H'], os.path.getsize(f'{OUT}/{name}.jpg') // 1024, 'KB')
    b.close()
