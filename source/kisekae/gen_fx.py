"""的中ボタン・デカ的中ボタン・フリーズ的中ボタン（デフォルト）の見本の画面：Fx_Hit.dc.html・Fx_Big.dc.html・Fx_Freeze.dc.html
   python3 gen_fx.py fx_blobs.json
   fx_blobs.json：{"back": "<id>", "front": "<id>"}（ボードを持つ馬の2枚）＋メモの静止画（s_…。そろっていればメモ Fx_Memo.dc.html も作る）
   流れ：記録する → PUSHボタン（上下に動く）→ タップ → 馬がボードを持って出てくる（ボードに当たった買い目）
   フリーズ（3連単の当たりに超大穴＝10〜12番人気の馬）：虹色にギラギラ光るめちゃくちゃデカいPUSH → タップで「プチュン」
   （テレビを消したように 横の線 → 点 → 真っ暗）→ 一瞬止まる → 雷と虹の大当たり →「超大穴!!」→ 雷の中から馬がボード"""
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


def bolt(seed, x0, y0, x1, y1, d, n=10, amp=24, branches=3):
    """雷（ジグザグの線＋枝）：390×844の画面の上の座標。d＝落ちる時刻（秒）"""
    rnd = random.Random(seed)
    pts = [(x0, y0)]
    for i in range(1, n):
        t = i / n
        pts.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp), y0 + (y1 - y0) * t + rnd.uniform(-amp * .3, amp * .3)))
    pts.append((x1, y1))
    path = lambda q: 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in q)
    out = [f'<path class="gl" pathLength="1" d="{path(pts)}"></path><path class="co" pathLength="1" d="{path(pts)}"></path>']
    for k in range(branches):
        i = rnd.randint(2, n - 3)
        bx, by = pts[i]
        side = rnd.choice([-1, 1])
        q = [(bx, by)]
        for j in range(1, 4):
            q.append((q[-1][0] + side * rnd.uniform(12, 24), q[-1][1] + rnd.uniform(16, 28)))
        out.append(f'<path class="gl s" pathLength="1" d="{path(q)}"></path><path class="co s" pathLength="1" d="{path(q)}"></path>')
    return f'<svg class="bolt" style="--d:{d}s" viewBox="0 0 390 844" aria-hidden="true">{"".join(out)}</svg>'


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
/* ---------- フリーズ的中：虹色にギラギラ光る めちゃくちゃデカいPUSH → プチュン（真っ暗）→ 雷と虹の大当たり ----------
   秒は押してから。<W>＝歪みが終わってプチュン・<B>＝真っ暗のあと「ドーン」（プチュン専用の2秒の演出）・<S>＝雷が落ちて馬が出る */
