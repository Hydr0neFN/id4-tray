[English](README.md) · **繁體中文**

# id4-tray

Audient iD4 MKII 的 Windows 小工具，常駐在系統匣。不用開 iD mixer 就能改取樣率和 ASIO buffer 大小。

**非官方專案。** 本專案與 Audient、Thesycon 沒有隸屬關係，未經其認可，也不受其支援。
「Audient」和「iD」是各自權利人的商標。請自行承擔使用風險。

## 一眼看

| | |
|---|---|
| 要解決的問題 | iD mixer 得一直開著，才能改取樣率或 buffer 大小。有些系統上 iD 4.4.2 開著的時候還會寫一個很大的 log 檔。 |
| 做了什麼 | 一個系統匣程式，可以改取樣率和 ASIO buffer 大小，也能開啟或關閉 iD mixer。 |
| 為什麼可行 | 關掉 iD 之後 driver 還是會保留設定，所以這兩項設定用一個小程式處理就夠。 |
| 技術 | Python 3.10 以上（64 位元）、pywin32、Pillow、Thesycon `TUSBAUDIO` driver API。 |
| 實測環境 | Audient iD4 MKII、driver 5.5.1（`audientusbaudio.sys`）、iD app 4.4.2、Windows 11 Pro。 |
| 待確認 | 還沒驗證的：重開機後，或重新插上裝置後，設定會不會留著。 |

## 功能

- 系統匣圖示，滑過去顯示目前的取樣率和 ASIO buffer 大小。
- 選單：取樣率（44.1 / 48 / 88.2 / 96 kHz）。
- 選單：ASIO buffer 大小（8 到 2048 samples）。
- 選單：開啟或關閉 iD mixer（拿來調 monitor mix 和其他設定）。

它不能取代 iD mixer：monitor mix、loopback 和 firmware 更新還是得用 iD 應用程式。

## 運作方式

```
 id4_tray.py (tray icon and menu)
        |
        +-- audientusbaudioapi_x64.dll (Audient driver, Thesycon TUSBAUDIO API)
        |       sample rate and ASIO buffer size
        |
        +-- iD.exe (iD mixer application, opened or closed from the menu)
```

程式控制 driver 列出的第一台裝置。系統匣的提示文字直接跟 driver 讀目前的取樣率和 ASIO buffer 大小。

## 實測環境

| 項目     | 版本                            |
|----------|---------------------------------|
| 裝置     | Audient iD4 MKII                |
| Driver   | 5.5.1 (`audientusbaudio.sys`)   |
| iD app   | 4.4.2                           |
| 作業系統 | Windows 11 Pro                  |

其他 iD 介面用的是同一套 driver 系列，有機會可以用，不過沒測過。

## 安裝與執行

需求：

- Windows 10 或 11，64 位元。
- Audient USB 音效 driver，裝在預設路徑
  (`C:\Program Files\Audient\USBAudioDriver\x64\audientusbaudioapi_x64.dll`)。
- Python 3.10 以上，64 位元。

```
pip install -r requirements.txt
pythonw id4_tray.py
```

要開機自動啟動，就把 `pythonw.exe "<path>\id4_tray.py"` 的捷徑放進 `shell:startup` 開的資料夾。

這個 repo 裡面沒有 Audient 或 Thesycon 的檔案。程式載入的是 Audient 安裝程式放在你電腦上的
driver API DLL。圖示（`id4.ico`）會在第一次執行時產生。

## 怎麼跟 driver 溝通

driver API DLL 匯出的是 `TUSBAUDIO_*` 函式。程式用到的這些呼叫是從觀察來的。函式清單和
ASIO info block 的欄位配置見 [docs/driver-api.zh-TW.md](docs/driver-api.zh-TW.md)。

`dev/asio_info.py` 會印出 ASIO info block，也可以從命令列設 buffer 大小。

## 限制與待辦

- 還沒驗證的：重開機後，或重新插上裝置後，設定會不會留著。
- 其他 iD 介面用的是同一套 driver 系列，有機會可以用，不過沒測過。
- monitor mix、loopback 和 firmware 更新還是得用 iD 應用程式。

## 授權

MIT。詳見 `LICENSE`。
