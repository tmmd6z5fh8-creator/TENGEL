# 的中⑧ 花束：花が ヒラヒラ（実験）の デザインの 設定を 作る（まさちゃん 11/05 20:26「花がヒラヒラ動く演出できる？そんなに激しくなく！」）
#   python3 bloom_design.py <花の 一覧 json> <出す design json>
#   花の 一覧 = { "b1": [ {id, c:[x,y], r | rx,ry, o?:[x,y]（回る まん中：ない ときは c）, sw?, kind?}, … ], "b2": …, "b3": …, "b4": … }
#   花ごとに：印＝まん中の だ円（半径の 55%）・outer＝半径の 1.15倍＋4px・モデルは つかわない（trust_mask: false・seg なし＝絵の ふち線で 分ける）
#   動き：まん中の まわりで ゆっくり 左右に 回る（sw 度）＋ 少し 向きを かえる（fy 度）。花ごとに 時間を ずらす（いっしょに 動かない）
import json, sys, math
E = json.load(open(sys.argv[1], encoding='utf8')); OUT = sys.argv[2]
B = '/home/claude/work/bcpic'; O = '/home/claude/work/bcpic/chr'
DIRS = {'b1': ('d8_1', 'bloom1'), 'b2': ('d8_2', 'bloom2'), 'b3': ('d8', 'bloom3'), 'b4': ('d8_4', 'bloom4')}
base = {"bg_thr": 0.12, "halo": 3, "orphan_dist": 0, "core_thr": 0.75, "parts": [],
        "fill": {"mode": "smooth", "glow_px": 3, "glow_thr": 40, "grow": 2, "grow_plate": 3, "edge_px": 2.0, "frag_max": 60, "ring": 6}}
stages = []
for key in ('b1', 'b2', 'b3', 'b4'):
    if key not in E: continue
    d, out = DIRS[key]; parts = []; mo = {}
    for i, e in enumerate(E[key]):
        cx, cy = e['c']; rx = e.get('rx', e.get('r')); ry = e.get('ry', e.get('r'))
        inner = [{"ell": [[cx, cy], max(4, rx * 0.55), max(4, ry * 0.55)]}] + e.get('inner', [])
        outer = [{"ell": [[cx, cy], rx * 1.15 + 4, ry * 1.15 + 4]}] if 'outer' not in e else e['outer']
        parts.append({"id": e['id'], "inner": inner, "outer": outer, "min_part": 300, "trust_mask": False})
        # 時間の ずらし：花ごとに ちがう（黄金比で ちらす）
        u = (i * 0.618034 + (0.31 if key in ('b2', 'b4') else 0.0)) % 1.0; v = (i * 0.414214 + 0.17) % 1.0
        tulip = 'o' in e                     # チューリップ（もとの まわりで ゆれる）・ほかの 花（まん中の まわりで 回る）
        mo[e['id']] = {"o": e.get('o', [cx, cy]), "sw": e.get('sw', 3.0 if tulip else 4.0), "st": round(3.4 + 1.0 * u, 2), "fy": e.get('fy', 10.0 if tulip else 12.0),
                       "sf": round(2.3 + 0.7 * v, 2), "dt": round(0.4 + 2.4 * u, 2), "dp": round(0.2 + 1.8 * v, 2)}
    stages.append({"dir": f"{B}/{d}", "out": f"{O}/{out}", "over": {"parts": parts}, "motion": mo})
D = {"base": base, "seg": [], "stages": stages, "motion": {}, "layers_top": True, "stage_json": f"{O}/stage_all.json"}
json.dump(D, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('stages', len(stages), [len(s['over']['parts']) for s in stages])
