"""開運の「招き馬」のキャラクター（SVG・240×256・アニメの塗り）
   招き猫のような白い馬：白い体に黒い太い線、赤い耳の中と目の上の赤いかざり、金のたてがみ・前髪・しっぽ・ひづめ。
   顔は正面向き（上が広く、下の鼻先がまるい馬の顔・正面の鼻の穴・うすく笑う口）。目は丸みのあるつり目で、金色に横長のひとみ（少し不気味）。
   右前足は体の横から出して、あごの横の高さにあげて招く（首輪にかからない・ひづめの裏はうすい桃色）。左前足で「千両」の小判をだく。
   赤い首輪に金の鈴。影は青みの灰色1段（くっきり）。形はすべて一から作ったオリジナル
   python3 flat/lucky_maneki.py <出力.svg>（確かめ用）"""
import sys, math

VB_W, VB_H = 240, 270
BY = 14                            # 体のずらし（頭が長くなったぶん下へ）
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


HEAD = ('M120 28 C150 28 172 44 178 68 C182 82 182 96 176 108 C171 118 166 126 164 136 C162 146 166 154 162 160 '
        'C156 168 140 170 120 170 C100 170 84 168 78 160 C74 154 78 146 76 136 C74 126 69 118 64 108 C58 96 58 82 62 68 C68 44 90 28 120 28 Z')
