"""大理石の壁紙の動き（まさちゃんの指定「1〜2でゆっくり向きを逆向きへ振り向き（馬の首で逆方向を２度見、3秒で一気に逆向きへ振り向く、
   8秒に一度リピートで繰り返す」「一気に振り向くのは2秒くらいかけて」「9秒〜17秒の中で、ランダムでヒヒィーン（文字はなし）って首と前脚動かす・
   現実の馬っぽく」「または9秒くらいかけて、後ろ脚の大理石を ずっ！ずっ！ずっ！ずっ！ずっ！って画面からフェードアウト（右を向いている時限定）・
   画面右から左へ同じ手順で戻って」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">）。像と台のまわりだけに flat/marble_run.py の コマ（背景ごと切りぬいた・すき通しなし・
     シートは ふり向き look／左 → 右 turnB／右 → 左 turnD／ヒヒィーン neighL・neighR）を重ねて、キーフレーム（step-end）で コマを めくる
   - ふり向き（CYCLE 秒で1回り・SIDE_S 秒ずつ 左向き → 右向き）。片がわの中の時刻：
       0〜1秒 そのまま → 1〜2秒 ゆっくり うしろへ ふり向く → 2.1〜2.3秒 前へもどる → 2.45秒 2度見（少し行きすぎて もどる）
       → 3〜5秒 体ごと くるっと 反対向きに（2秒・こちらを向きながら回る・頭は うしろを見たまま 体が追いつく）→ 8秒まで そのまま
   - 出来事（EV_LOOP 秒で1回り・いつも同じ順番）：ふり向いたあとの 休み（片がわの 5〜9秒）に、前の出来事から 9〜17秒ごと（ばらばら）に
       ヒヒィーン … 体を起こして 首を上げ 頭をふり上げ、前足を 交互に 前へ 打ち出して 頭を少しふる（NEIGH_S 秒・字はなし）
       ずっ！ずっ！ … 右を向いている時だけ。台ごと（台の影も）ずっ！と5回 右へすべって 画面の外へ（あとの2回で うすくなって消える・
                      すべるたびに 台の下に 粉が ふわっ）→ しばらく 何もない → 左を向いて 画面の右から ずっ！と5回 もとの場所へ もどる（24秒）。
                      動いているあいだは 像も台も影もない 背景だけの絵（plate）を いまの絵の上に重ねる。
                      はじめと おわりの つなぎ目（まさちゃんの指定「中央についてからリセットされるとき、馬の切り替わりが映ってるから繋ぎが分からないように」）：
                      すべる絵と 背景だけの絵を ひとまとめ（.mwG）にして、止まっている時に いまの絵と ふわっと 入れかえる
                      （はじめ FADE_IN 秒・おわり FADE_OUT 秒。どちらも 同じ形の 同じ絵どうしなので、入れかわりが 見えない）
     ずっ！ずっ！の あいだも ふり向きの1回りは 見えない所で すすむ（もどった時に ちょうど左向きの 休み）
   - ページを開くと 0秒（いまの絵と同じ）から。視差効果を減らす（prefers-reduced-motion）なら 重ねる絵を出さない（いまの絵だけ）
   - キャンバスでは /_blob/<id>（marble_blobs.json の base・look・turnB・turnD・neighL・neighR・spR・spL・plate）・切りぬく場所と コマのならびは marble_run.json
   - 第4.155版（まさちゃん 2026/11/11・動きの 見本を 見て「大理石OK！」）：像は まさちゃんの 3D の 馬（flat/marble_glb.py・flat/marble_glb_run.py：金の 帯の 白い 大理石の 台の 上で 立ち上がる 馬）。
     動き（この ファイルの 予定）は 前と 同じ。**馬（主役）だけ 高画質**：コマの シートと すべる 絵は 画面の 3倍（marble_run.json の crop・frame・sprites の box は
     前と 同じ「壁紙の 絵 780×320 の 画素」＝ 2で わって pt。絵は その 1.5倍の 細かさ ＝ CSS の background-size（pt）が 絵を ちぢめて 置く ので、ここの 計算は かわらない）。
     背景（止まった 絵・背景 だけの 絵）は 780×320 の まま。視差効果を 減らす とき：重ねる 絵は 出さないが、ふり向きの シートの さいしょの コマ（左向きの 像・画面の 3倍）だけ 動かさずに 出す
     （前は 止まった 絵 だけ ＝ 像も 画面の 2倍 だった。シルバー帯・ゴールド帯・マスター帯と 同じ：止めた ときも 馬は 高画質）
   - 第4.167版（まさちゃん 2026/11/13「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）：コマは 1/30秒の きざみ。
     前は 角度を きざんだ コマ（ふり向き 12きざみ・体が 回る 30きざみ・ヒヒィーン 1秒に 15コマ）を「いちばん 近い コマ」で めくって いた（1秒に 12〜24コマ・間が ふぞろい）→
     1/30秒ごとの 時刻の 形を 1コマずつ 描いた コマ（flat/marble_glb_run.py の frame_list：ふり向き 片がわ 42コマ・体が 回る 59コマ・ヒヒィーン 77コマ）を、その 時刻に めくる。
     2度見の 時刻（T_SNAP）と 出来事の はじめは 1/30秒の きざみに そろえた。動いて いる 間の コマ（look・turnB・turnD・neighL・neighR）は コマが 2倍より 多く なる ので
     画面の 2倍（1まいの シートの 画素は 前と 同じ くらい＝読む 重さは かわらない）、止まって いる 間の 像（rest：左向き・右向き）は 今までどおり 画面の 3倍。
     ふり向き 〜 体が 回る 間（片がわの 1〜5秒）は ずっと 2倍の コマ（とちゅうの 短い 休みも 2倍の 止まった 形）＝細かさが ちらちら かわらない
   クラスの名前は mw…（的中ボタンの .mb とは別）
   python3 marble_wall.py --judge <Judge_Marble.dc.html> <marble_blobs.json> <marble_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 marble_wall.py --plan <marble_run.json>  → 出来事の予定とコマの予定"""
