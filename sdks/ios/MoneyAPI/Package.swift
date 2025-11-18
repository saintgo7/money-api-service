// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "MoneyAPI",
    platforms: [
        .iOS(.v13),
        .macOS(.v10_15),
        .tvOS(.v13),
        .watchOS(.v6)
    ],
    products: [
        .library(
            name: "MoneyAPI",
            targets: ["MoneyAPI"]
        )
    ],
    dependencies: [],
    targets: [
        .target(
            name: "MoneyAPI",
            dependencies: []
        ),
        .testTarget(
            name: "MoneyAPITests",
            dependencies: ["MoneyAPI"]
        )
    ]
)
