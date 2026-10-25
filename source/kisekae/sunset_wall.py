"""夕焼けの壁紙の動き（まさちゃんの指定「常に走っている、地面の模様が動く 同じ模様をリピートする、1秒〜2秒で夕日が沈み真っ暗になる、
   1秒真っ暗で、2秒〜4秒に元の位置に夕日が戻る、10秒に一回リピートする」。馬が左向きなので 地面は左から右へ・夕日は「2〜4秒」。
   そのあと「もう少し日が沈むの速度と日が出る速度を遅くして」→ 沈むのも 上がるのも 2秒に）：ページに入れる HTML と CSS
   絵は flat/sunset_run.py の4まい（空（鳥なし：鳥は ページの SVG）・夕日・地面＝横にくり返せる絵・馬＝ギャロップのコマを横に並べた絵）。キャンバスでは /_blob/<id>（sunset_blobs.json）
   - いちばん下は いまの止まった絵（<img class="bnr">）。その上に 空 → 鳥（SVG・羽ばたいて 左へ ゆっくり 飛ぶ） → 夕日 → 地面 → 馬 → 暗くする幕
   - 馬は ギャロップのコマを RUN_S 秒で1回（steps）。地面は 左から右へ 流れて くり返す（左向きに走る馬が 前へ進んで見える。
     速さは 地面についているひづめに合わせる：ギャロップ1回で sunset_run.json の ground.px_per_cycle）
   - 10秒で1回り（CYCLE）：0〜1秒 いつもの夕焼け → 1〜3秒 夕日が 丘のうしろへ ゆっくり沈んで だんだん暗くなり、3秒で 真っ暗 →
     3秒から 夕日が 地平線の下を上がってきて 4秒に顔を出す（3〜4秒は 真っ暗）→ 4〜6秒 明るくなりながら ゆっくり上がって 6秒で もとの位置 → 10秒まで いつもの夕焼け
     （馬と地面は 暗い間も 走りつづける）
   - 視差効果を減らす（prefers-reduced-motion）なら 動く絵を消して いまの止まった絵だけ
   クラスの名前は ssw・sx…（的中ボタンの ss… とは別）
   python3 sunset_wall.py --judge <Judge_Sunset.dc.html> <sunset_blobs.json> <sunset_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）"""
import sys, re, json

STATIC = '/_blob/5f93d2cbb5295e4148858bf5daf03c5a'        # いまの止まった絵（WebP）
ALT = ('夕日を背に丘をかける馬のシルエット（風になびく細い毛のたてがみとしっぽ・夕日がわのふちの光）と、紫からオレンジの空のイラスト'
       '（馬がいつも走って地面が流れ、小さな鳥が羽ばたきながら飛び、10秒に1回 夕日が沈んで真っ暗になり、また夕日が戻る）')
CYCLE = 10.0
RUN_S = .5                                   # ギャロップ1回の秒
# 鳥（flat/sunset_banner.py の BIRDS と 同じ 場所・大きさ・色。絵の 画素 780×320）。空の 絵（sky）からは 鳥を ぬいて、ページの SVG で 羽ばたきながら
# 左へ 飛ばす（2026/10/25 まさちゃん「夕焼けは、背景の小さな鳥も常に動かして！」）
BIRDS = [(120, 70, 8), (150, 58, 6), (176, 76, 7), (650, 60, 7)]
BIRD_INK = '#2A1235'
GLIDE_S = 64.0                               # 画面の はしから はしまで（右の 外 → 左の 外・430px）飛ぶ 秒（地面の 流れより ずっと ゆっくり＝遠く）
GLIDE_W = 430                                # 右の 外（410）から 左の 外（-20）まで
FLAP = (0.52, 0.47, 0.58, 0.44)              # 羽ばたき（上げ下げ 1回の 秒・鳥ごとに 少し ちがう。1秒に 1回 くらい）
BOB = (1.7, 2.1, 1.9, 2.3)                   # 上下の ゆれ（秒）
DARK = '#06040C'                             # 真っ暗の色
SUN_DOWN, SUN_PEEK = 40, 34                  # 夕日が いちばん下（3秒）・顔を出す所（4秒）の ずれ（px・上のふちが 丘の上のふち）
SET, DARK_T, RISE = (1, 3), (3, 4), (4, 6)   # 沈む・真っ暗・上がる（秒）。まさちゃん「もう少し…遅くして」→ 沈むのも上がるのも 1秒 → 2秒
# 夕日：(秒, 下へのずれ, 次までの動き)・暗くする幕：(秒, こさ, 次までの動き)。上がりはじめの速さは 真っ暗の間の終わりの速さと そろえる
#   （真っ暗の間 quad-in で 6px → 終わりの速さ 12px/秒。上がる 34px・2秒 → はじめの かたむき 12÷17 ≒ .706 → cubic-bezier(.3,.212,…)）
SUN = [(0, 0, 'linear'), (SET[0], 0, 'ease-in'), (SET[1], SUN_DOWN, 'quad-in'), (DARK_T[1], SUN_PEEK, 'cubic-bezier(.3,.212,.3,1)'), (RISE[1], 0, 'linear'), (CYCLE, 0, 'linear')]
FADE = [(0, 0, 'linear'), (SET[0], 0, 'ease-in'), (SET[1], 1, 'linear'), (DARK_T[1], 1, 'ease-out'), (RISE[1], 0, 'linear'), (CYCLE, 0, 'linear')]
EASE = {'quad-in': 'cubic-bezier(.3333,0,.6667,.3333)'}


