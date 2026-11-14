# えらんだ 落ち方を アプリ用の 数に する（60コマ／秒・絵の 画素・回る 角度・当たった 時）＋ 見る 用の 絵
import sys, pickle, json, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
from PIL import Image, ImageDraw
import physics as PH
import pick as PK
import cam as C
import world as WD
APP = ROOT + '/app/'


def export(res, picks, F):
    out = []
    for c, got in enumerate(picks):
        for i in got:
            r = res[i]
            px, py = C.proj(r['x'], r['y'], WD.ZC)
            fr = []
            for x, y, a in zip(px, py, r['a']):
                fr += [int(round(x * 10)), int(round(y * 10)), int(round(math.degrees(a)))]
            hits = [[int(round(h[0] * 60)), h[1], h[2], min(99, int(round(h[3] * 60)))] for h in r['hits']]      # [コマ, 種類（0 釘・1 コップ・2 輪・3 かべ）, 番号, 強さ]
            out.append(dict(cup=c, tin=int(round(r['tin'] * 60)), n=len(px), f=fr, h=hits))
    return out


if __name__ == '__main__':
    res = []
    for p in sys.argv[1:]:
        res += pickle.load(open(p, 'rb'))['res']
    picks, F = PK.choose(res)
    for c, got in enumerate(picks):
        for i in got:
            f = F[i]; print(f'cup {c}: sim {i} tin {f["tin"]:.2f} dur {f["dur"]:.2f} pegs {f["npeg"]} seq {f["seq"]} cuphits {f["ncup"]} ring {f["nring"]} wall {f["nwall"]} stall {f["stall"]:.2f} vx0 {res[i]["vx0"]:+.3f}')
    P = export(res, picks, F)
    js = json.dumps(P, separators=(',', ':'))
    open(APP + 'paths.json', 'w').write(js); print('paths', len(P), 'json', len(js), 'B')
    pickle.dump(dict(res=[res[i] for got in picks for i in got]), open(APP + 'paths_src.pkl', 'wb'))
    # 見る 用：台の 絵の 上に 玉を 重ねる（6コマ ごと）
    base = Image.open(APP + 'base.png').convert('RGBA'); front = Image.open(APP + 'front.png').convert('RGBA')
    ball = Image.open(APP + 'ball.png').convert('RGBA')
    rpx = WD.R_BALL * C.scale_at(WD.ZC)
    box = (100, 560, 1020, 1280)
    tiles = []
    for p in P:
        im = base.copy()
        n = p['n']
        for k in list(range(0, n, 5)) + [n - 1]:
            x, y, a = p['f'][3 * k] / 10, p['f'][3 * k + 1] / 10, p['f'][3 * k + 2]
            fi = int(round((a % 360) / 360 * 32)) % 32
            cell = ball.crop(((fi % 8) * 96, (fi // 8) * 96, (fi % 8) * 96 + 96, (fi // 8) * 96 + 96))
            d = int(round(rpx * 2 * 96 / 88))
            cell = cell.resize((d, d), Image.LANCZOS)
            im.alpha_composite(cell, (int(round(x - d / 2)), int(round(y - d / 2))))
        im.alpha_composite(front)
        dr = ImageDraw.Draw(im); dr.text((box[0] + 10, box[1] + 6), f'cup {p["cup"]}  in {p["tin"] / 60:.2f}s  end {p["n"] / 60:.2f}s', fill=(0, 0, 0, 255))
        bg = Image.new('RGBA', im.size, (40, 52, 46, 255)); bg.alpha_composite(im)
        tiles.append(bg.crop(box).convert('RGB').resize(((box[2] - box[0]) // 2, (box[3] - box[1]) // 2), Image.LANCZOS))
    w, h = tiles[0].size
    sheet = Image.new('RGB', (w * 4, h * 4), 'white')
    for i, t in enumerate(tiles): sheet.paste(t, ((i % 4) * w, (i // 4) * h))
    sheet.save(APP + 'paths_view.png'); print(sheet.size)
