import sys
import os
import re
import shutil
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox, filedialog

PROTOCOL = "fordapp"
TEMP_REGISTRATION = False

def register_windows(exe_path=None):
    if exe_path is None:
        exe_path = os.path.abspath(sys.argv[0])
    import winreg
    command = f'"{exe_path}" "%1"'
    key_path = rf"Software\Classes\{PROTOCOL}"
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"URL:{PROTOCOL} Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
            with winreg.CreateKey(key, r"shell\\open\\command") as command_key:
                winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        return True
    except Exception as e:
        messagebox.showerror("Registry Error", str(e))
        return False

def unregister_windows(silent=False):
    import winreg
    key_path = rf"Software\Classes\{PROTOCOL}"
    
    def delete_key_recursive(key, path):
        try:
            with winreg.OpenKey(key, path, 0, winreg.KEY_ALL_ACCESS) as subkey:
                info = winreg.QueryInfoKey(subkey)
                for _ in range(info[0]):
                    sub_name = winreg.EnumKey(subkey, 0)
                    delete_key_recursive(subkey, sub_name)
            winreg.DeleteKey(key, path)
        except FileNotFoundError:
            pass
            
    try:
        delete_key_recursive(winreg.HKEY_CURRENT_USER, key_path)
        return True
    except Exception as e:
        if not silent:
            messagebox.showerror("Uninstall Error", f"Failed to remove registry keys: {str(e)}")
        return False

def register_linux(exe_path=None):
    if exe_path is None:
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

def unregister_linux(silent=False):
    desktop_path = os.path.expanduser(f"~/.local/share/applications/{PROTOCOL}-handler.desktop")
    try:
        if os.path.exists(desktop_path):
            os.remove(desktop_path)
        os.system("update-desktop-database ~/.local/share/applications")
        return True
    except Exception as e:
        if not silent:
            messagebox.showerror("Uninstall Error", f"Failed to remove desktop entry: {str(e)}")
        return False

def register_mac():
    current_exe = os.path.abspath(sys.argv[0])
    if ".app" in current_exe:
        app_path = current_exe
        while app_path and not app_path.endswith(".app"):
            app_path = os.path.dirname(app_path)
        if app_path and os.path.exists(app_path):
            dest_app = os.path.join('/Applications', os.path.basename(app_path))
            if os.path.abspath(app_path) == os.path.abspath(dest_app):
                return True
            try:
                if os.path.exists(dest_app):
                    shutil.rmtree(dest_app)
                shutil.copytree(app_path, dest_app)
                os.system(f"open {dest_app}")
                return True
            except Exception as e:
                messagebox.showerror("Installation Error", f"Failed to copy app to /Applications: {str(e)}")
                return False
    messagebox.showinfo("macOS Registration", "macOS registers URL protocols automatically via the .app bundle.\n\nEnsure you are running the bundled FordAppHandler.app rather than raw python.")
    return True

def unregister_mac(silent=False):
    app_path = '/Applications/FordAppHandler.app'
    try:
        if os.path.exists(app_path):
            shutil.rmtree(app_path)
        return True
    except Exception as e:
        if not silent:
            messagebox.showerror("Uninstall Error", f"Failed to remove app from /Applications: {str(e)}")
        return False

def check_registration_status():
    """Returns (is_registered, registered_path)"""
    if sys.platform == 'win32':
        import winreg
        key_path = rf"Software\Classes\{PROTOCOL}\shell\open\command"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                val = winreg.QueryValue(key, "")
                match = re.match(r'"([^"]+)"', val)
                if match:
                    path = match.group(1)
                else:
                    path = val.split()[0] if val else ""
                
                if os.path.exists(path):
                    return True, path
                else:
                    return False, f"Broken link (points to non-existent {path})"
        except FileNotFoundError:
            return False, "Not registered"
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    elif sys.platform == 'linux':
        desktop_path = os.path.expanduser(f"~/.local/share/applications/{PROTOCOL}-handler.desktop")
        if os.path.exists(desktop_path):
            try:
                with open(desktop_path, 'r') as f:
                    for line in f:
                        if line.startswith("Exec="):
                            parts = line.split("Exec=")
                            if len(parts) > 1:
                                path = parts[1].split()[0]
                                if os.path.exists(path):
                                    return True, path
                                else:
                                    return False, f"Broken link (points to non-existent {path})"
            except Exception:
                pass
            return True, desktop_path
        return False, "Not registered"
        
    elif sys.platform == 'darwin':
        app_path = '/Applications/FordAppHandler.app'
        if os.path.exists(app_path):
            return True, app_path
        return False, "Not registered in /Applications"
        
    return False, "Unsupported platform"

