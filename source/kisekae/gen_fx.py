"""的中ボタン・デカ的中ボタン・フリーズ的中ボタン（デフォルト）・隠れど的中・ハズレの見本の画面：
   Fx_Hit.dc.html・Fx_Big.dc.html・Fx_Freeze.dc.html・Fx_Hidden.dc.html・Fx_Miss.dc.html ＋ 結果のボード26テーマの一覧 Fx_Boards.dc.html
   python3 gen_fx.py fx_blobs.json
   fx_blobs.json：フリーズの絵（fz_ncore・fz_nglow＝テンゲルのアイコンから作ったネオンの線画のマスク。T1 の背景）
   ＋メモの静止画（s_…。そろっていればメモ Fx_Memo.dc.html も作る）
   ＋効果音（snd_hit_push・snd_hit・snd_big_push・snd_big・snd_fz_push・snd_fz。gen_sfx.py の音。あれば見本の画面で鳴らして、
     同じフォルダの sfx_wave.json と合わせて効果音のメモ Fx_Sound.dc.html も作る）
   流れ：記録する → PUSHボタン（上下に動く）→ タップ → 壁紙のテーマのボードが出る（当たった買い目。ボードは boards.py・馬は出さない）
   フリーズ（3連単の当たりに超大穴＝10〜12番人気の馬）：虹色にギラギラ光るめちゃくちゃデカいPUSH → タップした瞬間にパチスロのフリーズのように
   白く光って横に流れるノイズ → 青い画面に白い光と細い電気 → 青白い横一本線に1pxの電気（プチュン）→ 点に縮んで消える → 真っ暗（1.5秒）
   → 虹色ネオンのカット（どてき！！・ど！・ど的中！！！！）→ 虹色の大当たりの画面に「ど的中」とボード
   カットの文字と結果の「ど的中」は筆の字（brush.py で描いた形 brush_glyphs.json・フォントなし）：虹色・金と黒のふち・金の立体・つや
   隠れど的中（デカ的中の2〜7回に1回・ランダム）：デカ的中のPUSH → タップでそのまま、ど的中の演出 → 見出し「隠れど的中！！！」のボード
   ハズレ：記録する → ボタンなしでボードだけ（静かに出る・音なし）"""
import os, re, sys, json, random, math
from urllib.parse import quote
from gen_screens import SVG_A
from boards import board_css, board_html, font_links as theme_fonts, ORDERED, BY_ID, CAT_ORDER
from themes20 import CATS

K = os.path.dirname(os.path.abspath(__file__))
P = f'{K}/canvas/project' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock'
blobs = json.load(open(sys.argv[1]))
RANCH = open(f'{P}/Judge_Ranch.dc.html', encoding='utf-8').read()
RANCH_VARS = re.search(r'^\.ph\{(--bg:[^}]*)\}', RANCH, re.M).group(1)
BANNER = re.search(r'<img class="bnr" src="(/_blob/[0-9a-f]{32})"', RANCH).group(1)

# 見本の画面のテーマ（牧場）。結果のボードは壁紙のテーマごと（boards.py。26テーマの一覧は Fx_Boards）
THEME = 'ranch'

# 馬番の枠の色（12頭のレース）
WAKU = {1: 'w1', 2: 'w2', 3: 'w3', 4: 'w3', 5: 'w4', 6: 'w4', 7: 'w5', 8: 'w5', 9: 'w6', 10: 'w6', 11: 'w7', 12: 'w8'}
WAKU = {6: 'w5', 2: 'w2', 10: 'w7', 7: 'w6', 1: 'w1', 4: 'w4', 11: 'w8'}   # 判定画面の見本と同じ色に合わせる


def num(n, extra=''):
    return f'<span class="n {WAKU.get(n, "w1")}{extra}">{n}</span>'


def combo(nums, sep, mark=()):
    s = f'<span class="ar">{sep}</span>'
    return s.join(num(x, ' zx' if x in mark else '') for x in nums)


CONF_COLS_HIT = ['#E8382F', '#F3C316', '#3E7B1E', '#1F5FC9', '#F27BB0', '#FFFFFF', '#F08A1C']


def confetti(n, seed, rainbow=False, d0=0.0):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(2, 98)
        d = d0 + rnd.uniform(0, 2.2)
        t = rnd.uniform(2.4, 4.2)
        w = rnd.uniform(6, 10)
        h = rnd.uniform(10, 16)
        r = rnd.choice([-1, 1]) * rnd.uniform(360, 900)
        c = f'hsl({int(i * 360 / n)},95%,62%)' if rainbow else rnd.choice(CONF_COLS_HIT)
        out.append(f'<i style="--x:{x:.1f}%;--d:{d:.2f}s;--t:{t:.2f}s;--w:{w:.0f}px;--h:{h:.0f}px;--r:{r:.0f}deg;--c:{c}"></i>')
    return ''.join(out)


def sparkles(n, seed, white=False):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(4, 96); y = rnd.uniform(6, 92)
        s = rnd.uniform(10, 26); d = rnd.uniform(0, 1.6)
        c = rnd.randint(0, 359)
        col = '#FFFFFF' if white else f'hsl({c},100%,75%)'
        out.append(f'<b style="--x:{x:.1f}%;--y:{y:.1f}%;--s:{s:.0f}px;--d:{d:.2f}s;--c:{col}"></b>')
    return ''.join(out)


def coins(n, seed, d0=0.0):
    """金のコイン（くるくる回りながら落ちる）"""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(3, 97); d = d0 + rnd.uniform(0, 2.0); t = rnd.uniform(2.2, 3.6); w = rnd.uniform(12, 19)
        out.append(f'<i class="cn" style="--x:{x:.1f}%;--d:{d:.2f}s;--t:{t:.2f}s;--w:{w:.0f}px"></i>')
    return ''.join(out)


def burst(x, y, d, s, c1, c2, seed, n=12, ring=True, star=True, z=None, dist=(.55, 1.0)):
    """爆発の光：ギザギザの星形の光（.bs1）・衝撃の輪（.bw）・飛び散る光の破片 n こ。(x, y)＝まん中・d＝秒・s＝大きさ・c1/c2＝光の色"""
    rnd = random.Random(seed)
    pts = []
    for i in range(32):
        a = math.pi * 2 * i / 32 + rnd.uniform(-.05, .05)
        r = rnd.uniform(40, 50) if i % 2 == 0 else rnd.uniform(14, 22)
        pts.append(f'{50 + r * math.sin(a):.1f}% {50 - r * math.cos(a):.1f}%')
    deb = ''
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-.3, .3)) / n
        dd = s * rnd.uniform(*dist)
        deb += (f'<i style="--dx:{math.cos(a) * dd:.0f}px;--dy:{math.sin(a) * dd:.0f}px;--r:{math.degrees(a):.0f}deg;'
                f'--t:{rnd.uniform(.38, .6):.2f}s;--c:hsl({rnd.randint(0, 359)},100%,{rnd.randint(60, 75)}%)"></i>')
    zs = f'z-index:{z};' if z is not None else ''
    st = f'<b class="bs1" style="clip-path:polygon({",".join(pts)})"></b>' if star else ''
    rg = '<b class="bw"></b>' if ring else ''
    return f'<i class="bx" style="{zs}--x:{x:g}px;--y:{y:g}px;--d:{fz_sec(d)};--s:{s:g}px;--c1:{c1};--c2:{c2}" aria-hidden="true">{st}{rg}{deb}</i>'


BURST_CSS = r'''
/* 爆発の光（文字やボードが出るとき）：ギザギザの星形の光がはじけて消える・衝撃の輪・飛び散る光の破片。小さな範囲で1回だけ光る（画面全体は光らせない） */
.bx{position:absolute;left:var(--x);top:var(--y);width:0;height:0;pointer-events:none}
.bx .bs1{position:absolute;left:calc(var(--s) / -2);top:calc(var(--s) / -2);width:var(--s);height:var(--s);
  background:radial-gradient(circle,#FFFFFF 0 7%,var(--c1) 20%,var(--c2) 44%,rgba(0,0,0,0) 68%);opacity:0;animation:bxS .36s cubic-bezier(.1,.8,.3,1) var(--d) forwards}
@keyframes bxS{0%{opacity:1;transform:scale(.12)}45%{opacity:1}100%{opacity:0;transform:scale(1.2)}}
.bx .bw{position:absolute;left:calc(var(--s) * -.35);top:calc(var(--s) * -.35);width:calc(var(--s) * .7);height:calc(var(--s) * .7);border-radius:50%;
  border:6px solid var(--c1);box-shadow:0 0 14px var(--c1),inset 0 0 10px var(--c1);opacity:0;animation:bxW .42s ease-out var(--d) forwards}
@keyframes bxW{0%{opacity:1;transform:scale(.2)}100%{opacity:0;transform:scale(2)}}
.bx > i{position:absolute;left:-7px;top:-2px;width:14px;height:4px;border-radius:2px;background:var(--c);box-shadow:0 0 6px var(--c);
  opacity:0;animation:bxD var(--t) cubic-bezier(.12,.7,.3,1) var(--d) forwards}
@keyframes bxD{0%{opacity:1;transform:translate(0,0) rotate(var(--r)) scaleX(2.2)}100%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--r)) scaleX(.5)}}
@media (prefers-reduced-motion:reduce){.bx{display:none}}
'''


COMMON_CSS = r'''body{margin:0}
*{box-sizing:border-box}
.ph{RANCH}
.ph{--pushA:#E8382F;--pushB:#A51A12;--pushC:#FF9A8A;--rim:#F6E7B8;--rimD:#B98A3A;--bFrame:#8A5A2B;--bFace:#FFFDF5;--bInk:#3A2414;--hitRed:#E8382F;--ray:rgba(255,236,170,.55);
  --pushFace:radial-gradient(72% 40% at 50% 14%,rgba(255,255,255,.9),rgba(255,255,255,.3) 58%,rgba(255,255,255,0) 100%),linear-gradient(180deg,var(--pushC) 0%,var(--pushA) 40%,var(--pushB) 86%,#5E0A05 100%)}
.ph{width:390px;height:844px;position:relative;overflow:hidden;display:flex;flex-direction:column;background-color:var(--bg);background-image:radial-gradient(#E1EFC4 1.6px,transparent 2px);background-size:18px 18px;color:var(--ink);font-family:var(--font),sans-serif;-webkit-font-smoothing:antialiased}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.hd{position:relative;z-index:2;flex:none;padding:10px 16px 12px;background:var(--hd);color:var(--hdInk);border-bottom:4px solid #A8743F}
.hd-r1{display:flex;align-items:center;justify-content:space-between;height:42px}
.logo{display:flex;align-items:center;font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:26px;line-height:1;color:var(--logo);text-shadow:var(--logoS)}
.iii{display:inline-flex;gap:3px;margin-left:6px}
.iii i{display:block;width:5.5px;height:21px;background:var(--iii);border:var(--iiiB);border-radius:var(--iiiR)}
.mbtn{display:inline-flex;align-items:center;gap:6px;height:38px;padding:0 15px;border-radius:999px;border:1.5px solid var(--mLine);background:var(--mBg);color:var(--mInk);font-family:var(--font),sans-serif;font-weight:700;font-size:14px;cursor:pointer}
.mbtn svg{width:18px;height:18px}
.bnr{flex:none;display:block;width:390px;height:120px;object-fit:cover;object-position:50% 70%}
.ct{flex:1;min-height:0;overflow:hidden;padding:14px 14px 0}
.card{position:relative;background:var(--card);border:var(--cardB);border-radius:var(--radius);box-shadow:var(--cardS);padding:14px}
.ch{margin:0 0 10px;font-size:13px;font-weight:700;color:var(--sub)}
.rh{display:flex;align-items:baseline;gap:10px}
.rk{font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:22px;color:var(--ink)}
.rs{font-size:12px;color:var(--sub)}
.lab{margin:12px 0 6px;font-size:12px;font-weight:700;color:var(--sub)}
.fin{display:flex;align-items:center;gap:8px}
.fin span.k{font-size:12px;font-weight:700;color:var(--sub)}
.n{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:30px;padding:0 6px;border-radius:var(--nR);font:700 15px/1 "BIZ UDPGothic",sans-serif}
.w1{background:#FFFFFF;color:#1F1F1F;border:1.5px solid #9AA0A6}
.w2{background:#222222;color:#FFFFFF}
.w4{background:#1F5FC9;color:#FFFFFF}
.w5{background:#F3C316;color:#1F1F1F}
.w6{background:#1E8E3E;color:#FFFFFF}
.w7{background:#F08A1C;color:#1F1F1F}
.ar{color:var(--sub);font-weight:700;padding:0 2px}
.bets{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.bets li{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:var(--rs);background:var(--zBg);border:var(--zB)}
.bt{flex:none;min-width:46px;height:24px;padding:0 8px;border-radius:999px;background:var(--znBg);color:var(--znInk);font-size:12px;font-weight:800;display:inline-flex;align-items:center;justify-content:center}
.bc{display:flex;align-items:center;gap:3px;flex:1}
.bc .n{min-width:26px;height:26px;font-size:13px}
.by{font-size:12.5px;font-weight:700;color:var(--ink)}
.pay{display:flex;align-items:center;justify-content:space-between;margin-top:10px;padding:10px 12px;border-radius:var(--rs);border:1.5px dashed var(--tagLine);font-size:13px;font-weight:700;color:var(--ink)}
.pay b{font-size:17px}
.rec{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:50px;margin-top:14px;border:0;border-radius:var(--btnR);background:var(--btn);color:var(--btnInk);box-shadow:var(--btnS);font-family:var(--font),sans-serif;font-weight:800;font-size:17px;cursor:pointer}
.rec svg{width:20px;height:20px}
.note{margin:10px 2px 0;font-size:11.5px;line-height:1.5;color:var(--sub)}
/* ---------- 重ねる画面 ---------- */
.ov{position:absolute;inset:0;z-index:20;display:flex;align-items:center;justify-content:center;overflow:hidden}
.dim{position:absolute;inset:0;background:rgba(24,14,4,.62);animation:fadeIn .25s ease-out both}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
/* PUSHボタン（横長の長方形・角は丸い） */
.pbox{position:relative;display:flex;flex-direction:column;align-items:center}
.push{--pr:26px;position:relative;z-index:2;width:200px;height:100px;border-radius:var(--pr);border:0;padding:0;cursor:pointer;background:var(--pushFace);
  box-shadow:inset 0 -9px 0 rgba(0,0,0,.2),inset 0 2px 0 rgba(255,255,255,.55),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #6E4E1A,0 22px 34px rgba(0,0,0,.5);
  animation:bob .9s ease-in-out infinite,popIn .35s cubic-bezier(.2,1.6,.4,1) both}
.push span{position:relative;font:400 40px/1 "Dela Gothic One",sans-serif;color:#FFFFFF;letter-spacing:.04em;text-shadow:0 3px 0 var(--pushB),0 0 14px rgba(255,255,255,.55)}
.push::after{content:"";position:absolute;inset:-18px;border-radius:calc(var(--pr) + 18px);border:3px solid rgba(255,232,150,.95);animation:ring 1.2s ease-out infinite}
.pshadow{width:200px;height:22px;margin-top:22px;border-radius:50%;background:rgba(0,0,0,.45);filter:blur(4px);animation:shad .9s ease-in-out infinite}
.tap{margin:16px 0 0;font:400 20px/1 "Dela Gothic One",sans-serif;color:#FFF3C8;letter-spacing:.1em;animation:blink 1s steps(2) infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-18px)}}
@keyframes shad{0%,100%{transform:scale(1);opacity:.55}50%{transform:scale(.72);opacity:.3}}
@keyframes ring{0%{transform:scale(.88);opacity:.95}100%{transform:scale(1.4);opacity:0}}
@keyframes popIn{from{scale:.2}to{scale:1}}
@keyframes blink{0%{opacity:1}100%{opacity:.35}}
@keyframes raysIn{from{opacity:0;scale:.3}to{opacity:1;scale:1}}
@keyframes spin{to{rotate:360deg}}
@keyframes pop{0%{transform:scale(0)}100%{transform:scale(1)}}
@keyframes rowIn{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
/* 買い目の行は0.15秒おき（--i＝何行目か）。合計と「とじる」は最後の行のあと（--n＝行の数。3行より少なくても3行ぶん待つ） */
.ov .brows li{animation:rowIn .35s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .15s)}
.ov .btot{animation:rowIn .35s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .15s)}
.ov .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .15s + var(--tc))}
/* 押したあと（PUSHがあった所から光ってはじける） */
.pressed{position:absolute;z-index:3;left:50%;top:calc(50% - 40px);width:200px;height:100px;margin:-50px 0 0 -100px;border-radius:26px;background:var(--pushFace);
  box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD);animation:press .45s ease-in both}
@keyframes press{0%{transform:scale(1)}35%{transform:scale(.82);filter:brightness(1.4)}100%{transform:scale(1.9);opacity:0;filter:brightness(3)}}
/* 結果のボード（壁紙のテーマのボード・boards.py）を入れる箱：この箱が動く（下から出る・落ちてくる・炎の中からドン）。馬は出さない */
.hb{position:absolute;z-index:6;left:50%;top:196px;width:350px;margin-left:-175px}
.close{position:absolute;z-index:8;left:50%;bottom:64px;transform:translateX(-50%);height:46px;padding:0 34px;border-radius:999px;border:2px solid rgba(255,255,255,.85);background:rgba(0,0,0,.35);color:#FFFFFF;font-family:var(--font),sans-serif;font-weight:800;font-size:15px;cursor:pointer;animation:fadeUp .4s ease-out both}
@keyframes fadeUp{from{opacity:0;transform:translate(-50%,12px)}to{opacity:1;transform:translate(-50%,0)}}
/* 紙ふぶき */
.conf{position:absolute;inset:0;z-index:7;pointer-events:none}
.conf i{position:absolute;left:var(--x);top:-30px;width:var(--w);height:var(--h);background:var(--c);border-radius:2px;opacity:0;animation:fall var(--t) linear var(--d) infinite}
@keyframes fall{0%{opacity:1;transform:translateY(0) rotate(0)}85%{opacity:1}100%{opacity:0;transform:translateY(900px) rotate(var(--r))}}
/* 視差効果を減らす：上下・回転・広がる光・紙ふぶきを止めて、ボードはふわっと出す */
@media (prefers-reduced-motion:reduce){.push,.pshadow,.push::after,.halo b,.tap,.conf i,.rays,.rbow,.ring,.glow,.spk b{animation:none!important}.conf,.pressed,.push::after{display:none}.hb{animation:fadeIn .5s ease-out .2s both!important}}
'''

HIT_CSS = r'''
/* ---------- 的中：あたたかい光 → ボードが下から出る ---------- */
.rays{position:absolute;z-index:4;left:50%;top:44%;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;
  background:repeating-conic-gradient(var(--ray) 0 7deg,transparent 7deg 18deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);
  animation:raysIn .6s ease-out .2s both,spin 22s linear infinite}
.hit .hb{animation:riseUp .7s cubic-bezier(.2,1.35,.4,1) .3s both}
@keyframes riseUp{from{transform:translateY(720px)}to{transform:translateY(0)}}
.hit .bh{animation:pop .5s cubic-bezier(.2,1.8,.4,1) .95s both}
.hit{--t0:1.15s;--tc:.2s}
'''

MISS_CSS = r'''
/* ---------- ハズレ：ボタンなし。記録したら、暗い幕とテーマのボードが静かに出る（光・紙ふぶき・音なし） ---------- */
.miss .hb{animation:missIn .4s cubic-bezier(.2,.8,.3,1) .1s both}
@keyframes missIn{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
.ov.miss{--t0:.45s;--tc:.15s}
.ov.miss .brows li{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .08s)}
.ov.miss .btot{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s)}
.ov.miss .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s + var(--tc))}
'''

