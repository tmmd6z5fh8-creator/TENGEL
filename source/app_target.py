# App Store版の中身（build_pwa.py の TARGET=app・説明書の 'app'・公開するページ）だけにかける変換
#  ・特定の競馬場・団体の名前（大井・JRA など）、商標の名前（WIN5）、版の名前（第13改訂版・第12 など）を、アプリの中に1つも残さない
#    開催場は、使う人が入れたもの・画像から読み取ったものだけが出る。マザーデータの名前は使う人が自由に付ける（はじめは「マザーデータ1〜3」）
#  ・アプリに入れるデータ（1つ目のマザーデータ）は、開催場の名前を消して「しるし」（ハッシュ）だけ残す。
#    入れた開催場（または画像から読んだ開催場）のしるしが同じなら、ふつうの判定。ちがえば【参考判定】（Web版と同じ動き）
#  ・プログラムの中のメモ（コメント）は消す（名前やメモが中に残らないように）
#  ・最後に、出さない言葉が1つも残っていないことを確かめる（残っていたら作らない）
# Web版（ホーム画面のアプリ）と claude.ai版は、この変換をしない（今までどおり）
import os, re, unicodedata

# アプリの中に出さない言葉（競馬場・団体・商標・版の名前・個人の呼び名）
FORBIDDEN = ['大井', '船橋', '川崎', '浦和', '門別', '盛岡', '水沢', '金沢', '笠松', '名古屋', '園田', '姫路', '高知', '佐賀', '帯広',
             '札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉', 'ばんえい',
             'JRA', 'NAR', 'TCK', 'WIN5', 'Win5', '中央競馬', '地方競馬', '南関', 'UMACA', 'ウインズ',
             '改訂', '第13', '第12', '第11', 'まさちゃん', '姫に送', '姫フィルター',
             # App Store版は画像の読み取りを端末の中でするので、外のAIサービス・APIキーの名前も入れない
             'Anthropic', 'anthropic', 'Claude', 'sk-ant', 'APIキー', 'platform.claude']


def norm_venue(s):
    """開催場の名前をそろえる（全角・半角・空白・「競馬場」「競馬」をそろえる）。JSの T.vnorm() と同じ"""
    s = re.sub(r'\s', '', unicodedata.normalize('NFKC', str(s or '')))
    return re.sub(r'(競馬場|競馬)$', '', s)


def fnv(s):
    """開催場の名前の「しるし」（名前そのものはアプリに入れない）。JSの T.vhash() と同じ（FNV-1a 32bit・文字ごと）"""
    h = 0x811c9dc5
    for ch in norm_venue(s):
        h ^= ord(ch); h = (h * 0x01000193) & 0xffffffff
    return format(h, 'x')


def mother(rows):
    """アプリに入れるマザーデータ（1つ目）：開催場の名前を消して、id の 'oi' を 'm1' に。開催場は「しるし」だけ返す"""
    venues = sorted({r.get('venue') or '' for r in rows} - {''})
    out = []
    for r in rows:
        x = dict(r); x['venue'] = ''
        x['id'] = re.sub(r'-[a-z]+(-\d+)$', r'-m1\1', x['id'])
        assert x['id'] != r['id'] or not r.get('venue'), r['id']
        out.append(x)
    return out, [fnv(v) for v in venues]


# ---------- コメントを消す（文字列・テンプレート・正規表現の中はそのまま） ----------
_KW_RE = ('return', 'typeof', 'case', 'do', 'else', 'in', 'of', 'new', 'delete', 'void', 'throw', 'yield', 'await', 'instanceof')


def strip_js_comments(src):
    out, i = _scan(src, 0, False)
    return ''.join(out)


def _scan(src, i, in_expr):
    """src[i:] を読んで、コメントを除いた部分を返す。in_expr＝テンプレートの ${ } の中（対応する } で止まる）"""
    out, n, depth, last, word = [], len(src), 0, '', ''
    while i < n:
        c = src[i]
        if in_expr and c == '}' and depth == 0:
            return out, i + 1
        if c in '"\'':
            j = i + 1
            while j < n and src[j] != c:
                if src[j] == '\\':
                    j += 2; continue
                if src[j] == '\n':
                    raise ValueError('文字列が閉じていない: ' + src[i:i + 60])
                j += 1
            out.append(src[i:j + 1]); i = j + 1; last, word = c, ''; continue
        if c == '`':
            buf, j = ['`'], i + 1
            while j < n:
                d = src[j]
                if d == '\\':
                    buf.append(src[j:j + 2]); j += 2; continue
                if d == '`':
                    buf.append('`'); j += 1; break
                if d == '$' and j + 1 < n and src[j + 1] == '{':
                    sub, j = _scan(src, j + 2, True)
                    buf.append('${' + ''.join(sub) + '}'); continue
                buf.append(d); j += 1
            else:
                raise ValueError('テンプレートが閉じていない')
            out.append(''.join(buf)); i = j; last, word = '`', ''; continue
        if c == '/' and src.startswith('//', i):
            j = src.find('\n', i); i = n if j < 0 else j; continue
        if c == '/' and src.startswith('/*', i):
            j = src.find('*/', i + 2)
            if j < 0:
                raise ValueError('コメントが閉じていない')
            out.append(' '); i = j + 2; continue
        if c == '/' and (last == '' or last in '(,=:[!&|?{};+-*%<>~^' or word in _KW_RE):
            j, cls = i + 1, False
            while j < n:
                d = src[j]
                if d == '\\':
                    j += 2; continue
                if d == '[':
                    cls = True
                elif d == ']':
                    cls = False
                elif d == '/' and not cls:
                    break
                elif d == '\n':
                    raise ValueError('正規表現が閉じていない: ' + src[i:i + 60])
                j += 1
            j += 1
            while j < n and (src[j].isalpha()):
                j += 1
            out.append(src[i:j]); i = j; last, word = '/', ''; continue
        if c in '{':
            depth += 1
        elif c == '}':
            depth -= 1
        if c.isspace():
            out.append(c); i += 1; continue
        if c.isalnum() or c in '_$':
            j = i
            while j < n and (src[j].isalnum() or src[j] in '_$'):
                j += 1
            word = src[i:j]; out.append(word); i = j; last = 'a'; continue
        out.append(c); i += 1; last, word = c, ''
    if in_expr:
        raise ValueError('${ が閉じていない')
    return out, i


