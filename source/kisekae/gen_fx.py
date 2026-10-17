"""的中ボタン・デカ的中ボタン（ベース）の見本の画面：Fx_Hit.dc.html・Fx_Big.dc.html
   python3 gen_fx.py fx_blobs.json
   fx_blobs.json：{"back": "<id>", "front": "<id>"}（ボードを持つ馬の2枚）
   流れ：記録する → PUSHボタン（上下に動く）→ タップ → 馬がボードを持って出てくる（ボードに当たった買い目）"""
import os, re, sys, json, random
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
WAKU = {6: 'w5', 2: 'w2', 10: 'w7', 7: 'w6', 1: 'w1', 4: 'w4'}   # 判定画面の見本と同じ色に合わせる


def num(n):
    return f'<span class="n {WAKU.get(n, "w1")}">{n}</span>'


def combo(nums, sep):
    s = f'<span class="ar">{sep}</span>'
    return s.join(num(x) for x in nums)


CONF_COLS_HIT = ['#E8382F', '#F3C316', '#3E7B1E', '#1F5FC9', '#F27BB0', '#FFFFFF', '#F08A1C']


def confetti(n, seed, rainbow=False):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(2, 98)
        d = rnd.uniform(0, 2.2)
        t = rnd.uniform(2.4, 4.2)
        w = rnd.uniform(6, 10)
        h = rnd.uniform(10, 16)
        r = rnd.choice([-1, 1]) * rnd.uniform(360, 900)
        c = f'hsl({int(i * 360 / n)},95%,62%)' if rainbow else rnd.choice(CONF_COLS_HIT)
        out.append(f'<i style="--x:{x:.1f}%;--d:{d:.2f}s;--t:{t:.2f}s;--w:{w:.0f}px;--h:{h:.0f}px;--r:{r:.0f}deg;--c:{c}"></i>')
    return ''.join(out)


def sparkles(n, seed):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(4, 96); y = rnd.uniform(6, 92)
        s = rnd.uniform(10, 26); d = rnd.uniform(0, 1.6)
        out.append(f'<b style="--x:{x:.1f}%;--y:{y:.1f}%;--s:{s:.0f}px;--d:{d:.2f}s;--c:hsl({rnd.randint(0, 359)},100%,75%)"></b>')
    return ''.join(out)


COMMON_CSS = r'''body{margin:0}
*{box-sizing:border-box}
.ph{RANCH}
.ph{--pushA:#E8382F;--pushB:#A51A12;--pushC:#FF9A8A;--rim:#F6E7B8;--rimD:#B98A3A;--bFrame:#8A5A2B;--bFace:#FFFDF5;--bInk:#3A2414;--hitRed:#E8382F;--ray:rgba(255,236,170,.55)}
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
/* PUSHボタン */
.pbox{position:relative;display:flex;flex-direction:column;align-items:center}
.push{position:relative;z-index:2;width:150px;height:150px;border-radius:50%;border:0;padding:0;cursor:pointer;
  background:radial-gradient(circle at 34% 28%,#FFFFFF 0 5%,var(--pushC) 13%,var(--pushA) 44%,var(--pushB) 82%,#5E0A05 100%);
  box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #6E4E1A,0 22px 34px rgba(0,0,0,.5);
  animation:bob .9s ease-in-out infinite,popIn .35s cubic-bezier(.2,1.6,.4,1) both}
.push span{position:relative;font:400 38px/1 "Dela Gothic One",sans-serif;color:#FFFFFF;letter-spacing:.04em;text-shadow:0 3px 0 var(--pushB),0 0 14px rgba(255,255,255,.55)}
.push::after{content:"";position:absolute;inset:-18px;border-radius:50%;border:3px solid rgba(255,232,150,.95);animation:ring 1.2s ease-out infinite}
.pshadow{width:150px;height:22px;margin-top:22px;border-radius:50%;background:rgba(0,0,0,.45);filter:blur(4px);animation:shad .9s ease-in-out infinite}
.tap{margin:16px 0 0;font:400 20px/1 "Dela Gothic One",sans-serif;color:#FFF3C8;letter-spacing:.1em;animation:blink 1s steps(2) infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-18px)}}
@keyframes shad{0%,100%{transform:scale(1);opacity:.55}50%{transform:scale(.72);opacity:.3}}
@keyframes ring{0%{transform:scale(.88);opacity:.95}100%{transform:scale(1.4);opacity:0}}
@keyframes popIn{from{scale:.2}to{scale:1}}
@keyframes blink{0%{opacity:1}100%{opacity:.35}}
/* 押したあと */
.pressed{position:absolute;z-index:3;left:50%;top:50%;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;
  background:radial-gradient(circle at 34% 28%,#FFFFFF 0 5%,var(--pushC) 13%,var(--pushA) 44%,var(--pushB) 82%,#5E0A05 100%);
  box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD);animation:press .45s ease-in both}
@keyframes press{0%{transform:scale(1)}35%{transform:scale(.82);filter:brightness(1.4)}100%{transform:scale(1.9);opacity:0;filter:brightness(3)}}
/* ボードを持つ馬 */
.hb{position:absolute;z-index:6;left:50%;top:150px;width:HBWpx;height:HBHpx;margin-left:-HBW2px}
.hb img{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}
.board{position:absolute;left:BDXpx;top:BDYpx;width:BDWpx;height:BDHpx;border-radius:16px;border:8px solid var(--bFrame);background:var(--bFace);
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
@media (prefers-reduced-motion:reduce){.push,.pshadow,.push::after,.tap,.conf i,.rays,.rbow,.ring,.spk b{animation:none!important}.conf{display:none}}
'''

