"""着せ替えの字（App Store版 第4弾：アップデート指示書 15章・16.1）：テーマのフォント 29ファミリーを「使う字だけ」に しぼって WOFF2 にする。
     python3 kisekae/build_fonts.py [google/fonts の ofl フォルダ]   （既定：~/google/fonts/ofl＝github.com/google/fonts の sparse clone）
   出すもの（リポジトリに入れる：ios/fonts/ks/）
     <Family>-<太さ>.woff2 … しぼったフォント（SIL OFL 1.1 のまま。どのフォントにも Reserved Font Name は無い＝名前を変えなくてよい）
     OFL-<Family>.txt      … そのフォントの OFL の全文（コピー）
     fonts.json            … 一覧（family・weight・file・role・glyphs・bytes・元のファイル）。build_pwa.py が @font-face を作る・test が 字の 漏れを 確かめる
     chars_body.txt / chars_disp.txt … 残した字（本文用・見出し用）
   残す字（15章）
     本文（role=body：テーマの --font）… アプリの画面の言葉（src.html・pwa_ui.js・points_ui.js・reserve.js・fx.js・kisekae.js の文字列。コメントは除く）＋
                                          このアプリについて（legal）＋ 着せ替えの名前・説明 ＋ ASCII ＋ かな。ユーザーが入れた字（開催場・レース名など）は BIZ UDPGothic で出る
     見出し（role=disp：テーマの --dfont・PUSHの字・太さ 800 以上）… ロゴ・層・ゾーン・第○・○R・P・ボードの見出し（的中！…）・PUSH・タップ！・とじる・判定不可 などの決まった言葉＋ ASCII＋数字
   何回作っても 同じ ファイルに なる（fontTools の subset・brotli は node の zlib）。"""
import io
import json
import os
import re
import shutil
import sys
import unicodedata

K = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(K)
OUT = os.path.join(SRC, 'ios', 'fonts', 'ks')
sys.path.insert(0, K)
try:
    import brotli  # noqa: F401
except ImportError:
    import brotli_node as brotli
    sys.modules['brotli'] = brotli
from fontTools import subset  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.varLib import instancer  # noqa: E402

# Google Fonts の ofl フォルダの名前と、静的／可変のファイル
FOLDER = {'BIZ UDPMincho': 'bizudpmincho', 'Cherry Bomb One': 'cherrybombone', 'DotGothic16': 'dotgothic16', 'Hachi Maru Pop': 'hachimarupop',
          'Kaisei Decol': 'kaiseidecol', 'Kaisei Opti': 'kaiseiopti', 'Kaisei Tokumin': 'kaiseitokumin', 'Kiwi Maru': 'kiwimaru', 'Klee One': 'kleeone',
          'M PLUS 1': 'mplus1', 'M PLUS 1p': 'mplus1p', 'M PLUS Rounded 1c': 'mplusrounded1c', 'Mochiy Pop One': 'mochiypopone', 'Murecho': 'murecho',
          'Potta One': 'pottaone', 'Rampart One': 'rampartone', 'Reggae One': 'reggaeone', 'RocknRoll One': 'rocknrollone', 'Shippori Mincho': 'shipporimincho',
          'Shippori Mincho B1': 'shipporiminchob1', 'Tsukimi Rounded': 'tsukimirounded', 'Yomogi': 'yomogi', 'Yuji Mai': 'yujimai', 'Yuji Syuku': 'yujisyuku',
          'Yusei Magic': 'yuseimagic', 'Zen Antique Soft': 'zenantiquesoft', 'Zen Kaku Gothic New': 'zenkakugothicnew', 'Zen Maru Gothic': 'zenmarugothic',
          'Zen Old Mincho': 'zenoldmincho'}
