# アプリに 入れる 絵・動画・音の フォルダを きめる（第4.146版・まさちゃん 2026/11/10 21:26「圧縮少しやわらか−45Mbの方でやって！」）
#   もと（マスター）＝ios/<名前>（fx_assets・bcp_assets・tc_assets・fig_assets）：道具が 作る もの。**さわらない・上書きしない**（作り直せない ものも ある）
#   軽い 版＝ios/lite/<名前>（kisekae/lite_assets.py が 作る：動画 CRF 29・絵 WebP quality 75・ほかは そのままの 写し ＋ 台帳 lite.info）
#   adir(名前)：軽い 版が あれば そちら（古く なって いたら 止める：もとを 作り直した あとは lite_assets.py を もう一度）・なければ もと。
#     LITE=0 で いつも もと（軽く する 前の 絵で ためす とき）。どちらも リポジトリには 入れない（.gitignore）
#   使う 所：build_ios.py（Resources に 入れる もの）・テスト（test_native.py・test_tc.py・test_fig.py・test_bcp_still.py・test_bcx_flash.py：アプリに 入る 絵で ためす）
import json, os, re, sys
W = os.path.dirname(os.path.abspath(__file__))
NAMES = ('fx_assets', 'bcp_assets', 'tc_assets', 'fig_assets')
INFO = 'lite.info'          # 台帳（JSON）。名前の おわりが json・webp・bin・m4a で ない ので、フォルダごと 入れる ビルドの 所でも アプリには 入らない


def master(name):
    return os.path.join(W, 'ios', name)


def lite(name):
    return os.path.join(W, 'ios', 'lite', name)


def superseded(name, files):
    """新しい 形に 置きかえた ので アプリにも 軽い 版にも 入れない ファイル（もとの フォルダには 残す＝マスターは 消さない・上書きしない）"""
    files = set(files)
    if name == 'fig_assets' and 'fg_shelf2.json' in files:      # 第4.153版：棚は 貼り直した fg_shelf2.*（kisekae/fig/shelf_reuv.py）を 使う。前の fg_shelf.* は 入れない
        return {f for f in files if re.fullmatch(r'fg_shelf(\.json|\.bin|_c\d+\.webp)', f)}
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