def strip_web_only(text):
    """Web版だけの部分（/*@web-only*/ 〜 /*@/web-only*/：APIキーで Claude に読ませる画像の読み取りなど）を、App Store版からまるごと消す"""
    out, n = re.subn(r'/\*@web-only\*/[\s\S]*?/\*@/web-only\*/', '', text)
    if n != WEB_ONLY_BLOCKS:
        raise SystemExit(f'App Store版：Web版だけの部分（@web-only）の数がちがうよ（{WEB_ONLY_BLOCKS}のはずが{n}）')
    if '@web-only' in out:
        raise SystemExit('App Store版：@web-only の印が閉じていないよ')
    return out


WEB_ONLY_BLOCKS = 4   # pwa_shim.js（Claude での読み取り）・pwa_ui.js（APIキーのカード）・src.html（Claude への指示・メッセージ）


def strip_page_comments(html):
    """ページの <script> と <style> と HTML のコメントを消す（script・style の中の文字はHTMLのコメントとして扱わない）"""
    parts, pos = [], 0
    for m in re.finditer(r'(<(script|style)[^>]*>)([\s\S]*?)(</\2>)', html):
        parts.append(re.sub(r'<!--[\s\S]*?-->', '', html[pos:m.start()]))
        body = strip_js_comments(m.group(3)) if m.group(2) == 'script' else re.sub(r'/\*[\s\S]*?\*/', '', m.group(3))
        parts.append(m.group(1) + body + m.group(4)); pos = m.end()
    parts.append(re.sub(r'<!--[\s\S]*?-->', '', html[pos:]))
    return ''.join(parts)


def check_clean(text, what):
    """出さない言葉が残っていないか（残っていたら、どこかを出して止める）"""
    bad = []
    for w in FORBIDDEN:
        for m in re.finditer(re.escape(w), text):
            bad.append(f'「{w}」… {text[max(0, m.start() - 50):m.end() + 40]!r}')
    if bad:
        raise SystemExit(f'App Store版の{what}に、出さない言葉が {len(bad)} か所残っているよ：\n' + '\n'.join(bad[:80]))


def apply(text, table, what):
    """(前, 後, 数) の表で置きかえる。数＝前の文字がちょうどいくつあるはずか（ちがったら止める＝元のプログラムが変わったら気づく）。
    前が re.compile されたものなら正規表現で置きかえる。APP_TARGET_REPORT=1 のときは、止めずに全部の食い違いを出す（直すとき用）"""
    report = os.environ.get('APP_TARGET_REPORT') == '1'; bad = []
    for a, b, k in table:
        if hasattr(a, 'sub'):
            got = len(a.findall(text)); text2 = a.sub(lambda m: b, text)
        else:
            got = text.count(a); text2 = text.replace(a, b)
        if got != k:
            bad.append(f'App Store版の{what}：置きかえる文字の数がちがうよ（{k}つのはずが{got}つ）：{(a.pattern if hasattr(a, "sub") else a)[:90]!r}')
            if not report:
                raise SystemExit(bad[-1])
        text = text2
    if bad:
        print('\n'.join(bad))
    return text


