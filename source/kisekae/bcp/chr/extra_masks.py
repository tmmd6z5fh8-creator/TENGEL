# キャラだけ 動かす（実験）：デザインの 設定（designs/*.json）が つかう 色の マスクを 作る（絵から 作る・絵は リポジトリに 入れない）
#   python3 extra_masks.py carry   → carry_ribbons_bg.png（背景の 印）・carry_ribbons_still.png（光の ふちにも 入れない）
#   python3 extra_masks.py wait    → wait1〜3_books_bg.png（左の 本：たてがみの 毛は のぞく）
#   python3 extra_masks.py next    → next1〜4_band.png（next_band.py：ボードの 下の 白い 帯）
#   python3 extra_masks.py toast   → toast_<段>_{T,B,bg,still}.png（toast_seeds.py）
#   出す 所：/home/claude/work/bcpic/chr（デザインの 設定に 書いて ある パス）
import sys, os, subprocess
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image
B_ = '/home/claude/work/bcpic'; O_ = '/home/claude/work/bcpic/chr'; H_ = os.path.dirname(os.path.abspath(__file__))
what = sys.argv[1] if len(sys.argv) > 1 else 'all'
def save(m, p): Image.fromarray((m.astype(np.uint8) * 255)).save(p); print(p, int(m.sum()))
if what in ('carry', 'all'):
    # 的中⑦ 馬が運ぶ：赤・青の リボン（馬の うしろ・まわりを 通る）は 動かさない。色で 見つけて、えらんだ かたまり だけ
    a = np.asarray(Image.open(f'{B_}/d7_1/clean.png').convert('RGB')).astype(np.int32); H, W = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 150) & (g < 90) & (b < 100) & (r - g > 90); blue = (b > 140) & (r < 90) & (b - r > 90)
    red[:730] = False; blue[:730] = False
    keepR = {'R0', 'R1', 'R3', 'R5', 'R10', 'R6', 'R7', 'R8', 'R14', 'R22', 'R15', 'R17', 'R2', 'R30', 'R33'}   # 大きい 順の 番号（馬の 体の 赤い 所は のぞく）
    keepB = {'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B8', 'B9'}
    rib = np.zeros((H, W), bool)
    for nm, m, keep in (('R', red, keepR), ('B', blue, keepB)):
        lab, n = ndi.label(ndi.binary_opening(m, iterations=1)); sz = ndi.sum(m, lab, range(1, n + 1)); k = 0
        for i in np.argsort(-sz):
            if sz[i] < 150: break
            if f'{nm}{k}' in keep: rib |= lab == (i + 1)
            k += 1
    rib = ndi.binary_closing(rib, iterations=2)
    save(ndi.binary_erosion(rib, iterations=3), f'{O_}/carry_ribbons_bg.png')
    save(ndi.binary_erosion(rib, iterations=1), f'{O_}/carry_ribbons_still.png')
if what in ('wait', 'all'):
    # ハズレ④ 結果待ち（1〜3回目）：左の 本の 山。たてがみ（赤茶の 毛・色が こい）と その まわり 3px は 本に しない
    poly = np.array([[0, 900], [230, 900], [230, 1100], [0, 1135]], np.int32)
    for d, nm in (('h4_1', 'wait1'), ('h4_2', 'wait2'), ('h4_3', 'wait3')):
        a = np.asarray(Image.open(f'{B_}/{d}/clean.png').convert('RGB')).astype(np.float32); H, W = a.shape[:2]
        mx = a.max(-1); mn = a.min(-1); sat = (mx - mn) / np.maximum(mx, 1)
        R = np.zeros((H, W), np.uint8); cv2.fillPoly(R, [poly], 1); R = R.astype(bool)
        warm = (a[..., 0] >= a[..., 1]) & (a[..., 0] >= a[..., 2])
        fur = (sat >= 0.8) & (mx <= 150) & warm & R
        body = np.zeros((H, W), bool); body[1100:1135, 60:230] = True
        lab, n = ndi.label(ndi.binary_closing(fur, iterations=1))
        keep = set(np.unique(lab[body & (lab > 0)])) - {0}
        mane = ndi.binary_fill_holes(np.isin(lab, list(keep)))
        near = ndi.binary_dilation(mane, iterations=3)
        bg = R & ~near
        low = np.zeros((H, W), bool); low[1100:1135, 0:62] = True
        bg[1100:, :] = False; bg |= (R & ~near & low)
        save(bg, f'{O_}/{nm}_books_bg.png')
if what in ('next', 'all'):
    for d, nm in (('h2', 'next1'), ('h2_2', 'next2'), ('h2_3', 'next3'), ('h2_4', 'next4')):
        subprocess.run(['python3', os.path.join(H_, 'next_band.py'), f'{B_}/{d}/clean.png', f'{O_}/{nm}_band.png'], check=True)
if what in ('toast', 'all'):
    # toast は 上の 馬の モデルの マスク（toast1/m_T.png）を つかう：先に run_design.py design_toast.json toast1 で 1回 切る
    subprocess.run(['python3', os.path.join(H_, 'toast_seeds.py')], check=True)
