**English** · [繁體中文](driver-api.zh-TW.md)

[Back to README](../README.md)

# How id4-tray talks to the driver

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
