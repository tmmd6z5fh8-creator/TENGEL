# アプリに 入れる 絵・動画・音の フォルダを きめる（第4.146版・まさちゃん 2026/11/10 21:26「圧縮少しやわらか−45Mbの方でやって！」）
#   もと（マスター）＝ios/<名前>（fx_assets・bcp_assets・tc_assets・fig_assets）：道具が 作る もの。**さわらない・上書きしない**（作り直せない ものも ある）
#   軽い 版＝ios/lite/<名前>（kisekae/lite_assets.py が 作る：動画 CRF 24〈第4.155版までは 29〉・絵 WebP quality 75・ほかは そのままの 写し ＋ 台帳 lite.info）
#   adir(名前)：軽い 版が あれば そちら（古く なって いたら 止める：もとを 作り直した あとは lite_assets.py を もう一度）・なければ もと。
#     LITE=0 で いつも もと（軽く する 前の 絵で ためす とき）。どちらも リポジトリには 入れない（.gitignore）
#   使う 所：build_ios.py（Resources に 入れる もの）・テスト（test_native.py・test_tc.py・test_fig.py・test_bcp_still.py・test_bcx_flash.py：アプリに 入る 絵で ためす）
import json, os, re, sys
W = os.path.dirname(os.path.abspath(__file__))
NAMES = ('fx_assets', 'bcp_assets', 'tc_assets', 'fig_assets')
TC_GONE = frozenset(('tc_se_flop.m4a', 'tc_se_goron.m4a', 'tc_se_lie.m4a', 'tc_se_hop.m4a', 'tc_se_unlock.m4a'))
#   第4.156版：使わなく なった 音（tc/tc_care.js が 出さなく なった できごと flop・goron・lie。hop は 11/09 に ぴょんの 音を はしゃぐ（frisk）に かえて から 鳴らして いなかった。
#   unlock は tc_se_piron.m4a と 中身が 同じ ＝ アプリは piron を 鳴らす：tc/tc_app.js の SE_SKIP）
FX_GONE = re.compile(r'pm_.+\.webp|sfx_(pc|zp|spg|spg_up)\.m4a|spg_up\.mp4')
#   第4.162版（まさちゃん 2026/11/12 22:56「プレミアムど的中／超プレミアム神様的中／この二つ消して！」）：なくした 演出の 絵（pm_…：43まい）・音（プレミアム・超プレミアム・
#   超プレミアム神様・昇格）・昇格の 動画。アプリは もう 使わない（kisekae/build_fx.py の ASSET_FILES に ない）ので 軽い 版にも 入れない（もとの フォルダには 残す）
FX_NEW = ((('sgd_film2.mp4', 'sgd_last2.webp', 'sfx_sgd2.m4a'), ('sgd_film.mp4', 'sgd_last.webp', 'sfx_sgd.m4a')),
          (('sd_film2.mp4', 'sd_last2.webp'), ('sd_film.mp4', 'sd_last.webp')),
          (('nd_film2.mp4', 'nd_last2.webp'), ('nd_film.mp4', 'nd_last.webp')),
          (('sd_film3.mp4', 'sd_last3.webp'), ('sd_film.mp4', 'sd_last.webp', 'sd_film2.mp4', 'sd_last2.webp')),
          (('nd_film3.mp4', 'nd_last3.webp'), ('nd_film.mp4', 'nd_last.webp', 'nd_film2.mp4', 'nd_last2.webp')),
          (('sd_film4.mp4', 'sd_last4.webp'), ('sd_film.mp4', 'sd_last.webp', 'sd_film2.mp4', 'sd_last2.webp', 'sd_film3.mp4', 'sd_last3.webp')),
          (('nd_film4.mp4', 'nd_last4.webp'), ('nd_film.mp4', 'nd_last.webp', 'nd_film2.mp4', 'nd_last2.webp', 'nd_film3.mp4', 'nd_last3.webp')),
          (('gk_film2.mp4', 'gk_last2.webp'), ('gk_film.mp4', 'gk_last.webp')))
