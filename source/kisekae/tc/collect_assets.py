# トレーニングセンターの 絵・形・音を アプリ用に 集める（ios/tc_assets/ に 名前だけで ならべる：build_ios.py が Resources/ に 入れる）
#   python3 collect_assets.py <作業フォルダ（h3d・user_icons・app_snd が ある 所）> [出す フォルダ ios/tc_assets]
#   ・まさちゃんの 絵（フィールド・馬の 3D・バケツと エサの 3D・うんち・アイテム・バナー・アイコン・ルーレット・扉と チケット）と それから 作った もの は
#     公開の リポジトリに 入れない（.gitignore：ios/tc_assets/）。この スクリプトだけ 入れる
#   ・PNG は 入れない（build_ios.py の きまり）：ゆれ・ライトの 地図は WebP（ロスレス＝値が かわらない）に する
#   ・第4.152版：おそうじの 絵と 形（tc_trash1〜4.webp・tc_prop_broom.*・tc_prop_pan.*）は kisekae/tc/clean_assets.py が 作る（<作業フォルダ>/clean_app/ に あれば ここで いっしょに 入れる）。
#     この スクリプトは 出す フォルダを 作り直す ので、clean_app/ が ない まま 走らせると おそうじの 絵と 形が なくなる → clean_assets.py <おそうじの 作業フォルダ> ios/tc_assets を もう一度
import json, os, shutil, sys
from PIL import Image
SRC = os.path.abspath(sys.argv[1]); H3 = os.path.join(SRC, 'h3d')
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..', 'ios', 'tc_assets'))
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
got = {}


def put(src, name=None):
    name = name or os.path.basename(src); assert '/' not in name and not name.lower().endswith('.png'), name
    assert name.lower() not in got, ('同じ 名前', name)
    shutil.copy(src, os.path.join(OUT, name)); got[name.lower()] = os.path.getsize(src)


def webp(src, name, lossless=False, size=None, q=90):
    im = Image.open(src); im.load()
    if size: im.thumbnail(size, Image.LANCZOS)
    if im.mode not in ('RGB', 'RGBA'): im = im.convert('RGBA')
    p = os.path.join(OUT, name); assert name.lower() not in got, name
    im.save(p, 'WEBP', lossless=lossless, quality=100 if lossless else q, method=6, exact=lossless)
    got[name.lower()] = os.path.getsize(p)


# フィールド（朝・夕方・夜・幻の馬・神様馬）・ゆれ・ライトの 地図
for f in ('morning', 'evening', 'night', 'abyss', 'divine'): put(os.path.join(H3, f'tc_field_{f}.webp'))
for f in ('morning', 'evening', 'night', 'none'): webp(os.path.join(H3, f'tc_sway_{f}.png'), f'tc_sway_{f}.webp', lossless=True)
for f in ('evening', 'night'): webp(os.path.join(H3, f'tc_light_{f}.png'), f'tc_light_{f}.webp', lossless=True)
# 馬（5色 × 5段階・幻の馬・神様馬）：形（json＋bin）と 絵（色・法線）
need = set()
for c in ('brown', 'madara', 'black', 'white', 'hada'):
    for s in range(1, 6): need.add(f'tc_horse_bk_{c}_s{s}')
need |= {'tc_horse_bk_kamisama', 'tc_horse_bk_maboroshi'}
bins, texs = set(), set()
for nm in sorted(need):
    m = json.load(open(os.path.join(H3, nm + '.json'))); put(os.path.join(H3, nm + '.json'))
    bins.add(m.get('bin') or nm + '.bin')
    for k in ('tex', 'ntex'):
        if m.get(k): texs.add(m[k])
for b in sorted(bins): put(os.path.join(H3, b))
for t in sorted(texs): put(os.path.join(H3, t))
# うんち・アイテム・バナー・3D の バケツと エサ
for i in (1, 2, 3): put(os.path.join(H3, f'tc_poop{i}.webp'))
IT = os.path.join(H3, 'tc_items')
for f in ('tc_item_apple.webp', 'tc_item_carrot.webp', 'tc_item_carrot_gold.webp', 'tc_item_bucket.webp', 'tc_banner_kamisama.webp', 'tc_banner_maboroshi.webp'): put(os.path.join(IT, f))
for nm in ('tc_prop_bucket', 'tc_prop_feed'):
    m = json.load(open(os.path.join(IT, nm + '.json'))); put(os.path.join(IT, nm + '.json')); put(os.path.join(IT, m.get('bin') or nm + '.bin'))
    for k in ('tex', 'ntex'):
        if m.get(k): put(os.path.join(IT, m[k]))
# アイコン（右上の 丸い ボタン・作戦会議の 帯）
#   丸い ボタンの 絵＝まさちゃんの アイコン（11/10 09:57「トレーニングセンターのアイコンこれにして！」：折り紙の 仔馬・ブラシ・エサの バケツ・金の ふち）。
#   思い出フィギュアの アイコン（fg_icon.webp）と 同じ 作り方で 大きさを そろえる（kisekae/fab_icon.py：丸を 切り出して 232px で 240×240 の まん中に）
UI = os.path.join(SRC, 'user_icons')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import fab_icon
assert 'tc_icon_tc.webp' not in got
fab_icon.make(os.path.join(UI, 'icon_training_center.png'), os.path.join(OUT, 'tc_icon_tc.webp')); got['tc_icon_tc.webp'] = os.path.getsize(os.path.join(OUT, 'tc_icon_tc.webp'))
webp(os.path.join(UI, 'icon_sakusen_kaigi.png'), 'tc_icon_plan.webp', size=(720, 200), q=92)
# ルーレット（3つの 絵の 部品と 置き場所）
RP = os.path.join(H3, 'rt_parts')
for th in ('normal', 'maboroshi', 'kamisama'):
    for p in ('plate', 'knob', 'stick', 'ptr'): put(os.path.join(RP, f'rt_{th}_{p}.webp'))
put(os.path.join(RP, 'geom.json'), 'tc_rt_geom.json')
# 壁紙チケット（扉・チケット）
TK = os.path.join(H3, 'tk_src')
for f in ('tk_door_closed.webp', 'tk_door_open.webp', 'tk_ticket.webp'): put(os.path.join(TK, f))
# 音（snd/export_app.py で 作った m4a）
SD = os.path.join(SRC, 'app_snd')
for f in sorted(os.listdir(SD)):
    if f.endswith('.m4a'): put(os.path.join(SD, f))
tot = sum(got.values())
print('集めた', len(got), 'こ', round(tot / 1e6, 1), 'MB →', OUT)
# おそうじ（第4.152版）：ゴミの 絵・3D の ほうき・ちりとり（clean_assets.py の 出した もの）
CL = os.path.join(SRC, 'clean_app')
if os.path.isdir(CL):
    for f in sorted(os.listdir(CL)):
        if f.startswith(('tc_trash', 'tc_prop_broom', 'tc_prop_pan')): put(os.path.join(CL, f))
else:
    print('※ おそうじの 絵と 形（clean_app/）が ない：kisekae/tc/clean_assets.py で 作って ios/tc_assets に 足す')
