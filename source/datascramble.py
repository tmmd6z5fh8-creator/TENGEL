"""【第4.155版から 使わない：前の 形（data/mother_app.json・sc:1）を 開く／新しい 形に 写す（dataseal.py convert）ため だけに のこして ある。アプリには 入らない。
   いまは dataseal.py（標準の 暗号 AES-GCM・アプリは iOS に 入って いる 暗号で 開く）。下は 第4.124版の ときの 説明】
   App Store版の「データの更新」で 読む ファイル（data/mother_app.json）の 中身を、そのままでは 読めない ように する（第4.124版・2026/11/04 まさちゃん「閉じて！」「公開のまま暗号化だけ」）。
   ・暗号の しくみ（AES など）ではなく、鍵で 作った 乱数の 列を 重ねる スクランブル（xoshiro128**）。〔第4.124版の ときは「Apple の 輸出の 申告は かわらない」と 書いた が、
     鍵で 中身を かくす 独自の 計算は Apple の 表の「独自の 暗号化アルゴリズム」に あたる おそれが ある と 見直して、第4.155版で やめた〕
   ・鍵（16バイト）は リポジトリに 入れない：xt/data_key.txt（.gitignore の xt/）か 環境変数 TENGEL_DATA_KEY（32 文字の 16進）。
     なく した ときは claude.ai の Project の「テンゲル_データ更新の鍵」から 戻す（鍵が かわると、出した アプリが 新しい データを 読めなく なる）
   ・CI 用の ビルド（公開の ios ブランチ）は TENGEL_DATA_KEY に ダミーの 鍵を 入れて 作る（本物の 鍵を 公開しない）
   ・同じ 中身なら 同じ ファイル（salt は 中身の SHA-256 から）。16進で 書く（base64 だと 出さない 言葉の 並びが まぎれる ことが ある）
   JS 側は pwa_shim.js の unscramble（同じ 計算）。"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, 'xt', 'data_key.txt')
M = 0xFFFFFFFF


def load_key(required=True):
    v = (os.environ.get('TENGEL_DATA_KEY') or '').strip().lower()
    if not v and os.path.exists(KEY_FILE):
        v = open(KEY_FILE, encoding='utf8').read().strip().lower()
    if not v:
        if required:
            raise SystemExit('データの更新の 鍵（source/xt/data_key.txt）が ないよ。claude.ai の Project の「テンゲル_データ更新の鍵」から 戻してね')
        return None
    if not re.fullmatch(r'[0-9a-f]{32}', v):
        raise SystemExit('データの更新の 鍵の 形が ちがうよ（16進 32 文字）')
    return bytes.fromhex(v)


def _splitmix32(x):
    z = (x + 0x9E3779B9) & M
    z = ((z ^ (z >> 16)) * 0x85EBCA6B) & M
    z = ((z ^ (z >> 13)) * 0xC2B2AE35) & M
    return (z ^ (z >> 16)) & M


def _rotl(x, k):
    return ((x << k) | (x >> (32 - k))) & M


def keystream(key, salt, n):
    k = [int.from_bytes(key[i:i + 4], 'little') for i in range(0, 16, 4)]
    t = [int.from_bytes(salt[i:i + 4], 'little') for i in range(0, 8, 4)]
    s = [_splitmix32(k[0] ^ t[0]), _splitmix32(k[1] ^ t[1]), _splitmix32(k[2] ^ 0xA5A5A5A5), _splitmix32(k[3] ^ 0x5A5A5A5A)]
    if not any(s):
        s[0] = 1
    out = bytearray()
    while len(out) < n:
        r = (_rotl((s[1] * 5) & M, 7) * 9) & M
        tt = (s[1] << 9) & M
        s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]; s[2] ^= tt; s[3] = _rotl(s[3], 11)
        out += r.to_bytes(4, 'little')
    return bytes(out[:n])


def scramble_doc(text, key, kind='mother'):
    """{"app":"tengel","kind":…,"sc":1,"salt":16進,"data":16進}"""
    raw = text.encode('utf8')
    salt = hashlib.sha256(key + raw).digest()[:8]
    ks = keystream(key, salt, len(raw))
    data = bytes(a ^ b for a, b in zip(raw, ks))
    return json.dumps({'app': 'tengel', 'kind': kind, 'sc': 1, 'salt': salt.hex(), 'data': data.hex()}, separators=(',', ':'))


def unscramble_doc(env_text, key):
    e = json.loads(env_text)
    assert e.get('sc') == 1, 'スクランブルの 形が ちがうよ'
    salt, data = bytes.fromhex(e['salt']), bytes.fromhex(e['data'])
    return bytes(a ^ b for a, b in zip(data, keystream(key, salt, len(data)))).decode('utf8')


if __name__ == '__main__':
    import sys
    if sys.argv[1:2] == ['new-key']:   # 鍵を 作る（はじめの 1回だけ）
        if os.path.exists(KEY_FILE):
            raise SystemExit('もう 鍵が あるよ：' + KEY_FILE)
        os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
        open(KEY_FILE, 'w', encoding='utf8').write(os.urandom(16).hex() + '\n')
        print('作ったよ：', KEY_FILE)
    elif sys.argv[1:2] == ['scramble']:   # python3 datascramble.py scramble <ふつうの json> <出す ファイル>
        src, dst = sys.argv[2], sys.argv[3]
        txt = open(src, encoding='utf8').read()
        if json.loads(txt).get('sc') == 1:
            raise SystemExit('もう スクランブルして あるよ：' + src)
        open(dst, 'w', encoding='utf8').write(scramble_doc(txt, load_key()))
        print('スクランブルしたよ：', dst)
