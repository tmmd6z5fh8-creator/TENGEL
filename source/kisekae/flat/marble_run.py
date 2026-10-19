"""大理石の壁紙の動き（まさちゃんの指定「1〜2でゆっくり向きを逆向きへ振り向き（馬の首で逆方向を２度見、3秒で一気に逆向きへ振り向く、
   8秒に一度リピートで繰り返す」）：動く絵のコマ
   - いまの絵（flat/marble_banner.py）と同じ場面・同じカメラ・同じ光・同じ乱数で、像の馬を 3D のまま動かして描く：
       ふり向き（look）… 首と頭を、首の根元を通る たての軸のまわりに うしろへ まわす（頭は ぜんぶ・首は 根元から うなじへ だんだん：
                          marble_horse.Look）。左向きの像は こちら（カメラ）がわを通って 右へ（＋）、右向きの像は 左へ（−）
       くるっと（psi）… 像（馬と岩）を 台のまん中の たての軸のまわりに まわす（marble_horse.Spin）。左向き psi=0 → 右向き psi=PSI_R
                          （上から見て 16°こちらを向いた像が、こちらを向きながら回って、右向きで 16°こちらを向く）。
                          頭は先に うしろを見ているので、体が回るあいだ 頭の向きは ほとんど そのまま（look を psi と反対に もどす）
   - コマ（FRAMES）：A＝左向きの ふり向き（look 0 → LOOK・さいごに 少し行きすぎ LOOK_OVER）／B＝左 → 右（体が回る）／
                     C＝右向きの ふり向き（look 0 → −LOOK・−LOOK_OVER）／D＝右 → 左。A0 は いまの絵と 1画素もちがわない
   - 像と台のまわりだけ 切りぬいた コマ（背景ごと・不透明）を シート1まい（よこ COLS）にする（ロスあり）。ページで コマを めくる（kisekae/marble_wall.py）
   python3 flat/marble_run.py <出力フォルダ>  → marble_frames.webp・marble_run.json
   （sdfr がいる・1コマ 約12秒。描いたコマは <出力フォルダ>/cache に のこして 2回目は描かない）"""
import sys, os, json
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import marble_banner as MB

LOOK, LOOK_OVER, PSI_R = 150.0, 160.0, 148.0    # ふり向く角度・2度見で 少し行きすぎる角度・右向きの psi
N_LOOK, N_TURN = 12, 12                          # ふり向き（0 → LOOK）・体が回る の きざみ
RX1 = 600                                        # 描く範囲の右のはし（左は 0 から：いまの絵と同じ乱数になるように 行の はじめから描く）
COLS = 10                                        # シートの よこの コマ数
MARGIN = 6                                       # 切りぬきの よゆう（画素）
Q = 90                                           # シートの ロスありの質


def frame_list():
    """[(名前, psi, look)]：A・B・C・D の じゅん"""
    out = [(f'A{k:02d}', 0.0, LOOK * k / N_LOOK) for k in range(N_LOOK + 1)] + [(f'A{N_LOOK + 1:02d}', 0.0, LOOK_OVER)]
    out += [(f'B{k:02d}', PSI_R * k / N_TURN, LOOK * (1 - k / N_TURN)) for k in range(1, N_TURN)]
    out += [(f'C{k:02d}', PSI_R, -LOOK * k / N_LOOK) for k in range(N_LOOK + 1)] + [(f'C{N_LOOK + 1:02d}', PSI_R, -LOOK_OVER)]
    out += [(f'D{k:02d}', PSI_R * (1 - k / N_TURN), -LOOK * (1 - k / N_TURN)) for k in range(1, N_TURN)]
    return out


def render_frames(cache, names=None):
    """コマを描いて cache に（<名前>.png：絵の 0〜RX1・ロスなし／<名前>.json：像と台の はんい）。もう あるコマは描かない"""
    todo = [f for f in frame_list() if (names is None or f[0] in names) and not os.path.exists(os.path.join(cache, f[0] + '.png'))]
    if not todo:
        return
    cam = MB.camera()
    bg = MB.background()
    try:
        for name, psi, look in todo:
            sc = MB.scene(cam, ss=2, rect=(0, 0, RX1, MB.Hh), psi=psi, look=look)
            R = MB.render(sc, f'run{os.getpid()}')
            img = MB.compose(bg.copy(), R, sc, cam)
            u8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)[:, :RX1]
            ys, xs = np.nonzero(R['a'][:, :RX1] > 0)
            cv2.imwrite(os.path.join(cache, name + '.png'), cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
            json.dump(dict(psi=psi, look=look, box=[int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]),
                      open(os.path.join(cache, name + '.json'), 'w'))
            print(name, psi, round(look, 1), flush=True)
    finally:
        MB.cleanup()


def build_sheet(out_dir, cache):
    fl = frame_list()
    boxes = [json.load(open(os.path.join(cache, n + '.json')))['box'] for n, _, _ in fl]
    x0 = min(b[0] for b in boxes) - MARGIN
    y0 = max(0, min(b[1] for b in boxes) - MARGIN)
    x1 = max(b[2] for b in boxes) + MARGIN
    y1 = min(MB.Hh, max(b[3] for b in boxes) + MARGIN)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2                            # 2倍の絵 → ページの画素が 整数になるように
    x1, y1 = x1 + x1 % 2, y1 + y1 % 2
    assert x1 <= RX1, (x1, RX1)
    fw, fh = x1 - x0, y1 - y0
    rows = (len(fl) + COLS - 1) // COLS
    sheet = np.zeros((rows * fh, COLS * fw, 3), np.uint8)
    for i, (n, _, _) in enumerate(fl):
        im = cv2.imread(os.path.join(cache, n + '.png'))
        r, c = divmod(i, COLS)
        sheet[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw] = im[y0:y1, x0:x1]
    cv2.imwrite(os.path.join(out_dir, 'marble_frames.webp'), sheet, [cv2.IMWRITE_WEBP_QUALITY, Q])
    meta = dict(size=[MB.W, MB.Hh], crop=[x0, y0, x1, y1], frame=[fw, fh], cols=COLS, rows=rows,
                frames=[n for n, _, _ in fl], psi=[round(p, 3) for _, p, _ in fl], look=[round(l, 3) for _, _, l in fl],
                LOOK=LOOK, LOOK_OVER=LOOK_OVER, PSI_R=PSI_R, N_LOOK=N_LOOK, N_TURN=N_TURN)
    json.dump(meta, open(os.path.join(out_dir, 'marble_run.json'), 'w'), ensure_ascii=False, indent=1)
    return meta


if __name__ == '__main__':
    out = sys.argv[1]
    cache = os.path.join(out, 'cache')
    os.makedirs(cache, exist_ok=True)
    render_frames(cache, set(sys.argv[2:]) or None)
    if not sys.argv[2:]:
        m = build_sheet(out, cache)
        print('crop', m['crop'], 'frame', m['frame'], 'sheet', m['cols'], 'x', m['rows'])