# ---------- アプリの画面（index.html：判定エンジン・画面・pwa_shim.js・pwa_ui.js） ----------
# コメントを消したあとにかける
INDEX = [
    # 判定エンジン：版の名前・開催場の「しるし」・地元（ふつうの判定）かどうか
    ("const VERSION = '第13改訂版';",
     "const VERSION = 'テンゲルⅢ';\n"
     r"  const vnorm = v => String(v || '').normalize('NFKC').replace(/\s/g, '').replace(/(競馬場|競馬)$/, '');" "\n"
     "  const vhash = v => { let h = 0x811c9dc5; for (const ch of vnorm(v)) { h ^= ch.codePointAt(0); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16); };\n"
     "  const homeOf = v => !vnorm(v) || (typeof window !== 'undefined' && Array.isArray(window.__MOTHER_HOME) && window.__MOTHER_HOME.includes(vhash(v)));", 1),
    ("const isOi = (rec.venue || '大井') === '大井';", 'const isOi = homeOf(rec.venue);', 1),
    ("const venue = (inp.venue || '大井').trim() || '大井';\n    const isOi = venue === '大井';", "const venue = String(inp.venue || '').trim();\n    const isOi = homeOf(venue);", 1),
    ('return { VERSION, ZN,', 'return { VERSION, vnorm, vhash, homeOf, ZN,', 1),
    # 上の版の表示（「大井 第13改訂版」）：カスタム買い目のときだけ出す
    ('<span class="ver">大井 第13改訂版</span>', '<span class="ver"></span>', 1),
    ("v.textContent = (typeof Slots !== 'undefined' && Slots.on && Slots.active !== 1 ? '' : '大井 ') + '第13改訂版' + (T.isCustom() ? '・カスタム' : '');",
     "v.textContent = T.isCustom() ? 'カスタム買い目' : '';", 1),
    # 開催場：はじめは空（空なら、いま使っているマザーデータの開催場として判定）。候補は自分の記録にある開催場
    ('<input id="fVenue" list="venues" value="大井" autocomplete="off">', '<input id="fVenue" list="venues" value="" placeholder="空でもOK" autocomplete="off">', 1),
    (re.compile(r"const VENUES = \{ '大井': 'oi',[^\n]*?\};"), 'const VENUES = {};', 1),
    ("venueKey(venue || '大井')", "venueKey(venue || '')", 1),
    ("const blankForm = () => ({ id: null, venue: '大井',", "const blankForm = () => ({ id: null, venue: '',", 1),
    ("{ example: true, venue: '大井', r: '8',", "{ example: true, venue: '', r: '8',", 1),
    ("$('#venues').innerHTML = Object.keys(VENUES).map(v => `<option value=\"${v}\">`).join('');",
     "const fillVenues = () => { const vs = [...new Set([...st.bets.values()].map(b => String(b.venue || '').trim()).filter(Boolean))].slice(0, 40); $('#venues').innerHTML = vs.map(v => `<option value=\"${esc(v)}\">`).join(''); };\n"
     "$('#fVenue').addEventListener('focus', fillVenues);", 1),
    ("const venue = (f.venue || '大井').trim() || '大井';", "const venue = String(f.venue || '').trim();", 1),
    # 自分自身（マザーデータに入っている同じ日付・Rのレース）を外す：開催場の列がないので、日付とRで探す（1つ目も）
    ('if (!excluded && home && Slots.on && Slots.active !== 1 && f.date && f.r)', 'if (!excluded && home && f.date && f.r)', 1),
    ('J.isOi = home; J.mother = motherName(); J.motherN = Slots.on ? Slots.active : 1;',
     "J.isOi = home; J.mother = motherName(); J.motherN = Slots.on ? Slots.active : 1; J.builtin = !Slots.on || (slotObj(Slots.active) || {}).source === 'app';", 1),
    # マザーデータの名前と「地元」：アプリに入っているデータ＝しるし、自分で入れたデータ＝名前に開催場が入っているか
    (re.compile(r"const JRA_VENUES = \[[^\]]*\];\n"), '', 1),
    ("return s ? s.name : '大井'; }", "return s ? s.name : 'マザーデータ'; }", 1),
    ("function slotHome(s, venue) {\n  if (!venue) return false;\n  if (!s) return venue === '大井';\n  if (s.n === 1 && venue === '大井') return true;\n  const nm = s.name || '';\n"
     "  return nm.includes(venue) || (/JRA|中央/i.test(nm) && JRA_VENUES.includes(venue));\n}\n"
     "const motherHome = venue => Slots.on ? slotHome(slotObj(Slots.active), venue) : venue === '大井';\n"
     "const otherHome = venue => Slots.on ? Slots.list.find(s => !s.active && s.usable && slotHome(s, venue)) || null : null;",
     "function slotHome(s, venue) {\n  const v = T.vnorm(venue); if (!v) return true;\n  if (!s || (s.n === 1 && s.source === 'app')) return T.homeOf(v);\n  return T.vnorm(s.name).includes(v);\n}\n"
     "const motherHome = venue => slotHome(Slots.on ? slotObj(Slots.active) : null, venue);\n"
     "const otherHome = venue => Slots.on && T.vnorm(venue) ? Slots.list.find(s => !s.active && s.usable && slotHome(s, venue)) || null : null;", 1),
    # 芝のレース：アプリに入っているデータはダートだけ
    ("const shiba = J.surface === '芝' && J.motherN === 1 ? '<span class=\"chip\">芝レース（大井はダートのみ）</span>' : '';",
     "const shiba = J.surface === '芝' && J.builtin ? '<span class=\"chip\">芝レース（アプリに入っているデータはダートだけ）</span>' : '';", 1),
    ("if (J.surface === '芝' && J.motherN === 1) o.push('※芝レース（大井はダートのみ）');",
     "if (J.surface === '芝' && J.builtin) o.push('※芝レース（アプリに入っているデータはダートのレースだけ）');", 1),
    ('o.push(`開催場：${J.venue}`);', "o.push(`開催場：${J.venue || '—'}`);", 1),
    # 単勝5連勝（WIN5）の説明
    ("'開催場を入れてね（WIN5はJRAのレースだよ）'", "'開催場を入れてね'", 1),
    ('JRAが指定する<b>5レースの1着を全部当てる</b>馬券だよ（', '主催者が指定する<b>5レースの1着を全部当てる</b>馬券（単勝5連勝）だよ（', 1),
    ('JRAのレースは【参考判定】（${esc(motherName())}のデータでの目安）だよ。', 'マザーデータと違う開催場のレースは【参考判定】（${esc(motherName())}のデータでの目安）だよ。', 1),
    ('<span class="small muted">（JRAのWIN5対象レースのとき）</span>', '<span class="small muted">（単勝5連勝の対象レースのとき）</span>', 1),
    # 記録・収支：開催場は入れたものだけ。【参考判定】は保存したときの判定で決める
    ("${(b.venue && b.venue !== '大井') ? esc(b.venue) + '（参考）' : ''}", "${(b.venue && (b.snap || {}).isOi === false) ? esc(b.venue) + '（参考）' : ''}", 1),
    ("venue: b.venue || '大井', date: b.date", "venue: b.venue || '', date: b.date", 1),
    ("${dlabel(b.date)} ${b.venue || '大井'}${b.r}R を開いたよ", "${dlabel(b.date)} ${b.venue ? b.venue + ' ' : ''}${b.r}R を開いたよ", 1),
    ("b.date.replace(/-/g, '/'), b.venue || '大井', b.r,", "b.date.replace(/-/g, '/'), b.venue || '', b.r,", 1),
    ("const others = list.filter(b => b.venue && b.venue !== '大井');\n  if (others.length) h += row('うち大井以外（参考）', others);",
     "const others = list.filter(b => (b.snap || {}).isOi === false);\n  if (others.length) h += row('うち参考判定のレース', others);", 1),
    # 実測：版の名前（第13・第12）→ 本線・旧本線・最新
    ("⑦ 本線（${T.isCustom() ? 'カスタム買い目' : '第13'}）と旧本線（第12）", "⑦ 本線（${T.isCustom() ? 'カスタム買い目' : '初期の買い目'}）と旧本線", 1),
    ('`第12の帯：${J.c.band12}　`', '`帯：${J.c.band12}　`', 1),
    ('第12の帯', '旧本線の帯', 2),
    ('第13新規', '最新', 12),
    ('item(`大井以外：${esc(v)}`, c, 50,', 'item(`他の開催場：${esc(v)}`, c, 50,', 1),
    # 買い目編集
    ('基盤データ（大井）では${pv.n}走。', '基盤データでは${pv.n}走。', 1),
    ('<h2>基盤データ（大井）の更新</h2>', '<h2>基盤データの更新</h2>', 1),
    ("'買い目を第13改訂版の初期に戻したよ'", "'買い目を初期の設定に戻したよ'", 1),
    ('第13改訂版の初期', '初期の買い目', 3),
    ('`このiPhoneに入っている${motherName()}のデータ：', '`この端末に入っている${motherName()}のデータ：', 1),
    # pwa_shim.js：マザーデータの名前（はじめ）・お知らせ
    # 第4.123版（まさちゃん 2026/11/04「マザーデータ①の名称をテンゲルデータに変えて！ だからマザーデータ②.③.④は、マザーデータ① マザーデータ② マザーデータ③にして！」）：1つ目＝テンゲルデータ・2〜4つ目＝マザーデータ①〜③
    ("var DEFAULT_NAMES = { 1: '大井競馬', 2: 'JRA', 3: '船橋競馬', 4: 'マザーデータ4' };", "var DEFAULT_NAMES = { 1: 'テンゲルデータ', 2: 'マザーデータ①', 3: 'マザーデータ②', 4: 'マザーデータ③' };", 1),
    ('下のテンゲル基盤データ（①〜⑦）には入らないよ。', '下の実測（①〜⑦）には入らないよ。', 1),
    ("'1つ目（大井）は空にできないよ'", "'1つ目は空にできないよ'", 1),
    ('アプリに入っている大井データ', 'アプリに入っているデータ', 3),
    # pwa_ui.js：マザーデータ・バックアップ・版
    ("const tagOf = n => +n === 1 ? { venue: '大井', key: 'oi' } : { venue: '', key: 'm' + n };", "const tagOf = n => ({ venue: '', key: 'm' + n });", 1),
    ("return esc(head) + '<br>マザーデータに入れられるのは、<b>姫フィルターのExcel（検証データのシートがあるもの）</b>だよ。分析シートと分析表に打ち込んだ新しいレースは、姫に送ってね（日付とRで合わせて入れるよ）。';",
     'return esc(head);', 1),
    ("<dd>${esc(APP_VER || '—')}（第13改訂版）</dd>", "<dd>${esc(APP_VER || '—')}</dd>", 1),
    ("中身 ${esc(APP_VER || '—')}（第13改訂版）</span>", "中身 ${esc(APP_VER || '—')}</span>", 1),
    ("'アプリに入っていた大井データ'", "'アプリに入っていたデータ'", 1),
    ("(NATIVE ? '大井のデータ（Excel）を新しくしたら、ファイルを選ぶだけで入れ替えられるよ。' : '大井の姫フィルター（Excel）を更新したら、ファイルを選ぶだけで入れ替えられるよ。')",
     "'Excel（検証データ）を新しくしたら、ファイルを選ぶだけで入れ替えられるよ。'", 1),
    ("'このマザーデータに入れるデータを選んでね。大井の<b>検証データと同じA〜P列</b>", "'このマザーデータに入れるデータを選んでね。<b>検証データの形のA〜P列</b>", 1),
    ("'大井のデータも新しくなるよ。'", "'マザーデータも新しくなるよ。'", 2),
    ('msg.push(`大井データも${d.mother.rows.length}走に戻したよ`);', 'msg.push(`「${L().names()[1]}」のデータも${d.mother.rows.length}走に戻したよ`);', 1),
    ("${data.mother ? '・大井データ' : ''}", "${data.mother ? '・1つ目のマザーデータ' : ''}", 1),
    # 単勝5連勝（WIN5 は商標なので使わない。2026/10/25 まさちゃん「5重勝じゃなくて、単勝5連勝にして！」）。関数の名前も
    ('WIN5', '単勝5連勝', 31),
    ('renderWin5', 'renderW5', 7),
    # 画像の 読み取りは 複勝を 読まない（第4.65版・2026/10/25 まさちゃん「複勝読み取り機能は無くして！別に無くて大丈夫！」）：案内の 文から 複勝を 外す
    ('<span class="small muted" id="ocrHint">単勝・複勝と3連単人気順のスクショを1〜3枚</span>', '<span class="small muted" id="ocrHint">単勝と3連単人気順のスクショを1〜3枚</span>', 1),
    ('<b>単勝・複勝の表</b>（馬番と単勝・複勝のオッズ）と<b>3連単の人気順</b>が、', '<b>単勝の表</b>（馬番と単勝のオッズ）と<b>3連単の人気順</b>が、', 1),
    ('開催場・R・距離・馬場・頭数・単勝・複勝・3連単の人気順を読み取って、入力欄に入れるよ。', '開催場・R・距離・馬場・頭数・単勝・3連単の人気順を読み取って、入力欄に入れるよ（複勝は読まないよ。大穴の並びに使うだけなので、なくても判定できるよ）。', 1),
    ('<li><b>単勝・複勝の表</b>（馬番・単勝・複勝のオッズが並んだ画面）と、', '<li><b>単勝の表</b>（馬番と単勝のオッズが並んだ画面）と、', 1),
]


