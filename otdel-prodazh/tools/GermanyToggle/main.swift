import Cocoa

let SERVICE = "Wi-Fi"
let HOST = "127.0.0.1"
let PORT = 8118
let PROXY_SCRIPT = "/Users/tatiana/Desktop/Обучение ИИ/proekty/Мои проекты/otdel-prodazh/tools/local-proxy.py"
let PYTHON = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/python/bin/python3"

func run(_ path: String, _ args: [String]) -> String {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: path)
    p.arguments = args
    let pipe = Pipe()
    p.standardOutput = pipe
    p.standardError = pipe
    try? p.run()
    p.waitUntilExit()
    let d = pipe.fileHandleForReading.readDataToEndOfFile()
    return String(data: d, encoding: .utf8) ?? ""
}

func proxyEnabled() -> Bool {
    let out = run("/usr/sbin/networksetup", ["-getsecurewebproxy", SERVICE])
    return out.contains("Enabled: Yes")
}

func setProxy(_ on: Bool) {
    if on {
        _ = run("/usr/sbin/networksetup", ["-setwebproxy", SERVICE, HOST, "\(PORT)"])
        _ = run("/usr/sbin/networksetup", ["-setsecurewebproxy", SERVICE, HOST, "\(PORT)"])
        ensureLocalProxy()
    } else {
        _ = run("/usr/sbin/networksetup", ["-setwebproxystate", SERVICE, "off"])
        _ = run("/usr/sbin/networksetup", ["-setsecurewebproxystate", SERVICE, "off"])
    }
}

func ensureLocalProxy() {
    let check = run("/usr/bin/curl", ["-s", "-m", "2", "-x", "http://\(HOST):\(PORT)", "https://api.ipify.org"])
    if check.isEmpty {
        let p = Process()
        p.executableURL = URL(fileURLWithPath: PYTHON)
        p.arguments = [PROXY_SCRIPT]
        p.standardOutput = FileHandle.nullDevice
        p.standardError = FileHandle.nullDevice
        try? p.run()
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    var item: NSStatusItem!

    func applicationDidFinishLaunching(_ n: Notification) {
        item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        item.button?.title = proxyEnabled() ? "🇩🇪 ВКЛ" : "🇩🇪 выкл"
        rebuildMenu()
    }

    func rebuildMenu() {
        let menu = NSMenu()
        let state = proxyEnabled()
        let toggle = NSMenuItem(title: state ? "Выключить (для Авито)" : "Включить (Германия)",
                                action: #selector(toggleProxy), keyEquivalent: "t")
        toggle.target = self
        menu.addItem(toggle)
        menu.addItem(NSMenuItem.separator())
        let status = NSMenuItem(title: state ? "Сейчас: через Германию" : "Сейчас: напрямую",
                                action: nil, keyEquivalent: "")
        status.isEnabled = false
        menu.addItem(status)
        menu.addItem(NSMenuItem.separator())
        let quit = NSMenuItem(title: "Закрыть", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        menu.addItem(quit)
        item.menu = menu
    }

    @objc func toggleProxy() {
        setProxy(!proxyEnabled())
        item.button?.title = proxyEnabled() ? "🇩🇪 ВКЛ" : "🇩🇪 выкл"
        rebuildMenu()
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.accessory)
app.run()
