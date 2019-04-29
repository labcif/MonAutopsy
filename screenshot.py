import autoit
import ctypes
import pyautogui as ImageGrab

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible


def foreach_window(hwnd, lParam):
    global wantedWindow
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        if "Autopsy" in buff.value:
            wantedWindow = buff.value
            return True


EnumWindows(EnumWindowsProc(foreach_window), 0)

if wantedWindow is not None:
    autoit.win_activate(wantedWindow)
    autoit.win_set_state(wantedWindow, flag=3)
    image = ImageGrab.screenshot()
    image.crop()
    image.save('screenshot.jpg')
