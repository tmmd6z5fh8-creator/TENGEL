import Foundation

/// App Storeに出ている、このアプリのいちばん新しい版の情報
struct StoreInfo: Sendable {
    var found = false
    var version = ""
    var url = ""
    var notes = ""
    var date = ""
    var error = ""

    /// Webの画面に渡す形（JSON）
    var dictionary: [String: Any] {
        ["found": found, "version": version, "url": url, "notes": notes, "date": date, "error": error]
    }
}

/// App Storeに新しい版が出ているかを Apple に聞く（App Storeの検索の lookup）。
/// 送るのはアプリのID（bundle ID）と国だけで、使う人の情報は送らない。
/// アプリ本体の更新は App Store がする（ここでは版を調べて、画面に「新しい版があるよ」と出すだけ）。
enum StoreCheck {
    static func lookup() async -> StoreInfo {
        var info = StoreInfo()
        guard let bundleID = Bundle.main.bundleIdentifier, !bundleID.isEmpty,
              var parts = URLComponents(string: "https://itunes.apple.com/lookup") else {
            info.error = "アプリのIDがわからないよ"
            return info
        }
        parts.queryItems = [
            URLQueryItem(name: "bundleId", value: bundleID),
            URLQueryItem(name: "country", value: "jp"),
            // 古い答え（キャッシュ）を使わない
            URLQueryItem(name: "t", value: String(Int(Date().timeIntervalSince1970)))
        ]
        guard let url = parts.url else {
            info.error = "問い合わせ先が作れなかったよ"
            return info
        }
        var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 20)
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                info.error = "Appleから返事がなかったよ"
                return info
            }
            guard let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let results = object["results"] as? [[String: Any]],
                  let first = results.first else {
                // まだApp Storeに出ていない（見つからない）
                return info
            }
            info.found = true
            info.version = first["version"] as? String ?? ""
            info.url = first["trackViewUrl"] as? String ?? ""
            info.notes = first["releaseNotes"] as? String ?? ""
            info.date = first["currentVersionReleaseDate"] as? String ?? ""
        } catch {
            info.error = error.localizedDescription
        }
        return info
    }
}
