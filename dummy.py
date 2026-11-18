"""假遊戲程序：顯示遊戲名與經過時間，關閉視窗即結束。"""
import sys
import time
import tkinter as tk

name = sys.argv[1] if len(sys.argv) > 1 else "Dummy Game"
start = time.time()

# Discord 對有可見視窗的程序偵測較穩定，所以不做成背景程序
root = tk.Tk()
root.title(name)
root.geometry("280x90")
label = tk.Label(root, font=("Segoe UI", 12))
label.pack(expand=True)


def tick():
    elapsed = int(time.time() - start)
    label.config(text=f"{name}\n已執行 {elapsed // 60:02d}:{elapsed % 60:02d}")
    root.after(1000, tick)


tick()
root.mainloop()