#   第4.162版（22:32「一枚目の球体のシーン消して！…鳥居とか文字関係はこのファイルのデータを使って！」）：超神様の 動画・さいごの 1まい・音は 新しい もの（…2）を 使う。
#   新しい ものが 3つ そろって いる ときは 前の もの（球体の 場面 あり）は 入れない（もとの フォルダには 残す）
#   第4.163版（11/13 00:15「極ど的中の演出の馬、文字をこのファイルと入れ替えて！」・02:35「ノーマルど的中演出の文字このファイルと入れ替えて！」）：極ど的中（紫電）と
#   ノーマルど的中の 動画・さいごの 1まいも 新しい もの（…2）。組ごとに、新しい ものが そろって いる ときだけ 前の ものを 入れない（音は 前と 同じ）
#   第4.164版（11/13 08:28「全体的に文字が読みづらい！色合い明るくして！あと一枚目は、ど！的中の文字少しだけ浮かせて！」）：字を 明るく した 動画・さいごの 1まい（…3）。
#   組は（新しい もの, その ときに 入れない 前の もの）。…3 が そろって いる ときは …2 と はじめの ものを 入れない（どれも もとの フォルダには 残す）
#   第4.171版（まさちゃん 2026/11/14 16:18「①的中演出の画質上げる！」）：極ど的中・ノーマルど的中は 3倍（1170×2532）で 描き直した 動画と さいごの 1まい（…4）・
#   神様極的中は 3倍に のばした もの（gk_film2.mp4・gk_last2.webp）。そろって いる 組は 前の もの（…3・はじめの もの）を 入れない
RT_OLD = re.compile(r'rt_(normal|maboroshi|kamisama)_(plate|knob|stick|ptr)\.webp')      # ルーレットの 前の 絵（第4.157版まで）
INFO = 'lite.info'          # 台帳（JSON）。名前の おわりが json・webp・bin・m4a で ない ので、フォルダごと 入れる ビルドの 所でも アプリには 入らない


def master(name):
    return os.path.join(W, 'ios', name)


def lite(name):
    return os.path.join(W, 'ios', 'lite', name)


