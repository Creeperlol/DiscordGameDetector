# DiscordGameDetector

讓 Discord 偵測到「正在玩」某款遊戲。

## 原理

Discord 會比對正在執行的程序 exe 名稱，對照它的公開清單 `https://discord.com/api/v9/applications/detectable`。本工具把一個小小的虛擬程式（`dummy.exe`）複製成遊戲的 exe 名稱再執行，Discord 就會顯示正在玩該遊戲。

## 安裝

需要 Windows 與 Python 3.12+。

```bash
pip install -r requirements.txt
pyinstaller --onefile --noconsole dummy.py
```

## 使用

```bash
python app.py
```

1. 輸入遊戲名稱或 Application ID 搜尋
2. 選擇遊戲，按「開始」
3. 保持 Discord 桌面版開啟（設定 → 活動隱私 → 開啟「顯示目前活動」）
4. 不使用時按「停止」

## 免責聲明

使用本工具可能違反 Discord 服務條款與 Quest 規則，可能導致獎勵被收回或帳號受到處分。
使用風險自負。

## License

[MIT](LICENSE)
