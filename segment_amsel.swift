import Foundation
import Vision
import CoreImage
import CoreGraphics
import ImageIO

let inputPath = "demo-expert/assets/dr-amsel.jpg"
let outputPath = "demo-expert/assets/dr-amsel-isolated.png"

guard let inputURL = URL(string: "file://" + FileManager.default.currentDirectoryPath + "/" + inputPath),
      let inputCI = CIImage(contentsOf: inputURL) else {
    print("Failed to load input image")
    exit(1)
}

let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8

let handler = VNImageRequestHandler(ciImage: inputCI, options: [:])
do {
    try handler.perform([request])
} catch {
    print("Error performing segmentation: \(error)")
    exit(1)
}

guard let result = request.results?.first else {
    print("No segmentation result")
    exit(1)
}

let maskPixelBuffer = result.pixelBuffer
let maskCI = CIImage(cvPixelBuffer: maskPixelBuffer)

// Scale mask up to original image size
let scaleX = inputCI.extent.width / maskCI.extent.width
let scaleY = inputCI.extent.height / maskCI.extent.height
let scaledMask = maskCI.transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))

// Blend input image with transparent background using the mask
let filter = CIFilter(name: "CIBlendWithMask")!
filter.setValue(inputCI, forKey: kCIInputImageKey)
filter.setValue(CIImage.empty(), forKey: kCIInputBackgroundImageKey)
filter.setValue(scaledMask, forKey: kCIInputMaskImageKey)

guard let outputCI = filter.outputImage else {
    print("Failed to blend image with mask")
    exit(1)
}

let context = CIContext()
guard let outputCG = context.createCGImage(outputCI, from: inputCI.extent) else {
    print("Failed to create CGImage")
    exit(1)
}

let outputURL = URL(fileURLWithPath: outputPath)
guard let destination = CGImageDestinationCreateWithURL(outputURL as CFURL, "public.png" as CFString, 1, nil) else {
    print("Failed to create CGImageDestination")
    exit(1)
}

CGImageDestinationAddImage(destination, outputCG, nil)
if CGImageDestinationFinalize(destination) {
    print("Successfully saved isolated portrait to \(outputPath)")
} else {
    print("Failed to write PNG")
    exit(1)
}
