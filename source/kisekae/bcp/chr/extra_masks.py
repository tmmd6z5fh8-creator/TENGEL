# キャラだけ 動かす（実験）：デザインの 設定（designs/*.json）が つかう 色の マスクを 作る（絵から 作る・絵は リポジトリに 入れない）
#   python3 extra_masks.py carry   → carry_ribbons_bg.png（背景の 印）・carry_ribbons_still.png（光の ふちにも 入れない）
#   python3 extra_masks.py wait    → wait1〜3_books_bg.png（左の 本：たてがみの 毛は のぞく）
#   python3 extra_masks.py next    → next1〜4_band.png（next_band.py：ボードの 下の 白い 帯）
#   python3 extra_masks.py toast   → toast_<段>_{T,B,bg,still,arch}.png（toast_seeds.py）
#   python3 extra_masks.py ring    → ring1〜4_board.png（ボード：右上・左上の 馬は この うしろ）
#   python3 extra_masks.py rain    → rain1〜4_lines_{L,R}.png（頭の まわりの 青い たての 線：馬と いっしょに 動かす 印）
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
    # 上の 馬の あごの 前に ある 王冠（ボードの 上の ふち）：うしろの キャラ（behind）の ボード（toast_<段>_arch.png）
    for d in ('d2_1', 'd2_2', 'd2', 'd2_4'):
        sh = 2 if d in ('d2_2', 'd2') else 0
        still = np.asarray(Image.open(f'{O_}/toast_{d}_still.png')) > 127
        box = np.zeros_like(still); box[340 + sh:428 + sh, 498:594] = True
        save(ndi.binary_closing(still & box, iterations=2) & box, f'{O_}/toast_{d}_arch.png')
if what in ('ring', 'all'):
    # 的中① 廻る：ボード（紺の 板＋ふち線：板を 22px ふくらませる）。右上・左上の 馬は この ボードの うしろ（behind）
    for d, nm in (('d1b_1', 'ring1'), ('d1b_2', 'ring2'), ('d1b', 'ring3'), ('d1b_4', 'ring4')):
        a = np.asarray(Image.open(f'{B_}/{d}/clean.png').convert('RGB')).astype(np.float32); H, W = a.shape[:2]
        r, g, b = a[..., 0], a[..., 1], a[..., 2]; V = a.max(-1)
        navy = (b - r > 15) & (V < 110); q = np.zeros((H, W), np.uint8); cv2.rectangle(q, (180, 415), (870, 955), 1, -1); navy &= q.astype(bool)
        lab, n = ndi.label(navy); sz = np.bincount(lab.ravel()); sz[0] = 0; panel = ndi.binary_fill_holes(lab == sz.argmax())
        save(cv2.dilate(panel.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45))).astype(bool), f'{O_}/{nm}_board.png')
