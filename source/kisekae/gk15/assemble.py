# 神様極的中 第15稿：第14稿（できた 動画）に 3つの 直しを 入れた 新しい できた 動画を 作る（リポジトリの 外・新しい 名前：前の ものは 上書きしない）
#   ① 顔の まだら（face_fix.py：コマ 30〜112）② ばくはつの かけらを うすく（debris.py：116〜130）③ 寄りを ゆっくり（slowcu.py：155〜198 の 44コマ → 96コマ）
#   動画の 明るさ・色の 面（Y・U・V）を そのまま 使う：直して いない 画素は 第14稿と 1つも ちがわない（直した 所は、直す 前と 後の 絵の 差 だけを 面に 足す）
#   python3 assemble.py <第14稿 mp4> <出す mp4>     （GK15_WORK＝作業フォルダ：src/ に 第14稿の コマ・face_out/・debris_out/ に face_fix.py・debris.py が 作った コマ）
import os, sys, subprocess, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slowcu
D = os.environ.get('GK15_WORK', '/home/claude/work/v215/gk')
W, H, N = 780, 1688, 361
SRC, OUT = sys.argv[1], sys.argv[2]
assert not os.path.exists(OUT), f'もう ある（上書きしない）：{OUT}'
FS = W * H * 3 // 2


def planes(buf):
    a = np.frombuffer(buf, np.uint8); return a[:W * H].reshape(H, W), a[W * H:W * H * 5 // 4].reshape(H // 2, W // 2), a[W * H * 5 // 4:].reshape(H // 2, W // 2)


def delta(mod, src):
    """直した 絵と もとの 絵（どちらも BGR の PNG）の 差を、動画の 面（Y・U・V：BT.601・せまい 範囲）の 差に"""
    d = cv2.imread(mod).astype(np.float32) - cv2.imread(src).astype(np.float32); b, g, r = d[..., 0], d[..., 1], d[..., 2]
    y = (65.481 * r + 128.553 * g + 24.966 * b) / 255; u = (-37.797 * r - 74.203 * g + 112.0 * b) / 255; v = (112.0 * r - 93.786 * g - 18.214 * b) / 255
    half = lambda a: a.reshape(H // 2, 2, W // 2, 2).mean((1, 3))
    return y, half(u), half(v)


dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-s', f'{W}x{H}', '-framerate', '30', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12',
                        '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', OUT], stdin=subprocess.PIPE)
put = lambda P: enc.stdin.write(b''.join(np.ascontiguousarray(p).tobytes() for p in P))
n_out = 0; cu = []; kinds = dict(same=0, face=0, debris=0, cu=0)
for f in range(N):
    buf = dec.stdout.read(FS); assert len(buf) == FS, f'コマ {f} が 読めない'
    P = planes(buf)
    cus = [c for c in slowcu.CUS if c <= f < c + slowcu.N_SRC]
    if cus:
        cu.append(tuple(p.copy() for p in P))
        if len(cu) == slowcu.N_SRC:
            for Q in slowcu.slow(cu): put(Q); n_out += 1; kinds['cu'] += 1
            cu = []
        continue
    mod = next((p for p in (f'{D}/face_out/{f:04d}.png', f'{D}/debris_out/{f:04d}.png') if os.path.exists(p)), None)
    if mod:
        dy, du, dv = delta(mod, f'{D}/src/{f:04d}.png')
        P = tuple(np.clip(np.round(p.astype(np.float32) + d), 0, 255).astype(np.uint8) for p, d in zip(P, (dy, du, dv)))
        kinds['face' if 'face_out' in mod else 'debris'] += 1
    else:
        kinds['same'] += 1
    put(P); n_out += 1
assert not dec.stdout.read(1) and not cu
enc.stdin.close(); assert enc.wait() == 0; dec.wait()
print(OUT, n_out, 'コマ', kinds, f'{os.path.getsize(OUT) / 1e6:.2f}MB')