def superseded(name, files):
    """新しい 形に 置きかえた ので アプリにも 軽い 版にも 入れない ファイル（もとの フォルダには 残す＝マスターは 消さない・上書きしない）"""
    files = set(files)
    if name == 'fx_assets':
        old = {f for f in files if FX_GONE.fullmatch(f)}
        for new, prev in FX_NEW:
            if set(new) <= files:
                old |= files & set(prev)
        return old
    if name == 'fig_assets' and 'fg_shelf2.json' in files:      # 第4.153版：棚は 貼り直した fg_shelf2.*（kisekae/fig/shelf_reuv.py）を 使う。前の fg_shelf.* は 入れない
        return {f for f in files if re.fullmatch(r'fg_shelf(\.json|\.bin|_c\d+\.webp)', f)}
    if name == 'tc_assets':                                     # 第4.156版（まさちゃん 2026/11/12 04:20「トレーニングセンターの馬の寝転ぶ演出は全部消して！」「いないデータの削除」）：
        old = files & TC_GONE                                   #   横に なる 動きの 音（どさっ・ごろん・ねる）は もう 鳴らない ので アプリに 入れない（もとの フォルダには 残す）
        # 第4.158版（まさちゃん 2026/11/12 08:59「画像がなんかまだらに色がついてるから綺麗にできる？」）：ルーレットの 絵は きれいに した 新しい 絵（rt_<絵>_<部品>2.webp：
        #   kisekae/tc/rt_clean.py）を 使う。新しい 絵が ある 部品の 前の 絵（rt_<絵>_<部品>.webp）は 入れない（もとの フォルダには 残す）
        old |= {f for f in files if RT_OLD.fullmatch(f) and f[:-5] + '2.webp' in files}
        # 第4.159版：お世話の あとの PUSH の 絵は 赤い ボタンと 黒い 台の 2まい（tc_push_cap.webp・tc_push_base.webp：kisekae/tc/push_asset.py）。
        #   はじめに 作った 1まいの 絵（tc_push.webp）は 使わない ので 入れない（もとの フォルダには 残す）
        if 'tc_push_cap.webp' in files and 'tc_push_base.webp' in files:
            old |= files & {'tc_push.webp'}
        # 第4.159版（まさちゃん 11/12 13:30「ドーン！！みたいな音と一緒にテロップ出して！」）：ルーレットの 高い 方は ドーン！！（tc_se_doon.m4a：kisekae/tc/telop_asset.py）・
        #   安い 方は デカ的中と 同じ 音 ＝ 前の 確定の 音（tc_se_rt_confirm.m4a）は もう 鳴らない ので 入れない（もとの フォルダには 残す）
        if 'tc_se_doon.m4a' in files:
            old |= files & {'tc_se_rt_confirm.m4a'}
        # 第4.161版（まさちゃん 2026/11/12 18:00「神様馬、赤丸の位置から動く変なパーツが飛び出てる／幻の馬は…立髪の毛の色がブラック…身体の表面…ボヤけて…全て改善して！」）：
        #   神様馬・幻の馬の 形は 直した 新しい 形（tc_horse_bk_<名前>2.json＋.bin：kisekae/tc/horse_fix.py）を 使う。前の 形は 入れない（もとの フォルダには 残す）
        for h in ('kamisama', 'maboroshi'):
            if {f'tc_horse_bk_{h}2.json', f'tc_horse_bk_{h}2.bin'} <= files:
                old |= files & {f'tc_horse_bk_{h}.json', f'tc_horse_bk_{h}.bin'}
        # 第4.165版（まさちゃん 2026/11/13 12:36「お世話トークン購入のアイコンやっぱりこっちで！」）：「お世話トークン購入」の 絵は 丸い 絵（tc_icon_buy2.webp：
        #   kisekae/tc/buy_asset.py）。はじめの 横長の 絵（tc_icon_buy.webp）は 使わない ので 入れない（もとの フォルダには 残す）
        if 'tc_icon_buy2.webp' in files:
            old |= files & {'tc_icon_buy.webp'}
        # 第4.171版（まさちゃん 2026/11/14 16:18「トレーニングセンターの神様馬出現中のBGM:もっとアップテンポで掻き立てられるようなBGM」）：神様馬の フィールドの BGM は
        #   新しい 曲（tc_bgm_divine2.m4a：kisekae/tc/snd/bgm_tengel.py）。前の 曲（tc_bgm_divine.m4a）は もう 鳴らない ので 入れない（もとの フォルダには 残す）
        if 'tc_bgm_divine2.m4a' in files:
            old |= files & {'tc_bgm_divine.m4a'}
        # 第4.171版（17:49「テンゲルのBGMは、この動画の背景で流れているBGMが理想！」）：テンゲルBGM は 第2稿（bgm_tengel2.m4a：のどかな 村の ふんいき）。第1稿（bgm_tengel.m4a）は 入れない（もとの フォルダには 残す）
        #   → 18:49「BGMもっとゆっくりで、鳥の声や笛の音入れて！」：第3稿（bgm_tengel3.m4a）。第1稿・第2稿は 入れない
        #   → 19:09「一回、鳥の声と笛の音だけにしてみて！もっとゆったりで！」：第4稿（bgm_tengel4.m4a）。第1稿〜第3稿は 入れない
        #   → 19:25「ここに馬の走る音と、もう少し太い音の笛を混ぜて！ゆったりね！」：第5稿（bgm_tengel5.m4a）。第1稿〜第4稿は 入れない
        #   → 19:41「もう一段階太い笛と、かなり音が低い笛も重ねて音入れて！」・19:42「馬の鳴き声と、馬が走る音追加して！」：第6稿（bgm_tengel6.m4a）
        #   → 19:57「この笛を、バイオリンぽくできる？」：第7稿（bgm_tengel7.m4a）→ 20:12「ごめん！笛に戻して！もっとゆったりで！」・20:15「あと風の音も入れて！」：第8稿（bgm_tengel8.m4a）→ 20:27「もっと笛の音ゆっくりして！」：第9稿（bgm_tengel9.m4a）
        #   きまり：bgm_tengel<番号>.m4a（番号なし＝第1稿）の うち、番号の いちばん 大きい もの だけ 入れる（前の 稿は もとの フォルダに 残す）
        import re as _re
        _bg = sorted((int(_m.group(1) or 1), f) for f in files for _m in [_re.fullmatch(r'bgm_tengel(\d*)\.m4a', f)] if _m)
        #   → 22:05「やっぱりテンゲルBGMも消して！無しでいいや！」（第4.172版）：テンゲルBGM は なし ＝ どの 稿も アプリに 入れない（もとの フォルダには 残す）
        old |= {f for _, f in _bg}
        # 第4.165版（まさちゃん 2026/11/13 14:16「何か変だから、2枚目のアイコンにして、作戦会議のすぐ下に設置してみて！」）：「壁紙&ボード着せ替え」の 絵は 横長の カプセル
        #   （tc_icon_kise2.webp：kisekae/tc/kise_asset.py）。はじめの 丸い 絵（tc_icon_kise.webp）は 使わない ので 入れない（もとの フォルダには 残す）
        if 'tc_icon_kise2.webp' in files:
            old |= files & {'tc_icon_kise.webp'}
        # 第4.168版（まさちゃん 2026/11/14 01:26「二枚目の赤丸の立髪の一部が色がおかしい！直して！」）：2段目の 大きさ（s2）の 馬は、たてがみの さいごの ふさを
        #   たてがみの 色に ぬり直した 絵と それを 指す 形の 名前（tc_c_<色>_s<数>v2.webp＋tc_horse_bk_<色>_s<数>v2.json：kisekae/tc/mane_fix.py）を 使う。
        #   2つ そろって いる 色は、前の 絵と 前の 形の 名前（.json）を 入れない（もとの フォルダには 残す。形 .bin と 法線の 絵は 今までの ものを 使う）
        for f in files:
            mm = re.fullmatch(r'tc_horse_bk_(.+_s\d)v2\.json', f)
            if mm and f'tc_c_{mm.group(1)}v2.webp' in files:
                old |= files & {f'tc_horse_bk_{mm.group(1)}.json', f'tc_c_{mm.group(1)}.webp'}
        return old
    return set()


