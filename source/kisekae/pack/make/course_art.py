"""競馬場（上から見た）の 壁紙（壁紙パック・第4.93版）の 馬：真上から 見た サラブレッドと 騎手（まさちゃんの 指定「馬達をもっとリアルな馬にして」）
   絵は pack/course.py の top_sheet（SVG：こし・胴・肩・首・頭・耳・前髪・たてがみ・顔の 白い すじ・ギャロップで 前後に のびる 4本の 足・なびく しっぽ・
   前かがみの 騎手＝ヘルメット・勝負服の せなか（もよう）・うで・白い ズボンの ひざ・ブーツ・手綱・鞍の 下の 布・影）。
   8頭 × NF コマを 1まい（たて 8行・よこ NF コマ）の すき通しの WebP に する（画面の 3倍の 画素：まわしても ぼやけない）。
   大きさは course.HS2（第4.94版：0.95 → 0.70＝前の 7割4分・まさちゃんの 指定「もっと馬小さくして」）
   python3 kisekae/pack/make/course_art.py [--out DIR]   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の course.horses"""
import os
import sys

import numpy as np
import cv2

os.environ.setdefault('PACK_ONLY', 'course')          # pack を 読む とき ほかの テーマを 読まない
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import save_webp, record, preview_png  # noqa: E402  (sys.path に flat・pack の 親を 足す)
from cute_horse import svg_rgba  # noqa: E402
from pack.course import SILKS, NF, CW, CH, HS2, top_sheet  # noqa: E402

SC = 3                     # 画面の px あたりの 画素


def build(out=None):
    cw, ch = round(CW * HS2 * SC), round(CH * HS2 * SC)
    rows = []
    for k in range(len(SILKS)):
        pm = svg_rgba(top_sheet(k), cw * NF, ch)                  # premultiplied RGBA（0〜1）
        a = pm[..., 3:4]
        rgb = np.where(a > 1e-4, pm[..., :3] / np.maximum(a, 1e-4), 0)
        rows.append(np.concatenate([rgb, a], -1))
    sheet = np.concatenate(rows, 0)
    u8 = (np.clip(sheet, 0, 1) * 255 + .5).astype(np.uint8)
    if out:
        os.makedirs(out, exist_ok=True)
        preview_png(u8, os.path.join(out, 'course_horses.png'), bg=(134, 199, 115))
    bid = save_webp(u8, quality=92)
    meta = dict(frames=NF, rows=len(SILKS), cell=[cw, ch], scale=SC)
    record('course', 'horses', bid, meta)
    print('horses', bid, meta, u8.shape, flush=True)
    return bid


if __name__ == '__main__':
    o = None
    for a in sys.argv[1:]:
        if a.startswith('--out='):
            o = a.split('=', 1)[1]
    build(o)
