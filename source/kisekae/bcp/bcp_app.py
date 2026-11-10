# 結果ボードカスタム（絵の ボード・第4.121版）：アプリに 入れる データ（window.__BCP）と 絵の ファイルの 名前
#   まさちゃんの デザイン 14こ（的中①〜⑨・ハズレ①〜⑤）。ボードを持つ馬（15）は bcx.js の 部品（ここには 入らない）
#   build_pwa.py（TARGET=app）が bundle_js() を index.html に 入れる。build_ios.py が files() の 絵を Resources に 入れる
#   （ios/bcp_assets/ か BCP_ASSETS=<フォルダ>。まさちゃんの 絵 なので リポジトリには 入れない。ない とき（CI）は いつもの ボードで 出る）
#   第4.145版：動く 絵で キャラなしの 背景（bgx）が ある デザインは 止まった 絵を 入れない（pics・stage_files・stills_out）
#   python3 kisekae/bcp/bcp_app.py            … 中身の 数と、見本を 作った ときの 置き方（作業フォルダの geom.json）と 同じかを 確かめる
#   python3 kisekae/bcp/bcp_app.py <絵の フォルダ> … 絵が そろって いるかも 確かめる
import glob, json, os, sys
import numpy as np

H = os.path.dirname(os.path.abspath(__file__))
DES = os.path.join(H, 'designs')


def _st(names, at=(1, 2, 3, 4)):
    return [[n, d] for n, d in zip(at, names)]


# 番号の 順（points.js の BOARD_ITEMS の 1〜14 と 同じ id・when）。段＝[連続の 数, デザイン]：その 数から その 絵（いちばん 上の 段は その 上も ずっと）
#   的中：連続的中の 数（1・2・3・4連勝〜）。出世馬：1・2・3・4・8・16・24連勝〜。ハズレ：続けて ハズレた 数（1・2・3・4回目〜）
ITEMS = [
    ('ring', 'hit', _st(['ring1', 'ring2', 'ring3', 'ring4'])),            # 的中① 結果ボードを廻る
    ('toast', 'hit', _st(['toast1', 'toast2', 'toast3', 'toast4'])),       # 的中② 馬達の祝杯
    ('race', 'hit', _st(['race1', 'race2', 'race3', 'race4'])),            # 的中③ 馬レース結果ボード
    ('snap', 'hit', _st(['selfie1', 'selfie2', 'selfie3', 'selfie4'])),    # 的中④ 自撮り結果ボード
    ('seal', 'hit', _st(['stamp1', 'stamp2', 'stamp3', 'stamp4'])),        # 的中⑤ スタンプ結果ボード
    ('cup', 'hit', _st(['trophy1', 'trophy2', 'trophy3', 'trophy4'])),     # 的中⑥ トロフィー結果ボード
    ('hoist', 'hit', _st(['carry1', 'carry2', 'carry3', 'carry4'])),       # 的中⑦ 馬が運ぶ結果ボード
    ('bloom', 'hit', _st(['bouquet1', 'bouquet2', 'bouquet3', 'bouquet4'])),   # 的中⑧ 花束結果ボード
    ('climb', 'hit', _st(['shusse1', 'shusse2', 'shusse3', 'shusse4', 'shusse8', 'shusse16', 'shusse24'], (1, 2, 3, 4, 8, 16, 24))),   # 的中⑨ 出世馬
    ('rain', 'miss', _st(['miss1', 'miss1_2', 'miss1_3', 'miss1_4'])),     # ハズレ① 二人でしょんぼり
    ('next', 'miss', _st(['miss2', 'miss2_2', 'miss2_3', 'miss2_4'])),     # ハズレ② 次…！
    ('cover', 'miss', _st(['miss3', 'miss3_2', 'miss3_3', 'miss3_4'])),    # ハズレ③ 隠蔽作戦
    ('wait', 'miss', _st(['miss4', 'miss4_2', 'miss4_3', 'miss4_4'])),     # ハズレ④ ボード結果待ち
    ('pen', 'miss', _st(['miss5', 'miss5_2', 'miss5_3', 'miss5_4'])),      # ハズレ⑤ 書き換え参戦
]
THUMB = 'bcp_t_{}.webp'          # 設定の タイルの 見本（bcp_thumbs.py で 作る・いちばん はじめの 段）
# 第4.129版（まさちゃん 2026/11/08「完成した動くカスタムボードを、アプリ内に入れてほしい！」）：キャラが 動く 絵の ボード（kisekae/bcp/chr の 道具で 作った もの）。
#   chr/motion.json＝{ デザイン: { bgx・fgx（キャラなしの 背景・前の 絵）・layers（キャラ）・oc・ot（動かない 物）・top・amb（まわりの 光と 雲） } }（bcx.js の picParts）。
#   出世馬（climb）は まだ 動かない（止まった 絵）
MOTION = json.load(open(os.path.join(H, 'chr', 'motion.json'), encoding='utf8'))


