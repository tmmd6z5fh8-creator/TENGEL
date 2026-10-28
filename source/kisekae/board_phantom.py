"""結果ボードカスタム「出世馬」の 8回目からの 幻の 馬（第4.91版）：3Dの 馬（horse3d の 立ち上がる 形）を 描いて、
   形（体・たてがみと しっぽ・光の 当たる 所・かげ）を SVG の 線に して、bcx_phantom.js（window.TengelBoardPhantom）に 書く。
   形は すべて 一から 作った オリジナル（このリポジトリの 3Dの 馬）。絵の ファイルは 使わない（SVG なので 絵なしの CI でも 出る）。
     python3 kisekae/board_phantom.py [出力.js] [--png 確かめる.png]"""
import sys, os, json, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'r3d'))
import style2d as S2
from style2d import frame_horse, render_horse, mane_tail
import horse3d as Hm

W, H = 720, 900
BOX = (60, 40, 660, 860)


def pose():
    p = dict(Hm.REAR)
    p['fore'] = dict(L=[-62, 30, -96, -136], R=[-80, 10, -112, -152])   # 前足を 高く かかげる
    p['neck_rot'] = -50.0
    p['head_ang'] = -18.0                                                 # 頭を 上へ（ほえる）
    p['tail'] = [-118, -104]
    return p


def contour_path(mask, eps=0.9, min_area=60):
    """0/1 の 形 → SVG の d（外の ふちと 穴）"""
    m = (mask > 0.5).astype(np.uint8)
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < min_area:
            continue
        a = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        if len(a) < 3:
            continue
        out.append('M' + ' '.join(f'{int(x)} {int(y)}' for x, y in a) + 'Z')
    return ''.join(out)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else os.path.join(HERE, '..', 'bcx_phantom.js')
    png = sys.argv[sys.argv.index('--png') + 1] if '--png' in sys.argv else None
    tmp = os.path.join(S2.TMP, f'ph{os.getpid()}'); os.makedirs(tmp, exist_ok=True); S2.TMP = tmp
    P = pose()
    e, t = frame_horse(P, BOX, W, H, facing='left', azim=-10, elev=6)
    R = render_horse(P, e, t, 26, W, H, ss=2, name='ph')
    A = np.clip(R['a'], 0, 1)
    hair, ha = mane_tail(R, (H, W), '#FFFFFF', '#DDDDDD', mode='flow', scale=1.5, seed=11, tail_len=1.25, mane_len=1.15, wind_ang=0.25)
    body = A > 0.5
    allm = np.maximum(A, ha) > 0.5
    # 光：左上から（向きは 左）。法線で 光の 当たる 所と かげ
    n = R['n']
    L = np.array([-0.55, 0.65, 0.52]); L /= np.linalg.norm(L)
    lit = np.sum(n * L, -1)
    lit = cv2.GaussianBlur((lit * A).astype(np.float32), (0, 0), 3) / np.maximum(cv2.GaussianBlur(A.astype(np.float32), (0, 0), 3), 1e-3)
    hi = body & (lit > 0.55)
    sh = body & (lit < 0.05)
    k = 1000 / H                                                        # 座標は 高さ 1000 に
    sc = lambda m: cv2.resize(m.astype(np.uint8) * 255, (int(W * k), 1000), interpolation=cv2.INTER_LINEAR) > 127
    d = dict(w=int(W * k), h=1000,
             all=contour_path(sc(allm), 1.1), body=contour_path(sc(body), 1.1), hair=contour_path(sc(ha > 0.5), 1.1),
             hi=contour_path(sc(hi), 1.6, 300), sh=contour_path(sc(sh), 1.6, 300),
             eye=[round(float(R['eye'][0] * k), 1), round(float(R['eye'][1] * k), 1)], muzzle=[round(float(R['muzzle'][0] * k), 1), round(float(R['muzzle'][1] * k), 1)],
             poll=[round(float(R['poll'][0] * k), 1), round(float(R['poll'][1] * k), 1)],
             crest=[[round(float(x * k), 1), round(float(y * k), 1)] for x, y in np.asarray(R['crest'])[::3]],      # 首の 上の 線（たてがみの 炎を 出す 所）
             tail=[[round(float(x * k), 1), round(float(y * k), 1)] for x, y in np.asarray(R['tail'])])             # しっぽの 根元から
    js = ('// 結果ボードカスタム「出世馬」の 幻の 馬の 形（kisekae/board_phantom.py で 作る：3Dの 馬を SVG の 線に したもの・オリジナル）\n'
          '(function (root) { root.TengelBoardPhantom = ' + json.dumps(d, separators=(',', ':')) + '; })(typeof window !== \'undefined\' ? window : globalThis);\n')
    open(out, 'w', encoding='utf-8').write(js)
    print(out, len(js), {k2: len(v) for k2, v in d.items() if isinstance(v, str)}, d['eye'], d['muzzle'])
    if png:
        img = np.zeros((H, W, 3), np.uint8) + 30
        img[allm] = (90, 70, 160); img[body] = (150, 120, 230); img[hi] = (220, 210, 255); img[sh] = (70, 50, 130)
        cv2.circle(img, (int(R['eye'][0]), int(R['eye'][1])), 6, (0, 255, 255), -1)
        cv2.imwrite(png, img)


if __name__ == '__main__':
    main()
