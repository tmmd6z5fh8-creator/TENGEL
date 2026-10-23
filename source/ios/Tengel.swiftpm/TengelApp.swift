import SwiftUI

// テンゲル（iPhone・iPadのアプリ）
// 画面はWeb版と同じもの（Resources/ に入っている）を、アプリの中のWeb画面で開く。
// 記録はアプリの中に保存して、アプリの中のファイルにも自動でバックアップする（AppFiles.swift）。
/// 起動のときにやること：結果確認のお知らせ（Notify.swift）の受け口を、アプリが起動し終わる前に入れる
/// （押されたお知らせでアプリが開いたときに、そのお知らせを受けとるため）
final class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        Notify.shared.install()
        return true
    }
}

@main
struct TengelApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        ZStack {
            // 上の時計・電池のところは、画面の地の色（ダークモードも）
            Color(uiColor: .tengelPage)
                .ignoresSafeArea()
            // 下のタブは、Webの画面が自分でホームバーをよけるので、下は端まで広げる
            TengelWebView()
                .ignoresSafeArea(edges: .bottom)
        }
    }
}

extension UIColor {
    /// Webの画面の地の色（--bg）と同じ色
    static var tengelPage: UIColor {
        UIColor { traits in
            traits.userInterfaceStyle == .dark
                ? UIColor(red: 12 / 255, green: 17 / 255, blue: 33 / 255, alpha: 1)
                : UIColor(red: 236 / 255, green: 238 / 255, blue: 243 / 255, alpha: 1)
        }
    }
}