HIT_CSS = r'''
/* ---------- 的中：あたたかい光 → 馬が下から出る ---------- */
.rays{position:absolute;z-index:4;left:50%;top:44%;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;
  background:repeating-conic-gradient(var(--ray) 0 7deg,transparent 7deg 18deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);
  animation:raysIn .6s ease-out .2s both,spin 22s linear infinite}
@keyframes raysIn{from{opacity:0;scale:.3}to{opacity:1;scale:1}}
@keyframes spin{to{rotate:360deg}}
.hit .hb{animation:riseUp .7s cubic-bezier(.2,1.35,.4,1) .3s both}
@keyframes riseUp{from{transform:translateY(560px)}to{transform:translateY(0)}}
.hit .bh{animation:pop .5s cubic-bezier(.2,1.8,.4,1) .95s both}
@keyframes pop{0%{transform:scale(0)}100%{transform:scale(1)}}
.hit .brows li{animation:rowIn .35s ease-out both}
.hit .brows li:nth-child(1){animation-delay:1.15s}
.hit .brows li:nth-child(2){animation-delay:1.3s}
.hit .brows li:nth-child(3){animation-delay:1.45s}
.hit .btot{animation:rowIn .35s ease-out 1.6s both}
@keyframes rowIn{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
.hit .close{animation-delay:1.8s}
'''

