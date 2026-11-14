# トレーニングセンターの 音を アプリ用に 書き出す（m4a・Resources に 名前だけで 入れる）
#   python3 export_app.py <出す フォルダ>
#   ・環境音（朝・夕方・夜）：60秒の ループ（はじめと おわりを 重ねる）→ tc_amb_<tod>.m4a
#   ・BGM（幻の馬・神様馬）：bgm.py の 60秒 ループ → tc_bgm_<abyss|divine>.m4a
#   ・ルーレットの BGM（第4.168版）：bgm_roulette.py の 8小節 ループ（約14.5秒）→ tc_bgm_roulette.m4a（これ だけ 作る とき → python3 export_app.py <出す フォルダ> tc_bgm_roulette）
#   ・テンゲルBGM と 神様馬の BGM の 第2稿（第4.171版）：bgm_tengel.py → bgm_tengel9.m4a（16小節・36 BPM・約106.7秒：笛 4本・鳥の 声・馬の 鳴き声と 走る 音・風の 音。第1稿 bgm_tengel.m4a・第2稿〜第8稿 bgm_tengel2〜8.m4a）・tc_bgm_divine2.m4a（32小節・約49.2秒）
#   ・お世話の 音：sfx_care.py の render を できごと 1つずつ → tc_se_<k>.m4a（slot_1〜10・bite_apple／carrot・banin_kamisama／maboroshi）
#     第4.159版：PUSH の 音 だけ 足す とき → python3 export_app.py <出す フォルダ> tc_se_pfo,tc_se_dedeen,tc_se_kyuin,tc_se_doon（できた 4つを ios/tc_assets へ 写す：前から ある 音は 作り直さない）
#   ・ルーレット：sfx_roulette.py の 部品 → tc_se_rt_<lever|tick|stop|confirm>.m4a
#   ・ルーレットの 高い 方の 爆発（第4.171版）：sfx_boom.py → tc_se_boom.m4a（これ だけ 作る とき → python3 export_app.py <出す フォルダ> tc_se_boom）
#   ・チケット：sfx_ticket.py の render を できごと 1つずつ → tc_se_tk_<k>.m4a
import os, sys, subprocess, tempfile, math
import numpy as np
from scipy.io import wavfile
H_ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H_)
import amb, bgm, bgm_roulette, sfx_care, sfx_roulette, sfx_ticket
SR = amb.SR
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
TMP = tempfile.mkdtemp()
ONLY = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None


