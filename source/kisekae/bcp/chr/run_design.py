# キャラだけ 動かす（実験）：1つの デザインの 4つの 段を まとめて 切りぬいて 舞台の 絵に する
#   python3 run_design.py <デザインの 設定 json>
#   設定 = { base: <段1の chr の cfg（parts・fill など）>, seg: [[x0,y0,x1,y1, "名前"], …]（モデルを かける 四角）,
#            stages: [{ dir: <bcpic の デザインの フォルダ>, out: <chr の 出力>, over?: {…}（その 段だけ かえる 所） }, …],
#            motion: { <part の id>: {dp, dt, o?: "top"|"feet"|[x,y]} } , stage_json: <window.__BCPCHR の json> }
import json, os, subprocess, sys
import numpy as np
from PIL import Image
H_ = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(sys.argv[1], encoding='utf8'))
only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
SRV = D.get('srv', '/home/claude/work/bcpic/chr/stage')
def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        r = dict(a)
        for k, v in b.items(): r[k] = merge(a.get(k), v) if k in a else v
        return r
    return b
for st in D['stages']:
    name = json.load(open(os.path.join(st['dir'], 'cfg.json'), encoding='utf8'))['name']
    if only and name not in only: continue
    O = st['out']; os.makedirs(O, exist_ok=True)
    masks = []
    for sb in D['seg']:
        x0, y0, x1, y1, nm = sb[:5]
        mp = os.path.join(O, f'm_{nm}.png'); masks.append(mp)
        if not os.path.exists(mp) or os.environ.get('RESEG'):
            if len(sb) > 5 and sb[5] == 'flip':
                # 左右を 入れかえた 絵で モデルを かける（モデルは 場所で 見え方が かわる：二人でしょんぼりの 左の 馬は 入れかえると よく 見える）
                im_ = Image.open(os.path.join(st['dir'], 'src.png')).convert('RGB'); Wd = im_.width
                fp = os.path.join(O, '_flip_src.png'); im_.transpose(Image.FLIP_LEFT_RIGHT).save(fp)
                subprocess.run(['python3', os.path.join(H_, 'seg.py'), fp, f'{Wd - x1},{y0},{Wd - x0},{y1}', mp], check=True, stdout=subprocess.DEVNULL)
                Image.open(mp).transpose(Image.FLIP_LEFT_RIGHT).save(mp); os.remove(fp)
            else:
                subprocess.run(['python3', os.path.join(H_, 'seg.py'), os.path.join(st['dir'], 'src.png'), f'{x0},{y0},{x1},{y1}', mp], check=True, stdout=subprocess.DEVNULL)
    c = merge(json.loads(json.dumps(D['base'])), st.get('over', {}))
    # 段ごとに キャラの 印を たす（add_inner: {id: [形]}）・キャラの 設定を かえる（part_over: {id: {…}}）
    for pid, kv in st.get('part_over', {}).items():
        for p_ in c['parts']:
            if p_['id'] == pid:
                for k_, v_ in kv.items():
                    if v_ is None: p_.pop(k_, None)
                    else: p_[k_] = json.loads(json.dumps(v_))
    for pid, lst in st.get('add_inner', {}).items():
        for p_ in c['parts']:
            if p_['id'] == pid: p_.setdefault('inner', []).extend(lst)

    c['clean'] = os.path.join(st['dir'], 'clean.png'); c['out'] = O; c['masks'] = masks
    # src_fg：前の 絵（fg.png）を 重ねた 絵から 切りぬく（ボードの 中を 消した 時に 消えて、前の 絵で もどして いる 花の 所も キャラに 入る＝
    #   動いても 前の 絵の 所だけ 止まって 花が 切れて 見えない。まさちゃん 11/05 21:18「ここが花が切れてる！」）
    if D.get('src_fg') and os.path.exists(os.path.join(st['dir'], 'fg.png')):
        cl_ = np.asarray(Image.open(c['clean']).convert('RGB')).astype(np.float32)
        fg_ = np.asarray(Image.open(os.path.join(st['dir'], 'fg.png')).convert('RGBA')).astype(np.float32); fa_ = fg_[..., 3:4] / 255
        Image.fromarray(np.clip(fg_[..., :3] * fa_ + cl_ * (1 - fa_) + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(O, 'src_fg.png'))
        c['clean'] = os.path.join(O, 'src_fg.png')
    dcfg = json.load(open(os.path.join(st['dir'], 'cfg.json'), encoding='utf8'))
    if os.path.exists(os.path.join(st['dir'], 'fgmask.png')) and dcfg.get('fg') and not D.get('no_board'):
        c['board'] = {'quad': dcfg['quad'], 'fgmask': os.path.join(st['dir'], 'fgmask.png')}
    elif D.get('board_all'):            # 前の 絵が ない デザイン：板の 中 ぜんぶ（アプリの 字が 出る 所）を キャラに 入れない
        c['board'] = {'quad': dcfg['quad']}
    # 動きの 設定（なめらかな ふちの はばの 計算に つかう）・まとめる キャラ
    mo_ = {}
    for k_, v_ in D.get('motion', {}).items(): mo_[k_] = dict(v_)
    for k_, v_ in st.get('motion', {}).items(): mo_.setdefault(k_, {}).update(v_)
    c['motion'] = mo_
    grp_ = st.get('groups', D.get('groups'))
    if grp_ == 'all': grp_ = {'G': [p_['id'] for p_ in c['parts']]}
    c['groups'] = grp_ or {}
    json.dump(c, open(os.path.join(O, 'cfg.json'), 'w'), ensure_ascii=False, indent=1)
    r = subprocess.run(['python3', os.path.join(H_, 'chr_split.py'), os.path.join(O, 'cfg.json')], capture_output=True, text=True)
    if r.returncode: print(r.stdout[-800:], r.stderr[-1500:]); sys.exit(1)
    # だき合う・ふれ合う キャラは 1つに まとめて いっしょに 動かす（腕・ひづめが 2つに 分かれて 切れない）：groups: {新しい id: [id, …]}
    grp = st.get('groups', D.get('groups'))
    if grp == 'all': grp = {'G': [p_['id'] for p_ in c['parts']]}
    if grp:
        img_ = np.asarray(Image.open(c['clean']).convert('RGB'))
        newp = []; used = set()
        for gid, mem in grp.items():
            mem = [m_ for m_ in mem if any(p_['id'] == m_ for p_ in c['parts'])]
            if not mem: continue
            a_ = None; rgb_ = img_.astype(np.float32).copy()
            for m_ in mem:
                L_ = np.asarray(Image.open(os.path.join(O, m_ + '.png')).convert('RGBA')).astype(np.float32)
                al_ = L_[..., 3]; rgb_ = np.where((al_ > 0)[..., None], L_[..., :3], rgb_)
                a_ = al_ if a_ is None else np.maximum(a_, al_)
            Image.fromarray(np.dstack([np.clip(rgb_, 0, 255), a_]).astype(np.uint8), 'RGBA').save(os.path.join(O, gid + '.png'))
            newp.append({'id': gid, 'members': mem}); used |= set(mem)
        c['parts'] = newp + [p_ for p_ in c['parts'] if p_['id'] not in used]
        json.dump(c, open(os.path.join(O, 'cfg.json'), 'w'), ensure_ascii=False, indent=1)
    # 止まって いる ときの ちがい（かく 順に 重ねる）
    src = np.asarray(Image.open(c['clean']).convert('RGB')).astype(np.float32)
    comp = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.float32)
    for p in c['parts']:
        L = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA')).astype(np.float32); a = L[..., 3:4] / 255
        comp = L[..., :3] * a + comp * (1 - a)
    if os.path.exists(os.path.join(O, 'occl.png')):        # ボードの 前に 重ねる 所（動かない 元の 絵）
        oc_ = np.asarray(Image.open(os.path.join(O, 'occl.png')).convert('L')).astype(np.float32)[..., None] / 255
        comp = src * oc_ + comp * (1 - oc_)
    dmax = float(np.abs(comp - src).max())
    # 舞台の 絵
    mo = {'parts': [dict({'id': p['id']}, **D.get('motion', {}).get(p['id'], {})) for p in c['parts']]}
    # 段ごとの 動き（stage の motion）・キャラの 前に ある 動かない 物（occl：ボードの ふち など。キャラが うしろに まわりこむ）
    for p_ in mo['parts']:
        p_.update(st.get('motion', {}).get(p_['id'], {}))
    if c.get('occl'): mo['occl'] = c['occl']
    if D.get('occl_top'): mo['occl_top'] = True
    if D.get('layers_top'): mo['top'] = True            # キャラを ぜんぶ アプリの ボードの 上に（花束：花は いつも ボードの 前）          # 動かない 前の 絵の ボードの 前の 所を いちばん 上にも（chr_stage.py）
    mp_ = os.path.join(O, 'motion.json'); json.dump(mo, open(mp_, 'w'), ensure_ascii=False)
    r = subprocess.run(['python3', os.path.join(H_, 'chr_stage.py'), st['dir'], O, SRV, mp_, D['stage_json']], capture_output=True, text=True)
    if r.returncode: print(r.stdout[-800:], r.stderr[-1500:]); sys.exit(1)
    print(name, 'rest diff max', round(dmax, 3), '|', r.stdout.strip().splitlines()[-1])