BIG_CSS = r'''
/* ---------- デカ的中：大きいPUSH・虹色に光る ---------- */
.ov.big .dim{background:radial-gradient(circle at 50% 46%,rgba(60,30,90,.55),rgba(6,4,18,.86) 70%)}
.push.big{width:210px;height:210px;animation:bobBig .8s ease-in-out infinite,popIn .4s cubic-bezier(.2,1.6,.4,1) both}
.push.big span{font-size:56px}
.push.big::before{content:"";position:absolute;inset:-26px;border-radius:50%;z-index:-1;
  background:conic-gradient(#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);
  -webkit-mask-image:radial-gradient(circle,transparent 0 62%,#000 63% 100%);mask-image:radial-gradient(circle,transparent 0 62%,#000 63% 100%);
  animation:spin 1.4s linear infinite;filter:drop-shadow(0 0 10px rgba(255,255,255,.8))}
.push.big::after{inset:-40px;border:4px solid transparent;background:conic-gradient(#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3B3B) border-box;
  -webkit-mask:linear-gradient(#000 0 0) padding-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:ring 1s ease-out infinite}
.pshadow.big{width:210px;margin-top:30px;animation:shadBig .8s ease-in-out infinite}
.tap.big{font-size:26px;background:linear-gradient(90deg,#FF5A5A,#FFD93B,#5BE38A,#4FD3FF,#B07CFF,#FF5A5A);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:rbowText 1.6s linear infinite}
@keyframes bobBig{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-26px) scale(1.04)}}
@keyframes shadBig{0%,100%{transform:scale(1);opacity:.6}50%{transform:scale(.68);opacity:.28}}
@keyframes rbowText{to{background-position:200% 0}}
.spk{position:absolute;inset:0;z-index:1;pointer-events:none}
.spk b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);background:var(--c);
  clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%);animation:twinkle 1.6s ease-in-out var(--d) infinite;opacity:0}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(.3) rotate(0)}50%{opacity:1;transform:scale(1) rotate(45deg)}}
.pressed.big{width:210px;height:210px;margin:-105px 0 0 -105px}
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
  opacity:0;animation:shock 1s ease-out both}
.ring.r1{animation-delay:.28s}.ring.r2{animation-delay:.55s}.ring.r3{animation-delay:.85s}
@keyframes shock{0%{opacity:1;scale:.2}100%{opacity:0;scale:3.2}}
.big .hb{animation:emerge 1s ease-out .85s both}
@keyframes emerge{0%{opacity:0;transform:scale(.6);filter:brightness(3.2) blur(3px)}60%{opacity:1;transform:scale(1.06);filter:brightness(1.6) blur(0)}100%{transform:scale(1);filter:none}}
.big .board{box-shadow:0 0 0 3px rgba(255,255,255,.9),0 0 26px 6px rgba(255,236,160,.85),0 10px 22px rgba(0,0,0,.3)}
.big .bh{font-size:31px;background:linear-gradient(90deg,#FF3B3B,#FF9F1A,#E8C200,#2DBB55,#1FA8E0,#4C6BFF,#B34CFF,#FF3B3B);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;filter:drop-shadow(0 2px 0 #FFFFFF) drop-shadow(0 3px 0 rgba(0,0,0,.18));
  animation:pop .55s cubic-bezier(.2,1.8,.4,1) 1.5s both,rbowText 2s linear 1.5s infinite}
.big .brows li{animation:rowIn .35s ease-out both}
.big .brows li:nth-child(1){animation-delay:1.75s}
.big .brows li:nth-child(2){animation-delay:1.9s}
.big .brows li:nth-child(3){animation-delay:2.05s}
.big .brows li.top{background:linear-gradient(#FFFDF5,#FFFDF5) padding-box,linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF) border-box;border:2px solid transparent}
.big .btot{animation:rowIn .35s ease-out 2.2s both}
.big .close{animation-delay:2.5s}
'''

HEADER = f'''  <header class="hd">
    <div class="hd-r1">
      <div class="logo">テンゲル<span class="sr">Ⅲ</span><span class="iii" aria-hidden="true"><i></i><i></i><i></i></span></div>
      <button class="mbtn" type="button"><svg {SVG_A}><path d="M3.5 5.5h6a2.5 2.5 0 0 1 2.5 2.5v11a2 2 0 0 0-2-2H3.5z"></path><path d="M20.5 5.5h-6A2.5 2.5 0 0 0 12 8v11a2 2 0 0 1 2-2h6.5z"></path></svg>説明書</button>
    </div>
  </header>
  <img class="bnr" src="{BANNER}" alt="青空と芝生、木の柵、草原に立つ栗毛の馬のイラスト">'''


def form(bets, pay_total, note):
    rows = ''.join(f'<li><span class="bt">{t}</span><span class="bc">{combo(c, s)}</span><span class="by">{y}</span></li>' for t, c, s, y, _, _ in bets)
    return f'''  <main class="ct">
    <section class="card">
      <h2 class="ch">レースの結果を記録</h2>
      <div class="rh"><span class="rk">9R</span><span class="rs">1400m ダ・良・12頭・予約したレース</span></div>
      <p class="lab">着順（馬番）</p>
      <div class="fin"><span class="k">1着</span>{num(6)}<span class="k">2着</span>{num(2)}<span class="k">3着</span>{num(10)}</div>
      <p class="lab">予約した買い目</p>
      <ul class="bets">{rows}</ul>
      <div class="pay"><span>払戻（回収額）</span><b>{pay_total}</b></div>
      <button class="rec" type="button" onClick="{{{{toPush}}}}"><svg {SVG_A}><path d="M5 4.5h11l3 3v12H5z"></path><path d="M8 4.5v5h7v-5M8 19.5v-5h8v5"></path></svg>記録する</button>
      <p class="note">{note}</p>
    </section>
  </main>'''