def write(name, buf, br='96k'):
    """buf：(2, n) か (n,)。−1〜1 に おさめて m4a に"""
    if buf.ndim == 1: buf = np.stack([buf, buf])
    pk = float(np.abs(buf).max())
    if pk > 0.97: buf = buf * (0.97 / pk)
    w = os.path.join(TMP, name + '.wav'); wavfile.write(w, SR, (buf.T * 32767).astype(np.int16))
    o = os.path.join(OUT, name + '.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-c:a', 'aac', '-b:a', br, '-movflags', '+faststart', o], check=True)
    print(name, round(buf.shape[1] / SR, 2), '秒', os.path.getsize(o) // 1024, 'KB', 'peak', round(pk, 3), flush=True)


def trim(buf, lead=0.05, floor=1e-4, tail=0.08):
    """前の 余白（lead 秒：できごとの 時刻）を 切って、うしろの 無音を 切る"""
    i0 = int(lead * SR); buf = buf[:, i0:]
    a = np.abs(buf).max(0); nz = np.nonzero(a > floor)[0]
    if len(nz): buf = buf[:, :min(buf.shape[1], nz[-1] + int(tail * SR))]
    n = min(int(0.01 * SR), buf.shape[1]); buf[:, -n:] *= np.linspace(1, 0, n)
    return buf


def want(n): return ONLY is None or any(n.startswith(p) for p in ONLY)


# ---- 環境音・BGM ----
for tod in ('morning', 'evening', 'night'):
    nm = f'tc_amb_{tod}'
    if not want(nm): continue
    L, X = 60.0, 4.0
    s = amb.scene(L + X + 1, tod, 105)
    n, x = int(L * SR), int(X * SR); fade = np.sin(np.linspace(0, np.pi / 2, x)) ** 2
    loop = s[:, :n].copy(); loop[:, :x] = s[:, :x] * fade + s[:, n:n + x] * (1 - fade)
    write(nm, loop, '96k')
for nm, fn in (('tc_bgm_abyss', bgm.abyss), ('tc_bgm_divine', bgm.divine)):
    if want(nm): write(nm, fn(), '112k')
if want('tc_bgm_roulette'):      # 第4.168版：ルーレットの 間の BGM（フィールドの 音の かわりに 鳴らす）
    # くり返す 1回り（8小節）の 前に おしりの 0.5秒・うしろに 頭の 0.5秒を つける（同じ 音の つづき）。アプリは まん中の 1回り だけを くり返す（tc/tc_app.js の LOOPS：pre 0.5秒・len 8小節）
    #   ＝ m4a を 読む 道具が 頭に 短い 無音を つけても（その ぶん ずれても）、つなぎ目は 同じ 音どうしで リズムが とばない
    _lp = bgm_roulette.roulette(); _p = int(round(0.5 * SR))
    write('tc_bgm_roulette', np.concatenate([_lp[:, -_p:], _lp, _lp[:, :_p]], 1), '112k')
# 第4.171版（まさちゃん 2026/11/14 16:18・17:08）：テンゲルBGM（判定・記録 などの 画面：bgm.js）と 神様馬の BGM の 第2稿（tc/tc_app.js の AMB.divine）。bgm_tengel.py の 曲。
#   どれも ルーレットの BGM と 同じ 形（くり返す 1回りの 前に おしりの 0.5秒・うしろに 頭の 0.5秒）。作る とき → python3 export_app.py <出す フォルダ> bgm_tengel9,tc_bgm_divine2
#   bgm_tengel＝テンゲルBGM の 第1稿（108 BPM の 明るい 曲）・bgm_tengel2＝第2稿（のどかな 村の ふんいき・116 BPM）：どちらも アプリには 入れない／bgm_tengel3＝第3稿（もっと ゆっくり 88 BPM・笛・鳥の 声）／bgm_tengel4＝第4稿（19:09「一回、鳥の声と笛の音だけにしてみて！もっとゆったりで！」：笛 1本 と 鳥の 声 だけ・60 BPM）：どれも アプリには 入れない／
#   bgm_tengel5＝第5稿（19:25「ここに馬の走る音と、もう少し太い音の笛を混ぜて！ゆったりね！」：第4稿 ＋ 太い 音の 笛 ＋ 馬の 走る 音）：アプリには 入れない
#   bgm_tengel6＝第6稿（19:41「もう一段階太い笛と、かなり音が低い笛も重ねて音入れて！」・19:42「馬の鳴き声と、馬が走る音追加して！」：笛 4本・鳥の 声・馬の 鳴き声と 走る 音）・bgm_tengel7＝第7稿（19:57「この笛を、バイオリンぽくできる？」：4本を 弦の 音に）：どれも アプリには 入れない／
#   bgm_tengel8＝第8稿（20:12「ごめん！笛に戻して！もっとゆったりで！」・20:15「あと風の音も入れて！」：笛 4本に もどす・48 BPM・風の 音）：アプリには 入れない／
#   bgm_tengel9＝第9稿（20:27「もっと笛の音ゆっくりして！」：36 BPM・笛の 吹き方も ゆっくり：アプリに 入れる）
#   稿の 名前は bgm_tengel.py の SONGS（tengel・tengel2・…）から 作る ＝ 稿が ふえても ここは 直さない
import bgm_tengel as _bt
for _nm, _key in [('bgm_' + _k, _k) for _k in _bt.SONGS if _k.startswith('tengel')] + [('tc_bgm_divine2', 'divine2')]:
    if not want(_nm): continue
    import bgm_tengel
    _lp, _S = bgm_tengel.SONGS[_key](); _p = int(round(0.5 * SR)); assert _lp.shape[1] == _S.n, (_lp.shape, _S.n)
    write(_nm, np.concatenate([_lp[:, -_p:], _lp, _lp[:, :_p]], 1), '128k')

# ---- お世話の 音 ----
KINDS = ['button', 'unfold', 'fold', 'rub', 'heart', 'nod', 'swish', 'nuzzle', 'stretch', 'sneeze', 'tilt', 'calm', 'frisk', 'yawn', 'lie', 'nope', 'wait', 'ready', 'zoomin',
         'max', 'gather', 'hop', 'flop', 'goron', 'unlock', 'stock', 'call', 'turn', 'amae', 'heartpop', 'paper', 'chooser', 'pick', 'token', 'bucket', 'munch', 'lick',
         'yummy', 'beg', 'gold', 'sweep', 'inpan', 'kira', 'luck', 'piron', 'sniff', 'nibble', 'banout',
         'pfo', 'dedeen', 'kyuin', 'doon']      # 第4.159版：お世話の あとの PUSH の 音（sfx_push.py：プフォ・デデーン・キュインキュイーン）・ルーレットの 高い 方の テロップ（ドーン！！）
VAR = [('slot_%d' % n, {'k': 'slot', 'n': n}) for n in range(1, 11)] + [('bite_apple', {'k': 'bite', 'kind': 'apple'}), ('bite_carrot', {'k': 'bite', 'kind': 'carrot'}),
       ('banin_kamisama', {'k': 'banin', 'kind': 'kamisama'}), ('banin_maboroshi', {'k': 'banin', 'kind': 'maboroshi'})]
for nm, e in [(k, {'k': k}) for k in KINDS] + VAR:
    if not want('tc_se_' + nm): continue
    ev = dict(e); ev['t'] = 0.05
    buf = sfx_care.render(8.0, [ev], 0.0)
    if np.abs(buf).max() < 1e-5: print('音なし', nm); continue
    write('tc_se_' + nm, trim(buf))

# ---- ルーレット ----
rng = np.random.default_rng(7)
for nm, x, g in (('lever', sfx_roulette.lever_snd(rng), sfx_roulette.G_LEVER), ('tick', sfx_roulette.tick_snd(rng), sfx_roulette.G_TICK),
                 ('stop', sfx_roulette.stop_snd(rng), sfx_roulette.G_STOP), ('confirm', sfx_roulette.confirm_snd(rng), sfx_roulette.G_CONF)):
    if not want('tc_se_rt_' + nm): continue
    y = amb.place(x, 0.0, g * 1.41, 0.08)
    write('tc_se_rt_' + nm, trim(np.concatenate([np.zeros((2, int(0.05 * SR))), y], 1)))

# ---- ルーレットの 高い 方の 爆発（第4.171版：sfx_boom.py。動画 tc_rt_boom.mp4 と いっしょに 鳴らす）----
if want('tc_se_boom'):
    import sfx_boom
    write('tc_se_boom', trim(np.concatenate([np.zeros((2, int(0.05 * SR))), sfx_boom.boom_snd()], 1)))

# ---- チケット ----
for k in ('fall', 'land', 'tapshow', 'tap', 'open', 'white', 'reveal', 'ticket', 'get'):
    if not want('tc_se_tk_' + k): continue
    evs = [{'t': 0.05, 'k': k}]
    if k == 'land': evs.append({'t': 2.6, 'k': 'tap_dummy'})          # きらきらは 2.5秒（タップまでの 長さは アプリで ちがう）
    buf = sfx_ticket.render(7.0, evs)
    buf = 0.5 * np.tanh(buf / 0.5)
    write('tc_se_tk_' + k, trim(buf))
print('done', OUT)