# 第4.192版：Web版と 同じ ファイル（src.html・pwa_ui.js・pwa_shim.js・規約の 文）の 画面の 文を、アプリ だけ 漢字に そろえる（kanji_app.py と 同じ 決まり）。
#   まさちゃん 2026/11/18 01:11「漢字とひらがなが混合してるところをみつけて、統一させる 基本は漢字に統一する」。Web版の 画面は 変えない。
#   (前, 後, 数)：前の 言い回しが アプリの index.html に ちょうど その 数 ある（ちがったら 止まる＝元の 文が 変わったら 気づく）
KANJI_INDEX = [      # 長い 言い回しから 順に かける
    ('連勝の記録は、ふつうの記録・', '連勝の記録は、普通の記録・', 1),      # src.html の WIN5 の 文（INDEX で「単勝5連勝」に した あと）
    ('て削除され、もどせません（キーチェーンの「しるし」は残る', 'て削除され、戻せません（キーチェーンの「印」は残る', 1),
    ('たあとでも「ひとつ前のデータに戻す」で、いまのデータ', 'たあとでも「1つ前のデータに戻す」で、今のデータ', 1),
    ('終わったら、いちばん下の「結', '終わったら、一番下の「結', 1),
    ('きのために、ときどき<b>フ', 'きのために、時々<b>フ', 1),
    ('配なときは、ひとりで悩まず', '配なときは、一人で悩まず', 1),
    ('ります）に「しるし」として', 'ります）に「印」として', 1),
    ('<li>そのほか、記載さ', '<li>その他、記載さ', 1),
    ('すると消え、もどせません', 'すると消え、戻せません', 1),
    ('たデータは「ひとつ前のデ', 'たデータは「1つ前のデ', 1),
    ('を選べるよ（うすい番号＝', 'を選べるよ（薄い番号＝', 2),
    ('P</b>・いま ${p', 'P</b>・今 ${p', 1),
    ('me)}」とちがうかも。', 'me)}」と違うかも。', 1),
    ('ったゾーン、ほかの券種は', 'ったゾーン、他の券種は', 1),
    ('っているよ（ほかの買い目', 'っているよ（他の買い目', 1),
    ('と 入るよ（いまは 2頭', 'と 入るよ（今は 2頭', 1),
    ('的中の演出のあとに<b>', '的中の演出の後に<b>', 1),
    ('すと、演出のあとに払戻を', 'すと、演出の後に払戻を', 1),
    ('br><b>いまのデータ', 'br><b>今のデータ', 1),
    ('「足す」は、いまのレース', '「足す」は、今のレース', 1),
    ('を足したよ（いまのレース', 'を足したよ（今のレース', 1),
    ('緒に消えて、もどせないの', '緒に消えて、戻せないの', 1),
    ('sion}（いまの版が最', 'sion}（今の版が最', 1),
    ('のデータは「ひとつ前のデ', 'のデータは「1つ前のデ', 1),
    ('（発走時刻をすぎている', '（発走時刻を過ぎている', 1),
    ('art} をすぎている', 'art} を過ぎている', 1),
    ('><dt>いまの版</', '><dt>今の版</', 2),
    ('><dt>いまのデータ', '><dt>今のデータ', 1),
    ('データの形がちがうよ', 'データの形が違うよ', 5),
    ('購入額はあとで入れて', '購入額は後で入れて', 1),
    ('<dt>いまのデータ', '<dt>今のデータ', 2),
    ('>足す（いまのレース', '>足す（今のレース', 1),
    ('<p>はじめてのプ', '<p>初めてのプ', 1),
    ('足す（いまのレース', '足す（今のレース', 1),
    ('ときどき保存して', '時々保存して', 1),
    ('>いまの${p', '>今の${p', 1),
    ('>ほかのレース', '>他のレース', 1),
    ('ほんとに外す？', '本当に外す？', 1),
    ('ほんとに新しく', '本当に新しく', 1),
    ('結果を記録ずみ', '結果を記録済み', 1),
    ('予約ずみ（結果', '予約済み（結果', 1),
    ('ほんとに消す？', '本当に消す？', 4),
    ('>あとで入れる', '>後で入れる', 1),
    ('>いまは${e', '>今は${e', 1),
    ('ほんとに戻す？', '本当に戻す？', 2),
    ('ほんとに「${', '本当に「${', 1),
    ('>いまの「${', '>今の「${', 1),
    ('ほんとに入れ替', '本当に入れ替', 2),
    ('（ひとつ前に戻', '（1つ前に戻', 1),
    ('いまはこの端', '今はこの端', 1),
    ('いまはiPh', '今はiPh', 1),
    ('ほかの画面で', '他の画面で', 1),
    ('ひとつ前のデ', '1つ前のデ', 3),
    ('うすい番号は', '薄い番号は', 1),
    ('いまは入力例', '今は入力例', 1),
    ('いまのレース', '今のレース', 1),
    ('>とじる</', '>閉じる</', 1),
    ('つづけて<b', '続けて<b', 1),
    ('えらんでから', '選んでから', 1),
    ('ちがっていた', '違っていた', 1),
    ('いまの「${', '今の「${', 1),
    ('いまの版が最', '今の版が最', 2),
    ('いまは新しい', '今は新しい', 1),
    ('いまは自分で', '今は自分で', 1),
    ('いまのデータ', '今のデータ', 1),
    ('いまのアプリ', '今のアプリ', 1),
    # 第4.192版の 2回目（〜たあと・ぜんぜん・まちがい など）：前の 行の あとに かける
    ('買ったあとに読み込', '買った後に読み込', 2),
    ('受け取ってもどします', '受け取って戻します', 1),
    ('気のならびがぜんぜんちがうので', '気の並びが全然違うので', 1),
    ('まちがいがないか', '間違いがないか', 1),
    ('（あとから変え', '（後から変え', 1),
    ('金額は あとから', '金額は 後から', 1),
    ('入れたあとの金額', '入れた後の金額', 1),
    ('（いまと同じ内容', '（今と同じ内容', 1),
    ('入れたあとでも「1', '入れた後でも「1', 1),
]