def motion_files(name):
    """動く 絵の ボードの ファイル（今の 止まった 絵 bcp_<name>.webp・_fg.webp は のぞく）"""
    m = MOTION.get(name)
    if not m:
        return []
    fl = [m.get('bgx'), m.get('fgx')] + [l['src'] for l in m['layers']] + [l.get('f') for l in m['layers']]
    fl += [m[k]['src'] for k in ('oc', 'ot') if m.get(k)]
    if m.get('amb'):
        fl += [m['amb'][k] for k in ('m1', 'm2', 'm3', 'f')]
    out = []
    for f in fl:
        if f and f not in out and f not in (f'bcp_{name}.webp', f'bcp_{name}_fg.webp'):
            out.append(f)
    return out


# 第4.145版（まさちゃん 2026/11/10 20:04「やって！」＝止まった 版を やめて、動く 版の 部品を 重ねて 同じ 絵を 出す）：
#   キャラなしの 背景（bgx）が ある デザイン（48こ）は 止まった 絵（bcp_<name>.webp・_fg.webp）を アプリに 入れない（部品を 重ねた 形が 止まった 絵と 同じ：chr/chr_snap.py）。
#   トロフィー（光と 雲だけ・bgx なし）と 出世馬（動かない）は 止まった 絵の まま。止まった 絵は 部品を 作り直す ときの もと なので 絵の フォルダ（ios/bcp_assets）には 残す
def pics(name):
    """アプリが 読む 背景と 前の 絵の 名前（bcx.js の picBg・picFg と 同じ きまり）。
       第4.150版（まさちゃん 2026/11/11 02:36「結果カスタムボードの動き全部無くして！…その代わり、画質あげて！」）：どの デザインも 止まった 絵（bcp_<name>.webp・前の 絵 _fg.webp）。
       キャラが 動く 部品（chr/motion.json の bgx・fgx・layers・光と 雲）は アプリに 入れない（道具と 部品は 手元に のこす：もどす ときは この 関数と design の mo）"""
    bg = f'bcp_{name}.webp'
    fg = f'bcp_{name}_fg.webp' if cfg(name).get('fg') else None
    return bg, fg


def stage_files(name):
    """その デザインで アプリが 読む 絵 ぜんぶ（背景・前の 絵・動く 絵の 部品・まわりの 光と 雲）"""
    bg, fg = pics(name)
    return [bg] + ([fg] if fg else [])      # 第4.150版：止まった 絵 だけ（動く 絵の 部品 motion_files は 入れない）


def cfg(name):
    return json.load(open(os.path.join(DES, name + '.json'), encoding='utf8'))


def geom(c):
    """bcp_bg.py と 同じ 置き方：絵の px → 舞台（390×844）の pt。板の 四すみ Qs・ボードの 高さ HP"""
    Q = np.array(c['quad'], np.float64)
    fx0, fx1 = c['frame_lr']
    S = c.get('S') or (380.0 / (fx1 - fx0))
    OX = 195 - S * c.get('cx', (fx0 + fx1) / 2)
    OY = c['top_pt'] - S * (Q[0, 1] + Q[1, 1]) / 2
    wq = (np.linalg.norm(Q[1] - Q[0]) + np.linalg.norm(Q[2] - Q[3])) / 2
    hq = (np.linalg.norm(Q[3] - Q[0]) + np.linalg.norm(Q[2] - Q[1])) / 2
    HP = float(c.get('hp') or round(350 * hq / wq, 1))
    return S, OX, OY, HP, Q * S + np.array([OX, OY])