def get_default_install_path():
    if sys.platform == 'win32':
        return os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~/AppData/Local')), 'Programs', 'FordAppHandler')
    elif sys.platform == 'linux':
        return os.path.expanduser('~/.local/share/FordAppHandler')
    elif sys.platform == 'darwin':
        return '/Applications'
    return None

def trigger_self_delete(installed_dir):
    is_frozen = getattr(sys, 'frozen', False)
    if not is_frozen:
        return
        
    current_exe = os.path.abspath(sys.argv[0])
    
    if sys.platform == 'win32':
        if os.path.basename(installed_dir).lower() in ("fordapphandler", "fordapp-handler"):
            cmd = f'choice /d y /t 2 > nul & del /f /q "{current_exe}" & rd /s /q "{installed_dir}"'
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    elif sys.platform == 'linux':
        if os.path.basename(installed_dir).lower() in ("fordapphandler", "fordapp-handler"):
            cmd = f'sleep 2 && rm -f "{current_exe}" && rm -rf "{installed_dir}"'
            subprocess.Popen(cmd, shell=True)

def install_and_register(target_dir, on_success_callback=None):
    global TEMP_REGISTRATION
    current_exe = os.path.abspath(sys.argv[0])
    
    if not target_dir.endswith("FordAppHandler") and not target_dir.endswith("fordapp-handler") and sys.platform != 'darwin':
        target_dir = os.path.join(target_dir, "FordAppHandler")
        
    current_dir = os.path.dirname(current_exe)
    
    if sys.platform == 'darwin':
        if register_mac():
            if on_success_callback:
                on_success_callback()
            return True
        return False
        
    dest_exe = os.path.join(target_dir, os.path.basename(current_exe))
    
    if os.path.abspath(current_exe) == os.path.abspath(dest_exe):
        if sys.platform == 'win32':
            success = register_windows(current_exe)
        else:
            success = register_linux(current_exe)
            
        if success:
            TEMP_REGISTRATION = False
            messagebox.showinfo("Success", "Protocol handler registered successfully!")
            if on_success_callback:
                on_success_callback()
            return True
        return False
        
    try:
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(current_exe, dest_exe)
        
        # Copy readme files if available
        readme_name = "README.txt"
        readme_src = os.path.join(current_dir, readme_name)
        if os.path.exists(readme_src):
            shutil.copy2(readme_src, os.path.join(target_dir, readme_name))
        else:
            readme_src_md = os.path.join(current_dir, "readme.md")
            if os.path.exists(readme_src_md):
                shutil.copy2(readme_src_md, os.path.join(target_dir, "readme.md"))
                
    except Exception as e:
        messagebox.showerror("Installation Error", f"Failed to copy files to:\n{target_dir}\n\nError: {str(e)}\n\nMake sure you have write permissions.")
        return False
        
    if sys.platform == 'win32':
        success = register_windows(dest_exe)
    else:
        success = register_linux(dest_exe)
        
    if success:
        TEMP_REGISTRATION = False
        messagebox.showinfo(
            "Installation Successful",
            f"FordApp Handler has been successfully installed and registered!\n\n"
            f"Location: {dest_exe}\n\n"
            f"You can now safely close this window and delete the downloaded file from your current folder."
        )
        if on_success_callback:
            on_success_callback()
        return True
    return False

