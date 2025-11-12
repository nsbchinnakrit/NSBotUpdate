from Module.GameControl import *
from Module.ThreadGame import *
from Module.loadconfig import *
from Module.logsystem import MyLog
from Module.Utils import GameUtils
import time, subprocess
import logging
import threading
from Module.loadconfig import config

_localVariable=threading.local()
_displayChat=0
_cAttackRealm=0
_idlecount=0

class Event(threading.Thread):
    def __init__(self,Server, windowName, beforetotal, total, pid, bondlingmode, pactsettings, crystal_use, tomb, snowball, azure, kuro):
        threading.Thread.__init__(self)
        self.__sv = Server
        self.__windowName = windowName
        self.__beforetotal = beforetotal
        self.__total = total
        self.__pid = pid
        self.__bondlingmode = bondlingmode
        self.__pactsettings = pactsettings
        self.__crystal_use = crystal_use
        self.__tomb = tomb
        self.__snowball = snowball
        self.__azure = azure
        self.__kuro = kuro
        self.__gui = GameControl(self.__windowName, 0)
        self.game_utils = GameUtils(self.__gui, self.__pid)
        self.game_utils.set_total(self.__total)  # Set total for idle detection

        color_templates = {
        }

        gray_templates = {
            # DEFAULT
            "IMAGE_ROOM_BACK": config['DEFAULT']['IMAGE_ROOM_BACK'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],
            "IMAGE_FAILED": config['DEFAULT']['IMAGE_FAILED'],
            "IMAGE_FINISHED1": config['DEFAULT']['IMAGE_FINISHED1'],
            "IMAGE_FINISHED2": config['DEFAULT']['IMAGE_FINISHED2'],
            "IMAGE_FINISHED1S1": config['DEFAULT']['IMAGE_FINISHED1S1'],
            "IMAGE_FINISHED1S2": config['DEFAULT']['IMAGE_FINISHED1S2'],
            "IMAGE_FINISHED1S3": config['DEFAULT']['IMAGE_FINISHED1S3'],
            "IMAGE_FINISHED_CP": config['DEFAULT']['IMAGE_FINISHED_CP'],

            # Server-specific
            "IMAGE_REALM_RAID": config[self.__sv]['IMAGE_REALM_RAID'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_READY": config[self.__sv]['IMAGE_READY'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],

            # EVENT
            # "IMAGE_EVENT_ICON": config['EVENT']['IMAGE_EVENT_ICON'],
            "IMAGE_EVENT_LOCK": config['EVENT']['IMAGE_EVENT_LOCK'],
            "IMAGE_EVENT_LOCK2": config['EVENT']['IMAGE_EVENT_LOCK2'],
            "IMAGE_EVENT_LOCKED": config['EVENT']['IMAGE_EVENT_LOCKED'],
            "IMAGE_EVENT_LOCKED2": config['EVENT']['IMAGE_EVENT_LOCKED2'],
            "IMAGE_EVENT_START": config['EVENT']['IMAGE_EVENT_START'],
            "IMAGE_EVENT_REWARD": config['EVENT']['IMAGE_EVENT_REWARD'],

            #WANTED Quest
            "IMAGE_CLOSEWANTED": config['DEFAULT']['IMAGE_CLOSEWANTED'],
            "IMAGE_WQ_JADE": config['DEFAULT']['IMAGE_WQ_JADE'],
            "IMAGE_WQ_COIN": config['DEFAULT']['IMAGE_WQ_COIN'],
            "IMAGE_WQ_SUSHI": config['DEFAULT']['IMAGE_WQ_SUSHI'],
            "IMAGE_WQ_FOODDOG": config['DEFAULT']['IMAGE_WQ_FOODDOG'],
            "IMAGE_WQ_FOODCAT": config['DEFAULT']['IMAGE_WQ_FOODCAT'],
        }
    
        self.load_templates(gray_templates, gray=1)
        self.load_templates(color_templates, gray=0)
    
    def load_templates(self, paths, gray=1):
        self.__gui.load_templates(paths, gray=gray)
        mode = "GRAY" if gray else "COLOR"
        # logging.info("Event template loaded (%s): %d templates", mode, len(paths))

#   
    def gameModeEvent(self):
        global _displayChat, _cAttackRealm
        CLICK_SOULMAX=(568, 387)
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+195, 600), pos2=(_displayChat+544, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                continue

            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start
            
            position = (self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCK"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625))) or (
                        self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCK2"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625)))
            if position != False:
                self.__gui.mouse_click_bg(position)
                self.game_utils.reset_idle_count()
                continue

            position = (self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCKED"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625), threshold=0.84)) or (
                        self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCKED2"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625)))
            if position != False:
                logging.info('Start Challenge!')
                self.__gui.mouse_click_bg(pos=(_displayChat+1009, 529), pos_end=(_displayChat+1079, 581))
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue

            if _cAttackRealm >= 12:
                logging.info("Unable to process, Exit!")
                self.game_utils.create_file(str(self.__total))
                subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                            creationflags=subprocess.CREATE_NO_WINDOW)
                return

            position=self.__gui.find_game_img(self.__gui.templates["IMAGE_FAILED"], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                _cAttackRealm=0
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                self.game_utils.reset_idle_count()
                continue
                
            if (self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1"], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED_CP"], part=1, pos1=(_displayChat+360, 80), pos2=(_displayChat+500, 160)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S1"], part=1, pos1=(_displayChat+326, 119), pos2=(_displayChat+434, 215)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S3"], part=1, pos1=(_displayChat+50, 550), pos2=(_displayChat+450, 610)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED2"], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_REWARD"], part=1, pos1=(_displayChat+252, 155), pos2=(_displayChat+330, 300)) != False):
                logging.info("Battle End, Victory!")
                _cAttackRealm=0
                self.game_utils.reset_idle_count()
                while True:
                    if self.__gui.find_game_img(self.__gui.templates["IMAGE_COOP2_SEAL"], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates["IMAGE_CHATDETECT"])) or self.__gui.find_game_img(self.__gui.templates["IMAGE_CHATSTICKER"], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCKED"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625), threshold=0.84)) or (
                        self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCKED2"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625), threshold=0.84)) or (
                        self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCK"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625), threshold=0.84)) or (
                        self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCK2"], part=1, pos1=(_displayChat+505, 560), pos2=(_displayChat+980, 625), threshold=0.84)):
                        break

                    if (self.__gui.find_game_img(self.__gui.templates["IMAGE_SOULMAX"], part=1, pos1=(_displayChat+361, 207), pos2=(_displayChat+778, 343))) != False:
                        logging.info('Closed "Soul limit Maxed out" popup!')
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)
                        continue
                    self.__gui.mouse_click_bg((_displayChat+35, 540))
                break

            if self.__gui.find_game_img(self.__gui.templates["IMAGE_SOULMAX"], part=1, pos1=(_displayChat+361, 207), pos2=(_displayChat+778, 343)) != False:
                logging.info('Closed "Soul limit Maxed out" popup!')
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                self.game_utils.reset_idle_count()
            
            else:
                self.game_utils.reset_idle_count()
            
            time.sleep(0.2)
    
    def run(self):
        count=self.__beforetotal
        self.game_utils.create_file(data=str(count))
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeEvent()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.game_utils.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()