# 第4.211版（まさちゃん 2026/11/22 21:36「不正にポイントやバトルコイン、お世話トークンを手に入れる抜け穴は無いか全部細かく徹底的に確認して！」）：
#   保存して ある 字を そのまま 画面（HTML）に 入れて いた 所を、字と して 出す（esc）・欄の 名前（id・for）に 使う 字は 英数字と - _ だけ。
#   App Store版は ポイントが ある ので、画面に 入った 字が タグと して 読まれる（＝スクリプトを 動かせる）と ポイントを 作れて しまう。打った 字・画像から 読んだ 字・ファイルから 読んだ 字が
#   ここへ とどく 道は 入口で ふさいで ある（区切りの 字は「-」に・ファイルの 字は 全角に・記録の id は 日付と 16進の 字）が、出す 側でも 止める（test_inject.py が 総当たりで 見る）。
#   Web版は かえない（ポイントが ない・src.html は Web版と 同じ ファイル）→ アプリを 作る ときに 置きかえる
SAFE_INDEX = [
    # 判定画面の 人気順位の 表：3連単の 組番（入力の 字）
    ("const x = J.x, arrow = s => String(s || '').replace(/[-－ー‐ｰ\\s]+/g, '→');\n  const so = (v, cb) => v == null ? '読取不可' : (cb ? arrow(cb) + ' / ' : '') + fmt(v) + '倍';",
     "const x = J.x, arrow = s => String(s || '').replace(/[-－ー‐ｰ\\s]+/g, '→');\n  const so = (v, cb) => v == null ? '読取不可' : (cb ? esc(arrow(cb)) + ' / ' : '') + fmt(v) + '倍';", 1),
    # 買い目の 組の 一覧：券種の 名前・組
    ("\">${R.label(t, c)}</span>`; }).join('　');", "\">${esc(R.label(t, c))}</span>`; }).join('　');", 1),
    ('<div class="betrow"><span class="bt">${t}</span>', '<div class="betrow"><span class="bt">${esc(t)}</span>', 1),
    # 予約済み・結果待ちの 窓：馬番の 丸・層の 札
    ('const chips = nos => (nos || []).map(no => `<span class="num ${wakuCls(no, n)}">${no}</span>`).join(\'\');', 'const chips = nos => (nos || []).map(no => `<span class="num ${wakuCls(no, n)}">${esc(no)}</span>`).join(\'\');', 1),
    ('<div class="rvh"><span class="lb L${L}">${L}</span>', '<div class="rvh"><span class="lb L${esc(L)}">${esc(L)}</span>', 1),
    # 記録の 入力の 欄の 名前（id・for）：記録の id から 作る
    ("const sfx = ctx.scope + '-' + (v.id || 'new');", "const sfx = (ctx.scope + '-' + (v.id || 'new')).replace(/[^A-Za-z0-9_-]/g, '_');", 1),
    ("sfx = 'rsv-' + b.id, sn = b.snap || {};", "sfx = ('rsv-' + b.id).replace(/[^A-Za-z0-9_-]/g, '_'), sn = b.snap || {};", 1),
]


