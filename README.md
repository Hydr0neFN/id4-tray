# id4-tray

A small Windows tray app for the Audient iD4 MKII. It changes the sample rate and the ASIO buffer size
without the iD mixer application.

**Unofficial.** This project is not affiliated with, endorsed by, or supported by Audient or Thesycon.
"Audient" and "iD" are trademarks of their owners. Use it at your own risk.

## Why

The iD mixer application must stay open to change the sample rate or the buffer size. On some systems
iD 4.4.2 also writes a large log file while it runs. The driver keeps its settings without the
application, so a small tray app is sufficient for these two settings.

## What it does

- Tray icon with a tooltip that shows the current sample rate and ASIO buffer size.
- Menu: sample rate (44.1 / 48 / 88.2 / 96 kHz).
- Menu: ASIO buffer size (8 to 2048 samples).
- Menu: open or close the iD mixer (for the monitor mix and other settings).

It does not replace the iD mixer: monitor mix, loopback and firmware updates still need the iD application.

## Requirements

- Windows 10 or 11, 64-bit.
- The Audient USB audio driver, installed in the default folder
  (`C:\Program Files\Audient\USBAudioDriver\x64\audientusbaudioapi_x64.dll`).
- Python 3.10 or later, 64-bit.

This repository contains no Audient or Thesycon files. The app loads the driver API DLL that the
Audient installer puts on your PC.

## Install and run

```
pip install -r requirements.txt
pythonw id4_tray.py
```

To start it at login, put a shortcut to `pythonw.exe "<path>\id4_tray.py"` in the folder that
`shell:startup` opens.

## Tested with

| Item     | Version                         |
|----------|---------------------------------|
| Device   | Audient iD4 MKII                |
| Driver   | 5.5.1 (`audientusbaudio.sys`)   |
| iD app   | 4.4.2                           |
| OS       | Windows 11 Pro                  |

Other iD interfaces use the same driver family and can work, but they are not tested.
The app controls the first device that the driver lists.

Not verified yet: whether the settings stay after a reboot or after you reconnect the device.

## How it talks to the driver

The driver API DLL exports `TUSBAUDIO_*` functions. The calls that this app uses, found by observation:

| Function                                                        | Use                         |
|-----------------------------------------------------------------|-----------------------------|
| `TUSBAUDIO_EnumerateDevices()`                                  | refresh the device list     |
| `TUSBAUDIO_OpenDeviceByIndex(index, &handle)` / `CloseDevice`   | open and close a device     |
| `TUSBAUDIO_GetSupportedSampleRates(handle, max, rates[], &n)`   | list sample rates           |
| `TUSBAUDIO_GetCurrentSampleRate(handle, &rate)`                 | read the sample rate        |
| `TUSBAUDIO_SetSampleRate(handle, rate)`                         | set the sample rate         |
| `TUSBAUDIO_GetASIOInstanceInfo(0, uint[])`                      | read ASIO state (see below) |
| `TUSBAUDIO_SetASIOBufferPreferredSize(0, rate, size, 0x10000)`  | set the ASIO buffer size    |

`GetASIOInstanceInfo` fills an array of 32-bit words: word 0 is the sample rate, words 5 and 6 are the
input and output latency in samples, word 7 is the current buffer size, word 8 is the number of
supported sizes, and the sizes start at word 9. The ASIO calls take no device handle.

`dev/asio_info.py` prints the ASIO info block and can set a buffer size from the command line.

## License

MIT. See `LICENSE`.
