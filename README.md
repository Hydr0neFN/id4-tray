**English** · [繁體中文](README.zh-TW.md)

# id4-tray

A small Windows tray app for the Audient iD4 MKII. It changes the sample rate and the ASIO buffer size
without the iD mixer application.

**Unofficial.** This project is not affiliated with, endorsed by, or supported by Audient or Thesycon.
"Audient" and "iD" are trademarks of their owners. Use it at your own risk.

## At a glance

| | |
|---|---|
| Problem | The iD mixer application must stay open to change the sample rate or the buffer size. On some systems iD 4.4.2 also writes a large log file while it runs. |
| What I built | A tray app that sets the sample rate and the ASIO buffer size, and opens or closes the iD mixer. |
| Why it can work | The driver keeps its settings without the application, so a small tray app is sufficient for these two settings. |
| Stack | Python 3.10 or later (64-bit), pywin32, Pillow, Thesycon `TUSBAUDIO` driver API. |
| Verified on | Audient iD4 MKII, driver 5.5.1 (`audientusbaudio.sys`), iD app 4.4.2, Windows 11 Pro. |
| Open | Not verified yet: whether the settings stay after a reboot or after you reconnect the device. |

## What it does

- Tray icon with a tooltip that shows the current sample rate and ASIO buffer size.
- Menu: sample rate (44.1 / 48 / 88.2 / 96 kHz).
- Menu: ASIO buffer size (8 to 2048 samples).
- Menu: open or close the iD mixer (for the monitor mix and other settings).

It does not replace the iD mixer: monitor mix, loopback and firmware updates still need the iD application.

## How it works

```
 id4_tray.py (tray icon and menu)
        |
        +-- audientusbaudioapi_x64.dll (Audient driver, Thesycon TUSBAUDIO API)
        |       sample rate and ASIO buffer size
        |
        +-- iD.exe (iD mixer application, opened or closed from the menu)
```

The app controls the first device that the driver lists. The tooltip reads the current sample rate and
ASIO buffer size from the driver.

## Tested with

| Item     | Version                         |
|----------|---------------------------------|
| Device   | Audient iD4 MKII                |
| Driver   | 5.5.1 (`audientusbaudio.sys`)   |
| iD app   | 4.4.2                           |
| OS       | Windows 11 Pro                  |

Other iD interfaces use the same driver family and can work, but they are not tested.

## Build / run

Requirements:

- Windows 10 or 11, 64-bit.
- The Audient USB audio driver, installed in the default folder
  (`C:\Program Files\Audient\USBAudioDriver\x64\audientusbaudioapi_x64.dll`).
- Python 3.10 or later, 64-bit.

```
pip install -r requirements.txt
pythonw id4_tray.py
```

To start it at login, put a shortcut to `pythonw.exe "<path>\id4_tray.py"` in the folder that
`shell:startup` opens.

This repository contains no Audient or Thesycon files. The app loads the driver API DLL that the
Audient installer puts on your PC. The icon (`id4.ico`) is drawn on first run.

## How it talks to the driver

The driver API DLL exports `TUSBAUDIO_*` functions. The calls that this app uses were found by
observation. See [docs/driver-api.md](docs/driver-api.md) for the function list and the layout of the
ASIO info block.

`dev/asio_info.py` prints the ASIO info block and can set a buffer size from the command line.

## Limits and open items

- Not verified yet: whether the settings stay after a reboot or after you reconnect the device.
- Other iD interfaces use the same driver family and can work, but they are not tested.
- Monitor mix, loopback and firmware updates still need the iD application.

## License

MIT. See `LICENSE`.
