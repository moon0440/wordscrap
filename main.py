import pickle
import pyautogui
import nltk
from itertools import permutations
from time import sleep
from pathlib import Path
import enchant
from spellchecker import SpellChecker

from get_screenshot import go_again, scrn_shot
import sys

from screenshot_v2 import GameWin

word_file = 'words.pkl'
if not Path(word_file).exists():
    all_words = nltk.corpus.brown.words() + nltk.corpus.words.words() + nltk.corpus.abc.words()
    # english_vocab1 = list(w.upper() for w in all_words)
    english_vocab = set(w.upper() for w in all_words)
    with open(word_file, 'wb') as handle:
        pickle.dump(english_vocab, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(word_file, 'rb') as handle:
    english_vocab = pickle.load(handle)

up_left_x = 82
up_left_y = 520
box_size = 285
region = (up_left_x, up_left_y, up_left_x + box_size, up_left_y + box_size)
# fn = lambda x: 0 if x > thresh else 255
thresh = 10
fn = lambda x: 0 if x < thresh else 255
# e = enchant.Dict("en_US")
spell = SpellChecker()

def solve_word(letter_pos):
    for k, v in letter_pos.items():
        pyautogui.moveTo(v['x'], v['y'], duration=1)


def solve_words(words, letter_pos, gw):
    for i,w in enumerate(words):
        sleep(0.25)
        if gw.select_menu_templates(click=False):
            break
        print(f"Solving {i}/{len(words)} possible words -> {w}")
        pos_used = []

        for l in w:
            cur_pos = next((index for (index, d) in enumerate(letter_pos) if d["letter"] == l and index not in pos_used), None)
            pos_used.append(cur_pos)
            pyautogui.moveTo(letter_pos[cur_pos]['x'], letter_pos[cur_pos]['y'], duration=0.05)
            if len(pos_used) == 1:
                pyautogui.mouseDown(button='left')
        pyautogui.mouseUp(button='left')

def start_level():
    # Point(x=226, y=667)
    pyautogui.moveTo(226, 676, duration=0.05)
    pyautogui.click()
    sleep(1)


def next_level():
    print("Waiting before starting next level...")
    sleep(10)
    # input("go again?")

def possible_words(letter_pos):
    st = ''.join([l['letter'] for l in letter_pos if l['letter'] != "NONE"])
    print(f"Found letters: {st}")
    words = []
    for l in range(len(st),2,-1):
        st_perms = [''.join(i).upper() for i in permutations(st, l)]
        # new_words = [w for w in st_perms if e.check(w)]
        new_words = [w.upper() for w in spell.known(st_perms)]

        words.extend(new_words)
        # english_vocab = set(w.upper() for w in all_words)
        # words.extend(english_vocab.intersection(st_perms))
    # words = list(set(words))
    return sorted(list(set(words)), key=len, reverse=True)


def main():
    gw = GameWin()
    while True:
        while gw.select_menu_templates():
            sleep(1)

        # start_level()
        restart = True
        while restart:
            letter_pos, restart = scrn_shot(region)
            if gw.select_menu_templates(click=False):
                break
        words = possible_words(letter_pos)
        solve_words(words, letter_pos, gw)
        # while not gw.select_menu_templates():
        #     sleep(1)



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # do nothing here
        sys.exit(0)
