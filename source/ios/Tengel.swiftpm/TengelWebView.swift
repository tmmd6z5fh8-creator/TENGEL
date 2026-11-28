import AVFoundation
import SwiftUI
import UIKit
import WebKit

/// アプリの中のWeb画面（テンゲルの画面そのもの）
struct TengelWebView: UIViewRepresentable {
    func makeCoordinator() -> WebBridge {
        WebBridge()
    }

    func makeUIView(context: Context) -> WebHostView {
        WebHostView(webView: context.coordinator.makeWebView())
    }

    func updateUIView(_ view: WebHostView, context: Context) {}
}

/// iPad など 広い 画面で 使う「iPhone の 大きさ」（第4.156版・まさちゃん 2026/11/12「アプリ自体、iPadでもiPhoneと同じ大きさで表示されるようにして！」）
/// ・App Store版は iPhone用（iPad では iPadOS が iPhone の 大きさの 窓で 動かす＝互換モード）なので、お客さんの 画面は かわらない。
///   かわる のは iPad の 画面いっぱいの 窓で 動かす とき（Swift Playgrounds の ▶）だけ：アプリを iPhone の 大きさ（390×844）で まん中に 置く（まわりは 黒）
/// ・ねらい：iPad の 広い 幅（834pt など）に 合わせて 壁紙や 動画を 2倍あまりに 引きのばさない ＝ iPhone の お客さんが 見る のと 同じ 見え方を iPad で 確かめられる
///   （390×844 は 壁紙の 舞台の 幅 390・的中の 動画 780×1688 と ぴったり 同じ ＝ iPad の 画面〈2倍〉の 点と 1対1 に なる）
enum PhoneFrame {
    static let size = CGSize(width: 390, height: 844)
    /// これより 広い 幅の とき iPhone の 大きさで 置く（iPhone は いちばん 広くても 440pt。iPad の 細い 窓〈Slide Over 320〜375pt など〉は そのまま 窓いっぱい）
    static let wideWidth: CGFloat = 480
    static func isWide(_ width: CGFloat) -> Bool { width > wideWidth }
}

/// Web画面の入れ物。時計・電波（ステータスバー）やホームバーに重なる分を測って、Webの画面に --top-inset／--bottom-inset（px）として渡す。
/// ふつうは画面の上は安全な範囲の中に置かれるので 0。Swift Playgrounds のプレビューなど、安全な範囲が正しく伝わらないところでも
/// 上の帯やボタンが時計・電波の下に重ならないようにするためのもの（Webの画面は max(env(safe-area-inset-*), var(--*-inset)) で使う）。
final class WebHostView: UIView {
    let webView: WKWebView
    private var sent: (top: Int, bottom: Int) = (-1, -1)

