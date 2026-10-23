import Foundation
import UserNotifications

/// 結果確認のお知らせ（13章）：端末の中から出すお知らせ（ローカル通知）。サーバーもプッシュ通知もいらない。
///  ・Webの画面が「予約したレース」の一覧（発走の15分後の時刻つき）を渡す → 近い順に64件まで入れ直す（sync）
///  ・押されたら Webの画面に知らせる（window.__nativeEvent('notify', { race })）。Webがまだ開いていない（アプリを閉じていた）ときは取っておいて、開いたときに渡す（opened）
///  ・お知らせの文は Webの画面が決める（開催場・R・レース名＝読んだ名前・入れた名前だけ）
///  UNUserNotificationCenter の返事（UNNotificationRequest など）は Sendable ではないので、nonisolated の関数の中で読んで、文字列や数だけを返す（Swift 6 の厳しいチェックでも通る形）
private let notifyPrefix = "tengel-race-"
private let notifyMax = 64

/// Webの画面から受けとる1件（Sendable）
private struct SyncItem: Sendable {
    let id: String
    let at: Double   // ミリ秒
    let title: String
    let body: String
    let race: String?
}

/// 待っているお知らせ1件（Sendable）
private struct PendingItem: Sendable {
    let id: String
    let title: String
    let body: String
    let at: Int?
    let race: String?
}

@MainActor
final class Notify: NSObject, UNUserNotificationCenterDelegate {
    static let shared = Notify()

    /// 押されたお知らせを Webの画面へ
    var onOpen: (([String: Any]) -> Void)?
    private var pendingOpen: [String: Any]?

    /// アプリが起動したらすぐ呼ぶ（起動のときに押されたお知らせを受けとるため）
    func install() {
        UNUserNotificationCenter.current().delegate = self
    }

    // MARK: Webの画面からのお願い

    /// { op: 'status' | 'permission' | 'sync' | 'pending' | 'opened', items: [{ id, at（ミリ秒）, title, body, race }] }
    func handle(_ p: [String: Any]) async -> [String: Any] {
        switch p["op"] as? String ?? "" {
        case "status":
            return ["ok": true, "auth": await Self.authName()]
        case "permission":
            do {
                let granted = try await Self.requestPermission()
                return ["ok": true, "granted": granted, "auth": await Self.authName()]
            } catch {
                return ["ok": false, "granted": false, "error": error.localizedDescription, "auth": await Self.authName()]
            }
        case "sync":
            let items = (p["items"] as? [[String: Any]] ?? []).compactMap { it -> SyncItem? in
                guard let id = it["id"] as? String, !id.isEmpty, let at = (it["at"] as? NSNumber)?.doubleValue else { return nil }
                return SyncItem(id: id, at: at, title: (it["title"] as? String) ?? "結果を確認しよう！", body: (it["body"] as? String) ?? "", race: it["race"] as? String)
            }
            let n = await Self.sync(items)
            return ["ok": true, "scheduled": n, "auth": await Self.authName()]
        case "pending":
            let list: [[String: Any]] = await Self.pendingItems().map { x in
                var d: [String: Any] = ["id": x.id, "title": x.title, "body": x.body]
                if let at = x.at { d["at"] = at }
                if let race = x.race { d["race"] = race }
                return d
            }
            return ["ok": true, "list": list]
        case "opened":
            let o = pendingOpen
            pendingOpen = nil
            return ["ok": true, "opened": (o as Any?) ?? NSNull()]
        default:
            return ["ok": false, "error": "unknown op"]
        }
    }

    /// 押されたお知らせを Webの画面へ（まだ開いていなければ取っておく）
    func opened(_ race: String, id: String) {
        let p: [String: Any] = ["race": race, "id": id]
        if let f = onOpen { f(p) } else { pendingOpen = p }
    }

    // MARK: UNUserNotificationCenter（nonisolated：返事を文字列・数にしてから返す）

    private nonisolated static func authName() async -> String {
        let s = await UNUserNotificationCenter.current().notificationSettings()
        switch s.authorizationStatus {
        case .authorized: return "authorized"
        case .denied: return "denied"
        case .provisional: return "provisional"
        case .ephemeral: return "ephemeral"
        case .notDetermined: return "notDetermined"
        @unknown default: return "unknown"
        }
    }

    private nonisolated static func requestPermission() async throws -> Bool {
        try await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge])
    }

    private nonisolated static func pendingItems() async -> [PendingItem] {
        let reqs = await UNUserNotificationCenter.current().pendingNotificationRequests()
        return reqs.filter { $0.identifier.hasPrefix(notifyPrefix) }.map { r in
            var at: Int? = nil
            if let t = r.trigger as? UNTimeIntervalNotificationTrigger, let d = t.nextTriggerDate() { at = Int(d.timeIntervalSince1970 * 1000) }
            return PendingItem(id: String(r.identifier.dropFirst(notifyPrefix.count)), title: r.content.title, body: r.content.body, at: at, race: r.content.userInfo["race"] as? String)
        }
    }

    /// 待たせるお知らせをまとめて入れ直す：テンゲルのものを全部消して、これからの分を近い順に64件まで入れる
    private nonisolated static func sync(_ items: [SyncItem]) async -> Int {
        let center = UNUserNotificationCenter.current()
        let reqs = await center.pendingNotificationRequests()
        let mine = reqs.map(\.identifier).filter { $0.hasPrefix(notifyPrefix) }
        if !mine.isEmpty { center.removePendingNotificationRequests(withIdentifiers: mine) }
        let now = Date().timeIntervalSince1970 * 1000
        let future = items.filter { $0.at > now + 1000 }.sorted { $0.at < $1.at }.prefix(notifyMax)
        var n = 0
        for it in future {
            let content = UNMutableNotificationContent()
            content.title = it.title
            content.body = it.body
            content.sound = .default
            if let race = it.race { content.userInfo = ["race": race] }
            let trigger = UNTimeIntervalNotificationTrigger(timeInterval: max(1, (it.at - now) / 1000), repeats: false)
            let req = UNNotificationRequest(identifier: notifyPrefix + it.id, content: content, trigger: trigger)
            do { try await center.add(req); n += 1 } catch { continue }
        }
        return n
    }

    // MARK: UNUserNotificationCenterDelegate（アプリを開いているときも出す・押されたら知らせる）

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .list, .sound])
    }

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter, didReceive response: UNNotificationResponse, withCompletionHandler completionHandler: @escaping () -> Void) {
        let req = response.notification.request
        let race = req.content.userInfo["race"] as? String ?? ""
        let id = req.identifier.hasPrefix(notifyPrefix) ? String(req.identifier.dropFirst(notifyPrefix.count)) : req.identifier
        Task { @MainActor in Notify.shared.opened(race, id: id) }
        completionHandler()
    }
}