BIG_CSS = r'''
/* ---------- デカ的中：大きいPUSH・虹色に光る ---------- */
.ov.big .dim{background:radial-gradient(circle at 50% 46%,rgba(60,30,90,.55),rgba(6,4,18,.86) 70%)}
/* 押したあとの画面（.rv）は、PUSHの画面と同じ暗さのまま始める（暗さがいったん消えてまた暗くなると、白い光の前にもう1回光ってしまう） */
.ov.rv .dim{animation:none}
.push.big{--pr:36px;width:280px;height:140px;animation:bobBig .8s ease-in-out infinite,popIn .4s cubic-bezier(.2,1.6,.4,1) both}
.push.big span{font-size:56px}
/* 虹の輪：形はボタンと同じ横長のまま、色だけがぐるぐる回る */
.halo{position:absolute;inset:-30px;z-index:-1;border-radius:calc(var(--pr) + 30px);filter:drop-shadow(0 0 8px rgba(255,255,255,.85));pointer-events:none}
.halo i{position:absolute;inset:0;border-radius:inherit;padding:10px;overflow:hidden;
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
.halo b{position:absolute;left:50%;top:50%;width:440px;height:440px;margin:-220px 0 0 -220px;
  background:conic-gradient(#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);animation:spin 1.4s linear infinite}
.push.big::after{inset:-44px;border-radius:calc(var(--pr) + 44px);border:4px solid transparent;background:conic-gradient(#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3B3B) border-box;
  -webkit-mask:linear-gradient(#000 0 0) padding-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:ring 1s ease-out infinite}
.pshadow.big{width:280px;margin-top:30px;animation:shadBig .8s ease-in-out infinite}
.tap.big{font-size:26px;background:linear-gradient(90deg,#FF5A5A,#FFD93B,#5BE38A,#4FD3FF,#B07CFF,#FF5A5A);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:rbowText 1.6s linear infinite}
@keyframes bobBig{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-26px) scale(1.04)}}
@keyframes shadBig{0%,100%{transform:scale(1);opacity:.6}50%{transform:scale(.68);opacity:.28}}
@keyframes rbowText{to{background-position:200% 0}}
.spk{position:absolute;inset:0;z-index:1;pointer-events:none}
.spk b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);background:var(--c);
  clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%);animation:twinkle 1.6s ease-in-out var(--d) infinite;opacity:0}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(.3) rotate(0)}50%{opacity:1;transform:scale(1) rotate(45deg)}}
.pressed.big{top:calc(50% - 47px);width:280px;height:140px;margin:-70px 0 0 -140px;border-radius:36px}
/* 押したあと（パチンコの当たりのように速く・勢いよく）：はじける → 0.04秒 白く光る・爆発・虹の光の筋 → 虹の輪3つ（0.1・0.25・0.4秒）
   → 0.38秒 ボードがドンと落ちてくる（0.55秒に着地・爆発）→ 0.7秒「デカ的中!!」→ 0.9秒〜 買い目（0.08秒おき）→ 1.4秒 とじる */
.pressed.big{animation:press .28s ease-in both}
.flash{position:absolute;inset:0;z-index:9;background:#FFFFFF;pointer-events:none;animation:flash .5s ease-out .04s both}
@keyframes flash{0%{opacity:0}12%{opacity:1}100%{opacity:0}}
.rbow{position:absolute;z-index:3;left:50%;top:44%;width:1100px;height:1100px;margin:-550px 0 0 -550px;border-radius:50%;
  background:conic-gradient(#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);
  -webkit-mask-image:repeating-conic-gradient(#000 0 6deg,transparent 6deg 15deg),radial-gradient(circle,#000 0 10%,transparent 60%);
  -webkit-mask-composite:source-in;mask-image:repeating-conic-gradient(#000 0 6deg,transparent 6deg 15deg),radial-gradient(circle,#000 0 10%,transparent 60%);mask-composite:intersect;
  opacity:.85;animation:raysIn .25s cubic-bezier(.2,.9,.3,1) .04s both,spin 30s linear infinite}
.glow{position:absolute;z-index:4;left:50%;top:44%;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 22%,rgba(255,248,214,.9) 34%,rgba(255,230,160,.45) 52%,transparent 70%);
  animation:wrap .55s ease-out .04s both,breathe 2.4s ease-in-out .6s infinite}
@keyframes wrap{0%{scale:.1;opacity:0}60%{scale:1.3;opacity:1}100%{scale:1.15;opacity:.95}}
@keyframes breathe{0%,100%{scale:1.15}50%{scale:1.25}}
.ring{position:absolute;z-index:5;left:50%;top:44%;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;
  background:conic-gradient(#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3B3B);
  -webkit-mask-image:radial-gradient(circle,transparent 0 64%,#000 66% 72%,transparent 74%);mask-image:radial-gradient(circle,transparent 0 64%,#000 66% 72%,transparent 74%);
  opacity:0;animation:shock2 .42s ease-out forwards}
/* 虹の輪3つ（キュウィン×3）：だんだん大きい輪がポンと出て消える（同じ所が何回も光らないように、輪の大きさを変える） */
.ring.r1{--rs:.9;animation-delay:.1s}.ring.r2{--rs:1.5;animation-delay:.25s}.ring.r3{--rs:2.2;animation-delay:.4s}
@keyframes shock2{0%{opacity:.7;scale:calc(var(--rs) * .6)}100%{opacity:0;scale:calc(var(--rs) * 1.25)}}
@keyframes shock{0%{opacity:1;scale:.2}100%{opacity:0;scale:3.2}}
.big .hb{animation:bslam .42s cubic-bezier(.2,.9,.3,1.1) .38s both}
@keyframes bslam{0%{opacity:0;transform:translateY(-70px) scale(1.45);filter:brightness(3) blur(3px)}55%{opacity:1;transform:translateY(8px) scale(.96);filter:brightness(1.7) blur(0)}78%{transform:translateY(-3px) scale(1.02);filter:brightness(1.15)}100%{transform:none;filter:none}}
/* 見出し「デカ的中!!」：虹色の文字（boards.py）がたたきつけるように出て、色が流れる */
.big .bh{animation:bhSlam .3s cubic-bezier(.2,1.5,.4,1) .7s both,rbowText 2s linear .7s infinite}
@keyframes bhSlam{0%{opacity:0;transform:scale(2.6)}60%{opacity:1;transform:scale(.9)}100%{opacity:1;transform:scale(1)}}
.ov.big{--t0:.9s;--tc:.25s}
.ov.big .brows li{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .08s)}
.ov.big .btot{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s)}
.ov.big .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s + var(--tc))}

'''

