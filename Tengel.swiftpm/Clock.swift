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
/// 第4.212版：電源を 入れ直した あと などは、正しい 時刻を Apple の サーバーに 聞く（net：下）。
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

    // MARK: - インターネットの 時刻（第4.212版）

    /// インターネットの 時刻の 答え（Webの 画面に わたす 形は dictionary）
    struct NetTime: Sendable {
        var ok = false
        var t = 0.0        // 時刻（1970年からの ミリ秒）
        var mono = 0.0     // その ときの 電源を 入れてからの 時間（ミリ秒）
        var rt = 0.0       // 行って 帰る までの 時間（ミリ秒）
        var why = ""
        var dictionary: [String: Any] { ["ok": ok, "t": t, "mono": mono, "rt": rt, "why": why] }
    }

    /// キャッシュも クッキーも 持たない 通信（この 問い合わせ だけに 使う）
    private static let session: URLSession = {
        let c = URLSessionConfiguration.ephemeral
        c.timeoutIntervalForRequest = 6
        c.timeoutIntervalForResource = 8
        c.waitsForConnectivity = false
        c.httpCookieStorage = nil
        c.urlCache = nil
        c.requestCachePolicy = .reloadIgnoringLocalCacheData
        return URLSession(configuration: c)
    }()

    private static func monoNow() -> Double { Double(mach_continuous_time()) * ratio / 1_000_000 }

    /// 正しい 時刻を Apple の サーバーに 聞く（Webの 画面からの お願い「clock」に net が ついて いる とき）。
    /// 電源を 入れ直した あとは、電源を 入れてからの 時間（mono）が 0 から 始まる ので、切れて いた あいだに どれだけ たったかが アプリの 中 だけ では わからない。
    /// → App Store に 新しい 版が 出て いるかを 聞く のと 同じ 問い合わせ先（StoreCheck：App Store の lookup）の 返事に ついて いる 日付（HTTP の Date）を 読む。
    /// 送る のは アプリの ID（bundle ID）と 国 だけで、使う 人の 情報は 送らない。返事の 中身は 使わない（日付 だけ）。
    static func net() async -> NetTime {
        var out = NetTime()
        guard let bundleID = Bundle.main.bundleIdentifier, !bundleID.isEmpty,
              var parts = URLComponents(string: "https://itunes.apple.com/lookup") else {
            out.why = "id"
            return out
        }
        parts.queryItems = [
            URLQueryItem(name: "bundleId", value: bundleID),
            URLQueryItem(name: "country", value: "jp"),
            // 古い 答え（キャッシュ）を 使わない
            URLQueryItem(name: "t", value: String(Int(Date().timeIntervalSince1970)))
        ]
        guard let url = parts.url else {
            out.why = "url"
            return out
        }
        var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 6)
        request.httpMethod = "HEAD"
        let m0 = monoNow()
        do {
            let (_, response) = try await session.data(for: request)
            let m1 = monoNow()
            guard let http = response as? HTTPURLResponse,
                  let text = http.value(forHTTPHeaderField: "Date"),
                  let date = httpDate(text) else {
                out.why = "date"
                return out
            }
            var t = date.timeIntervalSince1970 * 1000
            // とちゅうの サーバーが おぼえて いた 返事 だった とき：作られて から たった 秒（Age）を 足す
            if let age = http.value(forHTTPHeaderField: "Age"), let a = Double(age.trimmingCharacters(in: .whitespaces)), a >= 0, a < 86_400 {
                t += a * 1000
            }
            out.rt = m1 - m0
            guard out.rt >= 0, out.rt < 8000, t > 1_700_000_000_000 else {
                out.why = "range"
                return out
            }
            out.ok = true
            out.t = t + 500            // 日付は 秒まで（切りすて）→ まん中に
            out.mono = (m0 + m1) / 2   // 行きと 帰りの まん中
        } catch {
            out.why = "net"
        }
        return out
    }

    /// HTTP の 日付（例：Sun, 22 Nov 2026 17:24:35 GMT）
    private static func httpDate(_ text: String) -> Date? {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(secondsFromGMT: 0)
        f.dateFormat = "EEE, dd MMM yyyy HH:mm:ss zzz"
        return f.date(from: text.trimmingCharacters(in: .whitespaces))
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
