import Foundation
import Security

/// キーチェーンに残す「しるし」（ユーザーのデータではない）。
///  ・初回プレゼント（1,500P）を受け取ったしるし（gift-first）… アプリを消して入れ直しても、もう一度はもらえない
///  ・サブスクのPを足した取引の番号（granted-sub）… 入れ直して同じ月のPを2回もらわない
/// iCloudキーチェーンで同期する（同じApple IDのほかの端末でも、初回のPはもう一度もらえない）。
/// ポイントの台帳そのものはアプリの中（IndexedDB＋自動バックアップ）で、アプリを消すと消える。
enum Markers {
    static let service = "jp.tengel.app.markers"

    /// 値を読む。なければ nil。読めなかった（エラー）ときは "error:<番号>" を返す
    static func get(_ key: String) -> (value: String?, error: String?) {
        var q = query(key)
        q[kSecReturnData as String] = kCFBooleanTrue
        q[kSecMatchLimit as String] = kSecMatchLimitOne
        var out: CFTypeRef?
        let st = SecItemCopyMatching(q as CFDictionary, &out)
        if st == errSecSuccess, let data = out as? Data {
            return (String(data: data, encoding: .utf8) ?? "", nil)
        }
        if st == errSecItemNotFound {
            return (nil, nil)
        }
        return (nil, "error:\(st)")
    }

    /// 値を書く（あれば書きかえる）
    @discardableResult
    static func set(_ key: String, _ value: String) -> String? {
        let data = Data(value.utf8)
        var q = query(key)
        let attrs: [String: Any] = [kSecValueData as String: data]
        var st = SecItemUpdate(q as CFDictionary, attrs as CFDictionary)
        if st == errSecItemNotFound {
            q[kSecValueData as String] = data
            // いつ開いても読めるように。iCloudキーチェーンで同期するので ThisDeviceOnly は付けない
            q[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlock
            st = SecItemAdd(q as CFDictionary, nil)
        }
        return st == errSecSuccess ? nil : "error:\(st)"
    }

    @discardableResult
    static func remove(_ key: String) -> String? {
        let st = SecItemDelete(query(key) as CFDictionary)
        return st == errSecSuccess || st == errSecItemNotFound ? nil : "error:\(st)"
    }

    private static func query(_ key: String) -> [String: Any] {
        [kSecClass as String: kSecClassGenericPassword,
         kSecAttrService as String: service,
         kSecAttrAccount as String: key,
         kSecAttrSynchronizable as String: kCFBooleanTrue as Any]
    }

    /// Webの画面からのお願い：{ op: 'get'|'set'|'del', key, value }
    static func handle(_ p: [String: Any]) -> [String: Any] {
        guard let key = p["key"] as? String, !key.isEmpty, key.count <= 64 else { return ["ok": false, "error": "bad key"] }
        switch p["op"] as? String ?? "get" {
        case "set":
            let value = p["value"] as? String ?? "1"
            guard value.count <= 4000 else { return ["ok": false, "error": "too long"] }
            if let e = set(key, value) { return ["ok": false, "error": e] }
            return ["ok": true]
        case "del":
            if let e = remove(key) { return ["ok": false, "error": e] }
            return ["ok": true]
        default:
            let r = get(key)
            if let e = r.error { return ["ok": false, "error": e] }
            return ["ok": true, "value": r.value as Any, "has": r.value != nil]
        }
    }
}
