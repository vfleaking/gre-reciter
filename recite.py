# -*- coding: utf-8 -*-

import os.path
import random
import os
import requests
import sys
import playsound
import threading
import math
import json
from queue import Queue
import numpy as np

# ======== constants ========

BUS = 10
BUN = 6
BU = 20
BR = 3

# ======== functions ========

def edit_distance(seq1, seq2):  
    n = len(seq1) + 1
    m = len(seq2) + 1
    dp = np.zeros((n, m))
    for x in range(n):
        dp[x, 0] = x
    for y in range(m):
        dp[0, y] = y

    for x in range(1, n):
        for y in range(1, m):
            c = 0 if seq1[x - 1] == seq2[y - 1] else 1
            dp[x, y] = min(
                dp[x - 1, y] + 1,
                dp[x - 1, y - 1] + c,
                dp[x, y - 1] + 1
            )
    return dp[n - 1, m - 1]

def load_data():
    if not os.path.isfile('data'):
        words = []
        cur_word = []
        with open('3000_QA.txt', 'r') as f:
            while True:
                line = f.readline()
                if line == '':
                    break
                if line == '\n':
                    if cur_word != []:
                        words.append(cur_word)
                        cur_word = []
                else:
                    if line[0] == 'A':
                        line = line[:2] + ' ' + line[6:]
                    if line[-1] != '\n':
                        line += '\n'
                    cur_word.append(line)
        if cur_word != []:
            words.append(cur_word)

        for i in range(len(words)):
            words[i] = { 'Q': words[i][0], 'A': words[i][1:], 'R': [] }
        ts = 0

        with open('data', 'wb') as f:
            f.write(json.dumps((words, ts), ensure_ascii=False, indent=4).encode('utf-8'))
    else:
        with open('data', 'r') as f:
            words, ts = json.loads(f.read())
    return words, ts

def word_word(word):
    return word['Q'][2:].split()[0]

def word_play(word):
    try:
        w = word_word(word)

        if not os.path.isdir('pronu'):
            os.mkdir('pronu')

        if not os.path.isfile('pronu/' + w + '.mp3'):
            url = 'http://www.iciba.com/' + w
            text = requests.get(url).text
            x = text.find(u'<span>美')
            if x == -1:
                return
            x = text.find('<i class="new-speak-step"', x)
            if x == -1:
                return
            x = text.find('sound(', x)
            if x == -1:
                return
            x += 7
            y = text.find("'", x)
            if y == -1:
                return
            sound_url = text[x:y]

            with open('pronu/' + w + '.mp3', 'wb') as f:
                f.write(requests.get(sound_url).content)

        playsound.playsound('pronu/' + w + '.mp3')
    except Exception as e:
        print(e)
        return

class WordPlayThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._queue = Queue()
        self.daemon = True

    def play(self, word):
        self._queue.put(word)

    def run(self):
        while True:
            word = self._queue.get()
            word_play(word)

wp_thread = WordPlayThread()
wp_thread.start()

# 
# Estimate the probability that the user remembers the word
# 
# word: a dict which stores all the information about the word
# word['Q']: the spelling and the pronunciation of the word
# word['A']: the explanation of the word
# word['R']: a list of (r, t) in the increasing order of t.
#            (0, t): the user did NOT remember the word at timestamp t
#            (1, t): the user did     remember the word at timestamp t
# 
# Feel free to modify this function if the current algorithm does not fit you well
# 
def word_acc(word):
    if word['R'] == []:
        return 1.0
    beta = 0.6
    val = 0.0
    for r, t in word['R']:
        val = val * beta + r
    val /= (1 - beta ** len(word['R'])) / (1 - beta)
    return val

#
# return the unnormalized probability that the word will be chosen
#
# Feel free to modify this function if the current algorithm does not fit you well
# 
def word_p(word):
    if word['R'] == []:
        return 1.0
    if word['R'][-1][0] == 0:
        return 10.0
    return math.exp(math.log(8) * (1 - word_acc(word)))

def get_intractable():
    return sorted(filter(lambda word: word_acc(word) == 0, words), key=lambda word: len(word['R']), reverse=True)

