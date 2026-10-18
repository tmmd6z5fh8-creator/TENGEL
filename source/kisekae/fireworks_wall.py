"""花火の壁紙の動き（まさちゃんの指定）：ページに入れる HTML と CSS
   「花火が画面上にある間は、常にキラキラの花火は動いている、1秒〜2秒で画面の花火が徐々に花火が消えて、4秒〜5秒で周りの花火を打ち上げで、
    6秒から7秒で馬の花火を打ち上げる 12秒に一回リピートする」
   - いちばん下は 夜空・星・ちょうちんの絵（花火なし・<img class="bnr">）。その上に、花火4つと馬の光を それぞれ「足す光」の絵として重ねて、
     mix-blend-mode:plus-lighter で足す（flat/fireworks_banner.py --layers。ぜんぶ足すと いつもの絵と同じ）
   - 12秒で1回り（CYCLE）：
     0〜1秒 花火と馬が出ている（光の点が きらっ きらっ と光り、花火は ゆっくり広がる）→
     1〜2秒 だんだん消える（少し広がって、火の粉が下へ落ちるように少し下がる）→ 2〜4秒 夜空とちょうちんだけ →
     4〜5秒 まわりの花火を打ち上げる（ちょうちんの上から 光の玉が上がって、上で ぱっと開く。4つを少しずつずらして）→
     6〜7秒 馬の花火を打ち上げる（光の玉が上がって、まん中から まるく広がるように 馬があらわれる）→ 12秒まで 出ている → くり返す
   - 「キラキラ」は、花火の光の点と 馬の線の上の点に、4つの角の きらっ（白いしん・花火の色の光）を いくつも重ねて、ばらばらに光らせる
   - 視差効果を減らす（prefers-reduced-motion）なら 動かさない（花火と馬が ぜんぶ出た いつもの絵）
   - キャンバスでは /_blob/<id>（fireworks_blobs.json の base＝下の絵・layers＝足す光）・置く場所は fireworks_layers.json
   クラスの名前は hq…
   python3 fireworks_wall.py --judge <Judge_Fireworks.dc.html> <fireworks_blobs.json> <fireworks_layers.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）"""
import sys, re, json, math

ALT = '夜空に上がる花火と、金とピンクの光の線でえがいた、かける馬（しっぽはしだれ柳の花火）、ちょうちんのイラスト（花火がきらきら光って、消えて、また打ち上がる）'
CYCLE = 12.0
FADE = (1.0, 2.0)                  # だんだん消える
LAUNCH = [4.0, 4.3, 4.15, 4.45]    # まわりの花火4つの 打ち上げ（光の玉が上がりはじめる秒）。ピンク → 水色 → 黄 → オレンジ
RISE = 0.45                        # 光の玉が上がる秒（上がりきったら ぱっと開く）
OPEN = 0.45                        # 開く秒
HORSE = 6.0                        # 馬の花火の 打ち上げ
HRISE, HOPEN = 0.5, 0.5
GROUND = 236                       # 光の玉が出てくる高さ（ちょうちんの上・絵の画素）


def pct(t):
    return f'{round(t / CYCLE * 100, 3):g}%'


def star(L, col, gid):
    """きらっ（4つの角の星・白いしん・まわりに花火の色の光）"""
    w = L * .16
    d = f'M0 {-L}Q{w:.1f} {-w:.1f} {L} 0Q{w:.1f} {w:.1f} 0 {L}Q{-w:.1f} {w:.1f} {-L} 0Q{-w:.1f} {-w:.1f} 0 {-L}Z'
    return f'<circle r="{L * .9:.1f}" fill="url(#{gid})"/><path d="{d}" fill="#FFFFFF"/>'


