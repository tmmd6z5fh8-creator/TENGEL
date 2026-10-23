import Foundation
import StoreKit

/// App内課金（StoreKit 2）：ポイントのパック（消耗型）とサブスク（1か月・自動更新）。
/// 買う・届く・終わらせる（finish）はここ。ポイントを台帳に足すのはWebの画面（points_ui.js）で、
/// 台帳に書けたら Web → アプリ に finish をお願いする（書く前には終わらせない）。
/// 新しい取引（更新・返金・ほかの端末での購入）は Transaction.updates で届くので、Webの画面に知らせる（window.__nativeEvent('iap', …)）。
@MainActor
final class Store {
    static let shared = Store()
    static let packIDs = ["jp.tengel.app.points500", "jp.tengel.app.points1000", "jp.tengel.app.points2000", "jp.tengel.app.points4000"]
    static let subIDs = ["jp.tengel.app.sub2000", "jp.tengel.app.sub4400", "jp.tengel.app.sub9200"]
    static var allIDs: [String] { packIDs + subIDs }

    private var products: [String: Product] = [:]
    private var listener: Task<Void, Never>?
    /// 新しい取引が届いたときに呼ぶ（Webの画面へ知らせる）
    var onTransaction: (([String: Any]) -> Void)?

    /// 起動したら、取引の更新を聞きはじめる
    func start() {
        guard listener == nil else { return }
        listener = Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                if case .verified(let tx) = result {
                    self.onTransaction?(Self.dict(tx))
                }
            }
        }
    }

    // MARK: 商品

    func loadProducts() async -> [String: Any] {
        do {
            let list = try await Product.products(for: Self.allIDs)
            products = Dictionary(uniqueKeysWithValues: list.map { ($0.id, $0) })
            let rows: [[String: Any]] = Self.allIDs.compactMap { id in
                guard let p = products[id] else { return nil }
                var d: [String: Any] = ["id": id, "title": p.displayName, "price": p.displayPrice, "kind": Self.subIDs.contains(id) ? "sub" : "pack",
                                        "amount": NSDecimalNumber(decimal: p.price).doubleValue, "currency": p.priceFormatStyle.currencyCode]
                if let s = p.subscription { d["period"] = "\(s.subscriptionPeriod.value)\(s.subscriptionPeriod.unit)" }
                return d
            }
            return ["ok": true, "products": rows, "missing": Self.allIDs.filter { products[$0] == nil }]
        } catch {
            return ["ok": false, "error": error.localizedDescription]
        }
    }

    // MARK: 買う

    func buy(_ id: String) async -> [String: Any] {
        if products[id] == nil { _ = await loadProducts() }
        guard let p = products[id] else { return ["ok": false, "state": "no_product"] }
        do {
            let result = try await p.purchase()
            switch result {
            case .success(let verification):
                switch verification {
                case .verified(let tx):
                    return ["ok": true, "state": "ok", "tx": Self.dict(tx)]
                case .unverified(_, let err):
                    return ["ok": false, "state": "unverified", "error": err.localizedDescription]
                }
            case .userCancelled:
                return ["ok": false, "state": "cancelled"]
            case .pending:
                return ["ok": false, "state": "pending"]
            @unknown default:
                return ["ok": false, "state": "unknown"]
            }
        } catch {
            return ["ok": false, "state": "failed", "error": error.localizedDescription]
        }
    }

    // MARK: 届いているのにまだ台帳に入れていない取引・いまのサブスク

    /// まだ終わらせていない取引（アプリを開いたときに見る）
    func unfinished() async -> [[String: Any]] {
        var out: [[String: Any]] = []
        for await result in Transaction.unfinished {
            if case .verified(let tx) = result { out.append(Self.dict(tx)) }
        }
        return out
    }

    /// いま有効なもの（サブスクの今の期間・まだ終わらせていない消耗型）。「購入を復元」でAppleと合わせたあとに見る
    func current() async -> [[String: Any]] {
        var out: [[String: Any]] = []
        for await result in Transaction.currentEntitlements {
            if case .verified(let tx) = result { out.append(Self.dict(tx)) }
        }
        return out
    }

    /// 購入を復元：Appleと合わせる → いま有効な取引を返す
    func restore() async -> [String: Any] {
        do {
            try await AppStore.sync()
        } catch {
            return ["ok": false, "error": error.localizedDescription]
        }
        return ["ok": true, "current": await current(), "unfinished": await unfinished()]
    }

    /// 台帳に書けた取引を終わらせる
    func finish(_ id: UInt64) async -> Bool {
        for await result in Transaction.unfinished {
            if case .verified(let tx) = result, tx.id == id {
                await tx.finish()
                return true
            }
        }
        return false
    }

    /// サブスクの状態（Webの画面の「サブスク」の欄に出す）
    func subscriptionStatus() async -> [String: Any] {
        var active: [[String: Any]] = []
        for await result in Transaction.currentEntitlements {
            guard case .verified(let tx) = result, Self.subIDs.contains(tx.productID) else { continue }
            var d = Self.dict(tx)
            if let p = products[tx.productID], let sub = p.subscription, let statuses = try? await sub.status {
                for s in statuses {
                    if case .verified(let info) = s.renewalInfo {
                        d["willRenew"] = info.willAutoRenew
                        if let next = info.autoRenewPreference { d["next"] = next }
                        d["state"] = Self.stateName(s.state)
                    }
                }
            }
            active.append(d)
        }
        return ["ok": true, "active": active]
    }

    private static func stateName(_ s: Product.SubscriptionInfo.RenewalState) -> String {
        switch s {
        case .subscribed: return "subscribed"
        case .expired: return "expired"
        case .inBillingRetryPeriod: return "billingRetry"
        case .inGracePeriod: return "grace"
        case .revoked: return "revoked"
        default: return "unknown"
        }
    }

    /// 取引 → Webの画面に渡す形
    static func dict(_ tx: Transaction) -> [String: Any] {
        let f = ISO8601DateFormatter()
        var d: [String: Any] = ["id": String(tx.id), "originalId": String(tx.originalID), "product": tx.productID,
                                "kind": subIDs.contains(tx.productID) ? "sub" : "pack", "date": f.string(from: tx.purchaseDate),
                                "revoked": tx.revocationDate != nil, "env": "\(tx.environment)"]
        if let e = tx.expirationDate { d["expires"] = f.string(from: e) }
        if let r = tx.revocationDate { d["revokedAt"] = f.string(from: r) }
        return d
    }

    /// Webの画面からのお願い：{ op: 'products'|'buy'|'restore'|'unfinished'|'current'|'finish'|'status', id }
    func handle(_ p: [String: Any]) async -> [String: Any] {
        switch p["op"] as? String ?? "" {
        case "products": return await loadProducts()
        case "buy": return await buy(p["id"] as? String ?? "")
        case "restore": return await restore()
        case "unfinished": return ["ok": true, "list": await unfinished()]
        case "current": return ["ok": true, "list": await current()]
        case "status": return await subscriptionStatus()
        case "finish":
            guard let s = p["id"] as? String, let id = UInt64(s) else { return ["ok": false, "error": "bad id"] }
            return ["ok": await finish(id)]
        default: return ["ok": false, "error": "unknown op"]
        }
    }
}