def do_uninstall(silent=False):
    global TEMP_REGISTRATION
    registered, reg_path = check_registration_status()
    
    if not silent:
        confirm = messagebox.askyesno(
            "Confirm Uninstall",
            "Are you sure you want to uninstall FordApp Handler?\n"
            "This will remove the custom protocol registration."
        )
        if not confirm:
            return False
            
    if sys.platform == 'win32':
        success = unregister_windows(silent)
    elif sys.platform == 'linux':
        success = unregister_linux(silent)
    elif sys.platform == 'darwin':
        success = unregister_mac(silent)
    else:
        success = False
        
    if not success:
        if not silent:
            messagebox.showerror("Error", "Failed to unregister the protocol handler.")
        return False
        
    TEMP_REGISTRATION = False
        
    current_exe = os.path.abspath(sys.argv[0])
    current_dir = os.path.dirname(current_exe)
    is_installed_folder = os.path.basename(current_dir).lower() in ("fordapphandler", "fordapp-handler")
    
    if is_installed_folder:
        if not silent:
            delete_files = messagebox.askyesno(
                "Delete Files",
                f"Protocol handler registration has been removed.\n\n"
                f"Would you like to delete the application folder and its files?\n"
                f"Folder: {current_dir}"
            )
        else:
            delete_files = True
            
        if delete_files:
            if not silent:
                messagebox.showinfo(
                    "Uninstall Complete",
                    "The application will now close and delete its installed folder automatically."
                )
            trigger_self_delete(current_dir)
            sys.exit(0)
        else:
            if not silent:
                messagebox.showinfo("Uninstall Complete", "Registration removed. Application files were not deleted.")
    else:
        if registered and os.path.exists(reg_path):
            installed_dir = os.path.dirname(reg_path)
            is_installed_folder_name = os.path.basename(installed_dir).lower() in ("fordapphandler", "fordapp-handler")
            is_executable = reg_path.lower().endswith('.exe') or '.app' in reg_path.lower()
            if is_installed_folder_name and is_executable and os.path.abspath(installed_dir) != os.path.abspath(current_dir):
                if not silent:
                    delete_files = messagebox.askyesno(
                        "Delete Files",
                        f"Protocol handler registration has been removed.\n\n"
                        f"An existing installation folder was found at:\n{installed_dir}\n\n"
                        f"Would you like to delete this folder and all its contents?"
                    )
                else:
                    delete_files = True
                    
                if delete_files:
                    try:
                        shutil.rmtree(installed_dir)
                        if not silent:
                            messagebox.showinfo("Success", "Protocol unregistered and installed folder deleted successfully.")
                    except Exception as e:
                        if not silent:
                            messagebox.showerror("Error", f"Failed to delete installed folder:\n{str(e)}")
                else:
                    if not silent:
                        messagebox.showinfo("Success", "Protocol unregistered. Installed folder was not deleted.")
            else:
                if not silent:
                    messagebox.showinfo("Success", "Protocol unregistered successfully.")
        else:
            if not silent:
                messagebox.showinfo("Success", "Protocol unregistered successfully.")
    return True

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width/2) - (width/2))
    y = int((screen_height/2) - (height/2))
    root.geometry(f'{width}x{height}+{x}+{y}')

def make_button_interactive(btn, bg_normal, bg_hover, fg_normal, fg_hover):
    def on_enter(e):
        if btn['state'] != tk.DISABLED:
            btn.config(bg=bg_hover, fg=fg_hover)
    def on_leave(e):
        if btn['state'] != tk.DISABLED:
            btn.config(bg=bg_normal, fg=fg_normal)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def show_url_gui(url):
    root = tk.Tk()
    root.title(f"{PROTOCOL.capitalize()} URL Handler")
    root.configure(bg="#1e1e2e")
    center_window(root, 600, 170)
    root.resizable(False, False)

    tk.Label(
        root, 
        text="Authorization URL Received:", 
        font=("Segoe UI", 11, "bold"), 
        bg="#1e1e2e", 
        fg="#89b4fa"
    ).pack(pady=(15, 5))

    url_var = tk.StringVar(value=url)
    entry = tk.Entry(
        root, 
        textvariable=url_var, 
        state='readonly', 
        width=70, 
        font=("Consolas", 10),
        bg="#252538",
        fg="#cdd6f4",
        readonlybackground="#252538",
        selectbackground="#45475a",
        selectforeground="#cdd6f4",
        bd=1,
        relief=tk.SOLID
    )
    entry.pack(padx=25, pady=5)

    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(url)
        root.update()
        messagebox.showinfo("Success", "URL copied to clipboard!")

    btn_copy = tk.Button(
        root, 
        text="Copy URL to Clipboard", 
        command=copy_to_clipboard, 
        font=("Segoe UI", 10, "bold"), 
        bg="#a6e3a1",
        fg="#11111b",
        activebackground="#b4befe",
        activeforeground="#11111b",
        relief=tk.FLAT,
        bd=0,
        width=25,
        height=1
    )
    make_button_interactive(btn_copy, "#a6e3a1", "#b4befe", "#11111b", "#11111b")
    btn_copy.pack(pady=15)
    
    root.mainloop()

