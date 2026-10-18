"""ドット絵の壁紙の動き（まさちゃんの指定）：ページに入れる HTML と CSS
   「常に走っている、10秒に一回止まる2秒止まってまた走りだす」→「止まってからの走り出しが唐突だから、走り出しもちゃんとして！」→
   「4秒〜13秒 ランダムでジャンプ、一回転してユーザーの方を1秒見てから走り出して！」「ジャンプまたは一回転」→
   「20秒〜23秒に一回立ち止まるのがなくなってるよ！」
   - いちばん下は いまの止まった絵（<img class="bnr">）。馬の動く所だけに flat/pixel_run.py のコマ（空・丘・コースごと切りぬいて横に並べた1まい・
     すき通しなし）を重ねる。コマの空・丘・コースは いまの絵と同じなので、切れ目は見えない
   - 馬は走っていて、次の2つが ばらばらに起きる：
     ・**ジャンプ か 一回転**（どちらかは ばらばら）：走りだしてから 4〜13秒（毎回ちがう）で
       ジャンプ：けり出して 足をたたんで高く跳ぶ（地面に かげ）→ 前足をつっぱって おりる（土けむり）→ ななめ → こっちを向く
       一回転：小さく跳ねながら くるっと1回転して、こっちを向いて おりる（土けむり）
       そのあと **こっちを1秒見る**（とちゅうで まばたき）→ ななめ → かまえる → 走りだす
     ・**立ち止まる**：20〜23秒に1回（毎回ちがう）。すべって止まる（ブレーキ2コマ・土けむり）→ 立って待つ（首と頭が少し上下）→ かまえる。止まっているのは2秒
     走りだしは どれも同じ：けり出す（土けむり）→ 1歩め ゆっくり → 2歩め 少し速く → 全速
   - 「ばらばら」は、決めておいた順番（EVENTS：種類と 走る秒）を 87秒で1回りさせる（CSS だけで動く・牧場の壁紙と同じやり方）。
     ジャンプ・一回転の前に走る秒が 4〜13秒、立ち止まる間が 20〜23秒 になっているかは plan() で確かめる
   - 全速の重ね（.pqr・ギャロップ1回 RUN_S 秒の steps）と、それ以外のコマを1つずつ決めた重ね（.pqx・1回りの step-end）を入れかえる。
     どれも同じ時に始まるので ずれない。全速の始まりと終わりは どれも RUN_S の倍数なので、つなぎ目も同じコマ
   - ページを開いた時は「かまえる」から始まる（どの動きも同じだけ先へ進めて始める：animation-delay -START_AT 秒）
   - 下の絵（5倍）もコマ（ドットのまま1倍）も ロスなしの WebP で、ドットは ぼかさずに大きくする（image-rendering:pixelated）。
     画面の細かさが ちがっても 重ねた所の さかい目が出ない（ドットも くっきり）
   - 視差効果を減らす（prefers-reduced-motion）なら、重ねを消して いまの止まった絵だけ
   - キャンバスでは /_blob/<id>（pixel_blobs.json の static＝下の絵・run＝コマ）・切りぬく場所とコマの並びは pixel_run.json
   クラスの名前は pq…（的中ボタンの .dp とは別）
   python3 pixel_wall.py --judge <Judge_Pixel.dc.html> <pixel_blobs.json> <pixel_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 pixel_wall.py --plan                                                         → 1回りの予定（何秒に何をするか）"""
import sys, re, json, math

ALT = '昔のゲームのようなドット絵で、コースを走る馬と「GO!」の文字（馬がいつも走り、ときどきジャンプか一回転して こっちを1秒見て、ときどき立ち止まって、また走りだす）'
RUN_S = .5                         # 全速のギャロップ1回の秒（.pqr）
# 起きること：(種類, 走る秒＝けり出してから次まで)。0.5秒きざみ（全速の つなぎ目を ギャロップ1回の倍数に）。
#   ジャンプ・一回転の前に走る秒は 4〜13秒・立ち止まる間（立ち止まり → 次の立ち止まり）は 20〜23秒（plan で確かめる）
EVENTS = [('stop', 6.5), ('jump', 9.5),                    # 立ち止まる間 20.5秒
          ('stop', 4.5), ('spin', 4.0), ('jump', 7.0),     # 22.5秒
          ('stop', 11.0), ('spin', 6.0),                   # 21.5秒
          ('stop', 13.0), ('jump', 5.0)]                   # 22.5秒 → 1回り 87秒
EV = dict(                         # (始めてからの秒, コマ)
    stop=[(0.0, 'brake0'), (0.15, 'brake1'), (0.30, 'stand0'), (0.75, 'stand1'), (1.20, 'stand0'), (1.65, 'ready')],   # すべって止まる → 立って待つ → かまえる
    jump=[(0.0, 'push')] + [(0.12 + 0.08 * i, f'jair{i}') for i in range(8)]                      # けり出して跳ぶ（宙 0.64秒）
         + [(0.76, 'brake1'), (0.90, 'turn'), (1.02, 'look'), (1.42, 'blink'), (1.54, 'look'),    # おりる → ななめ → こっちを1秒見る（まばたき）
            (2.02, 'turn'), (2.14, 'ready')],                                                    # → ななめ → かまえる
    spin=[(0.07 * i, f'spin{i}') for i in range(11)]                                            # 小さく跳ねて 1回転と4分の1（0.77秒）
         + [(0.77, 'sland'), (0.92, 'look'), (1.34, 'blink'), (1.46, 'look'),                   # こっちを向いて おりる → 1秒見る（まばたき）
            (1.92, 'turn'), (2.04, 'ready')])                                                    # → ななめ → かまえる
