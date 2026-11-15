# アプリの 中の「使って いない ファイル」を さがす（第4.175版：まさちゃん「アプリ内のいらないデータも消して！」）
#   python3 app_unused.py <Tengel.swiftpm の フォルダ か .zip> [-v]
#   → 使って いない ファイルが あれば 名前を 出して 1 で 終わる（なければ 0）。何も 消さない・何も 書きかえない
#
# なぜ いるか：build_ios.py は 素材の フォルダ（ios/tc_assets・ios/fig_assets）の 中身を ぜんぶ アプリに 入れる（古い 版は assets_dir.superseded() の 表で 外す）。
#   表に 書き忘れると、もう 使わない 絵・動画・音が アプリに 入った まま に なる。それを ここで 見つける（test_iphone_only.py が 毎回 たしかめる）
#
# 「使って いる」の 決め方（Resources の 中の ファイル 1つずつ）：
#   1) 名前が そのまま、アプリの 中の 文字（index.html・manual.html・*.js・*.json・*.svg・*.css・Swift）に 出て くる（自分の 中は 数えない）
#   2) 名前を 組み立てる 所（`tc_field_${name}.webp`・'ks_' + id + '.json'・"bcp_t_{}_b.webp"）に 当てはまる。
#      変わる 所（${…}）に 入る 字は、数字・空・コードや データに 字（'…'・"…"）で 出て くる もの だけ（何でも 当てはまる ことに しない）。
#      2段の 組み立て（'tc_se_' + nm + '.m4a' の nm が 'slot_' + n・'bite_' + 'apple'）は「+ の 前に 書かれた 字（'slot_' +）＋ 数字 か 字」まで 見る
#   3) 形の ファイル（<名前>.json と <名前>.bin を 読む ローダー）：<名前> が コードに 字で 出て くる（'tc_prop_bucket'）・
#      拡張子の ない 組み立て（`tc_horse_bk_${c}_s${s}${…}`）に 当てはまる・mesh('fg' + n) の 形に 当てはまる
# 見ない もの：Resources の 外（Swift・アイコン）・Resources の 中の フォルダ（ja.lproj：iOS が 読む）
# 限り（見つけられない もの。そこは 人が 読んで たしかめる・test_iphone_only.py の 版ごとの チェックが 見る）：
#   ・名前は 出て くるが、その コードには もう 来ない（死んだ コード）
#   ・使う 所が 一部 だけの 動画・音（第4.175版で 見つけた ノーマルど的中：極ど的中の 入りが はじめの 5.34秒 だけ 使う → kisekae/lite_assets.py の CUT・ACUT で はじめ だけ 入れる）
#   ・古い 名前を 読む 予備の コードが 残って いる もの（rt_<テーマ>_<部品>.webp：新しい rt_…2.webp が ない とき だけ 読む）
#   ・数字の 範囲（fg9.bin：フィギュアは 8体 だが、mesh('fg' + n) の n が いくつ までかは 見ない）
#   ・使って いない ファイル だけが 名前を 書いて いる ファイル
import os, re, sys, zipfile, tempfile, shutil

EXT = r'(?:webp|m4a|mp4|json|bin|woff2|svg|jpg|png|ttf|xlsx|html|js)'
TEXT = ('.html', '.js', '.json', '.svg', '.css')
V = '\x00'                                           # 組み立ての 形の 中の「変わる 所」の しるし


def _split(expr):
    # 'a' + x + '_' + y  →  ['a', V, '_', V]（かっこの 中に + が ある ときは まとめて V 1つ）
    out = []; depth = 0; cur = ''
    for ch in expr:
        if ch in '([{': depth += 1
        elif ch in ')]}': depth -= 1
        if ch == '+' and depth == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    out.append(cur.strip())
    parts = []
    for t in out:
        m = re.fullmatch(r"'([^'\n]*)'", t) or re.fullmatch(r'"([^"\n]*)"', t)
        parts.append(m.group(1) if m else V)
    return parts


def _norm(parts):
    # となり合う 字を つなぐ・先頭の フォルダ（tc_items/）を 落とす（アプリは 名前だけで 読む）
    out = []
    for p in parts:
        if p != V and out and out[-1] != V: out[-1] += p
        else: out.append(p)
    if out and out[0] != V and '/' in out[0]: out[0] = out[0].rsplit('/', 1)[1]
    return tuple(out)


def patterns(code):
    """コードの 中の 名前を 組み立てる 形：（拡張子つき の 形の 集まり・拡張子なし の 形の 集まり）。形は 字と V の 並び"""
    withx, noext = set(), set()
    for m in re.finditer(r'`([^`\n]{1,160})`', code):                       # `…${…}…`
        s = m.group(1)
        if '${' not in s: continue
        parts = []; i = 0
        while i < len(s):
            j = s.find('${', i)
            if j < 0: parts.append(s[i:]); break
            if j > i: parts.append(s[i:j])
            d = 1; k = j + 2
            while k < len(s) and d:
                d += (s[k] == '{') - (s[k] == '}'); k += 1
            parts.append(V); i = k
        fixed = ''.join(p for p in parts if p != V)
        if not re.fullmatch(r'[A-Za-z0-9_\-./]*', fixed): continue          # 名前に 使えない 字（空白・< など）が ある もの は 名前では ない
        p = _norm(parts)
        if re.search(r'\.' + EXT + r'$', fixed): withx.add(p)
        elif p and p[0] != V and len(p[0]) >= 6: noext.add(p)
    for m in re.finditer(r"'[A-Za-z0-9_\-./]{1,40}'\s*\+[^;\n]{1,100}?\+\s*'[A-Za-z0-9_\-]{0,30}\." + EXT + r"'", code):      # 'a' + x + '.webp'
        withx.add(_norm(_split(m.group(0))))
    for m in re.finditer(r'"([A-Za-z0-9_\-]*\{\}[A-Za-z0-9_\-]*\.' + EXT + r')"', code):                                    # "bcp_t_{}_b.webp"（データの 中の 形）
        a, b = m.group(1).split('{}', 1); withx.add(_norm([a, V, b]))
    for m in re.finditer(r"\bmesh\(\s*'([A-Za-z0-9_]{2,20})'\s*\+\s*\w+\s*\)", code):                                      # mesh('fg' + n)
        noext.add((m.group(1), V))
    return withx, noext


