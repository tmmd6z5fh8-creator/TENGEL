"""的中ボタン・デカ的中ボタン・フリーズ的中ボタン（デフォルト）の見本の画面：Fx_Hit.dc.html・Fx_Big.dc.html・Fx_Freeze.dc.html
   python3 gen_fx.py fx_blobs.json
   fx_blobs.json：{"back": "<id>", "front": "<id>"}（ボードを持つ馬の2枚）＋フリーズの絵（fz_warp・fz_icon・fz_ncore・fz_nglow）
   ＋メモの静止画（s_…。そろっていればメモ Fx_Memo.dc.html も作る）
   流れ：記録する → PUSHボタン（上下に動く）→ タップ → 馬がボードを持って出てくる（ボードに当たった買い目）
   フリーズ（3連単の当たりに超大穴＝10〜12番人気の馬）：虹色にギラギラ光るめちゃくちゃデカいPUSH → タップでパチスロのフリーズのように
   画面がバグる → 青白い横一本線にプチュン → 真っ暗（2秒）→ 虹色ネオンの超高速カット →「ど的中」が炎と光の中からドーン → 炎の中から馬がボード"""
import os, re, sys, json, random, math
from urllib.parse import quote
from gen_screens import SVG_A

K = os.path.dirname(os.path.abspath(__file__))
P = f'{K}/canvas/project' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock'
blobs = json.load(open(sys.argv[1]))
rect = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else dict(x=24, y=267, w=672, h=440, W=720, H=900)
RANCH = open(f'{P}/Judge_Ranch.dc.html', encoding='utf-8').read()
RANCH_VARS = re.search(r'^\.ph\{(--bg:[^}]*)\}', RANCH, re.M).group(1)
BANNER = re.search(r'<img class="bnr" src="(/_blob/[0-9a-f]{32})"', RANCH).group(1)

# ボードを持つ馬：画像 720×900 → 画面では 360×450
SC = 0.5
HB_W, HB_H = rect['W'] * SC, rect['H'] * SC
BD = dict(x=rect['x'] * SC, y=rect['y'] * SC, w=rect['w'] * SC, h=rect['h'] * SC)

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
/* ボードを持つ馬 */
.hb{position:absolute;z-index:6;left:50%;top:150px;width:HBWpx;height:HBHpx;margin-left:-HBW2px}
.hb img{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}
.board{position:absolute;left:BDXpx;top:BDYpx;width:BDWpx;min-height:BDHpx;border-radius:16px;border:8px solid var(--bFrame);background:var(--bFace);
  box-shadow:0 10px 22px rgba(0,0,0,.28),inset 0 0 0 2px rgba(0,0,0,.05);padding:30px 16px 12px;display:flex;flex-direction:column;align-items:stretch;gap:7px;color:var(--bInk)}
