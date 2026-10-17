"""開運の馬のキャラクター（SVG・200×210）：金色の子馬が前を向いておすわりし、
   片方の前足をあげて「おいで」と福を招き、もう片方の前足で小判（千両）をだいている。
   緑の首輪に金の鈴・キラキラの目・ほっぺ・にっこり口。色は壁紙の緑と金に合わせる。形はすべて一から作ったオリジナル
   python3 flat/lucky_pony.py <出力.svg>（確かめ用）"""
import sys, math

OUT = '#6B4510'          # 線（こげ茶の金）
LW = 3.0


def star4(cx, cy, r, fill, rot=0.0, k=0.28):
    pts = []
    for i in range(8):
        a = rot + i * math.pi / 4
        rr = r if i % 2 == 0 else r * k
        pts.append(f'{cx + math.cos(a) * rr:.2f},{cy + math.sin(a) * rr:.2f}')
    return f"<polygon points='{' '.join(pts)}' fill='{fill}'/>"


def pony_svg(w=200, h=210):
    defs = (
        "<defs>"
        "<radialGradient id='gHead' cx='0.42' cy='0.32' r='0.75'><stop offset='0' stop-color='#FFF1B8'/><stop offset='0.55' stop-color='#F8D25E'/>"
        "<stop offset='1' stop-color='#E8AE3E'/></radialGradient>"
        "<radialGradient id='gBody' cx='0.40' cy='0.28' r='0.85'><stop offset='0' stop-color='#FFEBA6'/><stop offset='0.6' stop-color='#F6CB52'/>"
        "<stop offset='1' stop-color='#E3A63A'/></radialGradient>"
        "<linearGradient id='gMane' x1='0' y1='0' x2='0.3' y2='1'><stop offset='0' stop-color='#F7AA44'/><stop offset='1' stop-color='#D8701C'/></linearGradient>"
        "<linearGradient id='gKoban' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#FFF7CF'/><stop offset='0.45' stop-color='#F4CF58'/>"
        "<stop offset='1' stop-color='#C38E26'/></linearGradient>"
        "<linearGradient id='gBell' x1='0' y1='0' x2='0.6' y2='1'><stop offset='0' stop-color='#FFF4C2'/><stop offset='0.5' stop-color='#F0C24C'/>"
        "<stop offset='1' stop-color='#B9861F'/></linearGradient>"
        "<linearGradient id='gCollar' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#37A05A'/><stop offset='1' stop-color='#1A5E33'/></linearGradient>"
        "</defs>")
    s = []
    st = f"stroke='{OUT}' stroke-width='{LW}' stroke-linejoin='round' stroke-linecap='round'"
    # しっぽ（体のうしろ・右下でくるん）
    s.append(f"<path d='M138 172 C154 160 172 160 184 170 C178 170 174 174 176 180 C182 178 188 182 190 190 C182 186 176 188 174 196 "
             f"C168 190 160 190 154 196 C152 188 146 184 138 186 Z' fill='url(#gMane)' {st}/>")
    s.append("<path d='M150 172 C160 168 170 168 178 172' fill='none' stroke='#FFD089' stroke-width='2.2' stroke-linecap='round' opacity='0.85'/>")
    # たてがみ（頭のうしろ・両がわ）
    s.append(f"<path d='M128 34 C150 34 168 52 166 74 C174 84 172 100 162 108 C164 98 158 92 150 92 C154 84 150 74 142 70 Z' fill='url(#gMane)' {st}/>")
    s.append(f"<path d='M72 34 C52 36 36 52 38 72 C32 82 34 96 42 102 C42 92 48 86 54 84 C50 76 54 66 60 62 Z' fill='url(#gMane)' {st}/>")
    # 耳
    for sx in (1, -1):
        X = lambda x: 100 + (x - 100) * sx
        s.append(f"<path d='M{X(64)} 50 C{X(52)} 34 {X(46)} 16 {X(51)} 4 C{X(63)} 12 {X(77)} 26 {X(83)} 40 Z' fill='url(#gHead)' {st}/>")
        s.append(f"<path d='M{X(63)} 40 C{X(58)} 30 {X(55)} 20 {X(56)} 13 C{X(63)} 19 {X(70)} 27 {X(74)} 36 Z' fill='#F1A65E' opacity='0.85'/>")
    # 体（おすわり）・うしろ足のもも
    body = 'M64 124 C54 146 50 170 54 192 C58 202 142 202 146 192 C150 170 146 146 136 124 C122 116 78 116 64 124 Z'
    thighL = 'M46 186 C44 170 58 160 74 164 C86 168 88 186 80 196 C70 204 50 202 46 186 Z'
    thighR = 'M154 186 C156 170 142 160 126 164 C114 168 112 186 120 196 C130 204 150 202 154 186 Z'
    s.append(f"<g fill='{OUT}' stroke='{OUT}' stroke-width='{LW * 2}' stroke-linejoin='round'><path d='{body}'/><path d='{thighL}'/><path d='{thighR}'/></g>")
    s.append(f"<g fill='url(#gBody)'><path d='{body}'/><path d='{thighL}'/><path d='{thighR}'/></g>")
    s.append(f"<path d='M74 168 C80 176 82 188 78 196' fill='none' stroke='{OUT}' stroke-width='2.2' stroke-linecap='round' opacity='0.55'/>")
    s.append(f"<path d='M126 168 C120 176 118 188 122 196' fill='none' stroke='{OUT}' stroke-width='2.2' stroke-linecap='round' opacity='0.55'/>")
    s.append("<ellipse cx='100' cy='166' rx='25' ry='25' fill='#FFF2CC' opacity='0.95'/>")             # おなか
    # うしろ足のひづめ（前に出ている）
    for x in (58, 142):
        s.append(f"<path d='M{x - 13} 192 C{x - 13} 186 {x + 13} 186 {x + 13} 192 L{x + 12} 201 C{x + 6} 205 {x - 6} 205 {x - 12} 201 Z' fill='#C9862E' {st}/>")
        s.append(f"<path d='M{x - 8} 191 C{x - 3} 189 {x + 3} 189 {x + 8} 191' fill='none' stroke='#F2C27A' stroke-width='1.6' stroke-linecap='round'/>")
    # 小判（おなかの前）
    s.append(f"<ellipse cx='105' cy='167' rx='19.5' ry='27' fill='url(#gKoban)' {st}/>")
    s.append("<ellipse cx='105' cy='167' rx='14.5' ry='21.5' fill='none' stroke='#C38E26' stroke-width='1.3'/>")
    for k in range(-6, 7):
        y = 167 + k * 3.4
        hw = 14.0 * math.sqrt(max(0.0, 1 - ((y - 167) / 22.0) ** 2))
        if hw > 3:
            s.append(f"<line x1='{105 - hw:.1f}' y1='{y:.1f}' x2='{105 + hw:.1f}' y2='{y:.1f}' stroke='#D9A63A' stroke-width='0.9' opacity='0.8'/>")
    s.append("<rect x='98.5' y='152' width='13' height='29' rx='1.8' fill='#FFF3C4' stroke='#B07A1C' stroke-width='1'/>")
    s.append("<text x='105' y='165' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='12' fill='#6E4508' text-anchor='middle'>千</text>")
    s.append("<text x='105' y='178.5' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='12' fill='#6E4508' text-anchor='middle'>両</text>")
    s.append("<path d='M94 154 C96 149 100 146 104 145' fill='none' stroke='#FFFFFF' stroke-width='2' stroke-linecap='round' opacity='0.85'/>")
    # 小判をだく前足（右がわ）
    armR = 'M137 130 C148 144 148 164 138 174 C132 180 124 180 122 174 C120 166 128 160 130 150 Z'
    s.append(f"<path d='{armR}' fill='url(#gBody)' {st}/>")
    s.append(f"<path d='M132 174 C132 167 126 163 120 165 C114 168 114 177 119 181 C124 185 132 181 132 174 Z' fill='#C9862E' {st}/>")
    # 首輪と鈴
    s.append(f"<path d='M62 124 C80 136 120 136 138 124 L139 132 C120 145 80 145 61 132 Z' fill='url(#gCollar)' stroke='#123F22' stroke-width='2' stroke-linejoin='round'/>")
    # 頭（大きい丸＋鼻先）
    head = 'M100 26 C134 26 154 48 153 76 C152 92 144 102 138 108 C140 124 124 136 100 136 C76 136 60 124 62 108 C56 102 48 92 47 76 C46 48 66 26 100 26 Z'
    s.append(f"<path d='{head}' fill='url(#gHead)' {st}/>")
    s.append("<path d='M100 86 C124 86 138 98 137 112 C136 126 120 134 100 134 C80 134 64 126 63 112 C62 98 76 86 100 86 Z' fill='#FFF0C6'/>")   # 鼻先（明るい）
    s.append("<ellipse cx='84' cy='46' rx='15' ry='8' fill='#FFFFFF' opacity='0.35' transform='rotate(-18 84 46)'/>")                       # 頭のつや
    # 前髪（くるんと立つ）
    s.append(f"<path d='M86 40 C80 26 88 12 102 12 C116 12 124 24 118 34 C114 28 108 26 104 30 C110 32 112 40 106 44 C100 48 92 46 86 40 Z' fill='url(#gMane)' {st}/>")
    s.append("<path d='M94 24 C98 18 106 17 111 21' fill='none' stroke='#FFD089' stroke-width='2' stroke-linecap='round' opacity='0.85'/>")
    # 目（キラキラ）
    for cx in (80, 120):
        s.append(f"<ellipse cx='{cx}' cy='74' rx='8' ry='10' fill='#3A2410'/>")
        s.append(f"<ellipse cx='{cx}' cy='79' rx='5.5' ry='4' fill='#7A4A1C' opacity='0.9'/>")
        s.append(f"<circle cx='{cx - 3}' cy='70' r='3.2' fill='#FFFFFF'/>")
        s.append(star4(cx + 3.2, 78.5, 2.6, '#FFF3B0', rot=0.0, k=0.3))
    # ほっぺ・鼻の穴・口
    s.append("<ellipse cx='63' cy='96' rx='9' ry='6' fill='#FF9A86' opacity='0.55'/>")
    s.append("<ellipse cx='137' cy='96' rx='9' ry='6' fill='#FF9A86' opacity='0.55'/>")
    s.append("<ellipse cx='90' cy='104' rx='3.8' ry='2.6' fill='#9A6422' transform='rotate(25 90 104)'/>")
    s.append("<ellipse cx='110' cy='104' rx='3.8' ry='2.6' fill='#9A6422' transform='rotate(-25 110 104)'/>")
    s.append(f"<path d='M88 115 C93 125 107 125 112 115 C106 118 94 118 88 115 Z' fill='#E4736A' stroke='{OUT}' stroke-width='2.4' stroke-linejoin='round'/>")
    s.append("<path d='M95 121 C98 124 102 124 105 121' fill='none' stroke='#FF9F8F' stroke-width='1.6' stroke-linecap='round'/>")
    # 鈴（鼻先の下）
    s.append(f"<circle cx='100' cy='142' r='8.5' fill='url(#gBell)' stroke='{OUT}' stroke-width='2.2'/>")
    s.append(f"<path d='M93.5 142 L106.5 142' stroke='{OUT}' stroke-width='1.6' stroke-linecap='round'/>")
    s.append(f"<circle cx='100' cy='146' r='1.8' fill='{OUT}'/>")
    s.append(f"<path d='M100 146 L100 149.5' stroke='{OUT}' stroke-width='1.5' stroke-linecap='round'/>")
    s.append("<circle cx='97' cy='138.5' r='2' fill='#FFFFFF' opacity='0.9'/>")
    # あげた前足（左がわ：福を招く）
    armL = 'M66 132 C54 132 44 124 40 112 C36 102 38 92 44 88 C52 84 58 90 58 98 C58 106 62 114 70 118 Z'
    s.append(f"<path d='{armL}' fill='url(#gBody)' {st}/>")
    s.append(f"<path d='M37 92 C36 82 44 76 52 78 C58 80 60 88 56 94 C52 99 41 100 37 92 Z' fill='#C9862E' {st}/>")
    s.append("<path d='M42 84 C45 80 50 79 53 81' fill='none' stroke='#F2C27A' stroke-width='1.6' stroke-linecap='round'/>")
    # キラキラ（まわり）
    for (x, y, r, rot) in ((26, 66, 6.5, 0.0), (174, 120, 5.5, 0.4), (34, 140, 4.2, 0.2), (166, 44, 4.8, 0.0), (130, 186, 3.6, 0.3)):
        s.append(star4(x, y, r, '#FFF6C8', rot=rot, k=0.25))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 200 210'>{defs}{''.join(s)}</svg>"


if __name__ == '__main__':
    open(sys.argv[1], 'w').write(pony_svg())
    print(sys.argv[1])