FREEZE_CSS = r'''
/* ---------- フリーズ的中：虹色にギラギラ光る めちゃくちゃデカいPUSH → タップでパチスロのフリーズのように ----------
   （押したあとの秒は下の「押したあと」に書いてある） */
.w3{background:#E0322B;color:#FFFFFF}
.w8{background:#F27BB0;color:#1F1F1F}
.ov.fz{--rb:#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B;--ink2:#2A1259;--t0:<R+.45>;--tc:.25s}
/* 結果の買い目は0.08秒おき（パチンコの当たりのように速く） */
.ov.fz .brows li{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .08s)}
.ov.fz .btot{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s)}
.ov.fz .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s + var(--tc))}
.ov.fz .dim{background:radial-gradient(circle at 50% 44%,rgba(84,26,136,.55),rgba(5,2,14,.94) 66%)}
/* PUSHのうしろ：ぼかした虹（回る）と白い光の筋 */
.aura{position:absolute;left:50%;top:44%;width:600px;height:600px;margin:-300px 0 0 -300px;border-radius:50%;background:conic-gradient(var(--rb));filter:blur(40px);opacity:.6;animation:spin 3.2s linear infinite}
.prays{position:absolute;left:50%;top:44%;width:1100px;height:1100px;margin:-550px 0 0 -550px;border-radius:50%;
  background:repeating-conic-gradient(rgba(255,255,255,.34) 0 4deg,transparent 4deg 12deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 14%,transparent 56%);mask-image:radial-gradient(circle,#000 0 14%,transparent 56%);animation:spin 9s linear infinite}
/* 画面のふちが虹色に光る */
.edge{position:absolute;inset:0;z-index:11;pointer-events:none;box-shadow:inset 0 0 22px 6px rgba(255,70,200,.55),inset 0 0 64px 14px rgba(70,190,255,.32);animation:edge 1.2s ease-in-out infinite alternate}
@keyframes edge{from{opacity:.55}to{opacity:1}}
.frame{position:absolute;inset:0;z-index:12;pointer-events:none;padding:5px;overflow:hidden;
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
.frame b{position:absolute;left:50%;top:50%;width:1000px;height:1000px;margin:-500px 0 0 -500px;background:conic-gradient(var(--rb));animation:spin 1.6s linear infinite}
/* PUSH：横340×縦170（デカの1.2倍）。面は虹色が流れる＋ラメ＋白い光がサッと走る。白と紫のふち・虹の輪。1.3秒ごとにブルブルッ */
.push.fz{--pr:46px;width:340px;height:170px;background:#3A1E78;
  box-shadow:0 0 0 8px #FFFFFF,0 0 0 14px #3A1E78,0 12px 0 14px #1E0F45,0 0 54px 24px rgba(255,255,255,.3),0 30px 46px rgba(0,0,0,.6);
  animation:fzBob .85s ease-in-out infinite,fzBuzz 1.3s linear infinite,popIn .5s cubic-bezier(.2,1.6,.4,1) both}
.push.fz .face,.push.fz .gloss,.push.fz .glit{position:absolute;inset:0;border-radius:inherit;pointer-events:none}
.push.fz .face{background:repeating-linear-gradient(100deg,#FF3B3B 0,#FF9F1A 42px,#FFE53B 84px,#3BE26A 126px,#2FD6FF 168px,#4C6BFF 210px,#B34CFF 252px,#FF3BB8 294px,#FF3B3B 336px) 0 0/341.2px 100%;animation:fzFlow 1.4s linear infinite}
.push.fz .gloss{background:radial-gradient(70% 36% at 50% 10%,rgba(255,255,255,.95),rgba(255,255,255,.4) 55%,rgba(255,255,255,0) 100%),linear-gradient(180deg,rgba(255,255,255,0) 50%,rgba(48,12,96,.45) 100%);
  box-shadow:inset 0 -12px 0 rgba(0,0,0,.2),inset 0 3px 0 rgba(255,255,255,.8)}
.push.fz .glit{overflow:hidden}
.push.fz .glit b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);border-radius:50%;background:#FFFFFF;
  box-shadow:0 0 4px 1px rgba(255,255,255,.9);opacity:.15;animation:lame .8s ease-in-out var(--d) infinite alternate}
@keyframes lame{from{opacity:.12}to{opacity:1}}
.push.fz .spk{border-radius:inherit;overflow:hidden}
.push.fz span{font-size:80px;letter-spacing:.02em;color:#FFFFFF;
  text-shadow:3px 0 0 var(--ink2),-3px 0 0 var(--ink2),0 3px 0 var(--ink2),0 -3px 0 var(--ink2),2px 2px 0 var(--ink2),-2px 2px 0 var(--ink2),2px -2px 0 var(--ink2),-2px -2px 0 var(--ink2),0 8px 0 var(--ink2),0 0 26px rgba(255,255,255,.95)}
.push.fz::before{content:"";position:absolute;inset:0;z-index:3;border-radius:inherit;pointer-events:none;
  background:linear-gradient(105deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.95) 50%,rgba(255,255,255,0) 70%) -130% 0/55% 100% no-repeat;mix-blend-mode:screen;animation:glint 1.5s ease-in-out .3s infinite}
.push.fz::after{inset:-40px;border-radius:calc(var(--pr) + 40px);border:5px solid transparent;background:conic-gradient(var(--rb)) border-box;
  -webkit-mask:linear-gradient(#000 0 0) padding-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:ring .8s ease-out infinite}
.push.fz .halo{inset:-25px;border-radius:calc(var(--pr) + 25px);filter:drop-shadow(0 0 8px #FFFFFF) drop-shadow(0 0 20px rgba(255,110,230,.85))}
.push.fz .halo i{padding:10px}
.push.fz .halo b{width:620px;height:620px;margin:-310px 0 0 -310px;animation:spin .9s linear infinite}
@keyframes fzFlow{to{background-position:341.2px 0}}
@keyframes fzBob{0%,100%{translate:0 0}50%{translate:0 -22px}}
@keyframes fzBuzz{0%,16%,100%{rotate:0deg}2%{rotate:-2.4deg}4%{rotate:2.4deg}6%{rotate:-2deg}8%{rotate:2deg}10%{rotate:-1.4deg}12%{rotate:1.4deg}14%{rotate:-.6deg}}
@keyframes glint{0%{background-position:-130% 0}55%,100%{background-position:230% 0}}
.pshadow.fz{width:330px;height:26px;margin-top:36px;animation:shadFz .85s ease-in-out infinite}
@keyframes shadFz{0%,100%{transform:scale(1);opacity:.62}50%{transform:scale(.7);opacity:.3}}
.tap.fz{margin-top:20px;font-size:32px;background:linear-gradient(90deg,#FF6A6A,#FFE04D,#6BEB98,#5FDBFF,#C08CFF,#FF6A6A);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 3px 0 var(--ink2)) drop-shadow(0 0 7px rgba(255,255,255,.7));animation:rbowText 1.1s linear infinite}
/* ---------- 押したあと（パチスロのフリーズのように。押した瞬間にフリーズ） ----------
   秒は押してから。0＝白く光って横に流れるノイズ・<B>＝青い画面と白い光・<W>＝まわりが暗くなって青白い横一本線（細い電気）・<Z>＝線が点に縮んで消える
   ・（真っ暗1.5秒）・<M>＝虹色ネオンのカット・<R>＝結果（虹色の大当たりの画面・上に「ど的中」・テーマのボード） */
.ov.fz .blk{position:absolute;inset:0;background:#000000}
@keyframes vis{from,to{visibility:visible}}
@keyframes on1{from,to{opacity:1}}
@keyframes fzOn{from,to{opacity:1}}
.ov.fz .pc,.ov.fz .mt,.ov.fz .fin,.ov.fz .xf{position:absolute;inset:0;overflow:hidden;pointer-events:none}
/* ===== 1) フリーズ（押した瞬間＝0秒〜）：まさちゃんの送ってくれたパチスロのフリーズの動画のような動き（台の絵や音は使わない）
   白く光る → 明るい色の帯が横に流れる（走査線・青いブロック・縦の線）→ 赤い粒 → <B> 青い画面にまぶしい横の帯・白い光がふくらむ・細い稲妻
   → <W> まわりが暗くなって青白い横一本線（まん中にフレア・線にまとわりつく1pxの細い電気がバチバチ）→ <Z> 線が両はしから点に縮む・光の粒が散る → 真っ暗
   1コマ＝1/30秒。光の点めつを防ぐ：明るい色の帯どうしは明るさ0.8より上（切りかわっても点めつにならない）。強く光るのは、まん中の帯と細い線・小さな粒だけ ===== */
.pc{z-index:39;visibility:hidden;animation:vis <Z+.4> steps(1)}
.pc .pf{position:absolute;inset:0;visibility:hidden}
.pc .sm,.pc .nz,.pc .pcd{position:absolute;inset:0}
.pc i{position:absolute;visibility:hidden;animation:vis var(--t) steps(1) var(--d)}
/* 白く光る（0〜.2）・まぶしい帯のある水色（.2〜<B>）・青い画面（<B-.033>〜・<W> から暗くなる） */
.pc .p0{background:linear-gradient(172deg,#FFFFFF 0%,#F6FEFF 45%,#E6FBFF 100%);animation:vis .2s steps(1)}
.pc .pa{background:linear-gradient(180deg,#BFF2FF 0%,#ECFDFF 32%,#FFFFFF 50%,#E2FFF4 68%,#9CEBFF 100%);animation:vis .0667s steps(1) .0666s}
.pc .pb{background:linear-gradient(180deg,#7FDDFF 0%,#D5F8FF 38%,#FFFFFF 52%,#C9FFC2 74%,#6FE08E 100%);animation:vis .0667s steps(1) .1333s}
.pc .p1{background:linear-gradient(180deg,#2F8BFF 0%,#5CC6FF 30%,#C6F4FF 44%,#FFFFFF 50%,#C6F4FF 56%,#5CC6FF 70%,#2F8BFF 100%);animation:vis <B-.2> steps(1) .2s}
.pc .p2{background:radial-gradient(ellipse 130% 60% at 50% 50%,#3E7CFF 0%,#1A4BE0 30%,#0B2496 62%,#040B3E 100%);animation:vis <W+.1-B+.034> steps(1) <B-.034>,pOut .07s linear <W> forwards}
.pc .p2b{background:linear-gradient(180deg,rgba(120,200,255,0) 38%,rgba(190,235,255,.85) 47%,#FFFFFF 49.6%,#FFFFFF 50.4%,rgba(190,235,255,.85) 53%,rgba(120,200,255,0) 62%);
  animation:vis <W+.1-B+.034> steps(1) <B-.034>,pOut .07s linear <W> forwards}
@keyframes pOut{to{opacity:0}}
/* 走査線（1px）：白く光ってから <W> まで */
.pc .psl{background:repeating-linear-gradient(180deg,rgba(0,30,110,.26) 0 1px,rgba(0,0,0,0) 1px 3px);animation:vis <W+.07> steps(1)}
/* 横に流れる帯・ブロック・縦の線・赤い粒・点々（1コマずつ） */
.pc .sm i{height:var(--h);left:var(--x);top:var(--y);width:var(--w);background:linear-gradient(90deg,rgba(255,255,255,0),var(--c) 12%,var(--c) 78%,rgba(255,255,255,0))}
.pc .nz i{left:var(--x);top:var(--y);width:var(--w);height:var(--h);background:var(--c)}
/* まん中の白い光：ふくらむ・しぼむ（1コマずつ・<B>〜） */
.pc .pfx{position:absolute;left:-75px;top:<LINE-150>px;width:540px;height:300px;border-radius:50%;opacity:0;
  background:radial-gradient(ellipse 50% 50% at 50% 50%,#FFFFFF 0 16%,rgba(214,242,255,.95) 30%,rgba(120,190,255,.5) 50%,rgba(60,130,255,0) 70%);animation:pfx <W+.1-B> steps(1) <B> forwards}
/* ふくらむ → 少ししぼむ → もっとふくらむ → 線につぶれる（まん中はずっと白いまま。光る⇔暗いになるのはふちだけ） */
@keyframes pfx{0%{opacity:1;transform:scale(1)}30%{opacity:1;transform:scale(.74,.66)}56%{opacity:1;transform:scale(1.14,.94)}80%{opacity:1;transform:scale(.8,.14)}100%{opacity:0;transform:scale(.6,.08)}}
/* 青白い横一本線（.267〜）：<W> からちらつく → <Z> 両はしから縮む */
.pc .pcl{position:absolute;left:0;right:0;top:<LINE-1>px;height:2px;visibility:hidden;
  background:linear-gradient(90deg,rgba(150,200,255,.25),#D8EEFF 6%,#FFFFFF 50%,#D8EEFF 94%,rgba(150,200,255,.25));
  box-shadow:0 0 2px #FFFFFF,0 0 6px #BFE3FF,0 0 14px #4F96FF,0 0 30px #2A5CFF;
  animation:vis <Z+.18-.266> steps(1) .266s,pclFl .067s steps(1) <W> 3,pclX .18s cubic-bezier(.55,0,.9,.45) <Z> forwards}
@keyframes pclFl{0%{opacity:1}50%{opacity:.62}}
@keyframes pclX{from{transform:scaleX(1)}to{transform:scaleX(0)}}
.pc .pcf{position:absolute;left:50%;top:<LINE>px;width:0;height:0;opacity:0;animation:on1 <Z+.25-W> steps(1) <W>,pcfS .26s ease-in <Z+.08> forwards}
.pc .pcf b{position:absolute;border-radius:50%}
.pc .pcf .f1{left:-210px;top:-10px;width:420px;height:20px;background:radial-gradient(ellipse 50% 50% at 50% 50%,#FFFFFF 0 6%,rgba(190,225,255,.9) 14%,rgba(70,130,255,.45) 38%,rgba(40,90,255,0) 70%);animation:pcfP .067s steps(1) <W> 4}
.pc .pcf .f2{left:-40px;top:-40px;width:80px;height:80px;background:radial-gradient(circle,#FFFFFF 0 12%,rgba(170,215,255,.85) 26%,rgba(60,120,255,.3) 52%,rgba(40,90,255,0) 72%)}
.pc .pcf .f3{left:-1px;top:-30px;width:2px;height:60px;border-radius:1px;background:linear-gradient(180deg,rgba(255,255,255,0),#FFFFFF 50%,rgba(255,255,255,0))}
@keyframes pcfP{0%{opacity:1}50%{opacity:.72}}
@keyframes pcfS{0%{transform:scale(1)}55%{transform:scale(.4)}100%{transform:scale(0);opacity:0}}
/* 電気（稲妻）：いちばん細い線（芯0.8px・枝0.5px）。中点をずらして細かくギザギザ・枝分かれ。1コマごとに形が変わる（本物の放電のように） */
.pc .pca{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible;filter:drop-shadow(0 0 1.2px #CDEFFF) drop-shadow(0 0 4px #3D8DFF)}
.pc .pca path{fill:none;stroke:#F3FBFF;stroke-linecap:round;stroke-linejoin:round;visibility:hidden;animation:vis var(--t) steps(1) var(--d)}
/* 散る光の粒（下へ落ちながら消える） */
.pc .pcd i{left:var(--x);top:var(--y);width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);border-radius:50%;background:#D8F0FF;box-shadow:0 0 3px #5EA8FF;
  visibility:visible;opacity:0;animation:pcd var(--t) cubic-bezier(.2,.6,.4,1) var(--d) forwards}
@keyframes pcd{0%{opacity:1;translate:0 0}100%{opacity:0;translate:var(--dx) var(--dy)}}
/* ===== 3) 真っ暗（<Z+.4>〜<M>・1.5秒）→ 4) 虹色ネオンのカット（<M>〜<R>）：まさちゃんの指定の文字が、カットごとに出る
   T1「ど」「て」「き」「！」「！」→ T2「どてき！！」（階段）→ T3「どてき！！」「どてき！！」→ T4 白く光る →「ど！」×4 → T5「ど的中」「！！！！」（そろってから1.5秒）→ 結果
   どてき！！・ど！は、押した直後のPUSHのようにバグりながら（赤と水色の色ずれ・横ズレの帯）大きな筆の字で、場所と向きはバラバラ
   視覚酔い・光の点めつを防ぐ：画面全体が回る・迫る・流れる・ゆれる動きはしない（背景は止める）。動くのは文字と小さな光だけ（どの点も明るい⇔暗いが1秒に3回まで） ===== */
.mt{z-index:30}
.sc{position:absolute;inset:0;overflow:hidden;visibility:hidden}
.mfl{position:absolute;inset:0;z-index:5;background:#FFFFFF;opacity:0}
@keyframes mfl{0%{opacity:.7}100%{opacity:0}}
/* ネオンの線画：芯（白っぽい虹）と光（こい虹）を、テンゲルのアイコンからひろった線の形でくりぬく。虹色はゆっくり流れる（回らない） */
.nic{position:absolute;left:50%;top:0}
.nic .ng,.nic .nc{position:absolute;inset:0;background:repeating-linear-gradient(135deg,#FF2BD6 0,#FF9F1A 86px,#FFE53B 172px,#3CFF6A 258px,#2FD6FF 344px,#6A5BFF 430px,#FF2BD6 516px) 0 -400px/2600px 2600px no-repeat;
  -webkit-mask:url(/_blob/NGLOW) 0 0/100% 100%;mask:url(/_blob/NGLOW) 0 0/100% 100%;animation:nflow 4s linear infinite}
.nic .ng{opacity:.85}
.nic .nc{background-image:repeating-linear-gradient(135deg,#FF8AE6 0,#FFC77A 86px,#FFF08A 172px,#9CFFB4 258px,#8CEBFF 344px,#ABA2FF 430px,#FF8AE6 516px);-webkit-mask-image:url(/_blob/NCORE);mask-image:url(/_blob/NCORE)}
.nic.alt .ng{background-image:repeating-linear-gradient(135deg,#FF6A00 0,#FFE53B 104px,#FF2BD6 208px,#2FD6FF 312px,#3CFF6A 416px,#FF6A00 520px)}
.nic.alt .nc{background-image:repeating-linear-gradient(135deg,#FFB27A 0,#FFF08A 104px,#FF8AE6 208px,#8CEBFF 312px,#9CFFB4 416px,#FFB27A 520px)}
.nic.alt .ng,.nic.alt .nc{animation-name:nflow2}
@keyframes nflow{to{background-position:-729.7px -400px}}
@keyframes nflow2{to{background-position:-735.4px -400px}}
.stf{position:absolute;inset:0;background:radial-gradient(1.2px 1.2px at 20px 30px,#FFFFFF 50%,rgba(255,255,255,0) 51%) 0 0/71px 67px,radial-gradient(1px 1px at 50px 10px,#BFD8FF 50%,rgba(191,216,255,0) 51%) 0 0/53px 89px,
  radial-gradient(1.6px 1.6px at 30px 60px,#FFFFFF 50%,rgba(255,255,255,0) 51%) 0 0/113px 97px,radial-gradient(circle at 30% 30%,rgba(122,59,255,.5),rgba(122,59,255,0) 50%),
  radial-gradient(circle at 75% 70%,rgba(47,140,255,.45),rgba(47,140,255,0) 50%),#05020F}
/* 集中線：止まったまま（迫ってこない） */
.spd{position:absolute;inset:-100px;opacity:.55;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,255,255,0) 0 3deg,rgba(255,255,255,.7) 3deg 3.35deg,rgba(255,255,255,0) 3.35deg 7.3deg),
  repeating-conic-gradient(from 1.7deg at 50% 50%,rgba(80,220,255,0) 0 5deg,rgba(80,220,255,.55) 5deg 5.5deg,rgba(80,220,255,0) 5.5deg 11deg);
  -webkit-mask-image:radial-gradient(circle at 50% 50%,transparent 0 16%,#000 42%);mask-image:radial-gradient(circle at 50% 50%,transparent 0 16%,#000 42%)}
.orb{position:absolute;left:50%;top:46%;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 9%,#C8FFE0 18%,#3CFF9A 34%,rgba(60,255,154,.35) 52%,rgba(60,255,154,0) 70%);animation:orb 1.2s ease-in-out infinite alternate}
@keyframes orb{from{transform:scale(.94)}to{transform:scale(1.04)}}
/* 筆の字（まさちゃんの指定「パチンコのロゴのような字体とレインボーカラー」）：brush.py で描いた筆の形（フォントなし・写真の字の形は使わない）。
   下から：金の立体（CSS の drop-shadow を5つ重ねる・金 → こげ茶）→ 黒いふち → 金のふち → こげ茶の細いふち → 面（白 → 虹色を右下に少しずらして重ねる＝左上のふちが白く光る → 上半分につや）。まわりに白と色の光 */
.bzd{position:absolute;width:0;height:0;overflow:hidden}
.bz{position:absolute;left:0;top:0;overflow:visible}
.bz .k{fill:#0A0014;stroke:#0A0014;stroke-width:120px;stroke-linejoin:round}
.bz .g{fill:url(#bzGd);stroke:url(#bzGd);stroke-width:76px;stroke-linejoin:round}
.bz .d{fill:#3A1200;stroke:#3A1200;stroke-width:22px;stroke-linejoin:round}
.bz .w{fill:#FFFFFF}
.bz .h{fill:url(#bzGl)}
/* 光がサッと走る（「ど的中」だけ・1.1秒ごと） */
.bz .shn{animation:bzSh 1.1s ease-in-out var(--sd) infinite}
@keyframes bzSh{0%{transform:translateX(0)}60%,100%{transform:translateX(var(--s1))}}
/* T5「ど的中」「！」：ポンと出て少し傾いたまま止まる */
.bzt{position:absolute;left:var(--x);top:var(--y);width:var(--w);height:var(--h);margin:calc(var(--h) / -2) 0 0 calc(var(--w) / -2);opacity:0;transform:rotate(var(--r));
  animation:gqIn .18s cubic-bezier(.3,.7,.3,1) var(--d) forwards}
/* バグる筆の字（T1〜T4）：1文字（「ど！」は2文字）ずつ大きく、場所・大きさ・向きはバラバラ。押した直後のPUSHのように乱れる：
   赤と水色のずれ・横にずれる帯2本（それぞれ1回・1コマずつ）・まわりに小さなブロック。文字はずっとガクガクふるえる（左右上下と傾き・1秒に4回）。
   筆の字は明るさの差が大きい（黒と金のふち・虹色・白い光）ので、前のネオンの字より動きの回数をへらした（光の点めつを1秒に3回までにするため） */
.gq{position:absolute;left:var(--x);top:var(--y);width:var(--w);height:var(--h);margin:calc(var(--h) / -2) 0 0 calc(var(--w) / -2);opacity:0;transform:rotate(var(--r));
  animation:gqIn .16s cubic-bezier(.3,.7,.3,1) var(--d) forwards}
/* たたきつけるように出る：大きく → 少し小さく → ちょうど（0.16秒・はね返りは1回） */
@keyframes gqIn{0%{opacity:0;transform:rotate(var(--r)) scale(1.5)}60%{opacity:1;transform:rotate(var(--r)) scale(.92)}100%{opacity:1;transform:rotate(var(--r)) scale(1)}}
.gq .gj{position:absolute;inset:0;animation:gqV var(--vt) steps(1) var(--vd) infinite}
.gq .gr,.gq .gc{mix-blend-mode:screen;opacity:.8;animation:gqR .9s steps(1) var(--d) both}
.gq .gc{animation-name:gqC}
.gq .gr .k{fill:#FF1E5A;stroke:#FF1E5A}
.gq .gc .k{fill:#00E6FF;stroke:#00E6FF}
.gq .s{position:absolute;inset:0;opacity:0}
.gq .s1{clip-path:inset(18% -40% 60% -40%);animation:gqS1 .9s steps(1) var(--d) both}
.gq .s2{clip-path:inset(56% -40% 22% -40%);animation:gqS2 .9s steps(1) var(--d) both}
@keyframes gqR{from,to{translate:-12px 1px}}
@keyframes gqC{from,to{translate:12px -1px}}
@keyframes gqV{0%{translate:0 0;rotate:0deg}25%{translate:var(--va) calc(var(--va) * -.55);rotate:var(--vr)}50%{translate:calc(var(--va) * -.85) calc(var(--va) * .45);rotate:calc(var(--vr) * -1)}75%{translate:calc(var(--va) * .4) calc(var(--va) * .8);rotate:calc(var(--vr) * .5)}}
@keyframes gqS1{0%{opacity:0;translate:0 0}8%{opacity:1;translate:var(--a1) 0}12%{opacity:0;translate:0 0}}
@keyframes gqS2{0%{opacity:0;translate:0 0}30%{opacity:1;translate:var(--a2) 0}34%{opacity:0;translate:0 0}}
/* まわりの小さなブロック（1コマずつ） */
.bk i{position:absolute;left:var(--x);top:var(--y);width:var(--w);height:var(--h);background:var(--c);opacity:0;animation:on1 var(--t) steps(1) var(--d)}
/* 文字が出たときの光の輪（小さく1回） */
.tr{position:absolute;left:var(--x);top:var(--y);width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;border:5px solid var(--g);box-shadow:0 0 12px var(--g);opacity:0;animation:cring .45s ease-out var(--d) forwards}
@keyframes cring{0%{opacity:1;scale:.3}100%{opacity:0;scale:2}}
/* T1（<M>〜）：テンゲルのアイコンのネオン（画面よりデカい・止まっている）。まん中で大爆発 */
.t1{animation:vis <T2> steps(1) <M>}
.t1 .bg{position:absolute;inset:0;background:radial-gradient(circle at 16% 20%,#FF2BD6 0,rgba(255,43,214,0) 40%),radial-gradient(circle at 86% 16%,#2FD6FF 0,rgba(47,214,255,0) 38%),
  radial-gradient(circle at 80% 80%,#FFE53B 0,rgba(255,229,59,0) 42%),radial-gradient(circle at 18% 84%,#3CFF6A 0,rgba(60,255,106,0) 42%),radial-gradient(circle at 50% 48%,#7A3BFF 0,rgba(122,59,255,0) 58%),#14062E}
.t1 .dk{position:absolute;inset:0;background:rgba(8,2,26,.55)}
.t1 .nic{width:1100px;height:1100px;margin-left:-550px;top:-150px}
.t1 .dk2{position:absolute;inset:0;background:rgba(8,2,26,.35)}
/* T2（<M+T2>〜）：星空・光の玉 */
.t2{animation:vis <T3-T2> steps(1) <M+T2>}
/* T3（<M+T3>〜）：ネオンのギザギザ（止まっている） */
.t3{background:#06021A;animation:vis <T4-T3> steps(1) <M+T3>}
.t3 .zz{position:absolute;left:50%;top:50%;width:2800px;height:2800px;margin:-1400px 0 0 -1400px;transform:scale(.6);opacity:.5}
.t3 .zz svg{display:block;width:100%;height:100%}
/* T4（<M+T4>〜）：星空に「ど！」×4（1つずつ光の破片が飛び散る） */
.t4{animation:vis <T5-T4> steps(1) <M+T4>}
.t4 .glw{position:absolute;inset:0;background:radial-gradient(circle at 50% 44%,rgba(255,60,200,.45),rgba(122,59,255,.2) 40%,rgba(5,2,15,0) 70%)}
/* T5（<M+T5>〜<R>）：ネオンのパチンコの当たりのような虹色（黒に光る虹の光線・虹の輪・白く光るまん中・ネオンの星・きらめき）に「ど的中」「！！！！」。そろってから1.5秒 */
.t5{background:#06010F;animation:vis <R-M-T5> steps(1) <M+T5>}
.t5 .nr{position:absolute;left:50%;top:44%;width:1600px;height:1600px;margin:-800px 0 0 -800px;border-radius:50%;
  background:repeating-conic-gradient(from -1.2deg,#FF0844 0 2.4deg,rgba(0,0,0,0) 2.4deg 6deg,#FF9500 6deg 8.4deg,rgba(0,0,0,0) 8.4deg 12deg,#FFE600 12deg 14.4deg,rgba(0,0,0,0) 14.4deg 18deg,
    #19FF6E 18deg 20.4deg,rgba(0,0,0,0) 20.4deg 24deg,#00E5FF 24deg 26.4deg,rgba(0,0,0,0) 26.4deg 30deg,#C23CFF 30deg 32.4deg,rgba(0,0,0,0) 32.4deg 36deg);
  -webkit-mask-image:radial-gradient(circle,transparent 0 3%,#000 9%,#000 46%,transparent 62%);mask-image:radial-gradient(circle,transparent 0 3%,#000 9%,#000 46%,transparent 62%)}
.t5 .nr.g{filter:blur(9px);opacity:.95}
.t5 .nw{position:absolute;left:50%;top:44%;width:1600px;height:1600px;margin:-800px 0 0 -800px;border-radius:50%;
  background:repeating-conic-gradient(from 1.8deg,rgba(255,255,255,.85) 0 .5deg,rgba(255,255,255,0) .5deg 12deg);
  -webkit-mask-image:radial-gradient(circle,transparent 0 3%,#000 8%,rgba(0,0,0,.5) 30%,transparent 50%);mask-image:radial-gradient(circle,transparent 0 3%,#000 8%,rgba(0,0,0,.5) 30%,transparent 50%)}
.t5 .rg{position:absolute;left:50%;top:44%;width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);border-radius:50%;
  background:conic-gradient(#FF0844,#FF9500,#FFE600,#19FF6E,#00E5FF,#3D5BFF,#C23CFF,#FF0844);
  -webkit-mask:radial-gradient(circle,transparent 0 calc(50% - 6px),#000 calc(50% - 5px) calc(50% - 1px),transparent 50%);mask:radial-gradient(circle,transparent 0 calc(50% - 6px),#000 calc(50% - 5px) calc(50% - 1px),transparent 50%);
  filter:drop-shadow(0 0 6px rgba(255,255,255,.8)) drop-shadow(0 0 14px rgba(255,80,220,.7))}
.t5 .core{position:absolute;left:50%;top:44%;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 5%,rgba(255,255,255,.9) 9%,rgba(255,236,170,.55) 17%,rgba(255,120,220,.25) 30%,rgba(120,60,255,0) 52%)}
.t5 .bs{position:absolute;left:50%;top:44%;width:170px;height:170px;margin:-85px 0 0 -85px;background:linear-gradient(135deg,#FFFFFF,#FFF4B0 45%,#FFC83A);
  clip-path:polygon(50% 0,59% 41%,100% 50%,59% 59%,50% 100%,41% 59%,0 50%,41% 41%)}
.t5 .bsg{position:absolute;inset:0;filter:drop-shadow(0 0 10px #FF3BD2) drop-shadow(0 0 20px #2FF3FF)}
.t5 .spk b{filter:drop-shadow(0 0 4px var(--c))}
/* この背景だけ動く（まさちゃんの指定）：光の波が光線にそって外へ流れる（0.45秒ごと）・虹の輪が外へ広がって消える・まん中の光と星がふくらむ。回らない */
.t5 .rw{position:absolute;inset:0;
  -webkit-mask-image:repeating-conic-gradient(from -1.2deg at 50% 44%,#000 0 2.4deg,rgba(0,0,0,0) 2.4deg 6deg);mask-image:repeating-conic-gradient(from -1.2deg at 50% 44%,#000 0 2.4deg,rgba(0,0,0,0) 2.4deg 6deg)}
.t5 .rw i{position:absolute;left:50%;top:44%;width:240px;height:240px;margin:-120px 0 0 -120px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,0) 0 50%,rgba(255,250,225,.75) 63%,rgba(255,255,255,0) 77%);opacity:0;animation:rwv 1.35s cubic-bezier(.25,.1,.6,1) var(--d) infinite}
@keyframes rwv{0%{opacity:1;transform:scale(.3)}80%{opacity:.85}100%{opacity:0;transform:scale(4.6)}}
.t5 .rg{animation:rgo 1.6s ease-out var(--d) infinite}
@keyframes rgo{0%{opacity:0;transform:scale(.7)}18%{opacity:1}100%{opacity:0;transform:scale(1.45)}}
.t5 .core{animation:cbr .9s ease-in-out <M+T5> infinite alternate}
@keyframes cbr{from{scale:.9}to{scale:1.12}}
.t5 .bs{animation:cbr .9s ease-in-out <M+T5> infinite alternate}
/* ===== 5) 結果（<R>）：白く光る → 虹色の大当たりの画面（まさちゃんの指定「虹色の大当たり感強く」）に、上に「ど的中」・まん中からテーマのボード（画面はゆらさない）
   虹色の光線（止まったまま・回さない）・「ど的中」のうしろの白い光・虹の輪が外へ広がる・虹色のきらめきが上る・コイン・紙ふぶき ===== */
.xf{z-index:45}
.rfl{position:absolute;inset:0;background:#FFFFFF;opacity:0;animation:mfl .4s ease-out <R> forwards}
.fin{z-index:20;opacity:0;animation:fzOn .01s linear <R> forwards}
.fsk{position:absolute;inset:0}
.fin .fb{position:absolute;inset:0;background:radial-gradient(circle at 50% 94px,#FFFFFF 0,#FFF8DC 30px,rgba(255,236,170,.8) 64px,rgba(255,190,240,0) 190px),
  radial-gradient(circle at 50% 94px,rgba(26,6,52,0) 260px,rgba(26,6,52,.32) 600px,rgba(16,4,36,.6) 900px),
  repeating-conic-gradient(from -1.75deg at 50% 94px,#FF2D55 0 3.5deg,#3A1060 3.5deg 7deg,#FF9500 7deg 10.5deg,#3A1060 10.5deg 14deg,#FFEA00 14deg 17.5deg,#3A1060 17.5deg 21deg,
    #2BFF4F 21deg 24.5deg,#3A1060 24.5deg 28deg,#00D9FF 28deg 31.5deg,#3A1060 31.5deg 35deg,#3D63FF 35deg 38.5deg,#3A1060 38.5deg 42deg,#C23CFF 42deg 45.5deg,#3A1060 45.5deg 49deg)}
/* 虹色の光線の上に白い細い光線（明るさがゆっくり変わるだけ） */
.fin .frr{position:absolute;left:50%;top:94px;width:1800px;height:1800px;margin:-900px 0 0 -900px;border-radius:50%;
  background:repeating-conic-gradient(from 1deg,rgba(255,255,255,.55) 0 .8deg,rgba(255,255,255,0) .8deg 10deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 4%,transparent 50%);mask-image:radial-gradient(circle,#000 0 4%,transparent 50%);animation:frP 1.6s ease-in-out <R> infinite alternate}
/* 虹の輪：「ど的中」から外へ広がって消える（2つ・1.8秒ごと） */
.fin .frg i{position:absolute;left:50%;top:94px;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;opacity:0;
  background:conic-gradient(#FF2D55,#FF9500,#FFEA00,#2BFF4F,#00D9FF,#3D63FF,#C23CFF,#FF2D55);
  -webkit-mask:radial-gradient(circle,transparent 0 calc(50% - 5px),#000 calc(50% - 4px) calc(50% - 1px),transparent 50%);mask:radial-gradient(circle,transparent 0 calc(50% - 5px),#000 calc(50% - 4px) calc(50% - 1px),transparent 50%);
  filter:drop-shadow(0 0 6px rgba(255,255,255,.8));animation:frg 1.8s ease-out var(--d) infinite}
@keyframes frg{0%{opacity:0;transform:scale(.4)}12%{opacity:1}100%{opacity:0;transform:scale(3.4)}}
@keyframes frP{from{opacity:.75}to{opacity:1}}
.fin .emb i{position:absolute;left:var(--x);bottom:-20px;width:var(--s);height:var(--s);border-radius:50%;background:#FFFFFF;box-shadow:0 0 5px 2px var(--c);opacity:0;animation:emb var(--t) linear var(--d) infinite}
@keyframes emb{0%{opacity:0;translate:0 0}10%{opacity:1}80%{opacity:.9}100%{opacity:0;translate:var(--dx) -900px}}
/* 上の「ど的中」：筆の字（虹色・金と黒のふち・金の立体・つや・光がサッと走る）。うしろで虹色の炎が燃える・白い光 */
.dlg{position:absolute;left:0;right:0;top:282px;height:200px;opacity:0;transform:translateY(-302px) scale(.62);animation:dPop .3s cubic-bezier(.2,.9,.3,1.2) <R+.03> forwards}
@keyframes dPop{from{opacity:0;transform:translateY(-302px) scale(.85)}to{opacity:1;transform:translateY(-302px) scale(.62)}}
.dlg .dfl{position:absolute;left:-20px;right:-20px;top:-40px;bottom:-30px;border-radius:50%;
  background:radial-gradient(ellipse 50% 50% at 50% 58%,rgba(255,255,255,.95) 0,rgba(255,240,190,.8) 30%,rgba(255,120,220,.4) 55%,rgba(150,110,255,0) 74%);animation:dfl .5s ease-in-out <R> infinite alternate}
@keyframes dfl{from{transform:scale(1,1)}to{transform:scale(1.04,1.1)}}
/* 文字のうしろで燃える虹色の炎（ゆらゆら・ちらちら） */
.dlg .ffl{position:absolute;left:0;top:0;width:390px;height:200px;overflow:visible;filter:drop-shadow(0 0 6px rgba(255,255,255,.85))}
.dlg .ffl path{transform-box:fill-box;transform-origin:50% 100%;animation:flk var(--t) ease-in-out var(--d) infinite alternate}
@keyframes flk{0%{transform:scale(1,.82) skewX(-4deg)}50%{transform:scale(.92,1.08) skewX(3deg)}100%{transform:scale(1.04,1.16) skewX(-2deg)}}
/* 出たときの光の輪 */
.dlg .dr{position:absolute;left:50%;top:104px;width:260px;height:260px;margin:-130px 0 0 -130px;border-radius:50%;border:7px solid #FFF3B0;
  box-shadow:0 0 22px 4px #FFB000,inset 0 0 22px 4px #FFB000;opacity:0;animation:dr .5s ease-out <R+.12> forwards}
@keyframes dr{0%{opacity:1;transform:scale(.3)}100%{opacity:0;transform:scale(2.6)}}
.dlg .dsb{position:absolute;left:0;right:0;top:-6px;text-align:center;font:700 15px/1 "BIZ UDPGothic",sans-serif;letter-spacing:.42em;padding-left:.42em;color:#FFFFFF;text-shadow:0 0 6px #FF3BD2,0 0 14px #7A3BFF,0 2px 0 #2A0A48}
.dlg .dw{position:absolute;left:50%;top:122px;width:var(--w);height:var(--h);margin:calc(var(--h) / -2) 0 0 calc(var(--w) / -2)}
.dlg .dsp b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);background:#FFFFFF;
  clip-path:polygon(50% 0,58% 42%,100% 50%,58% 58%,50% 100%,42% 58%,0 50%,42% 42%);filter:drop-shadow(0 0 4px #FFE08A);opacity:0;animation:twinkle .9s ease-in-out var(--d) infinite}
/* まん中からボードがドンと出る（<R>・爆発）。コインはボードのうしろ・紙ふぶきは前 */
.fin .hb{z-index:6;animation:strike .45s cubic-bezier(.2,.9,.3,1.1) <R+.06> both}
@keyframes strike{0%{opacity:0;transform:translateY(-36px) scale(.7);filter:brightness(4) blur(2px)}30%{opacity:1;transform:translateY(8px) scale(1.06);filter:brightness(2.2) blur(0)}55%{transform:translateY(-4px) scale(.99);filter:brightness(1.3)}100%{transform:none;filter:none}}
.fin .conf.cb{z-index:5}
.fin .conf{z-index:7}
.fin .dlg{z-index:8}
.conf i.cn{height:var(--w);border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFFBE0 0 16%,#FFD54A 32%,#E0A100 70%,#9A6A00 100%);box-shadow:0 0 6px rgba(255,220,120,.9);animation:coin var(--t) linear var(--d) infinite}
@keyframes coin{0%{opacity:1;transform:translateY(0) rotateY(0)}85%{opacity:1}100%{opacity:0;transform:translateY(900px) rotateY(1080deg)}}
.ov.fz .close{z-index:60}
/* ボード（boards.py の .rb.fz：枠は虹色・回さない）の動き：見出しがたたきつけるように出て虹色が流れる・帯・超大穴の馬番の輪の色が回る・3連単の行に光が走る */
.fz .bh{animation:bhSlam .3s cubic-bezier(.2,1.5,.4,1) <R+.3> both,rbowText 1.2s linear <R+.3> infinite}
.zrib{animation:rowIn .22s ease-out <R+.36> both}
.n.zx{animation:zx 1.2s linear infinite}
@keyframes zx{0%,100%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FF3B3B,0 0 10px 4px rgba(255,59,59,.65)}20%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FFC21A,0 0 10px 4px rgba(255,194,26,.65)}40%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #2DBB55,0 0 10px 4px rgba(45,187,85,.65)}60%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #1FA8E0,0 0 10px 4px rgba(31,168,224,.65)}80%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #B34CFF,0 0 10px 4px rgba(179,76,255,.65)}}
.fz .brows li.top::after{animation:glint 1.8s ease-in-out <R+.6> infinite}
/* 視差効果を減らす：フリーズ（プチュン）・ネオンのカット・虹の輪・きらめき・紙ふぶきを止める。押すと1秒真っ暗 → 虹色の画面と「ど的中」（上）・ボードをふわっと出す */
@media (prefers-reduced-motion:reduce){
  .push.fz,.push.fz::before,.push.fz .face,.push.fz .glit b,.pshadow.fz,.tap.fz,.aura,.prays,.edge,.frame b,.n.zx,.fz .brows li.top::after{animation:none!important}
  .push.fz::after,.ov.fz .pc,.ov.fz .mt,.ov.fz .xf,.ov.fz .emb,.ov.fz .conf,.ov.fz .dsp,.ov.fz .dr,.ov.fz .frg{display:none}
  .push.fz .glit b{opacity:.6}
  .ov.fz{--t0:1.9s}
  .ov.fz .fin{animation:fadeIn .6s ease-out 1s both!important}
  .ov.fz .frr,.ov.fz .dfl,.ov.fz .ffl path{animation:none!important}
  .ov.fz .bz .shn{display:none}
  .ov.fz .dlg{animation:none!important;opacity:1}
  .ov.fz .hb{animation:fadeIn .5s ease-out 1.3s both!important}
  .fz .bh{animation:fadeIn .4s ease-out 1.6s both!important}
  .zrib{animation:fadeIn .4s ease-out 1.7s both!important}
}
'''

