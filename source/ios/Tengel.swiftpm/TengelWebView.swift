import SwiftUI
import UIKit
import WebKit

/// アプリの中のWeb画面（テンゲルの画面そのもの）
struct TengelWebView: UIViewRepresentable {
    func makeCoordinator() -> WebBridge {
        WebBridge()
    }

    func makeUIView(context: Context) -> WKWebView {
        context.coordinator.makeWebView()
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}
}

/// Webの画面とアプリをつなぐ：共有シート（ファイルに保存）・コピー・自動バックアップ・外のリンク
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
        webView.load(URLRequest(url: AppSchemeHandler.startURL))
        return webView
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
        if navigationAction.targetFrame?.isMainFrame != false {
            UIApplication.shared.open(url, options: [:], completionHandler: nil)
            return .cancel
        }
        return .allow
    }

    /// Web画面の中身が落ちたら、開き直す（記録は保存場所に残っている）
    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        webView.reload()
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