def expected(name):
    """軽い 版に 置く ファイル（もとの フォルダの もの ぜんぶ〈新しい 形に 置きかえた ものは のぞく〉。結果ボードの 絵は アプリに 入れる もの だけ＝bcp_app.files()）"""
    m = master(name)
    if not os.path.isdir(m):
        return []
    if name == 'bcp_assets':
        p = os.path.join(W, 'kisekae', 'bcp')
        if p not in sys.path:
            sys.path.insert(0, p)
        import bcp_app
        return sorted(f for f in bcp_app.files() if os.path.isfile(os.path.join(m, f)))
    fs = [f for f in os.listdir(m) if os.path.isfile(os.path.join(m, f))]; old = superseded(name, fs)
    return sorted(f for f in fs if f not in old)


def manifest(name):
    mf = os.path.join(lite(name), INFO)
    return json.load(open(mf, encoding='utf8')) if os.path.isfile(mf) else None


def stale(name):
    """軽い 版が 古い わけ（新しければ ''）。軽い 版が ない ときは None"""
    try:
        man = manifest(name)
    except Exception as e:
        return '台帳（lite.info）が 読めない：' + str(e)
    if man is None:
        return None
    m, p = master(name), lite(name)
    want = expected(name)
    if sorted(man['files']) != want:
        d = sorted(set(want) ^ set(man['files']))
        return 'ファイルの ならびが かわった：' + '・'.join(d[:5]) + ('…' if len(d) > 5 else '')
    for f, e in man['files'].items():
        st = os.stat(os.path.join(m, f))
        if [st.st_size, st.st_mtime_ns] != e['src'][:2]:
            return 'もとが かわった：' + f
        pp = os.path.join(p, f)
        if not os.path.isfile(pp) or os.path.getsize(pp) != e['size']:
            return '軽い 版が ない・大きさが ちがう：' + f
    return ''


def adir(name):
    """アプリに 入れる（テストで 使う）フォルダ"""
    assert name in NAMES, name
    if os.environ.get('LITE', '1') == '0':
        return master(name)
    why = stale(name)
    if why is None:
        return master(name)
    if why:
        raise SystemExit(f'※ 軽い 版（ios/lite/{name}）が 古い：{why}\n   python3 kisekae/lite_assets.py で 作り直してね（LITE=0 を つけると もとの 絵を 使う）')
    return lite(name)


def is_lite(name):
    return os.environ.get('LITE', '1') != '0' and stale(name) == ''


if __name__ == '__main__':
    for n in NAMES:
        w = stale(n)
        print(n, '→', 'もと（軽い 版は ない）' if w is None else ('軽い 版' if w == '' else '古い：' + w), adir(n) if not w else '')
