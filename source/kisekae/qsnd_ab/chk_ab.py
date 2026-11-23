# 聞きくらべ用の 2組（a＝今の 音・b＝軽い 音）を くらべる：大きさ・長さ・ずれ・SNR・ヘッダーの おくれ（LAME タグ）
#   python3 kisekae/qsnd_ab/chk_ab.py <作業フォルダ>        （数字は <作業フォルダ>/meta_raw.json に 書く：build_page.py が 読む）
#   za・zb＝zip の 中での 大きさの 見つもり（zlib 9）。ずれ・長さが ちがう 音が あれば 終わりの 行に 出る（0 で ないと くり返しの 所が ずれる）
import json, os, subprocess, sys, zlib
import numpy as np
SR = 44100
W = sys.argv[1]
D = W + '/snd'


def dec(path, ch):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], check=True, stdout=subprocess.PIPE).stdout
    return np.frombuffer(raw, dtype='<f4').reshape(-1, ch).astype(np.float64)


def chans(path):
    return int(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=channels', '-of', 'csv=p=0', path], check=True, stdout=subprocess.PIPE).stdout.decode().strip())


def lame(b):
    """はじめの フレームの Xing/Info と LAME の つづき（エンコーダーの 名前・おくれ・うしろの つめもの）"""
    i = 0
    if b[:3] == b'ID3':
        i = 10 + ((b[6] & 0x7f) << 21 | (b[7] & 0x7f) << 14 | (b[8] & 0x7f) << 7 | (b[9] & 0x7f))
    h = int.from_bytes(b[i:i + 4], 'big')
    mono = ((h >> 6) & 3) == 3
    off = i + 4 + (17 if mono else 32)
    tag = b[off:off + 4].decode('latin1')
    flags = int.from_bytes(b[off + 4:off + 8], 'big')
    p = off + 8
    if flags & 1: p += 4
    if flags & 2: p += 4
    if flags & 4: p += 100
    if flags & 8: p += 4
    enc = b[p:p + 9].decode('latin1')
    dp = b[p + 21:p + 24]
    delay = (dp[0] << 4) | (dp[1] >> 4); pad = ((dp[1] & 15) << 8) | dp[2]
    return tag, enc, delay, pad


def lag(x, y, m=3000):
    n = min(len(x), len(y), SR * 6)
    a = x[:n].sum(axis=1); b = y[:n].sum(axis=1)
    a = a - a.mean(); b = b - b.mean()
    A = np.fft.rfft(a, 2 * n); B = np.fft.rfft(b, 2 * n)
    c = np.fft.irfft(A * np.conj(B))
    c = np.concatenate([c[-m:], c[:m + 1]])
    return int(np.argmax(c)) - m


out = []
for f in sorted(os.listdir(D + '/a')):
    pa, pb = f'{D}/a/{f}', f'{D}/b/{f}'
    ch = chans(pa)
    assert chans(pb) == ch
    x, y = dec(pa, ch), dec(pb, ch)
    ba, bb = open(pa, 'rb').read(), open(pb, 'rb').read()
    n = min(len(x), len(y))
    d = x[:n] - y[:n]
    snr = 10 * np.log10((x[:n] ** 2).sum() / max((d ** 2).sum(), 1e-30))
    rms = lambda v: 20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-12)
    r = dict(f=f, ch=ch, a=len(ba), b=len(bb), za=len(zlib.compress(ba, 9)), zb=len(zlib.compress(bb, 9)), na=len(x), nb=len(y), lag=lag(x, y), snr=round(float(snr), 1),
             rms=round(float(rms(y[:n]) - rms(x[:n])), 2), pk=round(float(20 * np.log10(np.abs(x).max() + 1e-12)), 1), la=lame(ba), lb=lame(bb), sec=round(len(x) / SR, 2))
    out.append(r)
    print(f"{f:18s} ch{ch} {r['a']:8d} → {r['b']:8d}  zip {r['za']:8d} → {r['zb']:8d}  len {r['na']:8d}/{r['nb']:8d} lag {r['lag']:3d}  SNR {r['snr']:5.1f}  rmsΔ {r['rms']:+.2f}  {r['sec']:6.2f}s  A{r['la']} B{r['lb']}")
A = sum(r['a'] for r in out); B = sum(r['b'] for r in out); ZA = sum(r['za'] for r in out); ZB = sum(r['zb'] for r in out)
print(f"合計 {A} → {B}（{A - B}）  zip {ZA} → {ZB}（{ZA - ZB}）  長さが ちがう：{sum(1 for r in out if r['na'] != r['nb'])}  ずれ：{sum(1 for r in out if r['lag'])}")
json.dump(out, open(W + '/meta_raw.json', 'w'), ensure_ascii=False, indent=0)