# ---------- 第4.212版：値段・5連の 読み込み・記録を まとめて 消す（アプリ だけ） ----------
#   src.html・pwa_shim.js は Web版と 同じ ファイル なので かえず、アプリを 作る ときに 置きかえる（いちばん あとに かける：前の 表で 言葉を そろえた あとの 文）。
#   ・読み込み 200P → 400P・マザーデータの 枠 15,000P → 23,000P（画面の 文。値段 そのものは points.js の COST）
#   ・5連の 予想の 読み込み：何レース目か（n）を わたす（points_ui.js の readCharge が 1レースごとに 数える）
#   ・記録を まとめて 消す 窓口 TengelLocal.delBets（古い 台帳の リセット：old_reset.js。1回の 書きこみで 消して、画面には 1回 だけ 知らせる）
V212_INDEX = [
    ('読み込みの 200P は使うよ', '読み込みの 400P は使うよ', 2),
    ('（15,000P）', '（23,000P）', 3),
    ('w5: st.w5edit ? { date: st.w5.date } : null', 'w5: st.w5edit ? { date: st.w5.date, n: st.w5edit } : null', 1),
    ('putBets: function (list) {',
     "delBets: function (ids) { return ready.then(function () { var list = (ids || []).filter(function (id) { return mem.bets.has(id); }); if (!list.length) return 0; need(); "
     "var t = idb.transaction('bets', 'readwrite'), s = t.objectStore('bets'); list.forEach(function (id) { s.delete(id); }); "
     "return done(t).then(function () { list.forEach(function (id) { mem.bets.delete(id); }); notify('bets'); return list.length; }); }); },\n    putBets: function (list) {", 1),
]


