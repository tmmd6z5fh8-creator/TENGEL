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

/// オッズ画面のスクショの文字を、この端末の中で読む（Apple の Vision）。
/// 画像も読んだ文字も、どこにも送らない。料金もかからない。
/// 読めた文字と位置を Web の画面に渡して、表の形（単勝・複勝・3連単の人気順）は Web の画面が組み立てる。
enum TextReader {
    static func read(base64: String) async -> TextResult {
        await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                continuation.resume(returning: recognize(base64: base64))
            }
        }
    }

    private static func recognize(base64: String) -> TextResult {
        var result = TextResult()
        let t0 = Date()
        guard let data = Data(base64Encoded: base64, options: [.ignoreUnknownCharacters]),
              let source = CGImageSourceCreateWithData(data as CFData, nil),
              let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
            result.error = "image_rejected"
            return result
        }
        result.width = image.width
        result.height = image.height
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.usesLanguageCorrection = false   // 数字（オッズ・馬番）を言葉に直されないように
        request.minimumTextHeight = 0.006        // 表の小さい文字も読む（画像の高さに対する割合）
        let wanted = ["ja-JP", "en-US"]
        if let supported = try? request.supportedRecognitionLanguages(), !supported.isEmpty {
            let use = wanted.filter { supported.contains($0) }
            request.recognitionLanguages = use.isEmpty ? [supported[0]] : use
        } else {
            request.recognitionLanguages = wanted
        }
        let handler = VNImageRequestHandler(cgImage: image, orientation: orientation(of: source), options: [:])
        do {
            try handler.perform([request])
        } catch {
            result.error = error.localizedDescription
            return result
        }
        var lines: [TextLine] = []
        for observation in request.results ?? [] {
            guard let candidate = observation.topCandidates(1).first, !candidate.string.isEmpty else { continue }
            let box = observation.boundingBox   // 左下が原点
            lines.append(TextLine(text: candidate.string, x: box.minX, y: 1 - box.maxY, w: box.width, h: box.height, conf: Double(candidate.confidence)))
        }
        result.lines = lines
        result.ok = true
        result.ms = Int(Date().timeIntervalSince(t0) * 1000)
        return result
    }

    /// 画像の向き（スクショはふつう上向き。写真を選んだときのために EXIF も見る）
    private static func orientation(of source: CGImageSource) -> CGImagePropertyOrientation {
        guard let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
              let raw = props[kCGImagePropertyOrientation] as? UInt32,
              let value = CGImagePropertyOrientation(rawValue: raw) else { return .up }
        return value
    }
}
