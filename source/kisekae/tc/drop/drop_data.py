# アプリ用の データ（tc_dp.json：場所と 玉の 落ち方）と 絵（webp）を 1つの フォルダに 出す
#   python3 -I drop_data.py <出力の フォルダ>
import sys, os, json, shutil
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
from PIL import Image
import cam as C
import world as WD
import physics as PH
import drop_layers as DL
APP = ROOT + '/app/'
ART = ROOT + '/art/out/'


def webp(im, path, q=90):
    im.save(path, 'WEBP', quality=q, method=6, alpha_quality=100)
    return os.path.getsize(path)


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    d = np.load(APP + 'base.npz')
    H, W = d['z'].shape
    sizes = {}
    base = Image.fromarray(np.dstack([d['rgb'], d['alpha']]), 'RGBA')
    sizes['tc_dp_base.webp'] = webp(base, os.path.join(out, 'tc_dp_base.webp'), 92)
    fr, box = DL.front_layer(d)
    ys, xs = np.nonzero(fr[..., 3] > 0)
    fb = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    sizes['tc_dp_front.webp'] = webp(Image.fromarray(fr[fb[1]:fb[3], fb[0]:fb[2]], 'RGBA'), os.path.join(out, 'tc_dp_front.webp'), 92)
    so = json.load(open(APP + 'see_open.json'))
    sizes['tc_dp_see.webp'] = webp(Image.open(APP + 'see_open.png'), os.path.join(out, 'tc_dp_see.webp'), 92)
    sizes['tc_dp_ball.webp'] = webp(Image.open(APP + 'ball.png'), os.path.join(out, 'tc_dp_ball.webp'), 90)
    for i in range(1, 7):
        for k in ('uma', 'hold'):
            shutil.copyfile(f'{ART}tc_dp_{k}{i}.webp', os.path.join(out, f'tc_dp_{k}{i}.webp')); sizes[f'tc_dp_{k}{i}.webp'] = os.path.getsize(os.path.join(out, f'tc_dp_{k}{i}.webp'))
    # 入口の ボタンに のせる 小さい 台の 絵
    ih = 300; iw = int(round(W * ih / H))
    sizes['tc_dp_icon.webp'] = webp(base.resize((iw, ih), Image.LANCZOS), os.path.join(out, 'tc_dp_icon.webp'), 90)
    # 場所
    L1 = json.load(open(APP + 'layout1.json')); L2 = json.load(open(APP + 'layout2.json'))
    sx = sorted(q['cx'] for q in L1['sockets']); step = (sx[-1] - sx[0]) / 4
    hold_x = [round(sx[0] + step * i, 1) for i in range(5)]
    assert all(min(abs(a - b) for b in hold_x) < 3 for a in sx), (sx, hold_x)
    pegs = json.load(open(ROOT + '/out/pegs_orig.json'))
    r1 = lambda v: round(float(v), 1)
    cup_c = [((a + b) / 2, PH.RIM_Y) for a, b in PH.CUP_X]
    data = dict(
        v=1, img=[W, H],
        ball=dict(r=r1(WD.R_BALL * C.scale_at(WD.ZC)), start=[r1(v) for v in C.proj(PH.START[0], PH.START[1], WD.ZC)]),
        front=[fb[0], fb[1], fb[2] - fb[0], fb[3] - fb[1]],
        lcd=[559.5, 1166.0, 91.0, 118.0],
        hold=dict(x=hold_x, y=r1(L1['sockets'][0]['cy']), w=98),
        go=dict(box=L2['btn_go']['box'], poly=L2['btn_go']['poly']),
        see=dict(box=L2['btn_see']['box'], poly=[[196, 1630], [262, 1578], [858, 1578], [924, 1630], [900, 1665], [872, 1708], [248, 1708], [220, 1665]], open=[so['x'], so['y'], so['w'], so['h']]),
        cups=[[r1(v) for v in C.proj(x, y, 0.09)] for x, y in cup_c],
        pegs=[[r1(v) for v in C.proj(p['ax'], p['ay'], 0.105)] for p in pegs],
        paths=json.load(open(APP + 'paths.json')))
    js = json.dumps(data, separators=(',', ':'))
    open(os.path.join(out, 'tc_dp.json'), 'w').write(js); sizes['tc_dp.json'] = len(js)
    for k, v in sizes.items(): print(f'{k:22s} {v:8d} B')
    print('total', sum(sizes.values()), 'B', 'files', len(sizes))
    print({k: v for k, v in data.items() if k != 'paths'})