HEADER = f'''  <header class="hd">
    <div class="hd-r1">
      <div class="logo">テンゲル<span class="sr">Ⅲ</span><span class="iii" aria-hidden="true"><i></i><i></i><i></i></span></div>
      <button class="mbtn" type="button"><svg {SVG_A}><path d="M3.5 5.5h6a2.5 2.5 0 0 1 2.5 2.5v11a2 2 0 0 0-2-2H3.5z"></path><path d="M20.5 5.5h-6A2.5 2.5 0 0 0 12 8v11a2 2 0 0 1 2-2h6.5z"></path></svg>説明書</button>
    </div>
  </header>
  <img class="bnr" src="{BANNER}" alt="青空と芝生、木の柵、草原に立つ栗毛の馬のイラスト">'''


def form(bets, pay_total, note, fin=(6, 2, 10)):
    rows = ''.join(f'<li><span class="bt">{t}</span><span class="bc">{combo(c, s)}</span><span class="by">{y}</span></li>' for t, c, s, y, _, _ in bets)
    return f'''  <main class="ct">
    <section class="card">
      <h2 class="ch">レースの結果を記録</h2>
      <div class="rh"><span class="rk">9R</span><span class="rs">1400m ダ・良・12頭・予約したレース</span></div>
      <p class="lab">着順（馬番）</p>
      <div class="fin"><span class="k">1着</span>{num(fin[0])}<span class="k">2着</span>{num(fin[1])}<span class="k">3着</span>{num(fin[2])}</div>
      <p class="lab">予約した買い目</p>
      <ul class="bets">{rows}</ul>
      <div class="pay"><span>払戻（回収額）</span><b>{pay_total}</b></div>
      <button class="rec" type="button" onClick="{{{{toPush}}}}"><svg {SVG_A}><path d="M5 4.5h11l3 3v12H5z"></path><path d="M8 4.5v5h7v-5M8 19.5v-5h8v5"></path></svg>記録する</button>
      <p class="note">{note}</p>
    </section>
  </main>'''


def bet_rows(bets, kind, mark=()):
    """ボードの行：当たった買い目だけ（ハズレは全部・払戻0円）。デカ・ど的中・隠れど的中は3連単の行に虹色のふち（.top）"""
    rows, k = '', 0
    for t, c, s, y, p, hit in bets:
        if kind != 'miss' and not hit:
            continue
        cls = ' class="top"' if (kind in ('big', 'fz', 'hidden') and t == '3連単') else ''
        pay = '0円' if kind == 'miss' else p
        rows += (f'<li{cls} style="--i:{k}"><span class="bt tag">{t}</span><span class="bc">{combo(c, s, mark if t == "3連単" else ())}</span>'
                 f'<span class="by">{y}</span><span class="bp">{pay}</span></li>')
        k += 1
    return rows, k


def board(kind, bets, total, rib='', mark=(), tid=THEME, race='9R'):
    """結果のボード（壁紙のテーマ tid のボード・boards.py）。kind：hit・big・fz・hidden・miss ／ rib：見出しの下の帯 ／ mark：虹色の輪をつける馬番"""
    rows, _ = bet_rows(bets, kind, mark)
    return board_html(tid, kind, rows, total, race=race, rib=rib)


FZ_X = 11    # 見本の超大穴の馬（11番・11番人気）
# フリーズの時刻（押してから）：押した瞬間（0秒）にフリーズ（白く光って横に流れるノイズ）・B＝青い画面と白い光・W＝まわりが暗くなって青白い横一本線（細い電気）
# ・Z＝線が点に縮んで消える（このあと真っ暗1.5秒）・M＝虹色ネオンのカット・R＝結果（虹色の大当たりの画面・上に「ど的中」・テーマのボード）
# まさちゃんの指定：前の「押した瞬間の画面がバグる」はやめて、押した瞬間にフリーズ（パチスロのプチュン）
FZ_T = dict(B=.3, W=.45, Z=.62, M=2.52, R=6.9)
# 虹色ネオンのカットの始まり（<M> からの秒）。パチンコの当たりのように速く・激しく：T1「どてき！！」→ T2 → T3（×2）→ T4「ど！」×4 → T5「ど的中！！！！」
# T5 の「！」がそろうのは <M+T5+.23>、そこから HOLD 秒で結果（R ＝ M＋T5＋.23＋HOLD）
MT_T = dict(T2=.6, T3=1.15, T4=1.75, T5=2.65, HOLD=1.5)
assert abs(FZ_T['R'] - (FZ_T['M'] + MT_T['T5'] + .23 + MT_T['HOLD'])) < 1e-9
assert abs(FZ_T['M'] - (FZ_T['Z'] + .4 + 1.5)) < 1e-9    # 線が消えてから真っ暗1.5秒
LINE_Y = 422    # 青白い横一本線の高さ（px）
def svg_url(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe="/:=' .,-") + '")'


def fz_sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


def fz_css():
    """FREEZE_CSS の <M+.85>・<W+.07> などを秒に直す（<LINE-150> などは px）・ネオンの線画の絵を入れる"""
    css = re.sub(r'<LINE([+\-]\d+)?>', lambda m: f'{LINE_Y + int(m.group(1) or 0)}', FREEZE_CSS)
    css = re.sub(r'<([A-Z][A-Z0-9.+\-]*)>', lambda m: fz_sec(eval(m.group(1), {}, dict(FZ_T, **MT_T))), css)
    for k, v in (('NGLOW', blobs['fz_nglow']), ('NCORE', blobs['fz_ncore'])):
        css = css.replace(k, v)
    return css + MT['css'] + '\n'


def glitter(n, seed):
    """PUSHの面のラメ（小さな光の点がばらばらに光る）"""
    rnd = random.Random(seed)
    return ''.join(f'<b style="--x:{rnd.uniform(3, 97):.1f}%;--y:{rnd.uniform(6, 94):.1f}%;--s:{rnd.uniform(1.6, 3.6):.1f}px;--d:{rnd.uniform(0, 1.6):.2f}s"></b>' for _ in range(n))


def fz_push():
    """フリーズのPUSHの画面"""
    return f'''<div class="dim"></div>
    <div class="aura"></div><div class="prays"></div>
    <div class="spk">{sparkles(30, 21)}</div>
    <div class="pbox">
      <button class="push fz" type="button" onClick="{{{{toReveal}}}}" aria-label="フリーズ的中ボタン"><i class="halo" aria-hidden="true"><i><b></b></i></i><i class="face"></i><i class="gloss"></i><i class="glit">{glitter(56, 37)}</i><i class="spk">{sparkles(7, 31, white=True)}</i><span>PUSH</span></button>
      <div class="pshadow fz"></div>
      <p class="tap fz">タップ!!</p>
    </div>
    <div class="edge"></div><div class="frame"><b></b></div>'''


def bez_prog(t, x1, y1, x2, y2):
    """cubic-bezier の時刻 t（0〜1）のときの進み（0〜1）"""
    bx = lambda s: 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
    by = lambda s: 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if bx(m) < t else (lo, m)
    return by((lo + hi) / 2)


# ---------- フリーズ（押した瞬間から）：まさちゃんの送ってくれたパチスロのフリーズの動画のような動き（台の絵や音は使わない） ----------
FR = 1 / 30      # 1コマ（液晶のコマ）
# 横に流れる帯の色：明るい色（明るさ0.8より上）を多めに、あざやかな水色・緑を少し（帯が変わるのは2コマに1回だけ）
SMEAR_HI = ('#FFFFFF', '#E9FFFF', '#FFF35C', '#D2FF4A', '#9CFF6A', '#FAFFA8')
SMEAR_MID = ('#4FE3FF', '#3CFF8A', '#00C8FF', '#7DF0FF')


def bolt(rnd, pts, rough, depth):
    """稲妻：折れ線 pts を中点ずらしで細かくギザギザにする（深さ depth・ずらす強さ rough）"""
    for _ in range(depth):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy) or 1
            off = rnd.uniform(-1, 1) * rough * L
            out += [((ax + bx) / 2 - dy / L * off, (ay + by) / 2 + dx / L * off), (bx, by)]
        pts = out
    return pts


def bolt_d(pts):
    """path の d（座標は2倍の整数・相対で短く。viewBox は 780×1688）"""
    q = [(round(x * 2), round(y * 2)) for x, y in pts]
    return f'M{q[0][0]} {q[0][1]}l' + ' '.join(f'{b[0] - a[0]} {b[1] - a[1]}' for a, b in zip(q, q[1:]))


def bolts_line(rnd, x0, x1, n, wander=9, rmin=60):
    """横一本線にそって走る電気 n 本（x0〜x1 のあいだ）＋枝。戻り値 [(点, 太さ)]"""
    out = []
    for _ in range(n):
        a = rnd.uniform(x0, max(x0, x1 - rmin))
        b = min(x1, a + rnd.uniform(rmin, max(rmin, x1 - x0)))
        k = max(2, round((b - a) / 42))
        base = [(a + (b - a) * j / k, LINE_Y + (rnd.uniform(-wander, wander) if 0 < j < k else rnd.uniform(-2, 2))) for j in range(k + 1)]
        pts = bolt(rnd, base, .3, 3)
        out.append((pts, 1.6))
        for _ in range(rnd.randint(0, 3)):            # 枝（上か下へ）
            px, py = pts[rnd.randrange(1, len(pts) - 1)]
            ang = rnd.uniform(.35, 1.2) * rnd.choice([-1, 1]) + rnd.choice([0, math.pi])
            L = rnd.uniform(10, 42)
            out.append((bolt(rnd, [(px, py), (px + math.cos(ang) * L, py + math.sin(ang) * L)], .32, 3), 1.0))
    return out


def bolt_curve(rnd, xa, xb, h):
    """横の帯の上に弓なりに走る電気（動画の青い画面の大きな稲妻のように）"""
    k = 9
    base = [(xa + (xb - xa) * j / k, LINE_Y - 4 * h * (j / k) * (1 - j / k) + rnd.uniform(-5, 5)) for j in range(k + 1)]
    return bolt(rnd, base, .24, 3)


def freeze_layers(seed=93):
    """押した瞬間のフリーズ（HTML）：白く光る → 横に流れる帯 → 赤い粒 → 青い画面と白い光・細い電気 → 横一本線と電気 → 点に縮む・光の粒"""
    rnd = random.Random(seed)
    B, W, Z = FZ_T['B'], FZ_T['W'], FZ_T['Z']
    sec = lambda v: f'{v - .0001:.4f}'.rstrip('0').rstrip('.') + 's'     # コマの切れ目より少し前から（60コマ/秒の画面でもすき間ができないように）
    sm, nz, arcs, dust = [], [], [], []

    def it(lst, d, t, **v):
        lst.append('<i style="' + f'--d:{sec(d)};--t:{sec(t)};' + ''.join(f'--{k}:{x}{"px" if isinstance(x, (int, float)) else ""};' for k, x in v.items()) + '"></i>')
    # 白く光る2コマ（0〜.067）：青いブロックがまるく集まる・縦に抜けた線
    for f in range(2):
        d = f * FR
        cx, cy = 236 + f * 6, 470 - f * 4
        for _ in range(16):
            a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(26, 60)
            s = rnd.choice([4, 5, 6, 8, 10])
            it(nz, d, FR, x=round(cx + math.cos(a) * r), y=round(cy + math.sin(a) * r * 1.1), w=s, h=s + rnd.choice([0, 2, 6]),
               c=rnd.choice(['#3F72FF', '#2C5BF0', '#6E9BFF', '#8DB4FF']))
        for _ in range(9):
            it(nz, d, FR, x=round(rnd.uniform(150, 330)), y=round(rnd.uniform(60, 300)), w=1, h=round(rnd.uniform(40, 170)), c='rgba(70,120,255,.55)')
        for _ in range(3):         # 細い明るい帯（始まり）
            it(sm, d, FR, x=round(rnd.uniform(-40, 160)), y=round(rnd.uniform(80, 760)), w=round(rnd.uniform(120, 360)), h=rnd.choice([2, 3, 5]), c=rnd.choice(SMEAR_HI[2:]))
    # 横に流れる帯（.067〜.2）：2つの場面（2コマずつ）。2コマめは帯が少し横にずれる。後の場面は下のほうに緑と黄色の大きい帯
    for s in range(2):
        d = (2 + s * 2) * FR
        for _ in range(15):
            low = s == 1 and rnd.random() < .55
            y = rnd.uniform(400, 820) if low else rnd.uniform(10, 830)
            x, w = rnd.uniform(-90, 230), rnd.uniform(130, 480)
            h = rnd.choice([3, 5, 8, 14, 22, 34, 52, 76])
            c = rnd.choice(SMEAR_MID) if rnd.random() < .3 else rnd.choice(SMEAR_HI)
            for f in range(2):
                it(sm, d + f * FR, FR, x=round(x + f * rnd.uniform(-14, 14)), y=round(y), w=round(w), h=h, c=c)
        for _ in range(4):
            it(nz, d + rnd.choice([0, FR]), FR, x=round(rnd.uniform(-20, 250)), y=round(rnd.uniform(40, 800)), w=round(rnd.uniform(60, 240)), h=rnd.choice([1, 2, 2, 3]),
               c=rnd.choice(['#3A6BFF', '#1F4FE0', '#5C8BFF', '#FF4FD8']))
        for _ in range(5):
            s_ = rnd.choice([5, 6, 8])
            it(nz, d + rnd.choice([0, FR]), FR, x=round(rnd.uniform(160, 330)), y=round(rnd.uniform(150, 420)), w=s_, h=s_ + 4, c='#3060F0')
    # 赤い粒（.2〜.267・2コマ）：まぶしい帯のまわりに
    for f in range(2):
        d = .2 + f * FR
        for _ in range(70):
            it(nz, d, FR, x=round(rnd.uniform(-4, 386)), y=round(LINE_Y + rnd.gauss(0, 26) - 6 + f * 8), w=rnd.choice([2, 3, 4, 5, 7]), h=rnd.choice([1, 2, 2, 3]),
               c=rnd.choice(['#FF2D55', '#FF4F70', '#E8003A', '#FF7A8E']))
    # 点々（<B+.033>〜・1コマ）：縦の短い点々があちこちに
    d = B + FR
    for _ in range(90):
        y = LINE_Y + rnd.gauss(0, 120)
        it(nz, d, FR, x=round(rnd.uniform(0, 389)), y=round(y), w=rnd.choice([1, 1, 2]), h=rnd.choice([3, 4, 6, 9]),
           c=rnd.choice(['#FFE65A', '#FF6A5A', '#FFFFFF', '#7AF0FF', '#FFC2E0']))
    # 電気：1コマ（1/30秒）ずつ形が変わる
    plan = [(.2 + FR, 1, 1), (8 * FR, 2, 2), (B, 1, 2), (B + FR, 0, 2), (B + 2 * FR, 1, 2), (B + 3 * FR, 1, 2), (W - FR / 2, 0, 3)]
    for d, ncurve, nline in plan:
        for _ in range(ncurve):
            xa = rnd.uniform(-20, 120)
            arcs.append((bolt_curve(rnd, xa, xa + rnd.uniform(160, 300), rnd.uniform(40, 120)), 1.4, d))
        for pts, sw in bolts_line(rnd, 0, 390, nline, wander=14):
            arcs.append((pts, sw, d))
    f = 0
    while W + f * FR < Z - .005:           # 横一本線（<W>〜<Z>）：線の全体に3〜4本ずつ（＋枝）
        for pts, sw in bolts_line(rnd, -6, 396, rnd.choice([3, 4]), wander=12, rmin=140):
            arcs.append((pts, sw, W + f * FR))
        f += 1
    f = 0
    while Z + f * FR < Z + .17:            # 縮むとき（<Z>〜）：残っている線の上だけ
        d = Z + f * FR
        hw = 195 * (1 - bez_prog(min(1, (d + FR / 2 - Z) / .18), .55, 0, .9, .45))
        if hw > 12:
            for pts, sw in bolts_line(rnd, 195 - hw, 195 + hw, 3, wander=5, rmin=min(60, hw)):
                arcs.append((pts, sw * .85, d))
        f += 1
    paths = ''.join(f'<path style="--d:{sec(d)};--t:{sec(FR)};stroke-width:{sw:g}" d="{bolt_d(pts)}"></path>' for pts, sw, d in arcs)
    # 散る光の粒：線から下へ落ちながら消える（縮むときは残っている線から）
    for _ in range(54):
        d = rnd.uniform(W + .05, Z + .2)
        hw = 195 if d < Z else 195 * (1 - bez_prog(min(1, (d - Z) / .18), .55, 0, .9, .45))
        x = 195 + rnd.uniform(-hw, hw)
        it(dust, d, rnd.uniform(.3, .6), x=round(x, 1), y=round(LINE_Y + rnd.uniform(-2, 2), 1), s=round(rnd.uniform(1.2, 2.4), 1),
           dx=round(rnd.uniform(-50, 50)), dy=round(rnd.uniform(6, 60)))
    return (f'<div class="pc" aria-hidden="true"><div class="pf p0"></div><div class="pf pa"></div><div class="pf pb"></div><div class="sm">{"".join(sm)}</div><div class="pf p1"></div>'
            f'<div class="pf p2"></div><div class="pf p2b"></div><div class="pfx"></div><div class="nz">{"".join(nz)}</div><div class="pf psl"></div>'
            f'<div class="pcl"></div><div class="pcf"><b class="f1"></b><b class="f2"></b><b class="f3"></b></div>'
            f'<svg class="pca" viewBox="0 0 780 1688">{paths}</svg><div class="pcd">{"".join(dust)}</div></div>')


