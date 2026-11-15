import Foundation
import MultipeerConnectivity

// 馬カードバトルの「部屋」（第4.176版・まさちゃん 2026/11/15 21:54「部屋を作成して、友達と対戦」）
//  ・近くに いる iPhone どうしが 直接 つながる（Apple の MultipeerConnectivity：Wi‑Fi・Bluetooth）。サーバーは 使わない・インターネットにも 出ない
//  ・部屋を 作る 人（ホスト）＝まわりに「部屋番号」を 知らせる ／ 入る 人（ゲスト）＝同じ 番号の 部屋を さがして 入る。つながるのは 1対1
//  ・通信は 暗号化（encryptionPreference: .required）。送るのは 対戦の 手と 画面に 出す ことだけ（Webの 画面が 作る 文字）。名前や 端末の 名前は 送らない
//  ・Webの 画面からの お願い（window.webkit.messageHandlers.tengel の name: "room"）：
//      { op: "host", room: "1234" }・{ op: "join", room: "1234" }・{ op: "send", data: "…" }・{ op: "stop" }・{ op: "state" }
//  ・Webの 画面への 知らせ（window.__nativeEvent("room", …)）：
//      { ev: "state", state: "hosting"／"searching"／"connecting"／"connected"／"idle" }・{ ev: "data", data: "…" }・{ ev: "error", why: "…" }
//  ・Package.swift の capabilities に .localNetwork（説明の 文と Bonjour の 名前 _tengel-cb._tcp／_udp）が いる（はじめて 使う ときに iOS が「ローカルネットワーク」の 確認を 出す）
//  ・MultipeerConnectivity の 返事は いろいろな スレッドに 来る → つなぎ役（RoomLink）が 自分の 鍵（NSLock）で 守って、
//    アプリ（メイン）には 文字と 数だけ の できごと（RoomEvent：Sendable）を 渡す（Swift 6 の 厳しい チェックでも 通る 形）

/// Bonjour の サービスの 名前（15字まで・小文字と 数字と ハイフン）
private let roomService = "tengel-cb"

/// つなぎ役から アプリ（メイン）へ 渡す できごと
struct RoomEvent: Sendable {
    let link: Int        // どの つなぎ役の できごとか（前の 部屋の 残りを 捨てる ため）
    let kind: String     // "state"・"data"・"error"
    let text: String
}

/// Webの 画面と つなぎ役の あいだ（メイン）
@MainActor
final class Room {
    static let shared = Room()

    /// Webの 画面へ
    var onEvent: (([String: Any]) -> Void)?

    private var link: RoomLink?
    private var serial = 0
    private var state = "idle"

    func handle(_ p: [String: Any]) -> [String: Any] {
        let op = p["op"] as? String ?? ""
        switch op {
        case "host", "join":
            let room = p["room"] as? String ?? ""
            guard room.count == 4, room.allSatisfy({ ("0"..."9").contains($0) }) else {
                return ["ok": false, "why": "room"]
            }
            stop()
            serial += 1
            let host = op == "host"
            let made = RoomLink(id: serial, room: room, host: host) { ev in
                Task { @MainActor in Room.shared.deliver(ev) }
            }
            link = made
            state = host ? "hosting" : "searching"
            made.start()
            return ["ok": true, "state": state]
        case "send":
            guard let link, let text = p["data"] as? String else { return ["ok": false, "why": "off"] }
            return ["ok": link.send(text)]
        case "stop":
            stop()
            return ["ok": true]
        case "state":
            return ["ok": true, "state": state]
        default:
            return ["ok": false, "why": "op"]
        }
    }

    private func stop() {
        link?.stop()
        link = nil
        state = "idle"
    }

    private func deliver(_ ev: RoomEvent) {
        guard ev.link == serial, link != nil else { return }
        switch ev.kind {
        case "state":
            state = ev.text
            if ev.text == "idle" {
                link?.stop()
                link = nil
            }
            onEvent?(["ev": "state", "state": ev.text])
        case "data":
            onEvent?(["ev": "data", "data": ev.text])
        default:
            stop()
            onEvent?(["ev": "error", "why": ev.text])
        }
    }
}

/// つなぎ役：MultipeerConnectivity の 部品を 持って、返事を 受ける。中の 変わる ものは lock で 守る
final class RoomLink: NSObject, MCSessionDelegate, MCNearbyServiceAdvertiserDelegate, MCNearbyServiceBrowserDelegate, @unchecked Sendable {
    private let id: Int
    private let room: String
    private let host: Bool
    private let emit: @Sendable (RoomEvent) -> Void
    private let lock = NSLock()
    private let me: MCPeerID
    private let session: MCSession
    private var advertiser: MCNearbyServiceAdvertiser?
    private var browser: MCNearbyServiceBrowser?
    private var other: MCPeerID?          // つないで いる（つなぎ中の）相手
    private var connected = false
    private var stopped = false
    private var tries = 0

    init(id: Int, room: String, host: Bool, emit: @escaping @Sendable (RoomEvent) -> Void) {
        self.id = id
        self.room = room
        self.host = host
        self.emit = emit
        // 相手に 見える 名前：でたらめな 字（端末の 名前・持ち主の 名前は 使わない）
        me = MCPeerID(displayName: "tengel-" + String(UInt32.random(in: 0...UInt32.max), radix: 16))
        session = MCSession(peer: me, securityIdentity: nil, encryptionPreference: .required)
        super.init()
        session.delegate = self
    }

