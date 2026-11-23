# MP3 を、音を 1サンプルも かえずに 小さく 包み直す（第4.212版・まさちゃん 2026/11/23 10:12「音の質感、音が俺が聞いてる音と変わらないならやって欲しい！」）
#   音を 作り直す（もう 一度 MP3 に する）のでは ない。MP3 の コマ（フレーム）の 中の「音の データ」（main data）は 1ビットも さわらず、
#   決まった 大きさの コマ（CBR 256k／192k）に 入って いた「つめもの」（使って いない ビット）だけを ぬいて、コマを 小さい 大きさ（VBR）に かえる。
#   ・コマの 数・順・コマごとの 音の データ・サイド情報（main_data_begin の ほか）・はじめの おくれ（delay）・おわりの 余り（padding）は 同じ
#     → どの プレーヤーで ほどいても、出て くる 音は もとと 同じ サンプル（くり返しの 所も ずれない）。mp3packer と 同じ 考え方
#   ・頭の しるし（Xing／Info ＋ LAME の 追記）は ffmpeg（Lavf の mp3enc.c）と 同じ 作り方で 書き直す（VBR に なる ので Info → Xing・目次・大きさ・CRC）
#   使い方：
#     python3 kisekae/mp3_repack.py <もとの mp3> <出す mp3>      … 1つ 包み直す（たしかめて から 書く）
#     python3 kisekae/mp3_repack.py --selfcheck <mp3> …          … 頭の しるしの 作り方が もとの ファイルと 同じに なるか（1バイトも ちがわない こと）
#   たしかめ（verify）：もとと 出した ものを コマごとに 読み直して、音の データ・サイド情報・コマの 数が 同じ ことを 見る（ちがえば 書かない）
import struct, sys

BR1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]      # MPEG1 Layer3 の ビットレート（kbps）
MDB_MAX = 511                                                                  # main_data_begin は 9ビット（前の コマの あきを 511バイト まで 使える）
XING_NUM_BAGS = 400                                                            # Lavf（mp3enc.c）の 目次の 作り方と 同じ 数


def crc16(data, crc=0):
    """CRC-16（ANSI・下の ビットから：Lavf の AV_CRC_16_ANSI_LE）"""
    for x in data:
        crc ^= x
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def bits(b, pos, n):
    v = 0
    for k in range(pos, pos + n):
        v = (v << 1) | ((b[k >> 3] >> (7 - (k & 7))) & 1)
    return v


def parse(b):
    """→ dict(id3＝頭の ID3v2・frames＝[コマ]・tail＝おわりの 余分)。コマ＝dict(hdr, side, area, mdb, nbits, ln, br, mono)"""
    i = 0
    if b[:3] == b'ID3':
        i = 10 + ((b[6] & 0x7f) << 21 | (b[7] & 0x7f) << 14 | (b[8] & 0x7f) << 7 | (b[9] & 0x7f))
    id3 = b[:i]; fr = []; first = None
    while i + 4 <= len(b):
        h = struct.unpack('>I', b[i:i + 4])[0]
        if (h >> 21) & 0x7ff != 0x7ff:
            break
        ver = (h >> 19) & 3; layer = (h >> 17) & 3; prot = (h >> 16) & 1; bri = (h >> 12) & 15; sri = (h >> 10) & 3; pad = (h >> 9) & 1; chm = (h >> 6) & 3
        if ver != 3 or layer != 1 or bri in (0, 15) or sri != 0:
            raise ValueError('MPEG1 Layer3・44.1kHz の コマ では ない（%d バイト目）' % i)
        if not prot:
            raise ValueError('CRC つきの コマは あつかわない')
        mono = chm == 3; ns = 17 if mono else 32; ln = 144000 * BR1[bri] // 44100 + pad
        if i + ln > len(b):
            raise ValueError('さいごの コマが 欠けて いる')
        fixed = h & 0xFFFF0DCF                                                  # ビットレート・つめものの 1バイト（padding）・左右の 合わせ方（コマごとに かわる）の ほかは 同じ はず
        if fr:                                                                  # はじめの コマ（頭の しるし）は ステレオの 書き方 などが ちがっても よい（Lavf：stereo／音の コマは joint stereo）。チャンネルの 数は 同じ はず
            if first is None: first = fixed
            elif fixed != first: raise ValueError('コマの 形（モノ／ステレオ など）が とちゅうで かわる（%d バイト目）' % i)
            if mono != fr[0]['mono']: raise ValueError('頭の しるしと 音の コマで チャンネルの 数が ちがう')
        side = b[i + 4:i + 4 + ns]; nch = 1 if mono else 2; p = 9 + (5 if mono else 3) + 4 * nch; nb = 0
        for _ in range(2 * nch):
            nb += bits(side, p, 12); p += 59
        fr.append(dict(hdr=b[i:i + 4], side=side, area=b[i + 4 + ns:i + ln], mdb=bits(side, 0, 9), nbits=nb, ln=ln, br=BR1[bri], mono=mono))
        i += ln
    return dict(id3=id3, frames=fr, tail=b[i:])


