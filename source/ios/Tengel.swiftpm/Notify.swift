import Foundation
import UserNotifications

/// 結果確認のお知らせ（13章）：端末の中から出すお知らせ（ローカル通知）。サーバーもプッシュ通知もいらない。
///  ・Webの画面が「予約したレース」の一覧（発走の15分後の時刻つき）を渡す → 近い順に64件まで入れ直す（sync）
///  ・押されたら Webの画面に知らせる（window.__nativeEvent('notify', { race })）。Webがまだ開いていない（アプリを閉じていた）ときは取っておいて、開いたときに渡す（opened）
///  ・お知らせの文は Webの画面が決める（開催場・R・レース名＝読んだ名前・入れた名前だけ）
@MainActor
final class Notify: NSObject, UNUserNotificationCenterDelegate {
    static let shared = Notify()
    static let prefix = "tengel-race-"
    static let maxPending = 64

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
            return ["ok": true, "auth": await authName()]
        case "permission":
            do {
                let granted = try await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge])
                return ["ok": true, "granted": granted, "auth": await authName()]
            } catch {
                return ["ok": false, "granted": false, "error": error.localizedDescription, "auth": await authName()]
            }
        case "sync":
            let items = p["items"] as? [[String: Any]] ?? []
            let n = await sync(items)
            return ["ok": true, "scheduled": n, "auth": await authName()]
        case "pending":
            let reqs = await UNUserNotificationCenter.current().pendingNotificationRequests()
            let list: [[String: Any]] = reqs.filter { $0.identifier.hasPrefix(Self.prefix) }.map { r in
                var d: [String: Any] = ["id": String(r.identifier.dropFirst(Self.prefix.count)), "title": r.content.title, "body": r.content.body]
                if let t = r.trigger as? UNTimeIntervalNotificationTrigger, let d2 = t.nextTriggerDate() { d["at"] = Int(d2.timeIntervalSince1970 * 1000) }
                if let race = r.content.userInfo["race"] as? String { d["race"] = race }
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

    private func authName() async -> String {
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

    /// 待たせるお知らせをまとめて入れ直す：テンゲルのものを全部消して、これからの分を近い順に64件まで入れる
    private func sync(_ items: [[String: Any]]) async -> Int {
        let center = UNUserNotificationCenter.current()
        let reqs = await center.pendingNotificationRequests()
        let mine = reqs.map(\.identifier).filter { $0.hasPrefix(Self.prefix) }
        if !mine.isEmpty { center.removePendingNotificationRequests(withIdentifiers: mine) }
        let now = Date().timeIntervalSince1970 * 1000
        let future = items.compactMap { it -> (Double, [String: Any])? in
            guard let at = (it["at"] as? NSNumber)?.doubleValue, at > now + 1000, let id = it["id"] as? String, !id.isEmpty else { return nil }
            return (at, it)
        }.sorted { $0.0 < $1.0 }.prefix(Self.maxPending)
        var n = 0
        for (at, it) in future {
            let content = UNMutableNotificationContent()
            content.title = (it["title"] as? String) ?? "結果を確認しよう！"
            content.body = (it["body"] as? String) ?? ""
            content.sound = .default
            if let race = it["race"] as? String { content.userInfo = ["race": race] }
            let trigger = UNTimeIntervalNotificationTrigger(timeInterval: max(1, (at - now) / 1000), repeats: false)
            let req = UNNotificationRequest(identifier: Self.prefix + (it["id"] as? String ?? ""), content: content, trigger: trigger)
            do { try await center.add(req); n += 1 } catch { continue }
        }
        return n
    }

    /// 押されたお知らせを Webの画面へ（まだ開いていなければ取っておく）
    func opened(_ race: String, id: String) {
        let p: [String: Any] = ["race": race, "id": id]
        if let f = onOpen { f(p) } else { pendingOpen = p }
    }

    // MARK: UNUserNotificationCenterDelegate（アプリを開いているときも出す・押されたら知らせる）

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .list, .sound])
    }

    nonisolated func userNotificationCenter(_ center: UNUserNotificationCenter, didReceive response: UNNotificationResponse, withCompletionHandler completionHandler: @escaping () -> Void) {
        let req = response.notification.request
        let race = req.content.userInfo["race"] as? String ?? ""
        let id = req.identifier.hasPrefix(Self.prefix) ? String(req.identifier.dropFirst(Self.prefix.count)) : req.identifier
        Task { @MainActor in Notify.shared.opened(race, id: id) }
        completionHandler()
    }
}