def literals(text):
    """コード・データの 中の 字（'…'・"…"）の 集まり"""
    lit = set(re.findall(r"'([A-Za-z0-9_\-]{1,60})'", text)); lit |= set(re.findall(r'"([A-Za-z0-9_\-]{1,60})"', text)); lit |= set(re.findall(r'`([A-Za-z0-9_\-]{1,60})`', text))
    return lit


def prefixes(code):
    """+ の 前に 書かれた 字（'slot_' + n の slot_）の 集まり：3字より 長い もの だけ"""
    return set(re.findall(r"'([A-Za-z0-9_\-]{3,40})'\s*\+", code))


def _fit(parts, name, ok):
    # 形（字と V の 並び）に 名前が 当てはまるか。V に 入る 字は ok(字) が 真の もの だけ（分け方は ぜんぶ ためす）
    if not parts: return name == ''
    p = parts[0]
    if p != V: return name.startswith(p) and _fit(parts[1:], name[len(p):], ok)
    return any(ok(name[:i]) and _fit(parts[1:], name[i:], ok) for i in range(len(name) + 1))


def unused(pkg):
    """アプリ（Tengel.swiftpm の フォルダ）を 調べる → dict(files=数, lit=[…], pat=[…], model=[…], unused=[…])"""
    R = os.path.join(pkg, 'Resources')
    files = sorted(f for f in os.listdir(R) if os.path.isfile(os.path.join(R, f)))
    corpus = {}
    for f in files:
        if f.endswith(TEXT): corpus[f] = open(os.path.join(R, f), encoding='utf8', errors='replace').read()
    for f in sorted(os.listdir(pkg)):
        if f.endswith('.swift'): corpus['swift:' + f] = open(os.path.join(pkg, f), encoding='utf8', errors='replace').read()
    code = '\n'.join(t for k, t in corpus.items() if k.endswith(('.html', '.js')) or k.startswith('swift:'))
    alltext = '\n'.join(corpus.values())
    withx, noext = patterns(code + '\n' + '\n'.join(t for k, t in corpus.items() if k.endswith('.json')))
    lit = literals(alltext); pre = prefixes(code)
    ok1 = lambda s: s == '' or s.isdigit() or s in lit
    ok = lambda s: ok1(s) or any(s.startswith(q) and len(s) > len(q) and ok1(s[len(q):]) for q in pre)
    res = dict(files=len(files), lit=[], pat=[], model=[], unused=[])
    for f in files:
        if any(f in t for k, t in corpus.items() if k != f): res['lit'].append(f); continue
        if any(_fit(p, f, ok) for p in withx): res['pat'].append(f); continue
        base, ext = os.path.splitext(f)
        if ext in ('.json', '.bin') and (base in lit or any(_fit(p, base, ok) for p in noext)): res['model'].append(f); continue
        res['unused'].append(f)
    return res


def _open(path):
    # フォルダ か zip（zip は 一時の 場所に ひらく）→（Tengel.swiftpm の フォルダ, 片付ける 関数）
    if os.path.isdir(path):
        if os.path.isdir(os.path.join(path, 'Resources')): return path, (lambda: None)
        for d in sorted(os.listdir(path)):
            if d.endswith('.swiftpm') and os.path.isdir(os.path.join(path, d, 'Resources')): return os.path.join(path, d), (lambda: None)
        raise SystemExit('Resources が 見つからない：' + path)
    tmp = tempfile.mkdtemp(prefix='app_unused_')
    with zipfile.ZipFile(path) as z: z.extractall(tmp)
    for d in sorted(os.listdir(tmp)):
        if d.endswith('.swiftpm'): return os.path.join(tmp, d), (lambda: shutil.rmtree(tmp, ignore_errors=True))
    shutil.rmtree(tmp, ignore_errors=True); raise SystemExit('zip の 中に .swiftpm が ない：' + path)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('-')]
    if not a: raise SystemExit('python3 app_unused.py <Tengel.swiftpm の フォルダ か .zip> [-v]')
    pkg, done = _open(a[0])
    try:
        r = unused(pkg); R = os.path.join(pkg, 'Resources'); size = lambda fs: sum(os.path.getsize(os.path.join(R, f)) for f in fs) / 1e6
        print(f'アプリの 中の ファイル {r["files"]}こ（{size(r["lit"] + r["pat"] + r["model"] + r["unused"]):.2f}MB）')
        print(f'  名前が そのまま コードに 出て くる：{len(r["lit"])}こ（{size(r["lit"]):.2f}MB）')
        print(f'  名前を 組み立てる 所に 当てはまる：{len(r["pat"])}こ（{size(r["pat"]):.2f}MB）')
        print(f'  形の ファイル（ローダーが 読む）：{len(r["model"])}こ（{size(r["model"]):.2f}MB）')
        print(f'  使って いない：{len(r["unused"])}こ（{size(r["unused"]):.2f}MB）')
        if '-v' in sys.argv:
            for k in ('pat', 'model'):
                for f in r[k]: print('   ', k, f)
        for f in r['unused']: print('    使って いない', f, os.path.getsize(os.path.join(R, f)))
    finally: done()
    sys.exit(1 if r['unused'] else 0)
