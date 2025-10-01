import logging
import threading
import time
import subprocess
from Module.loadconfig import config

class GameUtils:
    def __init__(self, gui, pid, displayChat=0):
        self.__gui = gui
        self.__pid = pid
        self._displayChat = displayChat
        self._last_activity_time = time.time()
        self.__total = 0  # Will be set by the game mode

    def set_total(self, total):
        self.__total = total

    def detectAssistance(self):
        position1 = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(self._displayChat+455, 135), pos2=(self._displayChat+495, 175))
        position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(self._displayChat+560, 300), pos2=(self._displayChat+607, 397))
        position3 = self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])
        wq_jade = config['VALUE']['WQ_JADE']
        wq_coin = config['VALUE']['WQ_COIN']
        wq_sushi = config['VALUE']['WQ_SUSHI']
        wq_food = config['VALUE']['WQ_FOOD']
        idle_timeout_minutes = config['VALUE'].get('IDLE_TIMEOUT_MINUTES', 1)  # Default 1 minute if not set
        idle_timeout_seconds = idle_timeout_minutes * 60

        if self._displayChat == 0 and position3:
            self._displayChat = 525
            self.__gui.recheckRect()
            logging.info('External chat detected.')
            self.reset_idle_count()

        if (not position3) and position2:
            self.__gui.mouse_click_bg(position2)
            self._displayChat = 0
            self.__gui.recheckRect()
            logging.info('ChatPanel detected, closed!')
            self.reset_idle_count()

        if position1:
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_JADE']) and wq_jade
            ) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_COIN']) and wq_coin
            ) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_SUSHI']) and wq_sushi
            ) or ((self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_FOODDOG']) or self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_FOODCAT'])) and wq_food):
                logging.info("Accept wanted quest!")
                self.__gui.mouse_click_bg((self._displayChat+757, 368))
                screenshot = self.__gui.takescreenshot('คนเหลี่ยมๆ')
                self.create_file2(data=screenshot)
                self.reset_idle_count()
            else:
                logging.info("Refuse to accept the invitation for the wanted seal.")
                self.__gui.mouse_click_bg((self._displayChat+757, 461))
                self.__gui.takescreenshot('คนเหลี่ยมๆ')
                self.reset_idle_count()
        
        # Check if idle timeout has been reached
        idle_time = time.time() - self._last_activity_time
        if idle_time >= idle_timeout_seconds:
            logging.info(f"Idle timeout reached ({idle_timeout_minutes} minutes). Exiting.")
            self.create_file(str(self.__total))
            subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                        creationflags=subprocess.CREATE_NO_WINDOW)
            return

    def reset_idle_count(self):
        """Reset the idle timer. This should be called whenever there is user activity."""
        self._last_activity_time = time.time()
        # For compatibility with existing code that uses global _idlecount
        global _idlecount
        if '_idlecount' in globals():
            _idlecount = 0

    def create_file(self, data='0'):
        temp = f"runprocess/temp{self.__pid}.txt"
        try:
            with open(temp, "w") as file:
                file.write(data)
                file.close
        except Exception as error:
            logging.error(error)
    
    def create_file2(self, data='False'):
        temp = f"runprocess/wanted{self.__pid}.txt"
        try:
            with open(temp, "w") as file:
                file.write(data)
                file.close
        except Exception as error:
            logging.error(error) 