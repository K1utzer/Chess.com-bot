import win32api, win32con
import time

class MouseControl:

    def mousePos(self, x, y):
        try:
            win32api.SetCursorPos((x, y))
        except Exception as e:
            print(e)

    def mouseClick(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.2)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
