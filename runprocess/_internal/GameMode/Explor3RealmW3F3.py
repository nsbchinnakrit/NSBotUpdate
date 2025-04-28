from Module.GameControl import *
from Module.ThreadGame import *
from Module.Util import *
from Module.loadconfig import *
import time
import pyautogui, subprocess

_localVariable=threading.local()
_displayChat=0
_is3Realm=False
_cAttackRealm=0
_exit = True
cantattk=0
_setround=0
_firstcheck=True
_isFail=0
_idlecount=0

CLICK_SOULMAX=(568, 387)
CLICK_FINISH2=(35, 510)
SLIDE_STORY_COORDINATE=[(_displayChat+200,200),(_displayChat+1000,200)]
START_SOUL_COORDINATE = (1075, 565)

class Explor3RealmW3F3(threading.Thread):
    def __init__(self,Server, windowName, beforetotal, total, pid, bondlingmode, pactsettings, crystal_use, tomb, snowball, azure, kuro, markboss):
        # global svselect
        threading.Thread.__init__(self)
        self.__sv=Server
        self.__hwnd=windowName
        self.__beforetotal=beforetotal
        self.__total=total
        self.__pid=pid
        self.__gui=GameControl(self.__hwnd,0)
    
        color_templates = {
        }

        gray_templates = {
            # EXPLORE
            "IMAGE_STORY_BOX_PATH": config['EXPLORE']['IMAGE_STORY_BOX_PATH'],
            "IMAGE_STORY_FIGHT_PATH": config['EXPLORE']['IMAGE_STORY_FIGHT_PATH'],
            "IMAGE_STORY_FIGHT_BOSS_PATH": config['EXPLORE']['IMAGE_STORY_FIGHT_BOSS_PATH'],
            "IMAGE_STORY_CHERRY_CAKE_PATH": config['EXPLORE']['IMAGE_STORY_CHERRY_CAKE_PATH'],
            "IMAGE_STORY_LIST_CHAPTER_PATH": config['EXPLORE']['IMAGE_STORY_LIST_CHAPTER_PATH'],
            "IMAGE_STORY_GET_REWARD_PATH": config['EXPLORE']['IMAGE_STORY_GET_REWARD_PATH'],
            "IMAGE_STORY_BACK_PATH": config['EXPLORE']['IMAGE_STORY_BACK_PATH'],
            "IMAGE_STORY_AUTOFOOD_PATH": config[self.__sv]['IMAGE_STORY_AUTOFOOD_PATH'],
            "IMAGE_STORY_START_PATH": config[self.__sv]['IMAGE_STORY_START_PATH'],

            # SOUL
            "IMAGE_SOUL_ROOM_DETECT_PATH": config['SOUL']['IMAGE_SOUL_ROOM_DETECT_PATH'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],

            # REALM
            "IMAGE_REALM_FN3R_PATH": config['REALM']['IMAGE_REALM_FN3R_PATH'],
            "IMAGE_REALM_CLOSE": config['REALM']['IMAGE_REALM_CLOSE'],
            "IMAGE_REALM_LOCK_PATH": config['REALM']['IMAGE_REALM_LOCK_PATH'],
            "IMAGE_REALM_3RAID_PATH": config['REALM']['IMAGE_REALM_3RAID_PATH'],
            "IMAGE_REALM_3RAID2_PATH": config['REALM']['IMAGE_REALM_3RAID2_PATH'],
            "IMAGE_REALM_3RAIDFROG_PATH": config['REALM']['IMAGE_REALM_3RAIDFROG_PATH'],
            "IMAGE_REALM_SECTIONFROG_PATH": config['REALM']['IMAGE_REALM_SECTIONFROG_PATH'],
            "IMAGE_REALM_SECTION_PATH": config['REALM']['IMAGE_REALM_SECTION_PATH'],
            "IMAGE_REALM_SECTION2_PATH": config['REALM']['IMAGE_REALM_SECTION2_PATH'],
            "IMAGE_REALM_JADE_PATH": config['REALM']['IMAGE_REALM_JADE_PATH'],
            "IMAGE_REALM_EMPTY_TICKET2": config[self.__sv]['IMAGE_REALM_EMPTY_TICKET2'],
            "IMAGE_REALM_CANCEL_BATTLE": config[self.__sv]['IMAGE_REALM_CANCEL_BATTLE'],
            "IMAGE_REALM_RAID_PATH": config[self.__sv]['IMAGE_REALM_RAID_PATH'],
            "IMAGE_REALM_ATK_PATH": config[self.__sv]['IMAGE_REALM_ATK_PATH'],
            "IMAGE_REALM_REFRESH_PATH": config[self.__sv]['IMAGE_REALM_REFRESH_PATH'],
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],
            "IMAGE_REALM_GUILD_PATH": config[self.__sv]['IMAGE_REALM_GUILD_PATH'],
            "IMAGE_REALM_COOLDOWN": config[self.__sv]['IMAGE_REALM_COOLDOWN'],
            "IMAGE_REALM_RAID_FAILED": config['REALM']['IMAGE_REALM_RAID_FAILED'],

            # REALM - GB & CN
            "IMAGE_REALM_EMPTY_TICKET": config[self.__sv]['IMAGE_REALM_EMPTY_TICKET'],
            "IMAGE_BUFF": config[self.__sv]['IMAGE_BUFF'],

            # DEFAULT
            "IMAGE_FINISHED2_PATH": config['DEFAULT']['IMAGE_FINISHED2_PATH'],
            "IMAGE_FINISHED1_PATH": config['DEFAULT']['IMAGE_FINISHED1_PATH'],
            "IMAGE_FINISHED1S2_PATH": config['DEFAULT']['IMAGE_FINISHED1S2_PATH'],
            "IMAGE_FINISHED1S3_PATH": config['DEFAULT']['IMAGE_FINISHED1S3_PATH'],
            "IMAGE_FAILED_PATH": config['DEFAULT']['IMAGE_FAILED_PATH'],
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
            "IMAGE_READY_PATH": config[self.__sv]['IMAGE_READY_PATH'],
        }


        self.load_templates(gray_templates, gray=1)
        self.load_templates(color_templates, gray=0)
    
    def load_templates(self, paths, gray=1):
        self.__gui.load_templates(paths, gray=gray)
        mode = "GRAY" if gray else "COLOR"
        # logging.info("Event template loaded (%s): %d templates", mode, len(paths))
                
    def gameModeExplore_3Realm(self):
        global _cAttackRealm, _setround, _firstcheck, _idlecount
        logging.debug("Working in [gameModeExplore_3Realm]")
        while True: 
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+448, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                _idlecount+=1
                continue

            detectAssistance = threading.Thread(target=self.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET2'],part=1, pos1=(_displayChat+79, 6), pos2=(_displayChat+940, 47), threshold=0.90)
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER_PATH'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180))  
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILD_PATH'], part=1, pos1=(_displayChat+1000, 194), pos2=(_displayChat+1132, 446))
            position4=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+874, 80), pos2=(_displayChat+1112, 174))
            position5=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX_PATH'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
            #time.sleep(5)
            if position5 != False:
                logging.info("Box Found. (Func.1)")
                self.__gui.mouse_click_bg(position5)
                _idlecount=0
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
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET'],threshold=0.97) !=False:
                        logging.info("Close RealmPage...")
                        self.__gui.mouse_click_bg((_displayChat+1070, 120))
                        if _firstcheck == False:
                            _setround+=1
                            _idlecount=0
                            self.create_file(data=str(_setround))
                            _firstcheck = True
                        time.sleep(1)
                        break
                        #sys.exit()
                    if position4 != False and position3 == False:
                        self.__gui.mouse_click_bg(position4)
                        logging.info('Close Explore Page.')
                        #Click icon realm
                        time.sleep(1)
                        self.gameModeRealmRaid()
                        break
                    else:
                        self.gameModeRealmRaid()

            if position == False and position2 != False or self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_START_PATH'],part=1, pos1=(_displayChat+770, 448), pos2=(_displayChat+907, 517)) != False:
                self.gameModeExplor()
            
            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'])
            if position != False:
                logging.info("Battle End, Fail..")
                cantattk=0
                _cAttackRealm=0
                _idlecount=0
                self.__gui.mouse_click_bg(position)
                continue

            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH']) or self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2_PATH'], part=1, pos1=(_displayChat+30, 30), pos2=(_displayChat+95, 95)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S3_PATH']) or self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'])) != False:
                logging.info("Battle End, Victory!")
                cantattk=0
                _idlecount=0
                while True:
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or (
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_BUFF'])) != False:
                        break
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+874, 80), pos2=(_displayChat+1112, 174)) != False or self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False:
                        _cAttackRealm=0
                        break
                break

            #soulmax
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                logging.info("Soul Max")
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)
                continue

            else:
                _idlecount+=1
    
    def gameModeExplor(self):
        global _displayChat, _cAutoRotation, cantattk, _setround, _firstcheck, _idlecount
        logging.debug("Working in [gameModeExplor]")
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+369, 600), pos2=(_displayChat+448, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                _idlecount+=1
                continue
                
            detectAssistance = threading.Thread(target=self.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX_PATH'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'],part=1, pos1=(_displayChat+896, 101), pos2=(_displayChat+964, 171))
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILD_PATH'], part=1, pos1=(_displayChat+1000, 194), pos2=(_displayChat+1132, 446))    

            if position != False:
                logging.info("Box Found. (Func.2)")
                self.__gui.mouse_click_bg(position)
                time.sleep(4)
                if position != False and position2 != False:
                    self.__gui.mouse_click_bg(position2)
                    time.sleep(1)
                self.__gui.mouse_click_bg(position)
                time.sleep(1)

            if cantattk >= 12 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE'], part=1, pos1=(_displayChat+792, 143), pos2=(_displayChat+875, 200)) != False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+361, 337), pos2=(_displayChat+575, 420)) != False) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX_PATH'], part=1, pos1=(_displayChat+260, 280), pos2=(_displayChat+424, 332)) == False):
                logging.info("Unable to process, Exit!")
                total = str(self.__total)
                self.create_file(data=total)
                args = ['taskkill', '/F', '/PID', str(self.__pid)]
                subprocess.Popen(args)
                sys.exit()
            
            if position2 != False and position3 != False:
                logging.debug("Return to Main function")
                self.gameModeExplore_3Realm()
                
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_AUTOFOOD_PATH'],part=1, pos1=(_displayChat+90, 575), pos2=(_displayChat+265, 625))
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

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49))
            if position == False:
                time.sleep(1)
                position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER_PATH'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180))  
                if _firstcheck == False and (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET2'],part=1, pos1=(_displayChat+79, 6), pos2=(_displayChat+940, 47))) != False:
                    _setround+=1
                    _idlecount=0
                    self.create_file(data=str(_setround))
                    _firstcheck = True
                    self.gameModeExplore_3Realm() 
                elif position != False:
                    _localVariable.isBossDetected=False
                    logging.info("Entering last chapter..")
                    self.__gui.mouse_click_bg((position[0],position[1]+370))
                    _idlecount=0
                    time.sleep(1)
                    continue
                
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_START_PATH'],part=1, pos1=(_displayChat+770, 448), pos2=(_displayChat+907, 517))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX_PATH'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
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
                                detectAssistance = threading.Thread(target=self.detectAssistance())
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
                    logging.info("Starting exploration.... ")
                    self.__gui.mouse_click_bg(position)
                    cantattk+=1
                    _firstcheck = False
                    _idlecount=0
                    continue
                else:
                    self.__gui.mouse_click_bg(position3)
                    time.sleep(1)
                    break
            
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_PATH'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49))
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_BOSS_PATH'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            if position == False and position2 != False and position3 == False:
                if (position == False) and (position3 == False):
                    self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[1],SLIDE_STORY_COORDINATE[0])
                    _localVariable.detectCount -= 1
                    if _localVariable.detectCount < 1:
                        # self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[1],SLIDE_STORY_COORDINATE[0])
                        self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[0],SLIDE_STORY_COORDINATE[1])
                        _localVariable.detectCount=30
            if position3 != False:
                logging.info("BOSS was detected: ")
                self.__gui.mouse_click_bg(position3)
                _localVariable.isBossDetected=True
                _firstcheck = False
                cantattk+=1
                _idlecount=0
                time.sleep(1)
                continue

            if position != False:
                logging.info("Monster was detected... ")
                self.__gui.mouse_click_bg(position)
                cantattk+=1
                _idlecount=0
                time.sleep(1)
                continue

            #=========================================get ready=================================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY_PATH'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
            if position != False:
                logging.info("Starting battle.... ")
                self.__gui.mouse_click_bg(position)
                #time.sleep(2)
                continue

            #=========================================Finish=================================================
            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                cantattk=0
                _idlecount=0
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                continue

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))
            if position != False:
                cantattk=0
                _idlecount=0
                self.__gui.mouse_click_bg(position)
                continue


            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2_PATH'], part=1, pos1=(_displayChat+35, 555), pos2=(_displayChat+95, 605))) != False:
                logging.info("Battle End, Victory!")
                cantattk=0
                _idlecount=0
                while True:
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or 
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER_PATH'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180)) != False):
                        time.sleep(1)
                        break
                    #soulmax
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                        logging.info("Soul Max")
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)
                        continue
                break

            #==========================================Reward settlement=============================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_GET_REWARD_PATH'],part=1, pos1=(_displayChat+190, 310), pos2=(_displayChat+921, 561))
            if position != False:
                logging.info("Get treasure.... ")
                self.__gui.send_esc_down()
                time.sleep(2)
                self.__gui.mouse_click_bg((_displayChat+655, 383))
                _idlecount=0
                
            #soulmax
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                logging.info("Soul Max")
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)
                continue
                
            else:
                _idlecount+=1
    
    def gameModeRealmRaid(self):
        global _cAttackRealm, _displayChat, _is3Realm, _setround, _firstcheck, _idlecount, _isFail
        logging.debug("Working in [gameModeRealmRaid]")
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            IMAGE_REALM_COOLDOWN = self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_COOLDOWN'], part=1, pos1=(_displayChat+840, 490), pos2=(_displayChat+1025, 570), threshold=0.95)
            if (INBATTLE != False and COOP_QUEST == False and _isFail < 3) or (IMAGE_REALM_COOLDOWN != False and (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAID_PATH'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAIDFROG_PATH'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571))) and _isFail >= 3):
                time.sleep(1)
                _idlecount+=1
                continue

            detectAssistance = threading.Thread(target=self.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            #If Found Daruma
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_FN3R_PATH'], part=1, pos1=(_displayChat+451, 413), pos2=(_displayChat+675, 545))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            if position and position2:
                logging.info('3 Realm Raid Reward')
                time.sleep(2)
                self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                time.sleep(2)
                _is3Realm = True
                _idlecount=0
            
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
            position = (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET'], part=1, pos1=(_displayChat+1005, 10), pos2=(_displayChat+1105, 45), threshold=0.97))
            if  position:
                time.sleep(1)
                logging.info("Game Mode Story")
                self.__gui.mouse_click_bg((_displayChat+1063, 116))
                time.sleep(2)
                if _firstcheck == False:
                    _setround+=1
                    self.create_file(data=str(_setround))
                    _firstcheck = True
                    _idlecount=0
                self.gameModeExplore_3Realm()

            #Click icon realm
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_RAID_PATH'], part=1, pos1=(_displayChat+44, 547), pos2=(_displayChat+664, 632))
            if position != False:
                logging.info("Click icon realm raid...")
                self.__gui.mouse_click_bg(position)
                time.sleep(3)
                continue
            
            #lock line up
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_LOCK_PATH'], part=1, pos1=(_displayChat+713, 512), pos2=(_displayChat+775, 556))
            if position != False:
                logging.info("Successfully lock lineup...")
                self.__gui.mouse_click_bg(position)
                continue
            
            if _is3Realm == False:
                position=(self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAID_PATH'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAIDFROG_PATH'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)))
                if position == False:
                    # logging.info('Not Found 3Realm raid icon')
                    # _is3Realm = False
                    pass
                else:
                    logging.debug('set 3Realm raid state = True')
                    _is3Realm = True

            #Click Realm
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTIONFROG_PATH'], part=1, pos1=(_displayChat+117, 115), pos2=(_displayChat+1020, 490), threshold=0.91)
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2_PATH'], part=1, pos1=(_displayChat+117, 115), pos2=(_displayChat+1020, 490))
            positionatk=(position or position2)
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK_PATH'], part=1, pos1=(_displayChat+242, 296), pos2=(_displayChat+993, 621))
            position4=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_REFRESH_PATH'], part=1, pos1=(_displayChat+840, 490), pos2=(_displayChat+1025, 570), threshold=0.96)
            position5=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            #This to Refresh#=========================================================================================================
            if _is3Realm != False and _isFail >= 3 and position4 != False:
                logging.debug('This should refresh')
                self.__gui.mouse_click_bg(position4)
                time.sleep(1)
                #This to Click OK button
                if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+555, 430)) != False:
                    self.__gui.mouse_click_bg((position4[0]-253,position4[1]-145))
                    logging.debug('set 3Realm raid state = False')
                    _is3Realm = False
                    _isFail = 0
                    _idlecount=0
                    time.sleep(1)
            
            if _is3Realm != False and (_isFail < 3) and position5 != False:
                time.sleep(1)
                logging.debug("_isFail : %s", _isFail)
                if positionatk != False and _is3Realm != False:
                        self.__gui.mouse_click_bg(positionatk)
                        logging.info("Click Enemy Section..")
                        _cAttackRealm+=1
                        _exit = False
                        _idlecount=0
                        time.sleep(1)
                        position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK_PATH'], part=1, pos1=(_displayChat+280, 315), pos2=(_displayChat+995, 620))
                        if position3:
                            logging.debug('Click Attack Button')
                            self.__gui.mouse_click_bg(position3)
                        else:
                            self.__gui.mouse_click_bg((positionatk[0]-77,positionatk[1]+167))
                        time.sleep(2)
                        _idlecount=0
                        while True:
                            _idlecount+=1
                            if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(560, 300), pos2=(607, 397)):
                                detectAssistance = threading.Thread(target=self.detectAssistance())
                                detectAssistance.setDaemon(True)
                                detectAssistance.start

                            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_BACK'], gray=1) or self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'], gray=1, threshold=0.78)) != False:
                                self.__gui.send_esc_down()
                                time.sleep(0.4)
                                self.__gui.mouse_click_bg((_displayChat+655, 383))
                                self.__gui.mouse_click_bg((_displayChat+655, 383))
                                _exit = True
                                break

                            if _idlecount>=80:
                                self.__gui.mouse_click_bg((_displayChat+1071, 117))
                                break

            #This Click Enemy#=========================================================================================================
            if _is3Realm == False and position5 != False:
                time.sleep(1)
                if _is3Realm == False and position5 != False:
                    if positionatk != False and _is3Realm == False:
                        logging.info("Click Enemy Section..")
                        self.__gui.mouse_click_bg(positionatk)
                        time.sleep(2)
                        _cAttackRealm+=1
                        _idlecount=0
                        position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK_PATH'], part=1, pos1=(_displayChat+280, 315), pos2=(_displayChat+995, 620))
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
                logging.debug('This is "Enemy Cant Attalck"')
                time.sleep(1)
                self.__gui.mouse_click_bg(position4)
                time.sleep(1)
                #This to Click OK button
                if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+555, 430)) != False:
                    self.__gui.mouse_click_bg((position4[0]-253,position4[1]-145))
                    logging.debug('set 3Realm raid state = False')
                    _is3Realm = False
                    _idlecount=0
                    time.sleep(1)
            
            #=========================================get ready=================================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY_PATH'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
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
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                logging.info("Battle End, Fail..")
                _cAttackRealm=0
                _idlecount=0
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(560, 300), pos2=(607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                    
                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))) != False:
                        _cAttackRealm=0
                        _idlecount=0
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))

            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
                logging.info("Battle End, Victory!")
                #time.sleep(5)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(560, 300), pos2=(607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))) != False:
                        _cAttackRealm=0
                        _idlecount=0
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                break

            else:
                _idlecount+=1
                time.sleep(1)
    
    def detectAssistance(self):
        global _displayChat, _idlecount
        position1 = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
        position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397))
        position3 = self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])
        # position4 = self.__gui.find_game_img(self.__gui.templates['IMAGE_CLOSEWANTED'])
        wq_jade = config['VALUE']['WQ_JADE']
        wq_coin = config['VALUE']['WQ_COIN']
        wq_sushi = config['VALUE']['WQ_SUSHI']
        wq_food = config['VALUE']['WQ_FOOD']

        if _displayChat == 0 and position3:
            _displayChat = 525
            self.__gui.recheckRect()
            logging.info('External chat detected.')

        if (not position3) and position2:
            self.__gui.mouse_click_bg(position2)
            _displayChat = 0
            self.__gui.recheckRect()
            logging.info('ChatPanel detected, closed!')

        if position1:
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_JADE']) and wq_jade
            ) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_COIN']) and wq_coin
            ) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_SUSHI']) and wq_sushi
            ) or ((self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_FOODDOG']) or self.__gui.find_game_img(self.__gui.templates['IMAGE_WQ_FOODCAT'])) and wq_food):
                logging.info("Accept wanted quest!")
                self.__gui.mouse_click_bg((_displayChat+757, 368))
                screenshot = self.__gui.takescreenshot('คนเหลี่ยมๆ')
                self.create_file2(data=screenshot)
            else:
                logging.info("Refuse to accept the invitation for the wanted seal.")
                self.__gui.mouse_click_bg((_displayChat+757, 461))
                self.__gui.takescreenshot('คนเหลี่ยมๆ')
        
        # if position4 != False:
        #     logging.info('Close Event Wanted!')
        #     self.__gui.mouse_click_bg(position4)
        
        if _idlecount >= 1200:
            logging.info("Idle Count = 1200, Exit.")
            total = str(self.__total)
            self.create_file(data=total)
            args = ['taskkill', '/F', '/PID', str(self.__pid)]
            subprocess.Popen(args)
            sys.exit()


    def create_file(self, data='0'):
        temp_path = f"runprocess/temp{self.__pid}.txt"
        try:
            with open(temp_path, "w") as file:
                file.write(data)
                file.close
        except Exception as error:
            logging.error(error)
    
    def create_file2(self, data='False'):
        temp_path = f"runprocess/wanted{self.__pid}.txt"
        try:
            with open(temp_path, "w") as file:
                file.write(data)
                file.close
        except Exception as error:
            logging.error(error)

    def run(self):
        count=self.__beforetotal
        self.create_file(data=str(count))
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
            # self.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()