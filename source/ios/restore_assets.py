# 作業の 場所が 新しく なって 絵・音・形（リポジトリに 入れない もの）が なくなった ときに、前に 作った App Store版の パッケージ（zip か フォルダ）から 戻す
#   python3 ios/restore_assets.py <Tengel_xxxx.swiftpm.zip か Tengel.swiftpm フォルダ>
#   Resources/ の 名前で 分ける（build_ios.py の 入れ方の 逆）：
#     ks_<32けた>.<形> → ios/kisekae_blobs/<32けた>.<形>（着せ替えの 見本の 絵）
#     build_fx の ASSET_FILES → ios/fx_assets/（的中ボタンの 絵と 音）
#     bcp_app.files() → ios/bcp_assets/（結果ボードカスタムの 絵の ボード）
#     tc_・rt_・tk_ で はじまる 絵・形・音・動画 と bgm_tengel.m4a（テンゲルBGM）→ ios/tc_assets/（トレーニングセンター）
#     fg で はじまる 形・絵 → ios/fig_assets/（思い出フィギュア）
#   データの 鍵（xt/data_key.txt）は claude.ai の Project の「テンゲル_データ更新の鍵」から 戻す（ここでは 戻さない）
import os, re, shutil, sys, zipfile
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(W, 'kisekae')); sys.path.insert(0, os.path.join(W, 'kisekae', 'bcp'))
from build_fx import ASSET_FILES
import bcp_app
FX, BCP = set(ASSET_FILES), set(bcp_app.files())
src = sys.argv[1]
if src.endswith('.zip'):
    z = zipfile.ZipFile(src); names = {n.split('/')[-1]: n for n in z.namelist() if '/Resources/' in n and not n.endswith('/') and n.count('/Resources/') == 1 and '/' not in n.split('/Resources/')[1]}
    read = lambda f: z.read(names[f])
else:
    res = os.path.join(src, 'Resources'); names = {f: os.path.join(res, f) for f in os.listdir(res) if os.path.isfile(os.path.join(res, f))}
    read = lambda f: open(names[f], 'rb').read()
got = {}
def put(sub, name, f):
    d = os.path.join(W, 'ios', sub); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, name), 'wb').write(read(f)); got[sub] = got.get(sub, 0) + 1
for f in sorted(names):
    m = re.fullmatch(r'ks_([0-9a-f]{32})\.(webp|png|jpg|jpeg|gif|svg)', f)
    if m: put('kisekae_blobs', f'{m.group(1)}.{m.group(2)}', f)
    elif f in FX: put('fx_assets', f, f)
    elif f in BCP: put('bcp_assets', f, f)
    elif (re.match(r'(tc_|rt_|tk_)', f) and f.rsplit('.', 1)[-1].lower() in ('webp', 'json', 'bin', 'm4a', 'mp4') and f != 'tc_bundle.js') or re.fullmatch(r'bgm_tengel\d*\.m4a', f): put('tc_assets', f, f)      # 第4.171版：爆発の 動画（tc_rt_boom.mp4）・テンゲルBGM（bgm_tengel.m4a）も
    elif re.match(r'fg', f) and f.rsplit('.', 1)[-1].lower() in ('webp', 'json', 'bin'): put('fig_assets', f, f)
print('戻した：', got)
print('的中ボタン', got.get('fx_assets', 0), '/', len(FX), '・結果ボード', got.get('bcp_assets', 0), '/', len(BCP))
