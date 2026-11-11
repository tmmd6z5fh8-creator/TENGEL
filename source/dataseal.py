"""App Store版の「データの更新」で 読む ファイル（data/mother_app2.json）を、鍵が ないと 読めない ように 封じる（第4.155版・2026/11/11 まさちゃん「入れていいよ！」）。
   ・暗号は 世界の 標準の AES-GCM（鍵 128bit）。アプリは **iOS に 入って いる 暗号（Apple CryptoKit）で 開く**（ios/Tengel.swiftpm/DataSeal.swift）＝ アプリは 自分の 暗号の 計算を 持たない。
     Apple の 輸出の 申告（ビルドごとの 暗号化の 質問）：「Apple の OS が 提供する 暗号化アルゴリズム だけ」＝ 書類は いらない（答えは「上記のアルゴリズムのいずれでもない」）。
     Android版を 作る ときは、Android に 入って いる AES-GCM で 同じ ファイルを 同じ 鍵で 開ける
   ・前（第4.124〜4.154版）は 姫が 作った スクランブル（datascramble.py：xoshiro128** の 乱数の 列を 重ねる）。独自の 計算は Apple の 表の「独自の 暗号化アルゴリズム」
     （アメリカの 書類 CCATS が いる）に あたる おそれが ある ので やめた。前の ファイル（data/mother_app.json・sc:1）は 前の テスト版の ために 公開の 場所に のこす（新しい アプリは 読まない）
   ・鍵は 前と 同じ（16バイト）：リポジトリに 入れない。xt/data_key.txt（.gitignore の xt/）か 環境変数 TENGEL_DATA_KEY（32 文字の 16進）。
     なく した ときは claude.ai の Project の「テンゲル_データ更新の鍵」から 戻す（鍵が かわると、出した アプリが 新しい データを 読めなく なる）
   ・CI 用の ビルド（公開の ios ブランチ）は TENGEL_DATA_KEY に ダミーの 鍵（0 が 32こ）を 入れて 作る（本物の 鍵を 公開しない）
   ・同じ 中身なら 同じ ファイル：nonce（12バイト）は SHA-256(鍵 ＋ 中身) の はじめ（中身が ちがえば nonce も ちがう ＝ 同じ nonce を 2つの 中身に 使わない）
   ・16進で 書く（base64 だと 出さない 言葉の 並びが まぎれる ことが ある）
   形：{"app":"tengel","kind":"mother","sc":2,"iv":16進 24文字,"data":16進（暗号文 ＋ しるし 16バイト）}
   封じる 計算：Python の cryptography が あれば それ（OpenSSL）。なければ この ファイルの 中の AES-GCM（_gcm：作る ときだけ 使う・アプリには 入らない。test_dataentry.py が 2つを 見くらべる）
   python3 dataseal.py seal <ふつうの json> <出す ファイル>       … ふつうの JSON を 封じる
   python3 dataseal.py convert <前の 形（sc:1）> <出す ファイル>    … 前の スクランブルの ファイルを 開いて、同じ 中身を 新しい 形に
   python3 dataseal.py open <封じた ファイル>                     … 開いて、中身の あらまし（版・数）を 出す（確かめ用）
   python3 dataseal.py vector                                    … CI の 確かめ用の 見本（ダミーの 鍵で 封じた 短い 文）"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, 'xt', 'data_key.txt')
DUMMY_KEY = bytes(16)                    # CI 用の ビルドの 鍵（公開）


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


# ---------- AES-128-GCM（cryptography が ない ときの 予備：NIST SP 800-38D。作る ときだけ 使う）----------
def _sbox():
    p = q = 1
    s = [0] * 256
    while True:
        p = (p ^ (p << 1) ^ (0x1B if p & 0x80 else 0)) & 0xFF                # p × 3
        q ^= q << 1; q ^= q << 2; q ^= q << 4; q &= 0xFF                      # q ÷ 3
        if q & 0x80:
            q ^= 0x09
        x = q ^ ((q << 1) | (q >> 7)) ^ ((q << 2) | (q >> 6)) ^ ((q << 3) | (q >> 5)) ^ ((q << 4) | (q >> 4))
        s[p] = (x ^ 0x63) & 0xFF
        if p == 1:
            break
    s[0] = 0x63
    return s


_S = _sbox()
_X2 = [((b << 1) ^ (0x1B if b & 0x80 else 0)) & 0xFF for b in range(256)]


def _expand(key):
    assert len(key) == 16
    w = [list(key[i:i + 4]) for i in range(0, 16, 4)]
    rc = 1
    for i in range(4, 44):
        t = list(w[i - 1])
        if i % 4 == 0:
            t = [_S[t[1]] ^ rc, _S[t[2]], _S[t[3]], _S[t[0]]]
            rc = _X2[rc]
        w.append([a ^ b for a, b in zip(w[i - 4], t)])
    return [sum(w[r * 4:(r + 1) * 4], []) for r in range(11)]


def _block(rk, blk):
    s = [a ^ b for a, b in zip(blk, rk[0])]
    for r in range(1, 11):
        s = [_S[v] for v in s]
        s = [s[(i + 4 * (i % 4)) % 16] for i in range(16)]                   # 行を ずらす（列ごとに ならんだ 16こ）
        if r < 10:
            o = []
            for c in range(0, 16, 4):
                a0, a1, a2, a3 = s[c:c + 4]
                o += [_X2[a0] ^ _X2[a1] ^ a1 ^ a2 ^ a3, a0 ^ _X2[a1] ^ _X2[a2] ^ a2 ^ a3, a0 ^ a1 ^ _X2[a2] ^ _X2[a3] ^ a3, _X2[a0] ^ a0 ^ a1 ^ a2 ^ _X2[a3]]
            s = o
        s = [a ^ b for a, b in zip(s, rk[r])]
    return bytes(s)


def _gmul(x, y):
    z, v = 0, y
    for i in range(127, -1, -1):
        if (x >> i) & 1:
            z ^= v
        v = (v >> 1) ^ (0xE1 << 120 if v & 1 else 0)
    return z


def _gcm(key, iv, data, encrypt):
    """AES-128-GCM（nonce 12バイト・しるし 16バイト・AAD なし）。encrypt＝True：中身 → 暗号文＋しるし／False：暗号文＋しるし → 中身（しるしが 合わなければ ValueError）"""
    assert len(iv) == 12
    rk = _expand(key)
    h = int.from_bytes(_block(rk, bytes(16)), 'big')
    j0 = iv + b'\x00\x00\x00\x01'
    ct_in = data if encrypt else data[:-16]
    out = bytearray()
    for i in range(0, len(ct_in), 16):
        ks = _block(rk, iv + (i // 16 + 2).to_bytes(4, 'big'))
        out += bytes(a ^ b for a, b in zip(ct_in[i:i + 16], ks))
    ct = bytes(out) if encrypt else ct_in
    y = 0
    for i in range(0, len(ct), 16):
        y = _gmul(y ^ int.from_bytes(ct[i:i + 16].ljust(16, b'\x00'), 'big'), h)
    y = _gmul(y ^ (len(ct) * 8), h)
    tag = bytes(a ^ b for a, b in zip(y.to_bytes(16, 'big'), _block(rk, j0)))
    if encrypt:
        return ct + tag
    if tag != data[-16:]:
        raise ValueError('しるしが 合わない（鍵か 中身が ちがう）')
    return bytes(out)


def _aesgcm(key, iv, data, encrypt, pure=False):
    if not pure:
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except Exception:
            AESGCM = None
        if AESGCM is not None:
            try:
                return AESGCM(key).encrypt(iv, data, None) if encrypt else AESGCM(key).decrypt(iv, data, None)
            except Exception as e:
                if encrypt:
                    raise
                raise ValueError('しるしが 合わない（鍵か 中身が ちがう）') from e
    return _gcm(key, iv, data, encrypt)


# ---------- 封じる・開く ----------
def seal_doc(text, key, kind='mother', pure=False):
    """{"app":"tengel","kind":…,"sc":2,"iv":16進,"data":16進}"""
    raw = text.encode('utf8')
    iv = hashlib.sha256(key + raw).digest()[:12]
    return json.dumps({'app': 'tengel', 'kind': kind, 'sc': 2, 'iv': iv.hex(), 'data': _aesgcm(key, iv, raw, True, pure).hex()}, separators=(',', ':'))


def open_doc(env_text, key, pure=False):
    e = json.loads(env_text)
    assert e.get('sc') == 2, '封じた 形が ちがうよ'
    return _aesgcm(key, bytes.fromhex(e['iv']), bytes.fromhex(e['data']), False, pure).decode('utf8')


VECTOR_TEXT = '{"app":"tengel","kind":"selftest","msg":"テンゲル ok"}'       # CI の 確かめ用（ダミーの 鍵で 封じる：ios/ci/selftest.js）


if __name__ == '__main__':
    import sys
    cmd = sys.argv[1:2]
    if cmd == ['seal']:
        src, dst = sys.argv[2], sys.argv[3]
        txt = open(src, encoding='utf8').read()
        if json.loads(txt).get('sc') is not None:
            raise SystemExit('もう 封じて あるよ：' + src)
        open(dst, 'w', encoding='utf8').write(seal_doc(txt, load_key()))
        print('封じたよ：', dst)
    elif cmd == ['convert']:
        import datascramble
        src, dst = sys.argv[2], sys.argv[3]
        key = load_key()
        txt = datascramble.unscramble_doc(open(src, encoding='utf8').read(), key)
        doc = json.loads(txt)
        assert doc.get('app') == 'tengel' and isinstance(doc.get('rows'), list), '中身の 形が ちがうよ'
        out = seal_doc(txt, key)
        assert open_doc(out, key) == txt and open_doc(out, key, pure=True) == txt
        open(dst, 'w', encoding='utf8').write(out)
        print('新しい 形に したよ：', dst, '・版', doc.get('ver'), '・', len(doc['rows']), '走・', len(out), '文字')
    elif cmd == ['open']:
        doc = json.loads(open_doc(open(sys.argv[2], encoding='utf8').read(), load_key()))
        print('開けたよ：', {k: (v if not isinstance(v, list) else f'{len(v)}こ') for k, v in doc.items()})
    elif cmd == ['vector']:
        print(seal_doc(VECTOR_TEXT, DUMMY_KEY, kind='selftest'))
    else:
        raise SystemExit(__doc__)
