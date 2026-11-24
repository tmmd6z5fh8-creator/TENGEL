# 神様極的中 第16稿：第14稿（できた 動画）から、新しい できた 動画を 作る（リポジトリの 外・新しい 名前：前の ものは 上書きしない）（第4.216版）
#   まさちゃん 2026/11/24 11:01「神様極的中の、神様的中のカットインもう少し早くして！ 神様極的中の、最初の神様塗り直してくれたけど、塗った感がきになる… 3Dのデータから入れ直すことできる？」
#             12:23「神様馬の顔をスタートもっと下向きで、光りが強くなるにつれて上を向くようにして！」
#   ① はじめの 顔（コマ 0〜112）＝ 3D から 描いた コマ（face3d.py：<作業>/out/）。113・114 は 爆発の 光の 中に 顔が 少し のこる ので、112 の「新しい − 第14稿」の 差を 明るさに 合わせて 足す
#   ② ばくはつの かけらを うすく（第15稿と 同じ：v215 の debris_out・116〜130）
#   ③ 寄り（神・様・的・中）＝ 1つ 0.6秒（18コマ。第15稿は 0.8秒＝24コマ・第14稿は 0.37秒＝11コマ）：gk15/slowcu.py で コマの 間を 作る
#   動画の 明るさ・色の 面（Y・U・V）に、直した 絵と 第14稿の 絵の 差 だけを 足す（直して いない 画素は 第14稿と 1つも ちがわない）
#   python3 assemble.py <第14稿 mp4> <出す mp4>   （GK16_WORK＝3D の コマの 作業フォルダ（out/）・GK15_WORK＝第14稿の コマ（src/）と かけら（debris_out/））
import os, sys, subprocess, numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gk15'))
import slowcu
slowcu.N_OUT = 18                                                              # 寄り 1つ 0.6秒
D15 = os.environ.get('GK15_WORK', '/home/claude/work/v215/gk')
D16 = os.environ.get('GK16_WORK', '/home/claude/work/v216/gk2')
W, H, N = 780, 1688, 361
FACE_LAST = 112
CARRY = {113: 1.0, 114: 0.45}                                                  # 爆発の はじまり：112 の 差を どれだけ のこすか（明るく なった 所ほど 少なく）
SRC, OUT = sys.argv[1], sys.argv[2]
assert not os.path.exists(OUT), f'もう ある（上書きしない）：{OUT}'
FS = W * H * 3 // 2


def planes(buf):
    a = np.frombuffer(buf, np.uint8); return a[:W * H].reshape(H, W), a[W * H:W * H * 5 // 4].reshape(H // 2, W // 2), a[W * H * 5 // 4:].reshape(H // 2, W // 2)


def yuv_delta(d):
    """BGR の 差（float）→ 動画の 面（Y・U・V：BT.601・せまい 範囲）の 差"""
    b, g, r = d[..., 0], d[..., 1], d[..., 2]
    y = (65.481 * r + 128.553 * g + 24.966 * b) / 255; u = (-37.797 * r - 74.203 * g + 112.0 * b) / 255; v = (112.0 * r - 93.786 * g - 18.214 * b) / 255
    half = lambda a: a.reshape(H // 2, 2, W // 2, 2).mean((1, 3))
    return y, half(u), half(v)


def src_png(f):
    return cv2.imread(f'{D15}/src/{f:04d}.png').astype(np.float32)


def lumf(a):
    return a[..., 2] * 0.299 + a[..., 1] * 0.587 + a[..., 0] * 0.114


D112 = cv2.imread(f'{D16}/out/{FACE_LAST:04d}.png').astype(np.float32) - src_png(FACE_LAST)
L112 = lumf(src_png(FACE_LAST))
dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-s', f'{W}x{H}', '-framerate', '30', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12',
                        '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', OUT], stdin=subprocess.PIPE)
put = lambda P: enc.stdin.write(b''.join(np.ascontiguousarray(p).tobytes() for p in P))
n_out = 0; cu = []; kinds = dict(same=0, face3d=0, carry=0, debris=0, cu=0)
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
    d = None
    if f <= FACE_LAST:
        d = cv2.imread(f'{D16}/out/{f:04d}.png').astype(np.float32) - src_png(f); kinds['face3d'] += 1
    elif f in CARRY:
        s = src_png(f); w = np.clip(1 - (lumf(s) - L112) / 110.0, 0, 1)[..., None]       # 光で 白く なった 所は 差を 入れない
        d = D112 * w * CARRY[f]; kinds['carry'] += 1
    elif os.path.exists(f'{D15}/debris_out/{f:04d}.png'):
        d = cv2.imread(f'{D15}/debris_out/{f:04d}.png').astype(np.float32) - src_png(f); kinds['debris'] += 1
    else:
        kinds['same'] += 1
    if d is not None:
        P = tuple(np.clip(np.round(p.astype(np.float32) + dd), 0, 255).astype(np.uint8) for p, dd in zip(P, yuv_delta(d)))
    put(P); n_out += 1
assert not dec.stdout.read(1) and not cu
enc.stdin.close(); assert enc.wait() == 0; dec.wait()
print(OUT, n_out, 'コマ', kinds, f'{os.path.getsize(OUT) / 1e6:.2f}MB')