.w3{background:#E0322B;color:#FFFFFF}
.w8{background:#F27BB0;color:#1F1F1F}
.ov.fz{--rb:#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B;--ink2:#2A1259;--t0:<S+.85>;--tc:.35s}
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
/* ---------- 押したあと ---------- */
.ov.fz .blk{position:absolute;inset:0;background:#000000}
/* 歪み（0〜<W>）：押した瞬間の画面を細い帯に切って、波のように左右にずらす（だんだん強く）。ときどき帯がちぎれる・色がずれる・走査線・縦にガクッ。
   テレビの砂嵐（ザザーッ）が4回強く混ざって、最後は画面ぜんぶが砂嵐になる */
.wrp{position:absolute;inset:0;z-index:15;overflow:hidden;background:#000000;
  animation:wwob <W> linear both,wcol <W> steps(1) both,crtOff .08s cubic-bezier(.6,0,1,.6) <W> forwards}
.wrp i{position:absolute;left:-60px;width:510px;background:url(/_blob/WARPID) 60px 0/390px 844px repeat-x;animation:wk0 <W> linear both}
.wrp .scl,.wrp .nz,.wrp .gb,.wrp .snw,.wrp .snb{position:absolute;inset:0;pointer-events:none}
.wrp .scl{background:repeating-linear-gradient(180deg,rgba(0,0,0,.34) 0 1px,rgba(0,0,0,0) 1px 3px);opacity:0;animation:wramp <W> ease-in both}
.wrp .nz{background:NOISE 0 0/180px 180px;opacity:0;animation:wnz <W> ease-in both,nzj .3s steps(1) infinite}
.wrp .gb b{position:absolute;left:0;right:0;top:var(--y);height:var(--h);background:var(--c);opacity:0;animation:gbar var(--t) linear var(--d)}
/* 砂嵐：白黒の細かい粒（1粒 約1px）が1コマごとに入れかわる。強くなる所（ザザッ）が4回と、上から下へ流れる砂嵐の帯 */
.wrp .snw{background:SNOW 0 0/200px 200px;opacity:0;animation:snw <W> linear both,snj .05s steps(1) infinite}
.wrp .snb b{position:absolute;left:0;right:0;top:calc(var(--h) * -1);height:var(--h);background:SNOW 0 0/200px 200px;visibility:hidden;
  -webkit-mask-image:linear-gradient(180deg,transparent,#000 30%,#000 70%,transparent);mask-image:linear-gradient(180deg,transparent,#000 30%,#000 70%,transparent);
  animation:snb var(--t) linear var(--d),snj .05s steps(1) infinite}
.wrp::after{content:"";position:absolute;inset:0;background:#FFFFFF;opacity:0;animation:crtW .08s linear <W> forwards}
@keyframes wramp{0%{opacity:0}100%{opacity:1}}
@keyframes wnz{0%{opacity:0}55%{opacity:.12}100%{opacity:.42}}
@keyframes nzj{0%{background-position:0 0}20%{background-position:-61px 37px}40%{background-position:47px -83px}60%{background-position:-19px -29px}80%{background-position:88px 54px}}
@keyframes gbar{from,to{opacity:.9}}
@keyframes snw{0%,14%{opacity:0}16%{opacity:.62}21%{opacity:.08}36%{opacity:.06}39%{opacity:.76}45%{opacity:.12}58%{opacity:.18}61%{opacity:.86}67%{opacity:.26}77%{opacity:.42}80%{opacity:.92}86%{opacity:.55}92%{opacity:.85}100%{opacity:1}}
@keyframes snj{0%{background-position:0 0}25%{background-position:-73px 41px}50%{background-position:59px -97px}75%{background-position:-31px -53px}}
@keyframes snb{from{visibility:visible;translate:0 0}to{visibility:visible;translate:0 1000px}}
@keyframes wwob{0%{transform:none}25%{transform:scale(1.01,.99)}50%{transform:scale(.985,1.02) skewX(-.8deg)}61%{transform:scale(1.02,.985) skewX(.6deg)}62%{transform:translateY(-14px) scale(1.02,.985)}65%{transform:translateY(9px) scale(1.02,.985)}67%{transform:scale(1.02,.98) skewX(1deg)}80%{transform:scale(1.04,.96) skewX(1.6deg)}90%{transform:scale(.97,1.04) skewX(-2.2deg)}100%{transform:scale(1.05,.95) skewX(2.6deg)}}
@keyframes wcol{0%{filter:none}18%{filter:hue-rotate(25deg) saturate(1.3)}24%{filter:none}41%{filter:hue-rotate(-40deg) saturate(1.6)}46%{filter:none}63%{filter:hue-rotate(70deg) saturate(1.8) contrast(1.1)}68%{filter:saturate(1.4)}79%{filter:hue-rotate(-90deg) saturate(2)}86%{filter:hue-rotate(140deg) saturate(2.2) contrast(1.15)}93%{filter:hue-rotate(-160deg) saturate(2.4) contrast(1.2)}100%{filter:none}}
/* プチュン（<W>）：砂嵐の画面が縦につぶれて、いちばん細い白い線（1ピクセル＝画面の点1つぶん）に（〜<W+.08>）
   → ジリジリ静電気（<W+.06>〜<W+.5>：線がチラチラ・細かい火花がはじける・線のまわりに1ピクセルの細かい砂嵐）
   → 光が線の上を左から右へ走って、通ったところから線が消える（<W+.5>〜<W+.72>）→ 真っ暗 */
@keyframes crtOff{0%{transform:scale(1.05,.95) skewX(2.6deg);filter:brightness(1)}99%{transform:scale(1.05,.0004) skewX(0deg);filter:brightness(2.6);opacity:1}100%{transform:scale(1.05,.0004);opacity:0}}
@keyframes crtW{0%{opacity:0}60%{opacity:.4}100%{opacity:1}}
.tvw{position:absolute;inset:0;z-index:16;pointer-events:none}
.tvl{position:absolute;left:0;right:0;top:50%;height:1px;margin-top:-.5px;background:#FFFFFF;transform:scaleY(.34);
  box-shadow:0 0 1px #FFFFFF,0 0 3px rgba(190,225,255,.9),0 0 9px rgba(120,170,255,.55);opacity:0;
  animation:tvOn .01s linear <W+.06> forwards,tvFl .05s steps(1) <W+.06> 9,tvJit .04s steps(1) <W+.06> 11,tvErase .22s cubic-bezier(.5,0,.85,.5) <W+.5> forwards}
.tvs{position:absolute;left:0;right:0;top:50%;height:16px;margin-top:-8px;background:NOISEF 0 0/120px 120px;mix-blend-mode:screen;
  -webkit-mask-image:linear-gradient(180deg,transparent,#000 40%,#000 60%,transparent);mask-image:linear-gradient(180deg,transparent,#000 40%,#000 60%,transparent);
  opacity:0;animation:tvsOn .44s linear <W+.06> forwards,snj .05s steps(1) infinite,tvErase .22s cubic-bezier(.5,0,.85,.5) <W+.5> forwards}
@keyframes tvOn{from,to{opacity:1}}
@keyframes tvFl{0%{opacity:1}35%{opacity:.45}55%{opacity:1}80%{opacity:.7}}
@keyframes tvJit{0%{translate:0 0}50%{translate:0 .6px}}
@keyframes tvErase{from{clip-path:inset(0 0 0 0)}to{clip-path:inset(0 0 0 100%)}}
@keyframes tvsOn{0%{opacity:.95}100%{opacity:.55}}
/* ジリジリの火花：細い線（0.6px）のギザギザが一瞬（0.045秒）ずつ、あちこちで光る */
.tva{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible;filter:drop-shadow(0 0 1.5px #CFF0FF) drop-shadow(0 0 4px #6FA8FF)}
.tva path{fill:none;stroke:#FFFFFF;stroke-width:.6;stroke-linecap:round;stroke-linejoin:round;visibility:hidden;animation:arc .045s steps(1) var(--d)}
.tva circle{fill:#FFFFFF;visibility:hidden;animation:arc .045s steps(1) var(--d)}
@keyframes arc{from,to{visibility:visible}}
/* 消える：光（左から右へ走る）と、通ったあとに飛ぶ小さな火花 */
.tvh{position:absolute;left:-45px;top:50%;width:60px;height:10px;margin-top:-5px;
  background:radial-gradient(50% 50% at 75% 50%,#FFFFFF 0 16%,rgba(205,232,255,.95) 26%,rgba(120,175,255,.4) 52%,rgba(120,175,255,0) 74%);
  opacity:0;animation:tvh .22s cubic-bezier(.5,0,.85,.5) <W+.5> forwards}
@keyframes tvh{0%{opacity:1;translate:0 0}94%{opacity:1}100%{opacity:0;translate:390px 0}}
.tvp i{position:absolute;left:var(--x);top:50%;width:2px;height:2px;margin:-1px 0 0 -1px;border-radius:50%;background:#FFFFFF;box-shadow:0 0 3px #BFE6FF;
  opacity:0;animation:tvp .18s ease-out var(--d) forwards}
@keyframes tvp{0%{opacity:1;translate:0 0}100%{opacity:0;translate:var(--dx) var(--dy)}}
/* 真っ暗のあと、まん中に光の星（<B-.28>）→ <B> ドーン */
.ign,.igg{position:absolute;z-index:16;left:50%;top:44%;opacity:0;animation:ign .28s ease-in <B-.28> forwards}
.ign{width:44px;height:44px;margin:-22px 0 0 -22px;background:#FFFFFF;clip-path:polygon(50% 0,58% 42%,100% 50%,58% 58%,50% 100%,42% 58%,0 50%,42% 42%)}
.igg{width:60px;height:60px;margin:-30px 0 0 -30px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.95),rgba(200,170,255,.5) 40%,rgba(255,255,255,0) 70%)}
@keyframes ign{0%{opacity:1;transform:scale(.1) rotate(0)}92%{opacity:1;transform:scale(3.2) rotate(80deg)}100%{opacity:0;transform:scale(3.4) rotate(90deg)}}
.flash.fz{z-index:17;opacity:0;animation:fzFlash .4s ease-out <B> forwards}
@keyframes fzFlash{0%{opacity:1}100%{opacity:0}}
/* ゆれる層（<B>から見える）。<B>にドーン・アイコンが上と下に当たるたびに小さく・1文字ずつ小さく・<T+.6>の雷・<S>の雷でゆれる */
.shk{position:absolute;inset:0;z-index:1;opacity:0;
  animation:fzOn .01s linear <B> forwards,shake .5s linear <B>,
    shakeS .16s linear <B+.66>,shakeS .16s linear <B+1.08>,shakeS .16s linear <B+1.5>,shakeS .16s linear <B+1.92>,shakeS .16s linear <B+2.34>,shakeS .16s linear <B+2.73>,
    shakeS .2s linear <T+.08>,shakeS .2s linear <T+.22>,shakeS .2s linear <T+.36>,shakeS .22s linear <T+.5>,shake .35s linear <T+.6>,shake .45s linear <S>}
.rvw{position:absolute;inset:0;z-index:13;pointer-events:none;opacity:0;animation:fzOn .01s linear <B> forwards}
.rvw .frame b{animation:none}
@keyframes fzOn{from,to{opacity:1}}
@keyframes shake{0%,100%{translate:0 0}10%{translate:-10px 6px}20%{translate:9px -8px}30%{translate:-8px -5px}40%{translate:7px 7px}50%{translate:-6px 4px}60%{translate:5px -4px}70%{translate:-3px 3px}80%{translate:2px -2px}90%{translate:-1px 1px}}
@keyframes shakeS{0%,100%{translate:0 0}20%{translate:-5px 4px}40%{translate:5px -4px}60%{translate:-4px -3px}80%{translate:3px 3px}}
/* 背景：回らない（虹のぐるぐるはやめた）。夜空のような深い紫・白い光の筋（回らずに明るさだけゆっくり変わる）・サーチライト */
.fzbg{position:absolute;z-index:1;inset:-40px;background:radial-gradient(circle at 50% 44%,#6A33A6 0%,#341266 30%,#160838 60%,#05020D 100%)}
.vig{position:absolute;z-index:2;inset:-40px;background:radial-gradient(circle at 50% 44%,rgba(255,255,255,.3) 0,rgba(255,255,255,0) 22%,rgba(10,3,24,0) 55%,rgba(5,2,13,.55) 90%)}
.beams{position:absolute;z-index:3;inset:0;pointer-events:none}
.beams i{position:absolute;bottom:-30px;width:190px;height:980px;transform-origin:50% 100%;rotate:var(--a0);
  background:linear-gradient(0deg,rgba(255,255,255,.6),rgba(255,255,255,.16) 55%,rgba(255,255,255,0));
  clip-path:polygon(44% 100%,56% 100%,100% 0,0 0);mix-blend-mode:screen;animation:sweep 1.9s ease-in-out <B> infinite alternate}
.beams i:nth-child(1){left:-60px;--a0:-34deg;--a1:22deg}
.beams i:nth-child(2){right:-60px;--a0:34deg;--a1:-22deg;animation-direction:alternate-reverse}
@keyframes sweep{from{rotate:var(--a0)}to{rotate:var(--a1)}}
.ov.fz .rbow{z-index:4;background:repeating-conic-gradient(rgba(255,240,200,.5) 0 4deg,transparent 4deg 11deg);opacity:1;
  -webkit-mask-image:radial-gradient(circle,#000 0 8%,transparent 56%);mask-image:radial-gradient(circle,#000 0 8%,transparent 56%);
  animation:raysIn .5s ease-out <B> both,rayP 1.1s ease-in-out <B+.5> infinite alternate}
@keyframes rayP{from{opacity:1}to{opacity:.55}}
.ov.fz .glow{z-index:5;width:440px;height:440px;margin:-220px 0 0 -220px;animation:fzWrap 1s ease-out <B> both,breathe 1.8s ease-in-out <B+1> infinite}
@keyframes fzWrap{0%{scale:.1;opacity:0}40%{scale:1.6;opacity:.95}100%{scale:1.15;opacity:.85}}
.ov.fz .ring{z-index:6}
.ov.fz .ring.r1{animation-delay:<B>}.ov.fz .ring.r4{animation-delay:<S>}
/* 雷（強く光るのは<W>・<B>・<T+.6>・<S>：1秒に3回までにする） */
.bolt{position:absolute;z-index:7;left:0;top:0;width:390px;height:844px;pointer-events:none;overflow:visible;opacity:0;
  filter:drop-shadow(0 0 5px #A8ECFF) drop-shadow(0 0 14px #8A6BFF);animation:bolt .55s ease-out var(--d) forwards}
.bolt path{fill:none;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1 1;stroke-dashoffset:1;animation:boltDraw .08s linear var(--d) forwards}
.bolt .gl{stroke:rgba(180,235,255,.9);stroke-width:8}
.bolt .co{stroke:#FFFFFF;stroke-width:3}
.bolt .gl.s{stroke-width:5}
.bolt .co.s{stroke-width:1.8}
@keyframes bolt{0%{opacity:1}50%{opacity:.9}100%{opacity:0}}
@keyframes boltDraw{to{stroke-dashoffset:0}}
/* ---------- プチュン専用のド派手演出（<B>〜<S>） ----------
   <B>〜<T>（3秒）：テンゲルのアイコンが虹色に光りながら左右にブルブル振動して、画面いっぱいに上下にビュンビュン動く（虹色の残像3つ。
   上と下に当たるたびに白い輪と小さなゆれ）・集中線・金のコインがはじける・花火 → 上で止まる
   → <T+.08>〜「超」「大」「穴」「!!」が1文字ずつドン（文字ごとに色の輪）→ <T+.6> 雷が落ちる → アイコンと文字が手前へ飛んで消える → <S> 雷の中から馬 */
.sp{position:absolute;inset:0;z-index:8;pointer-events:none;animation:spOut .3s ease-in <S> forwards}
@keyframes spOut{to{opacity:0}}
.spl{position:absolute;inset:-80px;transform-origin:50% 44.5%;
  background:repeating-conic-gradient(from 0deg at 50% 44.5%,rgba(255,255,255,0) 0 2.3deg,rgba(255,255,255,.85) 2.3deg 2.7deg,rgba(255,255,255,0) 2.7deg 5.2deg),
    repeating-conic-gradient(from 1.9deg at 50% 44.5%,rgba(255,255,255,0) 0 3.2deg,rgba(255,255,255,.6) 3.2deg 3.45deg,rgba(255,255,255,0) 3.45deg 7.7deg);
  -webkit-mask-image:radial-gradient(circle at 50% 44.5%,transparent 0 26%,#000 46%);mask-image:radial-gradient(circle at 50% 44.5%,transparent 0 26%,#000 46%);
  animation:spl .3s steps(1) infinite}
@keyframes spl{0%{rotate:0deg}33%{rotate:1.6deg}66%{rotate:-1.1deg}}
.tic{position:absolute;left:50%;top:0;width:250px;height:250px;margin-left:-125px;opacity:0;
  animation:fzOn .01s linear <B> forwards,ticY 3s ease-in-out <B> forwards,ticOut .3s ease-in <T+.62> forwards}
.tic.g1{animation-delay:<B+.04>,<B+.04>,<T+.62>}
.tic.g2{animation-delay:<B+.08>,<B+.08>,<T+.62>}
.tic.g3{animation-delay:<B+.12>,<B+.12>,<T+.62>}
.tiv{position:absolute;inset:0;animation:vib .07s linear infinite}
.tis{position:absolute;inset:0;animation:ticPop .35s cubic-bezier(.2,1.6,.4,1) <B> both}
.tic.g1 .tis{animation-delay:<B+.04>}.tic.g2 .tis{animation-delay:<B+.08>}.tic.g3 .tis{animation-delay:<B+.12>}
.tib{position:absolute;inset:-9px;border-radius:27%;background:linear-gradient(135deg,#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8);animation:tglow .9s linear infinite}
.tii{position:absolute;inset:0;border-radius:22%;background:url(/_blob/ICONID) center/cover;box-shadow:0 0 0 3px #FFFFFF;overflow:hidden}
.tii::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,rgba(255,255,255,0) 35%,rgba(255,255,255,.75) 50%,rgba(255,255,255,0) 65%) -150% 0/60% 100% no-repeat;animation:glint .8s ease-in-out infinite}
.gh{position:absolute;inset:-6px;border-radius:26%;filter:blur(7px)}
.g1 .gh{background:#2FD6FF;opacity:.6}
.g2 .gh{background:#FF3BB8;opacity:.45}
.g3 .gh{background:#FFE53B;opacity:.32}
@keyframes ticY{0%,8%{translate:0 246px}22%{translate:0 34px}36%{translate:0 560px}50%{translate:0 34px}64%{translate:0 560px}78%{translate:0 34px}91%{translate:0 560px}100%{translate:0 64px}}
@keyframes ticPop{from{scale:.15}to{scale:1}}
@keyframes ticOut{to{opacity:0;scale:1.6;filter:brightness(2) blur(3px)}}
@keyframes vib{0%,100%{translate:-6px 0}50%{translate:6px 0}}
@keyframes tglow{0%,100%{box-shadow:0 0 22px 8px rgba(255,59,59,.85),0 0 60px 20px rgba(255,59,59,.45)}17%{box-shadow:0 0 22px 8px rgba(255,159,26,.85),0 0 60px 20px rgba(255,159,26,.45)}33%{box-shadow:0 0 22px 8px rgba(255,229,59,.85),0 0 60px 20px rgba(255,229,59,.45)}50%{box-shadow:0 0 22px 8px rgba(59,226,106,.85),0 0 60px 20px rgba(59,226,106,.45)}67%{box-shadow:0 0 22px 8px rgba(47,214,255,.85),0 0 60px 20px rgba(47,214,255,.45)}83%{box-shadow:0 0 22px 8px rgba(179,76,255,.85),0 0 60px 20px rgba(179,76,255,.45)}}
.tir{position:absolute;left:50%;top:var(--y);width:200px;height:200px;margin:-100px 0 0 -100px;border-radius:50%;border:4px solid #FFFFFF;
  box-shadow:0 0 16px #FFFFFF,inset 0 0 12px rgba(255,255,255,.8);opacity:0;animation:tir .4s ease-out var(--d) forwards}
@keyframes tir{0%{opacity:.95;scale:.4}100%{opacity:0;scale:1.9}}
.sl2{position:absolute;left:0;top:352px;width:390px;height:96px;animation:sl2p .4s ease-out <T+.6> both,sl2z .35s ease-in <T+.8> forwards}
.sl2 b{position:absolute;top:0;left:var(--x);width:var(--w);height:96px;opacity:0;animation:chr .42s cubic-bezier(.2,.9,.3,1.25) var(--d) forwards}
.sl2 span{position:absolute;left:-20px;right:-20px;top:0;text-align:center;white-space:nowrap;font:400 80px/1 "Dela Gothic One",sans-serif}
.sl2 .o{color:var(--ink2);-webkit-text-stroke:14px var(--ink2);filter:drop-shadow(0 0 12px rgba(255,255,255,.9)) drop-shadow(0 0 22px var(--g))}
.sl2 .f{background:linear-gradient(180deg,#FFFFFF 0%,#FFF6B0 38%,#FFC83A 58%,#FF8A1A 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-stroke:2px #FFFFFF}
.sl2 u{position:absolute;left:var(--x);top:48px;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;border:6px solid var(--g);box-shadow:0 0 14px var(--g),inset 0 0 10px var(--g);opacity:0;animation:cring .5s ease-out var(--d) forwards}
@keyframes chr{0%{opacity:0;scale:4;rotate:-14deg}50%{opacity:1;scale:.86;rotate:0deg}72%{scale:1.1}100%{opacity:1;scale:1}}
@keyframes cring{0%{opacity:1;scale:.3}100%{opacity:0;scale:2.3}}
@keyframes sl2p{0%{scale:1;filter:none}35%{scale:1.08;filter:brightness(1.7)}100%{scale:1;filter:none}}
@keyframes sl2z{to{scale:2.6;opacity:0;filter:blur(4px)}}
.bst{position:absolute;left:50%;top:44%;width:0;height:0}
.bst i{position:absolute;left:calc(var(--w) / -2);top:calc(var(--w) / -2);width:var(--w);height:var(--w);border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#FFFBE0 0 16%,#FFD54A 32%,#E0A100 70%,#9A6A00 100%);box-shadow:0 0 8px rgba(255,220,120,.95);
  opacity:0;animation:bst .9s cubic-bezier(.12,.75,.3,1) var(--d) forwards}
@keyframes bst{0%{opacity:1;transform:translate(0,0) scale(.3) rotateY(0deg)}75%{opacity:1}100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1.15) rotateY(900deg)}}
.fw{position:absolute;left:var(--x);top:var(--y);width:0;height:0}
.fw i{position:absolute;left:-3.5px;top:-3.5px;width:7px;height:7px;border-radius:50%;background:var(--c);box-shadow:0 0 7px 2px var(--c);
  opacity:0;animation:fw .7s cubic-bezier(.15,.8,.35,1) var(--d) forwards}
@keyframes fw{0%{opacity:1;transform:translate(0,0) scale(1.4)}70%{opacity:1}100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(.4)}}
.ov.fz .spk{z-index:9}
.ov.fz .spk.top{z-index:12}
/* 雷の光の中から馬がボードを持って出る（<S>）。コインは馬のうしろ・紙ふぶきは前 */
.ov.fz .conf.cb{z-index:9}
.ov.fz .hb{z-index:10;animation:strike .8s ease-out <S> both}
@keyframes strike{0%{opacity:0;transform:translateY(-36px) scale(.7);filter:brightness(4) blur(2px)}30%{opacity:1;transform:translateY(8px) scale(1.06);filter:brightness(2.2) blur(0)}55%{transform:translateY(-4px) scale(.99);filter:brightness(1.3)}100%{transform:none;filter:none}}
.ov.fz .conf{z-index:11}
.conf i.cn{height:var(--w);border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFFBE0 0 16%,#FFD54A 32%,#E0A100 70%,#9A6A00 100%);box-shadow:0 0 6px rgba(255,220,120,.9);animation:coin var(--t) linear var(--d) infinite}
@keyframes coin{0%{opacity:1;transform:translateY(0) rotateY(0)}85%{opacity:1}100%{opacity:0;transform:translateY(900px) rotateY(1080deg)}}
.ov.fz .close{z-index:18}
/* ボード：枠は虹色（回さない） */
.fz .board{border-color:transparent;background-clip:padding-box;box-shadow:0 0 0 3px #FFFFFF,0 0 28px 8px rgba(255,255,255,.9),0 0 64px 18px rgba(255,110,230,.55),0 12px 24px rgba(0,0,0,.35)}
.fz .board > .halo{inset:-8px;z-index:auto;border-radius:16px;filter:none}
.fz .board > .halo i{padding:8px}
.fz .board > .halo b{width:700px;height:700px;margin:-350px 0 0 -350px;animation:none}
.fz .bh{font-size:30px;background:linear-gradient(90deg,#FF3B3B,#FF9F1A,#E8C200,#2DBB55,#1FA8E0,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;filter:drop-shadow(0 2px 0 #FFFFFF) drop-shadow(0 3px 0 rgba(0,0,0,.2));
  animation:pop .55s cubic-bezier(.2,1.8,.4,1) <S+.6> both,rbowText 1.2s linear <S+.6> infinite}
.zrib{display:flex;align-items:center;justify-content:center;gap:6px;align-self:center;margin-top:1px;padding:3px 10px 3px 4px;border-radius:999px;background:var(--ink2);color:#FFFFFF;font-size:12px;font-weight:700;white-space:nowrap;
  box-shadow:0 0 0 2px #FFFFFF,0 0 12px rgba(179,76,255,.7);animation:rowIn .35s ease-out <S+.7> both}
.zrib .zt{padding:3px 8px;border-radius:999px;background:linear-gradient(180deg,#FFF3B0,#FFC21A);color:var(--ink2);font-weight:800;font-size:11.5px}
.zrib .n{min-width:22px;height:22px;font-size:12px}
.n.zx{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FF3BB8,0 0 10px 4px rgba(255,59,184,.6);animation:zx 1.2s linear infinite}
@keyframes zx{0%,100%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FF3B3B,0 0 10px 4px rgba(255,59,59,.65)}20%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FFC21A,0 0 10px 4px rgba(255,194,26,.65)}40%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #2DBB55,0 0 10px 4px rgba(45,187,85,.65)}60%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #1FA8E0,0 0 10px 4px rgba(31,168,224,.65)}80%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #B34CFF,0 0 10px 4px rgba(179,76,255,.65)}}
.fz .brows li.top{position:relative;background:linear-gradient(#FFFDF5,#FFFDF5) padding-box,linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3BB8) border-box;border:2px solid transparent;padding:4px 6px}
.fz .brows li{flex-wrap:wrap}
.fz .brows li.top{gap:3px;padding:4px 5px}
.fz .brows li.top::after{content:"";position:absolute;inset:0;border-radius:8px;pointer-events:none;background:linear-gradient(105deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.75) 50%,rgba(255,255,255,0) 70%) -130% 0/50% 100% no-repeat;animation:glint 1.8s ease-in-out <S+1.05> infinite}
.fz .btot b{background:linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3BB8) 0 100%/100% 3px no-repeat;padding-bottom:4px}
/* 視差効果を減らす：ふるえ・回転・広がる光・歪み・砂嵐・プチュン・ゆれ・雷・白い光・アイコンの演出を止める。1秒真っ暗 → 夜空の画面と馬・ボードをふわっと出す */
@media (prefers-reduced-motion:reduce){
  .push.fz,.push.fz::before,.push.fz .face,.push.fz .glit b,.pshadow.fz,.tap.fz,.aura,.prays,.edge,.frame b,.beams i,.n.zx,.fz .brows li.top::after,.fz .board > .halo b{animation:none!important}
  .push.fz::after,.ov.fz .wrp,.ov.fz .tvw,.ov.fz .ign,.ov.fz .igg,.ov.fz .flash,.ov.fz .bolt,.ov.fz .sp,.ov.fz .ring,.ov.fz .beams,.ov.fz .conf{display:none}
  .push.fz .glit b{opacity:.6}
  .ov.fz{--t0:1.9s}
  .ov.fz .shk,.ov.fz .rvw{animation:fadeIn .6s ease-out 1s both!important}
  .ov.fz .rbow{animation:none!important}
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
# フリーズの時刻（押してから）：W＝歪みが終わってプチュン・B＝真っ暗のあと「ドーン」（テンゲルのアイコンが3秒）・T＝アイコンが止まって「超大穴!!」・S＝雷が落ちて馬が出る
FZ_T = dict(W=1.0, B=2.4, T=5.4, S=6.6)
WARP_N = 44        # 歪みの帯の数（1本 約19px）
NOISE = 'url("data:image/svg+xml,' + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'>"
    "<feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' seed='7' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 1.5 0 0 0 -.45'/></filter>"
    "<rect width='180' height='180' filter='url(#n)'/></svg>", safe="/:=' .,-") + '")'
# 砂嵐：白黒の粒（1粒 約1px・不透明）。プチュンの線のまわり：もっと細かい白い粒（1粒 約1/3px＝画面の点1つぶん）
SNOW = 'url("data:image/svg+xml,' + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='s'>"
    "<feTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='1' seed='3' stitchTiles='stitch'/>"
    "<feColorMatrix values='2.2 0 0 0 -.6 2.2 0 0 0 -.6 2.2 0 0 0 -.6 0 0 0 0 1'/></filter>"
    "<rect width='200' height='200' filter='url(#s)'/></svg>", safe="/:=' .,-") + '")'
NOISEF = 'url("data:image/svg+xml,' + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' width='360' height='360'><filter id='f'>"
    "<feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='1' seed='9' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 2.4 0 0 0 -.9'/></filter>"
    "<rect width='360' height='360' filter='url(#f)'/></svg>", safe="/:=' .,-") + '")'



def warp_keyframes(n=WARP_N, seed=51):
    """歪みの帯ごとの動き：だんだん強くなる波（ゆっくりの大きい波＋速い小さい波）＋ときどき帯がちぎれる"""
    rnd = random.Random(seed)
    W = FZ_T['W']
    tears = []
    for _ in range(14):
        t = rnd.uniform(.12, .97)
        k0 = rnd.randrange(n)
        tears.append((t, k0, min(n, k0 + rnd.randint(1, 4)), rnd.choice([-1, 1]) * rnd.uniform(14, 46) * (.4 + t)))
    m = 32
    out = []
    for k in range(n):
        y = (k + .5) / n
        parts = []
        for i in range(m + 1):
            u = i / m
            t = u * W
            x = (3 + 40 * u ** 1.5) * math.sin(2 * math.pi * (2.2 * t + 2.6 * y)) + 10 * u ** 2 * math.sin(2 * math.pi * (5.0 * t + 7.0 * y + .3))
            for te, k0, k1, dx in tears:
                if k0 <= k < k1 and abs(t - te) < .5 * W / m:
                    x += dx
            parts.append(f'{u * 100:g}%{{translate:{x:.1f}px 0}}')
        out.append(f'@keyframes wk{k}{{{"".join(parts)}}}')
    return '\n'.join(out)


def fz_css():
    """FREEZE_CSS の <B+.02> などを秒に直す・歪みの絵とノイズを入れる・帯ごとの動きを足す"""
    def rep(m):
        v = FZ_T[m.group(1)] + float(m.group(2) or 0)
        return f'{v:.2f}'.rstrip('0').rstrip('.') + 's'
    css = re.sub(r'<([WBTS])([+-][0-9.]+)?>', rep, FREEZE_CSS)
    css = css.replace('NOISEF', NOISEF).replace('SNOW', SNOW).replace('ICONID', blobs['fz_icon'])
    return css.replace('WARPID', blobs['fz_warp']).replace('NOISE', NOISE) + '/* 歪みの帯ごとの動き（gen_fx.py の warp_keyframes で作る） */\n' + warp_keyframes() + '\n'


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


def warp_layers(seed=53):
    """歪み：押した瞬間の画面（fz_warp の絵）を WARP_N 本の帯に切る＋走査線・ノイズ・ちぎれる光の線"""
    h = 844 / WARP_N
    strips = ''.join(f'<i style="top:{k * h:.2f}px;height:{h + 1.5:.2f}px;background-position:60px {-k * h:.2f}px;animation-name:wk{k}"></i>' for k in range(WARP_N))
    rnd = random.Random(seed)
    W = FZ_T['W']
    bars = ''.join(f'<b style="--y:{rnd.uniform(40, 800):.0f}px;--h:{rnd.choice([1, 2, 2, 3, 5])}px;--d:{rnd.uniform(.25, .97) * W:.2f}s;--t:{rnd.uniform(.04, .09):.2f}s;--c:{rnd.choice(["#FFFFFF", "#FF3BB8", "#2FD6FF", "#FFE53B"])}"></b>' for _ in range(12))
    snow = ''.join(f'<b style="--h:{h}px;--t:{t:.2f}s;--d:{d * W:.2f}s"></b>' for h, t, d in ((90, .24, .17), (130, .28, .4), (70, .2, .62), (150, .3, .78)))
    return (f'<div class="wrp" aria-hidden="true">{strips}<div class="scl"></div><div class="nz"></div>'
            f'<div class="snw"></div><div class="snb">{snow}</div><div class="gb">{bars}</div></div>')


def burst(n, seed, d, dist=(230, 420), size=(12, 20), fall=90):
    """金のコインがまん中からはじける"""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-.3, .3)) / n
        r = rnd.uniform(*dist)
        out.append(f'<i style="--dx:{math.cos(a) * r:.0f}px;--dy:{math.sin(a) * r + fall:.0f}px;--w:{rnd.uniform(*size):.0f}px;--d:{d + rnd.uniform(0, .08):.2f}s"></i>')
    return f'<div class="bst">{"".join(out)}</div>'


def firework(x, y, d, seed, n=18):
    """花火（虹色の光の粒が丸く広がる）"""
    rnd = random.Random(seed)
    dots = ''.join(f'<i style="--dx:{math.cos(2 * math.pi * i / n) * r:.0f}px;--dy:{math.sin(2 * math.pi * i / n) * r + 14:.0f}px;--c:hsl({int(i * 360 / n)},100%,68%)"></i>'
                   for i, r in ((i, rnd.uniform(80, 136)) for i in range(n)))
    return f'<div class="fw" style="--x:{x}px;--y:{y}px;--d:{d:.2f}s">{dots}</div>'


def slam_chars(T):
    """「超」「大」「穴」「!!」が1文字ずつドン（文字ごとに色の輪）"""
    chars = [('超', 43, 80, T + .08, '#FF3BB8'), ('大', 123, 80, T + .22, '#2FD6FF'), ('穴', 203, 80, T + .36, '#FFE53B'), ('!!', 283, 64, T + .5, '#3BE26A')]
    out = ''
    for c, x, w, d, g in chars:
        out += f'<b style="--x:{x}px;--w:{w}px;--d:{d:.2f}s;--g:{g}"><span class="o">{c}</span><span class="f">{c}</span></b>'
        out += f'<u style="--x:{x + w / 2:g}px;--d:{d:.2f}s;--g:{g}"></u>'
    return f'<div class="sl2" aria-hidden="true">{out}</div>'



def bez_time(u, x1=.5, y1=0, x2=.85, y2=.5):
    """cubic-bezier の進み u（0〜1）になる時刻（0〜1）"""
    bx = lambda t: 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3
    by = lambda t: 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if by(m) < u else (lo, m)
    return bx((lo + hi) / 2)


def jag(rnd, x0, y0, x1, y1, n, amp):
    """ギザギザの線（火花）"""
    pts = []
    for j in range(n + 1):
        u = j / n
        k = math.sin(math.pi * u) * amp * rnd.uniform(-1, 1)
        nx, ny = -(y1 - y0), (x1 - x0)
        L = math.hypot(nx, ny) or 1
        pts.append((x0 + (x1 - x0) * u + nx / L * k, y0 + (y1 - y0) * u + ny / L * k))
    return 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts), pts[-1]


def tv_layers(seed=91):
    """プチュン：1ピクセルの線・線のまわりの細かい砂嵐・ジリジリの火花・左から右へ走る光と、通ったあとの火花"""
    rnd = random.Random(seed)
    W = FZ_T['W']
    y0 = 422
    arcs = []
    for _ in range(36):            # 線の上のジリジリ（W+.06〜W+.5）
        d = W + rnd.uniform(.06, .47)
        x = rnd.uniform(4, 386)
        L = rnd.uniform(10, 46)
        side = rnd.choice([-1, 1])
        path, end = jag(rnd, x - L / 2, y0 + rnd.uniform(-1, 1), x + L / 2, y0 + side * rnd.uniform(1, 8), rnd.randint(3, 6), rnd.uniform(2, 6))
        arcs.append(f'<path style="--d:{d:.3f}s" d="{path}"></path>')
        if rnd.random() < .5:
            arcs.append(f'<circle style="--d:{d:.3f}s" cx="{end[0]:.1f}" cy="{end[1]:.1f}" r=".9"></circle>')
    for _ in range(14):            # プチュンの直前（W-.18〜W）：画面のあちこちでジリッ
        d = W - rnd.uniform(.02, .18)
        x, y = rnd.uniform(20, 370), rnd.uniform(60, 790)
        a = rnd.uniform(0, 2 * math.pi)
        L = rnd.uniform(18, 60)
        path, _ = jag(rnd, x, y, x + math.cos(a) * L, y + math.sin(a) * L, rnd.randint(4, 7), rnd.uniform(3, 8))
        arcs.append(f'<path style="--d:{d:.3f}s" d="{path}"></path>')
    sparks = ''
    for i in range(16):            # 走る光が通ったところから飛ぶ火花
        u = (i + .5) / 16
        d = W + .5 + .22 * bez_time(u)
        sparks += f'<i style="--x:{390 * u:.1f}px;--d:{d:.3f}s;--dx:{rnd.uniform(-3, 10):.0f}px;--dy:{rnd.choice([-1, 1]) * rnd.uniform(5, 16):.0f}px"></i>'
    return (f'<div class="tvw" aria-hidden="true"><div class="tvs"></div><div class="tvl"></div>'
            f'<svg class="tva" viewBox="0 0 390 844">{"".join(arcs)}</svg><div class="tvh"></div><div class="tvp">{sparks}</div></div>')


def icon_show():
    """テンゲルのアイコン（3秒）：虹色の残像3つ（うしろ）＋アイコン＋上と下に当たったときの白い輪"""
    B = FZ_T['B']
    ghosts = ''.join(f'<div class="tic {g}"><div class="tiv"><div class="tis"><i class="gh"></i></div></div></div>' for g in ('g3', 'g2', 'g1'))
    main = '<div class="tic"><div class="tiv"><div class="tis"><i class="tib"></i><i class="tii"></i></div></div></div>'
    hits = ((.22, 159), (.36, 685), (.50, 159), (.64, 685), (.78, 159), (.91, 685))      # ticY の 上（34px）・下（560px）
    rings = ''.join(f'<i class="tir" style="--y:{y}px;--d:{B + 3 * p:.2f}s"></i>' for p, y in hits)
    return rings + ghosts + main

def fz_layers(bets, total):
    """フリーズの押したあと（下から）：黒 → ゆれる層（虹の画面・2秒の演出・馬とボード）→ 画面のふちの虹 → 歪み（→ プチュン）→ 線・点・星 → 白い光"""
    rib = f'<div class="zrib"><b class="zt">超大穴</b>{num(FZ_X, " zx")}<span>{FZ_X}番人気が3連単に！</span></div>'
    ring = '<i class="halo" aria-hidden="true"><i><b></b></i></i>'
    B, T, S = FZ_T['B'], FZ_T['T'], FZ_T['S']
    bolts = bolt(41, 34, -12, 150, 430, B) + bolt(43, 362, -12, 248, 470, B) + bolt(47, 210, -12, 196, 300, S, n=9, amp=20)
    show = ('<div class="sp" aria-hidden="true"><div class="spl"></div>'
            + burst(36, 71, B + 1.1) + burst(28, 73, B + 2.0, dist=(160, 330), size=(10, 16))
            + firework(84, 196, B + 1.3, 81) + firework(304, 236, B + 1.75, 83) + firework(196, 640, B + 2.2, 85) + firework(96, 560, B + 2.6, 87)
            + icon_show() + bolt(61, 120, -12, 170, 362, T + .6, n=9, amp=18) + slam_chars(T) + '</div>')
    return f'''<div class="blk"></div>
    <div class="shk">
      <div class="fzbg"></div><div class="vig"></div>
      <div class="beams"><i></i><i></i></div>
      <div class="rbow"></div><div class="glow"></div>
      <div class="ring r1"></div><div class="ring r4"></div>
      {bolts}
      {show}
      <div class="spk">{sparkles(34, 13)}</div>
      <div class="conf cb">{coins(22, 8, B + .1)}</div>
      <div class="hb">
        <img src="/_blob/{blobs['back']}" alt="ボードを持つ馬">
        {board('フリーズ的中!!!', bets, total, top_first=True, rib=rib, mark=(FZ_X,), ring=ring)}
        <img src="/_blob/{blobs['front']}" alt="">
      </div>
      <div class="conf">{confetti(40, 7, rainbow=True, d0=B + .05)}</div>
      <div class="spk top">{sparkles(12, 17)}</div>
    </div>
    <div class="rvw"><div class="edge"></div><div class="frame"><b></b></div></div>
    {warp_layers()}
    {tv_layers()}
    <div class="igg"></div><div class="ign"></div>
    <div class="flash fz"></div>'''


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


MEMO_W, MEMO_H = 2200, 1300


def memo_page():
    """メモのボード（静止画11枚＋Fableに渡す決まり）"""
    def still(key, cap):
        return f'<figure class="st"><img src="/_blob/{blobs[key]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'
    hit = still('s_hit_form', '① 記録する') + still('s_hit_push', '② PUSHが上下に動く') + still('s_hit_board', '③ タップ → 馬がボード')
    big = still('s_big_push', '① 大きいPUSH（虹の輪）') + still('s_big_light', '② 虹色の光に包まれる') + still('s_big_board', '③ 光の中から馬がボード')
    fz = (still('s_fz_push', '① 虹色の超デカPUSH') + still('s_fz_warp', '② 歪み＋砂嵐（1秒）') + still('s_fz_off', '③ プチュン（ジリジリ）')
          + still('s_fz_show', '④ テンゲルのアイコン（3秒）') + still('s_fz_board', '⑤ 雷の中から馬がボード'))
    Wt, B, T, S = FZ_T['W'], FZ_T['B'], FZ_T['T'], FZ_T['S']
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
.rows{{display:grid;grid-template-columns:3fr 3fr 5fr;gap:20px;margin-top:20px}}
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
  <p class="t2">まさちゃんの指定：記録して <b>当たり → 的中ボタン</b>、<b>3連単が当たり → デカ的中ボタン</b>、<b>3連単の当たりに超大穴（10〜12番人気）の馬 → フリーズ的中ボタン</b>。タップすると、壁紙の馬がボードを持って出てきて、当たった買い目を報告する。フリーズは、虹色にギラギラ光るめちゃくちゃデカいPUSH → タップで画面が止まって1秒グニャッと歪む（テレビの砂嵐が混ざる）→「プチュン」（1ピクセルの線がジリジリ → 光が横に走って消える）→ テンゲルのアイコンが虹色に光りながら画面いっぱいに上下に3秒 →「超大穴!!」→ 雷の中から馬がボード。となりの3つの画面は、タップで動く見本（どれもデフォルト＝全テーマ共通の動き）。</p>
  <div class="rows">
    <section class="grp"><h2>的中ボタン<small>当たったとき</small></h2><div class="sts">{hit}</div></section>
    <section class="grp"><h2>デカ的中ボタン<small>3連単が当たったとき</small></h2><div class="sts">{big}</div></section>
    <section class="grp fzg"><h2>フリーズ的中ボタン<small>3連単の当たりに超大穴（10〜12番人気）</small></h2><div class="sts">{fz}</div></section>
  </div>
  <div class="boxes">
    <div class="box"><h3>出るとき</h3><ul><li>結果を<b>記録したとき</b>だけ（あとで直したとき・まとめて入れた記録・外れ・中止では出ない）</li><li>出るのは1つだけ。強い順に <b>フリーズ</b>（3連単が当たって、その3頭に超大穴＝10〜12番人気がいる。13番人気より下は入れない）＞ <b>デカ</b>（3連単が当たり）＞ <b>的中</b>（それ以外の当たり）</li><li>人気は、そのレースを判定したときの単勝オッズの順（判定の超大穴 J・K・L と同じ）。人気がわからないレースはフリーズにしない（デカ）<b>※仮</b></li><li>お知らせ（発走15分後）から開いて記録したときも同じ</li></ul></div>
    <div class="box"><h3>流れと時間（的中・デカ）</h3><ul><li><b>的中</b>：押す → 0.3秒 馬が下から → 0.95秒「的中！」→ 1.15秒〜 買い目 → 1.8秒 とじる</li><li><b>デカ</b>：押す → 0.2秒 白く光る → 0.25秒 虹の光の筋と輪 → 0.85秒 光の中から馬 → 1.5秒「デカ的中!!」→ 1.75秒〜 買い目 → 2.5秒 とじる</li><li><b>PUSHは横長の長方形（角は丸い）</b>。上下に0.9秒（デカは0.8秒・大きく・まわりに虹の輪）でくり返す</li></ul></div>
    <div class="box"><h3>フリーズの流れと時間</h3><ul><li><b>PUSH</b>：横340×縦170・角46px（デカの1.2倍）。虹色が流れる面・ラメ・白い光がサッと走る・白と紫のふち・まわりに虹の輪。上下に22px・0.85秒／1.3秒ごとにブルブルッ／画面のふちが虹色に光る</li><li><b>歪み（0〜{sec(Wt)}秒）</b>：押した瞬間の画面が止まって、細い帯（44本）に切れて波のように左右にずれる（だんだん強く・ちぎれる・色ずれ・走査線・縦にガクッ）。テレビの砂嵐が4回ザザッと強くなり、帯になって上から下へ流れ、最後は画面ぜんぶ砂嵐</li><li><b>プチュン（{sec(Wt)}秒）</b>：砂嵐の画面が縦につぶれて、いちばん細い白い線（画面の点1つぶん）→ ジリジリ静電気（{sec(Wt + .06)}〜{sec(Wt + .5)}秒：線がチラチラ・細い火花・線のまわりに細かい砂嵐）→ 光が線の上を左から右へ走って、通ったところから消える（〜{sec(Wt + .72)}秒）→ 真っ暗 → {sec(B - .28)}秒 まん中に光の星</li><li><b>{sec(B)}〜{sec(T)}秒 テンゲルのアイコン（3秒）</b>：ドーン（白い光・雷2本・ゆれ）→ アイコン（250px・角の丸い四角）が虹色に光りながら左右にブルブル、画面いっぱいに上下に3往復（虹色の残像3つ・上と下に当たるたびに白い輪とゆれ）・集中線・金のコイン・花火 → 上で止まる</li><li><b>{sec(T)}秒</b>〜「超」「大」「穴」「!!」が1文字ずつドン → {sec(T + .6)}秒 雷 → アイコンと文字が手前へ飛んで消える → <b>{sec(S)}秒</b> 雷の中から馬がボード → {sec(S + .6)}秒「フリーズ的中!!!」→ {sec(S + .85)}秒〜 買い目 → {sec(S + .85 + .45 + .35)}秒 とじる</li></ul></div>
    <div class="box"><h3>重ねる順（下から）</h3><ul><li><b>的中・デカ</b>：暗い幕 → 光 → <b>馬（うしろの絵）→ ボード（文字はHTML）→ 前足の先（前の絵）</b>（ひづめがボードのふちにかかる）→ 紙ふぶき → とじる → （デカ）白い光</li><li><b>フリーズ</b>：黒 → ゆれる層（夜空・光の筋・サーチライト・光・輪・雷・演出（集中線・コイン・花火・白い輪・アイコンの残像・アイコン・「超大穴!!」）・きらめき・コイン・馬とボード・紙ふぶき）→ 画面のふちの虹 → 歪み（押した瞬間の画面の絵を帯に切ったもの・走査線・ノイズ・砂嵐）→ プチュン（細かい砂嵐・線・火花・走る光）→ 星 → 白い光 → とじる</li></ul></div>
    <div class="box"><h3>ボードに書くもの</h3><ul><li>R・当たった買い目（券種・馬番・金額・払戻）・払戻の合計。ユーザーが自分で入れた買い目だけ（判定の画面に点数・組番を出さない決まりはそのまま）</li><li>デカ・フリーズは3連単の行がいちばん上で虹色の枠（フリーズは光が走る）</li><li><b>フリーズ</b>：見出し「フリーズ的中!!!」・その下に「超大穴 ⑪ 11番人気が3連単に！」の帯・3連単の行の超大穴の馬番に虹色の輪・ボードの枠は虹色（回さない）</li><li>払戻が長いと次の行へ。帯のぶんボードが長いので、フリーズは6行まで（7つ以上は上から5行＋「ほか○点」<b>※仮</b>）</li></ul></div>
    <div class="box"><h3>テーマ（壁紙）ごとに変えるところ</h3><ul><li><b>馬の絵2枚</b>（うしろ・前足の先）と、ボードの四角の位置</li><li>PUSHの色（--pushA・--pushB・--pushC・--rim・--rimD）・ボードの枠・面・文字（--bFrame・--bFace・--bInk・--hitRed）・光の色（--ray）</li><li><b>フリーズは全テーマ共通</b>（変わるのは馬の絵とボードの面・文字だけ）。押したあとに回る虹（虹のぐるぐる）は使わない</li><li>シルバー帯・ゴールド帯・マスター帯は指示書9.1の指定どおり（あとで作る）</li></ul></div>
    <div class="box"><h3>光と見やすさ</h3><ul><li>強く光るのは<b>1秒に3回まで</b>（光の点めつで気分が悪くなる人がいるため）：{sec(Wt)}秒（プチュン）・{sec(B)}秒（ドーン）・{sec(T + .6)}秒（雷）・{sec(S)}秒（雷と馬）。いちばん近いところでも1秒に2回。砂嵐は明るさがほぼ一定（灰色）</li><li>iPhoneの「視差効果を減らす」がオンなら：上下・ふるえ・回転・広がる光・紙ふぶき・きらめき・歪み・砂嵐・プチュン・アイコンの演出・ゆれ・雷・白い光を止める。フリーズは押すと1秒真っ暗 → 夜空の画面と馬・ボードをふわっと出す</li><li>音は見本に入れていない</li></ul></div>
    <div class="box"><h3>容量</h3><ul><li>馬の絵は1テーマ約27KB（WebP 2枚）。フリーズで足す絵は<b>テンゲルのアイコン</b>だけ（App Storeのアイコンと同じ絵・WebP 750×750 約52KB）。虹・雷・コイン・星・花火・文字・砂嵐はCSSとSVG</li><li>歪みに使う「押した瞬間の画面の絵」は、アプリでは押した瞬間に撮る（WKWebView の takeSnapshot）。見本では見本の画面の絵（WebP 約60KB）</li><li>動きは全部CSS（動画なし）・新しいフォントなし（Dela Gothic One・BIZ UDPゴシック）。いまの馬は見本（牧場の栗毛）</li></ul></div>
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


STILLS = ('s_hit_form', 's_hit_push', 's_hit_board', 's_big_push', 's_big_light', 's_big_board', 's_fz_push', 's_fz_warp', 's_fz_off', 's_fz_show', 's_fz_board')

if __name__ == '__main__':
    out = os.environ.get('FX_OUT', P)
    for kind, fn in (('hit', 'Fx_Hit.dc.html'), ('big', 'Fx_Big.dc.html'), ('fz', 'Fx_Freeze.dc.html')):
        open(f'{out}/{fn}', 'w', encoding='utf-8').write(page(kind))
        print(fn)
    if all(k in blobs for k in STILLS):
        open(f'{out}/Fx_Memo.dc.html', 'w', encoding='utf-8').write(memo_page())
        print('Fx_Memo.dc.html')
