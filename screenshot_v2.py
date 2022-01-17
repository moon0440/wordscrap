import math
import string
from datetime import datetime
from pathlib import Path
from time import sleep
import d3dshot
from PIL import Image
import cv2
import numpy as np
import pyautogui
from time import sleep

from image_similarity_measures.quality_metrics import ssim


class GameWin:

    def __init__(self):
        self.game_win_name = 'BlueStacks'
        self.letters_img_dir = './letter_images/'
        self.matching_pct = 0.97
        self.set_game_win_size = dict(width=594, height=1030)
        self.template_match_min = 11_000_000.0
        # self.game_region = self.game_region()
        # self.menu_templates = self.load_menu_templates()
        self.d = d3dshot.create(capture_output="numpy")
        self.last_menu_item_pos = (0,0)
        self.piggy_bank_pos = (362, 182)

        self.load_menu_templates()
        self.load_game_window()
        self.reload_base_images()
        # self.game_region_screenshot = self.game_region_screenshot()

    def reload_base_images(self):
        self.letter_base_images = {}
        dir_list = list(string.ascii_uppercase) + ["NONE"]
        for x in dir_list:
            Path(f'{self.letters_img_dir}{x}').mkdir(parents=True, exist_ok=True)
            if not x in self.letter_base_images.keys():
                self.letter_base_images[x] = []
            for f in Path(f'{self.letters_img_dir}{x}').glob('*.png'):
                # print(f)
                self.letter_base_images[x].append(
                    np.array(Image.open(f, formats=['PNG']))
                )


    def load_game_window(self):
        if not any([w.title == self.game_win_name for w in pyautogui.getAllWindows()]):
            raise Exception(f"Cannot find window with name {self.game_win_name}")

        self.game_win = pyautogui.getWindowsWithTitle(self.game_win_name)[0]
        self.game_win.activate()
        self.game_win.moveTo(0, 0)
        self.game_win.resizeTo(self.set_game_win_size['width'], self.set_game_win_size['height'])

    # @property
    # def game_win(self):
    #     return pyautogui.getWindowsWithTitle(self.game_win_name)[0]

    def load_menu_templates(self):
        files = list(Path(r'./menu_images').glob('**/*.png'))
        menu_templates = {f.parent.name:[] for f in files}
        for f in files:
            menu_templates[f.parent.name].append( dict(
                img=np.array(Image.open(f, formats=['PNG']))
            ))

        self.menu_templates = menu_templates

    def menu_item_on_screen(self):
        return self.select_menu_templates(self, click=False)

    def select_menu_templates(self, click=True):
        n = self.game_region_screenshot
        mt = self.menu_templates
        game_win = cv2.cvtColor(n, cv2.COLOR_BGR2GRAY)
        for k,v in mt.items():

            for template in v:
                template_img = cv2.cvtColor(template['img'], cv2.COLOR_BGR2GRAY)
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
        left, top, right, bottom = self.game_win.box
        region = (left, top, right-left, bottom-top)
        return region

    @property
    def letters_region(self):
        left, top, right, bottom = 101, 653, 459, 1011
        region = (left, top, right, bottom)
        return region

    @property
    def game_region_screenshot(self):
        n = self.d.screenshot(region=self.game_region)
        n[n < 255] = 0

        return n

    @property
    def letters_region_screenshot(self):
        n = self.d.screenshot(region=self.letters_region)
        print(f"WhitePixels: {len(n[n == 255])} -- BlackPixels: {len(n[n == 0])}")
        if len(n[n == 0]) > len(n[n == 255]):
            n[n > 0] = 255

        return n


    @property
    def game_offset(self):
        # Returns H and W offsets based on game region
        left, top, _, _ = self.game_region
        return (left, top)

    @property
    def datetime_filename(self):
        now = datetime.now().isoformat()
        return now.split('.')[0].replace("-",'').replace(':','')

    def edge_detect_letters(self):
        return cv2.Canny(self.letters_region_screenshot, 25, 100)

    def edge_detect_screenshot(self):
        return cv2.Canny(self.game_region_screenshot, 50, 200)

    def save_screenshot(self):
        im = Image.fromarray(self.edge_detect_screenshot())
        im = Image.fromarray(self.game_region_screenshot)
        # im = Image.fromarray(self.letters_region_screenshot)
        im.save(f"./temp_images/{self.datetime_filename}.png")

    def show_screenshot(self):
        im = Image.fromarray(self.edge_detect_screenshot())
        im.show()

    def letter_boxes(self):
        letters = []
        force_restart = False
        org_img = Image.fromarray(self.letters_region_screenshot)  # 1
        img = np.array(org_img)
        # img = self.edge_detect_letters()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
        # cv2.imshow('thresh', thresh)
        ctrs, hier = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
        pad = 5
        for i, ctr in enumerate(sorted_ctrs):
            x, y, w, h = cv2.boundingRect(ctr)
            roi = img[y + pad:y + h + pad, x + pad:x + w + pad]

            # if h > 30:
            #     print(w,h)

            # if 52 < h < 65: # for 5 chars
            box_size = 60
            if 47 <= h <= 61:
                w_diff, h_diff = box_size - w, box_size - h
                x = x - math.floor(w_diff / 2)
                y = y - math.floor(h_diff / 2)
                w, h = box_size, box_size
                rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow('rect', rect)

                letter_box_img = Image.fromarray(thresh).crop((x - pad, y - pad, x + w + pad, y + h + pad))

                letter=False
                sim_dict = {}
                best = 0.0
                for k, v in self.letter_base_images.items():
                    for letter_sample in v:
                        sim = ssim(np.array(letter_box_img), letter_sample)
                        best = sim if sim > best else best
                        sim_dict[k] = sim
                        if sim >= self.matching_pct:
                            # if sim <= matching_pct:
                            letter = k
                            break
                    if letter:
                        break
                print(f"Best: {best:.02f} -- Letter: {letter}")
                if not letter and letter != "NONE":
                    letter_box_img.show()
                    # cv2.imshow('rect', rect)
                    letter_input = input(f"Best Match={best:.02f} -- What is this letter: ")
                    for i in range(0, 1000):
                        fn = f"{self.letters_img_dir}{letter_input.upper()}/{i:04d}.png"
                        if not Path(fn).exists():
                            break

                    # input(f"LETTER ALREADY EXISTS!!!: {sim_dict[letter_input]}")
                    letter_box_img.save(fn)
                    self.reload_base_images()

                    return None, True

                letters.append({
                    'letter': letter,
                    'x': int(x+(w/2)+self.letters_region[0]),
                    'y': int(y+(h/2)+self.letters_region[1])
                })

        return letters, force_restart


def main():
    gw = GameWin()
    gw.save_screenshot()
    # gw.show_screenshot()
    gw.letter_boxes()
    # for _ in range(0,100):
    #     sleep(3)
    #     gw.check_menu_templates():
        # gw.select_menu_templates(click=False)


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