def pct(t):
    s = f'{t / CYCLE * 100:.4f}'.rstrip('0').rstrip('.')
    return s + '%'


def num(v, nd=3):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def birds_svg():
    """鳥 4羽の SVG（画面の px・390×160）。外の <g>＝いまの絵の 場所、.sxBm＝左へ 飛ぶ（はしから はしまで GLIDE_S 秒・いまの 場所から はじまる ように 負の delay）
       ＋ 上下の ゆれ、.sxBw＝左右の 羽（体の 点を 中心に 回して 羽ばたく：transform-box:fill-box の 右下／左下が 体の 点）"""
    out = ['<svg class="sxb" viewBox="0 0 390 160" width="390" height="160" aria-hidden="true">']
    for i, (x, y, sz) in enumerate(BIRDS):
        bx, by, s_ = x / 2, y / 2, sz / 2
        delay = -((410 - bx) / GLIDE_W) * GLIDE_S                     # いまの 場所に いる 時刻から（右の 外 410 → 左の 外 -20 を 同じ 速さで：群れの 形が くずれない）
        g0, g1 = 410 - bx, -20 - bx                                   # この 鳥の 動く はば（外の <g> で いまの 場所に 置いてあるので、そこからの ずれ）
        wl = f'M{num(-s_)},0 L{num(-s_ * .45)},{num(-s_ * .5)} L0,0'
        wr = f'M0,0 L{num(s_ * .45)},{num(-s_ * .5)} L{num(s_)},0'
        out.append(f'<g transform="translate({num(bx)} {num(by)})"><g class="sxBm" style="--g0:{num(g0)}px;--g1:{num(g1)}px;--gd:{num(delay, 2)}s;--bb:{BOB[i]:g}s;--bd:{num(-i * .7, 2)}s">'
                   f'<g class="sxBb" style="--fs:{FLAP[i]:g}s;--fd:{num(-i * .13, 2)}s">'
                   f'<path class="sxBw l" d="{wl}" fill="none" stroke="{BIRD_INK}" stroke-width=".66" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<path class="sxBw r" d="{wr}" fill="none" stroke="{BIRD_INK}" stroke-width=".66" stroke-linecap="round" stroke-linejoin="round"/>'
                   '</g></g></g>')
    out.append('</svg>')
    return ''.join(out)


def birds_css():
    kf_glide = '@keyframes sxGlide{from{transform:translateX(var(--g0))}to{transform:translateX(var(--g1))}}'   # 鳥ごとの はば（--g0 → --g1）・いまの 場所は delay で
    return ('.ssw .sxb{position:absolute;left:0;top:0;width:390px;height:160px;overflow:visible;pointer-events:none}'
            '.ssw .sxBm{animation:sxGlide ' + f'{GLIDE_S:g}s linear infinite var(--gd)' + '}'
            '.ssw .sxBb{animation:sxBob var(--bb) ease-in-out infinite alternate var(--bd)}'
            '.ssw .sxBw{transform-box:fill-box;animation:sxFlapL var(--fs) ease-in-out infinite alternate var(--fd)}'
            '.ssw .sxBw.l{transform-origin:100% 100%}'
            '.ssw .sxBw.r{transform-origin:0 100%;animation-name:sxFlapR}'
            + kf_glide
            + '@keyframes sxBob{from{transform:translateY(-1.2px)}to{transform:translateY(1.2px)}}'
            + '@keyframes sxFlapL{from{transform:rotate(-14deg)}to{transform:rotate(22deg)}}'
            + '@keyframes sxFlapR{from{transform:rotate(14deg)}to{transform:rotate(-22deg)}}')


