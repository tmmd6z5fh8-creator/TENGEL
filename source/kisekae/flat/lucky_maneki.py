"""開運の「招き馬」のキャラクター（SVG・240×250・アニメの塗り）
   招き猫のような白い馬：白い体に黒い太い線、赤い耳の中と目の上の赤いかざり、金色の目、金のたてがみ・前髪・しっぽ・ひづめ。
   右前足（近いほう）を顔の横にあげて福を招き（ひづめの裏はうすい桃色）、左前足で「千両」の小判をだく。赤い首輪に金の鈴。
   顔は少し右を向き、まるい鼻先・桃色の鼻の穴・にっこり口。影は青みの灰色1段（くっきり）。形はすべて一から作ったオリジナル
   python3 flat/lucky_maneki.py <出力.svg>（確かめ用）"""
import sys, math

VB_W, VB_H = 240, 252
OUT = '#23202A'          # 線
LW = 4.6
LW2 = 3.0
WHITE = '#FFFFFF'
SHADE = '#DCE2EE'        # 白の影（青みの灰色）
GOLD = '#F5C542'
GOLD_SH = '#D8902A'
GOLD_HI = '#FFF0A6'
RED = '#D9302C'
RED_SH = '#A51D22'
PINK = '#F7B7B5'
MUZ = '#FFF0F0'
MUZ_SH = '#F3D3D6'


def star4(cx, cy, r, fill, rot=0.0, k=0.28):
    pts = []
    for i in range(8):
        a = rot + i * math.pi / 4
        rr = r if i % 2 == 0 else r * k
        pts.append(f'{cx + math.cos(a) * rr:.2f},{cy + math.sin(a) * rr:.2f}')
    return f"<polygon points='{' '.join(pts)}' fill='{fill}'/>"


def P(d, fill, w=LW, extra=''):
    return f"<path d='{d}' fill='{fill}' stroke='{OUT}' stroke-width='{w}' stroke-linejoin='round' stroke-linecap='round' {extra}/>"


def L(d, w=LW2, col=OUT, extra=''):
    return f"<path d='{d}' fill='none' stroke='{col}' stroke-width='{w}' stroke-linejoin='round' stroke-linecap='round' {extra}/>"


HG = (12, 2)                       # 頭のずらし（頭の形は lucky_pony と同じなかま：右を向いた丸い鼻先）
HEAD = ('M98 22 C122 22 140 32 148 48 C151 55 153 60 157 64 C170 69 179 82 179 98 '
        'C179 117 163 129 141 130 C126 131 112 131 98 130 C82 128 70 120 62 110 C55 100 50 86 50 70 C50 42 72 22 98 22 Z')
TORSO = 'M86 138 C72 158 64 188 66 220 C68 238 84 245 130 245 C176 245 192 238 194 220 C197 188 190 158 176 138 Z'
HAUNCH_L = 'M44 222 C44 204 56 194 72 194 C88 194 98 206 98 222 C98 238 86 246 70 246 C54 246 44 238 44 222 Z'
HAUNCH_R = 'M158 222 C158 206 168 194 184 194 C200 194 212 204 212 222 C212 238 202 246 186 246 C170 246 158 238 158 222 Z'
ARM_UP = 'M104 152 C88 159 68 161 57 151 C48 143 43 128 43 111 L69 108 C70 121 74 129 82 133 C89 137 97 138 104 138 Z'
ARM_UP_LN = 'M104 152 C88 159 68 161 57 151 C48 143 43 128 43 111 M69 108 C70 121 74 129 82 133 C89 137 97 138 104 138'
ARM_KB = 'M156 146 C170 146 184 154 184 172 C184 190 180 204 172 212 L156 206 C160 194 162 182 160 168 C159 160 158 152 156 146 Z'
ARM_KB_LN = 'M156 146 C170 146 184 154 184 172 C184 190 180 204 172 212 M156 206 C160 194 162 182 160 168 C159 160 158 152 156 146'


