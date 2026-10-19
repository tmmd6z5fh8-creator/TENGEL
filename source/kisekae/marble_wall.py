"""大理石の壁紙の動き（まさちゃんの指定「1〜2でゆっくり向きを逆向きへ振り向き（馬の首で逆方向を２度見、3秒で一気に逆向きへ振り向く、
   8秒に一度リピートで繰り返す」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">）。像と台のまわりだけに flat/marble_run.py の コマ（背景ごと切りぬいた・すき通しなし・
     シート1まい）を重ねて、キーフレーム（step-end）で コマを めくる。コマの背景は いまの絵と同じなので 切れ目は見えない
   - 1回り CYCLE 秒（SIDE_S 秒ずつ 左向き → 右向き）。片がわの中の時刻：
       0〜1秒 そのまま → 1〜2秒 ゆっくり うしろへ ふり向く（首と頭が こちらがわを通って 反対を向く）→ 2.1〜2.3秒 前へもどる
       → 2.45秒 2度見（ぱっと うしろを見る・少し行きすぎて もどる）→ 3〜3.5秒 体ごと くるっと 反対向きに（こちらを向きながら回る・
       頭は うしろを見たまま 体が追いつく）→ 8秒まで そのまま。8秒から 同じことを 反対へ（16秒で もとの左向き）
   - ページを開くと 0秒（いまの絵と同じ）から。視差効果を減らす（prefers-reduced-motion）なら コマを出さない（いまの絵だけ）
   - キャンバスでは /_blob/<id>（marble_blobs.json の base・frames）・切りぬく場所と コマの ならびは marble_run.json
   クラスの名前は mw…（的中ボタンの .mb とは別）
   python3 marble_wall.py --judge <Judge_Marble.dc.html> <marble_blobs.json> <marble_run.json>  → 判定画面の上の絵を「ふり向く像」に書きかえる（何回やっても同じ）
   python3 marble_wall.py --plan <marble_run.json>  → コマの予定"""
import sys, re, json, math

ALT = ('金の帯の台の上の岩で、後ろ足で立ち上がる白い大理石の馬の像（波打つたてがみ・台までとどくしっぽ）と月桂樹のイラスト'
       '（8秒ごとに 像の馬が うしろを2度見して、くるっと 反対を向く）')
SIDE_S = 8.0                     # 片がわ（左向き・右向き）の秒
CYCLE = 2 * SIDE_S
T_SLOW = (1.0, 2.0)              # ゆっくり ふり向く（0 → LOOK）
T_BACK = (2.1, 2.3)              # 前へもどる（LOOK → 0）
T_SNAP = (2.45, 2.6, 2.72)       # 2度見：ぱっと うしろを見て（0 → LOOK_OVER）・少しもどる（→ LOOK）
T_TURN = (3.0, 3.5)              # 体ごと くるっと（psi 0 → PSI_R・頭は うしろを見たまま）
DT = 0.005                       # 予定を しらべる きざみ（秒）


def ease(x):
    x = min(1.0, max(0.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 2


def look_at(t, run):
    """片がわの中の時刻 t（ふり向くまで）→ ふり向きの大きさ（度・0 … LOOK_OVER）"""
    L, LO = run['LOOK'], run['LOOK_OVER']
    span = lambda a, b: (t - a) / (b - a)
    if t < T_SLOW[0]:
        return 0.0
    if t < T_SLOW[1]:
        return L * ease(span(*T_SLOW))
    if t < T_BACK[0]:
        return L
    if t < T_BACK[1]:
        return L * (1 - ease(span(*T_BACK)))
    if t < T_SNAP[0]:
        return 0.0
    if t < T_SNAP[1]:
        return LO * ease_out(span(T_SNAP[0], T_SNAP[1]))
    if t < T_SNAP[2]:
        return LO + (L - LO) * ease(span(T_SNAP[1], T_SNAP[2]))
    return L


def frame_at(t, run):
    """1回りの中の時刻 t → コマの名前"""
    side = int(t // SIDE_S) % 2                                          # 0：左向きから・1：右向きから
    t = t % SIDE_S
    A, B, C = ('A', 'B', 'C') if side == 0 else ('C', 'D', 'A')
    NL, NT = run['N_LOOK'], run['N_TURN']
    if t >= T_TURN[1]:
        return f'{C}00'
    if t >= T_TURN[0]:
        k = int(round(ease((t - T_TURN[0]) / (T_TURN[1] - T_TURN[0])) * NT))
        return f'{A}{NL:02d}' if k == 0 else f'{C}00' if k == NT else f'{B}{k:02d}'
    v = look_at(t, run)
    step = run['LOOK'] / NL
    if v > run['LOOK']:
        return f'{A}{NL + 1:02d}' if v - run['LOOK'] > (run['LOOK_OVER'] - run['LOOK']) / 2 else f'{A}{NL:02d}'
    return f'{A}{int(round(v / step)):02d}'


def plan(run):
    """[(時刻, コマの名前)]：コマが かわる時だけ（はじめは 0 秒）"""
    out = []
    n = int(round(CYCLE / DT))
    for i in range(n):
        t = i * DT
        f = frame_at(t, run)
        if not out or out[-1][1] != f:
            out.append((round(t, 3), f))
    return out


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：base（いまの止まった絵）・frames（コマのシート）→ '/_blob/<id>'。run：marble_run.json"""
    x0, y0, x1, y1 = (v // 2 for v in run['crop'])
    fw, fh = (v // 2 for v in run['frame'])
    cols, rows = run['cols'], run['rows']
    idx = {n: i for i, n in enumerate(run['frames'])}
    kf = ''
    for t, f in plan(run) + [(CYCLE, 'A00')]:
        r, c = divmod(idx[f], cols)
        p = t / CYCLE * 100
        kf += f'{p:.3f}'.rstrip('0').rstrip('.') + f'%{{background-position:{-c * fw}px {-r * fh}px}}'
    html = f'<div class="mww" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["base"]}" alt=""><i class="mwS" aria-hidden="true"></i></div>'
    css = ('.mww{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.mww .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           f'.mww .mwS{{position:absolute;left:{x0}px;top:{y0}px;width:{fw}px;height:{fh}px;'
           f'background:url({blobs["frames"]}) 0 0/{cols * fw}px {rows * fh}px no-repeat;animation:mwTurn {CYCLE:g}s step-end infinite}}'
           f'@keyframes mwTurn{{{kf}}}'
           '@media (prefers-reduced-motion:reduce){.mww .mwS{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Marble.dc.html）の上の絵を「ふり向く像」に書きかえる（<img class="bnr"> か、前に入れた <div class="mww">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="mww" .*?</i></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 大理石の壁紙：8秒ごとに 像の馬が うしろを2度見して、くるっと 反対を向く（marble_wall.py） */\n{css}\n/* /大理石の壁紙 */\n'
    if '/* 大理石の壁紙：' in page:
        page = re.sub(r'/\* 大理石の壁紙：.*?/\* /大理石の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    if '--plan' in sys.argv:
        for t, f in plan(json.load(open(sys.argv[sys.argv.index('--plan') + 1]))):
            print(f'{t:6.3f}  {f}')
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