def design(name):
    c = cfg(name)
    assert c['name'] == name, name
    _, _, _, HP, Qs = geom(c)
    L = c['layout']
    lay = {k: L[k] for k in ('normal', 'rib', 'many') if k in L}
    assert not L.get('stars') and not L.get('garland') and not L.get('star_img'), name + '：ボードの 中の 飾りは 使わない（まさちゃん 21:49）'
    d = {'hp': HP, 'q': [[round(float(x), 2), round(float(y), 2)] for x, y in Qs], 'fg': 1 if c.get('fg') else 0,
         'ts': L.get('title_style', ''), 'nt': 1 if L.get('hide_title') else 0, 'L': lay}
    # 第4.150版：動きの データ（mo）は 入れない（bcx.js は mo が なければ 止まった 絵を 出す）
    if c.get('close_border'):
        sh = c.get('close_shadow') or ('0 0 0 1px rgba(0,0,0,.35),0 0 %s %s' % (c.get('close_glow_r', '10px'), c.get('close_glow', 'rgba(255,200,90,.35)')))
        d['cl'] = [c['close_border'], c.get('close_bg', 'rgba(0,0,0,.35)'), sh, c.get('close_css', '')]
    return d


def data():
    items, des = {}, {}
    for iid, kind, st in ITEMS:
        items[iid] = {'k': kind, 'st': st}
        for _, n in st:
            des[n] = design(n)
    return {'items': items, 'd': des, 'thumb': THUMB}


def files():
    """アプリの Resources に 入れる 絵（名前だけ・平らに 並べる・同じ 名前は 1回：トロフィーの 光と 雲の 向きの 絵は 4段で 1組）"""
    out = []
    for iid, _, st in ITEMS:
        out.append(THUMB.format(iid))
        for _, n in st:
            for f in stage_files(n):
                if f not in out:
                    out.append(f)
    return out


def stills_out():
    """アプリに 入れない 止まった 絵（部品を 重ねて 出す デザインの bcp_<name>.webp・_fg.webp）"""
    out = []
    for _, _, st in ITEMS:
        for _, n in st:
            use = stage_files(n)
            out += [f for f in [f'bcp_{n}.webp'] + ([f'bcp_{n}_fg.webp'] if cfg(n).get('fg') else []) if f not in use]
    return out


def bundle_js():
    s = json.dumps(data(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return 'window.__BCP=' + s + ';'


if __name__ == '__main__':
    d = data()
    print('items', len(d['items']), 'designs', len(d['d']), 'files', len(files()), 'js', len(bundle_js()),
          'motion', len(MOTION), 'motion files', sum(len(motion_files(n)) for n in MOTION), '入れない 止まった 絵', len(stills_out()))
    for n in MOTION:
        assert n in d['d'], n + '：アプリの デザインに ない'
    # 作業フォルダ（見本を 作った ところ）の geom.json と 同じか
    work = os.environ.get('BCP_WORK', '/home/claude/work/bcpic')
    seen = 0
    for cf in sorted(glob.glob(os.path.join(work, '*', 'cfg.json'))):
        c = json.load(open(cf, encoding='utf8')); n = c.get('name')
        if n not in d['d']:
            continue
        gp = os.path.join(os.path.dirname(cf), 'geom.json')
        if not os.path.exists(gp):
            continue
        g = json.load(open(gp))
        dd = d['d'][n]
        e1 = abs(g['HP'] - dd['hp']); e2 = float(np.abs(np.array(g['Qs']) - np.array(dd['q'])).max())
        same = json.dumps(c, sort_keys=True, ensure_ascii=False) == json.dumps(cfg(n), sort_keys=True, ensure_ascii=False)
        if e1 > 1e-6 or e2 > .01 or not same:
            print('ちがう', n, os.path.dirname(cf), round(e1, 4), round(e2, 4), 'cfg同じ' if same else 'cfgちがう')
        seen += 1
    print('geom を くらべた', seen, '/', len(d['d']))
    if len(sys.argv) > 1:
        miss = [f for f in files() if not os.path.exists(os.path.join(sys.argv[1], f))]
        print('絵が ない', len(miss), miss[:20])