GO = dict(stop=2.0, jump=2.5, spin=2.5)    # 始めてから けり出すまで（立ち止まるのは2秒）
START = ([(0.0, 'push')] + [(0.30 + 0.125 * i, 'dash' if i == 0 else f'run{i}') for i in range(8)]     # けり出す → 1歩め（1コマ0.125秒）
         + [(1.30 + 0.0875 * i, f'run{i}') for i in range(8)])                                   # → 2歩め（0.0875秒）→ 全速（0.0625秒）
FULL = 2.0                         # けり出してから全速まで
START_AT = EV[EVENTS[0][0]][-1][0]  # ページを開いた時は 1回めの「かまえる」から（よーい → どん）


def plan():
    """1回りの予定：(.pqx の (秒, コマ or None＝全速), 全速の (始まり, 終わり), 1回りの秒)。
       ジャンプ・一回転の前に走る秒（4〜13秒）・立ち止まる間（20〜23秒）・全速の つなぎ目（RUN_S の倍数）を確かめる"""
    seq, full, t = [], [], 0.0
    starts = []
    for i, (kind, run) in enumerate(EVENTS):
        assert run >= FULL + 1
        nxt = EVENTS[(i + 1) % len(EVENTS)][0]
        if nxt != 'stop':
            assert 4 <= run <= 13, (i, run)
        starts.append((t, kind))
        go = GO[kind]
        seq += [(t + a, k) for a, k in EV[kind]] + [(t + go + a, k) for a, k in START] + [(t + go + FULL, None)]
        full.append((t + go + FULL, t + go + run))
        t += go + run
    stops = [a for a, k in starts if k == 'stop']
    for a, b in zip(stops, stops[1:] + [stops[0] + t]):
        assert 20 <= b - a <= 23, (a, b)
    for a, b in full:
        assert abs(a / RUN_S - round(a / RUN_S)) < 1e-9 and abs(b / RUN_S - round(b / RUN_S)) < 1e-9
    return seq, full, t


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：static（いまの止まった絵）・run（コマ）→ '/_blob/<id>'。run：pixel_run.json"""
    x0, y0, cw, ch = (v // 2 for v in run['cell'])
    order = run['order']
    n, nr = len(order), run['run']
    seq, full, cyc = plan()
    # %は 小数5けたで切り捨て（少しだけ早めに切りかえる：全速の終わりで ギャロップが次の1回に入る前に 入れかわる）
    pct = lambda t: '100%' if abs(t - cyc) < 1e-9 else f'{math.floor(t / cyc * 1e7 + 1e-6) / 1e5:.5f}'.rstrip('0').rstrip('.') + '%'
    kx, hidden = [], True
    for t, k in seq:
        if k is None:
            kx.append(f'{pct(t)}{{opacity:0}}')
            hidden = True
        else:
            kx.append(f'{pct(t)}{{{"opacity:1;" if hidden else ""}transform:translateX({-order.index(k) * cw}px)}}')
            hidden = False
    kx.append('100%{opacity:0}')
    ka = ['0%{opacity:0}'] + [f'{pct(a)}{{opacity:1}}{pct(b)}{{opacity:0}}' for a, b in full]
    d = f'-{START_AT:g}s'
    pix = 'image-rendering:-webkit-optimize-contrast;image-rendering:pixelated'
    html = (f'<div class="pqw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["static"]}" alt="">'
            '<div class="pqh"><i class="pqr"></i><i class="pqx"></i></div></div>')
    css = ('.pqw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           f'.pqw .bnr{{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%;{pix}}}'
           f'.pqw .pqh{{position:absolute;left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.pqw .pqh i{{position:absolute;left:0;top:0;height:{ch}px;background:url({blobs["run"]}) 0 0/{n * cw}px {ch}px no-repeat;{pix}}}'
           f'.pqw .pqh .pqr{{width:{nr * cw}px;opacity:0;animation:pqRun {RUN_S}s steps({nr}) {d} infinite,pqA {cyc:g}s step-end {d} infinite}}'
           f'.pqw .pqh .pqx{{width:{n * cw}px;animation:pqX {cyc:g}s step-end {d} infinite}}'
           f'@keyframes pqRun{{to{{transform:translateX(-{nr * cw}px)}}}}'
           f'@keyframes pqA{{{"".join(ka)}}}'
           f'@keyframes pqX{{{"".join(kx)}}}'
           '@media (prefers-reduced-motion:reduce){.pqw .pqh{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Pixel.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="pqw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, k = re.subn(r'<div class="pqw" .*?</i></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)   # 前に入れた重ね（何回でも同じ）
    assert k == 1, 'banner not found'
    block = f'/* ドット絵の壁紙：馬がいつも走り、ときどきジャンプか一回転して こっちを1秒見て、20〜23秒に1回 立ち止まる（pixel_wall.py） */\n{css}\n/* /ドット絵の壁紙 */\n'
    if '/* ドット絵の壁紙：' in page:
        page = re.sub(r'/\* ドット絵の壁紙：.*?/\* /ドット絵の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    if '--plan' in sys.argv:
        seq, full, cyc = plan()
        t = 0.0
        name = dict(stop='立ち止まる', jump='ジャンプ', spin='一回転')
        for (kind, run), (a, b) in zip(EVENTS, full):
            print(f'{t:6.2f}秒 {name[kind]} → {t + GO[kind]:6.2f}秒 けり出す → {a:6.2f}〜{b:6.2f}秒 全速（走りだしてから {run}秒）')
            t = b
        print(f'1回り {cyc}秒')
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
