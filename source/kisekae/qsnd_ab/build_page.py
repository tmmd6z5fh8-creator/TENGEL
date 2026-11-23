# 聞きくらべの ページを 作る：page.tpl.html ＋ 音の 数字（meta_raw.json）＋ エリアの 名前・セリフ・鳴らし方（quest_data.json）→ <出力>/index.html と 音（a/・b/）
#   python3 kisekae/qsnd_ab/build_page.py <作業フォルダ> <出力フォルダ>
#   じゅんばん：mk_b.sh → chk_ab.py → quest_data.js → build_page.py → test_page.py → 公開（index.html と a/・b/ の MP3。_local.html は 手元で 見る 用）
#   くらべる 音：軽い 音に すると zip の 中で 10KB より 多く へる もの（へらない・大きく なる 音は 今の まま）
import json, os, shutil, sys
W, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
ZIP_NOW = 194979435          # App Store版 zip（第4.212版）
MIN_SAVE = 10000             # これ より へらない 音は 包み直さない
HOT_SNR = 36.0               # これ より 小さい（ちがいが 大きい）音に ◆
meta = {r['f']: r for r in json.load(open(f'{W}/meta_raw.json'))}
quest = json.load(open(f'{W}/quest_data.json'))


def excerpt(line):
    t = line.replace('　', ' ').strip()
    i = t.find('「')
    if i > 3: t = t[:i].strip()
    elif i == 0:
        j = t.find('」'); t = t[:j + 1] if j > 0 else t
    if len(t) > 20: t = t[:19].rstrip() + '…'
    return t


sounds = []
for q in quest:
    lv = q['lv']
    f = f'cb_q_bgm{lv:02d}.mp3'; m = meta[f]; b = q['b']
    if 'len' in b: lp = dict(ls=0.25, le=round(0.25 + b['len'] / 44100, 6), at=0.5)
    else: lp = dict(ls=round(b['ls'] / 44100, 6), le=None if b['le'] is None else round(b['le'] / 44100, 6), at=0)
    sounds.append(dict(id=f'bgm{lv:02d}', lv=lv, k='bgm', f=f, **lp))
    ses = []
    for k in range(len(q['s'])):
        taps = [i for i, x in enumerate(q['t']) if x == k and (i == 0 or q['t'][i - 1] != k)]
        assert len(taps) == 1, (lv, k, taps)
        i = taps[0]
        ses.append(dict(id=f"se{lv:02d}{'abc'[k]}", lv=lv, k='se', f=f"cb_q_se{lv:02d}{'abc'[k]}.mp3", tap=i + 1, say=excerpt(q['say'][i])))
    sounds += sorted(ses, key=lambda s: s['tap'])
for s in sounds:
    m = meta[s['f']]
    save = m['za'] - m['zb']
    s.update(sec=m['sec'], a=m['a'], b=m['b'], save=save, snr=m['snr'])
    s['in'] = 1 if save >= MIN_SAVE else 0
    if not s['in']: s['why'] = 'bigger' if save <= 0 else 'small'
    s['hot'] = 1 if s['in'] and m['snr'] < HOT_SNR else 0
    assert m['na'] == m['nb'] and m['lag'] == 0
assert len(sounds) == 37 and len({s['id'] for s in sounds}) == 37
inc = [s for s in sounds if s['in']]
data = dict(areas=[q['area'] for q in quest], sounds=sounds, total=dict(save=sum(s['save'] for s in inc), zip=ZIP_NOW, n=len(inc)))
tpl = open(f'{HERE}/page.tpl.html', encoding='utf8').read()
assert tpl.count('/*__DATA__*/null') == 1
js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
os.makedirs(OUT, exist_ok=True)
open(f'{OUT}/index.html', 'w', encoding='utf8').write(tpl.replace('/*__DATA__*/null', js))
for d in ('a', 'b'):
    shutil.rmtree(f'{OUT}/{d}', ignore_errors=True); os.makedirs(f'{OUT}/{d}')
    for s in inc: shutil.copyfile(f"{W}/snd/{d}/{s['f']}", f"{OUT}/{d}/{s['f']}")
# 手元で 見る 用（公開は しない）：公開の ときに つく 外わくと 同じ ような ものを つけた ページ
skel = ('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style></head><body>')
open(f'{OUT}/_local.html', 'w', encoding='utf8').write(skel + tpl.replace('/*__DATA__*/null', js) + '</body></html>')
hot = [s for s in inc if s['hot']]
print(f"くらべる 音 {len(inc)}（BGM {sum(1 for s in inc if s['k'] == 'bgm')}・効果音 {sum(1 for s in inc if s['k'] == 'se')}）  今の まま {37 - len(inc)}：{' '.join(s['id'] for s in sounds if not s['in'])}")
print(f"へる 量（zip）{data['total']['save']} B ＝ {data['total']['save'] / 1e6:.2f}MB   {ZIP_NOW / 1e6:.1f} → {(ZIP_NOW - data['total']['save']) / 1e6:.1f}MB")
print(f"◆ {len(hot)}：{' '.join(s['id'] + '(' + str(s['snr']) + ')' for s in hot)}")
print(f"ページ {os.path.getsize(OUT + '/index.html')} B   音 a {sum(os.path.getsize(f'{OUT}/a/' + x) for x in os.listdir(OUT + '/a'))} B・b {sum(os.path.getsize(f'{OUT}/b/' + x) for x in os.listdir(OUT + '/b'))} B（{len(os.listdir(OUT + '/a'))}＋{len(os.listdir(OUT + '/b'))} こ）")
for s in sounds: print(f"  {s['id']:7s} Lv{s['lv']:<2d} {'BGM' if s['k'] == 'bgm' else str(s['tap']) + 'タップ目'}  {s.get('say', '')}  {s['sec']}s save {s['save']} snr {s['snr']} in {s['in']} hot {s['hot']}" + (f" loop {s['ls']}〜{s['le']} at {s['at']}" if s['k'] == 'bgm' else ''))
