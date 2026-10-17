"""開運の馬のキャラクター（SVG・214×212）：右を向いておすわりした子馬。顔はななめ向きで、まるい大きな鼻先。
   近いほうの前足（右前足）を顔の横にあげて福を招き（右の前足は金運）、遠いほうの前足で「千両」の小判をだく。緑の首輪に金の鈴。
   クリーム色の体・茶色のたてがみと前髪・太いこげ茶の線・ベタぬり・小さな目・にっこり口・ほっぺ。
   参考にした子馬のイラストはふんいき（色・線・ゆるい顔）だけ。形・ポーズ・向きはすべて一から作ったオリジナル
   python3 flat/lucky_pony.py <出力.svg>（確かめ用）"""
import sys, math

VB_W, VB_H = 214, 212
OUT = '#5E3F1E'          # 線
LW = 4.2
BODY = '#F5D485'         # 体（金色がかったクリーム）
MUZ = '#FCE9BE'          # 鼻先
SHADE = '#E9C26F'        # 首の下のかげ
HAIR = '#9C6A3A'         # たてがみ・しっぽ・ひづめ
HAIR_HI = '#B98654'
EYE = '#4A3017'
CHEEK = '#F3A387'
EAR_IN = '#F2C08E'


def star4(cx, cy, r, fill, rot=0.0, k=0.28):
    pts = []
    for i in range(8):
        a = rot + i * math.pi / 4
        rr = r if i % 2 == 0 else r * k
        pts.append(f'{cx + math.cos(a) * rr:.2f},{cy + math.sin(a) * rr:.2f}')
    return f"<polygon points='{' '.join(pts)}' fill='{fill}'/>"


def P(d, fill, extra=''):
    return f"<path d='{d}' fill='{fill}' stroke='{OUT}' stroke-width='{LW}' stroke-linejoin='round' stroke-linecap='round' {extra}/>"


HEAD = ('M98 22 C122 22 140 32 148 48 C151 55 153 60 157 64 C170 69 179 82 179 98 '
        'C179 117 163 129 141 130 C126 131 112 131 98 130 C82 128 70 120 62 110 C55 100 50 86 50 70 C50 42 72 22 98 22 Z')
TORSO = 'M60 150 C66 136 86 130 104 130 C124 130 142 136 148 150 C154 166 154 188 148 202 C140 208 74 208 64 202 C56 188 54 164 60 150 Z'
KX, KY = 124, 174
FORELOCK = ('M80 38 C78 26 88 16 101 16 C113 16 121 24 120 33 C119 40 113 44 107 42 C110 38 109 33 105 32 '
            'C101 31 98 34 98 38 C95 36 91 36 88 39 C85 42 81 42 80 38 Z')
ARM = 'M88 142 C80 144 70 144 64 141 C60 132 60 122 62 112 L42 110 C38 124 38 142 44 154 C50 162 72 163 88 160 Z'
ARM_LN = 'M88 160 C72 163 50 162 44 154 C38 142 38 124 42 110 M62 112 C60 122 60 132 64 141 C70 144 80 144 88 142'
HOOF_UP = 'M37 110 C35 99 43 91 52 91 C61 91 68 98 66 107 C65 114 58 118 49 117 C43 116 38 114 37 110 Z'
HAUNCH = 'M34 178 C34 158 48 146 66 146 C84 146 98 160 98 178 C98 196 86 206 66 206 C46 206 34 196 34 178 Z'


