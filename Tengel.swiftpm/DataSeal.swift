import CryptoKit
import Foundation

/// 「データの更新」の ファイルを 開く（第4.155版）。
///  ・暗号は iOS に 入って いる もの（Apple CryptoKit の AES-GCM）だけを 使う。アプリは 自分の 暗号の 計算を 持たない
///   （輸出の 申告：Apple の OS が 提供する 暗号化 だけ）。
///  ・鍵（16バイト）・nonce（12バイト）・中身（暗号文 ＋ しるし 16バイト）は 16進の 文字で、Web の 画面が わたす（pwa_shim.js の unseal）。
///  ・封じる 側は source/dataseal.py。鍵や 中身が ちがう（しるしが 合わない）ときは nil
enum DataSeal {
    /// { key, iv, data }（16進）→ 開いた 文字（UTF-8）。開けない ときは nil
    static func open(_ p: [String: Any]) -> String? {
        guard let key = bytes(p["key"] as? String), key.count == 16,
              let iv = bytes(p["iv"] as? String), iv.count == 12,
              let data = bytes(p["data"] as? String), data.count > 16 else { return nil }
        do {
            let nonce = try AES.GCM.Nonce(data: iv)
            let box = try AES.GCM.SealedBox(nonce: nonce, ciphertext: data.dropLast(16), tag: data.suffix(16))
            let plain = try AES.GCM.open(box, using: SymmetricKey(data: key))
            return String(data: plain, encoding: .utf8)
        } catch {
            return nil
        }
    }

    /// 16進の 文字 → バイト。16進で ない 字・奇数の 長さは nil
    private static func bytes(_ text: String?) -> Data? {
        guard let text else { return nil }
        let u = Array(text.utf8)
        guard u.count % 2 == 0 else { return nil }
        var out = Data(capacity: u.count / 2)
        var i = 0
        while i < u.count {
            guard let a = nibble(u[i]), let b = nibble(u[i + 1]) else { return nil }
            out.append(a << 4 | b)
            i += 2
        }
        return out
    }

    private static func nibble(_ c: UInt8) -> UInt8? {
        switch c {
        case 48...57: return c - 48      // 0〜9
        case 97...102: return c - 87     // a〜f
        case 65...70: return c - 55      // A〜F
        default: return nil
        }
    }
}
