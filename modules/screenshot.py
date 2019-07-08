import psutil, autoit, time, pyautogui, ctypes

#Only Windows
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
wantedWindow = None
autopsyProcessId = psutil.Process()
window_process_id = ctypes.c_ulong()

def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        global wantedWindow
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        if "autopsy" in str(buff.value).lower():
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_process_id))
            possibleAutopsyProcess = psutil.Process(window_process_id.value)
            if possibleAutopsyProcess.pid == autopsyProcessId.pid: #or "java" in possibleAutopsyProcess.name():
                wantedWindow = buff.value
            else:
                 for children in autopsyProcessId.children(recursive=True):
                     if children.pid == possibleAutopsyProcess.pid:
                         wantedWindow = buff.value
    return True

def screenshotAutopsy(id):
    global wantedWindow
    global autopsyProcessId
    autopsyProcessId = psutil.Process(id)
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    if wantedWindow is None:
        print("Plz notify admin that autopsy GUI is down")
    else:
        autoit.win_activate(wantedWindow)
        autoit.win_set_state(wantedWindow, flag=autoit.properties.SW_MAXIMIZE)
        autoit.send("!{h}", 0)
        autoit.send("{DOWN}")
        autoit.send("{DOWN}")
        autoit.send("{ENTER}")
        time.sleep(0.5)
        pyautogui.screenshot("miscellaneous/autopsy.png")
        autoit.send("{ESC}")