def pony_svg(w=VB_W, h=VB_H):
    s = []
    s.append("<defs>"
             f"<clipPath id='hc'><path d='{HEAD}'/></clipPath>"
             "<linearGradient id='kbG' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#FFF7CF'/><stop offset='0.45' stop-color='#F4CF58'/>"
             "<stop offset='1' stop-color='#C38E26'/></linearGradient>"
             "<linearGradient id='blG' x1='0' y1='0' x2='0.6' y2='1'><stop offset='0' stop-color='#FFF4C2'/><stop offset='0.5' stop-color='#F0C24C'/>"
             "<stop offset='1' stop-color='#B9861F'/></linearGradient>"
             "</defs>")
    # しっぽ（左うしろで上にくるん）
    s.append(P('M40 184 C24 182 12 170 12 154 C12 142 18 132 26 128 C24 138 28 146 34 146 C30 136 36 126 44 124 '
               'C42 134 46 142 52 146 L52 176 Z', HAIR))
    # たてがみ（頭のうしろ＝左がわ、首から肩へ）
    s.append(P('M66 40 C48 44 38 60 42 78 C32 88 32 104 42 112 C34 122 38 136 50 142 C54 134 62 130 72 130 L72 50 Z', HAIR))
    # 体（胴＋うしろ足のもも）：線を先にぬって、上から色
    s.append(f"<g fill='{OUT}' stroke='{OUT}' stroke-width='{LW * 2}' stroke-linejoin='round'><path d='{TORSO}'/><path d='{HAUNCH}'/></g>")
    s.append(f"<g fill='{BODY}'><path d='{TORSO}'/><path d='{HAUNCH}'/></g>")
    s.append(f"<path d='M92 166 C100 176 100 189 94 199' fill='none' stroke='{OUT}' stroke-width='{LW * 0.8}' stroke-linecap='round'/>")
    # 首の下のかげ
    s.append(f"<path d='M74 132 C90 146 124 148 144 140 C138 134 122 130 104 130 C92 130 82 130 74 132 Z' fill='{SHADE}'/>")
    # うしろ足のひづめ（ももの前）
    s.append(P('M78 197 C78 189 102 188 104 196 C104 204 80 206 78 197 Z', HAIR))
    s.append(f"<path d='M84 194 C88 191.5 96 191.5 100 193.5' fill='none' stroke='{HAIR_HI}' stroke-width='2' stroke-linecap='round'/>")
    # 遠いほうの前足（左前足）：小判のうしろから下へ
    s.append(P('M126 138 C138 136 150 142 150 156 C151 170 150 184 146 194 L128 194 C128 176 128 156 126 138 Z', BODY))
    # 小判（おなかの前）
    kx, ky = KX, KY
    s.append(f"<g transform='rotate(-9 {kx} {ky})'>")
    s.append(P(f'M{kx} {ky - 22} C{kx + 11} {ky - 22} {kx + 16} {ky - 12} {kx + 16} {ky} C{kx + 16} {ky + 12} {kx + 11} {ky + 22} {kx} {ky + 22} '
               f'C{kx - 11} {ky + 22} {kx - 16} {ky + 12} {kx - 16} {ky} C{kx - 16} {ky - 12} {kx - 11} {ky - 22} {kx} {ky - 22} Z', 'url(#kbG)'))
    s.append(f"<ellipse cx='{kx}' cy='{ky}' rx='11.6' ry='17.4' fill='none' stroke='#C38E26' stroke-width='1.2'/>")
    for k in range(-5, 6):
        y = ky + k * 3.2
        hw = 11.0 * math.sqrt(max(0.0, 1 - ((y - ky) / 17.4) ** 2))
        if hw > 3 and abs(k) > 2:
            s.append(f"<line x1='{kx - hw:.1f}' y1='{y:.1f}' x2='{kx + hw:.1f}' y2='{y:.1f}' stroke='#D9A63A' stroke-width='0.9'/>")
    s.append(f"<rect x='{kx - 6}' y='{ky - 12.5}' width='12' height='25' rx='1.6' fill='#FFF3C4' stroke='#B07A1C' stroke-width='1'/>")
    s.append(f"<text x='{kx}' y='{ky - 1.2}' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='10.5' fill='#6E4508' text-anchor='middle'>千</text>")
    s.append(f"<text x='{kx}' y='{ky + 10.4}' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='10.5' fill='#6E4508' text-anchor='middle'>両</text>")
    s.append(f"<path d='M{kx - 10} {ky - 12} C{kx - 8} {ky - 17} {kx - 4} {ky - 20} {kx + 1} {ky - 20}' fill='none' stroke='#FFFFFF' stroke-width='2' stroke-linecap='round' opacity='0.85'/>")
    s.append("</g>")
    # 遠いほうの前足のひづめ：小判の右下をささえる
    s.append(P('M128 196 C126 188 132 182 140 182 C148 182 154 188 152 196 C150 203 132 204 128 196 Z', HAIR))
    s.append(f"<path d='M133 189 C136 185.5 142 185 146 187' fill='none' stroke='{HAIR_HI}' stroke-width='2' stroke-linecap='round'/>")
    # 首輪と鈴
    s.append(f"<path d='M62 118 C80 136 128 140 150 126 L152 134 C130 150 78 146 60 126 Z' fill='#2F8F4E' stroke='#163F25' stroke-width='2.2' stroke-linejoin='round'/>")
    s.append(f"<circle cx='118' cy='141' r='7' fill='url(#blG)' stroke='{OUT}' stroke-width='2.2'/>")
    s.append(f"<path d='M112.4 141 L123.6 141' stroke='{OUT}' stroke-width='1.5' stroke-linecap='round'/>")
    s.append(f"<circle cx='118' cy='144.4' r='1.5' fill='{OUT}'/>")
    s.append("<circle cx='115.6' cy='138.2' r='1.7' fill='#FFFFFF' opacity='0.9'/>")
    # 耳（頭のうしろ）
    s.append(P('M70 38 C63 27 62 14 66 6 C68 2 72 2 76 4 C86 10 94 19 98 30 Z', BODY))
    s.append(f"<path d='M74 32 C70 24 70 16 73 10 C81 15 88 22 91 29 Z' fill='{EAR_IN}'/>")
    s.append(P('M110 28 C113 18 122 9 133 5 C137 3 140 5 140 9 C141 19 139 29 132 38 Z', BODY))
    s.append(f"<path d='M116 27 C119 19 126 13 134 10 C136 18 134 26 129 32 Z' fill='{EAR_IN}'/>")
    # 頭
    s.append(P(HEAD, BODY))
    s.append(f"<g clip-path='url(#hc)'><ellipse cx='141' cy='105' rx='42' ry='27.5' fill='{MUZ}' transform='rotate(6 141 105)'/></g>")
    s.append(f"<path d='{HEAD}' fill='none' stroke='{OUT}' stroke-width='{LW}' stroke-linejoin='round'/>")
    # 前髪（右へくるん）
    s.append(P(FORELOCK, HAIR))
    s.append(f"<path d='M88 26 C92 21.5 99 20 105 21' fill='none' stroke='{HAIR_HI}' stroke-width='2.2' stroke-linecap='round'/>")
    # 目
    for (cx, cy, rx, ry) in ((94, 74, 6.6, 8.8), (140, 70, 5.0, 7.6)):
        s.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{EYE}'/>")
        s.append(f"<circle cx='{cx + rx * 0.3:.1f}' cy='{cy - ry * 0.38:.1f}' r='{rx * 0.32:.1f}' fill='#FFFFFF'/>")
    # ほっぺ・鼻の穴・口
    s.append(f"<ellipse cx='86' cy='98' rx='11' ry='7' fill='{CHEEK}' opacity='0.85'/>")
    s.append(f"<ellipse cx='146' cy='104' rx='3' ry='3.6' fill='{EYE}'/>")
    s.append(f"<ellipse cx='162' cy='100' rx='2.5' ry='3.1' fill='{EYE}'/>")
    s.append(f"<path d='M130 114 C138 122 152 122 160 114' fill='none' stroke='{OUT}' stroke-width='3.4' stroke-linecap='round'/>")
    # 近いほうの前足（右前足）：顔の横にあげて福を招く（いちばん手前）
    s.append(f"<path d='{ARM}' fill='{BODY}'/>")
    s.append(f"<path d='{ARM_LN}' fill='none' stroke='{OUT}' stroke-width='{LW}' stroke-linejoin='round' stroke-linecap='round'/>")
    s.append(P(HOOF_UP, HAIR))
    s.append(f"<path d='M43 101 C45 96.5 50 94.5 55 95.5' fill='none' stroke='{HAIR_HI}' stroke-width='2' stroke-linecap='round'/>")
    # キラキラ
    for (x, y, r, rot) in ((190, 50, 6.0, 0.0), (22, 98, 4.6, 0.3), (196, 150, 4.2, 0.2), (176, 24, 3.8, 0.0)):
        s.append(star4(x, y, r, '#FFF6C8', rot=rot, k=0.25))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {VB_W} {VB_H}'>" + ''.join(s) + "</svg>")


if __name__ == '__main__':
    open(sys.argv[1], 'w').write(pony_svg())
    print(sys.argv[1])
