import pyautogui
from time import sleep

# sleep(3)
# p = pyautogui.position()
# Next level pos Point(x=240, y=662)
# Box up-left: Point(x=97, y=530)
# Box up-right: Point(x=357, y=532)
# Box bot-right: Point(x=380, y=788)
# Box bot-left: Point(x=84, y=798)

pos_map = {
    "next_level_box": {'x':240, "y":662}
}


def go_to_next_level():
    pyautogui.click(**pos_map['next_level_box'])

go_to_next_level()
# print(p)