import sys, re, json, math, random
from wall_util import feather   # コマの 入れものの ふちを ぼかす（拡大した 時の 細い 線を 消す・2026/10/25）

ALT = ('金の帯の台の上で、後ろ足で立ち上がる白い大理石の馬の像（波打つたてがみ・台までとどくしっぽ）と月桂樹のイラスト'
       '（8秒ごとに 像の馬が うしろを2度見して、くるっと 反対を向く。ときどき いななく・右を向いている時は 台ごと ずっずっと 外へ出て もどってくる）')
SIDE_S = 8.0                     # 片がわ（左向き・右向き）の秒
CYCLE = 2 * SIDE_S
T_SLOW = (1.0, 2.0)              # ゆっくり ふり向く（0 → LOOK）
T_BACK = (2.1, 2.3)              # 前へもどる（LOOK → 0）
FPS = 30                         # コマは 1/30秒の きざみ
T_SNAP = (74 / FPS, 78 / FPS, 82 / FPS)   # 2度見：ぱっと うしろを見て（0 → LOOK_OVER）・少しもどる（→ LOOK）。第4.167版：2.45・2.6・2.72秒 → 1/30秒の きざみ（2.467・2.6・2.733秒）
T_TURN = (3.0, 5.0)              # 体ごと くるっと（2秒・psi 0 → PSI_R・頭は うしろを見たまま）
REST = 5.0                       # 片がわの中で 休みが はじまる秒（つぎの ふり向きは 9秒＝つぎの片がわの 1秒）
EV_SIDES = 24                    # 出来事の1回りの 片がわの数（EV_LOOP＝192秒＝ふり向きの12回り）
EV_LOOP = EV_SIDES * SIDE_S
EV_GAP = (9.0, 17.0)             # 出来事と つぎの出来事の間（はじめ → はじめ：ずっ！ずっ！の あとは もどってから 6.4〜14.4秒）
NEIGH_OFF = (0.05, 1.35)         # ヒヒィーンを はじめる所（休みの はじめから。おわりは つぎの ふり向きより前）
SLIDE_OFF = (0.1, 0.6)           # ずっ！ずっ！を はじめる所
SLIDE_P = 0.35                   # 右を向いた 休みで ずっ！ずっ！にする わりあい（ほかは ヒヒィーン）
OUT_S, AWAY_S, BACK_S = 9.5, 5.0, 9.5                     # ずっ！ずっ！：出ていく・いない・もどる 秒（あわせて 24秒＝片がわ3つ）
PUSH_T = (0.6, 2.4, 4.2, 6.0, 7.8)                         # 1回ずつの ずっ！の はじめ（出ていく・もどる の中の秒）
PUSH_D = 0.26                    # ずっ！1回の秒（さいしょ速く すぐ止まる）
OUT_X = (0, 36, 80, 134, 204, 292)                         # 出ていく：ずっ！ごとの 位置（ページの画素・右へ。だんだん大きく。292 で 像も 台も 影も 画面の 外＝像の 左はし 117＋292 > 390）
OUT_OP = (1, 1, 1, 1, 1, 1)                                # 出ていく：うすくしない（2026/10/25 まさちゃん「画面から消える時、戻ってくる最初、が薄くなるから薄くしないでそのままにして！」。前は 4回目から うすく していた）
BACK_X = (292, 204, 134, 80, 36, 0)                        # もどる：右から 左へ（だんだん小さく）
BACK_OP = (1, 1, 1, 1, 1, 1)                               # もどる：うすくしない（前は はじめの 2回が うすかった）
LIFT, TILT = 1.5, 1.4            # ずっ！の時に 少し うき上がる（画素）・すべる向きへ かたむく（度）
FADE_IN, FADE_OUT = 0.3, 0.6     # ずっ！ずっ！の はじめ・おわりに いまの絵と ふわっと 入れかえる 秒（止まっている時）
DT = 0.005                       # 予定を しらべる きざみ（秒）
SEED = 0                         # 出来事の順番を決める 乱数の はじめ（いつも同じ予定になるように：schedule が しらべて決める）


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