    init(webView: WKWebView) {
        self.webView = webView
        super.init(frame: .zero)
        backgroundColor = .tengelPage
        addSubview(webView)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { nil }

    /// 広い 画面（iPad の 画面いっぱいの 窓）か：その ときは Webの 画面を iPhone の 大きさで まん中に 置く（PhoneFrame）
    var framed: Bool { PhoneFrame.isWide(bounds.width) }

    override func layoutSubviews() {
        super.layoutSubviews()
        let wide = framed
        let frame = wide ? phoneRect() : bounds
        if webView.frame != frame { webView.frame = frame }
        backgroundColor = wide ? .black : .tengelPage
        pushInsets()
    }

    override func safeAreaInsetsDidChange() {
        super.safeAreaInsetsDidChange()
        setNeedsLayout()
        pushInsets()
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        setNeedsLayout()
        pushInsets()
        // 第4.224版：時計・電池の 字の 白／黒（覚えて いる 値）を 窓に 出た ときから
        StatusBarStyle.apply(in: window)
    }

    /// iPhone の 大きさの 置き場：時計の 帯・ホームバーに 重ならない 範囲の まん中（高さが 足りない ときは その 範囲の 高さ まで）。点の ずれが 出ない ように 整数の 位置に 置く
    private func phoneRect() -> CGRect {
        let o = overlap
        let top = CGFloat(o.top), areaH = max(0, bounds.height - top - CGFloat(o.bottom))
        let w = min(PhoneFrame.size.width, bounds.width), h = min(PhoneFrame.size.height, areaH)
        return CGRect(x: ((bounds.width - w) / 2).rounded(), y: (top + (areaH - h) / 2).rounded(), width: w, height: h)
    }

    /// Webの 画面に 渡す 重なり。iPhone の 大きさで 置いた とき（framed）は 時計の 帯・ホームバーを よけて 置く ので 0
    var insets: (top: Int, bottom: Int) {
        framed ? (0, 0) : overlap
    }

    /// 上と下の、重なる分（pt）。上＝時計・電波の帯のうち、この入れ物にかかっている高さ。下＝ホームバーのうち、この入れ物にかかっている高さ
    var overlap: (top: Int, bottom: Int) {
        guard let window, bounds.height > 0, bounds.width > 0 else { return (0, 0) }
        let me = convert(bounds, to: window)
        var top = window.safeAreaInsets.top - me.minY
        if let bar = window.windowScene?.statusBarManager, !bar.isStatusBarHidden, window.frame.origin == .zero {
            let frame = bar.statusBarFrame
            if frame.height > 0, frame.height < 120 {
                top = max(top, frame.maxY - me.minY)
            }
        }
        let bottom = window.safeAreaInsets.bottom - (window.bounds.maxY - me.maxY)
        // iPad で アプリを 画面いっぱいに 動かす とき（Swift Playgrounds の ▶ など）、時計・電池の 帯の 高さが 0 と 返って くる ことが ある
        // → 画面いっぱいの 窓で 上の あきが 0 なら、iPad の 時計の 帯の 高さ（ホームバーの ある iPad は 24pt・ホームボタンの iPad は 20pt）を 足す（第4.59版・まさちゃんの iPad の 画面）
        if top <= 0, me.minY <= 0, UIDevice.current.userInterfaceIdiom == .pad,
           window.frame.origin == .zero, window.bounds.size == (window.windowScene?.screen ?? window.screen).bounds.size {
            top = window.safeAreaInsets.bottom > 0 ? 24 : 20
        }
        return (Int(max(0, top).rounded()), Int(max(0, bottom).rounded()))
    }

    /// Webの画面に重なる分を渡す（変わったときだけ。force はページを開き直したとき）
    func pushInsets(force: Bool = false) {
        let v = insets
        if !force, v == sent { return }
        sent = v
        let js = "(function(){var s=document.documentElement&&document.documentElement.style;if(!s)return;s.setProperty('--top-inset','\(v.top)px');s.setProperty('--bottom-inset','\(v.bottom)px');})()"
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    /// テスト用：測った値（CIで確かめる）
    var layoutInfo: [String: Any] {
        let v = insets
        let w = window
        return ["top": v.top, "bottom": v.bottom, "safeTop": w?.safeAreaInsets.top ?? -1, "safeBottom": w?.safeAreaInsets.bottom ?? -1,
                "statusBar": w?.windowScene?.statusBarManager?.statusBarFrame.height ?? -1, "y": w.map { convert(bounds, to: $0).minY } ?? -1,
                "height": bounds.height, "windowHeight": w?.bounds.height ?? -1,
                // 第4.156版：iPhone の 大きさで 置いたか（iPad の 広い 窓）・Webの 画面の 置き場
                "framed": framed, "hostWidth": bounds.width, "windowWidth": w?.bounds.width ?? -1,
                "webX": webView.frame.minX, "webY": webView.frame.minY, "webWidth": webView.frame.width, "webHeight": webView.frame.height,
                "statusBarHidden": w?.windowScene?.statusBarManager?.isStatusBarHidden ?? false,
                // 第4.224版：時計・電池の 帯の 色と 字（statusBarStyle：1＝白い 字・3＝黒い 字）
                "statusBarStyle": w?.windowScene?.statusBarManager?.statusBarStyle.rawValue ?? -1, "tint": StatusBarTint.shared.info]
    }
}

/// Webの画面とアプリをつなぐ：共有シート（ファイルに保存）・コピー・自動バックアップ・App Storeの版・画像の文字の読み取り・外のリンク
@MainActor
final class WebBridge: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
    private weak var webView: WKWebView?
    private var backupWritten = false

    func makeWebView() -> WKWebView {
        let config = WKWebViewConfiguration()
        config.setURLSchemeHandler(AppSchemeHandler(), forURLScheme: AppSchemeHandler.scheme)
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        config.userContentController.add(self, name: "tengel")
        config.userContentController.addUserScript(
            WKUserScript(source: Self.infoScript(), injectionTime: .atDocumentStart, forMainFrameOnly: true)
        )
        #if DEBUG
        SelfTest.install(on: config)
        #endif

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = self
        webView.allowsLinkPreview = false
        webView.isOpaque = false
        webView.backgroundColor = .tengelPage
        webView.scrollView.backgroundColor = .tengelPage
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        #if DEBUG
        if #available(iOS 16.4, *) {
            webView.isInspectable = true
        }
        #endif
        self.webView = webView
        AppFiles.clearSharedFiles()
        // App内課金：新しい取引（更新・返金・ほかの端末での購入）が届いたら、Webの画面に知らせる（台帳に足すのはWeb側）
        Store.shared.onTransaction = { [weak self] tx in self?.event("iap", tx) }
        Store.shared.start()
        // 結果確認のお知らせが押されたら、Webの画面に知らせる（そのレースの結果入力へ）
        Notify.shared.onOpen = { [weak self] p in self?.event("notify", p) }
        // 馬カードバトルの 部屋（第4.176版：近くの iPhone と 直接 つながる）：つながりの ようす・届いた 手を Webの 画面に 知らせる
        Room.shared.onEvent = { [weak self] p in self?.event("room", p) }
        // キーボードが 出た／しまった を Webの 画面に 知らせる（数字の 欄で キーボードが 出なければ アプリの 中の テンキーを 出す：第4.62版）
        for (name, open) in [(UIResponder.keyboardWillShowNotification, true), (UIResponder.keyboardWillHideNotification, false)] {
            NotificationCenter.default.addObserver(forName: name, object: nil, queue: .main) { [weak self] n in
                let h = (n.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect)?.height ?? 0
                Task { @MainActor in self?.event("keyboard", ["open": open, "height": Double(h)]) }
            }
        }
        // 第4.233版（まさちゃん 2026/11/27 22:48「アプリ開いてる状態で、一度下げて他のアプリ開くと音出なくなるからそれも改善して！」）：
        //   アプリが 前に もどった・ほかの アプリの 音で とぎれた のが おわった → 音の 出口（AVAudioSession）を 起こし直して、Webの 画面に 知らせる（audio）。
        //   Webの 画面は 止まった 音の 出口を resume し直し、動かなければ 作り直す（fx.js の TengelAudioWake）
        NotificationCenter.default.addObserver(forName: UIApplication.didBecomeActiveNotification, object: nil, queue: .main) { [weak self] _ in
            Task { @MainActor in
                AudioWake.activate()
                self?.event("audio", ["why": "active"])
            }
        }
        NotificationCenter.default.addObserver(forName: AVAudioSession.interruptionNotification, object: nil, queue: .main) { [weak self] n in
            let raw = (n.userInfo?[AVAudioSessionInterruptionTypeKey] as? NSNumber)?.uintValue ?? 0
            guard AVAudioSession.InterruptionType(rawValue: raw) == .ended else { return }
            Task { @MainActor in
                AudioWake.activate()
                self?.event("audio", ["why": "interruption"])
            }
        }
        webView.load(URLRequest(url: AppSchemeHandler.startURL))
        return webView
    }

