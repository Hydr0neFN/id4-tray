"""Tray app for the Audient iD4 MKII: sample rate and ASIO buffer size without iD.exe.

Run: pythonw id4_tray.py
Talks to the driver through audientusbaudioapi_x64.dll (Thesycon TUSBAUDIO API).
Needs pywin32 and Pillow (icon is drawn on first run).
"""
import ctypes as C
import os
import subprocess
import sys

import win32api
import win32con
import win32event
import win32gui
import winerror

HERE = os.path.dirname(os.path.abspath(__file__))
API_DLL = r"C:\Program Files\Audient\USBAudioDriver\x64\audientusbaudioapi_x64.dll"
ID_EXE = r"C:\Program Files\Audient\iD\iD.exe"
ICON = os.path.join(HERE, "id4.ico")
CLASS_NAME = "Id4TrayWindow"
WM_TRAY = win32con.WM_USER + 20
CMD_RATE = 1000  # + index into the rate list
CMD_BUF = 1100  # + index into the buffer size list
CMD_OPEN_ID = 2001
CMD_CLOSE_ID = 2002
CMD_EXIT = 2003
u = C.c_uint

api = C.WinDLL(API_DLL)
api.TUSBAUDIO_StatusCodeStringA.restype = C.c_char_p


def _status(st):
    return api.TUSBAUDIO_StatusCodeStringA(u(st & 0xFFFFFFFF)).decode()


class Device:
    """Open the first iD device for one operation, then close it (survives a replug)."""

    def __enter__(self):
        api.TUSBAUDIO_EnumerateDevices()
        self.h = u(0)
        st = api.TUSBAUDIO_OpenDeviceByIndex(u(0), C.byref(self.h))
        if st != 0:
            raise OSError("iD4 not found: " + _status(st))
        return self.h

    def __exit__(self, *exc):
        api.TUSBAUDIO_CloseDevice(self.h)


def get_rate():
    with Device() as h:
        r = u(0)
        st = api.TUSBAUDIO_GetCurrentSampleRate(h, C.byref(r))
        if st != 0:
            raise OSError(_status(st))
        return r.value


def get_rates():
    with Device() as h:
        arr = (u * 32)()
        n = u(0)
        st = api.TUSBAUDIO_GetSupportedSampleRates(h, u(32), arr, C.byref(n))
        if st != 0:
            raise OSError(_status(st))
        return list(arr[: n.value])


def set_rate(rate):
    with Device() as h:
        st = api.TUSBAUDIO_SetSampleRate(h, u(rate))
        if st != 0:
            raise OSError(_status(st))


def get_asio():
    """Return (sample rate, current buffer size, supported sizes), all in samples.

    Layout of the info block (driver 5.5.1): word 0 rate, 5/6 in/out latency,
    7 current size, 8 count, 9.. sizes.
    """
    api.TUSBAUDIO_EnumerateDevices()
    buf = (u * 512)()
    st = api.TUSBAUDIO_GetASIOInstanceInfo(u(0), buf)
    if st != 0:
        raise OSError(_status(st))
    n = min(buf[8], 32)
    return buf[0], buf[7], list(buf[9:9 + n])


def set_buffer(size):
    rate = get_asio()[0]
    st = api.TUSBAUDIO_SetASIOBufferPreferredSize(u(0), u(rate), u(size), u(0x10000))
    if st != 0:
        raise OSError(_status(st))


def id_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq iD.exe", "/NH"], capture_output=True, text=True,
                         creationflags=0x08000000).stdout
    return "iD.exe" in out


def make_icon():
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, 61, 61), radius=12, fill=(28, 28, 30, 255), outline=(240, 240, 240, 255), width=3)
    try:
        font = ImageFont.truetype("arialbd.ttf", 34)
    except OSError:
        font = ImageFont.load_default()
    d.text((32, 32), "iD", font=font, fill=(255, 255, 255, 255), anchor="mm")
    img.save(ICON, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)])