def maneki_svg(w=VB_W, h=VB_H):
    s = []
    s.append("<defs>"
             f"<clipPath id='mk_head'><path d='{HEAD}'/></clipPath>"
             f"<clipPath id='mk_torso'><path d='{TORSO}'/></clipPath>"
             "<linearGradient id='mk_ear' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#E8352E'/><stop offset='1' stop-color='#F9A23B'/></linearGradient>"
             "<linearGradient id='mk_kb' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#FFF4B8'/><stop offset='0.42' stop-color='#F5C542'/>"
             "<stop offset='1' stop-color='#D18A22'/></linearGradient>"
             "<linearGradient id='mk_bell' x1='0' y1='0' x2='0.6' y2='1'><stop offset='0' stop-color='#FFF4B8'/><stop offset='0.5' stop-color='#F5C542'/>"
             "<stop offset='1' stop-color='#C98420'/></linearGradient>"
             "<radialGradient id='mk_eye' cx='0.5' cy='0.62' r='0.62'><stop offset='0' stop-color='#FFD65A'/><stop offset='0.7' stop-color='#F2A12C'/>"
             "<stop offset='1' stop-color='#C8641C'/></radialGradient>"
             "</defs>")
    # ---------- しっぽ（右うしろ・金） ----------
    s.append(P('M192 204 C212 200 226 186 228 168 C222 174 216 176 211 174 C220 163 219 148 210 141 C210 153 206 163 198 167 L 194 200 Z', GOLD))
    s.append(f"<path d='M210 150 C214 158 213 166 206 172' fill='none' stroke='{GOLD_SH}' stroke-width='3' stroke-linecap='round'/>")
    # ---------- たてがみ（頭のうしろ・左） ----------
    s.append(f"<g transform='translate({HG[0]} {HG[1]})'>")
    s.append(P('M66 40 C48 44 38 60 42 78 C32 88 32 104 42 112 C34 122 38 136 50 142 C54 134 62 130 72 130 L72 50 Z', GOLD))
    s.append(f"<path d='M47 66 C42 76 42 86 46 94 M44 108 C40 116 42 126 48 134' fill='none' stroke='{GOLD_SH}' stroke-width='3' stroke-linecap='round'/>")
    s.append('</g>')
    # ---------- 体：線を先にぬって、上から白 ----------
    s.append(f"<g fill='{OUT}' stroke='{OUT}' stroke-width='{LW * 2}' stroke-linejoin='round'><path d='{TORSO}'/><path d='{HAUNCH_L}'/><path d='{HAUNCH_R}'/></g>")
    s.append(f"<g fill='{WHITE}'><path d='{TORSO}'/><path d='{HAUNCH_L}'/><path d='{HAUNCH_R}'/></g>")
    # 影（右がわ・首の下・もものした）
    s.append(f"<g clip-path='url(#mk_torso)'><path d='M174 140 C188 162 194 196 190 240 L210 240 L210 130 Z' fill='{SHADE}'/>"
             f"<path d='M80 140 C100 160 160 162 182 140 L182 160 C160 176 102 176 80 158 Z' fill='{SHADE}'/></g>")
    s.append(f"<path d='M162 232 C172 240 198 240 208 228 C206 240 196 246 186 246 C174 246 164 240 162 232 Z' fill='{SHADE}'/>")
    s.append(f"<path d='M48 232 C58 240 84 240 94 230 C92 240 84 246 70 246 C58 246 50 240 48 232 Z' fill='{SHADE}'/>")
    # ももの前のふちの線
    s.append(L('M94 206 C100 216 100 230 94 240'))
    s.append(L('M162 206 C156 216 156 230 162 240'))
    # かざりの丸（招き猫ふう：金の丸に赤いふち）
    s.append(f"<circle cx='66' cy='215' r='8.5' fill='{RED}' stroke='{OUT}' stroke-width='2.2'/>")
    s.append(f"<circle cx='66' cy='215' r='4.8' fill='{GOLD}'/>")
    # うしろ足のひづめ（金）
    for cx in (84, 172):
        s.append(f"<ellipse cx='{cx}' cy='240' rx='16' ry='8.5' fill='{GOLD}' stroke='{OUT}' stroke-width='{LW2 + 0.6}'/>")
        s.append(f"<path d='M{cx - 9} 237 C{cx - 4} 234 {cx + 4} 234 {cx + 9} 237' fill='none' stroke='{GOLD_HI}' stroke-width='2.4' stroke-linecap='round'/>")
    # ---------- 小判（おなかの前） ----------
    kx, ky = 128, 195
    s.append(f"<g transform='rotate(-6 {kx} {ky})'>")
    s.append(P(f'M{kx} {ky - 37} C{kx + 18} {ky - 37} {kx + 27} {ky - 20} {kx + 27} {ky} C{kx + 27} {ky + 20} {kx + 18} {ky + 37} {kx} {ky + 37} '
               f'C{kx - 18} {ky + 37} {kx - 27} {ky + 20} {kx - 27} {ky} C{kx - 27} {ky - 20} {kx - 18} {ky - 37} {kx} {ky - 37} Z', 'url(#mk_kb)'))
    s.append(f"<ellipse cx='{kx}' cy='{ky}' rx='20' ry='29' fill='none' stroke='{GOLD_SH}' stroke-width='1.6'/>")
    for k in range(-8, 9):
        y = ky + k * 3.3
        hw = 19.0 * math.sqrt(max(0.0, 1 - ((y - ky) / 28.5) ** 2))
        if hw > 3 and abs(k) > 4:
            s.append(f"<line x1='{kx - hw:.1f}' y1='{y:.1f}' x2='{kx + hw:.1f}' y2='{y:.1f}' stroke='{GOLD_SH}' stroke-width='1.1' opacity='0.8'/>")
    s.append(f"<rect x='{kx - 9}' y='{ky - 17}' width='18' height='34' rx='2' fill='#FFF6D0' stroke='{GOLD_SH}' stroke-width='1.4'/>")
    s.append(f"<text x='{kx}' y='{ky - 2}' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='14' fill='{RED}' text-anchor='middle'>千</text>")
    s.append(f"<text x='{kx}' y='{ky + 13.5}' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='14' fill='{RED}' text-anchor='middle'>両</text>")
    s.append(f"<path d='M{kx - 18} {ky - 18} C{kx - 15} {ky - 27} {kx - 8} {ky - 32} {kx} {ky - 33}' fill='none' stroke='#FFFFFF' stroke-width='3' stroke-linecap='round' opacity='0.9'/>")
    s.append("</g>")
    # ---------- 小判をだく左前足 ----------
    s.append(f"<path d='{ARM_KB}' fill='{WHITE}'/>")
    s.append(f"<path d='M174 156 C182 168 182 190 176 204 L168 208 C174 192 174 172 168 160 Z' fill='{SHADE}'/>")
    s.append(L(ARM_KB_LN, LW))
    s.append(P('M150 212 C148 202 156 196 166 197 C176 198 182 206 178 214 C175 220 162 222 156 219 C152 217 151 215 150 212 Z', GOLD, LW2 + 0.6))
    s.append(f"<path d='M157 204 C161 200 168 200 172 203' fill='none' stroke='{GOLD_HI}' stroke-width='2.4' stroke-linecap='round'/>")
    # ---------- 首輪と鈴 ----------
    s.append(P('M80 130 C100 146 156 148 178 132 L180 144 C156 162 100 160 78 144 Z', RED, LW2 + 0.4))
    s.append(L('M81 135 C102 150 154 152 178 137', 1.8, GOLD))
    s.append(L('M79 141 C100 156 156 158 179 142', 1.8, GOLD))
    s.append(f"<circle cx='130' cy='158' r='12' fill='url(#mk_bell)' stroke='{OUT}' stroke-width='{LW2}'/>")
    s.append(L('M119 156 L141 156', 2.2))
    s.append(f"<circle cx='130' cy='162.5' r='2.4' fill='{OUT}'/>")
    s.append(L('M130 163 L130 168.5', 2.2))
    s.append("<circle cx='125.5' cy='152.5' r='2.6' fill='#FFFFFF'/>")
    # ---------- 耳・頭・顔（頭のずらし HG） ----------
    s.append(f"<g transform='translate({HG[0]} {HG[1]})'>")
    s.append(P('M70 38 C63 27 62 14 66 6 C68 2 72 2 76 4 C86 10 94 19 98 30 Z', WHITE))
    s.append("<path d='M74 32 C70 24 70 16 73 10 C81 15 88 22 91 29 Z' fill='url(#mk_ear)'/>")
    s.append(P('M110 28 C113 18 122 9 133 5 C137 3 140 5 140 9 C141 19 139 29 132 38 Z', WHITE))
    s.append("<path d='M116 27 C119 19 126 13 134 10 C136 18 134 26 129 32 Z' fill='url(#mk_ear)'/>")
    s.append(P(HEAD, WHITE))
    s.append(f"<g clip-path='url(#mk_head)'>"
             f"<path d='M150 46 C166 60 176 80 178 100 C178 118 166 128 150 132 L200 140 L200 30 Z' fill='{SHADE}'/>"
             f"<ellipse cx='141' cy='105' rx='42' ry='27.5' fill='{MUZ}' transform='rotate(6 141 105)'/>"
             f"<path d='M100 124 C120 134 152 132 176 116 L182 140 L96 140 Z' fill='{MUZ_SH}'/>"
             "</g>")
    s.append(f"<path d='{HEAD}' fill='none' stroke='{OUT}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(P('M80 38 C78 26 88 16 101 16 C113 16 121 24 120 33 C119 40 113 44 107 42 C110 38 109 33 105 32 '
               'C101 31 98 34 98 38 C95 36 91 36 88 39 C85 42 81 42 80 38 Z', GOLD, LW2 + 0.8))
    s.append(f"<path d='M88 26 C92 21.5 99 20 105 21' fill='none' stroke='{GOLD_HI}' stroke-width='2.6' stroke-linecap='round'/>")
    # 目の上の赤いかざり（招き猫ふう）
    s.append("<path d='M80 58 C85 51 95 48 105 51 C97 52 90 55 85 61 Z' fill='#E8452C'/>")
    s.append("<path d='M128 52 C135 47 145 48 151 54 C145 52 138 52 131 55 Z' fill='#E8452C'/>")
    # 目（金色のひとみ・黒いひとみ孔・白い光）
    for (cx, cy, rx, ry) in ((95, 76, 10.5, 12.5), (139, 72, 8.0, 11.0)):
        s.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{OUT}'/>")
        s.append(f"<ellipse cx='{cx}' cy='{cy + ry * 0.12:.1f}' rx='{rx * 0.78:.1f}' ry='{ry * 0.80:.1f}' fill='url(#mk_eye)'/>")
        s.append(f"<ellipse cx='{cx}' cy='{cy + ry * 0.05:.1f}' rx='{rx * 0.42:.1f}' ry='{ry * 0.62:.1f}' fill='{OUT}'/>")
        s.append(f"<circle cx='{cx - rx * 0.28:.1f}' cy='{cy - ry * 0.40:.1f}' r='{rx * 0.30:.1f}' fill='#FFFFFF'/>")
        s.append(f"<circle cx='{cx + rx * 0.30:.1f}' cy='{cy + ry * 0.30:.1f}' r='{rx * 0.14:.1f}' fill='#FFFFFF'/>")
    # ほっぺ・鼻の穴・口
    s.append(f"<ellipse cx='80' cy='100' rx='10' ry='6' fill='{PINK}' opacity='0.9'/>")
    s.append(f"<ellipse cx='146' cy='104' rx='3.4' ry='4.2' fill='{OUT}' transform='rotate(-10 146 104)'/>")
    s.append(f"<ellipse cx='162.5' cy='100' rx='2.8' ry='3.6' fill='{OUT}' transform='rotate(12 162.5 100)'/>")
    s.append(f"<path d='M128 115 C134 125 152 126 160 114 C152 118 136 118 128 115 Z' fill='#C9343B' stroke='{OUT}' stroke-width='2.4' stroke-linejoin='round'/>")
    s.append(f"<path d='M136 119 C140 123 148 123 152 119' fill='none' stroke='#F49AA0' stroke-width='3' stroke-linecap='round'/>")
    s.append('</g>')
    # ---------- あげた右前足（招く・いちばん手前） ----------
    s.append(f"<path d='{ARM_UP}' fill='{WHITE}'/>")
    s.append(f"<path d='M47 118 C47 132 51 144 60 150 C72 156 90 154 102 150 L102 146 C88 150 72 150 64 144 C57 138 54 128 53 118 Z' fill='{SHADE}'/>")
    s.append(L(ARM_UP_LN, LW))
    s.append(f"<circle cx='58' cy='134' r='6' fill='{RED}' stroke='{OUT}' stroke-width='1.8'/>")
    s.append(f"<circle cx='58' cy='134' r='3.2' fill='{GOLD}'/>")
    # ひづめ（ふちは金・裏はうすい桃色）
    s.append(P('M36 108 C32 94 41 83 55 83 C69 83 78 93 75 106 C73 115 63 120 52 119 C44 118 38 114 36 108 Z', GOLD, LW2 + 0.6))
    s.append("<path d='M42 104 C40 95 46 89 55 89 C64 89 70 95 68 103 C66 110 59 113 52 112 C47 111 43 108 42 104 Z' fill='#F9C6C4'/>")
    s.append(f"<path d='M45 91 C49 87 57 86 62 88' fill='none' stroke='{GOLD_HI}' stroke-width='2.2' stroke-linecap='round'/>")
    # ---------- キラキラ ----------
    for (x, y, r, rot) in ((24, 70, 7.5, 0.0), (214, 112, 6.0, 0.3), (28, 160, 4.6, 0.2), (204, 28, 5.2, 0.0)):
        s.append(star4(x, y, r, '#FFD45A', rot=rot, k=0.25))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {VB_W} {VB_H}'>" + ''.join(s) + "</svg>")


if __name__ == '__main__':
    open(sys.argv[1], 'w').write(maneki_svg())
    print(sys.argv[1])
