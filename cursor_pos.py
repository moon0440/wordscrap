import pyautogui
from time import sleep
sleep(3)
for _ in range(4):
    sleep(2)
    p = pyautogui.position()
    print(p)