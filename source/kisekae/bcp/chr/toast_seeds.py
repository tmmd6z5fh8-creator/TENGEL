# 祝杯（toast）：4つの 段で 色が かわらない 所＝馬（印）・大きく かわる 所＝光・ボードの ふち（背景の 印）
#   段2・段3 は 絵が 2px 下に ずれて いる（高さ 1501）：そろえて くらべ、印も 段ごとに ずらして 出す
import numpy as np, cv2, json
import scipy.ndimage as ndi
from PIL import Image
B_ = '/home/claude/work/bcpic'; O_ = '/home/claude/work/bcpic/chr'
names = ['d2_1', 'd2_2', 'd2', 'd2_4']; shift = {'d2_1': 0, 'd2_2': 2, 'd2': 2, 'd2_4': 0}
ref = np.asarray(Image.open(f'{B_}/d2_1/clean.png').convert('RGB')).astype(np.float32); H, W = ref.shape[:2]
al = []
for d in names:
    a = np.asarray(Image.open(f'{B_}/{d}/clean.png').convert('RGB')).astype(np.float32); s = shift[d]
    al.append(a[s:s + H])
D = np.zeros((H, W), np.float32)
for i in range(4):
    for j in range(i + 1, 4): D = np.maximum(D, np.abs(al[i] - al[j]).max(-1))
Ds = cv2.GaussianBlur(D, (0, 0), 1.5)
r, g, b = ref[..., 0], ref[..., 1], ref[..., 2]
yel = (r > 200) & (g > 170) & (b < 140) & (r - b > 90)
yel = ndi.binary_opening(yel, iterations=2); lab, n = ndi.label(yel); sz = ndi.sum(yel, lab, range(1, n + 1))
yel = np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 300])
yy, xx = np.mgrid[0:H, 0:W]
q = np.array([[150, 386], [940, 419], [922, 943], [83, 891]], np.int32); bm = np.zeros((H, W), np.uint8); cv2.fillPoly(bm, [q], 1)
board = cv2.erode(bm, np.ones((31, 31), np.uint8)).astype(bool)          # 板の 中（ふちは のぞく）
cool = np.zeros((H, W), bool)                                                # ボードの ふちの 紺・灰（どれか 1つの 段で 紺・灰なら ふち：馬の 毛は どの 段でも 茶色）
for a_ in al: cool |= ((a_[..., 2] - a_[..., 0] > 5) & (a_.max(-1) < 120)) | ((a_[..., 2] - a_[..., 0] > 30) & (a_.max(-1) < 200))   # 紺・灰・青い 線
cool &= (yy > 820) & (yy < 1040)
lo = ndi.binary_erosion(Ds < 28, iterations=3) & ~cv2.dilate(yel.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~board
lo &= ~cv2.dilate(cool.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
head = ((xx - 520) / 230.0) ** 2 + ((yy - 235) / 200.0) ** 2 <= 1
# 上の 馬：モデルの マスク（toast1/m_T.png・はっきり 切れて いる）で 毛・たてがみも 印に
MT = np.asarray(Image.open(f'{O_}/toast1/m_T.png').convert('L')).astype(np.float32)[:H] / 255
tarea = np.zeros((H, W), bool); tarea[0:440, 260:800] = True
T = (lo & head & (yy < 410)) | (ndi.binary_erosion(MT > 0.5, iterations=4) & (yy < 372) & tarea) | (ndi.binary_erosion(MT > 0.22, iterations=1) & (yy < 320) & tarea)   # 毛の ふち線まで
Bm = lo & (yy > 860) & (yy < 1205)
for m_ in (T, Bm):
    lab, n = ndi.label(m_); sz = ndi.sum(m_, lab, range(1, n + 1)); m_[:] = np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 120])
# 下の 馬の 耳（光で 色が かわる＝色の くらべでは 見つからない）：手で 印を おいて、まわりは 背景の 印に しない
EARS = [  # (守る 形, 印の 線, 太さ)
    ([[12, 862], [30, 858], [50, 880], [62, 930], [60, 962], [40, 968], [15, 958], [8, 915]], [[30, 882], [40, 950]], 6),
    ([[150, 925], [165, 880], [180, 872], [192, 900], [192, 950], [160, 962]], [[172, 892], [178, 945]], 5),
    ([[186, 935], [195, 925], [215, 948], [228, 990], [205, 1000], [188, 980]], [[198, 945], [210, 988]], 5),
    ([[325, 960], [340, 935], [355, 945], [362, 1000], [335, 1000]], [[345, 952], [350, 992]], 4),
    ([[392, 960], [402, 948], [425, 958], [445, 995], [440, 1012], [400, 1012]], [[408, 966], [425, 1002]], 6),
    ([[560, 955], [575, 915], [588, 900], [600, 915], [610, 960], [600, 985], [570, 985]], [[585, 915], [594, 970]], 6),
    ([[690, 1000], [700, 968], [722, 955], [735, 975], [725, 1005]], [[705, 995], [718, 968]], 5),
    ([[812, 1000], [828, 962], [848, 950], [870, 975], [880, 1030], [820, 1030]], [[845, 965], [852, 1015]], 7),
    ([[880, 975], [895, 930], [908, 918], [925, 945], [930, 995], [885, 995]], [[905, 932], [908, 985]], 6),
    ([[1005, 990], [1020, 945], [1040, 932], [1048, 940], [1048, 1000]], [[1028, 950], [1035, 990]], 5),
    (None, [[728, 990], [745, 972], [770, 964], [800, 978]], 6),   # bw4 の 頭の 毛（毛は 線の まわり だけ 守る：毛の 上の 帯は 背景）
    (None, [[455, 968], [490, 952], [530, 948], [552, 962]], 6),                 # まん中の 馬の 頭の 毛
    (None, [[262, 950], [285, 930], [305, 920], [326, 934]], 5),                 # 2番目の 馬の 頭の 毛
    ([[266, 926], [270, 912], [279, 905], [292, 904], [300, 907], [302, 912], [290, 915], [278, 925]], [[270, 918], [277, 910], [286, 907], [296, 909]], 2)]     # 2番目の 馬の 上の 毛の たば（白い 光の 線より 上は ふち）
