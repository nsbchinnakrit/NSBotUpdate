from Module.GameControl import *
from Module.ThreadGame import *
from Module.loadconfig import *
from Module.Utils import GameUtils
import time, subprocess
import threading
import logging
from Module.loadconfig import config

_localVariable=threading.local()
_displayChat=0
_cAttackRealm=0
_idlecount=0

class SingleSoul(threading.Thread):
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
            # SOUL
            "IMAGE_SINGLE_SOUL_LOCK": config['SOUL']['IMAGE_SINGLE_SOUL_LOCK'],
            "IMAGE_SINGLE_SOUL_STAT": config['SOUL']['IMAGE_SINGLE_SOUL_STAT'],
            "IMAGE_SINGLE_TOTEM_STAT": config['SOUL']['IMAGE_SINGLE_TOTEM_STAT'],
            "IMAGE_SOUL_INVITE_CHECKBOX": config['SOUL']['IMAGE_SOUL_INVITE_CHECKBOX'],
            "IMAGE_SOUL_PETREWARD": config[self.__sv]['IMAGE_SOUL_PETREWARD'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],

            # REALM
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],

            # DEFAULT
            "IMAGE_EMPTY_SUSHI": config['DEFAULT']['IMAGE_EMPTY_SUSHI'],
            "IMAGE_EMPTY_SUSHI_CLOSE": config['DEFAULT']['IMAGE_EMPTY_SUSHI_CLOSE'],
            "IMAGE_FAILED": config['DEFAULT']['IMAGE_FAILED'],
            "IMAGE_FINISHED0": config['DEFAULT']['IMAGE_FINISHED0'],
            "IMAGE_FINISHED1": config['DEFAULT']['IMAGE_FINISHED1'],
            "IMAGE_FINISHED1S2": config['DEFAULT']['IMAGE_FINISHED1S2'],
            "IMAGE_FINISHED2": config['DEFAULT']['IMAGE_FINISHED2'],
            "IMAGE_BOSSHP": config['DEFAULT']['IMAGE_BOSSHP'],
            "IMAGE_BOSSMARK": config[self.__sv]['IMAGE_BOSSMARK'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],

            # SERVER (self.__sv)
            "IMAGE_READY": config[self.__sv]['IMAGE_READY'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],

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


    def gameModeSoul(self):
        global _displayChat, _cAttackRealm
        CLICK_SOULMAX=(568, 387)
        START_SOUL_COORDINATE=(1075, 565)
        while True:  
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+459, 600), pos2=(_displayChat+544, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                continue

            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            #lock line up
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_SOUL_LOCK'], part=1, pos1=(_displayChat+475, 485), pos2=(_displayChat+540, 540))
            position2=(self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_SOUL_STAT'], part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1136, 640))) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_TOTEM_STAT'], part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1136, 640)))
            if position != False and position2 != False:
                logging.info("Successfully lock lineup...")
                self.__gui.mouse_click_bg(position)
            
            if position2:
                time.sleep(0.5)
                logging.info('Start Challenge!')
                _cAttackRealm+=1
                self.game_utils.reset_idle_count()
                self.__gui.mouse_click_bg(position2)

            if _cAttackRealm >= 12 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE'], part=1, pos1=(_displayChat+792, 143), pos2=(_displayChat+875, 200)) != False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+361, 337), pos2=(_displayChat+575, 420)) != False) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX'], part=1, pos1=(_displayChat+260, 280), pos2=(_displayChat+540, 360)) == False):
                logging.info("Unable to process, Exit!")
                self.game_utils.create_file(str(self.__total))
                subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                            creationflags=subprocess.CREATE_NO_WINDOW)
                return

            gameready=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY'], part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1106, 607))
            if gameready != False:
                self.__gui.mouse_click_bg(gameready)
                time.sleep(1)
                continue
            
            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                _cAttackRealm=0
                self.game_utils.reset_idle_count()
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                    if position == False:
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))

             #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 10), pos2=(_displayChat+459, 192)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2'], part=1, pos1=(_displayChat+30, 30), pos2=(_displayChat+95, 95))) != False:
                logging.info("Battle End, Victory!")
                _cAttackRealm=0
                self.game_utils.reset_idle_count()
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_SOUL_STAT'], part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1136, 640))) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_TOTEM_STAT'], part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1136, 640))) != False:
                        break

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_PETREWARD'], part=1, pos1=(_displayChat+103, 197), pos2=(_displayChat+304, 282)):
                        logging.info("Claim Pet Reward.")
                        self.__gui.mouse_click_bg((_displayChat + 950, 450))
                        time.sleep(1)

                    #soulmax
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                        logging.info('Closed "Soul limit Maxed out" popup!')
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)

                    self.__gui.mouse_click_bg(START_SOUL_COORDINATE)
                break

            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_PETREWARD'], part=1, pos1=(_displayChat+103, 197), pos2=(_displayChat+304, 282)):
                logging.info("Claim Pet Reward.")
                self.__gui.mouse_click_bg((_displayChat + 950, 450))
                time.sleep(1)

            #soulmax
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                logging.info('Closed "Soul limit Maxed out" popup!')
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)
            
            else:
                time.sleep(1)
    
    def run(self):
        count=self.__beforetotal
        self.game_utils.create_file(data=str(count))
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeSoul()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.game_utils.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()