def is_tag(f):
    """頭の しるしの コマ（Xing／Info）か"""
    return f['nbits'] == 0 and f['area'][:4] in (b'Xing', b'Info')


def payloads(fr):
    """音の コマごとの 音の データ（バイト）：コマの データは、自分の 所の main_data_begin バイト 前から 始まって、(nbits+7)//8 バイト"""
    S = b''.join(f['area'] for f in fr); out = []; off = 0; end = 0
    for k, f in enumerate(fr):
        st = off - f['mdb']; n = (f['nbits'] + 7) // 8
        if st < end or st + n > off + len(f['area']):
            raise ValueError('コマ %d の 音の データの 場所が おかしい（前と 重なる・自分の コマを はみ出す）' % k)
        out.append(S[st:st + n]); end = st + n; off += len(f['area'])
    return out


def side_key(f):
    """サイド情報から main_data_begin（はじめの 9ビット）を のぞいた もの（くらべる 用）"""
    return bytes([f['side'][0] & 0, f['side'][1] & 0x7f]) + f['side'][2:]


def sizes(ns, top):
    """えらべる コマ：[(音の データを 入れられる バイト, ビットレートの 番号, つめものの 1バイト)]（小さい 順）。もとの ビットレート（top）より 大きい コマは 使わない"""
    out = []
    for bri in range(1, BR1.index(top) + 1):
        for pad in (0, 1):
            out.append((144000 * BR1[bri] // 44100 + pad - 4 - ns, bri, pad))
    return sorted(out)


def toc_bags(tag_ln, lens):
    """Lavf（mp3enc.c の mp3_xing_add_frame）と 同じ 数え方：→ (目次 100こ, 大きさの 合計)"""
    size = tag_ln; seen = 0; want = 1; pos = 0; bag = [0] * XING_NUM_BAGS
    for ln in lens:
        seen += 1; size += ln
        if want == seen:
            bag[pos] = size; pos += 1
            if pos == XING_NUM_BAGS:
                for i in range(1, XING_NUM_BAGS, 2): bag[i >> 1] = bag[i]
                want *= 2; pos = XING_NUM_BAGS // 2
            seen = 0
    toc = [0] + [min(255, 256 * bag[i * pos // 100] // size) for i in range(1, 100)]
    return toc, size


def tag_frame(tag, audio, vbr):
    """頭の しるしの コマを 書き直す（Lavf の mp3_update_xing と 同じ）：しるしの 字・コマの 数・大きさ・目次・LAME の 追記の 大きさと CRC。ほかは もとの まま"""
    t = bytearray(tag['hdr'] + tag['side'] + tag['area']); ns = len(tag['side']); x = 4 + ns
    flags = struct.unpack('>I', t[x + 4:x + 8])[0]
    if flags != 15: raise ValueError('頭の しるしの 形が ちがう（flags %d）' % flags)
    toc, size = toc_bags(len(t), [len(a) for a in audio])
    t[x:x + 4] = b'Xing' if vbr else b'Info'
    t[x + 8:x + 12] = struct.pack('>I', len(audio)); t[x + 12:x + 16] = struct.pack('>I', size); t[x + 16:x + 116] = bytes(toc)
    e = x + 120                                                                 # LAME の 追記（36バイト）：…・delay／padding（21〜23）・…・音の 大きさ（28〜31）・音の CRC（32〜33）・しるしの CRC（34〜35）
    t[e + 28:e + 32] = struct.pack('>I', size)
    c = 0
    for a in audio: c = crc16(a, c)
    t[e + 32:e + 34] = struct.pack('>H', c)
    t[e + 34:e + 36] = struct.pack('>H', crc16(bytes(t[:190])))                # Lavf：コマの はじめの 190バイト（モノラルは しるしの CRC の 所〈まだ 前の 値〉も 入る → 下で 合わせる）
    return bytes(t)


def tag_crc_fix(t, old):
    """しるしの CRC：Lavf は「CRC を 書く 前の コマ」の はじめの 190バイトで 数える。ステレオは CRC の 所が 190バイト目 から なので そのまま。
    モノラルは CRC の 所（175〜176バイト目）が 190バイトの 中に 入る → 書く 前の 値（0）で 数える"""
    ns = 17 if (t[3] >> 6) & 3 == 3 else 32; e = 4 + ns + 120; z = bytearray(t)
    if e + 34 < 190:
        z[e + 34:e + 36] = b'\x00\x00'
        z[e + 34:e + 36] = struct.pack('>H', crc16(bytes(z[:190])))
    return bytes(z)


def repack(b):
    """→ (包み直した バイト, 知らせ dict)"""
    P = parse(b); fr = P['frames']
    if not fr or not is_tag(fr[0]): raise ValueError('頭の しるし（Xing／Info）が ない')
    tag, au = fr[0], fr[1:]; ns = len(tag['side']); data = payloads(au); n = len(au); SZ = sizes(ns, max(f['br'] for f in au)); cmax = SZ[-1][0]
    # うしろから：コマ k の 前に あいて いないと いけない バイト（大きい コマは 前の コマの あきを 借りる）
    need = [0] * (n + 1)
    for k in range(n - 1, -1, -1):
        need[k] = max(0, len(data[k]) + need[k + 1] - cmax)
        if need[k] > MDB_MAX: raise ValueError('コマ %d が 大きすぎて 入らない' % k)
    out = []; stream = bytearray(); avail = 0; waste = 0; brs = set()
    for k, f in enumerate(au):
        mdb = min(avail, MDB_MAX)
        if avail > mdb: waste += avail - mdb                                    # 511バイトより 前の あきは 使えない（つめものの まま）
        d = data[k]; want = len(d) - mdb + need[k + 1]
        cap, bri, pad = next(s for s in SZ if s[0] >= want)
        st = len(stream) - mdb                                                  # この コマの 音の データが 始まる 所（流れの 中）
        stream[st:st + len(d)] = d if st + len(d) <= len(stream) else d[:len(stream) - st]
        if st + len(d) > len(stream): stream += d[len(stream) - st:]
        used_own = max(0, len(d) - mdb); stream += bytes(cap - used_own)        # 自分の コマの のこりは あき（0）
        avail = mdb + cap - len(d)
        h = struct.unpack('>I', f['hdr'])[0] & 0xFFFF0DFF | bri << 12 | pad << 9
        s = bytearray(f['side']); s[0] = mdb >> 1; s[1] = (s[1] & 0x7f) | (mdb & 1) << 7
        out.append((struct.pack('>I', h), bytes(s), cap)); brs.add(BR1[bri])
    frames = []; off = 0
    for h, s, cap in out:
        frames.append(h + s + bytes(stream[off:off + cap])); off += cap
    vbr = len(brs) > 1 or (brs and brs != {tag['br']})
    t = tag_crc_fix(tag_frame(tag, frames, vbr), tag)
    res = P['id3'] + t + b''.join(frames) + P['tail']
    return res, dict(frames=n, old=len(b), new=len(res), waste=waste + avail, brs=sorted(brs), vbr=vbr)


def verify(a, b):
    """もと a と 包み直し b：コマの 数・コマごとの 音の データ・サイド情報（main_data_begin の ほか）・コマの 形・ID3・おわりの 余分・delay／padding が 同じ → ''（ちがえば わけ）"""
    A, B = parse(a), parse(b); fa, fb = A['frames'], B['frames']
    if A['id3'] != B['id3'] or A['tail'] != B['tail']: return 'ID3／おわりの 余分が ちがう'
    if len(fa) != len(fb): return 'コマの 数が ちがう'
    if not is_tag(fb[0]): return '頭の しるしが ない'
    e = 120                                                                     # area（サイド情報の あと）の 中の LAME の 追記の はじまり：しるし 4・flags 4・コマの 数 4・大きさ 4・目次 100・quality 4
    if fa[0]['area'][e + 21:e + 24] != fb[0]['area'][e + 21:e + 24] or fa[0]['area'][e:e + 21] != fb[0]['area'][e:e + 21]: return 'delay／padding が ちがう'
    if struct.unpack('>I', fb[0]['area'][8:12])[0] != len(fb) - 1: return '頭の しるしの コマの 数が ちがう'
    if struct.unpack('>I', fb[0]['area'][12:16])[0] != len(b) - len(B['id3']) - len(B['tail']): return '頭の しるしの 大きさが ちがう'
    da, db = payloads(fa[1:]), payloads(fb[1:])
    for k in range(len(da)):
        x, y = fa[k + 1], fb[k + 1]
        if da[k] != db[k]: return 'コマ %d の 音の データが ちがう' % k
        if side_key(x) != side_key(y) or x['nbits'] != y['nbits']: return 'コマ %d の サイド情報が ちがう' % k
        if struct.unpack('>I', x['hdr'])[0] & 0xFFFF0DFF != struct.unpack('>I', y['hdr'])[0] & 0xFFFF0DFF: return 'コマ %d の 形が ちがう' % k
    return ''


def selfcheck(b):
    """もとの ファイルの コマ から 頭の しるしを 作り直すと、もとの 頭の しるしと 1バイトも ちがわないか（作り方が Lavf と 同じ ことの たしかめ）"""
    P = parse(b); fr = P['frames']; tag = fr[0]
    old = tag['hdr'] + tag['side'] + tag['area']
    new = tag_crc_fix(tag_frame(tag, [f['hdr'] + f['side'] + f['area'] for f in fr[1:]], old[4 + len(tag['side']):8 + len(tag['side'])] == b'Xing'), tag)
    return old == new, [i for i in range(len(old)) if old[i] != new[i]][:8]


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--selfcheck':
        bad = 0
        for p in sys.argv[2:]:
            ok, where = selfcheck(open(p, 'rb').read()); bad += 0 if ok else 1
            print(('同じ   ' if ok else '※ちがう') + ' ' + p + ('' if ok else ' ' + str(where)))
        sys.exit(1 if bad else 0)
    if len(sys.argv) != 3:
        sys.exit('使い方：python3 kisekae/mp3_repack.py <もとの mp3> <出す mp3>')
    a = open(sys.argv[1], 'rb').read(); b, r = repack(a); w = verify(a, b)
    if w: sys.exit('※ たしかめで ちがい：' + w)
    open(sys.argv[2], 'wb').write(b)
    print(f"{r['old']:,} → {r['new']:,} B（{r['new'] / r['old'] * 100:.1f}%）・コマ {r['frames']}こ・{r['brs'][0]}〜{r['brs'][-1]}kbps")


if __name__ == '__main__':
    main()
