import ctypes
import logging
import os
import sys
import time
import traceback
import random
import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui
from Module.loadconfig import *
from timeit import default_timer as timer
from PIL import Image
from functools import lru_cache

from functools import lru_cache

@lru_cache(maxsize=128)
def _load_template_cached(img_path, gray):
    flag = cv2.IMREAD_GRAYSCALE if gray else cv2.IMREAD_COLOR
    return cv2.imread(img_path, flag)


fimg = config['VALUE']['FIND_IMG_DELAY']

class GameControl:
    global fimg
    def __init__(self, hwnd, quit_game_enable=1):
        self.run = True
        self.hwnd = hwnd
        self.findimgdelay = config['VALUE']['FIND_IMG_DELAY']
        self.quit_game_enable = quit_game_enable
        self.debug_enable = False

        l1, t1, r1, b1 = win32gui.GetWindowRect(self.hwnd)
        l2, t2, r2, b2 = win32gui.GetClientRect(self.hwnd)
        self._client_h = b2 - t2
        self._client_w = r2 - l2
        self._border_l = ((r1 - l1) - (r2 - l2)) // 2
        self._border_t = ((b1 - t1) - (b2 - t2)) - self._border_l

        self.client = 0
        if self.client == 1:
            from ppadb.client import Client as AbdClient
            client = AbdClient(host='127.0.0.1', port=5037)
            devices = client.devices()

    def stop(self):
        self.run = False

    def init_mem(self):
        self.hwindc = win32gui.GetWindowDC(self.hwnd)
        self.srcdc = win32ui.CreateDCFromHandle(self.hwindc)
        self.memdc = self.srcdc.CreateCompatibleDC()
        self.bmp = win32ui.CreateBitmap()
        self.bmp.CreateCompatibleBitmap(self.srcdc, self._client_w, self._client_h)
        self.memdc.SelectObject(self.bmp)

    def recheckRect(self):
        logging.debug('Detected ChatPanel: GetClientRect')
        l1, t1, r1, b1 = win32gui.GetWindowRect(self.hwnd)
        l2, t2, r2, b2 = win32gui.GetClientRect(self.hwnd)
        self._client_h = b2 - t2
        self._client_w = r2 - l2
        self._border_l = ((r1 - l1) - (r2 - l2)) // 2
        self._border_t = ((b1 - t1) - (b2 - t2)) - self._border_l

    def _buffer_to_img(self, bmp, width, height, gray=0):
        signedIntsArray = bmp.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (height, width, 4)
        if gray:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def window_full_shot(self, file_name=None, gray=0):
        try:
            if not hasattr(self, 'memdc'):
                self.init_mem()
            target = (0, 0) if self.client == 0 else (0, -35)
            self.memdc.BitBlt(target, (self._client_w, self._client_h), self.srcdc,
                              (self._border_l, self._border_t), win32con.SRCCOPY)
            if file_name:
                self.bmp.SaveBitmapFile(self.memdc, file_name)
                return
            return self._buffer_to_img(self.bmp, self._client_w, self._client_h, gray)
        except Exception:
            self.init_mem()
            logging.warning(traceback.format_exc())

    def window_part_shot(self, pos1, pos2, file_name=None, gray=0):
        w = pos2[0] - pos1[0]
        h = pos2[1] - pos1[1]
        hwindc = win32gui.GetWindowDC(self.hwnd)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, w, h)
        memdc.SelectObject(bmp)

        offset = (pos1[0] + self._border_l, pos1[1] + self._border_t)
        if self.client == 0:
            memdc.BitBlt((0, 0), (w, h), srcdc, offset, win32con.SRCCOPY)
        else:
            memdc.BitBlt((0, -35), (w, h), srcdc, offset, win32con.SRCCOPY)

        if file_name:
            bmp.SaveBitmapFile(memdc, file_name)
            self._release_dc(srcdc, memdc, hwindc, bmp)
            return
        img = self._buffer_to_img(bmp, w, h, gray)
        self._release_dc(srcdc, memdc, hwindc, bmp)
        return img

    def _release_dc(self, srcdc, memdc, hwindc, bmp):
        srcdc.DeleteDC()
        memdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwindc)
        win32gui.DeleteObject(bmp.GetHandle())

    def takescreenshot(self, locationsave=''):
        name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        folder_path = os.path.join('./', locationsave)
        os.makedirs(folder_path, exist_ok=True)
        img_src_path = os.path.join(folder_path, f"{name}.png")
        self.window_full_shot(img_src_path)
        logging.info('Take Screenshot: %s', img_src_path)
        return name + '.png'

    def wait_game_img(self, img_path, max_time=100, quit=True):
        start_time = time.time()
        while time.time() - start_time <= max_time and self.run:
            maxVal, maxLoc = self.find_img(img_path)
            if maxVal > 0.9:
                return maxLoc
            time.sleep(1 if max_time > 5 else 0.1)
        if quit:
            self.quit_game()
        return False

    def find_img(self, img_template_path, part=0, pos1=None, pos2=None, gray=0, center=True, delay=fimg):
        if delay > 0:
            time.sleep(delay)

        img_src = self.window_part_shot(pos1, pos2, None, gray) if part == 1 else self.window_full_shot(None, gray)
        
        img_template = _load_template_cached(img_template_path, gray)
        if img_template is None or img_src is None:
            logging.warning(f"Template or source image is None: {img_template_path}")
            return 0, 0

        if (img_src.shape[0] < img_template.shape[0] or img_src.shape[1] < img_template.shape[1]):
            logging.warning(f"Template size {img_template.shape} is larger than source image {img_src.shape}")
            return 0, 0

        try:
            res = cv2.matchTemplate(img_src, img_template, cv2.TM_CCOEFF_NORMED)
            _, maxVal, _, maxLoc = cv2.minMaxLoc(res)

            if self.debug_enable:
                img = self.window_part_shot(pos1, pos2, None, gray) if part == 1 else self.window_full_shot()
                self.img = cv2.rectangle(img, maxLoc, (maxLoc[0] + img_template.shape[1], maxLoc[1] + img_template.shape[0]), (0, 255, 0), 3)
                show_img(img)
                logging.info("Top left point location: %s", maxLoc)
                logging.info("Score: %.4f", maxVal)

            if center:
                maxLoc = [int(maxLoc[0] + img_template.shape[1] / 2), int(maxLoc[1] + img_template.shape[0] / 2)]

            return maxVal, maxLoc

        except Exception as e:
            logging.warning(f"find_img failed: {e}")
            return 0, 0
    
    def find_game_img(self, img_path, part=0, pos1=None, pos2=None, gray=1, center=True, delay=fimg, threshold=0.9):
        maxVal, maxLoc = self.find_img(img_path, part, pos1, pos2, gray, center, delay)
        if maxVal > thread:
            logging.debug('Detected:%s, value:%.4f, pos:%s', img_path, maxVal, maxLoc)
            return list(maxLoc)
        return False

    def quit_game(self):
        self.clean_mem()
        logging.info("Quitting game and cleaning up.")
        sys.exit(0)

    def clean_mem(self):
        self.srcdc.DeleteDC()
        self.memdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwindc)
        win32gui.DeleteObject(self.bmp.GetHandle())


    def send_esc_down(self, getkey='d'):
        '''
        Send Key Down and Key Up
        '''
        if getkey == 'd':
            key = win32con.WM_KEYDOWN
        else:
            key = win32con.WM_KEYUP
        if self.client == 0:
            logging.info('Press "ESC"')
            win32api.PostMessage(self.hwnd, key, win32con.VK_ESCAPE, 0)
        if self.client == 1:
            os.system('adb shell input keyevent 4')

    def mouse_click_bg(self, pos, pos_end=None):
        
        '''
            Background mouse click
            : param pos: (x, y) the coordinates of the mouse click
            : param pos_end = None: (x, y) If pos_end is not empty, 
            the mouse clicks a random position in the area where pos is the upper left corner coordinate pos_end is the lower right corner coordinate
        '''
        if self.debug_enable:
            img = self.window_full_shot()
            self.img = cv2.rectangle(img, pos, None, (255, 0, 0), 3)
            show_img(img)

        if pos_end == None:
            pos_rand = pos
        else:
            pos_rand = (random.randint(
                pos[0], pos_end[0]), random.randint(pos[1], pos_end[1]))
        if self.client == 0:
            # logging.debug("Click:%s" %str(pos_rand))
            #win32gui.SendMessage(self.hwnd, win32con.BM_CLICK,300,300)
            win32gui.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE,
                                 0, win32api.MAKELONG(pos_rand[0], pos_rand[1]))
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN,
                                 0, win32api.MAKELONG(pos_rand[0], pos_rand[1]))
            time.sleep(random.randint(20, 80)/1000)
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP,
                                 0, win32api.MAKELONG(pos_rand[0], pos_rand[1]))

        else:
            command = str(pos_rand[0]) + ' ' + str(pos_rand[1])
            logging.debug('adb shell input tap (pos:%s)'%command)
            os.system('adb shell input tap ' + command)