def zigzag():
    """S2：ネオンのギザギザ（12の角の星）が16重。外ほど太い"""
    out = []
    for k in range(16):
        R = 80 * 1.3 ** k
        pts = ' '.join(f'{(R if i % 2 == 0 else R * .6) * math.cos(math.pi * i / 12 + (k % 2) * math.pi / 12):.0f},'
                       f'{(R if i % 2 == 0 else R * .6) * math.sin(math.pi * i / 12 + (k % 2) * math.pi / 12):.0f}' for i in range(24))
        h, sw = (k * 53 + 300) % 360, 5 + k * 2.6
        out.append(f'<polygon points="{pts}" stroke="hsl({h},100%,58%)" stroke-width="{sw * 2.4:.1f}" stroke-opacity=".32"></polygon>'
                   f'<polygon points="{pts}" stroke="hsl({h},100%,60%)" stroke-width="{sw:.1f}"></polygon>'
                   f'<polygon points="{pts}" stroke="#FFFFFF" stroke-width="{sw * .3:.1f}"></polygon>')
    return f'<svg viewBox="-1400 -1400 2800 2800" fill="none" stroke-linejoin="miter" aria-hidden="true">{"".join(out)}</svg>'


def neon_icon(alt=False):
    return f'<div class="nic{" alt" if alt else ""}"><div class="nv"><i class="ng"></i><i class="nc"></i></div></div>'


def ring(x, y, d, g):
    return f'<i class="tr" style="--x:{x:g}px;--y:{y:g}px;--d:{fz_sec(d)};--g:{g}"></i>'


# ---------- 筆の字（ど的中の演出の文字）：brush.py で描いた形（brush_glyphs.json・フォントなし） ----------
BZ = json.load(open(f'{K}/brush_glyphs.json', encoding='utf-8'))
BZ_RB = ((0, '#FF2D55'), (.18, '#FF9500'), (.36, '#FFEA00'), (.54, '#2BFF4F'), (.72, '#00D9FF'), (.88, '#3D63FF'), (1, '#C23CFF'))   # 虹色
BZ_EX = ('#FFD447', '#D9971A', '#A6680A', '#6E4205', '#3E2402')   # 金の立体（字に近い → 遠い。CSS の drop-shadow を5つ重ねる）
BZ_PAL = dict(   # 虹色の向き（1：上 → 下・2：左上 → 右下・3：右上 → 左下）・まわりの光の色・爆発の光の色（2つ）
    pink=(1, '#FF3BD2', '#FFD0F7', '#FF3BD2'), blue=(2, '#2FB4FF', '#D2FBFF', '#2FB4FF'), gold=(3, '#FFB300', '#FFF8C0', '#FFB300'),
    green=(2, '#3CFF6A', '#EEFFC0', '#3CFF6A'), white=(1, '#FFFFFF', '#FFFBE0', '#FF5A00'), fire=(1, '#FF9A00', '#FFF6C8', '#FF6A00'))
_bzn = [0]


def bz_defs():
    """筆の字の形・虹色（3つの向き）・金・つや・光の筋（ページに1回だけ。字は <use> でここを指す）"""
    def lg(i, x1, y1, x2, y2):
        return (f'<linearGradient id="bzR{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
                + ''.join(f'<stop offset="{o:g}" stop-color="{c}"></stop>' for o, c in BZ_RB) + '</linearGradient>')
    shapes = ''.join(f'<path id="bz-{g["id"]}" d="{g["d"]}" fill-rule="evenodd" clip-rule="evenodd"></path>'
                     f'<clipPath id="bzc-{g["id"]}"><use href="#bz-{g["id"]}"></use></clipPath>' for g in BZ.values())
    grads = (lg(1, 0, 0, 0, 1) + lg(2, 0, 0, 1, 1) + lg(3, 1, 0, 0, 1)
             + '<linearGradient id="bzGd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFBE0"></stop><stop offset=".28" stop-color="#FFD54A"></stop>'
               '<stop offset=".5" stop-color="#A86400"></stop><stop offset=".53" stop-color="#FFE88A"></stop><stop offset=".8" stop-color="#FFB000"></stop>'
               '<stop offset="1" stop-color="#6A3A00"></stop></linearGradient>'
             + '<linearGradient id="bzGl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".6"></stop>'
               '<stop offset=".4" stop-color="#FFFFFF" stop-opacity=".1"></stop><stop offset=".41" stop-color="#FFFFFF" stop-opacity="0"></stop></linearGradient>'
             + '<linearGradient id="bzSh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"></stop>'
               '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".9"></stop><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"></stop></linearGradient>')
    return f'<svg class="bzd" width="0" height="0" aria-hidden="true"><defs>{shapes}{grads}</defs></svg>'


def bz_word(text, fs, rb=1, kern=-90, scales=None, dys=None, shine=None):
    """筆の字の部品（1文字＝1000 → fs px）。字の並びのまん中（横のまん中・縦の 500）が、置く場所のまん中になる。
       戻り値：W・H（px）・vb（viewBox）・defs（1回だけ置く：字の並び bw・面 bf）・stack（重ねる順）"""
    _bzn[0] += 1
    n = _bzn[0]
    x = 0
    items = face = clip = ''
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for i, c in enumerate(text):
        g = BZ[c]
        s = scales[i] if scales else 1
        dy = dys[i] if dys else 0
        tr = f'translate({x:.0f} {dy:.0f})' + (f' scale({s:g})' if s != 1 else '')
        u = f'href="#bz-{g["id"]}"'
        items += f'<use {u} transform="{tr}"></use>'
        face += (f'<g transform="{tr}" clip-path="url(#bzc-{g["id"]})"><use {u} class="w"></use>'
                 f'<use {u} transform="translate(9 12)" fill="url(#bzR{rb})"></use><use {u} class="h"></use></g>')
        clip += f'<use {u} transform="{tr}"></use>'
        bx = g['bbox']
        x0, y0 = min(x0, x + bx[0] * s), min(y0, dy + bx[1] * s)
        x1, y1 = max(x1, x + bx[2] * s), max(y1, dy + bx[3] * s)
        x += g['adv'] * s + kern
    cx = (x - kern) / 2
    m = 70    # 黒いふちのぶん
    hw, hh = max(cx - x0, x1 - cx) + m, max(500 - y0, y1 - 500) + m
    vb = f'{cx - hw:.0f} {500 - hh:.0f} {2 * hw:.0f} {2 * hh:.0f}'
    defs = f'<g id="bw{n}">{items}</g><g id="bf{n}">{face}</g>'
    stack = f'<use href="#bw{n}" class="k"></use><use href="#bw{n}" class="g"></use><use href="#bw{n}" class="d"></use><use href="#bf{n}"></use>'
    if shine is not None:    # 光がサッと走る（面だけ）
        defs += f'<clipPath id="bzs{n}">{clip}</clipPath>'
        stack += (f'<g clip-path="url(#bzs{n})"><g transform="skewX(-18)"><rect class="shn" x="{cx - hw - 420:.0f}" y="{500 - hh:.0f}" width="420" height="{2 * hh:.0f}" '
                  f'fill="url(#bzSh)" style="--sd:{shine};--s1:{2 * hw + 900:.0f}px"></rect></g></g>')
    return dict(n=n, W=round(2 * hw * fs / 1000, 1), H=round(2 * hh * fs / 1000, 1), vb=vb, defs=f'<defs>{defs}</defs>', stack=stack, fs=fs)


def bz_svg(wd, glow, defs=True, flat=False):
    """筆の字の絵：金の立体（drop-shadow を重ねる）とまわりの光は CSS の filter（大きさに合わせる）。flat：filter なし（横ズレの帯用・軽く）"""
    fs = wd['fs']
    if flat:
        return f'<svg class="bz" viewBox="{wd["vb"]}" width="{wd["W"]:g}" height="{wd["H"]:g}" aria-hidden="true">{wd["stack"]}</svg>'
    ex = ' '.join(f'drop-shadow({fs * .0063:.2f}px {fs * .0126:.2f}px 0 {c})' for c in BZ_EX)
    flt = f'filter:{ex} drop-shadow(0 0 {fs * .025:.1f}px rgba(255,255,255,.75)) drop-shadow(0 0 {fs * .08:.1f}px {glow})'
    return (f'<svg class="bz" viewBox="{wd["vb"]}" width="{wd["W"]:g}" height="{wd["H"]:g}" style="{flt}" aria-hidden="true">'
            f'{wd["defs"] if defs else ""}{wd["stack"]}</svg>')


def bz_sil(wd, cls):
    """色ずれ用の影（字の形＋黒いふちの太さ・赤か水色）"""
    return f'<svg class="bz {cls}" viewBox="{wd["vb"]}" width="{wd["W"]:g}" height="{wd["H"]:g}" aria-hidden="true"><use href="#bw{wd["n"]}" class="k"></use></svg>'


def bzt(text, cx, cy, fs, d, pal, r=0, z=1, **kw):
    """止まった筆の字（T5）：ポンと出て、少し傾いたまま"""
    rb, glow = BZ_PAL[pal][:2]
    wd = bz_word(text, fs, rb=rb, **kw)
    return (f'<div class="bzt" style="z-index:{z};--x:{cx}px;--y:{cy}px;--w:{wd["W"]:g}px;--h:{wd["H"]:g}px;--d:{fz_sec(d)};--r:{r}deg">'
            f'{bz_svg(wd, glow)}</div>')


VT = 1.0   # 文字のブルブル：1回り1秒で4か所 → 1秒に4回、大きくガクガク動く（筆の字は明るさの差が大きいので、前の1秒に約7回だと点めつが多すぎた）


def gq(text, cx, cy, fs, d, pal, r=0, seed=0, z=1):
    """バグる筆の字：まん中(cx, cy)・大きさ fs・傾き r・色 pal（BZ_PAL）・z（重なったときの上下。先に読む字を上に）"""
    rnd = random.Random(seed)
    rb, glow = BZ_PAL[pal][:2]
    wd = bz_word(text, fs, rb=rb, kern=-80)
    cp = bz_svg(wd, glow, defs=False, flat=True)    # 横ズレの帯（1コマずつ）は立体と光なしで軽く
    a1, a2 = rnd.choice([-1, 1]) * rnd.uniform(.12, .2) * fs, rnd.choice([-1, 1]) * rnd.uniform(.1, .18) * fs
    va, vr, vd = rnd.uniform(.075, .095) * fs, rnd.choice([-1, 1]) * rnd.uniform(4, 6), -rnd.uniform(0, VT)
    return (f'<div class="gq" style="z-index:{z};--x:{cx}px;--y:{cy}px;--w:{wd["W"]:g}px;--h:{wd["H"]:g}px;--d:{fz_sec(d)};--r:{r}deg;'
            f'--a1:{a1:.0f}px;--a2:{a2:.0f}px;--va:{va:.1f}px;--vr:{vr:.1f}deg;--vt:{VT}s;--vd:{vd:.2f}s"><div class="gj">'
            f'{bz_sil(wd, "gr")}{bz_sil(wd, "gc")}{bz_svg(wd, glow)}<i class="s s1">{cp}</i><i class="s s2">{cp}</i></div></div>')


def blocks(n, d0, d1, seed):
    """まわりの小さなブロック（ネオンの色・1コマずつ・毎回ちがう場所）"""
    rnd = random.Random(seed)
    out = ''
    for _ in range(n):
        out += (f'<i style="--x:{rnd.uniform(0, 340):.0f}px;--y:{rnd.uniform(60, 780):.0f}px;--w:{rnd.uniform(24, 90):.0f}px;--h:{rnd.uniform(4, 16):.0f}px;'
                f'--c:{rnd.choice(["#FF2BD6", "#2FF3FF", "#FFF23A", "#3CFF6A", "#FFFFFF"])};--d:{fz_sec(rnd.uniform(d0, d1))};--t:.034s"></i>')
    return f'<div class="bk">{out}</div>'


# T1〜T3 の「どてき！！」：(字, x, y, 大きさ, 傾き)。ど・て・き と「！」「！」（音の gen_sfx.py も、この順と時刻で鳴らす）
DOTEKI = 'どてき！！'


def mt_layers(seed=71):
    """虹色ネオンのカット（T1〜T5）：まさちゃんの指定の文字「どてき！！」「どてき！！」「どてき！！どてき！！」「ど！ど！ど！ど！」「ど的中！！！！」
       文字は筆の字（パチンコのロゴのような字体と虹色）。どてき！！・ど！は1文字ずつ大きくバグる（場所・大きさ・向きはバラバラ）、ど的中は止まる。
       パチンコの当たりのように速く・激しく：文字はたたきつけるように出て、「！」「ど！」「ど的中」が出るたびに爆発（星形の光・衝撃の輪・光の破片）"""
    M = FZ_T['M']
    T2, T3, T4, T5 = (M + MT_T[k] for k in ('T2', 'T3', 'T4', 'T5'))
    rnd = random.Random(seed)
    # T1：まん中で大爆発 → 「ど」「て」「き」「！」・右に大きな「！」（爆発）
    t1 = burst(190, 420, M + .02, 290, '#FFF0FA', '#FF2BD6', 61, n=20, z=0)
    t1 += ''.join(gq(c, x, y, fs, M + .05 + i * .05, 'pink', r, seed=10 + i, z=6 - i) for i, (c, x, y, fs, r) in enumerate(
        (('ど', 104, 240, 200, -12), ('て', 282, 330, 178, 9), ('き', 112, 560, 196, 7), ('！', 276, 636, 186, -8))))
    t1 += burst(332, 472, M + .27, 210, '#E8FFFF', '#3FF4FF', 62, n=12, z=0) + gq('！', 332, 472, 212, M + .27, 'pink', 14, seed=14, z=7)
    t1 += blocks(8, M + .06, M + .5, 21)
    # T2：左上から右下へ階段のように（最後の「！」で爆発）
    t2 = ''.join(gq(c, x, y, fs, T2 + .03 + i * .045, 'blue', r, seed=20 + i, z=9 - i) for i, (c, x, y, fs, r) in enumerate(
        (('ど', 80, 168, 172, -10), ('て', 162, 322, 156, 8), ('き', 240, 480, 174, -6), ('！', 292, 636, 164, 12), ('！', 338, 762, 170, 18))))
    t2 += burst(338, 762, T2 + .21, 250, '#FFE8FA', '#FF4FD8', 63, n=12, z=0) + blocks(8, T2 + .04, T2 + .48, 22)
    # T3：「どてき！！」を2つ（大きく・画面からはみ出てもいい。上は右上がり・下は右下がり。1文字ずつ上下にずらす。最後の「！」で爆発）
    t3 = ''
    for k, (x0, y0, x1, y1, fs, d0, pal, c1, c2) in enumerate(((36, 404, 362, 86, 134, T3 + .03, 'gold', '#FFF8C0', '#FFB300'),
                                                               (36, 548, 362, 796, 132, T3 + .22, 'green', '#F0FFC8', '#3CFF6A'))):
        for i, c in enumerate(DOTEKI):
            u = i / 4
            x, y = round(x0 + (x1 - x0) * u), round(y0 + (y1 - y0) * u + rnd.uniform(-12, 12))
            t3 += gq(c, x, y, fs + rnd.randint(-6, 12), d0 + i * .04, pal, round(rnd.uniform(-12, 12)), seed=30 + k * 10 + i, z=19 - k * 10 - i)
            if i == 4:
                t3 += burst(x, y, d0 + i * .04, 240, c1, c2, 64 + k, n=12, z=0)
    t3 += blocks(8, T3 + .03, T3 + .52, 23)
    # T4：「ど！」×4（大きく・はみ出てもいい・バラバラ・1つずつ光の破片が飛び散る）
    t4 = ''
    for i, (x, y, fs, r, pal) in enumerate(((158, 172, 196, -12, 'pink'), (238, 370, 182, 10, 'blue'), (148, 566, 204, 7, 'gold'), (240, 752, 190, -9, 'green'))):
        d = T4 + .12 + i * .17
        t4 += burst(x, y, d, 420, BZ_PAL[pal][2], BZ_PAL[pal][3], 70 + i, n=18, star=False, ring=False, z=0) + gq('ど！', x, y, fs, d, pal, r, seed=40 + i)
    t4 += blocks(10, T4 + .12, T4 + .85, 24)
    # T5：「ど的中」（大爆発・光がサッと走る）「！！！！」（そろってから HOLD 秒）
    t5 = burst(195, 365, T5 + .02, 320, '#FFFBE0', '#FF5A00', 80, n=22, ring=False, z=0)
    t5 += bzt('ど的中', 195, 360, 134, T5 + .02, 'white', r=-6, z=2, scales=(.78, 1, 1), dys=(-150, 0, 0), kern=-90, shine=fz_sec(T5 + .35))
    for i, ((x, y, fs, r), pal) in enumerate(zip(((58, 530, 108, -14), (148, 566, 120, 8), (240, 518, 104, -6), (326, 568, 116, 12)), ('pink', 'gold', 'green', 'blue'))):
        t5 += bzt('！', x, y, fs, T5 + .08 + i * .05, pal, r=r, z=3 + i)
    t5_rings = ''.join(f'<i class="rg" style="--s:{sz}px;--d:{fz_sec(T5 - k * .4)}"></i>' for k, sz in enumerate((250, 410, 600, 830)))
    t5_waves = '<div class="rw">' + ''.join(f'<i style="--d:{fz_sec(T5 + k * .45)}"></i>' for k in range(3)) + '</div>'
    html = f'''<div class="mt" aria-hidden="true">
      <div class="sc t1"><div class="bg"></div><div class="dk"></div>{neon_icon()}<div class="dk2"></div>{t1}</div>
      <div class="sc t2"><div class="stf"></div><div class="spd"></div><div class="orb"></div><div class="spk">{sparkles(26, 47)}</div>{t2}</div>
      <div class="sc t3"><div class="zz">{zigzag()}</div>{t3}</div>
      <div class="sc t4"><div class="stf"></div><div class="glw"></div><div class="spk">{sparkles(22, 43, white=True)}</div>{t4}</div>
      <div class="sc t5"><div class="nr g"></div><div class="nr"></div><div class="nw"></div>{t5_waves}{t5_rings}<div class="core"></div><div class="bsg"><div class="bs"></div></div>
        <div class="spk">{sparkles(34, 59)}</div>{t5}</div>
    </div>'''
    return dict(css='', html=html)


def embers(n, seed):
    """虹色のきらめき（下から上へ）"""
    rnd = random.Random(seed)
    R = FZ_T['R']
    return ''.join(f'<i style="--x:{rnd.uniform(0, 390):.0f}px;--s:{rnd.uniform(3, 6):.1f}px;--t:{rnd.uniform(1.6, 3.2):.2f}s;--d:{R + rnd.uniform(0, 2):.2f}s;--dx:{rnd.uniform(-60, 60):.0f}px;'
                   f'--c:hsl({i * 360 // n},100%,62%)"></i>' for i in range(n))


