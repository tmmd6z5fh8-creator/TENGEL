"""的中ボタン（App Store版 第3弾：アップデート指示書 10章・16.2〜16.6）：見本（gen_fx.py・boards.py）の CSS と HTML を、
   アプリの画面（source/fx.js）が使う形に束ねる。
     python3 build_fx.py <出力.json>     … 確かめる用（build_pwa.py は TARGET=app のとき bundle() を呼んで index.html に入れる）
   束ねるもの
     css   … 見本の COMMON_CSS（重ねる画面から）・HIT_CSS・MISS_CSS・BIG_CSS・BURST_CSS・fz_css()（FREEZE_CSS＋ネオンのカット）・
             いつもの（default）のボード（boards.py）・アプリ用の足し（舞台・お金なしの行）。
             全部の選択子を .fxs（390×844 の舞台）の中だけに効かせ、@keyframes の名前に fx を付ける（アプリの CSS とかぶらない）。
             「視差効果を減らす」の @media の中身は .fxs.calm にも効かせる（設定の「演出を控えめにする」：16.6）
     push  … PUSHの画面（hit・big・fz）。隠れど的中は big の PUSH
     reveal… 押したあと（hit・big・miss・fz）。{{BOARD}} にボード・{{N}} に行の数が入る。隠れど的中は fz の押したあと
     board … ボードの部品（すみの飾り・見出し）。行は fx.js が作る（券種ごとの 結果・お金なし：16.4）
     sfx   … 効果音のファイル名（アプリの Resources に入れる。リポジトリには入れない：1章の11）
   見本の /_blob/… の絵は、アプリの中のファイル（fz_nglow.webp・fz_ncore.webp）に置きかえる。"""
import json
import os
import re
import sys

K = os.path.dirname(os.path.abspath(__file__))
ASSETS = dict(nglow='fz_nglow.webp', ncore='fz_ncore.webp')
SFX = dict(hit_push='sfx_hit_push.m4a', hit='sfx_hit.m4a', big_push='sfx_big_push.m4a', big='sfx_big.m4a', fz_push='sfx_fz_push.m4a', fz='sfx_fz.m4a')
ASSET_FILES = sorted(ASSETS.values()) + sorted(SFX.values())


def load_gen_fx():
    """gen_fx.py を読む（読むときに sys.argv[1] の fx_blobs.json を開くので、いったん差しかえる）"""
    if 'gen_fx' in sys.modules:
        return sys.modules['gen_fx']
    argv, path0 = sys.argv, list(sys.path)
    sys.argv = ['gen_fx.py', os.path.join(K, 'fx_blobs.json')]
    if K not in sys.path:
        sys.path.insert(0, K)
    try:
        import gen_fx as G
    finally:
        sys.argv = argv
    return G


# ---------------------------------------------------------------- CSS を舞台（.fxs）の中だけに効かせる
def split_top(s, sep):
    """かっこ・引用符の外の sep で分ける"""
    out, cur, depth, q = [], '', 0, ''
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = ''
            continue
        if ch in '"\'':
            q = ch
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == sep and depth == 0:
            out.append(cur)
            cur = ''
            continue
        cur += ch
    if cur.strip():
        out.append(cur)
    return out


def split_rules(css):
    """CSS → [(選択子または @…, 中身)]（いちばん外のブロックごと。コメントは消す）"""
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        sel = css[i:j].strip()
        depth, k, q = 0, j, ''
        while k < n:
            c = css[k]
            if q:
                if c == '\\':
                    k += 2
                    continue
                if c == q:
                    q = ''
            elif c in '"\'':
                q = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        out.append((sel, css[j + 1:k]))
        i = k + 1
    return out