    func start() {
        if host {
            let made = MCNearbyServiceAdvertiser(peer: me, discoveryInfo: ["room": room, "v": "1"], serviceType: roomService)
            made.delegate = self
            lock.lock()
            advertiser = made
            lock.unlock()
            made.startAdvertisingPeer()
        } else {
            let made = MCNearbyServiceBrowser(peer: me, serviceType: roomService)
            made.delegate = self
            lock.lock()
            browser = made
            lock.unlock()
            made.startBrowsingForPeers()
        }
    }

    func send(_ text: String) -> Bool {
        lock.lock()
        let to = connected ? other : nil
        lock.unlock()
        guard let to, let data = text.data(using: .utf8) else { return false }
        do {
            try session.send(data, toPeers: [to], with: .reliable)
            return true
        } catch {
            return false
        }
    }

    func stop() {
        lock.lock()
        if stopped {
            lock.unlock()
            return
        }
        stopped = true
        let a = advertiser
        let b = browser
        advertiser = nil
        browser = nil
        lock.unlock()
        a?.stopAdvertisingPeer()
        a?.delegate = nil
        b?.stopBrowsingForPeers()
        b?.delegate = nil
        session.delegate = nil
        session.disconnect()
    }

    private func say(_ kind: String, _ text: String) {
        lock.lock()
        let off = stopped
        lock.unlock()
        if !off {
            emit(RoomEvent(link: id, kind: kind, text: text))
        }
    }

    // MARK: ホスト（部屋を 作った 人）：入りたい 人が 来た

    func advertiser(_ advertiser: MCNearbyServiceAdvertiser, didReceiveInvitationFromPeer peerID: MCPeerID, withContext context: Data?, invitationHandler: @escaping (Bool, MCSession?) -> Void) {
        let want = context.flatMap { String(data: $0, encoding: .utf8) } ?? ""
        lock.lock()
        let ok = !stopped && other == nil && want == room      // 部屋番号が 同じ・まだ だれも 入って いない
        if ok {
            other = peerID
        }
        lock.unlock()
        invitationHandler(ok, ok ? session : nil)
        if ok {
            say("state", "connecting")
        }
    }

    func advertiser(_ advertiser: MCNearbyServiceAdvertiser, didNotStartAdvertisingPeer error: Error) {
        say("error", "advertise")
    }

    // MARK: ゲスト（部屋に 入る 人）：部屋が 見つかった

    func browser(_ browser: MCNearbyServiceBrowser, foundPeer peerID: MCPeerID, withDiscoveryInfo info: [String: String]?) {
        guard let info, info["room"] == room else { return }
        lock.lock()
        let ok = !stopped && other == nil
        if ok {
            other = peerID
            tries += 1
        }
        lock.unlock()
        guard ok else { return }
        say("state", "connecting")
        browser.invitePeer(peerID, to: session, withContext: room.data(using: .utf8), timeout: 20)
    }

    func browser(_ browser: MCNearbyServiceBrowser, lostPeer peerID: MCPeerID) {
    }

    func browser(_ browser: MCNearbyServiceBrowser, didNotStartBrowsingForPeers error: Error) {
        say("error", "browse")
    }

    // MARK: つながり

    func session(_ session: MCSession, peer peerID: MCPeerID, didChange state: MCSessionState) {
        var out: String?
        var failed = false
        var again: MCNearbyServiceBrowser?
        var quietA: MCNearbyServiceAdvertiser?
        var quietB: MCNearbyServiceBrowser?
        lock.lock()
        if !stopped && other == peerID {
            if state == .connected {
                connected = true
                out = "connected"
                quietA = advertiser      // つながったら もう 知らせない・さがさない
                quietB = browser
            } else if state == .notConnected {
                if connected {
                    connected = false
                    other = nil
                    out = "idle"         // つながって いた のが 切れた
                } else {
                    other = nil          // つなぐ とちゅうで だめだった：ホストは 次の 人を 待つ・ゲストは もう一度 さがす（5回まで）
                    if host {
                        out = "hosting"
                    } else if tries < 5 {
                        out = "searching"
                        again = browser
                    } else {
                        failed = true
                    }
                }
            }
        }
        lock.unlock()
        quietA?.stopAdvertisingPeer()
        quietB?.stopBrowsingForPeers()
        if let again {
            again.stopBrowsingForPeers()
            again.startBrowsingForPeers()
        }
        if let out {
            say("state", out)
        }
        if failed {
            say("error", "connect")
        }
    }

    func session(_ session: MCSession, didReceive data: Data, fromPeer peerID: MCPeerID) {
        lock.lock()
        let mine = connected && other == peerID
        lock.unlock()
        guard mine, data.count <= 65536, let text = String(data: data, encoding: .utf8) else { return }
        say("data", text)
    }

    func session(_ session: MCSession, didReceive stream: InputStream, withName streamName: String, fromPeer peerID: MCPeerID) {
    }

    func session(_ session: MCSession, didStartReceivingResourceWithName resourceName: String, fromPeer peerID: MCPeerID, with progress: Progress) {
    }

    func session(_ session: MCSession, didFinishReceivingResourceWithName resourceName: String, fromPeer peerID: MCPeerID, at localURL: URL?, withError error: Error?) {
    }
}