WNAME = {100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black'}
IN_APP = ('BIZ UDPGothic', 'Dela Gothic One')   # もうアプリに入っている（ios/fonts・丸ごと）

# 見出し用の決まった言葉（アプリの --font-display の所・ボードの見出し・PUSH）
DISP_WORDS = ('テンゲルⅢ', 'ABC層堅警戒穴', '人気中穴大穴超大穴対象外', '第１２３０４５６７８９', '点的中デカど隠れハズレ神様超', '！!!?？', 'PUSH', 'タップ！とじる',
              '判定不可（データ不足）', '姫ゲート待機中', '記録を読み込み中…', '基盤データに接続できません', 'この月年の記録はまだないよ', '「」はまだ空だよ',
              'テンゲル基盤データ', '円Ｐ・→／〜％%.,:-+ 　', '予約レース結果', 'あと枚',
              # 第4.85版：ボードの 札（券種・的中／不的中／返還：太さ 800 → 見出し用の 顔に なる 字が ある）・単勝5連勝の ①〜⑩
              '単勝複勝枠連枠単馬連馬単ワイド３連複３連単返還不的中番', '①②③④⑤⑥⑦⑧⑨⑩')
ASCII = ''.join(chr(c) for c in range(32, 127))
KANA = ''.join(chr(c) for c in range(0x3041, 0x3097)) + ''.join(chr(c) for c in range(0x30A1, 0x30FB)) + 'ー゛゜々〆〇ゝゞヽヾ'


def strip_text(path):
    """ソースから 画面に出る 文字を 集める（コメントは消す）"""
    import importlib.util
    spec = importlib.util.spec_from_file_location('app_target', os.path.join(SRC, 'app_target.py'))
    at = importlib.util.module_from_spec(spec); spec.loader.exec_module(at)
    s = open(path, encoding='utf-8').read()
    if path.endswith('.html'):
        return at.strip_page_comments(s)
    try:
        return at.strip_js_comments(s)
    except Exception:
        return s


def body_chars():
    txt = ''
    for f in ('src.html', 'pwa_ui.js', 'points_ui.js', 'points.js', 'reserve.js', 'custom_rate.js', 'fx.js', 'kisekae.js', 'pwa_shim.js'):
        p = os.path.join(SRC, f)
        if os.path.exists(p):
            txt += strip_text(p)
    import importlib.util
    spec = importlib.util.spec_from_file_location('build_legal', os.path.join(SRC, 'legal', 'build_legal.py'))
    bl = importlib.util.module_from_spec(spec); spec.loader.exec_module(bl)
    txt += json.dumps(bl.about('app'), ensure_ascii=False)
    import build_kisekae as BK
    for t in BK.theme_list():
        txt += t['name'] + t['desc'] + t.get('group', '')
    txt += ''.join(DISP_WORDS) + ASCII + KANA
    chars = {c for c in txt if ord(c) >= 32 and unicodedata.category(c)[0] not in ('C', 'Z') or c == ' '}
    chars -= set('﻿‍️')
    chars -= {c for c in chars if 0x1F000 <= ord(c) <= 0x1FAFF or 0x2600 <= ord(c) <= 0x27BF}   # 絵文字は 端末の 絵文字で 出る
    return ''.join(sorted(chars))


def disp_chars():
    # 第4.85版：かな・カナも 入れる（見出しの 字で 出る「マザーデータ1」や 名前を つけた マザーデータ（かな）が、ない 字だけ 端末の 字に なって 字体が まざる のを ふせぐ）
    chars = set(''.join(DISP_WORDS) + ASCII + '０１２３４５６７８９' + KANA)
    chars -= {c for c in chars if unicodedata.category(c)[0] == 'C'}
    return ''.join(sorted(chars))


def plan():
    """(family, weight, role) の一覧：テーマの fonts（themes20・boards.OLD）と 的中ボタンの fonts（gen_fx.THEMED）から。
       role：body＝テーマの --font で 太さ 700 以下（本文の字を残す）／disp＝それ以外（見出しの字だけ）"""
    import build_kisekae as BK
    fam = {}
    for t in BK.THEMES_ALL:
        body = t['v']['font'].strip('"')
        for spec in t['fonts']:
            name, _, w = spec.partition(':')
            name = name.replace('+', ' ')
            ws = [int(x) for x in w.split('@')[1].split(';')] if w else [400]
            d = fam.setdefault(name, {})
            for x in ws:
                d[x] = 'body' if (name == body and x <= 700) else d.get(x, 'disp')
    for th in BK.push_fonts():
        name, _, w = th.partition(':')
        name = name.replace('+', ' ')
        ws = [int(x) for x in w.split('@')[1].split(';')] if w else [400]
        d = fam.setdefault(name, {})
        for x in ws:
            d.setdefault(x, 'disp')
    out = []
    for name in sorted(fam):
        if name in IN_APP:
            continue
        for w in sorted(fam[name]):
            out.append((name, w, fam[name][w]))
    return out


def source_font(ofl, family, weight):
    folder = os.path.join(ofl, FOLDER[family])
    files = sorted(os.listdir(folder))
    var = [f for f in files if f.endswith('.ttf') and '[' in f]
    if var:
        return os.path.join(folder, var[0]), True
    base = FOLDER[family]
    cand = [f for f in files if f.lower().endswith('.ttf') and f.lower().replace('-', '').startswith(base.replace(' ', '')) and f.endswith('-' + WNAME[weight] + '.ttf')]
    if not cand:
        cand = [f for f in files if f.endswith('-' + WNAME[weight] + '.ttf')]
    if not cand:
        raise SystemExit(f'{family} の 太さ {weight} の ファイルが ないよ：{files}')
    return os.path.join(folder, cand[0]), False


def license_text(ofl, family):
    """そのフォントの OFL の全文。OFL.txt が無いフォルダ（M PLUS Rounded 1c）は METADATA.pb の著作権の行＋OFL 1.1 の本文（ほかのフォルダの OFL.txt の 2段落目から）"""
    lic = os.path.join(ofl, FOLDER[family], 'OFL.txt')
    if os.path.exists(lic):
        return open(lic, encoding='utf-8').read()
    meta = open(os.path.join(ofl, FOLDER[family], 'METADATA.pb'), encoding='utf-8').read()
    m = re.search(r'copyright:\s*"([^"]+)"', meta)
    assert m and 'license: "OFL"' in meta, family
    body = open(os.path.join(ofl, 'mplus1p', 'OFL.txt'), encoding='utf-8').read()
    body = body[body.index('This Font Software is licensed'):]
    return m.group(1) + '\n\n' + body


def build(ofl, out=OUT):
    bc, dc = body_chars(), disp_chars()
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    open(os.path.join(out, 'chars_body.txt'), 'w', encoding='utf-8').write(bc)
    open(os.path.join(out, 'chars_disp.txt'), 'w', encoding='utf-8').write(dc)
    rows, total = [], 0
    for family, weight, role in plan():
        src, is_var = source_font(ofl, family, weight)
        font = TTFont(src)
        if is_var:
            font = instancer.instantiateVariableFont(font, {'wght': weight}, inplace=False, updateFontNames=False)
        text = bc if role == 'body' else dc
        opt = subset.Options()
        opt.layout_features = ['kern', 'ccmp', 'liga', 'locl', 'palt', 'mark', 'mkmk']   # 字の形の置きかえ（縦書き・異体字 など）は入れない＝字の数が ふくらまない
        opt.hinting = False
        opt.desubroutinize = True
        opt.name_IDs = ['*']           # 著作権・ライセンスの 名前の 表は 残す（OFL）
        opt.name_legacy = True
        opt.name_languages = ['*']
        opt.notdef_outline = True
        opt.recalc_bounds = True
        opt.recalc_timestamp = False
        opt.flavor = 'woff2'
        sub = subset.Subsetter(opt)
        sub.populate(text=text)
        sub.subset(font)
        font.flavor = 'woff2'
        fn = f'{family.replace(" ", "")}-{weight}.woff2'
        buf = io.BytesIO(); font.save(buf)
        data = buf.getvalue()
        open(os.path.join(out, fn), 'wb').write(data)
        glyphs = len(font.getGlyphOrder())
        total += len(data)
        rows.append(dict(family=family, weight=weight, file=fn, role=role, glyphs=glyphs, bytes=len(data), src=os.path.relpath(src, ofl)))
        open(os.path.join(out, f'OFL-{family.replace(" ", "")}.txt'), 'w', encoding='utf-8').write(license_text(ofl, family))
        print(f'{fn:40s} {role:4s} {glyphs:5d} glyphs {len(data) / 1024:7.1f} KB  ← {os.path.basename(src)}{" (wght " + str(weight) + ")" if is_var else ""}')
    json.dump(dict(chars=dict(body=len(bc), disp=len(dc)), fonts=rows, total=total, source='github.com/google/fonts (ofl)'),
              open(os.path.join(out, 'fonts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(rows)} files  {total / 1e6:.2f} MB  body chars {len(bc)}  disp chars {len(dc)}')
    return rows


if __name__ == '__main__':
    ofl = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/google/fonts/ofl')
    if not os.path.isdir(ofl):
        raise SystemExit(f'google/fonts の ofl フォルダが ないよ：{ofl}（git clone --depth 1 --filter=blob:none --sparse https://github.com/google/fonts → git sparse-checkout set --no-cone ofl/<名前> …）')
    build(ofl)