protect = np.zeros((H, W), np.uint8); ear_seed = np.zeros((H, W), np.uint8)
for poly_, line_, r_ in EARS:
    if poly_ is not None: cv2.fillPoly(protect, [np.array(poly_, np.int32)], 1)
    cv2.polylines(ear_seed, [np.array(line_, np.int32)], False, 1, thickness=2 * r_)
protect = cv2.dilate(protect, np.ones((5, 5), np.uint8)).astype(bool)
Bm |= ear_seed.astype(bool)
body = np.zeros((H, W), np.uint8)                       # 下の 馬の 体（頭より 下〜手すりの 上）は ぜんぶ 馬（すき間も 体・たてがみ）
cv2.fillPoly(body, [np.array([[0, 1040], [1048, 1040], [1048, 1200], [800, 1194], [500, 1188], [200, 1181], [0, 1175]], np.int32)], 1)
Bm |= body.astype(bool)
horse = T | Bm
near13 = cv2.dilate(horse.astype(np.uint8), np.ones((13, 13), np.uint8)).astype(bool)
near5 = cv2.dilate(horse.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
frame = np.zeros((H, W), bool); frame[355:440, 80:980] = True                 # ボードの 上の ふち（王冠・アーチ）：馬の すぐ そばまで 背景の 印
band = np.zeros((H, W), bool); band[860:990, :] = True                       # ボードの 下の ふち（下の 馬の 頭の うしろ）：耳の ふちは 光で 色が かわるので 近くは 印に しない
navy = (cool | ((b - r > 5) & (ref.max(-1) < 120))) & (frame | band)         # アーチの 中・頭の あいだの 紺・灰（板の 色）も 背景
near3 = cv2.dilate(horse.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
near5 = cv2.dilate(horse.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
# 下の 馬の 頭の うしろの ボードの ふち：銀の 段（d2_2）で 色が うすく（銀・白）、段で 大きく かわる 所＝ふち（馬の 毛は 銀の 段でも 茶色）
a2 = al[1]; sat2 = (a2.max(-1) - a2.min(-1)) / np.maximum(a2.max(-1), 1)
uu = yy - (891 + (xx - 83) * (52.0 / 839))
bzone = (uu > -30) & (uu < 110) & (yy > 830) & (yy < 1040)
bar = ndi.binary_erosion(bzone & (sat2 < 0.24) & (D > 60), iterations=1)
bgT = ndi.binary_erosion(MT < 0.07, iterations=2) & tarea & ~frame & ~near5      # 上の 馬の まわりは モデルの 背景
bg = ((Ds > 55) & ~np.where(frame, near5, near13) & ~bzone & ~(tarea & ~frame)) | bgT | ndi.binary_erosion(yel, iterations=2) | (navy & ~near3) | bar
for (cx, cy), rr in (((985, 888), 22), ((1027, 922), 13)):           # 右上の きらきら（馬の 耳の そば：馬と いっしょに 動かない）
    cv2.circle(bg.view(np.uint8), (cx, cy), rr, 1, -1)
bg &= ~protect
bg &= ~cv2.dilate(ear_seed, np.ones((5, 5), np.uint8)).astype(bool)   # 手で おいた 耳・毛の 印は 背景の 印より つよい
cv2.rectangle(bg.view(np.uint8), (406, 878), (450, 900), 1, -1)        # 「！」の 左の 紺の かけら
for (cx, cy), rr in (((655, 972), 24), ((968, 880), 20)):              # 頭の あいだの 紙ふぶき・きらきら
    cv2.circle(bgu := bg.view(np.uint8), (cx, cy), rr, 1, -1)
bg &= ~board
still = bg & (bzone | frame)                       # ふちの 帯で 背景と きめた 所は 光の ふち（halo）にも 入れない
for d in names:
    s = shift[d]; Hd = H + s if s else H
    for nm, m_ in (('T', T), ('B', Bm), ('bg', bg), ('still', still)):
        o = np.zeros((1501, W), np.uint8); o[s:s + H] = m_; Image.fromarray(o * 255).save(f'{O_}/toast_{d}_{nm}.png')
np.save('/tmp/claude-0/-home-claude/5cf5eba2-63a4-523b-8a91-64c54d2d6b4b/scratchpad/toast_D2.npy', D)
print('T', int(T.sum()), 'B', int(Bm.sum()), 'bg', int(bg.sum()))
