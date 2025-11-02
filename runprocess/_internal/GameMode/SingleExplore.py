from Module.GameControl import *
from Module.ThreadGame import *
from Module.loadconfig import *
from Module.Utils import GameUtils
import time
import pyautogui, subprocess
import threading
import logging
from Module.loadconfig import config

_localVariable=threading.local()
_displayChat=0
_cAttackRealm=0
_idlecount=0
cantattk=0

class SingleExplore(threading.Thread):
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
            # EXPLORE
            "IMAGE_STORY_BOX": config['EXPLORE']['IMAGE_STORY_BOX'],
            "IMAGE_STORY_CHERRY_CAKE": config['EXPLORE']['IMAGE_STORY_CHERRY_CAKE'],
            "IMAGE_STORY_LIST_CHAPTER": config['EXPLORE']['IMAGE_STORY_LIST_CHAPTER'],
            "IMAGE_STORY_FIGHT": config['EXPLORE']['IMAGE_STORY_FIGHT'],
            "IMAGE_STORY_FIGHT_BOSS": config[self.__sv]['IMAGE_STORY_FIGHT_BOSS'],
            "IMAGE_STORY_GET_REWARD": config[self.__sv]['IMAGE_STORY_GET_REWARD'],

            # DEFAULT
            "IMAGE_EMPTY_SUSHI": config['DEFAULT']['IMAGE_EMPTY_SUSHI'],
            "IMAGE_EMPTY_SUSHI_CLOSE": config['DEFAULT']['IMAGE_EMPTY_SUSHI_CLOSE'],
            "IMAGE_FAILED": config['DEFAULT']['IMAGE_FAILED'],
            "IMAGE_FINISHED2": config['DEFAULT']['IMAGE_FINISHED2'],
            "IMAGE_FINISHED1": config['DEFAULT']['IMAGE_FINISHED1'],
            "IMAGE_FINISHED1S2": config['DEFAULT']['IMAGE_FINISHED1S2'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],

            # SOUL
            "IMAGE_SOUL_INVITE_CHECKBOX": config['SOUL']['IMAGE_SOUL_INVITE_CHECKBOX'],

            # REALM
            "IMAGE_REALM_CLOSE": config['REALM']['IMAGE_REALM_CLOSE'],

            # SERVER-SPECIFIC (self.__sv)
            "IMAGE_STORY_LIMIT": config[self.__sv]['IMAGE_STORY_LIMIT'],
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],
            "IMAGE_STORY_AUTOFOOD": config[self.__sv]['IMAGE_STORY_AUTOFOOD'],
            "IMAGE_STORY_START": config[self.__sv]['IMAGE_STORY_START'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_READY": config[self.__sv]['IMAGE_READY'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],
            "IMAGE_STORY_REWARD_CONFIRMED": config[self.__sv]['IMAGE_STORY_REWARD_CONFIRMED'],
        
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


    def gameModeExplore(self):
        global _isPaused, _displayChat, _cAutoRotation, cantattk
        CLICK_SOULMAX=(568, 387)
        CLICK_FINISH2=(35, 510)
        SLIDE_STORY_COORDINATE=[(_displayChat+200,200),(_displayChat+1000,200)]
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+459, 600), pos2=(_displayChat+544, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                continue
                
            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start
            
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'],part=1, pos1=(_displayChat+896, 101), pos2=(_displayChat+964, 171))
            if position != False:
                logging.info("Box Found. (Func.2)")
                self.__gui.mouse_click_bg(position)
                time.sleep(4)
                if position != False and position2 != False:
                    self.__gui.mouse_click_bg(position2)
                    time.sleep(1)
                self.__gui.mouse_click_bg(position)
                time.sleep(1)

            position=(self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIMIT']) or self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)))
            if position != False:
                cantattk+=1
                logging.info("Unable to process, try (%s/3)"%cantattk)
                
            
            if cantattk >= 10 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE'], part=1, pos1=(_displayChat+792, 143), pos2=(_displayChat+875, 200)) != False):
                logging.info("Unable to process, Exit!")
                self.game_utils.create_file(str(self.__total))
                subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                            creationflags=subprocess.CREATE_NO_WINDOW)
                return
            
                
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_AUTOFOOD'],part=1, pos1=(_displayChat+90, 575), pos2=(_displayChat+265, 625))
            if position != False:
                logging.info("Click Auto Rotation")
                self.__gui.mouse_click_bg((_displayChat+117, 599))
                _cAutoRotation+=1
                if _cAutoRotation >= 3:
                    logging.info("Exit!")
                    pyautogui.alert(text='auto rotation food runs out, stop working..', title='Exit!', button='OK')
                    args = ['taskkill', '/F', '/PID', str(self.__pid)]
                    subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(1)

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49))
            if position == False:
                position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180))  
                if position != False:
                    _localVariable.isBossDetected=False
                    logging.info("Entering last chapter.... ")
                    self.__gui.mouse_click_bg((position[0],position[1]+370))
                    cantattk+=1
                    self.game_utils.reset_idle_count()
                    time.sleep(1)
                    continue
                

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_START'],part=1, pos1=(_displayChat+770, 448), pos2=(_displayChat+907, 517))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'],part=1, pos1=(_displayChat+896, 101), pos2=(_displayChat+964, 171))
            if position != False:
                #time.sleep(0.5)
                if position2 != False and position3 != False:
                    logging.info("Box Found (Func3)")
                    self.__gui.mouse_click_bg(position)
                    time.sleep(2)
                    if position2 != False:
                        while True:
                            self.__gui.mouse_click_bg(position3)
                            time.sleep(1)
                            if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                                detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                                detectAssistance.setDaemon(True)
                                detectAssistance.start
                            if position3 == False and position2 != False:
                                self.__gui.mouse_click_bg(position2)
                                time.sleep(1)
                            break
                        break
                    else:
                        break
                elif position2 == False:
                    _localVariable.isBossDetected=False
                    logging.info("Enter Explore!")
                    self.__gui.mouse_click_bg(position)
                    continue
                else:
                    self.__gui.mouse_click_bg(position3)
                    time.sleep(1)
                    break
            
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49))
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_BOSS'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            if position == False and position2 != False and position3 == False:
                if (position == False) and (position3 == False):
                    self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[1],SLIDE_STORY_COORDINATE[0])
                    _localVariable.detectCount -= 1
                    if _localVariable.detectCount < 1:
                        # self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[1],SLIDE_STORY_COORDINATE[0])
                        self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[0],SLIDE_STORY_COORDINATE[1])
                        _localVariable.detectCount=30

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_BOSS'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            if position != False:
                logging.info("BOSS Found! Start fighting..")
                self.__gui.mouse_click_bg(position)
                _localVariable.isBossDetected=True
                cantattk+=1
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            if position != False:
                logging.info("Start fighting..")
                self.__gui.mouse_click_bg(position)
                cantattk+=1
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue

            #=========================================get ready=================================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_READY'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
            if position != False:
                # logging.info("Starting battle.... ")
                self.__gui.mouse_click_bg(position)
                #time.sleep(2)
                continue

            #=========================================Finish=================================================
            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                cantattk=0
                self.game_utils.reset_idle_count()
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                continue

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))
            if position != False:
                cantattk=0
                self.game_utils.reset_idle_count()
                self.__gui.mouse_click_bg(position)
                continue


            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2'], part=1, pos1=(_displayChat+35, 555), pos2=(_displayChat+95, 605))) != False:
                logging.info("Battle End, Victory!")
                cantattk=0
                self.game_utils.reset_idle_count()
                while True:
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False:
                        time.sleep(1)
                        break

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                        logging.info('Closed "Soul limit Maxed out" popup!')
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)
                        continue
                break

            #==========================================Reward settlement=============================================
            # if (self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BACK'])!= False
            #     or self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_REWARD_CONFIRMED']) != False or self.__gui.find_game_img(IMAGE_STORY_REWARD_CONFIRMEDCN) != False):
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_GET_REWARD'],part=1, pos1=(_displayChat+190, 310), pos2=(_displayChat+921, 561))
            if position != False:
                logging.info("Challenge finished. Exiting for next round.")
                self.__gui.send_esc_down()
                time.sleep(2)
                self.game_utils.reset_idle_count()
                self.__gui.mouse_click_bg((_displayChat+655, 383))
            
            else:
                self.game_utils.reset_idle_count()
    
    def run(self):
        count=self.__beforetotal
        self.game_utils.create_file(data=str(count))
        _localVariable.detectCount=30
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeExplore()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.game_utils.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()
