# Ford/Lincoln Protocol Handler

A cross-platform application that registers custom URI schemes (`fordapp://` and `lincolnapp://`) with the operating system. When a browser redirects to either URL, the OS launches this application, captures the URL, and presents a GUI to the user to copy the authorization token/URL.

---

## 🚀 Installation & Build

You can either download a pre-built binary for your platform or build it from source.

### Option 1: Download Pre-built Binaries
Download the executable for your platform and architecture from the [GitHub Releases](https://github.com/JosephBlock/fordapp-handler/releases) page:
*   **Windows**:
    - `FordAppHandler-windows-x86_64.exe` (64-bit Intel/AMD)
    - `FordAppHandler-windows-x86.exe` (32-bit Intel/AMD)
    - `FordAppHandler-windows-arm64.exe` (64-bit ARM)
*   **Linux**:
    - `FordAppHandler-linux-x86_64` (64-bit Intel/AMD)
    - `FordAppHandler-linux-x86` (32-bit Intel/AMD)
    - `FordAppHandler-linux-arm64` (64-bit ARM)
*   **macOS**:
    - `FordAppHandler-macos-arm64.zip` (extract to get `FordAppHandler-macos-arm64.app` for Apple Silicon)
    - `FordAppHandler-macos-x86_64.zip` (extract to get `FordAppHandler-macos-x86_64.app` for Intel Macs)

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

## 🛠️ Setup & Installation

To make the operating system recognize `fordapp://` and `lincolnapp://` URLs, you must install and register the handler.

### Windows

Choose one of the two options in the Setup Wizard:

#### Option 1: Permanent Installation (Recommended)
1. Run `FordAppHandler.exe` directly (without command-line arguments) to launch the Setup Wizard.
2. Click **Install & Register Protocol (Recommended)**.
3. Choose the installation folder:
   - **Recommended (Yes)**: Installs to User Programs (`%LOCALAPPDATA%\Programs\FordAppHandler`). This does **not** require administrator privileges.
   - **Custom (No)**: Allows you to select any folder on your machine.
4. The wizard copies the executable and registers the protocol pointing to that installed location.
5. Once completed, you can safely delete the downloaded copy from your Downloads folder.
6. Click **Test Protocol Handler (Run End-to-End Test)** to verify the system handler is working.

#### Option 2: Temporary / In-Place Registration
1. Run `FordAppHandler.exe` directly.
2. Click **Register Current File Location (Temporary - Removed on Close)**.
3. This registers the protocol pointing to the current folder and file location *without* copying any files.
4. Keep the Setup window open and click **Test Protocol Handler (Run End-to-End Test)** to test your setup.
5. Once you close the Setup window, the protocol registration will be automatically deleted from your system registry.

### Linux

Choose one of the two options in the Setup Wizard:

#### Option 1: Permanent Installation (Recommended)
1. Run `FordAppHandler` directly to launch the Setup Wizard.
2. Click **Install & Register Protocol (Recommended)**.
3. Choose the installation folder:
   - **Recommended (Yes)**: Installs to User Programs (`~/.local/share/FordAppHandler`).
   - **Custom (No)**: Allows you to select any folder.
4. The wizard copies the file and registers the desktop entry at `~/.local/share/applications/fordapp-handler.desktop`.
5. Once completed, you can safely delete the downloaded copy.
6. Click **Test Protocol Handler (Run End-to-End Test)** to verify the registration.

#### Option 2: Temporary / In-Place Registration
1. Run `FordAppHandler` directly.
2. Click **Register Current File Location (Temporary - Removed on Close)**.
3. Registers the protocol pointing to the current file location.
4. Click **Test Protocol Handler (Run End-to-End Test)** to test the registration.
5. Closing the Setup window automatically deletes the desktop entry and cleans up the registration.

### macOS
macOS registers URL handlers automatically using the `Info.plist` inside the application bundle.
1. Move `FordAppHandler.app` to your `/Applications` directory.
2. Double-click the application once to launch it. macOS will read the plist bundle config and register both the `fordapp://` and `lincolnapp://` schemes.

#### ⚠️ macOS Gatekeeper / Security Warning
Since the binary is unsigned, macOS may block the app or say it is damaged. You can resolve this by removing the quarantine flag. Open a terminal and run:
```bash
xattr -d com.apple.quarantine /Applications/FordAppHandler.app
```


### 🧹 Uninstallation

To completely remove the handler and clean up registrations:

#### Option A: Via the GUI (Windows & Linux)
1. Run the application (either the installed folder or the setup tool).
2. Click the **Uninstall / Clean Up** button.
3. If running from the installed folder, it will prompt to delete the application files and folder automatically upon exit.

#### Option B: Via Command Line (Windows & Linux)
Run the executable with the uninstall argument from your terminal:

**Windows**:
```cmd
FordAppHandler.exe --uninstall
# Silent mode (no prompts):
FordAppHandler.exe --uninstall --silent
```

**Linux**:
```bash
./FordAppHandler --uninstall
# Silent mode (no prompts):
./FordAppHandler --uninstall --silent
```

*Supported uninstall arguments: `--uninstall`, `-u`, `/uninstall`. Supported silent arguments: `--silent`, `-s`.*

#### Option C: macOS
To uninstall on macOS, delete the application bundle from your applications folder:
```bash
rm -rf /Applications/FordAppHandler.app
```

---


---

## 📱 How to Use

Once registered, clicking or navigating to any URL starting with `fordapp://` or `lincolnapp://` (for example: `fordapp://auth?token=123456` or `lincolnapp://auth?token=123456`) in your web browser will trigger the application:

1. The OS will automatically launch the **FordApp Handler** GUI.
2. The UI displays the received URL in a text field.
3. Click **Copy URL** to copy the URL to your clipboard for use elsewhere.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///d:/GIT/fordapp-handler/LICENSE) file for details.