def word_r(word):
    s = ''
    for r, t in word['R']:
        if r == 1:
            s += 'O'   # remember
        else:
            s += 'X'   # not remember
    return s

def show_word(word, interactive=True):
    print(word['Q'], end='')
    if interactive:
        print()
        input('Press Enter to continue')
        print()
        wp_thread.play(word)
    for line in word['A']:
        print(line, end='')
    print()
    print('history:', word_r(word))

def rand_word():
    tot = 0.0
    for word in words:
        tot += word_p(word)

    r = random.random() * tot
    for word in words:
        r -= word_p(word)
        if r <= 0:
            return word
    return words[-1]

def print_stat():
    cnt_learned = 0
    cnt_learning = 0
    cnt_meet = 0
    tot_p = 0.0
    for word in words:
        tot_p += word_p(word)
        if len(word['R']) == 0:
            continue
        cnt_meet += 1
        q = word['R'][-2:]
        if all((r == 1 for r, t in q)):
            cnt_learned += 1
        q = word['R'][-5:]
        if any((r == 0 for r, t in q)):
            cnt_learning += 1

    print('total word weights:', '%.3f' % tot_p)
    print('learned:', cnt_learned, '%.2f%%' % (100.0 * cnt_learned / len(words)))
    print('learning:', cnt_learning, '%.2f%%' % (100.0 * cnt_learning / len(words)))
    print('intractable:', len(get_intractable()))
    print('meet:', cnt_meet, '%.2f%%' % (100.0 * cnt_meet / len(words)))
    print()

def do_you_remember():
    print('Is it the explanation in your memory?')
    print('No: Press Enter.    Yes: Any character + Enter.')
    return input() != ''

# ======== main ========

words, ts = load_data()

if len(sys.argv) == 2:
    if sys.argv[1] == 'list-intractable':
        intra = get_intractable()
        print("intractable:", "(" + str(len(intra)), "word(s) in total)", end=' ')
        for word in intra:
            print(word_word(word), end=' ')
        print()
        for word in intra:
            if word_acc(word) == 0:
                show_word(word, interactive=False)
                print()
        sys.exit()
    if sys.argv[1] == 'list':
        li = []
        for word in words:
            li.append((word_p(word), word))
        li.sort(key=lambda x: -x[0])
        for w, word in li:
            show_word(word, interactive=False)
            print()
        sys.exit()
    if sys.argv[1] == 'test':
        shuffled_words = words[:]
        random.shuffle(shuffled_words)
        passed = 0
        for i, word in enumerate(shuffled_words):
            os.system('clear')
            print('#' + str(i + 1))
            print("%.2f%%" % (passed / (i + 1) * 100))
            print()
            show_word(word)
            if do_you_remember():
                passed += 1
        sys.exit()

ts0 = ts

last_word = None
while True:
    batch = []
    for b in range(BUS):
        word = rand_word()
        while word in batch or (b < BUN and word['R'] != []):
            word = rand_word()
        batch.append(word)
    
    lw = [(word, min((edit_distance(word_word(word), word_word(b)) for b in batch))) for word in words]
    random.shuffle(lw)
    lw = filter(lambda wk: wk[1] != 0, lw)
    lw = sorted(lw, key=lambda wk: wk[1])
    for word, k in lw[:BU - BUS]:
        batch.append(word)

    ts0 = ts

    for i in range(BR):
        dl = []

        random.shuffle(batch)

        for wi in range(len(batch)):
            word = batch[wi]

            ts += 1
            os.system('clear')
            print('#' + str(ts), '[Round %d-%d, %d/%d words, start: #%d]' % (i + 1, wi + 1, len(batch) - len(dl), BU, ts0))
            print_stat()
            show_word(word)

            if do_you_remember():
                a = 1
                dl.append(wi)
            else:
                a = 0
            word['R'].append((a, ts))

        for i in reversed(range(len(dl))):
            del batch[dl[i]]

        if not batch:
            break

    with open('data', 'wb') as f:
        f.write(json.dumps((words, ts), ensure_ascii=False, indent=4).encode('utf-8'))
