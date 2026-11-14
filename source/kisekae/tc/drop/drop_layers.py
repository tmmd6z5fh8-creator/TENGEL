# 台の 絵から アプリ用の 層を 作る：手前の 層（玉より 手前に ある 所＝釘の 先・コップの 前）
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
from PIL import Image
import cam as C
import world as WD

APP = ROOT + '/app/'


def front_layer(d):
    """玉の 中心の 深さ（WD.ZC）より 手前の 画素（釘の 先・コップの 前の かべ）。出口（受け皿）は 入れない＝玉は 出口の 手前を 通る"""
    z, al, rgb = d['z'], d['alpha'].astype(np.float32) / 255, d['rgb']
    H, W = z.shape
    k = np.clip((z - (WD.ZC - 0.004)) / 0.008, 0, 1); k = k * k * (3 - 2 * k)
    x0, y0 = C.proj(-0.47, 0.272, WD.ZC); x1, y1 = C.proj(0.47, -0.345, WD.ZC)
    YY, XX = np.mgrid[0:H, 0:W]
    reg = (XX >= x0) & (XX <= x1) & (YY >= y0) & (YY <= y1)
    a = np.where(reg, k * al, 0.0)
    return np.dstack([rgb, (a * 255 + 0.5).astype(np.uint8)]), (int(x0), int(y0), int(np.ceil(x1)), int(np.ceil(y1)))


if __name__ == '__main__':
    d = np.load(APP + 'base.npz')
    fr, box = front_layer(d)
    Image.fromarray(fr, 'RGBA').save(APP + 'front.png')
    print('front box', box, 'pixels', int((fr[..., 3] > 0).sum()))
    # 見る 用：手前の 層 だけ（うしろは 暗い）
    bg = Image.new('RGBA', (fr.shape[1], fr.shape[0]), (60, 20, 80, 255)); bg.alpha_composite(Image.fromarray(fr, 'RGBA'))
    bg.crop((box[0] - 20, box[1] - 20, box[2] + 20, box[3] + 20)).convert('RGB').save(APP + 'front_view.png')