def dlogo():
    """結果の上の「ど的中」：筆の字（虹色・金と黒のふち・金の立体・つや・光がサッと走る）＋うしろの炎＋上の小さい英語＋きらめき"""
    R = FZ_T['R']
    wd = bz_word('ど的中', 156, rb=1, kern=-90, scales=(.78, 1, 1), dys=(-100, 0, 0), shine=fz_sec(R + .3))
    word = f'<div class="dw" style="--w:{wd["W"]:g}px;--h:{wd["H"]:g}px">{bz_svg(wd, "#FFB000")}</div>'
    glints = ''.join(f'<b style="--x:{x}px;--y:{y}px;--s:{s}px;--d:{R + .3 + i * .12:.2f}s"></b>'
                     for i, (x, y, s) in enumerate(((52, 70, 22), (150, 44, 28), (262, 40, 24), (352, 92, 30), (300, 178, 20), (86, 176, 24))))
    rnd = random.Random(23)
    flames = ''
    for i in range(15):
        cx = 12 + i * 26.3 + rnd.uniform(-7, 7)
        w, h, base = rnd.uniform(46, 78), rnd.uniform(120, 200) * (1.15 if 4 <= i <= 10 else .85), 168 + rnd.uniform(-6, 6)
        d = (f'M{cx - w / 2:.0f} {base:.0f} C{cx - w / 2:.0f} {base - h * .45:.0f} {cx - w * .12:.0f} {base - h * .55:.0f} {cx + rnd.uniform(-6, 6):.0f} {base - h:.0f} '
             f'C{cx + w * .12:.0f} {base - h * .55:.0f} {cx + w / 2:.0f} {base - h * .45:.0f} {cx + w / 2:.0f} {base:.0f} Z')
        flames += f'<path d="{d}" fill="url(#dflg)" style="--t:{rnd.uniform(.45, .7):.2f}s;--d:{-rnd.uniform(0, .6):.2f}s"></path>'
    flames = f'<g mask="url(#dflk)">{flames}</g>'
    grad = ('<defs><linearGradient id="dflg" x1="0" y1="0" x2="390" y2="0" gradientUnits="userSpaceOnUse">'     # 虹色の炎（横に虹色）
            + ''.join(f'<stop offset="{o:g}" stop-color="{c}"></stop>' for o, c in BZ_RB)
            + '</linearGradient><linearGradient id="dflm" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"></stop>'
            '<stop offset=".12" stop-color="#FFFFFF"></stop><stop offset=".55" stop-color="#FFFFFF" stop-opacity=".85"></stop><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"></stop>'
            '</linearGradient><mask id="dflk" maskUnits="userSpaceOnUse" x="0" y="-60" width="390" height="260"><rect x="0" y="-60" width="390" height="260" fill="url(#dflm)"></rect></mask></defs>')
    return (f'<div class="dlg" role="img" aria-label="ど的中"><div class="dfl"></div><svg class="ffl" viewBox="0 0 390 200" aria-hidden="true">{grad}{flames}</svg>'
            f'<div class="dr"></div><div class="dsb">SUPER LONGSHOT</div>{word}<div class="dsp">{glints}</div></div>')


def fz_layers(bets, total, kind='fz'):
    """フリーズの押したあと（下から）：黒 → 結果（虹色の大当たりの画面・上に「ど的中」・テーマのボード）→ ネオンのカット → 押した瞬間のフリーズ（プチュン）→ 白い光
       kind：fz（超大穴の馬の帯）／hidden（隠れど的中：デカ的中が化けた帯）"""
    if kind == 'hidden':
        rib = '<div class="zrib"><b class="zt">隠れ</b><span>デカ的中が ど的中に化けた！</span></div>'
        bd = board('hidden', bets, total, rib=rib)
    else:
        rib = f'<div class="zrib"><b class="zt">超大穴</b>{num(FZ_X, " zx")}<span>{FZ_X}番人気が3連単に！</span></div>'
        bd = board('fz', bets, total, rib=rib, mark=(FZ_X,))
    R = FZ_T['R']
    return f'''{bz_defs()}<div class="blk"></div>
    <div class="fin"><div class="fsk">
      <div class="fb"></div><div class="frr"></div><div class="frg"><i style="--d:{fz_sec(R + .1)}"></i><i style="--d:{fz_sec(R + 1)}"></i></div>
      {burst(195, 330, R + .02, 520, '#FFFFFF', '#FF3BD2', 90, n=22)}
      <div class="emb">{embers(36, 11)}</div>
      <div class="conf cb">{coins(22, 8, R)}</div>
      <div class="hb">{bd}</div>
      {dlogo()}
      <div class="conf">{confetti(40, 7, rainbow=True, d0=R)}</div>
    </div></div>
    {MT['html']}
    {FZ_HTML}
    <div class="xf" aria-hidden="true"><div class="rfl"></div></div>'''


FZ_HTML = freeze_layers()
MT = mt_layers()


PAGES = dict(   # 種類 → ファイル名・名前（見本の画面のタイトル）
    hit=('Fx_Hit.dc.html', '的中ボタン（デフォルト）'), big=('Fx_Big.dc.html', 'デカ的中ボタン（デフォルト）'),
    fz=('Fx_Freeze.dc.html', 'フリーズ的中ボタン（デフォルト）'), hidden=('Fx_Hidden.dc.html', '隠れど的中（デカ的中ボタン → ど的中）'),
    miss=('Fx_Miss.dc.html', 'ハズレ（ボードだけ）'))
BETS_HIT = [('馬単', [6, 2], '→', '100円', '1,840円', True), ('馬連', [2, 6], '-', '100円', '690円', True), ('3連単', [6, 10, 2], '→', '100円', '0円', False)]
BETS_BIG = [('3連単', [6, 2, 10], '→', '100円', '48,920円', True), ('馬単', [6, 2], '→', '100円', '1,840円', True), ('ワイド', [2, 10], '-', '100円', '0円', False)]
BETS_FZ = [('3連単', [FZ_X, 6, 2], '→', '100円', '286,370円', True), ('馬単', [FZ_X, 6], '→', '100円', '24,180円', True), ('ワイド', [2, FZ_X], '-', '100円', '4,950円', True)]
BETS_MISS = [('3連単', [6, 2, 10], '→', '100円', '0円', False), ('馬単', [6, 2], '→', '100円', '0円', False), ('ワイド', [2, 10], '-', '100円', '0円', False)]