def board(title, bets, total, top_first=False):
    rows = ''
    for t, c, s, y, p, hit in bets:
        if not hit:
            continue
        cls = ' class="top"' if (top_first and t == '3連単') else ''
        rows += f'<li{cls}><span class="bt">{t}</span><span class="bc">{combo(c, s)}</span><span class="by">{y}</span><span class="bp">{p}</span></li>'
    return f'''<div class="board"><div class="bh">{title}</div><div class="bsub">9R の当たった買い目</div><ul class="brows">{rows}</ul><div class="btot">払戻 合計<b>{total}</b></div></div>'''


def page(kind):
    big = kind == 'big'
    if big:
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
      <button class="push{pb}" type="button" onClick="{{{{toReveal}}}}" aria-label="{'デカ的中ボタン' if big else '的中ボタン'}"><span>PUSH</span></button>
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
    reveal = f'''  <sc-if value="{{{{isReveal}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov{pb} {'big' if big else 'hit'}">
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
    css = (COMMON_CSS.replace('RANCH', RANCH_VARS) + (BIG_CSS if big else HIT_CSS))
    css = (css.replace('HBW2', f'{HB_W / 2:g}').replace('HBW', f'{HB_W:g}').replace('HBH', f'{HB_H:g}')
              .replace('BDX', f'{BD["x"]:g}').replace('BDY', f'{BD["y"]:g}').replace('BDW', f'{BD["w"]:g}').replace('BDH', f'{BD["h"]:g}'))
    name = 'デカ的中ボタン' if big else '的中ボタン'
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{name}（ベース）</title>
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
{form(bets, total, note)}
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


def memo_page():
    """メモのボード（静止画6枚＋Fableに渡す決まり）"""
    def still(key, cap):
        return f'<figure class="st"><img src="/_blob/{blobs[key]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'
    hit = still('s_hit_form', '① 記録する') + still('s_hit_push', '② PUSHが上下に動く') + still('s_hit_board', '③ タップ → 馬がボード')
    big = still('s_big_push', '① 大きいPUSH（虹の輪）') + still('s_big_light', '② 虹色の光に包まれる') + still('s_big_board', '③ 光の中から馬がボード')
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
.gd{{width:1320px;height:1060px;overflow:hidden;background:#F4F2EC;color:#22252E;font-family:"BIZ UDPGothic",sans-serif;padding:34px 40px 0}}
.t1{{margin:0;font-family:"Dela Gothic One",sans-serif;font-weight:400;font-size:32px;line-height:1.2;color:#161F3D}}
.t2{{margin:8px 0 0;font-size:14.5px;line-height:1.7;color:#4E5466}}
.rows{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}}
.grp{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:14px;padding:14px 16px}}
.grp h2{{margin:0 0 10px;font-size:17px;color:#161F3D}}
.grp h2 small{{font-size:12.5px;font-weight:700;color:#8A6A38;margin-left:8px}}
.sts{{display:flex;gap:10px}}
.st{{margin:0;flex:1}}
.st img{{display:block;width:100%;aspect-ratio:390/844;object-fit:cover;border-radius:10px;border:1px solid #DDD8CC}}
.st figcaption{{margin-top:6px;font-size:12.5px;font-weight:700;color:#3E4352;text-align:center}}
.boxes{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:18px}}
.box{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:12px;padding:12px 14px}}
.box h3{{margin:0 0 6px;font-size:14px;color:#161F3D}}
.box p,.box li{{margin:0;font-size:12.5px;line-height:1.65;color:#4E5466}}
.box ul{{margin:0;padding-left:1.1em}}
.box b{{color:#22252E}}
</style>
</helmet>
<div class="gd">
  <h1 class="t1">的中ボタン・デカ的中ボタン（ベース）</h1>
  <p class="t2">まさちゃんの指定：記録して <b>3連単以外が当たり → 的中ボタン</b>（PUSHが上下に動く）→ タップで、壁紙の馬がボードを持って出てきて、ボードに当たった買い目。<b>3連単が当たり → デカ的中ボタン</b>（大きいPUSH）→ タップで、虹色の派手な光に包まれて、馬がボードを持って出てくる。となりの2つの画面（的中・デカ的中）は、タップで動く見本。</p>
  <div class="rows">
    <section class="grp"><h2>的中ボタン<small>3連単以外が当たったとき</small></h2><div class="sts">{hit}</div></section>
    <section class="grp"><h2>デカ的中ボタン<small>3連単が当たったとき</small></h2><div class="sts">{big}</div></section>
  </div>
  <div class="boxes">
    <div class="box"><h3>出るとき</h3><ul><li>結果を<b>記録したとき</b>だけ（あとで直したとき・まとめて入れた記録・外れ・中止では出ない）</li><li>3連単が当たっていれば、ほかの券種もいっしょに当たっていても<b>デカ的中</b></li><li>お知らせ（発走15分後）から開いて記録したときも同じ</li></ul></div>
    <div class="box"><h3>流れと時間</h3><ul><li><b>的中</b>：押す → 0.3秒 馬が下から → 0.95秒「的中！」→ 1.15秒〜 買い目 → 1.8秒 とじる</li><li><b>デカ</b>：押す → 0.2秒 白く光る → 0.25秒 虹の光の筋と輪 → 0.85秒 光の中から馬 → 1.5秒「デカ的中!!」→ 1.75秒〜 買い目 → 2.5秒 とじる</li><li>PUSHは上下に0.9秒（デカは0.8秒・大きく）でくり返す</li></ul></div>
    <div class="box"><h3>重ねる順（下から）</h3><ul><li>暗い幕 → 光（的中＝光の筋／デカ＝虹の筋・光・輪）</li><li><b>馬（うしろの絵）→ ボード（文字はHTML）→ 前足の先（前の絵）</b>：ひづめがボードのふちにかかって見える</li><li>紙ふぶき → （デカ）白い光 → とじる</li></ul></div>
    <div class="box"><h3>ボードに書くもの</h3><ul><li>R・当たった買い目（券種・馬番・金額・払戻）・払戻の合計</li><li>3連単の行は虹色の枠</li><li>ユーザーが自分で入れた買い目だけ（判定の画面に点数・組番を出さない決まりはそのまま）</li></ul></div>
    <div class="box"><h3>テーマ（壁紙）ごとに変えるところ</h3><ul><li><b>馬の絵2枚</b>（うしろ・前足の先）と、ボードの四角の位置</li><li>PUSHの色（--pushA・--pushB・--pushC・--rim・--rimD）・ボードの枠と面（--bFrame・--bFace・--bInk）・光の色（--ray）</li><li>シルバー帯・ゴールド帯・マスター帯は指示書9.1の指定どおり（あとで作る）</li></ul></div>
    <div class="box"><h3>容量と見やすさ</h3><ul><li>馬の絵は1テーマ約27KB（WebP 2枚）。動きは全部CSS（動画なし）・新しいフォントなし（Dela Gothic One・BIZ UDPゴシック）</li><li>iPhoneの「視差効果を減らす」がオンなら、上下の動き・回転・紙ふぶきを止める</li><li>いまの馬は見本（牧場の栗毛）。壁紙を描き直したら、テーマごとに作る</li></ul></div>
  </div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1320,"height":1060}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


if __name__ == '__main__':
    for kind, fn in (('hit', 'Fx_Hit.dc.html'), ('big', 'Fx_Big.dc.html')):
        open(f'{P}/{fn}', 'w', encoding='utf-8').write(page(kind))
        print(fn)
    if 's_hit_form' in blobs:
        open(f'{P}/Fx_Memo.dc.html', 'w', encoding='utf-8').write(memo_page())
        print('Fx_Memo.dc.html')
