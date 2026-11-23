# 神様馬の BGM 第3稿（第4.214版）：まさちゃんの 曲を アプリ用の 形に する
#   まさちゃん 2026/11/24 01:16「トレーニングセンターの神様馬のBGM、これのリピートにして！」（TENGER_BGM_App_Loop：60.000秒の くり返しの 曲。
#   11/23 22:48「このBGMの時々なる、ブォみたいな音だけ消せる？」で 姫が 4か所の「ブォ」を 消した もの＝TENGER_BGM_App_Loop_ブォなし.wav）
#
#   python3 kisekae/tc/snd/bgm_divine3.py [もとの wav] [出す フォルダ]
#     もと（マスター）：ios/tc_src/TENGER_BGM_App_Loop_ブォなし.wav（まさちゃんの 曲：リポジトリに 入れない・上書きしない）
#     出す 所：ios/tc_assets/tc_bgm_divine3.m4a（リポジトリに 入れない）→ そのあと python3 kisekae/lite_assets.py（軽い 版の フォルダへ 写す）
#
#   ・形：ルーレットの BGM・第2稿（tc_bgm_divine2.m4a）と 同じ ＝ くり返す 1回り（60秒）の 前に おしりの 0.5秒・うしろに 頭の 0.5秒（同じ 音の つづき）。
#     アプリ（tc/tc_app.js の LOOPS.divine＝{ pre: 0.5, len: 60 }）は まん中の 1回り だけを くり返す
#     ＝ m4a を 読む 道具が 頭に 短い 無音を つけても（その ぶん ずれても）、つなぎ目は 同じ 音どうし
#   ・曲の おわり → 頭 は もとから つながって いる（波が そのまま つづく：下の たしかめ）＝ 手を 入れない（重ねたり 小さく したり しない）
#   ・大きさ：−5.0dB（GAIN_DB）。もとの 曲は −19.0 LUFS・山 −6.8dB で、アプリの ほかの BGM（第2稿 −25.4 LUFS・カードバトル −23〜−28 LUFS）より 大きい。
#     −5.0dB で −24.0 LUFS・全体 −26.6dB・山 −11.8dB（test_bgm.py の きまり：全体 −31〜−25dB・山 −11dB より 下＝お世話の 音が うもれない）。
#     iPhone の スピーカーで 出る 所（300Hz より 上）は −26.1 LUFS（第2稿 −27.4）・1kHz より 上は −32.5 LUFS（第2稿 −30.0）＝ 第2稿と 同じ くらいに 聞こえる
#   ・m4a（AAC）112kbps（幻の馬の BGM と 同じ）
import hashlib, os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile

H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(os.path.dirname(os.path.dirname(H)))
SRC = os.path.join(W, 'ios', 'tc_src', 'TENGER_BGM_App_Loop_ブォなし.wav')
SHA = 'd4766f78d64286e763ae48a46968578b4061a134bd01c04f760079b21bebd4d3'      # まさちゃんが 11/24 01:16 に 送って くれた ファイル（＝姫が「ブォ」を 消した もの）
NAME = 'tc_bgm_divine3'
SR, FRAMES = 44100, 2646000      # 60.000秒
PRE = 0.5                        # 前後の つづき（秒）
GAIN_DB = -5.0
BR = '112k'


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else SRC
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(W, 'ios', 'tc_assets')
    raw = open(src, 'rb').read(); sha = hashlib.sha256(raw).hexdigest()
    if sha != SHA and os.environ.get('FORCE') != '1':
        sys.exit(f'もとの ファイルが 決めた もの では ない（{sha[:16]}…）。新しい 曲に する ときは SHA を 書きかえる（ためす だけ なら FORCE=1）')
    sr, x16 = wavfile.read(src)
    assert sr == SR and x16.dtype == np.int16 and x16.ndim == 2 and x16.shape[1] == 2, (sr, x16.dtype, x16.shape)
    assert sha != SHA or len(x16) == FRAMES, len(x16)
    x = x16.astype(np.float64) / 32768.0; n = len(x)
    # おわり → 頭 が つながって いるか（段・プツが ない）：さいごの サンプル → はじめの サンプルの 差と 曲がり方（2回の 差）が、ふだんの 値より 小さい
    step = np.abs(x[0] - x[-1]).max(); usual = np.percentile(np.abs(np.diff(x, axis=0)), 99)
    w = np.vstack([x[-64:], x[:64]]); bend = np.abs(w[2:] - 2 * w[1:-1] + w[:-2]).sum(axis=1)[56:70].max()
    bend_usual = np.percentile(np.abs(x[2:] - 2 * x[1:-1] + x[:-2]).sum(axis=1), 99.9)
    print(f'おわり → 頭：段 {step * 32768:.0f}（ふだんの となりの 差 99% {usual * 32768:.0f}）・曲がり方 {bend * 32768:.0f}（ふだん 99.9% {bend_usual * 32768:.0f}）')
    assert step < usual and bend < bend_usual, 'おわり → 頭 が つながって いない（くり返すと プツッと 鳴る）'
    g = 10 ** (GAIN_DB / 20); p = int(round(PRE * SR))
    y = np.concatenate([x[-p:], x, x[:p]]) * g
    pk = float(np.abs(y).max()); assert pk < 0.97, pk
    os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp(); wv = os.path.join(tmp, NAME + '.wav'); wavfile.write(wv, SR, y.astype(np.float32))      # 小数の まま 渡す（小さく した ぶん 目が あらく ならない）
    o = os.path.join(out, NAME + '.m4a')
    if os.path.exists(o) and os.environ.get('FORCE') != '1':
        sys.exit(f'{o} は もう ある（上書きしない）。作り直す ときは FORCE=1')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wv, '-c:a', 'aac', '-b:a', BR, '-movflags', '+faststart', o], check=True)
    os.remove(wv); os.rmdir(tmp)
    # できた ファイルを ほどいて たしかめる：長さ・前後の つづきが 同じ 音か
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', o, '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True)
    d = np.frombuffer(r.stdout, np.int16).reshape(-1, 2).astype(np.float64) / 32768; m = d.mean(1)
    a = m[2400:p - 2400]; best = max(float(np.corrcoef(a, m[n + 2400 + k:n + 2400 + k + len(a)])[0, 1]) for k in range(-2400, 2401, 4))
    rms = 20 * np.log10(np.sqrt(np.mean(d ** 2))); dpk = 20 * np.log10(np.abs(d).max())
    print(f'{NAME}.m4a：{len(d) / SR:.3f}秒（1回り {n / SR:.3f}秒＋前後 {PRE}秒）・{os.path.getsize(o):,} B・全体 {rms:.1f}dB・山 {dpk:.1f}dB・前後の つづきの 似かた {best:.4f}')
    assert abs(len(d) / SR - (n / SR + 2 * PRE)) < 0.08 and best > 0.99, (len(d) / SR, best)


if __name__ == '__main__':
    main()
