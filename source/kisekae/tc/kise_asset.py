# 「壁紙&ボード着せ替え」の ボタンの 絵を アプリ用に 置く（第4.165版・まさちゃん 2026/11/13 13:55「黄丸のところに、タップすると壁紙や結果ボードカスタムのところに飛べるアイコン設置して！」
#   → 14:16「何か変だから、2枚目のアイコンにして、作戦会議のすぐ下に設置してみて！あと下にテロップ入れて！壁紙&ボード着せ替え、って！」
#   ＋ 金の 輪の 横長の カプセル・うすい 緑の 地に 壁紙の 札（笑って いる 茶色の 馬と 富士山）と 金の ふちの 紺の ボードと ピンクの 筆の 絵 1まい）
#   python3 kisekae/tc/kise_asset.py <まさちゃんの 絵（PNG・すき通し）> [ios/tc_assets]
#   → tc_icon_kise2.webp（幅 440px：すき通って いない 所〈カプセル〉を 切り出して、まわりに 4px の すきま。たてよこの 比は もとの まま ＝ 見える カプセルは 432×155 ほど）
#   ・使う 所：tc/tc_launch.js の 判定タブの「レース情報」の カードの 右上（#kiseBtn：作戦会議の 札の すぐ 下・その 下に 名前の 札「壁紙&ボード着せ替え」）
#     → 押すと 設定タブの「着せ替え」（すぐ 下が「結果ボードカスタム」）。tc_launch.js の KISE_AR（よこ÷たて）は この 絵の 比と 同じに する（ここで 出る 数）
#   ・はじめに 置いた 丸い 絵（tc_icon_kise.webp：13:55 の 1枚め）は もう 使わない（マスターは 消さない・assets_dir.py が アプリに 入れない）
#   ・もとの 絵（まさちゃんの PNG）と できた ファイルは リポジトリに 入れない（ios/tc_assets/ は .gitignore）
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_launch.js の 名前も かえる）
#   ・kisekae/tc/collect_assets.py は 出す フォルダを 作り直す ので、走らせた あとは これを もう一度。足した あとは python3 kisekae/lite_assets.py
import io, os, sys
from PIL import Image
NAME, W_OUT, PAD, Q = 'tc_icon_kise2.webp', 440, 4, 92


def make(src):
    im = Image.open(src).convert('RGBA')
    box = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    assert box, ('すきとおって いない 所が ない', src)
    cut = im.crop(box); w, h = cut.size; assert w > h * 2, ('横長の 絵では ない', cut.size)
    aw = W_OUT - PAD * 2; ah = int(round(aw * h / w))
    small = cut.convert('RGBa').resize((aw, ah), Image.LANCZOS).convert('RGBA')       # ちぢめる ときは 色に すき通り具合を かけてから（ふちに すじが 出ない）
    out = Image.new('RGBA', (W_OUT, ah + PAD * 2), (0, 0, 0, 0)); out.paste(small, (PAD, PAD))
    buf = io.BytesIO(); out.save(buf, 'WEBP', quality=Q, method=6)
    return out, buf.getvalue(), w / h


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ios', 'tc_assets')
    assert os.path.isdir(out_dir), out_dir
    im, data, ar = make(src)
    dst = os.path.join(out_dir, NAME)
    if os.path.exists(dst):
        if open(dst, 'rb').read() == data: print('同じ ものが もう ある：', dst); return
        raise SystemExit(f'もう ある ファイルと 中身が ちがう（上書きしない）：{dst}')
    with open(dst, 'xb') as f: f.write(data)
    print(f'{NAME}：{im.size[0]}×{im.size[1]}・{len(data):,}B・カプセルの よこ÷たて {ar:.4f} → {dst}')


if __name__ == '__main__':
    main()
