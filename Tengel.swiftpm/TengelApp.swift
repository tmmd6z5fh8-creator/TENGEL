import AVFoundation
import SwiftUI

// テンゲル（iPhone・iPadのアプリ）
// 画面はWeb版と同じもの（Resources/ に入っている）を、アプリの中のWeb画面で開く。
// 記録はアプリの中に保存して、アプリの中のファイルにも自動でバックアップする（AppFiles.swift）。
/// 起動のときにやること：結果確認のお知らせ（Notify.swift）の受け口を、アプリが起動し終わる前に入れる
/// （押されたお知らせでアプリが開いたときに、そのお知らせを受けとるため）
/// ・的中ボタンの効果音（第3弾）：消音スイッチ（マナーモード）なら鳴らさない・ほかのアプリの音楽は止めずに重ねる（AVAudioSession の ambient）
final class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        Notify.shared.install()
        try? AVAudioSession.sharedInstance().setCategory(.ambient, mode: .default, options: [.mixWithOthers])
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
            // iPad など 広い 画面：まわりを 黒に（アプリは まん中に iPhone の 大きさで 出る：WebHostView）。iPhone では 何も 描かない
            WideBackdrop()
            // 下のタブは、Webの画面が自分でホームバーをよけるので、下は端まで広げる
            TengelWebView()
                .ignoresSafeArea(edges: .bottom)
        }
    }
}

/// iPad など 広い 画面（幅 480pt より 広い）の まわりの 色（黒）。時計・電池の 帯も かくす（黒の 上では 読めない ため）。
/// iPhone・iPad の 細い 窓では すき通し＝何も かえない（第4.156版：PhoneFrame）
struct WideBackdrop: View {
    var body: some View {
        GeometryReader { geo in
            let wide = PhoneFrame.isWide(geo.size.width)
            Color.black
                .opacity(wide ? 1 : 0)
                .ignoresSafeArea()
                .statusBarHidden(wide)
        }
        .allowsHitTesting(false)
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
