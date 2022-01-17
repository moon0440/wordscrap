from pathlib import Path
from time import sleep

import d3dshot
from PIL import Image
import cv2
import numpy as np
import pyautogui

class GameWin:
    def __init__(self):
        self.template_match_min = 10_000_000.0
        # self.game_region = self.game_region()
        # self.menu_templates = self.load_menu_templates()
        self.d = d3dshot.create(capture_output="numpy")
        self.last_menu_item_pos = (0,0)
        self.piggy_bank_pos = (362, 182)

        self.load_menu_templates()
        # self.game_region_screenshot = self.game_region_screenshot()


    def load_menu_templates(self):
        files = list(Path(r'./menu_images').glob('**/*.png'))
        menu_templates = {f.parent.name:[] for f in files}
        for f in files:
            menu_templates[f.parent.name].append(np.array(Image.open(f, formats=['PNG'])))

        self.menu_templates = menu_templates

    def select_menu_templates(self, click=True):
        n = self.game_region_screenshot
        mt = self.menu_templates
        game_win = cv2.cvtColor(n, cv2.COLOR_BGR2GRAY)
        for k,v in mt.items():
            for template in v:
                template_img = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                result = cv2.matchTemplate(game_win, template_img, cv2.TM_CCOEFF)
                (_, max_val, _, max_loc) = cv2.minMaxLoc(result)
                # print(k,max_val)
                if max_val > self.template_match_min:
                    print(f"Found template on-screen -> {k} with maxVal of {max_val}")
                    if click and k != 'PIGGYBANK':
                        self.click_center_template(template_img, max_loc)
                    elif click and k == 'PIGGYBANK':
                        pyautogui.moveTo(self.piggy_bank_pos)
                        pyautogui.click()
                    return True

        # print("nothing found")
        return False

    def click_center_template(self, template_img, max_loc):
        (h, w) = template_img.shape[:2]
        template_center = (w/2, h/2)
        c = tuple((np.array(max_loc) + np.array(template_center) + np.array(self.game_offset)).astype(int))
        self.last_menu_item_pos = c
        pyautogui.moveTo(c)
        pyautogui.click()

    @property
    def game_region(self):
        left, top, right, bottom = 3, 35, 450, 860
        region = (left, top, right-left, bottom-top)
        return region

    @property
    def game_region_screenshot(self):
        n = self.d.screenshot(region=self.game_region)
        n[n < 255] = 0
        return n
    @property
    def game_offset(self):
        # Returns H and W offsets based on game region
        left, top, _, _ = self.game_region
        return (left, top)

    def edge_detect(n):
        return cv2.Canny(n, 50, 200)

    def save_screenshot(self):
        self.game_region_screenshot
        im = Image.fromarray(self.game_region_screenshot).convert("L")
        im.save(f"./menu_images/last.png")

def main():
    gw = GameWin()
    gw.save_screenshot()
    # for _ in range(0,100):
    #     sleep(3)
    #     # gw.check_menu_templates():
    #     gw.select_menu_templates(click=False)


    # d = d3dshot.create(capture_output="numpy")
    # n = d.screenshot(region=game_region())
    # n[n < 255] = 0
    # im = Image.fromarray(n).convert("L")
    # im.show()
    #
    # found = None
    #
    # mt = menu_templates()
    # game_win = cv2.cvtColor(n, cv2.COLOR_BGR2GRAY)
    # level_template = cv2.cvtColor(mt['level'][0], cv2.COLOR_BGR2GRAY)
    # result = cv2.matchTemplate(game_win, level_template, cv2.TM_CCOEFF)
    # (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
    # print(maxVal)
    # # 4_863_113.5 - NOT on screen
    # # 23_263_432.0 - on screen
    # (h, w) = mt['level'][0].shape[:2]
    # template_center = (w/2, h/2)
    # # (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    # # (endX, endY) = (int((maxLoc[0] + w) * r), int((maxLoc[1] + h) * r))
    # go = game_offset()
    # c = tuple((np.array(maxLoc) + np.array(template_center) + np.array(go)).astype(int))
    # # c = tuple((np.array(maxLoc) + np.array(template_center)).astype(int))
    # # Point(x=191, y=479)
    # pyautogui.moveTo(c)

    print('debug')


if __name__ == "__main__":
    main()