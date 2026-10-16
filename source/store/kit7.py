# App Store掲載キット・ポイント版（claude.aiのアーティファクト）を作る
#   python3 store/kit7.py <フォルダ>   … <フォルダ>/listing7.json（store/listing7.py が作る）と <フォルダ>/media/ を使って <フォルダ>/kit7.html
# 製品ページ（紹介ページ）の並び：いちばん左にプレビュー動画 → 画面写真10枚 → 説明文・App内課金・情報（よその会社のデザインはまねしない・テンゲルの紺と金）
import html, json, os, sys
OUT = sys.argv[1]
L = json.load(open(os.path.join(OUT, 'listing7.json'), encoding='utf-8'))
F = {f['key']: f for f in L['fields']}
IAP = L['iap']
HAS_PREV = os.path.exists(os.path.join(OUT, 'media', 'prev_iphone.mp4'))
esc = lambda s: html.escape(str(s or ''))
SHOTS = ['即判定（1500Pプレゼント）', 'スクショを入れるだけ', 'ゾーンまで判定', '買い目編集', '買う馬を選ぶ', 'Pカスタム', 'マザーデータ', '単勝5連予想', '収支の記録', 'サブスク']


def field(key, label=None, note=None, mono=False):
    f = F[key]; lim = f['limit']; c = f['count']; unit = 'バイト' if f['unit'] == 'bytes' else '文字'
    meter = (f'<div class="meter" aria-label="{c}{unit}（上限{lim}{unit}）"><i style="width:{min(100, c / lim * 100):.1f}%"></i></div>'
             f'<span class="cnt">{c}<small>/{lim}{unit}</small></span>') if lim else ''
    n = note if note is not None else f['note']
    return f'''<article class="fld" id="f-{esc(key)}">
  <header><div><span class="where">{esc(f['sec'])}</span><h3>{esc(label or key)}</h3></div><div class="ctr">{meter}<button class="copy" type="button" data-copy="v-{esc(key)}">コピー</button></div></header>
  <pre class="val{' mono' if mono else ''}" id="v-{esc(key)}">{esc(f['value'])}</pre>
  {f'<p class="note">{esc(n)}</p>' if n else ''}
</article>'''


def answers():
    return ''.join(f'<div class="ans"><h3>{esc(k)}</h3><ul>' + ''.join(f'<li>{esc(v)}</li>' for v in vs) + '</ul></div>' for k, vs in L['answers'].items() if not k.startswith('App内課金') and not k.startswith('サブスクリプション') and k != '先に決めること')


yen = lambda y: f'{y:,}円'
cons_rows = ''.join(f'<tr><td><b>{esc(p["name"])}</b><br><small class="mono">{esc(p["id"])}</small></td><td>消耗型</td><td>{esc(p["desc"])}</td><td class="num">{yen(p["inc"])}<br><small>税抜{yen(p["ex"])}</small></td></tr>' for p in IAP['consumable'])
sub_rows = ''.join(f'<tr><td><b>{esc(s["name"])}</b><br><small class="mono">{esc(s["id"])}</small></td><td>自動更新・1か月<br><small>レベル{s["level"]}</small></td><td>{esc(s["desc"])}</td><td class="num">月額{yen(s["inc"])}<br><small>税抜{yen(s["ex"])}</small></td></tr>' for s in IAP['subs'])
iap_list = ''.join(f'<li><span>{esc(p["name"])}</span><b>{yen(p["inc"])}</b></li>' for p in IAP['consumable']) + ''.join(f'<li><span>{esc(s["name"])}</span><b>{yen(s["inc"])}</b></li>' for s in IAP['subs'])
use_list = ''.join(f'<li><span>{esc(a)}</span><b>{esc(b)}</b></li>' for a, b in IAP['use'])
decide = ''.join(f'<li><span class="st need">決める</span><div>{esc(x)}</div></li>' for x in L['answers']['先に決めること'])
later = ''.join(f'<div class="fld"><header><div><span class="where">あとで</span><h3>{esc(k)}</h3></div><div class="ctr"><button class="copy" type="button" data-copy="later-{i}">コピー</button></div></header><pre class="val" id="later-{i}">{esc(v)}</pre><p class="note">紹介特典をアプリで作って、審査の決まりに合うと確かめてから使ってね。</p></div>' for i, (k, v) in enumerate(L['later'].items()))
M = L['media']
media_rows = ''.join(f'<tr><td class="mono">{esc(m.get("file") or (m["dir"] + "/01〜10.png"))}</td><td class="mono">{esc(m["size"])}</td><td>{esc(m["where"])}</td></tr>' for m in M.values())
HEAD = F['名前']['value'].split('｜')
desc = F['概要']['value']
desc_head = '\n'.join(desc.split('\n')[:3])

