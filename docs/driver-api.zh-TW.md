[English](driver-api.md) · **繁體中文**

[回到 README](../README.zh-TW.md)

# id4-tray 怎麼跟 driver 溝通

driver API DLL 匯出的是 `TUSBAUDIO_*` 函式。程式用到的這些呼叫是從觀察來的：

| 函式                                                            | 用途                        |
|-----------------------------------------------------------------|-----------------------------|
| `TUSBAUDIO_EnumerateDevices()`                                  | 更新裝置清單                |
| `TUSBAUDIO_OpenDeviceByIndex(index, &handle)` / `CloseDevice`   | 開啟、關閉裝置              |
| `TUSBAUDIO_GetSupportedSampleRates(handle, max, rates[], &n)`   | 列出支援的取樣率            |
| `TUSBAUDIO_GetCurrentSampleRate(handle, &rate)`                 | 讀取樣率                    |
| `TUSBAUDIO_SetSampleRate(handle, rate)`                         | 設定取樣率                  |
| `TUSBAUDIO_GetASIOInstanceInfo(0, uint[])`                      | 讀 ASIO 狀態（見下文）      |
| `TUSBAUDIO_SetASIOBufferPreferredSize(0, rate, size, 0x10000)`  | 設定 ASIO buffer 大小       |

`GetASIOInstanceInfo` 會填一個 32-bit word 陣列：word 0 是取樣率，word 5 和 word 6 是輸入、輸出的
latency（單位 samples），word 7 是目前的 buffer 大小，word 8 是支援的尺寸數量，尺寸從 word 9 開始。
ASIO 這幾個呼叫不需要裝置 handle。

`dev/asio_info.py` 會印出 ASIO info block，也可以從命令列設 buffer 大小。