def inline(blobs, run, alt=ALT, static=STATIC):
    """(html, css)。blobs：sky・sun・ground・horse → '/_blob/<id>'。run：sunset_run.json"""
    W2, H2 = (v // 2 for v in run['size'])
    sx0, sy0, sw, sh = (v // 2 for v in run['sun']['box'])
    gy0 = run['ground']['y0'] // 2
    gh = H2 - gy0
    h = run['horse']
    n = h['frames']
    hx, hy, cw, ch = (v // 2 for v in h['cell'])
    flow = W2 * RUN_S / (run['ground']['px_per_cycle'] / 2)          # 地面が1まいぶん（390px）流れる秒
    html = (f'<div class="ssw" role="img" aria-label="{alt}"><img class="bnr" src="{static}" alt="">'
            '<div class="sxk"></div>' + birds_svg() + '<div class="sxs"></div><div class="sxg"></div><div class="sxh"><div class="sxr"></div></div><div class="sxd"></div></div>')
    kf = lambda name, ks, fmt: f'@keyframes {name}{{' + ''.join(f'{pct(t)}{{{fmt(v)};animation-timing-function:{EASE.get(e, e)}}}' for t, v, e in ks) + '}'
    css = (f'.ssw{{position:relative;flex:none;width:{W2}px;height:{H2}px;overflow:hidden}}'
           '.ssw .bnr{position:absolute;left:0;top:0}'
           '.ssw .sxk,.ssw .sxs,.ssw .sxg,.ssw .sxh,.ssw .sxd{position:absolute}'
           f'.ssw .sxk{{left:0;top:0;width:{W2}px;height:{H2}px;background:url({blobs["sky"]}) 0 0/{W2}px {H2}px no-repeat}}'
           f'.ssw .sxs{{left:{sx0}px;top:{sy0}px;width:{sw}px;height:{sh}px;background:url({blobs["sun"]}) 0 0/{sw}px {sh}px no-repeat;'
           f'animation:sxSun {CYCLE:g}s linear infinite}}'
           f'.ssw .sxg{{left:-{W2}px;top:{gy0}px;width:{2 * W2}px;height:{gh}px;background:url({blobs["ground"]}) 0 0/{W2}px {gh}px repeat-x;'
           f'will-change:transform;animation:sxFlow {num(flow, 4)}s linear infinite}}'
           f'.ssw .sxh{{left:{hx}px;top:{hy}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.ssw .sxr{{width:{n * cw}px;height:{ch}px;background:url({blobs["horse"]}) 0 0/{n * cw}px {ch}px no-repeat;animation:sxRun {RUN_S:g}s steps({n}) infinite}}'
           f'.ssw .sxd{{left:0;top:0;width:{W2}px;height:{H2}px;background:{DARK};opacity:0;animation:sxDark {CYCLE:g}s linear infinite}}'
           + kf('sxSun', SUN, lambda v: f'transform:translateY({num(v)}px)')
           + kf('sxDark', FADE, lambda v: f'opacity:{num(v)}')
           + f'@keyframes sxFlow{{from{{transform:translateX(0)}}to{{transform:translateX({W2}px)}}}}'
           + f'@keyframes sxRun{{to{{transform:translateX(-{n * cw}px)}}}}'
           + birds_css()
           + '@media (prefers-reduced-motion:reduce){.ssw .sxk,.ssw .sxb,.ssw .sxs,.ssw .sxg,.ssw .sxh,.ssw .sxd{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Sunset.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="ssw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, k = re.subn(r'<div class="ssw" .*?<div class="sxd"></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* 夕焼けの壁紙：馬がいつも走って地面が流れ、10秒に1回 夕日が沈んで真っ暗 → また戻る（sunset_wall.py） */\n{css}\n/* /夕焼けの壁紙 */\n'
    if '/* 夕焼けの壁紙：' in page:
        page = re.sub(r'/\* 夕焼けの壁紙：.*?/\* /夕焼けの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: (v if v.startswith('/_blob/') else f'/_blob/{v}') for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    i = sys.argv.index('--judge')
    judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