hero_media = ('<video id="pv" src="media/prev_iphone.mp4" poster="media/prev_iphone.jpg" autoplay muted loop playsinline></video>' if HAS_PREV
              else '<img id="pv" src="media/ip_01.jpg" alt="1枚目の画面写真：スクショを選ぶだけで即判定・初回ダウンロードで1500Pプレゼント">')
hero_btns = ('<button class="btn" type="button" id="snd" aria-pressed="false">音を出す</button>' if HAS_PREV else '') + \
    '<button class="btn" type="button" data-dev="iphone" aria-pressed="true">iPhone</button><button class="btn" type="button" data-dev="ipad" aria-pressed="false">iPad</button>'
prev_fact = '2本（iPhone 886×1920・iPad 1200×1600・29.5秒）' if HAS_PREV else 'これから作るよ（アプリの画面だけ・29.5秒）'

page = f'''<title>テンゲル 掲載キット（ポイント版）</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&family=Dela+Gothic+One&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>
/* 掲載キット（ポイント版）：App Storeの製品ページの並び（動画→画面写真→説明→App内課金→情報）と、App Store Connect に入れるものを上から順に。
   テンゲルの紺と金（アプリ・CMと同じ世界）。暗い1テーマで決め打ち */
:root{{
  --bg:#0a1024; --panel:#111a38; --panel2:#17224a; --line:#28356a; --ink:#eef1fb; --muted:#9ba7cb; --gold:#e2a23b; --gold2:#ffd45c; --ok:#43d18e; --warn:#ff9a6b; --red:#d6261d;
  --f-disp:"Dela Gothic One","Hiragino Sans","Yu Gothic",sans-serif; --f-body:"BIZ UDPGothic","Hiragino Sans","Yu Gothic UI",Meiryo,sans-serif; --f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  --r:14px; color-scheme:dark;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 var(--f-body);-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1080px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 64px}}
h1,h2,h3{{text-wrap:balance}}
h2{{font-family:var(--f-disp);font-weight:400;font-size:21px;letter-spacing:.04em;margin:0 0 4px;color:var(--gold2)}}
.lead{{margin:0 0 18px;color:var(--muted);font-size:14px}}
section{{margin-top:44px}}
.mono{{font-family:var(--f-mono);font-variant-numeric:tabular-nums}}
.draft{{display:flex;gap:12px;align-items:flex-start;background:rgba(255,154,107,.1);border:1px solid rgba(255,154,107,.45);border-radius:var(--r);padding:12px 14px;margin:0 0 18px;font-size:14px}}
.draft b{{color:var(--warn)}}
.hero{{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:32px;align-items:start;
  background:radial-gradient(ellipse 60% 70% at 18% 30%,rgba(226,162,59,.22),rgba(226,162,59,0) 70%),linear-gradient(160deg,#16224d,#0b1229 70%);
  border:1px solid var(--line);border-radius:22px;padding:24px}}
.shot{{border-radius:22px;overflow:hidden;box-shadow:0 0 0 1.5px rgba(255,214,102,.85),0 0 30px rgba(255,150,0,.35),0 24px 50px rgba(0,0,0,.6);max-width:300px;margin:0 auto;background:#000}}
.shot img,.shot video{{display:block;width:100%;height:auto}}
.vbar{{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:14px}}
.btn{{font:700 13px var(--f-body);color:var(--ink);background:var(--panel2);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}}
.btn[aria-pressed="true"]{{background:var(--gold);border-color:var(--gold);color:#1a1000}}
.btn:focus-visible,.copy:focus-visible,.more:focus-visible{{outline:2px solid var(--gold2);outline-offset:2px}}
.store{{min-width:0}}
.eyebrow{{font:600 11.5px var(--f-mono);letter-spacing:.14em;color:var(--gold);text-transform:uppercase;margin:0}}
.appline{{display:flex;gap:16px;align-items:center;margin:12px 0 10px}}
.appline img{{width:92px;height:92px;border-radius:21px;box-shadow:0 0 0 1px rgba(255,255,255,.12),0 8px 20px rgba(0,0,0,.45);flex:none}}
.appline h1{{font-family:var(--f-disp);font-weight:400;font-size:26px;line-height:1.25;margin:0;letter-spacing:.02em}}
.appline h1 span{{display:block;font-family:var(--f-body);font-weight:700;font-size:15px;opacity:.9;margin-top:2px}}
.appline .sub{{color:var(--muted);font-size:13.5px;margin-top:4px}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 14px}}
.chip{{font-size:12px;padding:3px 10px;border-radius:999px;border:1px solid var(--line);color:var(--muted);background:rgba(255,255,255,.03)}}
.chip.g{{border-color:rgba(226,162,59,.6);color:var(--gold2)}}
.promo{{background:rgba(0,0,0,.22);border:1px solid var(--line);border-radius:12px;padding:12px 14px;font-size:14px;margin:0}}
.facts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:16px 0 0}}
.facts div{{background:rgba(0,0,0,.2);border:1px solid var(--line);border-radius:12px;padding:10px 12px;min-width:0}}
.facts dt{{font:600 11px var(--f-mono);letter-spacing:.1em;color:var(--gold)}}
.facts dd{{margin:2px 0 0;font-size:13.5px}}
/* 並び */
.tabs{{display:flex;gap:8px;margin:0 0 12px;flex-wrap:wrap}}
.strip{{display:flex;gap:12px;overflow-x:auto;padding:4px 2px 14px;scroll-snap-type:x mandatory}}
.strip figure{{margin:0;flex:none;scroll-snap-align:start;position:relative}}
.strip img{{display:block;border-radius:14px;border:1px solid var(--line);height:440px;width:auto;max-width:none}}
.strip.pad img{{height:330px}}
.strip figcaption{{font:600 11px var(--f-mono);color:var(--muted);margin-top:6px;letter-spacing:.04em}}
.strip .play{{position:absolute;left:50%;top:calc(50% - 12px);transform:translate(-50%,-50%);width:54px;height:54px;border-radius:50%;background:rgba(0,0,0,.55);border:2px solid rgba(255,255,255,.85);display:grid;place-items:center}}
.strip .play::after{{content:"";margin-left:5px;border-left:16px solid #fff;border-top:10px solid transparent;border-bottom:10px solid transparent}}
.first{{position:absolute;left:8px;top:8px;font:700 11px var(--f-body);background:var(--gold);color:#1a1000;border-radius:999px;padding:2px 8px}}
/* ページの下のほう（イメージ） */
.below{{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:16px;align-items:start}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;min-width:0}}
.card h3{{margin:0 0 8px;font-size:15px;color:var(--gold2)}}
.desc{{white-space:pre-wrap;word-break:break-word;font-size:14px;line-height:1.8;margin:0}}
.desc.clip{{max-height:7.3em;overflow:hidden;-webkit-mask-image:linear-gradient(180deg,#000 60%,transparent)}}
.more{{font:700 13px var(--f-body);color:var(--gold2);background:none;border:0;padding:6px 0 0;cursor:pointer}}
.kv{{list-style:none;margin:0;padding:0}}
.kv li{{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-bottom:1px solid var(--line);font-size:14px}}
.kv li:last-child{{border-bottom:0}}
.kv b{{font-family:var(--f-mono);font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}}
.kv span{{min-width:0}}
/* コピーして貼る */
.flds{{display:grid;gap:14px}}
.fld{{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;min-width:0}}
.fld header{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
.fld h3{{margin:0;font-size:16px}}
.where{{font:600 11px var(--f-mono);letter-spacing:.08em;color:var(--gold)}}
.ctr{{display:flex;align-items:center;gap:10px}}
.meter{{width:84px;height:6px;border-radius:999px;background:var(--panel2);overflow:hidden;border:1px solid var(--line)}}
.meter i{{display:block;height:100%;background:var(--ok)}}
.cnt{{font:600 13px var(--f-mono);font-variant-numeric:tabular-nums}}
.cnt small{{color:var(--muted);font-weight:500}}
.copy{{font:700 13px var(--f-body);color:#1a1000;background:linear-gradient(180deg,#ffe08a,#e2a23b);border:0;border-radius:9px;padding:7px 14px;cursor:pointer;min-width:84px}}
.copy.done{{background:var(--ok);color:#06210f}}
.val{{margin:10px 0 0;white-space:pre-wrap;word-break:break-word;font:15px/1.8 var(--f-body);background:rgba(0,0,0,.25);border:1px solid var(--line);border-radius:10px;padding:10px 12px;max-height:340px;overflow:auto}}
.val.mono{{font-family:var(--f-mono);font-size:13.5px}}
.note{{margin:8px 0 0;font-size:12.5px;color:var(--muted)}}
/* 答え・表 */
.answers{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
.ans{{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;min-width:0}}
.ans h3{{margin:0 0 6px;font-size:15px;color:var(--gold2)}}
.ans ul{{margin:0;padding-left:1.1em}}
.ans li{{margin:4px 0;font-size:14px}}
.tbl{{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r)}}
table{{border-collapse:collapse;width:100%;font-size:14px;min-width:620px}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font:600 12px var(--f-mono);letter-spacing:.06em;color:var(--muted);background:var(--panel)}}
td.num{{text-align:right;font-family:var(--f-mono);font-variant-numeric:tabular-nums;white-space:nowrap}}
tr:last-child td{{border-bottom:0}}
td small{{color:var(--gold2)}}
.todo{{list-style:none;margin:0;padding:0;display:grid;gap:10px}}
.todo li{{display:grid;grid-template-columns:auto minmax(0,1fr);gap:12px;align-items:start;background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px;font-size:14px}}
.st{{font:700 11.5px var(--f-body);padding:2px 9px;border-radius:999px;white-space:nowrap}}
.st.need{{background:rgba(255,154,107,.16);color:var(--warn);border:1px solid rgba(255,154,107,.5)}}
.st.ok{{background:rgba(67,209,142,.14);color:var(--ok);border:1px solid rgba(67,209,142,.45)}}
.foot{{margin-top:48px;font-size:12.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px}}
.foot a{{color:var(--gold2)}}
#toast{{position:fixed;left:50%;bottom:calc(20px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);background:var(--ok);color:#06210f;font-weight:700;padding:8px 16px;border-radius:999px;font-size:13.5px}}
@media (max-width:760px){{
  .hero{{grid-template-columns:minmax(0,1fr);padding:18px}}
  .answers,.facts,.below{{grid-template-columns:minmax(0,1fr)}}
  .strip img{{height:360px}} .strip.pad img{{height:250px}}
  .appline img{{width:72px;height:72px;border-radius:17px}} .appline h1{{font-size:22px}}
}}
@media (prefers-reduced-motion:reduce){{.strip{{scroll-behavior:auto}}}}
</style>

<div class="wrap">
<div class="draft" role="note"><span class="st need">下書き</span><div><b>ポイントの帯・ロック・購入の画面はイメージ</b>（アプリはこれからFableで作る）。アプリができたら、本物の画面で撮り直してから出してね（審査では、画面写真と説明がアプリそのものと同じか見られるよ）。</div></div>
<section class="hero" aria-label="App Storeの製品ページのいちばん上">
  <div>
    <div class="shot" id="phone">{hero_media}</div>
    <div class="vbar">{hero_btns}</div>
  </div>
  <div class="store">
    <p class="eyebrow">App Store 製品ページ（紹介ページ）</p>
    <div class="appline"><img src="media/icon.png" alt="テンゲルのアイコン"><div><h1>{esc(HEAD[0])}<span>{esc('｜'.join(HEAD[1:]))}</span></h1><div class="sub">{esc(F['サブタイトル']['value'])}</div></div></div>
    <div class="chips"><span class="chip g">スポーツ</span><span class="chip">18+</span><span class="chip">iPhone・iPad</span><span class="chip">日本語</span><span class="chip g">App内課金あり</span><span class="chip g">無料</span></div>
    <p class="promo">{esc(F['プロモーション用テキスト']['value'])}</p>
    <dl class="facts">
      <div><dt>プレビュー動画</dt><dd>{prev_fact}</dd></div>
      <div><dt>画面写真</dt><dd>20枚（iPhone 6.9インチ・iPad 13インチ 各10枚）</dd></div>
      <div><dt>App内課金</dt><dd>ポイント4つ・サブスク3つ（価格は税込）</dd></div>
      <div><dt>貼る文</dt><dd>9つ（名前・説明・キーワード・審査へのメモ など）</dd></div>
    </dl>
  </div>
</section>

<section aria-labelledby="h-strip">
  <h2 id="h-strip">App Storeでの並び</h2>
  <p class="lead">検索結果では最初の3枚まで、ページでは動画のあとに01から順に並ぶよ。1〜3枚目に「スクショを入れるだけで判定」をまとめてあるよ。</p>
  <div class="tabs"><button class="btn" type="button" data-strip="iphone" aria-pressed="true">iPhone（6.9インチ）</button><button class="btn" type="button" data-strip="ipad" aria-pressed="false">iPad（13インチ）</button></div>
  <div class="strip" id="strip"></div>
</section>

<section aria-labelledby="h-below">
  <h2 id="h-below">ページの下のほう</h2>
  <p class="lead">画面写真の下に出る、説明・App内課金・ポイントの使い方。説明は最初の3行だけ見えて、「さらに表示」で全部出るよ。</p>
  <div class="below">
    <div class="card"><h3>説明（最初の3行）</h3><p class="desc clip" id="desc">{esc(desc)}</p><button class="more" type="button" id="more" aria-expanded="false">さらに表示</button></div>
    <div style="display:grid;gap:16px;min-width:0">
      <div class="card"><h3>App内課金（価格は税込）</h3><ul class="kv">{iap_list}</ul></div>
      <div class="card"><h3>ポイントの使い方（初回{IAP['gift']:,}Pプレゼント）</h3><ul class="kv">{use_list}</ul></div>
    </div>
  </div>
</section>

<section aria-labelledby="h-copy">
  <h2 id="h-copy">コピーして貼る文</h2>
  <p class="lead">App Store Connect の同じ名前の欄に、そのまま貼ってね。数字はAppleの上限までの使った量。</p>
  <div class="flds">
    {field('名前')}
    {field('サブタイトル')}
    {field('プロモーション用テキスト')}
    {field('概要')}
    {field('キーワード', mono=True)}
    {field('サポートURL', mono=True)}
    {field('プライバシーポリシーURL', mono=True)}
    {field('著作権')}
    {field('App Reviewへのメモ（英語）')}
    {later}
  </div>
</section>

<section aria-labelledby="h-iap">
  <h2 id="h-iap">App内課金・サブスクの登録</h2>
  <p class="lead">App Store Connect の「App内課金」と「サブスクリプション」に、この通りに登録。製品IDはあとから変えられないので、Fableにも同じIDを使ってもらってね。</p>
  <div class="tbl"><table><thead><tr><th>表示名・製品ID</th><th>種類</th><th>説明（45文字まで）</th><th>価格</th></tr></thead><tbody>{cons_rows}{sub_rows}</tbody></table></div>
  <p class="note">サブスクのグループ名：{esc(IAP['subs_group'])}（レベル1がいちばん上のプラン）。価格はまさちゃんの税抜の値段に消費税10%を足した税込。App Storeで選べる価格に合わせて決めてね。</p>
</section>

<section aria-labelledby="h-ans">
  <h2 id="h-ans">質問への答え</h2>
  <p class="lead">App Store Connect で聞かれる質問。画面の言葉は少しちがうことがあるよ。</p>
  <div class="answers">{answers()}</div>
</section>

<section aria-labelledby="h-todo">
  <h2 id="h-todo">出す前に決めること</h2>
  <ul class="todo">
    {decide}
    <li><span class="st need">撮り直す</span><div>ポイントの画面（帯・ロック・購入）は、Fableでアプリができたら本物の画面で撮り直す。プレビュー動画も同じ。</div></li>
    <li><span class="st need">直す</span><div>プライバシーポリシーと特定商取引法の表記に、ポイント・サブスクのことを書き足す（いまは「追加で支払う機能はありません」になっている）。</div></li>
  </ul>
</section>

<section aria-labelledby="h-media">
  <h2 id="h-media">画像と動画の入れ場所</h2>
  <p class="lead">ファイルはチャットに送ったものを使ってね（このページからは保存できないの）。画面写真は透明なしのPNG・Appleの決まりの大きさで作ってあるよ。</p>
  <div class="tbl"><table><thead><tr><th>ファイル</th><th>大きさ</th><th>入れる場所</th></tr></thead><tbody>{media_rows}</tbody></table></div>
</section>

<p class="foot">画面は架空のレースの例。Appleの決まり：
<a href="https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications" target="_blank" rel="noopener">スクショの仕様</a>・
<a href="https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications" target="_blank" rel="noopener">プレビューの仕様</a>・
<a href="https://developer.apple.com/app-store/review/guidelines/" target="_blank" rel="noopener">審査ガイドライン（3.1 App内課金）</a></p>
</div>
<div id="toast" hidden role="status"></div>

<script>
(() => {{
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
  const toast = msg => {{ const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => {{ t.hidden = true; }}, 1800); }};
  document.addEventListener('click', e => {{
    const b = e.target.closest('.copy'); if (!b) return;
    const el = document.getElementById(b.dataset.copy), text = el.textContent;
    const ok = () => {{ b.textContent = 'コピーした'; b.classList.add('done'); toast('コピーしたよ'); setTimeout(() => {{ b.textContent = 'コピー'; b.classList.remove('done'); }}, 1600); }};
    const sel = () => {{ const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); toast('文字を選んだよ。長押しでコピーしてね'); }};
    try {{ navigator.clipboard.writeText(text).then(ok, sel); }} catch (err) {{ sel(); }}
  }});
  $('#more').addEventListener('click', e => {{ const d = $('#desc'), open = d.classList.toggle('clip'); e.currentTarget.textContent = open ? 'さらに表示' : 'たたむ'; e.currentTarget.setAttribute('aria-expanded', String(!open)); }});
  const HAS_PREV = {'true' if HAS_PREV else 'false'};
  const pv = $('#pv'), ph = $('#phone');
  $$('[data-dev]').forEach(b => b.addEventListener('click', () => {{
    const pad = b.dataset.dev === 'ipad';
    $$('[data-dev]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    ph.style.maxWidth = pad ? '420px' : '300px';
    if (HAS_PREV) {{ pv.src = pad ? 'media/prev_ipad.mp4' : 'media/prev_iphone.mp4'; pv.poster = pad ? 'media/prev_ipad.jpg' : 'media/prev_iphone.jpg'; pv.play().catch(() => {{}}); }}
    else pv.src = pad ? 'media/pad_01.jpg' : 'media/ip_01.jpg';
  }}));
  const snd = $('#snd');
  if (snd) snd.addEventListener('click', e => {{ pv.muted = !pv.muted; e.currentTarget.setAttribute('aria-pressed', String(!pv.muted)); e.currentTarget.textContent = pv.muted ? '音を出す' : '音を消す'; pv.play().catch(() => {{}}); }});
  const NAMES = {json.dumps(SHOTS, ensure_ascii=False)};
  const strip = $('#strip');
  function paint(dev) {{
    const pad = dev === 'ipad', p = pad ? 'pad' : 'ip';
    strip.className = 'strip' + (pad ? ' pad' : '');
    const head = HAS_PREV ? `<figure><img src="media/prev_${{pad ? 'ipad' : 'iphone'}}.jpg" alt="プレビュー動画（最初に出る）"><span class="first">動画（最初）</span><span class="play" aria-hidden="true"></span><figcaption>PREVIEW 29.5s</figcaption></figure>` : '';
    strip.innerHTML = head + NAMES.map((n, i) => `<figure><img src="media/${{p}}_${{String(i + 1).padStart(2, '0')}}.jpg" alt="画面写真${{i + 1}}：${{n}}" loading="lazy"><figcaption>${{String(i + 1).padStart(2, '0')}} ${{n}}</figcaption></figure>`).join('');
  }}
  $$('[data-strip]').forEach(b => b.addEventListener('click', () => {{ $$('[data-strip]').forEach(x => x.setAttribute('aria-pressed', String(x === b))); paint(b.dataset.strip); }}));
  paint('iphone');
}})();
</script>
'''
open(os.path.join(OUT, 'kit7.html'), 'w', encoding='utf-8').write(page)
print('kit7.html', len(page), 'preview' if HAS_PREV else 'no preview yet')