class Tray:
    def __init__(self):
        self.rates = []
        self.bufs = []
        self.tip = ""
        self.taskbar_created = win32gui.RegisterWindowMessage("TaskbarCreated")
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = CLASS_NAME
        wc.lpfnWndProc = {
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_TIMER: self.on_timer,
            WM_TRAY: self.on_tray,
            self.taskbar_created: self.on_taskbar_created,
        }
        win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(CLASS_NAME, "iD4 tray", 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
        if not os.path.exists(ICON):
            make_icon()
        self.hicon = win32gui.LoadImage(0, ICON, win32con.IMAGE_ICON, 0, 0,
                                        win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        self.add_icon()
        C.windll.user32.SetTimer(self.hwnd, 1, 5000, None)

    def make_tip(self):
        try:
            return "iD4: %.1f kHz, buffer %d" % (get_rate() / 1000, get_asio()[1])
        except OSError:
            return "iD4: not connected"

    def add_icon(self):
        self.tip = self.make_tip()
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, (self.hwnd, 0, flags, WM_TRAY, self.hicon, self.tip))

    def refresh_tip(self):
        tip = self.make_tip()
        if tip != self.tip:
            self.tip = tip
            flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, (self.hwnd, 0, flags, WM_TRAY, self.hicon, tip))

    def on_taskbar_created(self, hwnd, msg, wp, lp):
        self.add_icon()
        return 0

    def on_timer(self, hwnd, msg, wp, lp):
        self.refresh_tip()
        return 0

    def on_tray(self, hwnd, msg, wp, lp):
        if lp in (win32con.WM_RBUTTONUP, win32con.WM_LBUTTONUP):
            self.show_menu()
        return 0

    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        try:
            self.rates = get_rates()
            cur = get_rate()
            for i, r in enumerate(self.rates):
                flags = win32con.MF_STRING | (win32con.MF_CHECKED if r == cur else 0)
                win32gui.AppendMenu(menu, flags, CMD_RATE + i, "%.1f kHz" % (r / 1000))
            _, cur_buf, self.bufs = get_asio()
            sub = win32gui.CreatePopupMenu()
            for i, b in enumerate(self.bufs):
                flags = win32con.MF_STRING | (win32con.MF_CHECKED if b == cur_buf else 0)
                win32gui.AppendMenu(sub, flags, CMD_BUF + i, "%d samples" % b)
            win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
            win32gui.AppendMenu(menu, win32con.MF_POPUP, sub, "ASIO buffer: %d samples" % cur_buf)
        except OSError:
            win32gui.AppendMenu(menu, win32con.MF_STRING | win32con.MF_GRAYED, 0, "iD4 not connected")
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
        if id_running():
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_CLOSE_ID, "Close iD mixer (stops its log)")
        else:
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_OPEN_ID, "Open iD mixer (monitor mix)")
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
        win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_EXIT, "Exit")
        x, y = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, x, y, 0, self.hwnd, None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def on_command(self, hwnd, msg, wp, lp):
        cmd = win32api.LOWORD(wp)
        try:
            if CMD_RATE <= cmd < CMD_RATE + 32:
                if not self.rates:
                    self.rates = get_rates()
                set_rate(self.rates[cmd - CMD_RATE])
                self.refresh_tip()
            elif CMD_BUF <= cmd < CMD_BUF + 32:
                if not self.bufs:
                    self.bufs = get_asio()[2]
                set_buffer(self.bufs[cmd - CMD_BUF])
                self.refresh_tip()
            elif cmd == CMD_OPEN_ID:
                subprocess.Popen([ID_EXE], cwd=os.path.dirname(ID_EXE))
            elif cmd == CMD_CLOSE_ID:
                subprocess.run(["taskkill", "/IM", "iD.exe", "/F"], capture_output=True, creationflags=0x08000000)
            elif cmd == CMD_EXIT:
                win32gui.DestroyWindow(self.hwnd)
        except OSError as e:
            win32gui.MessageBox(self.hwnd, str(e), "iD4 tray", win32con.MB_ICONWARNING)
        return 0

    def on_destroy(self, hwnd, msg, wp, lp):
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, 0))
        win32gui.PostQuitMessage(0)
        return 0


def main():
    mutex = win32event.CreateMutex(None, False, "Id4TraySingleInstance")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        sys.exit(0)
    Tray()
    win32gui.PumpMessages()
    del mutex


if __name__ == "__main__":
    main()
