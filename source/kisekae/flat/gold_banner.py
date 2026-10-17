"""金（780×320）：全力で駆ける 金の馬の像（一から作った創作の絵）。全体を金でまとめる
   シルバー（flat/silver_banner.py）と同じ像・同じ作り（ヘアラインの地・光の輪・走る勢いのすじ・みがいた床にうつる像・きらめき）で、
   色だけ金にする（GOLD のパレット）。像はみがいた金（金属）で、まわりの光（上はあたたかい白・地平はこげ茶・下は暗い）が体に映る
   python3 flat/gold_banner.py <出力.webp>（sdfr がいる）"""
import sys, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import silver_banner as SB
import style2d as S2
from style2d import save_webp

GOLD = dict(
    env=((0.86, 0.80, 0.68), (0.10, 0.07, 0.03), (0.025, 0.018, 0.008), (0.0, 0.0, 0.0)),
    lobes=(((0.30, 0.90, -0.40), (1.55, 1.42, 1.15), 6.0),              # 上・手前のやわらかい光
           ((-0.60, 0.30, 0.60), (1.0, 0.92, 0.70), 10.0)),             # うしろからのふちの光
    lights=(((0.55, 0.65, -0.55), (1.0, 0.97, 0.88), 10, 1),            # 主光
            ((-0.50, 0.30, -0.60), (0.26, 0.23, 0.17), 8, 0)),          # 補助
    metal=(1.00, 0.76, 0.30), rough=0.08,                               # 像：みがいた金
    bg=[(0, '#F7EBC6'), (0.5, '#D9B460'), (1, '#9A7228')],              # 金の地（上はシャンパンゴールド・下は深い金）
    glow=(0.17, 0.15, 0.10), ring=(1.0, 0.93, 0.70), streak=(0.13, 0.11, 0.07),
    floor=[(0, '#7A5A1E'), (1, '#3A2A0C')], spark=(1.0, 0.96, 0.82))


if __name__ == '__main__':
    out = sys.argv[1]
    tmp = os.path.join(S2.TMP, f'gold{os.getpid()}')
    os.makedirs(tmp, exist_ok=True)
    try:
        R, S = SB.render3d(tmp, GOLD)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    img = SB.compose(R, pal=GOLD)
    save_webp(img, out)
