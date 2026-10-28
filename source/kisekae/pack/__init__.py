"""壁紙パック（App Store版 第4.92版・まさちゃんの 指定）：買い切り 1,500円の 新しい 壁紙 11枚。
   買った あとに 読み込んだ レース 5つごとに、下の 順で 1枚ずつ 解放（55レースで 全部）。ポイントでは 買えない。帯の 壁紙の ミッション（8・16・25枚）の 枚数に 数える。
   どの テーマも いまの 30テーマと 同じ 一式：上の絵（動く 壁紙）・色・字・形（themes20 と 同じ 形の dict）・背景の もよう・すみの 飾り・的中の PUSH と はじける かけら・結果の ボード。
   テーマごとの ファイル（pack/<id>.py）が 持つ もの：
     THEME      … themes20.THEMES と 同じ 形（id・cat＝7・name・desc・title・banner・alt・fonts・v・chk・css・orn・guide）
     banner(B)  … 上の絵の (html, css)。B：blobs.json の その テーマの 絵の id（'/_blob/<id>'）と シートの 大きさ
     PUSH       … 的中ボタンの 記号（2文字）・face(sfx)・decor(sfx)・burst()・CSS（push_events.py と 同じ 形）
   絵の id（馬の コマの シート・止まった 絵）は blobs.json（pack/make/<id>_art.py が 作る。絵は ios/kisekae_blobs/＝git に 入れない）"""
import importlib
import json
import os

PACK = os.path.dirname(os.path.abspath(__file__))
# 解放の 順（まさちゃんの 指定の 順）
ORDER = ['pirate', 'course', 'space', 'paddock', 'deepsea', 'dino', 'kirie', 'ukiyoe', 'steam', 'future', 'tanabata']
CAT = 7
CAT_NAME = '壁紙パック'
PRODUCT = 'jp.tengel.app.wallpack1'
EVERY = 5          # 読み込み 5レースごとに 1枚


def _mods():
    """できて いる テーマの ファイルを 読む。PACK_ONLY=<id>,<id>… なら その テーマだけ（作って いる 途中の ほかの テーマに じゃまされない ため）"""
    only = [x for x in os.environ.get('PACK_ONLY', '').split(',') if x]
    out = {}
    for tid in ORDER:
        if only and tid not in only:
            continue
        if os.path.exists(os.path.join(PACK, tid + '.py')):
            out[tid] = importlib.import_module('pack.' + tid)
    return out


MODS = _mods()
IDS = [t for t in ORDER if t in MODS]          # できて いる テーマ（作って いる 途中でも ビルドが 通る ように）


def blobs(tid=None):
    p = os.path.join(PACK, 'blobs.json')
    d = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    return d.get(tid, {}) if tid else d


def B(tid):
    """その テーマの 絵：名前 → {'url': '/_blob/<id>', …シートの 大きさ}"""
    return {k: dict(v, url='/_blob/' + v['id']) for k, v in blobs(tid).items()}


def themes():
    return [MODS[t].THEME for t in IDS]


def banner(tid):
    return MODS[tid].banner(B(tid))


def still_id(tid):
    """止まった 絵（選ぶ画面の 小さな 絵・視差効果を減らす 時）の id。なければ ''"""
    return blobs(tid).get('still', {}).get('id', '')


def push_codes():
    return {MODS[t].PUSH['code']: MODS[t].PUSH for t in IDS if getattr(MODS[t], 'PUSH', None)}


def push_code(tid):
    m = MODS.get(tid)
    return m.PUSH['code'] if m is not None and getattr(m, 'PUSH', None) else ''
