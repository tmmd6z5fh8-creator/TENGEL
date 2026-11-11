# 競馬新聞の 走る コマ：いまと 同じ 絵を 1.5倍の 細かさ（iPhone の 3倍の 画面に ぴったり）で
#   第4.156版（まさちゃん 2026/11/12 04:20「Aにして！」＝走る コマを 画面の 3倍に。A／B の 見くらべの 見本と 同じ 作り方）
#   墨の 馬は 小さく する 前の 絵（3倍）から 1.5倍へ。紙と 字は いまの 絵（1倍）を なめらかに 広げた もの（＝いま 画面に 出て いる 見え方と 同じ：馬 だけ 高画質）
#   python3 flat/hq_news.py <出す フォルダ>   → news_run_hq.webp（1.5倍）・news_run_1x.webp（いまと 同じ 作り方：もとの 絵と 見くらべる 用）
import os, sys, json, math
import numpy as np, cv2
K = os.environ.get('HQ_K') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K + '/flat'); sys.path.insert(0, K)      # HQ_K＝kisekae を まるごと 写した 作業用の フォルダ（3D の 下絵を r3d/tmp に たくさん 書く ので、写しで 走らせると リポジトリが よごれない）
import news_banner as NB, news_run as NR
from ink_horse import save_webp, blur, over
OUT = 1.5; W, Hh = NB.W, NB.Hh; W2, H2 = int(W * OUT), int(Hh * OUT)
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
info = json.load(open(K + '/news_run.json')); x0, y0, cw, ch = info['cell']; n = info['frames']; dys = info['dy']
ink0, R0 = NB.ink_layer(); cam = R0['cam']
paper1 = NB.render(np.zeros((Hh, W), np.float32))                       # 紙と 字（馬なし・1倍）
paper2 = cv2.resize(paper1, (W2, H2), interpolation=cv2.INTER_LINEAR)   # 画面が 広げる のと 同じ（なめらかに）
# 字が 墨の 上に 重なる 所（いまの 絵は 字を あとから 描く）：馬なし と 墨で ぬりつぶした 絵の ちがいから 字の 濃さを 出す
full1 = NB.render(np.ones((Hh, W), np.float32))
den = np.maximum((paper1 - full1).mean(-1), 1e-3); base = float(np.percentile(den, 99))
txt1 = np.clip(1 - den / base, 0, 1); txt1[txt1 < 0.12] = 0      # 紙の ざらつき（4%）は 字に 数えない
txt2 = cv2.resize(txt1, (W2, H2), interpolation=cv2.INTER_LINEAR)
sheet2 = np.zeros((int(ch * OUT), int(cw * OUT) * n, 3), np.float32); sheet1 = np.zeros((ch, cw * n, 3), np.float32); ov = 0.0
for f in range(n):
    g = f / n
    ink1, R = NB.ink_layer(NR.pose_at(g), cam, NR.look_at(g), name=f'news_run{f}')
    sheet1[:, f * cw:(f + 1) * cw] = NB.render(ink1, dys[f])[y0:y0 + ch, x0:x0 + cw]
    ink2 = np.clip(cv2.resize(R['ink_s'], (W2, H2), interpolation=cv2.INTER_AREA), 0, 1)
    if dys[f]: ink2 = cv2.warpAffine(ink2, np.float32([[1, 0, 0], [0, 1, dys[f] * OUT]]), (W2, H2), flags=cv2.INTER_LINEAR, borderValue=0)
    ov = max(ov, float((ink2 * txt2).max()))
    k = ink2 * (1 - txt2)                                                # 字の 下に なる 所は 墨を のせない
    img = paper2 * (1 - (blur(ink2, 1.2 * OUT) * 0.10 * (1 - txt2))[..., None])
    img = over(img, NB.INKC, k)
    sheet2[:, f * int(cw * OUT):(f + 1) * int(cw * OUT)] = img[int(y0 * OUT):int((y0 + ch) * OUT), int(x0 * OUT):int((x0 + cw) * OUT)]
    print('frame', f, flush=True)
save_webp(sheet1, f'{out}/news_run_1x.webp', q=86); save_webp(sheet2, f'{out}/news_run_hq.webp', q=86)
print('字と 墨の 重なり（いちばん 大きい 所）', round(ov, 3), 'sizes', os.path.getsize(f'{out}/news_run_1x.webp'), os.path.getsize(f'{out}/news_run_hq.webp'))
# 入れ方：python3 flat/hq_install.py news <出す フォルダ>（手元の 絵の フォルダ ios/kisekae_blobs と 台帳へ。前の 絵は 消さない）