def glints(pts, x0, y0, col, gid, seed):
    out = ''
    for i, (x, y) in enumerate(pts):
        dur = 1.5 + ((i * 7 + seed) % 5) * .22
        dl = -((i * 0.53 + seed * .31) % dur)
        L = 7 + ((i * 3 + seed) % 4) * 1.6
        out += (f'<g transform="translate({x - x0:.1f} {y - y0:.1f})"><g class="hqt" style="animation-duration:{dur:.2f}s;animation-delay:{dl:.2f}s">'
                f'{star(L, col, gid)}</g></g>')
    return out


def inline(blobs, lay, alt=ALT):
    """(html, css)。blobs：base（花火なしの絵）・layers（足す光）→ '/_blob/<id>'。lay：fireworks_layers.json"""
    sw, sh = lay['sheet']
    H, css_l, kf = '', [], []
    rockets, flashes = '', ''
    for k, e in enumerate(lay['layers']):
        x, y, w, h = e['rect']
        cx, cy = e['center']
        col = e.get('color', '#FFE7A8')
        gid = f'hqG{k}'
        H += (f'<div class="hqk hq{k}"><svg class="hqg" viewBox="0 0 {w} {h}" width="{w // 2}" height="{h // 2}" aria-hidden="true">'
              f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{col}" stop-opacity=".9"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient></defs>'
              f'{glints(e["glints"], x, y, col, gid, k)}</svg></div>')
        ox, oy = (cx - x) / 2, (cy - y) / 2
        css_l.append(f'.hqw .hq{k}{{left:{x // 2}px;top:{y // 2}px;width:{w // 2}px;height:{h // 2}px;'
                     f'background:url({blobs["layers"]}) 0 {-e["sheet_y"] / 2:g}px/{sw / 2:g}px {sh / 2:g}px no-repeat;'
                     f'transform-origin:{ox:g}px {oy:g}px;animation-name:hqK{k}}}')
        if e['kind'] == 'burst':
            L0 = LAUNCH[k]
            B = L0 + RISE
            kf.append(f'@keyframes hqK{k}{{0%,{pct(FADE[0])}{{opacity:1;transform:translateY(0) scale(1);animation-timing-function:ease-in}}'
                      f'{pct(FADE[1])}{{opacity:0;transform:translateY(5px) scale(1.06)}}'
                      f'{pct(FADE[1] + .02)},{pct(B)}{{opacity:0;transform:translateY(0) scale(.2);animation-timing-function:cubic-bezier(.1,.75,.3,1)}}'
                      f'{pct(B + OPEN)}{{opacity:1;transform:translateY(0) scale(.92);animation-timing-function:linear}}'
                      f'100%{{opacity:1;transform:translateY(0) scale(1)}}}}')
            x0 = cx + (-10 if k % 2 else 12)
        else:
            L0, B = HORSE, HORSE + HRISE
            R = 140
            kf.append(f'@keyframes hqK{k}{{0%,{pct(FADE[0])}{{opacity:1;transform:translateY(0) scale(1);clip-path:circle({R}px at {ox:g}px {oy:g}px);animation-timing-function:ease-in}}'
                      f'{pct(FADE[1])}{{opacity:0;transform:translateY(5px) scale(1.02);clip-path:circle({R}px at {ox:g}px {oy:g}px)}}'
                      f'{pct(FADE[1] + .02)},{pct(B)}{{opacity:0;transform:translateY(0) scale(.86);clip-path:circle(0px at {ox:g}px {oy:g}px);animation-timing-function:cubic-bezier(.15,.7,.3,1)}}'
                      f'{pct(B + HOPEN)}{{opacity:1;transform:translateY(0) scale(1);clip-path:circle({R}px at {ox:g}px {oy:g}px)}}'
                      f'100%{{opacity:1;transform:translateY(0) scale(1);clip-path:circle({R}px at {ox:g}px {oy:g}px)}}}}')
            x0 = cx
        # 光の玉（ちょうちんの上から まっすぐ上がって、上で消える）・開く時の小さな光
        rk = f'hqR{k}'
        rockets += (f'<g class="hqr" style="animation-name:{rk}"><path d="M0 2V46" stroke="url(#hqTl)" stroke-width="7" stroke-linecap="round" opacity=".35"/>'
                    f'<path d="M0 0V40" stroke="url(#hqTl)" stroke-width="2.6" stroke-linecap="round"/>'
                    f'<circle r="11" fill="url(#hqHd)"/><circle r="3.6" fill="#FFF8E0"/></g>')
        kf.append(f'@keyframes {rk}{{0%,{pct(L0)}{{opacity:0;transform:translate({x0:g}px,{GROUND}px);animation-timing-function:cubic-bezier(.25,.6,.35,1)}}'
                  f'{pct(L0 + .08)}{{opacity:1}}{pct(B - .01)}{{opacity:1;transform:translate({cx:g}px,{cy:g}px)}}'
                  f'{pct(B)},100%{{opacity:0;transform:translate({cx:g}px,{cy:g}px)}}}}')
        fk = f'hqF{k}'
        flashes += f'<circle class="hqf" cx="0" cy="0" r="18" fill="url(#hqHd)" style="animation-name:{fk};translate:{cx}px {cy}px"/>'
        kf.append(f'@keyframes {fk}{{0%,{pct(B)}{{opacity:0;scale:.3}}{pct(B + .06)}{{opacity:.9;scale:1}}{pct(B + .3)},100%{{opacity:0;scale:1.5}}}}')
    sky = (f'<svg class="hqs" viewBox="0 0 780 320" width="390" height="160" aria-hidden="true"><defs>'
           '<linearGradient id="hqTl" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="46"><stop offset="0" stop-color="#FFF1C4"/><stop offset=".45" stop-color="#FFB45A" stop-opacity=".7"/>'
           '<stop offset="1" stop-color="#FF7A3A" stop-opacity="0"/></linearGradient>'
           '<radialGradient id="hqHd"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".35" stop-color="#FFE7A8" stop-opacity=".6"/>'
           '<stop offset="1" stop-color="#FFD45E" stop-opacity="0"/></radialGradient></defs>'
           f'{rockets}{flashes}</svg>')
    html = (f'<div class="hqw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["base"]}" alt="">{H}{sky}</div>')
    css = ('.hqw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;isolation:isolate}'
           '.hqw .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           f'.hqw .hqk{{position:absolute;mix-blend-mode:plus-lighter;animation:{CYCLE:g}s linear infinite}}'
           '.hqw .hqg{position:absolute;left:0;top:0;overflow:visible}'
           '.hqw .hqt{transform-box:view-box;transform-origin:0 0;animation:hqTw 1.8s ease-in-out infinite}'
           '@keyframes hqTw{0%,100%{transform:scale(0) rotate(0)}50%{transform:scale(1) rotate(45deg)}}'
           '.hqw .hqs{position:absolute;left:0;top:0;mix-blend-mode:plus-lighter;overflow:visible}'
           f'.hqw .hqr,.hqw .hqf{{transform-box:view-box;transform-origin:0 0;opacity:0;animation-duration:{CYCLE:g}s;animation-timing-function:linear;animation-iteration-count:infinite}}'
           + ''.join(css_l) + ''.join(kf)
           + '@media (prefers-reduced-motion:reduce){.hqw .hqk{animation:none}.hqw .hqg,.hqw .hqs{display:none}}')
    return html, css


def judge_inline(fn, blobs, lay):
    """判定画面（Judge_Fireworks.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="hqw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, lay)
    page, k = re.subn(r'<div class="hqw" .*?</svg></div>(?=\s*<main)|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* 花火の壁紙：花火がきらきら光って、消えて、また打ち上がる（fireworks_wall.py） */\n{css}\n/* /花火の壁紙 */\n'
    if '/* 花火の壁紙：' in page:
        page = re.sub(r'/\* 花火の壁紙：.*?/\* /花火の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