def show_setup_gui():
    root = tk.Tk()
    root.title(f"{PROTOCOL.capitalize()} Protocol Handler Setup")
    root.configure(bg="#1e1e2e")
    center_window(root, 550, 460)
    root.resizable(False, False)
    
    header_frame = tk.Frame(root, bg="#252538", height=60)
    header_frame.pack(fill=tk.X, side=tk.TOP)
    header_frame.pack_propagate(False)
    
    tk.Label(
        header_frame, 
        text=f"{PROTOCOL.upper()} Protocol Handler Setup", 
        font=("Segoe UI", 14, "bold"), 
        bg="#252538", 
        fg="#89b4fa"
    ).pack(pady=15)
    
    desc_frame = tk.Frame(root, bg="#1e1e2e")
    desc_frame.pack(padx=25, pady=(15, 10), fill=tk.X)
    
    desc_text = (
        f"This utility registers a custom URI scheme ({PROTOCOL}://) with your system.\n"
        f"When browser-based authentication redirects to a {PROTOCOL}:// URL, the OS launches\n"
        f"this handler to automatically copy the authorization token."
    )
    tk.Label(
        desc_frame, 
        text=desc_text, 
        font=("Segoe UI", 9), 
        bg="#1e1e2e", 
        fg="#a6adc8", 
        justify=tk.LEFT
    ).pack(anchor="w")
    
    status_frame = tk.LabelFrame(
        root, 
        text=" Current System Status ", 
        font=("Segoe UI", 9, "bold"), 
        bg="#1e1e2e", 
        fg="#89b4fa", 
        bd=1, 
        relief=tk.SOLID
    )
    status_frame.pack(padx=25, pady=10, fill=tk.X)
    
    status_var = tk.StringVar()
    path_var = tk.StringVar()
    
    status_label = tk.Label(status_frame, textvariable=status_var, font=("Segoe UI", 10, "bold"), bg="#1e1e2e")
    status_label.pack(anchor="w", padx=15, pady=(8, 2))
    
    path_label = tk.Label(
        status_frame, 
        textvariable=path_var, 
        font=("Consolas", 8), 
        bg="#1e1e2e", 
        fg="#a6adc8", 
        wraplength=480, 
        justify=tk.LEFT
    )
    path_label.pack(anchor="w", padx=15, pady=(2, 8))
    
    def refresh_status():
        registered, reg_path = check_registration_status()
        if registered:
            status_var.set("● REGISTERED")
            status_label.config(fg="#a6e3a1")
            path_var.set(f"Registered path: {reg_path}")
            btn_uninstall.config(state=tk.NORMAL, bg="#f38ba8", fg="#11111b")
            btn_test.config(state=tk.NORMAL, bg="#a6e3a1", fg="#11111b")
        else:
            status_var.set("○ NOT REGISTERED")
            status_label.config(fg="#f38ba8")
            path_var.set(f"Details: {reg_path}")
            btn_test.config(state=tk.DISABLED, bg="#313244", fg="#585b70")
            if reg_path == "Not registered":
                btn_uninstall.config(state=tk.DISABLED, bg="#313244", fg="#585b70")
            else:
                btn_uninstall.config(state=tk.NORMAL, bg="#f38ba8", fg="#11111b")
                
    buttons_frame = tk.Frame(root, bg="#1e1e2e")
    buttons_frame.pack(padx=25, pady=15, fill=tk.X)
    
    def on_install_click():
        default_dir = get_default_install_path()
        ans = messagebox.askyesnocancel(
            "Installation Directory Selection",
            f"Would you like to install FordApp Handler to the recommended location?\n\n"
            f"Recommended Location:\n{default_dir}\n\n"
            f"• Click 'Yes' to install to the recommended location.\n"
            f"• Click 'No' to choose a custom directory.\n"
            f"• Click 'Cancel' to abort registration."
        )
        if ans is True:
            install_and_register(default_dir, on_success_callback=refresh_status)
        elif ans is False:
            custom_dir = filedialog.askdirectory(title="Select Folder to Install FordApp Handler")
            if custom_dir:
                install_and_register(custom_dir, on_success_callback=refresh_status)
                
    def on_register_inplace_click():
        global TEMP_REGISTRATION
        current_exe = os.path.abspath(sys.argv[0])
        if sys.platform == 'win32':
            success = register_windows(current_exe)
        else:
            success = register_linux(current_exe)
        if success:
            TEMP_REGISTRATION = True
            messagebox.showinfo("Success", "Registered current file location temporarily!\n\nThis registration will be automatically removed when you close this Setup window.")
            refresh_status()
            
    def on_uninstall_click():
        if do_uninstall(silent=False):
            refresh_status()
            
    def on_test_click():
        try:
            webbrowser.open(f"{PROTOCOL}://test-connection-successful")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {str(e)}")
            
    def create_styled_button(parent, text, command, bg_color, fg_color, bg_hover, fg_hover, height=1):
        btn = tk.Button(
            parent, 
            text=text, 
            command=command, 
            font=("Segoe UI", 9, "bold"), 
            bg=bg_color, 
            fg=fg_color, 
            activebackground=bg_hover, 
            activeforeground=fg_hover, 
            relief=tk.FLAT, 
            bd=0, 
            height=height
        )
        make_button_interactive(btn, bg_color, bg_hover, fg_color, fg_hover)
        return btn

    btn_install = create_styled_button(
        buttons_frame, 
        text="Install & Register Protocol (Recommended)", 
        command=on_install_click,
        bg_color="#89b4fa",
        fg_color="#11111b",
        bg_hover="#b4befe",
        fg_hover="#11111b"
    )
    btn_install.pack(fill=tk.X, pady=4)
    
    btn_inplace = create_styled_button(
        buttons_frame,
        text="Register Current File Location (Temporary - Removed on Close)",
        command=on_register_inplace_click,
        bg_color="#313244",
        fg_color="#cdd6f4",
        bg_hover="#45475a",
        fg_hover="#cdd6f4"
    )
    btn_inplace.pack(fill=tk.X, pady=4)
    
    btn_test = create_styled_button(
        buttons_frame,
        text="Test Protocol Handler (Run End-to-End Test)",
        command=on_test_click,
        bg_color="#a6e3a1",
        fg_color="#11111b",
        bg_hover="#b4befe",
        fg_hover="#11111b"
    )
    btn_test.pack(fill=tk.X, pady=4)
    
    bottom_row = tk.Frame(buttons_frame, bg="#1e1e2e")
    bottom_row.pack(fill=tk.X, pady=4)
    
    btn_uninstall = create_styled_button(
        bottom_row,
        text="Uninstall / Clean Up",
        command=on_uninstall_click,
        bg_color="#f38ba8",
        fg_color="#11111b",
        bg_hover="#f38ba8",
        fg_hover="#ffffff"
    )
    btn_uninstall.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
    
    def on_close():
        global TEMP_REGISTRATION
        if TEMP_REGISTRATION:
            if sys.platform == 'win32':
                unregister_windows(silent=True)
            elif sys.platform == 'linux':
                unregister_linux(silent=True)
            elif sys.platform == 'darwin':
                unregister_mac(silent=True)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    btn_close = create_styled_button(
        bottom_row,
        text="Close Setup",
        command=on_close,
        bg_color="#313244",
        fg_color="#cdd6f4",
        bg_hover="#45475a",
        fg_hover="#cdd6f4"
    )
    btn_close.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
    
    refresh_status()
    root.mainloop()

if __name__ == "__main__":
    uninstall_args = {'--uninstall', '-u', '/uninstall'}
    silent_args = {'--silent', '-s'}
    
    args = [arg.lower() for arg in sys.argv[1:]]
    
    is_uninstall = any(arg in uninstall_args for arg in args)
    is_silent = any(arg in silent_args for arg in args)
    
    if is_uninstall:
        do_uninstall(silent=is_silent)
        sys.exit(0)
        
    received_url = None
    for arg in sys.argv[1:]:
        if arg.startswith(f"{PROTOCOL}://"):
            received_url = arg
            break
            
    if received_url:
        show_url_gui(received_url)
    else:
        show_setup_gui()