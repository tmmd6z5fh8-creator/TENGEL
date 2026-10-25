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

    override func layoutSubviews() {
        super.layoutSubviews()
        webView.frame = bounds
        pushInsets()
    }

    override func safeAreaInsetsDidChange() {
        super.safeAreaInsetsDidChange()
        pushInsets()
    }

    override func didMoveToWindow() {
        super.didMoveToWindow()
        pushInsets()
    }

    /// 上と下の、重なる分（pt）。上＝時計・電波の帯のうち、この画面にかかっている高さ。下＝ホームバーのうち、この画面にかかっている高さ
    var insets: (top: Int, bottom: Int) {
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
                "height": bounds.height, "windowHeight": w?.bounds.height ?? -1]
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
        // キーボードが 出た／しまった を Webの 画面に 知らせる（数字の 欄で キーボードが 出なければ アプリの 中の テンキーを 出す：第4.62版）
        for (name, open) in [(UIResponder.keyboardWillShowNotification, true), (UIResponder.keyboardWillHideNotification, false)] {
            NotificationCenter.default.addObserver(forName: name, object: nil, queue: .main) { [weak self] n in
                let h = (n.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect)?.height ?? 0
                Task { @MainActor in self?.event("keyboard", ["open": open, "height": Double(h)]) }
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
            Task { [weak self] in
                let result = await TextReader.read(base64: image)
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
        guard let webView, let text = p["text"] as? String else {
            reply(id, ok: false, value: "中身がないよ")
            return
        }
        let fileURL: URL
        do {
            fileURL = try AppFiles.shareFile(named: p["name"] as? String ?? "テンゲル.txt", text: text)
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
}
