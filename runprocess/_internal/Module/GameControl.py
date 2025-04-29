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

class GameControl:
    def __init__(self, hwnd, load_templates, mode=0, quit_game_enable=1):
        self.run = True
        self.hwnd = hwnd
        self.findimgdelay = config['VALUE']['FIND_IMG_DELAY']
        self.quit_game_enable = quit_game_enable
        self.debug_enable = False
        self.mode = mode
        self.templates = {}           # <<<<<<<<<< สำคัญ!
        self.template_labels = {}      # <<<<<<<<<< สำคัญ!
        self.color_templates = set()   # <<<<<<<<<< สำคัญ!
        self.gray_templates = set()    # <<<<<<<<<< สำคัญ!
        self.exclude_log_templates = set()

        self._init_capture()


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
        
        # กำหนดชื่อรูปที่ไม่ต้อง log
        self.exclude_log_templates = {
            # "IMAGE_BACK2",
            "IMAGE_REALM_COOLDOWN",
            # "IMAGE_REALM_3RAID_PATH",
            'IMAGE_INBATTLE',
        }
    
    def load_templates(self, paths, gray=1):
        mode = "GRAY" if gray else "COLOR"
        for label, filepath in paths.items():
            if not os.path.exists(filepath):
                logging.warning(f"Template not found: {filepath}")
                continue

            flag = cv2.IMREAD_GRAYSCALE if gray else cv2.IMREAD_COLOR
            template = cv2.imread(filepath, flag)

            if template is None:
                logging.warning(f"Failed to load template: {filepath}")
                continue

            self.templates[label] = template
            self.template_labels[id(template)] = label

            # >>>> อันนี้คือส่วนที่เพิ่มเข้าไป <<<<
            if gray:
                if not hasattr(self, 'gray_templates'):
                    self.gray_templates = set()
                self.gray_templates.add(label)
            else:
                if not hasattr(self, 'color_templates'):
                    self.color_templates = set()
                self.color_templates.add(label)
            # >>>> จบ <<<<

        logging.info("Event template loaded (%s): %d templates", mode, len(paths))

    def _init_capture(self):
        self.hwindc = win32gui.GetWindowDC(self.hwnd)
        self.srcdc = win32ui.CreateDCFromHandle(self.hwindc)
        self.memdc = self.srcdc.CreateCompatibleDC()

        l, t, r, b = win32gui.GetClientRect(self.hwnd)
        self._client_w = r - l
        self._client_h = b - t

        self.bmp = win32ui.CreateBitmap()
        self.bmp.CreateCompatibleBitmap(self.srcdc, self._client_w, self._client_h)
        self.memdc.SelectObject(self.bmp)

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

        # ===== NEW: Re-init memdc & bitmap =====
        try:
            self.srcdc.DeleteDC()
            self.memdc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, self.hwindc)
            win32gui.DeleteObject(self.bmp.GetHandle())
        except Exception:
            logging.warning("Failed to delete old DC or Bitmap.")

        self.init_mem()
        # ========================================


    def _buffer_to_img(self, bmp, width, height, gray=0):
        signedIntsArray = bmp.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')

        expected_size = width * height * 4
        if img.size != expected_size:
            logging.error(f"_buffer_to_img: Mismatch buffer size. Got {img.size}, expected {expected_size} ({width}x{height}x4)")
            return None

        try:
            img.shape = (height, width, 4)
        except ValueError:
            logging.error(f"_buffer_to_img: Failed to reshape buffer ({img.size} bytes) into ({height},{width},4)")
            return None

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
            img = self._buffer_to_img(self.bmp, self._client_w, self._client_h, gray)
            if img is None:
                logging.warning("window_full_shot: Failed to capture image, trying to re-init mem.")
                self.init_mem()
            return img
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

        if img is None:
            logging.warning("window_part_shot: Failed to capture part image.")
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

    def find_img(self, img_template, part=0, pos1=None, pos2=None, gray=0, center=True, delay=0.0, label=None):
        '''
        Find template image (ndarray only)
        :param img_template: Template image as numpy.ndarray
        '''
        if label is None:
            try:
                label = self.template_labels.get(id(img_template), "Unknown")
            except Exception:
                label = "Unknown"

        if not isinstance(img_template, np.ndarray):
            try:
                label = label or self.template_labels.get(id(img_template), "Unknown")
            except Exception:
                label = "Unknown"

            logging.warning(
                f"[find_game_img] Invalid template input type '{type(img_template).__name__}' for label '{label}'."
            )
            return False

        if delay > 0:
            time.sleep(delay)

        img_src = self.window_part_shot(pos1, pos2, None, gray) if part == 1 else self.window_full_shot(None, gray)
        if img_src is None:
            logging.warning("Screenshot is None.")
            return 0, 0

        # Safety check size
        if (img_src.shape[0] < img_template.shape[0]) or (img_src.shape[1] < img_template.shape[1]):
            logging.warning(
                f"[find_img] Template '{label}' size {img_template.shape} is larger than source image {img_src.shape}"
            )
            return 0, 0

        # Safety check dtype and dimension
        if img_src.dtype != img_template.dtype or img_src.ndim != img_template.ndim:
            logging.warning(
                f"[find_img] Type mismatch: src={img_src.dtype}/{img_src.shape}, tpl={img_template.dtype}/{img_template.shape}"
            )
            return 0, 0

        # Safety check depth (must be uint8 or float32)
        if img_src.dtype not in [np.uint8, np.float32]:
            logging.warning(f"[find_img] Invalid src depth {img_src.dtype} (must be uint8 or float32)")
            return 0, 0
        if img_template.dtype not in [np.uint8, np.float32]:
            logging.warning(f"[find_img] Invalid template depth {img_template.dtype} (must be uint8 or float32)")
            return 0, 0

        try:
            res = cv2.matchTemplate(img_src, img_template, cv2.TM_CCOEFF_NORMED)
            _, maxVal, _, maxLoc = cv2.minMaxLoc(res)

            if part == 1 and pos1 is not None:
                maxLoc = (maxLoc[0] + pos1[0], maxLoc[1] + pos1[1])

            if center:
                maxLoc = [
                    int(maxLoc[0] + img_template.shape[1] / 2),
                    int(maxLoc[1] + img_template.shape[0] / 2)
                ]

            if self.debug_enable:
                img = self.window_part_shot(pos1, pos2, None, gray) if part == 1 else self.window_full_shot()
                self.img = cv2.rectangle(
                    img,
                    (maxLoc[0] - img_template.shape[1] // 2, maxLoc[1] - img_template.shape[0] // 2),
                    (maxLoc[0] + img_template.shape[1] // 2, maxLoc[1] + img_template.shape[0] // 2),
                    (0, 255, 0),
                    3
                )
                show_img(self.img)
                logging.info("Top left point location: %s", maxLoc)
                logging.info("Score: %.4f", maxVal)

            return maxVal, maxLoc

        except Exception as e:
            logging.warning(f"[find_img] Failed ({label}): {e}")
            return 0, 0


    def find_game_img(self, img_template, part=0, pos1=None, pos2=None, gray=None, center=True, delay=0.04, threshold=0.9, label=None):
        '''
        Find game image using preloaded numpy template
        '''
        if label is None:
            label = self.template_labels.get(id(img_template), "Unknown")

        # ======== เพิ่มตรงนี้: เลือก gray อัตโนมัติ ========
        if gray is None:
            if label in self.color_templates:
                gray = 0  # ใช้สี (BGR)
            else:
                gray = 1  # ใช้ขาวดำ (Gray)
        # ================================================

        start_time = time.perf_counter()

        maxVal, maxLoc = self.find_img(img_template, part, pos1, pos2, gray, center, delay, label)

        elapsed = (time.perf_counter() - start_time) * 1000  # ms

        if maxVal > threshold:
            if label not in self.exclude_log_templates:
                if center:
                    top_left = (
                        int(maxLoc[0] - img_template.shape[1] / 2),
                        int(maxLoc[1] - img_template.shape[0] / 2)
                    )
                else:
                    top_left = maxLoc

                bottom_right = (
                    top_left[0] + img_template.shape[1],
                    top_left[1] + img_template.shape[0]
                )

                logging.debug(
                    f'Detected \"{label}\" with value: %.4f, pos: {maxLoc}, match_area=({top_left}, {bottom_right}) (%.2f ms)',
                    maxVal, elapsed
                )
            return list(maxLoc)

        return False

    
    def find_game_img_count(self, img_template, part=0, pos1=None, pos2=None, gray=1, delay=0.0, threshold=0.9, label=None):
        '''
        Return count of matched images (grouped to avoid duplicates)
        '''
        if label is None:
            label = self.template_labels.get(id(img_template), "Unknown")

        if delay > 0:
            time.sleep(delay)

        img_src = self.window_part_shot(pos1, pos2, None, gray) if part == 1 else self.window_full_shot(None, gray)
        if img_src is None:
            logging.warning("Screenshot is None.")
            return 0

        try:
            res = cv2.matchTemplate(img_src, img_template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            rectangles = []

            for pt in zip(*loc[::-1]):
                rect = [int(pt[0]), int(pt[1]), img_template.shape[1], img_template.shape[0]]
                rectangles.append(rect)
                rectangles.append(rect)  # ต้องใส่ซ้ำสำหรับ groupRectangles

            rectangles, _ = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
            count = len(rectangles)

            logging.debug(f'Counted {count} unique matches for "{label}" with threshold {threshold}')
            return count

        except Exception as e:
            logging.warning(f"[find_game_img_count] Failed ({label}): {e}")
            return 0



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
    
    def mouse_drag_bg(self, pos1, pos2,delay=0.04):
        '''
            :param pos1: (x,y) 
            :param pos2: (x,y) 
        '''
        if self.client == 0:
            move_x = np.linspace(pos1[0], pos2[0], num=20, endpoint=True)[0:]
            move_y = np.linspace(pos1[1], pos2[1], num=20, endpoint=True)[0:]
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN,
                                 0, win32api.MAKELONG(pos1[0], pos1[1]))
            for i in range(20):
                x = int(round(move_x[i]))
                y = int(round(move_y[i]))
                win32gui.SendMessage(
                    self.hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x, y))
                time.sleep(delay)
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP,
                                 0, win32api.MAKELONG(pos2[0], pos2[1]))
        else:
            command = str(pos1[0])+' ' + str(pos1[1]) + \
                ' '+str(pos2[0])+' '+str(pos2[1])
            os.system('adb shell input swipe '+command)
