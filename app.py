import sys
import os
import tkinter as tk
from tkinter import messagebox

PROTOCOL = "fordapp"

def register_windows():
    import winreg
    exe_path = os.path.abspath(sys.argv[0])
    command = f'"{exe_path}" "%1"'
    key_path = rf"Software\Classes\{PROTOCOL}"
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"URL:{PROTOCOL} Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
            with winreg.CreateKey(key, r"shell\open\command") as command_key:
                winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        return True
    except Exception as e:
        messagebox.showerror("Registry Error", str(e))
        return False

def register_linux():
    exe_path = os.path.abspath(sys.argv[0])
    desktop_file = f"""[Desktop Entry]
Name=FordApp Handler
Exec={exe_path} %u
Type=Application
Terminal=false
MimeType=x-scheme-handler/{PROTOCOL};
"""
    desktop_path = os.path.expanduser(f"~/.local/share/applications/{PROTOCOL}-handler.desktop")
    
    try:
        os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
        with open(desktop_path, "w") as f:
            f.write(desktop_file)
        
        # Update MIME database
        os.system(f"xdg-mime default {PROTOCOL}-handler.desktop x-scheme-handler/{PROTOCOL}")
        os.system("update-desktop-database ~/.local/share/applications")
        return True
    except Exception as e:
        messagebox.showerror("Desktop Entry Error", str(e))
        return False

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width/2) - (width/2))
    y = int((screen_height/2) - (height/2))
    root.geometry(f'{width}x{height}+{x}+{y}')

def show_url_gui(url):
    root = tk.Tk()
    root.title(f"{PROTOCOL.capitalize()} Handler")
    center_window(root, 600, 150)

    tk.Label(root, text="Authorization URL Received:", font=("Arial", 10, "bold")).pack(pady=(15, 5))

    url_var = tk.StringVar(value=url)
    entry = tk.Entry(root, textvariable=url_var, state='readonly', width=75, font=("Consolas", 10))
    entry.pack(padx=20, pady=5)

    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(url)
        root.update()
        messagebox.showinfo("Success", "URL copied to clipboard!")

    tk.Button(root, text="Copy URL", command=copy_to_clipboard, width=20, bg="#0078D7", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
    root.mainloop()

def show_setup_gui():
    root = tk.Tk()
    root.title(f"{PROTOCOL.capitalize()} Setup")
    center_window(root, 400, 150)

    tk.Label(root, text="No URL provided. Running in Setup Mode.", font=("Arial", 10)).pack(pady=(15, 10))

    def do_register():
        if sys.platform == 'win32':
            if register_windows(): messagebox.showinfo("Success", "Registered successfully on Windows!")
        elif sys.platform == 'linux':
            if register_linux(): messagebox.showinfo("Success", "Registered successfully on Linux!")
        elif sys.platform == 'darwin':
            messagebox.showinfo("macOS", "macOS handles registration automatically via the .app bundle's Info.plist.\n\nJust ensure you are running the bundled .app file and not the raw python script.")

    tk.Button(root, text="Register Protocol Handler", command=do_register, width=25, font=("Arial", 10, "bold")).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    # Check for incoming URL in arguments
    received_url = None
    for arg in sys.argv[1:]:
        if arg.startswith(f"{PROTOCOL}://"):
            received_url = arg
            break
            
    if received_url:
        show_url_gui(received_url)
    else:
        show_setup_gui()