# ---------- 第4.221版（まさちゃん 2026/11/25 12:13「テンゲルデータのみは、記録数載せなくていい！他の解放したマザーデータは全て表示して！」・答え「使っているデータだけ」）----------
#   画面の 上の データの 札（#dbpill）：テンゲルデータを 使って いる ときは 名前 だけ（前は「テンゲルデータ・記録 ○件」）。
#   マザーデータ①〜③を 使って いる ときは 今までどおり ぜんぶ（「マザーデータ① ○走・記録 ○件」）。札は 使って いる データ 1つ だけ。src.html は Web版と 同じ ファイル なので アプリを 作る ときに 置きかえる
V221_INDEX = [
    ("p.textContent = fx ? `${Slots.on ? motherName() : 'テンゲルデータ'}・記録 ${st.bets.size}件${st.canWrite ? '' : '（閲覧のみ）'}`",
     "p.textContent = fx ? `${Slots.on ? motherName() : 'テンゲルデータ'}${st.canWrite ? '' : '（閲覧のみ）'}`", 1),
]


def app_index(html):
    """App Store版の index.html：コメントを消して、名前を置きかえて、残っていないか確かめる"""
    html = strip_web_only(html)
    html = strip_page_comments(html)
    html = apply(html, INDEX, 'index.html')
    html = apply(html, KANJI_INDEX, 'index.html（漢字に そろえる）')
    html = apply(html, SAFE_INDEX, 'index.html（字と して 出す）')      # 第4.211版
    html = apply(html, V212_INDEX, 'index.html（第4.212版：値段・5連・記録を まとめて 消す）')
    html = apply(html, V221_INDEX, 'index.html（第4.221版：テンゲルデータの 札は 名前 だけ）')
    check_clean(html, 'index.html')
    return html