    /// アプリ → Webの画面への知らせ（window.__nativeEvent(name, payload)）
    private func event(_ name: String, _ payload: Any) {
        guard let webView else { return }
        let js = "window.__nativeEvent && window.__nativeEvent(\(Self.jsonLiteral(name)), \(Self.jsonLiteral(payload)))"
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    /// 拡大（2本指）：ふだんは viewport の決まり（最大3倍）で拡大できる。演出・アプリを開いた時の画面のときは 1倍にもどして止める
    private func zoom(_ p: [String: Any]) {
        guard let webView else { return }
        let sv = webView.scrollView
        if p["reset"] as? Bool == true, sv.zoomScale != 1 {
            sv.setZoomScale(1, animated: true)
        }
        if let lock = p["lock"] as? Bool {
            sv.pinchGestureRecognizer?.isEnabled = !lock
        }
    }

    /// アプリの版などを、Webの画面が読む前に入れておく（window.__NATIVE_INFO）
    private static func infoScript() -> String {
        let info = Bundle.main.infoDictionary ?? [:]
        let fields: [String: String] = [
            "version": info["CFBundleShortVersionString"] as? String ?? "",
            "build": info["CFBundleVersion"] as? String ?? "",
            "device": UIDevice.current.userInterfaceIdiom == .pad ? "pad" : "phone"
        ]
        return "window.__NATIVE_INFO = \(jsonLiteral(fields));"
    }

    /// 値をJavaScriptにそのまま書ける形（JSON）にする
    static func jsonLiteral(_ value: Any) -> String {
        guard JSONSerialization.isValidJSONObject([value]),
              let data = try? JSONSerialization.data(withJSONObject: [value]),
              let text = String(data: data, encoding: .utf8) else { return "null" }
        return String(text.dropFirst().dropLast())   // [値] の [ ] を外す
    }

    // MARK: - ページの移動

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction) async -> WKNavigationActionPolicy {
        guard let url = navigationAction.request.url, let scheme = url.scheme?.lowercased() else {
            return .cancel
        }
        if scheme == AppSchemeHandler.scheme || scheme == "about" || scheme == "blob" || scheme == "data" {
            return .allow
        }
        // テンゲルの外のページ（http・https・メールなど）は、Safariなどアプリの外で開く
        //（説明書は アプリの 中の 重ねた 窓（iframe）で 開くので、その 中の リンクを 押した ときも 外で 開く：第4.62版）
        if navigationAction.targetFrame?.isMainFrame != false || navigationAction.navigationType == .linkActivated {
            UIApplication.shared.open(url, options: [:], completionHandler: nil)
            return .cancel
        }
        return .allow
    }

