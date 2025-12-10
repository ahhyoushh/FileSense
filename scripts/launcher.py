import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import time
from pathlib import Path
import signal
import pystray
from PIL import Image, ImageDraw

PY_EXE = sys.executable  # current Python interpreter


class ScriptLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileSense Launcher")
        self.geometry("740x480")
        self.resizable(False, False)

        # state vars
        self.proc_script = None
        self.proc_watcher = None

        # file paths and dirs
        self.script_path = tk.StringVar(value="script.py")
        self.script_dir = tk.StringVar(value="")
        self.watcher_path = tk.StringVar(value="watcher.py")
        self.watcher_dir = tk.StringVar(value="")

        self._build_ui()

        # tray
        self.tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    # =============== UI ===============
    def _build_ui(self):
        pad = 8
        frm = ttk.Frame(self, padding=pad)
        frm.pack(fill=tk.BOTH, expand=True)

        # -------- script section --------
        box1 = ttk.LabelFrame(frm, text="Script Runner (--dir)", padding=pad)
        box1.pack(fill=tk.X, padx=pad, pady=(pad, 0))

        row1 = ttk.Frame(box1)
        row1.pack(fill=tk.X, pady=4)
        ttk.Label(row1, text="Script file:").pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.script_path, width=50).pack(side=tk.LEFT, padx=6)
        ttk.Button(row1, text="Browse", command=self.browse_script).pack(side=tk.LEFT)

        row2 = ttk.Frame(box1)
        row2.pack(fill=tk.X, pady=4)
        ttk.Label(row2, text="--dir folder:").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.script_dir, width=45).pack(side=tk.LEFT, padx=6)
        ttk.Button(row2, text="Browse Dir", command=self.browse_script_dir).pack(side=tk.LEFT)

        btns1 = ttk.Frame(box1)
        btns1.pack(fill=tk.X, pady=6)
        ttk.Button(btns1, text="Start Script", command=self.start_script).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns1, text="Stop Script", command=self.stop_script).pack(side=tk.LEFT, padx=6)

        # -------- watcher section --------
        box2 = ttk.LabelFrame(frm, text="Watcher (-d / --dir, stop.flag)", padding=pad)
        box2.pack(fill=tk.X, padx=pad, pady=(pad, 0))

        row3 = ttk.Frame(box2)
        row3.pack(fill=tk.X, pady=4)
        ttk.Label(row3, text="Watcher file:").pack(side=tk.LEFT)
        ttk.Entry(row3, textvariable=self.watcher_path, width=50).pack(side=tk.LEFT, padx=6)
        ttk.Button(row3, text="Browse", command=self.browse_watcher).pack(side=tk.LEFT)

        row4 = ttk.Frame(box2)
        row4.pack(fill=tk.X, pady=4)
        ttk.Label(row4, text="-d folder:").pack(side=tk.LEFT)
        ttk.Entry(row4, textvariable=self.watcher_dir, width=45).pack(side=tk.LEFT, padx=6)
        ttk.Button(row4, text="Browse Dir", command=self.browse_watcher_dir).pack(side=tk.LEFT)

        btns2 = ttk.Frame(box2)
        btns2.pack(fill=tk.X, pady=6)
        ttk.Button(btns2, text="Start Watcher", command=self.start_watcher).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns2, text="Kill Watcher (force)", command=self.kill_watcher_force).pack(side=tk.LEFT, padx=6)

        # -------- log section --------
        log_box = ttk.LabelFrame(frm, text="Log Output", padding=pad)
        log_box.pack(fill=tk.BOTH, expand=True, padx=pad, pady=(pad, 0))
        self.log = scrolledtext.ScrolledText(log_box, height=10, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True)
        self.log.configure(state=tk.DISABLED)

        # -------- status --------
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

    # =============== Tray ===============
    def create_tray_image(self, size=64, color1="black", color2="white"):
        img = Image.new("RGB", (size, size), color1)
        dc = ImageDraw.Draw(img)
        dc.ellipse((size//4, size//4, size*3//4, size*3//4), fill=color2)
        return img

    def hide_window(self):
        self.withdraw()
        image = self.create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Restore", self.show_window),
            pystray.MenuItem("Quit", self.quit_app)
        )
        self.tray_icon = pystray.Icon("FileSense", image, "FileSense Launcher", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.log_msg("Window minimized to tray.")

    def show_window(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.log_msg("Window restored from tray.")

    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    # =============== Utilities ===============
    def log_msg(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{ts}] {msg}\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)
        self.status_var.set(msg)

    def browse_script(self):
        p = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if p: self.script_path.set(p)

    def browse_watcher(self):
        p = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if p: self.watcher_path.set(p)

    def browse_script_dir(self):
        d = filedialog.askdirectory()
        if d: self.script_dir.set(d)

    def browse_watcher_dir(self):
        d = filedialog.askdirectory()
        if d: self.watcher_dir.set(d)

    # =============== Script Control ===============
    def start_script(self):
        if self.proc_script and self.proc_script.poll() is None:
            self.log_msg("Script already running.")
            return
        script = Path(self.script_path.get())
        if not script.exists():
            messagebox.showerror("Error", f"Script not found: {script}")
            return
        dir_arg = self.script_dir.get().strip()
        if not dir_arg:
            messagebox.showerror("Error", "Please select directory for --dir.")
            return

        cmd = [PY_EXE, str(script), "--dir", dir_arg]
        self.log_msg(f"Running script: {' '.join(cmd)}")

        try:
            self.proc_script = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            threading.Thread(target=self._stream_output, args=(self.proc_script, "script"), daemon=True).start()
        except Exception as e:
            self.log_msg(f"Error starting script: {e}")

    def stop_script(self):
        if not self.proc_script or self.proc_script.poll() is not None:
            self.log_msg("No running script.")
            return
        self.log_msg("Stopping script...")
        self.proc_script.terminate()
        threading.Thread(target=self._wait_and_kill, args=(self.proc_script, "script"), daemon=True).start()

    # =============== Watcher Control ===============
    def start_watcher(self):
        if self.proc_watcher and self.proc_watcher.poll() is None:
            self.log_msg("Watcher already running.")
            return
        watcher = Path(self.watcher_path.get())
        if not watcher.exists():
            messagebox.showerror("Error", f"Watcher not found: {watcher}")
            return
        dir_arg = self.watcher_dir.get().strip()
        if not dir_arg:
            messagebox.showerror("Error", "Please select directory for watcher -d.")
            return

        cmd = [PY_EXE, "-u", str(watcher), "-d", dir_arg]
        self.log_msg(f"Running watcher: {' '.join(cmd)}")

        try:
            self.proc_watcher = subprocess.Popen(
                cmd,
                cwd=str(watcher.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # merge stderr into stdout so all logs show up
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            threading.Thread(
                target=self._stream_output_unbuffered,
                args=(self.proc_watcher, "watcher"),
                daemon=True,
            ).start()

        except Exception as e:
            self.log_msg(f"Error starting watcher: {e}")


    def kill_watcher_force(self):
        if not self.proc_watcher or self.proc_watcher.poll() is not None:
            self.log_msg("No watcher to kill.")
            return
        self.log_msg("Force killing watcher...")
        self.proc_watcher.kill()
        self.log_msg("Watcher killed.")

    # =============== Helpers ===============
    def _stream_output(self, proc, label):
        try:
            for line in proc.stdout:
                self.log_msg(f"{label}: {line.strip()}")
            err = proc.stderr.read()
            if err:
                for l in err.splitlines():
                    self.log_msg(f"{label} ERR: {l}")
        finally:
            self.log_msg(f"{label} exited ({proc.poll()})")

    def _stream_output_unbuffered(self, proc, label):
        # reads in real time
        for line in iter(proc.stdout.readline, ''):
            if line:
                self.log_msg(f"{label}: {line.rstrip()}")
        proc.stdout.close()
        proc.wait()
        self.log_msg(f"{label} exited ({proc.returncode})")

    def _wait_and_kill(self, proc, label):
        time.sleep(3)
        if proc.poll() is None:
            proc.kill()
            self.log_msg(f"{label} killed forcefully.")


if __name__ == "__main__":
    app = ScriptLauncher()
    app.mainloop()