# ---------- 説明書（manual/build_manual.py の 'app'） ----------
# 項目（content.html・content_app.html）の中身にかける。共通の言いかえ（WIN5→単勝5連勝 など）は最後にページ全体にかける
MANUAL_SEC = [
    ('<b>マザーデータ</b><span>参考的中率に使うデータ。ふだんは「大井競馬」のままでOK', '<b>データ</b><span>参考的中率に使うデータ（テンゲルデータ・マザーデータ①〜③）。普段はテンゲルデータ（アプリに入っているデータ）のままでOK', 1),      # 第4.206版：アプリの 言い方に
    ('開催場は「大井」のように入れる', '開催場は空でもOK（空なら、今使っているマザーデータの開催場として判定）', 1),
    ('使っているマザーデータと開催場が違うと【参考判定】になるよ（大井のデータなら、大井以外のレース）。', '入れた開催場が、使っているマザーデータの開催場と違うと【参考判定】になるよ。', 1),
    ('第12改訂版のゾーン。比べるための記録用で、買い目じゃないよ', '前の版のゾーン。比べるための記録用で、買い目じゃないよ', 1),
    ('JRAのWIN5対象レースのとき、①〜⑤に入れる', '単勝5連勝の対象レースのとき、①〜⑤に入れる', 1),
    ('第13改訂版のはじめの設定だよ。', '初めの設定だよ。', 1),
    ('WIN5は、JRAが指定する5レースの1着を全部当てる馬券。', '単勝5連勝は、主催者が指定する5レースの1着を全部当てる馬券。', 1),
    ('層・区分・比。JRAのレースは【参考判定】', '層・区分・比。マザーデータと違う開催場のレースは【参考判定】', 1),
    ('第13新規（10/8〜）', '最新（10/8〜）', 2),
    ('第13（本線）と第12（旧本線）の的中・回収率と、見直しの進み具合', '本線と旧本線の的中・回収率と、見直しの進み具合', 1),
    ('はじめは第13改訂版のまま。', '初めは初期の買い目だよ。', 1),
    ('「第13改訂版の初期」か「カスタム」か', '「初期の買い目」か「カスタム」か', 1),
    ('基盤データ（大井）で、この買い目が当たった数', '今使っているデータで、この買い目が当たった割合（マザーデータ①〜③のときは数も。テンゲルデータのときは%だけ）', 1),
    ('「全部の区分を第13改訂版の初期に戻す」', '「全部の区分を初期の買い目に戻す」', 1),
    ('ルールは「テンゲルシステムⅢ 第13改訂版」のとおり。', 'ルールは「テンゲルシステムⅢ」のとおり。', 1),
    ('第12改訂版のゾーン。本線（第13）と比べるための記録用で、買い目じゃない', '前の版のゾーン。本線と比べるための記録用で、買い目じゃない', 1),
    ('第13改訂版の初期から変えた買い目', '初期の買い目から変えた買い目', 1),
    # 第4.123版：アプリに 入っている データは「テンゲルデータ」（中身・数は 見せない・レースは 足せない）／自分の データは「マザーデータ①〜③」
    ('<p>上半分は自分の収支、下半分はマザーデータの実測①〜⑦だよ。2つは別のデータ。</p>', '<p>上半分は自分の収支、下半分はマザーデータ①〜③の実測①〜⑦だよ（テンゲルデータの実測は見られないよ）。2つは別のデータ。</p>', 1),
    ('<h3>テンゲル基盤データ ①〜⑦</h3>', '<h3>実測 ①〜⑦（マザーデータ①〜③）</h3>', 1),
    ('<p>マザーデータと期間を選ぶと、そのデータで計算した表が出るよ。', '<p>マザーデータ①〜③と期間を選ぶと、そのデータで計算した表が出るよ（テンゲルデータを使っているときは、実測と見直し基準は出ないよ）。', 1),
    ('<span>その区分で、そのゾーンが実際に出た割合（マザーデータの実測）</span>', '<span>その区分で、そのゾーンが実際に出た割合（使っているデータの実測。テンゲルデータのときは%だけで、レースの数（n）は出さないよ）</span>', 1),
    ('<li><div><b>全文コピー・保存</b><span>判定の全文をコピー／判定と結果を保存</span></div></li>', '<li><div><b>全文コピー</b><span>判定の全文をコピー（買い目の予約は、下の「買い目」のカード）</span></div></li>', 1),
    ('<li><div><b>全STEPを表示</b><span>STEP0〜T3の全文</span></div></li>', '<li><div><b>人気順位の表</b><span>人気・馬番・記号・単勝オッズの表</span></div></li>', 1),
    ('<dt>マザーデータ</dt><dd>参考的中率と実測①〜⑦を計算する、もとのデータ（3つまで）。基盤データともいう</dd>', '<dt>テンゲルデータ</dt><dd>アプリに入っているデータ。参考的中率の%に使うよ（中身・レースの数は見られない・レースは足せない）</dd><dt>マザーデータ</dt><dd>自分で入れる、参考的中率と実測①〜⑦の元のデータ（①〜③）。①は初めから・②③はPカスタムで解放</dd>', 1),
]
MANUAL_PAGE = [
    ('WIN5', '単勝5連勝', None),   # 数は説明書の中身で変わるので数えない（最後に check_clean で確かめる）
]


def app_manual_sections(sec):
    """説明書の項目（{id: 中身}）を置きかえる。各言いかえが、どこかの項目にちょうど決まった数だけあること"""
    joined = '\n'.join(sec[k] for k in sorted(sec))
    for a, b, k in MANUAL_SEC:
        got = joined.count(a)
        if got != k:
            raise SystemExit(f'App Store版の説明書：置きかえる文字の数がちがうよ（{k}つのはずが{got}つ）：{a[:60]!r}')
    for x in sec:
        for a, b, _ in MANUAL_SEC:
            sec[x] = sec[x].replace(a, b)
    return sec


def kanji_manual(page):
    """第4.192版：説明書（アプリ）の 文を 漢字に そろえる（kanji_app.py の 決まり。<style> の 中は さわらない）。
    説明書の 中身（content.html）は Web版と 同じ なので、アプリを 作る ときに かける（content_app.html は 書きかえ ずみ）"""
    import importlib.util
    spec = importlib.util.spec_from_file_location('kanji_app', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kanji_app.py'))
    K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
    parts = re.split(r'(<style[^>]*>.*?</style>)', page, flags=re.S)
    return ''.join(x if x.startswith('<style') else K.convert(x) for x in parts)


def app_manual_page(page):
    page = strip_page_comments(page)
    for a, b, _ in MANUAL_PAGE:
        page = page.replace(a, b)
    page = kanji_manual(page)
    check_clean(page, 'manual.html')
    return page
