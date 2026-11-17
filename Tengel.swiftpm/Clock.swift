import Foundation
import Security

/// 時計の 番人（第4.191版）に わたす 時計。
/// iPhone の 時計（設定で 日付を かえられる）とは べつに、電源を 入れてからの 時間（設定では かえられない）を わたす。
/// Webの 画面（clock_guard.js の TengelClock）が この 2つを くらべて、日付を 進めた・もどした ことを 見つける
/// （ログインボーナス・カードバトルの ミッションの 月・サブスクの ポイントの 期限を、本当の 時刻で 決める）。
///  ・wall：いまの 時刻（1970年からの ミリ秒・設定で かえられる）
///  ・mono：電源を 入れてからの 時間（ねむって いる 間も 進む・ミリ秒：mach_continuous_time）
///  ・boot：電源を 入れる たびに かわる 番号（iOS が 見せて くれない ときは 空）
///  ・proc：アプリを 開く たびに かわる 番号
///  ・dev：この 端末の 番号（キーチェーンの この 端末 だけの しるし：バックアップから べつの 端末に もどすと かわる・iCloud で 同期しない）
/// どの 値も どこにも 送らない（アプリの 中で、前に 見た ときから どれだけ たったかを はかる だけ）。
enum Clock {
    /// アプリを 開く たびに かわる 番号
    static let proc = UUID().uuidString

    /// 電源を 入れる たびに かわる 番号（アプリが 動いて いる あいだは かわらない）
    static let boot: String = {
        var size = 0
        guard sysctlbyname("kern.bootsessionuuid", nil, &size, nil, 0) == 0, size > 1, size <= 64 else { return "" }
        var buf = [CChar](repeating: 0, count: size + 1)
        guard sysctlbyname("kern.bootsessionuuid", &buf, &size, nil, 0) == 0 else { return "" }
        return buf.withUnsafeBufferPointer { p in p.baseAddress.map { String(cString: $0) } ?? "" }
    }()

    private static let ratio: Double = {
        var info = mach_timebase_info_data_t()
        guard mach_timebase_info(&info) == KERN_SUCCESS, info.denom > 0 else { return 1 }
        return Double(info.numer) / Double(info.denom)
    }()

    private static let service = "jp.tengel.app.clock"

    /// いまの 時計（Webの 画面からの お願い「clock」）
    static func sample() -> [String: Any] {
        let wall = Date().timeIntervalSince1970 * 1000
        let mono = Double(mach_continuous_time()) * ratio / 1_000_000
        return ["wall": wall, "mono": mono, "boot": boot, "proc": proc, "dev": device]
    }

    /// この 端末の 番号（はじめて 使う ときに 作って キーチェーンに 入れる。読めない ときは 空）。
    /// アプリが 動いて いる あいだに 1回 だけ 読む（static let：Swift 6 でも かわる 共有の 値を 持たない）
    private static let device: String = {
        let base: [String: Any] = [kSecClass as String: kSecClassGenericPassword,
                                   kSecAttrService as String: service,
                                   kSecAttrAccount as String: "device"]
        var q = base
        q[kSecReturnData as String] = kCFBooleanTrue
        q[kSecMatchLimit as String] = kSecMatchLimitOne
        var out: CFTypeRef?
        let st = SecItemCopyMatching(q as CFDictionary, &out)
        if st == errSecSuccess, let data = out as? Data, let s = String(data: data, encoding: .utf8), !s.isEmpty {
            return s
        }
        guard st == errSecItemNotFound else { return "" }      // 読めない（まだ ロックを 外して いない・シミュレーターの 署名なし ビルド など）：番号なし（Webの 画面は 同じ 端末と みなす）
        let s = UUID().uuidString
        var add = base
        add[kSecValueData as String] = Data(s.utf8)
        // この 端末 だけ（べつの 端末に もどした バックアップには 入らない・iCloud キーチェーンで 同期しない）
        add[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        return SecItemAdd(add as CFDictionary, nil) == errSecSuccess ? s : ""
    }()
}