def tick_plan(run):
    """片がわ（SIDE_S 秒）の きざみ（1/30秒）ごとの コマ：[(きざみの 番号, シート, コマの 名前の しっぽ)]。しっぽ：'' ＝止まった 形（rest：画面の 3倍）・
       'r' ＝動きの とちゅうの 止まった 形（look の シート）・'<番号>' ＝その 形が はじめて 出る きざみの 番号（look・turn）。
       ふり向き（T_SLOW の はじめの 次の きざみ 〜 T_TURN の はじめ）は look・体が 回る 間（T_TURN）は turn・ほかは rest"""
    n = int(round(SIDE_S * FPS))
    i0, i1, i2 = int(round(T_SLOW[0] * FPS)), int(round(T_TURN[0] * FPS)), int(round(T_TURN[1] * FPS))
    for t in T_SLOW + T_BACK + T_SNAP + T_TURN:
        assert abs(t * FPS - round(t * FPS)) < 1e-9, t
    out, seen = [], {}
    for i in range(n):
        if i <= i0 or i >= i2:
            out.append((i, 'rest', ''))
        elif i <= i1:
            v = round(look_at(i / FPS, run), 3)
            out.append((i, 'look', 'r' if v == 0 else seen.setdefault(v, f'{i:03d}')))
        else:
            out.append((i, 'turn', f'{i:03d}'))
    return out


def look_frames(run):
    """ふり向きの コマ（片がわ）：[(しっぽ, ふり向きの 大きさ〈度〉)]（'r'＝0）"""
    out, seen = [('r', 0.0)], set()
    for i, sh, tail in tick_plan(run):
        if sh == 'look' and tail != 'r' and tail not in seen:
            seen.add(tail)
            out.append((tail, round(look_at(i / FPS, run), 3)))
    return out


def turn_frames():
    """体が 回る コマ：[(しっぽ, 回った わりあい 0〜1)]（T_TURN の 間の きざみ）"""
    i1, i2 = int(round(T_TURN[0] * FPS)), int(round(T_TURN[1] * FPS))
    return [(f'{i:03d}', ease((i - i1) / (i2 - i1))) for i in range(i1 + 1, i2)]