def page(kind):
    """見本の画面（記録する → PUSH → タップ → 結果のボード）。kind：hit・big・fz・hidden（デカのPUSH → ど的中）・miss（PUSHなし）"""
    big = kind in ('big', 'hidden')          # PUSHはデカ（隠れど的中もデカのPUSH）
    fz = kind in ('fz', 'hidden')            # 押したあとは、ど的中
    fin = (6, 2, 10)
    if kind == 'fz':
        bets, total, fin = BETS_FZ, '315,500円', (FZ_X, 6, 2)
        note = f'3連単が当たって、3頭の中に超大穴（10〜12番人気）がいるので、記録するとフリーズ的中ボタンが出るよ（見本・架空のレース。{FZ_X}番が{FZ_X}番人気）'
    elif kind == 'hidden':
        bets, total = BETS_BIG, '50,760円'
        note = '3連単が当たったのでデカ的中ボタン。デカ的中の2〜7回に1回（ランダム）は隠れど的中で、押すとど的中になるよ（見本・架空のレース）'
    elif kind == 'big':
        bets, total, note = BETS_BIG, '50,760円', '3連単が当たったので、記録するとデカ的中ボタンが出るよ（見本・架空のレース）'
    elif kind == 'miss':
        bets, total, fin = BETS_MISS, '0円', (7, 1, 4)
        note = '外れたので、記録するとハズレのボードだけが出るよ（ボタンなし・見本・架空のレース）'
    else:
        bets, total, note = BETS_HIT, '2,530円', '3連単は外れ・馬単と馬連が当たったので、記録すると的中ボタンが出るよ（見本・架空のレース）'
    pb = ' big' if big else ''
    push = f'''  <sc-if value="{{{{isPush}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov{pb}">
    <div class="dim"></div>
    {'<div class="spk">' + sparkles(22, 5) + '</div>' if big else ''}
    <div class="pbox">
      <button class="push{pb}" type="button" onClick="{{{{toReveal}}}}" aria-label="{'デカ的中ボタン' if big else '的中ボタン'}">{'<i class="halo" aria-hidden="true"><i><b></b></i></i>' if big else ''}<span>PUSH</span></button>
      <div class="pshadow{pb}"></div>
      <p class="tap{pb}">タップ！</p>
    </div>
  </div>
  </sc-if>'''
    nhit = len(bets) if kind == 'miss' else sum(1 for b in bets if b[5])
    if kind == 'big':
        layers = ('<div class="rbow"></div><div class="glow"></div><div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>'
                  '<div class="spk">' + sparkles(26, 9) + '</div>'
                  + burst(195, 371, .04, 600, '#FFF6C8', '#FFB21A', 5, n=18, z=5)          # 押した瞬間の爆発
                  + burst(195, 420, .55, 660, '#FFFFFF', '#FF3BB8', 6, n=14, star=False, z=5)   # ボードの着地（ボードのうしろ・輪と光の破片だけ）
                  + burst(195, 316, .7, 300, '#FFFFFF', '#FFE53B', 7, n=0, star=False, z=7))   # 「デカ的中!!」の輪
        conf, flash, cls = confetti(34, 3, rainbow=True), '<div class="flash"></div>', ' big big rv'
    elif kind == 'miss':
        layers, conf, flash, cls = '', '', '', ' miss'
    else:
        layers, conf, flash, cls = '<div class="rays"></div>', confetti(28, 2), '', ' hit'
    reveal = f'''  <sc-if value="{{{{isReveal}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov{cls}" style="--n:{nhit}">
    <div class="dim"></div>
    {layers}
    {'' if kind == 'miss' else f'<div class="pressed{pb}"></div>'}
    <div class="hb">{board(kind, bets, total)}</div>
    {f'<div class="conf">{conf}</div>' if conf else ''}
    {flash}
    <button class="close" type="button" onClick="{{{{toForm}}}}">とじる</button>
  </div>
  </sc-if>'''
    if kind == 'fz':
        push = f'''  <sc-if value="{{{{isPush}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov fz">
    {fz_push()}
  </div>
  </sc-if>'''
    if fz:
        reveal = f'''  <sc-if value="{{{{isReveal}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov fz" style="--n:{nhit}">
    {fz_layers(bets, total, kind)}
    <button class="close" type="button" onClick="{{{{toForm}}}}">とじる</button>
  </div>
  </sc-if>'''
    if kind == 'miss':
        push = ''
    css = COMMON_CSS.replace('RANCH', RANCH_VARS)
    if fz:
        css += BIG_CSS + BURST_CSS + fz_css()
    elif kind == 'big':
        css += BIG_CSS + BURST_CSS
    elif kind == 'miss':
        css += MISS_CSS
    else:
        css += HIT_CSS
    css += board_css([THEME])
    fn, name = PAGES[kind]
    starts = '["form","reveal"]' if kind == 'miss' else '["form","push","reveal"]'
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{name}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&amp;display=swap">
<style>
{css}
</style>
</helmet>
<div class="ph">
{HEADER}
{form(bets, total, note, fin)}
{push}
{reveal}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"start":{{"editor":"enum","options":{starts},"default":"form"}},"$preview":{{"width":390,"height":844}}}}'>
{page_js(kind)}</script>
</body>
</html>
'''


# ---------- 結果のボードの一覧（26テーマ × 的中・ハズレ ＋ ボードの種類） ----------
CELL_W, COLS, GGAP, GPAD = 752, 5, 28, 40
BOARDS_W, BOARDS_H = 2 * GPAD + COLS * CELL_W + (COLS - 1) * GGAP, 3860
OLD_DESC = dict(default='紺×金', ranch='黄緑', cute='ピンク', kids='薄い黄色×パウダーホワイト', gold='金色')


def theme_label(t):
    from themes20 import THEMES as T20
    for x in T20:
        if x['id'] == t['id']:
            return x['title']
    return f"{t['name']}（{OLD_DESC.get(t['id'], '')}）"


def boards_page():
    """26テーマの結果のボード（的中・ハズレ）と、ボードの種類（見本：いつもの）。動きなし・テーマの字はGoogle Fonts"""
    ids = [t['id'] for t in ORDERED]
    rib_fz = f'<div class="zrib"><b class="zt">超大穴</b>{num(FZ_X, " zx")}<span>{FZ_X}番人気が3連単に！</span></div>'
    rib_hd = '<div class="zrib"><b class="zt">隠れ</b><span>デカ的中が ど的中に化けた！</span></div>'
    kinds = [('hit', BETS_HIT, '2,530円', '', (), '的中（当たり）'), ('big', BETS_BIG, '50,760円', '', (), 'デカ的中（3連単が当たり）'),
             ('fz', BETS_FZ, '315,500円', rib_fz, (FZ_X,), 'ど的中（3連単に超大穴）'),
             ('hidden', BETS_BIG, '50,760円', rib_hd, (), '隠れど的中（デカ的中の2〜7回に1回）'), ('miss', BETS_MISS, '0円', '', (), 'ハズレ（ボタンなし）')]
    var = ''.join(f'<figure>{board(k, b, tot, rib=rb, mark=mk, tid="default")}<figcaption>{cap}</figcaption></figure>' for k, b, tot, rb, mk, cap in kinds)
    var += ('<div class="vnote"><h3>ボードの決まり</h3><ul>'
            '<li>どのテーマも同じ形：<b>ふち</b>（背景のもよう）→ <b>上の帯</b>（見出し）→ <b>カード</b>（買い目）・すみに<b>飾り</b>。色・字・もよう・飾りは、そのテーマの判定画面と同じ</li>'
            '<li><b>的中</b>：見出しはテーマのロゴの字と色 ／ <b>デカ的中</b>：虹色の見出しと光るふち・3連単の行に虹色のふち ／ <b>ど的中・隠れど的中</b>：虹色の枠と炎の光・見出しの下に帯 ／ <b>ハズレ</b>：静かな見出し・入れた買い目を全部・払戻0円</li>'
            '<li><b>隠れど的中</b>：デカ的中の2〜7回に1回（ランダム）。デカのPUSHを押すと、そのまま、ど的中の演出 →「隠れど的中！！！」</li>'
            '<li>払戻が長いと、その行の払戻だけ次の行へ。<b>馬番の枠の色は全テーマ同じ</b></li></ul></div>')
    groups = ''
    for c in CAT_ORDER:
        ts = [t for t in ORDERED if t['cat'] == c]
        cells = ''
        for t in ts:
            cells += (f'<section class="cell"><h3>{theme_label(t)}</h3><div class="pair">'
                      f'<figure><span class="lb">的中</span>{board("hit", BETS_HIT, "2,530円", tid=t["id"])}</figure>'
                      f'<figure><span class="lb">ハズレ</span>{board("miss", BETS_MISS, "0円", tid=t["id"])}</figure></div></section>')
        groups += f'<h2 class="gh">{CATS[c]}<small>{len(ts)}テーマ</small></h2><div class="grid">{cells}</div>'
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>結果のボード（26テーマ）</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{theme_fonts(ids, extra=['BIZ+UDPGothic:wght@400;700', 'Dela+Gothic+One'])}
<style>
body{{margin:0}}
*{{box-sizing:border-box}}
.gd{{width:{BOARDS_W}px;height:{BOARDS_H}px;overflow:hidden;background:#F4F2EC;color:#22252E;font-family:"BIZ UDPGothic",sans-serif;padding:34px {GPAD}px 0}}
.t1{{margin:0;font-family:"Dela Gothic One",sans-serif;font-weight:400;font-size:34px;line-height:1.2;color:#161F3D}}
.t2{{margin:10px 0 0;max-width:2400px;font-size:15px;line-height:1.75;color:#4E5466}}
.t2 b{{color:#22252E}}
.vr{{margin-top:22px;padding:18px 24px 22px;border-radius:18px;background:#1E1A2C}}
.vr h2{{margin:0 0 16px;font-size:19px;color:#FFFFFF}}
.vr h2 small{{margin-left:10px;font-size:13px;font-weight:700;color:#CFC8E8}}
.vrow{{display:flex;gap:26px;align-items:flex-start}}
.vrow figure{{margin:0;display:flex;flex-direction:column;align-items:center;gap:12px}}
.vrow figcaption{{font-size:14px;font-weight:700;color:#ECE8F8}}
.vnote{{flex:1;min-width:0;margin-left:14px;padding:16px 22px 14px;border-radius:14px;background:rgba(255,255,255,.07);color:#E6E2F4}}
.vnote h3{{margin:0 0 8px;font-size:16px;color:#FFFFFF}}
.vnote ul{{margin:0;padding-left:1.2em}}
.vnote li{{margin:0 0 7px;font-size:14px;line-height:1.75}}
.vnote b{{color:#FFFFFF}}
.gh{{display:flex;align-items:baseline;gap:10px;margin:30px 0 14px;font-size:21px;color:#161F3D}}
.gh small{{font-size:13px;font-weight:700;color:#8A6A38}}
.grid{{display:grid;grid-template-columns:repeat({COLS},{CELL_W}px);gap:{GGAP}px}}
.cell{{border-radius:16px;background:#2A231D;padding:12px 16px 18px}}
.cell h3{{margin:0 0 12px;font-size:16px;line-height:1.3;color:#FFFFFF}}
.pair{{display:flex;gap:20px;align-items:flex-start}}
.pair figure{{margin:0;display:flex;flex-direction:column;gap:7px}}
.pair .lb{{font-size:12px;font-weight:700;color:#D6CBB8}}
{board_css(ids)}
</style>
</helmet>
<div class="gd">
  <h1 class="t1">結果のボード（壁紙のテーマごと・26テーマ）</h1>
  <p class="t2">まさちゃんの指定：結果は<b>馬がボードを持つのをやめて、壁紙のテーマに沿ったボード</b>に（的中もハズレも）。ボードは、そのテーマの判定画面をぎゅっと小さくした形：<b>ふち＝背景のもよう・見出し＝上の帯（ロゴと同じ字と色）・買い目＝カード・すみの飾り</b>。色は判定画面と同じ（文字と背景のコントラストは確かめずみの値）。デカ的中は虹色の見出しと光るふち、ど的中・隠れど的中は虹色の枠と炎の光、ハズレは静かな見出しで払戻0円。<b>馬番の枠の色はどのテーマも同じ</b>。見本の画面（となりの5つ）は牧場のボード。</p>
  <section class="vr"><h2>ボードの種類<small>見本：いつもの（紺×金）</small></h2><div class="vrow">{var}</div></section>
  {groups}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{BOARDS_W},"height":{BOARDS_H}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


# ---------- 効果音（gen_sfx.py で作った音。fx_blobs.json の snd_… があれば、見本の画面で鳴らす） ----------
SND = {'hit': ('snd_hit_push', 'snd_hit'), 'big': ('snd_big_push', 'snd_big'), 'fz': ('snd_fz_push', 'snd_fz'),
       'hidden': ('snd_big_push', 'snd_fz')}     # 隠れど的中：PUSHはデカの音・タップはど的中の音（ハズレは音なし）
WAVES = json.load(open(f'{K}/sfx_wave.json')) if os.path.exists(f'{K}/sfx_wave.json') else None

# 鳴らす部品（Web Audio。読み込みは先に・鳴らすのは押したときだけ・押した瞬間を0秒にして動きとそろえる）
SFX_JS = '''  sfxDecode(c, b) {
    return new Promise(function (ok) {
      try { var q = c.decodeAudioData(b, ok, function () { ok(null); }); if (q && q.catch) q.catch(function () { ok(null); }); } catch (e) { ok(null); }
    });
  }
  sfxInit() {
    // 音は先に読んで、音のデータにしておく（鳴らすのは押したときだけ）
    if (this._sx) return this._sx;
    var self = this, sx = this._sx = { raw: {}, buf: {}, ctx: null, src: null, el: null, id: 0, ok: 0 };
    var urls = this.sfxUrls(), dec = null;
    var OC = typeof window === 'undefined' ? null : (window.OfflineAudioContext || window.webkitOfflineAudioContext);
    if (OC) { try { dec = new OC(2, 44100, 44100); } catch (e) { dec = null; } }
    if (typeof fetch === 'function') {
      Object.keys(urls).forEach(function (k) {
        sx.raw[k] = fetch(urls[k]).then(function (r) { return r.ok ? r.arrayBuffer() : null; }).catch(function () { return null; });
        if (dec) sx.buf[k] = sx.raw[k].then(function (b) { return b ? self.sfxDecode(dec, b.slice(0)) : null; });
      });
    }
    return sx;
  }
  sfx(k, from, wait, done) {
    // 押した瞬間を0秒として、音の from 秒の所から wait 秒後に鳴らす（読むのが0.1秒より遅れたら、遅れたぶん先から鳴らして動きとそろえる）
    var self = this, sx = this.sfxInit();
    this.hush();
    var id = sx.id, t0 = Date.now(), url = this.sfxUrls()[k];
    var end = function () { if (done && id === sx.id) done(); };
    from = from || 0;
    wait = wait || 0;
    var AC = typeof window === 'undefined' ? null : (window.AudioContext || window.webkitAudioContext);
    if (!sx.ctx && AC) { try { sx.ctx = new AC(); } catch (e) { sx.ctx = null; } }
    var ctx = sx.ctx;
    if (!ctx || !sx.raw[k]) {
      if (from || wait || typeof Audio === 'undefined') { end(); return; }
      try { var a = new Audio(url); a.onended = end; sx.el = a; var p = a.play(); if (p && p.catch) p.catch(end); } catch (e) { end(); }
      return;
    }
    if (ctx.state !== 'running' && ctx.resume) { try { ctx.resume(); } catch (e) {} }
    if (!sx.ok) {
      sx.ok = 1;
      try { var s0 = ctx.createBufferSource(); s0.buffer = ctx.createBuffer(1, 1, 22050); s0.connect(ctx.destination); s0.start(0); } catch (e) {}
    }
    (sx.buf[k] || Promise.resolve(null)).then(function (buf) {
      // 先に読めなかったときは、鳴らす方で読みなおす
      return buf || sx.raw[k].then(function (b) { return b ? self.sfxDecode(ctx, b.slice(0)) : null; });
    }).then(function (buf) {
      if (id !== sx.id) return;
      var el = (Date.now() - t0) / 1000, late = Math.max(0, el - wait), off = from + (late > .1 ? late : 0);
      if (!buf || off >= buf.duration) { end(); return; }
      var s = ctx.createBufferSource();
      s.buffer = buf;
      s.connect(ctx.destination);
      s.onended = end;
      s.start(ctx.currentTime + Math.max(0, wait - el), off);
      sx.src = s;
    });
  }
  hush() {
    var sx = this._sx;
    if (!sx) return;
    sx.id++;
    if (sx.src) { try { sx.src.stop(); } catch (e) {} sx.src = null; }
    if (sx.el) { try { sx.el.pause(); } catch (e) {} sx.el = null; }
  }
  slow() {
    // iPhoneの「視差効果を減らす」
    return typeof window !== 'undefined' && !!window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
'''


def page_js(kind):
    """見本の画面のスクリプト。音があれば：記録する → PUSHの音／PUSHをタップ → タップの音（フリーズは視差効果を減らすなら1秒後に結果の所から）／とじる → 止める
       ハズレ：記録する → すぐボード（PUSHなし・音なし）"""
    ids = [blobs.get(k) for k in SND.get(kind, ())]
    on, head, init = dict(push='', tap='', form=''), '', ''
    if ids and all(ids):
        tap = "self.sfx('tap'); "
        if kind in ('fz', 'hidden'):
            tap = f"if (self.slow()) self.sfx('tap', {FZ_T['R']:g}, 1); else self.sfx('tap'); "
        on = dict(push="self.sfx('push'); ", tap=tap, form='self.hush(); ')
        head = f"  sfxUrls() {{\n    return {{ push: '/_blob/{ids[0]}', tap: '/_blob/{ids[1]}' }};\n  }}\n" + SFX_JS
        init = '    this.sfxInit();\n'
    return ('class Component extends DCLogic {\n' + head
            + '  renderVals() {\n' + init
            + "    var st = this.state || {};\n"
            + "    var ph = st.ph || this.props.start || 'form';\n"
            + "    var self = this;\n"
            + "    return {\n"
            + "      isPush: ph === 'push',\n"
            + "      isReveal: ph === 'reveal',\n"
            + f"      toPush: function () {{ {on['push']}self.setState({{ ph: '{'reveal' if kind == 'miss' else 'push'}' }}); }},\n"
            + f"      toReveal: function () {{ {on['tap']}self.setState({{ ph: 'reveal' }}); }},\n"
            + f"      toForm: function () {{ {on['form']}self.setState({{ ph: 'form' }}); }}\n"
            + "    };\n"
            + "  }\n"
            + "}\n")


SOUND_W, SOUND_H = 2200, 1470
SND_INFO = (   # キー・見出し・小見出し・PUSHの音・色・目もり（秒）
    ('hit', '的中ボタン', '当たったとき・ハ長調（明るく軽く）', 'ピロリン↑（鐘が3つ上がる）＋キラキラ', ('#C8281F', '#FF9A3C'), .5),
    ('big', 'デカ的中ボタン', '3連単が当たったとき・ニ長調・重く重低音で（速く勢いよく）', 'ドゥン（重低音）＋キュイーン↑（低めから）＋低いうなり', ('#7B4CFF', '#FF3BB8'), .5),
    ('fz', 'ど的中ボタン（フリーズ的中ボタン）', '3連単の当たりに超大穴（10〜12番人気）<br>ホ長調・低音と重低音（いちばん派手）', 'ドォォン（重低音）＋グォォォン↑（低いうなりが1オクターブ上がる）＋低いどら',
     ('#FF3B3B', '#FF9F1A', '#FFE53B', '#3BE26A', '#2FD6FF', '#4C6BFF', '#B34CFF', '#FF3BB8'), 1.0),
)


def snd_events():
    """タップの音の中身（秒・終わり・音・画面）。フリーズは FZ_T の時刻"""
    B, W, Z, M, R = (FZ_T[k] for k in 'BWZMR')
    T4, T5 = M + MT_T['T4'], M + MT_T['T5']
    return {
        'hit': [(0, None, 'ポン', '押した'), (.22, .97, 'ヒュイーン↑', 'ボードが下から'), (.95, None, 'キラーン', '「的中！」'),
                (1.15, 1.3, 'ピン・ポン', '買い目が1行ずつ'), (1.6, None, 'チャリーン', '払戻の合計（コイン）')],
        'big': [(0, None, 'ガツッ', '押した'), (.04, None, 'ドォォン!!', '白く光る・爆発・虹の光の筋'), (.1, None, 'キュウィン', '虹の輪①（下にドン）'),
                (.25, None, 'キュウィン', '虹の輪②（少し高く）'), (.4, None, 'キュウィン', '虹の輪③（もっと高く）'),
                (.55, None, 'ズドン', 'ボードが落ちてきて着地（0.38秒〜）'), (.7, None, 'ジャーン!!', '「デカ的中!!」（低い金管）'),
                (.9, .98, 'ピン・ピン', '買い目（0.08秒おき）'), (1.14, None, 'パッパッ＋ジャラジャラ', '払戻の合計（メダル）'), (1.4, None, 'パーン', 'ファンファーレ')],
        'fz': [(0, None, 'ドンッ（重低音）＋ギュッ↓', '押した瞬間にフリーズ（白く光る）'), (0, W, 'ビーーッ（角ばった電子音）＋ザザッ・チリチリ', '横に流れる帯・赤い粒（コマに合わせて揺れる・途切れる）'),
               (B, B + .11, 'ヴォン・ヴォン（低い）', '青い画面・白い光がふくらむ'), (W, None, 'ブツッ（電子音がいきなり消える）', '青白い横一本線'),
               (W, Z + .15, 'バチバチッ・ジジッ', '線にまとわりつく細い電気（コマごとに形が変わる）'), (Z, Z + .2, 'ヒュゥン↓ → プツッ', '点に縮んで消える・光の粒'),
               (Z + .2, M, '無音', '真っ暗（フリーズの間）'),
               (M, T4, 'ドガーン!! → ドドド・ドガッ・ドガン×4', '大爆発 →「どてき！！」ど・て・き は1文字ずつ小さな爆発・「！」でドガッ・「！」で爆発（低いベースが刻む）'),
               (T4 + .12, T4 + .63, 'ドガン×4（だんだん高く）', '「ど！」×4（重低音の爆発）'), (T4 + .71, T5, 'ドドドドッ', '低いタムの連打'),
               (T5, None, 'ドガーン!!＋低い金管', '「ど的中！！！！」大爆発'), (T5 + .45, R, 'ドン・ドン（0.45秒ごと）', '光の波と輪に合わせて（小さな爆発）'),
               (R, R + .3, '大爆発 → ズドン＋ジャーン', '結果（虹色の大当たりの画面）→ ボードの着地・「ど的中！！！」'),
               (R + .45, R + .69, 'ボン・ボン・ボン → ゴーン＋ジャラジャラ', '買い目（0.08秒おき）→ 払戻の合計（メダル）')],
    }


def ssec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def wave_svg(key, name, wv, evs, cols, step):
    """タップの音の波形（音の大きさ・dB）と、番号つきの印・秒の目もり"""
    PX, WW, MT, WH = 14, 1664, 30, 92
    TW, TH = PX * 2 + WW, MT + WH + 26
    d, h = wv['d'], wv['h']
    X = lambda t: PX + t / d * WW
    mid, amp, n = MT + WH / 2, WH / 2 - 2, len(h)
    pts = [(X(0), 0)] + [(X((i + .5) * d / n), max(v, .015) * amp) for i, v in enumerate(h)] + [(X(d), 0)]
    poly = ' '.join(f'{x:.0f},{mid - a:.0f}' for x, a in pts) + ' ' + ' '.join(f'{x:.0f},{mid + a:.0f}' for x, a in reversed(pts))
    stops = ''.join(f'<stop offset="{i / max(1, len(cols) - 1):.3f}" stop-color="{c}"></stop>' for i, c in enumerate(cols))
    band = ''.join(f'<rect x="{X(t0):.1f}" y="{MT}" width="{X(t1) - X(t0):.1f}" height="{WH}" rx="4" fill="#161F3D" fill-opacity=".07"></rect>'
                   for t0, t1, *_ in evs if t1)
    marks = ''
    for i, (t0, *_) in enumerate(evs, 1):
        x = X(t0)
        marks += (f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{MT - 4}" y2="{MT + WH}" stroke="#22252E" stroke-opacity=".35" stroke-dasharray="3 3"></line>'
                  f'<circle cx="{x:.1f}" cy="13" r="11" class="mk"></circle>'
                  f'<text x="{x:.1f}" y="17.5" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">{i}</text>')
    ticks, t = '', 0.0
    while t <= d + 1e-6:
        x = X(t)
        ticks += (f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{MT + WH}" y2="{MT + WH + 5}" stroke="#6A7080"></line>'
                  f'<text x="{x:.1f}" y="{MT + WH + 19}" text-anchor="middle" font-size="12" fill="#6A7080">{ssec(t)}{"秒" if t == 0 else ""}</text>')
        t = round(t + step, 6)
    return (f'<svg class="wv" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}" role="img" aria-label="{name}のタップの音の大きさ（{ssec(d)}秒）" font-family="BIZ UDPGothic, sans-serif">'
            f'<defs><linearGradient id="wg{key}" x1="0" x2="1" y1="0" y2="0">{stops}</linearGradient></defs>{band}'
            f'<line x1="{PX}" x2="{PX + WW}" y1="{mid:.0f}" y2="{mid:.0f}" stroke="#22252E" stroke-opacity=".15"></line>'
            f'<polygon points="{poly}" fill="url(#wg{key})"></polygon>{marks}{ticks}</svg>')


PLAY_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"></path></svg>'
STOP_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"></rect></svg>'


def sound_page():
    """効果音のメモ：▶で聞ける・タップの音の波形と中身・アプリで鳴らすときの決まり"""
    evs_all = snd_events()
    R = FZ_T['R']
    secs = ''
    for key, name, sub, pdesc, cols, step in SND_INFO:
        wp, wt = WAVES[f'sfx_{key}_push'], WAVES[f'sfx_{key}']
        evs = evs_all[key]
        items = ''.join(f'<li><span class="no">{i}</span><span class="tx"><span class="tm">{ssec(t0)}{"〜" + ssec(t1) if t1 else ""}秒</span> <b>{snd}</b> <span class="wh">{what}</span></span></li>'
                        for i, (t0, t1, snd, what) in enumerate(evs, 1))
        secs += f'''
  <section class="sn {key}">
    <div class="sl">
      <h2>{name}<small>{sub}</small></h2>
      <button class="pl" type="button" onClick="{{{{p_{key}_push}}}}" aria-pressed="{{{{a_{key}_push}}}}">{PLAY_SVG}PUSHが出たとき<small>{ssec(wp['d'])}秒</small></button>
      <p class="pd">{pdesc}</p>
      <button class="pl" type="button" onClick="{{{{p_{key}}}}}" aria-pressed="{{{{a_{key}}}}}">{PLAY_SVG}PUSHをタップしたとき<small>{ssec(wt['d'])}秒</small></button>
      <p class="pd">右の波形（0秒＝押した瞬間。見本の画面の動きと同じ時刻）</p>
      <p class="lv">大きさ：PUSH {wp['lufs']:g}・タップ {wt['lufs']:g} LUFS</p>
    </div>
    <div class="sr">{wave_svg(key, name, wt, evs, cols, step)}<ol class="ev">{items}</ol></div>
  </section>'''
    keys = [k for k, *_ in SND_INFO]
    urls = ',\n      '.join(f"{k}_push: '/_blob/{blobs[f'snd_{k}_push']}', {k}: '/_blob/{blobs[f'snd_{k}']}'" for k in keys)
    vals = ',\n      '.join(f"p_{k}: play('{k}'), a_{k}: on === '{k}' ? 'true' : 'false'" for k in [x for k in keys for x in (f'{k}_push', k)])
    box = '<div class="box"><h3>{}</h3><ul>{}</ul></div>'.format
    boxes = (box('鳴らすとき', '<li><b>PUSHの音</b>：PUSHが出た瞬間（結果を記録して当たりのとき。3つのボタンのうち出た1つの音だけ）</li>'
                 '<li><b>隠れど的中</b>：PUSHが出たときはデカの音・タップでど的中の音（見た目もデカ → ど的中）。<b>ハズレは音なし</b></li>'
                 '<li><b>タップの音</b>：PUSHを押した瞬間が0秒。画面の動きと同じ時刻で、見本の画面（となりの3つ）でも同じに鳴る</li>'
                 '<li>「とじる」・ほかの画面へ移る・アプリを閉じる → すぐ止める。鳴っている途中で次の音が鳴るときは、前の音を止めてから</li>')
             + box('iPhoneでの鳴らし方（アプリ）', '<li><b>消音スイッチ（マナーモード）なら鳴らさない</b>・ほかのアプリの音楽は止めずに重ねる（AVAudioSession の ambient）。音量はiPhoneの音量のまま</li>'
                   '<li>設定に「効果音」オン／オフ（最初はオン）<b>※仮</b></li>'
                   f'<li>「視差効果を減らす」がオン：的中・デカは同じ音。ど的中は動きが短い（1秒真っ暗 → 結果）ので、押して1秒後に、ど的中の音の{ssec(R)}秒（結果のドォン・パッパッパーン）から鳴らす <b>※仮</b>（見本の画面も同じ）</li>')
             + box('大きさとファイル', '<li>6つ：sfx_hit_push・sfx_hit・sfx_big_push・sfx_big・sfx_fz_push・sfx_fz（AAC 160kbps・m4a・ぜんぶで約490KB）</li>'
                   '<li>大きさはそろえて、強いボタンほど少し大きく（的中 −16〜−17・デカ −13〜−14・ど的中 −13 LUFS）。いちばん大きい所も −1dB 以下（音割れしない）</li>'
                   '<li><b>デカとど的中は低音と重低音</b>：重低音はスマホのスピーカーからはほとんど出ないので、ひずませて作った倍音で低音を感じるようにして、ジャーンやファンファーレには高めの音も小さく重ねた。イヤホン・ヘッドホンだと重低音まで聞こえる。スマホのスピーカーでは的中より少し小さめに聞こえることがある</li>'
                   '<li>買い目の音は見本の行の数（的中・デカ2行・ど的中3行）。4行以上だと合計が出る前に「チャリーン」が鳴るので、アプリでは行と合計の音を分けて、出るたびに鳴らす（あとで作る）<b>※仮</b></li>')
             + box('作り方', '<li>音は全部プログラムで作った（gen_sfx.py・numpy と scipy）。<b>録音や、ほかの音のデータ（サンプル）は使っていない</b></li>'
                   '<li>鐘（FM）・金管（ノコギリ波を重ねる）・ドラム・コイン・「シュッ」（ノイズ）・キュウィン（すばやく上がるシンセ）・爆発（はじける音・爆風・重低音・地ひびき・かけら）を組み合わせて、残響・イコライザー・圧縮で仕上げ。デカとど的中は重低音のドォォン・爆発・低いうなり・低いどら・低い金管で、仕上げも低音用（ど的中は FZ_LOW・FZ_MID で重低音と低音の楽器の大きさを変えられる）</li>'
                   '<li>ど的中は gen_fx.py の時刻（FZ_T・MT_T）を読むので、動きを変えたら作り直すだけで音もそろう：python3 gen_sfx.py &lt;フォルダ&gt; → ffmpeg で m4a に</li>'))
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>効果音のメモ</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&amp;display=swap">
<style>
body{{margin:0}}
*{{box-sizing:border-box}}
.gd{{width:{SOUND_W}px;height:{SOUND_H}px;overflow:hidden;background:#F4F2EC;color:#22252E;font-family:"BIZ UDPGothic",sans-serif;padding:34px 40px 0}}
.hdr{{display:flex;align-items:flex-start;justify-content:space-between;gap:40px}}
.t1{{margin:0;font-family:"Dela Gothic One",sans-serif;font-weight:400;font-size:32px;line-height:1.2;color:#161F3D}}
.t2{{margin:8px 0 0;max-width:1560px;font-size:14.5px;line-height:1.7;color:#4E5466}}
.stop{{flex:none;display:inline-flex;align-items:center;gap:8px;height:48px;margin-top:4px;padding:0 24px;border-radius:999px;border:2px solid #161F3D;background:#FFFFFF;color:#161F3D;font-family:"BIZ UDPGothic",sans-serif;font-weight:700;font-size:15px;cursor:pointer}}
.stop svg{{width:16px;height:16px}}
.sn{{--c:#161F3D;display:grid;grid-template-columns:360px minmax(0,1fr);gap:28px;margin-top:16px;background:#FFFFFF;border:1px solid #DDD8CC;border-radius:14px;padding:16px 20px}}
.sn.hit{{--c:#C8281F}}
.sn.big{{--c:#7B4CFF}}
.sn.fz{{border:2px solid transparent;background:linear-gradient(#FFFFFF,#FFFFFF) padding-box,linear-gradient(90deg,#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8) border-box}}
.sn h2{{margin:0;font-size:19px;line-height:1.3;color:#161F3D}}
.sn h2 small{{display:block;margin-top:4px;font-size:12.5px;font-weight:700;color:#8A6A38}}
.pl{{display:flex;align-items:center;gap:10px;width:100%;height:48px;margin-top:12px;padding:0 16px;border-radius:12px;border:2px solid var(--c);background:#FFFFFF;color:#161F3D;font-family:"BIZ UDPGothic",sans-serif;font-weight:700;font-size:15px;text-align:left;cursor:pointer}}
.pl svg{{flex:none;width:18px;height:18px;color:var(--c)}}
.pl small{{margin-left:auto;font-size:12.5px;color:#5A6070}}
.pl[aria-pressed="true"]{{background:var(--c);color:#FFFFFF}}
.pl[aria-pressed="true"] svg,.pl[aria-pressed="true"] small{{color:#FFFFFF}}
.pd{{margin:6px 2px 0;font-size:12.5px;line-height:1.55;color:#4E5466}}
.lv{{margin:10px 2px 0;font-size:12px;color:#5A6070}}
.wv{{display:block}}
.wv .mk{{fill:var(--c)}}
.ev{{list-style:none;margin:8px 0 0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px 18px}}
.ev li{{display:grid;grid-template-columns:20px minmax(0,1fr);column-gap:7px;align-items:start;font-size:13px;line-height:20px;color:#22252E}}
.no{{display:flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--c);color:#FFFFFF;font-size:11.5px;font-weight:700;line-height:1}}
.tm{{font-size:12.5px;font-weight:700;color:#5A6070}}
.wh{{font-size:12.5px;color:#4E5466}}
.boxes{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:18px}}
.box{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:12px;padding:12px 14px}}
.box h3{{margin:0 0 6px;font-size:14px;color:#161F3D}}
.box li{{margin:0;font-size:12.5px;line-height:1.65;color:#4E5466}}
.box ul{{margin:0;padding-left:1.1em}}
.box b{{color:#22252E}}
</style>
</helmet>
<div class="gd">
  <div class="hdr">
    <div>
      <h1 class="t1">効果音（的中ボタン・デカ的中ボタン・ど的中ボタン）</h1>
      <p class="t2">まさちゃんの指定：3つのボタンに効果音（的中はOK・デカはタップでキュウィンを3回、全体を重く重低音に・ど的中は全体を低音と重低音で、「どてき！！」からは爆発のようにずっしり重く）。動きもパチンコの当たりのように速く・勢いよくした。送ってくれた3つの動画は音が入っていなかったので、それぞれの動きに合わせて新しく作った（全部プログラムで作った音。録音や、ほかの音は使っていない）。<b>ど的中のフリーズは押した瞬間</b>（まさちゃんの指定。送ってくれたパチスロのフリーズの動画のように、ドンッ＋ビーーッ…ブツッ（電子音がいきなり消える）→ 細い電気のバチバチ → 無音。動画の音は使わず、似た感じに作った）。▶で聞ける（もう一度押すと止まる）。となりの3つの見本の画面も、「記録する」と「PUSH」のタップで同じ音が鳴る。iPhoneが消音（マナーモード）だと鳴らないことがある。</p>
    </div>
    <button class="stop" type="button" onClick="{{{{stop}}}}">{STOP_SVG}とめる</button>
  </div>{secs}
  <div class="boxes">{boxes}</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{SOUND_W},"height":{SOUND_H}}}}}'>
class Component extends DCLogic {{
  sfxUrls() {{
    return {{
      {urls}
    }};
  }}
{SFX_JS}  renderVals() {{
    this.sfxInit();
    var st = this.state || {{}};
    var on = st.on || '';
    var self = this;
    var play = function (k) {{
      return function () {{
        if (on === k) {{ self.hush(); self.setState({{ on: '' }}); return; }}
        self.sfx(k, 0, 0, function () {{ self.setState({{ on: '' }}); }});
        self.setState({{ on: k }});
      }};
    }};
    return {{
      {vals},
      stop: function () {{ self.hush(); self.setState({{ on: '' }}); }}
    }};
  }}
}}
</script>
</body>
</html>
'''


MEMO_W, MEMO_H = 2200, 2340


def memo_page():
    """メモのボード（静止画18枚＋Fableに渡す決まり）"""
    def still(key, cap):
        return f'<figure class="st"><img src="/_blob/{blobs[key]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'
    hit = still('s_hit_form', '① 記録する') + still('s_hit_push', '② PUSHが上下に動く') + still('s_hit_board', '③ タップ → ボード')
    big = still('s_big_push', '① 大きいPUSH（虹の輪）') + still('s_big_light', '② 爆発・虹の輪（キュウィン）') + still('s_big_board', '③ ボードがドン！')
    fz = (still('s_fz_push', '① 虹色の超デカPUSH') + still('s_fz_noise', '② タップでフリーズ') + still('s_fz_line', '③ 横一本線と細い電気')
          + still('s_fz_doteki', '④「どてき！！」') + still('s_fz_dodo', '⑤「ど！ど！ど！ど！」') + still('s_fz_logo', '⑥「ど的中！！！！」') + still('s_fz_result', '⑦ 結果（上に ど的中）'))
    hd = still('s_big_push', '① デカのPUSH') + still('s_fz_noise', '② タップでフリーズ') + still('s_hd_result', '③「隠れど的中！！！」')
    ms = still('s_miss_form', '① 記録する') + still('s_miss_board', '② ボードだけ')
    B, W, Z, M, R = (FZ_T[k] for k in 'BWZMR')
    T5 = M + MT_T['T5']
    sec = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>的中ボタンのメモ</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&amp;display=swap">
<style>
body{{margin:0}}
*{{box-sizing:border-box}}
.gd{{width:{MEMO_W}px;height:{MEMO_H}px;overflow:hidden;background:#F4F2EC;color:#22252E;font-family:"BIZ UDPGothic",sans-serif;padding:34px 40px 0}}
.t1{{margin:0;font-family:"Dela Gothic One",sans-serif;font-weight:400;font-size:32px;line-height:1.2;color:#161F3D}}
.t2{{margin:8px 0 0;max-width:1560px;font-size:14.5px;line-height:1.7;color:#4E5466}}
.rows{{display:grid;grid-template-columns:3fr 3fr 7fr;gap:20px;margin-top:20px}}
.rows.r2{{grid-template-columns:3fr 2fr 8fr;margin-top:16px}}
.grp{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:14px;padding:14px 16px}}
.grp.fzg{{border:2px solid transparent;background:linear-gradient(#FFFFFF,#FFFFFF) padding-box,linear-gradient(90deg,#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8) border-box}}
.grp h2{{margin:0 0 10px;font-size:17px;color:#161F3D}}
.grp h2 small{{font-size:12.5px;font-weight:700;color:#8A6A38;margin-left:8px}}
.sts{{display:flex;gap:10px}}
.st{{margin:0;flex:1;min-width:0}}
.st img{{display:block;width:100%;aspect-ratio:390/844;object-fit:cover;border-radius:10px;border:1px solid #DDD8CC}}
.st figcaption{{margin-top:6px;font-size:12.5px;font-weight:700;color:#3E4352;text-align:center}}
.boxes{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:18px}}
.box{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:12px;padding:12px 14px}}
.box h3{{margin:0 0 6px;font-size:14px;color:#161F3D}}
.box p,.box li{{margin:0;font-size:12.5px;line-height:1.65;color:#4E5466}}
.box ul{{margin:0;padding-left:1.1em}}
.box b{{color:#22252E}}
.grp.bx ul{{margin:0;padding-left:1.1em}}
.grp.bx li{{margin:0 0 4px;font-size:13px;line-height:1.7;color:#4E5466}}
.grp.bx b{{color:#22252E}}
</style>
</helmet>
<div class="gd">
  <h1 class="t1">的中ボタン・デカ的中ボタン・フリーズ的中ボタン（デフォルト）・隠れど的中・ハズレ</h1>
  <p class="t2">まさちゃんの指定：記録して <b>当たり → 的中ボタン</b>、<b>3連単が当たり → デカ的中ボタン</b>、<b>3連単の当たりに超大穴（10〜12番人気）の馬 → フリーズ的中ボタン</b>、<b>デカ的中の2〜7回に1回（ランダム）→ 隠れど的中</b>（デカのPUSHを押すと、そのまま、ど的中）、<b>ハズレ → ボタンなしでボードだけ</b>。タップすると<b>壁紙のテーマのボード</b>が出て、当たった買い目を報告する（<b>馬がボードを持つのはやめた</b>。的中もハズレも、ボードはテーマに沿った形）。フリーズは、まさちゃんの送ってくれたパチスロのフリーズの動画のように（台の絵や文字は使わない）：虹色にギラギラ光るめちゃくちゃデカいPUSH → <b>タップした瞬間にフリーズ</b>（まさちゃんの指定。白く光る → 横に流れるノイズ → 青い画面に白い光と細い電気 → 青白い横一本線に1pxの電気がバチバチ → 点に縮んで消える）→ 真っ暗のまま1.5秒 → 虹色ネオンのカット（「どてき！！」「ど！ど！ど！ど！」）→「ど的中！！！！」（そろってから1.5秒）→ <b>虹色の大当たりの画面</b>に、上に「ど的中」・まん中からボード。<b>文字はパチンコのロゴのような筆の字と虹色</b>（まさちゃんの指定。写真の字の形は使わず、筆の動きから描いた）。視覚酔いしないように、画面全体が回る・迫る・ゆれる動きはしない。となりの5つの画面は、タップで動く見本（どれもデフォルト＝全テーマ共通の動き・ボードは牧場）。</p>
  <div class="rows">
    <section class="grp"><h2>的中ボタン<small>当たったとき</small></h2><div class="sts">{hit}</div></section>
    <section class="grp"><h2>デカ的中ボタン<small>3連単が当たったとき</small></h2><div class="sts">{big}</div></section>
    <section class="grp fzg"><h2>フリーズ的中ボタン<small>3連単の当たりに超大穴（10〜12番人気）</small></h2><div class="sts">{fz}</div></section>
  </div>
  <div class="rows r2">
    <section class="grp fzg"><h2>隠れど的中<small>デカ的中の2〜7回に1回</small></h2><div class="sts">{hd}</div></section>
    <section class="grp"><h2>ハズレ<small>ボタンなし</small></h2><div class="sts">{ms}</div></section>
    <section class="grp bx"><h2>結果のボード（壁紙のテーマごと）と、隠れど的中の決まり</h2><ul>
      <li><b>馬は出さない</b>（まさちゃんの指定）。的中・デカ的中・ど的中・隠れど的中・ハズレ、どれも<b>壁紙のテーマのボード</b>。26テーマの見本は「結果のボード（26テーマ）」、作り方は boards.py</li>
      <li>ボード＝<b>そのテーマの判定画面をぎゅっと小さくした形</b>：ふち＝背景のもよう（--bg と背景のルール）・見出し＝上の帯（--hd・--hdInk・--hdB・帯の飾り）・見出しの字＝ロゴと同じ（--dfont・--logo・--logoS）・買い目＝カード（--card・--cardB・--cardS）と行（--zBg・--zB）・券種＝タグ（--tagBg・--tagInk・--tagLine）・払戻＝--acc・合計＝--ink・すみの飾り（判定画面のカードと同じ所）。色は判定画面と同じ（コントラストを確かめた値）。馬番の枠の色は全テーマ同じ</li>
      <li><b>デカ</b>：まわりが光る・見出しは虹色（黒いふち）・3連単の行に虹色のふち。<b>ど的中・隠れど的中</b>：枠は虹色（回さない）・炎の光。<b>ハズレ</b>：見出しは上の帯の文字の色で静かに・払戻0円・光も紙ふぶきも音もなし</li>
      <li><b>隠れど的中</b>：デカ的中が出るたびに数えて、<b>2〜7回目（ランダム）の1回</b>。出たら、次の回数をまた2〜7からランダムに決める。数は端末に保存（アプリを閉じても続く・記録やバックアップとは別）。本物のど的中（超大穴）は数えない <b>※仮</b></li>
      <li>見た目は<b>デカ的中のPUSH</b>（PUSHが出たときの音もデカ）→ タップで<b>そのまま、ど的中の演出</b>（押した瞬間にフリーズ・音はど的中）→ 結果の見出し「<b>隠れど的中！！！</b>」・帯「隠れ　デカ的中が ど的中に化けた！」（超大穴の帯のかわり）</li>
    </ul></section>
  </div>
  <div class="boxes">
    <div class="box"><h3>出るとき</h3><ul><li>結果を<b>記録したとき</b>だけ（あとで直したとき・まとめて入れた記録・中止では出ない）</li><li>出るのは1つだけ。強い順に <b>フリーズ</b>（3連単が当たって、その3頭に超大穴＝10〜12番人気がいる。13番人気より下は入れない）＞ <b>デカ</b>（3連単が当たり。2〜7回に1回は<b>隠れど的中</b>）＞ <b>的中</b>（それ以外の当たり）</li><li><b>ハズレ</b>（当たりが1つもない）：PUSHは出さずに、ハズレのボードだけ</li><li>人気は、そのレースを判定したときの単勝オッズの順（判定の超大穴 J・K・L と同じ）。人気がわからないレースはフリーズにしない（デカ）<b>※仮</b></li><li>お知らせ（発走15分後）から開いて記録したときも同じ</li></ul></div>
    <div class="box"><h3>流れと時間（的中・デカ・ハズレ）</h3><ul><li><b>的中</b>：押す → 0.3秒 ボードが下から → 0.95秒「的中！」→ 1.15秒〜 買い目 → 1.8秒 とじる</li><li><b>デカ</b>（パチンコの当たりのように速く・勢いよく）：押す → 0.04秒 白く光る・爆発・虹の光の筋 → 0.1・0.25・0.4秒 虹の輪（キュウィン×3・だんだん大きく）→ 0.38秒 ボードがドンと落ちてくる（0.55秒 着地・光の破片）→ 0.7秒「デカ的中!!」がたたきつけるように → 0.9秒〜 買い目（0.08秒おき）→ 1.4秒 とじる</li><li><b>ハズレ</b>：記録する → 暗い幕 → 0.1秒 ボードが静かに出る（0.4秒）→ 0.45秒〜 買い目（0.08秒おき）→ 0.85秒 とじる</li><li><b>PUSHは横長の長方形（角は丸い）</b>。上下に0.9秒（デカは0.8秒・大きく・まわりに虹の輪）でくり返す</li></ul></div>
    <div class="box"><h3>フリーズの流れと時間</h3><ul><li><b>PUSH</b>：横340×縦170・角46px（デカの1.2倍）。虹色が流れる面・ラメ・白い光がサッと走る・白と紫のふち・まわりに虹の輪。上下に22px・0.85秒／1.3秒ごとにブルブルッ／画面のふちが虹色に光る</li><li><b>押した瞬間にフリーズ（0秒〜）</b>（まさちゃんの指定：前のバグる画面はやめた。送ってくれたパチスロのフリーズの動画のような動き。台の絵は使わない）：1コマ＝1/30秒。白く光る（青いブロックが丸く集まる・縦に抜けた線）→ 0.07秒〜 明るい色の帯が横に流れる（コマごとに場所が変わる・下に緑と黄色）→ 0.2秒〜 まぶしい帯のある水色に赤い粒 → {sec(B)}秒 青い画面にまぶしい横の帯・<b>まん中の白い光がふくらむ・しぼむ</b>・弓なりの電気・縦の点々 → {sec(W)}秒 まわりが暗くなって<b>青白い横一本線</b>（まん中にフレア）・<b>線にまとわりつく電気がバチバチ</b>（いちばん細い線＝芯0.8px・枝0.5px。中点をずらして細かくギザギザ・枝分かれ・1コマごとに形が変わる）→ {sec(Z)}秒 線が両はしから点に縮んで消える（光の粒が下へ落ちながら散る）→ <b>真っ暗のまま1.5秒</b>（フリーズの間）。走査線（1px）は {sec(W)}秒まで</li><li><b>虹色ネオンのカット（{sec(M)}〜{sec(R)}秒・5つ）</b>：まさちゃんの指定の文字。<b>パチンコのロゴのような筆の字と虹色</b>（虹色の面・左上のふちが白く光る・上半分につや・こげ茶と金と黒のふち・金の立体・まわりに光。brush.py）。「どてき！！」「ど！」は<b>1文字ずつ大きく</b>、押した直後のPUSHのように乱れる（赤と水色のずれ・横にずれる帯・まわりに小さなブロック）。文字は<b>たたきつけるように出て</b>（0.16秒）、<b>ずっとガクガクふるえる</b>（左右上下と傾き・1秒に4回。筆の字は明るさの差が大きいので、光の点めつが多くならないように前より少なく）。<b>パチンコの当たりのように速く・激しく</b>：「！」「ど！」「ど的中」が出るたびに<b>爆発</b>（星形の光がはじける・衝撃の輪・光の破片が飛び散る）。場所・大きさ・向きはバラバラ：真っ暗から大爆発 → テンゲルのアイコンのネオンに「ど」「て」「き」「！」と大きな「！」（{sec(M)}秒〜）→ 星空に「どてき！！」（左上から右下へ階段・{sec(M + MT_T['T2'])}秒〜）→ ネオンのギザギザに大きな「どてき！！」×2（画面からはみ出る・{sec(M + MT_T['T3'])}秒〜）→ 星空に大きな「ど！」×4（{sec(M + MT_T['T4'])}秒〜・0.17秒おき）→ <b>ネオンのパチンコの当たりのような虹色</b>（{sec(T5)}秒〜）（黒に光る虹の光線・虹の輪・白く光るまん中と星・きらめき）に「ど的中」（光がサッと走る）「！！！！」（<b>そろってから1.5秒</b>）。<b>この背景だけ動く</b>：光の波が光線にそって外へ流れる（0.45秒ごと）・虹の輪が外へ広がって消える・まん中がふくらむ（回らない）。ほかのカットの背景は止まったまま</li><li><b>{sec(R)}秒 結果</b>：白く光る → <b>虹色の大当たりの画面</b>（まさちゃんの指定。「ど的中」から虹色の光線と白い細い光線・まん中の白い光・虹の輪が外へ広がる（1.8秒ごと・2つ）・虹色のきらめきが上る・光線は止まったまま回さない）で爆発、上に「ど的中」（筆の字・うしろで虹色の炎がゆらゆら・光がサッと走る・きらめき・SUPER LONGSHOT）・まん中からボードがドンと出る → {sec(R + .3)}秒「ど的中！！！」（隠れど的中は「隠れど的中！！！」）→ {sec(R + .45)}秒〜 買い目（0.08秒おき）→ {sec(R + .45 + .24 + .25)}秒 とじる</li><li><b>隠れど的中</b>：デカのPUSH → タップで、ここに書いた流れと同じ（押した瞬間にフリーズ）</li></ul></div>
    <div class="box"><h3>重ねる順（下から）</h3><ul><li><b>的中・デカ・ハズレ</b>：暗い幕 → 光（ハズレはなし）→ <b>テーマのボード</b>（ふち＝背景のもよう → 上の帯と見出し → カードと買い目 → すみの飾り。文字はHTML）→ 紙ふぶき → とじる → （デカ）白い光</li><li><b>フリーズ・隠れど的中</b>：黒 → 虹色の大当たりの画面（虹色の光線・白い光線・虹の輪・虹色のきらめき・コイン・テーマのボード・「ど的中」と虹色の炎・紙ふぶき）→ ネオンのカット（5つ・文字・白い光）→ 押した瞬間のフリーズ（白い画面・横に流れる帯・水色の画面・青い画面・まぶしい帯・白い光・ブロックと粒・走査線・横一本線・フレア・電気・光の粒）→ 白い光 → とじる</li></ul></div>
    <div class="box"><h3>ボードに書くもの</h3><ul><li>見出し（的中！・デカ的中!!・ど的中！！！・隠れど的中！！！・ハズレ。全角の「！」が3つ続くところは字の間をつめる）・R・買い目（券種・馬番・金額・払戻）・払戻の合計。ユーザーが自分で入れた買い目だけ（判定の画面に点数・組番を出さない決まりはそのまま）</li><li>当たりは当たった買い目だけ。<b>ハズレは入れた買い目を全部</b>（払戻0円）・小見出しは「9R の買い目」</li><li>デカ・フリーズ・隠れど的中は3連単の行がいちばん上で虹色の枠（フリーズは光が走る）</li><li><b>フリーズ</b>：上に「ど的中」（筆の字・虹色の炎）・見出しの下に「超大穴 ⑪ 11番人気が3連単に！」の帯・3連単の行の超大穴の馬番に虹色の輪。<b>隠れど的中</b>：帯は「隠れ　デカ的中が ど的中に化けた！」</li><li>払戻が長いと、その行の払戻だけ次の行へ（右によせる）。帯のぶんボードが長いので、フリーズは6行まで（7つ以上は上から5行＋「ほか○点」<b>※仮</b>）</li></ul></div>
    <div class="box"><h3>テーマ（壁紙）ごとに変えるところ</h3><ul><li><b>結果のボード</b>：判定画面と同じ変数と飾り（boards.py が themes20.py・判定画面から読む）。新しい絵はいらない</li><li>PUSHの色（--pushA・--pushB・--pushC・--rim・--rimD）・光の色（--ray）</li><li><b>フリーズは全テーマ共通</b>（変わるのはボードだけ）。回る虹（虹のぐるぐる）は使わない（虹色は流れるだけ）</li><li>シルバー帯・ゴールド帯・マスター帯は指示書9.1の指定どおり（あとで作る）</li></ul></div>
    <div class="box"><h3>光と見やすさ</h3><ul><li><b>視覚酔いしないように</b>：画面全体が回る・迫る（トンネル）・流れる・ゆれる動きはしない。背景は止めて、動くのは文字（ポンと出る・乱れる・ふるえる）・小さな光・きらめきと、「ど的中！！！！」と結果の背景の光の波と輪だけ（外へ広がる・回らない）。虹色が流れるのは4秒で1回りよりゆっくり</li><li>強く光るのは<b>画面のどの点でも1秒に3回まで</b>（光の点めつで気分が悪くなる人がいるため。スマホは画面が目に近いので、画面の10%の広さでも数えた）。動画の明るさを1コマずつ・点ごとに測って確かめた。画面全体が白く光るのは デカの0.04秒（一瞬まっ白）・フリーズの押した瞬間（白い画面。横に流れる帯は明るい色どうしで、切りかわっても点めつにならないようにした）・{sec(R)}秒（弱め）だけ。爆発の光は小さな範囲で1回ずつ。デカの虹の輪は同じ所が何回も光らないように大きさを変えた・虹の光の筋はゆっくり回す（30秒で1回り）・押したあとの暗い幕はPUSHの画面の暗さのまま始める（いったん明るくなってまた暗くなると、白い光の前にもう1回光ってしまう）。ハズレは光らない</li><li>iPhoneの「視差効果を減らす」がオンなら：フリーズ（プチュン）・ネオンのカット・虹の輪・炎のゆらゆら・きらめき・紙ふぶき・PUSHの動きを止める。押すと1秒真っ暗 → 虹色の画面と「ど的中」（上）・ボードをふわっと出す。効果音は右の「効果音のメモ」（見本の画面もタップで鳴る）</li></ul></div>
    <div class="box"><h3>容量</h3><ul><li><b>ボードに絵は使わない</b>（テーマの色・もよう・飾りのSVGとCSSだけ。見出しの字はテーマの見出しのフォント）。フリーズで足す絵は、テンゲルのアイコンから作った<b>ネオンの線画のマスク2枚</b>だけ（芯 1024 約59KB・光 512 約40KB。neon_icon.py。T1 の背景）。ほかの虹・文字・炎・ギザギザ・電気・ノイズはCSSとSVG</li><li>バグる画面をやめたので、<b>押した瞬間の画面の絵（スクリーンショット）はいらない</b>（前はアプリで撮る予定だった）</li><li>動きは全部CSS（動画なし）・新しいフォントなし（テーマのフォント・Dela Gothic One・BIZ UDPゴシック）。<b>ど的中の筆の字はフォントではなくSVGの形</b>（brush.py で筆の動きから描いた6文字：ど・て・き・！・的・中。brush_glyphs.json 約12KB。金の立体とまわりの光は CSS の drop-shadow）</li></ul></div>
  </div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{MEMO_W},"height":{MEMO_H}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


STILLS = ('s_hit_form', 's_hit_push', 's_hit_board', 's_big_push', 's_big_light', 's_big_board',
          's_fz_push', 's_fz_noise', 's_fz_line', 's_fz_doteki', 's_fz_dodo', 's_fz_logo', 's_fz_result',
          's_hd_result', 's_miss_form', 's_miss_board')

if __name__ == '__main__':
    out = os.environ.get('FX_OUT', P)
    for kind, (fn, _) in PAGES.items():
        open(f'{out}/{fn}', 'w', encoding='utf-8').write(page(kind))
        print(fn)
    open(f'{out}/Fx_Boards.dc.html', 'w', encoding='utf-8').write(boards_page())
    print('Fx_Boards.dc.html')
    if all(k in blobs for k in STILLS):
        open(f'{out}/Fx_Memo.dc.html', 'w', encoding='utf-8').write(memo_page())
        print('Fx_Memo.dc.html')
    if WAVES and all(k in blobs for v in SND.values() for k in v):
        open(f'{out}/Fx_Sound.dc.html', 'w', encoding='utf-8').write(sound_page())
        print('Fx_Sound.dc.html')
