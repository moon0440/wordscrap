from pathlib import Path
import math

import string
from cv2 import cv2
import numpy as np
import d3dshot
from PIL import Image, ImageFilter
from image_similarity_measures.quality_metrics import rmse, ssim, sre, fsim
import sys
import time


matching_pct = 0.95
gettrace = getattr(sys, 'gettrace', None)
SHOW = gettrace
SHOW = False
# SHOW = True
d = d3dshot.create()
net = cv2.dnn.readNet('frozen_east_text_detection.pb')
img_path = './letter_images/'
letter_base_images = {}





# letter_base_images = {c: np.array(Image.open(f"{img_path}{c}.png", formats=['PNG'])) for c in string.ascii_uppercase if Path(f"{img_path}{c}.png").exists()}
# p = Path(r'C:\Users\akrio\Desktop\Test').glob('**/*')
# files = [x for x in p if x.is_file()]


def reload_base_images():
    global letter_base_images
    dir_list = list(string.ascii_uppercase) + ["NONE"]
    for x in dir_list:
        Path(f'{img_path}{x}').mkdir(parents=True, exist_ok=True)
        if not x in letter_base_images.keys():
            letter_base_images[x] = []
        for f in Path(f'{img_path}{x}').glob('*.png'):
            # print(f)
            letter_base_images[x].append(
                np.array(Image.open(f, formats=['PNG']))
            )

reload_base_images()


def scrn_shot(region):
    letters = []
    force_restart = False
    # org_img = d.screenshot(region=region).reduce(3)
    org_img = d.screenshot(region=region)
    img = np.array(org_img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if SHOW:
        cv2.imshow('gray', gray)

    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    if SHOW:
        cv2.imshow('thresh', thresh)

    # im2, ctrs, hier = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    ctrs, hier = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

    pad = 5
    for i, ctr in enumerate(sorted_ctrs):
        x, y, w, h = cv2.boundingRect(ctr)

        roi = img[y+pad:y + h+pad, x+pad:x + w+pad]

        if h > 30 and SHOW:
            print(w,h)
        # if 52 < h < 65: # for 5 chars
        if 47 <= h < 52: # for 6 chars
            w_diff = 55 - w
            h_diff = 55 - h
            x = x - math.floor(w_diff/2)
            w = 55
            y = y - math.floor(h_diff / 2)
            h = 55
            # print(x, w, y, h)
            rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if SHOW:
                cv2.imshow('rect', rect)

            letter_box_img= Image.fromarray(thresh).crop((x-pad, y-pad, x + w+pad, y + h+pad))#.filter(ImageFilter.ModeFilter(size=1))
            letter = False
            sim_dict = {}
            best = 0.0
            for k,v in letter_base_images.items():
                for letter_sample in v:
                    sim = ssim(np.array(letter_box_img), letter_sample)
                    best = sim if sim > best else best
                    sim_dict[k] = sim
                    if sim >= matching_pct:
                    # if sim <= matching_pct:
                        letter = k
                        break
                if letter:
                    break
            print(f"Best: {best:.02f} -- Letter: {letter}")


            if not letter and not SHOW and letter != "NONE":
                letter_box_img.show()
                letter_input = input(f"Best Match={best:.02f} -- What is this letter: ")
                for i in range(0,1000):
                    fn = f"{img_path}{letter_input.upper()}/{i:04d}.png"
                    if not Path(fn).exists():
                        break

                # input(f"LETTER ALREADY EXISTS!!!: {sim_dict[letter_input]}")
                letter_box_img.save(fn)
                reload_base_images()
                return None, True
            letters.append({
                'letter': letter,
                'x': int(x+(w/2)+region[0]),
                'y': int(y+(h/2)+region[1])
            })

    if SHOW:
        cv2.waitKey(0)
    # if len(letters) != 6:
    #     print("Did not find 5 words... restarting")
    #     force_restart = True
    return letters, force_restart

def go_again(region, letters):
    time.sleep(1.0)
    new_letters = scrn_shot(region)
    print(letters)
    print(new_letters)
    return len(letters) == len(new_letters)