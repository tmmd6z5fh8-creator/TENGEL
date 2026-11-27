import AVFoundation
import ObjectiveC
import SwiftUI
import UIKit

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

/// 第4.233版：音の 出口（AVAudioSession）を ambient（消音スイッチなら 鳴らさない・ほかの アプリの 音楽は 止めずに 重ねる）で 起こし直す。
/// アプリが 前に もどった とき・ほかの アプリの 音で とぎれた のが おわった とき に 呼ぶ（TengelWebView.swift）。起こせなくても 何も しない
enum AudioWake {
    static func activate() {
        let s = AVAudioSession.sharedInstance()
        try? s.setCategory(.ambient, mode: .default, options: [.mixWithOthers])
        try? s.setActive(true)
    }
}

@main
struct TengelApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    var body: some Scene {
        WindowGroup {
            ContentView(tint: StatusBarTint.shared)
        }
    }
}

struct ContentView: View {
    @ObservedObject var tint: StatusBarTint
    var body: some View {
        ZStack {
            // 上の時計・電池のところ：すぐ 下の 上の 帯（header.top）の いちばん 上の 色（着せ替えの テーマ・ダークモードで かわる：第4.224版 StatusBarTint）。
            // 前は 画面の 地の 色（.tengelPage）。Webの 画面が 下に しきつめる ので、見えるのは 時計・電池の 帯 だけ
            Color(uiColor: tint.color)
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

    /// 上の 帯（header.top）の 色＝Webの 画面の --night（いつもの テーマ・ダークモードも）。はじめて 開いて Webの 画面が 色を 知らせる までの 時計・電池の 帯の 色（第4.224版）
    static var tengelNight: UIColor {
        UIColor { traits in
            traits.userInterfaceStyle == .dark
                ? UIColor(red: 9 / 255, green: 14 / 255, blue: 28 / 255, alpha: 1)
                : UIColor(red: 22 / 255, green: 32 / 255, blue: 61 / 255, alpha: 1)
        }
    }

    /// "#RRGGBB" の 色（ちがう 形なら nil）
    convenience init?(tengelHex text: String) {
        var s = text.trimmingCharacters(in: .whitespaces)
        if s.hasPrefix("#") { s.removeFirst() }
        guard s.count == 6, s.allSatisfy({ $0.isHexDigit }), let v = UInt32(s, radix: 16) else { return nil }
        self.init(red: CGFloat((v >> 16) & 0xFF) / 255, green: CGFloat((v >> 8) & 0xFF) / 255, blue: CGFloat(v & 0xFF) / 255, alpha: 1)
    }
}

/// 時計・電池の 帯（ステータスバー）の 色と 字の 白／黒（第4.224版：まさちゃん 2026/11/26「青四角のところ色壁紙の色と合わせることって可能？」）
/// ・色と 字の 白／黒は Webの 画面（kisekae.js）が きめて 知らせる（上の 帯の いちばん 上の 色・着せ替えの テーマや ダークモードが かわる たびに）
/// ・次に 開いた ときも すぐ 同じ 色に なる ように 端末に 覚える（はじめて 開く ときは いつもの テーマの 上の 帯の 色・白い 字）
@MainActor
final class StatusBarTint: ObservableObject {
    static let shared = StatusBarTint()
    @Published private(set) var color: UIColor
    private(set) var hex: String
    private(set) var light: Bool
    private static let colorKey = "statusBarColor", lightKey = "statusBarLight"

    private init() {
        let d = UserDefaults.standard
        if let h = d.string(forKey: Self.colorKey), let c = UIColor(tengelHex: h) {
            hex = h
            color = c
            light = d.object(forKey: Self.lightKey) as? Bool ?? true
        } else {
            hex = ""
            color = .tengelNight
            light = true
        }
        StatusBarStyle.current = light ? .lightContent : .darkContent
    }

    /// Webの 画面から：色（"#RRGGBB"）と 字を 白に するか。形が ちがう ときは 何も かえない（false）
    func set(hex text: String, light white: Bool, window: UIWindow?) -> Bool {
        guard let c = UIColor(tengelHex: text) else { return false }
        let h = text.trimmingCharacters(in: .whitespaces).uppercased()
        let d = UserDefaults.standard
        if h != hex {
            hex = h
            color = c
            d.set(h, forKey: Self.colorKey)
        }
        if white != light {
            light = white
            d.set(white, forKey: Self.lightKey)
        }
        StatusBarStyle.current = white ? .lightContent : .darkContent
        StatusBarStyle.apply(in: window)
        return true
    }

    /// テスト用（CI）：いまの 色と 字の 白／黒
    var info: [String: Any] { ["color": hex, "light": light] }
}

/// 時計・電池の 字の 白／黒。SwiftUI には この 字の 色を きめる 方法が ない ので、いちばん 外側の 入れ物（SwiftUI の UIHostingController）の
/// preferredStatusBarStyle を、current を 返す ものに 入れかえる（1つの 型に 1回・Objective-C の しくみ：公開されて いる 関数 だけ）。
/// 入れかえられなかった ときは 今までどおり（iPhone の ライト／ダークに 合わせた 字）
enum StatusBarStyle {
    // UIKit が 字の 色を 聞く のも ここを かえる のも メインの スレッド だけ（Swift 6 の きまりでは「メイン だけで 使う」と 書く 必要が ある：nonisolated(unsafe)）
    nonisolated(unsafe) static var current: UIStatusBarStyle = .lightContent
    nonisolated(unsafe) private static var patched: [ObjectIdentifier] = []

    @MainActor
    static func apply(in window: UIWindow?) {
        guard let root = window?.rootViewController else { return }
        if let cls = object_getClass(root) { patch(cls) }
        root.setNeedsStatusBarAppearanceUpdate()
    }

    private static func patch(_ cls: AnyClass) {
        let id = ObjectIdentifier(cls)
        if patched.contains(id) { return }
        patched.append(id)
        let sel = #selector(getter: UIViewController.preferredStatusBarStyle)
        guard let method = class_getInstanceMethod(cls, sel) else { return }
        let block: @convention(block) (AnyObject) -> Int = { _ in StatusBarStyle.current.rawValue }
        let imp = imp_implementationWithBlock(block)
        let types = method_getTypeEncoding(method)
        if !class_addMethod(cls, sel, imp, types) {
            class_replaceMethod(cls, sel, imp, types)
        }
    }
}
