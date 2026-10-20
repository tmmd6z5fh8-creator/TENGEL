"""的中ボタン・デカ的中ボタン・フリーズ的中ボタン（デフォルト）・隠れど的中・ハズレの見本の画面：
   Fx_Hit.dc.html・Fx_Big.dc.html・Fx_Freeze.dc.html・Fx_Hidden.dc.html・Fx_Miss.dc.html ＋ 結果のボード30テーマの一覧 Fx_Boards.dc.html
   python3 gen_fx.py fx_blobs.json
   fx_blobs.json：フリーズの絵（fz_ncore・fz_nglow＝テンゲルのアイコンから作ったネオンの線画のマスク。T1 の背景）
   ＋メモの静止画（s_…。そろっていればメモ Fx_Memo.dc.html も作る）
   ＋効果音（snd_hit_push・snd_hit・snd_big_push・snd_big・snd_fz_push・snd_fz。gen_sfx.py の音。あれば見本の画面で鳴らして、
     同じフォルダの sfx_wave.json と合わせて効果音のメモ Fx_Sound.dc.html も作る）
   流れ：記録する → PUSHボタン（上下に動く）→ タップ → 壁紙のテーマのボードが出る（当たった買い目。ボードは boards.py・馬は出さない）
   フリーズ（3連単の当たりに超大穴＝10〜12番人気の馬）：虹色にギラギラ光るめちゃくちゃデカいPUSH → タップした瞬間にパチスロのフリーズのように
   白く光って横に流れるノイズ → 青い画面に白い光と細い電気 → 青白い横一本線に1pxの電気（プチュン）→ 点に縮んで消える → 真っ暗（1.5秒）
   → 虹色ネオンのカット（どてき！！・ど！・ど的中！！！！）→ 虹色の大当たりの画面に「ど的中」とボード
   カットの文字と結果の「ど的中」は筆の字（brush.py で描いた形 brush_glyphs.json・フォントなし）：虹色・金と黒のふち・金の立体・つや
   隠れど的中（デカ的中の2〜7回に1回・ランダム）：デカ的中のPUSH → タップでそのまま、ど的中の演出 → 見出し「隠れど的中！！！」のボード
   ハズレ：記録する → ボタンなしでボードだけ（静かに出る・音なし）"""
import os, re, sys, json, random, math
from urllib.parse import quote
from gen_screens import SVG_A
from boards import board_css, board_html, font_links as theme_fonts, ORDERED, BY_ID, CAT_ORDER, scoped
from themes20 import CATS, hanamaru_d
import push_events as PE           # 行事の4テーマの 的中ボタン（クリスマスツリー・かぼちゃ・チョコ・マシュマロ）

K = os.path.dirname(os.path.abspath(__file__))
P = f'{K}/canvas/project' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock'
blobs = json.load(open(sys.argv[1]))
RANCH = open(f'{P}/Judge_Ranch.dc.html', encoding='utf-8').read()
RANCH_VARS = re.search(r'^\.ph\{(--bg:[^}]*)\}', RANCH, re.M).group(1)
BANNER = '/_blob/4d32303d3e8ea65630ceca0f8b0b72e6'    # 牧場の上の絵（動かない絵・キャンバスの絵）。判定画面 Judge_Ranch は ranch.py の inline（馬が右へ左へ）

# 見本の画面のテーマ（牧場）。結果のボードは壁紙のテーマごと（boards.py。30テーマの一覧は Fx_Boards）
THEME = 'ranch'
RANCH_ALT = '青空と芝生、木の柵、草原に立つ栗毛の馬のイラスト'

# テーマごとの見本（まさちゃんの指定があったテーマだけ）：見本の画面の種類 → 元の種類・テーマ・判定画面・PUSHの形・字
THEMED = dict(
    hit_gold=dict(base='hit', tid='gold', banner='gold', push='gp', fonts=['Zen+Kaku+Gothic+New:wght@400;500;700']),   # カッコいい：黒と金の ぷるんぷるんPUSH・壁紙のおしりが ぷるん
    hit_ranch=dict(base='hit', tid='ranch', banner='ranch', push='gr'),   # 牧場：芝生でできたPUSH・壁紙の馬が右へ左へ（1〜8秒・ときどき立ち止まって芝を食べる／こっちを見る）
    hit_sakura=dict(base='hit', tid='sakura', banner='sakura', push='sk', fonts=BY_ID['sakura']['fonts']),   # 桜：桜がついたPUSH・壁紙にいつも桜が降る・馬が ときどき 首を下げて 草を食べる
    hit_sea=dict(base='hit', tid='sea', banner='sea', push='se', fonts=BY_ID['sea']['fonts']),   # 海：海の模様のPUSH・壁紙で馬がいつも走って景色が流れる
    hit_autumn=dict(base='hit', tid='autumn', banner='autumn', push='mo', fonts=BY_ID['autumn']['fonts']),   # 紅葉：紅葉がついたPUSH・壁紙にいつも紅葉が降る・馬が ときどき 首を下げて 草を食べる
    hit_snow=dict(base='hit', tid='snow', banner='snow', push='yk', fonts=BY_ID['snow']['fonts']),   # 雪：雪が積もったPUSH・壁紙にいつも雪が降る・馬が ときどき 首を下げて 草を食べる
    hit_newyear=dict(base='hit', tid='newyear', banner='newyear', push='ny', fonts=BY_ID['newyear']['fonts']),   # お正月：初日の出が映ったPUSH・壁紙の初日の出の光が右回り（馬は動かさない）
    hit_news=dict(base='hit', tid='news', banner='news', push='np', fonts=BY_ID['news']['fonts']),   # 競馬新聞：新聞でできたPUSH・壁紙の墨の馬がいつも走る
    hit_ink=dict(base='hit', tid='ink', banner='ink', push='nk', fonts=BY_ID['ink']['fonts']),   # 水墨画：墨画でできたPUSH・壁紙の2頭がいつも走る
    hit_carousel=dict(base='hit', tid='carousel', banner='carousel', push='mg', fonts=BY_ID['carousel']['fonts']),   # メリーゴーランド：メリーゴーランドのPUSH・壁紙の木馬が上下する
    hit_stars=dict(base='hit', tid='stars', banner='stars', push='sz', fonts=BY_ID['stars']['fonts']),   # 星座：星でできたPUSH・壁紙の星が流れてペガサスがきらきら（8秒に1回 鼻から しっぽへ キラキラ）
    hit_neon=dict(base='hit', tid='neon', banner='neon', push='nn', fonts=BY_ID['neon']['fonts']),   # ネオン：ネオンでできたPUSH・壁紙の馬が走って10秒に1回 流れ星
    hit_pixel=dict(base='hit', tid='pixel', banner='pixel', push='dp', fonts=BY_ID['pixel']['fonts']),   # ドット絵：ドットでできたPUSH・壁紙の馬が走って（うしろの丘と雲が ゆっくり流れる） ときどきジャンプか一回転して こっちを見る・20〜23秒に1回 立ち止まる
    hit_fireworks=dict(base='hit', tid='fireworks', banner='fireworks', push='hn', fonts=BY_ID['fireworks']['fonts']),   # 花火：花火でできたPUSH・壁紙の花火が 打ち上がって咲き、散り散りに消える（馬は あとから・ときどき5つ一斉）
    hit_kids=dict(base='hit', tid='kids', banner='kids', push='ke', fonts=BY_ID['kids']['fonts']),   # 子供向け：毛糸でできたPUSH・壁紙の毛糸玉が左から右へ転がって、ロボットと馬が目で追い、止まると馬が跳ねて喜ぶ → ロボットが拾いに行って うっかり蹴り、いっしょに右へ → 持って戻って 左へポーン（1.7秒あけて また転がる）。ときどき ロボットが故障して 馬が「ヒヒーン」→ 直って取りにいく／馬が取りにいく
    hit_cute=dict(base='hit', tid='cute', banner='cute', push='kw', fonts=BY_ID['cute']['fonts']),   # かわいい：ハートでできたPUSH・壁紙のハートとリボンがゆれて、大きいハートとポニーが近づき、当たるとポニーが飛び跳ねて喜ぶ（8秒）
    hit_sunset=dict(base='hit', tid='sunset', banner='sunset', push='ss', fonts=BY_ID['sunset']['fonts']),   # 夕焼け：夕日の映ったPUSH・壁紙の馬がいつも走って地面が左から右へ流れ、10秒に1回 夕日が ゆっくり沈んで真っ暗（1〜3秒）→ 4〜6秒で もとの位置へ
    hit_night=dict(base='hit', tid='night', banner='night', push='nb', fonts=BY_ID['night']['fonts']),   # ナイター：ナイター照明に照らされたPUSH・壁紙の3頭が いつも走って景色が流れ、1〜5秒ごとに順位が入れかわり、20秒でゴール（1着は ばらばら）→ 止まって暗く → 表彰 → 照明がついて また走りだす
    hit_marble=dict(base='hit', tid='marble', banner='marble', push='mb', fonts=BY_ID['marble']['fonts']),   # 大理石：大理石でできたPUSH・壁紙の像の馬が 8秒ごとに うしろを2度見して、くるっと 反対を向く・ときどき ヒヒィーン／台ごと ずっずっと 外へ出て もどる
    hit_lucky=dict(base='hit', tid='lucky', banner='lucky', push='kb', fonts=BY_ID['lucky']['fonts']),   # 開運：小判でできたPUSH・壁紙に いつも小判が降って、招き馬が 8秒ごとに 右の前足を がたがた → 一気に 振り下ろす・11〜19秒ごとに 上を向いて 招きながら ヒヒィーン
    hit_silks=dict(base='hit', tid='silks', banner='silks', push='sj', fonts=BY_ID['silks']['fonts']),   # 勝負服：勝負服でできたPUSH・壁紙の馬が走って柄が流れる
    hit_chalk=dict(base='hit', tid='chalk', banner='chalk', push='kk', fonts=BY_ID['chalk']['fonts']),   # 黒板：黒板にチョークで書いたPUSH・壁紙の馬を 10秒ごとに 黒板消しで消して、チョークで 書きなおす（3種類の馬）
    hit_silver=dict(base='hit', tid='silver', banner='silver', push='ag', fonts=BY_ID['silver']['fonts']),   # シルバー帯：シルバーでできたPUSH（めちゃくちゃ輝く）・壁紙の銀の馬の像が いつも キラキラ
    hit_golden=dict(base='hit', tid='golden', banner='golden', push='au', fonts=BY_ID['golden']['fonts']),   # ゴールド帯：ゴールドでできたPUSH（めちゃくちゃ輝く）・壁紙の金の馬の像が いつも 金に キラキラ
    hit_tengel=dict(base='hit', tid='tengel', banner='tengel', push='tg', fonts=BY_ID['tengel']['fonts']),   # マスター帯：説明書の上の絵と 同じ 長方形の テンゲルの PUSHが 緑の雷を まとう・壁紙は アイコンの馬は 動かさず（元の絵）、数字が動き、緑の雷が 枠じゅう ビリビリ
    hit_xmas=dict(base='hit', tid='xmas', banner='xmas', push='xm', fonts=BY_ID['xmas']['fonts']),   # クリスマス：クリスマスツリーのPUSH・壁紙は 止まった絵（push_events.py）
    hit_halloween=dict(base='hit', tid='halloween', banner='halloween', push='hw', fonts=BY_ID['halloween']['fonts']),   # ハロウィン：かぼちゃのPUSH・壁紙は 止まった絵
    hit_valentine=dict(base='hit', tid='valentine', banner='valentine', push='vl', fonts=BY_ID['valentine']['fonts']),   # バレンタイン：チョコのPUSH・壁紙は 止まった絵
    hit_whiteday=dict(base='hit', tid='whiteday', banner='whiteday', push='wd', fonts=BY_ID['whiteday']['fonts']),   # ホワイトデー：マシュマロのPUSH・壁紙は 止まった絵
)
AUTUMN_BLOB = '/_blob/1c869ee9f9195c4625d3997d66463e57'    # 紅葉の上の絵（WebP・blobs20.json の autumn）。もみじはこの上に SVG を重ねる（momiji.py）
SNOW_BLOB = '/_blob/6683d421d2b9e7e0503e7173da2288ba'      # 雪の上の絵（WebP・blobs20.json の snow）。降る雪はこの上に SVG を重ねる（yuki.py）
SAKURA_BLOB = '/_blob/3b3f002de6b9b1c35fec1c32400e1494'    # 桜の上の絵（WebP・blobs20.json の sakura）。花びらはこの上に SVG を重ねる（sakura.py）


def step_data():
    """桜・紅葉・雪の馬の動き（step_wall.load：キャンバスの id と 置く場所・時間わりの種）"""
    import step_wall
    return step_wall.load(f'{K}/step_blobs.json', f'{K}/step_run.json')


def theme_banner(name):
    """テーマの上の絵をページにじかに入れる形（<svg class="bnr">）と動きの CSS（カッコいい＝gold.py・牧場＝ranch.py の inline）"""
    if name == 'gold':
        import gold
        return gold.inline()
    if name == 'ranch':
        import ranch
        return ranch.inline()
    if name == 'sakura':                  # 桜：花びらが降る SVG（sakura.py）＋ 馬の動き（コマは flat/step_run.py・時間わりは step_plan.py・キャンバスの id は step_blobs.json・置く場所は step_run.json・step_wall.py）
        import sakura
        return sakura.inline(SAKURA_BLOB, step=step_data())
    if name == 'autumn':                  # 紅葉：もみじが降る SVG（momiji.py）＋ 馬の動き
        import momiji
        return momiji.inline(AUTUMN_BLOB, step=step_data())
    if name == 'snow':                    # 雪：雪が降る SVG（yuki.py）＋ 馬の動き
        import yuki
        return yuki.inline(SNOW_BLOB, step=step_data())
    if name == 'sunset':                  # 夕焼け：絵は flat/sunset_run.py の4まい（空・夕日・地面・走るコマ。キャンバスの id は sunset_blobs.json・大きさは sunset_run.json）・暗くなるのはページの幕
        import sunset_wall
        return sunset_wall.inline(sunset_wall.load_blobs(f'{K}/sunset_blobs.json'), json.load(open(f'{K}/sunset_run.json')))
    if name == 'cute':                    # かわいい：絵は cute.py の部品（いつもの絵と同じ形）を重ねて、ハート・リボン・ポニーだけを動かす（cute_wall.py・新しい絵はいらない）
        import cute_wall
        return cute_wall.inline()
    if name == 'kids':                    # 子供向け：絵は kids.py の部品（いつもの絵と同じ形）を重ねて、毛糸玉・目・馬・ロボットを動かす（kids_wall.py・新しい絵はいらない）
        import kids_wall
        return kids_wall.inline()
    if name == 'fireworks':               # 花火：下の絵（花火なし）と 足す光（花火4つ・馬）は flat/fireworks_banner.py --layers・足す光を 光の粒ごとに8組に分けた絵は fireworks_wall.py --scatter（キャンバスの id は fireworks_blobs.json・置く場所は fireworks_layers.json）・光の玉・火の粉・きらっは SVG
        import fireworks_wall
        return fireworks_wall.inline(fireworks_wall.load_blobs(f'{K}/fireworks_blobs.json'), json.load(open(f'{K}/fireworks_layers.json')))
    if name == 'pixel':                   # ドット絵：走る・立ち止まる・ジャンプ・一回転・こっちを見る・走りだす コマ（馬だけ）・遠くの景色（雲と丘）・前の景色と 下の絵（ロスなし）は flat/pixel_run.py（キャンバスの id は pixel_blobs.json・切りぬく場所と景色の帯は pixel_run.json）
        import pixel_wall
        return pixel_wall.inline(pixel_wall.load_blobs(f'{K}/pixel_blobs.json'), json.load(open(f'{K}/pixel_run.json')))
    if name == 'neon':                    # ネオン：走るコマは flat/neon_run.py（キャンバスの id は neon_blobs.json・切りぬく場所は neon_run.json）・流れ星はページの SVG
        import neon_wall
        return neon_wall.inline(neon_wall.load_blobs(f'{K}/neon_blobs.json'), json.load(open(f'{K}/neon_run.json')))
    if name == 'silks':                   # 勝負服：背景のくり返しと走るコマは flat/silks_run.py（キャンバスの id は silks_blobs.json・切りぬく場所は silks_run.json）
        import silks_wall
        return silks_wall.inline(silks_wall.load_blobs(f'{K}/silks_blobs.json'), json.load(open(f'{K}/silks_run.json')))
    if name == 'stars':                   # 星座：下の絵は flat/pegasus_banner.py --base（キャンバスの id は stars_blobs.json・星の位置は stars_pts.json）・星とキラキラはページの SVG
        import stars_wall
        return stars_wall.inline(stars_wall.load_blobs(f'{K}/stars_blobs.json'), json.load(open(f'{K}/stars_pts.json')))
    if name == 'carousel':                # メリーゴーランド：下の絵は flat/carousel_banner.py --base（キャンバスの id は carousel_blobs.json）・木馬はページの SVG
        import carousel_wall
        return carousel_wall.inline(carousel_wall.load_blobs(f'{K}/carousel_blobs.json'))
    if name == 'ink':                     # 水墨画：走るコマは flat/sumi_run.py（キャンバスの id は ink_blobs.json・切りぬく場所は ink_run.json）
        import ink_wall
        return ink_wall.inline(ink_wall.load_blobs(f'{K}/ink_blobs.json'), json.load(open(f'{K}/ink_run.json')))
    if name == 'news':                    # 競馬新聞：走るコマは flat/news_run.py（キャンバスの id は news_blobs.json・切りぬく場所は news_run.json）
        import news_wall
        return news_wall.inline(news_wall.load_blobs(f'{K}/news_blobs.json'), json.load(open(f'{K}/news_run.json')))
    if name == 'newyear':                 # お正月：絵は flat/newyear_banner.py --layers の2まい（キャンバスの id は newyear_blobs.json・光の決まりは newyear_sun.json）。馬は動かさない（まさちゃんの指定）
        import newyear_wall
        return newyear_wall.inline(newyear_wall.load_blobs(f'{K}/newyear_blobs.json'), json.load(open(f'{K}/newyear_sun.json')))
    if name == 'night':                   # ナイター：くり返せる背景3まい・1頭ずつの ギャロップと 止まる／走りだす コマのシート・表彰の絵は flat/night_run.py（キャンバスの id は night_blobs.json・置く場所は night_run.json）・ゴール板とバッジはページの SVG
        import night_wall
        return night_wall.inline(night_wall.load_blobs(f'{K}/night_blobs.json'), json.load(open(f'{K}/night_run.json')))
    if name == 'marble':                  # 大理石：下の絵は いまの絵・像と台のまわりの コマのシート（ふり向き・体が回る・ヒヒィーン）と すべる絵・背景だけの絵は flat/marble_run.py（キャンバスの id は marble_blobs.json・切りぬく場所と コマのならびは marble_run.json）
        import marble_wall
        return marble_wall.inline(marble_wall.load_blobs(f'{K}/marble_blobs.json'), json.load(open(f'{K}/marble_run.json')))
    if name == 'lucky':                   # 開運：絵は flat/lucky_banner.py の部品（いつもの絵と同じ形）を重ねて、招き馬の右前足・頭を動かし、小判を降らせる（lucky_wall.py・新しい絵はいらない）
        import lucky_wall
        return lucky_wall.inline()
    if name == 'chalk':                   # 黒板：馬のない黒板・馬3頭の ぬりと線・消したあとの もやは flat/chalk_run.py（キャンバスの id は chalk_blobs.json・置く場所と書く線は chalk_run.json）・黒板消しとチョークはページの SVG
        import chalk_wall
        return chalk_wall.inline(chalk_wall.load_blobs(f'{K}/chalk_blobs.json'), json.load(open(f'{K}/chalk_run.json')))
    if name in ('silver', 'golden'):      # シルバー帯・ゴールド帯：いまの絵と きらめきを ぬいた絵は flat/metal_run.py（キャンバスの id は metal_blobs.json・像の形と きらめきの場所は metal_run.json）・きらめき・光の粒・光の輪はページの SVG（像の上を 左から右へ 通る 光の帯は やめた）
        import metal_wall
        mn = 'silver' if name == 'silver' else 'gold'
        return metal_wall.inline(mn, metal_wall.load_blobs(f'{K}/metal_blobs.json', mn), json.load(open(f'{K}/metal_run.json')))
    if name == 'tengel':                  # マスター帯：上の絵は いまの絵の まま（キャンバスの id は tengel_blobs.json）・数字の 場所は tengel_run.json（flat/tengel_run.py）・数字と雷はページの SVG
        import tengel_wall
        return tengel_wall.inline(tengel_wall.load_blobs(f'{K}/tengel_blobs.json'), json.load(open(f'{K}/tengel_run.json')))
    if name == 'sea':                     # 海：絵は flat/sea_run.py の4まい（キャンバスの id は sea_blobs.json・大きさは sea_run.json）
        import sea_wall
        return sea_wall.inline(json.load(open(f'{K}/sea_blobs.json')), json.load(open(f'{K}/sea_run.json')))
    if name in EVENTS:                    # 行事の4テーマ（クリスマス・ハロウィン・バレンタイン・ホワイトデー）：壁紙は 止まった絵（キャンバスの id は blobs20.json・絵の説明は themes20.py の alt）
        from themes20 import THEMES as T20
        t = next(x for x in T20 if x['id'] == name)
        return f'<img class="bnr" src="/_blob/{json.load(open(f"{K}/blobs20.json"))[name]}" alt="{t["alt"]}">', ''
    raise KeyError(name)


EVENTS = ('xmas', 'halloween', 'valentine', 'whiteday')

# 馬番の枠の色（12頭のレース）
WAKU = {1: 'w1', 2: 'w2', 3: 'w3', 4: 'w3', 5: 'w4', 6: 'w4', 7: 'w5', 8: 'w5', 9: 'w6', 10: 'w6', 11: 'w7', 12: 'w8'}
WAKU = {6: 'w5', 2: 'w2', 10: 'w7', 7: 'w6', 1: 'w1', 4: 'w4', 11: 'w8'}   # 判定画面の見本と同じ色に合わせる


def num(n, extra=''):
    return f'<span class="n {WAKU.get(n, "w1")}{extra}">{n}</span>'


def combo(nums, sep, mark=()):
    s = f'<span class="ar">{sep}</span>'
    return s.join(num(x, ' zx' if x in mark else '') for x in nums)


CONF_COLS_HIT = ['#E8382F', '#F3C316', '#3E7B1E', '#1F5FC9', '#F27BB0', '#FFFFFF', '#F08A1C']


def confetti(n, seed, rainbow=False, d0=0.0):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(2, 98)
        d = d0 + rnd.uniform(0, 2.2)
        t = rnd.uniform(2.4, 4.2)
        w = rnd.uniform(6, 10)
        h = rnd.uniform(10, 16)
        r = rnd.choice([-1, 1]) * rnd.uniform(360, 900)
        c = f'hsl({int(i * 360 / n)},95%,62%)' if rainbow else rnd.choice(CONF_COLS_HIT)
        out.append(f'<i style="--x:{x:.1f}%;--d:{d:.2f}s;--t:{t:.2f}s;--w:{w:.0f}px;--h:{h:.0f}px;--r:{r:.0f}deg;--c:{c}"></i>')
    return ''.join(out)


def sparkles(n, seed, white=False):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(4, 96); y = rnd.uniform(6, 92)
        s = rnd.uniform(10, 26); d = rnd.uniform(0, 1.6)
        c = rnd.randint(0, 359)
        col = '#FFFFFF' if white else f'hsl({c},100%,75%)'
        out.append(f'<b style="--x:{x:.1f}%;--y:{y:.1f}%;--s:{s:.0f}px;--d:{d:.2f}s;--c:{col}"></b>')
    return ''.join(out)


def coins(n, seed, d0=0.0):
    """金のコイン（くるくる回りながら落ちる）"""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(3, 97); d = d0 + rnd.uniform(0, 2.0); t = rnd.uniform(2.2, 3.6); w = rnd.uniform(12, 19)
        out.append(f'<i class="cn" style="--x:{x:.1f}%;--d:{d:.2f}s;--t:{t:.2f}s;--w:{w:.0f}px"></i>')
    return ''.join(out)


def burst(x, y, d, s, c1, c2, seed, n=12, ring=True, star=True, z=None, dist=(.55, 1.0)):
    """爆発の光：ギザギザの星形の光（.bs1）・衝撃の輪（.bw）・飛び散る光の破片 n こ。(x, y)＝まん中・d＝秒・s＝大きさ・c1/c2＝光の色"""
    rnd = random.Random(seed)
    pts = []
    for i in range(32):
        a = math.pi * 2 * i / 32 + rnd.uniform(-.05, .05)
        r = rnd.uniform(40, 50) if i % 2 == 0 else rnd.uniform(14, 22)
        pts.append(f'{50 + r * math.sin(a):.1f}% {50 - r * math.cos(a):.1f}%')
    deb = ''
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-.3, .3)) / n
        dd = s * rnd.uniform(*dist)
        deb += (f'<i style="--dx:{math.cos(a) * dd:.0f}px;--dy:{math.sin(a) * dd:.0f}px;--r:{math.degrees(a):.0f}deg;'
                f'--t:{rnd.uniform(.38, .6):.2f}s;--c:hsl({rnd.randint(0, 359)},100%,{rnd.randint(60, 75)}%)"></i>')
    zs = f'z-index:{z};' if z is not None else ''
    st = f'<b class="bs1" style="clip-path:polygon({",".join(pts)})"></b>' if star else ''
    rg = '<b class="bw"></b>' if ring else ''
    return f'<i class="bx" style="{zs}--x:{x:g}px;--y:{y:g}px;--d:{fz_sec(d)};--s:{s:g}px;--c1:{c1};--c2:{c2}" aria-hidden="true">{st}{rg}{deb}</i>'


BURST_CSS = r'''
/* 爆発の光（文字やボードが出るとき）：ギザギザの星形の光がはじけて消える・衝撃の輪・飛び散る光の破片。小さな範囲で1回だけ光る（画面全体は光らせない） */
.bx{position:absolute;left:var(--x);top:var(--y);width:0;height:0;pointer-events:none}
.bx .bs1{position:absolute;left:calc(var(--s) / -2);top:calc(var(--s) / -2);width:var(--s);height:var(--s);
  background:radial-gradient(circle,#FFFFFF 0 7%,var(--c1) 20%,var(--c2) 44%,rgba(0,0,0,0) 68%);opacity:0;animation:bxS .36s cubic-bezier(.1,.8,.3,1) var(--d) forwards}
@keyframes bxS{0%{opacity:1;transform:scale(.12)}45%{opacity:1}100%{opacity:0;transform:scale(1.2)}}
.bx .bw{position:absolute;left:calc(var(--s) * -.35);top:calc(var(--s) * -.35);width:calc(var(--s) * .7);height:calc(var(--s) * .7);border-radius:50%;
  border:6px solid var(--c1);box-shadow:0 0 14px var(--c1),inset 0 0 10px var(--c1);opacity:0;animation:bxW .42s ease-out var(--d) forwards}
@keyframes bxW{0%{opacity:1;transform:scale(.2)}100%{opacity:0;transform:scale(2)}}
.bx > i{position:absolute;left:-7px;top:-2px;width:14px;height:4px;border-radius:2px;background:var(--c);box-shadow:0 0 6px var(--c);
  opacity:0;animation:bxD var(--t) cubic-bezier(.12,.7,.3,1) var(--d) forwards}
@keyframes bxD{0%{opacity:1;transform:translate(0,0) rotate(var(--r)) scaleX(2.2)}100%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--r)) scaleX(.5)}}
@media (prefers-reduced-motion:reduce){.bx{display:none}}
'''


COMMON_CSS = r'''body{margin:0}
*{box-sizing:border-box}
.ph{RANCH}
.ph{--pushA:#E8382F;--pushB:#A51A12;--pushC:#FF9A8A;--rim:#F6E7B8;--rimD:#B98A3A;--bFrame:#8A5A2B;--bFace:#FFFDF5;--bInk:#3A2414;--hitRed:#E8382F;--ray:rgba(255,236,170,.55);
  --pushFace:radial-gradient(72% 40% at 50% 14%,rgba(255,255,255,.9),rgba(255,255,255,.3) 58%,rgba(255,255,255,0) 100%),linear-gradient(180deg,var(--pushC) 0%,var(--pushA) 40%,var(--pushB) 86%,#5E0A05 100%)}
.ph{width:390px;height:844px;position:relative;overflow:hidden;display:flex;flex-direction:column;background-color:var(--bg);background-image:radial-gradient(#E1EFC4 1.6px,transparent 2px);background-size:18px 18px;color:var(--ink);font-family:var(--font),sans-serif;-webkit-font-smoothing:antialiased}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.hd{position:relative;z-index:2;flex:none;padding:10px 16px 12px;background:var(--hd);color:var(--hdInk);border-bottom:4px solid #A8743F}
.hd-r1{display:flex;align-items:center;justify-content:space-between;height:42px}
.logo{display:flex;align-items:center;font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:26px;line-height:1;color:var(--logo);text-shadow:var(--logoS)}
.iii{display:inline-flex;gap:3px;margin-left:6px}
.iii i{display:block;width:5.5px;height:21px;background:var(--iii);border:var(--iiiB);border-radius:var(--iiiR)}
.mbtn{display:inline-flex;align-items:center;gap:6px;height:38px;padding:0 15px;border-radius:999px;border:1.5px solid var(--mLine);background:var(--mBg);color:var(--mInk);font-family:var(--font),sans-serif;font-weight:700;font-size:14px;cursor:pointer}
.mbtn svg{width:18px;height:18px}
.bnr{flex:none;display:block;width:390px;height:120px;object-fit:cover;object-position:50% 70%}
.ct{flex:1;min-height:0;overflow:hidden;padding:14px 14px 0}
.card{position:relative;background:var(--card);border:var(--cardB);border-radius:var(--radius);box-shadow:var(--cardS);padding:14px}
.ch{margin:0 0 10px;font-size:13px;font-weight:700;color:var(--sub)}
.rh{display:flex;align-items:baseline;gap:10px}
.rk{font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:22px;color:var(--ink)}
.rs{font-size:12px;color:var(--sub)}
.lab{margin:12px 0 6px;font-size:12px;font-weight:700;color:var(--sub)}
.fin{display:flex;align-items:center;gap:8px}
.fin span.k{font-size:12px;font-weight:700;color:var(--sub)}
.n{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:30px;padding:0 6px;border-radius:var(--nR);font:700 15px/1 "BIZ UDPGothic",sans-serif}
.w1{background:#FFFFFF;color:#1F1F1F;border:1.5px solid #9AA0A6}
.w2{background:#222222;color:#FFFFFF}
.w4{background:#1F5FC9;color:#FFFFFF}
.w5{background:#F3C316;color:#1F1F1F}
.w6{background:#1E8E3E;color:#FFFFFF}
.w7{background:#F08A1C;color:#1F1F1F}
.ar{color:var(--sub);font-weight:700;padding:0 2px}
.bets{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.bets li{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:var(--rs);background:var(--zBg);border:var(--zB)}
.bt{flex:none;min-width:46px;height:24px;padding:0 8px;border-radius:999px;background:var(--znBg);color:var(--znInk);font-size:12px;font-weight:800;display:inline-flex;align-items:center;justify-content:center}
.bc{display:flex;align-items:center;gap:3px;flex:1}
.bc .n{min-width:26px;height:26px;font-size:13px}
.by{font-size:12.5px;font-weight:700;color:var(--ink)}
.pay{display:flex;align-items:center;justify-content:space-between;margin-top:10px;padding:10px 12px;border-radius:var(--rs);border:1.5px dashed var(--tagLine);font-size:13px;font-weight:700;color:var(--ink)}
.pay b{font-size:17px}
.rec{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:50px;margin-top:14px;border:0;border-radius:var(--btnR);background:var(--btn);color:var(--btnInk);box-shadow:var(--btnS);font-family:var(--font),sans-serif;font-weight:800;font-size:17px;cursor:pointer}
.rec svg{width:20px;height:20px}
.note{margin:10px 2px 0;font-size:11.5px;line-height:1.5;color:var(--sub)}
/* ---------- 重ねる画面 ---------- */
.ov{position:absolute;inset:0;z-index:20;display:flex;align-items:center;justify-content:center;overflow:hidden}
.dim{position:absolute;inset:0;background:rgba(24,14,4,.62);animation:fadeIn .25s ease-out both}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
/* PUSHボタン（横長の長方形・角は丸い） */
.pbox{position:relative;display:flex;flex-direction:column;align-items:center}
.push{--pr:26px;position:relative;z-index:2;width:200px;height:100px;border-radius:var(--pr);border:0;padding:0;cursor:pointer;background:var(--pushFace);
  box-shadow:inset 0 -9px 0 rgba(0,0,0,.2),inset 0 2px 0 rgba(255,255,255,.55),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #6E4E1A,0 22px 34px rgba(0,0,0,.5);
  animation:bob .9s ease-in-out infinite,popIn .35s cubic-bezier(.2,1.6,.4,1) both}
.push span{position:relative;font:400 40px/1 "Dela Gothic One",sans-serif;color:#FFFFFF;letter-spacing:.04em;text-shadow:0 3px 0 var(--pushB),0 0 14px rgba(255,255,255,.55)}
.push::after{content:"";position:absolute;inset:-18px;border-radius:calc(var(--pr) + 18px);border:3px solid rgba(255,232,150,.95);animation:ring 1.2s ease-out infinite}
.pshadow{width:200px;height:22px;margin-top:22px;border-radius:50%;background:rgba(0,0,0,.45);filter:blur(4px);animation:shad .9s ease-in-out infinite}
.tap{margin:16px 0 0;font:400 20px/1 "Dela Gothic One",sans-serif;color:#FFF3C8;letter-spacing:.1em;animation:blink 1s steps(2) infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-18px)}}
@keyframes shad{0%,100%{transform:scale(1);opacity:.55}50%{transform:scale(.72);opacity:.3}}
@keyframes ring{0%{transform:scale(.88);opacity:.95}100%{transform:scale(1.4);opacity:0}}
@keyframes popIn{from{scale:.2}to{scale:1}}
@keyframes blink{0%{opacity:1}100%{opacity:.35}}
@keyframes raysIn{from{opacity:0;scale:.3}to{opacity:1;scale:1}}
@keyframes spin{to{rotate:360deg}}
@keyframes pop{0%{transform:scale(0)}100%{transform:scale(1)}}
@keyframes rowIn{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
/* 買い目の行は0.15秒おき（--i＝何行目か）。合計と「とじる」は最後の行のあと（--n＝行の数。3行より少なくても3行ぶん待つ） */
.ov .brows li{animation:rowIn .35s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .15s)}
.ov .btot{animation:rowIn .35s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .15s)}
.ov .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .15s + var(--tc))}
/* 押したあと（PUSHがあった所から光ってはじける） */
.pressed{position:absolute;z-index:3;left:50%;top:calc(50% - 40px);width:200px;height:100px;margin:-50px 0 0 -100px;border-radius:26px;background:var(--pushFace);
  box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD);animation:press .45s ease-in both}
@keyframes press{0%{transform:scale(1)}35%{transform:scale(.82);filter:brightness(1.4)}100%{transform:scale(1.9);opacity:0;filter:brightness(3)}}
/* 結果のボード（壁紙のテーマのボード・boards.py）を入れる箱：この箱が動く（下から出る・落ちてくる・炎の中からドン）。馬は出さない */
.hb{position:absolute;z-index:6;left:50%;top:196px;width:350px;margin-left:-175px}
.close{position:absolute;z-index:8;left:50%;bottom:64px;transform:translateX(-50%);height:46px;padding:0 34px;border-radius:999px;border:2px solid rgba(255,255,255,.85);background:rgba(0,0,0,.35);color:#FFFFFF;font-family:var(--font),sans-serif;font-weight:800;font-size:15px;cursor:pointer;animation:fadeUp .4s ease-out both}
@keyframes fadeUp{from{opacity:0;transform:translate(-50%,12px)}to{opacity:1;transform:translate(-50%,0)}}
/* 紙ふぶき */
.conf{position:absolute;inset:0;z-index:7;pointer-events:none}
.conf i{position:absolute;left:var(--x);top:-30px;width:var(--w);height:var(--h);background:var(--c);border-radius:2px;opacity:0;animation:fall var(--t) linear var(--d) infinite}
@keyframes fall{0%{opacity:1;transform:translateY(0) rotate(0)}85%{opacity:1}100%{opacity:0;transform:translateY(900px) rotate(var(--r))}}
/* 視差効果を減らす：上下・回転・広がる光・紙ふぶきを止めて、ボードはふわっと出す */
@media (prefers-reduced-motion:reduce){.push,.pshadow,.push::after,.halo b,.tap,.conf i,.rays,.rbow,.ring,.glow,.spk b{animation:none!important}.conf,.pressed,.push::after{display:none}.hb{animation:fadeIn .5s ease-out .2s both!important}}
'''

HIT_CSS = r'''
/* ---------- 的中：あたたかい光 → ボードが下から出る ---------- */
.rays{position:absolute;z-index:4;left:50%;top:44%;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;
  background:repeating-conic-gradient(var(--ray) 0 7deg,transparent 7deg 18deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);mask-image:radial-gradient(circle,#000 0 18%,transparent 62%);
  animation:raysIn .6s ease-out .2s both,spin 22s linear infinite}
.hit .hb{animation:riseUp .7s cubic-bezier(.2,1.35,.4,1) .3s both}
@keyframes riseUp{from{transform:translateY(720px)}to{transform:translateY(0)}}
.hit .bh{animation:pop .5s cubic-bezier(.2,1.8,.4,1) .95s both}
.hit{--t0:1.15s;--tc:.2s}
'''

MISS_CSS = r'''
/* ---------- ハズレ：ボタンなし。記録したら、暗い幕とテーマのボードが静かに出る（光・紙ふぶき・音なし） ---------- */
.miss .hb{animation:missIn .4s cubic-bezier(.2,.8,.3,1) .1s both}
@keyframes missIn{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
.ov.miss{--t0:.45s;--tc:.15s}
.ov.miss .brows li{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .08s)}
.ov.miss .btot{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s)}
.ov.miss .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s + var(--tc))}
'''

BIG_CSS = r'''
/* ---------- デカ的中：大きいPUSH・虹色に光る ---------- */
.ov.big .dim{background:radial-gradient(circle at 50% 46%,rgba(60,30,90,.55),rgba(6,4,18,.86) 70%)}
/* 押したあとの画面（.rv）は、PUSHの画面と同じ暗さのまま始める（暗さがいったん消えてまた暗くなると、白い光の前にもう1回光ってしまう） */
.ov.rv .dim{animation:none}
.push.big{--pr:36px;width:280px;height:140px;animation:bobBig .8s ease-in-out infinite,popIn .4s cubic-bezier(.2,1.6,.4,1) both}
.push.big span{font-size:56px}
/* 虹の輪：形はボタンと同じ横長のまま、色だけがぐるぐる回る */
.halo{position:absolute;inset:-30px;z-index:-1;border-radius:calc(var(--pr) + 30px);filter:drop-shadow(0 0 8px rgba(255,255,255,.85));pointer-events:none}
.halo i{position:absolute;inset:0;border-radius:inherit;padding:10px;overflow:hidden;
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
.halo b{position:absolute;left:50%;top:50%;width:440px;height:440px;margin:-220px 0 0 -220px;
  background:conic-gradient(#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);animation:spin 1.4s linear infinite}
.push.big::after{inset:-44px;border-radius:calc(var(--pr) + 44px);border:4px solid transparent;background:conic-gradient(#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3B3B) border-box;
  -webkit-mask:linear-gradient(#000 0 0) padding-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:ring 1s ease-out infinite}
.pshadow.big{width:280px;margin-top:30px;animation:shadBig .8s ease-in-out infinite}
.tap.big{font-size:26px;background:linear-gradient(90deg,#FF5A5A,#FFD93B,#5BE38A,#4FD3FF,#B07CFF,#FF5A5A);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:rbowText 1.6s linear infinite}
@keyframes bobBig{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-26px) scale(1.04)}}
@keyframes shadBig{0%,100%{transform:scale(1);opacity:.6}50%{transform:scale(.68);opacity:.28}}
@keyframes rbowText{to{background-position:200% 0}}
.spk{position:absolute;inset:0;z-index:1;pointer-events:none}
.spk b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);background:var(--c);
  clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%);animation:twinkle 1.6s ease-in-out var(--d) infinite;opacity:0}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(.3) rotate(0)}50%{opacity:1;transform:scale(1) rotate(45deg)}}
.pressed.big{top:calc(50% - 47px);width:280px;height:140px;margin:-70px 0 0 -140px;border-radius:36px}
/* 押したあと（パチンコの当たりのように速く・勢いよく）：はじける → 0.04秒 白く光る・爆発・虹の光の筋 → 虹の輪3つ（0.1・0.25・0.4秒）
   → 0.38秒 ボードがドンと落ちてくる（0.55秒に着地・爆発）→ 0.7秒「デカ的中!!」→ 0.9秒〜 買い目（0.08秒おき）→ 1.4秒 とじる */
.pressed.big{animation:press .28s ease-in both}
.flash{position:absolute;inset:0;z-index:9;background:#FFFFFF;pointer-events:none;animation:flash .5s ease-out .04s both}
@keyframes flash{0%{opacity:0}12%{opacity:1}100%{opacity:0}}
.rbow{position:absolute;z-index:3;left:50%;top:44%;width:1100px;height:1100px;margin:-550px 0 0 -550px;border-radius:50%;
  background:conic-gradient(#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);
  -webkit-mask-image:repeating-conic-gradient(#000 0 6deg,transparent 6deg 15deg),radial-gradient(circle,#000 0 10%,transparent 60%);
  -webkit-mask-composite:source-in;mask-image:repeating-conic-gradient(#000 0 6deg,transparent 6deg 15deg),radial-gradient(circle,#000 0 10%,transparent 60%);mask-composite:intersect;
  opacity:.85;animation:raysIn .25s cubic-bezier(.2,.9,.3,1) .04s both,spin 30s linear infinite}
.glow{position:absolute;z-index:4;left:50%;top:44%;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 22%,rgba(255,248,214,.9) 34%,rgba(255,230,160,.45) 52%,transparent 70%);
  animation:wrap .55s ease-out .04s both,breathe 2.4s ease-in-out .6s infinite}
@keyframes wrap{0%{scale:.1;opacity:0}60%{scale:1.3;opacity:1}100%{scale:1.15;opacity:.95}}
@keyframes breathe{0%,100%{scale:1.15}50%{scale:1.25}}
.ring{position:absolute;z-index:5;left:50%;top:44%;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;
  background:conic-gradient(#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3B3B);
  -webkit-mask-image:radial-gradient(circle,transparent 0 64%,#000 66% 72%,transparent 74%);mask-image:radial-gradient(circle,transparent 0 64%,#000 66% 72%,transparent 74%);
  opacity:0;animation:shock2 .42s ease-out forwards}
/* 虹の輪3つ（キュウィン×3）：だんだん大きい輪がポンと出て消える（同じ所が何回も光らないように、輪の大きさを変える） */
.ring.r1{--rs:.9;animation-delay:.1s}.ring.r2{--rs:1.5;animation-delay:.25s}.ring.r3{--rs:2.2;animation-delay:.4s}
@keyframes shock2{0%{opacity:.7;scale:calc(var(--rs) * .6)}100%{opacity:0;scale:calc(var(--rs) * 1.25)}}
@keyframes shock{0%{opacity:1;scale:.2}100%{opacity:0;scale:3.2}}
.big .hb{animation:bslam .42s cubic-bezier(.2,.9,.3,1.1) .38s both}
@keyframes bslam{0%{opacity:0;transform:translateY(-70px) scale(1.45);filter:brightness(3) blur(3px)}55%{opacity:1;transform:translateY(8px) scale(.96);filter:brightness(1.7) blur(0)}78%{transform:translateY(-3px) scale(1.02);filter:brightness(1.15)}100%{transform:none;filter:none}}
/* 見出し「デカ的中!!」：虹色の文字（boards.py）がたたきつけるように出て、色が流れる */
.big .bh{animation:bhSlam .3s cubic-bezier(.2,1.5,.4,1) .7s both,rbowText 2s linear .7s infinite}
@keyframes bhSlam{0%{opacity:0;transform:scale(2.6)}60%{opacity:1;transform:scale(.9)}100%{opacity:1;transform:scale(1)}}
.ov.big{--t0:.9s;--tc:.25s}
.ov.big .brows li{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .08s)}
.ov.big .btot{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s)}
.ov.big .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s + var(--tc))}

'''

FREEZE_CSS = r'''
/* ---------- フリーズ的中：虹色にギラギラ光る めちゃくちゃデカいPUSH → タップでパチスロのフリーズのように ----------
   （押したあとの秒は下の「押したあと」に書いてある） */
.w3{background:#E0322B;color:#FFFFFF}
.w8{background:#F27BB0;color:#1F1F1F}
.ov.fz{--rb:#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B;--ink2:#2A1259;--t0:<R+.45>;--tc:.25s}
/* 結果の買い目は0.08秒おき（パチンコの当たりのように速く） */
.ov.fz .brows li{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + var(--i) * .08s)}
.ov.fz .btot{animation:rowIn .22s ease-out both;animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s)}
.ov.fz .close{animation-delay:calc(var(--t0) + max(var(--n), 3) * .08s + var(--tc))}
.ov.fz .dim{background:radial-gradient(circle at 50% 44%,rgba(84,26,136,.55),rgba(5,2,14,.94) 66%)}
/* PUSHのうしろ：ぼかした虹（回る）と白い光の筋 */
.aura{position:absolute;left:50%;top:44%;width:600px;height:600px;margin:-300px 0 0 -300px;border-radius:50%;background:conic-gradient(var(--rb));filter:blur(40px);opacity:.6;animation:spin 3.2s linear infinite}
.prays{position:absolute;left:50%;top:44%;width:1100px;height:1100px;margin:-550px 0 0 -550px;border-radius:50%;
  background:repeating-conic-gradient(rgba(255,255,255,.34) 0 4deg,transparent 4deg 12deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 14%,transparent 56%);mask-image:radial-gradient(circle,#000 0 14%,transparent 56%);animation:spin 9s linear infinite}
/* 画面のふちが虹色に光る */
.edge{position:absolute;inset:0;z-index:11;pointer-events:none;box-shadow:inset 0 0 22px 6px rgba(255,70,200,.55),inset 0 0 64px 14px rgba(70,190,255,.32);animation:edge 1.2s ease-in-out infinite alternate}
@keyframes edge{from{opacity:.55}to{opacity:1}}
.frame{position:absolute;inset:0;z-index:12;pointer-events:none;padding:5px;overflow:hidden;
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
.frame b{position:absolute;left:50%;top:50%;width:1000px;height:1000px;margin:-500px 0 0 -500px;background:conic-gradient(var(--rb));animation:spin 1.6s linear infinite}
/* PUSH：横340×縦170（デカの1.2倍）。面は虹色が流れる＋ラメ＋白い光がサッと走る。白と紫のふち・虹の輪。1.3秒ごとにブルブルッ */
.push.fz{--pr:46px;width:340px;height:170px;background:#3A1E78;
  box-shadow:0 0 0 8px #FFFFFF,0 0 0 14px #3A1E78,0 12px 0 14px #1E0F45,0 0 54px 24px rgba(255,255,255,.3),0 30px 46px rgba(0,0,0,.6);
  animation:fzBob .85s ease-in-out infinite,fzBuzz 1.3s linear infinite,popIn .5s cubic-bezier(.2,1.6,.4,1) both}
.push.fz .face,.push.fz .gloss,.push.fz .glit{position:absolute;inset:0;border-radius:inherit;pointer-events:none}
.push.fz .face{background:repeating-linear-gradient(100deg,#FF3B3B 0,#FF9F1A 42px,#FFE53B 84px,#3BE26A 126px,#2FD6FF 168px,#4C6BFF 210px,#B34CFF 252px,#FF3BB8 294px,#FF3B3B 336px) 0 0/341.2px 100%;animation:fzFlow 1.4s linear infinite}
.push.fz .gloss{background:radial-gradient(70% 36% at 50% 10%,rgba(255,255,255,.95),rgba(255,255,255,.4) 55%,rgba(255,255,255,0) 100%),linear-gradient(180deg,rgba(255,255,255,0) 50%,rgba(48,12,96,.45) 100%);
  box-shadow:inset 0 -12px 0 rgba(0,0,0,.2),inset 0 3px 0 rgba(255,255,255,.8)}
.push.fz .glit{overflow:hidden}
.push.fz .glit b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);border-radius:50%;background:#FFFFFF;
  box-shadow:0 0 4px 1px rgba(255,255,255,.9);opacity:.15;animation:lame .8s ease-in-out var(--d) infinite alternate}
@keyframes lame{from{opacity:.12}to{opacity:1}}
.push.fz .spk{border-radius:inherit;overflow:hidden}
.push.fz span{font-size:80px;letter-spacing:.02em;color:#FFFFFF;
  text-shadow:3px 0 0 var(--ink2),-3px 0 0 var(--ink2),0 3px 0 var(--ink2),0 -3px 0 var(--ink2),2px 2px 0 var(--ink2),-2px 2px 0 var(--ink2),2px -2px 0 var(--ink2),-2px -2px 0 var(--ink2),0 8px 0 var(--ink2),0 0 26px rgba(255,255,255,.95)}
.push.fz::before{content:"";position:absolute;inset:0;z-index:3;border-radius:inherit;pointer-events:none;
  background:linear-gradient(105deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.95) 50%,rgba(255,255,255,0) 70%) -130% 0/55% 100% no-repeat;mix-blend-mode:screen;animation:glint 1.5s ease-in-out .3s infinite}
.push.fz::after{inset:-40px;border-radius:calc(var(--pr) + 40px);border:5px solid transparent;background:conic-gradient(var(--rb)) border-box;
  -webkit-mask:linear-gradient(#000 0 0) padding-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:ring .8s ease-out infinite}
.push.fz .halo{inset:-25px;border-radius:calc(var(--pr) + 25px);filter:drop-shadow(0 0 8px #FFFFFF) drop-shadow(0 0 20px rgba(255,110,230,.85))}
.push.fz .halo i{padding:10px}
.push.fz .halo b{width:620px;height:620px;margin:-310px 0 0 -310px;animation:spin .9s linear infinite}
@keyframes fzFlow{to{background-position:341.2px 0}}
@keyframes fzBob{0%,100%{translate:0 0}50%{translate:0 -22px}}
@keyframes fzBuzz{0%,16%,100%{rotate:0deg}2%{rotate:-2.4deg}4%{rotate:2.4deg}6%{rotate:-2deg}8%{rotate:2deg}10%{rotate:-1.4deg}12%{rotate:1.4deg}14%{rotate:-.6deg}}
@keyframes glint{0%{background-position:-130% 0}55%,100%{background-position:230% 0}}
.pshadow.fz{width:330px;height:26px;margin-top:36px;animation:shadFz .85s ease-in-out infinite}
@keyframes shadFz{0%,100%{transform:scale(1);opacity:.62}50%{transform:scale(.7);opacity:.3}}
.tap.fz{margin-top:20px;font-size:32px;background:linear-gradient(90deg,#FF6A6A,#FFE04D,#6BEB98,#5FDBFF,#C08CFF,#FF6A6A);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 3px 0 var(--ink2)) drop-shadow(0 0 7px rgba(255,255,255,.7));animation:rbowText 1.1s linear infinite}
/* ---------- 押したあと（パチスロのフリーズのように。押した瞬間にフリーズ） ----------
   秒は押してから。0＝白く光って横に流れるノイズ・<B>＝青い画面と白い光・<W>＝まわりが暗くなって青白い横一本線（細い電気）・<Z>＝線が点に縮んで消える
   ・（真っ暗1.5秒）・<M>＝虹色ネオンのカット・<R>＝結果（虹色の大当たりの画面・上に「ど的中」・テーマのボード） */
.ov.fz .blk{position:absolute;inset:0;background:#000000}
@keyframes vis{from,to{visibility:visible}}
@keyframes on1{from,to{opacity:1}}
@keyframes fzOn{from,to{opacity:1}}
.ov.fz .pc,.ov.fz .mt,.ov.fz .fin,.ov.fz .xf{position:absolute;inset:0;overflow:hidden;pointer-events:none}
/* ===== 1) フリーズ（押した瞬間＝0秒〜）：まさちゃんの送ってくれたパチスロのフリーズの動画のような動き（台の絵や音は使わない）
   白く光る → 明るい色の帯が横に流れる（走査線・青いブロック・縦の線）→ 赤い粒 → <B> 青い画面にまぶしい横の帯・白い光がふくらむ・細い稲妻
   → <W> まわりが暗くなって青白い横一本線（まん中にフレア・線にまとわりつく1pxの細い電気がバチバチ）→ <Z> 線が両はしから点に縮む・光の粒が散る → 真っ暗
   1コマ＝1/30秒。光の点めつを防ぐ：明るい色の帯どうしは明るさ0.8より上（切りかわっても点めつにならない）。強く光るのは、まん中の帯と細い線・小さな粒だけ ===== */
.pc{z-index:39;visibility:hidden;animation:vis <Z+.4> steps(1)}
.pc .pf{position:absolute;inset:0;visibility:hidden}
.pc .sm,.pc .nz,.pc .pcd{position:absolute;inset:0}
.pc i{position:absolute;visibility:hidden;animation:vis var(--t) steps(1) var(--d)}
/* 白く光る（0〜.2）・まぶしい帯のある水色（.2〜<B>）・青い画面（<B-.033>〜・<W> から暗くなる） */
.pc .p0{background:linear-gradient(172deg,#FFFFFF 0%,#F6FEFF 45%,#E6FBFF 100%);animation:vis .2s steps(1)}
.pc .pa{background:linear-gradient(180deg,#BFF2FF 0%,#ECFDFF 32%,#FFFFFF 50%,#E2FFF4 68%,#9CEBFF 100%);animation:vis .0667s steps(1) .0666s}
.pc .pb{background:linear-gradient(180deg,#7FDDFF 0%,#D5F8FF 38%,#FFFFFF 52%,#C9FFC2 74%,#6FE08E 100%);animation:vis .0667s steps(1) .1333s}
.pc .p1{background:linear-gradient(180deg,#2F8BFF 0%,#5CC6FF 30%,#C6F4FF 44%,#FFFFFF 50%,#C6F4FF 56%,#5CC6FF 70%,#2F8BFF 100%);animation:vis <B-.2> steps(1) .2s}
.pc .p2{background:radial-gradient(ellipse 130% 60% at 50% 50%,#3E7CFF 0%,#1A4BE0 30%,#0B2496 62%,#040B3E 100%);animation:vis <W+.1-B+.034> steps(1) <B-.034>,pOut .07s linear <W> forwards}
.pc .p2b{background:linear-gradient(180deg,rgba(120,200,255,0) 38%,rgba(190,235,255,.85) 47%,#FFFFFF 49.6%,#FFFFFF 50.4%,rgba(190,235,255,.85) 53%,rgba(120,200,255,0) 62%);
  animation:vis <W+.1-B+.034> steps(1) <B-.034>,pOut .07s linear <W> forwards}
@keyframes pOut{to{opacity:0}}
/* 走査線（1px）：白く光ってから <W> まで */
.pc .psl{background:repeating-linear-gradient(180deg,rgba(0,30,110,.26) 0 1px,rgba(0,0,0,0) 1px 3px);animation:vis <W+.07> steps(1)}
/* 横に流れる帯・ブロック・縦の線・赤い粒・点々（1コマずつ） */
.pc .sm i{height:var(--h);left:var(--x);top:var(--y);width:var(--w);background:linear-gradient(90deg,rgba(255,255,255,0),var(--c) 12%,var(--c) 78%,rgba(255,255,255,0))}
.pc .nz i{left:var(--x);top:var(--y);width:var(--w);height:var(--h);background:var(--c)}
/* まん中の白い光：ふくらむ・しぼむ（1コマずつ・<B>〜） */
.pc .pfx{position:absolute;left:-75px;top:<LINE-150>px;width:540px;height:300px;border-radius:50%;opacity:0;
  background:radial-gradient(ellipse 50% 50% at 50% 50%,#FFFFFF 0 16%,rgba(214,242,255,.95) 30%,rgba(120,190,255,.5) 50%,rgba(60,130,255,0) 70%);animation:pfx <W+.1-B> steps(1) <B> forwards}
/* ふくらむ → 少ししぼむ → もっとふくらむ → 線につぶれる（まん中はずっと白いまま。光る⇔暗いになるのはふちだけ） */
@keyframes pfx{0%{opacity:1;transform:scale(1)}30%{opacity:1;transform:scale(.74,.66)}56%{opacity:1;transform:scale(1.14,.94)}80%{opacity:1;transform:scale(.8,.14)}100%{opacity:0;transform:scale(.6,.08)}}
/* 青白い横一本線（.267〜）：<W> からちらつく → <Z> 両はしから縮む */
.pc .pcl{position:absolute;left:0;right:0;top:<LINE-1>px;height:2px;visibility:hidden;
  background:linear-gradient(90deg,rgba(150,200,255,.25),#D8EEFF 6%,#FFFFFF 50%,#D8EEFF 94%,rgba(150,200,255,.25));
  box-shadow:0 0 2px #FFFFFF,0 0 6px #BFE3FF,0 0 14px #4F96FF,0 0 30px #2A5CFF;
  animation:vis <Z+.18-.266> steps(1) .266s,pclFl .067s steps(1) <W> 3,pclX .18s cubic-bezier(.55,0,.9,.45) <Z> forwards}
@keyframes pclFl{0%{opacity:1}50%{opacity:.62}}
@keyframes pclX{from{transform:scaleX(1)}to{transform:scaleX(0)}}
.pc .pcf{position:absolute;left:50%;top:<LINE>px;width:0;height:0;opacity:0;animation:on1 <Z+.25-W> steps(1) <W>,pcfS .26s ease-in <Z+.08> forwards}
.pc .pcf b{position:absolute;border-radius:50%}
.pc .pcf .f1{left:-210px;top:-10px;width:420px;height:20px;background:radial-gradient(ellipse 50% 50% at 50% 50%,#FFFFFF 0 6%,rgba(190,225,255,.9) 14%,rgba(70,130,255,.45) 38%,rgba(40,90,255,0) 70%);animation:pcfP .067s steps(1) <W> 4}
.pc .pcf .f2{left:-40px;top:-40px;width:80px;height:80px;background:radial-gradient(circle,#FFFFFF 0 12%,rgba(170,215,255,.85) 26%,rgba(60,120,255,.3) 52%,rgba(40,90,255,0) 72%)}
.pc .pcf .f3{left:-1px;top:-30px;width:2px;height:60px;border-radius:1px;background:linear-gradient(180deg,rgba(255,255,255,0),#FFFFFF 50%,rgba(255,255,255,0))}
@keyframes pcfP{0%{opacity:1}50%{opacity:.72}}
@keyframes pcfS{0%{transform:scale(1)}55%{transform:scale(.4)}100%{transform:scale(0);opacity:0}}
/* 電気（稲妻）：いちばん細い線（芯0.8px・枝0.5px）。中点をずらして細かくギザギザ・枝分かれ。1コマごとに形が変わる（本物の放電のように） */
.pc .pca{position:absolute;left:0;top:0;width:390px;height:844px;overflow:visible;filter:drop-shadow(0 0 1.2px #CDEFFF) drop-shadow(0 0 4px #3D8DFF)}
.pc .pca path{fill:none;stroke:#F3FBFF;stroke-linecap:round;stroke-linejoin:round;visibility:hidden;animation:vis var(--t) steps(1) var(--d)}
/* 散る光の粒（下へ落ちながら消える） */
.pc .pcd i{left:var(--x);top:var(--y);width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);border-radius:50%;background:#D8F0FF;box-shadow:0 0 3px #5EA8FF;
  visibility:visible;opacity:0;animation:pcd var(--t) cubic-bezier(.2,.6,.4,1) var(--d) forwards}
@keyframes pcd{0%{opacity:1;translate:0 0}100%{opacity:0;translate:var(--dx) var(--dy)}}
/* ===== 3) 真っ暗（<Z+.4>〜<M>・1.5秒）→ 4) 虹色ネオンのカット（<M>〜<R>）：まさちゃんの指定の文字が、カットごとに出る
   T1「ど」「て」「き」「！」「！」→ T2「どてき！！」（階段）→ T3「どてき！！」「どてき！！」→ T4 白く光る →「ど！」×4 → T5「ど的中」「！！！！」（そろってから1.5秒）→ 結果
   どてき！！・ど！は、押した直後のPUSHのようにバグりながら（赤と水色の色ずれ・横ズレの帯）大きな筆の字で、場所と向きはバラバラ
   視覚酔い・光の点めつを防ぐ：画面全体が回る・迫る・流れる・ゆれる動きはしない（背景は止める）。動くのは文字と小さな光だけ（どの点も明るい⇔暗いが1秒に3回まで） ===== */
.mt{z-index:30}
.sc{position:absolute;inset:0;overflow:hidden;visibility:hidden}
.mfl{position:absolute;inset:0;z-index:5;background:#FFFFFF;opacity:0}
@keyframes mfl{0%{opacity:.7}100%{opacity:0}}
/* ネオンの線画：芯（白っぽい虹）と光（こい虹）を、テンゲルのアイコンからひろった線の形でくりぬく。虹色はゆっくり流れる（回らない） */
.nic{position:absolute;left:50%;top:0}
.nic .ng,.nic .nc{position:absolute;inset:0;background:repeating-linear-gradient(135deg,#FF2BD6 0,#FF9F1A 86px,#FFE53B 172px,#3CFF6A 258px,#2FD6FF 344px,#6A5BFF 430px,#FF2BD6 516px) 0 -400px/2600px 2600px no-repeat;
  -webkit-mask:url(/_blob/NGLOW) 0 0/100% 100%;mask:url(/_blob/NGLOW) 0 0/100% 100%;animation:nflow 4s linear infinite}
.nic .ng{opacity:.85}
.nic .nc{background-image:repeating-linear-gradient(135deg,#FF8AE6 0,#FFC77A 86px,#FFF08A 172px,#9CFFB4 258px,#8CEBFF 344px,#ABA2FF 430px,#FF8AE6 516px);-webkit-mask-image:url(/_blob/NCORE);mask-image:url(/_blob/NCORE)}
.nic.alt .ng{background-image:repeating-linear-gradient(135deg,#FF6A00 0,#FFE53B 104px,#FF2BD6 208px,#2FD6FF 312px,#3CFF6A 416px,#FF6A00 520px)}
.nic.alt .nc{background-image:repeating-linear-gradient(135deg,#FFB27A 0,#FFF08A 104px,#FF8AE6 208px,#8CEBFF 312px,#9CFFB4 416px,#FFB27A 520px)}
.nic.alt .ng,.nic.alt .nc{animation-name:nflow2}
@keyframes nflow{to{background-position:-729.7px -400px}}
@keyframes nflow2{to{background-position:-735.4px -400px}}
.stf{position:absolute;inset:0;background:radial-gradient(1.2px 1.2px at 20px 30px,#FFFFFF 50%,rgba(255,255,255,0) 51%) 0 0/71px 67px,radial-gradient(1px 1px at 50px 10px,#BFD8FF 50%,rgba(191,216,255,0) 51%) 0 0/53px 89px,
  radial-gradient(1.6px 1.6px at 30px 60px,#FFFFFF 50%,rgba(255,255,255,0) 51%) 0 0/113px 97px,radial-gradient(circle at 30% 30%,rgba(122,59,255,.5),rgba(122,59,255,0) 50%),
  radial-gradient(circle at 75% 70%,rgba(47,140,255,.45),rgba(47,140,255,0) 50%),#05020F}
/* 集中線：止まったまま（迫ってこない） */
.spd{position:absolute;inset:-100px;opacity:.55;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,255,255,0) 0 3deg,rgba(255,255,255,.7) 3deg 3.35deg,rgba(255,255,255,0) 3.35deg 7.3deg),
  repeating-conic-gradient(from 1.7deg at 50% 50%,rgba(80,220,255,0) 0 5deg,rgba(80,220,255,.55) 5deg 5.5deg,rgba(80,220,255,0) 5.5deg 11deg);
  -webkit-mask-image:radial-gradient(circle at 50% 50%,transparent 0 16%,#000 42%);mask-image:radial-gradient(circle at 50% 50%,transparent 0 16%,#000 42%)}
.orb{position:absolute;left:50%;top:46%;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 9%,#C8FFE0 18%,#3CFF9A 34%,rgba(60,255,154,.35) 52%,rgba(60,255,154,0) 70%);animation:orb 1.2s ease-in-out infinite alternate}
@keyframes orb{from{transform:scale(.94)}to{transform:scale(1.04)}}
/* 筆の字（まさちゃんの指定「パチンコのロゴのような字体とレインボーカラー」）：brush.py で描いた筆の形（フォントなし・写真の字の形は使わない）。
   下から：金の立体（CSS の drop-shadow を5つ重ねる・金 → こげ茶）→ 黒いふち → 金のふち → こげ茶の細いふち → 面（白 → 虹色を右下に少しずらして重ねる＝左上のふちが白く光る → 上半分につや）。まわりに白と色の光 */
.bzd{position:absolute;width:0;height:0;overflow:hidden}
.bz{position:absolute;left:0;top:0;overflow:visible}
.bz .k{fill:#0A0014;stroke:#0A0014;stroke-width:120px;stroke-linejoin:round}
.bz .g{fill:url(#bzGd);stroke:url(#bzGd);stroke-width:76px;stroke-linejoin:round}
.bz .d{fill:#3A1200;stroke:#3A1200;stroke-width:22px;stroke-linejoin:round}
.bz .w{fill:#FFFFFF}
.bz .h{fill:url(#bzGl)}
/* 光がサッと走る（「ど的中」だけ・1.1秒ごと） */
.bz .shn{animation:bzSh 1.1s ease-in-out var(--sd) infinite}
@keyframes bzSh{0%{transform:translateX(0)}60%,100%{transform:translateX(var(--s1))}}
/* T5「ど的中」「！」：ポンと出て少し傾いたまま止まる */
.bzt{position:absolute;left:var(--x);top:var(--y);width:var(--w);height:var(--h);margin:calc(var(--h) / -2) 0 0 calc(var(--w) / -2);opacity:0;transform:rotate(var(--r));
  animation:gqIn .18s cubic-bezier(.3,.7,.3,1) var(--d) forwards}
/* バグる筆の字（T1〜T4）：1文字（「ど！」は2文字）ずつ大きく、場所・大きさ・向きはバラバラ。押した直後のPUSHのように乱れる：
   赤と水色のずれ・横にずれる帯2本（それぞれ1回・1コマずつ）・まわりに小さなブロック。文字はずっとガクガクふるえる（左右上下と傾き・1秒に4回）。
   筆の字は明るさの差が大きい（黒と金のふち・虹色・白い光）ので、前のネオンの字より動きの回数をへらした（光の点めつを1秒に3回までにするため） */
.gq{position:absolute;left:var(--x);top:var(--y);width:var(--w);height:var(--h);margin:calc(var(--h) / -2) 0 0 calc(var(--w) / -2);opacity:0;transform:rotate(var(--r));
  animation:gqIn .16s cubic-bezier(.3,.7,.3,1) var(--d) forwards}
/* たたきつけるように出る：大きく → 少し小さく → ちょうど（0.16秒・はね返りは1回） */
@keyframes gqIn{0%{opacity:0;transform:rotate(var(--r)) scale(1.5)}60%{opacity:1;transform:rotate(var(--r)) scale(.92)}100%{opacity:1;transform:rotate(var(--r)) scale(1)}}
.gq .gj{position:absolute;inset:0;animation:gqV var(--vt) steps(1) var(--vd) infinite}
.gq .gr,.gq .gc{mix-blend-mode:screen;opacity:.8;animation:gqR .9s steps(1) var(--d) both}
.gq .gc{animation-name:gqC}
.gq .gr .k{fill:#FF1E5A;stroke:#FF1E5A}
.gq .gc .k{fill:#00E6FF;stroke:#00E6FF}
.gq .s{position:absolute;inset:0;opacity:0}
.gq .s1{clip-path:inset(18% -40% 60% -40%);animation:gqS1 .9s steps(1) var(--d) both}
.gq .s2{clip-path:inset(56% -40% 22% -40%);animation:gqS2 .9s steps(1) var(--d) both}
@keyframes gqR{from,to{translate:-12px 1px}}
@keyframes gqC{from,to{translate:12px -1px}}
@keyframes gqV{0%{translate:0 0;rotate:0deg}25%{translate:var(--va) calc(var(--va) * -.55);rotate:var(--vr)}50%{translate:calc(var(--va) * -.85) calc(var(--va) * .45);rotate:calc(var(--vr) * -1)}75%{translate:calc(var(--va) * .4) calc(var(--va) * .8);rotate:calc(var(--vr) * .5)}}
@keyframes gqS1{0%{opacity:0;translate:0 0}8%{opacity:1;translate:var(--a1) 0}12%{opacity:0;translate:0 0}}
@keyframes gqS2{0%{opacity:0;translate:0 0}30%{opacity:1;translate:var(--a2) 0}34%{opacity:0;translate:0 0}}
/* まわりの小さなブロック（1コマずつ） */
.bk i{position:absolute;left:var(--x);top:var(--y);width:var(--w);height:var(--h);background:var(--c);opacity:0;animation:on1 var(--t) steps(1) var(--d)}
/* 文字が出たときの光の輪（小さく1回） */
.tr{position:absolute;left:var(--x);top:var(--y);width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;border:5px solid var(--g);box-shadow:0 0 12px var(--g);opacity:0;animation:cring .45s ease-out var(--d) forwards}
@keyframes cring{0%{opacity:1;scale:.3}100%{opacity:0;scale:2}}
/* T1（<M>〜）：テンゲルのアイコンのネオン（画面よりデカい・止まっている）。まん中で大爆発 */
.t1{animation:vis <T2> steps(1) <M>}
.t1 .bg{position:absolute;inset:0;background:radial-gradient(circle at 16% 20%,#FF2BD6 0,rgba(255,43,214,0) 40%),radial-gradient(circle at 86% 16%,#2FD6FF 0,rgba(47,214,255,0) 38%),
  radial-gradient(circle at 80% 80%,#FFE53B 0,rgba(255,229,59,0) 42%),radial-gradient(circle at 18% 84%,#3CFF6A 0,rgba(60,255,106,0) 42%),radial-gradient(circle at 50% 48%,#7A3BFF 0,rgba(122,59,255,0) 58%),#14062E}
.t1 .dk{position:absolute;inset:0;background:rgba(8,2,26,.55)}
.t1 .nic{width:1100px;height:1100px;margin-left:-550px;top:-150px}
.t1 .dk2{position:absolute;inset:0;background:rgba(8,2,26,.35)}
/* T2（<M+T2>〜）：星空・光の玉 */
.t2{animation:vis <T3-T2> steps(1) <M+T2>}
/* T3（<M+T3>〜）：ネオンのギザギザ（止まっている） */
.t3{background:#06021A;animation:vis <T4-T3> steps(1) <M+T3>}
.t3 .zz{position:absolute;left:50%;top:50%;width:2800px;height:2800px;margin:-1400px 0 0 -1400px;transform:scale(.6);opacity:.5}
.t3 .zz svg{display:block;width:100%;height:100%}
/* T4（<M+T4>〜）：星空に「ど！」×4（1つずつ光の破片が飛び散る） */
.t4{animation:vis <T5-T4> steps(1) <M+T4>}
.t4 .glw{position:absolute;inset:0;background:radial-gradient(circle at 50% 44%,rgba(255,60,200,.45),rgba(122,59,255,.2) 40%,rgba(5,2,15,0) 70%)}
/* T5（<M+T5>〜<R>）：ネオンのパチンコの当たりのような虹色（黒に光る虹の光線・虹の輪・白く光るまん中・ネオンの星・きらめき）に「ど的中」「！！！！」。そろってから1.5秒 */
.t5{background:#06010F;animation:vis <R-M-T5> steps(1) <M+T5>}
.t5 .nr{position:absolute;left:50%;top:44%;width:1600px;height:1600px;margin:-800px 0 0 -800px;border-radius:50%;
  background:repeating-conic-gradient(from -1.2deg,#FF0844 0 2.4deg,rgba(0,0,0,0) 2.4deg 6deg,#FF9500 6deg 8.4deg,rgba(0,0,0,0) 8.4deg 12deg,#FFE600 12deg 14.4deg,rgba(0,0,0,0) 14.4deg 18deg,
    #19FF6E 18deg 20.4deg,rgba(0,0,0,0) 20.4deg 24deg,#00E5FF 24deg 26.4deg,rgba(0,0,0,0) 26.4deg 30deg,#C23CFF 30deg 32.4deg,rgba(0,0,0,0) 32.4deg 36deg);
  -webkit-mask-image:radial-gradient(circle,transparent 0 3%,#000 9%,#000 46%,transparent 62%);mask-image:radial-gradient(circle,transparent 0 3%,#000 9%,#000 46%,transparent 62%)}
.t5 .nr.g{filter:blur(9px);opacity:.95}
.t5 .nw{position:absolute;left:50%;top:44%;width:1600px;height:1600px;margin:-800px 0 0 -800px;border-radius:50%;
  background:repeating-conic-gradient(from 1.8deg,rgba(255,255,255,.85) 0 .5deg,rgba(255,255,255,0) .5deg 12deg);
  -webkit-mask-image:radial-gradient(circle,transparent 0 3%,#000 8%,rgba(0,0,0,.5) 30%,transparent 50%);mask-image:radial-gradient(circle,transparent 0 3%,#000 8%,rgba(0,0,0,.5) 30%,transparent 50%)}
.t5 .rg{position:absolute;left:50%;top:44%;width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);border-radius:50%;
  background:conic-gradient(#FF0844,#FF9500,#FFE600,#19FF6E,#00E5FF,#3D5BFF,#C23CFF,#FF0844);
  -webkit-mask:radial-gradient(circle,transparent 0 calc(50% - 6px),#000 calc(50% - 5px) calc(50% - 1px),transparent 50%);mask:radial-gradient(circle,transparent 0 calc(50% - 6px),#000 calc(50% - 5px) calc(50% - 1px),transparent 50%);
  filter:drop-shadow(0 0 6px rgba(255,255,255,.8)) drop-shadow(0 0 14px rgba(255,80,220,.7))}
.t5 .core{position:absolute;left:50%;top:44%;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,#FFFFFF 0 5%,rgba(255,255,255,.9) 9%,rgba(255,236,170,.55) 17%,rgba(255,120,220,.25) 30%,rgba(120,60,255,0) 52%)}
.t5 .bs{position:absolute;left:50%;top:44%;width:170px;height:170px;margin:-85px 0 0 -85px;background:linear-gradient(135deg,#FFFFFF,#FFF4B0 45%,#FFC83A);
  clip-path:polygon(50% 0,59% 41%,100% 50%,59% 59%,50% 100%,41% 59%,0 50%,41% 41%)}
.t5 .bsg{position:absolute;inset:0;filter:drop-shadow(0 0 10px #FF3BD2) drop-shadow(0 0 20px #2FF3FF)}
.t5 .spk b{filter:drop-shadow(0 0 4px var(--c))}
/* この背景だけ動く（まさちゃんの指定）：光の波が光線にそって外へ流れる（0.45秒ごと）・虹の輪が外へ広がって消える・まん中の光と星がふくらむ。回らない */
.t5 .rw{position:absolute;inset:0;
  -webkit-mask-image:repeating-conic-gradient(from -1.2deg at 50% 44%,#000 0 2.4deg,rgba(0,0,0,0) 2.4deg 6deg);mask-image:repeating-conic-gradient(from -1.2deg at 50% 44%,#000 0 2.4deg,rgba(0,0,0,0) 2.4deg 6deg)}
.t5 .rw i{position:absolute;left:50%;top:44%;width:240px;height:240px;margin:-120px 0 0 -120px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,0) 0 50%,rgba(255,250,225,.75) 63%,rgba(255,255,255,0) 77%);opacity:0;animation:rwv 1.35s cubic-bezier(.25,.1,.6,1) var(--d) infinite}
@keyframes rwv{0%{opacity:1;transform:scale(.3)}80%{opacity:.85}100%{opacity:0;transform:scale(4.6)}}
.t5 .rg{animation:rgo 1.6s ease-out var(--d) infinite}
@keyframes rgo{0%{opacity:0;transform:scale(.7)}18%{opacity:1}100%{opacity:0;transform:scale(1.45)}}
.t5 .core{animation:cbr .9s ease-in-out <M+T5> infinite alternate}
@keyframes cbr{from{scale:.9}to{scale:1.12}}
.t5 .bs{animation:cbr .9s ease-in-out <M+T5> infinite alternate}
/* ===== 5) 結果（<R>）：白く光る → 虹色の大当たりの画面（まさちゃんの指定「虹色の大当たり感強く」）に、上に「ど的中」・まん中からテーマのボード（画面はゆらさない）
   虹色の光線（止まったまま・回さない）・「ど的中」のうしろの白い光・虹の輪が外へ広がる・虹色のきらめきが上る・コイン・紙ふぶき ===== */
.xf{z-index:45}
.rfl{position:absolute;inset:0;background:#FFFFFF;opacity:0;animation:mfl .4s ease-out <R> forwards}
.fin{z-index:20;opacity:0;animation:fzOn .01s linear <R> forwards}
.fsk{position:absolute;inset:0}
.fin .fb{position:absolute;inset:0;background:radial-gradient(circle at 50% 94px,#FFFFFF 0,#FFF8DC 30px,rgba(255,236,170,.8) 64px,rgba(255,190,240,0) 190px),
  radial-gradient(circle at 50% 94px,rgba(26,6,52,0) 260px,rgba(26,6,52,.32) 600px,rgba(16,4,36,.6) 900px),
  repeating-conic-gradient(from -1.75deg at 50% 94px,#FF2D55 0 3.5deg,#3A1060 3.5deg 7deg,#FF9500 7deg 10.5deg,#3A1060 10.5deg 14deg,#FFEA00 14deg 17.5deg,#3A1060 17.5deg 21deg,
    #2BFF4F 21deg 24.5deg,#3A1060 24.5deg 28deg,#00D9FF 28deg 31.5deg,#3A1060 31.5deg 35deg,#3D63FF 35deg 38.5deg,#3A1060 38.5deg 42deg,#C23CFF 42deg 45.5deg,#3A1060 45.5deg 49deg)}
/* 虹色の光線の上に白い細い光線（明るさがゆっくり変わるだけ） */
.fin .frr{position:absolute;left:50%;top:94px;width:1800px;height:1800px;margin:-900px 0 0 -900px;border-radius:50%;
  background:repeating-conic-gradient(from 1deg,rgba(255,255,255,.55) 0 .8deg,rgba(255,255,255,0) .8deg 10deg);
  -webkit-mask-image:radial-gradient(circle,#000 0 4%,transparent 50%);mask-image:radial-gradient(circle,#000 0 4%,transparent 50%);animation:frP 1.6s ease-in-out <R> infinite alternate}
/* 虹の輪：「ど的中」から外へ広がって消える（2つ・1.8秒ごと） */
.fin .frg i{position:absolute;left:50%;top:94px;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;opacity:0;
  background:conic-gradient(#FF2D55,#FF9500,#FFEA00,#2BFF4F,#00D9FF,#3D63FF,#C23CFF,#FF2D55);
  -webkit-mask:radial-gradient(circle,transparent 0 calc(50% - 5px),#000 calc(50% - 4px) calc(50% - 1px),transparent 50%);mask:radial-gradient(circle,transparent 0 calc(50% - 5px),#000 calc(50% - 4px) calc(50% - 1px),transparent 50%);
  filter:drop-shadow(0 0 6px rgba(255,255,255,.8));animation:frg 1.8s ease-out var(--d) infinite}
@keyframes frg{0%{opacity:0;transform:scale(.4)}12%{opacity:1}100%{opacity:0;transform:scale(3.4)}}
@keyframes frP{from{opacity:.75}to{opacity:1}}
.fin .emb i{position:absolute;left:var(--x);bottom:-20px;width:var(--s);height:var(--s);border-radius:50%;background:#FFFFFF;box-shadow:0 0 5px 2px var(--c);opacity:0;animation:emb var(--t) linear var(--d) infinite}
@keyframes emb{0%{opacity:0;translate:0 0}10%{opacity:1}80%{opacity:.9}100%{opacity:0;translate:var(--dx) -900px}}
/* 上の「ど的中」：筆の字（虹色・金と黒のふち・金の立体・つや・光がサッと走る）。うしろで虹色の炎が燃える・白い光 */
.dlg{position:absolute;left:0;right:0;top:282px;height:200px;opacity:0;transform:translateY(-302px) scale(.62);animation:dPop .3s cubic-bezier(.2,.9,.3,1.2) <R+.03> forwards}
@keyframes dPop{from{opacity:0;transform:translateY(-302px) scale(.85)}to{opacity:1;transform:translateY(-302px) scale(.62)}}
.dlg .dfl{position:absolute;left:-20px;right:-20px;top:-40px;bottom:-30px;border-radius:50%;
  background:radial-gradient(ellipse 50% 50% at 50% 58%,rgba(255,255,255,.95) 0,rgba(255,240,190,.8) 30%,rgba(255,120,220,.4) 55%,rgba(150,110,255,0) 74%);animation:dfl .5s ease-in-out <R> infinite alternate}
@keyframes dfl{from{transform:scale(1,1)}to{transform:scale(1.04,1.1)}}
/* 文字のうしろで燃える虹色の炎（ゆらゆら・ちらちら） */
.dlg .ffl{position:absolute;left:0;top:0;width:390px;height:200px;overflow:visible;filter:drop-shadow(0 0 6px rgba(255,255,255,.85))}
.dlg .ffl path{transform-box:fill-box;transform-origin:50% 100%;animation:flk var(--t) ease-in-out var(--d) infinite alternate}
@keyframes flk{0%{transform:scale(1,.82) skewX(-4deg)}50%{transform:scale(.92,1.08) skewX(3deg)}100%{transform:scale(1.04,1.16) skewX(-2deg)}}
/* 出たときの光の輪 */
.dlg .dr{position:absolute;left:50%;top:104px;width:260px;height:260px;margin:-130px 0 0 -130px;border-radius:50%;border:7px solid #FFF3B0;
  box-shadow:0 0 22px 4px #FFB000,inset 0 0 22px 4px #FFB000;opacity:0;animation:dr .5s ease-out <R+.12> forwards}
@keyframes dr{0%{opacity:1;transform:scale(.3)}100%{opacity:0;transform:scale(2.6)}}
.dlg .dsb{position:absolute;left:0;right:0;top:-6px;text-align:center;font:700 15px/1 "BIZ UDPGothic",sans-serif;letter-spacing:.42em;padding-left:.42em;color:#FFFFFF;text-shadow:0 0 6px #FF3BD2,0 0 14px #7A3BFF,0 2px 0 #2A0A48}
.dlg .dw{position:absolute;left:50%;top:122px;width:var(--w);height:var(--h);margin:calc(var(--h) / -2) 0 0 calc(var(--w) / -2)}
.dlg .dsp b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);margin:calc(var(--s) / -2) 0 0 calc(var(--s) / -2);background:#FFFFFF;
  clip-path:polygon(50% 0,58% 42%,100% 50%,58% 58%,50% 100%,42% 58%,0 50%,42% 42%);filter:drop-shadow(0 0 4px #FFE08A);opacity:0;animation:twinkle .9s ease-in-out var(--d) infinite}
/* まん中からボードがドンと出る（<R>・爆発）。コインはボードのうしろ・紙ふぶきは前 */
.fin .hb{z-index:6;animation:strike .45s cubic-bezier(.2,.9,.3,1.1) <R+.06> both}
@keyframes strike{0%{opacity:0;transform:translateY(-36px) scale(.7);filter:brightness(4) blur(2px)}30%{opacity:1;transform:translateY(8px) scale(1.06);filter:brightness(2.2) blur(0)}55%{transform:translateY(-4px) scale(.99);filter:brightness(1.3)}100%{transform:none;filter:none}}
.fin .conf.cb{z-index:5}
.fin .conf{z-index:7}
.fin .dlg{z-index:8}
.conf i.cn{height:var(--w);border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFFBE0 0 16%,#FFD54A 32%,#E0A100 70%,#9A6A00 100%);box-shadow:0 0 6px rgba(255,220,120,.9);animation:coin var(--t) linear var(--d) infinite}
@keyframes coin{0%{opacity:1;transform:translateY(0) rotateY(0)}85%{opacity:1}100%{opacity:0;transform:translateY(900px) rotateY(1080deg)}}
.ov.fz .close{z-index:60}
/* ボード（boards.py の .rb.fz：枠は虹色・回さない）の動き：見出しがたたきつけるように出て虹色が流れる・帯・超大穴の馬番の輪の色が回る・3連単の行に光が走る */
.fz .bh{animation:bhSlam .3s cubic-bezier(.2,1.5,.4,1) <R+.3> both,rbowText 1.2s linear <R+.3> infinite}
.zrib{animation:rowIn .22s ease-out <R+.36> both}
.n.zx{animation:zx 1.2s linear infinite}
@keyframes zx{0%,100%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FF3B3B,0 0 10px 4px rgba(255,59,59,.65)}20%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FFC21A,0 0 10px 4px rgba(255,194,26,.65)}40%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #2DBB55,0 0 10px 4px rgba(45,187,85,.65)}60%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #1FA8E0,0 0 10px 4px rgba(31,168,224,.65)}80%{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #B34CFF,0 0 10px 4px rgba(179,76,255,.65)}}
.fz .brows li.top::after{animation:glint 1.8s ease-in-out <R+.6> infinite}
/* 視差効果を減らす：フリーズ（プチュン）・ネオンのカット・虹の輪・きらめき・紙ふぶきを止める。押すと1秒真っ暗 → 虹色の画面と「ど的中」（上）・ボードをふわっと出す */
@media (prefers-reduced-motion:reduce){
  .push.fz,.push.fz::before,.push.fz .face,.push.fz .glit b,.pshadow.fz,.tap.fz,.aura,.prays,.edge,.frame b,.n.zx,.fz .brows li.top::after{animation:none!important}
  .push.fz::after,.ov.fz .pc,.ov.fz .mt,.ov.fz .xf,.ov.fz .emb,.ov.fz .conf,.ov.fz .dsp,.ov.fz .dr,.ov.fz .frg{display:none}
  .push.fz .glit b{opacity:.6}
  .ov.fz{--t0:1.9s}
  .ov.fz .fin{animation:fadeIn .6s ease-out 1s both!important}
  .ov.fz .frr,.ov.fz .dfl,.ov.fz .ffl path{animation:none!important}
  .ov.fz .bz .shn{display:none}
  .ov.fz .dlg{animation:none!important;opacity:1}
  .ov.fz .hb{animation:fadeIn .5s ease-out 1.3s both!important}
  .fz .bh{animation:fadeIn .4s ease-out 1.6s both!important}
  .zrib{animation:fadeIn .4s ease-out 1.7s both!important}
}
'''

def header(banner=BANNER, alt=RANCH_ALT, svg=None):
    img = svg or f'<img class="bnr" src="{banner}" alt="{alt}">'
    return f'''  <header class="hd">
    <div class="hd-r1">
      <div class="logo">テンゲル<span class="sr">Ⅲ</span><span class="iii" aria-hidden="true"><i></i><i></i><i></i></span></div>
      <button class="mbtn" type="button"><svg {SVG_A}><path d="M3.5 5.5h6a2.5 2.5 0 0 1 2.5 2.5v11a2 2 0 0 0-2-2H3.5z"></path><path d="M20.5 5.5h-6A2.5 2.5 0 0 0 12 8v11a2 2 0 0 1 2-2h6.5z"></path></svg>説明書</button>
    </div>
  </header>
  {img}'''


HEADER = header()


# ---------- テーマの見本：記録する画面をそのテーマの色と形に（変数とルールは boards.py の BY_ID ＝ 判定画面と同じ値） ----------
def theme_form_css(tid):
    t = BY_ID[tid]
    v = dict(t['v'])
    v.setdefault('btn', 'var(--gold)')
    v.setdefault('znBg', 'var(--gold)')
    out = ['.ph{' + ';'.join(f'--{k}:{x}' for k, x in v.items()) + '}', scoped(t['rules'], '.ph')]
    if tid == 'gold':   # カッコいい：判定画面（Judge_Gold）と同じ　ななめの格子の背景・金の線の帯・金の字・カードの角のひし形。上の絵は160pxぜんぶ（おしりの ぷるん が見えるように）
        out.append('.ph{background-size:auto}\n.ph .hd{border-bottom:0}\n.ph .w2{border:var(--w2B)}\n.ph .bnr{height:160px;object-position:50% 50%}\n'
                   '.ph .card::before,.ph .card::after{content:"";position:absolute;top:-7px;width:10px;height:10px;transform:rotate(45deg);background:linear-gradient(135deg,#FFF1B8,#C9952B);border:1px solid #5A400A}\n'
                   '.ph .card::before{left:-7px}\n.ph .card::after{right:-7px}')
    if tid == 'ranch':  # 牧場：上の絵は160pxぜんぶ（判定画面と同じ・馬が右はしから左はしまで行ったり来たり）
        out.append('.ph .bnr{height:160px}')
    if tid == 'sakura':  # 桜：上の絵は160pxぜんぶ（花びらが上から下まで降る）・上の帯の下の線は判定画面と同じ
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'sunset':  # 夕焼け：上の絵は160pxぜんぶ（馬が走って地面が流れる・夕日が沈んで また戻る）・上の帯の下は判定画面と同じ（線なし・だいだい → 紫の光の線）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'cute':       # かわいい：上の絵は160pxぜんぶ（ハートとポニーが近づいて、ポニーが飛び跳ねる）・上の帯の下は判定画面と同じ（ピンクの波だけ・茶色の線なし）
        out.append('.ph .bnr{height:160px}\n.ph .hd{border-bottom:0}')
    if tid == 'kids':       # 子供向け：上の絵は160pxぜんぶ（毛糸玉が左から右へ転がって、馬が跳ねる）・上の帯は判定画面と同じ（毛糸の編み目・縫い目）
        out.append('.ph .bnr{height:160px}')
    if tid == 'fireworks':  # 花火：上の絵は160pxぜんぶ（花火が消えて、また打ち上がる）・上の帯の下は判定画面と同じ（ちょうちん）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'pixel':     # ドット絵：上の絵は160pxぜんぶ（馬が走って、ときどきジャンプか一回転・ときどき立ち止まる）・上の帯の下は判定画面と同じ（水色の線）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'neon':      # ネオン：上の絵は160pxぜんぶ（馬が走って、流れ星）・上の帯の下は判定画面と同じ（ピンクの線）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'silks':     # 勝負服：上の絵は160pxぜんぶ（馬が走って、柄が流れる）・上の帯の下は判定画面と同じ（勝負服のしま）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'stars':     # 星座：上の絵は160pxぜんぶ（星が流れて、ペガサスがきらきら）・上の帯の下は判定画面と同じ（星座の線）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'carousel':  # メリーゴーランド：上の絵は160pxぜんぶ（木馬が上下する）・上の帯の下は判定画面と同じ（線なし）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'ink':      # 水墨画：上の絵は160pxぜんぶ（2頭が走る）・上の帯の下は判定画面と同じ（線はなく、筆の線だけ）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'news':     # 競馬新聞：上の絵は160pxぜんぶ（墨の馬が走る）・上の帯の下の二重線は判定画面と同じ
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'newyear':  # お正月：上の絵は160pxぜんぶ（初日の出の光が回る）・上の帯の下の金の線は判定画面と同じ
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'snow':    # 雪：上の絵は160pxぜんぶ（雪が上から下まで降る）・上の帯の下は判定画面と同じ（線なし）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'autumn':  # 紅葉：上の絵は160pxぜんぶ（もみじが上から下まで降る）・上の帯の下の線は判定画面と同じ
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid in EVENTS:    # 行事の4テーマ：上の絵は160pxぜんぶ（判定画面と同じ）・上の帯の下は判定画面と同じ（クリスマス＝赤い線・ハロウィン＝かぼちゃ・バレンタイン＝とろけるチョコ・ホワイトデー＝まるい波）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'sea':     # 海：上の絵は160pxぜんぶ（走る馬と流れる景色）・上の帯の下のふちは判定画面と同じ
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'lucky':   # 開運：上の絵は160pxぜんぶ（小判が上から下まで降る・招き馬の右前足が 下まで 振り下ろされる）・上の帯の下は判定画面と同じ（赤と金の線だけ）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'chalk':   # 黒板：上の絵は160pxぜんぶ（黒板と チョーク受けまで・黒板消しとチョークが動く）・上の帯の下は判定画面と同じ（こい木の色の線）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid in ('silver', 'golden'):   # シルバー帯・ゴールド帯：上の絵は160pxぜんぶ（きらめきが またたく・光の粒が うしろへ流れる・光の輪を 光が回る）・上の帯の下は判定画面と同じ（光る線）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    if tid == 'tengel':   # マスター帯：上の絵は160pxぜんぶ（数字が動く・枠の 緑の雷）・上の帯の下は判定画面と同じ（金の うすい線）
        out.append('.ph .bnr{height:160px;object-position:50% 50%}\n.ph .hd{border-bottom:var(--hdB)}')
    return '\n'.join(out) + '\n'


GP_CSS = r'''
/* ---------- カッコいい（金色）の的中ボタン：黒と金の、ぷるんぷるんしたPUSH（まさちゃんの指定） ----------
   黒いつやの面（上にうすい光）・金のふち（グラデーション）・金の「PUSH」。下を中心に、つぶれる → のびる をくり返す（ゼリーのように・1.2秒ごと） */
.push.gp,.pressed.gp{border:6px solid transparent;
  background:radial-gradient(70% 44% at 50% 10%,rgba(255,255,255,.5),rgba(255,255,255,.1) 58%,rgba(255,255,255,0) 100%) padding-box,
    linear-gradient(180deg,#3D3527 0%,#17130C 40%,#050403 100%) padding-box,
    linear-gradient(135deg,#8A6514,#F7E08A 22%,#C9952B 42%,#FFF1B8 62%,#D8A537 80%,#8A6514) border-box}
.push.gp{box-shadow:inset 0 -8px 0 rgba(0,0,0,.6),inset 0 2px 0 rgba(255,241,184,.4),0 0 0 2px #5A400A,0 8px 0 2px #2A1E06,0 0 26px rgba(243,212,122,.45),0 22px 34px rgba(0,0,0,.6);
  transform-origin:50% 100%;animation:gpPurun 1.2s ease-in-out infinite,popIn .35s cubic-bezier(.2,1.6,.4,1) both}
.push.gp span{display:block;background:linear-gradient(180deg,#FFF6D0 0%,#F3D47A 42%,#C9952B 60%,#FFE9A8 100%);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;
  filter:drop-shadow(0 2px 0 #000) drop-shadow(0 0 8px rgba(243,212,122,.5))}
.push.gp::after{border-color:rgba(243,212,122,.9)}
@keyframes gpPurun{0%,62%,100%{transform:translateY(0) scale(1,1)}8%{transform:translateY(0) scale(1.16,.82)}20%{transform:translateY(-10px) scale(.88,1.14)}32%{transform:translateY(0) scale(1.08,.93)}42%{transform:translateY(-3px) scale(.96,1.04)}52%{transform:translateY(0) scale(1.02,.98)}}
.pshadow.gp{animation:gpShad 1.2s ease-in-out infinite}
@keyframes gpShad{0%,62%,100%{transform:scale(1,1);opacity:.5}8%{transform:scale(1.2,1);opacity:.62}20%{transform:scale(.8,1);opacity:.32}32%{transform:scale(1.08,1);opacity:.55}42%{transform:scale(.95,1);opacity:.45}}
.tap.gp{color:#F3D47A}
.pressed.gp{box-shadow:0 0 0 2px #5A400A,0 0 30px rgba(243,212,122,.6)}
'''


# ---------- 牧場の的中ボタン：芝生でできたPUSH（まさちゃんの指定） ----------
TURF_C = ('#8ED24C', '#6DBE34', '#A9E26A', '#5AAE2B', '#7CC93E')       # 草の葉の色


def turf_blade(x, y, ang, h, w, c):
    """草の葉1枚：根もと (x, y)・向き ang（度。-90＝上）・長さ h・根もとの幅 w"""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)          # 葉の向き
    nx, ny = -uy, ux                           # 横
    tip = (x + ux * h, y + uy * h)
    bend = .18 * h                             # 先が少し曲がる
    l, r = (x - nx * w / 2, y - ny * w / 2), (x + nx * w / 2, y + ny * w / 2)
    q1 = (x + ux * h * .55 - nx * (w * .25 - bend * .3), y + uy * h * .55 - ny * (w * .25 - bend * .3))
    q2 = (x + ux * h * .5 + nx * (w * .3 + bend * .3), y + uy * h * .5 + ny * (w * .3 + bend * .3))
    p = lambda v: f'{v[0]:.1f} {v[1]:.1f}'
    return f'<path d="M{p(l)} Q{p(q1)} {p(tip)} Q{p(q2)} {p(r)} Z" fill="{c}"/>'


def rr_points(w, h, rad, step):
    """角丸の四角のふち：(x, y, 外向きの角度) を step ごとに（上 → 右 → 下 → 左）"""
    pts, L = [], []
    segs = [((rad, 0), (w - rad, 0), -90), ('arc', (w - rad, rad), -90, 0), ((w, rad), (w, h - rad), 0), ('arc', (w - rad, h - rad), 0, 90),
            ((w - rad, h), (rad, h), 90), ('arc', (rad, h - rad), 90, 180), ((0, h - rad), (0, rad), 180), ('arc', (rad, rad), 180, 270)]
    for sg in segs:
        if sg[0] == 'arc':
            (cx, cy), a0, a1 = sg[1], sg[2], sg[3]
            n = max(1, round(math.radians(a1 - a0) * rad / step))
            for i in range(n):
                a = a0 + (a1 - a0) * (i + .5) / n
                pts.append((cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a)), a, 'c'))
        else:
            (x0, y0), (x1, y1), a = sg
            n = max(1, round(math.hypot(x1 - x0, y1 - y0) / step))
            for i in range(n):
                t = (i + .5) / n
                pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, a, 's'))
    return pts


def daisy(cx, cy, r, petal='#FFFFFF', mid='#F7C531', n=7):
    out = ''.join(f'<ellipse cx="{cx + r * .62 * math.cos(2 * math.pi * i / n):.1f}" cy="{cy + r * .62 * math.sin(2 * math.pi * i / n):.1f}" rx="{r * .42:.1f}" ry="{r * .27:.1f}" '
                  f'transform="rotate({360 * i / n:.0f} {cx + r * .62 * math.cos(2 * math.pi * i / n):.1f} {cy + r * .62 * math.sin(2 * math.pi * i / n):.1f})" fill="{petal}"/>' for i in range(n))
    return out + f'<circle cx="{cx}" cy="{cy}" r="{r * .36:.1f}" fill="{mid}"/>'


def turf_svg(seed=8):
    """芝生のPUSHの絵（ボタンの 200×100 の上に重ねる。まわりに葉が出るので -16〜216 × -22〜128）：
       下に土の側面（小石）→ 芝の面（グラデーション・刈ったあとの縞・葉の模様・上の光）→ ふちの葉（上の葉は風でそよぐ .gs1・.gs2）→ 花"""
    rnd = random.Random(seed)
    W_, H_, RAD = 200, 100, 26
    defs = ('<defs><linearGradient id="grF" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A6E463"/><stop offset=".32" stop-color="#74C83A"/>'
            '<stop offset=".72" stop-color="#52A82A"/><stop offset="1" stop-color="#3B8A1E"/></linearGradient>'
            '<linearGradient id="grS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A5A2E"/><stop offset="1" stop-color="#4E2F14"/></linearGradient>'
            '<radialGradient id="grH" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="grC"><rect width="{W_}" height="{H_}" rx="{RAD}"/></clipPath></defs>')
    # 土の側面（ボタンの厚み）と小石
    out = f'<rect x="-1" y="10" width="{W_ + 2}" height="{H_}" rx="{RAD + 1}" fill="url(#grS)"/>'
    for i in range(11):
        x = 16 + i * 16.8 + rnd.uniform(-4, 4)
        out += f'<ellipse cx="{x:.1f}" cy="{H_ + rnd.uniform(3, 7):.1f}" rx="{rnd.uniform(1.4, 2.6):.1f}" ry="{rnd.uniform(1, 1.6):.1f}" fill="{rnd.choice(("#A87A4A", "#B98C5A", "#3E2410"))}"/>'
    # ふちの葉（下と横・動かない）：芝の面のうしろ
    back = ''
    for x, y, a, kind in rr_points(W_, H_, RAD, 5.2):
        if -90 < a < 270 and not (a == -90):
            if a == 90 and rnd.random() < .45:
                continue
            h = rnd.uniform(4, 7) if a in (0, 180) or kind == 'c' else rnd.uniform(3, 5.5)
            if a == 90:
                h = rnd.uniform(3.5, 6)
            back += turf_blade(x - math.cos(math.radians(a)) * 2, y - math.sin(math.radians(a)) * 2, a + rnd.uniform(-22, 22), h, rnd.uniform(3.4, 5), rnd.choice(TURF_C))
    out += back
    # 芝の面
    out += f'<rect width="{W_}" height="{H_}" rx="{RAD}" fill="url(#grF)"/>'
    face = ''
    # 刈ったあとの縞（競馬場の芝のように・うすく）
    for i in range(-2, 8):
        x = i * 34
        face += f'<path d="M{x} -2 L{x + 17} -2 L{x - 9} 104 L{x - 26} 104 Z" fill="#FFFFFF" opacity=".09"/>'
    # 葉の模様
    for i in range(150):
        x, y = rnd.uniform(2, W_ - 2), rnd.uniform(4, H_ - 2)
        if 30 < x < 170 and 24 < y < 76 and rnd.random() < .55:
            continue
        hh = rnd.uniform(3, 6.5)
        c = rnd.choice(('#C6F288', '#B3EA74', '#3F8F1F', '#4A9A25', '#9DDC5C'))
        face += f'<path d="M{x:.1f} {y:.1f} q{rnd.uniform(-1.2, 1.2):.1f} {-hh / 2:.1f} {rnd.uniform(-1.8, 1.8):.1f} {-hh:.1f}" stroke="{c}" stroke-width="1.3" stroke-linecap="round" fill="none" opacity=".6"/>'
    face += f'<ellipse cx="{W_ / 2}" cy="12" rx="86" ry="17" fill="url(#grH)"/>'
    out += f'<g clip-path="url(#grC)">{face}</g>'
    out += f'<rect x="1.5" y="1.5" width="{W_ - 3}" height="{H_ - 3}" rx="{RAD - 1.5}" fill="none" stroke="#2F7A14" stroke-opacity=".35" stroke-width="3"/>'
    # 上のふちの葉（風でそよぐ・2つの組が交互に）
    sway = ['', '']
    for x, y, a, kind in rr_points(W_, H_, RAD, 4.2):
        if a == -90:
            i = int(x / 4.2) % 2
            sway[i] += turf_blade(x + rnd.uniform(-1, 1), y + 2.5, -90 + rnd.uniform(-16, 16), rnd.uniform(8, 15), rnd.uniform(3.6, 5.4), rnd.choice(TURF_C))
        elif kind == 'c' and (a < 0 or a > 180):     # 上の角：少し短く
            out += turf_blade(x - math.cos(math.radians(a)) * 2.5, y - math.sin(math.radians(a)) * 2.5, a + rnd.uniform(-14, 14), rnd.uniform(6, 10), rnd.uniform(3.4, 5), rnd.choice(TURF_C))
    # 花：上のふちに背の高いデイジー（そよぐ）・面の左下に白・右上に黄色
    sway[0] += '<path d="M150 3 Q151 -6 153.5 -13" stroke="#4E9E27" stroke-width="2" fill="none" stroke-linecap="round"/>' + daisy(153.5, -15, 6.4)
    out += f'<g class="gs1">{sway[0]}</g><g class="gs2">{sway[1]}</g>'
    out += daisy(21, 78, 6.2) + daisy(181, 24, 5.6, petal='#FFE14D', mid='#F2A33A', n=6) + daisy(34, 88, 4, n=6)
    return (f'<i class="turf" aria-hidden="true"><svg viewBox="-16 -22 232 150" width="232" height="150">{defs}{out}</svg></i>')


def clippings(n=18, seed=4):
    """押した瞬間に、芝の葉と花びらがパッと舞う（ボタンのまん中から外へ → 少し落ちて消える）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 300 + rnd.uniform(-8, 8))
        dist = rnd.uniform(95, 165)
        x, y = math.cos(a) * dist * 1.25, math.sin(a) * dist * .85 - 20
        petal = i % 6 == 5
        c = '#FFFFFF' if petal and i % 12 == 5 else ('#FFE14D' if petal else rnd.choice(TURF_C))
        out += (f'<i class="{"pt" if petal else "bl"}" style="--x:{x:.0f}px;--y:{y:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(140, 320):.0f}deg;'
                f'--d:{rnd.uniform(0, .08):.2f}s;--c:{c}"></i>')
    return f'<div class="clips" aria-hidden="true">{out}</div>'


GR_CSS = r'''
/* ---------- 牧場の的中ボタン：芝生でできたPUSH（まさちゃんの指定） ----------
   芝の面（上は明るい黄緑 → 下は濃い緑・刈ったあとのうすい縞・葉の模様）・まわりに葉・下に土の側面（ボタンの厚み）・小さな花。
   白い「PUSH」に濃い緑のふち。上下の動きは的中と同じ。上のふちの葉と背の高い花が風でそよぐ（2.4秒）。押すと同じ芝のボタンがはじけて、芝の葉と花びらがパッと舞う */
.push.gr{background:none;box-shadow:0 26px 30px rgba(0,0,0,.42)}
.gr .turf{position:absolute;left:-16px;top:-22px;width:232px;height:150px;pointer-events:none}
.gr .turf svg{display:block;width:232px;height:150px;overflow:visible}
.push.gr span{color:#FFFFF4;text-shadow:0 3px 0 #2A6410,1.5px 0 0 #2A6410,-1.5px 0 0 #2A6410,0 -1.5px 0 #2A6410,0 0 14px rgba(255,255,230,.55)}
.push.gr::after{border-color:rgba(205,245,150,.95)}
.gr .gs1,.gr .gs2{transform-box:view-box;transform-origin:0 0;animation:grSway 2.4s ease-in-out infinite}
.gr .gs2{animation-delay:-1.2s}
@keyframes grSway{0%,100%{transform:skewX(-10deg)}50%{transform:skewX(10deg)}}
.tap.gr{color:#E6FFC2}
.pressed.gr{background:none;box-shadow:none}
.clips{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips i{position:absolute;opacity:0;animation:grFly .95s cubic-bezier(.15,.7,.3,1) var(--d) both}
.clips .bl{left:-2px;top:-7px;width:4px;height:14px;border-radius:50% 50% 30% 30%/90% 90% 10% 10%;background:var(--c)}
.clips .pt{left:-4px;top:-4px;width:8px;height:8px;border-radius:50% 50% 50% 0;background:var(--c)}
@keyframes grFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.5)}10%{opacity:1}62%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(var(--x),calc(var(--y) + 50px)) rotate(calc(var(--r) * 1.5)) scale(.9)}}
@media (prefers-reduced-motion:reduce){.gr .gs1,.gr .gs2{animation:none}.clips{display:none}}
'''


# ---------- 桜の的中ボタン：桜がついたPUSH（まさちゃんの指定） ----------
SK_PETAL = 'M0 0 C-6 -4 -9 -13 -4.4 -18.5 L0 -15.6 L4.4 -18.5 C9 -13 6 -4 0 0 Z'     # 判定画面のすみの桜（themes20.py の orn_sakura）と同じ花びら


def sk_flower(cx, cy, r, rot=0, fill='#F9C3D3'):
    """桜の花（5まい・先にくぼみ・濃い桜色のふち・おしべ）。r＝花びらの長さ"""
    k = r / 18.5
    out = ''.join(f'<path d="{SK_PETAL}" fill="{fill}" stroke="#C9577F" stroke-width="{1.2 / k:.2f}" stroke-linejoin="round" '
                  f'transform="translate({cx} {cy}) rotate({j * 72 + rot}) scale({k:.3f})"/>' for j in range(5))
    for j in range(5):
        a = math.radians(j * 72 + rot + 36 - 90)
        x, y = cx + r * .34 * math.cos(a), cy + r * .34 * math.sin(a)
        out += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E0668F" stroke-width="{max(.7, .05 * r):.2f}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{max(.9, .065 * r):.2f}" fill="#E0668F"/>'
    return out + f'<circle cx="{cx}" cy="{cy}" r="{.14 * r:.2f}" fill="#E0668F"/>'


def sk_bud(x, y, ang, s=1):
    return (f'<g transform="translate({x} {y}) rotate({ang}) scale({s})"><path d="M0 0 C-3.5 -3 -3.5 -9 0 -11 C3.5 -9 3.5 -3 0 0 Z" fill="#F07FA6" stroke="#C9577F" stroke-width="1"/>'
            f'<path d="M0 1 C-3 -1 -3.5 -3 -2.6 -4.4 L0 -2.6 L2.6 -4.4 C3.5 -3 3 -1 0 1 Z" fill="#8DBF55"/></g>')


def sk_leaf(x, y, ang, s=1):
    return (f'<g transform="translate({x} {y}) rotate({ang}) scale({s})"><path d="M0 0 C4 -3 12 -3 17 0 C12 3 4 3 0 0 Z" fill="#A8D46F" stroke="#6E9E3A" stroke-width=".9"/>'
            f'<path d="M1 0 L15 0" stroke="#6E9E3A" stroke-width=".7"/></g>')


def sakura_push_svg():
    """PUSHについた桜（ボタン 200×100 の上に重ねる。まわりに出るので -30〜230 × -36〜136）：
       左上に枝（花3つ・つぼみ・若葉）・右下にも花2つ。枝ごとに小さくゆれる（.skb1・.skb2）。左上の花から花びらが3まい、ひらひら落ちる（.skd）"""
    br1 = ('<path d="M-30 18 C-16 6 6 -10 34 -20 C44 -24 54 -26 62 -28" fill="none" stroke="#7A4A3A" stroke-width="4.2" stroke-linecap="round"/>'
           '<path d="M8 -9 C14 -20 22 -26 30 -32" fill="none" stroke="#7A4A3A" stroke-width="2.6" stroke-linecap="round"/>'
           '<path d="M-28 16.5 C-15 5 6 -11 33 -21.4" fill="none" stroke="#A9705A" stroke-width="1.2" stroke-linecap="round" opacity=".8"/>')
    br1 += sk_leaf(-14, 4, -128, .9) + sk_leaf(40, -22, -20, .8) + sk_bud(60, -28, 58, .95) + sk_bud(30, -32, 18, .8)
    br1 += sk_flower(-18, 14, 14.5, 10, '#FFF0F5') + sk_flower(26, -17, 14, 30) + sk_flower(1, -4, 18, -6, '#FBD3E0')
    br2 = ('<path d="M232 98 C220 106 206 112 186 120" fill="none" stroke="#7A4A3A" stroke-width="3.6" stroke-linecap="round"/>')
    br2 += sk_leaf(214, 109, 150, .85) + sk_bud(234, 92, 120, .9)
    br2 += sk_flower(180, 118, 13.5, 20, '#FFF0F5') + sk_flower(204, 104, 17, -12, '#FBD3E0')
    drops = ''.join(f'<g class="skd" style="animation-delay:{-1.1 * j:.1f}s"><path d="{SK_PETAL}" transform="translate({x} {y}) scale(.36)" fill="#FBD3E0" stroke="#C9577F" stroke-width="2.6"/></g>'
                    for j, (x, y) in enumerate(((10, -2), (26, -12), (-8, 10))))
    stuck = ''.join(f'<path d="{SK_PETAL}" transform="translate({x} {y}) rotate({a}) scale(.4)" fill="#FFF0F5" stroke="#C9577F" stroke-width="2.4" opacity=".95"/>'
                    for x, y, a in ((176, 22, 35), (22, 86, -50)))      # ボタンの面にのった花びら
    return ('<i class="sakb" aria-hidden="true"><svg viewBox="-30 -36 262 172" width="262" height="172">'
            f'{stuck}<g class="skb1">{br1}</g><g class="skb2">{br2}</g>{drops}</svg></i>')


def petal_burst(n=20, seed=6):
    """押した瞬間に、桜の花びらがパッと舞う（ボタンのまん中から外へ → ひらひら落ちて消える）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 330 + rnd.uniform(-8, 8))
        dist = rnd.uniform(100, 175)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 24
        out += (f'<i class="{("pa", "pb", "pc")[i % 3]}" style="--x:{x:.0f}px;--y:{y:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(160, 360):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips sk" aria-hidden="true">{out}</div>'


SK_PETAL_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-6.5 -13 13 14'%3E%3Cpath d='M0 0 C-6 -4 -9 -13 -4.4 -18.5 L0 -15.6 L4.4 -18.5 C9 -13 6 -4 0 0 Z' "
                "transform='scale(.62)' fill='%23COLOR' stroke='%23C9577F' stroke-width='1.6'/%3E%3C/svg%3E")

SK_CSS = r'''
/* ---------- 桜の的中ボタン：桜がついたPUSH（まさちゃんの指定） ----------
   桜色の面（上は明るく → 下は濃い桜色）・白っぽい桜色のふち・濃い桜色のふち・濃い桜色の厚み。白い「PUSH」に濃い桜色の影。
   左上に桜の枝（花3つ・つぼみ・若葉）・右下にも花2つ（判定画面のすみの桜と同じ花びら）。枝が小さくゆれて、左上の花から花びらがひらひら落ちる。
   上下の動きは的中と同じ。押すと同じボタンがはじけて、桜の花びらがパッと舞う */
.sk{--pushA:#F2739F;--pushB:#C2416E;--pushC:#FFC6D9;--rim:#FFF3F7;--rimD:#EE9DB8;
  --pushFace:radial-gradient(72% 40% at 50% 14%,rgba(255,255,255,.9),rgba(255,255,255,.3) 58%,rgba(255,255,255,0) 100%),linear-gradient(180deg,var(--pushC) 0%,var(--pushA) 40%,var(--pushB) 86%,#8E2A50 100%)}
.push.sk{box-shadow:inset 0 -9px 0 rgba(120,20,60,.16),inset 0 2px 0 rgba(255,255,255,.65),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #B5527A,0 22px 34px rgba(80,10,40,.45)}
.push.sk span{text-shadow:0 3px 0 #A3355C,0 0 14px rgba(255,255,255,.6)}
.push.sk::after{border-color:rgba(255,200,222,.95)}
.sk .sakb{position:absolute;left:-30px;top:-36px;width:262px;height:172px;pointer-events:none;z-index:3}
.sk .sakb svg{display:block;width:262px;height:172px;overflow:visible}
.sk .skb1,.sk .skb2,.sk .skd{transform-box:view-box;transform-origin:0 0}
.sk .skb1{animation:skSw1 2.8s ease-in-out infinite}
.sk .skb2{animation:skSw2 3.2s ease-in-out infinite}
@keyframes skSw1{0%,100%{transform:translate(-30px,18px) rotate(-3deg) translate(30px,-18px)}50%{transform:translate(-30px,18px) rotate(3deg) translate(30px,-18px)}}
@keyframes skSw2{0%,100%{transform:translate(232px,98px) rotate(3deg) translate(-232px,-98px)}50%{transform:translate(232px,98px) rotate(-3deg) translate(-232px,-98px)}}
.sk .skd{opacity:0;animation:skDrop 3.3s linear infinite}
@keyframes skDrop{0%{opacity:0;transform:translate(0,0) rotate(0)}8%{opacity:1}30%{transform:translate(9px,34px) rotate(70deg)}55%{transform:translate(-4px,70px) rotate(150deg)}
  80%{opacity:1;transform:translate(10px,104px) rotate(230deg)}100%{opacity:0;transform:translate(2px,128px) rotate(290deg)}}
.tap.sk{color:#FFE3EE}
.pressed.sk{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #B5527A}
.clips.sk{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.sk i{position:absolute;opacity:0;animation:skFly 1.25s cubic-bezier(.15,.7,.3,1) var(--d) both;left:-5px;top:-7px;width:10px;height:13px;background:center/contain no-repeat}
.clips.sk .pa{background-image:url("PETAL_A")}
.clips.sk .pb{background-image:url("PETAL_B")}
.clips.sk .pc{background-image:url("PETAL_C")}
@keyframes skFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.5,.5)}10%{opacity:1}45%{transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1,1)}
  70%{opacity:1;transform:translate(calc(var(--x) * 1.08),calc(var(--y) + 30px)) rotate(calc(var(--r) * 1.3)) scale(.35,1)}100%{opacity:0;transform:translate(calc(var(--x) * 1.12),calc(var(--y) + 64px)) rotate(calc(var(--r) * 1.6)) scale(1,1)}}
@media (prefers-reduced-motion:reduce){.sk .skb1,.sk .skb2{animation:none}.sk .skd,.clips.sk{display:none}}
'''.replace('PETAL_A', SK_PETAL_URI.replace('COLOR', 'FBD3E0')).replace('PETAL_B', SK_PETAL_URI.replace('COLOR', 'F7A8C4')).replace('PETAL_C', SK_PETAL_URI.replace('COLOR', 'FFF0F5'))


# ---------- 海の的中ボタン：海の模様のPUSH（まさちゃんの指定） ----------
def se_star(cx, cy, R, rot):
    """ひとで（5本の腕・先は丸く）"""
    pts = []
    for k in range(10):
        a = math.radians(rot + k * 36 - 90)
        r = R if k % 2 == 0 else R * .48
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = 'M' + ' '.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'
    dots = ''.join(f'<circle cx="{cx + R * .55 * math.cos(math.radians(rot + k * 72 - 90)):.1f}" cy="{cy + R * .55 * math.sin(math.radians(rot + k * 72 - 90)):.1f}" r="{R * .09:.1f}" fill="#FFE2B8"/>'
                   for k in range(5))
    return (f'<path d="{d}" fill="#FFA24C" stroke="#E2711D" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R * .16:.1f}" fill="#FFC27D"/>{dots}')


def sea_push_svg():
    """海の模様のPUSH（ボタン 200×100 の上に重ねる。まわりに出るので -24〜224 × -30〜130）：
       面＝海のグラデーションに青海波（白いうすい弧・下の段が上の段を隠す）・上に光・下に白い波（横に流れる .sewv）・泡が上る（.sebb）
       右上に浮き輪（判定画面のすみの浮き輪と同じ形・ゆれる .sebu）・左下に ひとで"""
    from themes20 import orn_sea
    W_, H_, RAD, R = 200, 100, 26, 14
    defs = ('<defs><linearGradient id="seF" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="100"><stop offset="0" stop-color="#8FDDF7"/>'
            '<stop offset=".38" stop-color="#36A6DE"/><stop offset=".78" stop-color="#1A72B8"/><stop offset="1" stop-color="#0E4C8A"/></linearGradient>'
            '<radialGradient id="seGl" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".62"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="seC"><rect width="{W_}" height="{H_}" rx="{RAD}"/></clipPath></defs>')
    face = f'<rect width="{W_}" height="{H_}" fill="url(#seF)"/>'
    for j in range(-1, 17):                                   # 青海波：上の段から（下の段が上の段の下半分を隠す）
        y = j * R / 2
        for i in range(-1, 9):
            cx = i * 2 * R + (R if j % 2 else 0)
            face += f'<path d="M{cx - R} {y} A{R} {R} 0 0 1 {cx + R} {y}Z" fill="url(#seF)"/>'
            face += ''.join(f'<path d="M{cx - r} {y} A{r} {r} 0 0 1 {cx + r} {y}" fill="none" stroke="#FFFFFF" stroke-opacity=".34" stroke-width="1.1"/>' for r in (R - 1.2, R - 5, R - 8.8))
    face += f'<ellipse cx="{W_ / 2}" cy="13" rx="88" ry="18" fill="url(#seGl)"/>'
    wv = ''.join(f'<path d="M{x} 86 q10 -9 20 0 q10 9 20 0" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-opacity=".9"/>' for x in range(-40, 241, 40))
    wv += f'<path d="M-40 92 {" ".join("q10 -7 20 0 q10 7 20 0" for _ in range(8))} V110 H-40Z" fill="#FFFFFF" fill-opacity=".35"/>'
    face += f'<g class="sewv">{wv}</g>'
    face += ''.join(f'<circle class="sebb" style="animation-delay:{-d:.1f}s" cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity=".9"/>'
                    for x, y, r, d in ((30, 96, 2.6, 0), (58, 100, 1.8, 1.1), (150, 98, 2.2, .5), (176, 100, 1.6, 2.0), (112, 100, 1.4, 1.6)))
    out = f'<g clip-path="url(#seC)">{face}</g>'
    out += f'<rect x="1.5" y="1.5" width="{W_ - 3}" height="{H_ - 3}" rx="{RAD - 1.5}" fill="none" stroke="#0E3A66" stroke-opacity=".28" stroke-width="3"/>'
    out += f'<g class="sebu"><g transform="translate(176 -16) rotate(8 22 23) scale(.95)">{orn_sea()}</g></g>'
    out += se_star(4, 96, 17, 12)
    return ('<i class="seab" aria-hidden="true"><svg viewBox="-24 -30 248 160" width="248" height="160">'
            f'{defs}{out}</svg></i>')


def water_burst(n=22, seed=9):
    """押した瞬間に、水しぶきがパッと飛ぶ（ボタンのまん中から外へ → 落ちて消える）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 320 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 170)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 26
        s = rnd.uniform(.6, 1.3)
        out += f'<i style="--x:{x:.0f}px;--y:{y:.0f}px;--s:{s:.2f};--d:{rnd.uniform(0, .08):.2f}s"></i>'
    return f'<div class="clips se" aria-hidden="true">{out}</div>'


SE_CSS = r'''
/* ---------- 海の的中ボタン：海の模様のPUSH（まさちゃんの指定） ----------
   面＝海のグラデーション（明るい水色 → 深い青）に青海波（白いうすい弧）・上に光・下に白い波（横に流れる）・泡が上る。
   白い泡のふち・紺のふち・紺の厚み。白い「PUSH」に紺の影。右上に浮き輪（ゆれる）・左下に ひとで。
   上下の動きは的中と同じ。押すと同じボタンがはじけて、水しぶきが飛ぶ */
.se{--pushA:#2EA0DC;--pushB:#0E5A9C;--pushC:#8FDDF7;--rim:#EAF8FF;--rimD:#0E3A66;
  --pushFace:radial-gradient(72% 40% at 50% 14%,rgba(255,255,255,.9),rgba(255,255,255,.3) 58%,rgba(255,255,255,0) 100%),linear-gradient(180deg,var(--pushC) 0%,var(--pushA) 40%,var(--pushB) 86%,#0A3766 100%)}
.push.se{box-shadow:inset 0 -9px 0 rgba(0,20,60,.18),inset 0 2px 0 rgba(255,255,255,.6),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #0B2D52,0 22px 34px rgba(0,20,50,.5)}
.push.se span{text-shadow:0 3px 0 #0B3A6B,0 0 14px rgba(255,255,255,.55)}
.push.se::after{border-color:rgba(150,230,255,.95)}
.se .seab{position:absolute;left:-24px;top:-30px;width:248px;height:160px;pointer-events:none}
.se .seab svg{display:block;width:248px;height:160px;overflow:visible}
.se .sewv{animation:seWave 2.6s linear infinite}
@keyframes seWave{from{transform:translateX(0)}to{transform:translateX(-40px)}}
.se .sebb{opacity:0;animation:seBub 3s ease-in infinite}
@keyframes seBub{0%{opacity:0;transform:translateY(0)}15%{opacity:.95}100%{opacity:0;transform:translateY(-74px)}}
.se .sebu{transform-box:view-box;transform-origin:0 0;animation:seBuoy 2.6s ease-in-out infinite}
@keyframes seBuoy{0%,100%{transform:translate(197px,-14px) rotate(-6deg) translate(-197px,14px)}50%{transform:translate(197px,-14px) rotate(6deg) translate(-197px,14px)}}
.tap.se{color:#DFF6FF}
.pressed.se{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #0B2D52}
.clips.se{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.se i{position:absolute;left:-5px;top:-5px;width:10px;height:10px;border-radius:50% 50% 50% 0;opacity:0;
  background:radial-gradient(circle at 38% 38%,#FFFFFF 0 22%,#B9EEFF 40%,#4FC3F7 100%);animation:seFly 1.05s cubic-bezier(.15,.7,.3,1) var(--d) both}
@keyframes seFly{0%{opacity:0;transform:translate(0,0) rotate(-45deg) scale(.4)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(-45deg) scale(var(--s))}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 90px)) rotate(-45deg) scale(var(--s))}}
@media (prefers-reduced-motion:reduce){.se .sewv,.se .sebu{animation:none}.se .sebb,.clips.se{display:none}}
'''


# ---------- 紅葉の的中ボタン：紅葉がついたPUSH（まさちゃんの指定） ----------
MO_COLORS = (('#E4572E', '#A33A16'), ('#C8341C', '#82200C'), ('#F08A24', '#B85A12'), ('#F2B634', '#B98418'))   # もみじの (面, ふちと柄)


def mo_leaf(x, y, s, rot, k, lid):
    """もみじ1枚（<defs> の葉 lid を使う）。(x, y)：葉のまん中・k：色の番号"""
    f_, s_ = MO_COLORS[k]
    return (f'<use href="#{lid}" transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f}) scale({s})" fill="{f_}" stroke="{s_}" '
            f'stroke-width="{1.3 / s:.2f}" stroke-linejoin="round"/>')


def mo_leaf_on(bx, by, ang, s, k, lid):
    """枝についたもみじ：柄のはしが (bx, by)・葉の先が ang 度の向き（0＝右・90＝下）"""
    r = math.radians(ang + 90)
    ex, ey = .5 * s, 19 * s                       # 柄のはし（葉の形の中で）
    return mo_leaf(bx - (ex * math.cos(r) - ey * math.sin(r)), by - (ex * math.sin(r) + ey * math.cos(r)), s, ang + 90, k, lid)


def momiji_push_svg(lid='moL'):
    """PUSHについた紅葉（ボタン 200×100 の上に重ねる。まわりに出るので -30〜230 × -36〜136）：
       左上に枝ともみじ7枚（赤・朱・橙・山吹）・右下にも枝ともみじ4枚（判定画面のすみのもみじと同じ形・柄で枝につく）・面にもみじ2枚。
       枝ごとに小さくゆれる（.mob1・.mob2）。左上の枝から もみじが3枚、ひらひら落ちる（.mod：葉のまん中を中心に回る）。
       lid：葉の形の id（PUSHと押したあとで別の id にする）"""
    from themes20 import maple_pts, P
    veins = ''.join(f'<path d="M0.5 3 L{.78 * L * math.cos(math.radians(a)):.1f} {.78 * L * math.sin(math.radians(a)):.1f}"/>'
                    for a, L in ((-90, 19.2), (-140, 17.6), (-40, 17.6), (-192, 14.4), (12, 14.4)))
    defs = (f'<defs><g id="{lid}"><path d="M1 3 Q2.5 11 0.5 19" fill="none" stroke-width="2.2" stroke-linecap="round"/><path d="{P(maple_pts(1.05, n=96))}"/>'
            f'<g fill="none" stroke-width=".9" opacity=".55">{veins}</g></g></defs>')
    on = lambda *a: mo_leaf_on(*a, lid)
    br1 = ('<path d="M-30 20 C-14 8 6 -8 32 -18 C42 -22 52 -25 60 -27" fill="none" stroke="#6B3A22" stroke-width="4.2" stroke-linecap="round"/>'
           '<path d="M10 -9 C15 -20 22 -26 28 -32" fill="none" stroke="#6B3A22" stroke-width="2.6" stroke-linecap="round"/>'
           '<path d="M-28 18.5 C-13 7 6 -9 31 -19.4" fill="none" stroke="#9A6040" stroke-width="1.2" stroke-linecap="round" opacity=".8"/>')
    br1 += (on(-24, 16, -115, .8, 2) + on(20, -23, -150, .66, 0) + on(28, -31, -75, .8, 2) + on(58, -26, -18, .75, 0)
            + on(-12, 9, 130, 1.0, 3) + on(42, -22, 80, .72, 3) + on(13, -8, 62, 1.35, 1))      # 最後の1枚（赤・大きい）はボタンの左上の角にかかる
    br2 = '<path d="M232 98 C220 106 206 112 186 120" fill="none" stroke="#6B3A22" stroke-width="3.6" stroke-linecap="round"/>'
    br2 += on(229, 99, -55, .8, 1) + on(222, 103, 40, .7, 0) + on(188, 119, 165, .9, 2) + on(209, 109, -138, 1.25, 3)   # 最後の1枚（山吹・大きい）は右下の角にかかる
    stuck = mo_leaf(176, 22, .42, 25, 1, lid) + mo_leaf(24, 84, .38, -60, 3, lid)      # ボタンの面にのった もみじ
    drops = ''.join(f'<g transform="translate({x} {y})"><g class="mod" style="animation-delay:{-1.2 * j:.1f}s">{mo_leaf(0, 0, .5, a, k, lid)}</g></g>'
                    for j, (x, y, a, k) in enumerate(((12, 2, 20, 0), (30, -12, -40, 3), (-6, 14, 75, 2))))
    return ('<i class="momb" aria-hidden="true"><svg viewBox="-30 -36 262 172" width="262" height="172">'
            f'{defs}{stuck}<g class="mob1">{br1}</g><g class="mob2">{br2}</g>{drops}</svg></i>')


def leaf_burst(n=20, seed=12):
    """押した瞬間に、もみじがパッと舞う（ボタンのまん中から外へ → ひらひら落ちて消える）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 330 + rnd.uniform(-8, 8))
        dist = rnd.uniform(100, 175)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 24
        out += (f'<i class="m{i % 4}" style="--x:{x:.0f}px;--y:{y:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(160, 360):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips mo" aria-hidden="true">{out}</div>'


def mo_leaf_uri(k):
    """もみじの絵（押したときに舞う葉）：data URI の SVG"""
    from themes20 import maple_pts, P
    f_, s_ = MO_COLORS[k]
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-18 -18 36 38'><path d='{P(maple_pts(1.05, n=64))}' fill='{f_}' stroke='{s_}' stroke-width='1.3' stroke-linejoin='round'/>"
           f"<path d='M1 3 Q2.5 11 0.5 19' fill='none' stroke='{s_}' stroke-width='2.2' stroke-linecap='round'/></svg>")
    return 'data:image/svg+xml,' + svg.replace('#', '%23').replace('<', '%3C').replace('>', '%3E')


MO_CSS = r'''
/* ---------- 紅葉の的中ボタン：紅葉がついたPUSH（まさちゃんの指定） ----------
   朱色の面（上は明るい橙 → 下は深い赤）・クリーム色のふち・山吹色のふち・こげ茶の厚み。白い「PUSH」に深い赤の影。
   左上に枝ともみじ7枚・右下にも枝ともみじ4枚（判定画面のすみのもみじと同じ形・赤・朱・橙・山吹・柄で枝につく）・面にもみじ2枚。
   枝が小さくゆれて、左上の枝から もみじがひらひら落ちる。上下の動きは的中と同じ。押すと同じボタンがはじけて、もみじがパッと舞う */
.mo{--pushA:#E4572E;--pushB:#A33A16;--pushC:#FFB27A;--rim:#FFF3DE;--rimD:#E8A13A;
  --pushFace:radial-gradient(72% 40% at 50% 14%,rgba(255,255,255,.85),rgba(255,255,255,.28) 58%,rgba(255,255,255,0) 100%),linear-gradient(180deg,var(--pushC) 0%,var(--pushA) 40%,var(--pushB) 86%,#6E2410 100%)}
.push.mo{box-shadow:inset 0 -9px 0 rgba(90,20,0,.18),inset 0 2px 0 rgba(255,255,255,.6),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #74270C,0 22px 34px rgba(60,20,0,.5)}
.push.mo span{text-shadow:0 3px 0 #7A2410,0 0 14px rgba(255,255,255,.55)}
.push.mo::after{border-color:rgba(255,214,150,.95)}
.mo .momb{position:absolute;left:-30px;top:-36px;width:262px;height:172px;pointer-events:none;z-index:3}
.mo .momb svg{display:block;width:262px;height:172px;overflow:visible}
.mo .mob1,.mo .mob2,.mo .mod{transform-box:view-box;transform-origin:0 0}
.mo .mob1{animation:moSw1 2.8s ease-in-out infinite}
.mo .mob2{animation:moSw2 3.2s ease-in-out infinite}
@keyframes moSw1{0%,100%{transform:translate(-30px,20px) rotate(-3deg) translate(30px,-20px)}50%{transform:translate(-30px,20px) rotate(3deg) translate(30px,-20px)}}
@keyframes moSw2{0%,100%{transform:translate(232px,98px) rotate(3deg) translate(-232px,-98px)}50%{transform:translate(232px,98px) rotate(-3deg) translate(-232px,-98px)}}
.mo .mod{opacity:0;animation:moDrop 3.6s linear infinite}
@keyframes moDrop{0%{opacity:0;transform:translate(0,0) rotate(0)}8%{opacity:1}30%{transform:translate(14px,34px) rotate(-35deg)}55%{transform:translate(-6px,70px) rotate(30deg)}
  80%{opacity:1;transform:translate(12px,104px) rotate(-25deg)}100%{opacity:0;transform:translate(0,128px) rotate(20deg)}}
.tap.mo{color:#FFE7C2}
.pressed.mo{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #74270C}
.clips.mo{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.mo i{position:absolute;opacity:0;animation:moFly 1.25s cubic-bezier(.15,.7,.3,1) var(--d) both;left:-8px;top:-8px;width:16px;height:17px;background:center/contain no-repeat}
.clips.mo .m0{background-image:url("LEAF_0")}
.clips.mo .m1{background-image:url("LEAF_1")}
.clips.mo .m2{background-image:url("LEAF_2")}
.clips.mo .m3{background-image:url("LEAF_3")}
@keyframes moFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.5,.5)}10%{opacity:1}45%{transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1,1)}
  70%{opacity:1;transform:translate(calc(var(--x) * 1.08),calc(var(--y) + 30px)) rotate(calc(var(--r) * 1.3)) scale(.4,1)}100%{opacity:0;transform:translate(calc(var(--x) * 1.12),calc(var(--y) + 64px)) rotate(calc(var(--r) * 1.6)) scale(1,1)}}
@media (prefers-reduced-motion:reduce){.mo .mob1,.mo .mob2{animation:none}.mo .mod,.clips.mo{display:none}}
'''
for _k in range(4):
    MO_CSS = MO_CSS.replace(f'LEAF_{_k}', mo_leaf_uri(_k))


# ---------- 雪の的中ボタン：雪が積もったPUSH（まさちゃんの指定） ----------
YK_EDGE = '#8FB3D6'        # 雪のふちの水色（壁紙の雪・yuki.py と同じ）


def yk_contour(n=150):
    """ボタンのいちばん外のふち（紺のふちの外がわ・角の丸み39）の上半分を n+1 点に：左の横（y=34）→ 左上の角 → 上 → 右上の角 → 右の横（y=34）。
       戻り値 [(u, x, y, 外向きの nx, ny)]（u：0〜1）"""
    segs = [8, math.pi / 2 * 39, 148, math.pi / 2 * 39, 8]
    tot = sum(segs)
    out = []
    for i in range(n + 1):
        s, u = tot * i / n, i / n
        if s <= segs[0]:
            out.append((u, -13, 34 - s, -1, 0))
            continue
        s -= segs[0]
        if s <= segs[1]:
            a = math.pi + s / 39
            out.append((u, 26 + 39 * math.cos(a), 26 + 39 * math.sin(a), math.cos(a), math.sin(a)))
            continue
        s -= segs[1]
        if s <= segs[2]:
            out.append((u, 26 + s, -13, 0, -1))
            continue
        s -= segs[2]
        if s <= segs[3]:
            a = math.pi * 1.5 + s / 39
            out.append((u, 174 + 39 * math.cos(a), 26 + 39 * math.sin(a), math.cos(a), math.sin(a)))
            continue
        s -= segs[3]
        out.append((u, 213, 26 + s, 1, 0))
    return out


YK_DRIPS = ((.3, 9.5, .02), (.52, 7, .022), (.745, 11, .019))     # 前に たれる雪：(場所 u・長さ・はば)
YK_MOUNDS = ((.2, 5.5, .085), (.38, 8, .1), (.6, 5, .09), (.8, 7, .095))   # 上の もり上がり：(場所 u・高さ・はば)


def yk_cap_path():
    """積もった雪の形：上はふわっと3〜4こ もり上がり（ふちから 11〜18px）・前は紺と白のふちをおおって面に少しかかる（たれる所が3つ）。両はしは横で細くなって終わる"""
    sm = lambda a, b, x: (lambda t: t * t * (3 - 2 * t))(min(1, max(0, (x - a) / (b - a))))
    top, bot = [], []
    for u, x, y, nx, ny in yk_contour():
        e = sm(0, .2, u) * sm(0, .2, 1 - u)
        to = e * (9.5 + sum(h * math.exp(-((u - c) / w) ** 2) for c, h, w in YK_MOUNDS) + .7 * math.sin(2 * math.pi * 9.4 * u + .4))
        ti = sm(0, .13, u) * sm(0, .13, 1 - u) * (8.5 + 1.4 * math.sin(2 * math.pi * 3.3 * u + 1.2))
        ti += sum(L * math.exp(-((u - u0) / w) ** 2) for u0, L, w in YK_DRIPS)
        top.append((x + nx * to, y + ny * to))
        bot.append((x - nx * ti, y - ny * ti))
    pts = top + bot[::-1]
    return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'


def yk_drip_tip(k):
    """たれる雪 k の先の場所"""
    u0, L, _ = YK_DRIPS[k]
    c = yk_contour()
    i = min(range(len(c)), key=lambda j: abs(c[j][0] - u0))
    _, x, y, nx, ny = c[i]
    sm = lambda a, b, x: (lambda t: t * t * (3 - 2 * t))(min(1, max(0, (x - a) / (b - a))))
    ti = sm(0, .13, u0) * sm(0, .13, 1 - u0) * (8.5 + 1.4 * math.sin(2 * math.pi * 3.3 * u0 + 1.2)) + L
    return x - nx * ti, y - ny * ti


def yk_crystal(arm, w1=2.2, w2=1.1):
    """雪の結晶（判定画面のすみの結晶と同じ形）：まん中が 0,0。水色の太い線の上に白い細い線"""
    lines = []
    for k in range(6):
        a = math.radians(k * 60 - 90)
        ca, sa = math.cos(a), math.sin(a)
        lines.append((0, 0, arm * ca, arm * sa))
        for r, L in ((.47, .27), (.74, .22)):
            px, py = arm * r * ca, arm * r * sa
            for sg in (-1, 1):
                b = a + sg * math.radians(45)
                lines.append((px, py, px + arm * L * math.cos(b), py + arm * L * math.sin(b)))
    d = ''.join(f'M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}' for x1, y1, x2, y2 in lines)
    return (f'<g fill="none" stroke-linecap="round"><path d="{d}" stroke="{YK_EDGE}" stroke-width="{w1}"/><path d="{d}" stroke="#FFFFFF" stroke-width="{w2}"/>'
            f'<circle r="{arm * .16:.1f}" fill="#FFFFFF" stroke="{YK_EDGE}" stroke-width=".7"/></g>')


def yk_icicle(x, L, w=6.4):
    """つらら（厚みの下のふち y=123 から下へ）"""
    y = 121.5
    return (f'<path d="M{x - w / 2:.1f} {y}L{x + w / 2:.1f} {y}L{x + .7:.1f} {y + L - 1:.1f}Q{x:.1f} {y + L + .8:.1f} {x - .7:.1f} {y + L - 1:.1f}Z" '
            f'fill="url(#{{G}})" stroke="#7FAAD3" stroke-width=".8" stroke-linejoin="round"/>'
            f'<path d="M{x - w / 2 + 1.4:.1f} {y + 1.5}L{x - .5:.1f} {y + L - 3:.1f}" stroke="#FFFFFF" stroke-width="1" stroke-linecap="round" opacity=".85"/>')


def yk_star(x, y, r):
    """きらっと光る小さな星（雪の上）"""
    k = r * .28
    return (f'<path d="M{x:.1f} {y - r:.1f}Q{x + k:.1f} {y - k:.1f} {x + r:.1f} {y:.1f}Q{x + k:.1f} {y + k:.1f} {x:.1f} {y + r:.1f}'
            f'Q{x - k:.1f} {y + k:.1f} {x - r:.1f} {y:.1f}Q{x - k:.1f} {y - k:.1f} {x:.1f} {y - r:.1f}Z" fill="#FFFFFF" stroke="{YK_EDGE}" stroke-width=".6"/>')


def snow_push_svg(sfx=''):
    """PUSHに積もった雪（ボタン 200×100 の上に重ねる。まわりに出るので -34〜234 × -44〜142）：
       上に雪がこんもり積もる（ふわっと もり上がり・紺と白のふちをおおって前に3か所たれる・両はしは横で細く）・下の厚みから つらら6本・面に雪の結晶2つ。
       雪の上で小さな星がきらっ（.ykt）・たれた所から ときどき雪のかたまりが ポロッと落ちる（.ykp）・ボタンの前を雪がふわふわ降る（.ykd：雪つぶ2つ・結晶2つ）。
       sfx：形の id のうしろにつける字（PUSHと押したあとで別の id にする）"""
    P_, G_, I_, C_ = f'ykP{sfx}', f'ykG{sfx}', f'ykI{sfx}', f'ykC{sfx}'
    defs = (f'<defs><path id="{P_}" d="{yk_cap_path()}"/>'
            f'<linearGradient id="{G_}" gradientUnits="userSpaceOnUse" x1="0" y1="-30" x2="0" y2="10"><stop offset="0" stop-color="#FFFFFF"/>'
            '<stop offset=".45" stop-color="#FFFFFF"/><stop offset=".72" stop-color="#EAF2FA"/><stop offset=".92" stop-color="#D3E3F2"/></linearGradient>'
            f'<linearGradient id="{I_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F6FBFF"/><stop offset=".55" stop-color="#CFE8FB"/>'
            f'<stop offset="1" stop-color="#9CC6EA"/></linearGradient><g id="{C_}">{yk_crystal(6)}</g></defs>')
    cap = (f'<use href="#{P_}" fill="{YK_EDGE}" stroke="{YK_EDGE}" stroke-width="2.4" stroke-linejoin="round"/>'
           f'<use href="#{P_}" fill="url(#{G_})"/>')
    cap += ''.join(f'<g transform="translate({x} {y})"><g class="ykt" style="animation-duration:{t}s;animation-delay:{dl}s">{yk_star(0, 0, r)}</g></g>'
                   for x, y, r, t, dl in ((46, -26, 3.6, 2.2, -.4), (118, -27, 3, 2.6, -1.5), (171, -24, 3.3, 2.4, -2.1)))
    ice = ''.join(yk_icicle(x, L) for x, L in ((40, 13), (51, 8), (62, 11), (138, 9), (150, 15), (162, 10))).replace('{G}', I_)
    face = ''.join(f'<use href="#{C_}" transform="translate({x} {y}) rotate({a}) scale({s})"/>' for x, y, a, s in ((176, 74, 12, .9), (24, 76, -8, .75)))
    clumps = ''
    for k, (t, dl) in ((0, (5.8, -1.2)), (2, (7.4, -4.6))):
        x, y = yk_drip_tip(k)
        clumps += (f'<g transform="translate({x:.1f} {y:.1f})"><g class="ykp" style="animation-duration:{t}s;animation-delay:{dl}s">'
                   f'<g fill="#FFFFFF" stroke="{YK_EDGE}" stroke-width=".8"><circle cx="-1.6" cy="3.4" r="3.2"/><circle cx="1.9" cy="3" r="2.7"/><circle cx=".2" cy="5.6" r="2.6"/></g>'
                   '<circle cx="-.4" cy="3.6" r="2.4" fill="#FFFFFF"/></g></g>')
    drops = ''
    for j, (x, y, kind, t) in enumerate(((22, -30, 'd', 4.6), (84, -36, 'c', 5.4), (140, -32, 'd', 4.2), (192, -38, 'c', 5.8))):
        body = (f'<circle r="2.8" fill="#FFFFFF" stroke="{YK_EDGE}" stroke-width=".6"/>' if kind == 'd'
                else f'<use href="#{C_}" transform="scale(.62)"/>')
        drops += (f'<g transform="translate({x} {y})"><g class="ykd" style="animation-duration:{t}s;animation-delay:{-t * j / 4:.2f}s">{body}</g></g>')
    return ('<i class="ykb" aria-hidden="true"><svg viewBox="-34 -44 268 186" width="268" height="186">'
            f'{defs}{ice}{face}{cap}{clumps}{drops}</svg></i>')


def snow_burst(n=24, seed=14):
    """押した瞬間に、雪けむりがボフッと広がる（ボタンのまん中から外へ → ふわっと広がって消える）。6つに1つは結晶"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(80, 160)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 20
        cls = 'c' if i % 6 == 3 else 'p'
        z = rnd.uniform(12, 24) if cls == 'p' else 16
        out += (f'<i class="{cls}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(120, 240):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips yk" aria-hidden="true">{out}</div>'


def yk_crystal_uri():
    """雪の結晶の絵（押したときに舞う結晶）：data URI の SVG"""
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-9 -9 18 18'>{yk_crystal(7.4, 2.4, 1.2)}</svg>".replace('"', "'")
    return 'data:image/svg+xml,' + svg.replace('#', '%23').replace('<', '%3C').replace('>', '%3E')


YK_CSS = r'''
/* ---------- 雪の的中ボタン：雪が積もったPUSH（まさちゃんの指定） ----------
   氷の色の面（上は白っぽい水色 → 下は深い青）・白いふち・紺のふち・こい紺の厚み。白い「PUSH」に紺の影。
   上に雪がこんもり積もる（ふわっと もり上がる・紺と白のふちをおおって前に3か所たれる・両はしは横で細く）・下の厚みから つらら6本・面に雪の結晶2つ（判定画面のすみの結晶と同じ形）。
   雪の上で小さな星がきらっ・たれた所から ときどき雪のかたまりが ポロッと落ちる・ボタンの前を雪がふわふわ降る。上下の動きは的中と同じ。押すと同じボタンがはじけて、雪けむりがボフッと広がる */
.yk{--pushA:#5E9FD6;--pushB:#2F6E9E;--pushC:#DDF0FF;--rim:#F4FAFF;--rimD:#2F6390;
  --pushFace:radial-gradient(72% 40% at 50% 14%,rgba(255,255,255,.9),rgba(255,255,255,.3) 58%,rgba(255,255,255,0) 100%),linear-gradient(180deg,var(--pushC) 0%,var(--pushA) 40%,var(--pushB) 86%,#224E78 100%)}
.push.yk{box-shadow:inset 0 -9px 0 rgba(10,40,80,.18),inset 0 2px 0 rgba(255,255,255,.65),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #1F4468,0 22px 34px rgba(10,25,50,.5)}
.push.yk span{text-shadow:0 3px 0 #1F4F7A,0 0 14px rgba(255,255,255,.6)}
.push.yk::after{border-color:rgba(214,236,255,.95)}
.yk .ykb{position:absolute;left:-34px;top:-44px;width:268px;height:186px;pointer-events:none;z-index:3}
.yk .ykb svg{display:block;width:268px;height:186px;overflow:visible}
.yk .ykt,.yk .ykp,.yk .ykd{transform-box:view-box;transform-origin:0 0}
.yk .ykt{animation:ykTw 2.4s ease-in-out infinite}
@keyframes ykTw{0%,100%{opacity:0;transform:scale(.3)}50%{opacity:1;transform:scale(1)}}
.yk .ykp{opacity:0;animation:ykClump 6s linear infinite}
@keyframes ykClump{0%{opacity:0;transform:translate(0,-3px) rotate(0) scale(.2)}10%{opacity:1;transform:translate(0,0) rotate(0) scale(1)}
  62%{opacity:1;transform:translate(0,0) rotate(0) scale(1);animation-timing-function:cubic-bezier(.5,0,.9,.6)}
  78%{opacity:0;transform:translate(3px,84px) rotate(40deg) scale(.9)}100%{opacity:0;transform:translate(3px,84px) rotate(40deg) scale(.2)}}
.yk .ykd{opacity:0;animation:ykDrop 5s linear infinite}
@keyframes ykDrop{0%{opacity:0;transform:translate(0,0) rotate(0)}10%{opacity:.95}30%{transform:translate(7px,48px) rotate(40deg)}55%{transform:translate(-5px,96px) rotate(90deg)}
  85%{opacity:.95;transform:translate(6px,146px) rotate(150deg)}100%{opacity:0;transform:translate(0,170px) rotate(180deg)}}
.tap.yk{color:#E3F2FF}
.pressed.yk{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #1F4468}
.clips.yk{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.yk i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:ykFly 1.3s cubic-bezier(.15,.7,.3,1) var(--d) both}
.clips.yk .p{border-radius:50%;background:radial-gradient(circle,#FFFFFF 0 38%,rgba(240,247,253,.85) 58%,rgba(225,238,250,0) 72%)}
.clips.yk .c{background:center/contain no-repeat url("CRYSTAL")}
@keyframes ykFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}12%{opacity:1}50%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.15),calc(var(--y) + 40px)) rotate(calc(var(--r) * 1.4)) scale(1.7)}}
@media (prefers-reduced-motion:reduce){.yk .ykt{animation:none;opacity:.9;transform:none}.yk .ykp,.yk .ykd,.clips.yk{display:none}}
'''.replace('CRYSTAL', yk_crystal_uri())


# ---------- お正月の的中ボタン：初日の出が映ったPUSH（まさちゃんの指定） ----------
NY_SUN = (100, 88, 22)          # 面の初日の出：まん中と半径（面は 200×100）


def ny_cloud(x0, y0, w, h, k0=0):
    """金の雲（すやり霞・壁紙の絵の雲と同じ形）：(x0, y0) から はば w・高さ h。下に こい金の影"""
    nb = int(w / 13)
    bumps = ''.join(f'<circle cx="{x0 + k * 13 + 6.5:.1f}" cy="{y0 + 1.5 * math.sin(k + k0):.1f}" r="{h * .62:.1f}"/>' for k in range(nb))
    band = f'<rect x="{x0}" y="{y0}" width="{w}" height="{h * .6:.1f}"/>'
    hi = ''.join(f'<circle cx="{x0 + k * 13 + 5:.1f}" cy="{y0 - h * .25 + 1.5 * math.sin(k + k0):.1f}" r="{h * .22:.1f}"/>' for k in range(nb))   # 雲の上の明るいところ
    return (f'<g fill="#B98322" transform="translate(0 1.2)">{bumps}{band}</g><g fill="#E9B949">{bumps}{band}</g>'
            f'<g fill="#F7D66B" opacity=".55">{hi}</g>')


def ny_star(x, y, r, fill='#FFF3C4'):
    """きらっと光る金の星（4つのとがり）"""
    k = r * .28
    return (f'<path d="M{x:.1f} {y - r:.1f}Q{x + k:.1f} {y - k:.1f} {x + r:.1f} {y:.1f}Q{x + k:.1f} {y + k:.1f} {x:.1f} {y + r:.1f}'
            f'Q{x - k:.1f} {y + k:.1f} {x - r:.1f} {y:.1f}Q{x - k:.1f} {y - k:.1f} {x:.1f} {y - r:.1f}Z" fill="{fill}"/>')


def newyear_face_svg(sfx=''):
    """PUSHの面に映った初日の出（面 200×100 の角の丸み26で切りぬく。文字の下）：
       夜明けの空（上は赤 → 下は だいだい・金）・太陽から出る金の光16本（壁紙と同じく右回りに回る .nyfr）・
       金の初日の出（まわりに光のにじみ）・その前に小さな富士山（雪の頂・壁紙の富士山と同じ形）・前に金の雲（すやり霞）・
       空に金の星がきらっ（.nytw）・上に つやの光・ときどき ななめに光がすっと通る（.nysh）。sfx：id のうしろにつける字"""
    sx, sy, sr = NY_SUN
    K_, S_, U_, R_, G_ = (f'ny{c}{sfx}' for c in 'KSURG')
    sc = sr / 78                   # 壁紙の絵の初日の出（半径78）→ 面の大きさ
    fuji = [(60, 300), (215, 120), (240, 112), (262, 118), (420, 300)]
    cap = [(178, 165), (215, 120), (240, 112), (262, 118), (300, 165), (284, 158), (270, 172), (252, 156), (236, 174), (220, 158), (204, 172), (192, 160)]
    pts = lambda ps: ' '.join(f'{sx + (x - 250) * sc:.1f},{sy + (y - 150) * sc:.1f}' for x, y in ps)
    n, R = 16, 150
    rays = ''.join(f'M0 0L{R * math.cos(math.radians(a - 4.5)):.1f} {R * math.sin(math.radians(a - 4.5)):.1f}'
                   f'L{R * math.cos(math.radians(a + 4.5)):.1f} {R * math.sin(math.radians(a + 4.5)):.1f}Z' for a in range(0, 360, 360 // n))
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="26"/></clipPath>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9E0D14"/><stop offset=".38" stop-color="#C8161D"/>'
            '<stop offset=".66" stop-color="#E2452A"/><stop offset=".84" stop-color="#F39A3A"/><stop offset="1" stop-color="#F8C55A"/></linearGradient>'
            f'<radialGradient id="{U_}" cx=".42" cy=".38" r=".7"><stop offset="0" stop-color="#FFF8D8"/><stop offset=".45" stop-color="#FBE08A"/>'
            '<stop offset="1" stop-color="#F2B33A"/></radialGradient>'
            f'<radialGradient id="{R_}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="{R}"><stop offset="0" stop-color="#FFE9A6" stop-opacity=".55"/>'
            '<stop offset=".35" stop-color="#FFE9A6" stop-opacity=".3"/><stop offset=".7" stop-color="#FFE9A6" stop-opacity=".1"/>'
            '<stop offset="1" stop-color="#FFE9A6" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".5"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    body = (f'<rect width="200" height="100" fill="url(#{S_})"/>'
            f'<g transform="translate({sx} {sy})"><g class="nyfr"><path d="{rays}" fill="url(#{R_})"/></g></g>'
            + ''.join(ny_star(x, y, r) for x, y, r in ((22, 22, 2.2), (176, 30, 1.8), (150, 12, 1.4), (44, 48, 1.3)))
            + ''.join(f'<g transform="translate({x} {y})"><g class="nytw" style="animation-delay:{dl}s">{ny_star(0, 0, r, "#FFF8DC")}</g></g>'
                      for x, y, r, dl in ((34, 30, 3.4, 0), (166, 18, 3, -1.1), (138, 44, 2.6, -2.2)))
            + f'<circle cx="{sx}" cy="{sy}" r="{sr + 12}" fill="#FFE9A6" opacity=".28"/><circle cx="{sx}" cy="{sy}" r="{sr + 5}" fill="#FFE9A6" opacity=".35"/>'
            f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="url(#{U_})"/>'
            f'<polygon points="{pts(fuji)}" fill="#1F3A6B"/><polygon points="{pts(cap)}" fill="#FFFFFF"/>'
            + ny_cloud(6, 88, 72, 9, 0) + ny_cloud(128, 91, 72, 9, 2)
            + '<ellipse cx="100" cy="6" rx="86" ry="20" fill="#FFFFFF" opacity=".22"/>'
            f'<g class="nysh"><rect x="-60" y="-10" width="34" height="130" fill="url(#{G_})" transform="rotate(18)"/></g>'
            '<rect y="91" width="200" height="9" fill="#5A0A0E" opacity=".16"/>')
    return (f'<i class="nyf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def newyear_decor_svg():
    """PUSHのまわりの金の雲（すやり霞）：左下と右上で、ふちにかかる（文字の上・ゆっくり左右にゆれる .nycl）"""
    return ('<i class="nyd" aria-hidden="true"><svg viewBox="-34 -30 268 160" width="268" height="160">'
            f'<g class="nycl">{ny_cloud(-30, 104, 84, 12, 1)}</g><g class="nycl r">{ny_cloud(146, -12, 84, 12, 3)}</g></svg></i>')


def newyear_push_svg(sfx=''):
    return newyear_face_svg(sfx) + newyear_decor_svg()


def gold_burst(n=24, seed=17):
    """押した瞬間に、金の星と金の粉がパッと広がる（ボタンのまん中から外へ → きらきら消える）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 170)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        cls = 's' if i % 3 == 0 else 'g'
        z = rnd.uniform(14, 22) if cls == 's' else rnd.uniform(6, 10)
        out += (f'<i class="{cls}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(90, 200):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips ny" aria-hidden="true">{out}</div>'


NY_STAR_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'%3E%3Cpath d='M0 -10Q2.8 -2.8 10 0Q2.8 2.8 0 10Q-2.8 2.8 -10 0Q-2.8 -2.8 0 -10Z' "
               "fill='%23FFE48A' stroke='%23C8901E' stroke-width='.8'/%3E%3C/svg%3E")

NY_CSS = r'''
/* ---------- お正月の的中ボタン：初日の出が映ったPUSH（まさちゃんの指定） ----------
   面に初日の出：夜明けの空（上は赤 → 下は だいだい・金）・太陽から出る金の光（壁紙と同じく右回りに回る）・金の初日の出・小さな富士山（雪の頂）・金の雲（すやり霞）。
   空に金の星がきらっ・上に つやの光・ときどき ななめに光がすっと通る（映りこみ）。クリーム色のふち・金のふち・こい赤の厚み。白い「PUSH」に こい赤の影。
   左下と右上に金の雲（ふちにかかって ゆっくりゆれる）。上下の動きは的中と同じ。押すと同じボタンがはじけて、金の星と金の粉がパッと広がる */
.ny{--pushA:#E2452A;--pushB:#9E0D14;--pushC:#F8C55A;--rim:#FFF4DC;--rimD:#E9B949;
  --pushFace:linear-gradient(180deg,#9E0D14 0%,#C8161D 38%,#E2452A 66%,#F39A3A 84%,#F8C55A 100%)}
.push.ny{box-shadow:inset 0 2px 0 rgba(255,255,255,.55),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #8A0E12,0 22px 34px rgba(60,0,0,.5)}
.push.ny span{text-shadow:0 3px 0 #8A0E12,0 0 10px rgba(110,8,10,.6)}
.push.ny::after{border-color:rgba(255,226,140,.95)}
.ny .nyf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:26px;overflow:hidden;pointer-events:none}
.ny .nyf svg{display:block;width:200px;height:100px}
.ny .nyd{position:absolute;left:-34px;top:-30px;width:268px;height:160px;pointer-events:none;z-index:3}
.ny .nyd svg{display:block;width:268px;height:160px;overflow:visible}
.ny .nyfr,.ny .nytw,.ny .nysh,.ny .nycl{transform-box:view-box;transform-origin:0 0}
.ny .nyfr{animation:nyFRot 24s linear infinite}
@keyframes nyFRot{to{transform:rotate(360deg)}}
.ny .nytw{animation:nyTw 2.2s ease-in-out infinite}
@keyframes nyTw{0%,100%{opacity:.15;transform:scale(.4)}50%{opacity:1;transform:scale(1)}}
.ny .nysh{animation:nyShine 4.2s ease-in-out infinite}
@keyframes nyShine{0%,55%{transform:translateX(0)}85%,100%{transform:translateX(300px)}}
.ny .nycl{animation:nyCloud 5s ease-in-out infinite alternate}.ny .nycl.r{animation-delay:-2.5s}
@keyframes nyCloud{from{transform:translateX(-4px)}to{transform:translateX(4px)}}
.tap.ny{color:#FFE9A6}
.pressed.ny{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #8A0E12}
.clips.ny{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.ny i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:nyFly 1.2s cubic-bezier(.15,.7,.3,1) var(--d) both}
.clips.ny .s{background:center/contain no-repeat url("STAR")}
.clips.ny .g{border-radius:50%;background:radial-gradient(circle at 38% 38%,#FFF6CF 0 25%,#F2C14E 60%,#C8901E 100%)}
@keyframes nyFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.12),calc(var(--y) + 46px)) rotate(calc(var(--r) * 1.5)) scale(.5)}}
@media (prefers-reduced-motion:reduce){.ny .nyfr,.ny .nytw,.ny .nysh,.ny .nycl{animation:none}.ny .nysh,.clips.ny{display:none}}
'''.replace('STAR', NY_STAR_URI)


# ---------- 競馬新聞の的中ボタン：新聞でできたPUSH（まさちゃんの指定） ----------
NP_INK, NP_RED, NP_GREY, NP_PAPER = '#141414', '#C81E1E', '#8C877D', '#F2EEE3'


def np_bars(x0, x1, ys, seed, h=2.2):
    """記事の行（灰色の棒）：x0〜x1 の はばで、行ごとに少し長さを変える。さいごの行は短い"""
    rnd = random.Random(seed)
    out = ''
    for i, y in enumerate(ys):
        w = (x1 - x0) * (rnd.uniform(.55, .75) if i == len(ys) - 1 else rnd.uniform(.88, 1))
        out += f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{h}" fill="{NP_GREY}"/>'
    return out


def news_face_svg(sfx=''):
    """PUSHの面＝新聞の紙面（面 200×100・角の丸み6で切りぬく。文字の下）：
       新聞紙の色（上は明るく下は少し黄ばむ）に網点・まん中に たたんだ折り目。
       上に題字「テンゲル競馬」（黒い帯に紙の色の字）・赤い◎（本命）と記事の行・右上に赤い「号外」（どきどき大きくなる .npg）・太い線。
       下に二重線と3段の記事の行（段のあいだに細い線）。まん中の見出しが「PUSH」（黒い字に赤いずれの影・CSS）。sfx：id のうしろにつける字"""
    K_, S_, D_ = (f'np{c}{sfx}' for c in 'KSD')
    font = "font-family=\"'Kaisei Tokumin',serif\" font-weight=\"800\" font-style=\"normal\""      # <i> の中なので、ななめにならないように
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="6"/></clipPath>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F8F5EC"/><stop offset="1" stop-color="#E8E0CE"/></linearGradient>'
            f'<pattern id="{D_}" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".6" fill="{NP_INK}" opacity=".07"/></pattern></defs>')
    body = (f'<rect width="200" height="100" fill="url(#{S_})"/><rect width="200" height="100" fill="url(#{D_})"/>'
            f'<rect x="8" y="6" width="70" height="15" fill="{NP_INK}"/>'
            f'<text x="43" y="16.9" font-size="9.6" fill="{NP_PAPER}" text-anchor="middle" letter-spacing=".5" {font}>テンゲル競馬</text>'
            f'<circle cx="88.5" cy="13.5" r="5.8" fill="none" stroke="{NP_RED}" stroke-width="1.8"/><circle cx="88.5" cy="13.5" r="2.4" fill="none" stroke="{NP_RED}" stroke-width="1.5"/>'
            + np_bars(98, 150, (8.5, 12.6, 16.7), 3, 2.1)
            + f'<g transform="translate(175 13.5)"><g class="npg"><rect x="-17" y="-8.5" width="34" height="17" fill="{NP_RED}"/>'
            f'<text y="4.4" font-size="12" fill="#FFFFFF" text-anchor="middle" {font}>号外</text></g></g>'
            f'<rect x="8" y="24.5" width="184" height="1.8" fill="{NP_INK}"/>'
            f'<rect x="8" y="73.2" width="184" height="1.3" fill="{NP_INK}"/><rect x="8" y="75.8" width="184" height=".6" fill="{NP_INK}"/>'
            + np_bars(8, 62, (80, 84.4, 88.8, 93.2), 5) + np_bars(70, 128, (80, 84.4, 88.8, 93.2), 6) + np_bars(136, 192, (80, 84.4, 88.8, 93.2), 7)
            + f'<rect x="65.6" y="79" width=".7" height="17" fill="{NP_INK}" opacity=".6"/><rect x="131.6" y="79" width=".7" height="17" fill="{NP_INK}" opacity=".6"/>'
            '<rect x="99" width="2" height="100" fill="#000000" opacity=".07"/><rect x="101" width=".9" height="100" fill="#FFFFFF" opacity=".55"/>'
            '<rect width="200" height="100" fill="none" stroke="#000000" stroke-opacity=".06" stroke-width="3"/>')
    return (f'<i class="npf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def news_stack_svg(sfx=''):
    """PUSHの厚み＝かさねた新聞の束（紙のふちの線。厚みの見える所だけ）"""
    C_ = f'npC{sfx}'
    lines = ''.join(f'<rect x="-14" y="{y}" width="228" height=".9" fill="{c}"/>'
                    for y, c in ((114.2, '#F7F3EA'), (115.6, '#A39A86'), (117.2, '#F7F3EA'), (118.6, '#A39A86'), (120.2, '#F7F3EA'), (121.6, '#A39A86')))
    return ('<i class="npt" aria-hidden="true"><svg viewBox="-20 -20 240 150" width="240" height="150">'
            f'<defs><clipPath id="{C_}"><rect x="-13" y="-3" width="226" height="126" rx="19"/></clipPath></defs>'     # 厚みの形（ふちの下に見える所だけに線がある）
            f'<g clip-path="url(#{C_})">{lines}</g></svg></i>')


def news_push_svg(sfx=''):
    return news_face_svg(sfx) + news_stack_svg(sfx)


def paper_burst(n=18, seed=19):
    """押した瞬間に、新聞の切れはしがパッと舞う（ボタンのまん中から外へ → くるくる裏返りながら落ちて消える）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 170)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 24
        out += (f'<i class="q{i % 3}" style="--x:{x:.0f}px;--y:{y:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(120, 300):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips np" aria-hidden="true">{out}</div>'


def np_scrap_uri(k):
    """新聞の切れはし（押したときに舞う）：0＝記事の行・1＝赤い◎・2＝黒い見出しの帯"""
    inner = {0: "<rect x='3' y='4' width='18' height='1.6' fill='%238C877D'/><rect x='3' y='7.5' width='16' height='1.6' fill='%238C877D'/><rect x='3' y='11' width='17' height='1.6' fill='%238C877D'/>",
             1: "<circle cx='9' cy='9' r='5' fill='none' stroke='%23C81E1E' stroke-width='1.6'/><circle cx='9' cy='9' r='2' fill='none' stroke='%23C81E1E' stroke-width='1.3'/>",
             2: "<rect x='3' y='3' width='18' height='4.5' fill='%23141414'/><rect x='3' y='9.5' width='15' height='1.4' fill='%238C877D'/>"}[k]
    w, h = (24, 15) if k != 1 else (18, 18)
    return (f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}'%3E%3Crect width='{w}' height='{h}' fill='%23F4F0E6' stroke='%23B5AC98' stroke-width='.6'/%3E"
            + inner.replace('<', '%3C').replace('>', '%3E') + "%3C/svg%3E")


NP_CSS = r'''
/* ---------- 競馬新聞の的中ボタン：新聞でできたPUSH（まさちゃんの指定） ----------
   面＝新聞の紙面（新聞紙の色に網点・たたんだ折り目・上に題字「テンゲル競馬」と赤い◎と記事・右上に赤い「号外」・下に3段の記事）。
   見出しの「PUSH」は黒い字に赤いずれの影。角は少しだけ丸い（新聞の四角）。紙の白いふち・黒い太いふち・厚みは かさねた新聞の束（紙のふちの線）。
   「号外」が どきどき大きくなる。上下の動きは的中と同じ。押すと同じボタンがはじけて（紙なので白く光らせない）、新聞の切れはしがパッと舞う */
.np{--pr:6px;--pushA:#F2EEE3;--pushB:#141414;--pushC:#F8F5EC;--rim:#FBF9F3;--rimD:#141414;
  --pushFace:linear-gradient(180deg,#F8F5EC,#E8E0CE)}
.push.np{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #CFC6B3,0 22px 34px rgba(0,0,0,.45)}
.push.np span{color:#141414;text-shadow:3px 3px 0 #C81E1E}
.push.np::after{border-color:rgba(200,30,30,.9)}
.np .npf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:6px;overflow:hidden;pointer-events:none;font-style:normal}
.np .npf svg{display:block;width:200px;height:100px}
.np .npt{position:absolute;left:-20px;top:-20px;width:240px;height:150px;pointer-events:none;z-index:3}
.np .npt svg{display:block;width:240px;height:150px;overflow:visible}
.np .npg{transform-box:view-box;transform-origin:0 0;animation:npPulse 1.6s ease-in-out infinite}
@keyframes npPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
.tap.np{color:#F2EEE3}
.pressed.np{border-radius:6px;box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #CFC6B3;animation-name:npPress}
@keyframes npPress{0%{transform:scale(1)}35%{transform:scale(.84)}100%{transform:scale(1.7);opacity:0}}   /* 紙の白は光らせない（ボードが出るところと重なって、ちかちかしないように） */
.clips.np{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.np i{position:absolute;opacity:0;left:-12px;top:-8px;width:24px;height:15px;background:center/contain no-repeat;box-shadow:0 1px 2px rgba(0,0,0,.25);
  animation:npFly 1.3s cubic-bezier(.15,.7,.3,1) var(--d) both}
.clips.np .q0{background-image:url("SCRAP_0")}
.clips.np .q1{width:18px;height:18px;left:-9px;top:-9px;background-image:url("SCRAP_1")}
.clips.np .q2{background-image:url("SCRAP_2")}
@keyframes npFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.4,.4)}10%{opacity:1}45%{transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1,1)}
  70%{opacity:1;transform:translate(calc(var(--x) * 1.08),calc(var(--y) + 34px)) rotate(calc(var(--r) * 1.3)) scale(-.6,1)}100%{opacity:0;transform:translate(calc(var(--x) * 1.12),calc(var(--y) + 70px)) rotate(calc(var(--r) * 1.6)) scale(1,1)}}
@media (prefers-reduced-motion:reduce){.np .npg{animation:none}.clips.np{display:none}}
'''
for _k in range(3):
    NP_CSS = NP_CSS.replace(f'SCRAP_{_k}', np_scrap_uri(_k))


# ---------- 水墨画の的中ボタン：墨画でできたPUSH（まさちゃんの指定） ----------
NK_INK, NK_PAPER, NK_RED = '#1C1A18', '#F5F0E4', '#B7282E'


def nk_stroke(seed=8):
    """太い筆の一画（左から右へ・面のまん中）：左は丸く入り、右へ行くほど少し細く、さいごは穂先が割れる。戻り値 (塗りの path, かすれの白い線)"""
    rnd = random.Random(seed)
    top, bot = [], []
    for i in range(45):
        x = 16 + i * 3.8
        t = (x - 16) / 168
        th = 21.5 - 4.5 * t
        cy = 50 + 1.5 * math.sin(t * 3.1 + .4)
        top.append((x, cy - th + 1.0 * math.sin(x / 9 + 1) + rnd.uniform(-.45, .45)))
        bot.append((x, cy + th + .9 * math.sin(x / 7.3 + 2) + rnd.uniform(-.45, .45)))
    x_end = top[-1][0]
    tips = []                                                           # 穂先：上から下へ、長いのと短いのが交互
    y_a, y_b = top[-1][1], bot[-1][1]
    for j in range(9):
        y = y_a + (y_b - y_a) * (j + .5) / 9
        tips += [(x_end + (rnd.uniform(7, 13) if j % 2 == 0 else rnd.uniform(1, 4)), y)]
    cy0 = (top[0][1] + bot[0][1]) / 2
    r0 = (bot[0][1] - top[0][1]) / 2
    cap = [(16 - r0 * .55 * math.sin(a), cy0 - r0 * math.cos(a)) for a in [k * math.pi / 10 for k in range(1, 10)]]   # 左の入り（丸い）
    pts = top + tips + bot[::-1] + cap[::-1]
    d = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
    kas = ''
    for j in range(11):                                                 # かすれ：右へ行くほど多い白い筋
        y = (top[-1][1] + 3) + (bot[-1][1] - top[-1][1] - 6) * (j + .5) / 11 + rnd.uniform(-1.2, 1.2)
        x0 = rnd.uniform(118, 160)
        kas += (f'<path d="M{x0:.1f} {y:.1f}Q{(x0 + 196) / 2:.1f} {y + rnd.uniform(-1.5, 1.5):.1f} 196 {y + rnd.uniform(-2, 2):.1f}" '
                f'stroke="{NK_PAPER}" stroke-width="{rnd.uniform(.7, 1.7):.2f}" stroke-linecap="round" opacity="{rnd.uniform(.55, .9):.2f}"/>')
    return d, kas


def nk_ridge(y0, amp, f, ph, fill_op):
    """遠くの山（にじむ墨）：面のいちばん下"""
    pts = [(x, y0 - amp * abs(math.sin(x / f + ph)) - 2.2 * math.sin(x / 6.5 + ph)) for x in range(-4, 206, 3)]
    return (f'<path d="M-4 104L' + 'L'.join(f'{x} {y:.1f}' for x, y in pts) + f'L206 104Z" fill="{NK_INK}" opacity="{fill_op}"/>')


def ink_face_svg(sfx=''):
    """PUSHの面＝墨画（面 200×100・角の丸み8で切りぬく。文字の下）：
       和紙（白っぽい生成り・細い繊維）・下に にじむ墨の遠い山2つ（霧がゆっくり横切る .nkm）・まん中に太い筆の一画（かすれ・にじみ）＝「PUSH」はその上に紙の色で抜く。
       右下に朱の落款「馬」・ところどころ墨のしぶき。紙の上で墨のしずくが ぽたっ → じわっと にじんで消える（.nkb）。sfx：id のうしろにつける字"""
    K_, P_, B_, F_, M_ = (f'nk{c}{sfx}' for c in 'KPBFM')
    rnd = random.Random(21)
    d, kas = nk_stroke()
    fibers = ''.join(f'<path d="M{x:.1f} {y:.1f}q{rnd.uniform(-6, 6):.1f} {rnd.uniform(-2, 2):.1f} {rnd.uniform(-10, 10):.1f} {rnd.uniform(-3, 3):.1f}" '
                     f'fill="none" stroke="#7A6A50" stroke-width=".5" opacity="{rnd.uniform(.12, .25):.2f}"/>'
                     for x, y in [(rnd.uniform(4, 196), rnd.uniform(4, 96)) for _ in range(16)])
    dots = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{NK_INK}" opacity=".85"/>'
                   for x, y, r in ((30, 18, 1.4), (34, 14, .8), (168, 84, 1.1), (60, 82, .9), (188, 20, 1.6), (182, 26, .8), (120, 86, .7)))
    blots = ''.join(f'<g transform="translate({x} {y})"><g class="nkb" style="animation-delay:{dl}s"><circle r="10" fill="url(#{B_})"/></g></g>'
                    for x, y, dl in ((18, 14, 0), (176, 13, -1.4), (100, 91, -2.8)))
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="8"/></clipPath>'
            f'<linearGradient id="{P_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBF8F1"/><stop offset="1" stop-color="#EEE6D4"/></linearGradient>'
            f'<radialGradient id="{B_}"><stop offset="0" stop-color="{NK_INK}" stop-opacity=".55"/><stop offset=".45" stop-color="{NK_INK}" stop-opacity=".22"/>'
            f'<stop offset="1" stop-color="{NK_INK}" stop-opacity="0"/></radialGradient>'
            f'<filter id="{F_}" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="1.6"/></filter>'
            f'<filter id="{M_}" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="3"/></filter></defs>')
    body = (f'<rect width="200" height="100" fill="url(#{P_})"/>{fibers}'
            f'<g filter="url(#{F_})">{nk_ridge(88, 9, 19, .6, .13)}{nk_ridge(95, 6, 12, 2.0, .2)}</g>'
            f'<g class="nkm"><ellipse cx="-30" cy="90" rx="34" ry="5" fill="#FFFFFF" opacity=".55" filter="url(#{M_})"/></g>'
            f'{blots}'
            f'<path d="{d}" fill="{NK_INK}" opacity=".22" filter="url(#{F_})"/><path d="{d}" fill="{NK_INK}"/>{kas}{dots}'
            f'<rect x="174" y="74" width="16" height="16" fill="{NK_RED}" opacity=".92"/>'
            f'<text x="182" y="86.2" font-size="12" fill="{NK_PAPER}" text-anchor="middle" font-family="\'Zen Old Mincho\',serif" font-weight="700" font-style="normal">馬</text>')
    return (f'<i class="nkf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def ink_decor_svg():
    """PUSHのまわり：左上に筆の円（円相）と小さな朱の印・まわりに墨のしぶき（文字の上・動かない）"""
    rnd = random.Random(33)
    a0, a1 = math.radians(200), math.radians(200 + 320)
    arc = lambda r, w, op: (f'<path d="M{-16 + r * math.cos(a0):.1f} {-12 + r * math.sin(a0):.1f}A{r} {r} 0 1 1 {-16 + r * math.cos(a1):.1f} {-12 + r * math.sin(a1):.1f}" '
                            f'fill="none" stroke="{NK_INK}" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>')
    enso = arc(14, 4.2, .9) + arc(15.5, 1.2, .5) + arc(12.6, .9, .45) + f'<rect x="-6" y="-2" width="6" height="6" fill="{NK_RED}"/>'
    spl = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(.8, 2.2):.1f}" fill="{NK_INK}" opacity=".85"/>'
                  for x, y in ((214, 4), (219, 10), (222, -2), (-20, 104), (-24, 98), (-14, 112), (206, 118), (212, 112), (100, -20), (108, -24)))
    return f'<i class="nkd" aria-hidden="true"><svg viewBox="-34 -30 268 160" width="268" height="160">{enso}{spl}</svg></i>'


def ink_push_svg(sfx=''):
    return ink_face_svg(sfx) + ink_decor_svg()


def ink_burst(n=20, seed=23):
    """押した瞬間に、墨がパッと飛び散る（ボタンのまん中から外へ → しずくが落ちて消える）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 330 + rnd.uniform(-8, 8))
        dist = rnd.uniform(80, 160)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 20
        z = rnd.uniform(6, 15)
        out += f'<i style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--d:{rnd.uniform(0, .08):.2f}s"></i>'
    return f'<div class="clips nk" aria-hidden="true">{out}</div>'


NK_CSS = r'''
/* ---------- 水墨画の的中ボタン：墨画でできたPUSH（まさちゃんの指定） ----------
   面＝墨画（和紙の生成り・細い繊維・下に にじむ墨の遠い山・まん中に太い筆の一画（入りは丸く、右はかすれて穂先が割れる・まわりに少しにじみ）・右下に朱の落款「馬」・墨のしぶき）。
   「PUSH」は筆の一画の上に紙の色で抜く。和紙のふち・墨の黒いふち・こい墨の厚み。左上に筆の円（円相）と朱の印。
   紙の上で墨のしずくが じわっと にじんで消える・山の前を霧がゆっくり横切る。上下の動きは的中と同じ。押すとボタンがはじけて（紙なので白く光らせない）、墨がパッと飛び散る */
.nk{--pr:8px;--pushA:#F5F0E4;--pushB:#1C1A18;--pushC:#FBF8F1;--rim:#F5F0E4;--rimD:#1C1A18;
  --pushFace:linear-gradient(180deg,#FBF8F1,#EEE6D4)}
.push.nk{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #3A3530,0 22px 34px rgba(0,0,0,.45)}
.push.nk span{color:#F5F0E4;text-shadow:0 0 1px rgba(245,240,228,.5)}
.push.nk::after{border-color:rgba(245,240,228,.85)}
.nk .nkf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:8px;overflow:hidden;pointer-events:none;font-style:normal}
.nk .nkf svg{display:block;width:200px;height:100px}
.nk .nkd{position:absolute;left:-34px;top:-30px;width:268px;height:160px;pointer-events:none;z-index:3}
.nk .nkd svg{display:block;width:268px;height:160px;overflow:visible}
.nk .nkb,.nk .nkm{transform-box:view-box;transform-origin:0 0}
.nk .nkb{opacity:0;animation:nkBlot 4.2s ease-out infinite}
@keyframes nkBlot{0%{opacity:0;transform:scale(.15)}12%{opacity:.95;transform:scale(.4)}70%{opacity:.6;transform:scale(1.15)}100%{opacity:0;transform:scale(1.35)}}
.nk .nkm{animation:nkMist 7s linear infinite}
@keyframes nkMist{from{transform:translateX(0)}to{transform:translateX(270px)}}
.tap.nk{color:#F5F0E4}
.pressed.nk{border-radius:8px;box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #3A3530;animation-name:nkPress}
@keyframes nkPress{0%{transform:scale(1)}35%{transform:scale(.84)}100%{transform:scale(1.7);opacity:0}}   /* 紙の白は光らせない */
.clips.nk{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.nk i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);border-radius:50% 50% 50% 45%;
  background:radial-gradient(circle at 40% 38%,#4A4642 0 18%,#1C1A18 55%,rgba(28,26,24,.85) 100%);animation:nkFly 1.15s cubic-bezier(.15,.7,.3,1) var(--d) both}
@keyframes nkFly{0%{opacity:0;transform:translate(0,0) scale(.4)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.08),calc(var(--y) + 80px)) scale(.7,1.3)}}
@media (prefers-reduced-motion:reduce){.nk .nkb,.nk .nkm{animation:none}.nk .nkb{opacity:0}.clips.nk{display:none}}
'''


# ---------- メリーゴーランドの的中ボタン：メリーゴーランドのPUSH（まさちゃんの指定） ----------
MG_LINE, MG_GOLD, MG_GOLD_D, MG_PINK = '#4A2A4E', '#E9C46A', '#C9952B', '#F49AC1'


def mg_horse(saddle, mane, ow=1.5):
    """小さな木馬（右向き・前足を上げた形・白い体・まわりに太い線・鞍とたてがみの色・金のひづめ）：
       0,0 は鞍の上（柱が通る所）。線は「線の色で太く描いてから白をのせる」ので、体と首のつなぎ目に線が出ない。
       柱が鞍と おなかを通る所に金の輪（木馬と一緒に上下する）"""
    body = 'M-12 -1C-12 -5 -4 -4 2 -3.5C7 -3 11 -1 11.5 3C12 7 6 8.5 0 8C-6 8 -13 7.5 -13.5 3C-14 1 -13 -.5 -12 -1Z'
    neck = ('M4 -3C6 -9 10 -14 14 -15.5C17.5 -16.5 21.5 -13 23.8 -9C24.6 -7.4 23.2 -5.8 21.5 -6.4'
            'C20 -7 18.6 -8.4 17.8 -9.8C15.5 -6.5 13.5 -2 11.5 3Z')                                   # 首と頭
    ear = 'M14.6 -15.2L15.2 -19.6L17.2 -15.6Z'
    legs = 'M-10.5 4.5L-14 9.5L-14.8 14.2M-6 6L-7 11L-5.6 15M9.5 3.5L14.6 5.6L14.2 9.6M6 5.5L9.6 9.6L7.8 13.4'   # うしろ足・前足（上げる）
    tail = 'M-12.5 -.5C-17 0 -19.5 4 -18.5 10C-17 8.5 -15.5 6 -13 3.5Z'
    mane_p = ('M4.2 -3.6C6.2 -9.2 9.8 -13.8 14 -15.6C13.2 -13.6 12.6 -12.6 13 -11C11.2 -10.6 11 -8.8 9.6 -8.2'
              'C8.8 -6.6 8.4 -5 7 -3.6Z')
    sad = 'M-6 -3.4C-3 -5 3 -4.8 5 -3L4.4 1.6Q0 4.4 -5.3 1.6Z'
    L = f'stroke="{MG_LINE}" stroke-linejoin="round" stroke-linecap="round"'
    return (f'<g fill="{MG_LINE}" {L} stroke-width="{2 * ow}"><path d="{body}"/><path d="{neck}"/><path d="{ear}"/><path d="{tail}"/></g>'   # 線（太く）
            f'<path d="{legs}" fill="none" {L} stroke-width="{3.2 + 2 * ow}"/>'
            f'<path d="{legs}" fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{tail}" fill="{mane}"/><path d="{body}" fill="#FFFFFF"/><path d="{neck}" fill="#FFFFFF"/><path d="{ear}" fill="#FFFFFF"/>'
            f'<path d="{mane_p}" fill="{mane}" {L} stroke-width=".9"/>'                                                          # たてがみ
            f'<path d="{sad}" fill="{saddle}" {L} stroke-width=".9"/>'                                                           # 鞍
            f'<path d="M-4 -4.4C-1 -6.2 2 -6.2 4 -4.2" fill="none" stroke="{MG_GOLD}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<path d="M21.6 -7.6L16.6 -13.4" fill="none" stroke="{saddle}" stroke-width="1.1" stroke-linecap="round"/>'           # くつわ
            f'<circle cx="19.3" cy="-11.6" r=".95" fill="{MG_LINE}"/><circle cx="21.2" cy="-8.8" r="1.3" fill="{MG_PINK}" opacity=".7"/>'   # 目・ほっぺ
            + ''.join(f'<circle cx="{x}" cy="{y}" r="1.7" fill="{MG_GOLD}" {L} stroke-width=".7"/>' for x, y in ((-14.8, 14.2), (-5.6, 15), (14.2, 9.6), (7.8, 13.4)))   # ひづめ
            + f'<rect x="-2.6" y="-6.6" width="5.2" height="2.6" rx="1" fill="{MG_GOLD}" stroke="{MG_LINE}" stroke-width=".7"/>'
            f'<rect x="-2.6" y="6.6" width="5.2" height="2.6" rx="1" fill="{MG_GOLD}" stroke="{MG_LINE}" stroke-width=".7"/>')   # 柱の金の輪


def mg_bulb(x, y, grp):
    """まわりの電球：消えた金の玉の上に、明るい玉と光（.mgl：a と b が交互に光る）"""
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="{MG_GOLD_D}" stroke="{MG_LINE}" stroke-width=".8"/>'
            f'<g class="mgl {grp}"><circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="#FFE9A0" opacity=".55"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="#FFF8DC" stroke="{MG_LINE}" stroke-width=".8"/></g>')


def carousel_face_svg(sfx=''):
    """PUSHの面（面 200×100・角の丸み22で切りぬく。文字の下）：
       ピンクから深いピンクのグラデーション・上に つやの光・ぼけた光の玉。下は金の床（メリーゴーランドの台）で、
       金の柱（上から床まで・文字のうしろ）の小さな木馬6頭が左から右へ回り（6秒で2頭ぶん・.mgx）、柱にそって上下する（2秒・となりどうしは反対・.mgy）。
       「PUSH」の文字は少し上（下を木馬が通る）。sfx：id のうしろにつける字"""
    K_, S_, G_, B_, H_ = (f'mg{c}{sfx}' for c in 'KSGBH')
    rnd = random.Random(41)
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="22"/></clipPath>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F9A6CC"/><stop offset=".45" stop-color="#E067A1"/>'
            '<stop offset=".8" stop-color="#C2437F"/><stop offset="1" stop-color="#A3326B"/></linearGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF1C2"/><stop offset=".45" stop-color="{MG_GOLD}"/>'
            f'<stop offset="1" stop-color="{MG_GOLD_D}"/></linearGradient>'
            f'<linearGradient id="{H_}"><stop offset="0" stop-color="{MG_GOLD_D}"/><stop offset=".45" stop-color="#FFF1C2"/><stop offset="1" stop-color="{MG_GOLD_D}"/></linearGradient>'
            f'<radialGradient id="{B_}"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient></defs>')
    bokeh = ''.join(f'<circle cx="{rnd.uniform(6, 194):.1f}" cy="{rnd.uniform(6, 70):.1f}" r="{rnd.uniform(5, 11):.1f}" fill="url(#{B_})" opacity="{rnd.uniform(.4, .8):.2f}"/>'
                    for _ in range(9))
    horses = ''
    for i, x in enumerate((-240, -150, -60, 30, 120, 210)):          # となりどうしは色と上下が反対（2頭ぶん流れて元にもどる）
        sad, mane = (MG_PINK, '#F7B6D2') if i % 2 == 0 else ('#7FD1C7', '#F7DE8A')
        horses += (f'<g transform="translate({x} 0)"><rect x="-1.5" y="-2" width="3" height="94" fill="url(#{H_})" stroke="{MG_LINE}" stroke-width=".7"/>'   # 金の柱（屋根から床まで・文字のうしろ）
                   f'<g transform="translate(0 75) scale(.8)"><g class="mgy" style="animation-delay:{-1.0 * (i % 2):.1f}s">{mg_horse(sad, mane)}</g></g></g>')
    body = (f'<rect width="200" height="100" fill="url(#{S_})"/>{bokeh}'
            '<ellipse cx="100" cy="6" rx="90" ry="20" fill="#FFFFFF" opacity=".22"/>'
            f'<g class="mgx">{horses}</g>'
            f'<rect y="90" width="200" height="10" fill="url(#{G_})"/><rect y="90" width="200" height="1.6" fill="{MG_LINE}" opacity=".55"/>'
            + ''.join(f'<circle cx="{x}" cy="95.2" r="1.5" fill="#FFF8DC"/>' for x in range(10, 200, 20)))
    return (f'<i class="mgf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def carousel_decor_svg(sfx=''):
    """PUSHのまわり：上に しま模様の屋根（ピンクと白・下は丸い波・金のふち・てっぺんに金の玉と旗）・
       両がわと下に 電球（a と b が交互に光る）。文字の上"""
    P_ = f'mgP{sfx}'
    n = 14
    xs = [-22 + 244 * k / n for k in range(n + 1)]
    apex = (100, -46)
    stripes = ''.join(f'<path d="M{apex[0]} {apex[1]}L{xs[k]:.1f} -12L{xs[k + 1]:.1f} -12Z" fill="{MG_PINK if k % 2 == 0 else "#FFFFFF"}"/>' for k in range(n))
    scal = ''.join(f'<path d="M{xs[k]:.1f} -12A{(xs[k + 1] - xs[k]) / 2:.1f} 6 0 0 0 {xs[k + 1]:.1f} -12Z" fill="{MG_PINK if k % 2 == 0 else "#FFFFFF"}" stroke="{MG_LINE}" stroke-width="1.4" stroke-linejoin="round"/>'
                   for k in range(n))
    roof = (f'<path d="M{apex[0]} {apex[1]}L222 -12L-22 -12Z" fill="#FFFFFF"/>{stripes}'
            f'<path d="M{apex[0]} {apex[1]}L222 -12L-22 -12Z" fill="none" stroke="{MG_LINE}" stroke-width="2" stroke-linejoin="round"/>{scal}'
            f'<rect x="-24" y="-14.5" width="248" height="4" rx="2" fill="{MG_GOLD}" stroke="{MG_LINE}" stroke-width="1.2"/>'
            + ''.join(f'<circle cx="{(xs[k] + xs[k + 1]) / 2:.1f}" cy="-6" r="1.8" fill="#FFF8DC" stroke="{MG_LINE}" stroke-width=".6"/>' for k in range(n))
            + f'<path d="M100 -46V-60" stroke="{MG_LINE}" stroke-width="1.6"/><path d="M100 -60L113 -56L100 -52Z" fill="{MG_PINK}" stroke="{MG_LINE}" stroke-width="1.2" stroke-linejoin="round"/>'
            f'<circle cx="100" cy="-46" r="3.4" fill="{MG_GOLD}" stroke="{MG_LINE}" stroke-width="1.2"/>')
    bulbs = ''
    k = 0
    for y in (14, 32, 50, 68, 86):
        for x in (-10.5, 210.5):
            bulbs += mg_bulb(x, y, 'a' if k % 2 == 0 else 'b'); k += 1
    for x in (22, 44, 66, 88, 112, 134, 156, 178):
        bulbs += mg_bulb(x, 110.5, 'a' if k % 2 == 0 else 'b'); k += 1
    return (f'<i class="mgd" aria-hidden="true"><svg viewBox="-34 -66 268 196" width="268" height="196">'
            f'<g class="mgr">{roof}</g>{bulbs}</svg></i>')


def carousel_push_svg(sfx=''):
    return carousel_face_svg(sfx) + carousel_decor_svg(sfx)


def carousel_burst(n=24, seed=29):
    """押した瞬間に、金の星・ピンクのハート・白いきらきらがパッと広がる"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 170)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        cls = 'st' if i % 3 == 0 else 'ht' if i % 3 == 1 else 'dt'
        z = rnd.uniform(14, 20) if cls != 'dt' else rnd.uniform(6, 9)
        out += (f'<i class="{cls}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(90, 220):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips mg" aria-hidden="true">{out}</div>'


MG_STAR_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'%3E%3Cpath d='M0 -9L2.6 -3.2 8.6 -2.8 4 1.2 5.4 7.2 0 4 -5.4 7.2 -4 1.2 -8.6 -2.8 -2.6 -3.2Z' "
               "fill='%23F7DE8A' stroke='%23C9952B' stroke-width='1' stroke-linejoin='round'/%3E%3C/svg%3E")
MG_HEART_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'%3E%3Cpath d='M0 7C-6 2 -9 -1 -9 -4.5 -9 -7.5 -6.5 -9 -4.5 -9 -2.5 -9 -1 -8 0 -6 1 -8 2.5 -9 4.5 -9 6.5 -9 9 -7.5 9 -4.5 9 -1 6 2 0 7Z' "
                "fill='%23F49AC1' stroke='%23B83A74' stroke-width='1' stroke-linejoin='round'/%3E%3C/svg%3E")

MG_CSS = r'''
/* ---------- メリーゴーランドの的中ボタン：メリーゴーランドのPUSH（まさちゃんの指定） ----------
   上に しま模様の屋根（ピンクと白・下は丸い波・金のふち・てっぺんに金の玉とピンクの旗）。面はピンクから深いピンク・ぼけた光の玉・下は金の床。
   金の柱の小さな木馬が 左から右へ回りながら（6秒で2頭ぶん）、柱にそって上下する（2秒・となりどうしは反対）。
   クリーム色のふち・金のふち・こい金の厚み。白い「PUSH」に こいピンクの影。両がわと下の電球が交互に光る（1.2秒）。
   上下の動きは的中と同じ。押すと同じボタンがはじけて、金の星・ピンクのハート・白いきらきらが広がる */
.mg{--pr:22px;--pushA:#E067A1;--pushB:#A3326B;--pushC:#F9A6CC;--rim:#FFF6D8;--rimD:#E9C46A;
  --pushFace:linear-gradient(180deg,#F9A6CC 0%,#E067A1 45%,#C2437F 80%,#A3326B 100%)}
.push.mg{box-shadow:inset 0 2px 0 rgba(255,255,255,.55),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #B0862C,0 22px 34px rgba(80,10,50,.45)}
.push.mg span{transform:translateY(-7px);text-shadow:0 3px 0 #8A2556,0 0 12px rgba(255,255,255,.5)}   /* 文字は少し上（下を木馬が通る） */
.push.mg::after{border-color:rgba(255,225,240,.95)}
.mg .mgf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:22px;overflow:hidden;pointer-events:none}
.mg .mgf svg{display:block;width:200px;height:100px}
.mg .mgd{position:absolute;left:-34px;top:-66px;width:268px;height:196px;pointer-events:none;z-index:3}
.mg .mgd svg{display:block;width:268px;height:196px;overflow:visible}
.mg .mgx,.mg .mgy{transform-box:view-box;transform-origin:0 0}
.mg .mgx{animation:mgRound 6s linear infinite}
@keyframes mgRound{from{transform:translateX(0)}to{transform:translateX(180px)}}
.mg .mgy{animation:mgBob 2s ease-in-out infinite}
@keyframes mgBob{0%,100%{transform:translateY(3px)}50%{transform:translateY(-5px)}}
.mg .mgl{animation:mgBlink 1.2s ease-in-out infinite}.mg .mgl.b{animation-delay:-.6s}
@keyframes mgBlink{0%,100%{opacity:1}50%{opacity:.12}}
.tap.mg{color:#FFE3F0}
.pressed.mg{border-radius:22px;box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #B0862C}
.clips.mg{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.mg i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:mgFly 1.25s cubic-bezier(.15,.7,.3,1) var(--d) both;background:center/contain no-repeat}
.clips.mg .st{background-image:url("STAR")}
.clips.mg .ht{background-image:url("HEART")}
.clips.mg .dt{border-radius:50%;background:radial-gradient(circle,#FFFFFF 0 35%,rgba(255,240,200,.8) 60%,rgba(255,255,255,0) 72%)}
@keyframes mgFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 50px)) rotate(calc(var(--r) * 1.4)) scale(.6)}}
@media (prefers-reduced-motion:reduce){.mg .mgx,.mg .mgy,.mg .mgl{animation:none}.clips.mg{display:none}}
'''.replace('STAR', MG_STAR_URI).replace('HEART', MG_HEART_URI)


# ---------- 星座の的中ボタン：星でできたPUSH（まさちゃんの指定） ----------
SZ_GOLD, SZ_PALE, SZ_LAV = '#FFD86B', '#FFF6DC', '#9C8CFF'
SZ_LETTERS = [   # 星座の「PUSH」（面 200×100 の座標）：線でむすぶ星の点（折れ線ごと）・大きく光る星
    dict(lines=[[(28, 73), (28, 27), (44, 28), (52, 35), (51, 45), (43, 51), (28, 51)]], big=[(28, 73), (28, 27), (52, 35)]),                       # P
    dict(lines=[[(64, 27), (64, 59), (69, 69), (77, 73), (85, 69), (90, 59), (90, 27)]], big=[(64, 27), (77, 73), (90, 27)]),                       # U
    dict(lines=[[(128, 33), (120, 27), (109, 28), (102, 35), (105, 45), (115, 50), (125, 55), (129, 63), (123, 71), (112, 73), (102, 67)]],
         big=[(128, 33), (115, 50), (102, 67)]),                                                                                                     # S
    dict(lines=[[(142, 27), (142, 73)], [(170, 27), (170, 73)], [(142, 50), (170, 50)]], big=[(142, 27), (170, 73), (170, 27)]),                   # H
]


def sz_sparkle(L, w=.09):
    """4本の光（細い）"""
    w = L * w
    return f'M0 {-L:g}Q{w:.2f} {-w:.2f} {L:g} 0Q{w:.2f} {w:.2f} 0 {L:g}Q{-w:.2f} {w:.2f} {-L:g} 0Q{-w:.2f} {-w:.2f} 0 {-L:g}Z'


def stars_face_svg(sfx=''):
    """PUSHの面（面 200×100・角の丸み24で切りぬく。文字の下）：夜空（紺から紫）・うすい天の川・小さい星（いくつかは またたく）・
       ときどき流れ星（5.5秒に1回・.szm）。まん中に 星座の「PUSH」：うすく光る字の形（ラベンダー）・金の線・点ごとに星・大きい星は きらっ（.szt）。sfx：id のうしろにつける字"""
    K_, S_, M_, G_, N_ = (f'szb{c}{sfx}' for c in 'KSMGN')
    rnd = random.Random(53)
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="24"/></clipPath>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B0924"/><stop offset=".55" stop-color="#1B1546"/>'
            '<stop offset="1" stop-color="#2D1B5A"/></linearGradient>'
            f'<linearGradient id="{M_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#FFE7A3" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="{G_}"><stop offset="0" stop-color="#FFF6DC" stop-opacity=".9"/><stop offset=".4" stop-color="{SZ_GOLD}" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="{SZ_GOLD}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="{N_}"><stop offset="0" stop-color="#B49CFF" stop-opacity=".55"/><stop offset="1" stop-color="#7A5CFF" stop-opacity="0"/></radialGradient></defs>')
    sky = (f'<rect width="200" height="100" fill="url(#{S_})"/>'
           f'<ellipse cx="100" cy="52" rx="120" ry="20" fill="url(#{N_})" transform="rotate(-16 100 52)" opacity=".55"/>'
           f'<ellipse cx="62" cy="62" rx="44" ry="13" fill="url(#{N_})" transform="rotate(-16 62 62)" opacity=".45"/>')
    dots = ''
    for i in range(46):                                                   # 小さい星（12こに1こは またたく）
        x, y, r = rnd.uniform(4, 196), rnd.uniform(4, 96), rnd.choice((.45, .55, .7, .9, 1.1))
        tw = i % 4 == 0
        dots += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#FFFFFF" opacity="{rnd.uniform(.45, .9):.2f}"'
                 + (f' class="szw2" style="animation-delay:{-rnd.uniform(0, 2.4):.2f}s"' if tw else '') + '/>')
    meteor = (f'<g class="szm"><path d="M0 0L38 -15" stroke="url(#{M_})" stroke-width="1.8" stroke-linecap="round"/>'
              '<circle r="1.7" fill="#FFFFFF"/></g>')
    glow = line = pts = ''
    for L in SZ_LETTERS:
        for pl in L['lines']:
            d = 'M' + 'L'.join(f'{x} {y}' for x, y in pl)
            glow += f'<path d="{d}"/>'
            line += f'<path d="{d}"/>'
            for x, y in pl:
                if (x, y) not in L['big']:
                    pts += f'<circle cx="{x}" cy="{y}" r="4.2" fill="url(#{G_})"/><circle cx="{x}" cy="{y}" r="1.9" fill="{SZ_PALE}"/>'
    k = 0
    for L in SZ_LETTERS:
        for x, y in L['big']:
            pts += (f'<g transform="translate({x} {y})"><g class="szt" style="animation-delay:{-(k * .618 % 1) * 2.2:.2f}s">'
                    f'<circle r="7.5" fill="url(#{G_})"/><path d="{sz_sparkle(9.5, .1)}" fill="{SZ_PALE}"/><circle r="2.3" fill="#FFFFFF"/></g></g>')
            k += 1
    letters = (f'<g fill="none" stroke="{SZ_LAV}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity=".3">{glow}</g>'
               f'<g fill="none" stroke="#FFE7A3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".95">{line}</g>{pts}')
    return (f'<i class="szp" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{sky}{dots}{meteor}{letters}</g></svg></i>')


def stars_decor_svg(sfx=''):
    """PUSHのまわり：ふちの帯（紺）に 小さい金の星を ならべて、光が ぐるっと回る（.szc）・右上に金の三日月（ゆっくり ゆれる）・左上に大きい星。文字の上"""
    C_ = f'szbC{sfx}'
    r0, x0, y0, x1, y1 = 28, -4, -4, 204, 104                              # ふちの帯のまん中の線（角の丸み 24＋4）
    segs = [((x0 + r0, y0), (x1 - r0, y0)), ((x1, y0 + r0), (x1, y1 - r0)), ((x1 - r0, y1), (x0 + r0, y1)), ((x0, y1 - r0), (x0, y0 + r0))]
    corners = [(x1 - r0, y0 + r0, -90), (x1 - r0, y1 - r0, 0), (x0 + r0, y1 - r0, 90), (x0 + r0, y0 + r0, 180)]
    path = []
    for (a, b), (cx, cy, ang) in zip(segs, corners):                       # 上 → 右上の角 → 右 → … の順に点を作る
        n = max(1, round(math.dist(a, b) / 16))
        path += [(a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n) for t in range(n)]
        path += [(cx + r0 * math.cos(math.radians(ang + 90 * t / 3)), cy + r0 * math.sin(math.radians(ang + 90 * t / 3))) for t in range(3)]
    N = len(path)
    rim = ''.join(f'<g transform="translate({x:.1f} {y:.1f})"><path class="szc" d="{sz_sparkle(3.6 if i % 2 == 0 else 2.6, .14)}" fill="{SZ_GOLD if i % 2 == 0 else SZ_PALE}"'
                  f' style="animation-delay:{-(i / N) * 2.4:.2f}s"/></g>' for i, (x, y) in enumerate(path))
    moon = (f'<g transform="translate(206 -10)"><g class="szo"><mask id="{C_}" maskUnits="userSpaceOnUse" x="-20" y="-20" width="40" height="40">'
            '<rect x="-20" y="-20" width="40" height="40" fill="#FFFFFF"/><circle cx="6.5" cy="-5" r="11.5" fill="#000000"/></mask>'
            f'<circle r="14" fill="{SZ_GOLD}" mask="url(#{C_})"/><circle r="14" fill="none" stroke="#B8860B" stroke-width="1" mask="url(#{C_})" opacity=".6"/></g></g>')
    star = (f'<g transform="translate(-8 -12)"><g class="szt" style="animation-delay:-.7s"><path d="{sz_sparkle(12, .12)}" fill="{SZ_PALE}"/>'
            '<circle r="2.4" fill="#FFFFFF"/></g></g>')
    return (f'<i class="szd" aria-hidden="true"><svg viewBox="-34 -40 268 180" width="268" height="180">'
            f'{rim}{moon}{star}</svg></i>')


def stars_push_svg(sfx=''):
    return stars_face_svg(sfx) + stars_decor_svg(sfx)


def stars_burst(n=26, seed=31):
    """押した瞬間に、金の星・白い きらきら・ラベンダーの小さい星がパッと広がる"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 175)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        cls = 'g5' if i % 3 == 0 else 'w4' if i % 3 == 1 else 'lv'
        z = rnd.uniform(15, 22) if cls != 'lv' else rnd.uniform(7, 10)
        out += (f'<i class="{cls}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(90, 240):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips sz" aria-hidden="true">{out}</div>'


SZ_STAR5_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'%3E%3Cpath d='M0 -9L2.6 -3.2 8.6 -2.8 4 1.2 5.4 7.2 0 4 -5.4 7.2 -4 1.2 -8.6 -2.8 -2.6 -3.2Z' "
                "fill='%23FFD86B' stroke='%23FFF6DC' stroke-width='.8' stroke-linejoin='round'/%3E%3C/svg%3E")
SZ_STAR4_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'%3E%3Cpath d='M0 -9.5Q1 -1 9.5 0Q1 1 0 9.5Q-1 1 -9.5 0Q-1 -1 0 -9.5Z' "
                "fill='%23FFF6DC'/%3E%3C/svg%3E")

SZ_CSS = r'''
/* ---------- 星座の的中ボタン：星でできたPUSH（まさちゃんの指定） ----------
   面は夜空（紺から紫・うすい天の川・小さい星がまたたく・ときどき流れ星）。まん中の「PUSH」は 星座：うすく光る字の形・金の線・点ごとに星・大きい星が きらっ。
   （ボタンの字は見えないようにして、星座の字を見せる。読み上げは「PUSH」のまま）
   ふちの帯（紺）に 小さい金の星をならべ、光がぐるっと回る（2.4秒）。外がわに金のふち・こい紫の厚み。右上に金の三日月（ゆっくり ゆれる）・左上に大きい星。
   上下の動きは的中と同じ。押すとボタンがはじけて（夜空なので強く光らせない）、金の星・白い きらきら・ラベンダーの星が広がる */
.sz{--pr:24px;--pushA:#B9ACFF;--pushB:#1A1440;--pushC:#2D1B5A;--rim:#17123F;--rimD:#FFD86B;
  --pushFace:linear-gradient(180deg,#0B0924 0%,#1B1546 55%,#2D1B5A 100%)}
.push.sz{box-shadow:inset 0 0 0 1px rgba(185,172,255,.35),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #3B2F86,0 0 34px rgba(185,172,255,.45),0 22px 34px rgba(0,0,0,.5)}
.push.sz span{color:transparent;text-shadow:none}
.push.sz::after{border-color:rgba(255,216,107,.85)}
.sz .szp{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:24px;overflow:hidden;pointer-events:none;font-style:normal}
.sz .szp svg{display:block;width:200px;height:100px}
.sz .szd{position:absolute;left:-34px;top:-40px;width:268px;height:180px;pointer-events:none;z-index:3;font-style:normal}
.sz .szd svg{display:block;width:268px;height:180px;overflow:visible}
.sz .szt,.sz .szm,.sz .szc,.sz .szo{transform-box:view-box;transform-origin:0 0}
.sz .szt{animation:szTwk 2.2s ease-in-out infinite}
@keyframes szTwk{0%,100%{transform:scale(.62) rotate(0deg);opacity:.6}50%{transform:scale(1.12) rotate(45deg);opacity:1}}
.sz .szw2{animation:szBlink 2.4s ease-in-out infinite}
@keyframes szBlink{0%,100%{opacity:.9}50%{opacity:.15}}
.sz .szm{opacity:0;animation:szMeteor 5.5s linear infinite 1.2s}
@keyframes szMeteor{0%{opacity:0;transform:translate(212px,2px)}3%{opacity:1}15%{opacity:0;transform:translate(96px,48px)}100%{opacity:0;transform:translate(96px,48px)}}
.sz .szc{animation:szChase 2.4s ease-in-out infinite}
@keyframes szChase{0%,100%{opacity:.35;transform:scale(.75)}12%{opacity:1;transform:scale(1.25)}35%{opacity:.35;transform:scale(.75)}}
.sz .szo{animation:szRock 4s ease-in-out infinite}
@keyframes szRock{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(8deg)}}
.tap.sz{color:#FFE7A3}
.pressed.sz{border-radius:24px;box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #3B2F86;animation-name:szPress}
@keyframes szPress{0%{transform:scale(1)}35%{transform:scale(.84);filter:brightness(1.3)}100%{transform:scale(1.75);opacity:0;filter:brightness(1.5)}}   /* 夜空は強く光らせない */
.clips.sz{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.sz i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:szFly 1.3s cubic-bezier(.15,.7,.3,1) var(--d) both;background:center/contain no-repeat}
.clips.sz .g5{background-image:url("STAR5")}
.clips.sz .w4{background-image:url("STAR4")}
.clips.sz .lv{border-radius:50%;background:radial-gradient(circle,#FFFFFF 0 30%,rgba(185,172,255,.85) 55%,rgba(185,172,255,0) 72%)}
@keyframes szFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 46px)) rotate(calc(var(--r) * 1.4)) scale(.6)}}
@media (prefers-reduced-motion:reduce){.sz .szt,.sz .szw2,.sz .szm,.sz .szc,.sz .szo{animation:none}.sz .szm{display:none}.clips.sz{display:none}}
'''.replace('STAR5', SZ_STAR5_URI).replace('STAR4', SZ_STAR4_URI)


# ---------- 勝負服の的中ボタン：勝負服でできたPUSH（まさちゃんの指定） ----------
SJ_NAVY, SJ_BLUE, SJ_RED, SJ_YEL, SJ_GRN = '#121A33', '#1A3FB8', '#E02424', '#FFC400', '#0F9D58'


def silks_face_svg(sfx=''):
    """PUSHの面（面 200×100・角の丸み18で切りぬく。文字の下）：勝負服の布（黄色に青のひし形・ひし形のさかいに細い紺の線）。
       サテンのつや（ななめの光と影・しわ）・つやの光が右から左へ流れる（3.2秒・.sjm）・まわりに白い縫い目。sfx：id のうしろにつける字"""
    K_, P_, L_, S_, G_ = (f'sjb{c}{sfx}' for c in 'KPLSG')
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="18"/></clipPath>'
            f'<pattern id="{P_}" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(45 100 50) translate(4 4)">'
            f'<rect width="24" height="24" fill="{SJ_YEL}"/><rect width="12" height="12" fill="{SJ_BLUE}"/><rect x="12" y="12" width="12" height="12" fill="{SJ_BLUE}"/></pattern>'
            f'<pattern id="{L_}" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45 100 50) translate(4 4)">'
            f'<path d="M0 0H12M0 0V12" stroke="{SJ_NAVY}" stroke-width="1" fill="none" opacity=".55"/></pattern>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".38"/>'
            '<stop offset=".28" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".55" stop-color="#000000" stop-opacity=".16"/>'
            '<stop offset=".72" stop-color="#FFFFFF" stop-opacity=".14"/><stop offset="1" stop-color="#000000" stop-opacity=".22"/></linearGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".5"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    folds = ('<path d="M18 100C40 70 52 44 50 0" stroke="#000000" stroke-opacity=".10" stroke-width="7" fill="none" stroke-linecap="round"/>'
             '<path d="M150 100C138 72 146 40 168 0" stroke="#000000" stroke-opacity=".09" stroke-width="8" fill="none" stroke-linecap="round"/>'
             '<path d="M30 100C50 72 62 46 62 0" stroke="#FFFFFF" stroke-opacity=".22" stroke-width="3" fill="none" stroke-linecap="round"/>'
             '<path d="M160 100C150 74 156 42 176 0" stroke="#FFFFFF" stroke-opacity=".2" stroke-width="3" fill="none" stroke-linecap="round"/>')
    body = (f'<rect width="200" height="100" fill="url(#{P_})"/><rect width="200" height="100" fill="url(#{L_})"/>{folds}'
            f'<rect width="200" height="100" fill="url(#{S_})"/>'
            f'<g class="sjm"><rect x="0" y="-20" width="46" height="140" fill="url(#{G_})" transform="skewX(-24)"/></g>'
            '<rect x="5.5" y="5.5" width="189" height="89" rx="13" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-dasharray="5 4" opacity=".9"/>')
    return (f'<i class="sjf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def silks_sleeve(sfx, side):
    """袖（青に黄の輪・はしは紺のふち）：肩（0,0）から外へ（左の袖は左右反対）。はためく（.sjv）"""
    C_ = f'sjbC{sfx}{side}'
    tube = 'M0 -15C14 -17 30 -14 44 -10C47 -3 47 4 44 11C30 14 14 16 0 15C-4 5 -4 -5 0 -15Z'
    return (f'<g class="sjv {"l" if side < 0 else "r"}"><g transform="scale({side} 1) rotate(38)">'
            f'<clipPath id="{C_}"><path d="{tube}"/></clipPath>'
            f'<path d="{tube}" fill="{SJ_BLUE}"/>'
            f'<g clip-path="url(#{C_})"><rect x="14" y="-20" width="8" height="40" fill="{SJ_YEL}"/><rect x="28" y="-20" width="8" height="40" fill="{SJ_YEL}"/>'
            '<rect x="-6" y="-20" width="60" height="12" fill="#FFFFFF" opacity=".22"/><rect x="-6" y="8" width="60" height="12" fill="#000000" opacity=".14"/></g>'
            f'<path d="{tube}" fill="none" stroke="{SJ_NAVY}" stroke-width="2.6" stroke-linejoin="round"/>'
            f'<path d="M42 -10C45 -3 45 4 42 11" stroke="#FFFFFF" stroke-width="3" fill="none"/>'
            f'<path d="M46 -10C49 -3 49 4 46 11" stroke="{SJ_NAVY}" stroke-width="2" fill="none"/></g></g>')


def silks_decor_svg(sfx=''):
    """PUSHのまわり：両がわに袖（はためく）・上のまん中に えり（紺のVの えりぐり・青いえりに黄のふち）。袖は面のうしろ、えりは文字の上"""
    sleeves = (f'<g transform="translate(-4 22)">{silks_sleeve(sfx, -1)}</g>'
               f'<g transform="translate(204 22)">{silks_sleeve(sfx, 1)}</g>')
    collar = (f'<path d="M80 -9H120L100 16Z" fill="{SJ_NAVY}"/>'
              f'<path d="M80 -9L100 16L94 21L72 -6Z" fill="{SJ_BLUE}" stroke="{SJ_NAVY}" stroke-width="2" stroke-linejoin="round"/>'
              f'<path d="M120 -9L100 16L106 21L128 -6Z" fill="{SJ_BLUE}" stroke="{SJ_NAVY}" stroke-width="2" stroke-linejoin="round"/>'
              f'<path d="M75 -5L96 19M125 -5L104 19" stroke="{SJ_YEL}" stroke-width="2.2" stroke-linecap="round"/>')
    return (f'<i class="sjs" aria-hidden="true"><svg viewBox="-60 -30 320 160" width="320" height="160">{sleeves}</svg></i>'
            f'<i class="sjd" aria-hidden="true"><svg viewBox="-60 -30 320 160" width="320" height="160">{collar}</svg></i>')


def silks_push_svg(sfx=''):
    return silks_face_svg(sfx) + silks_decor_svg(sfx)


def sj_diamond_uri(col):
    return ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'%3E%3Cpath d='M0 -9L7 0 0 9 -7 0Z' "
            f"fill='%23{col[1:]}' stroke='%23121A33' stroke-width='1.4' stroke-linejoin='round'/%3E%3C/svg%3E")


def silks_burst(n=24, seed=37):
    """押した瞬間に、勝負服の4色（黄・青・赤・緑）のひし形がくるくる回りながら広がる"""
    rnd = random.Random(seed)
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 175)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        cls = 'dy db dr dg'.split()[i % 4]
        out += (f'<i class="{cls}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{rnd.uniform(15, 22):.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(160, 320):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips sj" aria-hidden="true">{out}</div>'


SJ_CSS = r'''
/* ---------- 勝負服の的中ボタン：勝負服でできたPUSH（まさちゃんの指定） ----------
   面は勝負服の布：黄色に青のひし形（騎手の勝負服と同じ柄）・サテンのつやとしわ・つやの光が右から左へ流れる・まわりに白い縫い目。
   両がわに青い袖（黄の輪）が風ではためき、上のまん中に えり（紺のVの えりぐり・青いえりに黄のふち）。
   「PUSH」は白い字に紺のふち・赤いずれの影（漫画のロゴと同じ）。青いふち・紺のふち・こい青の厚み。
   上下の動きは的中と同じ。押すとボタンがはじけて（黄色は強く光らせない）、4色のひし形がくるくる広がる */
.sj{--pr:18px;--pushA:#FFC400;--pushB:#121A33;--pushC:#FFE07A;--rim:#1A3FB8;--rimD:#121A33;
  --pushFace:linear-gradient(180deg,#FFD84A,#FFC400)}
.push.sj{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #0F2A80,0 22px 34px rgba(0,0,0,.45)}
.push.sj span{color:#FFFFFF;text-shadow:2px 0 0 #121A33,-2px 0 0 #121A33,0 2px 0 #121A33,0 -2px 0 #121A33,2px 2px 0 #121A33,-2px 2px 0 #121A33,2px -2px 0 #121A33,-2px -2px 0 #121A33,5px 5px 0 #E02424}
.push.sj::after{border-color:rgba(255,196,0,.95)}
.sj .sjf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:18px;overflow:hidden;pointer-events:none;font-style:normal}
.sj .sjf svg{display:block;width:200px;height:100px}
.sj .sjs,.sj .sjd{position:absolute;left:-60px;top:-30px;width:320px;height:160px;pointer-events:none;font-style:normal}
.sj .sjs{z-index:-1}
.sj .sjd{z-index:3}
.sj .sjs svg,.sj .sjd svg{display:block;width:320px;height:160px;overflow:visible}
.sj .sjm,.sj .sjv{transform-box:view-box;transform-origin:0 0}
.sj .sjm{animation:sjSheen 3.2s ease-in-out infinite}
@keyframes sjSheen{0%{transform:translateX(230px)}60%,100%{transform:translateX(-90px)}}
.sj .sjv{animation:sjFlap .7s ease-in-out infinite alternate}
.sj .sjv.r{animation-delay:-.35s}
@keyframes sjFlap{from{transform:rotate(-5deg)}to{transform:rotate(6deg)}}
.tap.sj{color:#FFC400}
.pressed.sj{border-radius:18px;box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #0F2A80;animation-name:sjPress}
@keyframes sjPress{0%{transform:scale(1)}35%{transform:scale(.84);filter:brightness(1.15)}100%{transform:scale(1.75);opacity:0;filter:brightness(1.3)}}   /* 黄色は強く光らせない */
.clips.sj{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.sj i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:sjFly 1.25s cubic-bezier(.15,.7,.3,1) var(--d) both;background:center/contain no-repeat}
.clips.sj .dy{background-image:url("DY")}
.clips.sj .db{background-image:url("DB")}
.clips.sj .dr{background-image:url("DR")}
.clips.sj .dg{background-image:url("DG")}
@keyframes sjFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 52px)) rotate(calc(var(--r) * 1.4)) scale(.6)}}
@media (prefers-reduced-motion:reduce){.sj .sjm,.sj .sjv{animation:none}.sj .sjm{display:none}.clips.sj{display:none}}
'''.replace('DY', sj_diamond_uri(SJ_YEL)).replace('DB', sj_diamond_uri(SJ_BLUE)).replace('DR', sj_diamond_uri(SJ_RED)).replace('DG', sj_diamond_uri(SJ_GRN))


# ---------- ネオンの的中ボタン：ネオンでできたPUSH（まさちゃんの指定） ----------
NN_PINK, NN_CYAN, NN_PURP, NN_YEL = '#FF2BD6', '#2EEBFF', '#B36BFF', '#FFE45C'
NN_LETTERS = [   # ネオン管の「PUSH」（面 200×100 の座標・1本の管で書く字）
    'M30 74V28H46C58 28 62 35 62 41C62 47 57 53 46 53H30',                                               # P
    'M73 28V58C73 69 79 74 86.5 74C94 74 100 69 100 58V28',                                               # U
    'M136 34C132 29 126 27 121 27C113 27 108 32 108 38.5C108 46 116 48.5 122 50.5C130 53 137 55.5 137 63C137 70 130 74 122 74C114 74 109 70.5 107 66',  # S
    'M149 28V74M174 28V74M149 51H174',                                                                    # H
]
NN_CLIPS = [(30, 40), (30, 66), (86.5, 74), (108, 38.5), (137, 63), (149, 40), (174, 64)]   # 管をとめる金具


def nn_tube(d, col, core, cls='', sw=2.6, f=''):
    """ネオン管：外の光（ぼかし）・管の色・白っぽい しん"""
    return (f'<g class="{cls}" fill="none" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{d}" stroke="{col}" stroke-width="{sw * 4.4:.1f}" opacity=".55" filter="url(#{f})"/>'
            f'<path d="{d}" stroke="{col}" stroke-width="{sw * 2:.1f}" opacity=".9"/>'
            f'<path d="{d}" stroke="{core}" stroke-width="{sw:.1f}"/></g>')


def neon_face_svg(sfx=''):
    """PUSHの面（面 200×100・角の丸み16で切りぬく。文字の下）：夜のガラスの板（こい紫・下に うすいピンクの格子・小さい星）。
       まわりに水色のネオン管のわく（光の玉が ぐるっと走る・.nnc）・まん中に ピンクのネオン管の「PUSH」（いつも ほんのり明るさがゆれる・
       ときどき「S」だけ ちらっと暗くなる・.nnS）・管をとめる金具。sfx：id のうしろにつける字"""
    K_, G_, F_, B_ = (f'nnb{c}{sfx}' for c in 'KGFB')
    rnd = random.Random(61)
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="16"/></clipPath>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140A2A"/><stop offset=".6" stop-color="#0D0720"/>'
            '<stop offset="1" stop-color="#1E0A2E"/></linearGradient>'
            f'<filter id="{F_}" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="3.2"/></filter>'
            f'<filter id="{B_}" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="1.4"/></filter></defs>')
    grid = ''.join(f'<path d="M{100 + k * 9:.1f} 66L{100 + k * 40:.1f} 100" stroke="{NN_PINK}" stroke-width=".8" opacity=".22"/>' for k in range(-6, 7))
    grid += ''.join(f'<path d="M0 {66 + 34 * (j / 5) ** 1.8:.1f}H200" stroke="{NN_PINK}" stroke-width=".8" opacity=".22"/>' for j in range(0, 6))
    stars = ''.join(f'<circle cx="{rnd.uniform(6, 194):.1f}" cy="{rnd.uniform(5, 60):.1f}" r="{rnd.choice((.5, .6, .8)):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(.35, .7):.2f}"/>'
                    for _ in range(22))
    frame = 'M19 7H181A12 12 0 0 1 193 19V81A12 12 0 0 1 181 93H19A12 12 0 0 1 7 81V19A12 12 0 0 1 19 7Z'
    clips = ''.join(f'<rect x="{x - 2.2:.1f}" y="{y - 4:.1f}" width="4.4" height="8" rx="1.4" fill="#3A3550" stroke="#0B0618" stroke-width=".8"/>' for x, y in NN_CLIPS)
    letters = ''.join(nn_tube(d, NN_PINK, '#FFE6FA', 'nnS' if i == 2 else '', f=F_) for i, d in enumerate(NN_LETTERS))
    body = (f'<rect width="200" height="100" fill="url(#{G_})"/>{grid}{stars}'
            f'<g class="nnh">{nn_tube(frame, NN_CYAN, "#E6FDFF", sw=2.2, f=F_)}'
            f'<path class="nnc" d="{frame}" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="26 497.4" filter="url(#{B_})"/>'
            f'<g class="nnl">{letters}</g></g>{clips}'
            '<path d="M14 15C40 8 80 6 120 9" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity=".07"/>')
    return (f'<i class="nnf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def neon_decor_svg(sfx=''):
    """PUSHのまわり：左上と右下に ネオンの小さい星（またたく）・右上に黄色いネオンの いなずま。文字の上"""
    F_ = f'nnbD{sfx}'
    def spark(x, y, col, L, delay):
        w = L * .16
        d = f'M0 {-L}Q{w:.1f} {-w:.1f} {L} 0Q{w:.1f} {w:.1f} 0 {L}Q{-w:.1f} {w:.1f} {-L} 0Q{-w:.1f} {-w:.1f} 0 {-L}Z'
        return (f'<g transform="translate({x} {y})"><g class="nnt" style="animation-delay:{delay}s">'
                f'<path d="{d}" fill="{col}" filter="url(#{F_})" opacity=".8"/><path d="{d}" fill="{col}"/>'
                f'<path d="{d}" fill="#FFFFFF" transform="scale(.45)"/></g></g>')
    bolt = 'M214 -22L204 -4H212L200 14'
    return (f'<i class="nnd" aria-hidden="true"><svg viewBox="-34 -40 268 180" width="268" height="180"><defs>'
            f'<filter id="{F_}" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.4"/></filter></defs>'
            + spark(-14, -14, NN_CYAN, 11, 0) + spark(214, 118, NN_PINK, 9, -.9)
            + f'<g class="nnz">{nn_tube(bolt, NN_YEL, "#FFFBE0", sw=2.2, f=F_)}</g></svg></i>')


def neon_push_svg(sfx=''):
    return neon_face_svg(sfx) + neon_decor_svg(sfx)


def neon_burst(n=26, seed=43):
    """押した瞬間に、ネオン管のかけら（ピンク・水色・むらさき・黄色の光る短い管）と光の輪が広がる"""
    rnd = random.Random(seed)
    out = ''
    cols = (NN_PINK, NN_CYAN, NN_PURP, NN_YEL)
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 175)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        c = cols[i % 4]
        ring = i % 5 == 4
        z = rnd.uniform(9, 13) if ring else rnd.uniform(16, 26)
        out += (f'<i class="{"rg" if ring else "tb"}" style="--c:{c};--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;'
                f'--r:{rnd.choice((-1, 1)) * rnd.uniform(140, 320):.0f}deg;--d:{rnd.uniform(0, .1):.2f}s"></i>')
    return f'<div class="clips nn" aria-hidden="true">{out}</div>'


NN_CSS = r'''
/* ---------- ネオンの的中ボタン：ネオンでできたPUSH（まさちゃんの指定） ----------
   面は夜のガラスの板（こい紫・下に うすいピンクの格子・小さい星）。まん中に ピンクのネオン管で書いた「PUSH」（白っぽい しん・まわりに光）、
   まわりに水色のネオン管のわく（白い光の玉が ぐるっと走る 2.6秒）・管をとめる金具。ネオンは いつも ほんのり明るさがゆれて（2.4秒）、
   5秒に1回「S」だけ ちらっと暗くなる（消えない）。ボタンの字は見えないようにして ネオン管の字を見せる（読み上げは「PUSH」のまま）。
   こい紫のふち・黒いふち・水色の光。左上と右下に ネオンの星・右上に 黄色い いなずま。上下の動きは的中と同じ。
   押すとボタンがはじけて（強く光らせない）、ネオン管のかけらと光の輪が広がる */
.nn{--pr:16px;--pushA:#FF2BD6;--pushB:#0B0618;--pushC:#2EEBFF;--rim:#1A0F33;--rimD:#0B0618;
  --pushFace:linear-gradient(180deg,#140A2A,#0D0720)}
.push.nn{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #05030C,0 0 26px 14px rgba(46,235,255,.32),0 22px 34px rgba(0,0,0,.5)}
.push.nn span{color:transparent;text-shadow:none}
.push.nn::after{border-color:rgba(46,235,255,.9)}
.nn .nnf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:16px;overflow:hidden;pointer-events:none;font-style:normal}
.nn .nnf svg{display:block;width:200px;height:100px}
.nn .nnd{position:absolute;left:-34px;top:-40px;width:268px;height:180px;pointer-events:none;z-index:3;font-style:normal}
.nn .nnd svg{display:block;width:268px;height:180px;overflow:visible}
.nn .nnt{transform-box:view-box;transform-origin:0 0}
.nn .nnh{animation:nnHum 2.4s ease-in-out infinite}
@keyframes nnHum{0%,100%{opacity:1}50%{opacity:.86}}
.nn .nnS{animation:nnFlick 5s linear infinite}
@keyframes nnFlick{0%,70%,73%,76%,100%{opacity:1}71.5%{opacity:.4}74.5%{opacity:.55}}
.nn .nnc{animation:nnChase 2.6s linear infinite}
@keyframes nnChase{from{stroke-dashoffset:0}to{stroke-dashoffset:-523.4}}
.nn .nnt{animation:nnTw 1.8s ease-in-out infinite}
@keyframes nnTw{0%,100%{transform:scale(.7);opacity:.6}50%{transform:scale(1.1);opacity:1}}
.nn .nnz{animation:nnHum 1.6s ease-in-out infinite}
.tap.nn{color:#2EEBFF;text-shadow:0 0 6px rgba(46,235,255,.8)}
.pressed.nn{border-radius:16px;box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #05030C,0 0 26px 14px rgba(46,235,255,.32);animation-name:nnPress}
@keyframes nnPress{0%{transform:scale(1)}35%{transform:scale(.84);filter:brightness(1.3)}100%{transform:scale(1.75);opacity:0;filter:brightness(1.5)}}   /* 強く光らせない */
.clips.nn{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.nn i{position:absolute;opacity:0;animation:nnFly 1.25s cubic-bezier(.15,.7,.3,1) var(--d) both}
.clips.nn .tb{left:calc(var(--z) / -2);top:-2px;width:var(--z);height:4px;border-radius:2px;background:#FFFFFF;
  box-shadow:0 0 0 1.5px var(--c),0 0 8px 2px var(--c),0 0 16px 3px var(--c)}
.clips.nn .rg{left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);border-radius:50%;border:2px solid #FFFFFF;
  box-shadow:0 0 0 1.5px var(--c),0 0 8px 2px var(--c),inset 0 0 6px var(--c)}
@keyframes nnFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 46px)) rotate(calc(var(--r) * 1.4)) scale(.6)}}
@media (prefers-reduced-motion:reduce){.nn .nnh,.nn .nnS,.nn .nnc,.nn .nnt,.nn .nnz{animation:none}.nn .nnc{display:none}.clips.nn{display:none}}
'''


# ---------- ドット絵の的中ボタン：ドットでできたPUSH（まさちゃんの指定） ----------
DP_U = 5             # 1ドット＝5px（ボタンの面 200×100 ＝ 40×20 ドット）。色はドット絵のテーマと同じ16色から
DP_K, DP_NAVY, DP_PLUM, DP_RED, DP_PINK, DP_WHITE = '#000000', '#1D2B53', '#7E2553', '#FF004D', '#FF77A8', '#FFF1E8'
DP_YEL, DP_ORG, DP_GRAY, DP_LAV, DP_DGRAY, DP_BLUE, DP_GREEN, DP_BROWN = '#FFEC27', '#FFA300', '#C2C3C7', '#83769C', '#5F574F', '#29ADFF', '#00E436', '#AB5236'
DP_FONT = dict(      # 「PUSH」の太いドットの字（6×7）
    P=['XXXXX.', 'XX..XX', 'XX..XX', 'XXXXX.', 'XX....', 'XX....', 'XX....'],
    U=['XX..XX', 'XX..XX', 'XX..XX', 'XX..XX', 'XX..XX', 'XX..XX', '.XXXX.'],
    S=['.XXXXX', 'XX....', 'XX....', '.XXXX.', '....XX', '....XX', 'XXXXX.'],
    H=['XX..XX', 'XX..XX', 'XX..XX', 'XXXXXX', 'XX..XX', 'XX..XX', 'XX..XX'])
DP_SPARK = [{(0, 0): DP_WHITE},                                                          # きらっ（3コマ）：点
            {(0, 0): DP_WHITE, (1, 0): DP_YEL, (-1, 0): DP_YEL, (0, 1): DP_YEL, (0, -1): DP_YEL},   # 小さい十字
            {(0, 0): DP_WHITE, (1, 0): DP_WHITE, (-1, 0): DP_WHITE, (0, 1): DP_WHITE, (0, -1): DP_WHITE,
             **{(s * d, 0): c for s in (1, -1) for d, c in ((2, DP_YEL), (3, DP_ORG))},
             **{(0, s * d): c for s in (1, -1) for d, c in ((2, DP_YEL), (3, DP_ORG))}}]   # 大きい十字
DP_COIN = [['.XX.', 'XXXX', 'XXXX', 'XXXX', 'XXXX', '.XX.'], ['.X.', 'XXX', 'XXX', 'XXX', 'XXX', '.X.'], ['X'] * 6]   # 回る金貨：正面・ななめ・横
DP_HEART = ['.XX...XX.', 'XXXX.XXXX', 'XXXXXXXXX', 'XXXXXXXXX', '.XXXXXXX.', '..XXXXX..', '...XXX...', '....X....']   # テーマの飾りのハート


def dp_round(x0, y0, x1, y1, r):
    """角を段にけずった四角のドット（x0〜x1・y0〜y1 をふくむ）。r：けずる段の数"""
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            if max(x0 + r - x, x - x1 + r, 0) + max(y0 + r - y, y - y1 + r, 0) <= r}


def dp_outline(cells):
    """まわり1ドット（上下左右）"""
    return {(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)


def dp_cells(rows):
    return {(c, r) for r, row in enumerate(rows) for c, v in enumerate(row) if v != '.'}


def dp_rects(paint, u=DP_U):
    """ドットの絵（{(x, y): 色}）→ 色ごとに1つの <path>（横に続く同じ色は1つの四角）"""
    runs = {}
    for y in sorted({p[1] for p in paint}):
        xs = sorted(x for x, yy in paint if yy == y)
        i = 0
        while i < len(xs):
            j, c = i, paint[(xs[i], y)]
            while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1 and paint[(xs[j + 1], y)] == c:
                j += 1
            runs.setdefault(c, []).append(f'M{xs[i] * u} {y * u}h{(j - i + 1) * u}v{u}h-{(j - i + 1) * u}z')
            i = j + 1
    return ''.join(f'<path fill="{c}" d="{"".join(d)}"/>' for c, d in runs.items())


def dp_body(pushed=False):
    """ボタンのドット（{(x, y): 色}・面の左上が 0,0）：灰色の台（白い上と左・むらさきの下と右・黒いふち）に、
       赤いボタン（上と左はピンク・下と右は ちらし（市松）・厚み2ドット・黒いふち・左上に白い光）と、白と黄色の「PUSH」（こい影）。
       pushed：押しこまれた形（ボタンが2ドット下がって厚みがなくなる）"""
    P = {}
    base = dp_round(-3, -3, 42, 24, 2)
    for c in dp_outline(base):
        P[c] = DP_K
    for x, y in base:
        P[(x, y)] = (DP_WHITE if ((x, y - 1) not in base or (x - 1, y) not in base) else
                     DP_LAV if ((x, y + 1) not in base or (x + 1, y) not in base) else DP_GRAY)
    oy = 2 if pushed else 0
    for x in range(0, 40):                                  # 台のくぼみ（ボタンのうしろの かげ）
        for y in range(0, oy):
            P[(x, y)] = DP_DGRAY
    btn = dp_round(0, oy, 39, 21, 1)
    for c in dp_outline(btn):
        P[c] = DP_K
    for x, y in btn:
        f = y - oy                                          # 面の何段目か（20〜21 は厚み）
        if f >= 20:
            col = DP_PLUM
        elif f == 0 or x == 0:
            col = DP_PINK
        elif f == 19 or x == 39:
            col = DP_PLUM if (x + y) % 2 else DP_RED
        else:
            col = DP_RED
        P[(x, y)] = col
    for x, y in ((2, 2), (3, 2), (4, 2), (2, 3), (6, 2)):  # 左上の光
        P[(x, y + oy)] = DP_WHITE
    letters, x0 = [], 6
    for ch in 'PUSH':
        letters += [(x0 + c, 6 + oy + r) for c, r in dp_cells(DP_FONT[ch])]
        x0 += 7
    for x, y in letters:
        P[(x + 1, y + 1)] = DP_PLUM                         # 影
    for x, y in letters:
        P[(x, y)] = DP_WHITE if y - 6 - oy < 4 else DP_YEL  # 上は白・下は黄色
    return P


def pixel_face_svg(sfx='', pushed=False):
    """PUSHのボタン（台・ボタン・字。.push の左上から -20,-20 に 240×150）。面の上を ななめの光が ドットずつ通る（.dps）"""
    K_ = f'dpbK{sfx}'
    stripe = '<path d="' + ''.join(f'M{(-3 - y) * DP_U} {y * DP_U}h{2 * DP_U}v{DP_U}h-{2 * DP_U}z' for y in range(1, 19)) + '"/>'
    shine = '' if pushed else (f'<defs><clipPath id="{K_}"><rect x="5" y="5" width="190" height="90"/></clipPath></defs>'
                               f'<g clip-path="url(#{K_})"><g class="dps" fill="{DP_WHITE}" opacity=".4">{stripe}</g></g>')
    return (f'<i class="dpf" aria-hidden="true"><svg viewBox="-20 -20 240 150" width="240" height="150" shape-rendering="crispEdges">'
            f'{dp_rects(dp_body(pushed))}{shine}</svg></i>')


def dp_frames(frames, cls, at):
    """コマのドット絵を重ねて、決まった時だけ見せる（class＝cls＋コマの番号）。at：置く所（ドット）"""
    return ''.join(f'<g class="{cls}{i}" transform="translate({at[0] * DP_U} {at[1] * DP_U})">{dp_rects(fr)}</g>' for i, fr in enumerate(frames))


def dp_coin_frames():
    out = []
    for rows in DP_COIN:
        cells = dp_cells(rows)
        w = len(rows[0])
        cx = -(w // 2)
        cells = {(x + cx, y - 3) for x, y in cells}
        fr = {c: DP_K for c in dp_outline(cells)}
        for x, y in cells:
            k = x - cx
            fr[(x, y)] = (DP_ORG if w == 1 or k == w - 1 else DP_WHITE if k == 1 else DP_YEL)
        out.append(fr)
    return out


def pixel_decor_svg(sfx=''):
    """PUSHのまわり（.push の左上から -70,-60 に 340×230）：左に ▶ のカーソル（右へ ちょんちょん）・左上に回る金貨・
       右上と右下に きらっ（点 → 小さい十字 → 大きい十字）"""
    cur = dp_cells(['X...', 'XX..', 'XXX.', 'XXXX', 'XXX.', 'XX..', 'X...'])
    cur = {(x - 10, y + 7) for x, y in cur}
    cp = {c: DP_K for c in dp_outline(cur)}
    cp.update({c: DP_WHITE for c in cur})
    for x, y in cur:
        if y == 13 or (x, y + 1) not in cur:
            cp[(x, y)] = DP_GRAY                            # 下のふちは灰色
    spark = lambda at, k: f'<g class="dpk" style="animation-delay:{k}s">{dp_frames(DP_SPARK, "dpk", at)}</g>'
    return (f'<i class="dpd" aria-hidden="true"><svg viewBox="-70 -60 340 230" width="340" height="230" shape-rendering="crispEdges">'
            f'<g class="dpc">{dp_rects(cp)}</g>'
            f'<g class="dpm">{dp_frames(dp_coin_frames(), "dpm", (-8, -8))}</g>'
            + spark((45, -7), 0) + spark((48, 27), -.8) + '</svg></i>')


def pixel_push_svg(sfx=''):
    return pixel_face_svg(sfx, pushed=(sfx == '2')) + pixel_decor_svg(sfx)


def dp_strip_uri(frames, box, u):
    """コマのドット絵を横に並べた1まい（CSS の背景の data: URI・SVG・ドットのまま）。box：(x0, y0, はば, 高さ) ドット（どのコマも同じ四角）"""
    x0, y0, w, h = box
    paint = {(x - x0 + i * w, y - y0): c for i, fr in enumerate(frames) for (x, y), c in fr.items()}
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {len(frames) * w * u} {h * u}' shape-rendering='crispEdges'>"
           + dp_rects(paint, u).replace('"', "'") + '</svg>')
    return 'data:image/svg+xml,' + svg.replace('#', '%23').replace('<', '%3C').replace('>', '%3E')


def dp_sprite_uri(paint, u):
    xs, ys = [p[0] for p in paint], [p[1] for p in paint]
    return dp_strip_uri([paint], (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1), u)


def dp_heart():
    cells = dp_cells(DP_HEART)
    fr = {c: DP_K for c in dp_outline(cells)}
    for x, y in cells:
        fr[(x, y)] = DP_WHITE if (x, y) in {(1, 1), (1, 2), (2, 1)} else DP_PLUM if (x, y) in {(7, 4), (6, 5), (5, 6), (8, 3)} else DP_RED
    return fr


def dp_block(col, dark):
    cells = {(x, y) for x in range(3) for y in range(3)}
    fr = {c: DP_K for c in dp_outline(cells)}
    for x, y in cells:
        fr[(x, y)] = DP_WHITE if (x, y) == (0, 0) else dark if x == 2 or y == 2 else col
    return fr


def pixel_burst(n=26, seed=47):
    """押した瞬間に、ドットの金貨（くるくる回る）・ハート・きらっ・色のブロックが はじけて飛び、さいごは ちかちか点めつして消える（昔のゲームと同じ）"""
    rnd = random.Random(seed)
    out = ''
    kinds = 'c h s b1 c b2 s b3 c h b4 s'.split()
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(95, 180)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        k = kinds[i % len(kinds)]
        out += (f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--d:{rnd.uniform(0, .1):.2f}s"><b></b></i>')
    return f'<div class="clips dp" aria-hidden="true">{out}</div>'


DP_CSS = r'''
/* ---------- ドット絵の的中ボタン：ドットでできたPUSH（まさちゃんの指定） ----------
   ぜんぶ 5px の四角いドット（テーマと同じ16色）で描いた昔のゲームのボタン：灰色の台（白い上と左・むらさきの下と右・黒いふち）に、
   赤いボタン（上と左はピンク・下と右は市松のちらし・厚み・黒いふち・左上に白い光）。「PUSH」は太いドットの字（上は白・下は黄色・こい影）。
   面の上を ななめの光が ドットずつ通る（2.6秒に1回）。左に ▶ のカーソル（右へ ちょんちょん）・左上に回る金貨・右上と右下に きらっ。
   上下の動きも ドットずつ（6コマ）。わくの光の輪も 四角でカクカク広がる。押すと ボタンが へこんで（カチッ）、カクカク大きくなって消え（強く光らせない）、
   金貨・ハート・きらっ・ブロックが はじけて飛んで、さいごは ちかちか点めつして消える */
.dp{--pr:0px;--pushA:#FF004D;--pushB:#7E2553;--pushC:#FF77A8;--rim:#C2C3C7;--rimD:#000000;--pushFace:#FF004D}
.push.dp{background:none;box-shadow:none;border-radius:0;animation:dpBob .9s step-end infinite,dpPop .36s step-end both}
.push.dp span{color:transparent;text-shadow:none}
.push.dp::after{inset:-34px -34px -44px;border:0;border-radius:0;
  background:linear-gradient(#FFEC27,#FFEC27) 5px 0/calc(100% - 10px) 5px no-repeat,linear-gradient(#FFEC27,#FFEC27) 5px 100%/calc(100% - 10px) 5px no-repeat,
    linear-gradient(#FFEC27,#FFEC27) 0 5px/5px calc(100% - 10px) no-repeat,linear-gradient(#FFEC27,#FFEC27) 100% 5px/5px calc(100% - 10px) no-repeat;
  animation:dpRing 1.2s steps(4) infinite}
@keyframes dpRing{0%{transform:scale(.94);opacity:1}100%{transform:scale(1.22);opacity:0}}
@keyframes dpBob{0%,100%{transform:translateY(0)}16.6%{transform:translateY(-5px)}33.3%{transform:translateY(-10px)}50%{transform:translateY(-15px)}
  66.6%{transform:translateY(-10px)}83.3%{transform:translateY(-5px)}}
@keyframes dpPop{0%{scale:.25}25%{scale:.5}50%{scale:.8}75%{scale:1.08}100%{scale:1}}
.dp .dpf{position:absolute;left:-20px;top:-20px;width:240px;height:150px;pointer-events:none;font-style:normal}
.dp .dpf svg,.dp .dpd svg{display:block;overflow:visible}
.dp .dpd{position:absolute;left:-70px;top:-60px;width:340px;height:230px;pointer-events:none;z-index:3;font-style:normal}
.dp .dps{animation:dpShine 2.6s steps(60) .4s infinite}
@keyframes dpShine{0%{transform:translateX(0)}35%,100%{transform:translateX(300px)}}
.dp .dpc{animation:dpCur .8s step-end infinite}
@keyframes dpCur{0%,100%{transform:none}50%{transform:translateX(5px)}}
.dp .dpm0,.dp .dpm1,.dp .dpm2{opacity:0}
.dp .dpm0{opacity:1;animation:dpM0 1.8s step-end infinite}
.dp .dpm1{animation:dpM1 1.8s step-end infinite}
.dp .dpm2{animation:dpM2 1.8s step-end infinite}
@keyframes dpM0{0%,100%{opacity:1}8.3%{opacity:0}33.3%{opacity:1}}
@keyframes dpM1{0%,100%{opacity:0}8.3%{opacity:1}16.7%{opacity:0}25%{opacity:1}33.3%{opacity:0}}
@keyframes dpM2{0%,100%{opacity:0}16.7%{opacity:1}25%{opacity:0}}
.dp .dpk0,.dp .dpk1,.dp .dpk2{opacity:0;animation:1.6s step-end infinite;animation-delay:inherit}
.dp .dpk0{animation-name:dpK0}
.dp .dpk1{animation-name:dpK1}
.dp .dpk2{animation-name:dpK2}
@keyframes dpK0{0%,25%,100%{opacity:0}12.5%{opacity:1}62.5%{opacity:1}75%{opacity:0}}
@keyframes dpK1{0%,100%{opacity:0}25%{opacity:1}37.5%{opacity:0}50%{opacity:1}62.5%{opacity:0}}
@keyframes dpK2{0%,100%{opacity:0}37.5%{opacity:1}50%{opacity:0}}
.pshadow.dp{width:220px;height:15px;margin-top:44px;border-radius:0;filter:none;background:rgba(0,0,0,.42);
  clip-path:polygon(15px 0,calc(100% - 15px) 0,calc(100% - 15px) 5px,100% 5px,100% 10px,calc(100% - 15px) 10px,calc(100% - 15px) 15px,15px 15px,15px 10px,0 10px,0 5px,15px 5px);
  animation:dpShad .9s step-end infinite}
@keyframes dpShad{0%,100%{transform:scale(1)}16.6%{transform:scale(.92)}33.3%{transform:scale(.84)}50%{transform:scale(.76)}66.6%{transform:scale(.84)}83.3%{transform:scale(.92)}}
.tap.dp{font-family:"DotGothic16",sans-serif;font-size:22px;color:#FFEC27;text-shadow:3px 3px 0 #FF004D}
.pressed.dp{background:none;box-shadow:none;border-radius:0;animation:dpPress .5s step-end both}
@keyframes dpPress{0%{transform:none;opacity:1}20%{transform:scale(1.08);opacity:1}40%{transform:scale(1.2);opacity:.75}60%{transform:scale(1.34);opacity:.5}
  80%{transform:scale(1.48);opacity:.25}100%{transform:scale(1.6);opacity:0}}   /* へこむ → カクカク大きくなって消える（強く光らせない） */
.pressed.dp .dps{display:none}
.clips.dp{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.dp i{position:absolute;left:0;top:0;opacity:0;animation:dpFly 1.3s cubic-bezier(.15,.7,.3,1) var(--d) both,dpBlink 1.3s step-end var(--d) both}
.clips.dp b{position:absolute;display:block;background:0 0/100% 100% no-repeat}
.clips.dp .c b{left:-12px;top:-16px;width:24px;height:32px;background:url("DPC") 0 0/96px 32px no-repeat;animation:dpSpin .48s steps(4) infinite}
.clips.dp .h b{left:-22px;top:-20px;width:44px;height:40px;background-image:url("DPH")}
.clips.dp .s b{left:-14px;top:-14px;width:28px;height:28px;background-image:url("DPS")}
.clips.dp .b1 b,.clips.dp .b2 b,.clips.dp .b3 b,.clips.dp .b4 b{left:-10px;top:-10px;width:20px;height:20px}
.clips.dp .b1 b{background-image:url("DPB1")}
.clips.dp .b2 b{background-image:url("DPB2")}
.clips.dp .b3 b{background-image:url("DPB3")}
.clips.dp .b4 b{background-image:url("DPB4")}
@keyframes dpSpin{to{background-position:-96px 0}}
@keyframes dpFly{0%{transform:translate(0,0) scale(.4)}55%{transform:translate(var(--x),var(--y)) scale(1)}100%{transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 60px)) scale(1)}}
@keyframes dpBlink{0%{opacity:0}6%{opacity:1}70%{opacity:0}76%{opacity:1}82%{opacity:0}88%{opacity:1}94%,100%{opacity:0}}
@media (prefers-reduced-motion:reduce){.dp .dps,.dp .dpc,.dp .dpm0,.dp .dpm1,.dp .dpm2,.dp .dpk0,.dp .dpk1,.dp .dpk2{animation:none}.dp .dps,.dp .dpk0,.dp .dpk1,.dp .dpk2{display:none}
  .pshadow.dp{animation:none}.clips.dp{display:none}}
'''.replace('DPC', dp_strip_uri([dp_coin_frames()[i] for i in (0, 1, 2, 1)], (-3, -4, 6, 8), 4)).replace('DPH', dp_sprite_uri(dp_heart(), 4)) \
   .replace('DPS', dp_sprite_uri(DP_SPARK[2], 4)).replace('DPB1', dp_sprite_uri(dp_block(DP_BLUE, DP_NAVY), 4)) \
   .replace('DPB2', dp_sprite_uri(dp_block(DP_GREEN, '#008751'), 4)).replace('DPB3', dp_sprite_uri(dp_block(DP_YEL, DP_ORG), 4)) \
   .replace('DPB4', dp_sprite_uri(dp_block(DP_PINK, DP_PLUM), 4))


# ---------- 花火の的中ボタン：花火でできたPUSH（まさちゃんの指定） ----------
HN_PINK, HN_GOLD, HN_CYAN, HN_ORANGE, HN_HOT = '#FF6FA8', '#FFC24A', '#6FE3FF', '#FF9F5A', '#FFF4D2'


def hn_path_points(d, step):
    """M・V・H・C（大文字）だけの道すじを、step ごとの点にする（字の線の上に 火の玉を ならべる）"""
    toks = re.findall(r'[MVHC]|-?\d+(?:\.\d+)?', d)
    i, cur, polys, poly = 0, (0.0, 0.0), [], []
    while i < len(toks):
        c = toks[i]; i += 1
        if c == 'M':
            if poly:
                polys.append(poly)
            cur = (float(toks[i]), float(toks[i + 1])); i += 2
            poly = [cur]
        elif c == 'V':
            cur = (cur[0], float(toks[i])); i += 1
            poly.append(cur)
        elif c == 'H':
            cur = (float(toks[i]), cur[1]); i += 1
            poly.append(cur)
        elif c == 'C':
            p = [cur] + [(float(toks[i + 2 * k]), float(toks[i + 2 * k + 1])) for k in range(3)]; i += 6
            for t in [j / 16 for j in range(1, 17)]:
                poly.append(tuple((1 - t) ** 3 * p[0][a] + 3 * (1 - t) ** 2 * t * p[1][a] + 3 * (1 - t) * t * t * p[2][a] + t ** 3 * p[3][a] for a in (0, 1)))
            cur = p[3]
    if poly:
        polys.append(poly)
    out = []
    for poly in polys:
        seg = [math.dist(a, b) for a, b in zip(poly, poly[1:])]
        L = sum(seg)
        n = max(1, round(L / step))
        for k in range(n + 1):
            s, acc = L * k / n, 0.0
            for (a, b), l in zip(zip(poly, poly[1:]), seg):
                if acc + l >= s - 1e-9:
                    t = (s - acc) / l if l else 0
                    out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                    break
                acc += l
    keep = []
    for p in out:                                      # 重なった点（つなぎ目）は1つに
        if all(math.dist(p, q) > step * .55 for q in keep):
            keep.append(p)
    return keep


def fireworks_face_svg(sfx=''):
    """PUSHの面（面 200×100・角の丸み22で切りぬく。文字の下）：夏の夜空（こい紺・小さい星・字のうしろに うすい光）に、
       仕掛け花火の「PUSH」（字の線にそって 金の火の玉がならぶ・3つの組で ぱちぱち またたく・.hn1〜3）。字の下から
       金の火の粉が しずくのように こぼれ落ちる（ナイアガラ・.hnn）。ふちに ピンク → 金の光の線。sfx：id のうしろにつける字"""
    K_, G_, F_, E_, N_ = (f'hnb{c}{sfx}' for c in 'KGFEN')
    rnd = random.Random(83)
    pts = [p for d in NN_LETTERS for p in hn_path_points(d, 4.4)]
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="22"/></clipPath>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B1029"/><stop offset=".7" stop-color="#16204D"/>'
            '<stop offset="1" stop-color="#232B5E"/></linearGradient>'
            f'<radialGradient id="{N_}" cx=".5" cy=".5" r=".6"><stop offset="0" stop-color="{HN_PINK}" stop-opacity=".28"/><stop offset=".6" stop-color="{HN_GOLD}" stop-opacity=".08"/>'
            f'<stop offset="1" stop-color="{HN_GOLD}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{E_}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{HN_PINK}"/><stop offset="1" stop-color="{HN_GOLD}"/></linearGradient>'
            f'<filter id="{F_}" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>')
    stars = ''.join(f'<circle cx="{rnd.uniform(6, 194):.1f}" cy="{rnd.uniform(5, 95):.1f}" r="{rnd.choice((.5, .6, .8)):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(.3, .65):.2f}"/>'
                    for _ in range(18))
    glow = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8"/>' for x, y in pts)
    groups = ['', '', '']
    for i, (x, y) in enumerate(pts):
        groups[(i * 7 + int(x)) % 3] += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.45 + (i % 3) * .2:.2f}"/>'
    cores = ''.join(f'<g class="hn{k + 1}" fill="{HN_HOT}">{g}</g>' for k, g in enumerate(groups))
    drops = ''
    bottoms = [(x, y) for x, y in pts if y > 66]
    for k, (x, y) in enumerate(rnd.sample(bottoms, 11)):
        drops += (f'<g transform="translate({x:.1f} {y + 1:.1f})"><path class="hnn" d="M0 0V5" stroke="{HN_GOLD}" stroke-width="1.6" stroke-linecap="round" '
                  f'style="animation-duration:{rnd.uniform(.9, 1.4):.2f}s;animation-delay:{-rnd.uniform(0, 1.4):.2f}s"/></g>')
    body = (f'<rect width="200" height="100" fill="url(#{G_})"/>{stars}<rect width="200" height="100" fill="url(#{N_})"/>'
            f'<g fill="{HN_GOLD}" opacity=".9" filter="url(#{F_})">{glow}</g><g fill="{HN_PINK}" opacity=".35" filter="url(#{F_})">{glow}</g>'
            f'{cores}{drops}'
            f'<rect x="1.5" y="1.5" width="197" height="97" rx="20.5" fill="none" stroke="url(#{E_})" stroke-width="2.4" opacity=".9"/>'
            '<path d="M18 9C50 4 110 3 168 8" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" opacity=".09" fill="none"/>')
    return (f'<i class="hnf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def hn_mini_burst(col, n=12, r=15):
    """小さな花火（光の点が まるく ならぶ）"""
    out = ''
    for k in range(n):
        a = k / n * 2 * math.pi
        for j, f in enumerate((.45, .75, 1.0)):
            out += f'<circle cx="{math.cos(a) * r * f:.1f}" cy="{math.sin(a) * r * f + f * f * 2:.1f}" r="{.9 + j * .35:.2f}"/>'
    return f'<g fill="{col}">{out}</g><circle r="2.2" fill="#FFFFFF"/>'


def fireworks_decor_svg(sfx=''):
    """PUSHのまわり：左上・右上・左下・右下に 小さな花火（ピンク・金・水色・オレンジ）が かわるがわる ぱっと開いて消える"""
    F_ = f'hnbD{sfx}'
    spots = [(-26, -20, HN_PINK, 0), (226, -16, HN_GOLD, -.65), (232, 112, HN_CYAN, -1.3), (-30, 110, HN_ORANGE, -1.95)]
    out = ''
    for x, y, col, dl in spots:
        out += (f'<g transform="translate({x} {y})"><g class="hnp" style="animation-delay:{dl}s">'
                f'<g filter="url(#{F_})" opacity=".8">{hn_mini_burst(col)}</g>{hn_mini_burst(col)}</g></g>')
    return (f'<i class="hnd" aria-hidden="true"><svg viewBox="-44 -40 288 180" width="288" height="180"><defs>'
            f'<filter id="{F_}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2"/></filter></defs>{out}</svg></i>')


def fireworks_push_svg(sfx=''):
    return fireworks_face_svg(sfx) + fireworks_decor_svg(sfx)


def fireworks_burst(seed=59):
    """押した瞬間に、大きな花火：金・ピンク・水色の光のすじが まるく3重に開いて、下へたれながら ぱちぱち消える。まん中に光の輪"""
    rnd = random.Random(seed)
    out = ''
    for ring, (n, dist, col, z) in enumerate(((16, 170, HN_GOLD, 18), (13, 122, HN_PINK, 15), (10, 78, HN_CYAN, 12))):
        for i in range(n):
            a = (i + ring * .37) / n * 2 * math.pi + rnd.uniform(-.06, .06)
            d = dist * rnd.uniform(.88, 1.06)
            x, y = math.cos(a) * d * 1.12, math.sin(a) * d * .9 - 18
            out += (f'<i class="hs" style="--c:{col};--x:{x:.0f}px;--y:{y:.0f}px;--r:{math.degrees(a) + 90:.0f}deg;--z:{z}px;'
                    f'--d:{ring * .05 + rnd.uniform(0, .05):.2f}s"></i>')
    for k in range(2):
        out += f'<i class="hr" style="--c:{(HN_GOLD, HN_PINK)[k]};--z:{(64, 40)[k]}px;--d:{k * .08:.2f}s"></i>'
    return f'<div class="clips hn" aria-hidden="true">{out}</div>'


HN_CSS = r'''
/* ---------- 花火の的中ボタン：花火でできたPUSH（まさちゃんの指定） ----------
   面は夏の夜空（こい紺・小さい星・字のうしろに うすいピンクの光）。まん中に 仕掛け花火の「PUSH」：字の線にそって 金の火の玉がならび、
   3つの組で ぱちぱち またたく（0.9秒・ずらして）。字の下から 金の火の粉が しずくのように こぼれ落ちる（ナイアガラ）。ふちに ピンク → 金の光の線。
   ボタンの字は見えないようにして 火の玉の字を見せる（読み上げは「PUSH」のまま）。紺のふち・こい紺のふち・ピンクの光。
   まわりの4か所で 小さな花火が かわるがわる ぱっと開く（2.6秒）。上下の動きは的中と同じ。
   押すと ボタンがはじけて（強く光らせない）、大きな花火：金・ピンク・水色の光のすじが まるく3重に開いて、下へたれながら ぱちぱち消える */
.hn{--pr:22px;--pushA:#FF6FA8;--pushB:#0B1029;--pushC:#FFC24A;--rim:#1B2457;--rimD:#0B1029;
  --pushFace:linear-gradient(180deg,#0B1029,#232B5E)}
.push.hn{box-shadow:0 0 0 7px var(--rim),0 0 0 11px var(--rimD),0 9px 0 11px #070B1E,0 0 28px 12px rgba(255,111,168,.32),0 22px 34px rgba(0,0,0,.5)}
.push.hn span{color:transparent;text-shadow:none}
.push.hn::after{border-color:rgba(255,212,94,.9)}
.hn .hnf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:22px;overflow:hidden;pointer-events:none;font-style:normal}
.hn .hnf svg{display:block;width:200px;height:100px}
.hn .hnd{position:absolute;left:-44px;top:-40px;width:288px;height:180px;pointer-events:none;z-index:3;font-style:normal}
.hn .hnd svg{display:block;width:288px;height:180px;overflow:visible}
.hn .hn1,.hn .hn2,.hn .hn3{animation:hnTw .9s ease-in-out infinite}
.hn .hn2{animation-delay:-.3s}
.hn .hn3{animation-delay:-.6s}
@keyframes hnTw{0%,100%{opacity:1}50%{opacity:.45}}
.hn .hnn{transform-box:view-box;transform-origin:0 0;animation:hnDrop 1.1s linear infinite}
@keyframes hnDrop{0%{transform:translateY(0);opacity:0}15%{opacity:1}100%{transform:translateY(17px);opacity:0}}
.hn .hnp{transform-box:view-box;transform-origin:0 0;opacity:0;animation:hnPop 2.6s ease-out infinite}
@keyframes hnPop{0%{opacity:0;transform:scale(.2)}8%{opacity:1}30%{opacity:1;transform:scale(1)}55%{opacity:0;transform:scale(1.12) translateY(3px)}100%{opacity:0;transform:scale(1.12) translateY(3px)}}
.tap.hn{font-family:"Potta One",sans-serif;background:linear-gradient(90deg,#FF6FA8,#FFD45E);-webkit-background-clip:text;background-clip:text;color:transparent}
.pressed.hn{border-radius:22px;box-shadow:0 0 0 7px var(--rim),0 0 0 11px var(--rimD),0 9px 0 11px #070B1E,0 0 28px 12px rgba(255,111,168,.32);animation-name:hnPress}
@keyframes hnPress{0%{transform:scale(1)}35%{transform:scale(.86);filter:brightness(1.25)}100%{transform:scale(1.7);opacity:0;filter:brightness(1.4)}}   /* 強く光らせない */
.clips.hn{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.hn i{position:absolute;opacity:0}
.clips.hn .hs{left:-1.5px;top:calc(var(--z) / -2);width:3px;height:var(--z);border-radius:2px;
  background:linear-gradient(180deg,#FFFFFF 0,var(--c) 30%,transparent 100%);filter:drop-shadow(0 0 3px var(--c));
  animation:hnFly 1.4s cubic-bezier(.12,.75,.3,1) var(--d) both,hnSp 1.4s step-end var(--d) both}
@keyframes hnFly{0%{transform:translate(0,0) rotate(var(--r)) scale(.3)}50%{transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{transform:translate(calc(var(--x) * 1.08),calc(var(--y) + 44px)) rotate(var(--r)) scale(.7)}}
@keyframes hnSp{0%{opacity:0}5%{opacity:1}66%{opacity:.4}70%{opacity:1}76%{opacity:.4}82%{opacity:.9}88%{opacity:.3}94%,100%{opacity:0}}
.clips.hn .hr{left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);border-radius:50%;border:2px solid var(--c);
  box-shadow:0 0 10px var(--c);animation:hnRing .7s ease-out var(--d) both}
@keyframes hnRing{0%{opacity:.9;transform:scale(.2)}100%{opacity:0;transform:scale(2.6)}}
@media (prefers-reduced-motion:reduce){.hn .hn1,.hn .hn2,.hn .hn3,.hn .hnn,.hn .hnp{animation:none}.hn .hnn,.hn .hnp{display:none}.clips.hn{display:none}}
'''


# ---------- 子供向けの的中ボタン：毛糸でできたPUSH（まさちゃんの指定） ----------
KE_BR = '#8A5A35'                                   # 縫い目・ふち（子供向けの壁紙と同じ）
KE_KNIT = ('#F8AFC4', '#EE95B0', '#FFDCE6')         # 面の 編み目（下の色・目・光）＝壁紙の毛糸玉のピンク
KE_YARN = ('#FFF8EC', '#DCC0A2', '#B4798D')         # 字の毛糸（色・より目・ふち）


def ke_polys(d, sx=1.0, cx=100.0):
    """M・V・H・C（大文字）だけの道すじを、字の線ごとの こまかい折れ線にする（x は cx を中心に sx 倍）"""
    toks = re.findall(r'[MVHC]|-?\d+(?:\.\d+)?', d)
    i, cur, polys, poly = 0, (0.0, 0.0), [], []
    while i < len(toks):
        c = toks[i]; i += 1
        if c == 'M':
            if poly:
                polys.append(poly)
            cur = (float(toks[i]), float(toks[i + 1])); i += 2
            poly = [cur]
        elif c in 'VH':
            nxt = (cur[0], float(toks[i])) if c == 'V' else (float(toks[i]), cur[1]); i += 1
            poly.append(nxt)
            cur = nxt
        elif c == 'C':
            p = [cur] + [(float(toks[i + 2 * k]), float(toks[i + 2 * k + 1])) for k in range(3)]; i += 6
            for t in [j / 24 for j in range(1, 25)]:
                poly.append(tuple((1 - t) ** 3 * p[0][a] + 3 * (1 - t) ** 2 * t * p[1][a] + 3 * (1 - t) * t * t * p[2][a] + t ** 3 * p[3][a] for a in (0, 1)))
            cur = p[3]
    if poly:
        polys.append(poly)
    return [[(cx + (x - cx) * sx, y) for x, y in pl] for pl in polys]


def ke_resample(pl, step):
    """折れ線を step ごとの点にする（点・向き）"""
    seg = [math.dist(a, b) for a, b in zip(pl, pl[1:])]
    L = sum(seg)
    n = max(1, round(L / step))
    out = []
    for k in range(n + 1):
        s, acc = L * k / n, 0.0
        for j, ((a, b), l) in enumerate(zip(zip(pl, pl[1:]), seg)):
            if acc + l >= s - 1e-9 or j == len(seg) - 1:
                t = min(1.0, (s - acc) / l) if l else 0
                out.append(((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / (l or 1), (b[1] - a[1]) / (l or 1))))
                break
            acc += l
    return out


def ke_strand(pl, w=7.4, step=2.9):
    """毛糸の1本：ふち → 毛糸の色 → ふくらみの光 → より目（ななめの すじ）"""
    col, twist, line = KE_YARN
    d = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pl)
    hw = w / 2
    marks = ''
    pts = ke_resample(pl, step)
    for k, ((x, y), (tx, ty)) in enumerate(pts):
        if k == 0 or k == len(pts) - 1:
            continue
        nx, ny = -ty, tx
        a = (x + nx * hw * .86 - tx * 1.7, y + ny * hw * .86 - ty * 1.7)
        b = (x - nx * hw * .86 + tx * 1.7, y - ny * hw * .86 + ty * 1.7)
        marks += f'M{a[0]:.2f} {a[1]:.2f}L{b[0]:.2f} {b[1]:.2f}'
    return (f'<path d="{d}" stroke="{line}" stroke-width="{w + 2.4:.1f}"/>'
            f'<path d="{d}" stroke="{col}" stroke-width="{w:.1f}"/>'
            f'<path d="{d}" stroke="#FFFFFF" stroke-width="{w * .34:.2f}" opacity=".55" transform="translate(-.7 -.9)"/>'
            f'<path d="{marks}" stroke="{twist}" stroke-width="1.05"/>')


def keito_face_svg(sfx=''):
    """PUSHの面（面 200×100・角の丸み24で切りぬく）：ピンクの毛糸で編んだ面（編み目・上に つや・下は少し こく）に、
       クリーム色の太い毛糸で書いた「PUSH」（より目のある1本の毛糸・字ごとに ぴょこんと はねる .kel）。
       ふちの内がわに 茶色の縫い目（ぐるっと すすむ .kew）。sfx：id のうしろにつける字"""
    K_, P_, G_ = (f'ke{c}{sfx}' for c in 'KPG')
    k0, k1, k2 = KE_KNIT
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="24"/></clipPath>'
            f'<pattern id="{P_}" width="10" height="8.5" patternUnits="userSpaceOnUse">'
            f'<ellipse cx="2.6" cy="4.25" rx="2.1" ry="4" transform="rotate(-30 2.6 4.25)" fill="{k1}"/>'
            f'<ellipse cx="7.4" cy="4.25" rx="2.1" ry="4" transform="rotate(30 7.4 4.25)" fill="{k1}"/>'
            f'<path d="M1.6 2 q1 1.4 1.4 3.4 M8.4 2 q-1 1.4 -1.4 3.4" stroke="{k2}" stroke-width=".85" fill="none" stroke-linecap="round"/></pattern>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".4"/><stop offset=".42" stop-color="#FFFFFF" stop-opacity="0"/>'
            f'<stop offset=".75" stop-color="#B4597A" stop-opacity="0"/><stop offset="1" stop-color="#B4597A" stop-opacity=".28"/></linearGradient></defs>')
    letters = ''
    for k, d in enumerate(NN_LETTERS):
        strands = ''.join(ke_strand(pl) for pl in ke_polys(d, 1.06, 102))
        letters += (f'<g class="kel" style="animation-delay:{k * .12:.2f}s"><g fill="none" stroke-linecap="round" stroke-linejoin="round">{strands}</g></g>')
    body = (f'<rect width="200" height="100" fill="{k0}"/><rect width="200" height="100" fill="url(#{P_})"/>'
            f'<rect width="200" height="100" fill="url(#{G_})"/>'
            f'<rect class="kew" x="7" y="7" width="186" height="86" rx="17" fill="none" stroke="{KE_BR}" stroke-width="1.5" stroke-dasharray="5 3.8" stroke-linecap="round" opacity=".8"/>'
            f'{letters}')
    return (f'<i class="kef" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def ke_star(r, fill='#FFD966'):
    pts = [(math.cos(math.radians(-90 + 36 * i)) * (r if i % 2 == 0 else r * .5), math.sin(math.radians(-90 + 36 * i)) * (r if i % 2 == 0 else r * .5)) for i in range(10)]
    d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
    di = 'M' + ' L'.join(f'{x * .7:.1f} {y * .7:.1f}' for x, y in pts) + 'Z'
    return (f'<path d="{d}" fill="{fill}" stroke="{KE_BR}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="{di}" fill="none" stroke="{KE_BR}" stroke-width="1" stroke-dasharray="2.4 2" stroke-linecap="round" opacity=".75"/>')


def ke_heart(s, fill='#F7A8C0'):
    p = lambda k: lambda x, y: f'{x * s * k:.1f} {y * s * k:.1f}'
    hd = lambda k: (f'M{p(k)(0, -.45)} C{p(k)(-.15, -1.05)} {p(k)(-1.05, -1.0)} {p(k)(-1.0, -.25)} C{p(k)(-.95, .3)} {p(k)(-.35, .62)} {p(k)(0, 1.0)} '
                    f'C{p(k)(.35, .62)} {p(k)(.95, .3)} {p(k)(1.0, -.25)} C{p(k)(1.05, -1.0)} {p(k)(.15, -1.05)} {p(k)(0, -.45)} Z')
    return (f'<path d="{hd(1)}" fill="{fill}" stroke="{KE_BR}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="{hd(.72)}" fill="none" stroke="{KE_BR}" stroke-width="1" stroke-dasharray="2.4 2" stroke-linecap="round" opacity=".75"/>')


def ke_button(r, fill='#9FD5C0', dark='#5E9C84'):
    holes = ''.join(f'<circle cx="{x * r * .3:.1f}" cy="{y * r * .3:.1f}" r="{r * .13:.2f}" fill="{dark}"/>' for x, y in ((-1, -1), (1, -1), (-1, 1), (1, 1)))
    c = r * .3
    return (f'<circle r="{r}" fill="{fill}" stroke="{dark}" stroke-width="1.6"/><circle r="{r * .72:.1f}" fill="none" stroke="{dark}" stroke-width="1" opacity=".6"/>'
            f'{holes}<path d="M{-c:.1f} {-c:.1f}L{c:.1f} {c:.1f}M{c:.1f} {-c:.1f}L{-c:.1f} {c:.1f}" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round"/>')


def ke_ball(r, fill='#A9DCF3', dark='#6FB4D8'):
    """毛糸玉（まん中が 0,0）"""
    out = f'<circle r="{r}" fill="{fill}" stroke="{KE_BR}" stroke-width="1.6"/>'
    for d in (f'M{-r * .8:.1f} {-r * .4:.1f} q{r * .8:.1f} {-r * .4:.1f} {r * 1.6:.1f} {r * .27:.1f}', f'M{-r * .93:.1f} {r * .13:.1f} q{r * .93:.1f} {-r * .53:.1f} {r * 1.8:.1f} {r * .13:.1f}',
              f'M{-r * .67:.1f} {r * .67:.1f} q{r * .67:.1f} {-r * .4:.1f} {r * 1.4:.1f} 0', f'M{-r * .27:.1f} {-r * .93:.1f} q{-r * .27:.1f} {r * .93:.1f} {r * .13:.1f} {r * 1.87:.1f}',
              f'M{r * .3:.1f} {-r * .9:.1f} q{r * .25:.1f} {r * .8:.1f} {-r * .1:.1f} {r * 1.75:.1f}'):
        out += f'<path d="{d}" fill="none" stroke="{dark}" stroke-width="1.5" stroke-linecap="round"/>'
    return out


def keito_decor_svg(sfx=''):
    """PUSHのまわり（.push の左上から -60,-50 に 320×200）：黄色いフェルトのふちに 茶色の縫い目・
       右下に 水色の毛糸玉と 編み棒2本（ゆらゆら .keb・糸のはしが のびる）・左上に フェルトの星（きらっ .kes）・
       左下に フェルトのハート（どきどき .keh）・右上に ボタン（ゆらゆら .keu）"""
    rim = (f'<rect x="-3.6" y="-3.6" width="207.2" height="107.2" rx="27.6" fill="none" stroke="{KE_BR}" stroke-width="1.3" '
           f'stroke-dasharray="4.2 3.2" stroke-linecap="round" opacity=".85"/>')
    needles = ''
    for (x0, y0, x1, y1, knob) in ((-8, 4, 34, -40, '#F7A8C0'), (0, 8, 44, -22, '#FFD966')):
        needles += (f'<path d="M{x0} {y0}L{x1} {y1}" stroke="{KE_BR}" stroke-width="5.4" stroke-linecap="round"/>'
                    f'<path d="M{x0} {y0}L{x1} {y1}" stroke="#E2B27A" stroke-width="3.2" stroke-linecap="round"/>'
                    f'<circle cx="{x1}" cy="{y1}" r="4.6" fill="{knob}" stroke="{KE_BR}" stroke-width="1.4"/>')
    tail = f'<path d="M-15 8 C-30 18 -36 4 -48 12 C-56 17 -60 26 -70 24" fill="none" stroke="{KE_BR}" stroke-width="4.4" stroke-linecap="round"/>' \
           f'<path d="M-15 8 C-30 18 -36 4 -48 12 C-56 17 -60 26 -70 24" fill="none" stroke="#A9DCF3" stroke-width="2.4" stroke-linecap="round"/>'
    ball = (f'<g transform="translate(198 98)"><g class="keb">{tail}{needles}{ke_ball(17)}</g></g>')
    star = f'<g transform="translate(-16 -12)"><g class="kes">{ke_star(14)}</g></g>'
    heart = f'<g transform="translate(-16 90)"><g class="keh">{ke_heart(10)}</g></g>'
    btn = f'<g transform="translate(214 -12)"><g class="keu">{ke_button(11)}</g></g>'
    return (f'<i class="ked" aria-hidden="true"><svg viewBox="-60 -50 320 200" width="320" height="200">'
            f'{rim}{star}{heart}{btn}{ball}</svg></i>')


def keito_push_svg(sfx=''):
    return keito_face_svg(sfx) + keito_decor_svg(sfx)


def ke_uri(svg):
    return 'data:image/svg+xml,' + quote(svg, safe='')


KE_POMS = (('#F7A8C0', '#D9799A'), ('#FFD966', '#D9A93A'), ('#A9DCF3', '#6FB4D8'), ('#B6E8D1', '#6FBF9C'), ('#F6B27A', '#E8843F'))


def ke_pom_uri(col, dark):
    """ぽんぽん（毛糸のボール・ふわふわのふち）"""
    fuzz = ''.join(f'<path d="M{math.cos(a) * 5.2:.1f} {math.sin(a) * 5.2:.1f}L{math.cos(a) * 9.2:.1f} {math.sin(a) * 9.2:.1f}"/>'
                   for a in [k / 22 * 2 * math.pi for k in range(22)])
    return ke_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><g stroke='{col}' stroke-width='1.8' stroke-linecap='round'>{fuzz}</g>"
                  f"<circle r='6.4' fill='{col}'/><path d='M-3.6 -2 q3.6 -2.4 7.2 0 M-4 1.6 q4 -2.4 8 0' stroke='{dark}' stroke-width='1' fill='none' stroke-linecap='round'/></svg>")


def ke_item_uri(inner, vb='-12 -12 24 24'):
    return ke_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{vb}'>{inner}</svg>".replace('"', "'"))


def keito_burst(n=26, seed=61):
    """押した瞬間に、毛糸のぽんぽん（5色）・フェルトのハートと星・ボタン・毛糸のきれはしが ぽんっと広がる。まん中に 縫い目の輪"""
    rnd = random.Random(seed)
    kinds = ['p0', 'ht', 'p1', 'st', 'p2', 'bt', 'p3', 'cu', 'p4', 'ht', 'p1', 'st', 'p0']
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 170)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        k = kinds[i % len(kinds)]
        z = rnd.uniform(18, 24) if k[0] == 'p' else rnd.uniform(20, 26) if k in ('ht', 'st') else rnd.uniform(16, 20) if k == 'bt' else rnd.uniform(22, 28)
        out += (f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(90, 240):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    out += '<i class="kr"></i>'
    return f'<div class="clips ke" aria-hidden="true">{out}</div>'


KE_CSS = r'''
/* ---------- 子供向けの的中ボタン：毛糸でできたPUSH（まさちゃんの指定） ----------
   面は ピンクの毛糸で編んだ布（編み目・上に つや・下は少し こく）。まん中に クリーム色の太い毛糸で書いた「PUSH」
   （より目のある1本の毛糸・ネオンと同じ字の線を少し横に広げた形。字ごとに ぴょこんと はねる 1.8秒）。ふちの内がわに 茶色の縫い目が ぐるっと すすむ。
   黄色いフェルトのふち（茶色の縫い目）・茶色のふち・こい茶の厚み。右下に 水色の毛糸玉と編み棒（ゆらゆら）・左上に フェルトの星（きらっ）・
   左下に フェルトのハート（どきどき）・右上に ボタン（ゆらゆら）。ボタンの字は見えないようにして 毛糸の字を見せる（読み上げは「PUSH」のまま）。
   上下の動きは的中と同じ。押すと ボタンが むにゅっと つぶれて はじけ（強く光らせない）、毛糸のぽんぽん・ハート・星・ボタン・毛糸のきれはしが広がる */
.ke{--pr:24px;--pushA:#F8AFC4;--pushB:#B4597A;--pushC:#FFDCE6;--rim:#FFE58A;--rimD:#B88A5A;
  --pushFace:linear-gradient(180deg,#FFDCE6,#F8AFC4 45%,#EE95B0)}
.push.ke{box-shadow:inset 0 2px 0 rgba(255,255,255,.5),0 0 0 7px var(--rim),0 0 0 10px var(--rimD),0 9px 0 10px #8A5A35,0 20px 30px rgba(60,30,10,.45)}
.push.ke span{color:transparent;text-shadow:none}
.push.ke::after{border-color:rgba(255,255,255,.95);border-style:dashed}
.ke .kef{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:24px;overflow:hidden;pointer-events:none;font-style:normal}
.ke .kef svg{display:block;width:200px;height:100px}
.ke .ked{position:absolute;left:-60px;top:-50px;width:320px;height:200px;pointer-events:none;z-index:3;font-style:normal}
.ke .ked svg{display:block;width:320px;height:200px;overflow:visible}
.ke .kel{animation:keHop 1.8s ease-in-out infinite}
@keyframes keHop{0%,24%,100%{transform:translateY(0)}10%{transform:translateY(-2.6px)}}
.ke .kew{animation:keSew 1.4s linear infinite}
@keyframes keSew{to{stroke-dashoffset:-8.8}}
.ke .keb,.ke .kes,.ke .keh,.ke .keu{transform-box:view-box;transform-origin:0 0}
.ke .keb{animation:keRock 2.2s ease-in-out infinite}
@keyframes keRock{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}
.ke .kes{animation:keTwk 1.6s ease-in-out infinite}
@keyframes keTwk{0%,100%{transform:scale(.86) rotate(-8deg)}50%{transform:scale(1.08) rotate(8deg)}}
.ke .keh{animation:keBeat 1.1s ease-in-out infinite}
@keyframes keBeat{0%,40%,100%{transform:scale(1)}15%{transform:scale(1.16)}28%{transform:scale(.96)}}
.ke .keu{animation:keSwing 2.6s ease-in-out infinite}
@keyframes keSwing{0%,100%{transform:rotate(-14deg)}50%{transform:rotate(14deg)}}
.tap.ke{font-family:"Mochiy Pop One",sans-serif;color:#FFE58A;text-shadow:0 2px 0 #8A5A35}
.pressed.ke{border-radius:24px;box-shadow:0 0 0 7px var(--rim),0 0 0 10px var(--rimD),0 9px 0 10px #8A5A35;animation-name:kePress}
@keyframes kePress{0%{transform:scale(1)}32%{transform:scale(1.06,.84)}100%{transform:scale(1.6);opacity:0}}   /* 強く光らせない */
.clips.ke{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.ke i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:keFly 1.35s cubic-bezier(.15,.7,.3,1) var(--d) both;background:center/contain no-repeat}
.clips.ke .p0{background-image:url("P0")}
.clips.ke .p1{background-image:url("P1")}
.clips.ke .p2{background-image:url("P2")}
.clips.ke .p3{background-image:url("P3")}
.clips.ke .p4{background-image:url("P4")}
.clips.ke .ht{background-image:url("HT")}
.clips.ke .st{background-image:url("ST")}
.clips.ke .bt{background-image:url("BT")}
.clips.ke .cu{background-image:url("CU")}
.clips.ke .kr{left:-62px;top:-62px;width:124px;height:124px;border-radius:50%;border:3px dashed #FFF3B8;animation:keRing .7s ease-out both}
@keyframes keFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.08),calc(var(--y) + 54px)) rotate(calc(var(--r) * 1.4)) scale(.7)}}
@keyframes keRing{0%{opacity:.95;transform:scale(.3)}100%{opacity:0;transform:scale(2.4)}}
@media (prefers-reduced-motion:reduce){.ke .kel,.ke .kew,.ke .keb,.ke .kes,.ke .keh,.ke .keu{animation:none}.clips.ke{display:none}}
'''
for _k, (_c, _d) in enumerate(KE_POMS):
    KE_CSS = KE_CSS.replace(f'"P{_k}"', f'"{ke_pom_uri(_c, _d)}"')
KE_CSS = (KE_CSS.replace('"HT"', '"' + ke_item_uri(ke_heart(9)) + '"')
          .replace('"ST"', '"' + ke_item_uri(ke_star(11)) + '"')
          .replace('"BT"', '"' + ke_item_uri(ke_button(10)) + '"')
          .replace('"CU"', '"' + ke_item_uri('<path d="M-10 4 C-7 -7 -2 7 1 -2 S7 3 10 -5" fill="none" stroke="#8A5A35" stroke-width="4.6" stroke-linecap="round"/>'
                                             '<path d="M-10 4 C-7 -7 -2 7 1 -2 S7 3 10 -5" fill="none" stroke="#F7A8C0" stroke-width="2.8" stroke-linecap="round"/>') + '"'))


# ---------- かわいいの的中ボタン：ハートでできたPUSH（まさちゃんの指定） ----------
KW_LINE = '#A8416F'                                  # ふち（かわいいの壁紙と同じ）
KW_PINKS = ('#FF6FA8', '#FF8DC0', '#FFB7D3', '#FF4F9A')


def kw_heart_d(x, y, s):
    """ハートの形（まん中 x,y・大きさ s＝はばの半分くらい。cute.py・art.py の heart と同じ形）"""
    p = lambda a, b: f'{x + a * s:.2f} {y + b * s:.2f}'
    return (f'M{p(0, -.45)}C{p(-.15, -1.05)} {p(-1.05, -1.0)} {p(-1.0, -.25)}C{p(-.95, .3)} {p(-.35, .62)} {p(0, 1.0)}'
            f'C{p(.35, .62)} {p(.95, .3)} {p(1.0, -.25)}C{p(1.05, -1.0)} {p(.15, -1.05)} {p(0, -.45)}Z')


def kw_letter_points(step=6.2):
    """「PUSH」の字の線（ネオンと同じ字の線を少し横に広げた形）に、step ごとに ならべる点"""
    pts = []
    for d in NN_LETTERS:
        for pl in ke_polys(d, 1.06, 102):
            for (x, y), _t in ke_resample(pl, step):
                if all(math.dist((x, y), q) > step * .6 for q in pts):
                    pts.append((x, y))
    return pts


def kawaii_face_svg(sfx=''):
    """PUSHの面（面 200×100・角の丸み26で切りぬく）：ピンクのグラデーション・白い小さなハートの もよう・上に つや。
       まん中に 白いハートを ならべて書いた「PUSH」（ハートが 左から右へ 波のように どきどき ふくらむ .kwb）。sfx：id のうしろにつける字"""
    K_, G_, P_ = (f'kw{c}{sfx}' for c in 'KGP')
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="26"/></clipPath>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFB3D4"/><stop offset=".45" stop-color="#FF7DB4"/>'
            f'<stop offset="1" stop-color="#F0508F"/></linearGradient>'
            f'<pattern id="{P_}" width="22" height="20" patternUnits="userSpaceOnUse">'
            f'<path d="{kw_heart_d(5.5, 5, 2.4)}" fill="#FFFFFF" opacity=".22"/><path d="{kw_heart_d(16.5, 15, 2.4)}" fill="#FFFFFF" opacity=".22"/></pattern></defs>')
    hearts = ''
    for x, y in kw_letter_points():
        hearts += (f'<path class="kwb" style="animation-delay:{(x - 20) / 160 * .7:.2f}s" d="{kw_heart_d(x, y + .4, 3.6)}" '
                   f'fill="#FFFFFF" stroke="#D63A84" stroke-width=".9" stroke-linejoin="round"/>')
    body = (f'<rect width="200" height="100" fill="url(#{G_})"/><rect width="200" height="100" fill="url(#{P_})"/>'
            '<ellipse cx="100" cy="8" rx="92" ry="22" fill="#FFFFFF" opacity=".28"/>'
            '<path d="M22 14 q30 -9 64 -6" stroke="#FFFFFF" stroke-width="3.6" stroke-linecap="round" fill="none" opacity=".55"/>'
            f'{hearts}')
    return (f'<i class="kwf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def kw_rim_points(gap=11.5, off=4.6, r=26):
    """白いふちの まん中の線（PUSH の外がわ off）に、gap ごとに ならべる点"""
    R = r + off
    x0, y0, x1, y1 = -off, -off, 200 + off, 100 + off
    segs = []                                             # 角の丸い四角の まわりを細かい点に
    for a0, cx, cy in ((180, x0 + R, y0 + R), (270, x1 - R, y0 + R), (0, x1 - R, y1 - R), (90, x0 + R, y1 - R)):
        for k in range(13):
            a = math.radians(a0 + 90 * k / 12)
            segs.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    segs.append(segs[0])
    return [p for p, _t in ke_resample(segs, gap)][:-1]


def kawaii_decor_svg(sfx=''):
    """PUSHのまわり（.push の左上から -60,-60 に 320×220）：白いふちに ピンクのハートを ぐるっと（2組が かわるがわる ちかっ .kwr）・
       上のまん中に 大きいリボン（ゆらゆら .kwo）・両がわから 小さいハートが ふわふわ のぼる（.kwu）"""
    rim = ''
    for k, (x, y) in enumerate(kw_rim_points()):
        rim += f'<path class="kwr{k % 2}" d="{kw_heart_d(x, y + .3, 2.5)}" fill="{KW_PINKS[k % 2 * 3]}"/>'
    bow = f'<g transform="translate(100 -4)"><g class="kwo">{cute_bow(0, 0, .95)}</g></g>'
    ups = ''
    for k, (x, y, s, col, dl) in enumerate(((-24, 70, 6.5, KW_PINKS[0], 0), (224, 64, 7, KW_PINKS[1], -.9), (-14, 40, 4.6, '#FFFFFF', -1.6), (214, 30, 5, KW_PINKS[2], -.4))):
        line = f' stroke="{KW_LINE}" stroke-width="1.2"' if col == '#FFFFFF' else ''
        ups += f'<g transform="translate({x} {y})"><path class="kwu" style="animation-delay:{dl}s" d="{kw_heart_d(0, 0, s)}" fill="{col}"{line}/></g>'
    return (f'<i class="kwd" aria-hidden="true"><svg viewBox="-60 -60 320 220" width="320" height="220">'
            f'{ups}{rim}{bow}</svg></i>')


def cute_bow(cx, cy, s):
    import cute
    return cute.bow(cx, cy, s)


def kawaii_push_svg(sfx=''):
    return kawaii_face_svg(sfx) + kawaii_decor_svg(sfx)


def kw_heart_uri(fill, line=None):
    st = f" stroke='{line}' stroke-width='1.4'" if line else ''
    return ke_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-12 -12 24 24'><path d='{kw_heart_d(0, 0, 10)}' fill='{fill}'{st}/>"
                  f"<path d='M-6 -4 q1.5 -3 5 -3' stroke='#FFFFFF' stroke-width='1.6' stroke-linecap='round' fill='none' opacity='.7'/></svg>")


def kawaii_burst(n=28, seed=67):
    """押した瞬間に、ハート（ピンク・こいピンク・うすピンク・赤・白）とキラキラが ぱっと広がる。まん中から ハートの形の輪が広がる"""
    rnd = random.Random(seed)
    kinds = ['h0', 'h1', 'h2', 'h3', 'h4', 'sp', 'h0', 'h3', 'h1', 'h4', 'h2', 'sp']
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 175)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        k = kinds[i % len(kinds)]
        z = rnd.uniform(9, 13) if k == 'sp' else rnd.uniform(16, 28)
        out += (f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(40, 160):.0f}deg;'
                f'--d:{rnd.uniform(0, .1):.2f}s"></i>')
    out += '<i class="kh"></i>'
    return f'<div class="clips kw" aria-hidden="true">{out}</div>'


KW_CSS = r'''
/* ---------- かわいいの的中ボタン：ハートでできたPUSH（まさちゃんの指定） ----------
   面は ピンクのグラデーション（白い小さなハートの もよう・上に つや）。まん中に 白いハートを ならべて書いた「PUSH」
   （ネオンと同じ字の線を少し横に広げた形。ハートが 左から右へ 波のように どきどき ふくらむ 1.6秒）。
   白いふち（ピンクのハートが ぐるっと ならんで、2組が かわるがわる ちかっ）・ピンクのふち・こいピンクの厚み。
   上のまん中に 大きいリボン（ゆらゆら）・両がわから 小さいハートが ふわふわ のぼる。ボタンの字は見えないようにして ハートの字を見せる（読み上げは「PUSH」のまま）。
   上下の動きは的中と同じ。押すと どきっと ふくらんで はじけ（強く光らせない）、ハートとキラキラが広がり、ハートの形の輪が広がる */
.kw{--pr:26px;--pushA:#FF7DB4;--pushB:#C2307A;--pushC:#FFB3D4;--rim:#FFFFFF;--rimD:#FF8DC0;
  --pushFace:linear-gradient(180deg,#FFB3D4,#FF7DB4 45%,#F0508F)}
.push.kw{box-shadow:inset 0 2px 0 rgba(255,255,255,.6),0 0 0 9px var(--rim),0 0 0 13px var(--rimD),0 9px 0 13px #C2307A,0 0 26px 14px rgba(255,125,180,.35),0 20px 30px rgba(120,20,70,.4)}
.push.kw span{color:transparent;text-shadow:none}
.push.kw::after{border-color:rgba(255,255,255,.95);border-style:dotted;border-width:4px}
.kw .kwf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:26px;overflow:hidden;pointer-events:none;font-style:normal}
.kw .kwf svg{display:block;width:200px;height:100px}
.kw .kwd{position:absolute;left:-60px;top:-60px;width:320px;height:220px;pointer-events:none;z-index:3;font-style:normal}
.kw .kwd svg{display:block;width:320px;height:220px;overflow:visible}
.kw .kwb{transform-box:fill-box;transform-origin:50% 55%;animation:kwBeat 1.6s ease-in-out infinite}
@keyframes kwBeat{0%,30%,100%{transform:scale(1)}12%{transform:scale(1.32)}22%{transform:scale(.94)}}
.kw .kwr1{animation:kwBlink 1.2s ease-in-out infinite}
.kw .kwr0{animation:kwBlink 1.2s ease-in-out -.6s infinite}
@keyframes kwBlink{0%,100%{opacity:1}50%{opacity:.35}}
.kw .kwo{transform-box:view-box;transform-origin:0 0;animation:kwSway 2s ease-in-out infinite}
@keyframes kwSway{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}
.kw .kwu{transform-box:fill-box;transform-origin:50% 50%;opacity:0;animation:kwUp 2.4s ease-out infinite}
@keyframes kwUp{0%{opacity:0;transform:translateY(8px) scale(.5) rotate(-12deg)}20%{opacity:1}70%{opacity:1}100%{opacity:0;transform:translateY(-34px) scale(1.05) rotate(12deg)}}
.tap.kw{font-family:"Hachi Maru Pop",sans-serif;color:#FFFFFF;text-shadow:0 2px 0 #D63A84,0 0 10px rgba(255,125,180,.8)}
.pressed.kw{border-radius:26px;box-shadow:0 0 0 9px var(--rim),0 0 0 13px var(--rimD),0 9px 0 13px #C2307A;animation-name:kwPress}
@keyframes kwPress{0%{transform:scale(1)}22%{transform:scale(1.1)}40%{transform:scale(.86)}100%{transform:scale(1.6);opacity:0}}   /* 強く光らせない */
.clips.kw{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.kw i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:kwFly 1.35s cubic-bezier(.15,.7,.3,1) var(--d) both;background:center/contain no-repeat}
.clips.kw .h0{background-image:url("H0")}
.clips.kw .h1{background-image:url("H1")}
.clips.kw .h2{background-image:url("H2")}
.clips.kw .h3{background-image:url("H3")}
.clips.kw .h4{background-image:url("H4")}
.clips.kw .sp{background-image:url("SP")}
.clips.kw .kh{left:-60px;top:-56px;width:120px;height:112px;background-image:url("RING");animation:kwRing .75s ease-out both}
@keyframes kwFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.08),calc(var(--y) + 50px)) rotate(calc(var(--r) * 1.3)) scale(.75)}}
@keyframes kwRing{0%{opacity:.95;transform:scale(.3)}100%{opacity:0;transform:scale(2.3)}}
@media (prefers-reduced-motion:reduce){.kw .kwb,.kw .kwr0,.kw .kwr1,.kw .kwo{animation:none}.kw .kwu{display:none}.clips.kw{display:none}}
'''
for _k, (_f, _l) in enumerate((('#FF6FA8', None), ('#FF4F9A', None), ('#FFB7D3', None), ('#F0306E', None), ('#FFFFFF', '#D63A84'))):
    KW_CSS = KW_CSS.replace(f'"H{_k}"', f'"{kw_heart_uri(_f, _l)}"')
KW_CSS = (KW_CSS.replace('"SP"', '"' + ke_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><path d='M0 -9.5 Q1.6 -1.6 9.5 0 Q1.6 1.6 0 9.5 Q-1.6 1.6 -9.5 0 Q-1.6 -1.6 0 -9.5Z' fill='#FFFFFF'/></svg>") + '"')
          .replace('"RING"', '"' + ke_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-12 -12 24 23'><path d='{kw_heart_d(0, 0, 10.5)}' fill='none' stroke='#FFFFFF' stroke-width='1.2'/></svg>") + '"'))


# ---------- 夕焼けの的中ボタン：夕日の映ったPUSH（まさちゃんの指定） ----------
SS_SUN = (100, 66, 30)          # 面の夕日：まん中と半径（面は 200×100・水平線は y=66。上半分だけ見える・字のすき間と上から のぞく）
SS_INK = '#2A1235'              # 鳥（壁紙の鳥と同じ色）


def ss_bird(x, y, s, w=1.3):
    """鳥（壁紙と同じ「へ」の字を2つ つなげた形）"""
    return (f'<path d="M{x - s:.1f} {y:.1f}Q{x - s * .5:.1f} {y - s * .6:.1f} {x:.1f} {y:.1f}Q{x + s * .5:.1f} {y - s * .6:.1f} {x + s:.1f} {y:.1f}" '
            f'fill="none" stroke="{SS_INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def sunset_face_svg(sfx=''):
    """PUSHの面に映った夕焼け（面 200×100 の角の丸み26で切りぬく。文字の下）：
       夕焼けの空（上は こい紫 → 赤紫 → だいだい → 水平線の近くは 金）・うすい雲の筋（ゆっくり流れる .sscl）・
       水平線に しずみかけの夕日（まわりの光が ふわっと ふくらむ .ssgl）・下は 夕日が映った水（夕日の下に 光の筋が ゆらゆら .ssrf）・
       空に 鳥が2羽（はばたく .ssbd）・上に つやの光・ときどき ななめに光がすっと通る（.sssh）。sfx：id のうしろにつける字"""
    sx, sy, sr = SS_SUN
    K_, S_, U_, H_, W_, G_, C_ = (f'ss{c}{sfx}' for c in 'KSUHWGC')
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="26"/></clipPath>'
            f'<clipPath id="{C_}"><rect width="200" height="{sy}"/></clipPath>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B1450"/><stop offset=".3" stop-color="#5E2A86"/>'
            '<stop offset=".56" stop-color="#B23D72"/><stop offset=".8" stop-color="#EE6A4A"/><stop offset="1" stop-color="#FFB25A"/></linearGradient>'
            f'<linearGradient id="{W_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6A2A55"/><stop offset=".45" stop-color="#3E1C4C"/>'
            '<stop offset="1" stop-color="#22102E"/></linearGradient>'
            f'<radialGradient id="{U_}" cx=".5" cy=".62" r=".6"><stop offset="0" stop-color="#FFF8DC"/><stop offset=".55" stop-color="#FFE39A"/>'
            '<stop offset="1" stop-color="#FFB45A"/></radialGradient>'
            f'<radialGradient id="{H_}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="74"><stop offset="0" stop-color="#FFD08A" stop-opacity=".75"/>'
            '<stop offset=".35" stop-color="#FFB46A" stop-opacity=".35"/><stop offset=".7" stop-color="#FF9A6A" stop-opacity=".12"/>'
            '<stop offset="1" stop-color="#FF9A6A" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".45"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    clouds = ''.join(f'<g class="sscl" style="animation-delay:{dl}s"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{c}" opacity="{o}"/></g>'
                     for x, y, w, h, c, o, dl in ((-6, 17, 86, 3, '#D8608E', .55, 0), (118, 27, 92, 2.6, '#E87A84', .5, -2.2),
                                                  (14, 39, 70, 2.4, '#F49072', .5, -4.1), (132, 47, 64, 2, '#FFB07A', .5, -1.3)))
    refl = ''
    for i, y in enumerate((69, 72.4, 75.8, 79.2, 82.6, 86, 89.4, 92.8)):
        w = 44 - i * 4.4
        ox = (1.6, -1.2, 2.0, -1.8, 1.0, -0.8, 1.4, -1.0)[i]
        refl += (f'<g transform="translate({sx + ox:.1f} {y})"><g class="ssrf" style="animation-delay:{-i * .27:.2f}s">'
                 f'<rect x="{-w / 2:.1f}" y="-.8" width="{w:.1f}" height="1.6" rx=".8" fill="#FFD48A" opacity="{.92 - i * .08:.2f}"/></g></g>')
    sparkle = ''.join(f'<g transform="translate({x} {y})"><g class="ssrf" style="animation-delay:{dl}s"><rect x="{-w / 2}" y="-.6" width="{w}" height="1.2" rx=".6" fill="#FFC27A" opacity=".55"/></g></g>'
                      for x, y, w, dl in ((52, 74, 12, -.5), (150, 77, 14, -1.1), (38, 86, 10, -1.6), (166, 90, 12, -.2)))
    body = (f'<rect width="200" height="{sy}" fill="url(#{S_})"/>'
            f'<g transform="translate({sx} {sy})"><g class="ssgl"><circle r="74" fill="url(#{H_})"/></g></g>'
            + clouds
            + f'<ellipse cx="{sx}" cy="{sy}" rx="120" ry="12" fill="#FFB25A" opacity=".35"/>'
            f'<g clip-path="url(#{C_})"><circle cx="{sx}" cy="{sy}" r="{sr + 5}" fill="#FFE39A" opacity=".35"/><circle cx="{sx}" cy="{sy}" r="{sr}" fill="url(#{U_})"/></g>'
            f'<rect y="{sy}" width="200" height="{100 - sy}" fill="url(#{W_})"/>'
            f'<rect y="{sy - .6}" width="200" height="1.2" fill="#FFD48A" opacity=".55"/>'
            + refl + sparkle
            + f'<g transform="translate(34 22)"><g class="ssbd">{ss_bird(0, 0, 5.4)}</g></g>'
            f'<g transform="translate(164 13)"><g class="ssbd" style="animation-delay:-.35s">{ss_bird(0, 0, 4.2, 1.1)}</g></g>'
            '<ellipse cx="100" cy="6" rx="86" ry="20" fill="#FFFFFF" opacity=".18"/>'
            f'<g class="sssh"><rect x="-60" y="-10" width="34" height="130" fill="url(#{G_})" transform="rotate(18)"/></g>'
            '<rect y="91" width="200" height="9" fill="#12081A" opacity=".22"/>')
    return (f'<i class="ssf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def sunset_decor_svg():
    """PUSHのまわり：右上を 鳥が3羽（くの字にならんで はばたきながら ゆっくり ただよう .ssgd）・左下に 夕日の光の きらっ（.sstw）"""
    birds = ''.join(f'<g transform="translate({x} {y})"><g class="ssbd" style="animation-delay:{dl}s">{ss_bird(0, 0, s, 1.6)}</g></g>'
                    for x, y, s, dl in ((196, -14, 7.5, 0), (214, -4, 6, -.3), (180, -2, 5.5, -.55)))
    glint = ''.join(f'<g transform="translate({x} {y})"><g class="sstw" style="animation-delay:{dl}s">'
                    f'<path d="M0 -{r}Q{r * .25:.2f} -{r * .25:.2f} {r} 0Q{r * .25:.2f} {r * .25:.2f} 0 {r}Q-{r * .25:.2f} {r * .25:.2f} -{r} 0Q-{r * .25:.2f} -{r * .25:.2f} 0 -{r}Z" fill="#FFE3B0"/></g></g>'
                    for x, y, r, dl in ((-8, 104, 7, 0), (10, 118, 4.5, -1.1)))
    return ('<i class="ssd" aria-hidden="true"><svg viewBox="-34 -30 268 160" width="268" height="160">'
            f'<g class="ssgd">{birds}</g>{glint}</svg></i>')


def sunset_push_svg(sfx=''):
    return sunset_face_svg(sfx) + sunset_decor_svg()


def ss_uri(svg):
    return 'data:image/svg+xml,' + svg.replace('<', '%3C').replace('>', '%3E').replace('#', '%23').replace('"', "'")


def sunset_burst(n=26, seed=29):
    """押した瞬間に、夕日の光の粒（だいだい・桃色・金）と きらっ・鳥が ぱっと広がる。まん中から 夕日の色の 光の輪が広がる"""
    rnd = random.Random(seed)
    kinds = ['o', 'p', 'g', 'o', 'b', 'p', 'g', 'o', 'p', 'b', 'g', 'o', 'p']
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 172)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        k = kinds[i % len(kinds)]
        z = dict(o=rnd.uniform(9, 14), p=rnd.uniform(7, 11), g=rnd.uniform(14, 20), b=rnd.uniform(18, 24))[k]
        r = 0 if k == 'b' else rnd.choice((-1, 1)) * rnd.uniform(40, 160)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{rnd.uniform(0, .1):.2f}s"></i>'
    out += '<i class="ring"></i>'
    return f'<div class="clips ss" aria-hidden="true">{out}</div>'


SS_CSS = r'''
/* ---------- 夕焼けの的中ボタン：夕日の映ったPUSH（まさちゃんの指定） ----------
   面に夕焼け：空（上は こい紫 → 赤紫 → だいだい → 水平線の近くは 金）・うすい雲の筋（ゆっくり流れる）・水平線に しずみかけの夕日（まわりの光が ふわっと ふくらむ）。
   下は 夕日が映った水：夕日の下に 光の筋が ゆらゆら（8本・下ほど短い）・まわりにも 小さな光。空に鳥が2羽（はばたく）。上に つやの光・ときどき ななめに光がすっと通る。
   クリーム色のふち・さんご色のふち・こい紫の厚み。白い「PUSH」に こい紫のふちと 夕日の色の光。右上を 鳥が3羽 ただよい、左下に 夕日の光が きらっ。
   上下の動きは的中と同じ。押すと ふわっと ふくらんで はじけ（強く光らせない）、夕日の光の粒・きらっ・鳥が広がり、夕日の色の 光の輪が広がる */
.ss{--pushA:#EE6A4A;--pushB:#3A1D5C;--pushC:#FFB25A;--rim:#FFEADA;--rimD:#F2886A;
  --pushFace:linear-gradient(180deg,#2B1450 0%,#5E2A86 20%,#B23D72 37%,#EE6A4A 53%,#FFB25A 66%,#6A2A55 66%,#22102E 100%)}
.push.ss{box-shadow:inset 0 2px 0 rgba(255,255,255,.5),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #3A1D5C,0 0 26px 10px rgba(255,150,90,.28),0 22px 34px rgba(40,10,40,.5)}
.push.ss span{color:#FFF8EE;text-shadow:0 3px 0 #3A1D5C,0 0 2px #3A1D5C,0 0 3px #3A1D5C,0 0 14px rgba(255,170,90,.85)}
.push.ss::after{border-color:rgba(255,200,140,.95)}
.ss .ssf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:26px;overflow:hidden;pointer-events:none;font-style:normal}
.ss .ssf svg{display:block;width:200px;height:100px}
.ss .ssd{position:absolute;left:-34px;top:-30px;width:268px;height:160px;pointer-events:none;z-index:3;font-style:normal}
.ss .ssd svg{display:block;width:268px;height:160px;overflow:visible}
.ss .ssgl,.ss .sscl,.ss .sssh,.ss .ssgd{transform-box:view-box;transform-origin:0 0}
.ss .ssgl{animation:ssGlow 2.8s ease-in-out infinite}
@keyframes ssGlow{0%,100%{opacity:.78;transform:scale(.94)}50%{opacity:1;transform:scale(1.05)}}
.ss .sscl{animation:ssDrift 6s ease-in-out infinite alternate}
@keyframes ssDrift{from{transform:translateX(-5px)}to{transform:translateX(5px)}}
.ss .ssrf{transform-box:fill-box;transform-origin:50% 50%;animation:ssRef 1.9s ease-in-out infinite}
@keyframes ssRef{0%,100%{transform:scaleX(1);opacity:1}50%{transform:scaleX(.62) translateX(2px);opacity:.55}}
.ss .ssbd{transform-box:fill-box;transform-origin:50% 100%;animation:ssFlap .7s ease-in-out infinite}
@keyframes ssFlap{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.35)}}
.ss .ssgd{animation:ssGlide 4.5s ease-in-out infinite alternate}
@keyframes ssGlide{from{transform:translate(-6px,2px)}to{transform:translate(6px,-3px)}}
.ss .sstw{transform-box:fill-box;transform-origin:50% 50%;animation:ssTw 2.2s ease-in-out infinite}
@keyframes ssTw{0%,100%{opacity:.15;transform:scale(.4)}50%{opacity:1;transform:scale(1)}}
.ss .sssh{animation:ssShine 5s ease-in-out infinite}
@keyframes ssShine{0%,55%{transform:translateX(0)}85%,100%{transform:translateX(300px)}}
.tap.ss{font-family:"Kaisei Opti",serif;font-weight:700;color:#FFD9A8;text-shadow:0 2px 0 #3A1D5C,0 0 10px rgba(255,150,90,.8)}
.pressed.ss{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #3A1D5C;animation-name:ssPress}
@keyframes ssPress{0%{transform:scale(1)}25%{transform:scale(1.08)}45%{transform:scale(.9)}100%{transform:scale(1.6);opacity:0}}   /* 強く光らせない */
.clips.ss{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.ss i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:ssFly 1.3s cubic-bezier(.15,.7,.3,1) var(--d) both;background:center/contain no-repeat}
.clips.ss .o{border-radius:50%;background:radial-gradient(circle at 40% 40%,#FFF4D6 0 22%,#FFB25A 55%,rgba(238,106,74,0) 72%)}
.clips.ss .p{border-radius:50%;background:radial-gradient(circle at 40% 40%,#FFE6EE 0 20%,#F2709A 58%,rgba(194,65,107,0) 74%)}
.clips.ss .g{background-image:url("SP")}
.clips.ss .b{background-image:url("BD")}
.clips.ss .ring{left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:5px solid rgba(255,178,90,.85);box-shadow:0 0 18px rgba(255,140,90,.6);animation:ssRing .8s ease-out both}
@keyframes ssFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 44px)) rotate(calc(var(--r) * 1.3)) scale(.7)}}
@keyframes ssRing{0%{opacity:.95;transform:scale(.3)}100%{opacity:0;transform:scale(2.2)}}
@media (prefers-reduced-motion:reduce){.ss .ssgl,.ss .sscl,.ss .ssrf,.ss .ssbd,.ss .ssgd,.ss .sstw,.ss .sssh{animation:none}.ss .sssh,.ss .sstw,.clips.ss{display:none}}
'''
SS_CSS = (SS_CSS.replace('"SP"', '"' + ss_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><path d='M0 -9.5Q2.4 -2.4 9.5 0Q2.4 2.4 0 9.5Q-2.4 2.4 -9.5 0Q-2.4 -2.4 0 -9.5Z' fill='#FFE3B0'/></svg>") + '"')
          .replace('"BD"', '"' + ss_uri(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-11 -7 22 10'><path d='M-9 0Q-4.5 -5.4 0 0Q4.5 -5.4 9 0' fill='none' stroke='{SS_INK}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>") + '"'))



NB_LAMPS = ((-16, -12, -1), (216, -12, 1))    # ナイターの的中ボタン：照明（ランプの まん中・向き：-1＝左の照明（右下を照らす）／1＝右の照明）


def night_face_svg(sfx=''):
    """PUSHの面に ナイターのコース（面 200×100 の角の丸み26で切りぬく。文字の下）：
       夜空（星が ちかっ .nbst）・スタンド（屋根のふちの光・観客の光の粒が ちらちら .nbcr）・白い柵・ダート（照明の光だまりが ふわっと .nbpl）・
       上に つやの光・ときどき ななめに光がすっと通る（.nbsh）。sfx：id のうしろにつける字"""
    K_, S_, D_, P_, G_ = (f'nb{c}{sfx}' for c in 'KSDPG')
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="26"/></clipPath>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#060A26"/><stop offset=".55" stop-color="#121A52"/>'
            '<stop offset="1" stop-color="#2E2C78"/></linearGradient>'
            f'<linearGradient id="{D_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3C2A34"/><stop offset=".45" stop-color="#5E4240"/>'
            '<stop offset="1" stop-color="#8E6248"/></linearGradient>'
            f'<radialGradient id="{P_}"><stop offset="0" stop-color="#FFE3A8" stop-opacity=".62"/><stop offset=".5" stop-color="#FFC870" stop-opacity=".26"/>'
            '<stop offset="1" stop-color="#FFC870" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".4"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    stars = ''.join(f'<g transform="translate({x} {y})"><g class="nbst" style="animation-delay:{dl}s"><circle r="{r}" fill="#EAF0FF"/></g></g>'
                    for x, y, r, dl in ((24, 12, 1.1, 0), (62, 7, .8, -.9), (138, 9, 1.0, -1.7), (176, 16, .9, -.4), (98, 20, .7, -2.3), (150, 27, .7, -1.2)))
    stand = 'M0 47Q100 38 200 47L200 63L0 63Z'
    rnd = random.Random(41)
    crowd = ''
    for i in range(46):
        x, y = rnd.uniform(4, 196), rnd.uniform(52, 61)
        c = rnd.choice(('#FFE7A8', '#FFFFFF', '#A8C8FF', '#FF9AC8', '#9CF0FF', '#FFE7A8'))
        tw = i % 5 == 0
        dot = f'<circle r="{rnd.uniform(.45, .8):.2f}" fill="{c}" opacity="{rnd.uniform(.6, .95):.2f}"/>'
        crowd += (f'<g transform="translate({x:.1f} {y:.1f})"><g class="nbcr" style="animation-delay:{-rnd.uniform(0, 2.4):.2f}s">{dot}</g></g>' if tw
                  else f'<g transform="translate({x:.1f} {y:.1f})">{dot}</g>')
    streaks = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{c}" opacity="{o}"/>'
                      for x, y, w, h, c, o in ((8, 72, 34, 1.2, '#B08C70', .35), (120, 70, 42, 1.1, '#B08C70', .3), (60, 80, 52, 1.6, '#2A1A22', .25),
                                               (150, 86, 40, 1.8, '#B08C70', .3), (14, 92, 46, 2, '#2A1A22', .22), (96, 95, 60, 2, '#B08C70', .25)))
    pools = ''.join(f'<g transform="translate({x} 84)"><g class="nbpl" style="animation-delay:{dl}s"><ellipse rx="48" ry="17" fill="url(#{P_})"/></g></g>'
                    for x, dl in ((52, 0), (148, -1.6)))
    body = (f'<rect width="200" height="64" fill="url(#{S_})"/>' + stars
            + '<ellipse cx="100" cy="47" rx="120" ry="10" fill="#4E3A90" opacity=".45"/>'
            f'<path d="{stand}" fill="#191846"/><path d="M0 47Q100 38 200 47" fill="none" stroke="#A9B8FF" stroke-width=".8" opacity=".7"/>'
            + crowd
            + f'<rect y="63" width="200" height="37" fill="url(#{D_})"/>' + streaks + pools
            + '<rect y="61.6" width="200" height="1.6" fill="#E8ECFF"/>'
            + ''.join(f'<rect x="{x:.1f}" y="61.6" width=".8" height="4" fill="#E8ECFF"/>' for x in range(6, 200, 13))
            + '<ellipse cx="100" cy="5" rx="86" ry="18" fill="#FFFFFF" opacity=".14"/>'
            f'<g class="nbsh"><rect x="-60" y="-10" width="34" height="130" fill="url(#{G_})" transform="rotate(18)"/></g>'
            '<rect y="91" width="200" height="9" fill="#0A0612" opacity=".25"/>')
    return (f'<i class="nbf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def night_decor_svg(sfx=''):
    """PUSHのまわり：上の左右に 照明（柱・ランプの粒・光のにじみ・十字と横に長い光 .nblp）。照明から ボタンへ 光の すじ（.nbbm・ゆっくり ゆれる）"""
    B_, L_ = f'nbB{sfx}', f'nbL{sfx}'
    defs = (f'<defs><linearGradient id="{B_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF4D6" stop-opacity=".5"/>'
            '<stop offset=".55" stop-color="#FFE0A0" stop-opacity=".16"/><stop offset="1" stop-color="#FFE0A0" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="{L_}"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".25" stop-color="#FFF0C8" stop-opacity=".85"/>'
            '<stop offset=".6" stop-color="#FFC870" stop-opacity=".28"/><stop offset="1" stop-color="#FFC870" stop-opacity="0"/></radialGradient></defs>')
    out = defs
    for x, y, d in NB_LAMPS:
        ang = 33 if d < 0 else 147                                   # 光のすじの向き（ボタンのまん中の少し下へ）
        out += (f'<g transform="translate({x} {y})"><g class="nbbm{"" if d < 0 else " r"}">'
                f'<path d="M0 -5L150 -30L150 30L0 5Z" fill="url(#{B_})" transform="rotate({ang})"/></g></g>')
    for x, y, d in NB_LAMPS:
        pole = (f'<rect x="{x - 1.6}" y="{y + 6}" width="3.2" height="62" fill="#0C0D28"/>'
                + ''.join(f'<path d="M{x - 2.5} {y + yb}L{x + 2.5} {y + yb + 5}" stroke="#2A2C58" stroke-width="1"/>' for yb in range(14, 64, 10)))
        lamps = ''.join(f'<circle cx="{x - 8 + j * 4}" cy="{y - 3.5 + i * 3.5}" r="1.5" fill="#FFF8E4"/>' for i in range(3) for j in range(5))
        out += (pole + f'<rect x="{x - 10.5}" y="{y - 6}" width="21" height="12" rx="1.5" fill="#1A1C40"/>' + lamps
                + f'<g transform="translate({x} {y})"><g class="nblp" style="animation-delay:{0 if d < 0 else -1.3}s">'
                '<circle r="26" fill="url(#' + L_ + ')"/>'
                '<path d="M-58 0H58M0 -16V16M-9 -9L9 9M-9 9L9 -9" stroke="#FFF6DE" stroke-width="1.4" stroke-linecap="round" opacity=".85"/>'
                '<path d="M-58 0H58" stroke="#FFD48A" stroke-width="4" stroke-linecap="round" opacity=".25"/></g></g>')
    return f'<i class="nbd" aria-hidden="true"><svg viewBox="-34 -30 268 160" width="268" height="160">{out}</svg></i>'


def night_push_svg(sfx=''):
    return night_face_svg(sfx) + night_decor_svg(sfx)


def night_burst(n=26, seed=31):
    """押した瞬間に、照明の光の粒（あたたかい白・アンバー・青白）と きらっ が ぱっと広がる。まん中から アンバーの 光の輪が広がる"""
    rnd = random.Random(seed)
    kinds = ['w', 'a', 's', 'c', 'w', 'a', 's', 'w', 'c', 'a', 's']
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 172)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        k = kinds[i % len(kinds)]
        z = dict(w=rnd.uniform(10, 15), a=rnd.uniform(8, 12), c=rnd.uniform(7, 10), s=rnd.uniform(14, 20))[k]
        r = rnd.choice((-1, 1)) * rnd.uniform(40, 160) if k == 's' else 0
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{rnd.uniform(0, .1):.2f}s"></i>'
    out += '<i class="ring"></i>'
    return f'<div class="clips nb" aria-hidden="true">{out}</div>'


NB_CSS = r'''
/* ---------- ナイターの的中ボタン：ナイター照明に照らされたPUSH（まさちゃんの指定） ----------
   面に ナイターのコース：夜空（星が ちかっ）・スタンド（屋根のふちの光・観客の光の粒が ちらちら）・白い柵・ダート（照明の光だまりが ふわっと）。
   上の左右に 照明（柱・ランプの粒・光のにじみ・十字と横に長い光）があって、ボタンへ 光の すじが ゆっくり ゆれながら当たる。上に つやの光・ときどき ななめに光がすっと通る。
   あたたかい白のふち・アンバーのふち・こい紺の厚み・まわりに アンバーの光。白い「PUSH」に こい紺のふちと 照明の光。
   上下の動きは的中と同じ。押すと ふわっと ふくらんで はじけ（強く光らせない）、照明の光の粒と きらっ が広がり、アンバーの 光の輪が広がる */
.nb{--pushA:#FFB020;--pushB:#0E1324;--pushC:#FFD27A;--rim:#FFF3D6;--rimD:#FFB020;
  --pushFace:linear-gradient(180deg,#060A26 0%,#121A52 34%,#2E2C78 47%,#191846 50%,#191846 62%,#3C2A34 64%,#5E4240 80%,#8E6248 100%)}
.push.nb{box-shadow:inset 0 2px 0 rgba(255,255,255,.45),0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #070A16,0 0 30px 12px rgba(255,190,90,.30),0 22px 34px rgba(0,0,0,.55)}
.push.nb span{color:#FFFFFF;text-shadow:0 3px 0 #0E1324,0 0 2px #0E1324,0 0 3px #0E1324,0 0 16px rgba(255,214,140,.9)}
.push.nb::after{border-color:rgba(255,214,140,.95)}
.nb .nbf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:26px;overflow:hidden;pointer-events:none;font-style:normal}
.nb .nbf svg{display:block;width:200px;height:100px}
.nb .nbd{position:absolute;left:-34px;top:-30px;width:268px;height:160px;pointer-events:none;z-index:3;font-style:normal}
.nb .nbd svg{display:block;width:268px;height:160px;overflow:visible}
.nb .nbsh{transform-box:view-box;transform-origin:0 0;animation:nbShine 5s ease-in-out infinite}
@keyframes nbShine{0%,55%{transform:translateX(0)}85%,100%{transform:translateX(300px)}}
.nb .nbst{transform-box:fill-box;transform-origin:50% 50%;animation:nbTw 2.4s ease-in-out infinite}
@keyframes nbTw{0%,100%{opacity:.3;transform:scale(.6)}50%{opacity:1;transform:scale(1.15)}}
.nb .nbcr{animation:nbCrowd 1.9s ease-in-out infinite}
@keyframes nbCrowd{0%,100%{opacity:.35}50%{opacity:1}}
.nb .nbpl{transform-box:fill-box;transform-origin:50% 50%;animation:nbPool 3.4s ease-in-out infinite}
@keyframes nbPool{0%,100%{opacity:.8;transform:scale(.94)}50%{opacity:1;transform:scale(1.05)}}
.nb .nblp{transform-box:fill-box;transform-origin:50% 50%;animation:nbLamp 2.6s ease-in-out infinite}
@keyframes nbLamp{0%,100%{opacity:.82;transform:scale(.95)}50%{opacity:1;transform:scale(1.04)}}
.nb .nbbm{transform-box:view-box;transform-origin:0 0;animation:nbBeam 3.6s ease-in-out infinite alternate}
.nb .nbbm.r{animation-delay:-1.8s}
@keyframes nbBeam{from{transform:rotate(-4deg)}to{transform:rotate(4deg)}}
.tap.nb{font-family:"RocknRoll One",sans-serif;font-weight:400;color:#FFD27A;text-shadow:0 2px 0 #0E1324,0 0 10px rgba(255,176,32,.8)}
.pressed.nb{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #070A16;animation-name:nbPress}
@keyframes nbPress{0%{transform:scale(1)}25%{transform:scale(1.08)}45%{transform:scale(.9)}100%{transform:scale(1.6);opacity:0}}   /* 強く光らせない */
.clips.nb{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.nb i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:nbFly 1.3s cubic-bezier(.15,.7,.3,1) var(--d) both;background:center/contain no-repeat}
.clips.nb .w{border-radius:50%;background:radial-gradient(circle at 40% 40%,#FFFFFF 0 22%,#FFF0C8 50%,rgba(255,224,160,0) 72%)}
.clips.nb .a{border-radius:50%;background:radial-gradient(circle at 40% 40%,#FFF4D6 0 20%,#FFB020 58%,rgba(255,176,32,0) 74%)}
.clips.nb .c{border-radius:50%;background:radial-gradient(circle at 40% 40%,#FFFFFF 0 20%,#B8C8FF 58%,rgba(126,150,255,0) 74%)}
.clips.nb .s{background-image:url("SP")}
.clips.nb .ring{left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:5px solid rgba(255,190,80,.85);box-shadow:0 0 18px rgba(255,176,32,.6);animation:nbRing .8s ease-out both}
@keyframes nbFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 44px)) rotate(calc(var(--r) * 1.3)) scale(.7)}}
@keyframes nbRing{0%{opacity:.95;transform:scale(.3)}100%{opacity:0;transform:scale(2.2)}}
@media (prefers-reduced-motion:reduce){.nb .nbsh,.nb .nbst,.nb .nbcr,.nb .nbpl,.nb .nblp,.nb .nbbm{animation:none}.nb .nbsh,.clips.nb{display:none}}
'''
NB_CSS = NB_CSS.replace('"SP"', '"' + ss_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><path d='M0 -9.5Q2.4 -2.4 9.5 0Q2.4 2.4 0 9.5Q-2.4 2.4 -9.5 0Q-2.4 -2.4 0 -9.5Z' fill='#FFF0C8'/></svg>") + '"')


MB_VEINS = (                                     # 大理石の的中ボタン：面のすじ（200×100）。(道, 色, [(太さ, こさ)…])：太い うすい すじ → 細い こい すじ
    ('M-12 76C22 70 48 82 84 62S138 34 170 40S204 24 214 18', '#A89F91', ((6, .07), (2.4, .14), (.8, .42))),
    ('M84 62C96 72 114 76 128 92S154 104 168 112', '#B3AB9E', ((3, .06), (.7, .36))),
    ('M-8 30C22 37 40 22 66 29S112 47 138 31S184 9 208 4', '#C9A25E', ((3.2, .14), (.9, .72))),
    ('M138 31C146 40 160 44 176 58S196 70 210 72', '#C9A25E', ((.6, .5),)),
    ('M14 98C36 88 58 95 80 86', '#B3AB9E', ((.6, .34),)),
    ('M40 6C52 14 60 12 74 20', '#B3AB9E', ((.5, .3),)),
)


def marble_face_svg(sfx=''):
    """PUSHの面に 白い大理石（面 200×100 の角の丸み26で切りぬく。文字の下）：あたたかい白の地・灰色と金の すじ（MB_VEINS）・
       うちがわに 金の細い二重のわく・上に つやの光・ときどき ななめに 光がすっと通る（.mbsh）・すみに 光の きらっ（.mbgl）。
       押したあとの面（sfx あり）には、まん中から ぴしっと ひびが走る（.mbck）。sfx：id のうしろにつける字"""
    K_, S_, G_ = (f'mb{c}{sfx}' for c in 'KSG')
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="26"/></clipPath>'
            f'<linearGradient id="{S_}" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#F6F2EA"/>'
            '<stop offset="1" stop-color="#E7E0D3"/></linearGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".75"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    veins = ''.join(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w:g}" stroke-linecap="round" opacity="{o:g}"/>'
                    for d, c, ws in MB_VEINS for w, o in ws)
    frame = ('<rect x="7" y="7" width="186" height="86" rx="19" fill="none" stroke="#C9A25E" stroke-width="1.3" opacity=".9"/>'
             '<rect x="10.5" y="10.5" width="179" height="79" rx="16" fill="none" stroke="#E2CB93" stroke-width=".7" opacity=".9"/>')
    glint = ''.join(f'<g transform="translate({x} {y})"><g class="mbgl" style="animation-delay:{dl}s">'
                    f'<path d="M0 -{r}Q{r * .2:.2f} -{r * .2:.2f} {r} 0Q{r * .2:.2f} {r * .2:.2f} 0 {r}Q-{r * .2:.2f} {r * .2:.2f} -{r} 0Q-{r * .2:.2f} -{r * .2:.2f} 0 -{r}Z" fill="#FFFFFF"/>'
                    f'<circle r="{r * .22:.2f}" fill="#FFF6DC"/></g></g>'
                    for x, y, r, dl in ((24, 18, 6, 0), (178, 80, 5, -1.7)))
    crack = ''
    if sfx:
        crack = ('<g class="mbck" fill="none" stroke-linecap="round" stroke-linejoin="round">'
                 + ''.join(f'<path d="{d}" stroke="#FFFFFF" stroke-width="2.4" opacity=".9" pathLength="1"/><path d="{d}" stroke="#7A7062" stroke-width="1.1" pathLength="1"/>'
                           for d in ('M100 52L88 44L80 47L66 36L54 38L40 26', 'M100 52L112 58L121 55L134 66L146 64L162 76',
                                     'M100 52L103 64L97 72L101 86', 'M100 52L96 40L104 30L101 16'))
                 + '</g>')
    body = (f'<rect width="200" height="100" fill="url(#{S_})"/>{veins}'
            '<ellipse cx="100" cy="6" rx="92" ry="22" fill="#FFFFFF" opacity=".5"/>'
            '<rect y="88" width="200" height="12" fill="#B8AE9C" opacity=".14"/>'
            + frame + glint
            + f'<g class="mbsh"><rect x="-70" y="-10" width="40" height="130" fill="url(#{G_})" transform="rotate(20)"/></g>' + crack)
    return (f'<i class="mbf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def mb_laurel(flip, gid):
    """金の月桂樹の枝（PUSHの左／右に、下から上へ 弓なりに）：茎と、両がわに ならぶ葉（先ほど小さく）。
       ゆれる中心（下のはし）へ うごかして .mblf で まわし、もどす"""
    pts = []
    for k in range(25):
        u = k / 24
        th = math.radians(-54 + 108 * u)                            # 下 → 上
        pts.append((44 - 78 * math.cos(th), 50 + 64 * math.sin(th) * -1))
    if flip:
        pts = [(200 - x, y) for x, y in pts]
    d = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
    leaves = ''
    for k in range(2, 25, 2):
        (x0, y0), (x1, y1) = pts[k - 1], pts[k]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        s_ = 1 - 0.38 * k / 24
        for side in (-1, 1):
            leaves += (f'<ellipse cx="{x1:.1f}" cy="{y1:.1f}" rx="{7.6 * s_:.1f}" ry="{2.7 * s_:.1f}" fill="url(#{gid})" '
                       f'transform="rotate({ang + side * 40:.1f} {x1:.1f} {y1:.1f}) translate({6.2 * s_:.1f} 0)"/>')
    tip = pts[-1]
    leaves += f'<ellipse cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" rx="5" ry="2" fill="url(#{gid})" transform="rotate({math.degrees(math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])):.1f} {tip[0]:.1f} {tip[1]:.1f}) translate(3 0)"/>'
    bx, by = pts[0]
    return (f'<g transform="translate({bx:.1f} {by:.1f})"><g class="mblf{" r" if flip else ""}"><g transform="translate({-bx:.1f} {-by:.1f})">'
            f'<path d="{d}" fill="none" stroke="#B8893E" stroke-width="1.6" stroke-linecap="round"/>{leaves}</g></g></g>')


def marble_decor_svg(sfx=''):
    """PUSHのまわり：左右に 金の月桂樹の枝（下のはしを中心に ゆっくり ゆれる .mblf）・金の光の きらっ（.mbtw）"""
    gid = f'mbL{sfx}'
    defs = (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6DE97"/>'
            '<stop offset=".55" stop-color="#C9952B"/><stop offset="1" stop-color="#9C7426"/></linearGradient></defs>')
    tw = ''.join(f'<g transform="translate({x} {y})"><g class="mbtw" style="animation-delay:{dl}s">'
                 f'<path d="M0 -{r}Q{r * .22:.2f} -{r * .22:.2f} {r} 0Q{r * .22:.2f} {r * .22:.2f} 0 {r}Q-{r * .22:.2f} {r * .22:.2f} -{r} 0Q-{r * .22:.2f} -{r * .22:.2f} 0 -{r}Z" fill="#FFE7A8"/></g></g>'
                 for x, y, r, dl in ((-6, -22, 6, 0), (206, -20, 5, -.9), (-4, 124, 4.5, -1.6), (210, 122, 6, -2.3)))
    return (f'<i class="mbd" aria-hidden="true"><svg viewBox="-40 -30 280 160" width="280" height="160">{defs}'
            + mb_laurel(0, gid) + mb_laurel(1, gid) + tw + '</svg></i>')


def marble_push_svg(sfx=''):
    return marble_face_svg(sfx) + marble_decor_svg(sfx)


MB_SHARDS = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'><path d='M2 6L9 1L18 4L17 13L10 19L3 15Z' fill='#FBF9F4' stroke='#D8D0C2' stroke-width='.8'/>"
             "<path d='M3 12C7 10 9 13 12 9S16 7 18 6' fill='none' stroke='#A89F91' stroke-width='.8' opacity='.7'/><path d='M4 5L9 2L15 4' fill='none' stroke='#FFFFFF' stroke-width='1.2'/></svg>",
             "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'><path d='M1 9L7 2L15 1L19 8L13 18L5 16Z' fill='#F7F3EB' stroke='#D8D0C2' stroke-width='.8'/>"
             "<path d='M2 13C6 9 10 12 13 7S17 4 19 3' fill='none' stroke='#C9A25E' stroke-width='.9' opacity='.85'/><path d='M3 8L8 3L14 2' fill='none' stroke='#FFFFFF' stroke-width='1.2'/></svg>")


def marble_burst(n=26, seed=37):
    """押した瞬間に、大理石の かけら（白・すじ入り）と 金ぱく・金の きらっ が ぱっと広がる。まん中から 金の 光の輪が広がる"""
    rnd = random.Random(seed)
    kinds = ['m', 'g', 'k', 's', 'm', 'g', 'k', 'm', 's', 'g', 'k']
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(90, 172)
        x, y = math.cos(a) * dist * 1.2, math.sin(a) * dist * .85 - 22
        k = kinds[i % len(kinds)]
        z = dict(m=rnd.uniform(14, 20), k=rnd.uniform(11, 16), g=rnd.uniform(7, 10), s=rnd.uniform(14, 19))[k]
        r = rnd.choice((-1, 1)) * rnd.uniform(60, 200)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{rnd.uniform(0, .1):.2f}s"></i>'
    out += '<i class="ring"></i>'
    return f'<div class="clips mb" aria-hidden="true">{out}</div>'


MB_CSS = r'''
/* ---------- 大理石の的中ボタン：大理石でできたPUSH（まさちゃんの指定） ----------
   面に 白い大理石：あたたかい白の地・灰色と金の すじ・うちがわに 金の細い二重のわく・上に つやの光・ときどき ななめに 光がすっと通る・すみに 光の きらっ。
   金のふち（あいだに 大理石の白い帯）・こい金の厚み・まわりに 金の光。「PUSH」は しっぽり明朝の 金ぱくの字を 彫ったように（上に かげ・下に 光）。
   左右に 金の月桂樹の枝（ゆっくり ゆれる）・金の きらっ。上下の動きは的中と同じ。
   押すと まん中から ぴしっと ひびが走って（強く光らせない）、ふわっと ふくらんで くだけ、大理石の かけらと 金ぱく・きらっ が広がり、金の 光の輪が広がる */
.mb{--pushA:#C9A25E;--pushB:#8A6514;--pushC:#F3E2B8;--rim:#F8F4EC;--rimD:#C9A25E;--pushFace:linear-gradient(160deg,#FFFFFF,#F3EEE5 55%,#E6DED0)}
.push.mb{box-shadow:inset 0 2px 0 rgba(255,255,255,.95),inset 0 -6px 10px rgba(150,130,100,.16),0 0 0 8px var(--rim),0 0 0 9.5px #E2CB93,0 0 0 13px var(--rimD),0 10px 0 13px #8E6F3A,0 0 30px 12px rgba(233,207,142,.32),0 22px 34px rgba(40,26,6,.45)}
.push.mb span{font:800 42px/1 "Shippori Mincho B1",serif;letter-spacing:.1em;padding-left:.1em;color:transparent;background:linear-gradient(180deg,#F1D68E 0%,#C9962F 48%,#9C7426 56%,#D9B25A 100%);
  -webkit-background-clip:text;background-clip:text;text-shadow:none;filter:drop-shadow(0 1px 0 #FFFFFF) drop-shadow(0 -1px 0 rgba(110,80,30,.45))}
.push.mb::after{border-color:rgba(233,207,142,.95)}
.mb .mbf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:26px;overflow:hidden;pointer-events:none;font-style:normal}
.mb .mbf svg{display:block;width:200px;height:100px}
.mb .mbd{position:absolute;left:-40px;top:-30px;width:280px;height:160px;pointer-events:none;z-index:3;font-style:normal}
.mb .mbd svg{display:block;width:280px;height:160px;overflow:visible}
.mb .mbsh{transform-box:view-box;transform-origin:0 0;animation:mbShine 5.2s ease-in-out infinite}
@keyframes mbShine{0%,58%{transform:translateX(0)}88%,100%{transform:translateX(320px)}}
.mb .mbgl{transform-box:fill-box;transform-origin:50% 50%;animation:mbGlint 3.2s ease-in-out infinite}
@keyframes mbGlint{0%,62%,100%{opacity:0;transform:scale(.3) rotate(0deg)}74%{opacity:1;transform:scale(1) rotate(30deg)}86%{opacity:0;transform:scale(.5) rotate(50deg)}}
.mb .mbtw{transform-box:fill-box;transform-origin:50% 50%;animation:mbTw 2.6s ease-in-out infinite}
@keyframes mbTw{0%,100%{opacity:.25;transform:scale(.5)}50%{opacity:1;transform:scale(1.1)}}
.mb .mblf{transform-box:view-box;transform-origin:0 0;animation:mbSway 3.8s ease-in-out infinite alternate}
.mb .mblf.r{animation-delay:-1.9s}
@keyframes mbSway{from{transform:rotate(-2.5deg)}to{transform:rotate(2.5deg)}}
.mb .mbck path{stroke-dasharray:1 1;stroke-dashoffset:1;animation:mbCrack .14s ease-out .03s both}
@keyframes mbCrack{to{stroke-dashoffset:0}}
.tap.mb{font-family:"Shippori Mincho B1",serif;font-weight:800;color:#F3E2B8;letter-spacing:.14em;text-shadow:0 2px 0 #6E5428,0 0 10px rgba(233,207,142,.7)}
.pressed.mb{box-shadow:0 0 0 8px var(--rim),0 0 0 13px var(--rimD),0 10px 0 13px #8E6F3A;animation-name:mbPress}
@keyframes mbPress{0%{transform:scale(1);opacity:1}30%{transform:scale(.96);opacity:1}50%{transform:scale(1.06);opacity:.9}100%{transform:scale(1.55);opacity:0}}   /* ひびが走るまでは 不透明のまま・強く光らせない */
.clips.mb{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.mb i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:mbFly 1.3s cubic-bezier(.15,.7,.3,1) calc(var(--d) + .12s) both;background:center/contain no-repeat}
.clips.mb .m{background-image:url("SH1")}
.clips.mb .k{background-image:url("SH2")}
.clips.mb .g{border-radius:1px;background:linear-gradient(135deg,#FFF3C8 0%,#E2B65A 45%,#A87C22 100%)}
.clips.mb .s{background-image:url("SP")}
.clips.mb .ring{left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:5px solid rgba(233,207,142,.9);box-shadow:0 0 18px rgba(201,162,94,.55);animation:mbRing .8s ease-out .12s forwards}
@keyframes mbFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 60px)) rotate(calc(var(--r) * 1.4)) scale(.8)}}
@keyframes mbRing{0%{opacity:.95;transform:scale(.3)}100%{opacity:0;transform:scale(2.2)}}
@media (prefers-reduced-motion:reduce){.mb .mbsh,.mb .mbgl,.mb .mbtw,.mb .mblf,.mb .mbck path{animation:none}.mb .mbsh,.mb .mbgl,.clips.mb{display:none}}
'''
MB_CSS = (MB_CSS.replace('"SP"', '"' + ss_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><path d='M0 -9.5Q2.4 -2.4 9.5 0Q2.4 2.4 0 9.5Q-2.4 2.4 -9.5 0Q-2.4 -2.4 0 -9.5Z' fill='#FFE7A8'/></svg>") + '"')
          .replace('"SH1"', '"' + ss_uri(MB_SHARDS[0]) + '"').replace('"SH2"', '"' + ss_uri(MB_SHARDS[1]) + '"'))


def kb_star(x, y, r, fill, k=.24, cls='', dl=0.0, stroke=''):
    """4つの とがりの キラッ（まん中 x y・大きさ r）。cls：動き（.kbgl・.kbtw）"""
    pts = ' '.join(f'{x + math.sin(i * math.pi / 4) * (r if i % 2 == 0 else r * k):.2f},{y - math.cos(i * math.pi / 4) * (r if i % 2 == 0 else r * k):.2f}'
                   for i in range(8))
    st = f' stroke="{stroke}" stroke-width=".8" stroke-linejoin="round"' if stroke else ''
    poly = f'<polygon points="{pts}" fill="{fill}"{st}/>'
    if not cls:
        return poly
    return f'<g class="{cls}" style="transform-origin:{x:.1f}px {y:.1f}px;animation-delay:{dl:g}s">{poly}</g>'


def koban_face_svg(sfx=''):
    """小判の的中ボタン：PUSHの面に 小判（面 200×100 の だ円で切りぬく。文字の下）：金の地（左上が明るい）・内がわの だ円の線（こい金）・
       たての ござ目・左右のはしに 桜の刻印（丸い わく）・上に つやの光・下に かげ・ときどき ななめに 光がすっと通る（.kbsh）・
       すみに 光の きらっ（.kbgl）。sfx：id のうしろにつける字"""
    K_, S_, G_ = (f'kb{c}{sfx}' for c in 'KSG')
    defs = (f'<defs><clipPath id="{K_}"><ellipse cx="100" cy="50" rx="100" ry="50"/></clipPath>'
            f'<radialGradient id="{S_}" cx=".36" cy=".3" r=".9"><stop offset="0" stop-color="#FFF6C4"/><stop offset=".32" stop-color="#F8D35C"/>'
            '<stop offset=".72" stop-color="#E6AA36"/><stop offset="1" stop-color="#B57C1C"/></radialGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".75"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    goza = ''
    for k in range(-15, 16):                                  # ござ目（たての 細い線・内がわの だ円の中）
        x = 100 + k * 5.6
        hh = 37 * math.sqrt(max(0.0, 1 - ((x - 100) / 86) ** 2))
        if hh > 4:
            goza += f'M{x:.1f} {50 - hh:.1f}V{50 + hh:.1f}'
    crest = ''
    for cx in (17, 183):                                      # 左右のはしの 桜の刻印
        pet = ''.join(f'<ellipse cx="{cx}" cy="{50 - 3.6:.1f}" rx="2.3" ry="3.4" transform="rotate({i * 72} {cx} 50)" fill="#FBD96E" stroke="#A87418" stroke-width=".7"/>'
                      for i in range(5))
        crest += (f'<circle cx="{cx}" cy="50" r="9" fill="#EDBE45" stroke="#9A6A12" stroke-width="1.3"/>'
                  f'<circle cx="{cx}" cy="50" r="7.2" fill="none" stroke="#FFE69A" stroke-width=".7" opacity=".9"/>{pet}'
                  f'<circle cx="{cx}" cy="50" r="1.5" fill="#B07A1A"/>')
    body = (f'<rect width="200" height="100" fill="url(#{S_})"/>'
            f'<path d="{goza}" stroke="#B9801E" stroke-width="1" opacity=".42"/>'
            '<ellipse cx="100" cy="50" rx="89" ry="41" fill="none" stroke="#A87418" stroke-width="1.6"/>'
            '<ellipse cx="100" cy="50" rx="86" ry="38.2" fill="none" stroke="#FFE69A" stroke-width=".8" opacity=".85"/>'
            '<path d="M6 60C28 92 172 92 194 60L200 100H0Z" fill="#8A5A10" opacity=".2"/>'
            '<ellipse cx="82" cy="15" rx="70" ry="11" fill="#FFFFFF" opacity=".32"/>'
            '<path d="M24 36C40 17 72 9.5 100 9" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" opacity=".8"/>'
            + crest
            + kb_star(40, 22, 7, '#FFFFFF', cls='kbgl') + kb_star(166, 78, 6, '#FFFFFF', cls='kbgl', dl=-1.7)
            + f'<g class="kbsh"><rect x="-70" y="-10" width="40" height="130" fill="url(#{G_})" transform="rotate(20)"/></g>')
    return (f'<i class="kbf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def koban_decor_svg(sfx=''):
    """PUSHのまわり：左右に 小さな小判（ふわふわ ゆれる .kbbo）・金の キラッ（.kbtw）"""
    import lucky_wall
    gid = f'kbKg{sfx}'
    defs = (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF4B8"/>'
            '<stop offset=".45" stop-color="#F5C542"/><stop offset="1" stop-color="#D18A22"/></linearGradient></defs>')
    kob = ''
    for k, (x, y, h, rot, dl) in enumerate(((-16, 12, 36, -24, 0), (-6, 88, 25, 18, -1.1), (216, 16, 32, 22, -0.6), (208, 90, 23, -16, -1.7))):
        kob += (f'<g transform="translate({x} {y})"><g class="kbbo" style="animation-delay:{dl:g}s"><g transform="rotate({rot})">'
                + lucky_wall.koban_svg(h, gid) + '</g></g></g>')
    tw = ''.join(kb_star(x, y, r, '#FFE7A8', cls='kbtw', dl=dl) for x, y, r, dl in ((24, -14, 6, 0), (184, -16, 5, -.9), (-24, 54, 4.5, -1.6), (226, 58, 5.5, -2.3)))
    return (f'<i class="kbd" aria-hidden="true"><svg viewBox="-40 -30 280 160" width="280" height="160">{defs}'
            + kob + tw + '</svg></i>')


def koban_push_svg(sfx=''):
    return koban_face_svg(sfx) + koban_decor_svg(sfx)


def kb_piece(kind):
    """押した時に 飛びちる かけら（data URI の SVG）：k＝小判・c＝丸い金貨（四角い穴）"""
    if kind == 'k':
        import lucky_wall
        return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -15 20 30'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
                "<stop offset='0' stop-color='#FFF4B8'/><stop offset='.45' stop-color='#F5C542'/><stop offset='1' stop-color='#D18A22'/></linearGradient></defs>"
                + lucky_wall.koban_svg(26, 'g') + "</svg>")
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-12 -12 24 24'><circle r='10.5' fill='#F7C744' stroke='#23202A' stroke-width='2'/>"
            "<circle r='7.4' fill='none' stroke='#D99A2B' stroke-width='1.2'/><rect x='-2.6' y='-2.6' width='5.2' height='5.2' fill='#C9851F' stroke='#23202A' stroke-width='1.2'/>"
            "<path d='M-6.5 -1.5A6.6 6.6 0 0 1 -1.5 -6.5' fill='none' stroke='#FFF6C8' stroke-width='1.6' stroke-linecap='round'/></svg>")


def koban_burst(n=28, seed=41):
    """押した瞬間に、小判と 丸い金貨・金の粉・キラッ が ふん水のように 上へ はじけて、くるくる回りながら 落ちる。まん中から 金の 光の輪が広がる"""
    rnd = random.Random(seed)
    kinds = ['k', 'c', 'g', 's', 'k', 'c', 'k', 'g', 's', 'c', 'k']
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 300 + rnd.uniform(-8, 8))
        dist = rnd.uniform(80, 165)
        x, y = math.cos(a) * dist * 1.25, math.sin(a) * dist * .9 - 30
        k = kinds[i % len(kinds)]
        z = dict(k=rnd.uniform(17, 24), c=rnd.uniform(15, 20), g=rnd.uniform(6, 9), s=rnd.uniform(14, 19))[k]
        r = rnd.choice((-1, 1)) * rnd.uniform(120, 340)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{rnd.uniform(0, .12):.2f}s"></i>'
    out += '<i class="ring"></i>'
    return f'<div class="clips kb" aria-hidden="true">{out}</div>'


KB_CSS = r'''
/* ---------- 開運の的中ボタン：小判でできたPUSH（まさちゃんの指定） ----------
   ボタンが まるごと 小判（よこ長の だ円）：金の地・内がわの だ円の線・たての ござ目・左右のはしに 桜の刻印・上に つやの光・
   ときどき ななめに 光がすっと通る・すみに 光の きらっ。明るい金のふち・こい茶の線・下に 小判が2まい 重なった厚み・まわりに 金の光。
   「PUSH」は 刻印のように 彫った字（Zen Antique Soft・こい茶に 光のふち）。左右に 小さな小判が ふわふわ・金の キラッ。上下の動きは的中と同じ。
   押すと ちゃりんと ちぢんで ふくらみ（強く光らせない）、小判と 丸い金貨・金の粉・キラッ が ふん水のように 上へ はじけて 落ち、金の 光の輪が広がる */
.kb{--pushA:#F5C542;--pushB:#6B430A;--pushC:#FFF0B0;--rim:#F7D774;--rimD:#7A520C;--pushFace:radial-gradient(90% 90% at 36% 30%,#FFF6C4,#F8D35C 32%,#E6AA36 72%,#B57C1C)}
.push.kb{--pr:50%;box-shadow:inset 0 2px 0 rgba(255,255,255,.6),inset 0 -5px 8px rgba(140,90,10,.3),0 0 0 4px #F7D774,0 0 0 6px #7A520C,
  0 6px 0 6px #DCA436,0 7.5px 0 6px #7A520C,0 12px 0 6px #C48A22,0 13.5px 0 6px #6B4A0E,0 0 30px 12px rgba(255,214,90,.34),0 24px 34px rgba(0,0,0,.45)}
.push.kb span{font:400 44px/1 "Zen Antique Soft",serif;letter-spacing:.08em;padding-left:.08em;color:#6B430A;text-shadow:0 1.5px 0 #FFF2B0,0 -1px 0 rgba(90,55,5,.5)}
.push.kb::after{border-radius:50%;border-color:rgba(255,226,130,.95)}
.kb .kbf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:50%;overflow:hidden;pointer-events:none;font-style:normal}
.kb .kbf svg{display:block;width:200px;height:100px}
.kb .kbd{position:absolute;left:-40px;top:-30px;width:280px;height:160px;pointer-events:none;z-index:3;font-style:normal}
.kb .kbd svg{display:block;width:280px;height:160px;overflow:visible}
.kb .kbsh{transform-box:view-box;transform-origin:0 0;animation:kbShine 4.6s ease-in-out infinite}
@keyframes kbShine{0%,55%{transform:translateX(0)}85%,100%{transform:translateX(320px)}}
.kb .kbgl{animation:kbGlint 3s ease-in-out infinite}
@keyframes kbGlint{0%,62%,100%{opacity:0;transform:scale(.3) rotate(0deg)}74%{opacity:1;transform:scale(1) rotate(30deg)}86%{opacity:0;transform:scale(.5) rotate(50deg)}}
.kb .kbtw{animation:kbTw 2.4s ease-in-out infinite}
@keyframes kbTw{0%,100%{opacity:.25;transform:scale(.5)}50%{opacity:1;transform:scale(1.1)}}
.kb .kbbo{transform-box:view-box;transform-origin:0 0;animation:kbBob 2.6s ease-in-out infinite alternate}
@keyframes kbBob{from{transform:translate(0,-3px) rotate(-5deg)}to{transform:translate(0,3px) rotate(5deg)}}
.tap.kb{font-family:"Zen Antique Soft",serif;font-weight:400;color:#FFE08A;letter-spacing:.12em;text-shadow:0 2px 0 #6B430A,0 0 10px rgba(255,200,80,.75)}
.pressed.kb{border-radius:50%;box-shadow:0 0 0 4px #F7D774,0 0 0 6px #7A520C,0 6px 0 6px #DCA436,0 7.5px 0 6px #7A520C;animation-name:kbPress}
@keyframes kbPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.07)}100%{transform:scale(1.5);opacity:0}}   /* 強く光らせない */
.clips.kb{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.kb i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:kbFly 1.5s cubic-bezier(.2,.6,.4,1) calc(var(--d) + .1s) both;background:center/contain no-repeat}
.clips.kb .k{height:calc(var(--z) * 1.5);top:calc(var(--z) * -.75);background-image:url("KO")}
.clips.kb .c{background-image:url("CO")}
.clips.kb .g{border-radius:1px;background:linear-gradient(135deg,#FFF3C8 0%,#E8BC5A 45%,#A87C22 100%)}
.clips.kb .s{background-image:url("SP")}
.clips.kb .ring{left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:5px solid rgba(255,214,110,.9);box-shadow:0 0 18px rgba(245,197,66,.55);animation:kbRing .8s ease-out .1s forwards}
@keyframes kbFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.35)}8%{opacity:1}45%{opacity:1;transform:translate(calc(var(--x) * .8),var(--y)) rotate(calc(var(--r) * .45)) scale(1)}
  100%{opacity:0;transform:translate(var(--x),calc(var(--y) + 170px)) rotate(var(--r)) scale(.9)}}
@keyframes kbRing{0%{opacity:.95;transform:scale(.3)}100%{opacity:0;transform:scale(2.2)}}
@media (prefers-reduced-motion:reduce){.kb .kbsh,.kb .kbgl,.kb .kbtw,.kb .kbbo{animation:none}.kb .kbsh,.kb .kbgl,.clips.kb{display:none}}
'''
KB_CSS = (KB_CSS.replace('"SP"', '"' + ss_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><path d='M0 -9.5Q2.4 -2.4 9.5 0Q2.4 2.4 0 9.5Q-2.4 2.4 -9.5 0Q-2.4 -2.4 0 -9.5Z' fill='#FFF0B0'/></svg>") + '"')
          .replace('"KO"', '"' + ss_uri(kb_piece('k')) + '"').replace('"CO"', '"' + ss_uri(kb_piece('c')) + '"'))



# ---------- 黒板の的中ボタン：黒板にチョークで書いたPUSH（まさちゃんの指定） ----------
KK_CHALK, KK_YEL, KK_PINK = '#F3F1E7', '#F6E27F', '#F4A6C0'


def kk_filter(fid, seed=5):
    """チョークの ざらざら（ところどころ すける・ふちが けば立つ）"""
    return (f'<filter id="{fid}" x="-10%" y="-20%" width="120%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="1.5" numOctaves="2" seed="{seed}" result="n"/>'
            '<feDisplacementMap in="SourceGraphic" in2="n" scale="1.7" result="d"/>'
            '<feComposite in="d" in2="n" operator="arithmetic" k1="0" k2="1" k3="-.4" k4=".1"/></filter>')


def kk_rough(pts, seed, j=.55, closed=True):
    """手で書いた線（点を少し ずらす）の path"""
    rnd = random.Random(seed)
    q = [(x + rnd.uniform(-j, j), y + rnd.uniform(-j, j)) for x, y in pts]
    d = f'M{q[0][0]:.1f} {q[0][1]:.1f}' + ''.join(f'L{x:.1f} {y:.1f}' for x, y in q[1:])
    return d + ('Z' if closed else '')


def kk_rrect(x0, y0, x1, y1, r, n=10):
    """角の丸い四角の点（右上から 時計回り）"""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def kk_star(x, y, r, k=.45):
    return [(x + math.sin(i * math.pi / 5) * (r if i % 2 == 0 else r * k), y - math.cos(i * math.pi / 5) * (r if i % 2 == 0 else r * k)) for i in range(10)]


def kk_face_svg(sfx=''):
    """黒板の的中ボタン：PUSHの面＝小さな黒板（200×100）。消したあとの もや・チョークで書いた 立体のボタン（上の面と 下の厚み・厚みに ななめの線）と
       「PUSH」（Yomogi・チョークの ざらざら）・左上に 黄色い星・右下に ピンクの花丸・下に 白い点々。sfx：id のうしろにつける字"""
    F = f'kkC{sfx}'
    top = kk_rrect(30, 17, 170, 63, 15)
    bot = [(x, y + 9) for x, y in top if y > 40]
    side = 'M30 42V51M170 42V51'
    hatch = ''.join(f'M{x} 71l3 -6' for x in range(46, 156, 9))
    body = ('<rect width="200" height="100" fill="#24423A"/>'
            '<ellipse cx="54" cy="26" rx="58" ry="20" fill="#FFFFFF" opacity=".045"/><ellipse cx="150" cy="78" rx="62" ry="22" fill="#FFFFFF" opacity=".04"/>'
            '<path d="M6 88Q54 74 104 86T198 78" fill="none" stroke="#FFFFFF" stroke-opacity=".05" stroke-width="12" stroke-linecap="round"/>'
            f'<g filter="url(#{F})" fill="none" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{kk_rough(bot, 3, closed=False)}" stroke="{KK_CHALK}" stroke-width="2.2" opacity=".85"/>'
            f'<path d="{side}" stroke="{KK_CHALK}" stroke-width="2.2" opacity=".85"/>'
            f'<path d="{hatch}" stroke="{KK_CHALK}" stroke-width="1.3" opacity=".5"/>'
            f'<path d="{kk_rough(top, 1)}" stroke="{KK_CHALK}" stroke-width="2.6"/>'
            f'<path d="{kk_rough(top, 2, .8)}" stroke="{KK_CHALK}" stroke-width="1.2" opacity=".55"/>'
            f'<path d="{kk_rough(kk_star(15, 17, 8), 4, .3)}" stroke="{KK_YEL}" stroke-width="1.8"/>'
            f'<path d="{hanamaru_d(181, 80, 13)}" stroke="{KK_PINK}" stroke-width="1.5"/>'
            f'<path d="M12 84h3M20 88h2M182 14h3M188 20h2" stroke="{KK_CHALK}" stroke-width="1.6" opacity=".7"/>'
            '</g>'
            f'<text x="100" y="51" text-anchor="middle" font-family="Yomogi,sans-serif" font-size="34" letter-spacing="3" fill="#F7F5EC" filter="url(#{F})">PUSH</text>')
    return (f'<i class="kkf" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100"><defs>{kk_filter(F)}</defs>{body}</svg></i>')


def kk_decor_svg(sfx=''):
    """PUSHのまわり：木の枠の 木目・下に チョーク受け（白・黄・ピンクのチョークと 小さな黒板消し）・上の左右に チョークの星が きらっ（.kktw）"""
    F = f'kkD{sfx}'
    grain = ('M-7 -5.5H207M-7 -2.5H207M-7 102.5H207M-7 105.5H207'
             'M-5.5 0V100M-2.5 0V100M202.5 0V100M205.5 0V100')
    tray = ('<rect x="-16" y="117" width="232" height="8" rx="2.5" fill="#8A5A2B"/><rect x="-16" y="122" width="232" height="3" rx="1.5" fill="#5E3A18"/>'
            '<path d="M-13 118.6H213" stroke="#B07C45" stroke-width="1"/>'
            f'<rect x="16" y="111.5" width="22" height="6" rx="3" fill="{KK_CHALK}"/><rect x="44" y="112" width="16" height="5.5" rx="2.75" fill="{KK_YEL}"/>'
            f'<rect x="65" y="112" width="13" height="5.5" rx="2.75" fill="{KK_PINK}"/>'
            '<g transform="translate(172 110)"><rect x="-19" y="2.5" width="38" height="5" rx="1.5" fill="#EDE8DC"/><rect x="-19" y="-1.5" width="38" height="5.5" rx="2" fill="#2F4F8C"/>'
            '<rect x="-19" y="-1.5" width="38" height="9" rx="2" fill="none" stroke="#1C2B4A" stroke-width="1"/></g>')
    tw = ''.join(f'<g class="kktw" style="transform-origin:{x}px {y}px;animation-delay:{dl}s"><path d="{kk_rough(kk_star(x, y, r), 9 + i, .25)}" stroke="{c}" stroke-width="1.8"/></g>'
                 for i, (x, y, r, c, dl) in enumerate(((-24, -14, 7, KK_CHALK, 0), (226, -12, 6, KK_YEL, -1.1), (-30, 104, 5, KK_PINK, -.6), (232, 100, 5.5, KK_CHALK, -1.7))))
    return (f'<i class="kkd" aria-hidden="true"><svg viewBox="-40 -30 280 180" width="280" height="180"><defs>{kk_filter(F, 8)}</defs>'
            f'<path d="{grain}" stroke="#5E3A18" stroke-opacity=".45" stroke-width=".8" fill="none"/>{tray}'
            f'<g filter="url(#{F})" fill="none" stroke-linecap="round" stroke-linejoin="round">{tw}</g></svg></i>')


def chalk_push_svg(sfx=''):
    return kk_face_svg(sfx) + kk_decor_svg(sfx)


def kk_piece(kind):
    """押した時に 飛びちる チョークのかけら・星（data URI の SVG）：w・y・p＝チョーク（白・黄・ピンク）・s＝チョークの星"""
    if kind == 's':
        d = 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in kk_star(0, 0, 8.5)) + 'Z'
        return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><path d='{d}' fill='none' stroke='{KK_YEL}' stroke-width='1.8' stroke-linejoin='round'/></svg>"
    c = dict(w=KK_CHALK, y=KK_YEL, p=KK_PINK)[kind]
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 9'><rect x='.5' y='.5' width='23' height='8' rx='4' fill='{c}'/>"
            "<rect x='3' y='5.2' width='18' height='2.2' rx='1.1' fill='#000' opacity='.12'/></svg>")


def chalk_burst(n=26, seed=53):
    """押した瞬間に、チョークの粉が ふわっと ふくらみ、チョークのかけら（白・黄・ピンク）と 星が ふん水のように はじけて 落ちる。
       まん中に ピンクのチョークで 花丸を さっと書く（1本の線：うずまき → 花びら）"""
    rnd = random.Random(seed)
    out = ''
    for i in range(6):                                            # 粉
        a = 2 * math.pi * i / 6 + rnd.uniform(-.3, .3)
        out += f'<i class="pf" style="--x:{math.cos(a) * 46:.0f}px;--y:{math.sin(a) * 30 - 10:.0f}px;--z:{rnd.uniform(70, 100):.0f}px;--d:{rnd.uniform(0, .08):.2f}s"></i>'
    kinds = ['w', 'y', 'p', 's', 'w', 'p', 'y', 'w', 's']
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 300 + rnd.uniform(-8, 8))
        dist = rnd.uniform(80, 160)
        x, y = math.cos(a) * dist * 1.25, math.sin(a) * dist * .9 - 30
        k = kinds[i % len(kinds)]
        z = rnd.uniform(18, 24) if k != 's' else rnd.uniform(16, 22)
        r = rnd.choice((-1, 1)) * rnd.uniform(160, 420)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{rnd.uniform(0, .12):.2f}s"></i>'
    hm = (f'<svg class="hm" viewBox="-110 -110 220 220" width="220" height="220"><defs>{kk_filter("kkB", 11)}</defs>'
          f'<g filter="url(#kkB)" fill="none" stroke="{KK_PINK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
          f'<path class="hs" pathLength="100" d="{hanamaru_d(0, 0, 82, N=90)}"/></g></svg>')
    return f'<div class="clips kk" aria-hidden="true">{out}{hm}</div>'


KK_CSS = r"""
/* ---------- 黒板の的中ボタン：黒板にチョークで書いたPUSH（まさちゃんの指定） ----------
   ボタンが 小さな黒板：緑の黒板（消したあとの もや）・木の枠（木目）・下に チョーク受け（白・黄・ピンクのチョークと 小さな黒板消し）。
   黒板に チョークで書いた 立体のボタン（上の面と 下の厚み・厚みに ななめの線）と「PUSH」（Yomogi・ざらざら）・左上に 黄色い星・右下に ピンクの花丸。
   まわりに チョークの星が きらっ・光の輪は チョークの点線。上下の動きは的中と同じ。
   押すと ぎゅっと ちぢんで ふくらみ（強く光らせない）、チョークの粉が ふわっ・チョークのかけらと 星が はじけて 落ち、まん中に ピンクのチョークで 花丸を さっと書く */
.kk{--pr:10px;--pushA:#2C4E44;--pushB:#24423A;--pushC:#3A5E54;--rim:#9A6834;--rimD:#5E3A18;--pushFace:#24423A}
.push.kk{box-shadow:inset 0 0 0 2px rgba(0,0,0,.35),inset 0 0 16px rgba(0,0,0,.35),0 0 0 7px #9A6834,0 0 0 9px #5E3A18,0 9px 0 9px #6E4520,0 22px 30px rgba(0,0,0,.5)}
.push.kk span{color:transparent;text-shadow:none}
.push.kk::after{border:3px dashed rgba(243,241,231,.8);border-radius:calc(var(--pr) + 18px)}
.kk .kkf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:10px;overflow:hidden;pointer-events:none;font-style:normal}
.kk .kkf svg{display:block;width:200px;height:100px}
.kk .kkd{position:absolute;left:-40px;top:-30px;width:280px;height:180px;pointer-events:none;z-index:3;font-style:normal}
.kk .kkd svg{display:block;width:280px;height:180px;overflow:visible}
.kk .kktw{transform-box:view-box;animation:kkTw 2.6s ease-in-out infinite}
@keyframes kkTw{0%,100%{opacity:.35;transform:scale(.6) rotate(0deg)}50%{opacity:1;transform:scale(1.1) rotate(18deg)}}
.tap.kk{font-family:"Yomogi",sans-serif;font-weight:400;color:#F3F1E7;letter-spacing:.14em;text-shadow:0 0 6px rgba(255,255,255,.35)}
.pressed.kk{border-radius:10px;background:#24423A;box-shadow:0 0 0 7px #9A6834,0 0 0 9px #5E3A18,0 9px 0 9px #6E4520;animation-name:kkPress}
@keyframes kkPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.05)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
.clips.kk{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.kk i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) * -.19);width:var(--z);height:calc(var(--z) * .375);animation:kkFly 1.5s cubic-bezier(.2,.6,.4,1) calc(var(--d) + .06s) both;background:center/contain no-repeat}
.clips.kk .w{background-image:url("CW")}.clips.kk .y{background-image:url("CY")}.clips.kk .p{background-image:url("CP")}
.clips.kk .s{top:calc(var(--z) / -2);height:var(--z);background-image:url("ST")}
.clips.kk .pf{left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);border-radius:50%;
  background:radial-gradient(circle,rgba(243,241,231,.3) 0,rgba(243,241,231,.13) 45%,rgba(243,241,231,0) 70%);animation:kkPuff 1s ease-out var(--d) both}
.clips.kk .hm{position:absolute;left:-110px;top:-110px;width:220px;height:220px;overflow:visible;animation:kkHm 1.2s linear both}
.clips.kk .hs{stroke-dasharray:101 102;stroke-dashoffset:101;animation:kkDraw .36s linear .04s forwards}
@keyframes kkDraw{to{stroke-dashoffset:0}}
@keyframes kkHm{0%{opacity:1;transform:scale(.9) rotate(-8deg)}50%{opacity:1;transform:scale(1) rotate(0deg)}100%{opacity:0;transform:scale(1.06) rotate(4deg)}}
@keyframes kkFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.35)}8%{opacity:1}45%{opacity:1;transform:translate(calc(var(--x) * .8),var(--y)) rotate(calc(var(--r) * .45)) scale(1)}
  100%{opacity:0;transform:translate(var(--x),calc(var(--y) + 170px)) rotate(var(--r)) scale(.9)}}
@keyframes kkPuff{0%{opacity:0;transform:translate(0,0) scale(.3)}15%{opacity:1}100%{opacity:0;transform:translate(var(--x),var(--y)) scale(1.7)}}
@media (prefers-reduced-motion:reduce){.kk .kktw{animation:none}.clips.kk{display:none}}
"""
KK_CSS = (KK_CSS.replace('"CW"', '"' + ss_uri(kk_piece('w')) + '"').replace('"CY"', '"' + ss_uri(kk_piece('y')) + '"')
          .replace('"CP"', '"' + ss_uri(kk_piece('p')) + '"').replace('"ST"', '"' + ss_uri(kk_piece('s')) + '"'))


# ---------- シルバー帯・ゴールド帯の的中ボタン：シルバー・ゴールドでできたPUSH（まさちゃんの指定） ----------
# ag＝シルバー（銀）・au＝ゴールド（金）。同じ作りで 色だけ ちがう
MT_PAL = dict(
    ag=dict(plate=[(0, '#FFFFFF'), (.1, '#F3F6F9'), (.3, '#D6DCE3'), (.44, '#A4ADB7'), (.5, '#68727D'), (.56, '#7D8792'), (.72, '#C8CFD7'), (.88, '#EEF2F6'), (1, '#FFFFFF')],
            letter=[(0, '#FFFFFF'), (.38, '#E4E9EE'), (.5, '#8E98A3'), (.58, '#B9C1CA'), (1, '#FFFFFF')],
            edge='#232930', side=('#8A939D', '#39414A'), hair=('#FFFFFF', '#56616C'), star='#FFFFFF', glow='#B3CEFF', band='#F2F7FF', core='#FFFFFF',
            bevel=('#FFFFFF', '#6E7883'), rings=('#FFFFFF', '#8E98A3', '#EEF2F6', '#3E4650'), depth=('#9AA4AE', '#3A424B'), inS='rgba(40,50,60,.35)',
            aura=('rgba(255,255,255,.55)', 'rgba(160,195,255,.35)'), ring='rgba(232,240,255,.95)', rl='#FFFFFF',
            tap=('#F2F4F6', '0 2px 0 #3A424B,0 0 12px rgba(190,215,255,.95)'), chip=('#FFFFFF', '#C9D0D8', '#7D8792')),
    au=dict(plate=[(0, '#FFF9DE'), (.1, '#FDEBB0'), (.3, '#F2CA66'), (.44, '#CC9636'), (.5, '#8C5C12'), (.56, '#A6721F'), (.72, '#EBC15A'), (.88, '#FCE6A6'), (1, '#FFF8D8')],
            letter=[(0, '#FFFCEC'), (.38, '#FBE29C'), (.5, '#B47D20'), (.58, '#DEAB4A'), (1, '#FFF6D0')],
            edge='#3A2504', side=('#C08A2A', '#5E3E0A'), hair=('#FFF8DC', '#8E5E14'), star='#FFFBEA', glow='#FFC83A', band='#FFE9A0', core='#FFFDF2',
            bevel=('#FFF8DC', '#A06C18'), rings=('#FFF8DA', '#A8741E', '#FCE3A0', '#5A3A08'), depth=('#D9A43A', '#5E3E0A'), inS='rgba(110,70,10,.35)',
            aura=('rgba(255,228,150,.6)', 'rgba(255,185,50,.38)'), ring='rgba(255,226,130,.95)', rl='#FFF6D6',
            tap=('#FFE08A', '0 2px 0 #5E3E0A,0 0 12px rgba(255,205,90,.95)'), chip=('#FFF6D0', '#F2C55A', '#A8741E')))
MT_NAME = dict(ag='シルバー', au='ゴールド')
MT_LETTER = ((47, 38, 12), (110, 37, 10), (157, 40, 12))      # 「PUSH」の字のかどの きらっ（光の帯が通った時）


def mt_sheen_t(x, y, period=1.8, end=.55, dist=330.0, u0=-93.0, ang=22.0):
    """面の光の帯（1本め）のまん中が (x, y) を通る秒（ease-in-out で 0〜end の間に dist 動く・帯は ang 度 かたむく）"""
    a = math.radians(ang)
    T = x - u0 / math.cos(a) + y * math.tan(a)
    f = min(max(T / dist, 0.0), 1.0)
    bz = lambda u, p1, p2: 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u * u * p2 + u ** 3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        if bz(m, 0.0, 1.0) < f:
            lo = m
        else:
            hi = m
    return bz(lo, .42, .58) * end * period


def mt_stops(stops):
    return ''.join(f'<stop offset="{o:g}" stop-color="{c}"/>' for o, c in stops)


def mt_glint(x, y, L, fill, glow, cls, dl, streak=0.0):
    """きらっ（まん中 x y・横の光 L）：まわりの光（glow）・4つの とがり・小さい ななめの とがり・横に のびる光（streak＞0）。cls の動きは 0,0 ではなく x y が中心"""
    k = .14
    pts = ' '.join(f'{x + math.sin(i * math.pi / 4) * (L if i % 4 == 2 else L * .8 if i % 4 == 0 else L * k):.2f},'
                   f'{y - math.cos(i * math.pi / 4) * (L if i % 4 == 2 else L * .8 if i % 4 == 0 else L * k):.2f}' for i in range(8))
    pts2 = ' '.join(f'{x + math.sin(i * math.pi / 4 + math.pi / 4) * (L * .42 if i % 2 == 0 else L * .08):.2f},'
                    f'{y - math.cos(i * math.pi / 4 + math.pi / 4) * (L * .42 if i % 2 == 0 else L * .08):.2f}' for i in range(8))
    st = (f'<rect x="{x - L * streak:.1f}" y="{y - .7:.1f}" width="{2 * L * streak:.1f}" height="1.4" fill="url(#{glow}L)" opacity=".9"/>' if streak else '')
    return (f'<g class="{cls}" style="transform-origin:{x:.1f}px {y:.1f}px;animation-delay:{dl:g}s">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{L * .85:.1f}" fill="url(#{glow})"/>{st}'
            f'<polygon points="{pts2}" fill="{fill}" opacity=".85"/><polygon points="{pts}" fill="{fill}"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.2, L * .12):.1f}" fill="#FFFFFF"/></g>')


def mt_glow_defs(pre, gid):
    M = MT_PAL[pre]
    return (f'<radialGradient id="{gid}"><stop offset="0" stop-color="{M["glow"]}" stop-opacity=".95"/><stop offset=".38" stop-color="{M["glow"]}" stop-opacity=".42"/>'
            f'<stop offset="1" stop-color="{M["glow"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{gid}L" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{M["glow"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#FFFFFF"/><stop offset="1" stop-color="{M["glow"]}" stop-opacity="0"/></linearGradient>')


def mt_face_svg(pre, sfx=''):
    """シルバー・ゴールドの的中ボタン：PUSHの面（200×100・角の丸み26で切りぬく）＝ みがいた 銀（金）の板：
       上は 空の映りこみ（白く明るい）・まん中に 地平の映りこみ（こい帯）・下は また明るく。こまかい ヘアライン・上に つやの光・内がわの ふち（上は光・下はかげ）。
       「PUSH」は 銀（金）の 立体の字（こいふち・下に 厚み・上に 光のふち）。光の帯が 1.8秒ごとに ななめに すうっと 通る（2本・.{pre}sh）・
       あちこちで かわるがわる きらっ（.{pre}gl）。sfx：id のうしろにつける字"""
    M = MT_PAL[pre]
    K_, P_, T_, G_, C_, H_, R_, B_ = (f'{pre}{c}{sfx}' for c in 'KPTGCHRB')
    defs = (f'<defs><clipPath id="{K_}"><rect width="200" height="100" rx="26"/></clipPath>'
            f'<linearGradient id="{P_}" x1="0" y1="0" x2="0" y2="1">{mt_stops(M["plate"])}</linearGradient>'
            f'<linearGradient id="{T_}" gradientUnits="userSpaceOnUse" x1="0" y1="35" x2="0" y2="65">{mt_stops(M["letter"])}</linearGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{M["band"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{M["band"]}" stop-opacity=".8"/><stop offset="1" stop-color="{M["band"]}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="{C_}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{M["core"]}"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>'
            f'<pattern id="{H_}" width="200" height="3" patternUnits="userSpaceOnUse"><rect width="200" height=".7" fill="{M["hair"][0]}" opacity=".32"/>'
            f'<rect y="1.6" width="200" height=".6" fill="{M["hair"][1]}" opacity=".16"/></pattern>'
            + mt_glow_defs(pre, R_)
            + f'<linearGradient id="{B_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{M["bevel"][0]}"/><stop offset=".42" stop-color="{M["bevel"][0]}" stop-opacity="0"/>'
            f'<stop offset=".62" stop-color="{M["bevel"][1]}" stop-opacity="0"/><stop offset="1" stop-color="{M["bevel"][1]}"/></linearGradient></defs>')
    tx = lambda extra: (f'<text x="100" y="64.5" text-anchor="middle" font-family="Dela Gothic One,sans-serif" font-size="40" letter-spacing="1.5" '
                        f'stroke-linejoin="round"{extra}>PUSH</text>')
    letters = (''.join(tx(f' fill="{c}" stroke="{c}" stroke-width="2.6" transform="translate(0 {k})"') for k, c in ((4.5, M['side'][1]), (3, M['side'][1]), (1.5, M['side'][0])))
               + tx(f' fill="url(#{T_})" stroke="{M["edge"]}" stroke-width="2.6" paint-order="stroke"')
               + tx(' fill="none" stroke="#FFFFFF" stroke-width=".8" opacity=".75" transform="translate(0 -.8)"'))
    sheen = ''.join(f'<g class="{pre}sh{c}"><g transform="rotate(22)"><rect x="{x0}" y="-80" width="{w}" height="260" fill="url(#{G_})"/>'
                    f'<rect x="{x0 + w / 2 - cw / 2:g}" y="-80" width="{cw}" height="260" fill="url(#{C_})"/></g></g>'
                    for c, x0, w, cw in (('', -118, 50, 8), (' b', -96, 22, 4)))
    glints = ''.join(mt_glint(x, y, L, M['star'], R_, f'{pre}gl', dl) for x, y, L, dl in
                     ((30, 22, 13, 0), (171, 28, 12, -.32), (153, 82, 11, -.64), (47, 80, 11.5, -.96), (100, 12, 10, -1.28)))
    glints += ''.join(mt_glint(x, y, L, M['star'], R_, f'{pre}lg{i}', 0) for i, (x, y, L) in enumerate(MT_LETTER))
    body = (f'<rect width="200" height="100" fill="url(#{P_})"/><rect width="200" height="100" fill="url(#{H_})"/>'
            '<path d="M0 0H200V24Q100 36 0 24Z" fill="#FFFFFF" opacity=".26"/>'
            '<ellipse cx="62" cy="15" rx="58" ry="8" fill="#FFFFFF" opacity=".55"/>'
            '<path d="M20 29C50 16 122 12 178 19" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" opacity=".9"/>'
            '<path d="M16 87C62 96 138 96 184 87" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>'
            f'<rect x="1.5" y="1.5" width="197" height="97" rx="24.5" fill="none" stroke="url(#{B_})" stroke-width="3"/>'
            + letters + sheen + glints)
    return (f'<i class="{pre}f" aria-hidden="true"><svg viewBox="0 0 200 100" width="200" height="100">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def mt_rim_d(g, r=26.0):
    """ボタンの ふち（外へ g）を 左上から 時計回りに1周する道"""
    x0, y0, x1, y1, R = -g, -g, 200 + g, 100 + g, r + g
    return (f'M{x0 + R:g} {y0:g}H{x1 - R:g}A{R:g} {R:g} 0 0 1 {x1:g} {y0 + R:g}V{y1 - R:g}A{R:g} {R:g} 0 0 1 {x1 - R:g} {y1:g}'
            f'H{x0 + R:g}A{R:g} {R:g} 0 0 1 {x0:g} {y1 - R:g}V{y0 + R:g}A{R:g} {R:g} 0 0 1 {x0 + R:g} {y0:g}Z')


def mt_decor_svg(pre, sfx=''):
    """PUSHのまわり：ふちを 光が2つ ぐるっと回る（.{pre}rl）・まわりの 大きい きらっ（横に のびる光つき・.{pre}tw）・
       下から上へ ふわっと のぼる 光の粒（.{pre}fl）"""
    M = MT_PAL[pre]
    gid = f'{pre}Dg{sfx}'
    rim = mt_rim_d(9.5)                   # ふちの いちばん外の こい線の上
    rl = (f'<path d="{rim}" pathLength="100" fill="none" stroke="{M["glow"]}" stroke-width="9" stroke-linecap="round" stroke-dasharray="5 45" opacity=".45" class="{pre}rl"/>'
          f'<path d="{rim}" pathLength="100" fill="none" stroke="{M["rl"]}" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="5 45" class="{pre}rl"/>')
    tw = ''.join(mt_glint(x, y, L, M['star'], gid, f'{pre}tw', dl, streak=st) for x, y, L, dl, st in
                 ((-16, -9, 16, 0, 2.6), (216, 109, 14, -1.1, 2.6), (205, -17, 10, -.55, 0), (-7, 114, 9, -1.65, 0), (-31, 50, 8, -.8, 0), (233, 44, 9, -1.9, 0)))
    rnd = random.Random(61 if pre == 'ag' else 67)
    fl = ''
    for i in range(10):
        x = -24 + i * 27 + rnd.uniform(-8, 8)
        y = rnd.uniform(96, 124)
        dur = rnd.uniform(2.2, 3.2)
        fl += (f'<g class="{pre}fl" style="animation-duration:{dur:.2f}s;animation-delay:{-rnd.uniform(0, dur):.2f}s">'
               + mt_glint(x, y, rnd.uniform(4.5, 6.5), M['star'], gid, '', 0) + '</g>')
    return (f'<i class="{pre}d" aria-hidden="true"><svg viewBox="-40 -30 280 160" width="280" height="160"><defs>{mt_glow_defs(pre, gid)}</defs>'
            + rl + fl + tw + '</svg></i>')


def metal_push_svg(pre, sfx=''):
    return mt_face_svg(pre, sfx) + mt_decor_svg(pre, sfx)


def mt_piece(pre, kind):
    """押した時に 飛びちる かけら（data URI の SVG）：sh＝銀（金）の かけら・s＝きらっ"""
    M = MT_PAL[pre]
    c0, c1, c2 = M['chip']
    if kind == 'sh':
        return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
                f"<stop offset='0' stop-color='{c0}'/><stop offset='.42' stop-color='{c1}'/><stop offset='.55' stop-color='{c2}'/><stop offset='1' stop-color='{c0}'/>"
                f"</linearGradient></defs><path d='M10 1L19 8L12 19L2 13Z' fill='url(#g)' stroke='{M['edge']}' stroke-width='.7'/>"
                "<path d='M10 2.6L17 8.2' stroke='#FFFFFF' stroke-width='1.2' opacity='.9'/></svg>")
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -10 20 20'><defs><radialGradient id='r'>"
            f"<stop offset='0' stop-color='{M['glow']}' stop-opacity='.9'/><stop offset='1' stop-color='{M['glow']}' stop-opacity='0'/></radialGradient></defs>"
            "<circle r='8' fill='url(#r)'/>"
            f"<path d='M0 -9.5Q1.3 -1.3 9.5 0Q1.3 1.3 0 9.5Q-1.3 1.3 -9.5 0Q-1.3 -1.3 0 -9.5Z' fill='{M['star']}'/><circle r='1.4' fill='#FFFFFF'/></svg>")


def metal_burst(pre, n=28, seed=59):
    """押した瞬間に、銀（金）の かけら・きらっ・こまかい光の粒が ぱっと広がる。まん中に 横に のびる光・銀（金）の 光の輪が 2重に広がる"""
    rnd = random.Random(seed + (0 if pre == 'ag' else 7))
    kinds = ['sh', 's', 'g', 'sh', 's', 'g', 'sh', 's', 'sh', 'g']
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(85, 170)
        x, y = math.cos(a) * dist * 1.25, math.sin(a) * dist * .88 - 24
        k = kinds[i % len(kinds)]
        z = dict(sh=rnd.uniform(14, 20), s=rnd.uniform(16, 24), g=rnd.uniform(6, 9))[k]
        r = rnd.choice((-1, 1)) * rnd.uniform(120, 360)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--r:{r:.0f}deg;--d:{rnd.uniform(0, .12):.2f}s"></i>'
    out += '<i class="lf"></i><i class="ring"></i><i class="ring b"></i>'
    return f'<div class="clips {pre}" aria-hidden="true">{out}</div>'


MT_CSS = r'''
/* ---------- @N帯の的中ボタン：@NでできたPUSH（まさちゃんの指定） ----------
   面は みがいた @N の板：上は 空の映りこみ（白く明るい）・まん中に 地平の映りこみ（こい帯）・下は また明るく・こまかい ヘアライン・上に つやの光。
   「PUSH」は @N の 立体の字（こいふち・下に 厚み・上に 光のふち）。光の帯が 1.8秒ごとに ななめに すうっと 通る（2本）・面の あちこちで 0.32秒ごとに きらっ。
   @N の ふち（光る線・みぞ・@N の帯・こいふち）・@N の 厚み・まわりに @N の光。ふちを 光が2つ ぐるっと回る・まわりで 大きい きらっ（横に のびる光）・
   光の粒が 下から上へ ふわっと のぼる。上下の動きは的中と同じ。
   押すと ぎゅっと ちぢんで ふくらみ（強く光らせない）、@N の かけら・きらっ・光の粒が はじけ、まん中に 横に のびる光・@N の 光の輪が 2重に広がる */
.@P{--pr:26px;--pushA:@PA;--pushB:@PB;--pushC:#FFFFFF;--rim:@R3;--rimD:@R4;--pushFace:linear-gradient(180deg,@PLATE)}
.push.@P{box-shadow:inset 0 2px 0 rgba(255,255,255,.95),inset 0 -5px 8px @INS,0 0 0 2.5px @R1,0 0 0 5px @R2,0 0 0 8.5px @R3,0 0 0 10.5px @R4,
  0 8px 0 10.5px @D1,0 10px 0 10.5px @D2,0 0 26px 14px @AU1,0 0 64px 26px @AU2,0 22px 34px rgba(0,0,0,.45)}
.push.@P span{color:transparent;text-shadow:none}
.push.@P::after{border-color:@RING}
.@P .@Pf{position:absolute;left:0;top:0;width:200px;height:100px;border-radius:26px;overflow:hidden;pointer-events:none;font-style:normal}
.@P .@Pf svg{display:block;width:200px;height:100px}
.@P .@Pd{position:absolute;left:-40px;top:-30px;width:280px;height:160px;pointer-events:none;z-index:3;font-style:normal}
.@P .@Pd svg{display:block;width:280px;height:160px;overflow:visible}
.@P .@Psh{transform-box:view-box;transform-origin:0 0;animation:@PShine 1.8s ease-in-out infinite}
.@P .@Psh.b{animation-delay:.16s}
@keyframes @PShine{0%{transform:translateX(0)}55%,100%{transform:translateX(330px)}}
.@P .@Pgl{opacity:0;animation:@PGl 1.6s ease-in-out infinite}
@keyframes @PGl{0%,50%,100%{opacity:0;transform:scale(.2) rotate(0deg)}64%{opacity:1;transform:scale(1.15) rotate(45deg)}80%{opacity:.25;transform:scale(.5) rotate(80deg)}}
.@P .@Prl{animation:@PRim 1.3s linear infinite}
@keyframes @PRim{from{stroke-dashoffset:0}to{stroke-dashoffset:-50}}
.@P .@Ptw{animation:@PTw 2.2s ease-in-out infinite}
@keyframes @PTw{0%,100%{opacity:.3;transform:scale(.45) rotate(0deg)}45%{opacity:1;transform:scale(1.15) rotate(30deg)}60%{opacity:.85;transform:scale(.9) rotate(40deg)}}
.@P .@Pfl{opacity:0;animation:@PFl 2.6s linear infinite}
@keyframes @PFl{0%{opacity:0;transform:translate(0,0)}15%{opacity:1}45%{opacity:.35}70%{opacity:1}100%{opacity:0;transform:translate(6px,-118px)}}
.tap.@P{color:@TAP;text-shadow:@TAPS}
.pressed.@P{border-radius:26px;box-shadow:0 0 0 2.5px @R1,0 0 0 5px @R2,0 0 0 8.5px @R3,0 0 0 10.5px @R4,0 8px 0 10.5px @D1,0 10px 0 10.5px @D2;animation-name:@PPress}
@keyframes @PPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.07)}100%{transform:scale(1.5);opacity:0}}   /* 強く光らせない */
.clips.@P{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.@P i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);animation:@PFly 1.4s cubic-bezier(.15,.7,.3,1) calc(var(--d) + .1s) both;background:center/contain no-repeat}
.clips.@P .sh{background-image:url("SH")}
.clips.@P .s{background-image:url("SP")}
.clips.@P .g{border-radius:1px;background:linear-gradient(135deg,@C0 0%,@C1 45%,@C2 100%)}
.clips.@P .lf{left:-110px;top:-2px;width:220px;height:4px;border-radius:2px;background:linear-gradient(90deg,rgba(255,255,255,0),#FFFFFF 50%,rgba(255,255,255,0));animation:@PLf .5s ease-out .08s both}
.clips.@P .ring{left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:5px solid @RING;box-shadow:0 0 18px @AU2;animation:@PRing .8s ease-out .1s forwards}
.clips.@P .ring.b{border-width:3px;animation-delay:.28s}
@keyframes @PFly{0%{opacity:0;transform:translate(0,0) rotate(0) scale(.3)}10%{opacity:1}55%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}
  100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 60px)) rotate(calc(var(--r) * 1.4)) scale(.7)}}
@keyframes @PLf{0%{opacity:0;transform:scaleX(.1)}30%{opacity:1;transform:scaleX(1)}100%{opacity:0;transform:scaleX(1.3)}}
@keyframes @PRing{0%{opacity:.95;transform:scale(.3)}100%{opacity:0;transform:scale(2.2)}}
@media (prefers-reduced-motion:reduce){.@P .@Psh,.@P .@Pgl,.@P .@Prl,.@P .@Ptw,.@P .@Pfl,.@P [class*="@Plg"]{animation:none}.@P .@Psh,.@P .@Pgl,.@P .@Prl,.@P .@Pfl,.@P [class*="@Plg"],.clips.@P{display:none}}
'''


def mt_css(pre):
    M = MT_PAL[pre]
    rep = dict(N=MT_NAME[pre], PA=M['plate'][3][1], PB=M['depth'][1], PLATE=','.join(f'{c} {o * 100:g}%' for o, c in M['plate']),
               INS=M['inS'], R1=M['rings'][0], R2=M['rings'][1], R3=M['rings'][2], R4=M['rings'][3], D1=M['depth'][0], D2=M['depth'][1],
               AU1=M['aura'][0], AU2=M['aura'][1], RING=M['ring'], TAP=M['tap'][0], TAPS=M['tap'][1], C0=M['chip'][0], C1=M['chip'][1], C2=M['chip'][2])
    css = re.sub(r'@(PA|PB|PLATE|INS|R1|R2|R3|R4|D1|D2|AU1|AU2|RING|TAPS|TAP|C0|C1|C2)\b', lambda m: rep[m.group(1)], MT_CSS.replace('@N', rep['N']))
    css = css.replace('@P', pre)
    css = css.replace('@media (prefers-reduced-motion:reduce){', mt_letter_css(pre) + '@media (prefers-reduced-motion:reduce){', 1)
    return css.replace('"SH"', '"' + ss_uri(mt_piece(pre, 'sh')) + '"').replace('"SP"', '"' + ss_uri(mt_piece(pre, 's')) + '"')


def mt_letter_css(pre, period=1.8):
    """字のかどの きらっ：面の光の帯が そこを通った時に（1.8秒ごと）"""
    out = ''
    for i, (x, y, L) in enumerate(MT_LETTER):
        t = mt_sheen_t(x, y) + .02
        p = lambda v: f'{min(max(v, 0), period) / period * 100:.1f}%'
        out += (f'.{pre} .{pre}lg{i}{{opacity:0;animation:{pre}Lg{i} {period:g}s linear infinite}}'
                f'@keyframes {pre}Lg{i}{{0%,{p(t - .04)}{{opacity:0;transform:scale(0) rotate(0deg)}}{p(t + .1)}{{opacity:1;transform:scale(1.3) rotate(35deg)}}'
                f'{p(t + .42)},100%{{opacity:0;transform:scale(0) rotate(80deg)}}}}\n')
    return out


AG_CSS = mt_css('ag')
AU_CSS = mt_css('au')


# ---------- マスター帯の的中ボタン：説明書の上の絵と 同じ 長方形の テンゲルの PUSHが 緑の雷を まとう（まさちゃんの指定） ----------
# 1回目「テンゲルのアイコンのpushボタンが緑の雷を纏っている」→ 3回目（説明書の上の絵の スクショ）「テンゲルのアイコンpushボタン 写真みたいな長方形にして！」
TG_W, TG_H, TG_R = 300, 164, 15     # 説明書の上の絵（1200×655）と 同じ 横長・角の丸み（説明書の ページでは 357px で 18）
TG_GREEN = dict(core='#F4FFF8', mid='#6BFFAE', glow='#26FF82')
TG_PUSH = (200.9, 135, 27)          # 「PUSH」の まん中の x・字の下の線・字の大きさ：消した 版の行の所（「テンゲル」の札の下。札の まん中は 元の絵の x 803.5）


def tg_push_img():
    """ボタンの 面の絵（キャンバスの id：tengel_blobs.json の push＝flat/tengel_run.py の tengel_push.webp：説明書の上の絵から 版の行を 消しただけ）"""
    return '/_blob/' + json.load(open(f'{K}/tengel_blobs.json'))['push']


def tg_ring(g, n=96):
    """ボタンの ふち（外へ g・角は 丸く）を 1周する点（と 外向き）：上の辺の 左はしから 時計回りに 長さで 等分"""
    W, H, r = TG_W, TG_H, TG_R
    R = r + g
    arc = math.pi * R / 2
    segs = [((r, -g), (1, 0), W - 2 * r, (0, -1)), ((W - r, r), -math.pi / 2),
            ((W + g, r), (0, 1), H - 2 * r, (1, 0)), ((W - r, H - r), 0.0),
            ((W - r, H + g), (-1, 0), W - 2 * r, (0, 1)), ((r, H - r), math.pi / 2),
            ((-g, H - r), (0, -1), H - 2 * r, (-1, 0)), ((r, r), math.pi)]
    total = 2 * (W - 2 * r) + 2 * (H - 2 * r) + 4 * arc
    out = []
    for i in range(n):
        u = i / n * total
        for k, s in enumerate(segs):
            L = s[2] if len(s) == 4 else arc
            if u < L or k == len(segs) - 1:
                break
            u -= L
        if len(s) == 4:
            (x0, y0), (dx, dy), _, nrm = s
            p = (x0 + dx * u, y0 + dy * u)
        else:
            (cx, cy), a0 = s
            a = a0 + u / R
            p, nrm = (cx + R * math.cos(a), cy + R * math.sin(a)), (math.cos(a), math.sin(a))
        out.append((p, nrm))
    return out


# 緑の雷（2回目の指定「濃い緑のビリビリも混ぜて・それぞれ消えたりついたり・ピクセル1番細い線に」）：壁紙（tengel_wall.py）と 同じ 作り方・同じ色。
# ボタンの ふちに そって TG_BOLT_N 本。1本ずつ べつべつに ついたり消えたり（1回に 2〜6回 ちらちら・そのたび 形が かわる）
TG_BOLT_N = 32                      # ふちが 長くなったので 20 → 32（ふちの 長さあたりの 本数は 正方形の時と 同じ）
TG_BOLT_VAR = 3
TG_BOLT_P = (0.8, 0.95, 1.1, 1.25, 1.4, 1.6, 1.8)
TG_RING_N = 272                     # ふちの 1周（外へ 7.5 で 約950px）を 約3.5px ごとに
TG_SC = .6                          # 線の はば（壁紙の 0.6倍：芯 0.42px＝画面の 約1画素）


def tg_bolt_shape(i0, n, g, rnd):
    """ふちに そった いなずま 1つ：(main の点, 枝の list)。枝は 外へ・ときどき 角を こえて 面に かかる"""
    import tengel_wall as TW
    ring = tg_ring(g, TG_RING_N)
    base = [ring[(i0 + k) % TG_RING_N] for k in range(n + 1)]
    off = [0.0] * (n + 1)

    def rec(k0, k1, amp):
        if k1 - k0 < 2:
            return
        m = (k0 + k1) // 2
        off[m] = (off[k0] + off[k1]) / 2 + rnd.gauss(0, 1) * amp
        rec(k0, m, amp * .62)
        rec(m, k1, amp * .62)
    rec(0, n, 4.2)
    pts, out = [], []
    for k, (p, nrm) in enumerate(base):
        o = min(max(off[k] + rnd.uniform(-.6, .6) * (0 < k < n), -3.0), 6.5)
        pts.append((p[0] + nrm[0] * o, p[1] + nrm[1] * o))
        out.append(nrm)
    brs = TW.branches(pts, rnd, out, n=(1, 3), length=(5.0, 17.0), spread=(.3, 1.0), sub=.35)
    if rnd.random() < .3:                                    # 面に かかる 小さな いなずま
        j = rnd.randrange(len(pts) // 4, len(pts) - len(pts) // 4)
        q, nrm = pts[j], out[j]
        L = rnd.uniform(8, 15)
        a = math.atan2(-nrm[1], -nrm[0]) + rnd.uniform(-.5, .5)
        brs.append(TW.frac(q, (q[0] + math.cos(a) * L, q[1] + math.sin(a) * L), rnd, rough=.24, seg=2.4))
    return pts, brs


def tg_plan(seed=73):
    """[(色, 1回りの秒, 形ごとの 光る間, {形: (main, 枝)})]"""
    rnd = random.Random(seed)
    plans = []
    for j in range(TG_BOLT_N):
        i0 = int(TG_RING_N * (j + rnd.uniform(-.3, .3)) / TG_BOLT_N) % TG_RING_N
        n = rnd.randint(14, 30)
        g = rnd.uniform(5.0, 10.0)
        kind = ('hi', 'lo')[j % 2] if rnd.random() < .8 else ('lo', 'hi')[j % 2]
        P = rnd.choice(TG_BOLT_P)
        t, ranges = rnd.uniform(0, P), [[] for _ in range(TG_BOLT_VAR)]
        for k in range(rnd.randint(2, 6)):
            dur = rnd.uniform(.035, .08)
            ranges[k % TG_BOLT_VAR].append((t, t + dur))
            t += dur + rnd.uniform(.025, .07)
        shapes = {v: tg_bolt_shape(i0, n, g, rnd) for v in range(TG_BOLT_VAR) if ranges[v]}
        plans.append((kind, P, ranges, shapes))
    return plans


TG_PLAN = tg_plan()


def tg_bolt_css():
    """ボタンの いなずまの CSS（1本・1形ずつ visibility を step-end で）。視差効果を減らすなら 半分の 本の はじめの形だけ 止めて出す（.tgS）"""
    import tengel_wall as TW
    css = ['.tg .tgE{visibility:hidden}' + TW.bolt_css('tg', '.tg', TG_SC) + TW.bolt_css('tgx', '.clips.tg', .9)]
    for j, (kind, P, ranges, shapes) in enumerate(TG_PLAN):
        for v in shapes:
            css.append(f'.tg .tgE{j}v{v}{{animation:tgE{j}v{v} {P:g}s step-end infinite}}' + TW.vis_kf(f'tgE{j}v{v}', ranges[v], P))
    return '\n'.join(css) + '\n@media (prefers-reduced-motion:reduce){.tg .tgE{animation:none}.tg .tgS{visibility:visible}}\n'


def tg_face_svg(sfx=''):
    """テンゲルの 長方形の PUSH：面（300×164・角の丸み15で 切りぬく）＝ 説明書の上の絵と 同じ（外の すじの わく・パネル・盾のエンブレム・
       TENGER の金の文字・「テンゲル」の金の札）。消した 版の行の所（札の下）に 金の「PUSH」（上は 明るい金・まん中は こい金・こげ茶のふち・下に 厚み）。
       上に うすい つやの光"""
    K_, T_, G_ = (f'tg{c}{sfx}' for c in 'KTG')
    W, H = TG_W, TG_H
    px, py, fs = TG_PUSH
    top = py - fs * .74                     # 字の上（Dela Gothic One の 大文字の 高さ 約0.74）
    defs = (f'<defs><clipPath id="{K_}"><rect width="{W}" height="{H}" rx="{TG_R}"/></clipPath>'
            f'<linearGradient id="{T_}" gradientUnits="userSpaceOnUse" x1="0" y1="{top:.1f}" x2="0" y2="{py:g}"><stop offset="0" stop-color="#FFF4C8"/>'
            '<stop offset=".45" stop-color="#E9C46A"/><stop offset=".55" stop-color="#B98A30"/><stop offset="1" stop-color="#F3D88C"/></linearGradient>'
            f'<linearGradient id="{G_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".13"/>'
            '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>')
    tx = lambda extra: (f'<text x="{px:g}" y="{py:g}" text-anchor="middle" font-family="Dela Gothic One,sans-serif" font-size="{fs:g}" letter-spacing="1.4" '
                        f'stroke-linejoin="round"{extra}>PUSH</text>')
    body = (f'<rect width="{W}" height="{H}" fill="#0A1C23"/><image href="{tg_push_img()}" width="{W}" height="{H}" preserveAspectRatio="none"/>'
            + tx(' fill="#3A2A08" stroke="#3A2A08" stroke-width="2.6" transform="translate(0 2)"')
            + tx(f' fill="url(#{T_})" stroke="#2A1E06" stroke-width="2.2" paint-order="stroke"')
            + tx(' fill="none" stroke="#FFF6D2" stroke-width=".6" opacity=".7" transform="translate(0 -.6)"')
            + f'<path d="M6 34C50 12 100 6 150 6S250 12 294 34V5H6Z" fill="url(#{G_})"/>')
    return (f'<i class="tgf" aria-hidden="true"><svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}'
            f'<g clip-path="url(#{K_})">{body}</g></svg></i>')


def tg_decor_svg(sfx='', seed=73):
    """PUSHを まく 緑の雷（明るい緑と 濃い緑・1本ずつ ついたり消えたり：TG_PLAN・.tgE）・まわりの 緑の光（ゆっくり 強く弱く・.tgH）・外へ とぶ 火花（.tgs）"""
    import tengel_wall as TW
    rnd = random.Random(seed)
    W, H = TG_W, TG_H
    defs, body = '', ''
    for j, (kind, P, ranges, shapes) in enumerate(TG_PLAN):
        for v, (main, brs) in shapes.items():
            pid = f'tgE{j}v{v}{sfx}'
            defs += TW.bolt_defs(pid, main, brs)
            still = ' tgS' if j % 2 == 0 and v == min(shapes) else ''
            body += (f'<g class="tgE tgE{j}v{v}{still}">{TW.bolt_use(pid + "m", kind, pre="tg")}'
                     + (TW.bolt_use(pid + 'b', kind, 'br', pre='tg') if brs else '') + '</g>')
    halo = (f'<rect class="tgH" x="-9" y="-9" width="{W + 18}" height="{H + 18}" rx="{TG_R + 9}" fill="none" stroke="{TG_GREEN["glow"]}" stroke-width="14" opacity=".22"/>')
    sp = ''
    ring = tg_ring(10, 28)
    for i in range(14):
        p, nrm = ring[(i * 9) % len(ring)]
        L = rnd.uniform(16, 30)
        sp += (f'<circle class="tgs" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{rnd.uniform(1.1, 1.9):.1f}" fill="{TG_GREEN["core"]}" '
               f'style="--x:{nrm[0] * L:.1f}px;--y:{nrm[1] * L:.1f}px;animation-delay:{-i * .17:.2f}s"/>')
    return (f'<i class="tgd" aria-hidden="true"><svg viewBox="-50 -50 {W + 100} {H + 100}" width="{W + 100}" height="{H + 100}"><defs>{defs}</defs>'
            + halo + f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{body}</g>' + sp + '</svg></i>')


def tengel_push_svg(sfx=''):
    return tg_face_svg(sfx) + tg_decor_svg(sfx)


def tg_edge(a):
    """まん中から 角度 a の向きに すすんで ボタンの ふち（長方形）に 当たる点"""
    c, s = math.cos(a), math.sin(a)
    t = min(TG_W / 2 / max(abs(c), 1e-9), TG_H / 2 / max(abs(s), 1e-9))
    return c * t, s * t


def tengel_burst(n=24, seed=79):
    """押した瞬間に、明るい緑と 濃い緑の いなずまが ボタンの ふちから まわりへ ほとばしり（2回 ちらっ・細い線に 枝わかれ）、緑と白の 火花が とびちる。
       まん中から 横に のびる光・ボタンの形の 緑の 光の輪が 2重に広がる"""
    import tengel_wall as TW
    rnd = random.Random(seed)
    lines = dict(hi=[], lo=[])
    for i in range(12):
        a = 2 * math.pi * (i + rnd.uniform(-.3, .3)) / 12
        ex, ey = tg_edge(a)
        L = rnd.uniform(50, 100)
        p0 = (ex * .9, ey * .9)
        p1 = (ex + math.cos(a) * L, ey + math.sin(a) * L)
        main = TW.frac(p0, p1, rnd, rough=.2, seg=3.5)
        brs = TW.branches(main, rnd, (math.cos(a), math.sin(a)), n=(1, 2), length=(12.0, 30.0), spread=(.3, .8), sub=.4)
        lines['lo' if i % 3 == 0 else 'hi'] += [main] + brs
    defs = ''.join(f'<path id="tgB{k}" d="{" ".join(TW.pd(p) for p in v)}"/>' for k, v in lines.items())
    bolts = (f'<svg class="tgb" viewBox="-300 -230 600 460" width="600" height="460"><defs>{defs}</defs>'
             f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{TW.bolt_use("tgBlo", "lo", pre="tgx")}{TW.bolt_use("tgBhi", "hi", pre="tgx")}</g></svg>')
    out = ''
    for i in range(n):
        a = math.radians(-90 + (i / n - .5) * 340 + rnd.uniform(-8, 8))
        dist = rnd.uniform(80, 170)
        x, y = math.cos(a) * dist * 1.6, math.sin(a) * dist * .9 - 20
        k = 's' if i % 3 else 'w'
        z = rnd.uniform(5, 9)
        out += f'<i class="{k}" style="--x:{x:.0f}px;--y:{y:.0f}px;--z:{z:.0f}px;--d:{rnd.uniform(0, .12):.2f}s"></i>'
    out += '<i class="lf"></i><i class="ring"></i><i class="ring b"></i>'
    return f'<div class="clips tg" aria-hidden="true">{bolts}{out}</div>'


TG_CSS = r'''
/* ---------- マスター帯の的中ボタン：説明書の上の絵と 同じ 長方形の テンゲルの PUSHが 緑の雷を まとう（まさちゃんの指定） ----------
   ボタンは 説明書の上の絵と 同じ 横長の 長方形（300×164・角の丸み15）：外の すじの わく・パネル・盾のエンブレム・TENGER・「テンゲル」の札。
   消した 版の行の所（札の下）に 金の「PUSH」。金の細いふち・紺のふち・金のふち・こい金の厚み・まわりに 緑の光。
   明るい緑と 濃い緑の いなずまが ボタンの ふちに そって 32本（1本ずつ べつべつに ついたり消えたり：1回に 2〜6回 ちらちら・そのたび 形が かわる。
   線は いちばん細く・外へ 枝わかれ・ときどき 角を こえて 面に かかる）・火花が 外へ とぶ。上下の動きは的中と同じ。
   押すと ぎゅっと ちぢんで ふくらみ（強く光らせない）、明るい緑と 濃い緑の いなずまが ふちから まわりへ ほとばしり（2回 ちらっ）、緑と白の 火花・
   ボタンの形の 緑の 光の輪が 2重に広がる */
.tg{--pr:15px;--pushA:#E9C873;--pushB:#0A1B22;--pushC:#F4DC96;--rim:#E9C873;--rimD:#0A1B22;--pushFace:#0A1C23}
.push.tg{width:300px;height:164px;box-shadow:0 0 0 2px #E9C873,0 0 0 4.5px #0A1B22,0 0 0 6px #B48A3A,0 7px 0 6px #6E5216,0 8.5px 0 6px #0A1B22,
  0 0 18px 3px rgba(38,255,130,.2),0 0 50px 16px rgba(38,255,130,.1),0 22px 34px rgba(0,0,0,.5)}   /* 緑の光は ひかえめに（濃い緑の いなずまが 見えるように） */
.push.tg span{color:transparent;text-shadow:none}
.push.tg::after{border-color:rgba(107,255,174,.9)}
.pshadow.tg{width:300px}
.tg .tgf{position:absolute;left:0;top:0;width:300px;height:164px;border-radius:15px;overflow:hidden;pointer-events:none;font-style:normal}
.tg .tgf svg{display:block;width:300px;height:164px}
.tg .tgd{position:absolute;left:-50px;top:-50px;width:400px;height:264px;pointer-events:none;z-index:3;font-style:normal}
.tg .tgd svg{display:block;width:400px;height:264px;overflow:visible}
.tg .tgH{animation:tgH 1.4s ease-in-out infinite alternate}
@keyframes tgH{from{opacity:.06}to{opacity:.16}}
.tg .tgs{opacity:0;transform-box:fill-box;transform-origin:50% 50%;animation:tgS 1.7s ease-out infinite}
@keyframes tgS{0%{opacity:0;transform:translate(0,0) scale(1)}6%{opacity:1}40%{opacity:0;transform:translate(var(--x),var(--y)) scale(.4)}100%{opacity:0;transform:translate(var(--x),var(--y)) scale(.4)}}
.tap.tg{color:#F4DC96;text-shadow:0 2px 0 #0A1B22,0 0 12px rgba(38,255,130,.85)}
.pressed.tg{width:300px;height:164px;margin:-82px 0 0 -150px;border-radius:15px;background:#0A1C23;box-shadow:0 0 0 2px #E9C873,0 0 0 4.5px #0A1B22,0 0 0 6px #B48A3A,0 7px 0 6px #6E5216,0 0 18px 3px rgba(38,255,130,.2);animation-name:tgPress}
@keyframes tgPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.05)}100%{transform:scale(1.3);opacity:0}}   /* 強く光らせない */
.clips.tg{position:absolute;z-index:4;left:50%;top:calc(50% - 40px);width:0;height:0}
.clips.tg .tgb{position:absolute;left:-300px;top:-230px;width:600px;height:460px;overflow:visible;visibility:hidden;animation:tgBolt .5s step-end .06s both}
@keyframes tgBolt{0%{visibility:visible}16%{visibility:hidden}24%{visibility:visible}52%,100%{visibility:hidden}}
.clips.tg i{position:absolute;opacity:0;left:calc(var(--z) / -2);top:calc(var(--z) / -2);width:var(--z);height:var(--z);border-radius:50%;animation:tgFly 1.1s cubic-bezier(.15,.7,.3,1) calc(var(--d) + .08s) both}
.clips.tg .s{background:radial-gradient(circle,#F4FFF8 0 30%,rgba(107,255,174,.9) 50%,rgba(38,255,130,0) 72%)}
.clips.tg .w{background:radial-gradient(circle,#FFFFFF 0 35%,rgba(244,255,248,.6) 55%,rgba(244,255,248,0) 72%)}
.clips.tg .lf{left:-190px;top:-2px;width:380px;height:4px;border-radius:2px;background:linear-gradient(90deg,rgba(107,255,174,0),#F4FFF8 50%,rgba(107,255,174,0));animation:tgLf .45s ease-out .06s both}
.clips.tg .ring{left:-150px;top:-82px;width:300px;height:164px;border-radius:15px;border:4px solid rgba(107,255,174,.9);box-shadow:0 0 18px rgba(38,255,130,.6);animation:tgRing .8s ease-out .1s forwards}
.clips.tg .ring.b{border-width:2.5px;animation-delay:.26s}
@keyframes tgFly{0%{opacity:0;transform:translate(0,0) scale(.4)}10%{opacity:1}60%{opacity:1;transform:translate(var(--x),var(--y)) scale(1)}100%{opacity:0;transform:translate(calc(var(--x) * 1.1),calc(var(--y) + 40px)) scale(.6)}}
@keyframes tgLf{0%{opacity:0;transform:scaleX(.1)}30%{opacity:1;transform:scaleX(1)}100%{opacity:0;transform:scaleX(1.3)}}
@keyframes tgRing{0%{opacity:.9;transform:scale(.92)}100%{opacity:0;transform:scale(1.6)}}
@media (prefers-reduced-motion:reduce){.tg .tgH,.tg .tgs{animation:none}.tg .tgs,.clips.tg{display:none}}
''' + tg_bolt_css()


def form(bets, pay_total, note, fin=(6, 2, 10)):
    rows = ''.join(f'<li><span class="bt">{t}</span><span class="bc">{combo(c, s)}</span><span class="by">{y}</span></li>' for t, c, s, y, _, _ in bets)
    return f'''  <main class="ct">
    <section class="card">
      <h2 class="ch">レースの結果を記録</h2>
      <div class="rh"><span class="rk">9R</span><span class="rs">1400m ダ・良・12頭・予約したレース</span></div>
      <p class="lab">着順（馬番）</p>
      <div class="fin"><span class="k">1着</span>{num(fin[0])}<span class="k">2着</span>{num(fin[1])}<span class="k">3着</span>{num(fin[2])}</div>
      <p class="lab">予約した買い目</p>
      <ul class="bets">{rows}</ul>
      <div class="pay"><span>払戻（回収額）</span><b>{pay_total}</b></div>
      <button class="rec" type="button" onClick="{{{{toPush}}}}"><svg {SVG_A}><path d="M5 4.5h11l3 3v12H5z"></path><path d="M8 4.5v5h7v-5M8 19.5v-5h8v5"></path></svg>記録する</button>
      <p class="note">{note}</p>
    </section>
  </main>'''


def bet_rows(bets, kind, mark=()):
    """ボードの行：当たった買い目だけ（ハズレは全部・払戻0円）。デカ・ど的中・隠れど的中は3連単の行に虹色のふち（.top）"""
    rows, k = '', 0
    for t, c, s, y, p, hit in bets:
        if kind != 'miss' and not hit:
            continue
        cls = ' class="top"' if (kind in ('big', 'fz', 'hidden') and t == '3連単') else ''
        pay = '0円' if kind == 'miss' else p
        rows += (f'<li{cls} style="--i:{k}"><span class="bt tag">{t}</span><span class="bc">{combo(c, s, mark if t == "3連単" else ())}</span>'
                 f'<span class="by">{y}</span><span class="bp">{pay}</span></li>')
        k += 1
    return rows, k


def board(kind, bets, total, rib='', mark=(), tid=THEME, race='9R'):
    """結果のボード（壁紙のテーマ tid のボード・boards.py）。kind：hit・big・fz・hidden・miss ／ rib：見出しの下の帯 ／ mark：虹色の輪をつける馬番"""
    rows, _ = bet_rows(bets, kind, mark)
    return board_html(tid, kind, rows, total, race=race, rib=rib)


FZ_X = 11    # 見本の超大穴の馬（11番・11番人気）
# フリーズの時刻（押してから）：押した瞬間（0秒）にフリーズ（白く光って横に流れるノイズ）・B＝青い画面と白い光・W＝まわりが暗くなって青白い横一本線（細い電気）
# ・Z＝線が点に縮んで消える（このあと真っ暗1.5秒）・M＝虹色ネオンのカット・R＝結果（虹色の大当たりの画面・上に「ど的中」・テーマのボード）
# まさちゃんの指定：前の「押した瞬間の画面がバグる」はやめて、押した瞬間にフリーズ（パチスロのプチュン）
FZ_T = dict(B=.3, W=.45, Z=.62, M=2.52, R=6.9)
# 虹色ネオンのカットの始まり（<M> からの秒）。パチンコの当たりのように速く・激しく：T1「どてき！！」→ T2 → T3（×2）→ T4「ど！」×4 → T5「ど的中！！！！」
# T5 の「！」がそろうのは <M+T5+.23>、そこから HOLD 秒で結果（R ＝ M＋T5＋.23＋HOLD）
MT_T = dict(T2=.6, T3=1.15, T4=1.75, T5=2.65, HOLD=1.5)
assert abs(FZ_T['R'] - (FZ_T['M'] + MT_T['T5'] + .23 + MT_T['HOLD'])) < 1e-9
assert abs(FZ_T['M'] - (FZ_T['Z'] + .4 + 1.5)) < 1e-9    # 線が消えてから真っ暗1.5秒
LINE_Y = 422    # 青白い横一本線の高さ（px）
def svg_url(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe="/:=' .,-") + '")'


def fz_sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


def fz_css():
    """FREEZE_CSS の <M+.85>・<W+.07> などを秒に直す（<LINE-150> などは px）・ネオンの線画の絵を入れる"""
    css = re.sub(r'<LINE([+\-]\d+)?>', lambda m: f'{LINE_Y + int(m.group(1) or 0)}', FREEZE_CSS)
    css = re.sub(r'<([A-Z][A-Z0-9.+\-]*)>', lambda m: fz_sec(eval(m.group(1), {}, dict(FZ_T, **MT_T))), css)
    for k, v in (('NGLOW', blobs['fz_nglow']), ('NCORE', blobs['fz_ncore'])):
        css = css.replace(k, v)
    return css + MT['css'] + '\n'


def glitter(n, seed):
    """PUSHの面のラメ（小さな光の点がばらばらに光る）"""
    rnd = random.Random(seed)
    return ''.join(f'<b style="--x:{rnd.uniform(3, 97):.1f}%;--y:{rnd.uniform(6, 94):.1f}%;--s:{rnd.uniform(1.6, 3.6):.1f}px;--d:{rnd.uniform(0, 1.6):.2f}s"></b>' for _ in range(n))


def fz_push():
    """フリーズのPUSHの画面"""
    return f'''<div class="dim"></div>
    <div class="aura"></div><div class="prays"></div>
    <div class="spk">{sparkles(30, 21)}</div>
    <div class="pbox">
      <button class="push fz" type="button" onClick="{{{{toReveal}}}}" aria-label="フリーズ的中ボタン"><i class="halo" aria-hidden="true"><i><b></b></i></i><i class="face"></i><i class="gloss"></i><i class="glit">{glitter(56, 37)}</i><i class="spk">{sparkles(7, 31, white=True)}</i><span>PUSH</span></button>
      <div class="pshadow fz"></div>
      <p class="tap fz">タップ!!</p>
    </div>
    <div class="edge"></div><div class="frame"><b></b></div>'''


def bez_prog(t, x1, y1, x2, y2):
    """cubic-bezier の時刻 t（0〜1）のときの進み（0〜1）"""
    bx = lambda s: 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
    by = lambda s: 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if bx(m) < t else (lo, m)
    return by((lo + hi) / 2)


# ---------- フリーズ（押した瞬間から）：まさちゃんの送ってくれたパチスロのフリーズの動画のような動き（台の絵や音は使わない） ----------
FR = 1 / 30      # 1コマ（液晶のコマ）
# 横に流れる帯の色：明るい色（明るさ0.8より上）を多めに、あざやかな水色・緑を少し（帯が変わるのは2コマに1回だけ）
SMEAR_HI = ('#FFFFFF', '#E9FFFF', '#FFF35C', '#D2FF4A', '#9CFF6A', '#FAFFA8')
SMEAR_MID = ('#4FE3FF', '#3CFF8A', '#00C8FF', '#7DF0FF')


def bolt(rnd, pts, rough, depth):
    """稲妻：折れ線 pts を中点ずらしで細かくギザギザにする（深さ depth・ずらす強さ rough）"""
    for _ in range(depth):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy) or 1
            off = rnd.uniform(-1, 1) * rough * L
            out += [((ax + bx) / 2 - dy / L * off, (ay + by) / 2 + dx / L * off), (bx, by)]
        pts = out
    return pts


def bolt_d(pts):
    """path の d（座標は2倍の整数・相対で短く。viewBox は 780×1688）"""
    q = [(round(x * 2), round(y * 2)) for x, y in pts]
    return f'M{q[0][0]} {q[0][1]}l' + ' '.join(f'{b[0] - a[0]} {b[1] - a[1]}' for a, b in zip(q, q[1:]))


def bolts_line(rnd, x0, x1, n, wander=9, rmin=60):
    """横一本線にそって走る電気 n 本（x0〜x1 のあいだ）＋枝。戻り値 [(点, 太さ)]"""
    out = []
    for _ in range(n):
        a = rnd.uniform(x0, max(x0, x1 - rmin))
        b = min(x1, a + rnd.uniform(rmin, max(rmin, x1 - x0)))
        k = max(2, round((b - a) / 42))
        base = [(a + (b - a) * j / k, LINE_Y + (rnd.uniform(-wander, wander) if 0 < j < k else rnd.uniform(-2, 2))) for j in range(k + 1)]
        pts = bolt(rnd, base, .3, 3)
        out.append((pts, 1.6))
        for _ in range(rnd.randint(0, 3)):            # 枝（上か下へ）
            px, py = pts[rnd.randrange(1, len(pts) - 1)]
            ang = rnd.uniform(.35, 1.2) * rnd.choice([-1, 1]) + rnd.choice([0, math.pi])
            L = rnd.uniform(10, 42)
            out.append((bolt(rnd, [(px, py), (px + math.cos(ang) * L, py + math.sin(ang) * L)], .32, 3), 1.0))
    return out


def bolt_curve(rnd, xa, xb, h):
    """横の帯の上に弓なりに走る電気（動画の青い画面の大きな稲妻のように）"""
    k = 9
    base = [(xa + (xb - xa) * j / k, LINE_Y - 4 * h * (j / k) * (1 - j / k) + rnd.uniform(-5, 5)) for j in range(k + 1)]
    return bolt(rnd, base, .24, 3)


def freeze_layers(seed=93):
    """押した瞬間のフリーズ（HTML）：白く光る → 横に流れる帯 → 赤い粒 → 青い画面と白い光・細い電気 → 横一本線と電気 → 点に縮む・光の粒"""
    rnd = random.Random(seed)
    B, W, Z = FZ_T['B'], FZ_T['W'], FZ_T['Z']
    sec = lambda v: f'{v - .0001:.4f}'.rstrip('0').rstrip('.') + 's'     # コマの切れ目より少し前から（60コマ/秒の画面でもすき間ができないように）
    sm, nz, arcs, dust = [], [], [], []

    def it(lst, d, t, **v):
        lst.append('<i style="' + f'--d:{sec(d)};--t:{sec(t)};' + ''.join(f'--{k}:{x}{"px" if isinstance(x, (int, float)) else ""};' for k, x in v.items()) + '"></i>')
    # 白く光る2コマ（0〜.067）：青いブロックがまるく集まる・縦に抜けた線
    for f in range(2):
        d = f * FR
        cx, cy = 236 + f * 6, 470 - f * 4
        for _ in range(16):
            a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(26, 60)
            s = rnd.choice([4, 5, 6, 8, 10])
            it(nz, d, FR, x=round(cx + math.cos(a) * r), y=round(cy + math.sin(a) * r * 1.1), w=s, h=s + rnd.choice([0, 2, 6]),
               c=rnd.choice(['#3F72FF', '#2C5BF0', '#6E9BFF', '#8DB4FF']))
        for _ in range(9):
            it(nz, d, FR, x=round(rnd.uniform(150, 330)), y=round(rnd.uniform(60, 300)), w=1, h=round(rnd.uniform(40, 170)), c='rgba(70,120,255,.55)')
        for _ in range(3):         # 細い明るい帯（始まり）
            it(sm, d, FR, x=round(rnd.uniform(-40, 160)), y=round(rnd.uniform(80, 760)), w=round(rnd.uniform(120, 360)), h=rnd.choice([2, 3, 5]), c=rnd.choice(SMEAR_HI[2:]))
    # 横に流れる帯（.067〜.2）：2つの場面（2コマずつ）。2コマめは帯が少し横にずれる。後の場面は下のほうに緑と黄色の大きい帯
    for s in range(2):
        d = (2 + s * 2) * FR
        for _ in range(15):
            low = s == 1 and rnd.random() < .55
            y = rnd.uniform(400, 820) if low else rnd.uniform(10, 830)
            x, w = rnd.uniform(-90, 230), rnd.uniform(130, 480)
            h = rnd.choice([3, 5, 8, 14, 22, 34, 52, 76])
            c = rnd.choice(SMEAR_MID) if rnd.random() < .3 else rnd.choice(SMEAR_HI)
            for f in range(2):
                it(sm, d + f * FR, FR, x=round(x + f * rnd.uniform(-14, 14)), y=round(y), w=round(w), h=h, c=c)
        for _ in range(4):
            it(nz, d + rnd.choice([0, FR]), FR, x=round(rnd.uniform(-20, 250)), y=round(rnd.uniform(40, 800)), w=round(rnd.uniform(60, 240)), h=rnd.choice([1, 2, 2, 3]),
               c=rnd.choice(['#3A6BFF', '#1F4FE0', '#5C8BFF', '#FF4FD8']))
        for _ in range(5):
            s_ = rnd.choice([5, 6, 8])
            it(nz, d + rnd.choice([0, FR]), FR, x=round(rnd.uniform(160, 330)), y=round(rnd.uniform(150, 420)), w=s_, h=s_ + 4, c='#3060F0')
    # 赤い粒（.2〜.267・2コマ）：まぶしい帯のまわりに
    for f in range(2):
        d = .2 + f * FR
        for _ in range(70):
            it(nz, d, FR, x=round(rnd.uniform(-4, 386)), y=round(LINE_Y + rnd.gauss(0, 26) - 6 + f * 8), w=rnd.choice([2, 3, 4, 5, 7]), h=rnd.choice([1, 2, 2, 3]),
               c=rnd.choice(['#FF2D55', '#FF4F70', '#E8003A', '#FF7A8E']))
    # 点々（<B+.033>〜・1コマ）：縦の短い点々があちこちに
    d = B + FR
    for _ in range(90):
        y = LINE_Y + rnd.gauss(0, 120)
        it(nz, d, FR, x=round(rnd.uniform(0, 389)), y=round(y), w=rnd.choice([1, 1, 2]), h=rnd.choice([3, 4, 6, 9]),
           c=rnd.choice(['#FFE65A', '#FF6A5A', '#FFFFFF', '#7AF0FF', '#FFC2E0']))
    # 電気：1コマ（1/30秒）ずつ形が変わる
    plan = [(.2 + FR, 1, 1), (8 * FR, 2, 2), (B, 1, 2), (B + FR, 0, 2), (B + 2 * FR, 1, 2), (B + 3 * FR, 1, 2), (W - FR / 2, 0, 3)]
    for d, ncurve, nline in plan:
        for _ in range(ncurve):
            xa = rnd.uniform(-20, 120)
            arcs.append((bolt_curve(rnd, xa, xa + rnd.uniform(160, 300), rnd.uniform(40, 120)), 1.4, d))
        for pts, sw in bolts_line(rnd, 0, 390, nline, wander=14):
            arcs.append((pts, sw, d))
    f = 0
    while W + f * FR < Z - .005:           # 横一本線（<W>〜<Z>）：線の全体に3〜4本ずつ（＋枝）
        for pts, sw in bolts_line(rnd, -6, 396, rnd.choice([3, 4]), wander=12, rmin=140):
            arcs.append((pts, sw, W + f * FR))
        f += 1
    f = 0
    while Z + f * FR < Z + .17:            # 縮むとき（<Z>〜）：残っている線の上だけ
        d = Z + f * FR
        hw = 195 * (1 - bez_prog(min(1, (d + FR / 2 - Z) / .18), .55, 0, .9, .45))
        if hw > 12:
            for pts, sw in bolts_line(rnd, 195 - hw, 195 + hw, 3, wander=5, rmin=min(60, hw)):
                arcs.append((pts, sw * .85, d))
        f += 1
    paths = ''.join(f'<path style="--d:{sec(d)};--t:{sec(FR)};stroke-width:{sw:g}" d="{bolt_d(pts)}"></path>' for pts, sw, d in arcs)
    # 散る光の粒：線から下へ落ちながら消える（縮むときは残っている線から）
    for _ in range(54):
        d = rnd.uniform(W + .05, Z + .2)
        hw = 195 if d < Z else 195 * (1 - bez_prog(min(1, (d - Z) / .18), .55, 0, .9, .45))
        x = 195 + rnd.uniform(-hw, hw)
        it(dust, d, rnd.uniform(.3, .6), x=round(x, 1), y=round(LINE_Y + rnd.uniform(-2, 2), 1), s=round(rnd.uniform(1.2, 2.4), 1),
           dx=round(rnd.uniform(-50, 50)), dy=round(rnd.uniform(6, 60)))
    return (f'<div class="pc" aria-hidden="true"><div class="pf p0"></div><div class="pf pa"></div><div class="pf pb"></div><div class="sm">{"".join(sm)}</div><div class="pf p1"></div>'
            f'<div class="pf p2"></div><div class="pf p2b"></div><div class="pfx"></div><div class="nz">{"".join(nz)}</div><div class="pf psl"></div>'
            f'<div class="pcl"></div><div class="pcf"><b class="f1"></b><b class="f2"></b><b class="f3"></b></div>'
            f'<svg class="pca" viewBox="0 0 780 1688">{paths}</svg><div class="pcd">{"".join(dust)}</div></div>')


def zigzag():
    """S2：ネオンのギザギザ（12の角の星）が16重。外ほど太い"""
    out = []
    for k in range(16):
        R = 80 * 1.3 ** k
        pts = ' '.join(f'{(R if i % 2 == 0 else R * .6) * math.cos(math.pi * i / 12 + (k % 2) * math.pi / 12):.0f},'
                       f'{(R if i % 2 == 0 else R * .6) * math.sin(math.pi * i / 12 + (k % 2) * math.pi / 12):.0f}' for i in range(24))
        h, sw = (k * 53 + 300) % 360, 5 + k * 2.6
        out.append(f'<polygon points="{pts}" stroke="hsl({h},100%,58%)" stroke-width="{sw * 2.4:.1f}" stroke-opacity=".32"></polygon>'
                   f'<polygon points="{pts}" stroke="hsl({h},100%,60%)" stroke-width="{sw:.1f}"></polygon>'
                   f'<polygon points="{pts}" stroke="#FFFFFF" stroke-width="{sw * .3:.1f}"></polygon>')
    return f'<svg viewBox="-1400 -1400 2800 2800" fill="none" stroke-linejoin="miter" aria-hidden="true">{"".join(out)}</svg>'


def neon_icon(alt=False):
    return f'<div class="nic{" alt" if alt else ""}"><div class="nv"><i class="ng"></i><i class="nc"></i></div></div>'


def ring(x, y, d, g):
    return f'<i class="tr" style="--x:{x:g}px;--y:{y:g}px;--d:{fz_sec(d)};--g:{g}"></i>'


# ---------- 筆の字（ど的中の演出の文字）：brush.py で描いた形（brush_glyphs.json・フォントなし） ----------
BZ = json.load(open(f'{K}/brush_glyphs.json', encoding='utf-8'))
BZ_RB = ((0, '#FF2D55'), (.18, '#FF9500'), (.36, '#FFEA00'), (.54, '#2BFF4F'), (.72, '#00D9FF'), (.88, '#3D63FF'), (1, '#C23CFF'))   # 虹色
BZ_EX = ('#FFD447', '#D9971A', '#A6680A', '#6E4205', '#3E2402')   # 金の立体（字に近い → 遠い。CSS の drop-shadow を5つ重ねる）
BZ_PAL = dict(   # 虹色の向き（1：上 → 下・2：左上 → 右下・3：右上 → 左下）・まわりの光の色・爆発の光の色（2つ）
    pink=(1, '#FF3BD2', '#FFD0F7', '#FF3BD2'), blue=(2, '#2FB4FF', '#D2FBFF', '#2FB4FF'), gold=(3, '#FFB300', '#FFF8C0', '#FFB300'),
    green=(2, '#3CFF6A', '#EEFFC0', '#3CFF6A'), white=(1, '#FFFFFF', '#FFFBE0', '#FF5A00'), fire=(1, '#FF9A00', '#FFF6C8', '#FF6A00'))
_bzn = [0]


def bz_defs():
    """筆の字の形・虹色（3つの向き）・金・つや・光の筋（ページに1回だけ。字は <use> でここを指す）"""
    def lg(i, x1, y1, x2, y2):
        return (f'<linearGradient id="bzR{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
                + ''.join(f'<stop offset="{o:g}" stop-color="{c}"></stop>' for o, c in BZ_RB) + '</linearGradient>')
    shapes = ''.join(f'<path id="bz-{g["id"]}" d="{g["d"]}" fill-rule="evenodd" clip-rule="evenodd"></path>'
                     f'<clipPath id="bzc-{g["id"]}"><use href="#bz-{g["id"]}"></use></clipPath>' for g in BZ.values())
    grads = (lg(1, 0, 0, 0, 1) + lg(2, 0, 0, 1, 1) + lg(3, 1, 0, 0, 1)
             + '<linearGradient id="bzGd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFBE0"></stop><stop offset=".28" stop-color="#FFD54A"></stop>'
               '<stop offset=".5" stop-color="#A86400"></stop><stop offset=".53" stop-color="#FFE88A"></stop><stop offset=".8" stop-color="#FFB000"></stop>'
               '<stop offset="1" stop-color="#6A3A00"></stop></linearGradient>'
             + '<linearGradient id="bzGl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".6"></stop>'
               '<stop offset=".4" stop-color="#FFFFFF" stop-opacity=".1"></stop><stop offset=".41" stop-color="#FFFFFF" stop-opacity="0"></stop></linearGradient>'
             + '<linearGradient id="bzSh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"></stop>'
               '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".9"></stop><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"></stop></linearGradient>')
    return f'<svg class="bzd" width="0" height="0" aria-hidden="true"><defs>{shapes}{grads}</defs></svg>'


def bz_word(text, fs, rb=1, kern=-90, scales=None, dys=None, shine=None):
    """筆の字の部品（1文字＝1000 → fs px）。字の並びのまん中（横のまん中・縦の 500）が、置く場所のまん中になる。
       戻り値：W・H（px）・vb（viewBox）・defs（1回だけ置く：字の並び bw・面 bf）・stack（重ねる順）"""
    _bzn[0] += 1
    n = _bzn[0]
    x = 0
    items = face = clip = ''
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for i, c in enumerate(text):
        g = BZ[c]
        s = scales[i] if scales else 1
        dy = dys[i] if dys else 0
        tr = f'translate({x:.0f} {dy:.0f})' + (f' scale({s:g})' if s != 1 else '')
        u = f'href="#bz-{g["id"]}"'
        items += f'<use {u} transform="{tr}"></use>'
        face += (f'<g transform="{tr}" clip-path="url(#bzc-{g["id"]})"><use {u} class="w"></use>'
                 f'<use {u} transform="translate(9 12)" fill="url(#bzR{rb})"></use><use {u} class="h"></use></g>')
        clip += f'<use {u} transform="{tr}"></use>'
        bx = g['bbox']
        x0, y0 = min(x0, x + bx[0] * s), min(y0, dy + bx[1] * s)
        x1, y1 = max(x1, x + bx[2] * s), max(y1, dy + bx[3] * s)
        x += g['adv'] * s + kern
    cx = (x - kern) / 2
    m = 70    # 黒いふちのぶん
    hw, hh = max(cx - x0, x1 - cx) + m, max(500 - y0, y1 - 500) + m
    vb = f'{cx - hw:.0f} {500 - hh:.0f} {2 * hw:.0f} {2 * hh:.0f}'
    defs = f'<g id="bw{n}">{items}</g><g id="bf{n}">{face}</g>'
    stack = f'<use href="#bw{n}" class="k"></use><use href="#bw{n}" class="g"></use><use href="#bw{n}" class="d"></use><use href="#bf{n}"></use>'
    if shine is not None:    # 光がサッと走る（面だけ）
        defs += f'<clipPath id="bzs{n}">{clip}</clipPath>'
        stack += (f'<g clip-path="url(#bzs{n})"><g transform="skewX(-18)"><rect class="shn" x="{cx - hw - 420:.0f}" y="{500 - hh:.0f}" width="420" height="{2 * hh:.0f}" '
                  f'fill="url(#bzSh)" style="--sd:{shine};--s1:{2 * hw + 900:.0f}px"></rect></g></g>')
    return dict(n=n, W=round(2 * hw * fs / 1000, 1), H=round(2 * hh * fs / 1000, 1), vb=vb, defs=f'<defs>{defs}</defs>', stack=stack, fs=fs)


def bz_svg(wd, glow, defs=True, flat=False):
    """筆の字の絵：金の立体（drop-shadow を重ねる）とまわりの光は CSS の filter（大きさに合わせる）。flat：filter なし（横ズレの帯用・軽く）"""
    fs = wd['fs']
    if flat:
        return f'<svg class="bz" viewBox="{wd["vb"]}" width="{wd["W"]:g}" height="{wd["H"]:g}" aria-hidden="true">{wd["stack"]}</svg>'
    ex = ' '.join(f'drop-shadow({fs * .0063:.2f}px {fs * .0126:.2f}px 0 {c})' for c in BZ_EX)
    flt = f'filter:{ex} drop-shadow(0 0 {fs * .025:.1f}px rgba(255,255,255,.75)) drop-shadow(0 0 {fs * .08:.1f}px {glow})'
    return (f'<svg class="bz" viewBox="{wd["vb"]}" width="{wd["W"]:g}" height="{wd["H"]:g}" style="{flt}" aria-hidden="true">'
            f'{wd["defs"] if defs else ""}{wd["stack"]}</svg>')


def bz_sil(wd, cls):
    """色ずれ用の影（字の形＋黒いふちの太さ・赤か水色）"""
    return f'<svg class="bz {cls}" viewBox="{wd["vb"]}" width="{wd["W"]:g}" height="{wd["H"]:g}" aria-hidden="true"><use href="#bw{wd["n"]}" class="k"></use></svg>'


def bzt(text, cx, cy, fs, d, pal, r=0, z=1, **kw):
    """止まった筆の字（T5）：ポンと出て、少し傾いたまま"""
    rb, glow = BZ_PAL[pal][:2]
    wd = bz_word(text, fs, rb=rb, **kw)
    return (f'<div class="bzt" style="z-index:{z};--x:{cx}px;--y:{cy}px;--w:{wd["W"]:g}px;--h:{wd["H"]:g}px;--d:{fz_sec(d)};--r:{r}deg">'
            f'{bz_svg(wd, glow)}</div>')


VT = 1.0   # 文字のブルブル：1回り1秒で4か所 → 1秒に4回、大きくガクガク動く（筆の字は明るさの差が大きいので、前の1秒に約7回だと点めつが多すぎた）


def gq(text, cx, cy, fs, d, pal, r=0, seed=0, z=1):
    """バグる筆の字：まん中(cx, cy)・大きさ fs・傾き r・色 pal（BZ_PAL）・z（重なったときの上下。先に読む字を上に）"""
    rnd = random.Random(seed)
    rb, glow = BZ_PAL[pal][:2]
    wd = bz_word(text, fs, rb=rb, kern=-80)
    cp = bz_svg(wd, glow, defs=False, flat=True)    # 横ズレの帯（1コマずつ）は立体と光なしで軽く
    a1, a2 = rnd.choice([-1, 1]) * rnd.uniform(.12, .2) * fs, rnd.choice([-1, 1]) * rnd.uniform(.1, .18) * fs
    va, vr, vd = rnd.uniform(.075, .095) * fs, rnd.choice([-1, 1]) * rnd.uniform(4, 6), -rnd.uniform(0, VT)
    return (f'<div class="gq" style="z-index:{z};--x:{cx}px;--y:{cy}px;--w:{wd["W"]:g}px;--h:{wd["H"]:g}px;--d:{fz_sec(d)};--r:{r}deg;'
            f'--a1:{a1:.0f}px;--a2:{a2:.0f}px;--va:{va:.1f}px;--vr:{vr:.1f}deg;--vt:{VT}s;--vd:{vd:.2f}s"><div class="gj">'
            f'{bz_sil(wd, "gr")}{bz_sil(wd, "gc")}{bz_svg(wd, glow)}<i class="s s1">{cp}</i><i class="s s2">{cp}</i></div></div>')


def blocks(n, d0, d1, seed):
    """まわりの小さなブロック（ネオンの色・1コマずつ・毎回ちがう場所）"""
    rnd = random.Random(seed)
    out = ''
    for _ in range(n):
        out += (f'<i style="--x:{rnd.uniform(0, 340):.0f}px;--y:{rnd.uniform(60, 780):.0f}px;--w:{rnd.uniform(24, 90):.0f}px;--h:{rnd.uniform(4, 16):.0f}px;'
                f'--c:{rnd.choice(["#FF2BD6", "#2FF3FF", "#FFF23A", "#3CFF6A", "#FFFFFF"])};--d:{fz_sec(rnd.uniform(d0, d1))};--t:.034s"></i>')
    return f'<div class="bk">{out}</div>'


# T1〜T3 の「どてき！！」：(字, x, y, 大きさ, 傾き)。ど・て・き と「！」「！」（音の gen_sfx.py も、この順と時刻で鳴らす）
DOTEKI = 'どてき！！'


def mt_layers(seed=71):
    """虹色ネオンのカット（T1〜T5）：まさちゃんの指定の文字「どてき！！」「どてき！！」「どてき！！どてき！！」「ど！ど！ど！ど！」「ど的中！！！！」
       文字は筆の字（パチンコのロゴのような字体と虹色）。どてき！！・ど！は1文字ずつ大きくバグる（場所・大きさ・向きはバラバラ）、ど的中は止まる。
       パチンコの当たりのように速く・激しく：文字はたたきつけるように出て、「！」「ど！」「ど的中」が出るたびに爆発（星形の光・衝撃の輪・光の破片）"""
    M = FZ_T['M']
    T2, T3, T4, T5 = (M + MT_T[k] for k in ('T2', 'T3', 'T4', 'T5'))
    rnd = random.Random(seed)
    # T1：まん中で大爆発 → 「ど」「て」「き」「！」・右に大きな「！」（爆発）
    t1 = burst(190, 420, M + .02, 290, '#FFF0FA', '#FF2BD6', 61, n=20, z=0)
    t1 += ''.join(gq(c, x, y, fs, M + .05 + i * .05, 'pink', r, seed=10 + i, z=6 - i) for i, (c, x, y, fs, r) in enumerate(
        (('ど', 104, 240, 200, -12), ('て', 282, 330, 178, 9), ('き', 112, 560, 196, 7), ('！', 276, 636, 186, -8))))
    t1 += burst(332, 472, M + .27, 210, '#E8FFFF', '#3FF4FF', 62, n=12, z=0) + gq('！', 332, 472, 212, M + .27, 'pink', 14, seed=14, z=7)
    t1 += blocks(8, M + .06, M + .5, 21)
    # T2：左上から右下へ階段のように（最後の「！」で爆発）
    t2 = ''.join(gq(c, x, y, fs, T2 + .03 + i * .045, 'blue', r, seed=20 + i, z=9 - i) for i, (c, x, y, fs, r) in enumerate(
        (('ど', 80, 168, 172, -10), ('て', 162, 322, 156, 8), ('き', 240, 480, 174, -6), ('！', 292, 636, 164, 12), ('！', 338, 762, 170, 18))))
    t2 += burst(338, 762, T2 + .21, 250, '#FFE8FA', '#FF4FD8', 63, n=12, z=0) + blocks(8, T2 + .04, T2 + .48, 22)
    # T3：「どてき！！」を2つ（大きく・画面からはみ出てもいい。上は右上がり・下は右下がり。1文字ずつ上下にずらす。最後の「！」で爆発）
    t3 = ''
    for k, (x0, y0, x1, y1, fs, d0, pal, c1, c2) in enumerate(((36, 404, 362, 86, 134, T3 + .03, 'gold', '#FFF8C0', '#FFB300'),
                                                               (36, 548, 362, 796, 132, T3 + .22, 'green', '#F0FFC8', '#3CFF6A'))):
        for i, c in enumerate(DOTEKI):
            u = i / 4
            x, y = round(x0 + (x1 - x0) * u), round(y0 + (y1 - y0) * u + rnd.uniform(-12, 12))
            t3 += gq(c, x, y, fs + rnd.randint(-6, 12), d0 + i * .04, pal, round(rnd.uniform(-12, 12)), seed=30 + k * 10 + i, z=19 - k * 10 - i)
            if i == 4:
                t3 += burst(x, y, d0 + i * .04, 240, c1, c2, 64 + k, n=12, z=0)
    t3 += blocks(8, T3 + .03, T3 + .52, 23)
    # T4：「ど！」×4（大きく・はみ出てもいい・バラバラ・1つずつ光の破片が飛び散る）
    t4 = ''
    for i, (x, y, fs, r, pal) in enumerate(((158, 172, 196, -12, 'pink'), (238, 370, 182, 10, 'blue'), (148, 566, 204, 7, 'gold'), (240, 752, 190, -9, 'green'))):
        d = T4 + .12 + i * .17
        t4 += burst(x, y, d, 420, BZ_PAL[pal][2], BZ_PAL[pal][3], 70 + i, n=18, star=False, ring=False, z=0) + gq('ど！', x, y, fs, d, pal, r, seed=40 + i)
    t4 += blocks(10, T4 + .12, T4 + .85, 24)
    # T5：「ど的中」（大爆発・光がサッと走る）「！！！！」（そろってから HOLD 秒）
    t5 = burst(195, 365, T5 + .02, 320, '#FFFBE0', '#FF5A00', 80, n=22, ring=False, z=0)
    t5 += bzt('ど的中', 195, 360, 134, T5 + .02, 'white', r=-6, z=2, scales=(.78, 1, 1), dys=(-150, 0, 0), kern=-90, shine=fz_sec(T5 + .35))
    for i, ((x, y, fs, r), pal) in enumerate(zip(((58, 530, 108, -14), (148, 566, 120, 8), (240, 518, 104, -6), (326, 568, 116, 12)), ('pink', 'gold', 'green', 'blue'))):
        t5 += bzt('！', x, y, fs, T5 + .08 + i * .05, pal, r=r, z=3 + i)
    t5_rings = ''.join(f'<i class="rg" style="--s:{sz}px;--d:{fz_sec(T5 - k * .4)}"></i>' for k, sz in enumerate((250, 410, 600, 830)))
    t5_waves = '<div class="rw">' + ''.join(f'<i style="--d:{fz_sec(T5 + k * .45)}"></i>' for k in range(3)) + '</div>'
    html = f'''<div class="mt" aria-hidden="true">
      <div class="sc t1"><div class="bg"></div><div class="dk"></div>{neon_icon()}<div class="dk2"></div>{t1}</div>
      <div class="sc t2"><div class="stf"></div><div class="spd"></div><div class="orb"></div><div class="spk">{sparkles(26, 47)}</div>{t2}</div>
      <div class="sc t3"><div class="zz">{zigzag()}</div>{t3}</div>
      <div class="sc t4"><div class="stf"></div><div class="glw"></div><div class="spk">{sparkles(22, 43, white=True)}</div>{t4}</div>
      <div class="sc t5"><div class="nr g"></div><div class="nr"></div><div class="nw"></div>{t5_waves}{t5_rings}<div class="core"></div><div class="bsg"><div class="bs"></div></div>
        <div class="spk">{sparkles(34, 59)}</div>{t5}</div>
    </div>'''
    return dict(css='', html=html)


def embers(n, seed):
    """虹色のきらめき（下から上へ）"""
    rnd = random.Random(seed)
    R = FZ_T['R']
    return ''.join(f'<i style="--x:{rnd.uniform(0, 390):.0f}px;--s:{rnd.uniform(3, 6):.1f}px;--t:{rnd.uniform(1.6, 3.2):.2f}s;--d:{R + rnd.uniform(0, 2):.2f}s;--dx:{rnd.uniform(-60, 60):.0f}px;'
                   f'--c:hsl({i * 360 // n},100%,62%)"></i>' for i in range(n))


def dlogo():
    """結果の上の「ど的中」：筆の字（虹色・金と黒のふち・金の立体・つや・光がサッと走る）＋うしろの炎＋上の小さい英語＋きらめき"""
    R = FZ_T['R']
    wd = bz_word('ど的中', 156, rb=1, kern=-90, scales=(.78, 1, 1), dys=(-100, 0, 0), shine=fz_sec(R + .3))
    word = f'<div class="dw" style="--w:{wd["W"]:g}px;--h:{wd["H"]:g}px">{bz_svg(wd, "#FFB000")}</div>'
    glints = ''.join(f'<b style="--x:{x}px;--y:{y}px;--s:{s}px;--d:{R + .3 + i * .12:.2f}s"></b>'
                     for i, (x, y, s) in enumerate(((52, 70, 22), (150, 44, 28), (262, 40, 24), (352, 92, 30), (300, 178, 20), (86, 176, 24))))
    rnd = random.Random(23)
    flames = ''
    for i in range(15):
        cx = 12 + i * 26.3 + rnd.uniform(-7, 7)
        w, h, base = rnd.uniform(46, 78), rnd.uniform(120, 200) * (1.15 if 4 <= i <= 10 else .85), 168 + rnd.uniform(-6, 6)
        d = (f'M{cx - w / 2:.0f} {base:.0f} C{cx - w / 2:.0f} {base - h * .45:.0f} {cx - w * .12:.0f} {base - h * .55:.0f} {cx + rnd.uniform(-6, 6):.0f} {base - h:.0f} '
             f'C{cx + w * .12:.0f} {base - h * .55:.0f} {cx + w / 2:.0f} {base - h * .45:.0f} {cx + w / 2:.0f} {base:.0f} Z')
        flames += f'<path d="{d}" fill="url(#dflg)" style="--t:{rnd.uniform(.45, .7):.2f}s;--d:{-rnd.uniform(0, .6):.2f}s"></path>'
    flames = f'<g mask="url(#dflk)">{flames}</g>'
    grad = ('<defs><linearGradient id="dflg" x1="0" y1="0" x2="390" y2="0" gradientUnits="userSpaceOnUse">'     # 虹色の炎（横に虹色）
            + ''.join(f'<stop offset="{o:g}" stop-color="{c}"></stop>' for o, c in BZ_RB)
            + '</linearGradient><linearGradient id="dflm" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"></stop>'
            '<stop offset=".12" stop-color="#FFFFFF"></stop><stop offset=".55" stop-color="#FFFFFF" stop-opacity=".85"></stop><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"></stop>'
            '</linearGradient><mask id="dflk" maskUnits="userSpaceOnUse" x="0" y="-60" width="390" height="260"><rect x="0" y="-60" width="390" height="260" fill="url(#dflm)"></rect></mask></defs>')
    return (f'<div class="dlg" role="img" aria-label="ど的中"><div class="dfl"></div><svg class="ffl" viewBox="0 0 390 200" aria-hidden="true">{grad}{flames}</svg>'
            f'<div class="dr"></div><div class="dsb">SUPER LONGSHOT</div>{word}<div class="dsp">{glints}</div></div>')


def fz_layers(bets, total, kind='fz'):
    """フリーズの押したあと（下から）：黒 → 結果（虹色の大当たりの画面・上に「ど的中」・テーマのボード）→ ネオンのカット → 押した瞬間のフリーズ（プチュン）→ 白い光
       kind：fz（超大穴の馬の帯）／hidden（隠れど的中：デカ的中が化けた帯）"""
    if kind == 'hidden':
        rib = '<div class="zrib"><b class="zt">隠れ</b><span>デカ的中が ど的中に化けた！</span></div>'
        bd = board('hidden', bets, total, rib=rib)
    else:
        rib = f'<div class="zrib"><b class="zt">超大穴</b>{num(FZ_X, " zx")}<span>{FZ_X}番人気が3連単に！</span></div>'
        bd = board('fz', bets, total, rib=rib, mark=(FZ_X,))
    R = FZ_T['R']
    return f'''{bz_defs()}<div class="blk"></div>
    <div class="fin"><div class="fsk">
      <div class="fb"></div><div class="frr"></div><div class="frg"><i style="--d:{fz_sec(R + .1)}"></i><i style="--d:{fz_sec(R + 1)}"></i></div>
      {burst(195, 330, R + .02, 520, '#FFFFFF', '#FF3BD2', 90, n=22)}
      <div class="emb">{embers(36, 11)}</div>
      <div class="conf cb">{coins(22, 8, R)}</div>
      <div class="hb">{bd}</div>
      {dlogo()}
      <div class="conf">{confetti(40, 7, rainbow=True, d0=R)}</div>
    </div></div>
    {MT['html']}
    {FZ_HTML}
    <div class="xf" aria-hidden="true"><div class="rfl"></div></div>'''


FZ_HTML = freeze_layers()
MT = mt_layers()


PAGES = dict(   # 種類 → ファイル名・名前（見本の画面のタイトル）
    hit=('Fx_Hit.dc.html', '的中ボタン（デフォルト）'), big=('Fx_Big.dc.html', 'デカ的中ボタン（デフォルト）'),
    fz=('Fx_Freeze.dc.html', 'フリーズ的中ボタン（デフォルト）'), hidden=('Fx_Hidden.dc.html', '隠れど的中（デカ的中ボタン → ど的中）'),
    miss=('Fx_Miss.dc.html', 'ハズレ（ボードだけ）'),
    hit_gold=('Fx_HitGold.dc.html', '的中ボタン（カッコいい：黒と金のぷるんPUSH）'),
    hit_ranch=('Fx_HitRanch.dc.html', '的中ボタン（牧場：芝生のPUSH）'),
    hit_sakura=('Fx_HitSakura.dc.html', '的中ボタン（桜：桜がついたPUSH）'),
    hit_sea=('Fx_HitSea.dc.html', '的中ボタン（海：海の模様のPUSH）'),
    hit_autumn=('Fx_HitAutumn.dc.html', '的中ボタン（紅葉：紅葉がついたPUSH）'),
    hit_snow=('Fx_HitSnow.dc.html', '的中ボタン（雪：雪が積もったPUSH）'),
    hit_newyear=('Fx_HitNewYear.dc.html', '的中ボタン（お正月：初日の出が映ったPUSH）'),
    hit_news=('Fx_HitNews.dc.html', '的中ボタン（競馬新聞：新聞でできたPUSH）'),
    hit_ink=('Fx_HitInk.dc.html', '的中ボタン（水墨画：墨画でできたPUSH）'),
    hit_carousel=('Fx_HitCarousel.dc.html', '的中ボタン（メリーゴーランド：メリーゴーランドのPUSH）'),
    hit_stars=('Fx_HitStars.dc.html', '的中ボタン（星座：星でできたPUSH）'),
    hit_silks=('Fx_HitSilks.dc.html', '的中ボタン（勝負服：勝負服でできたPUSH）'),
    hit_neon=('Fx_HitNeon.dc.html', '的中ボタン（ネオン：ネオンでできたPUSH）'),
    hit_pixel=('Fx_HitPixel.dc.html', '的中ボタン（ドット絵：ドットでできたPUSH）'),
    hit_fireworks=('Fx_HitFireworks.dc.html', '的中ボタン（花火：花火でできたPUSH）'),
    hit_kids=('Fx_HitKids.dc.html', '的中ボタン（子供向け：毛糸でできたPUSH）'),
    hit_cute=('Fx_HitCute.dc.html', '的中ボタン（かわいい：ハートでできたPUSH）'),
    hit_sunset=('Fx_HitSunset.dc.html', '的中ボタン（夕焼け：夕日の映ったPUSH）'),
    hit_night=('Fx_HitNight.dc.html', '的中ボタン（ナイター：ナイター照明に照らされたPUSH）'),
    hit_marble=('Fx_HitMarble.dc.html', '的中ボタン（大理石：大理石でできたPUSH）'),
    hit_lucky=('Fx_HitLucky.dc.html', '的中ボタン（開運：小判でできたPUSH）'),
    hit_chalk=('Fx_HitChalk.dc.html', '的中ボタン（黒板：チョークで書いたPUSH）'),
    hit_silver=('Fx_HitSilver.dc.html', '的中ボタン（シルバー帯：シルバーでできたPUSH）'),
    hit_golden=('Fx_HitGolden.dc.html', '的中ボタン（ゴールド帯：ゴールドでできたPUSH）'),
    hit_tengel=('Fx_HitTengel.dc.html', '的中ボタン（マスター帯：緑の雷をまとう 説明書の上の絵と同じ 長方形の テンゲルのPUSH）'),
    hit_xmas=('Fx_HitXmas.dc.html', '的中ボタン（クリスマス：クリスマスツリーのPUSH）'),
    hit_halloween=('Fx_HitHalloween.dc.html', '的中ボタン（ハロウィン：かぼちゃのPUSH）'),
    hit_valentine=('Fx_HitValentine.dc.html', '的中ボタン（バレンタイン：チョコのPUSH）'),
    hit_whiteday=('Fx_HitWhiteDay.dc.html', '的中ボタン（ホワイトデー：マシュマロのPUSH）'))
BETS_HIT = [('馬単', [6, 2], '→', '100円', '1,840円', True), ('馬連', [2, 6], '-', '100円', '690円', True), ('3連単', [6, 10, 2], '→', '100円', '0円', False)]
BETS_BIG = [('3連単', [6, 2, 10], '→', '100円', '48,920円', True), ('馬単', [6, 2], '→', '100円', '1,840円', True), ('ワイド', [2, 10], '-', '100円', '0円', False)]
BETS_FZ = [('3連単', [FZ_X, 6, 2], '→', '100円', '286,370円', True), ('馬単', [FZ_X, 6], '→', '100円', '24,180円', True), ('ワイド', [2, FZ_X], '-', '100円', '4,950円', True)]
BETS_MISS = [('3連単', [6, 2, 10], '→', '100円', '0円', False), ('馬単', [6, 2], '→', '100円', '0円', False), ('ワイド', [2, 10], '-', '100円', '0円', False)]


def page(kind):
    """見本の画面（記録する → PUSH → タップ → 結果のボード）。kind：hit・big・fz・hidden（デカのPUSH → ど的中）・miss（PUSHなし）
       ・THEMED の種類（hit_gold など）＝そのテーマの見本（記録する画面とボードがそのテーマ・PUSHもそのテーマの形）"""
    th, page_kind = THEMED.get(kind, {}), kind
    kind, tid, pc = th.get('base', kind), th.get('tid', THEME), (' ' + th['push'] if th.get('push') else '')
    big = kind in ('big', 'hidden')          # PUSHはデカ（隠れど的中もデカのPUSH）
    fz = kind in ('fz', 'hidden')            # 押したあとは、ど的中
    fin = (6, 2, 10)
    if kind == 'fz':
        bets, total, fin = BETS_FZ, '315,500円', (FZ_X, 6, 2)
        note = f'3連単が当たって、3頭の中に超大穴（10〜12番人気）がいるので、記録するとフリーズ的中ボタンが出るよ（見本・架空のレース。{FZ_X}番が{FZ_X}番人気）'
    elif kind == 'hidden':
        bets, total = BETS_BIG, '50,760円'
        note = '3連単が当たったのでデカ的中ボタン。デカ的中の2〜7回に1回（ランダム）は隠れど的中で、押すとど的中になるよ（見本・架空のレース）'
    elif kind == 'big':
        bets, total, note = BETS_BIG, '50,760円', '3連単が当たったので、記録するとデカ的中ボタンが出るよ（見本・架空のレース）'
    elif kind == 'miss':
        bets, total, fin = BETS_MISS, '0円', (7, 1, 4)
        note = '外れたので、記録するとハズレのボードだけが出るよ（ボタンなし・見本・架空のレース）'
    else:
        bets, total, note = BETS_HIT, '2,530円', '3連単は外れ・馬単と馬連が当たったので、記録すると的中ボタンが出るよ（見本・架空のレース）'
    pb = ' big' if big else ''
    push = f'''  <sc-if value="{{{{isPush}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov{pb}">
    <div class="dim"></div>
    {'<div class="spk">' + sparkles(22, 5) + '</div>' if big else ''}
    <div class="pbox">
      <button class="push{pb}{pc}" type="button" onClick="{{{{toReveal}}}}" aria-label="{'デカ的中ボタン' if big else '的中ボタン'}">{'<i class="halo" aria-hidden="true"><i><b></b></i></i>' if big else ''}{turf_svg() if th.get('push') == 'gr' else ''}{sakura_push_svg() if th.get('push') == 'sk' else ''}{sea_push_svg() if th.get('push') == 'se' else ''}{momiji_push_svg() if th.get('push') == 'mo' else ''}{snow_push_svg() if th.get('push') == 'yk' else ''}{newyear_push_svg() if th.get('push') == 'ny' else ''}{news_push_svg() if th.get('push') == 'np' else ''}{ink_push_svg() if th.get('push') == 'nk' else ''}{carousel_push_svg() if th.get('push') == 'mg' else ''}{stars_push_svg() if th.get('push') == 'sz' else ''}{silks_push_svg() if th.get('push') == 'sj' else ''}{neon_push_svg() if th.get('push') == 'nn' else ''}{pixel_push_svg() if th.get('push') == 'dp' else ''}{fireworks_push_svg() if th.get('push') == 'hn' else ''}{keito_push_svg() if th.get('push') == 'ke' else ''}{kawaii_push_svg() if th.get('push') == 'kw' else ''}{sunset_push_svg() if th.get('push') == 'ss' else ''}{night_push_svg() if th.get('push') == 'nb' else ''}{marble_push_svg() if th.get('push') == 'mb' else ''}{koban_push_svg() if th.get('push') == 'kb' else ''}{chalk_push_svg() if th.get('push') == 'kk' else ''}{metal_push_svg(th['push']) if th.get('push') in ('ag', 'au') else ''}{tengel_push_svg() if th.get('push') == 'tg' else ''}{PE.push_svg(th['push']) if th.get('push') in PE.CODES else ''}<span>PUSH</span></button>
      <div class="pshadow{pb}{pc}"></div>
      <p class="tap{pb}{pc}">タップ！</p>
    </div>
  </div>
  </sc-if>'''
    nhit = len(bets) if kind == 'miss' else sum(1 for b in bets if b[5])
    if kind == 'big':
        layers = ('<div class="rbow"></div><div class="glow"></div><div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>'
                  '<div class="spk">' + sparkles(26, 9) + '</div>'
                  + burst(195, 371, .04, 600, '#FFF6C8', '#FFB21A', 5, n=18, z=5)          # 押した瞬間の爆発
                  + burst(195, 420, .55, 660, '#FFFFFF', '#FF3BB8', 6, n=14, star=False, z=5)   # ボードの着地（ボードのうしろ・輪と光の破片だけ）
                  + burst(195, 316, .7, 300, '#FFFFFF', '#FFE53B', 7, n=0, star=False, z=7))   # 「デカ的中!!」の輪
        conf, flash, cls = confetti(34, 3, rainbow=True), '<div class="flash"></div>', ' big big rv'
    elif kind == 'miss':
        layers, conf, flash, cls = '', '', '', ' miss'
    else:
        layers, conf, flash, cls = '<div class="rays"></div>', confetti(28, 2), '', ' hit'
    reveal = f'''  <sc-if value="{{{{isReveal}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov{cls}" style="--n:{nhit}">
    <div class="dim"></div>
    {layers}
    {'' if kind == 'miss' else f'<div class="pressed{pb}{pc}">{turf_svg() if th.get("push") == "gr" else ""}{sakura_push_svg() if th.get("push") == "sk" else ""}{sea_push_svg() if th.get("push") == "se" else ""}{momiji_push_svg("moP") if th.get("push") == "mo" else ""}{snow_push_svg("2") if th.get("push") == "yk" else ""}{newyear_push_svg("2") if th.get("push") == "ny" else ""}{news_push_svg("2") if th.get("push") == "np" else ""}{ink_push_svg("2") if th.get("push") == "nk" else ""}{carousel_push_svg("2") if th.get("push") == "mg" else ""}{stars_push_svg("2") if th.get("push") == "sz" else ""}{silks_push_svg("2") if th.get("push") == "sj" else ""}{neon_push_svg("2") if th.get("push") == "nn" else ""}{pixel_push_svg("2") if th.get("push") == "dp" else ""}{fireworks_push_svg("2") if th.get("push") == "hn" else ""}{keito_push_svg("2") if th.get("push") == "ke" else ""}{kawaii_push_svg("2") if th.get("push") == "kw" else ""}{sunset_push_svg("2") if th.get("push") == "ss" else ""}{night_push_svg("2") if th.get("push") == "nb" else ""}{marble_push_svg("2") if th.get("push") == "mb" else ""}{koban_push_svg("2") if th.get("push") == "kb" else ""}{chalk_push_svg("2") if th.get("push") == "kk" else ""}{metal_push_svg(th["push"], "2") if th.get("push") in ("ag", "au") else ""}{tengel_push_svg("2") if th.get("push") == "tg" else ""}{PE.push_svg(th["push"], "2") if th.get("push") in PE.CODES else ""}</div>'}{clippings() if th.get('push') == 'gr' else ''}{petal_burst() if th.get('push') == 'sk' else ''}{water_burst() if th.get('push') == 'se' else ''}{leaf_burst() if th.get('push') == 'mo' else ''}{snow_burst() if th.get('push') == 'yk' else ''}{gold_burst() if th.get('push') == 'ny' else ''}{paper_burst() if th.get('push') == 'np' else ''}{ink_burst() if th.get('push') == 'nk' else ''}{carousel_burst() if th.get('push') == 'mg' else ''}{stars_burst() if th.get('push') == 'sz' else ''}{silks_burst() if th.get('push') == 'sj' else ''}{neon_burst() if th.get('push') == 'nn' else ''}{pixel_burst() if th.get('push') == 'dp' else ''}{fireworks_burst() if th.get('push') == 'hn' else ''}{keito_burst() if th.get('push') == 'ke' else ''}{kawaii_burst() if th.get('push') == 'kw' else ''}{sunset_burst() if th.get('push') == 'ss' else ''}{night_burst() if th.get('push') == 'nb' else ''}{marble_burst() if th.get('push') == 'mb' else ''}{koban_burst() if th.get('push') == 'kb' else ''}{chalk_burst() if th.get('push') == 'kk' else ''}{metal_burst(th['push']) if th.get('push') in ('ag', 'au') else ''}{tengel_burst() if th.get('push') == 'tg' else ''}{PE.burst(th['push']) if th.get('push') in PE.CODES else ''}
    <div class="hb">{board(kind, bets, total, tid=tid)}</div>
    {f'<div class="conf">{conf}</div>' if conf else ''}
    {flash}
    <button class="close" type="button" onClick="{{{{toForm}}}}">とじる</button>
  </div>
  </sc-if>'''
    if kind == 'fz':
        push = f'''  <sc-if value="{{{{isPush}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov fz">
    {fz_push()}
  </div>
  </sc-if>'''
    if fz:
        reveal = f'''  <sc-if value="{{{{isReveal}}}}" hint-placeholder-val="{{{{false}}}}">
  <div class="ov fz" style="--n:{nhit}">
    {fz_layers(bets, total, kind)}
    <button class="close" type="button" onClick="{{{{toForm}}}}">とじる</button>
  </div>
  </sc-if>'''
    if kind == 'miss':
        push = ''
    css = COMMON_CSS.replace('RANCH', RANCH_VARS)
    if fz:
        css += BIG_CSS + BURST_CSS + fz_css()
    elif kind == 'big':
        css += BIG_CSS + BURST_CSS
    elif kind == 'miss':
        css += MISS_CSS
    else:
        css += HIT_CSS
    if th:
        css += theme_form_css(tid) + dict(gp=GP_CSS, gr=GR_CSS, sk=SK_CSS, se=SE_CSS, mo=MO_CSS, yk=YK_CSS, ny=NY_CSS, np=NP_CSS, nk=NK_CSS, mg=MG_CSS, sz=SZ_CSS, sj=SJ_CSS, nn=NN_CSS, dp=DP_CSS, hn=HN_CSS, ke=KE_CSS, kw=KW_CSS, ss=SS_CSS, nb=NB_CSS, mb=MB_CSS, kb=KB_CSS, kk=KK_CSS, ag=AG_CSS, au=AU_CSS, tg=TG_CSS, **PE.CSS).get(th.get('push'), '')
    css += board_css([tid])
    fn, name = PAGES[page_kind]
    fonts = ''.join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={f}&amp;display=swap">\n' for f in th.get('fonts', ()))
    hdr = HEADER
    if th.get('banner'):
        bsvg, bcss = theme_banner(th['banner'])
        hdr, css = header(svg=bsvg), css + bcss + '\n'
    starts = '["form","reveal"]' if kind == 'miss' else '["form","push","reveal"]'
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{name}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&amp;display=swap">
{fonts}<style>
{css}
</style>
</helmet>
<div class="ph">
{hdr}
{form(bets, total, note, fin)}
{push}
{reveal}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"start":{{"editor":"enum","options":{starts},"default":"form"}},"$preview":{{"width":390,"height":844}}}}'>
{page_js(page_kind)}</script>
</body>
</html>
'''


# ---------- 結果のボードの一覧（30テーマ × 的中・ハズレ ＋ ボードの種類） ----------
CELL_W, COLS, GGAP, GPAD = 752, 5, 28, 40
BOARDS_W, BOARDS_H = 2 * GPAD + COLS * CELL_W + (COLS - 1) * GGAP, 4280
OLD_DESC = dict(default='紺×金', ranch='黄緑', cute='ピンク', kids='薄い黄色×パウダーホワイト', gold='金色')


def theme_label(t):
    from themes20 import THEMES as T20
    for x in T20:
        if x['id'] == t['id']:
            return x['title']
    return f"{t['name']}（{OLD_DESC.get(t['id'], '')}）"


def boards_page():
    """30テーマの結果のボード（的中・ハズレ）と、ボードの種類（見本：いつもの）。動きなし・テーマの字はGoogle Fonts"""
    ids = [t['id'] for t in ORDERED]
    rib_fz = f'<div class="zrib"><b class="zt">超大穴</b>{num(FZ_X, " zx")}<span>{FZ_X}番人気が3連単に！</span></div>'
    rib_hd = '<div class="zrib"><b class="zt">隠れ</b><span>デカ的中が ど的中に化けた！</span></div>'
    kinds = [('hit', BETS_HIT, '2,530円', '', (), '的中（当たり）'), ('big', BETS_BIG, '50,760円', '', (), 'デカ的中（3連単が当たり）'),
             ('fz', BETS_FZ, '315,500円', rib_fz, (FZ_X,), 'ど的中（3連単に超大穴）'),
             ('hidden', BETS_BIG, '50,760円', rib_hd, (), '隠れど的中（デカ的中の2〜7回に1回）'), ('miss', BETS_MISS, '0円', '', (), 'ハズレ（ボタンなし）')]
    var = ''.join(f'<figure>{board(k, b, tot, rib=rb, mark=mk, tid="default")}<figcaption>{cap}</figcaption></figure>' for k, b, tot, rb, mk, cap in kinds)
    var += ('<div class="vnote"><h3>ボードの決まり</h3><ul>'
            '<li>どのテーマも同じ形：<b>ふち</b>（背景のもよう）→ <b>上の帯</b>（見出し）→ <b>カード</b>（買い目）・すみに<b>飾り</b>。色・字・もよう・飾りは、そのテーマの判定画面と同じ</li>'
            '<li><b>的中</b>：見出しはテーマのロゴの字と色 ／ <b>デカ的中</b>：虹色の見出しと光るふち・3連単の行に虹色のふち ／ <b>ど的中・隠れど的中</b>：虹色の枠と炎の光・見出しの下に帯 ／ <b>ハズレ</b>：静かな見出し・入れた買い目を全部・払戻0円</li>'
            '<li><b>隠れど的中</b>：デカ的中の2〜7回に1回（ランダム）。デカのPUSHを押すと、そのまま、ど的中の演出 →「隠れど的中！！！」</li>'
            '<li>払戻が長いと、その行の払戻だけ次の行へ。<b>馬番の枠の色は全テーマ同じ</b></li></ul></div>')
    groups = ''
    for c in CAT_ORDER:
        ts = [t for t in ORDERED if t['cat'] == c]
        cells = ''
        for t in ts:
            cells += (f'<section class="cell"><h3>{theme_label(t)}</h3><div class="pair">'
                      f'<figure><span class="lb">的中</span>{board("hit", BETS_HIT, "2,530円", tid=t["id"])}</figure>'
                      f'<figure><span class="lb">ハズレ</span>{board("miss", BETS_MISS, "0円", tid=t["id"])}</figure></div></section>')
        groups += f'<h2 class="gh">{CATS[c]}<small>{len(ts)}テーマ</small></h2><div class="grid">{cells}</div>'
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>結果のボード（{len(ORDERED)}テーマ）</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{theme_fonts(ids, extra=['BIZ+UDPGothic:wght@400;700', 'Dela+Gothic+One'])}
<style>
body{{margin:0}}
*{{box-sizing:border-box}}
.gd{{width:{BOARDS_W}px;height:{BOARDS_H}px;overflow:hidden;background:#F4F2EC;color:#22252E;font-family:"BIZ UDPGothic",sans-serif;padding:34px {GPAD}px 0}}
.t1{{margin:0;font-family:"Dela Gothic One",sans-serif;font-weight:400;font-size:34px;line-height:1.2;color:#161F3D}}
.t2{{margin:10px 0 0;max-width:2400px;font-size:15px;line-height:1.75;color:#4E5466}}
.t2 b{{color:#22252E}}
.vr{{margin-top:22px;padding:18px 24px 22px;border-radius:18px;background:#1E1A2C}}
.vr h2{{margin:0 0 16px;font-size:19px;color:#FFFFFF}}
.vr h2 small{{margin-left:10px;font-size:13px;font-weight:700;color:#CFC8E8}}
.vrow{{display:flex;gap:26px;align-items:flex-start}}
.vrow figure{{margin:0;display:flex;flex-direction:column;align-items:center;gap:12px}}
.vrow figcaption{{font-size:14px;font-weight:700;color:#ECE8F8}}
.vnote{{flex:1;min-width:0;margin-left:14px;padding:16px 22px 14px;border-radius:14px;background:rgba(255,255,255,.07);color:#E6E2F4}}
.vnote h3{{margin:0 0 8px;font-size:16px;color:#FFFFFF}}
.vnote ul{{margin:0;padding-left:1.2em}}
.vnote li{{margin:0 0 7px;font-size:14px;line-height:1.75}}
.vnote b{{color:#FFFFFF}}
.gh{{display:flex;align-items:baseline;gap:10px;margin:30px 0 14px;font-size:21px;color:#161F3D}}
.gh small{{font-size:13px;font-weight:700;color:#8A6A38}}
.grid{{display:grid;grid-template-columns:repeat({COLS},{CELL_W}px);gap:{GGAP}px}}
.cell{{border-radius:16px;background:#2A231D;padding:12px 16px 18px}}
.cell h3{{margin:0 0 12px;font-size:16px;line-height:1.3;color:#FFFFFF}}
.pair{{display:flex;gap:20px;align-items:flex-start}}
.pair figure{{margin:0;display:flex;flex-direction:column;gap:7px}}
.pair .lb{{font-size:12px;font-weight:700;color:#D6CBB8}}
{board_css(ids)}
</style>
</helmet>
<div class="gd">
  <h1 class="t1">結果のボード（壁紙のテーマごと・{len(ORDERED)}テーマ）</h1>
  <p class="t2">まさちゃんの指定：結果は<b>馬がボードを持つのをやめて、壁紙のテーマに沿ったボード</b>に（的中もハズレも）。ボードは、そのテーマの判定画面をぎゅっと小さくした形：<b>ふち＝背景のもよう・見出し＝上の帯（ロゴと同じ字と色）・買い目＝カード・すみの飾り</b>。色は判定画面と同じ（文字と背景のコントラストは確かめずみの値）。デカ的中は虹色の見出しと光るふち、ど的中・隠れど的中は虹色の枠と炎の光、ハズレは静かな見出しで払戻0円。<b>馬番の枠の色はどのテーマも同じ</b>。見本の画面（となりの5つ）は牧場のボード。</p>
  <section class="vr"><h2>ボードの種類<small>見本：いつもの（紺×金）</small></h2><div class="vrow">{var}</div></section>
  {groups}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{BOARDS_W},"height":{BOARDS_H}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


# ---------- 効果音（gen_sfx.py で作った音。fx_blobs.json の snd_… があれば、見本の画面で鳴らす） ----------
SND = {'hit': ('snd_hit_push', 'snd_hit'), 'big': ('snd_big_push', 'snd_big'), 'fz': ('snd_fz_push', 'snd_fz'),
       'hidden': ('snd_big_push', 'snd_fz')}     # 隠れど的中：PUSHはデカの音・タップはど的中の音（ハズレは音なし）
PAGE_SND = dict(SND, hit_gold=SND['hit'], hit_ranch=SND['hit'], hit_sakura=SND['hit'], hit_sea=SND['hit'], hit_autumn=SND['hit'], hit_snow=SND['hit'], hit_newyear=SND['hit'], hit_news=SND['hit'], hit_ink=SND['hit'], hit_carousel=SND['hit'], hit_stars=SND['hit'], hit_silks=SND['hit'], hit_neon=SND['hit'], hit_pixel=SND['hit'], hit_fireworks=SND['hit'], hit_kids=SND['hit'], hit_cute=SND['hit'], hit_sunset=SND['hit'], hit_night=SND['hit'], hit_marble=SND['hit'], hit_lucky=SND['hit'], hit_chalk=SND['hit'], hit_silver=SND['hit'], hit_golden=SND['hit'], hit_tengel=SND['hit'], hit_xmas=SND['hit'], hit_halloween=SND['hit'], hit_valentine=SND['hit'], hit_whiteday=SND['hit'])       # テーマの見本の音は、元の種類と同じ（カッコいい・牧場・桜・海・紅葉・雪・お正月・競馬新聞・水墨画・メリーゴーランド・星座・勝負服・ネオン・ドット絵・花火・子供向け・かわいい・夕焼け・ナイター・大理石・開運・黒板・シルバー帯・ゴールド帯・マスター帯・クリスマス・ハロウィン・バレンタイン・ホワイトデーの的中も的中の音）
WAVES = json.load(open(f'{K}/sfx_wave.json')) if os.path.exists(f'{K}/sfx_wave.json') else None

# 鳴らす部品（Web Audio。読み込みは先に・鳴らすのは押したときだけ・押した瞬間を0秒にして動きとそろえる）
SFX_JS = '''  sfxDecode(c, b) {
    return new Promise(function (ok) {
      try { var q = c.decodeAudioData(b, ok, function () { ok(null); }); if (q && q.catch) q.catch(function () { ok(null); }); } catch (e) { ok(null); }
    });
  }
  sfxInit() {
    // 音は先に読んで、音のデータにしておく（鳴らすのは押したときだけ）
    if (this._sx) return this._sx;
    var self = this, sx = this._sx = { raw: {}, buf: {}, ctx: null, src: null, el: null, id: 0, ok: 0 };
    var urls = this.sfxUrls(), dec = null;
    var OC = typeof window === 'undefined' ? null : (window.OfflineAudioContext || window.webkitOfflineAudioContext);
    if (OC) { try { dec = new OC(2, 44100, 44100); } catch (e) { dec = null; } }
    if (typeof fetch === 'function') {
      Object.keys(urls).forEach(function (k) {
        sx.raw[k] = fetch(urls[k]).then(function (r) { return r.ok ? r.arrayBuffer() : null; }).catch(function () { return null; });
        if (dec) sx.buf[k] = sx.raw[k].then(function (b) { return b ? self.sfxDecode(dec, b.slice(0)) : null; });
      });
    }
    return sx;
  }
  sfx(k, from, wait, done) {
    // 押した瞬間を0秒として、音の from 秒の所から wait 秒後に鳴らす（読むのが0.1秒より遅れたら、遅れたぶん先から鳴らして動きとそろえる）
    var self = this, sx = this.sfxInit();
    this.hush();
    var id = sx.id, t0 = Date.now(), url = this.sfxUrls()[k];
    var end = function () { if (done && id === sx.id) done(); };
    from = from || 0;
    wait = wait || 0;
    var AC = typeof window === 'undefined' ? null : (window.AudioContext || window.webkitAudioContext);
    if (!sx.ctx && AC) { try { sx.ctx = new AC(); } catch (e) { sx.ctx = null; } }
    var ctx = sx.ctx;
    if (!ctx || !sx.raw[k]) {
      if (from || wait || typeof Audio === 'undefined') { end(); return; }
      try { var a = new Audio(url); a.onended = end; sx.el = a; var p = a.play(); if (p && p.catch) p.catch(end); } catch (e) { end(); }
      return;
    }
    if (ctx.state !== 'running' && ctx.resume) { try { ctx.resume(); } catch (e) {} }
    if (!sx.ok) {
      sx.ok = 1;
      try { var s0 = ctx.createBufferSource(); s0.buffer = ctx.createBuffer(1, 1, 22050); s0.connect(ctx.destination); s0.start(0); } catch (e) {}
    }
    (sx.buf[k] || Promise.resolve(null)).then(function (buf) {
      // 先に読めなかったときは、鳴らす方で読みなおす
      return buf || sx.raw[k].then(function (b) { return b ? self.sfxDecode(ctx, b.slice(0)) : null; });
    }).then(function (buf) {
      if (id !== sx.id) return;
      var el = (Date.now() - t0) / 1000, late = Math.max(0, el - wait), off = from + (late > .1 ? late : 0);
      if (!buf || off >= buf.duration) { end(); return; }
      var s = ctx.createBufferSource();
      s.buffer = buf;
      s.connect(ctx.destination);
      s.onended = end;
      s.start(ctx.currentTime + Math.max(0, wait - el), off);
      sx.src = s;
    });
  }
  hush() {
    var sx = this._sx;
    if (!sx) return;
    sx.id++;
    if (sx.src) { try { sx.src.stop(); } catch (e) {} sx.src = null; }
    if (sx.el) { try { sx.el.pause(); } catch (e) {} sx.el = null; }
  }
  slow() {
    // iPhoneの「視差効果を減らす」
    return typeof window !== 'undefined' && !!window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
'''


def page_js(kind):
    """見本の画面のスクリプト。音があれば：記録する → PUSHの音／PUSHをタップ → タップの音（フリーズは視差効果を減らすなら1秒後に結果の所から）／とじる → 止める
       ハズレ：記録する → すぐボード（PUSHなし・音なし）"""
    ids = [blobs.get(k) for k in PAGE_SND.get(kind, ())]
    on, head, init = dict(push='', tap='', form=''), '', ''
    if ids and all(ids):
        tap = "self.sfx('tap'); "
        if kind in ('fz', 'hidden'):
            tap = f"if (self.slow()) self.sfx('tap', {FZ_T['R']:g}, 1); else self.sfx('tap'); "
        on = dict(push="self.sfx('push'); ", tap=tap, form='self.hush(); ')
        head = f"  sfxUrls() {{\n    return {{ push: '/_blob/{ids[0]}', tap: '/_blob/{ids[1]}' }};\n  }}\n" + SFX_JS
        init = '    this.sfxInit();\n'
    return ('class Component extends DCLogic {\n' + head
            + '  renderVals() {\n' + init
            + "    var st = this.state || {};\n"
            + "    var ph = st.ph || this.props.start || 'form';\n"
            + "    var self = this;\n"
            + "    return {\n"
            + "      isPush: ph === 'push',\n"
            + "      isReveal: ph === 'reveal',\n"
            + f"      toPush: function () {{ {on['push']}self.setState({{ ph: '{'reveal' if kind == 'miss' else 'push'}' }}); }},\n"
            + f"      toReveal: function () {{ {on['tap']}self.setState({{ ph: 'reveal' }}); }},\n"
            + f"      toForm: function () {{ {on['form']}self.setState({{ ph: 'form' }}); }}\n"
            + "    };\n"
            + "  }\n"
            + "}\n")


SOUND_W, SOUND_H = 2200, 1470
SND_INFO = (   # キー・見出し・小見出し・PUSHの音・色・目もり（秒）
    ('hit', '的中ボタン', '当たったとき・ハ長調（明るく軽く）', 'ピロリン↑（鐘が3つ上がる）＋キラキラ', ('#C8281F', '#FF9A3C'), .5),
    ('big', 'デカ的中ボタン', '3連単が当たったとき・ニ長調・重く重低音で（速く勢いよく）', 'ドゥン（重低音）＋キュイーン↑（低めから）＋低いうなり', ('#7B4CFF', '#FF3BB8'), .5),
    ('fz', 'ど的中ボタン（フリーズ的中ボタン）', '3連単の当たりに超大穴（10〜12番人気）<br>ホ長調・低音と重低音（いちばん派手）', 'ドォォン（重低音）＋グォォォン↑（低いうなりが1オクターブ上がる）＋低いどら',
     ('#FF3B3B', '#FF9F1A', '#FFE53B', '#3BE26A', '#2FD6FF', '#4C6BFF', '#B34CFF', '#FF3BB8'), 1.0),
)


def snd_events():
    """タップの音の中身（秒・終わり・音・画面）。フリーズは FZ_T の時刻"""
    B, W, Z, M, R = (FZ_T[k] for k in 'BWZMR')
    T4, T5 = M + MT_T['T4'], M + MT_T['T5']
    return {
        'hit': [(0, None, 'ポン', '押した'), (.22, .97, 'ヒュイーン↑', 'ボードが下から'), (.95, None, 'キラーン', '「的中！」'),
                (1.15, 1.3, 'ピン・ポン', '買い目が1行ずつ'), (1.6, None, 'チャリーン', '払戻の合計（コイン）')],
        'big': [(0, None, 'ガツッ', '押した'), (.04, None, 'ドォォン!!', '白く光る・爆発・虹の光の筋'), (.1, None, 'キュウィン', '虹の輪①（下にドン）'),
                (.25, None, 'キュウィン', '虹の輪②（少し高く）'), (.4, None, 'キュウィン', '虹の輪③（もっと高く）'),
                (.55, None, 'ズドン', 'ボードが落ちてきて着地（0.38秒〜）'), (.7, None, 'ジャーン!!', '「デカ的中!!」（低い金管）'),
                (.9, .98, 'ピン・ピン', '買い目（0.08秒おき）'), (1.14, None, 'パッパッ＋ジャラジャラ', '払戻の合計（メダル）'), (1.4, None, 'パーン', 'ファンファーレ')],
        'fz': [(0, None, 'ドンッ（重低音）＋ギュッ↓', '押した瞬間にフリーズ（白く光る）'), (0, W, 'ビーーッ（角ばった電子音）＋ザザッ・チリチリ', '横に流れる帯・赤い粒（コマに合わせて揺れる・途切れる）'),
               (B, B + .11, 'ヴォン・ヴォン（低い）', '青い画面・白い光がふくらむ'), (W, None, 'ブツッ（電子音がいきなり消える）', '青白い横一本線'),
               (W, Z + .15, 'バチバチッ・ジジッ', '線にまとわりつく細い電気（コマごとに形が変わる）'), (Z, Z + .2, 'ヒュゥン↓ → プツッ', '点に縮んで消える・光の粒'),
               (Z + .2, M, '無音', '真っ暗（フリーズの間）'),
               (M, T4, 'ドガーン!! → ドドド・ドガッ・ドガン×4', '大爆発 →「どてき！！」ど・て・き は1文字ずつ小さな爆発・「！」でドガッ・「！」で爆発（低いベースが刻む）'),
               (T4 + .12, T4 + .63, 'ドガン×4（だんだん高く）', '「ど！」×4（重低音の爆発）'), (T4 + .71, T5, 'ドドドドッ', '低いタムの連打'),
               (T5, None, 'ドガーン!!＋低い金管', '「ど的中！！！！」大爆発'), (T5 + .45, R, 'ドン・ドン（0.45秒ごと）', '光の波と輪に合わせて（小さな爆発）'),
               (R, R + .3, '大爆発 → ズドン＋ジャーン', '結果（虹色の大当たりの画面）→ ボードの着地・「ど的中！！！」'),
               (R + .45, R + .69, 'ボン・ボン・ボン → ゴーン＋ジャラジャラ', '買い目（0.08秒おき）→ 払戻の合計（メダル）')],
    }


def ssec(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def wave_svg(key, name, wv, evs, cols, step):
    """タップの音の波形（音の大きさ・dB）と、番号つきの印・秒の目もり"""
    PX, WW, MT, WH = 14, 1664, 30, 92
    TW, TH = PX * 2 + WW, MT + WH + 26
    d, h = wv['d'], wv['h']
    X = lambda t: PX + t / d * WW
    mid, amp, n = MT + WH / 2, WH / 2 - 2, len(h)
    pts = [(X(0), 0)] + [(X((i + .5) * d / n), max(v, .015) * amp) for i, v in enumerate(h)] + [(X(d), 0)]
    poly = ' '.join(f'{x:.0f},{mid - a:.0f}' for x, a in pts) + ' ' + ' '.join(f'{x:.0f},{mid + a:.0f}' for x, a in reversed(pts))
    stops = ''.join(f'<stop offset="{i / max(1, len(cols) - 1):.3f}" stop-color="{c}"></stop>' for i, c in enumerate(cols))
    band = ''.join(f'<rect x="{X(t0):.1f}" y="{MT}" width="{X(t1) - X(t0):.1f}" height="{WH}" rx="4" fill="#161F3D" fill-opacity=".07"></rect>'
                   for t0, t1, *_ in evs if t1)
    marks = ''
    for i, (t0, *_) in enumerate(evs, 1):
        x = X(t0)
        marks += (f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{MT - 4}" y2="{MT + WH}" stroke="#22252E" stroke-opacity=".35" stroke-dasharray="3 3"></line>'
                  f'<circle cx="{x:.1f}" cy="13" r="11" class="mk"></circle>'
                  f'<text x="{x:.1f}" y="17.5" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">{i}</text>')
    ticks, t = '', 0.0
    while t <= d + 1e-6:
        x = X(t)
        ticks += (f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{MT + WH}" y2="{MT + WH + 5}" stroke="#6A7080"></line>'
                  f'<text x="{x:.1f}" y="{MT + WH + 19}" text-anchor="middle" font-size="12" fill="#6A7080">{ssec(t)}{"秒" if t == 0 else ""}</text>')
        t = round(t + step, 6)
    return (f'<svg class="wv" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}" role="img" aria-label="{name}のタップの音の大きさ（{ssec(d)}秒）" font-family="BIZ UDPGothic, sans-serif">'
            f'<defs><linearGradient id="wg{key}" x1="0" x2="1" y1="0" y2="0">{stops}</linearGradient></defs>{band}'
            f'<line x1="{PX}" x2="{PX + WW}" y1="{mid:.0f}" y2="{mid:.0f}" stroke="#22252E" stroke-opacity=".15"></line>'
            f'<polygon points="{poly}" fill="url(#wg{key})"></polygon>{marks}{ticks}</svg>')


PLAY_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"></path></svg>'
STOP_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"></rect></svg>'


def sound_page():
    """効果音のメモ：▶で聞ける・タップの音の波形と中身・アプリで鳴らすときの決まり"""
    evs_all = snd_events()
    R = FZ_T['R']
    secs = ''
    for key, name, sub, pdesc, cols, step in SND_INFO:
        wp, wt = WAVES[f'sfx_{key}_push'], WAVES[f'sfx_{key}']
        evs = evs_all[key]
        items = ''.join(f'<li><span class="no">{i}</span><span class="tx"><span class="tm">{ssec(t0)}{"〜" + ssec(t1) if t1 else ""}秒</span> <b>{snd}</b> <span class="wh">{what}</span></span></li>'
                        for i, (t0, t1, snd, what) in enumerate(evs, 1))
        secs += f'''
  <section class="sn {key}">
    <div class="sl">
      <h2>{name}<small>{sub}</small></h2>
      <button class="pl" type="button" onClick="{{{{p_{key}_push}}}}" aria-pressed="{{{{a_{key}_push}}}}">{PLAY_SVG}PUSHが出たとき<small>{ssec(wp['d'])}秒</small></button>
      <p class="pd">{pdesc}</p>
      <button class="pl" type="button" onClick="{{{{p_{key}}}}}" aria-pressed="{{{{a_{key}}}}}">{PLAY_SVG}PUSHをタップしたとき<small>{ssec(wt['d'])}秒</small></button>
      <p class="pd">右の波形（0秒＝押した瞬間。見本の画面の動きと同じ時刻）</p>
      <p class="lv">大きさ：PUSH {wp['lufs']:g}・タップ {wt['lufs']:g} LUFS</p>
    </div>
    <div class="sr">{wave_svg(key, name, wt, evs, cols, step)}<ol class="ev">{items}</ol></div>
  </section>'''
    keys = [k for k, *_ in SND_INFO]
    urls = ',\n      '.join(f"{k}_push: '/_blob/{blobs[f'snd_{k}_push']}', {k}: '/_blob/{blobs[f'snd_{k}']}'" for k in keys)
    vals = ',\n      '.join(f"p_{k}: play('{k}'), a_{k}: on === '{k}' ? 'true' : 'false'" for k in [x for k in keys for x in (f'{k}_push', k)])
    box = '<div class="box"><h3>{}</h3><ul>{}</ul></div>'.format
    boxes = (box('鳴らすとき', '<li><b>PUSHの音</b>：PUSHが出た瞬間（結果を記録して当たりのとき。3つのボタンのうち出た1つの音だけ）</li>'
                 '<li><b>隠れど的中</b>：PUSHが出たときはデカの音・タップでど的中の音（見た目もデカ → ど的中）。<b>ハズレは音なし</b></li>'
                 '<li><b>タップの音</b>：PUSHを押した瞬間が0秒。画面の動きと同じ時刻で、見本の画面（となりの3つ）でも同じに鳴る</li>'
                 '<li>「とじる」・ほかの画面へ移る・アプリを閉じる → すぐ止める。鳴っている途中で次の音が鳴るときは、前の音を止めてから</li>')
             + box('iPhoneでの鳴らし方（アプリ）', '<li><b>消音スイッチ（マナーモード）なら鳴らさない</b>・ほかのアプリの音楽は止めずに重ねる（AVAudioSession の ambient）。音量はiPhoneの音量のまま</li>'
                   '<li>設定に「効果音」オン／オフ（最初はオン）<b>※仮</b></li>'
                   f'<li>「視差効果を減らす」がオン：的中・デカは同じ音。ど的中は動きが短い（1秒真っ暗 → 結果）ので、押して1秒後に、ど的中の音の{ssec(R)}秒（結果のドォン・パッパッパーン）から鳴らす <b>※仮</b>（見本の画面も同じ）</li>')
             + box('大きさとファイル', '<li>6つ：sfx_hit_push・sfx_hit・sfx_big_push・sfx_big・sfx_fz_push・sfx_fz（AAC 160kbps・m4a・ぜんぶで約460KB）</li>'
                   '<li>大きさはそろえて、強いボタンほど少し大きく（的中 −16〜−17・デカ −13〜−14・ど的中 −13 LUFS）。いちばん大きい所も −1dB 以下（音割れしない）</li>'
                   '<li><b>デカとど的中は低音と重低音</b>：重低音はスマホのスピーカーからはほとんど出ないので、ひずませて作った倍音で低音を感じるようにして、ジャーンやファンファーレには高めの音も小さく重ねた。イヤホン・ヘッドホンだと重低音まで聞こえる。スマホのスピーカーでは的中より少し小さめに聞こえることがある</li>'
                   '<li>買い目の音は見本の行の数（的中・デカ2行・ど的中3行）。4行以上だと合計が出る前に「チャリーン」が鳴るので、アプリでは行と合計の音を分けて、出るたびに鳴らす（あとで作る）<b>※仮</b></li>')
             + box('作り方', '<li>音は全部プログラムで作った（gen_sfx.py・numpy と scipy）。<b>録音や、ほかの音のデータ（サンプル）は使っていない</b></li>'
                   '<li>鐘（FM）・金管（ノコギリ波を重ねる）・ドラム・コイン・「シュッ」（ノイズ）・キュウィン（すばやく上がるシンセ）・爆発（はじける音・爆風・重低音・地ひびき・かけら）を組み合わせて、残響・イコライザー・圧縮で仕上げ。デカとど的中は重低音のドォォン・爆発・低いうなり・低いどら・低い金管で、仕上げも低音用（ど的中は FZ_LOW・FZ_MID で重低音と低音の楽器の大きさを変えられる）</li>'
                   '<li>ど的中は gen_fx.py の時刻（FZ_T・MT_T）を読むので、動きを変えたら作り直すだけで音もそろう：python3 gen_sfx.py &lt;フォルダ&gt; → ffmpeg で m4a に</li>'))
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>効果音のメモ</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&amp;display=swap">
<style>
body{{margin:0}}
*{{box-sizing:border-box}}
.gd{{width:{SOUND_W}px;height:{SOUND_H}px;overflow:hidden;background:#F4F2EC;color:#22252E;font-family:"BIZ UDPGothic",sans-serif;padding:34px 40px 0}}
.hdr{{display:flex;align-items:flex-start;justify-content:space-between;gap:40px}}
.t1{{margin:0;font-family:"Dela Gothic One",sans-serif;font-weight:400;font-size:32px;line-height:1.2;color:#161F3D}}
.t2{{margin:8px 0 0;max-width:1560px;font-size:14.5px;line-height:1.7;color:#4E5466}}
.stop{{flex:none;display:inline-flex;align-items:center;gap:8px;height:48px;margin-top:4px;padding:0 24px;border-radius:999px;border:2px solid #161F3D;background:#FFFFFF;color:#161F3D;font-family:"BIZ UDPGothic",sans-serif;font-weight:700;font-size:15px;cursor:pointer}}
.stop svg{{width:16px;height:16px}}
.sn{{--c:#161F3D;display:grid;grid-template-columns:360px minmax(0,1fr);gap:28px;margin-top:16px;background:#FFFFFF;border:1px solid #DDD8CC;border-radius:14px;padding:16px 20px}}
.sn.hit{{--c:#C8281F}}
.sn.big{{--c:#7B4CFF}}
.sn.fz{{border:2px solid transparent;background:linear-gradient(#FFFFFF,#FFFFFF) padding-box,linear-gradient(90deg,#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8) border-box}}
.sn h2{{margin:0;font-size:19px;line-height:1.3;color:#161F3D}}
.sn h2 small{{display:block;margin-top:4px;font-size:12.5px;font-weight:700;color:#8A6A38}}
.pl{{display:flex;align-items:center;gap:10px;width:100%;height:48px;margin-top:12px;padding:0 16px;border-radius:12px;border:2px solid var(--c);background:#FFFFFF;color:#161F3D;font-family:"BIZ UDPGothic",sans-serif;font-weight:700;font-size:15px;text-align:left;cursor:pointer}}
.pl svg{{flex:none;width:18px;height:18px;color:var(--c)}}
.pl small{{margin-left:auto;font-size:12.5px;color:#5A6070}}
.pl[aria-pressed="true"]{{background:var(--c);color:#FFFFFF}}
.pl[aria-pressed="true"] svg,.pl[aria-pressed="true"] small{{color:#FFFFFF}}
.pd{{margin:6px 2px 0;font-size:12.5px;line-height:1.55;color:#4E5466}}
.lv{{margin:10px 2px 0;font-size:12px;color:#5A6070}}
.wv{{display:block}}
.wv .mk{{fill:var(--c)}}
.ev{{list-style:none;margin:8px 0 0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px 18px}}
.ev li{{display:grid;grid-template-columns:20px minmax(0,1fr);column-gap:7px;align-items:start;font-size:13px;line-height:20px;color:#22252E}}
.no{{display:flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;background:var(--c);color:#FFFFFF;font-size:11.5px;font-weight:700;line-height:1}}
.tm{{font-size:12.5px;font-weight:700;color:#5A6070}}
.wh{{font-size:12.5px;color:#4E5466}}
.boxes{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:18px}}
.box{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:12px;padding:12px 14px}}
.box h3{{margin:0 0 6px;font-size:14px;color:#161F3D}}
.box li{{margin:0;font-size:12.5px;line-height:1.65;color:#4E5466}}
.box ul{{margin:0;padding-left:1.1em}}
.box b{{color:#22252E}}
</style>
</helmet>
<div class="gd">
  <div class="hdr">
    <div>
      <h1 class="t1">効果音（的中ボタン・デカ的中ボタン・ど的中ボタン）</h1>
      <p class="t2">まさちゃんの指定：3つのボタンに効果音（的中はOK・デカはタップでキュウィンを3回、全体を重く重低音に・ど的中は全体を低音と重低音で、「どてき！！」からは爆発のようにずっしり重く）。動きもパチンコの当たりのように速く・勢いよくした。送ってくれた3つの動画は音が入っていなかったので、それぞれの動きに合わせて新しく作った（全部プログラムで作った音。録音や、ほかの音は使っていない）。<b>ど的中のフリーズは押した瞬間</b>（まさちゃんの指定。送ってくれたパチスロのフリーズの動画のように、ドンッ＋ビーーッ…ブツッ（電子音がいきなり消える）→ 細い電気のバチバチ → 無音。動画の音は使わず、似た感じに作った）。▶で聞ける（もう一度押すと止まる）。となりの3つの見本の画面も、「記録する」と「PUSH」のタップで同じ音が鳴る。iPhoneが消音（マナーモード）だと鳴らないことがある。</p>
    </div>
    <button class="stop" type="button" onClick="{{{{stop}}}}">{STOP_SVG}とめる</button>
  </div>{secs}
  <div class="boxes">{boxes}</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{SOUND_W},"height":{SOUND_H}}}}}'>
class Component extends DCLogic {{
  sfxUrls() {{
    return {{
      {urls}
    }};
  }}
{SFX_JS}  renderVals() {{
    this.sfxInit();
    var st = this.state || {{}};
    var on = st.on || '';
    var self = this;
    var play = function (k) {{
      return function () {{
        if (on === k) {{ self.hush(); self.setState({{ on: '' }}); return; }}
        self.sfx(k, 0, 0, function () {{ self.setState({{ on: '' }}); }});
        self.setState({{ on: k }});
      }};
    }};
    return {{
      {vals},
      stop: function () {{ self.hush(); self.setState({{ on: '' }}); }}
    }};
  }}
}}
</script>
</body>
</html>
'''


MEMO_W, MEMO_H = 2200, 2340


def memo_page():
    """メモのボード（静止画18枚＋Fableに渡す決まり）"""
    def still(key, cap):
        return f'<figure class="st"><img src="/_blob/{blobs[key]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'
    hit = still('s_hit_form', '① 記録する') + still('s_hit_push', '② PUSHが上下に動く') + still('s_hit_board', '③ タップ → ボード')
    big = still('s_big_push', '① 大きいPUSH（虹の輪）') + still('s_big_light', '② 爆発・虹の輪（キュウィン）') + still('s_big_board', '③ ボードがドン！')
    fz = (still('s_fz_push', '① 虹色の超デカPUSH') + still('s_fz_noise', '② タップでフリーズ') + still('s_fz_line', '③ 横一本線と細い電気')
          + still('s_fz_doteki', '④「どてき！！」') + still('s_fz_dodo', '⑤「ど！ど！ど！ど！」') + still('s_fz_logo', '⑥「ど的中！！！！」') + still('s_fz_result', '⑦ 結果（上に ど的中）'))
    hd = still('s_big_push', '① デカのPUSH') + still('s_fz_noise', '② タップでフリーズ') + still('s_hd_result', '③「隠れど的中！！！」')
    ms = still('s_miss_form', '① 記録する') + still('s_miss_board', '② ボードだけ')
    B, W, Z, M, R = (FZ_T[k] for k in 'BWZMR')
    T5 = M + MT_T['T5']
    sec = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>的中ボタンのメモ</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&amp;display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&amp;display=swap">
<style>
body{{margin:0}}
*{{box-sizing:border-box}}
.gd{{width:{MEMO_W}px;height:{MEMO_H}px;overflow:hidden;background:#F4F2EC;color:#22252E;font-family:"BIZ UDPGothic",sans-serif;padding:34px 40px 0}}
.t1{{margin:0;font-family:"Dela Gothic One",sans-serif;font-weight:400;font-size:32px;line-height:1.2;color:#161F3D}}
.t2{{margin:8px 0 0;max-width:1560px;font-size:14.5px;line-height:1.7;color:#4E5466}}
.rows{{display:grid;grid-template-columns:3fr 3fr 7fr;gap:20px;margin-top:20px}}
.rows.r2{{grid-template-columns:3fr 2fr 8fr;margin-top:16px}}
.grp{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:14px;padding:14px 16px}}
.grp.fzg{{border:2px solid transparent;background:linear-gradient(#FFFFFF,#FFFFFF) padding-box,linear-gradient(90deg,#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8) border-box}}
.grp h2{{margin:0 0 10px;font-size:17px;color:#161F3D}}
.grp h2 small{{font-size:12.5px;font-weight:700;color:#8A6A38;margin-left:8px}}
.sts{{display:flex;gap:10px}}
.st{{margin:0;flex:1;min-width:0}}
.st img{{display:block;width:100%;aspect-ratio:390/844;object-fit:cover;border-radius:10px;border:1px solid #DDD8CC}}
.st figcaption{{margin-top:6px;font-size:12.5px;font-weight:700;color:#3E4352;text-align:center}}
.boxes{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:18px}}
.box{{background:#FFFFFF;border:1px solid #DDD8CC;border-radius:12px;padding:12px 14px}}
.box h3{{margin:0 0 6px;font-size:14px;color:#161F3D}}
.box p,.box li{{margin:0;font-size:12.5px;line-height:1.65;color:#4E5466}}
.box ul{{margin:0;padding-left:1.1em}}
.box b{{color:#22252E}}
.grp.bx ul{{margin:0;padding-left:1.1em}}
.grp.bx li{{margin:0 0 4px;font-size:13px;line-height:1.7;color:#4E5466}}
.grp.bx b{{color:#22252E}}
</style>
</helmet>
<div class="gd">
  <h1 class="t1">的中ボタン・デカ的中ボタン・フリーズ的中ボタン（デフォルト）・隠れど的中・ハズレ</h1>
  <p class="t2">まさちゃんの指定：記録して <b>当たり → 的中ボタン</b>、<b>3連単が当たり → デカ的中ボタン</b>、<b>3連単の当たりに超大穴（10〜12番人気）の馬 → フリーズ的中ボタン</b>、<b>デカ的中の2〜7回に1回（ランダム）→ 隠れど的中</b>（デカのPUSHを押すと、そのまま、ど的中）、<b>ハズレ → ボタンなしでボードだけ</b>。タップすると<b>壁紙のテーマのボード</b>が出て、当たった買い目を報告する（<b>馬がボードを持つのはやめた</b>。的中もハズレも、ボードはテーマに沿った形）。フリーズは、まさちゃんの送ってくれたパチスロのフリーズの動画のように（台の絵や文字は使わない）：虹色にギラギラ光るめちゃくちゃデカいPUSH → <b>タップした瞬間にフリーズ</b>（まさちゃんの指定。白く光る → 横に流れるノイズ → 青い画面に白い光と細い電気 → 青白い横一本線に1pxの電気がバチバチ → 点に縮んで消える）→ 真っ暗のまま1.5秒 → 虹色ネオンのカット（「どてき！！」「ど！ど！ど！ど！」）→「ど的中！！！！」（そろってから1.5秒）→ <b>虹色の大当たりの画面</b>に、上に「ど的中」・まん中からボード。<b>文字はパチンコのロゴのような筆の字と虹色</b>（まさちゃんの指定。写真の字の形は使わず、筆の動きから描いた）。視覚酔いしないように、画面全体が回る・迫る・ゆれる動きはしない。となりの5つの画面は、タップで動く見本（どれもデフォルト＝全テーマ共通の動き・ボードは牧場）。</p>
  <div class="rows">
    <section class="grp"><h2>的中ボタン<small>当たったとき</small></h2><div class="sts">{hit}</div></section>
    <section class="grp"><h2>デカ的中ボタン<small>3連単が当たったとき</small></h2><div class="sts">{big}</div></section>
    <section class="grp fzg"><h2>フリーズ的中ボタン<small>3連単の当たりに超大穴（10〜12番人気）</small></h2><div class="sts">{fz}</div></section>
  </div>
  <div class="rows r2">
    <section class="grp fzg"><h2>隠れど的中<small>デカ的中の2〜7回に1回</small></h2><div class="sts">{hd}</div></section>
    <section class="grp"><h2>ハズレ<small>ボタンなし</small></h2><div class="sts">{ms}</div></section>
    <section class="grp bx"><h2>結果のボード（壁紙のテーマごと）と、隠れど的中の決まり</h2><ul>
      <li><b>馬は出さない</b>（まさちゃんの指定）。的中・デカ的中・ど的中・隠れど的中・ハズレ、どれも<b>壁紙のテーマのボード</b>。{len(ORDERED)}テーマの見本は「結果のボード（{len(ORDERED)}テーマ）」、作り方は boards.py</li>
      <li>ボード＝<b>そのテーマの判定画面をぎゅっと小さくした形</b>：ふち＝背景のもよう（--bg と背景のルール）・見出し＝上の帯（--hd・--hdInk・--hdB・帯の飾り）・見出しの字＝ロゴと同じ（--dfont・--logo・--logoS）・買い目＝カード（--card・--cardB・--cardS）と行（--zBg・--zB）・券種＝タグ（--tagBg・--tagInk・--tagLine）・払戻＝--acc・合計＝--ink・すみの飾り（判定画面のカードと同じ所）。色は判定画面と同じ（コントラストを確かめた値）。馬番の枠の色は全テーマ同じ</li>
      <li><b>デカ</b>：まわりが光る・見出しは虹色（黒いふち）・3連単の行に虹色のふち。<b>ど的中・隠れど的中</b>：枠は虹色（回さない）・炎の光。<b>ハズレ</b>：見出しは上の帯の文字の色で静かに・払戻0円・光も紙ふぶきも音もなし</li>
      <li><b>隠れど的中</b>：デカ的中が出るたびに数えて、<b>2〜7回目（ランダム）の1回</b>。出たら、次の回数をまた2〜7からランダムに決める。数は端末に保存（アプリを閉じても続く・記録やバックアップとは別）。本物のど的中（超大穴）は数えない <b>※仮</b></li>
      <li>見た目は<b>デカ的中のPUSH</b>（PUSHが出たときの音もデカ）→ タップで<b>そのまま、ど的中の演出</b>（押した瞬間にフリーズ・音はど的中）→ 結果の見出し「<b>隠れど的中！！！</b>」・帯「隠れ　デカ的中が ど的中に化けた！」（超大穴の帯のかわり）</li>
    </ul></section>
  </div>
  <div class="boxes">
    <div class="box"><h3>出るとき</h3><ul><li>結果を<b>記録したとき</b>だけ（あとで直したとき・まとめて入れた記録・中止では出ない）</li><li>出るのは1つだけ。強い順に <b>フリーズ</b>（3連単が当たって、その3頭に超大穴＝10〜12番人気がいる。13番人気より下は入れない）＞ <b>デカ</b>（3連単が当たり。2〜7回に1回は<b>隠れど的中</b>）＞ <b>的中</b>（それ以外の当たり）</li><li><b>ハズレ</b>（当たりが1つもない）：PUSHは出さずに、ハズレのボードだけ</li><li>人気は、そのレースを判定したときの単勝オッズの順（判定の超大穴 J・K・L と同じ）。人気がわからないレースはフリーズにしない（デカ）<b>※仮</b></li><li>お知らせ（発走15分後）から開いて記録したときも同じ</li></ul></div>
    <div class="box"><h3>流れと時間（的中・デカ・ハズレ）</h3><ul><li><b>的中</b>：押す → 0.3秒 ボードが下から → 0.95秒「的中！」→ 1.15秒〜 買い目 → 1.8秒 とじる</li><li><b>デカ</b>（パチンコの当たりのように速く・勢いよく）：押す → 0.04秒 白く光る・爆発・虹の光の筋 → 0.1・0.25・0.4秒 虹の輪（キュウィン×3・だんだん大きく）→ 0.38秒 ボードがドンと落ちてくる（0.55秒 着地・光の破片）→ 0.7秒「デカ的中!!」がたたきつけるように → 0.9秒〜 買い目（0.08秒おき）→ 1.4秒 とじる</li><li><b>ハズレ</b>：記録する → 暗い幕 → 0.1秒 ボードが静かに出る（0.4秒）→ 0.45秒〜 買い目（0.08秒おき）→ 0.85秒 とじる</li><li><b>PUSHは横長の長方形（角は丸い）</b>。上下に0.9秒（デカは0.8秒・大きく・まわりに虹の輪）でくり返す</li></ul></div>
    <div class="box"><h3>フリーズの流れと時間</h3><ul><li><b>PUSH</b>：横340×縦170・角46px（デカの1.2倍）。虹色が流れる面・ラメ・白い光がサッと走る・白と紫のふち・まわりに虹の輪。上下に22px・0.85秒／1.3秒ごとにブルブルッ／画面のふちが虹色に光る</li><li><b>押した瞬間にフリーズ（0秒〜）</b>（まさちゃんの指定：前のバグる画面はやめた。送ってくれたパチスロのフリーズの動画のような動き。台の絵は使わない）：1コマ＝1/30秒。白く光る（青いブロックが丸く集まる・縦に抜けた線）→ 0.07秒〜 明るい色の帯が横に流れる（コマごとに場所が変わる・下に緑と黄色）→ 0.2秒〜 まぶしい帯のある水色に赤い粒 → {sec(B)}秒 青い画面にまぶしい横の帯・<b>まん中の白い光がふくらむ・しぼむ</b>・弓なりの電気・縦の点々 → {sec(W)}秒 まわりが暗くなって<b>青白い横一本線</b>（まん中にフレア）・<b>線にまとわりつく電気がバチバチ</b>（いちばん細い線＝芯0.8px・枝0.5px。中点をずらして細かくギザギザ・枝分かれ・1コマごとに形が変わる）→ {sec(Z)}秒 線が両はしから点に縮んで消える（光の粒が下へ落ちながら散る）→ <b>真っ暗のまま1.5秒</b>（フリーズの間）。走査線（1px）は {sec(W)}秒まで</li><li><b>虹色ネオンのカット（{sec(M)}〜{sec(R)}秒・5つ）</b>：まさちゃんの指定の文字。<b>パチンコのロゴのような筆の字と虹色</b>（虹色の面・左上のふちが白く光る・上半分につや・こげ茶と金と黒のふち・金の立体・まわりに光。brush.py）。「どてき！！」「ど！」は<b>1文字ずつ大きく</b>、押した直後のPUSHのように乱れる（赤と水色のずれ・横にずれる帯・まわりに小さなブロック）。文字は<b>たたきつけるように出て</b>（0.16秒）、<b>ずっとガクガクふるえる</b>（左右上下と傾き・1秒に4回。筆の字は明るさの差が大きいので、光の点めつが多くならないように前より少なく）。<b>パチンコの当たりのように速く・激しく</b>：「！」「ど！」「ど的中」が出るたびに<b>爆発</b>（星形の光がはじける・衝撃の輪・光の破片が飛び散る）。場所・大きさ・向きはバラバラ：真っ暗から大爆発 → テンゲルのアイコンのネオンに「ど」「て」「き」「！」と大きな「！」（{sec(M)}秒〜）→ 星空に「どてき！！」（左上から右下へ階段・{sec(M + MT_T['T2'])}秒〜）→ ネオンのギザギザに大きな「どてき！！」×2（画面からはみ出る・{sec(M + MT_T['T3'])}秒〜）→ 星空に大きな「ど！」×4（{sec(M + MT_T['T4'])}秒〜・0.17秒おき）→ <b>ネオンのパチンコの当たりのような虹色</b>（{sec(T5)}秒〜）（黒に光る虹の光線・虹の輪・白く光るまん中と星・きらめき）に「ど的中」（光がサッと走る）「！！！！」（<b>そろってから1.5秒</b>）。<b>この背景だけ動く</b>：光の波が光線にそって外へ流れる（0.45秒ごと）・虹の輪が外へ広がって消える・まん中がふくらむ（回らない）。ほかのカットの背景は止まったまま</li><li><b>{sec(R)}秒 結果</b>：白く光る → <b>虹色の大当たりの画面</b>（まさちゃんの指定。「ど的中」から虹色の光線と白い細い光線・まん中の白い光・虹の輪が外へ広がる（1.8秒ごと・2つ）・虹色のきらめきが上る・光線は止まったまま回さない）で爆発、上に「ど的中」（筆の字・うしろで虹色の炎がゆらゆら・光がサッと走る・きらめき・SUPER LONGSHOT）・まん中からボードがドンと出る → {sec(R + .3)}秒「ど的中！！！」（隠れど的中は「隠れど的中！！！」）→ {sec(R + .45)}秒〜 買い目（0.08秒おき）→ {sec(R + .45 + .24 + .25)}秒 とじる</li><li><b>隠れど的中</b>：デカのPUSH → タップで、ここに書いた流れと同じ（押した瞬間にフリーズ）</li></ul></div>
    <div class="box"><h3>重ねる順（下から）</h3><ul><li><b>的中・デカ・ハズレ</b>：暗い幕 → 光（ハズレはなし）→ <b>テーマのボード</b>（ふち＝背景のもよう → 上の帯と見出し → カードと買い目 → すみの飾り。文字はHTML）→ 紙ふぶき → とじる → （デカ）白い光</li><li><b>フリーズ・隠れど的中</b>：黒 → 虹色の大当たりの画面（虹色の光線・白い光線・虹の輪・虹色のきらめき・コイン・テーマのボード・「ど的中」と虹色の炎・紙ふぶき）→ ネオンのカット（5つ・文字・白い光）→ 押した瞬間のフリーズ（白い画面・横に流れる帯・水色の画面・青い画面・まぶしい帯・白い光・ブロックと粒・走査線・横一本線・フレア・電気・光の粒）→ 白い光 → とじる</li></ul></div>
    <div class="box"><h3>ボードに書くもの</h3><ul><li>見出し（的中！・デカ的中!!・ど的中！！！・隠れど的中！！！・ハズレ。全角の「！」が3つ続くところは字の間をつめる）・R・買い目（券種・馬番・金額・払戻）・払戻の合計。ユーザーが自分で入れた買い目だけ（判定の画面に点数・組番を出さない決まりはそのまま）</li><li>当たりは当たった買い目だけ。<b>ハズレは入れた買い目を全部</b>（払戻0円）・小見出しは「9R の買い目」</li><li>デカ・フリーズ・隠れど的中は3連単の行がいちばん上で虹色の枠（フリーズは光が走る）</li><li><b>フリーズ</b>：上に「ど的中」（筆の字・虹色の炎）・見出しの下に「超大穴 ⑪ 11番人気が3連単に！」の帯・3連単の行の超大穴の馬番に虹色の輪。<b>隠れど的中</b>：帯は「隠れ　デカ的中が ど的中に化けた！」</li><li>払戻が長いと、その行の払戻だけ次の行へ（右によせる）。帯のぶんボードが長いので、フリーズは6行まで（7つ以上は上から5行＋「ほか○点」<b>※仮</b>）</li></ul></div>
    <div class="box"><h3>テーマ（壁紙）ごとに変えるところ</h3><ul><li><b>結果のボード</b>：判定画面と同じ変数と飾り（boards.py が themes20.py・判定画面から読む）。新しい絵はいらない</li><li>PUSHの色（--pushA・--pushB・--pushC・--rim・--rimD）・光の色（--ray）</li><li><b>フリーズは全テーマ共通</b>（変わるのはボードだけ）。回る虹（虹のぐるぐる）は使わない（虹色は流れるだけ）</li><li><b>カッコいい（金色）</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>黒と金の ぷるんぷるん</b>（黒いつやの面・金のふち・金の字。下を中心に、つぶれる → のびる をくり返す。見本「的中ボタン（カッコいい）」）・壁紙の馬の<b>おしりが3秒に1回 ぷるん</b>（gold.py。視差効果を減らすなら止まる）</li><li><b>牧場</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>芝生でできたPUSH</b>（芝の面・まわりに葉・下に土・小さな花。上の葉がそよぐ・押すと芝の葉と花びらが舞う。見本「的中ボタン（牧場）」）・壁紙の馬が<b>右から左へ、左から右へ行ったり来たり</b>（片道1〜8秒・毎回ちがう速さ。速いと走る。着いたらふり向く）。<b>8〜22秒ごとに1回立ち止まって、芝生を食べる か こっちを見てしっぽを3回ふる</b>（ranch.py。視差効果を減らすなら止まる）</li><li><b>桜</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>桜がついたPUSH</b>（桜色の面・左上に桜の枝（花3つ・つぼみ・若葉）・右下にも花。枝がゆれて花びらがひらひら落ちる・押すと花びらが舞う。見本「的中ボタン（桜）」）・壁紙に<b>いつも桜の花びらが降っている</b>（28まい・奥は小さくゆっくり・手前は大きく・くるくる回って裏返る。壁紙の絵の上に重ねる SVG・sakura.py。視差効果を減らすなら消える）</li><li><b>海</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>海の模様のPUSH</b>（青海波・下に流れる白い波・上る泡・右上に浮き輪・左下に ひとで。押すと水しぶき。見本「的中ボタン（海）」）・壁紙は<b>馬がいつも走っていて、景色が右から左へ流れてくり返す</b>（いまの馬のギャロップ10コマ・空と雲 28秒／海 7秒／砂浜 2.3秒で1まいぶん。flat/sea_run.py の絵＋sea_wall.py。視差効果を減らすなら止まった絵）</li><li><b>紅葉</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>紅葉がついたPUSH</b>（朱色の面・左上と右下に枝ともみじ（赤・朱・橙・山吹）・面にもみじ。枝がゆれて もみじがひらひら落ちる・押すと もみじが舞う。見本「的中ボタン（紅葉）」）・壁紙に<b>いつも紅葉が降っている</b>（もみじ18枚・ゆらゆら／くるくる回って裏返る・奥は小さくゆっくり。壁紙の絵の上に重ねる SVG・momiji.py。視差効果を減らすなら消える）</li><li><b>雪</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>雪が積もったPUSH</b>（氷の色の面・上に雪がこんもり（前に3か所たれる）・下につらら・面に雪の結晶。雪の上がきらっ・ときどき雪のかたまりがポロッ・前を雪がふわふわ降る・押すと雪けむりがボフッ。見本「的中ボタン（雪）」）・壁紙に<b>いつも雪が降っている</b>（雪つぶ40こ＋結晶6こ・ふわふわゆれる・奥は小さくゆっくり。壁紙の絵の上に重ねる SVG・yuki.py。視差効果を減らすなら消える）</li><li><b>お正月</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>初日の出が映ったPUSH</b>（面に夜明けの空・右回りに回る金の光・初日の出・小さな富士山・金の雲・きらっと光る星・ななめに通る光。左下と右上に金の雲・押すと金の星と金の粉が広がる。見本「的中ボタン（お正月）」）・壁紙は<b>初日の出の光が右回りでいつも回る</b>（絵を「光より うしろ」と「光より前」の2まいに分けて、あいだの光12本を太陽のまん中で36秒に1回り。初日の出は<b>富士山の まん中</b>（頂上の まうえ）・<b>馬は 動かさない</b>（いまの絵のまま）。flat/newyear_banner.py --layers・newyear_wall.py。視差効果を減らすなら回らない）</li><li><b>桜・紅葉・雪の馬</b>（まさちゃんの指定）：壁紙の馬が<b>ときどき 首を下げて 草を食べる</b>（足は 4本とも 動かさない＝いまの絵のまま。紅葉の馬は 上げていた 手前の前足を 地面に おろした・5〜10秒ごとに 首を 1.6秒で ゆっくり地面まで下げて、1〜5秒 頭を小さく動かしながら 草を食べて、1.6秒で上げる。どれも ランダム（約2分で くり返し）。いまの絵と同じ馬・同じカメラで描いた55コマ（首の とちゅうは 頭の動く はばが そろう 47だんかい）の 動く所だけを 動きの はやさに合わせて めくる＝なめらか。flat/step_run.py・step_plan.py・step_wall.py。視差効果を減らすなら いまの絵）</li><li><b>競馬新聞</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>新聞でできたPUSH</b>（面が新聞の紙面：題字・赤い◎・記事の行・折り目・どきどきする赤い「号外」。見出しの「PUSH」は黒に赤いずれの影・厚みは かさねた新聞の束・押すと新聞の切れはしが舞う。見本「的中ボタン（競馬新聞）」）・壁紙は<b>墨の馬がいつも走っている</b>（いまの絵と同じ墨の馬・同じカメラで、ギャロップ1回10コマ・0.5秒。紙と字ごと馬の所だけ切りぬいて重ねる。flat/news_run.py・news_wall.py。視差効果を減らすなら止まった絵）</li><li><b>水墨画</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>墨画でできたPUSH</b>（面が墨画：和紙・にじむ遠い山・太い筆の一画に紙の色で抜いた「PUSH」・朱の落款「馬」・墨のしずくがにじむ・霧が横切る。左上に円相・押すと墨が飛び散る。見本「的中ボタン（水墨画）」）・壁紙は<b>2頭がいつも走っている</b>（いまの絵と同じ騎手と馬2頭・同じカメラ・同じ筆で、ギャロップ1回10コマ・足の運びをずらして競り合う。紙・山・地面ごと2頭の所だけ切りぬいて重ねる。flat/sumi_run.py・ink_wall.py。視差効果を減らすなら止まった絵）</li><li><b>メリーゴーランド</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>メリーゴーランドのPUSH</b>（上に しま模様の屋根と旗・面に金の柱の小さな木馬が回りながら上下・まわりの電球が交互に光る・押すと金の星とハートが広がる。見本「的中ボタン（メリーゴーランド）」）・壁紙は<b>木馬が柱にそって上下する</b>（2頭が交互に2.8秒で1往復・金の輪も一緒・床の影は上がると小さく。下の絵＋木馬はページの SVG・屋根と電球のうしろを通る。flat/carousel_banner.py --base・carousel_wall.py。視差効果を減らすなら止まる）</li><li><b>星座</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>星でできたPUSH</b>（夜空の面に 星座の「PUSH」：光る字の形・金の線・点ごとの星がきらっ・ふちの帯の小さい星を光が回る・ときどき流れ星・右上に三日月・押すと金の星と きらきらが広がる。見本「的中ボタン（星座）」）・壁紙は<b>うしろの星がゆっくり流れて、ペガサスがいつも きらきら。8秒に1回、鼻の頭から しっぽの先へ 星が つぎつぎに キラキラ</b>（同じ星を右から左へ流す・明るい星は速く暗い星はゆっくり・三日月のうしろを通る・星座の星が かわるがわる きらっ・外の線を光が回る。鼻 → 頭 → 首 → 背中 → しっぽの先の道すじを 光が1.8秒で進み、近い星から きらっ（翼と足の星は 少しおくれて）。下の絵＋星はページの SVG。flat/pegasus_banner.py --base・stars_wall.py。視差効果を減らすなら止まる）</li><li><b>勝負服</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>勝負服でできたPUSH</b>（面は黄色に青のひし形の勝負服の布・つやの光が流れる・白い縫い目・両がわに青い袖（黄の輪）がはためく・上に えり・押すと4色のひし形が広がる。見本「的中ボタン（勝負服）」）・壁紙は<b>馬がいつも走り、うしろの柄が右から左へ流れて くり返す</b>（いまの馬と同じ形・同じカメラでギャロップ10コマ・もくもくは うしろへ流れる。背景はコマ割りの柄を1まいにして くり返す。flat/silks_run.py・silks_wall.py。視差効果を減らすなら止まる）</li><li><b>ネオン</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>ネオンでできたPUSH</b>（夜のガラスの板に ピンクのネオン管の「PUSH」・水色のネオン管のわくを光が回る・ときどき「S」がちらっと暗くなる・まわりに ネオンの星と いなずま・押すと ネオン管のかけらと光の輪が広がる。見本「的中ボタン（ネオン）」）・壁紙は<b>馬がいつも走り、10秒に1回 流れ星が右上の空を流れる</b>（いまの馬と同じ形・同じカメラでギャロップ10コマ。flat/neon_run.py・neon_wall.py。視差効果を減らすなら止まった絵）</li><li><b>ドット絵</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>ドットでできたPUSH</b>（ぜんぶ5pxのドット・テーマと同じ16色：灰色の台に赤いボタン・太いドットの字「PUSH」（上は白・下は黄色）・面の上を ななめの光が ドットずつ通る・左に ▶ のカーソル・左上に回る金貨・右に きらっ・上下の動きも わくの光の輪も カクカク。押すと へこんで カクカク大きくなって消え、金貨・ハート・きらっ・ブロックが飛んで ちかちか消える。見本「的中ボタン（ドット絵）」）・壁紙は<b>馬がいつも走り、うしろの丘と雲が 右から左へ ゆっくり流れて くり返す（遠いので ゆっくり：丘は 画面のはばを 約24秒・雲は その半分の速さ。馬が止まる時は 景色も止まり、走りだすと だんだん もとの速さに）。走りだしてから4〜13秒（毎回ちがう）で ジャンプか一回転して こっちを1秒見てから また走りだす。20〜23秒に1回 立ち止まって2秒立つ</b>（いまのドットの馬と同じ形・同じカメラ。ジャンプ：けり出して 足をたたんで跳ぶ（地面に かげ）→ おりる（土けむり）→ こっちを向く／一回転：小さく跳ねて くるっと回って こっちを向いて おりる。こっちを1秒見て（まばたき）→ かまえる。立ち止まる：すべって止まる（土けむり）→ 立って待つ → かまえる。走りだしは どれも けり出す → 1歩め ゆっくり → 2歩め 少し速く → 全速（ギャロップ8コマ・0.5秒）。景色は 空・雲と丘（はば200ドットで くり返す・1ドットずつ動く）・前の景色（コース・さく・ゴール板・「GO!」）に分けて重ねる（ずれていない時は いまの絵と同じ）。決めておいた順番を87秒で1回り。ページを開くと「かまえる」から。下の絵とコマは ロスなしで、ドットは ぼかさない。flat/pixel_run.py・pixel_wall.py。視差効果を減らすなら止まった絵）</li><li><b>花火</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>花火でできたPUSH</b>（夏の夜空の面に 仕掛け花火の「PUSH」：字の線にそって 金の火の玉がならび ぱちぱち またたく・字の下から 金の火の粉が こぼれ落ちる・ふちに ピンク → 金の光の線・まわりの4か所で 小さな花火が かわるがわる開く。押すと 金・ピンク・水色の光のすじが 3重に開く大きな花火。見本「的中ボタン（花火）」）・壁紙は<b>花火4つを 少しずつずらして打ち上げ（光の玉が1秒で上がる）→ 咲いて → 4.7秒かけて 散り散りに消える（光の粒が ばらばらに広がって落ち、またたきながら消える・火の粉が落ちる）→ 4つが消えはじめた所で 馬の花火を打ち上げ → 1秒で咲いて 4.7秒で消える → 3秒後に また打ち上げ。3〜6回に1回は 5つ一斉</b>（足す光の絵を 光の粒ごとに8組に分けて重ねる：ぜんぶ足すと いつもの絵。175秒で1回り。flat/fireworks_banner.py --layers・fireworks_wall.py。視差効果を減らすなら いつもの絵）</li><li><b>子供向け</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>毛糸でできたPUSH</b>（ピンクの毛糸で編んだ面に クリーム色の太い毛糸で書いた「PUSH」：より目のある1本の毛糸・字ごとに ぴょこんと はねる・ふちの内がわの縫い目が ぐるっと すすむ・黄色いフェルトのふち。右下に 水色の毛糸玉と編み棒・左上に フェルトの星・左下に ハート・右上に ボタン。押すと むにゅっと つぶれて はじけ、毛糸のぽんぽん・ハート・星・ボタン・毛糸のきれはしが広がる。見本「的中ボタン（子供向け）」）・壁紙は<b>毛糸玉が左から右へ ころころ転がり（馬とロボットの うしろを通る）、ロボットの黒目と 馬のボタンの目が 追いかける（馬は 頭の下を通る時に のぞきこむ）→ ゆっくりになって止まる → 馬が ぴょん・ぴょんと跳ねて喜ぶ（ハートが3つ）→ ロボットが 拾いに とことこ → 足が当たって うっかり蹴っちゃう（あせ）→ あわてて追いかけて、毛糸玉といっしょに 右へ フェードアウト → 1秒後に 毛糸玉を 手に持って 右から戻ってくる（馬に見せる）→ 2秒後に 左へポーン（馬の上を越えて 左の外へ）→ 外に出てから 1.7秒あけて また左から 転がってくる。3〜8回に1回（ばらばら）は、追いかけようとした ロボットが 故障（ガクッ・目が ぐるぐる・アンテナが へにゃっ・火花・けむり）→ 馬が 前足を上げて 首を上にあげ「ヒヒーン！」→ ロボットが ピコーンと復活して 取りにいく（あとは いつもと同じ）。べつの 3〜8回に1回は、ロボットが 治らず（プスン）、馬が ぴょこぴょこ 取りにいって くわえて戻り、首を ふり上げて 左へポーン（そのあと ロボットは 再起動して もとの場所へ）</b>（いつもの絵と同じ部品を重ねて、動く所だけ動かす。ロボットは アンテナ・腕・足・体と頭に分けて動かす。馬は 向き・はねる・立ち上がる で動かす。9回ぶんを 132秒で1回り。kids.py・kids_wall.py。視差効果を減らすなら いつもの絵）</li><li><b>かわいい</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>ハートでできたPUSH</b>（ピンクの面に 白いハートを ならべて書いた「PUSH」：ハートが 左から右へ 波のように どきどき ふくらむ・白いふちに ピンクのハートが ぐるっと ならんで かわるがわる ちかっ・上に 大きいリボン（ゆらゆら）・両がわから 小さいハートが ふわふわ のぼる。押すと どきっと ふくらんで はじけ、ハートとキラキラが広がり、ハートの形の輪が広がる。見本「的中ボタン（かわいい）」）・壁紙は<b>小さいハート・大きいハート・リボンが いつも ゆれていて（ふわふわ・どきどき・ゆらゆら）、8秒で1回り：1〜5秒で ポニーは ぴょこぴょこ右へ・大きいハートは ふわっと左へ 近づいて、5秒で 鼻とハートが当たる（ハートが むにゅっ・ぽよん）→ その場所で ポニーが ぴょーん・ぴょんと飛び跳ねて喜ぶ（ハートが3つ）→ 6.4〜7.9秒で すーっと なめらかに もとの場所へ。それとは べつに 3〜9秒ごと（毎回ちがう）に こっちを1回見て、その3秒後に ゆっくり こっちを見て、1秒後に 2度見（目が まんまる・ぴょん・「！」）</b>（いつもの絵と同じ部品を重ねて、動く所だけ動かす。こっちを見る時は 頭だけ くるっと回して 正面の顔に。8回ぶんを96秒で1回り。cute.py・cute_wall.py。視差効果を減らすなら いつもの絵）</li><li><b>夕焼け</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>夕日の映ったPUSH</b>（面に夕焼け：こい紫 → 赤紫 → だいだい → 金の空・うすい雲の筋が ゆっくり流れる・水平線に しずみかけの夕日（まわりの光が ふわっと ふくらむ）・下は 夕日が映った水（光の筋が ゆらゆら）・鳥が2羽 はばたく・ときどき ななめに光が通る。クリーム色と さんご色のふち・こい紫の厚み・白い「PUSH」。右上を 鳥が3羽 ただよい、左下に 夕日の光が きらっ。押すと ふわっと ふくらんで はじけ、夕日の光の粒・きらっ・鳥が広がり、夕日の色の 光の輪が広がる。見本「的中ボタン（夕焼け）」）・壁紙は<b>馬がいつも走っていて（いまの絵と同じ馬のシルエットで ギャロップ10コマ・0.5秒・たてがみとしっぽが波打つ）、地面の草が 左から右へ 流れて くり返す（馬が左向きなので 前へ進んで見える）。10秒で1回り：1〜3秒で 夕日が丘のうしろへ ゆっくり沈んで だんだん暗くなり 3秒で真っ暗 → 3秒から 夕日が 地平線の下を上がってきて 4秒に顔を出し（3〜4秒は真っ暗）→ 明るくなりながら ゆっくり上がって 6秒で もとの位置</b>（空・夕日・地面・走るコマは flat/sunset_run.py の絵・暗くなるのは ページの幕。sunset_wall.py。視差効果を減らすなら いつもの絵）</li><li><b>ナイター</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>ナイター照明に照らされたPUSH</b>（面に ナイターのコース：夜空・星が ちかっ・スタンドの観客の光が ちらちら・白い柵・ダートの光だまり。上の左右に 照明（ランプの粒・十字と横に長い光）があって、ボタンへ 光のすじが ゆっくり ゆれながら当たる。あたたかい白とアンバーのふち・白い「PUSH」に照明の光。押すと ふわっと ふくらんで はじけ、照明の光の粒と きらっ が広がり、アンバーの光の輪。見本「的中ボタン（ナイター）」）・壁紙は<b>3頭が いつも走っていて、景色が右から左へ流れて くり返す（空とスタンドと照明は ゆっくり・奥の柵とダート・手前の柵ほど速い）。1〜5秒ごと（毎回ちがう）に となりどうしの順位が入れかわり（追いぬく）、照明がついてから 20秒で ゴール板が流れてきて 1着の鼻先を通る（板が ふわっと光る）→ 3頭が ゆっくり止まって（景色も止まる）5秒かけて 真っ暗に → 7秒 表彰（スポットライトの中に 勝った馬・騎手のガッツポーズ・優勝のレイ・金の「1着」のバッジ・紙ふぶき・カメラの光）→ 1秒で暗く → 2秒目に 照明が1つずつ ぱっとついて「スタート！」・3頭が走りだす。1着は レースごとに ばらばら（6レースで3頭とも2回・つづけて同じ馬はない）</b>（いまの絵と同じ馬と騎手・同じカメラで ギャロップ10コマ・0.5秒・影と うしろへ流れる砂けむりつき。止まる・立つ・走りだすは 足の運びが だんだん ゆっくり／速くなる 18コマ。表彰の絵は 1頭ずつ。背景は くり返せるように描き直した（照明は等間かくに）。1レース34秒・204秒で1回り。flat/night_run.py・night_wall.py。視差効果を減らすなら いまの絵）</li><li><b>大理石</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>大理石でできたPUSH</b>（面に 白い大理石：あたたかい白の地・灰色と金の すじ・うちがわに 金の細い二重のわく・上に つやの光・ときどき ななめに 光がすっと通る・すみに 光の きらっ。金のふち（あいだに 大理石の白い帯）・こい金の厚み・「PUSH」は しっぽり明朝の 金ぱくの字を 彫ったように。左右に 金の月桂樹の枝が ゆっくり ゆれる・金の きらっ。押すと まん中から ぴしっと ひびが走って くだけ（強く光らせない）、大理石の かけらと 金ぱく・きらっ が広がり、金の 光の輪が広がる。見本「的中ボタン（大理石）」）・壁紙は<b>像の馬が 8秒ごとに うしろを2度見して、くるっと 反対を向く：1〜2秒で ゆっくり うしろへ ふり向く（首と頭が こちらがわを通って 反対を向く）→ 前へもどって → 2.45秒に ぱっと 2度見（少し行きすぎて もどる）→ 3〜5秒の 2秒で 体ごと くるっと 反対向きに（こちらを向きながら回る・頭は うしろを見たまま 体が追いつく）。8秒後に 同じことを 反対へ（16秒で もとの向き）。ふり向いたあとの 休みに、9〜17秒ごと（ばらばら）で ヒヒィーン（体を起こして 首を上げ 頭をふり上げ、前足を 交互に 前へ 打ち出して 頭を少しふる・字はなし）か、右を向いている時だけ 台ごと ずっ！ずっ！と5回 右へすべって 画面の外へ消え（すべるたびに 台の下に 粉が ふわっ）、しばらくして 左を向いて 画面の右から ずっ！ずっ！と5回 もとの場所へ もどる（24秒）</b>（いまの絵と同じ場面・同じカメラ・同じ光で、像を 3D のまま動かして描いた コマ（像と台のまわりだけ：ふり向き 28・体が回る 58・ヒヒィーン 76）を めくる。すべる時は 像と台と影の絵を 背景だけの絵の上で 動かす（はじめと おわりは 止まっている時に いまの絵と ふわっと入れかえて、つなぎ目が見えない）。出来事の順番は 192秒で1回り。flat/marble_run.py・marble_wall.py。視差効果を減らすなら いまの絵）</li><li><b>開運</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>小判でできたPUSH</b>（ボタンが まるごと 小判：よこ長の だ円・金の地・内がわの だ円の線・たての ござ目・左右のはしに 桜の刻印・上に つやの光・ときどき ななめに 光がすっと通る・すみに 光の きらっ。明るい金のふち・下に 小判が2まい 重なった厚み・「PUSH」は 刻印のように 彫った字（Zen Antique Soft）。左右に 小さな小判が ふわふわ・金の キラッ。押すと ちゃりんと ちぢんで ふくらみ（強く光らせない）、小判と 丸い金貨・金の粉・キラッ が ふん水のように 上へ はじけて 落ち、金の 光の輪が広がる。見本「的中ボタン（開運）」）・壁紙は<b>いつも まわりに 小判が 上から下へ 降っている（うしろの小判は 蹄鉄と招き馬の うしろを通る・ゆれて くるっと 回り、ときどき きらっ）。招き馬の あげた右前足は 立体（まさちゃん「招くときはもっと腕動かして」「招く腕は立体にみてるようにして」：太さのある前足と 厚みのある ひづめを 3D で動かした コマ）。8秒ごとに：1〜2秒 ひづめが 前へ・うしろへ がたがた（前へ おれかけて 引っかかる・ふちの厚みが見える）→ 少し うしろへ ためて → 3秒で 一気に ひじから 前へ たおれて、ひづめが 手首で おれて 振り下ろす（近づいて 大きく・ひづめの 裏が見える）→ もどる。それとは べつに 11〜19秒ごと（ばらばら）に、首を上げて 上を向き（目も上を見る）、口を開けて ヒヒィーン（字はなし・頭と口が ふるえる・耳が たおれる・しっぽを ふる）と 鳴きながら 招く（前足を 前へ たおして もどす を 2〜3回）</b>（いつもの絵と同じ部品を重ねて、頭・顔・耳・たてがみ・しっぽを 動かす。右前足は 21コマを よこに ならべた帯を 窓の中で ずらして めくる。ヒヒィーンの順番は 96秒で1回り。flat/lucky_banner.py の parts・flat/lucky_maneki.py の rig・flat/lucky_arm.py・lucky_wall.py。視差効果を減らすなら いつもの絵）</li><li><b>黒板</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>黒板にチョークで書いたPUSH</b>（ボタンが 小さな黒板：緑の黒板に 消したあとの もや・木目の 木の枠・下に チョーク受け（白・黄・ピンクのチョークと 小さな黒板消し）。黒板に チョークで書いた 立体のボタン（上の面と 下の厚み・厚みに ななめの線）と「PUSH」（Yomogi・チョークの ざらざら）・左上に 黄色い星・右下に ピンクの花丸。まわりに チョークの星が きらっ・光の輪は チョークの点線。押すと ぎゅっと ちぢんで ふくらみ（強く光らせない）、チョークの粉が ふわっ・チョークのかけら（白・黄・ピンク）と 星が はじけて 落ち、まん中に ピンクのチョークで 花丸を さっと書く（花丸は 1本の線：うずまき → 花びら・線は 外に はみ出さない）。見本「的中ボタン（黒板）」）・壁紙は<b>10秒ごとに：1〜2.9秒で 黒板消しが たてに ゆっくり ごしごしして 馬を消す（こすった所に チョークの もやが残って ゆっくり うすくなる・チョークの粉が 落ちる）→ 3.5〜7.4秒で チョークが ゆっくり つぎの馬を書く（外の線を 鼻先から ひと回り → 地面の線 → しっぽから頭へ ジグザグに ぬる）。馬は 3種類を じゅんばんに：走る馬（いまの絵）→ くらと ゼッケン「1」をつけた競走馬（ゼッケンは 黄色のチョーク）→ 立っている馬</b>（いまの絵と同じ 3D の馬と チョークの ぬり方で描いた3頭。書く・消すは 馬の絵・もやの残る黒板で ぬった 線の のび（stroke-dashoffset）で、書きおわり・消しおわりに 同じ見た目の絵と 入れかえる。黒板消しとチョークは ページの SVG。30秒で1回り。flat/chalk_banner.py・flat/chalk_run.py・chalk_wall.py。視差効果を減らすなら いまの絵）</li><li><b>シルバー帯</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>シルバーでできたPUSH</b>（ボタンが まるごと みがいた銀の板：上は 空の映りこみ・まん中に 地平の映りこみ（こい帯）・下は また明るく・こまかい ヘアライン・上に つやの光。「PUSH」は 銀の 立体の字（こいふち・下に 厚み）。<b>めちゃくちゃ輝く</b>：光の帯が 1.8秒ごとに ななめに すうっと通り（2本）、通った字のかどが きらっ・面の あちこちで 0.32秒ごとに きらっ・ふちの こい線を 光が2つ ぐるっと回る・まわりで 大きい きらっ（横に のびる光）・光の粒が 下から上へ のぼる・まわりに 白い光。押すと ぎゅっと ちぢんで ふくらみ（強く光らせない）、銀の かけら・きらっ・光の粒が はじけ、まん中に 横に のびる光・銀の 光の輪が 2重に広がる。見本「的中ボタン（シルバー帯）」）・壁紙は<b>いつも 銀の馬の像が キラキラ輝く</b>（きらめき（14か所）が 4秒に2回ずつ ばらばらの順で きらっ（像の上を 左から右へ 通って 体を 光らせる 光の帯は まさちゃん「いらない」で やめた）・像の上の こまかい光の粒が ちかっ・光の粒が しっぽ・おしり・後ろ足から うしろへ ふわっと流れる・うしろの光の輪を 光が10秒で1回り（像の うしろを通る）。顔のすじは まさちゃん「もう少しフラット目に」で 平らにした（ゴールド帯も）。いまの絵と きらめきを ぬいた絵は flat/metal_run.py・metal_wall.py。視差効果を減らすなら いまの絵）</li><li><b>ゴールド帯</b>（まさちゃんの指定）：シルバー帯と同じ作りを金に。的中ボタンのPUSHは<b>ゴールドでできたPUSH</b>（みがいた金の板・金の 立体の字「PUSH」。<b>めちゃくちゃ輝く</b>：シルバー帯と同じ 光の帯・きらっ・ふちを回る光・のぼる光の粒を 金に・まわりに 金の光。押すと 金の かけら（金ぱく）・金の きらっ・金の 光の輪。見本「的中ボタン（ゴールド帯）」）・壁紙は<b>いつも 金の馬の像が 金に キラキラ輝く</b>（金の きらめき（光の帯は やめた）・うしろへ流れる 金の粉・光の輪を回る光。視差効果を減らすなら いまの絵）</li><li><b>マスター帯</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>説明書の上の絵と 同じ 長方形の テンゲルの PUSHが 緑の雷を まとう</b>（横長の ボタン 300×164：説明書の上の絵・版の行を 消した所（「テンゲル」の札の下）に 金の「PUSH」・金と紺のふち。明るい緑と 濃い緑の いなずま 32本が ふちに そって 1本ずつ ついたり消えたり（1回に 2〜6回 ちらちら・そのたび 形が かわる・線は いちばん細く・外へ 枝わかれ）・火花が 外へ とぶ。押すと ぎゅっと ちぢんで ふくらみ（強く光らせない）、いなずまが ふちから まわりへ ほとばしり（2回 ちらっ）、緑と白の 火花・ボタンの形の 緑の 光の輪が 2重に広がる。見本「的中ボタン（マスター帯）」）・壁紙は エンブレムの馬は 動かさず（元の絵のまま）、<b>いつも おしりから 後ろ足の まわりの 数字（0と1）が かわるがわる 反対の数字に（右から左へ 波のように）、枠じゅうに 明るい緑と 濃い緑の いなずまが ビリビリ（44本が 1本ずつ ついたり消えたり・いちばん細い線）・ときどき 枠から 大きな いなずま</b>（flat/tengel_run.py・tengel_wall.py。視差効果を減らすなら いまの絵）</li><li><b>クリスマス</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>クリスマスツリーのPUSH</b>（ボタンが まるごと クリスマスツリー：いちばん下の だんに「PUSH」・上に 2だんと 金の星・だんの ふちに 雪・金の かざり・赤と青と金の玉・あかりが ゆっくり またたく・まわりに 雪が ふる。押すと ちぢんで ふくらみ（強く光らせない）、金の星と 玉と 雪の結晶が はじけて 金の 光の輪。見本「的中ボタン（クリスマス）」）・壁紙は<b>サンタさんと クリスマスツリーと サンタの帽子の馬</b>（雪の夜の町・プレゼント。止まった絵・flat/xmas_banner.py）</li><li><b>ハロウィン</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>かぼちゃのPUSH</b>（ボタンが まるごと ジャック・オー・ランタン：光る 三角の目・「PUSH」は 光る口・中の光が ゆっくり ゆらぐ・まわりに こうもりと あめ。押すと ちぢんで ふくらみ、あめ・こうもり・小さな かぼちゃ・光の粒が はじけて オレンジの 光の輪。見本「的中ボタン（ハロウィン）」）・壁紙は<b>ドクロと ドラキュラと 光る かぼちゃと 魔女の帽子の馬</b>（満月・お城・こうもり。止まった絵・flat/halloween_banner.py）</li><li><b>バレンタイン</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>チョコのPUSH</b>（ボタンが まるごと 板チョコ：四角の くぼみ・ピンクの すじ・ピンクの 包み紙・チョコに うかした「PUSH」・ときどき つやが通る・まわりに ハートのチョコと トリュフ。押すと チョコの かけら・ハート・トリュフが はじけて ピンクの 光の輪。見本「的中ボタン（バレンタイン）」）・壁紙は<b>カップルと チョコと 赤いリボンの馬</b>（ハートの チョコを わたす 女の子・てれる 男の子・上から とろける チョコ。止まった絵・flat/valentine_banner.py）</li><li><b>ホワイトデー</b>（まさちゃんの指定）：的中ボタンのPUSHは<b>マシュマロのPUSH</b>（ボタンが まるごと ふわふわの マシュマロ：ぽよん ぽよんと ゆれる・水色の まるい「PUSH」・まわりに ピンクと水色の マシュマロ・水色の リボン。押すと ふにゃっと つぶれて ふくらみ、マシュマロ・キラッ・ハートが はじけて 水色の 光の輪。見本「的中ボタン（ホワイトデー）」）・壁紙は<b>カップルと マシュマロと 水色のリボンの馬</b>（マシュマロの びんを わたす 男の子・よろこぶ 女の子・マシュマロみたいな 雲。止まった絵・flat/whiteday_banner.py）</li></ul></div>
    <div class="box"><h3>光と見やすさ</h3><ul><li><b>視覚酔いしないように</b>：画面全体が回る・迫る（トンネル）・流れる・ゆれる動きはしない。背景は止めて、動くのは文字（ポンと出る・乱れる・ふるえる）・小さな光・きらめきと、「ど的中！！！！」と結果の背景の光の波と輪だけ（外へ広がる・回らない）。虹色が流れるのは4秒で1回りよりゆっくり</li><li>強く光るのは<b>画面のどの点でも1秒に3回まで</b>（光の点めつで気分が悪くなる人がいるため。スマホは画面が目に近いので、画面の10%の広さでも数えた）。動画の明るさを1コマずつ・点ごとに測って確かめた。画面全体が白く光るのは デカの0.04秒（一瞬まっ白）・フリーズの押した瞬間（白い画面。横に流れる帯は明るい色どうしで、切りかわっても点めつにならないようにした）・{sec(R)}秒（弱め）だけ。爆発の光は小さな範囲で1回ずつ。デカの虹の輪は同じ所が何回も光らないように大きさを変えた・虹の光の筋はゆっくり回す（30秒で1回り）・押したあとの暗い幕はPUSHの画面の暗さのまま始める（いったん明るくなってまた暗くなると、白い光の前にもう1回光ってしまう）。ハズレは光らない</li><li>iPhoneの「視差効果を減らす」がオンなら：フリーズ（プチュン）・ネオンのカット・虹の輪・炎のゆらゆら・きらめき・紙ふぶき・PUSHの動きを止める。押すと1秒真っ暗 → 虹色の画面と「ど的中」（上）・ボードをふわっと出す。効果音は右の「効果音のメモ」（見本の画面もタップで鳴る）</li></ul></div>
    <div class="box"><h3>容量</h3><ul><li><b>ボードに絵は使わない</b>（テーマの色・もよう・飾りのSVGとCSSだけ。見出しの字はテーマの見出しのフォント）。フリーズで足す絵は、テンゲルのアイコンから作った<b>ネオンの線画のマスク2枚</b>だけ（芯 1024 約59KB・光 512 約40KB。neon_icon.py。T1 の背景）。ほかの虹・文字・炎・ギザギザ・電気・ノイズはCSSとSVG</li><li>バグる画面をやめたので、<b>押した瞬間の画面の絵（スクリーンショット）はいらない</b>（前はアプリで撮る予定だった）</li><li>動きは全部CSS（動画なし）・新しいフォントなし（テーマのフォント・Dela Gothic One・BIZ UDPゴシック）。<b>ど的中の筆の字はフォントではなくSVGの形</b>（brush.py で筆の動きから描いた6文字：ど・て・き・！・的・中。brush_glyphs.json 約12KB。金の立体とまわりの光は CSS の drop-shadow）</li></ul></div>
  </div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{MEMO_W},"height":{MEMO_H}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


STILLS = ('s_hit_form', 's_hit_push', 's_hit_board', 's_big_push', 's_big_light', 's_big_board',
          's_fz_push', 's_fz_noise', 's_fz_line', 's_fz_doteki', 's_fz_dodo', 's_fz_logo', 's_fz_result',
          's_hd_result', 's_miss_form', 's_miss_board')

if __name__ == '__main__':
    out = os.environ.get('FX_OUT', P)
    for kind, (fn, _) in PAGES.items():
        open(f'{out}/{fn}', 'w', encoding='utf-8').write(page(kind))
        print(fn)
    open(f'{out}/Fx_Boards.dc.html', 'w', encoding='utf-8').write(boards_page())
    print('Fx_Boards.dc.html')
    if all(k in blobs for k in STILLS):
        open(f'{out}/Fx_Memo.dc.html', 'w', encoding='utf-8').write(memo_page())
        print('Fx_Memo.dc.html')
    if WAVES and all(k in blobs for v in SND.values() for k in v):
        open(f'{out}/Fx_Sound.dc.html', 'w', encoding='utf-8').write(sound_page())
        print('Fx_Sound.dc.html')
