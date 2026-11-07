# 動く 絵の ボード（第4.129版）：キャラが 動く 絵（chr_stage.py の 出力）を アプリの 止まった 絵（bcp_<名前>.webp・_fg.webp）に そろえる
#   python3 chr_snap.py <絵の フォルダ（ios/bcp_assets）> [名前,…]     … その フォルダに 動く 絵を 書く（もとは CHR_STAGE の 絵＝何回 やっても 同じ）
#   止まって いる 形（キャラが 動きだす 前）が 止まった 絵と 同じに なるように、下から じゅんに 重ねながら 色を きめる：
#   ・キャラなしの 背景（bgx）：キャラの ない 所と 絵の 外（床に うつる 所・上の 光）は 止まった 絵（前の 絵の 下に なる 色）
#   ・前の 絵（fgx）：キャラの ない 所は 止まった 前の 絵の 色
#   ・キャラ・動かない 物（oc・ot）・キャラの 前の 所（f）：下に 重なった 絵の 上で 止まった 絵に なる 色
#     （やわらかい ふちも：色 F・こさ a で a·F＋(1−a)·下 ＝ 止まった 絵。色が 0〜1 に おさまらない 所だけ こさを 上げる）
#     キャラは 元の 絵の まま の 所（かくれた 所を のばした 色で ない 所）だけ そろえる
#   → bcp_bg.py が 絵の 下の はしを 暗く する 所・床に うつる 所・絵の 圧縮の ちがいも 同じに なる（キャラが 動きだす とき 絵が かわって 見えない）
#   見つける もの：chr の 出力（CHR_WORK＝/home/claude/work/bcpic/chr の */cfg.json と motion.json・名前が 同じ もの）
#                 そろえる 前の 動く 絵（CHR_STAGE＝CHR_WORK/stage：chr_stage.py の 出力。ない ときは 絵の フォルダの もの）
#   SNAP_Q：画質（背景 88・ほか 90 が 基本＝止まった 絵と 同じ）・SNAP_DRY=1：書かずに ずれだけ 出す
import glob, json, os, sys
import numpy as np, cv2
from PIL import Image
from multiprocessing import Pool
H_ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H_)); import bcp_app as B
A = sys.argv[1]; only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
WORK = os.environ.get('CHR_WORK', '/home/claude/work/bcpic/chr')
SRC = os.environ.get('CHR_STAGE', os.path.join(WORK, 'stage'))
QB = int(os.environ.get('SNAP_QB', '88')); Q = int(os.environ.get('SNAP_Q', '90'))
DRY = os.environ.get('SNAP_DRY') == '1'
K = 3; Wc, Hc = 390 * K, 844 * K


def cut_of():
    out = {}
    for cf in glob.glob(os.path.join(WORK, '*', 'cfg.json')):
        O = os.path.dirname(cf)
        if not os.path.exists(os.path.join(O, 'motion.json')):
            continue
        c = json.load(open(cf, encoding='utf8'))
        cl = c.get('clean', '')
        d = os.path.dirname(c.get('board', {}).get('fgmask', '')) if cl.endswith('src_fg.png') else os.path.dirname(cl)
        if not d or not os.path.exists(os.path.join(d, 'cfg.json')):
            continue
        n = json.load(open(os.path.join(d, 'cfg.json'), encoding='utf8'))['name']
        t = os.path.getmtime(os.path.join(O, 'motion.json'))
        if n not in out or out[n][0] < t:
            out[n] = (t, O, d, c)
    return out


def rgba(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.float32) / 255


def src_of(f):
    p = os.path.join(SRC, f)
    return p if os.path.exists(p) else os.path.join(A, f)


