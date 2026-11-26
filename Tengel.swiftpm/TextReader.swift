import CoreGraphics
import Foundation
import ImageIO
import Vision

/// 画像から読めた1行（位置は画像の左上を原点にした 0〜1）
struct TextLine: Sendable {
    var text: String
    var x: Double
    var y: Double
    var w: Double
    var h: Double
    var conf: Double

    var dictionary: [String: Any] {
        ["text": text, "x": x, "y": y, "w": w, "h": h, "conf": conf]
    }
}

/// 画像の文字を読んだ結果
struct TextResult: Sendable {
    var ok = false
    var error = ""
    var lines: [TextLine] = []
    var width = 0
    var height = 0
    var ms = 0

    var dictionary: [String: Any] {
        ["ok": ok, "error": error, "lines": lines.map { $0.dictionary }, "w": width, "h": height, "ms": ms]
    }
}

/// 読み直しの しかた（第4.228版）：画像の 一部（crop）だけを 大きく して（scale）読む。
/// 単勝の 表で 馬番 だけ 読めなかった 行（細い 数字の「11」など）を、Web の 画面が その 所 だけ もう一度 読む ときに 使う。
struct ReadOptions: Sendable {
    var crop: [Double]? = nil       // [x, y, w, h]（画像の 左上が 原点・0〜1）
    var scale: Double = 1           // 切り取った 所を 何倍に して 読むか（1〜4）
    var fast = false                // 速い 読み方（字を 1つずつ 見る）
    var languages: [String]? = nil  // 読む 言葉（なければ 日本語と 英語）

    init(_ d: [String: Any]? = nil) {
        guard let d else { return }
        if let c = d["crop"] as? [Any] {
            let v = c.compactMap { ($0 as? NSNumber)?.doubleValue }
            if v.count == 4, v.allSatisfy({ $0.isFinite }) { crop = v }
        }
        if let s = (d["scale"] as? NSNumber)?.doubleValue, s.isFinite { scale = min(4, max(1, s)) }
        fast = (d["fast"] as? Bool) ?? false
        if let l = d["langs"] as? [String], !l.isEmpty { languages = l }
    }
}

/// オッズ画面のスクショの文字を、この端末の中で読む（Apple の Vision）。
/// 画像も読んだ文字も、どこにも送らない。料金もかからない。
/// 読めた文字と位置を Web の画面に渡して、表の形（単勝・複勝・3連単の人気順）は Web の画面が組み立てる。
enum TextReader {
    static func read(base64: String, options: ReadOptions = ReadOptions()) async -> TextResult {
        await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                continuation.resume(returning: recognize(base64: base64, options: options))
            }
        }
    }

    private static func recognize(base64: String, options: ReadOptions) -> TextResult {
        var result = TextResult()
        let t0 = Date()
        guard let data = Data(base64Encoded: base64, options: [.ignoreUnknownCharacters]),
              let source = CGImageSourceCreateWithData(data as CFData, nil),
              let full = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
            result.error = "image_rejected"
            return result
        }
        result.width = full.width
        result.height = full.height
        let W = Double(full.width), H = Double(full.height)
        var image = full
        let orient = orientation(of: source)
        var region = CGRect(x: 0, y: 0, width: CGFloat(W), height: CGFloat(H))   // 読む 所（画素・左上が 原点）
        if let c = options.crop {
            // 読み直し（第4.228版）：Web の 画面から 来る 画像は 上向きの JPEG（toJpeg で 描き直した もの）。向きの ある 画像は 切り取らない
            guard orient == .up else {
                result.error = "crop_unsupported"
                return result
            }
            let r = CGRect(x: CGFloat(c[0] * W), y: CGFloat(c[1] * H), width: CGFloat(c[2] * W), height: CGFloat(c[3] * H)).integral.intersection(region)
            guard !r.isNull, r.width >= 4, r.height >= 4, let part = full.cropping(to: r) else {
                result.error = "crop_rejected"
                return result
            }
            region = r
            image = options.scale > 1 ? (scaled(part, by: options.scale) ?? part) : part
        }
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = options.fast ? .fast : .accurate
        request.usesLanguageCorrection = false   // 数字（オッズ・馬番）を言葉に直されないように
        request.minimumTextHeight = options.crop == nil ? 0.006 : 0   // 表の小さい文字も読む（画像の高さに対する割合）。切り取った 所は 大きさで しぼらない
        let wanted = options.languages ?? ["ja-JP", "en-US"]
        if let supported = try? request.supportedRecognitionLanguages(), !supported.isEmpty {
            let use = wanted.filter { supported.contains($0) }
            request.recognitionLanguages = use.isEmpty ? [supported[0]] : use
        } else {
            request.recognitionLanguages = wanted
        }
        let handler = VNImageRequestHandler(cgImage: image, orientation: orient, options: [:])
        do {
            try handler.perform([request])
        } catch {
            result.error = error.localizedDescription
            return result
        }
        var lines: [TextLine] = []
        let rx = Double(region.minX), ry = Double(region.minY), rw = Double(region.width), rh = Double(region.height)
        for observation in request.results ?? [] {
            guard let candidate = observation.topCandidates(1).first, !candidate.string.isEmpty else { continue }
            let box = observation.boundingBox   // 左下が原点（読んだ 所の 中の 位置）→ 画像 全体の 位置（左上が 原点）に
            let bx = Double(box.minX), by = Double(box.maxY), bw = Double(box.width), bh = Double(box.height)
            lines.append(TextLine(text: candidate.string, x: (rx + bx * rw) / W, y: (ry + (1 - by) * rh) / H, w: bw * rw / W, h: bh * rh / H,
                                  conf: Double(candidate.confidence)))
        }
        result.lines = lines
        result.ok = true
        result.ms = Int(Date().timeIntervalSince(t0) * 1000)
        return result
    }

    /// 切り取った 所を 大きく する（細い 字を 読みやすく）
    private static func scaled(_ img: CGImage, by s: Double) -> CGImage? {
        let w = Int((Double(img.width) * s).rounded()), h = Int((Double(img.height) * s).rounded())
        guard w > 0, h > 0,
              let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                                  space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
        ctx.interpolationQuality = .high
        ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
        return ctx.makeImage()
    }

    /// 画像の向き（スクショはふつう上向き。写真を選んだときのために EXIF も見る）
    private static func orientation(of source: CGImageSource) -> CGImagePropertyOrientation {
        guard let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
              let raw = props[kCGImagePropertyOrientation] as? UInt32,
              let value = CGImagePropertyOrientation(rawValue: raw) else { return .up }
        return value
    }
}
