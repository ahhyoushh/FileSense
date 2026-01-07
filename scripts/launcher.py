import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from pathlib import Path
import time
import pystray
from PIL import Image, ImageDraw

# Ensure project root is in path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

PY_EXE = sys.executable

# --- THEME ---
COLOR_BG = "#202124"
COLOR_PANEL = "#2d2e31"
COLOR_TEXT = "#e8eaed"
COLOR_ACCENT = "#8ab4f8"
COLOR_SUCCESS = "#81c995"
COLOR_ERROR = "#f28b82"
FONT_MAIN = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI", 9, "bold")

class RLAuditWindow(tk.Toplevel):
    def __init__(self, parent, audit_script_path):
        super().__init__(parent)
        self.title("RL Diagnostics")
        self.geometry("600x400")
        self.configure(bg=COLOR_BG)
        self.audit_script = audit_script_path
        
        # Styles handling (inherits from parent usually, but explicit here for safety)
        container = ttk.Frame(self, padding=15, style="Panel.TFrame")
        container.pack(fill=tk.BOTH, expand=True)

        lbl = ttk.Label(container, text="Reinforcement Learning Audit", font=("Segoe UI", 12, "bold"), style="Panel.TLabel")
        lbl.pack(anchor="w", pady=(0, 10))

        self.btn_run = ttk.Button(container, text="Run Audit", command=self.run_audit, style="Accent.TButton", width=15)
        self.btn_run.pack(anchor="w", pady=(0, 10))

        # Output Log
        self.log = scrolledtext.ScrolledText(container, height=15, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9), relief="flat")
        self.log.pack(fill=tk.BOTH, expand=True)
    
    def run_audit(self):
        self.log.delete(1.0, tk.END)
        self.log.insert(tk.END, f"Running: {self.audit_script}\n\n")
        
        def _run():
            try:
                p = subprocess.Popen([PY_EXE, self.audit_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                out, _ = p.communicate()
                self.log.insert(tk.END, out)
            except Exception as e:
                self.log.insert(tk.END, f"Error: {e}")
        
        threading.Thread(target=_run, daemon=True).start()


class ScriptLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileSense")
        self.geometry("600x480")  # Compact Size
        self.configure(bg=COLOR_BG)
        
        # State
        self.proc_script = None
        self.proc_watcher = None

        # Paths
        self.script_path = tk.StringVar(value=str(Path(project_root) / "scripts" / "main.py"))
        self.script_dir = tk.StringVar(value=str(Path(project_root) / "files"))
        self.sorted_dir = tk.StringVar(value=str(Path(project_root) / "sorted"))
        self.watcher_path = tk.StringVar(value=str(Path(project_root) / "scripts" / "watcher.py"))
        self.rl_audit_path = tk.StringVar(value=str(Path(project_root) / "scripts" / "RL" / "rl_audit_safe.py"))

        # Options
        self.opt_single_thread = tk.BooleanVar(value=False)
        self.opt_no_gen = tk.BooleanVar(value=False)
        self.opt_no_logs = tk.BooleanVar(value=False)
        self.opt_auto_save_logs = tk.BooleanVar(value=True)
        self.opt_test_mode = tk.BooleanVar(value=False)
        self.opt_threads = tk.IntVar(value=6)
        self.opt_disable_rl = tk.BooleanVar(value=True)

        self._setup_styles()
        self._build_ui()
        
        # Tray
        self.tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def _setup_styles(self):
        style = ttk.Style(self)
        try: style.theme_use('clam') 
        except: pass
        
        style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_MAIN, borderwidth=0)
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Panel.TFrame", background=COLOR_PANEL)
        style.configure("Panel.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXT)
        style.configure("TButton", background="#3c4043", foreground="#ffffff", borderwidth=0, focuscolor=COLOR_ACCENT, padding=5)
        style.map("TButton", background=[("active", "#4a4d51")], foreground=[("active", "#ffffff")])
        style.configure("Accent.TButton", background=COLOR_ACCENT, foreground="#202124", font=FONT_BOLD)
        style.map("Accent.TButton", background=[("active", "#82b1ff")])
        style.configure("TCheckbutton", background=COLOR_BG, foreground=COLOR_TEXT)
        style.map("TCheckbutton", background=[("active", COLOR_BG)])
        style.configure("TEntry", fieldbackground="#3c4043", foreground="#ffffff", borderwidth=1, relief="solid")
        style.configure("TSpinbox", fieldbackground="#3c4043", foreground="#ffffff", arrowcolor="#ffffff", borderwidth=1, relief="solid")
        style.map("TSpinbox", fieldbackground=[("readonly", "#3c4043")], foreground=[("readonly", "#ffffff")])
        style.configure("TCombobox", fieldbackground="#3c4043", foreground="#ffffff", arrowcolor="#ffffff", borderwidth=1, relief="solid")
        style.map("TCombobox", fieldbackground=[("readonly", "#3c4043")], foreground=[("readonly", "#ffffff")], selectbackground=[("readonly", "#4a4d51")], selectforeground=[("readonly", "#ffffff")])

    def _build_ui(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        # 1. Config Section (Minimal)
        lbl = ttk.Label(main, text="Configuration", font=FONT_BOLD, foreground=COLOR_ACCENT)
        lbl.pack(anchor="w", pady=(0,5))

        f_paths = ttk.Frame(main)
        f_paths.pack(fill=tk.X, pady=(0,10))
        
        self._path_row(f_paths, "Target Dir:", self.script_dir, is_dir=True)
        self._path_row(f_paths, "Sorted Dir:", self.sorted_dir, is_dir=True)
        # Hidden power user paths? No, user asked for "all options displayed".
        self._path_row(f_paths, "Script File:", self.script_path, is_dir=False)
        self._path_row(f_paths, "Watcher File:", self.watcher_path, is_dir=False)

        # 2. Options Grid
        f_opts = ttk.Frame(main)
        f_opts.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(f_opts, text="Auto-Log", variable=self.opt_auto_save_logs).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Checkbutton(f_opts, text="No Logs", variable=self.opt_no_logs).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Checkbutton(f_opts, text="Strict Mode", variable=self.opt_no_gen).grid(row=0, column=2, sticky="w", padx=5)
        
        ttk.Checkbutton(f_opts, text="Dry Run", variable=self.opt_test_mode).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Checkbutton(f_opts, text="Single Thread", variable=self.opt_single_thread, command=self._toggle_threads).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Checkbutton(f_opts, text="Privacy Mode", variable=self.opt_disable_rl).grid(row=1, column=2, sticky="w", padx=5)
        
        f_th = ttk.Frame(f_opts)
        f_th.grid(row=0, column=3, sticky="w", padx=5)
        ttk.Label(f_th, text="Threads: ").pack(side=tk.LEFT)
        self.spin_threads = ttk.Spinbox(f_th, from_=1, to=32, textvariable=self.opt_threads, width=3)
        self.spin_threads.pack(side=tk.LEFT)
        
        # Model Selection
        f_model = ttk.Frame(main)
        f_model.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(f_model, text="Model:", foreground="#9aa0a6").pack(side=tk.LEFT, padx=(0,5))
        
        self.model_var = tk.StringVar(value="BAAI/bge-base-en-v1.5")
        models = ["BAAI/bge-base-en-v1.5", "all-MiniLM-L12-v2", "all-mpnet-base-v2"]
        self.combo_model = ttk.Combobox(f_model, textvariable=self.model_var, values=models, width=25, state="readonly")
        self.combo_model.pack(side=tk.LEFT, padx=5)
        
        # Recommendation Link
        lbl_rec = tk.Label(f_model, text="(Recommended)", bg=COLOR_BG, fg=COLOR_SUCCESS, cursor="hand2", font=("Segoe UI", 8, "underline"))
        lbl_rec.pack(side=tk.LEFT, padx=5)
        lbl_rec.bind("<Button-1>", lambda e: self.open_model_link())

        # 3. Actions Bar
        f_actions = ttk.Frame(main)
        f_actions.pack(fill=tk.X, pady=(0, 15))

        # Script Controls
        ttk.Button(f_actions, text="Start", style="Accent.TButton", command=self.start_script, width=8).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(f_actions, text="Stop", command=self.stop_script, width=8).pack(side=tk.LEFT, padx=(0,15))
        
        # Watcher Controls
        ttk.Button(f_actions, text="Run Watcher", command=self.start_watcher).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(f_actions, text="Kill Watcher", command=self.kill_watcher_force).pack(side=tk.LEFT, padx=(0,5))

        # 4. Logs Console
        self.log = scrolledtext.ScrolledText(main, height=8, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 8), relief="flat")
        self.log.pack(fill=tk.BOTH, expand=True)

        # 5. Bottom Tools
        f_tools = ttk.Frame(main, padding=(0,10,0,0))
        f_tools.pack(fill=tk.X)
        
        ttk.Button(f_tools, text="Diagnostics", command=self.open_rl_window, width=20).pack(side=tk.RIGHT)
        ttk.Button(f_tools, text="📂 Logs", command=self.open_logs_dir, width=10).pack(side=tk.RIGHT, padx=5)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(f_tools, textvariable=self.status_var, foreground="#808080", font=("Segoe UI", 8)).pack(side=tk.LEFT, anchor="s")

    def open_model_link(self):
        import webbrowser
        webbrowser.open("https://ahhyoushh.github.io/FileSense/wiki/metrics/")

    def _path_row(self, parent, label, var, is_dir):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=2)
        ttk.Label(f, text=label, width=10, foreground="#9aa0a6").pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        cmd = lambda: self.browse_dir(var) if is_dir else self.browse_file(var)
        ttk.Button(f, text="..", width=3, command=cmd).pack(side=tk.LEFT)

    def _toggle_threads(self):
        if self.opt_single_thread.get(): self.spin_threads.state(['disabled'])
        else: self.spin_threads.state(['!disabled'])

    def start_script(self):
        self._run_cmd("Script", [PY_EXE, "-u", self.script_path.get(), "--dir", self.script_dir.get(), "--sorted-dir", self.sorted_dir.get()], 
                      script_proc=True)

    def start_watcher(self):
        self._run_cmd("Watcher", [PY_EXE, "-u", self.watcher_path.get(), "-d", self.script_dir.get(), "--sorted-dir", self.sorted_dir.get()], 
                      watcher_proc=True)

    def _run_cmd(self, label, cmd_list, script_proc=False, watcher_proc=False):
        # Attach flags
        if script_proc:
            if self.opt_single_thread.get(): cmd_list.append("--single-thread")
            else: cmd_list.extend(["--threads", str(self.opt_threads.get())])
            if self.opt_no_gen.get(): cmd_list.append("--no-generation")
            if self.opt_no_logs.get(): cmd_list.append("--no-logs")
            if self.opt_auto_save_logs.get(): cmd_list.append("--auto-save-logs")
            if self.opt_test_mode.get(): cmd_list.append("--test")
            
            if self.opt_disable_rl.get():
                cmd_list.append("--disable-rl")
            else:
                cmd_list.append("--enable-rl")
            
            # Pass Model
            model_val = self.model_var.get()
            if model_val:
                cmd_list.extend(["--model", model_val])

            if self.proc_script and self.proc_script.poll() is None: return

        if watcher_proc:
            if self.opt_disable_rl.get():
                cmd_list.append("--disable-rl")
            else:
                cmd_list.append("--enable-rl")
            if self.proc_watcher and self.proc_watcher.poll() is None: return

        self.log_msg(f"Starting {label}...", "info")
        try:
            cwd = str(Path(cmd_list[2]).parent) # use script parent as cwd
            proc = subprocess.Popen(cmd_list, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                    text=True, bufsize=1, universal_newlines=True)
            
            if script_proc: self.proc_script = proc
            if watcher_proc: self.proc_watcher = proc
            
            threading.Thread(target=self._stream, args=(proc, label), daemon=True).start()
        except Exception as e:
            self.log_msg(f"{label} Fail: {e}", "err")

    def stop_script(self):
        if self.proc_script: self.proc_script.terminate()

    def kill_watcher_force(self):
        if self.proc_watcher: self.proc_watcher.kill()

    def open_rl_window(self):
        RLAuditWindow(self, self.rl_audit_path.get())

    def open_logs_dir(self):
        os.startfile(Path(project_root) / "logs")

    def browse_file(self, var):
        f = filedialog.askopenfilename()
        if f: var.set(f)

    def browse_dir(self, var):
        d = filedialog.askdirectory()
        if d: var.set(d)

    def log_msg(self, msg, tag=""):
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, f"{msg}\n", tag)
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)
        self.status_var.set(msg)

    def _stream(self, proc, label):
        for line in iter(proc.stdout.readline, ''):
            if line: self.log_msg(f"{label}: {line.strip()}")
        proc.wait()
        self.log_msg(f"{label} Stopped.")

    # Tray logic (Minimal)
    def hide_window(self):
        self.withdraw()
        img = Image.new('RGB', (64, 64), COLOR_BG)
        d = ImageDraw.Draw(img)
        d.ellipse([16,16,48,48], fill=COLOR_ACCENT)
        self.tray_icon = pystray.Icon("FS", img, "FileSense", pystray.Menu(
            pystray.MenuItem("Open", self.show_window), 
            pystray.MenuItem("Exit", self.quit_app)))
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, i=None, item=None):
        if self.tray_icon: self.tray_icon.stop()
        self.deiconify()

    def quit_app(self, i=None, item=None):
        if self.tray_icon: self.tray_icon.stop()
        if self.proc_script: self.proc_script.terminate()
        if self.proc_watcher: self.proc_watcher.terminate()
        self.destroy()

if __name__ == "__main__":
    app = ScriptLauncher()
    app.mainloop()