def save(f, a, q):
    if not DRY:
        Image.fromarray(np.clip(a * 255 + .5, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(A, f), quality=q, method=6)


def over(C, F, a):
    return F * a[..., None] + C * (1 - a[..., None])


def solve(F, a, U, T, m):
    # 下の 絵 U の 上で T に なる 色・こさ（こさは 上げる だけ・こさ 0 の 所は そのまま）。m：そろえる 重み（0〜1）
    d = T - U
    need = np.maximum(np.where(d > 0, d / np.maximum(1 - U, 1e-4), 0), np.where(d < 0, -d / np.maximum(U, 1e-4), 0)).max(-1)
    a2 = np.where(a > 0, np.maximum(a, np.minimum(need, 1)), 0)
    F2 = np.clip(U + d / np.maximum(a2, 1e-4)[..., None], 0, 1)
    F2 = np.where(a2[..., None] > 0, F2, F)
    return F2 * m[..., None] + F * (1 - m[..., None]), a2 * m + a * (1 - m)


def one(name):
    mo = B.MOTION[name]
    _, O, D, c = CUT[name]
    g = json.load(open(os.path.join(D, 'geom.json')))
    S, OX, OY = g['S'], g['OX'], g['OY']
    Mx = np.array([[S * K, 0, OX * K], [0, S * K, OY * K]], np.float32)
    img = np.asarray(Image.open(c['clean']).convert('RGB')).astype(np.int16)
    stb = rgba(os.path.join(A, f'bcp_{name}.webp'))[..., :3]
    fgp = os.path.join(A, f'bcp_{name}_fg.webp')
    stf = rgba(fgp) if os.path.exists(fgp) else None
    comp = stb.copy() if stf is None else over(stb, stf[..., :3], stf[..., 3])
    # 絵の ある 行（bcp_bg.py と 同じ）：その 外は 止まった 絵（床に うつる 所・上の 光）
    dcfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
    ph = Image.open(os.path.join(D, dcfg.get('src', 'src.png'))).size[1]
    ct, cb = dcfg.get('crop', [0, ph])
    top = max(0, int(np.ceil((OY + ct * S) * K))); bot = min(Hc, int(np.floor((OY + cb * S) * K)))
    # キャラの ない 所（元の 絵の まま の 所）：u＝1
    bgx_cut = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.int16)
    U0 = (np.abs(bgx_cut - img).max(-1) == 0).astype(np.float32)
    u = cv2.warpAffine(U0, Mx, (Wc, Hc), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=1)
    u[:top] = 1; u[bot:] = 1
    u = np.clip((u - .5) * 2, 0, 1)                       # キャラの そばは のばした 色の まま（動いた とき 元の キャラが 見えない）
    # 1) 前の 絵（アプリで つかう もの：fgx か 止まった 前の 絵）
    if stf is not None and mo.get('fgx'):
        fx = rgba(src_of(mo['fgx']))
        fx[..., :3] = over(fx[..., :3], stf[..., :3], u)
        save(mo['fgx'], fx, Q)
    else:
        fx = stf
    # 前の 絵の 下に なる 所の 目あて：前の 絵を 重ねて ちょうど 止まった 絵（前の 絵が こい 所は 止まった 背景）
    if fx is not None:
        fa = fx[..., 3:4]
        Tb = np.where(fa < .98, (comp - fx[..., :3] * fa) / np.maximum(1 - fa, 1e-4), stb)
        Tb = np.clip(Tb, 0, 1)
    else:
        Tb = comp
    # 2) キャラなしの 背景
    bx = rgba(src_of(mo['bgx']))
    bx[..., :3] = over(bx[..., :3], Tb, u); bx[..., 3] = 1
    save(mo['bgx'], bx, QB)
    C = bx[..., :3].copy()
    # 3) 下から じゅんに 重ねて そろえる（アプリと 同じ じゅん：bcx.js の picMotion）
    parts = json.load(open(os.path.join(O, 'motion.json'), encoding='utf8'))['parts']
    L = mo['layers']
    assert len(parts) == len(L), (name, len(parts), len(L))
    orig = {}

    def orig_w(i):
        if i not in orig:
            P = np.asarray(Image.open(os.path.join(O, parts[i]['id'] + '.png')).convert('RGBA')).astype(np.int16)
            o_ = (np.abs(P[..., :3] - img).max(-1) == 0).astype(np.float32)
            w = cv2.warpAffine(o_, Mx, (Wc, Hc), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            orig[i] = np.clip((w - .5) * 2, 0, 1)
        return orig[i]
    st = {'raise>.1': 0, 'raise>.3': 0}

    def put(f, box, T, m, q):
        x = rgba(src_of(f))
        x0, y0, bw, bh = [int(round(v * K)) for v in box]
        assert x.shape[:2] == (bh, bw), (name, f, x.shape, (bh, bw))
        Ub = C[y0:y0 + bh, x0:x0 + bw]
        F, a = solve(x[..., :3], x[..., 3], Ub, T[y0:y0 + bh, x0:x0 + bw], m[y0:y0 + bh, x0:x0 + bw])
        r = a - x[..., 3]; st['raise>.1'] += int((r > .1).sum()); st['raise>.3'] += int((r > .3).sum())
        x[..., :3] = F; x[..., 3] = a
        save(f, x, q)
        C[y0:y0 + bh, x0:x0 + bw] = over(Ub, F, a)
    one_ = np.ones((Hc, Wc), np.float32)
    if not mo.get('top'):
        for i, l in enumerate(L):
            put(l['src'], l['box'], Tb, orig_w(i), Q)
    if mo.get('oc'):
        put(mo['oc']['src'], mo['oc']['box'], Tb, one_, Q)
    if fx is not None:
        C[:] = over(C, fx[..., :3], fx[..., 3])
    if mo.get('top'):
        for i, l in enumerate(L):
            put(l['src'], l['box'], comp, orig_w(i), Q)
    for i, l in enumerate(L):
        if l.get('f'):
            put(l['f'], l['box'], comp, orig_w(i), Q)
    if mo.get('ot'):
        put(mo['ot']['src'], mo['ot']['box'], comp, one_, Q)
    d = np.abs(C - comp).max(-1) * 255
    return f"snap {name} parts {len(L)} rows {top} {bot} | ずれ p99.9 {np.percentile(d, 99.9):.1f} max {d.max():.1f} >10 {int((d > 10).sum())} >30 {int((d > 30).sum())} | こさを 上げた {st['raise>.1']}（.3以上 {st['raise>.3']}）"


CUT = cut_of()
if __name__ == '__main__':
    names = [n for n, mo in B.MOTION.items() if (not only or n in only) and not (mo.get('amb') and not mo['layers'])]   # まわりの 光と 雲：止まった 絵の まま
    with Pool(int(os.environ.get('SNAP_J', str(os.cpu_count() or 1)))) as P:
        for s in P.imap(one, names):
            print(s, flush=True)