def scope(css, prefix='.fxs', kf='fx'):
    """選択子に prefix を付け、@keyframes の名前に kf を付ける。prefers-reduced-motion の @media の中身は prefix.calm にも効かせる"""
    rules = split_rules(css)
    names = set()

    def collect(rs):
        for sel, body in rs:
            if sel.startswith('@keyframes'):
                names.add(sel.split()[1])
            elif sel.startswith('@media'):
                collect(split_rules(body))
    collect(rules)

    def rename(body):
        def fix(m):
            segs = []
            for s in split_top(m.group(2), ','):
                toks = s.strip().split(None, 1)
                if toks and toks[0] in names:
                    toks[0] = kf + toks[0]
                segs.append(' '.join(toks))
            return m.group(1) + ','.join(segs)
        return re.sub(r'(animation(?:-name)?\s*:)([^;}]*)', fix, body)

    calm_rules = []   # 「視差効果を減らす」の中身を .fxs.calm にも（いちばん最後に置く：ふつうの行より あとに 効かせる）

    def emit(rs, pre, calm):
        out = []
        for sel, body in rs:
            if sel.startswith('@keyframes'):
                out.append(f'@keyframes {kf}{sel.split()[1]}{{{body}}}')
            elif sel.startswith('@media'):
                inner = split_rules(body)
                out.append(sel + '{' + '\n'.join(emit(inner, pre, False)) + '}')
                if calm and 'prefers-reduced-motion' in sel:
                    calm_rules.extend(emit(inner, pre + '.calm', False))
            elif sel.startswith('@'):
                out.append(sel + '{' + body + '}')
            else:
                out.append(','.join(f'{pre} {s.strip()}' for s in split_top(sel, ',')) + '{' + rename(body) + '}')
        return out
    main = emit(rules, prefix, True)
    return '\n'.join(main + ['/* 設定の「演出を控えめにする」＝視差効果を減らすと同じ形（16.6） */'] + calm_rules) + '\n'


# ---------------------------------------------------------------- アプリ用の足し
# 舞台：画面のまん中に 390×844 を置いて、縦横の比を変えずに画面に入る大きさにする（--fxk は fx.js が決める：16.3「画面の大きさ」※仮）
STAGE_CSS = r'''
#fxOv{position:fixed;inset:0;z-index:80;background:var(--fxbd,rgba(24,14,4,.62));overflow:hidden;touch-action:none;-webkit-user-select:none;user-select:none}
#fxOv.rv.k-big,#fxOv.rv.k-hidden{--fxbd:rgba(6,4,18,.86)}
#fxOv.rv.k-fz{--fxbd:#000000}
#fxOv.k-fz:not(.rv){--fxbd:rgba(5,2,14,.9)}
html.fxon,html.fxon body{overflow:hidden!important}
.fxs{position:absolute;left:50%;top:50%;width:390px;height:844px;margin:-422px 0 0 -195px;transform:scale(var(--fxk,1));transform-origin:50% 50%;overflow:hidden;
  font-family:"BIZ UDPGothic",sans-serif;-webkit-font-smoothing:antialiased;color:#1B2238}
.fxs *{box-sizing:border-box}
.fxs .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.fxs .ov{z-index:20}
.fxs button{-webkit-appearance:none;appearance:none;font-family:inherit}
.fxs .push span{display:block}
/* ボード：お金は出さない（16.4・第4.53版）。券種ごとに 1行：券種・結果（的中／不的中／返還）・当たった 組番（3つまで＋ほか○点）。当たりのない 券種は うすく */
.fxs .rb .bsub{font-size:12px}
.fxs .rb .brows li{gap:3px 6px}
.fxs .rb .rs{flex:none;display:inline-flex;align-items:center;height:22px;padding:0 8px;border-radius:999px;font-size:11.5px;font-weight:800;letter-spacing:.02em;background:var(--acc);color:#FFFFFF}
.fxs .rb .rs.miss,.fxs .rb .rs.ref{background:transparent;color:var(--sub);border:1px solid var(--tagLine)}
.fxs .rb .brows li.no{opacity:.72}
.fxs .rb .brows li.no .bt{color:var(--sub)}
.fxs .rb .more{margin-left:auto;font-size:11px;font-weight:700;color:var(--sub);white-space:nowrap}
.fxs .rb .bc{flex-wrap:wrap}
.fxs .rb.miss .rs{background:transparent;color:var(--sub);border:1px solid var(--tagLine)}
.fxs .rb .zrib .n{margin:0 1px}
'''

