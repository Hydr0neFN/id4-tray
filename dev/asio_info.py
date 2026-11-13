"""Read ASIO instance info; optional: set the preferred ASIO buffer size (samples).

Usage: python asio_info.py [size]
Tested with driver 5.5.1 and an iD4 MKII.
"""
import ctypes as C
import sys

api = C.WinDLL(r"C:\Program Files\Audient\USBAudioDriver\x64\audientusbaudioapi_x64.dll")
api.TUSBAUDIO_StatusCodeStringA.restype = C.c_char_p
u = C.c_uint


def name(st):
    return api.TUSBAUDIO_StatusCodeStringA(u(st & 0xFFFFFFFF)).decode()


def info():
    buf = (u * 512)()
    st = api.TUSBAUDIO_GetASIOInstanceInfo(u(0), buf)
    return st, list(buf)


api.TUSBAUDIO_EnumerateDevices()
st, b = info()
print("GetASIOInstanceInfo:", name(st))
last = max((i for i, v in enumerate(b) if v), default=0)
for i in range(0, last + 1, 8):
    print("%3d (0x%03x):" % (i, i * 4), " ".join("%10d" % v for v in b[i:i + 8]))
if len(sys.argv) > 1 and st == 0:
    size = int(sys.argv[1])
    st2 = api.TUSBAUDIO_SetASIOBufferPreferredSize(u(0), u(b[0]), u(size), u(0x10000))
    print("SetASIOBufferPreferredSize(0, %d, %d, 0x10000):" % (b[0], size), name(st2))
    st, b2 = info()
    diff = [(i, b[i], b2[i]) for i in range(512) if b[i] != b2[i]]
    print("changed words (index, before, after):", diff)
