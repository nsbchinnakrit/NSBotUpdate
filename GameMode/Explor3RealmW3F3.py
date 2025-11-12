from Module.GameControl import *
from Module.ThreadGame import *
from Module.loadconfig import *
import time
import pyautogui, subprocess
import threading
import logging
from Module.loadconfig import config
from Module.Utils import GameUtils

_localVariable=threading.local()
_displayChat=0
_is3Realm=False
_cAttackRealm=0
_exit = True
cantattk=0
_firstcheck=True
_isFail=0

CLICK_SOULMAX=(568, 387)
CLICK_FINISH2=(35, 510)
SLIDE_STORY_COORDINATE=[(_displayChat+200,200),(_displayChat+1000,200)]
START_SOUL_COORDINATE = (1075, 565)

class Explor3RealmW3F3(threading.Thread):
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
            "IMAGE_STORY_FIGHT": config['EXPLORE']['IMAGE_STORY_FIGHT'],
            "IMAGE_STORY_FIGHT_BOSS": config[self.__sv]['IMAGE_STORY_FIGHT_BOSS'],
            "IMAGE_STORY_CHERRY_CAKE": config['EXPLORE']['IMAGE_STORY_CHERRY_CAKE'],
            "IMAGE_STORY_LIST_CHAPTER": config['EXPLORE']['IMAGE_STORY_LIST_CHAPTER'],
            "IMAGE_STORY_GET_REWARD": config[self.__sv]['IMAGE_STORY_GET_REWARD'],
            "IMAGE_STORY_BACK": config['EXPLORE']['IMAGE_STORY_BACK'],
            "IMAGE_STORY_AUTOFOOD": config[self.__sv]['IMAGE_STORY_AUTOFOOD'],
            "IMAGE_STORY_START": config[self.__sv]['IMAGE_STORY_START'],

            # SOUL
            "IMAGE_SOUL_ROOM_DETECT": config['SOUL']['IMAGE_SOUL_ROOM_DETECT'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],

            # REALM
            "IMAGE_REALM_FN3R": config['REALM']['IMAGE_REALM_FN3R'],
            "IMAGE_REALM_CLOSE": config['REALM']['IMAGE_REALM_CLOSE'],
            "IMAGE_REALM_LOCK": config['REALM']['IMAGE_REALM_LOCK'],
            "IMAGE_REALM_3RAID": config['REALM']['IMAGE_REALM_3RAID'],
            "IMAGE_REALM_3RAID2": config['REALM']['IMAGE_REALM_3RAID2'],
            "IMAGE_REALM_3RAIDFROG": config['REALM']['IMAGE_REALM_3RAIDFROG'],
            "IMAGE_REALM_SECTIONFROG": config['REALM']['IMAGE_REALM_SECTIONFROG'],
            "IMAGE_REALM_SECTION": config['REALM']['IMAGE_REALM_SECTION'],
            "IMAGE_REALM_SECTION2": config['REALM']['IMAGE_REALM_SECTION2'],
            "IMAGE_REALM_JADE": config['REALM']['IMAGE_REALM_JADE'],
            "IMAGE_REALM_EMPTY_TICKET2": config[self.__sv]['IMAGE_REALM_EMPTY_TICKET2'],
            "IMAGE_REALM_CANCEL_BATTLE": config[self.__sv]['IMAGE_REALM_CANCEL_BATTLE'],
            "IMAGE_REALM_RAID": config[self.__sv]['IMAGE_REALM_RAID'],
            "IMAGE_REALM_ATK": config[self.__sv]['IMAGE_REALM_ATK'],
            "IMAGE_REALM_REFRESH": config[self.__sv]['IMAGE_REALM_REFRESH'],
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],
            "IMAGE_REALM_GUILD": config[self.__sv]['IMAGE_REALM_GUILD'],
            "IMAGE_REALM_COOLDOWN": config[self.__sv]['IMAGE_REALM_COOLDOWN'],
            "IMAGE_REALM_RAID_FAILED": config['REALM']['IMAGE_REALM_RAID_FAILED'],

            # REALM - GB & CN
            "IMAGE_REALM_EMPTY_TICKET": config[self.__sv]['IMAGE_REALM_EMPTY_TICKET'],
            "IMAGE_BUFF": config[self.__sv]['IMAGE_BUFF'],

            # DEFAULT
            "IMAGE_FINISHED2": config['DEFAULT']['IMAGE_FINISHED2'],
            "IMAGE_FINISHED1": config['DEFAULT']['IMAGE_FINISHED1'],
            "IMAGE_FINISHED1S1": config['DEFAULT']['IMAGE_FINISHED1S1'],
            "IMAGE_FINISHED1S2": config['DEFAULT']['IMAGE_FINISHED1S2'],
            "IMAGE_FINISHED1S3": config['DEFAULT']['IMAGE_FINISHED1S3'],
            "IMAGE_FINISHED_CP": config['DEFAULT']['IMAGE_FINISHED_CP'],
            "IMAGE_FAILED": config['DEFAULT']['IMAGE_FAILED'],
            "IMAGE_EMPTY_SUSHI": config['DEFAULT']['IMAGE_EMPTY_SUSHI'],
            "IMAGE_EMPTY_SUSHI_CLOSE": config['DEFAULT']['IMAGE_EMPTY_SUSHI_CLOSE'],
            "IMAGE_BACK": config['DEFAULT']['IMAGE_BACK'],
            "IMAGE_BACK2": config['DEFAULT']['IMAGE_BACK2'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],
            "IMAGE_CLOSEWANTED": config['DEFAULT']['IMAGE_CLOSEWANTED'],
            "IMAGE_WQ_JADE": config['DEFAULT']['IMAGE_WQ_JADE'],
            "IMAGE_WQ_COIN": config['DEFAULT']['IMAGE_WQ_COIN'],
            "IMAGE_WQ_SUSHI": config['DEFAULT']['IMAGE_WQ_SUSHI'],
            "IMAGE_WQ_FOODDOG": config['DEFAULT']['IMAGE_WQ_FOODDOG'],
            "IMAGE_WQ_FOODCAT": config['DEFAULT']['IMAGE_WQ_FOODCAT'],

            # SHARED SERVER
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_READY": config[self.__sv]['IMAGE_READY'],
        }


        self.load_templates(gray_templates, gray=1)
        self.load_templates(color_templates, gray=0)
    
    def load_templates(self, paths, gray=1):
        self.__gui.load_templates(paths, gray=gray)
        mode = "GRAY" if gray else "COLOR"
        # logging.info("Event template loaded (%s): %d templates", mode, len(paths))
                
    def gameModeExplore_3Realm(self):
        global _cAttackRealm, _firstcheck, count
        logging.debug("Working in [gameModeExplore_3Realm]")
        while True: 
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+448, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue

            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET2'],part=1, pos1=(_displayChat+79, 6), pos2=(_displayChat+940, 47), threshold=0.90)
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180))  
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILD'], part=1, pos1=(_displayChat+1000, 194), pos2=(_displayChat+1132, 446))
            position4=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+874, 80), pos2=(_displayChat+1120, 160))
            position5=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
            #time.sleep(5)
            if position5 != False:
                logging.info("Box Found. (Func.1)")
                self.__gui.mouse_click_bg(position5)
                self.game_utils.reset_idle_count()
                time.sleep(1)
                if position4 != False:
                    self.__gui.mouse_click_bg(position4)
                    time.sleep(1)
                    self.__gui.mouse_click_bg(position5)
                    time.sleep(1)
                    continue
                
            position4=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+874, 80), pos2=(_displayChat+1112, 174))
            if position != False or position3 != False:
                logging.info("Change to Realm Raid")
                while True:
                    time.sleep(1)
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET'],threshold=0.97) !=False:
                        logging.info("Close RealmPage...")
                        self.__gui.mouse_click_bg((_displayChat+1070, 120))
                        if _firstcheck == False:
                            self.game_utils.reset_idle_count()
                            count+=1
                            self.game_utils.create_file(data=str(count))
                            _firstcheck = True
                        time.sleep(1)
                        break

                    if position4 != False and position3 == False:
                        self.__gui.mouse_click_bg(position4)
                        logging.info('Close Explore Page.')
                        #Click icon realm
                        time.sleep(1)
                        self.gameModeRealmRaid()
                        break
                    else:
                        self.gameModeRealmRaid()

            if position == False and position2 != False or self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_START'],part=1, pos1=(_displayChat+770, 448), pos2=(_displayChat+907, 517)) != False:
                self.gameModeExplor()
            
            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'])
            if position != False:
                logging.info("Battle End, Fail..")
                cantattk=0
                _cAttackRealm=0
                self.game_utils.reset_idle_count()
                self.__gui.mouse_click_bg(position)
                continue

            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'])) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2'], part=1, pos1=(_displayChat+30, 30), pos2=(_displayChat+95, 95))) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED_CP"], part=1, pos1=(_displayChat+360, 80), pos2=(_displayChat+500, 160)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S1"], part=1, pos1=(_displayChat+326, 119), pos2=(_displayChat+434, 215)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S3"], part=1, pos1=(_displayChat+50, 550), pos2=(_displayChat+450, 610)) != False) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'])) != False:                
                logging.info("Battle End, Victory!")
                cantattk=0
                self.game_utils.reset_idle_count()
                while True:
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or (
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_BUFF'])) != False:
                        break
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+874, 80), pos2=(_displayChat+1112, 174)) != False or self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False:
                        _cAttackRealm=0
                        break
                break

            #soulmax
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                logging.info('Closed "Soul limit Maxed out" popup!')
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)
                continue

            else:
                self.game_utils.reset_idle_count()
    
    def gameModeExplor(self):
        global _displayChat, _cAutoRotation, cantattk, _firstcheck, count
        logging.debug("Working in [gameModeExplor]")
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+369, 600), pos2=(_displayChat+448, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                continue
                
            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'],part=1, pos1=(_displayChat+896, 101), pos2=(_displayChat+1120, 160))
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILD'], part=1, pos1=(_displayChat+1000, 194), pos2=(_displayChat+1132, 446))    

            if position != False:
                logging.info("Box Found. (Func.2)")
                self.__gui.mouse_click_bg(position)
                time.sleep(4)
                if position != False and position2 != False:
                    self.__gui.mouse_click_bg(position2)
                    time.sleep(1)
                self.__gui.mouse_click_bg(position)
                time.sleep(1)
                self.game_utils.reset_idle_count()

            if cantattk >= 10 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE'], part=1, pos1=(_displayChat+792, 143), pos2=(_displayChat+875, 200)) != False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+361, 337), pos2=(_displayChat+575, 420)) != False) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX'], part=1, pos1=(_displayChat+260, 280), pos2=(_displayChat+424, 332)) == False):
                logging.info("Unable to process, Exit!")
                self.game_utils.create_file(str(self.__total))
                subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                            creationflags=subprocess.CREATE_NO_WINDOW)
                return
            
            if position2 != False and position3 != False:
                logging.debug("Return to Main function")
                self.gameModeExplore_3Realm()
                
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_AUTOFOOD'],part=1, pos1=(_displayChat+90, 575), pos2=(_displayChat+265, 625))
            if position != False:
                logging.info("Click Auto Rotation")
                self.__gui.mouse_click_bg((_displayChat+117, 599))
                _cAutoRotation+=1
                if _cAutoRotation >= 3:
                    logging.info("Exit!")
                    pyautogui.alert(text='auto rotation food runs out, stop working..', title='Exit!', button='OK')
                    args = ['taskkill', '/F', '/PID', str(self.__pid)]
                    subprocess.Popen(args)
                time.sleep(1)

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49))
            if position == False:
                time.sleep(1)
                position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180))  
                if _firstcheck == False and (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET2'],part=1, pos1=(_displayChat+79, 6), pos2=(_displayChat+940, 47))) != False:
                    _firstcheck = False
                    count+=1
                    self.game_utils.create_file(data=str(count))
                    self.gameModeExplore_3Realm() 
                elif position != False:
                    _localVariable.isBossDetected=False
                    logging.info("Entering last chapter..")
                    self.__gui.mouse_click_bg((position[0],position[1]+370))
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
                    self.game_utils.reset_idle_count()
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
                    logging.info("Start Explore!")
                    self.__gui.mouse_click_bg(position)
                    cantattk+=1
                    _firstcheck = False
                    time.sleep(1)
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
            if position3 != False:
                logging.info("BOSS Found! Start fighting..")
                self.__gui.mouse_click_bg(position3)
                _localVariable.isBossDetected=True
                _firstcheck = False
                cantattk+=1
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
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
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
            # if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192)) or 
            # self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2'], part=1, pos1=(_displayChat+35, 555), pos2=(_displayChat+95, 605))) != False:

            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2'], part=1, pos1=(_displayChat+35, 555), pos2=(_displayChat+95, 605))) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED_CP"], part=1, pos1=(_displayChat+360, 80), pos2=(_displayChat+500, 160)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S1"], part=1, pos1=(_displayChat+326, 119), pos2=(_displayChat+434, 215)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S3"], part=1, pos1=(_displayChat+50, 550), pos2=(_displayChat+450, 610)) != False) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'])) != False:
                logging.info("Battle End, Victory!")
                cantattk=0
                self.game_utils.reset_idle_count()
                while True:
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(560, 300), pos2=(607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or 
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180)) != False):
                        time.sleep(1)
                        break
                    #soulmax
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                        logging.info('Closed "Soul limit Maxed out" popup!')
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)
                        continue
                break

            #==========================================Reward settlement=============================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_GET_REWARD'],part=1, pos1=(_displayChat+190, 310), pos2=(_displayChat+921, 561))
            if position != False:
                logging.info("Challenge finished. Exiting for next round.")
                self.__gui.send_esc_down()
                time.sleep(2)
                self.__gui.mouse_click_bg((_displayChat+655, 383))
                self.game_utils.reset_idle_count()
                
            #soulmax
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                logging.info('Closed "Soul limit Maxed out" popup!')
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)
                continue
                
            else:
                self.game_utils.reset_idle_count()
    
    def gameModeRealmRaid(self):
        global _cAttackRealm, _displayChat, _is3Realm, _isFail, _exit, _firstcheck, count
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            IMAGE_REALM_COOLDOWN = self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_COOLDOWN'], part=1, pos1=(_displayChat+840, 490), pos2=(_displayChat+1025, 570), threshold=0.95)
            if (INBATTLE != False and COOP_QUEST == False and _isFail < 3) or (IMAGE_REALM_COOLDOWN != False and (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAID'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAIDFROG'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571))) and _isFail >= 3):
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue
                
            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            #If Found Daruma
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_FN3R'], part=1, pos1=(_displayChat+451, 413), pos2=(_displayChat+675, 545))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            if position and position2:
                logging.info('3 Realm Raid Reward')
                time.sleep(2)
                self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                time.sleep(2)
                _is3Realm = True
            
            Fail_count = self.__gui.find_game_img_count(self.__gui.templates['IMAGE_REALM_RAID_FAILED'], part=1, pos1=(_displayChat+117, 115), pos2=(_displayChat+1020, 490))
            # logging.debug('Raid Failed:%s', Fail_count)
            if Fail_count >= 3:
                logging.debug('set "_isFail = %s"', Fail_count)
                _isFail = Fail_count
            
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+555, 430)) != False:
                logging.info("Exit Battle..")
                time.sleep(0.4)
                self.__gui.mouse_click_bg((_displayChat+655, 383))
                _exit = True

            #not enough ticket
            # if self.__gameMode == 6:
            position = (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET'], part=1, pos1=(1005, 10), pos2=(1105, 45), threshold=0.97) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET'], part=1, pos1=(1530, 10), pos2=(1630, 45), threshold=0.97))
            if  position:
                time.sleep(1)
                logging.info("Game Mode Story")
                self.__gui.mouse_click_bg((_displayChat+1063, 116))
                time.sleep(2)
                if _firstcheck == False:
                    count+=1
                    self.game_utils.create_file(data=str(count))
                    _firstcheck = True
                self.gameModeExplore_3Realm()

            #Click icon realm
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_RAID'], part=1, pos1=(_displayChat+44, 547), pos2=(_displayChat+664, 632))
            if position != False:
                logging.info("Enter Realm Raid!")
                self.__gui.mouse_click_bg(position)
                time.sleep(1)
                continue
            
            #lock line up
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_LOCK'], part=1, pos1=(_displayChat+713, 512), pos2=(_displayChat+775, 556))
            if position != False:
                logging.info("Successfully lock lineup...")
                self.__gui.mouse_click_bg(position)
                continue
            
            if _is3Realm == False:
                position=(self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAID'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAIDFROG'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)))
                if position == False:
                    # logging.info('Not Found 3Realm raid icon')
                    # _is3Realm = False
                    pass
                else:
                    logging.debug('set 3Realm raid state = True')
                    _is3Realm = True
                    time.sleep(2)
                    self.__gui.mouse_click_bg((_displayChat+1136, 640))
                    time.sleep(2)

            #Click Realm
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTIONFROG'], part=1, pos1=(_displayChat+117, 115), pos2=(_displayChat+1020, 490), threshold=0.91)
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2'], part=1, pos1=(_displayChat+117, 115), pos2=(_displayChat+1020, 490))
            positionatk=(position or position2)
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK'], part=1, pos1=(_displayChat+242, 296), pos2=(_displayChat+993, 621))
            position4=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_REFRESH'], part=1, pos1=(_displayChat+840, 490), pos2=(_displayChat+1025, 570), threshold=0.96)
            position5=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            #This to Refresh#=========================================================================================================
            if _is3Realm != False and _isFail >= 3 and position4 != False:
                logging.info('Refresh Realm Raid Page!')
                self.__gui.mouse_click_bg(position4)
                time.sleep(1)
                #This to Click OK button
                if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+555, 430)) != False:
                    self.__gui.mouse_click_bg((position4[0]-253,position4[1]-145))
                    logging.debug('set 3Realm raid state = False')
                    _is3Realm = False
                    _isFail = 0
                    time.sleep(1)
            
            if _is3Realm != False and (_isFail < 3) and position5 != False:
                time.sleep(1)
                logging.debug("_isFail : %s", _isFail)
                if positionatk != False and _is3Realm != False:
                        self.__gui.mouse_click_bg(positionatk)
                        logging.info("Attack Realm!")
                        _cAttackRealm+=1
                        _exit = False
                        time.sleep(1)
                        position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK'], part=1, pos1=(_displayChat+280, 315), pos2=(_displayChat+995, 620))
                        if position3:
                            logging.debug('Click Attack Button')
                            self.__gui.mouse_click_bg(position3)
                        else:
                            self.__gui.mouse_click_bg((positionatk[0]-77,positionatk[1]+167))
                        time.sleep(2)
                        while True:
                            if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(560, 300), pos2=(607, 397)):
                                detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                                detectAssistance.setDaemon(True)
                                detectAssistance.start

                            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_BACK'], gray=1) or self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'], gray=1, threshold=0.78)) != False:
                                self.__gui.send_esc_down()
                                time.sleep(0.4)
                                self.__gui.mouse_click_bg((_displayChat+655, 383))
                                self.__gui.mouse_click_bg((_displayChat+655, 383))
                                _exit = True
                                break

            #This Click Enemy#=========================================================================================================
            if _is3Realm == False and position5 != False:
                time.sleep(1)
                if _is3Realm == False and position5 != False:
                    if positionatk != False and _is3Realm == False:
                        logging.info("Attack Realm!")
                        self.__gui.mouse_click_bg(positionatk)
                        time.sleep(2)
                        _cAttackRealm+=1
                        position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK'], part=1, pos1=(_displayChat+280, 315), pos2=(_displayChat+995, 620))
                        time.sleep(0.5)
                        if position3:
                            logging.debug('Click Attack Button')
                            self.__gui.mouse_click_bg(position3)
                        else:
                            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
                            time.sleep(0.5)
                            if position:
                                logging.debug('Click Close')
                                self.__gui.mouse_click_bg(position)
                            else:
                                logging.debug('Click Close with pos')
                                self.__gui.mouse_click_bg((_displayChat+1071, 117))
                            time.sleep(1)
                        # self.gameModeRealmRaid()
                #else====================================================================================================
            if positionatk == False and position4 != False:
                logging.debug("Can't Attalck, Skip!")
                time.sleep(1)
                self.__gui.mouse_click_bg(position4)
                time.sleep(1)
                #This to Click OK button
                if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+555, 430)) != False:
                    self.__gui.mouse_click_bg((position4[0]-253,position4[1]-145))
                    logging.debug('set 3Realm raid state = False')
                    _is3Realm = False
                    time.sleep(1)
            
            #=========================================get ready=================================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
            if position != False:
                # logging.info("Starting battle.... ")
                self.__gui.mouse_click_bg(position)
                time.sleep(2)
                continue
            
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL_BATTLE'], part=1, pos1=(_displayChat+405, 342), pos2=(_displayChat+547, 419)):
                logging.info("Exit Battle..")
                time.sleep(0.4)
                self.__gui.mouse_click_bg((_displayChat+655, 383))
                _exit = True

            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                logging.info("Battle End, Fail..")
                _cAttackRealm=0
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(560, 300), pos2=(607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                    
                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_JADE'])) != False:
                        _cAttackRealm=0
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))

            #check finish
            # if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (
            #     self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
            
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2'], part=1, pos1=(_displayChat+30, 30), pos2=(_displayChat+95, 95))) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED_CP"], part=1, pos1=(_displayChat+360, 80), pos2=(_displayChat+500, 160)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S1"], part=1, pos1=(_displayChat+326, 119), pos2=(_displayChat+434, 215)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S3"], part=1, pos1=(_displayChat+50, 550), pos2=(_displayChat+450, 610)) != False) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
                logging.info("Battle End, Victory!")
                #time.sleep(5)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(560, 300), pos2=(607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_JADE'])) != False:
                        _cAttackRealm=0
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                break

            else:
                time.sleep(1)
    
    def run(self):
        global count
        count=self.__beforetotal
        self.game_utils.create_file(data=str(count))
        _localVariable.detectCount=30
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeExplore_3Realm()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.game_utils.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()