PUSH_HIT = '''<div class="ov">
  <div class="dim"></div>
  <div class="pbox">
    <button class="push" type="button" data-fx="tap" aria-label="的中ボタン"><span>PUSH</span></button>
    <div class="pshadow"></div>
    <p class="tap">タップ！</p>
  </div>
</div>'''


# テーマの的中PUSH（第4弾・16.2.1）：{{PC}}＝クラスの頭（' sk' など）・{{SVG}}＝面の SVG（kisekae.js が ks_<id>.json から渡す）
PUSH_HIT_T = '''<div class="ov">
  <div class="dim"></div>
  <div class="pbox">
    <button class="push{{PC}}" type="button" data-fx="tap" aria-label="的中ボタン">{{SVG}}<span>PUSH</span></button>
    <div class="pshadow{{PC}}"></div>
    <p class="tap{{PC}}">タップ！</p>
  </div>
</div>'''


def push_big(G):
    return f'''<div class="ov big">
  <div class="dim"></div>
  <div class="spk">{G.sparkles(22, 5)}</div>
  <div class="pbox">
    <button class="push big" type="button" data-fx="tap" aria-label="デカ的中ボタン"><i class="halo" aria-hidden="true"><i><b></b></i></i><span>PUSH</span></button>
    <div class="pshadow big"></div>
    <p class="tap big">タップ！</p>
  </div>
</div>'''


def push_fz(G):
    h = G.fz_push().replace('onClick="{{toReveal}}"', 'data-fx="tap"')
    assert 'data-fx="tap"' in h and '{{' not in h
    return f'<div class="ov fz">\n    {h}\n  </div>'


CLOSE = '<button class="close" type="button" data-fx="close">とじる</button>'


def reveal_hit(G):
    return f'''<div class="ov hit" style="--n:{{{{N}}}}">
    <div class="dim"></div>
    <div class="rays"></div>
    <div class="pressed"></div>
    <div class="hb">{{{{BOARD}}}}</div>
    <div class="conf">{G.confetti(28, 2)}</div>
    {CLOSE}
  </div>'''


def reveal_hit_t(G):
    """テーマの的中の押したあと（16.2.1）：{{PRESSED}}＝押したあとの面・{{BURST}}＝そのテーマの はじけるかけら（見本の page() と同じ重ね方）"""
    return f'''<div class="ov hit" style="--n:{{{{N}}}}">
    <div class="dim"></div>
    <div class="rays"></div>
    <div class="pressed{{{{PC}}}}">{{{{PRESSED}}}}</div>{{{{BURST}}}}
    <div class="hb">{{{{BOARD}}}}</div>
    <div class="conf">{G.confetti(28, 2)}</div>
    {CLOSE}
  </div>'''


def reveal_big(G):
    layers = ('<div class="rbow"></div><div class="glow"></div><div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>'
              '<div class="spk">' + G.sparkles(26, 9) + '</div>'
              + G.burst(195, 371, .04, 600, '#FFF6C8', '#FFB21A', 5, n=18, z=5)          # 押した瞬間の爆発
              + G.burst(195, 420, .55, 660, '#FFFFFF', '#FF3BB8', 6, n=14, star=False, z=5)   # ボードの着地（ボードのうしろ・輪と光の破片だけ）
              + G.burst(195, 316, .7, 300, '#FFFFFF', '#FFE53B', 7, n=0, star=False, z=7))   # 「デカ的中!!」の輪
    return f'''<div class="ov big rv" style="--n:{{{{N}}}}">
    <div class="dim"></div>
    {layers}
    <div class="pressed big"></div>
    <div class="hb">{{{{BOARD}}}}</div>
    <div class="conf">{G.confetti(34, 3, rainbow=True)}</div>
    <div class="flash"></div>
    {CLOSE}
  </div>'''


