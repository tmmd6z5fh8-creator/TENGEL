"""PUSHボタンの 絵（第4.148版・まさちゃん 2026/11/10 20:36「（画像は1枚だけもらって、「光る・へこむ・はじける」はコードで動かす）これがいいかも！」
   → 11/11 00:02・00:05・00:16 に 31まい：壁紙 1つに 1まい・いつもの も）を、アプリに 入れる 形に する。
     python3 kisekae/push_art.py            ios/push_assets/src/<テーマの id>.png → ios/push_assets/pb_<id>.webp ＋ 台帳 pb.json（かわった もの だけ 作り直す）
     python3 kisekae/push_art.py --check    見る だけ（新しいか）
     python3 kisekae/push_art.py --force    ぜんぶ 作り直す
   もと（ios/push_assets/src/：まさちゃんの 絵 そのまま）は **読む だけ・上書きしない**。もとも できた 絵も リポジトリには 入れない（.gitignore）。
   する こと（絵の 中身は かえない）
     1) すき通りを ととのえる：うすい もや（アルファ 16 未満）は 消す・体（240 以上）は しっかり 不透明に・体から はなれた 小さな 点（64点 未満）は 消す
     2) 絵の まわりの 余白を 切って、4px だけ のこす
     3) 画面で 出す 大きさ（w・h：CSS の px）を 決める：どの 絵も 同じ くらいの 面積（AREA）・幅と 高さの 上限（MAX_W・MAX_H）
     4) いちばん 大きく 出す とき（虹色の 1.6倍・幅 372px まで＝fx.js の PZ）の 幅 × DPR に 合わせて 小さく して WebP（quality Q・すき通りは 劣化なし）
   アプリは 台帳の w・h・f を 使う（build_kisekae.py の push_art → window.__KS の themes[].pa → kisekae.js → fx.js）。"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from PIL import Image

K = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(K)
ROOT = os.environ.get('PUSH_ASSETS') or os.path.join(SRC, 'ios', 'push_assets')
IN = os.path.join(ROOT, 'src')
INFO = 'pb.json'
PREFIX = 'pb_'
# 出す 大きさ（CSS の px）：面積を そろえる（丸い 絵が 大きく・横長の 絵が 小さく 見えない ように）
AREA, MAX_W, MAX_H = 34000, 264, 186
# いちばん 大きく 出す とき：fx.js の push() と 同じ 式（1.6倍・幅 372px・高さ 480px で 頭打ち）
PZ_MAX, FIT_W, FIT_H = 1.6, 372, 480
PARAMS = dict(v=1, area=AREA, max_w=MAX_W, max_h=MAX_H, dpr=2.75, q=82, method=6, haze=16, solid=240, speck=64, pad=4)


def ids():
    """テーマの id（build_kisekae.py の 一覧と 同じ）"""
    if K not in sys.path:
        sys.path.insert(0, K)
    import build_kisekae as BK
    return list(BK.ORDER)


def disp(w, h):
    """絵の 大きさ（px）→ 画面で 出す 大きさ（CSS の px・偶数）"""
    a = w / h
    dw, dh = math.sqrt(AREA * a), math.sqrt(AREA / a)
    k = min(1, MAX_W / dw, MAX_H / dh)
    return int(round(dw * k / 2)) * 2, int(round(dh * k / 2)) * 2


def clean(im):
    a = np.array(im.convert('RGBA'))
    al = a[..., 3].astype(np.int32)
    al = np.where(al < PARAMS['haze'], 0, al)
    al = np.where(al >= PARAMS['solid'], 255, al)
    try:                                          # 体から はなれた 小さな 点（切りぬきの のこり）
        from scipy import ndimage as ndi
        lab, n = ndi.label(al > 0)
        if n > 1:
            sizes = np.bincount(lab.ravel())
            small = np.where(sizes < PARAMS['speck'])[0]
            small = small[small != 0]
            if len(small):
                al = np.where(np.isin(lab, small), 0, al)
    except ImportError:
        pass
    a[..., 3] = al.astype(np.uint8)
    a[al == 0, :3] = 0                            # すき通った 所の 色は 0（小さく する ときに 色が にじまない・圧縮も 小さく なる）
    im = Image.fromarray(a, 'RGBA')
    box = im.getbbox()
    im = im.crop(box)
    p = PARAMS['pad']
    out = Image.new('RGBA', (im.width + p * 2, im.height + p * 2), (0, 0, 0, 0))
    out.paste(im, (p, p))
    return out


def sig(path):
    st = os.stat(path)
    return [st.st_size, hashlib.sha1(open(path, 'rb').read()).hexdigest()]


def make(tid):
    src = os.path.join(IN, tid + '.png')
    im = clean(Image.open(src))
    w, h = disp(im.width, im.height)
    pz = max(1, min(PZ_MAX, FIT_W / w, FIT_H / h))
    iw = min(im.width, int(round(w * pz * PARAMS['dpr'])))
    ih = int(round(im.height * iw / im.width))
    if iw < im.width:
        im = im.convert('RGBa').resize((iw, ih), Image.LANCZOS).convert('RGBA')      # すき通りを かけた 色で 小さく する（ふちに 色が にじまない）
        a = np.array(im); a[a[..., 3] == 0, :3] = 0; im = Image.fromarray(a, 'RGBA')
    f = PREFIX + tid + '.webp'
    im.save(os.path.join(ROOT, f), 'WEBP', quality=PARAMS['q'], method=PARAMS['method'], alpha_quality=100, exact=False)
    back = Image.open(os.path.join(ROOT, f))
    assert back.size == (iw, ih) and back.mode == 'RGBA', (tid, back.size, back.mode)
    assert np.array_equal(np.array(back)[..., 3], np.array(im)[..., 3]), tid + '：すき通りが かわった'
    return dict(f=f, w=w, h=h, iw=iw, ih=ih, pz=round(pz, 3), size=os.path.getsize(os.path.join(ROOT, f)), src=sig(src))


def manifest():
    p = os.path.join(ROOT, INFO)
    return json.load(open(p, encoding='utf8')) if os.path.isfile(p) else None


def stale():
    """古い わけ（新しければ ''）。もとの 絵が ない ときは None"""
    if not os.path.isdir(IN):
        return None
    have = sorted(f[:-4] for f in os.listdir(IN) if f.endswith('.png'))
    if not have:
        return None
    man = manifest()
    if man is None:
        return '台帳（pb.json）が ない'
    if man.get('params') != PARAMS:
        return '作り方（PARAMS）が かわった'
    if sorted(man['files']) != have:
        return '絵の ならびが かわった：' + '・'.join(sorted(set(have) ^ set(man['files']))[:5])
    for tid, e in man['files'].items():
        if sig(os.path.join(IN, tid + '.png')) != e['src']:
            return 'もとが かわった：' + tid
        pth = os.path.join(ROOT, e['f'])
        if not os.path.isfile(pth) or os.path.getsize(pth) != e['size']:
            return 'できた 絵が ない・大きさが ちがう：' + e['f']
    return ''


def files():
    """アプリに 入れる 絵：{id: {f, w, h, iw, ih}}。もとが ない（CI）ときは {}。古い ときは 止まる"""
    why = stale()
    if why is None:
        return {}
    if why:
        raise SystemExit(f'※ PUSHボタンの 絵（{ROOT}）が 古い：{why}\n   python3 kisekae/push_art.py で 作り直してね')
    return {tid: {k: e[k] for k in ('f', 'w', 'h', 'iw', 'ih')} for tid, e in manifest()['files'].items()}


def build(force=False):
    have = sorted(f[:-4] for f in os.listdir(IN) if f.endswith('.png'))
    known = set(ids())
    extra = [t for t in have if t not in known]
    assert not extra, 'テーマに ない 名前の 絵：' + '・'.join(extra)
    man = manifest() or {}
    old = man.get('files', {}) if man.get('params') == PARAMS else {}
    out, made = {}, 0
    for tid in have:
        e = old.get(tid)
        ok = (not force and e and e['src'] == sig(os.path.join(IN, tid + '.png')) and os.path.isfile(os.path.join(ROOT, e['f']))
              and os.path.getsize(os.path.join(ROOT, e['f'])) == e['size'])
        if ok:
            out[tid] = e
        else:
            out[tid] = make(tid); made += 1
            print(f"{tid:10s} {out[tid]['w']}x{out[tid]['h']}（いちばん 大きい とき ×{out[tid]['pz']}）→ {out[tid]['iw']}x{out[tid]['ih']}px {out[tid]['size'] / 1e3:.0f}KB")
    for f in os.listdir(ROOT):                    # もう ない テーマの 絵は 消す（できた 絵 だけ・もとは さわらない）
        if f.startswith(PREFIX) and f.endswith('.webp') and f[len(PREFIX):-5] not in out:
            os.remove(os.path.join(ROOT, f))
    json.dump(dict(params=PARAMS, files=out), open(os.path.join(ROOT, INFO), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    miss = [t for t in ids() if t not in out]
    print(f'{len(out)}まい（作り直した {made}）・ぜんぶで {sum(e["size"] for e in out.values()) / 1e6:.2f}MB' + (f'・絵が ない テーマ：{"・".join(miss)}' if miss else '・テーマ ぜんぶに 絵が ある'))
    return out


if __name__ == '__main__':
    if '--check' in sys.argv:
        w = stale()
        print('もとの 絵が ない' if w is None else ('新しい' if w == '' else '古い：' + w))
        sys.exit(1 if w else 0)
    build('--force' in sys.argv)