if what in ('rain', 'all'):
    # ハズレ① 二人でしょんぼり：頭の まわりの 青い たての 線（しょんぼりの 線）。耳の うしろ・たてがみの 前を 通る ので、
    # 背景に のこすと 動いた とき 線の 所で たてがみが 切れる → 線は その 馬の 絵に 入れて いっしょに 動かす
    #   モデル（isnet-anime）は 暗い 背景の 前の 長い たてがみ・しっぽ・(3回目の)頭の 上・なみだ を 見のがす → 絵の 中の 線（ふとさ r）×色 で 印を 足す
    #   色：hairL＝茶色（赤 − 青 ≥ 12）・hairR＝こい 灰色（赤 − 青 ≥ −14：背景の 青い さくは 入らない）・tear＝水色・dark＝暗い（ひづめ）・any＝色を 見ない
    BOX = {'h1': {'L': [100, 580, 290, 860], 'R': [790, 580, 1000, 900]}, 'h1_2': {'L': [60, 580, 290, 860], 'R': [790, 580, 1000, 900]},
           'h1_3': {'L': [100, 580, 300, 860], 'R': [780, 580, 1000, 900]}, 'h1_4': {'L': [120, 720, 320, 1030], 'R': [760, 720, 960, 1030]}}
    SEEDS = {
        'h1': {'L': [('hairL', [(152, 826), (140, 920), (133, 1000), (126, 1070), (120, 1105)], 10), ('hairL', [(172, 860), (168, 960), (165, 1060), (165, 1095)], 7),
                     ('hairL', [(176, 1118), (145, 1148), (115, 1190), (103, 1228), (115, 1262)], 11), ('hairL', [(133, 1108), (100, 1112), (80, 1125), (70, 1150), (72, 1172)], 6),
                     ('hairL', [(408, 960), (413, 996)], 5), ('dark', 'rect', [200, 1250, 240, 1294]), ('dark', 'rect', [304, 1250, 348, 1294])],
               'R': [('hairR', [(905, 822), (912, 900), (916, 1000), (912, 1090), (908, 1120)], 11), ('hairR', [(890, 850), (893, 950), (893, 1080)], 7),
                     ('hairR', [(905, 1150), (920, 1190), (930, 1230), (925, 1262)], 13), ('any', [(735, 673)], 3), ('any', [(668, 972), (678, 995), (688, 1018)], 9),
                     ('dark', 'rect', [692, 1250, 732, 1294]), ('dark', 'rect', [804, 1250, 848, 1296])]},
        'h1_2': {'L': [('hairL', [(150, 860), (140, 967), (132, 1067), (129, 1115)], 10), ('hairL', [(168, 880), (165, 980), (162, 1080)], 6),
                       ('hairL', [(152, 1140), (136, 1200), (130, 1250)], 11), ('hairL', [(366, 965), (370, 990), (378, 1005), (385, 1012)], 5), ('hairL', [(269, 1229)], 6),
                       ('dark', 'rect', [200, 1252, 240, 1298]), ('dark', 'rect', [308, 1252, 348, 1298])],
                 'R': [('hairR', [(926, 840), (930, 967), (927, 1067), (922, 1118)], 11), ('hairR', [(905, 860), (907, 960), (905, 1080)], 6),
                       ('hairR', [(926, 1150), (935, 1205), (928, 1260)], 13), ('dark', 'rect', [688, 1252, 732, 1298]), ('dark', 'rect', [796, 1252, 840, 1298]),
                       ('any', [(865, 985), (875, 1020), (885, 1045)], 8), ('any', [(882, 1045), (888, 1080), (893, 1110)], 8), ('any', [(912, 1075)], 12),
                       ('any', [(667, 975), (676, 998), (684, 1022)], 9)]},
        'h1_3': {'L': [('hairL', [(225, 720), (300, 705), (380, 735)], 12), ('any', [(180, 730)], 16), ('any', [(428, 768)], 14),
                       ('tear', [(205, 850), (190, 890), (178, 930)], 7), ('tear', [(445, 835), (470, 860), (488, 880)], 6),
                       ('hairL', [(152, 847), (136, 947), (124, 1047), (119, 1091)], 10), ('hairL', [(141, 1080), (108, 1136), (91, 1202), (119, 1236)], 11),
                       ('any', [(176, 960), (178, 1050), (176, 1150), (172, 1230)], 7), ('hairL', [(398, 1008), (404, 1030), (408, 1050)], 9),
                       ('any', [(152, 790), (142, 820), (136, 848), (134, 866)], 14),
                       ('any', [(246, 975)], 20), ('any', [(443, 947)], 22), ('dark', 'rect', [192, 1206, 232, 1256]), ('dark', 'rect', [328, 1206, 372, 1256])],
                 'R': [('hairR', [(650, 720), (760, 700), (860, 730)], 12), ('any', [(636, 770)], 18), ('any', [(905, 760)], 18),
                       ('tear', [(640, 835), (600, 850), (570, 880), (560, 920)], 6), ('tear', [(865, 860), (885, 900), (900, 930)], 7),
                       ('any', [(915, 850), (920, 900), (925, 960), (928, 1020), (925, 1075)], 10), ('any', [(905, 1110), (915, 1150), (912, 1200), (905, 1240)], 16),
                       ('any', [(615, 947)], 22), ('any', [(821, 980)], 22), ('tear', [(575, 905), (565, 925), (558, 945)], 6), ('any', [(862, 945), (866, 985), (868, 1025)], 13),
                       ('any', [(915, 812)], 13),
                       ('dark', 'rect', [644, 1208, 688, 1258]), ('dark', 'rect', [796, 1210, 840, 1260])]},
        'h1_4': {'L': [('hairL', [(131, 942), (114, 1009), (103, 1076)], 10), ('hairL', [(87, 1098), (53, 1131), (42, 1176)], 12), ('any', [(462, 960)], 16),
                       ('hairL', [(20, 1080), (26, 1106), (35, 1130)], 6), ('hairL', [(38, 1196)], 5), ('hairL', [(56, 1084)], 5), ('hairL', [(418, 1110), (425, 1130)], 5),
                       ('dark', 'rect', [202, 1190, 242, 1224]), ('dark', 'rect', [258, 1190, 294, 1224]), ('dark', 'rect', [306, 1190, 346, 1224]), ('dark', 'rect', [358, 1190, 394, 1224])],
                 'R': [('any', [(915, 885), (925, 950), (935, 1020), (948, 1080)], 8), ('hairR', [(1000, 1110), (1020, 1150), (1030, 1190)], 12), ('any', [(618, 968)], 18),
                       ('hairR', [(648, 1060), (651, 1079), (665, 1106)], 5), ('any', [(953, 1085), (958, 1130), (962, 1178)], 6),
                       ('dark', 'rect', [666, 1190, 706, 1224]), ('dark', 'rect', [714, 1190, 754, 1224]), ('dark', 'rect', [762, 1190, 802, 1224]), ('dark', 'rect', [818, 1190, 858, 1224])]}}
    for k_, (d, bx) in enumerate(BOX.items()):
        a = np.asarray(Image.open(f'{B_}/{d}/clean.png').convert('RGB')).astype(np.float32); H, W = a.shape[:2]
        r, g, b = a[..., 0], a[..., 1], a[..., 2]; V = a.max(-1)
        blue = (b >= 140) & (b - r >= 70) & (b - g >= 35)
        vert = ndi.binary_opening(blue, structure=np.ones((21, 1), bool))                  # たてに 長い 所
        wide = ndi.binary_opening(vert, structure=np.ones((1, 15), bool))                  # はばの ある 光（雲・空）は のぞく
        thin = vert & ~ndi.binary_dilation(wide, iterations=2)
        lab, n = ndi.label(thin); keep = np.zeros((H, W), bool)
        for i, sl in enumerate(ndi.find_objects(lab)):
            if sl[0].stop - sl[0].start < 30 or sl[1].stop - sl[1].start > 14: continue
            comp = lab == (i + 1)
            ring = ndi.binary_dilation(comp, structure=np.ones((1, 13), bool)) & ~ndi.binary_dilation(comp, structure=np.ones((1, 5), bool))
            # 線は まわりより はっきり 明るい 青（雲の 中の 明るい すじ・さくの ふちは のぞく）。ふちの にじみは 光の ふち（halo）で 入る
            if V[comp].mean() - np.median(V[ring]) >= 35 and (b - r)[comp].mean() >= 80: keep |= comp
        col = {'hairL': (r - b) >= 12, 'hairR': (r - b) >= -14, 'tear': ((b - r) >= 25) & (V >= 140), 'dark': V < 90, 'any': np.ones((H, W), bool)}
        for side, (x0, y0, x1, y1) in bx.items():
            m = np.zeros((H, W), bool); m[y0:y1, x0:x1] = True
            sd = np.zeros((H, W), np.uint8)
            for kind, pts, rad in SEEDS[d][side]:
                tmp = np.zeros((H, W), np.uint8)
                if pts == 'rect': tmp[rad[1]:rad[3], rad[0]:rad[2]] = 1           # ひづめ（水に うつった ひづめは 入れない：四角の 中の 暗い 所だけ）
                elif len(pts) == 1: cv2.circle(tmp, pts[0], rad, 1, -1)
                else: cv2.polylines(tmp, [np.array(pts, np.int32)], False, 1, thickness=2 * rad + 1)
                sd |= (tmp.astype(bool) & col[kind]).astype(np.uint8)
            save((keep & m) | sd.astype(bool), f'{O_}/rain{k_ + 1}_seed_{side}.png')