REVEAL_MISS = f'''<div class="ov miss" style="--n:{{{{N}}}}">
    <div class="dim"></div>
    <div class="hb">{{{{BOARD}}}}</div>
    {CLOSE}
  </div>'''


def reveal_fz(G):
    """ど的中・隠れど的中の押したあと（見本の fz_layers と同じ重ね方。ボードは {{BOARD}}）"""
    R = G.FZ_T['R']
    return f'''<div class="ov fz" style="--n:{{{{N}}}}">
    {G.bz_defs()}<div class="blk"></div>
    <div class="fin"><div class="fsk">
      <div class="fb"></div><div class="frr"></div><div class="frg"><i style="--d:{G.fz_sec(R + .1)}"></i><i style="--d:{G.fz_sec(R + 1)}"></i></div>
      {G.burst(195, 330, R + .02, 520, '#FFFFFF', '#FF3BD2', 90, n=22)}
      <div class="emb">{G.embers(36, 11)}</div>
      <div class="conf cb">{G.coins(22, 8, R)}</div>
      <div class="hb">{{{{BOARD}}}}</div>
      {G.dlogo()}
      <div class="conf">{G.confetti(40, 7, rainbow=True, d0=R)}</div>
    </div></div>
    {G.MT['html']}
    {G.FZ_HTML}
    <div class="xf" aria-hidden="true"><div class="rfl"></div></div>
    {CLOSE}
  </div>'''


def board_parts():
    import boards
    t = boards.BY_ID['default']
    vb, body = t['orn']
    oc = ' o34' if vb.endswith('44 34') else ' o40' if vb.endswith('40 40') else ''
    orn = f'<svg class="orn{oc}" viewBox="{vb}" aria-hidden="true">{body}</svg>' if body else ''
    return dict(orn=orn, titles=dict(boards.TITLES))


def css_all(G):
    import boards
    common = G.COMMON_CSS
    i = common.index('/* ---------- 重ねる画面 ---------- */')
    head, tail = common[:i], common[i:]
    m = re.search(r'\.ph\{--pushA[\s\S]*?\}', head)
    assert m, 'COMMON_CSS の --pushA の行が見つからないよ'
    vars_rule = m.group(0).replace('.ph{', '.fxs{', 1)
    css = vars_rule + '\n' + tail + G.HIT_CSS + G.MISS_CSS + G.BIG_CSS + G.BURST_CSS + G.fz_css() + boards.board_css(['default'])
    # 見本の絵（キャンバスの /_blob/…）→ アプリの中のファイル
    for key, name in (('fz_nglow', ASSETS['nglow']), ('fz_ncore', ASSETS['ncore'])):
        blob = '/_blob/' + G.blobs[key]
        assert blob in css, key
        css = css.replace(blob, name)
    assert '/_blob/' not in css, '見本の絵が残っているよ'
    out = scope(css)
    # 選択子に付けた .fxs は、舞台そのもの（.fxs{…}）にも付いてしまう → 舞台の変数の行だけ直す
    out = out.replace('.fxs .fxs{', '.fxs{')
    return STAGE_CSS + out


def bundle():
    G = load_gen_fx()
    return dict(css=css_all(G), push=dict(hit=PUSH_HIT, hit_t=PUSH_HIT_T, big=push_big(G), fz=push_fz(G)),
                reveal=dict(hit=reveal_hit(G), hit_t=reveal_hit_t(G), big=reveal_big(G), miss=REVEAL_MISS, fz=reveal_fz(G)),
                board=board_parts(), sfx=dict(SFX), assets=dict(ASSETS), t=dict(R=G.FZ_T['R']))


def bundle_js():
    """index.html に入れる形（<script> の中。文字列は JSON なので、コメント消しで消えない）"""
    s = json.dumps(bundle(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return 'window.__FX=' + s + ';'


if __name__ == '__main__':
    b = bundle()
    if len(sys.argv) > 1:
        json.dump(b, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print({k: (len(v) if isinstance(v, str) else {kk: len(vv) if isinstance(vv, str) else vv for kk, vv in v.items()}) for k, v in b.items()})