    /// Web画面の中身が落ちたら、開き直す（記録は保存場所に残っている）
    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        webView.reload()
    }

    /// ページを開き終わったら（説明書に行き来したときも）、時計・電波に重なる分をもう一度渡す
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        (webView.superview as? WebHostView)?.pushInsets(force: true)
    }

    // MARK: - Webの画面からのお願い（window.webkit.messageHandlers.tengel）

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any], let name = body["name"] as? String else { return }
        let id = (body["id"] as? NSNumber)?.intValue ?? 0
        let payload = body["payload"]
        switch name {
        case "share":
            share(payload as? [String: Any] ?? [:], id: id)
        case "copy":
            UIPasteboard.general.string = payload as? String ?? ""
            reply(id, ok: true, value: true)
        case "backup":
            guard let text = (payload as? [String: Any])?["text"] as? String else {
                reply(id, ok: false, value: "中身がないよ")
                return
            }
            do {
                // アプリを開いて最初に書くときだけ、前のファイルを「ひとつ前」として残す
                try AppFiles.writeBackup(text, keepPrevious: !backupWritten)
                backupWritten = true
                reply(id, ok: true, value: true)
            } catch {
                reply(id, ok: false, value: "アプリの中に保存できなかったよ（\(error.localizedDescription)）")
            }
        case "store":
            // App Storeに出ている版を調べる（更新そのものは App Store がする）
            Task { [weak self] in
                let info = await StoreCheck.lookup()
                self?.reply(id, ok: true, value: info.dictionary)
            }
        case "ocr":
            // オッズ画面のスクショの文字を、この端末の中で読む（どこにも送らない）
            guard let image = (payload as? [String: Any])?["data"] as? String, !image.isEmpty else {
                reply(id, ok: true, value: ["ok": false, "error": "image_rejected"])
                return
            }
            // 第4.228版：opt＝読み直し（画像の 一部 だけ を 大きく して 読む。馬番 だけ 読めなかった 行）
            let options = ReadOptions((payload as? [String: Any])?["opt"] as? [String: Any])
            Task { [weak self] in
                let result = await TextReader.read(base64: image, options: options)
                self?.reply(id, ok: true, value: result.dictionary)
            }
        case "layout":
            // テスト用：時計・電波・ホームバーに重なる分の測り方
            reply(id, ok: true, value: (webView?.superview as? WebHostView)?.layoutInfo ?? [:])
        case "zoom":
            // 拡大を1倍にもどす・2本指の拡大を止める／もどす（{ reset, lock }）
            zoom(payload as? [String: Any] ?? [:])
            reply(id, ok: true, value: ["zoom": webView?.scrollView.zoomScale ?? 1, "pinch": webView?.scrollView.pinchGestureRecognizer?.isEnabled ?? true])
        case "marker":
            // キーチェーンの「しるし」（初回プレゼント・サブスクの取引の番号）。ユーザーのデータは入れない
            reply(id, ok: true, value: Markers.handle(payload as? [String: Any] ?? [:]))
        case "iap":
            // App内課金（商品・買う・復元・届いている取引・終わらせる）
            let p = payload as? [String: Any] ?? [:]
            Task { [weak self] in
                let r = await Store.shared.handle(p)
                self?.reply(id, ok: true, value: r)
            }
        case "notify":
            // 結果確認のお知らせ（許可・入れ直し・押されたお知らせ）。文はWebの画面が決める
            let p = payload as? [String: Any] ?? [:]
            Task { [weak self] in
                let r = await Notify.shared.handle(p)
                self?.reply(id, ok: true, value: r)
            }
        case "room":
            // 馬カードバトルの 部屋（第4.176版）：部屋を 作る・入る・手を 送る・やめる（Room.swift。近くの iPhone と 直接：サーバーなし）
            reply(id, ok: true, value: Room.shared.handle(payload as? [String: Any] ?? [:]))
        case "clock":
            // 時計の 番人（第4.191版）：いまの 時刻と、設定で かえられない 時計（電源を 入れてからの 時間・起動の 番号：Clock.swift）。どこにも 送らない
            // 第4.212版：net が ついて いたら、正しい 時刻を Apple の サーバーに 聞いて から 返す（電源を 入れ直した あと など：Clock.net）
            if let p = payload as? [String: Any], let n = p["net"] as? NSNumber, n.boolValue {
                Task { [weak self] in
                    let net = await Clock.net()
                    var value = Clock.sample()
                    value["net"] = net.dictionary
                    self?.reply(id, ok: true, value: value)
                }
            } else {
                reply(id, ok: true, value: Clock.sample())
            }
        case "statusBar":
            // 第4.224版：時計・電池の 帯の 色（"#RRGGBB"）と 字を 白に するか（light）。Webの 画面が 上の 帯の いちばん 上の 色を はかって 知らせる（kisekae.js）
            let p = payload as? [String: Any] ?? [:]
            let ok = StatusBarTint.shared.set(hex: p["color"] as? String ?? "", light: (p["light"] as? NSNumber)?.boolValue ?? true, window: webView?.window)
            reply(id, ok: ok, value: ok ? StatusBarTint.shared.info : "色の 形が ちがうよ")
        case "prompt":
            // 第4.235版：字を 打ちこむ 窓（iOS の 窓：UIAlertController ＋ 1行の 欄）。トレーニングセンターの 牧場の 看板の 名前（tc/tc_app.js）
            prompt(payload as? [String: Any] ?? [:], id: id)
        case "unseal":
            // 「データの更新」の ファイルを 開く（iOS に 入って いる 暗号＝Apple CryptoKit の AES-GCM。アプリは 自分の 暗号の 計算を 持たない：DataSeal.swift）
            if let text = DataSeal.open(payload as? [String: Any] ?? [:]) {
                reply(id, ok: true, value: text)
            } else {
                reply(id, ok: false, value: "データの形が違うよ")
            }
        #if DEBUG
        case "selftest":
            SelfTest.save(payload)
        #endif
        default:
            reply(id, ok: false, value: "知らないお願いだよ（\(name)）")
        }
    }

    private func reply(_ id: Int, ok: Bool, value: Any) {
        guard id > 0, let webView else { return }
        let js = "window.__nativeReply && window.__nativeReply(\(id), \(ok ? "true" : "false"), \(Self.jsonLiteral(value)))"
        webView.evaluateJavaScript(js, completionHandler: nil)
    }

    /// ファイルを共有シートで渡す（「ファイル」に保存・AirDrop・LINEなど）。渡したら true、閉じただけなら false を返す
    private func share(_ p: [String: Any], id: Int) {
        // 文字の ファイル（text）か、文字では ない ファイル（base64：第4.123版・Excel の ひな形）
        let bytes: Data? = (p["base64"] as? String).flatMap { Data(base64Encoded: $0) } ?? (p["text"] as? String).map { Data($0.utf8) }
        guard let webView, let data = bytes, !data.isEmpty else {
            reply(id, ok: false, value: "中身がないよ")
            return
        }
        let fileURL: URL
        do {
            fileURL = try AppFiles.shareFile(named: p["name"] as? String ?? "テンゲル.txt", data: data)
        } catch {
            reply(id, ok: false, value: "ファイルを作れなかったよ（\(error.localizedDescription)）")
            return
        }
        guard let presenter = Self.topViewController(from: webView) else {
            reply(id, ok: false, value: "画面が見つからなかったよ")
            return
        }
        let sheet = UIActivityViewController(activityItems: [fileURL], applicationActivities: nil)
        sheet.completionWithItemsHandler = { [weak self] _, completed, _, _ in
            guard let bridge = self else { return }
            Task { @MainActor in
                bridge.reply(id, ok: true, value: completed)
            }
        }
        if let pop = sheet.popoverPresentationController {   // iPadは吹き出しで出す
            pop.sourceView = webView
            pop.sourceRect = CGRect(x: webView.bounds.midX, y: webView.bounds.midY, width: 1, height: 1)
            pop.permittedArrowDirections = []
        }
        presenter.present(sheet, animated: true)
    }

    private static func topViewController(from view: UIView) -> UIViewController? {
        var top = view.window?.rootViewController
        while let next = top?.presentedViewController {
            top = next
        }
        return top
    }

    // MARK: - 字を 打ちこむ 窓（第4.235版）

    /// 第4.235版（まさちゃん 2026/11/28 08:41「牧場の名前変えようとしても入力するところが出てこないから改善して！」）：
    /// ・Web の 画面の 欄は、押した ときの 決まり（WKWebView）や 使い方（iPad の Swift Playgrounds・ペンシル）で キーボードが 出ない ことが ある
    ///   → iOS の 窓（UIAlertController ＋ 1行の 欄）で 打つ。欄は 窓が 出た とき 自分で キーボードを 出す（first responder）
    /// ・お願い：{ title, message, text（はじめの 字）, placeholder, max（字の 数）, empty（空の ときの 字）, ok, cancel, reset（空なら 出さない） }
    /// ・返事：{ ok: true, text } ／ { ok: false }（やめる）／ { ok: true, reset: true }（もとに もどす）／ { ok: false, busy: true }（もう 出て いる）
    /// ・max：Unicode の 字の 数（JavaScript の Array.from と 同じ 数え方）。こえたら「決める」を 押せない・窓の 字に「13/12文字（12文字までだよ）」
    /// ・キーボードの 決定（Return）＝「決める」（日本語の 変換中の 決定は 変換を 決める だけ：iOS が する）
    private var promptID = 0
    private var promptAlert: UIAlertController?
    private var promptOK: UIAlertAction?
    private var promptMax = 0
    private var promptNote = ""
    private var promptEmpty = ""
    #if DEBUG
    private var promptInfo: [String: Any] = [:]
    #endif

    private func prompt(_ p: [String: Any], id: Int) {
        guard let webView, let presenter = Self.topViewController(from: webView) else {
            reply(id, ok: false, value: "画面が見つからなかったよ")
            return
        }
        if promptID != 0 {
            if let shown = promptAlert, shown.presentingViewController != nil {   // もう 出て いる（すばやく 2回 押した）：前の 窓の まま
                reply(id, ok: true, value: ["ok": false, "busy": true])
                return
            }
            promptFinish(["ok": false], for: promptID)   // 前の 窓が もう ない（なにかで 消えた）：前の お願いは「やめる」に して 新しく 出す
        }
        let note = p["message"] as? String ?? ""
        let alert = UIAlertController(title: p["title"] as? String, message: note.isEmpty ? nil : note, preferredStyle: .alert)
        alert.addTextField(configurationHandler: nil)
        guard let field = alert.textFields?.first else {
            reply(id, ok: false, value: "欄を作れなかったよ")
            return
        }
        field.text = p["text"] as? String ?? ""
        field.placeholder = p["placeholder"] as? String
        field.clearButtonMode = .whileEditing
        field.returnKeyType = .done
        field.autocorrectionType = .no
        field.autocapitalizationType = .none
        field.spellCheckingType = .no
        field.delegate = self
        field.addTarget(self, action: #selector(promptChanged(_:)), for: .editingChanged)
        // ボタンの 返事は その 窓の お願い（id）に だけ（窓が 閉じる 間に 次の お願いが 来ても まざらない）
        let ok = UIAlertAction(title: p["ok"] as? String ?? "決める", style: .default) { [weak self] _ in
            guard let bridge = self else { return }
            Task { @MainActor in
                bridge.promptFinish(["ok": true, "text": bridge.promptAlert?.textFields?.first?.text ?? ""], for: id)
            }
        }
        alert.addAction(ok)
        if let reset = p["reset"] as? String, !reset.isEmpty {
            alert.addAction(UIAlertAction(title: reset, style: .default) { [weak self] _ in
                guard let bridge = self else { return }
                Task { @MainActor in
                    bridge.promptFinish(["ok": true, "reset": true], for: id)
                }
            })
        }
        alert.addAction(UIAlertAction(title: p["cancel"] as? String ?? "やめる", style: .cancel) { [weak self] _ in
            guard let bridge = self else { return }
            Task { @MainActor in
                bridge.promptFinish(["ok": false], for: id)
            }
        })
        alert.preferredAction = ok
        promptID = id
        promptAlert = alert
        promptOK = ok
        promptMax = max(0, (p["max"] as? NSNumber)?.intValue ?? 0)
        promptNote = note
        promptEmpty = p["empty"] as? String ?? ""
        promptCount(field)
        presenter.present(alert, animated: true) { [weak field] in
            guard let f = field else { return }
            Task { @MainActor in
                // 欄の 字を ぜんぶ 選ぶ（打つと 入れかわる：前の 名前を 1字ずつ 消さなくて いい）
                f.selectedTextRange = f.textRange(from: f.beginningOfDocument, to: f.endOfDocument)
            }
        }
        #if DEBUG
        // テスト（GitHub の Mac）：CI が 窓の スクショを 撮りおわる（ack の ファイル）まで 待って から、字を 入れて 決める
        if SelfTest.enabled, let auto = p["selftest"] as? [String: Any] {
            let ack = auto["ack"] as? String ?? "", answer = auto["text"] as? String ?? "", over = auto["over"] as? String ?? ""
            Task { [weak self] in
                let t0 = Date()
                if ack.isEmpty { try? await Task.sleep(nanoseconds: 1_500_000_000) }
                while !ack.isEmpty, SelfTest.file(named: ack) == nil, Date().timeIntervalSince(t0) < 70 {
                    try? await Task.sleep(nanoseconds: 300_000_000)
                }
                self?.promptAuto(answer: answer, over: over, waited: Date().timeIntervalSince(t0))
            }
        }
        #endif
    }

    @objc private func promptChanged(_ field: UITextField) {
        promptCount(field)
    }

    /// 字の 数を 窓に 出す・こえたら「決める」を 押せない
    private func promptCount(_ field: UITextField) {
        guard promptMax > 0, let alert = promptAlert else { return }
        let n = (field.text ?? "").unicodeScalars.count
        promptOK?.isEnabled = n <= promptMax
        let line = n > promptMax ? "\(n)/\(promptMax)文字（\(promptMax)文字までだよ）" : n > 0 ? "\(n)/\(promptMax)文字" : promptEmpty
        let text = [promptNote, line].filter { !$0.isEmpty }.joined(separator: "\n")
        alert.message = text.isEmpty ? nil : text
    }

    /// キーボードの 決定（Return）：窓を 閉じて「決める」と 同じ 返事
    fileprivate func promptReturn(_ field: UITextField) -> Bool {
        guard promptID != 0, let alert = promptAlert, field === alert.textFields?.first else { return true }
        guard promptOK?.isEnabled == true else { return false }
        #if DEBUG
        promptInfo["via"] = "return"
        #endif
        let text = field.text ?? ""
        alert.dismiss(animated: true)
        promptFinish(["ok": true, "text": text], for: promptID)
        return false
    }

    private func promptFinish(_ value: [String: Any], for id: Int) {
        guard id != 0, id == promptID else { return }   // もう 返事を した お願い・ほかの お願いの ボタンは 何も しない
        promptID = 0
        var v = value
        #if DEBUG
        if !promptInfo.isEmpty { v["auto"] = promptInfo }
        promptInfo = [:]
        #endif
        promptAlert = nil
        promptOK = nil
        reply(id, ok: true, value: v)
    }

    #if DEBUG
    /// テスト（GitHub の Mac）：窓が 出た ようすを 書きとめて、字を 入れて キーボードの 決定（Return と 同じ 道）
    private func promptAuto(answer: String, over: String, waited: Double) {
        guard promptID != 0, let alert = promptAlert, let field = alert.textFields?.first else { return }
        var info: [String: Any] = [
            "presented": alert.presentingViewController != nil,
            "first": field.isFirstResponder,
            "title": alert.title ?? "",
            "msg0": alert.message ?? "",
            "text0": field.text ?? "",
            "place": field.placeholder ?? "",
            "actions": alert.actions.map { $0.title ?? "" },
            "pref": alert.preferredAction?.title ?? "",
            "ok0": promptOK?.isEnabled ?? false,
            "done": field.returnKeyType == .done,
            "clear": field.clearButtonMode == .whileEditing,
            "waited": (waited * 10).rounded() / 10
        ]
        if let r = field.selectedTextRange {
            info["sel"] = [field.offset(from: field.beginningOfDocument, to: r.start), field.offset(from: r.start, to: r.end)]
        }
        if !over.isEmpty {
            field.text = over
            promptCount(field)
            info["overOK"] = promptOK?.isEnabled ?? true
            info["overMsg"] = alert.message ?? ""
        }
        field.text = answer
        promptCount(field)
        info["okOK"] = promptOK?.isEnabled ?? false
        info["msg"] = alert.message ?? ""
        promptInfo = info
        _ = promptReturn(field)
    }
    #endif
}

extension WebBridge: UITextFieldDelegate {
    /// 第4.235版：字を 打ちこむ 窓の 欄で キーボードの 決定（Return）＝「決める」
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        promptReturn(textField)
    }
}