def base_at(i, run):
    """ふり向きの1回り（CYCLE 秒）の中の きざみ i → (シート, コマの名前)。シート：rest・look・turnB・turnD"""
    n = int(round(SIDE_S * FPS))
    side = (i // n) % 2                                                  # 0：左向きから・1：右向きから
    A, B, C, sB = ('A', 'B', 'C', 'turnB') if side == 0 else ('C', 'D', 'A', 'turnD')
    _, sh, tail = tick_plan(run)[i % n]
    if sh == 'rest':
        return 'rest', (A if (i % n) * 1.0 / FPS < T_TURN[1] else C)
    if sh == 'look':
        return 'look', A + tail
    return sB, B + tail


def schedule(run):
    """出来事の予定 [(はじめの秒, 'neigh'|'slide', 向き 'L'|'R')]（EV_LOOP 秒の1回り）。いつも同じ予定（SEED から しらべて、決まりに合う さいしょの予定）。
       休みは 片がわ s の 8s+REST 秒から（s が偶数なら 右向き・奇数なら 左向き）。決まり：
       ヒヒィーン → つぎ：はじめ → はじめ が EV_GAP（1つあとの休みなら つぎを 1秒以上 おそく・2つあとなら おそすぎない）・
       ずっ！ずっ！ → つぎ：もどってから 6.4〜14.4秒（4つあとの休み）・ずっ！ずっ！は 右向きの休みだけ"""
    ns = run['NEIGH_S']
    lo, hi = EV_GAP[0] - ns, EV_GAP[1] - ns                           # おわり → つぎのはじめ
    dur = dict(neigh=ns, slide=OUT_S + AWAY_S + BACK_S)
    for seed in range(SEED, SEED + 20000):
        rnd = random.Random(seed)
        s = rnd.choice((1, 2))
        first, slots = s, []
        while True:
            kind = 'slide' if s % 2 == 0 and rnd.random() < SLIDE_P else 'neigh'
            slots.append((s, kind))
            step = 4 if kind == 'slide' else rnd.choice((1, 2, 2, 2))
            if s + step >= first + EV_SIDES:
                ok = s + step == first + EV_SIDES
                break
            s += step
        if not ok:
            continue
        evs = []
        for (s, kind) in slots:                                       # 休みの中の はじめ：決まりに合うように 乱数で
            rng = SLIDE_OFF if kind == 'slide' else NEIGH_OFF
            evs.append([s, kind, rnd.uniform(*rng)])
        good = True
        for _ in range(200):
            good = True
            for i in range(len(evs)):
                s0, k0, o0 = evs[i]
                s1, k1, o1 = evs[(i + 1) % len(evs)]
                t0 = s0 * SIDE_S + REST + o0
                t1 = s1 * SIDE_S + REST + o1 + (EV_LOOP if i == len(evs) - 1 else 0)
                gap = t1 - (t0 + dur[k0])
                if not lo - 1e-9 <= gap <= hi + 1e-9:
                    good = False
                    rng = SLIDE_OFF if k1 == 'slide' else NEIGH_OFF
                    evs[(i + 1) % len(evs)][2] = rnd.uniform(*rng)
                    if gap < lo and k0 == 'neigh':
                        evs[i][2] = rnd.uniform(NEIGH_OFF[0], NEIGH_OFF[0] + 0.3)
            if good:
                break
        kinds = [k for _, k, _ in evs]
        sides = [('R' if s % 2 == 0 else 'L') for s, k, _ in evs if k == 'neigh']
        if not good or kinds.count('slide') < 2 or sides.count('L') < 2 or sides.count('R') < 2:
            continue
        out = sorted((round(round((s * SIDE_S + REST + o) * FPS) / FPS, 5) % EV_LOOP, k, 'R' if s % 2 == 0 else 'L') for s, k, o in evs)   # はじめは 1/30秒の きざみに
        if out[0][0] > 16 or min(t for t, k, _ in out if k == 'slide') > 40:      # ページを開いて すぐ（16秒まで）に 1つめ・40秒までに ずっ！ずっ！
            continue
        if any(out[i][1] == 'slide' and out[(i + 1) % len(out)][1] == 'slide' for i in range(len(out))):   # ずっ！ずっ！は つづけない
            continue
        return out
    raise RuntimeError('no schedule')


def push_curve(u):
    """ずっ！1回の動き（u：0 → 1）→ (すすみ 0 → 1, うき上がり 0 → 1 → 0)"""
    return ease_out(u), math.sin(math.pi * u)


def slide_parts(t0):
    """ずっ！ずっ！（はじめ t0）の 動き：[(要素, 秒, 横の位置, うき上がり, かたむき, こさ)]・粉 [(秒, 横の位置, 向き, こさ)]・台を消す (はじめ, おわり)"""
    moves, dust = [], []
    for who, ts, X, OP, sgn in (('spR', t0, OUT_X, OUT_OP, 1), ('spL', t0 + OUT_S + AWAY_S, BACK_X, BACK_OP, -1)):
        moves.append((who, ts, X[0], 0.0, 0.0, OP[0]))
        for k, p in enumerate(PUSH_T):
            for j in range(7):
                u = j / 6
                e, h = push_curve(u)
                moves.append((who, ts + p + PUSH_D * u, X[k] + (X[k + 1] - X[k]) * e, -LIFT * h, sgn * TILT * h, OP[k] + (OP[k + 1] - OP[k]) * e))
            dust.append((ts + p, X[k], sgn, OP[k] if OP[k] > 0 else OP[k + 1]))
    return moves, dust, (t0, t0 + OUT_S + AWAY_S + BACK_S)


def _pct(t, period):
    return f'{t / period * 100:.5f}'.rstrip('0').rstrip('.') + '%'


def _kf(name, pts, period, smooth=False):
    """[(秒, 'css')] → @keyframes。おなじ値が つづく所は まとめる（smooth：なめらかに つなぐ動きなので、つづく所の 両はしは のこす）"""
    out = []
    for i, (t, v) in enumerate(pts):
        prev = pts[i - 1][1] if i else None
        nxt = pts[i + 1][1] if i + 1 < len(pts) else None
        if v != prev or (smooth and v != nxt):
            out.append(f'{_pct(t, period)}{{{v}}}')
    if not pts or pts[-1][0] < period:
        out.append(f'100%{{{pts[-1][1]}}}')
    return f'@keyframes {name}{{{"".join(out)}}}'


def vis_pts(pts, smooth=False):
    """こさの キーフレーム [(秒, 'css')] → こさ 0 の 間だけ visibility:hidden の キーフレーム（step-end で 使う）。
       smooth：なめらかに つなぐ 動き（次の キーフレームまでに こさが 0 より 大きく なる 間も 見せる）。
       見えない 間も 合成の 層の 画素を 使わない ように（まさちゃん「他も同じようにいらないデータ使ってるものが、もしあれは整えて！」）"""
    def op(v):
        m = re.search(r'opacity:([0-9.]+)', v)
        return float(m.group(1)) if m else 1.0
    out = []
    for i, (t, v) in enumerate(pts):
        o0 = op(v)
        o1 = op(pts[i + 1][1]) if i + 1 < len(pts) else o0
        show = o0 > 0 or (smooth and o1 > 0)
        out.append((t, f'visibility:{"visible" if show else "hidden"}'))
    return out


def tracks(run):
    """要素ごとの キーフレーム：コマ（step-end）＝{要素: (周期, [(秒, 'css')])}・すべる絵と 粉（なめらか）＝{要素: [(秒, 'css')]}・出来事の予定"""
    fw, fh = (v // 2 for v in run['frame'])
    assert run['FPS'] == FPS
    pos = {}
    for sname, sh in run['sheets'].items():
        for i, n in enumerate(sh['frames']):
            r, c = divmod(i, sh['cols'])
            assert n not in pos, n
            pos[n] = f'background-position:{-c * fw}px {-r * fh}px'
    F = {k: (CYCLE, []) for k in ('rest', 'look', 'turnB', 'turnD')}
    nc = int(round(CYCLE * FPS))
    for i in range(nc + 1):                                              # 1/30秒の きざみ ごと（同じ コマが つづく 所は _kf が まとめる）
        t = i / FPS
        sname, f = base_at(i % nc, run)
        for k in F:
            if k == 'rest':
                if sname == 'rest':                                   # ふり向き・体が 回る あいだは 前のコマのまま（上の 重ねが かくす）
                    F[k][1].append((round(t, 5), pos[f]))
            else:
                F[k][1].append((round(t, 5), pos[f] + ';opacity:1' if sname == k else 'opacity:0'))
    ev = schedule(run)
    ns = run['NEIGH_S']
    nk = int(round(ns * FPS))
    ne = int(round(EV_LOOP * FPS))
    for key, side in (('neighL', 'L'), ('neighR', 'R')):
        vals = ['opacity:0'] * (ne + 1)
        for t0, kind, sd in ev:
            if kind == 'neigh' and sd == side:
                for k in range(1, nk):                                 # コマ k（ヒヒィーンの k/30秒の 形）を はじめ＋k/30秒に
                    vals[(int(round(t0 * FPS)) + k) % ne] = pos[f'N{side}{k:02d}'] + ';opacity:1'
        vals[ne] = vals[0]
        F[key] = (EV_LOOP, [(round(i / FPS, 5), v) for i, v in enumerate(vals)])
    group = [(0.0, 'opacity:0')]                                       # すべる絵と 背景だけの絵の ひとまとめ（ふわっと 入れかえる）
    S = {'spR': [(0.0, 'opacity:0;transform:none')], 'spL': [(0.0, 'opacity:0;transform:none')], 'dust': [(0.0, 'opacity:0;transform:none')]}
    for t0, kind, side in sorted(ev):
        if kind != 'slide':
            continue
        moves, dust, (a, b) = slide_parts(t0)
        assert b <= EV_LOOP, 'slide across the loop end'
        group += [(a, 'opacity:0'), (a + FADE_IN, 'opacity:1'), (b, 'opacity:1'), (b + FADE_OUT, 'opacity:0')]
        for who in ('spR', 'spL'):
            mv = [m for m in moves if m[0] == who]
            S[who].append((mv[0][1] - 0.002, 'opacity:0;transform:none'))
            for _, t, x, y, r, op in mv:
                S[who].append((t, f'opacity:{op:.2f};transform:translate({x:.1f}px,{y:.2f}px) rotate({r:.2f}deg)'))
            end = b + FADE_OUT + 0.002 if who == 'spL' else mv[-1][1] + 0.01   # もどった絵は ふわっと 入れかわり おわるまで
            S[who].append((end - 0.002, S[who][-1][1]))
            S[who].append((end, 'opacity:0;transform:none'))
        for t, x, sgn, op in dust:
            S['dust'].append((t - 0.002, 'opacity:0;transform:none'))
            for j in range(6):
                u = j / 5
                S['dust'].append((t + 0.55 * u, f'opacity:{0.8 * op * (1 - u) ** 1.4 if j else 0:.2f};'
                                  f'transform:translate({x - sgn * 5 * u:.1f}px,0) scale({0.5 + 0.8 * ease_out(u):.2f},{0.6 + 0.5 * ease_out(u):.2f})'))
            S['dust'].append((t + 0.55 + 0.002, 'opacity:0;transform:none'))
    return F, group, S, ev


def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：base（いまの止まった絵）・シート（rest・look・turnB・turnD・neighL・neighR）・spR・spL・plate → '/_blob/<id>'。run：marble_run.json"""
    x0, y0, x1, y1 = (v // 2 for v in run['crop'])
    fw, fh = (v // 2 for v in run['frame'])
    F, group, S, ev = tracks(run)
    css = ('.mww{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.mww .bnr{position:absolute;left:0;top:0;width:390px;height:160px;object-position:50% 50%}'
           '.mww i{position:absolute;display:block;font-style:normal;pointer-events:none}'
           f'.mww .mwF{{left:{x0}px;top:{y0}px;width:{fw}px;height:{fh}px;background-repeat:no-repeat;animation-timing-function:step-end;animation-iteration-count:infinite}}'
           + feather('.mww .mwF', x0, y0, fw, fh))
    html = f'<div class="mww" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["base"]}" alt="">'
    for key, cls in (('rest', 'mwS'), ('look', 'mwM'), ('turnB', 'mwB'), ('turnD', 'mwD'), ('neighL', 'mwNL'), ('neighR', 'mwNR')):
        sh = run['sheets'][key]
        period, pts = F[key]
        css += (f'.mww .{cls}{{background-image:url({blobs[key]});background-size:{sh["cols"] * fw}px {sh["rows"] * fh}px;'
                + ('' if key == 'rest' else 'opacity:0;')
                + (f'animation-name:{cls}K;animation-duration:{period:g}s}}' + _kf(f'{cls}K', pts, period) if key == 'rest' else
                   f'animation-name:{cls}K,{cls}V;animation-duration:{period:g}s}}' + _kf(f'{cls}K', pts, period) + _kf(f'{cls}V', vis_pts(pts), period)))
        html += f'<i class="mwF {cls}" aria-hidden="true"></i>'
    css += (f'.mww .mwG{{left:0;top:0;width:390px;height:160px;opacity:0;animation:mwGK {EV_LOOP:g}s linear infinite,mwGV {EV_LOOP:g}s step-end infinite}}'   # ひとまとめ：ふわっと 入れかえる
            + _kf('mwGK', group, EV_LOOP, True) + _kf('mwGV', vis_pts(group, smooth=True), EV_LOOP))
    html += '<i class="mwG" aria-hidden="true">'
    px0, py0, px1, py1 = (v / 2 for v in run['plate'])              # 背景だけの絵：像と台と影の所だけ（ほかは すき通し）
    css += (f'.mww .mwP{{left:{px0:g}px;top:{py0:g}px;width:{px1 - px0:g}px;height:{py1 - py0:g}px;'
            f'background:url({blobs["plate"]}) 0 0/{px1 - px0:g}px {py1 - py0:g}px no-repeat}}')
    html += '<i class="mwP"></i>'
    b = run['sprites']['spR']
    fxc, fyb = b['foot'][0] / 2, b['foot'][1] / 2
    bw = (b['base'][1] - b['base'][0]) / 2
    dw = bw + 36
    css += (f'.mww .mwU{{left:{fxc - dw / 2:g}px;top:{fyb - 13:g}px;width:{dw:g}px;height:16px;opacity:0;transform-origin:50% 100%;'
            f'animation:mwUK {EV_LOOP:g}s linear infinite}}.mww .mwU svg{{display:block;width:100%;height:100%}}' + _kf('mwUK', S['dust'], EV_LOOP, True))
    html += ('<i class="mwU">'
             f'<svg viewBox="0 0 {dw:g} 16" preserveAspectRatio="none"><defs><radialGradient id="mwDu"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/>'
             '<stop offset=".6" stop-color="#EDE6DA" stop-opacity=".55"/><stop offset="1" stop-color="#E2D9CA" stop-opacity="0"/></radialGradient></defs>'
             + ''.join(f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="{rx:g}" ry="{ry:g}" fill="url(#mwDu)"/>'
                       for cx, cy, rx, ry in ((11, 11, 11, 5), (24, 9, 8, 4.5), (dw - 11, 11, 11, 5), (dw - 24, 9, 8, 4.5)))
             + '</svg></i>')
    for key in ('spR', 'spL'):
        b = run['sprites'][key]
        sx0, sy0, sx1, sy1 = (v / 2 for v in b['box'])
        fx, fy = b['foot'][0] / 2 - sx0, b['foot'][1] / 2 - sy0
        cls = 'mw' + key[2]
        css += (f'.mww .{cls}{{left:{sx0:g}px;top:{sy0:g}px;width:{sx1 - sx0:g}px;height:{sy1 - sy0:g}px;opacity:0;'
                f'background:url({blobs[key]}) 0 0/{sx1 - sx0:g}px {sy1 - sy0:g}px no-repeat;transform-origin:{fx:g}px {fy:g}px;'
                f'animation:{cls}K {EV_LOOP:g}s linear infinite}}' + _kf(f'{cls}K', S[key], EV_LOOP, True))
        html += f'<i class="{cls}"></i>'
    html += '</i></div>'
    css += '@media (prefers-reduced-motion:reduce){.mww i{display:none}.mww .mwS{display:block;animation:none}}'      # 止めた ときも 像は 高画質（さいしょの コマ＝左向き）
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Marble.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="mww">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="mww" .*?<i class="mwL"></i></i></div>|<div class="mww" .*?<i class="mwL" aria-hidden="true"></i></div>|'
                      r'<div class="mww" .*?<i class="mwS" aria-hidden="true"></i></div>|<img class="bnr" [^>]*>',
                      lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* 大理石の壁紙：8秒ごとに 像の馬が うしろを2度見して、くるっと 反対を向く・ときどき いななく／ずっずっと 外へ出て もどる（marble_wall.py） */\n{css}\n/* /大理石の壁紙 */\n'
    if '/* 大理石の壁紙：' in page:
        page = re.sub(r'/\* 大理石の壁紙：.*?/\* /大理石の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    if '--plan' in sys.argv:
        run = json.load(open(sys.argv[sys.argv.index('--plan') + 1]))
        for t, k, side in schedule(run):
            print(f'{t:8.3f}  {k:5s} {side}')
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
