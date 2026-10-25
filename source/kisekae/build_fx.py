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
   見本の /_blob/… の絵は、アプリの中のファイル（fz_nglow.webp・fz_ncore.webp）に置きかえる。
   第5弾（16.3 の 特別な 演出）：プレミアムど的中（pc・premium_cute.py）・超プレミアムど的中（zp・super_premium.py）・神様的中（gd・kami.py）・
     超神様的中（sgd・kami_super.py：動画）・超プレミアム神様的中（spg：超プレミアムの ①〜③ → 昇格の 動画 → 超神様の 動画）の CSS と 押したあとの HTML も 束ねる。
     絵（premium_blobs.json・kami_blobs.json の 名前.webp）・動画（sgd_film.mp4・spg_up.mp4）・さいごの 1まい（sgd_last.webp）・音 6こ も Resources に 入れる
     （build_fx_assets.py・build_fx_films.py で 手元に 作る）。動画は fx.js が <video> を 作って 舞台に 置く（art＝先に 読む 絵・films＝動画・t＝秒の きまり）"""
import json
import os
import re
import sys

K = os.path.dirname(os.path.abspath(__file__))
ASSETS = dict(nglow='fz_nglow.webp', ncore='fz_ncore.webp')
SFX = dict(hit_push='sfx_hit_push.m4a', hit='sfx_hit.m4a', big_push='sfx_big_push.m4a', big='sfx_big.m4a', fz_push='sfx_fz_push.m4a', fz='sfx_fz.m4a',
           pc='sfx_pc.m4a', zp='sfx_zp.m4a', gd='sfx_gd.m4a', sgd='sfx_sgd.m4a', spg_up='sfx_spg_up.m4a', spg='sfx_spg.m4a')   # 第5弾：特別な 演出の 音 6こ（16.5）
FILMS = dict(sgd_film='sgd_film.mp4', spg_up='spg_up.mp4')      # 第5弾：超神様の 動画（超神様的中・超プレミアム神様的中で 同じ）・昇格の 動画（15章）
STILL = dict(sgd_last='sgd_last.webp')                           # 超神様の 動画の さいごの 1まい（視差効果を減らす 時・動画が 動かない 時）


def blob_names():
    """見本の 絵の 名前（premium_blobs.json・kami_blobs.json）→ {名前: id}"""
    out = {}
    for fn in ('premium_blobs.json', 'kami_blobs.json'):
        out.update(json.load(open(os.path.join(K, fn), encoding='utf-8')))
    return out


ART = dict(pm=sorted(n + '.webp' for n in json.load(open(os.path.join(K, 'premium_blobs.json'), encoding='utf-8'))),     # プレミアムど的中の 絵 38まい（約2.1MB）
           gd=sorted(n + '.webp' for n in json.load(open(os.path.join(K, 'kami_blobs.json'), encoding='utf-8'))),        # 神様的中の 絵 24まい（約1.7MB）
           sgd=[STILL['sgd_last']])
ART_FILES = sorted(set(ART['pm'] + ART['gd'] + ART['sgd']))
ASSET_FILES = sorted(ASSETS.values()) + sorted(SFX.values()) + ART_FILES + sorted(FILMS.values())


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


def kf_names(css):
    """CSS の @keyframes の 名前（@media の 中も）"""
    names = set()

    def collect(rs):
        for sel, body in rs:
            if sel.startswith('@keyframes'):
                names.add(sel.split()[1])
            elif sel.startswith('@media'):
                collect(split_rules(body))
    collect(split_rules(css))
    return names


def rename_inline(html, names, kf='fx'):
    """HTML の style="animation:…" の 中の @keyframes の 名前にも kf を 付ける（見本の 押したあとは 行ごとに 秒を 入れた inline の animation が 多い）"""
    def fix_style(m):
        st = m.group(1)

        def fix(mm):
            segs = []
            for seg in split_top(mm.group(2), ','):
                toks = seg.strip().split(None, 1)
                if toks and toks[0] in names:
                    toks[0] = kf + toks[0]
                segs.append(' '.join(toks))
            return mm.group(1) + ','.join(segs)
        st = re.sub(r'(animation(?:-name)?\s*:)([^;"]*)', fix, st)
        return f'style="{st}"'
    return re.sub(r'style="([^"]*)"', fix_style, html)


# ---------------------------------------------------------------- アプリ用の足し
# 舞台：画面のまん中に 390×844 を置いて、縦横の比を変えずに画面に入る大きさにする（--fxk は fx.js が決める：16.3「画面の大きさ」※仮）
# 的中（k-hit）の ボードの まわりも デカ的中と 同じ 暗さ（2026/10/25 まさちゃん「的中の結果ボードの背景がおかしい。デカ的中以降の結果ボードの背景と形合わせて！」）
STAGE_CSS = r'''
#fxOv{position:fixed;inset:0;z-index:80;background:var(--fxbd,rgba(24,14,4,.62));overflow:hidden;touch-action:none;-webkit-user-select:none;user-select:none}
#fxOv.rv.k-hit,#fxOv.rv.k-big,#fxOv.rv.k-hidden{--fxbd:rgba(6,4,18,.86)}
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


def push_big_t(G):
    """デカ的中（と 隠れど的中）の PUSH の 画面：壁紙の テーマの PUSH（{{PBOX}}＝fx.js が そのテーマの PUSH・影・「タップ！」を 入れて、.pbox を --pz 倍に）
       第4.60版・まさちゃん「的中ボタン以降も壁紙のテーマにあったpushボタンで作成して！」。まわり（暗さ・きらめき）は デカ的中の まま"""
    return f'''<div class="ov big">
  <div class="dim"></div>
  <div class="spk">{G.sparkles(22, 5)}</div>
  <div class="pbox pz">{{{{PBOX}}}}</div>
</div>'''


def push_fz(G):
    h = G.fz_push().replace('onClick="{{toReveal}}"', 'data-fx="tap"')
    assert 'data-fx="tap"' in h and '{{' not in h
    return f'<div class="ov fz">\n    {h}\n  </div>'


def push_fz_t(G):
    """ど的中・特別な 演出（プレミアム〜超プレミアム神様）の PUSH の 画面：壁紙の テーマの PUSH（{{PBOX}}）。まわり（暗さ・虹の 光・光の すじ・ふち・わく・きらめき）は ど的中の まま。
       ど的中は 的中より 一回り 大きく（--pz）、それより 上は もう一回り 大きく 虹色（.rbw：fx.js が つける）"""
    h = G.fz_push().replace('onClick="{{toReveal}}"', 'data-fx="tap"')
    h2 = re.sub(r'<div class="pbox">[\s\S]*?<p class="tap fz">タップ!!</p>\s*</div>', '<div class="pbox pz">{{PBOX}}</div>', h)
    assert h2 != h and '{{PBOX}}' in h2 and 'class="push fz"' not in h2 and '.pbox' not in h2
    return f'<div class="ov fz">\n    {h2}\n  </div>'


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
    <div class="pzw" style="--pz:{{{{PZ}}}}"><div class="pressed{{{{PC}}}}">{{{{PRESSED}}}}</div>{{{{BURST}}}}</div>
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


# ---------------------------------------------------------------- 第5弾：特別な 演出の 押したあと（16.3）。ボードは {{BOARD}}（fx.js が そのテーマの ど的中の ボードを 入れる）
def reveal_pc(G):
    """プレミアムど的中（かわいいど的中）：premium_cute.py の pc_layers（絵は pm_….webp）"""
    return f'''<div class="ov fz pm" style="--n:{{{{N}}}}">
    {G.PC.pc_layers('{{BOARD}}')}
    {CLOSE}
  </div>'''


def reveal_zp(G):
    """超プレミアムど的中（手書き・鉛筆）：super_premium.py の zp_layers（絵なし）"""
    return f'''<div class="ov fz zp" style="--n:{{{{N}}}}">
    {G.SP.zp_layers('{{BOARD}}')}
    {CLOSE}
  </div>'''


def reveal_gd(G):
    """神様的中：kami.py の gd_layers（絵は gd_….webp）"""
    return f'''<div class="ov fz gd" style="--n:{{{{N}}}}">
    {G.GD.gd_layers('{{BOARD}}')}
    {CLOSE}
  </div>'''


def reveal_sgd(G):
    """超神様的中：kami_super.py の sgd_layers（動画 <video class="sgv"> は fx.js が 舞台に 置く。go＝動画が 動きだした・still＝さいごの 1まい）"""
    return f'''<div class="ov fz sgd" style="--n:{{{{N}}}}">
    {G.SG.sgd_layers('{{BOARD}}', STILL['sgd_last'])}
    {CLOSE}
  </div>'''


def reveal_spg(G):
    """超プレミアム神様的中：超プレミアムど的中の ①〜③（spz：き！で stop → 昇格の 動画が 動きだしたら gone）＋ 超神様（spg）。動画 2つ（spu・sgv）は fx.js が 舞台に 置く"""
    return f'''<div class="ov fz zp spz">
    {G.SP.zp_layers('', upto=3, sr=G.SG.SPG_SR)}
  </div>
  <div class="ov fz sgd spg" style="--n:{{{{N}}}}">
    {G.SG.sgd_layers('{{BOARD}}', STILL['sgd_last'], sr=G.SG.SPG_SR)}
    {CLOSE}
  </div>'''


def blob_files(G):
    """見本の /_blob/<id> → アプリの 中の ファイル名"""
    m = {G.blobs[k]: v for k, v in (('fz_nglow', ASSETS['nglow']), ('fz_ncore', ASSETS['ncore']), ('sgd_last', STILL['sgd_last']))}
    m.update({G.blobs[k]: v for k, v in FILMS.items()})
    m.update({bid: name + '.webp' for name, bid in blob_names().items()})
    return m


def deblob(text, G, what):
    for bid, name in blob_files(G).items():
        text = text.replace('/_blob/' + bid, name)
    assert '/_blob/' not in text, f'{what}：見本の絵が残っているよ'
    return text


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
    # 第5弾：特別な 演出（16.3）。動画の 入れもの .ph .sgv／.ph .spu は 舞台（.fxs）の 中の .sgv／.spu に
    css += G.PC.pc_css() + G.SP.zp_css() + G.GD.gd_css() + G.SG.sgd_css().replace('.ph .sgv', '.sgv') + G.SG.spg_css().replace('.ph .spu', '.spu')
    assert '.ph ' not in css, '見本の ページの 入れもの（.ph）が 残っているよ'
    # 見本の絵（キャンバスの /_blob/…）→ アプリの中のファイル
    for key in ('fz_nglow', 'fz_ncore'):
        assert '/_blob/' + G.blobs[key] in css, key
    css = deblob(css, G, 'css')
    out = scope(css)
    # 選択子に付けた .fxs は、舞台そのもの（.fxs{…}）にも付いてしまう → 舞台の変数の行だけ直す
    out = out.replace('.fxs .fxs{', '.fxs{')
    return STAGE_CSS + out, kf_names(css)


def bundle():
    G = load_gen_fx()
    css, names = css_all(G)
    fx5 = {k: deblob(rename_inline(fn(G), names), G, k) for k, fn in (('pc', reveal_pc), ('zp', reveal_zp), ('gd', reveal_gd), ('sgd', reveal_sgd), ('spg', reveal_spg))}
    for k, h in fx5.items():
        assert '{{BOARD}}' in h and '{{N}}' in h and 'data-fx="close"' in h, k
    SG = G.SG
    return dict(css=css, push=dict(hit=PUSH_HIT, hit_t=PUSH_HIT_T, big=push_big(G), big_t=push_big_t(G), fz=push_fz(G), fz_t=push_fz_t(G)),
                reveal=dict(hit=reveal_hit(G), hit_t=reveal_hit_t(G), big=reveal_big(G), miss=REVEAL_MISS, fz=reveal_fz(G), **fx5),
                board=board_parts(), sfx=dict(SFX), assets=dict(ASSETS), art=dict(ART), films=dict(FILMS),
                t=dict(R=G.FZ_T['R'], PC=G.PC.PC_T['RES'], GD=G.GD.GD_T['RES'],
                       SG=dict(FILM=round(SG.FILM, 4), RES=round(SG.RES, 4), STILL_FROM=round(SG.STILL_FROM, 4), STILL_WAIT=SG.STILL_WAIT, STILL_BOARD=round(SG.STILL_BOARD, 4),
                               UP_AT=SG.UP_AT, UP=round(SG.UP, 4), SPG_FILM=round(SG.SPG_FILM, 4), WAIT_MAX=SG.WAIT_MAX)))


def bundle_js():
    """index.html に入れる形（<script> の中。文字列は JSON なので、コメント消しで消えない）"""
    s = json.dumps(bundle(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return 'window.__FX=' + s + ';'


if __name__ == '__main__':
    b = bundle()
    if len(sys.argv) > 1:
        json.dump(b, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print({k: (len(v) if isinstance(v, str) else {kk: len(vv) if isinstance(vv, str) else vv for kk, vv in v.items()}) for k, v in b.items()})
