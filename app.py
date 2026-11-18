"""Discord Game Detector：讓 Discord 以為正在玩某款遊戲。"""
import json
import shutil
import subprocess
import sys
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import messagebox

BASE = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
DUMMY_EXE = BASE / "dist" / "dummy.exe"
GAMES_DIR = BASE / "games"
CACHE = BASE / "detectable.json"
URL = "https://discord.com/api/v9/applications/detectable"


def download_list():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        CACHE.write_bytes(resp.read())


def load_games():
    """回傳 [(id, name, [exe 路徑, ...])]，只保留有 Windows 執行檔的遊戲。"""
    if not CACHE.exists():
        download_list()
    games = []
    for app in json.loads(CACHE.read_text(encoding="utf-8")):
        exes = [e["name"] for e in app.get("executables") or []
                if e.get("os") == "win32" and not e.get("is_launcher")]
        if exes:
            games.append((app["id"], app["name"], exes))
    return games


class App:
    def __init__(self, root):
        self.root = root
        self.games = load_games()
        self.shown = []
        self.proc = None

        root.title("Discord Game Detector")
        root.geometry("520x420")

        top = tk.Frame(root)
        top.pack(fill="x", padx=8, pady=8)
        self.query = tk.StringVar()
        self.query.trace_add("write", lambda *_: self.search())
        tk.Entry(top, textvariable=self.query).pack(side="left", fill="x", expand=True)
        tk.Button(top, text="重新下載清單", command=self.refresh).pack(side="left", padx=4)

        self.listbox = tk.Listbox(root)
        self.listbox.pack(fill="both", expand=True, padx=8)

        bottom = tk.Frame(root)
        bottom.pack(fill="x", padx=8, pady=8)
        tk.Button(bottom, text="開始", width=10, command=self.start).pack(side="left")
        tk.Button(bottom, text="停止", width=10, command=self.stop).pack(side="left", padx=4)
        self.status = tk.Label(bottom, text=f"共 {len(self.games)} 款遊戲，輸入名稱或 ID 搜尋", anchor="w")
        self.status.pack(side="left", fill="x", expand=True)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def search(self):
        q = self.query.get().strip().lower()
        self.listbox.delete(0, "end")
        self.shown = [g for g in self.games if q and (q in g[1].lower() or q == g[0])][:200]
        for gid, name, exes in self.shown:
            self.listbox.insert("end", f"{name}  —  {exes[0]}")

    def refresh(self):
        try:
            download_list()
        except Exception as e:
            messagebox.showerror("下載失敗", str(e))
            return
        self.games = load_games()
        self.search()
        self.status.config(text=f"已更新，共 {len(self.games)} 款遊戲")

    def start(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        if not DUMMY_EXE.exists():
            messagebox.showerror("找不到 dummy.exe", f"請先執行：pyinstaller --onefile --noconsole dummy.py\n\n預期位置：{DUMMY_EXE}")
            return
        self.stop()
        gid, name, exes = self.shown[sel[0]]
        # Discord 會比對 exe 路徑的尾段（例如 bin/game.exe），所以要重建相同的資料夾結構
        target = GAMES_DIR / gid / Path(exes[0].lstrip(">/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DUMMY_EXE, target)
        self.proc = subprocess.Popen([str(target), name], cwd=target.parent)
        self.status.config(text=f"執行中：{name}")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            # PyInstaller onefile 會再開一個同名子程序，terminate() 只殺父程序，子程序會殘留
            subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"], capture_output=True)
        self.proc = None
        self.status.config(text="已停止")

    def on_close(self):
        self.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
