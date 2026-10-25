"""動く壁紙の 共通の 道具
   feather()：コマの 入れもの（切りぬいた 四角）の ふちを 2〜3px ぼかす mask の CSS。
     iPad など 画面の 幅に 合わせて 壁紙を 拡大する（#ksBnr .ksb の transform:scale）と、下の 止まった絵と、その上に 重ねた コマ（背景ごと 切りぬいた
     シート）は べつべつの 層として 拡大されるので、四角の ふちに 細い 線（1〜2画素の 色の 段差・紙の もようの 切れ目）が 見える。
     ふちを すき通しに ぼかすと、下の絵（同じ 背景）と まざって 線は 見えなくなる。絵の はし（0 や 390・160）に ついている ふちは ぼかさない。
     （2026/10/25 まさちゃん「水墨画の黄色い丸のあたりに、細い線が縦に入っているから消して！」。ネオンの 画面にも 同じ 線が 写っていた）"""


def feather(sel, x, y, w, h, W=390, H=160, px=3):
    """sel の ふちを ぼかす mask（左右・上下。絵の はしに ついている ふちは そのまま）。ぼかす ふちが なければ ''"""
    L = px if x > 0 else 0
    R = px if x + w < W else 0
    T = px if y > 0 else 0
    B = px if y + h < H else 0
    gs = []
    if L or R:
        gs.append(f'linear-gradient(to right,transparent,#000 {L}px,#000 calc(100% - {R}px),transparent)')
    if T or B:
        gs.append(f'linear-gradient(to bottom,transparent,#000 {T}px,#000 calc(100% - {B}px),transparent)')
    if not gs:
        return ''
    m = ','.join(gs)
    comp = '-webkit-mask-composite:source-in;mask-composite:intersect;' if len(gs) > 1 else ''
    return f'{sel}{{-webkit-mask-image:{m};mask-image:{m};{comp}}}'
