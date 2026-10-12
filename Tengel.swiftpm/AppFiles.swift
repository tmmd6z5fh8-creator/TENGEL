import Foundation
import WebKit

/// アプリの中の画面を tengel://localhost/ で出す。
/// Web版と同じように保存場所（IndexedDB・localStorage）が使えて、電波がなくても開ける。
final class AppSchemeHandler: NSObject, WKURLSchemeHandler {
    static let scheme = "tengel"
    static let startURL = URL(string: "tengel://localhost/index.html")!

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url else {
            urlSchemeTask.didFailWithError(URLError(.badURL))
            return
        }
        var path = url.path
        if path.isEmpty || path == "/" {
            path = "/index.html"
        }
        let name: String
        let body: Data?
        if path == "/__native/autobackup.json" {
            name = "autobackup.json"
            body = AppFiles.readBackup()
        } else {
            name = (path as NSString).lastPathComponent
            body = AppFiles.webFile(named: name).flatMap { try? Data(contentsOf: $0) }
        }
        if let body {
            respond(urlSchemeTask, url: url, status: 200, type: AppFiles.mimeType(for: name), body: body)
        } else {
            respond(urlSchemeTask, url: url, status: 404, type: "text/plain; charset=utf-8", body: Data("not found".utf8))
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

    private func respond(_ task: WKURLSchemeTask, url: URL, status: Int, type: String, body: Data) {
        let headers = ["Content-Type": type, "Content-Length": String(body.count), "Cache-Control": "no-store"]
        guard let response = HTTPURLResponse(url: url, statusCode: status, httpVersion: "HTTP/1.1", headerFields: headers) else {
            task.didFailWithError(URLError(.cannotParseResponse))
            return
        }
        task.didReceive(response)
        task.didReceive(body)
        task.didFinish()
    }
}

/// アプリの中のファイル：画面（Resources/）・自動バックアップ・共有するファイル
enum AppFiles {
    // MARK: 画面のファイル（Resources/ の中。名前だけで探す）

    /// 画面のファイルがある場所（アプリの中、またはアプリの中の .bundle）
    static let webRoots: [URL] = {
        let main = Bundle.main.bundleURL
        var roots = [main, main.appendingPathComponent("Resources", isDirectory: true)]
        if let items = try? FileManager.default.contentsOfDirectory(at: main, includingPropertiesForKeys: nil) {
            for item in items where item.pathExtension == "bundle" {
                roots.append(item)
                roots.append(item.appendingPathComponent("Resources", isDirectory: true))
            }
        }
        return roots
    }()

    static func webFile(named name: String) -> URL? {
        guard !name.isEmpty, !name.hasPrefix("."), !name.contains("/") else { return nil }
        for root in webRoots {
            let url = root.appendingPathComponent(name)
            if FileManager.default.fileExists(atPath: url.path) {
                return url
            }
        }
        return nil
    }

    static func mimeType(for name: String) -> String {
        switch (name as NSString).pathExtension.lowercased() {
        case "html", "htm": return "text/html; charset=utf-8"
        case "js", "mjs": return "text/javascript; charset=utf-8"
        case "css": return "text/css; charset=utf-8"
        case "json": return "application/json; charset=utf-8"
        case "svg": return "image/svg+xml"
        case "png": return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "webp": return "image/webp"
        case "gif": return "image/gif"
        case "mp4": return "video/mp4"
        case "woff2": return "font/woff2"
        case "woff": return "font/woff"
        case "ttf": return "font/ttf"
        default: return "application/octet-stream"
        }
    }

    // MARK: 自動バックアップ（記録・買い目・マザーデータ。APIキーは入らない）

    /// アプリの中の「Application Support」（iPhone・iPadのバックアップにも入る場所）
    static var supportDirectory: URL {
        let url = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        return url
    }

    static var backupURL: URL { supportDirectory.appendingPathComponent("tengel-autobackup.json") }
    static var previousBackupURL: URL { supportDirectory.appendingPathComponent("tengel-autobackup-prev.json") }

    static func writeBackup(_ text: String, keepPrevious: Bool) throws {
        let fm = FileManager.default
        let url = backupURL
        if keepPrevious, fm.fileExists(atPath: url.path) {
            let prev = previousBackupURL
            try? fm.removeItem(at: prev)
            try? fm.copyItem(at: url, to: prev)
        }
        try Data(text.utf8).write(to: url, options: .atomic)
    }

    static func readBackup() -> Data? {
        try? Data(contentsOf: backupURL)
    }

    // MARK: 共有シートで渡すファイル（一時的な場所）

    private static var shareRoot: URL {
        FileManager.default.temporaryDirectory.appendingPathComponent("share", isDirectory: true)
    }

    static func clearSharedFiles() {
        try? FileManager.default.removeItem(at: shareRoot)
    }

    static func shareFile(named rawName: String, text: String) throws -> URL {
        let dir = shareRoot.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        var name = rawName.components(separatedBy: CharacterSet(charactersIn: "/\\:")).joined(separator: "_")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if name.isEmpty || name.hasPrefix(".") {
            name = "テンゲル.txt"
        }
        let url = dir.appendingPathComponent(name)
        try Data(text.utf8).write(to: url, options: .atomic)
        return url
    }
}

#if DEBUG
/// 自動テスト（GitHubのMacのシミュレーターで使う）。起動するときに -tengelSelfTest をつけたときだけ動く
enum SelfTest {
    static var enabled: Bool { ProcessInfo.processInfo.arguments.contains("-tengelSelfTest") }

    static var documents: URL { FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0] }

    @MainActor
    static func install(on config: WKWebViewConfiguration) {
        guard enabled,
              let js = try? String(contentsOf: documents.appendingPathComponent("selftest.js"), encoding: .utf8) else { return }
        config.userContentController.addUserScript(WKUserScript(source: js, injectionTime: .atDocumentStart, forMainFrameOnly: true))
    }

    static func save(_ payload: Any?) {
        guard enabled, let p = payload as? [String: Any], let file = p["file"] as? String, let text = p["text"] as? String,
              !file.isEmpty, !file.contains("/"), !file.hasPrefix(".") else { return }
        try? Data(text.utf8).write(to: documents.appendingPathComponent(file), options: .atomic)
    }
}
#endif