.bh{text-align:center;font:400 34px/1 "Dela Gothic One",sans-serif;color:var(--hitRed);text-shadow:0 2px 0 #FFFFFF,0 4px 0 rgba(0,0,0,.12)}
.bsub{text-align:center;font-size:12.5px;font-weight:700;color:#7A5A3A;margin-top:-2px}
.brows{list-style:none;margin:2px 0 0;padding:0;display:flex;flex-direction:column;gap:6px}
.brows li{display:flex;align-items:center;gap:5px;padding:5px 7px;border-radius:10px;background:rgba(138,90,43,.08);white-space:nowrap}
.brows .bt{min-width:44px;height:22px;font-size:11.5px}
.brows .bc .n{min-width:24px;height:24px;font-size:12.5px}
.brows .by{font-size:11px;color:#7A5A3A}
.brows .bp{margin-left:auto;font-size:14.5px;font-weight:800;color:var(--hitRed)}
.brows .bc{flex:none;gap:2px}
.brows .ar{padding:0 1px}
.btot{display:flex;align-items:baseline;justify-content:flex-end;gap:8px;margin-top:auto;font-size:12.5px;font-weight:700;color:#5A3A1A}
.btot b{font:400 22px/1 "Dela Gothic One",sans-serif;color:var(--bInk)}
.close{position:absolute;z-index:8;left:50%;bottom:64px;transform:translateX(-50%);height:46px;padding:0 34px;border-radius:999px;border:2px solid rgba(255,255,255,.85);background:rgba(0,0,0,.35);color:#FFFFFF;font-family:var(--font),sans-serif;font-weight:800;font-size:15px;cursor:pointer;animation:fadeUp .4s ease-out both}
@keyframes fadeUp{from{opacity:0;transform:translate(-50%,12px)}to{opacity:1;transform:translate(-50%,0)}}
/* 紙ふぶき */
.conf{position:absolute;inset:0;z-index:7;pointer-events:none}
.conf i{position:absolute;left:var(--x);top:-30px;width:var(--w);height:var(--h);background:var(--c);border-radius:2px;opacity:0;animation:fall var(--t) linear var(--d) infinite}
@keyframes fall{0%{opacity:1;transform:translateY(0) rotate(0)}85%{opacity:1}100%{opacity:0;transform:translateY(900px) rotate(var(--r))}}
/* 視差効果を減らす：上下・回転・広がる光・紙ふぶきを止めて、馬とボードはふわっと出す */
@media (prefers-reduced-motion:reduce){.push,.pshadow,.push::after,.halo b,.tap,.conf i,.rays,.rbow,.ring,.glow,.spk b{animation:none!important}.conf,.pressed,.push::after{display:none}.hb{animation:fadeIn .5s ease-out .2s both!important}}
'''

HIT_CSS = r'''
/* ---------- 的中：あたたかい光 → 馬が下から出る ---------- */
.rays{position:absolute;z-index:4;left:50%;top:44%;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;
  background:repeating-conic-gradient(var(--ray) 0 7deg,transparent 7deg 18deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);
  animation:raysIn .6s ease-out .2s both,spin 22s linear infinite}
.hit .hb{animation:riseUp .7s cubic-bezier(.2,1.35,.4,1) .3s both}
@keyframes riseUp{from{transform:translateY(720px)}to{transform:translateY(0)}}
.hit .bh{animation:pop .5s cubic-bezier(.2,1.8,.4,1) .95s both}
.hit{--t0:1.15s;--tc:.2s}
'''

BIG_CSS = r'''
/* ---------- デカ的中：大きいPUSH・虹色に光る ---------- */
.ov.big .dim{background:radial-gradient(circle at 50% 46%,rgba(60,30,90,.55),rgba(6,4,18,.86) 70%)}
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
/* 押したあと：白く光る → 虹の光の筋と輪 → 光の中から馬 */
.flash{position:absolute;inset:0;z-index:9;background:#FFFFFF;pointer-events:none;animation:flash .9s ease-out .18s both}
@keyframes flash{0%{opacity:0}18%{opacity:1}100%{opacity:0}}
.rbow{position:absolute;z-index:3;left:50%;top:44%;width:1100px;height:1100px;margin:-550px 0 0 -550px;border-radius:50%;
  background:conic-gradient(#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);
  -webkit-mask-image:repeating-conic-gradient(#000 0 6deg,transparent 6deg 15deg),radial-gradient(circle,#000 0 10%,transparent 60%);
  -webkit-mask-composite:source-in;mask-image:repeating-conic-gradient(#000 0 6deg,transparent 6deg 15deg),radial-gradient(circle,#000 0 10%,transparent 60%);mask-composite:intersect;
  opacity:.85;animation:raysIn .7s ease-out .25s both,spin 7s linear infinite}
.glow{position:absolute;z-index:4;left:50%;top:44%;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 22%,rgba(255,248,214,.9) 34%,rgba(255,230,160,.45) 52%,transparent 70%);
  animation:wrap 1.3s ease-out .2s both,breathe 2.4s ease-in-out 1.5s infinite}
@keyframes wrap{0%{scale:.1;opacity:0}45%{scale:2.6;opacity:1}100%{scale:1.15;opacity:.95}}
@keyframes breathe{0%,100%{scale:1.15}50%{scale:1.25}}
.ring{position:absolute;z-index:5;left:50%;top:44%;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;
  background:conic-gradient(#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3B3B);
  -webkit-mask-image:radial-gradient(circle,transparent 0 64%,#000 66% 72%,transparent 74%);mask-image:radial-gradient(circle,transparent 0 64%,#000 66% 72%,transparent 74%);
  opacity:0;animation:shock 1s ease-out forwards}
.ring.r1{animation-delay:.28s}.ring.r2{animation-delay:.55s}.ring.r3{animation-delay:.85s}
@keyframes shock{0%{opacity:1;scale:.2}100%{opacity:0;scale:3.2}}
.big .hb{animation:emerge 1s ease-out .85s both}
@keyframes emerge{0%{opacity:0;transform:scale(.6);filter:brightness(3.2) blur(3px)}60%{opacity:1;transform:scale(1.06);filter:brightness(1.6) blur(0)}100%{transform:scale(1);filter:none}}
.big .board{box-shadow:0 0 0 3px rgba(255,255,255,.9),0 0 26px 6px rgba(255,236,160,.85),0 10px 22px rgba(0,0,0,.3)}
.big .bh{font-size:31px;background:linear-gradient(90deg,#FF3B3B,#FF9F1A,#E8C200,#2DBB55,#1FA8E0,#4C6BFF,#B34CFF,#FF3B3B);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;filter:drop-shadow(0 2px 0 #FFFFFF) drop-shadow(0 3px 0 rgba(0,0,0,.18));
  animation:pop .55s cubic-bezier(.2,1.8,.4,1) 1.5s both,rbowText 2s linear 1.5s infinite}
.ov.big{--t0:1.75s;--tc:.3s}
.big .brows li.top{background:linear-gradient(#FFFDF5,#FFFDF5) padding-box,linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF) border-box;border:2px solid transparent}

'''

FREEZE_CSS = r'''
/* ---------- フリーズ的中：虹色にギラギラ光る めちゃくちゃデカいPUSH → タップでパチスロのフリーズのように ----------
   （押したあとの秒は下の「押したあと」に書いてある） */
.w3{background:#E0322B;color:#FFFFFF}
.w8{background:#F27BB0;color:#1F1F1F}
.ov.fz{--rb:#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B;--ink2:#2A1259;--t0:<R+.85>;--tc:.35s}
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
/* ---------- 押したあと（パチスロのフリーズのように） ----------
   秒は押してから。<C>＝アイコンのドアップ・<H>＝横に流れる光・<E>＝画面が青く光る・<W>＝プチュン（青白い横一本線）・<Z>＝線が点に縮んで消える
   ・（真っ暗）・<M>＝虹色ネオンの超高速カット・<F>＝白い爆発 →「ど的中」・<R>＝馬がボード */
.ov.fz .blk{position:absolute;inset:0;background:#000000}
@keyframes vis{from,to{visibility:visible}}
@keyframes on1{from,to{opacity:1}}
@keyframes fzOn{from,to{opacity:1}}
.ov.fz .gl,.ov.fz .pc,.ov.fz .mt,.ov.fz .fin,.ov.fz .xf{position:absolute;inset:0;overflow:hidden;pointer-events:none}
/* ===== 1) グリッチ（0〜<E>）：押した瞬間の画面がバグる（色ずれ・横ズレ・ブロック・横の線・走査線）
   → <N>〜 一瞬もとに戻る → <C>〜 テンゲルのアイコンのドアップ（バグりながら少しずつ引く）→ <H>〜 横に流れる光の筋 ===== */
.gl{z-index:40;background:#000000;visibility:hidden;animation:vis <E> steps(1)}
.gl .sn,.gl .ic,.gl .sm,.gl .gS,.gl .gS i,.gl .gsc,.gl .ib{position:absolute;inset:0}
.gl .sn,.gl .sn .sl{background:url(/_blob/WARPID) 0 0/390px 844px}
.gl .ib,.gl .ic .sl{background:url(/_blob/ICONID) -795px -148px/1500px 1500px}
.gl .sn .gS{--im:url(/_blob/WARPID) 0 0/390px 844px}
.gl .ic .gS{--im:url(/_blob/ICONID) -795px -148px/1500px 1500px}
/* 色ずれ：赤だけの絵と水色だけの絵を左右にずらして重ねる（重なると元の色） */
.gl .gS{isolation:isolate;background:#000000;opacity:0}
.gl .gS i{background:var(--im),#FF0000;background-blend-mode:multiply}
.gl .gS i + i{background:var(--im),#00FFFF;background-blend-mode:multiply;mix-blend-mode:screen}
.gl .sl{position:absolute;left:0;width:390px;opacity:0}
.gl .ic{visibility:hidden;transform-origin:50% 45%;animation:vis <H-C> steps(1) <C>,icz <H-C> cubic-bezier(.2,.6,.4,1) <C> both}
@keyframes icz{from{scale:1.22}to{scale:1}}
/* 横に流れる光の筋（<H>〜<E>）：アイコンを横に引きのばした絵＋光の筋 */
.gl .sm{visibility:hidden;animation:vis <E-H> steps(1) <H>;background:linear-gradient(180deg,#020A3A 0%,#0A2FB0 30%,#1E78FF 47%,#8FE6FF 51%,#1E78FF 55%,#0A2FB0 72%,#020A3A 100%)}
.gl .sm .st{position:absolute;inset:0;background:url(/_blob/ICONID) -795px -148px/1500px 1500px;transform:scaleX(9);opacity:.6;mix-blend-mode:screen;filter:saturate(1.8) hue-rotate(150deg)}
.gl .sm b{position:absolute;left:0;top:var(--y);width:390px;height:var(--h);background:linear-gradient(90deg,rgba(255,255,255,0),var(--c) 28%,#FFFFFF 50%,var(--c) 72%,rgba(255,255,255,0));animation:smb var(--t) linear var(--d) both}
@keyframes smb{from{translate:-430px 0}to{translate:430px 0}}
/* 上にかぶせるもの：走査線・ブロック・横の線（画面全体が明るく⇔暗くなるものは使わない） */
.gl .gsc{background:repeating-linear-gradient(180deg,rgba(0,0,0,.3) 0 1px,rgba(0,0,0,0) 1px 3px)}
.gl .gbk i,.gl .gtr i{position:absolute;opacity:0;animation:on1 var(--t) steps(1) var(--d)}
.gl .gbk i{left:var(--x);top:var(--y);width:var(--w);height:var(--h);background:var(--c)}
.gl .gtr i{left:0;right:0;top:var(--y);height:var(--h);background:var(--c);box-shadow:0 0 6px var(--c)}
/* ===== 2) プチュン（<E>〜）：画面が青く光って、まん中の白い光が2回ふくらむ・稲妻がジリジリ
   → <W> 画面が縦につぶれて青白い横一本線（まん中に光のフレア）→ 線のまわりで静電気がジリジリ
   → <Z> 線が両はしから点に縮んで消える（光の粒が散る）→ 真っ暗 ===== */
.pc{z-index:39;visibility:hidden;animation:vis <Z+.8-E> steps(1) <E>}
.pcb{position:absolute;inset:0;background:radial-gradient(ellipse 85% 60% at 50% 50%,#9AD6FF 0%,#3A7EFF 26%,#0E33C2 56%,#030C4A 100%);opacity:0;
  animation:pcbOn <W-E> linear <E> both,pcbOff .08s cubic-bezier(.6,0,1,.6) <W> forwards}
.pcb::after{content:"";position:absolute;inset:0;background:NOISEF 0 0/120px 120px;mix-blend-mode:screen;opacity:.25}
@keyframes pcbOn{from,to{opacity:1}}
@keyframes pcbOff{0%{transform:scaleY(1);filter:brightness(1);opacity:1}99%{transform:scaleY(.004);filter:brightness(2.4);opacity:1}100%{transform:scaleY(.004);opacity:0}}
.pcg{position:absolute;left:50%;top:422px;width:640px;height:300px;margin:-150px 0 0 -320px;border-radius:50%;opacity:0;
  background:radial-gradient(ellipse 50% 50% at 50% 50%,#FFFFFF 0 14%,rgba(205,236,255,.95) 26%,rgba(110,175,255,.55) 48%,rgba(50,110,255,0) 72%);
  animation:pcgOn <W-E> ease-in-out <E> both,pcgSq .09s cubic-bezier(.6,0,1,.6) <W> forwards,pcgX .18s cubic-bezier(.55,0,.9,.45) <Z> forwards}
@keyframes pcgOn{0%{opacity:0;transform:scale(.6,.4)}25%{opacity:1;transform:scale(.95,.8)}100%{opacity:1;transform:scale(1.12,.74)}}
@keyframes pcgSq{from{opacity:1;transform:scale(1.12,.74)}to{opacity:1;transform:scale(1.15,.05)}}
@keyframes pcgX{from{opacity:1;transform:scale(1.15,.05)}to{opacity:1;transform:scale(0,.05)}}
.pcl{position:absolute;left:0;right:0;top:421px;height:2px;opacity:0;
  background:linear-gradient(90deg,rgba(150,200,255,.25),#D8EEFF 6%,#FFFFFF 50%,#D8EEFF 94%,rgba(150,200,255,.25));
  box-shadow:0 0 2px #FFFFFF,0 0 6px #BFE3FF,0 0 14px #4F96FF,0 0 30px #2A5CFF;
  animation:on1 <Z+.18-W-.05> steps(1) <W+.05>,pclFl .05s steps(1) <W+.05> 5,pclX .18s cubic-bezier(.55,0,.9,.45) <Z> forwards}
@keyframes pclFl{0%{opacity:1}50%{opacity:.6}}
@keyframes pclX{from{transform:scaleX(1)}to{transform:scaleX(0)}}
.pcf{position:absolute;left:50%;top:422px;width:0;height:0;opacity:0;animation:on1 <Z+.42-W> steps(1) <W>,pcfS .26s ease-in <Z+.14> forwards}
.pcf i{position:absolute;border-radius:50%}
.pcf .f1{left:-210px;top:-10px;width:420px;height:20px;background:radial-gradient(ellipse 50% 50% at 50% 50%,#FFFFFF 0 6%,rgba(190,225,255,.9) 14%,rgba(70,130,255,.45) 38%,rgba(40,90,255,0) 70%);animation:pcfP .07s steps(1) <W> 4}
.pcf .f2{left:-36px;top:-36px;width:72px;height:72px;background:radial-gradient(circle,#FFFFFF 0 12%,rgba(170,215,255,.85) 26%,rgba(60,120,255,.3) 52%,rgba(40,90,255,0) 72%)}
.pcf .f3{left:-1.5px;top:-34px;width:3px;height:68px;border-radius:2px;background:linear-gradient(180deg,rgba(255,255,255,0),#FFFFFF 50%,rgba(255,255,255,0))}
@keyframes pcfP{0%{opacity:1}50%{opacity:.7}}
@keyframes pcfS{0%{transform:scale(1)}55%{transform:scale(.4)}100%{transform:scale(0);opacity:0}}
/* ジリジリの稲妻：白い細い線のギザギザが一瞬ずつ（0.03〜0.07秒）あちこちで光る */
.pca{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible;filter:drop-shadow(0 0 2px #CFF0FF) drop-shadow(0 0 6px #4F8BFF)}
.pca path{fill:none;stroke:#FFFFFF;stroke-linecap:round;stroke-linejoin:round;visibility:hidden;animation:vis var(--t) steps(1) var(--d)}
.pca circle{fill:#FFFFFF;visibility:hidden;animation:vis var(--t) steps(1) var(--d)}
.pcd i{position:absolute;left:var(--x);top:var(--y);width:2px;height:2px;margin:-1px 0 0 -1px;border-radius:50%;background:#E4F3FF;box-shadow:0 0 4px #7FB6FF;
  opacity:0;animation:pcd var(--t) ease-out var(--d) forwards}
@keyframes pcd{0%{opacity:1;translate:0 0}100%{opacity:0;translate:var(--dx) var(--dy)}}
/* ===== 3) 真っ暗（<Z+.4>〜<M>）→ 4) 虹色ネオンのカット（<M>〜<F>）：まさちゃんの指定の文字が、カットごとにポンと出る
   T1「とんでも！」→ T2「とんでも！」→ T3「とんでも！」「とんでも！」→ T4 白く光る →「ど！」「ど！」「ど！」「ど！」→ T5「ど的中」「！！！！」→ T6 4つをまとめて
   視覚酔い・光の点めつを防ぐ：画面全体が回る・迫る・流れる・ゆれる動きはしない（背景は止める）。動くのは文字がポンと出るところと小さな光だけ。
   色が変わるのは3秒で1回りより遅く（画面のどの点も、明るい⇔暗いが1秒に3回まで） ===== */
.mt{z-index:30}
.sc{position:absolute;inset:0;overflow:hidden;visibility:hidden}
.mfl{position:absolute;inset:0;z-index:5;background:#FFFFFF;opacity:0}
.mfl.a{animation:mfl .4s ease-out <M> forwards}
.mfl.b{animation:mfl .4s ease-out <M+2.2> forwards}
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
/* 文字：白い太いふち＋光（.o）と、色（.f）。ポンと出て少し傾いたまま止まる */
.tx{position:absolute;left:var(--x,0px);width:var(--w,390px);top:var(--y);height:var(--h);opacity:0;transform:rotate(var(--r));animation:txIn .22s cubic-bezier(.2,.9,.3,1.2) var(--d) forwards}
.tx span{position:absolute;left:-40px;right:-40px;top:0;text-align:center;white-space:nowrap;font:400 var(--fs)/var(--h) "Dela Gothic One",sans-serif;letter-spacing:-.02em}
.tx .o{color:#FFFFFF;-webkit-text-stroke:var(--sw,14px) #FFFFFF;filter:drop-shadow(0 0 8px var(--g)) drop-shadow(0 0 18px var(--g))}
.tx .f{background:linear-gradient(160deg,var(--c1),var(--c2) 52%,var(--c3));-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-stroke:3px #1A0838}
.tx.dk .o{color:#1A0838;-webkit-text-stroke-color:#1A0838;filter:drop-shadow(0 0 3px #FFFFFF) drop-shadow(0 0 14px rgba(255,255,255,.9))}
@keyframes txIn{0%{opacity:0;transform:rotate(var(--r)) scale(1.7)}60%{opacity:1;transform:rotate(var(--r)) scale(.95)}100%{opacity:1;transform:rotate(var(--r)) scale(1)}}
/* 文字が出たときの光の輪（小さく1回） */
.tr{position:absolute;left:var(--x);top:var(--y);width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;border:5px solid var(--g);box-shadow:0 0 12px var(--g);opacity:0;animation:cring .45s ease-out var(--d) forwards}
@keyframes cring{0%{opacity:1;scale:.3}100%{opacity:0;scale:2}}
/* T1（<M>〜）：テンゲルのアイコンのネオン（画面よりデカい・止まっている） */
.t1{animation:vis .75s steps(1) <M>}
.t1 .bg{position:absolute;inset:0;background:radial-gradient(circle at 16% 20%,#FF2BD6 0,rgba(255,43,214,0) 40%),radial-gradient(circle at 86% 16%,#2FD6FF 0,rgba(47,214,255,0) 38%),
  radial-gradient(circle at 80% 80%,#FFE53B 0,rgba(255,229,59,0) 42%),radial-gradient(circle at 18% 84%,#3CFF6A 0,rgba(60,255,106,0) 42%),radial-gradient(circle at 50% 48%,#7A3BFF 0,rgba(122,59,255,0) 58%),#14062E}
.t1 .dk{position:absolute;inset:0;background:rgba(8,2,26,.55)}
.t1 .nic{width:1100px;height:1100px;margin-left:-550px;top:-150px}
/* T2（<M+.75>〜）：星空・光の玉 */
.t2{animation:vis .7s steps(1) <M+.75>}
/* T3（<M+1.45>〜）：ネオンのギザギザ（止まっている） */
.t3{background:#06021A;animation:vis .75s steps(1) <M+1.45>}
.t3 .zz{position:absolute;left:50%;top:50%;width:2800px;height:2800px;margin:-1400px 0 0 -1400px;transform:scale(.6);opacity:.6}
.t3 .zz svg{display:block;width:100%;height:100%}
/* T4（<M+2.2>〜）：白く光る → 星空に「ど！」×4 */
.t4{animation:vis 1.2s steps(1) <M+2.2>}
.t4 .glw{position:absolute;inset:0;background:radial-gradient(circle at 50% 44%,rgba(255,60,200,.45),rgba(122,59,255,.2) 40%,rgba(5,2,15,0) 70%)}
/* T5（<M+3.4>〜）：虹の光の筋（止まっている）に「ど的中」「！！！！」 */
.t5{background:#1A0838;animation:vis 1.1s steps(1) <M+3.4>}
.t5 .bu{position:absolute;left:50%;top:44%;width:1400px;height:1400px;margin:-700px 0 0 -700px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 4%,rgba(255,255,255,.8) 8%,rgba(255,255,255,0) 24%),repeating-conic-gradient(#FF2B4A 0 5deg,#FFE53B 5deg 10deg,#3CFF6A 10deg 15deg,#2FD6FF 15deg 20deg,#B34CFF 20deg 25deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 26%,rgba(0,0,0,.5) 46%,transparent 66%);mask-image:radial-gradient(circle,#000 0 26%,rgba(0,0,0,.5) 46%,transparent 66%)}
.t5 .bs{position:absolute;left:50%;top:44%;width:180px;height:180px;margin:-90px 0 0 -90px;background:#FF1E3C;clip-path:polygon(50% 0,60% 40%,100% 50%,60% 60%,50% 100%,40% 60%,0 50%,40% 40%);opacity:.9}
.t5 .dkb{position:absolute;inset:0;background:radial-gradient(ellipse 70% 30% at 50% 47%,rgba(26,8,56,.55),rgba(26,8,56,0) 70%)}
/* T6（<M+4.5>〜<F>）：アイコンのドアップ（ネオン）に、4つの言葉をまとめて */
.t6{background:#05020F;animation:vis <F-M-4.5> steps(1) <M+4.5>}
.t6 .nic{width:1700px;height:1700px;margin-left:-1122px;top:-150px;opacity:.75}
.t6 .shd{position:absolute;left:0;right:0;top:0;height:420px;background:linear-gradient(180deg,rgba(5,2,15,.85),rgba(5,2,15,.6) 70%,rgba(5,2,15,0))}
/* ===== 5) 白い爆発（<F>）→「ど的中」が炎と光の中からドーン → <R-.35> 上へ → <R> 炎の中から馬がボード（画面はゆらさない） ===== */
.xf{z-index:45}
.xpl{position:absolute;left:50%;top:44%;width:900px;height:900px;margin:-450px 0 0 -450px;opacity:0;animation:xpl .6s cubic-bezier(.12,.75,.3,1) <F> forwards}
.xpl svg{display:block;width:100%;height:100%}
@keyframes xpl{0%{opacity:1;transform:scale(.12) rotate(0deg)}45%{opacity:1}100%{opacity:0;transform:scale(1.9) rotate(8deg)}}
.xf2{position:absolute;inset:0;background:radial-gradient(circle at 50% 40%,rgba(255,255,255,.8),rgba(255,214,120,.5) 28%,rgba(255,120,0,0) 62%);opacity:0;animation:mfl .4s ease-out <R-.45> forwards}
.fin{z-index:20;opacity:0;animation:fzOn .01s linear <F> forwards}
.fsk{position:absolute;inset:0}
.fin .fb{position:absolute;inset:-40px;background:radial-gradient(circle at 50% 38%,#FFF6C8 0,#FFC21A 9%,#FF6A00 24%,#D61A00 44%,#6A0000 72%,#1A0000 100%)}
.fin .frr{position:absolute;left:50%;top:38%;width:1400px;height:1400px;margin:-700px 0 0 -700px;border-radius:50%;
  background:repeating-conic-gradient(rgba(255,244,200,.62) 0 3deg,rgba(255,244,200,0) 3deg 8.5deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 6%,transparent 55%);mask-image:radial-gradient(circle,#000 0 6%,transparent 55%);animation:frP 1.6s ease-in-out <F> infinite alternate}
@keyframes frP{from{opacity:.75}to{opacity:1}}
.fin .emb i{position:absolute;left:var(--x);bottom:-20px;width:var(--s);height:var(--s);border-radius:50%;background:#FFE7A0;box-shadow:0 0 6px 2px #FF8A00;opacity:0;animation:emb var(--t) linear var(--d) infinite}
@keyframes emb{0%{opacity:0;translate:0 0}10%{opacity:1}80%{opacity:.9}100%{opacity:0;translate:var(--dx) -900px}}
/* 「ど的中」：外側の黒い太いふち・金のふち・内側の細いふち・炎の色（上は白っぽい金 → 橙 → 赤）・光がサッと走る。少し右に傾ける */
.dlg{position:absolute;left:0;right:0;top:282px;height:200px;animation:dIn .34s cubic-bezier(.2,.9,.3,1.2) <F+.22> both,dUp .38s cubic-bezier(.5,0,.3,1) <R-.35> forwards}
@keyframes dIn{0%{opacity:0;transform:scale(2.8)}60%{opacity:1;transform:scale(.94)}100%{opacity:1;transform:scale(1)}}
@keyframes dUp{from{transform:scale(1)}to{transform:translateY(-302px) scale(.62)}}
.dlg .dfl{position:absolute;left:-20px;right:-20px;top:-40px;bottom:-30px;border-radius:50%;
  background:radial-gradient(ellipse 50% 50% at 50% 58%,rgba(255,236,150,.95) 0,rgba(255,140,0,.75) 36%,rgba(255,50,0,.35) 58%,rgba(255,40,0,0) 74%);animation:dfl .5s ease-in-out <F+.2> infinite alternate}
@keyframes dfl{from{transform:scale(1,1)}to{transform:scale(1.04,1.1)}}
/* 文字のうしろで燃える炎（ゆらゆら・ちらちら） */
.dlg .ffl{position:absolute;left:0;top:0;width:390px;height:200px;overflow:visible;filter:drop-shadow(0 0 6px rgba(255,110,0,.9))}
.dlg .ffl path{transform-box:fill-box;transform-origin:50% 100%;animation:flk var(--t) ease-in-out var(--d) infinite alternate}
@keyframes flk{0%{transform:scale(1,.82) skewX(-4deg)}50%{transform:scale(.92,1.08) skewX(3deg)}100%{transform:scale(1.04,1.16) skewX(-2deg)}}
/* 着地したときの光の輪 */
.dlg .dr{position:absolute;left:50%;top:104px;width:260px;height:260px;margin:-130px 0 0 -130px;border-radius:50%;border:7px solid #FFF3B0;
  box-shadow:0 0 22px 4px #FFB000,inset 0 0 22px 4px #FFB000;opacity:0;animation:dr .55s ease-out <F+.5> forwards}
@keyframes dr{0%{opacity:1;transform:scale(.3)}100%{opacity:0;transform:scale(2.6)}}
.dlg .dsb{position:absolute;left:0;right:0;top:-6px;text-align:center;font:700 15px/1 "BIZ UDPGothic",sans-serif;letter-spacing:.42em;padding-left:.42em;color:#FFFFFF;text-shadow:0 0 6px #FF3B00,0 0 14px #FF3B00,0 2px 0 #5A0000}
.dlg .dw{position:absolute;left:0;right:0;top:22px;height:160px;transform:skewX(-9deg)}
.dlg .dw span{position:absolute;left:-10px;right:-10px;top:0;text-align:center;white-space:nowrap;font:400 130px/160px "Dela Gothic One",sans-serif;letter-spacing:-.02em}
.dlg .dw small{font-size:90px;letter-spacing:.02em}
.dlg .o1{color:#2A0000;-webkit-text-stroke:24px #2A0000;filter:drop-shadow(2px 3px 0 #7A0A00) drop-shadow(2px 3px 0 #5A0000) drop-shadow(2px 3px 0 #3A0000) drop-shadow(0 0 22px rgba(255,110,0,.95))}
.dlg .o2{color:#FFC83A;-webkit-text-stroke:11px #FFC83A}
.dlg .o3{color:#5A0A00;-webkit-text-stroke:4px #5A0A00}
.dlg .f{background:linear-gradient(180deg,#FFFFFF 0%,#FFF6C0 15%,#FFD84A 33%,#FFFFFF 38%,#FFE58A 40%,#FFA200 53%,#FF5A00 67%,#D81000 83%,#7A0000 100%) 0 30px/100% 112px no-repeat;-webkit-background-clip:text;background-clip:text;color:transparent}
.dlg .h{background:linear-gradient(105deg,rgba(255,255,255,0) 38%,rgba(255,255,255,.95) 50%,rgba(255,255,255,0) 62%) -150% 0/60% 100% no-repeat;-webkit-background-clip:text;background-clip:text;color:transparent;
  animation:dsh 1.1s ease-in-out <F+.5> infinite}
@keyframes dsh{0%{background-position:-150% 0}60%,100%{background-position:250% 0}}
.dlg .dsp b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);background:#FFFFFF;
  clip-path:polygon(50% 0,58% 42%,100% 50%,58% 58%,50% 100%,42% 58%,0 50%,42% 42%);filter:drop-shadow(0 0 4px #FFE08A);opacity:0;animation:twinkle .9s ease-in-out var(--d) infinite}
/* 炎の中から馬がボードを持って出る（<R>）。コインは馬のうしろ・紙ふぶきは前 */
.fin .hb{z-index:6;animation:strike .8s ease-out <R> both}
@keyframes strike{0%{opacity:0;transform:translateY(-36px) scale(.7);filter:brightness(4) blur(2px)}30%{opacity:1;transform:translateY(8px) scale(1.06);filter:brightness(2.2) blur(0)}55%{transform:translateY(-4px) scale(.99);filter:brightness(1.3)}100%{transform:none;filter:none}}
.fin .conf.cb{z-index:5}
.fin .conf{z-index:7}
.fin .dlg{z-index:8}
.conf i.cn{height:var(--w);border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFFBE0 0 16%,#FFD54A 32%,#E0A100 70%,#9A6A00 100%);box-shadow:0 0 6px rgba(255,220,120,.9);animation:coin var(--t) linear var(--d) infinite}
@keyframes coin{0%{opacity:1;transform:translateY(0) rotateY(0)}85%{opacity:1}100%{opacity:0;transform:translateY(900px) rotateY(1080deg)}}
.ov.fz .close{z-index:60}
/* ボード：枠は虹色（回さない） */
.fz .board{border-color:transparent;background-clip:padding-box;box-shadow:0 0 0 3px #FFFFFF,0 0 28px 8px rgba(255,236,170,.9),0 0 64px 18px rgba(255,120,0,.6),0 12px 24px rgba(0,0,0,.35)}
.fz .board > .halo{inset:-8px;z-index:auto;border-radius:16px;filter:none}
.fz .board > .halo i{padding:8px}
.fz .board > .halo b{width:700px;height:700px;margin:-350px 0 0 -350px;animation:none}
.fz .bh{font-size:30px;background:linear-gradient(90deg,#FF3B3B,#FF9F1A,#E8C200,#2DBB55,#1FA8E0,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;filter:drop-shadow(0 2px 0 #FFFFFF) drop-shadow(0 3px 0 rgba(0,0,0,.2));
  animation:pop .55s cubic-bezier(.2,1.8,.4,1) <R+.6> both,rbowText 1.2s linear <R+.6> infinite}
.zrib{display:flex;align-items:center;justify-content:center;gap:6px;align-self:center;margin-top:1px;padding:3px 10px 3px 4px;border-radius:999px;background:var(--ink2);color:#FFFFFF;font-size:12px;font-weight:700;white-space:nowrap;
  box-shadow:0 0 0 2px #FFFFFF,0 0 12px rgba(179,76,255,.7);animation:rowIn .35s ease-out <R+.7> both}
.zrib .zt{padding:3px 8px;border-radius:999px;background:linear-gradient(180deg,#FFF3B0,#FFC21A);color:var(--ink2);font-weight:800;font-size:11.5px}
.zrib .n{min-width:22px;height:22px;font-size:12px}
.n.zx{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FF3BB8,0 0 10px 4px rgba(255,59,184,.6);animation:zx 1.2s linear infinite}
@keyframes zx{0%,100%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FF3B3B,0 0 10px 4px rgba(255,59,59,.65)}20%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FFC21A,0 0 10px 4px rgba(255,194,26,.65)}40%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #2DBB55,0 0 10px 4px rgba(45,187,85,.65)}60%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #1FA8E0,0 0 10px 4px rgba(31,168,224,.65)}80%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #B34CFF,0 0 10px 4px rgba(179,76,255,.65)}}
.fz .brows li.top{position:relative;background:linear-gradient(#FFFDF5,#FFFDF5) padding-box,linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3BB8) border-box;border:2px solid transparent;padding:4px 6px}
.fz .brows li{flex-wrap:wrap}
.fz .brows li.top{gap:3px;padding:4px 5px}
.fz .brows li.top::after{content:"";position:absolute;inset:0;border-radius:8px;pointer-events:none;background:linear-gradient(105deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.75) 50%,rgba(255,255,255,0) 70%) -130% 0/50% 100% no-repeat;animation:glint 1.8s ease-in-out <R+1.05> infinite}
.fz .btot b{background:linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3BB8) 0 100%/100% 3px no-repeat;padding-bottom:4px}
/* 視差効果を減らす：グリッチ・プチュン・ネオンのカット・爆発・ゆれ・炎の粒・紙ふぶきを止める。押すと1秒真っ暗 → 炎の画面と「ど的中」（上）・馬とボードをふわっと出す */
@media (prefers-reduced-motion:reduce){
  .push.fz,.push.fz::before,.push.fz .face,.push.fz .glit b,.pshadow.fz,.tap.fz,.aura,.prays,.edge,.frame b,.n.zx,.fz .brows li.top::after,.fz .board > .halo b{animation:none!important}
  .push.fz::after,.ov.fz .gl,.ov.fz .pc,.ov.fz .mt,.ov.fz .xf,.ov.fz .emb,.ov.fz .conf,.ov.fz .dsp,.ov.fz .dr{display:none}
  .push.fz .glit b{opacity:.6}
  .ov.fz{--t0:1.9s}
  .ov.fz .fin{animation:fadeIn .6s ease-out 1s both!important}
  .ov.fz .frr,.ov.fz .dfl,.ov.fz .dlg .h,.ov.fz .ffl path{animation:none!important}
  .ov.fz .dlg{animation:none!important;transform:translateY(-302px) scale(.62)}
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


def board(title, bets, total, top_first=False, rib='', mark=(), ring=''):
    """rib：見出しの下の帯（フリーズ：超大穴の馬）／mark：虹色の輪をつける馬番（3連単の行だけ）／ring：枠の虹（フリーズ）"""
    rows = ''
    k = 0
    for t, c, s, y, p, hit in bets:
        if not hit:
            continue
        cls = ' class="top"' if (top_first and t == '3連単') else ''
        k += 1
        rows += f'<li{cls} style="--i:{k - 1}"><span class="bt">{t}</span><span class="bc">{combo(c, s, mark if t == "3連単" else ())}</span><span class="by">{y}</span><span class="bp">{p}</span></li>'
    return f'''<div class="board">{ring}<div class="bh">{title}</div><div class="bsub">9R の当たった買い目</div>{rib}<ul class="brows">{rows}</ul><div class="btot">払戻 合計<b>{total}</b></div></div>'''


FZ_X = 11    # 見本の超大穴の馬（11番・11番人気）
# フリーズの時刻（押してから）：N＝グリッチが一瞬おさまる・C＝アイコンのドアップ・H＝横に流れる光・E＝画面が青く光る・W＝プチュン（青白い横一本線）
# ・Z＝線が点に縮んで消える（このあと真っ暗）・M＝虹色ネオンの超高速カット・F＝白い爆発 →「ど的中」・R＝馬がボード
FZ_T = dict(N=.5, C=.86, H=1.2, E=1.4, W=1.64, Z=1.98, M=4.4, F=9.9, R=11.9)
# プチュンの青い画面の細かい白い粒（1粒 約1/3px＝画面の点1つぶん。動かさない）
NOISEF = 'url("data:image/svg+xml,' + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='360' height='360'><filter id='f'>"
    "<feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='1' seed='9' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 2.4 0 0 0 -.9'/></filter>"
    "<rect width='360' height='360' filter='url(#f)'/></svg>", safe="/:=' .,-") + '")'


def svg_url(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe="/:=' .,-") + '")'


def fz_sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


def fz_css():
    """FREEZE_CSS の <M+.85>・<H-C> などを秒に直す・絵とノイズを入れる・グリッチの1コマごとの動きを足す"""
    css = re.sub(r'<([A-Z][A-Z0-9.+\-]*)>', lambda m: fz_sec(eval(m.group(1), {}, dict(FZ_T))), FREEZE_CSS)
    for k, v in (('NOISEF', NOISEF), ('ICONID', blobs['fz_icon']), ('WARPID', blobs['fz_warp']), ('NGLOW', blobs['fz_nglow']),
                 ('NCORE', blobs['fz_ncore'])):
        css = css.replace(k, v)
    return css + '/* グリッチ・文字の壁の1コマごとの動き（gen_fx.py の glitch・mt_layers で作る） */\n' + GL['css'] + MT['css'] + '\n'


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


def kf_steps(name, total, segs, base, fmt):
    """1コマずつ切りかわる動き（animation-timing-function: steps(1) で使う）。segs＝[(始まり, 終わり, 値)]・base＝それ以外の値"""
    pts = sorted({0.0, *[t for s in segs for t in s[:2] if t < total]})

    def at(t):
        for t0, t1, v in segs:
            if t0 <= t < t1:
                return v
        return base
    stops = ''.join(f'{t / total * 100:.3f}%{{{fmt(at(t))}}}' for t in pts)
    return f'@keyframes {name}{{{stops}100%{{{fmt(base)}}}}}'


# グリッチの台本：(始まり, 終わり, するもの)。S＝色ずれ(px・つけっぱなしで、ずれ方は2回だけ変わる)・L＝横ズレ（帯2本・強さpx）・B＝ブロック3つ・T＝横の線2本
# 画面のどの点も、明るい⇔暗いが1秒に3回までになるように、ズレ・ブロックは毎回ちがう場所に1コマだけ
GL_SCRIPT = [
    # 押した瞬間の画面（0〜N）
    (0.000, 0.034, 'S6 L24'), (0.034, 0.100, 'S6'), (0.100, 0.134, 'S6 B'), (0.134, 0.167, 'S6'), (0.167, 0.200, 'S10 L30 T'), (0.200, 0.267, 'S10'),
    (0.267, 0.300, 'S10 B'), (0.300, 0.334, 'S10'), (0.334, 0.367, 'S4 L20'), (0.367, 0.400, 'S4 T'), (0.400, 0.500, 'S4'),
    # 一瞬もとに戻る（N〜C）の途中で1回だけピクッ
    (0.700, 0.734, 'L12'),
    # テンゲルのアイコンのドアップ（C〜H）
    (0.860, 0.960, 'S12'), (0.960, 0.994, 'S12 L24'), (0.994, 1.060, 'S8'), (1.060, 1.094, 'S8 T'), (1.094, 1.127, 'S8 L20'), (1.127, 1.200, 'S4'),
]
GL_COLS = ['#FF2BD6', '#2FD6FF', '#3CFF6A', '#FFE53B', '#FFFFFF', '#000000', '#6A2BFF', '#FF3B3B']


def glitch(seed=61):
    """グリッチの部品（HTML）と1コマごとの動き（CSS）"""
    rnd = random.Random(seed)
    E, C, H = FZ_T['E'], FZ_T['C'], FZ_T['H']
    frames = [(t0, t1, fx.split(), 'ic' if t0 >= C else 'sn') for t0, t1, fx in GL_SCRIPT]
    css, html = [], {}
    # 色ずれ・横ズレ（押した瞬間の画面とアイコンでべつべつ）
    slices = {g: [(rnd.uniform(0, 800), rnd.uniform(14, 44)) for _ in range(n)] for g, n in (('sn', 12), ('ic', 8))}
    for g in ('sn', 'ic'):
        segs_o, segs_r, segs_c = [], [], []
        sl_segs = [[] for _ in slices[g]]
        free = list(range(len(slices[g])))
        rnd.shuffle(free)
        for t0, t1, fx, gg in frames:
            if gg != g:
                continue
            for f in fx:
                if f[0] == 'S':
                    d = float(f[1:])
                    segs_o.append((t0, t1, 1)); segs_r.append((t0, t1, (-d, 0))); segs_c.append((t0, t1, (d, 1)))
                if f[0] == 'L':
                    a = float(f[1:])
                    for _ in range(2):          # 1コマで帯2本・同じ帯は2回使わない
                        k = free.pop()
                        sl_segs[k].append((t0, t1, (rnd.choice([-1, 1]) * rnd.uniform(.4, 1) * a, rnd.random() < .3)))
        css.append(kf_steps(f'gS{g}', E, segs_o, 0, lambda v: f'opacity:{v}'))
        css.append(kf_steps(f'gR{g}', E, segs_r, (0, 0), lambda v: f'translate:{v[0]:g}px {v[1]:g}px'))
        css.append(kf_steps(f'gC{g}', E, segs_c, (0, 0), lambda v: f'translate:{v[0]:g}px {v[1]:g}px'))
        css.append(f'.gl .{g} .gS{{animation:gS{g} {fz_sec(E)} steps(1) both}}.gl .{g} .gS i{{animation:gR{g} {fz_sec(E)} steps(1) both}}.gl .{g} .gS i + i{{animation:gC{g} {fz_sec(E)} steps(1) both}}')
        els = []
        for k, ((y, h), segs) in enumerate(zip(slices[g], sl_segs)):
            if not segs:
                continue
            name = f'sl{g}{k}'
            css.append(kf_steps(name, E, segs, None,
                                lambda v: 'opacity:0;translate:0 0;filter:none' if v is None else f'opacity:1;translate:{v[0]:.0f}px 0;filter:{"invert(1) hue-rotate(90deg)" if v[1] else "none"}'))
            pos = f'0 {-y:.0f}px' if g == 'sn' else f'-795px {-148 - y:.0f}px'
            els.append(f'<i class="sl" style="top:{y:.0f}px;height:{h:.0f}px;background-position:{pos};animation:{name} {fz_sec(E)} steps(1) both"></i>')
        html[g] = ''.join(els)
    # ブロック（色の四角・ずれた画面のかけら）と横の線：毎回ちがう場所に1コマだけ
    blocks, tears = [], []
    for t0, t1, fx, g in frames:
        if 'B' in fx:
            for _ in range(3):
                x, y, w, h = rnd.uniform(-20, 330), rnd.uniform(20, 800), rnd.uniform(30, 120), rnd.uniform(6, 30)
                if rnd.random() < .5 and g == 'sn':
                    c = f'url(/_blob/{blobs["fz_warp"]}) {-x + rnd.uniform(-60, 60):.0f}px {-y:.0f}px/390px 844px'
                else:
                    c = rnd.choice(GL_COLS)
                blocks.append(f'<i style="--x:{x:.0f}px;--y:{y:.0f}px;--w:{w:.0f}px;--h:{h:.0f}px;--c:{c};--d:{fz_sec(t0)};--t:{fz_sec(t1 - t0)}"></i>')
        if 'T' in fx:
            for _ in range(2):
                tears.append(f'<i style="--y:{rnd.uniform(30, 820):.0f}px;--h:{rnd.choice([1, 1, 2, 3])}px;--c:{rnd.choice(["#FFFFFF", "#FF2BD6", "#2FD6FF", "#E8FF3A"])};--d:{fz_sec(t0)};--t:{fz_sec(t1 - t0)}"></i>')
    # 横に流れる光の筋（H〜E）
    bars = ''.join(f'<b style="--y:{rnd.gauss(422, 150):.0f}px;--h:{rnd.choice([1, 2, 2, 3, 4, 6])}px;--c:{rnd.choice(["#7FE0FF", "#3CFF6A", "#E8FF3A", "#FFFFFF", "#2F8BFF"])};'
                   f'--d:{fz_sec(H + rnd.uniform(0, .1))};--t:{fz_sec(rnd.uniform(.12, .2))}"></b>' for _ in range(14))
    html['all'] = (f'<div class="gl" aria-hidden="true">'
                   f'<div class="sn"><div class="gS"><i></i><i></i></div>{html["sn"]}</div>'
                   f'<div class="ic"><div class="ib"></div><div class="gS"><i></i><i></i></div>{html["ic"]}</div>'
                   f'<div class="sm"><div class="st"></div>{bars}</div>'
                   f'<div class="gsc"></div><div class="gbk">{"".join(blocks)}</div><div class="gtr">{"".join(tears)}</div></div>')
    return dict(css='\n'.join(css) + '\n', html=html['all'])


def bez_prog(t, x1, y1, x2, y2):
    """cubic-bezier の時刻 t（0〜1）のときの進み（0〜1）"""
    bx = lambda s: 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
    by = lambda s: 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if bx(m) < t else (lo, m)
    return by((lo + hi) / 2)


def jag(rnd, x0, y0, x1, y1, n, amp):
    """ギザギザの線（稲妻）"""
    pts = []
    for j in range(n + 1):
        u = j / n
        k = math.sin(math.pi * u) * amp * rnd.uniform(-1, 1)
        nx, ny = -(y1 - y0), (x1 - x0)
        L = math.hypot(nx, ny) or 1
        pts.append((x0 + (x1 - x0) * u + nx / L * k, y0 + (y1 - y0) * u + ny / L * k))
    return 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts), pts[-1]


def pc_layers(seed=93):
    """プチュン：青い画面・白い光・横一本線・まん中のフレア・ジリジリの稲妻・散る光の粒"""
    rnd = random.Random(seed)
    E, W, Z = FZ_T['E'], FZ_T['W'], FZ_T['Z']
    y0 = 422
    arcs = []

    def add(path, d, t, sw):
        arcs.append(f'<path style="--d:{fz_sec(d)};--t:{fz_sec(t)};stroke-width:{sw}" d="{path}"></path>')
    for _ in range(20):            # 青い画面のジリジリ（E〜W）：まん中の横の帯のあたりに大きめの稲妻
        d, t = rnd.uniform(E + .02, W - .02), rnd.uniform(.035, .07)
        x, y = rnd.uniform(10, 380), y0 + rnd.gauss(0, 55)
        L, a = rnd.uniform(40, 150), math.radians(rnd.uniform(-25, 25)) + rnd.choice([0, math.pi])
        add(jag(rnd, x, y, x + math.cos(a) * L, y + math.sin(a) * L, rnd.randint(5, 9), rnd.uniform(8, 22))[0], d, t, 1.4)
    for _ in range(40):            # 横一本線のまわり（W〜Z）：線にまとわりつく細かい稲妻
        d, t = rnd.uniform(W + .05, Z - .01), rnd.uniform(.03, .06)
        x, L, side = rnd.uniform(0, 390), rnd.uniform(14, 60), rnd.choice([-1, 1])
        path, end = jag(rnd, x - L / 2, y0 + rnd.uniform(-1, 1), x + L / 2, y0 + side * rnd.uniform(2, 14), rnd.randint(3, 6), rnd.uniform(2, 7))
        add(path, d, t, .9)
        if rnd.random() < .45:
            arcs.append(f'<circle style="--d:{fz_sec(d)};--t:{fz_sec(t)}" cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="1"></circle>')
    for _ in range(12):            # 線が縮むとき（Z〜）：残っている線の上だけ
        d, t = rnd.uniform(Z, Z + .15), rnd.uniform(.03, .05)
        hw = 195 * (1 - bez_prog((d - Z) / .18, .55, 0, .9, .45))
        x, L, side = rnd.uniform(195 - hw, 195 + hw), rnd.uniform(10, 36), rnd.choice([-1, 1])
        add(jag(rnd, x - L / 2, y0, x + L / 2, y0 + side * rnd.uniform(2, 10), rnd.randint(3, 5), rnd.uniform(2, 5))[0], d, t, .9)
    dust = ''
    for _ in range(28):            # 点になったところから散る光の粒
        x = 195 + rnd.uniform(-36, 36)
        dust += (f'<i style="--x:{x:.1f}px;--y:{y0 + rnd.uniform(-3, 3):.1f}px;--d:{fz_sec(Z + rnd.uniform(.1, .22))};--t:{fz_sec(rnd.uniform(.3, .55))};'
                 f'--dx:{(x - 195) * rnd.uniform(.5, 1.6) + rnd.uniform(-20, 20):.0f}px;--dy:{rnd.uniform(-26, 26):.0f}px"></i>')
    return (f'<div class="pc" aria-hidden="true"><div class="pcb"></div><div class="pcg"></div><div class="pcl"></div>'
            f'<div class="pcf"><i class="f1"></i><i class="f2"></i><i class="f3"></i></div>'
            f'<svg class="pca" viewBox="0 0 390 844">{"".join(arcs)}</svg><div class="pcd">{dust}</div></div>')


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


def tx(text, y, h, fs, d, cols, r=0, x=0, w=390, dark=False, sw=14):
    """ネオンの文字（白い太いふち＋光・色）。cols＝(上の色, まん中の色, 下の色, 光の色)"""
    c1, c2, c3, g = cols
    return (f'<div class="tx{" dk" if dark else ""}" style="--x:{x}px;--w:{w}px;--y:{y}px;--h:{h}px;--fs:{fs}px;--d:{fz_sec(d)};--r:{r}deg;'
            f'--c1:{c1};--c2:{c2};--c3:{c3};--g:{g};--sw:{sw}px"><span class="o">{text}</span><span class="f">{text}</span></div>')


def ring(x, y, d, g):
    return f'<i class="tr" style="--x:{x:g}px;--y:{y:g}px;--d:{fz_sec(d)};--g:{g}"></i>'


TX_PINK = ('#FFF26B', '#FF5AD2', '#8A2BFF', '#FF2BD6')
TX_CYAN = ('#B8FFF6', '#2FD6FF', '#3C5BFF', '#2FD6FF')
TX_GOLD = ('#FFF6B0', '#FFB21A', '#FF3B3B', '#FFB21A')
TX_LIME = ('#E8FFB0', '#3CFF6A', '#0FA850', '#3CFF6A')
TX_FIRE = ('#FFFFFF', '#FFD84A', '#FF5A00', '#FFFFFF')


def mt_layers(seed=71):
    """虹色ネオンのカット（T1〜T6）：まさちゃんの指定の文字「とんでも！」「とんでも！」「とんでも！とんでも！」「ど！ど！ど！ど！」「ど的中！！！！」"""
    M = FZ_T['M']
    t1 = tx('とんでも！', 470, 110, 72, M + .12, TX_PINK, r=-5) + ring(195, 525, M + .12, '#FF2BD6')
    t2 = tx('とんでも！', 230, 110, 74, M + .82, TX_CYAN, r=4) + ring(195, 285, M + .82, '#2FD6FF')
    t3 = (tx('とんでも！', 290, 100, 64, M + 1.52, TX_GOLD, r=-3) + ring(195, 340, M + 1.52, '#FFB21A')
          + tx('とんでも！', 400, 100, 64, M + 1.74, TX_LIME, r=3) + ring(195, 450, M + 1.74, '#3CFF6A'))
    t4 = ''
    for i, ((x, y), r, cols) in enumerate(zip(((4, 230), (196, 230), (4, 380), (196, 380)), (-6, 5, 4, -5), (TX_PINK, TX_CYAN, TX_GOLD, TX_LIME))):
        d = M + 2.34 + i * .22
        t4 += tx('ど！', y, 120, 88, d, cols, r=r, x=x, w=190) + ring(x + 95, y + 60, d, cols[3])
    t5 = tx('ど的中', 290, 150, 112, M + 3.48, TX_FIRE, r=-4, dark=True, sw=18) + ring(195, 365, M + 3.48, '#FFFFFF')
    for i, cols in enumerate((TX_PINK, TX_GOLD, TX_LIME, TX_CYAN)):
        t5 += tx('！', 440, 110, 84, M + 3.66 + i * .1, cols, r=-4, x=27 + 84 * i, w=84, dark=True, sw=16)
    t6 = (tx('とんでも！とんでも！', 96, 60, 34, M + 4.56, TX_PINK, sw=8) + tx('ど！ど！ど！ど！', 158, 64, 40, M + 4.7, TX_CYAN, sw=8)
          + tx('ど的中！！！！', 226, 74, 48, M + 4.84, TX_GOLD, sw=10))
    html = f'''<div class="mt" aria-hidden="true">
      <div class="sc t1"><div class="bg"></div><div class="dk"></div>{neon_icon()}{t1}</div>
      <div class="sc t2"><div class="stf"></div><div class="spd"></div><div class="orb"></div><div class="spk">{sparkles(26, 47)}</div>{t2}</div>
      <div class="sc t3"><div class="zz">{zigzag()}</div>{t3}</div>
      <div class="sc t4"><div class="stf"></div><div class="glw"></div><div class="spk">{sparkles(22, 43, white=True)}</div>{t4}</div>
      <div class="sc t5"><div class="bu"></div><div class="bs"></div><div class="dkb"></div>{t5}</div>
      <div class="sc t6">{neon_icon(alt=True)}<div class="shd"></div><div class="spk">{sparkles(16, 53)}</div>{t6}</div>
      <div class="mfl a"></div><div class="mfl b"></div>
    </div>'''
    return dict(css='', html=html)


def explosion(seed=97):
    """白い爆発（ギザギザのふちが桃・黄・水色）"""
    rnd = random.Random(seed)
    n = 64
    rs = [rnd.uniform(.55, 1.0) if i % 2 == 0 else rnd.uniform(.28, .5) for i in range(n)]
    poly = lambda sc: ' '.join(f'{450 + 440 * sc * r * math.cos(2 * math.pi * i / n):.0f},{450 + 440 * sc * r * math.sin(2 * math.pi * i / n):.0f}' for i, r in enumerate(rs))
    return ('<svg viewBox="0 0 900 900" aria-hidden="true">'
            + ''.join(f'<polygon points="{poly(sc)}" fill="{c}"></polygon>' for c, sc in (('#FF2BD6', 1.12), ('#FFE53B', 1.07), ('#2FD6FF', 1.03), ('#FFFFFF', 1.0))) + '</svg>')


def embers(n, seed):
    """炎の粒（下から上へ）"""
    rnd = random.Random(seed)
    F = FZ_T['F']
    return ''.join(f'<i style="--x:{rnd.uniform(0, 390):.0f}px;--s:{rnd.uniform(3, 6):.1f}px;--t:{rnd.uniform(1.6, 3.2):.2f}s;--d:{F + rnd.uniform(0, 2):.2f}s;--dx:{rnd.uniform(-60, 60):.0f}px"></i>' for _ in range(n))


def dlogo():
    """「ど的中」（外側の黒いふち・金のふち・内側のふち・炎の色・光が走る）＋上の小さい英語＋きらめき"""
    F = FZ_T['F']
    word = '<small>ど</small>的中'
    layers = ''.join(f'<span class="{c}">{word}</span>' for c in ('o1', 'o2', 'o3', 'f', 'h'))
    glints = ''.join(f'<b style="--x:{x}px;--y:{y}px;--s:{s}px;--d:{F + .5 + i * .15:.2f}s"></b>'
                     for i, (x, y, s) in enumerate(((52, 70, 22), (150, 44, 28), (262, 40, 24), (352, 92, 30), (300, 178, 20), (86, 176, 24))))
    rnd = random.Random(23)
    flames = ''
    for i in range(15):
        cx = 12 + i * 26.3 + rnd.uniform(-7, 7)
        w, h, base = rnd.uniform(46, 78), rnd.uniform(120, 200) * (1.15 if 4 <= i <= 10 else .85), 168 + rnd.uniform(-6, 6)
        d = (f'M{cx - w / 2:.0f} {base:.0f} C{cx - w / 2:.0f} {base - h * .45:.0f} {cx - w * .12:.0f} {base - h * .55:.0f} {cx + rnd.uniform(-6, 6):.0f} {base - h:.0f} '
             f'C{cx + w * .12:.0f} {base - h * .55:.0f} {cx + w / 2:.0f} {base - h * .45:.0f} {cx + w / 2:.0f} {base:.0f} Z')
        flames += f'<path d="{d}" fill="url(#dflg)" style="--t:{rnd.uniform(.45, .7):.2f}s;--d:{-rnd.uniform(0, .6):.2f}s"></path>'
    grad = ('<defs><linearGradient id="dflg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FFE680" stop-opacity="0"></stop><stop offset=".1" stop-color="#FFFFFF"></stop><stop offset=".26" stop-color="#FFE680"></stop>'
            '<stop offset=".5" stop-color="#FF9A00" stop-opacity=".95"></stop><stop offset=".8" stop-color="#FF3A00" stop-opacity=".6"></stop>'
            '<stop offset="1" stop-color="#B00000" stop-opacity="0"></stop></linearGradient></defs>')
    return (f'<div class="dlg" role="img" aria-label="ど的中"><div class="dfl"></div><svg class="ffl" viewBox="0 0 390 200" aria-hidden="true">{grad}{flames}</svg>'
            f'<div class="dr"></div><div class="dsb">SUPER LONGSHOT</div><div class="dw">{layers}</div><div class="dsp">{glints}</div></div>')


def fz_layers(bets, total):
    """フリーズの押したあと（下から）：黒 → 炎の画面（「ど的中」・馬とボード）→ ネオンのカット → プチュン → グリッチ → 爆発"""
    rib = f'<div class="zrib"><b class="zt">超大穴</b>{num(FZ_X, " zx")}<span>{FZ_X}番人気が3連単に！</span></div>'
    ring = '<i class="halo" aria-hidden="true"><i><b></b></i></i>'
    R = FZ_T['R']
    return f'''<div class="blk"></div>
    <div class="fin"><div class="fsk">
      <div class="fb"></div><div class="frr"></div>
      <div class="emb">{embers(36, 11)}</div>
      <div class="conf cb">{coins(22, 8, R)}</div>
      <div class="hb">
        <img src="/_blob/{blobs['back']}" alt="ボードを持つ馬">
        {board('フリーズ的中!!!', bets, total, top_first=True, rib=rib, mark=(FZ_X,), ring=ring)}
        <img src="/_blob/{blobs['front']}" alt="">
      </div>
      {dlogo()}
      <div class="conf">{confetti(40, 7, rainbow=True, d0=R)}</div>
    </div></div>
    {MT['html']}
    {pc_layers()}
    {GL['html']}
    <div class="xf" aria-hidden="true"><div class="xpl">{explosion()}</div><div class="xf2"></div></div>'''


GL = glitch()
MT = mt_layers()


def page(kind):
    big = kind == 'big'
    fz = kind == 'fz'
    fin = (6, 2, 10)
    if fz:
        bets = [('3連単', [FZ_X, 6, 2], '→', '100円', '286,370円', True), ('馬単', [FZ_X, 6], '→', '100円', '24,180円', True), ('ワイド', [2, FZ_X], '-', '100円', '4,950円', True)]
        total, fin = '315,500円', (FZ_X, 6, 2)
        note = f'3連単が当たって、3頭の中に超大穴（10〜12番人気）がいるので、記録するとフリーズ的中ボタンが出るよ（見本・架空のレース。{FZ_X}番が{FZ_X}番人気）'
    elif big:
        bets = [('3連単', [6, 2, 10], '→', '100円', '48,920円', True), ('馬単', [6, 2], '→', '100円', '1,840円', True), ('ワイド', [2, 10], '-', '100円', '0円', False)]
        total, note = '50,760円', '3連単が当たったので、記録するとデカ的中ボタンが出るよ（見本・架空のレース）'
    else:
        bets = [('馬単', [6, 2], '→', '100円', '1,840円', True), ('馬連', [2, 6], '-', '100円', '690円', True), ('3連単', [6, 10, 2], '→', '100円', '0円', False)]
        total, note = '2,530円', '3連単は外れ・馬単と馬連が当たったので、記録すると的中ボタンが出るよ（見本・架空のレース）'
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
    if big:
        layers = ('<div class="rbow"></div><div class="glow"></div><div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>'
                  '<div class="spk">' + sparkles(26, 9) + '</div>')
        title = 'デカ的中!!'
        conf = confetti(34, 3, rainbow=True)
        flash = '<div class="flash"></div>'
    else:
        layers = '<div class="rays"></div>'
        title = '的中！'
        conf = confetti(28, 2)
        flash = ''
    nhit = sum(1 for b in bets if b[5])
    reveal = f'''  <sc-if value="{{{{isReveal}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov{pb} {'big' if big else 'hit'}" style="--n:{nhit}">
    <div class="dim"></div>
    {layers}
    <div class="pressed{pb}"></div>
    <div class="hb">
      <img src="/_blob/{blobs['back']}" alt="ボードを持つ馬">
      {board(title, bets, total, top_first=big)}
      <img src="/_blob/{blobs['front']}" alt="">
    </div>
    <div class="conf">{conf}</div>
    {flash}
    <button class="close" type="button" onClick="{{{{toForm}}}}">とじる</button>
  </div>
  </sc-if>'''
    if fz:
        push = f'''  <sc-if value="{{{{isPush}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov fz">
    {fz_push()}
  </div>
  </sc-if>'''
        reveal = f'''  <sc-if value="{{{{isReveal}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov fz" style="--n:{nhit}">
    {fz_layers(bets, total)}
    <button class="close" type="button" onClick="{{{{toForm}}}}">とじる</button>
  </div>
  </sc-if>'''
    css = (COMMON_CSS.replace('RANCH', RANCH_VARS) + (BIG_CSS + fz_css() if fz else BIG_CSS if big else HIT_CSS))
    css = (css.replace('HBW2', f'{HB_W / 2:g}').replace('HBW', f'{HB_W:g}').replace('HBH', f'{HB_H:g}')
              .replace('BDX', f'{BD["x"]:g}').replace('BDY', f'{BD["y"]:g}').replace('BDW', f'{BD["w"]:g}').replace('BDH', f'{BD["h"]:g}'))
    name = 'フリーズ的中ボタン' if fz else 'デカ的中ボタン' if big else '的中ボタン'
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{name}（デフォルト）</title>
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
<script type="text/x-dc" data-dc-script data-props='{{"start":{{"editor":"enum","options":["form","push","reveal"],"default":"form"}},"$preview":{{"width":390,"height":844}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    var st = this.state || {{}};
    var ph = st.ph || this.props.start || 'form';
    var self = this;
    return {{
      isPush: ph === 'push',
      isReveal: ph === 'reveal',
      toPush: function () {{ self.setState({{ ph: 'push' }}); }},
      toReveal: function () {{ self.setState({{ ph: 'reveal' }}); }},
      toForm: function () {{ self.setState({{ ph: 'form' }}); }}
    }};
  }}
}}
</script>
</body>
</html>
'''


MEMO_W, MEMO_H = 2200, 1400


def memo_page():
    """メモのボード（静止画13枚＋Fableに渡す決まり）"""
    def still(key, cap):
        return f'<figure class="st"><img src="/_blob/{blobs[key]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'
    hit = still('s_hit_form', '① 記録する') + still('s_hit_push', '② PUSHが上下に動く') + still('s_hit_board', '③ タップ → 馬がボード')
    big = still('s_big_push', '① 大きいPUSH（虹の輪）') + still('s_big_light', '② 虹色の光に包まれる') + still('s_big_board', '③ 光の中から馬がボード')
    fz = (still('s_fz_push', '① 虹色の超デカPUSH') + still('s_fz_glitch', '② 画面がバグる') + still('s_fz_line', '③ プチュン（横一本線）')
          + still('s_fz_tonde', '④「とんでも！」') + still('s_fz_dodo', '⑤「ど！ど！ど！ど！」') + still('s_fz_logo', '⑥ ど的中') + still('s_fz_result', '⑦ 炎の中から馬がボード'))
    N, C, H, E, W, Z, M, F, R = (FZ_T[k] for k in 'NCHEWZMFR')
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
</style>
</helmet>
<div class="gd">
  <h1 class="t1">的中ボタン・デカ的中ボタン・フリーズ的中ボタン（デフォルト）</h1>
  <p class="t2">まさちゃんの指定：記録して <b>当たり → 的中ボタン</b>、<b>3連単が当たり → デカ的中ボタン</b>、<b>3連単の当たりに超大穴（10〜12番人気）の馬 → フリーズ的中ボタン</b>。タップすると、壁紙の馬がボードを持って出てきて、当たった買い目を報告する。フリーズは、まさちゃんの送ってくれたパチスロのフリーズの動画のように（台の絵や文字は使わない）：虹色にギラギラ光るめちゃくちゃデカいPUSH → タップで画面がバグる → テンゲルのアイコンのドアップ → 画面が青く光って青白い横一本線に「プチュン」（静電気がジリジリ → 点に縮んで消える）→ 真っ暗のまま2秒 → 虹色ネオンのカットに「とんでも！」「とんでも！」「とんでも！とんでも！」「ど！ど！ど！ど！」「ど的中！！！！」→ 白い爆発 →「ど的中」が炎と光の中からドーン → 炎の中から馬がボード。視覚酔いしないように、画面全体が回る・迫る・ゆれる動きはしない。となりの3つの画面は、タップで動く見本（どれもデフォルト＝全テーマ共通の動き）。</p>
  <div class="rows">
    <section class="grp"><h2>的中ボタン<small>当たったとき</small></h2><div class="sts">{hit}</div></section>
    <section class="grp"><h2>デカ的中ボタン<small>3連単が当たったとき</small></h2><div class="sts">{big}</div></section>
    <section class="grp fzg"><h2>フリーズ的中ボタン<small>3連単の当たりに超大穴（10〜12番人気）</small></h2><div class="sts">{fz}</div></section>
  </div>
  <div class="boxes">
    <div class="box"><h3>出るとき</h3><ul><li>結果を<b>記録したとき</b>だけ（あとで直したとき・まとめて入れた記録・外れ・中止では出ない）</li><li>出るのは1つだけ。強い順に <b>フリーズ</b>（3連単が当たって、その3頭に超大穴＝10〜12番人気がいる。13番人気より下は入れない）＞ <b>デカ</b>（3連単が当たり）＞ <b>的中</b>（それ以外の当たり）</li><li>人気は、そのレースを判定したときの単勝オッズの順（判定の超大穴 J・K・L と同じ）。人気がわからないレースはフリーズにしない（デカ）<b>※仮</b></li><li>お知らせ（発走15分後）から開いて記録したときも同じ</li></ul></div>
    <div class="box"><h3>流れと時間（的中・デカ）</h3><ul><li><b>的中</b>：押す → 0.3秒 馬が下から → 0.95秒「的中！」→ 1.15秒〜 買い目 → 1.8秒 とじる</li><li><b>デカ</b>：押す → 0.2秒 白く光る → 0.25秒 虹の光の筋と輪 → 0.85秒 光の中から馬 → 1.5秒「デカ的中!!」→ 1.75秒〜 買い目 → 2.5秒 とじる</li><li><b>PUSHは横長の長方形（角は丸い）</b>。上下に0.9秒（デカは0.8秒・大きく・まわりに虹の輪）でくり返す</li></ul></div>
    <div class="box"><h3>フリーズの流れと時間</h3><ul><li><b>PUSH</b>：横340×縦170・角46px（デカの1.2倍）。虹色が流れる面・ラメ・白い光がサッと走る・白と紫のふち・まわりに虹の輪。上下に22px・0.85秒／1.3秒ごとにブルブルッ／画面のふちが虹色に光る</li><li><b>バグる（0〜{sec(E)}秒）</b>：押した瞬間の画面に赤と水色の色ずれ（ずれ方が2回変わる）・1コマ（1/30秒）だけ横にズレる帯・ブロック・横の線（毎回ちがう場所）・走査線 → {sec(N)}秒 一瞬もとに戻る → {sec(C)}秒 テンゲルのアイコンのドアップ（バグりながら少し引く）→ {sec(H)}秒 横に流れる光の筋</li><li><b>プチュン（{sec(E)}秒〜）</b>：画面が青く光って、まん中の白い光がふくらむ・稲妻がジリジリ → {sec(W)}秒 画面が縦につぶれて<b>青白い横一本線</b>（まん中に光のフレア・線にまとわりつく静電気）→ {sec(Z)}秒 線が両はしから点に縮んで消える（光の粒が散る）→ <b>真っ暗のまま約2秒</b>（フリーズの間）</li><li><b>虹色ネオンのカット（{sec(M)}〜{sec(F)}秒・6つ）</b>：カットごとに文字がポンと出る（まさちゃんの指定）：白く光る → テンゲルのアイコンのネオンに「とんでも！」→ 星空と光の玉に「とんでも！」→ ネオンのギザギザに「とんでも！」「とんでも！」→ 白く光る → 星空に「ど！」「ど！」「ど！」「ど！」（2×2）→ 虹の光の筋に「ど的中」「！！！！」→ アイコンのドアップ（ネオン）に4つをまとめて。背景は止まったまま（回る・迫る・流れる・ゆれるはなし）</li><li><b>{sec(F)}秒 白い爆発 →「ど的中」</b>が炎と光の中からドーン（光の輪・炎がゆらゆら・光がサッと走る・きらめき。上に小さく SUPER LONGSHOT。画面はゆらさない）→ {sec(R - .35)}秒 上へ → <b>{sec(R)}秒</b> 炎の中から馬がボード → {sec(R + .6)}秒「フリーズ的中!!!」→ {sec(R + .85)}秒〜 買い目 → {sec(R + .85 + .45 + .35)}秒 とじる</li></ul></div>
    <div class="box"><h3>重ねる順（下から）</h3><ul><li><b>的中・デカ</b>：暗い幕 → 光 → <b>馬（うしろの絵）→ ボード（文字はHTML）→ 前足の先（前の絵）</b>（ひづめがボードのふちにかかる）→ 紙ふぶき → とじる → （デカ）白い光</li><li><b>フリーズ</b>：黒 → 炎の画面（炎の色・光の筋・炎の粒・コイン・馬とボード・「ど的中」・紙ふぶき）→ ネオンのカット（6つ・文字・白い光）→ プチュン（青い画面・白い光・線・フレア・稲妻・光の粒）→ バグる（押した瞬間の画面の絵・色ずれ・横ズレの帯・アイコンのドアップ・横に流れる光・走査線・ブロック・横の線）→ 白い爆発・光 → とじる</li></ul></div>
    <div class="box"><h3>ボードに書くもの</h3><ul><li>R・当たった買い目（券種・馬番・金額・払戻）・払戻の合計。ユーザーが自分で入れた買い目だけ（判定の画面に点数・組番を出さない決まりはそのまま）</li><li>デカ・フリーズは3連単の行がいちばん上で虹色の枠（フリーズは光が走る）</li><li><b>フリーズ</b>：上に「ど的中」（炎）・見出し「フリーズ的中!!!」・その下に「超大穴 ⑪ 11番人気が3連単に！」の帯・3連単の行の超大穴の馬番に虹色の輪・ボードの枠は虹色（回さない）</li><li>払戻が長いと次の行へ。帯のぶんボードが長いので、フリーズは6行まで（7つ以上は上から5行＋「ほか○点」<b>※仮</b>）</li></ul></div>
    <div class="box"><h3>テーマ（壁紙）ごとに変えるところ</h3><ul><li><b>馬の絵2枚</b>（うしろ・前足の先）と、ボードの四角の位置</li><li>PUSHの色（--pushA・--pushB・--pushC・--rim・--rimD）・ボードの枠・面・文字（--bFrame・--bFace・--bInk・--hitRed）・光の色（--ray）</li><li><b>フリーズは全テーマ共通</b>（変わるのは馬の絵とボードの面・文字だけ）。回る虹（虹のぐるぐる）は使わない（虹色は流れるだけ）</li><li>シルバー帯・ゴールド帯・マスター帯は指示書9.1の指定どおり（あとで作る）</li></ul></div>
    <div class="box"><h3>光と見やすさ</h3><ul><li><b>視覚酔いしないように</b>：画面全体が回る・迫る（トンネル）・流れる・ゆれる動きはしない。背景は止めて、動くのは文字がポンと出るところ・小さな光・炎の粒だけ。虹色が流れるのは4秒で1回りよりゆっくり</li><li>強く光るのは<b>画面のどの点でも1秒に3回まで</b>（光の点めつで気分が悪くなる人がいるため。スマホは画面が目に近いので、画面の10%の広さでも数えた）。動画の明るさを1コマずつ・点ごとに測って確かめた。白く光るのは {sec(M)}秒・{sec(M + 2.2)}秒（どちらも弱め）・{sec(F)}秒（爆発）・{sec(R - .45)}秒</li><li>iPhoneの「視差効果を減らす」がオンなら：バグる・プチュン・ネオンのカット・爆発・炎のゆらゆら・炎の粒・紙ふぶき・PUSHの動きを止める。押すと1秒真っ暗 → 炎の画面と「ど的中」（上）・馬とボードをふわっと出す。音は見本に入れていない</li></ul></div>
    <div class="box"><h3>容量</h3><ul><li>馬の絵は1テーマ約27KB（WebP 2枚）。フリーズで足す絵は<b>テンゲルのアイコン</b>（App Storeのアイコンと同じ絵・WebP 750×750 約52KB）と、アイコンから作った<b>ネオンの線画のマスク2枚</b>（芯 1024 約59KB・光 512 約40KB。neon_icon.py）。ほかの虹・文字・炎・ギザギザ・爆発・稲妻はCSSとSVG</li><li>バグるのに使う「押した瞬間の画面の絵」は、アプリでは押した瞬間に撮る（WKWebView の takeSnapshot）。見本では見本の画面の絵（WebP 約60KB）</li><li>動きは全部CSS（動画なし）・新しいフォントなし（Dela Gothic One・BIZ UDPゴシック）。いまの馬は見本（牧場の栗毛）</li></ul></div>
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
          's_fz_push', 's_fz_glitch', 's_fz_line', 's_fz_tonde', 's_fz_dodo', 's_fz_logo', 's_fz_result')

if __name__ == '__main__':
    out = os.environ.get('FX_OUT', P)
    for kind, fn in (('hit', 'Fx_Hit.dc.html'), ('big', 'Fx_Big.dc.html'), ('fz', 'Fx_Freeze.dc.html')):
        open(f'{out}/{fn}', 'w', encoding='utf-8').write(page(kind))
        print(fn)
    if all(k in blobs for k in STILLS):
        open(f'{out}/Fx_Memo.dc.html', 'w', encoding='utf-8').write(memo_page())
        print('Fx_Memo.dc.html')
