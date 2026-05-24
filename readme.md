# FordApp Protocol Handler

A cross-platform application that registers a custom URI scheme (`fordapp://`) with the operating system. When a browser redirects to `fordapp://`, the OS launches this application, captures the URL, and presents a GUI to the user to copy the authorization token/URL.

---

## 🚀 Installation & Build

You can either download a pre-built binary for your platform or build it from source.

### Option 1: Download Pre-built Binaries
Download the executable for your platform from the [GitHub Releases](https://github.com/your-username/fordapp-handler/releases) page:
*   **Windows**: `FordAppHandler-windows.exe`
*   **Linux**: `FordAppHandler-linux`
*   **macOS**: `FordAppHandler-macos.zip` (extract to get `FordAppHandler.app`)

### Option 2: Build From Source
If you prefer to build the executable yourself:
1. Install Python 3.
2. Install build dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Compile with PyInstaller:
   ```bash
   pyinstaller fordapp.spec
   ```
   The build output will be placed in the `dist/` directory.

---

## 🛠️ Setup (Registering the Protocol Handler)

To make the operating system recognize `fordapp://` URLs, you must register the application handler.

### Windows
1. Run `FordAppHandler-windows.exe` (or the compiled version) directly (without any command-line arguments).
2. The application will open in **Setup Mode**.
3. Click the **Register Protocol Handler** button.
4. A registry key will be created under `HKEY_CURRENT_USER\Software\Classes\fordapp`.

### Linux
1. Run `FordAppHandler-linux` (or the compiled version) directly.
2. The application will open in **Setup Mode**.
3. Click the **Register Protocol Handler** button.
4. A desktop entry will be generated at `~/.local/share/applications/fordapp-handler.desktop` and registered as the default handler for the `x-scheme-handler/fordapp` MIME type.

### macOS
macOS registers URL handlers automatically using the `Info.plist` inside the application bundle.
1. Move `FordAppHandler.app` to your `/Applications` directory.
2. Double-click the application once to launch it. macOS will read the plist bundle config and register the `fordapp://` scheme.

#### ⚠️ macOS Gatekeeper / Security Warning
Since the binary is unsigned, macOS may block the app or say it is damaged. You can resolve this by removing the quarantine flag. Open a terminal and run:
```bash
xattr -d com.apple.quarantine /Applications/FordAppHandler.app
```

---

## 📱 How to Use

Once registered, clicking or navigating to any URL starting with `fordapp://` (for example: `fordapp://auth?token=123456`) in your web browser will trigger the application:

1. The OS will automatically launch the **FordApp Handler** GUI.
2. The UI displays the received URL in a text field.
3. Click **Copy URL** to copy the URL to your clipboard for use elsewhere.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///d:/GIT/fordapp-handler/LICENSE) file for details.