TORSO = 'M78 146 C64 166 56 196 58 226 C60 242 76 249 120 249 C164 249 180 242 182 226 C184 196 176 166 162 146 Z'
HAUNCH_L = 'M38 228 C38 210 50 200 66 200 C82 200 92 212 92 228 C92 244 80 252 64 252 C48 252 38 244 38 228 Z'
HAUNCH_R = 'M148 228 C148 212 158 200 174 200 C190 200 202 210 202 228 C202 244 192 252 176 252 C160 252 148 244 148 228 Z'
ARM_UP = 'M82 188 C68 194 50 194 41 186 C33 178 29 162 30 146 L55 143 C55 154 58 162 64 168 C70 173 76 175 82 175 Z'
ARM_UP_LN = 'M82 188 C68 194 50 194 41 186 C33 178 29 162 30 146 M55 143 C55 154 58 162 64 168 C70 173 76 175 82 175'
ARM_KB = 'M150 162 C164 162 178 170 178 188 C178 206 174 220 166 228 L150 222 C154 210 156 198 154 184 C153 176 152 168 150 162 Z'
ARM_KB_LN = 'M150 162 C164 162 178 170 178 188 C178 206 174 220 166 228 M150 222 C154 210 156 198 154 184 C153 176 152 168 150 162'
EYE_L = 'M105 95 C101 76 86 70 77 84 C79 98 95 104 105 95 Z'          # つり目で少し丸い（外がつり上がる）
EYE_R = 'M135 95 C139 76 154 70 163 84 C161 98 145 104 135 95 Z'
LID_L = 'M105 95 C101 76 86 70 77 84'
LID_R = 'M135 95 C139 76 154 70 163 84'


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
             "<radialGradient id='mk_eye' cx='0.5' cy='0.55' r='0.6'><stop offset='0' stop-color='#FFF07A'/><stop offset='0.6' stop-color='#F6C437'/>"
             "<stop offset='1' stop-color='#D9861E'/></radialGradient>"
             f"<clipPath id='mk_eyeL'><path d='{EYE_L}'/></clipPath><clipPath id='mk_eyeR'><path d='{EYE_R}'/></clipPath>"
             "</defs>")
    G0 = f"<g transform='translate(0 {BY})'>"
    # ---------- しっぽ（右うしろ・金） ----------
    s.append(G0)
    s.append(P('M184 212 C204 208 218 194 220 176 C214 182 208 184 203 182 C212 171 211 156 202 149 C202 161 198 171 190 175 L 186 208 Z', GOLD))
    s.append(f"<path d='M202 158 C206 166 205 174 198 180' fill='none' stroke='{GOLD_SH}' stroke-width='3' stroke-linecap='round'/>")
    s.append('</g>')
    # ---------- たてがみ（頭のうしろ・左に流れる） ----------
    s.append(P('M70 58 C52 62 42 78 46 96 C38 106 39 122 50 130 C46 142 52 156 66 162 L80 150 L74 64 Z', GOLD))
    s.append(f"<path d='M52 84 C48 94 48 104 52 112 M50 128 C48 136 52 144 58 148' fill='none' stroke='{GOLD_SH}' stroke-width='3' stroke-linecap='round'/>")
    # ---------- 体：線を先にぬって、上から白 ----------
    s.append(G0)
    s.append(f"<g fill='{OUT}' stroke='{OUT}' stroke-width='{LW * 2}' stroke-linejoin='round'><path d='{TORSO}'/><path d='{HAUNCH_L}'/><path d='{HAUNCH_R}'/></g>")
    s.append(f"<g fill='{WHITE}'><path d='{TORSO}'/><path d='{HAUNCH_L}'/><path d='{HAUNCH_R}'/></g>")
    s.append(f"<g clip-path='url(#mk_torso)'><path d='M160 148 C174 170 180 204 176 248 L200 248 L200 138 Z' fill='{SHADE}'/>"
             f"<path d='M74 150 C92 170 148 172 166 150 L166 172 C148 188 92 188 74 170 Z' fill='{SHADE}'/></g>")
    s.append(f"<path d='M152 238 C162 246 188 246 198 234 C196 246 186 252 176 252 C164 252 154 246 152 238 Z' fill='{SHADE}'/>")
    s.append(f"<path d='M42 238 C52 246 78 246 88 236 C86 246 78 252 64 252 C52 252 44 246 42 238 Z' fill='{SHADE}'/>")
    s.append(L('M88 212 C94 222 94 236 88 246'))
    s.append(L('M152 212 C146 222 146 236 152 246'))
    s.append(f"<circle cx='62' cy='222' r='8.5' fill='{RED}' stroke='{OUT}' stroke-width='2.2'/>")
    s.append(f"<circle cx='62' cy='222' r='4.8' fill='{GOLD}'/>")
    for cx in (78, 162):
        s.append(f"<ellipse cx='{cx}' cy='246' rx='16' ry='8.5' fill='{GOLD}' stroke='{OUT}' stroke-width='{LW2 + 0.6}'/>")
        s.append(f"<path d='M{cx - 9} 243 C{cx - 4} 240 {cx + 4} 240 {cx + 9} 243' fill='none' stroke='{GOLD_HI}' stroke-width='2.4' stroke-linecap='round'/>")
    # ---------- 小判（おなかの前） ----------
    kx, ky = 122, 214
    s.append(f"<g transform='rotate(-5 {kx} {ky})'>")
    s.append(P(f'M{kx} {ky - 35} C{kx + 17} {ky - 35} {kx + 26} {ky - 19} {kx + 26} {ky} C{kx + 26} {ky + 19} {kx + 17} {ky + 35} {kx} {ky + 35} '
               f'C{kx - 17} {ky + 35} {kx - 26} {ky + 19} {kx - 26} {ky} C{kx - 26} {ky - 19} {kx - 17} {ky - 35} {kx} {ky - 35} Z', 'url(#mk_kb)'))
    s.append(f"<ellipse cx='{kx}' cy='{ky}' rx='19.5' ry='27.5' fill='none' stroke='{GOLD_SH}' stroke-width='1.6'/>")
    for k in range(-8, 9):
        y = ky + k * 3.2
        hw = 18.5 * math.sqrt(max(0.0, 1 - ((y - ky) / 27.0) ** 2))
        if hw > 3 and abs(k) > 4:
            s.append(f"<line x1='{kx - hw:.1f}' y1='{y:.1f}' x2='{kx + hw:.1f}' y2='{y:.1f}' stroke='{GOLD_SH}' stroke-width='1.1' opacity='0.8'/>")
    s.append(f"<rect x='{kx - 9}' y='{ky - 17}' width='18' height='34' rx='2' fill='#FFF6D0' stroke='{GOLD_SH}' stroke-width='1.4'/>")
    s.append(f"<text x='{kx}' y='{ky - 2}' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='14' fill='{RED}' text-anchor='middle'>千</text>")
    s.append(f"<text x='{kx}' y='{ky + 13.5}' font-family='Noto Serif CJK JP, serif' font-weight='900' font-size='14' fill='{RED}' text-anchor='middle'>両</text>")
    s.append(f"<path d='M{kx - 17} {ky - 17} C{kx - 14} {ky - 26} {kx - 8} {ky - 31} {kx} {ky - 32}' fill='none' stroke='#FFFFFF' stroke-width='3' stroke-linecap='round' opacity='0.9'/>")
    s.append("</g>")
    # ---------- 小判をだく左前足 ----------
    s.append(f"<path d='{ARM_KB}' fill='{WHITE}'/>")
    s.append(f"<path d='M168 172 C176 184 176 206 170 220 L162 224 C168 208 168 188 162 176 Z' fill='{SHADE}'/>")
    s.append(L(ARM_KB_LN, LW))
    s.append(P('M144 228 C142 218 150 212 160 213 C170 214 176 222 172 230 C169 236 156 238 150 235 C146 233 145 231 144 228 Z', GOLD, LW2 + 0.6))
    s.append(f"<path d='M151 220 C155 216 162 216 166 219' fill='none' stroke='{GOLD_HI}' stroke-width='2.4' stroke-linecap='round'/>")
    # ---------- 首輪と鈴 ----------
    s.append(P('M80 150 C96 166 144 166 160 150 L162 162 C144 180 96 180 78 162 Z', RED, LW2 + 0.4))
    s.append(L('M81 155 C98 170 142 170 160 155', 1.8, GOLD))
    s.append(L('M79 160 C96 176 144 176 161 160', 1.8, GOLD))
    s.append(f"<circle cx='120' cy='180' r='12' fill='url(#mk_bell)' stroke='{OUT}' stroke-width='{LW2}'/>")
    s.append(L('M109 178 L131 178', 2.2))
    s.append(f"<circle cx='120' cy='184.5' r='2.4' fill='{OUT}'/>")
    s.append(L('M120 185 L120 190.5', 2.2))
    s.append("<circle cx='115.5' cy='174.5' r='2.6' fill='#FFFFFF'/>")
    s.append('</g>')
    # ---------- 耳・頭・顔（正面） ----------
    s.append(P('M70 52 C63 36 62 16 68 4 C82 12 96 26 101 40 Z', WHITE))
    s.append("<path d='M74 44 C69 32 69 20 72 12 C82 19 91 29 95 38 Z' fill='url(#mk_ear)'/>")
    s.append(P('M170 52 C177 36 178 16 172 4 C158 12 144 26 139 40 Z', WHITE))
    s.append("<path d='M166 44 C171 32 171 20 168 12 C158 19 149 29 145 38 Z' fill='url(#mk_ear)'/>")
    s.append(P(HEAD, WHITE))
    s.append(f"<g clip-path='url(#mk_head)'>"
             f"<path d='M164 44 C178 62 184 88 178 112 C170 128 166 150 152 168 L200 176 L200 30 Z' fill='{SHADE}'/>"
             f"<ellipse cx='120' cy='149' rx='41' ry='22' fill='{MUZ}'/>"
             f"<path d='M78 160 C98 172 142 172 162 160 L166 176 L74 176 Z' fill='{MUZ_SH}'/>"
             "</g>")
    s.append(f"<path d='{HEAD}' fill='none' stroke='{OUT}' stroke-width='{LW}' stroke-linejoin='round'/>")
    s.append(L('M71 106 C79 114 83 124 81 134', 2.4))
    s.append(L('M169 106 C161 114 157 124 159 134', 2.4))
    # 前髪（金・まん中から右へくるん）
    s.append(P('M100 42 C98 28 108 18 122 18 C136 18 146 28 143 40 C141 48 133 51 127 48 C131 44 131 38 126 36 '
               'C122 35 118 38 119 43 C113 40 106 42 103 46 C101 47 100 45 100 42 Z', GOLD, LW2 + 0.8))
    s.append(f"<path d='M108 28 C113 23 121 22 127 23' fill='none' stroke='{GOLD_HI}' stroke-width='2.6' stroke-linecap='round'/>")
    # 目の上の赤いかざり（内がわが下がる・鋭く）
    s.append("<path d='M106 67 C98 59 86 55 74 57 C84 53 98 53 108 63 Z' fill='#E23B2A'/>")
    s.append("<path d='M134 67 C142 59 154 55 166 57 C156 53 142 53 132 63 Z' fill='#E23B2A'/>")
    # 目：切れ長の金色・横長のひとみ・上まぶたの太い線・外がわの赤いはね
    for (E, cid, cx, cy, ang, wing) in ((EYE_L, 'mk_eyeL', 91, 88.5, 17.0, 'M79 83 L68 77 L76 87 Z'),
                                         (EYE_R, 'mk_eyeR', 149, 88.5, -17.0, 'M161 83 L172 77 L164 87 Z')):
        s.append(f"<path d='{E}' fill='url(#mk_eye)'/>")
        s.append(f"<g clip-path='url(#{cid})'><rect x='{cx - 7.2}' y='{cy - 3.7}' width='14.4' height='7.4' rx='3.7' fill='{OUT}' transform='rotate({ang} {cx} {cy})'/>"
                 f"<path d='{E}' fill='none' stroke='#B8601A' stroke-width='3' opacity='0.55'/></g>")
        s.append(f"<path d='{E}' fill='none' stroke='{OUT}' stroke-width='2.4' stroke-linejoin='round'/>")
        s.append(f"<path d='{wing}' fill='#E23B2A' stroke='{OUT}' stroke-width='1.2' stroke-linejoin='round'/>")
        s.append(f"<circle cx='{cx - 4 if cx < 120 else cx + 4}' cy='{cy - 6}' r='1.8' fill='#FFFFFF'/>")
    s.append(L(LID_L, 4.2))
    s.append(L(LID_R, 4.2))
    # 鼻の穴（正面）・口（うすく笑う）
    s.append("<path d='M102 146 C98 150 98 158 103 160 C106 161 108 158 107 154 C106 151 104 149 102 146 Z' fill='#4A2E36'/>")
    s.append("<path d='M138 146 C142 150 142 158 137 160 C134 161 132 158 133 154 C134 151 136 149 138 146 Z' fill='#4A2E36'/>")
    s.append(L('M104 165 C112 169.5 128 169.5 136 165', 2.5))
    s.append(L('M102.5 162.5 L104.8 165.4', 2.0))
    s.append(L('M137.5 162.5 L135.2 165.4', 2.0))
    # ---------- あげた右前足（体の横から・あごの横の高さ） ----------
    s.append(G0)
    s.append(f"<path d='{ARM_UP}' fill='{WHITE}'/>")
    s.append(f"<path d='M34 152 C34 166 38 178 46 184 C56 190 70 190 80 186 L80 182 C70 186 58 186 50 180 C43 174 40 164 40 152 Z' fill='{SHADE}'/>")
    s.append(L(ARM_UP_LN, LW))
    s.append(f"<circle cx='44' cy='174' r='6' fill='{RED}' stroke='{OUT}' stroke-width='1.8'/>")
    s.append(f"<circle cx='44' cy='174' r='3.2' fill='{GOLD}'/>")
    s.append(P('M24 140 C20 126 29 115 43 115 C57 115 66 125 63 138 C61 147 51 152 40 151 C32 150 26 146 24 140 Z', GOLD, LW2 + 0.6))
    s.append("<path d='M30 136 C28 127 34 121 43 121 C52 121 58 127 56 135 C54 142 47 145 40 144 C35 143 31 140 30 136 Z' fill='#F9C6C4'/>")
    s.append(f"<path d='M33 123 C37 119 45 118 50 120' fill='none' stroke='{GOLD_HI}' stroke-width='2.2' stroke-linecap='round'/>")
    s.append('</g>')
    # ---------- キラキラ ----------
    for (x, y, r, rot) in ((26, 76, 7.5, 0.0), (214, 118, 6.0, 0.3), (18, 200, 4.6, 0.2), (204, 30, 5.2, 0.0)):
        s.append(star4(x, y, r, '#FFD45A', rot=rot, k=0.25))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {VB_W} {VB_H}'>" + ''.join(s) + "</svg>")


if __name__ == '__main__':
    open(sys.argv[1], 'w').write(maneki_svg())
    print(sys.argv[1])
