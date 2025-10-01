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
CLICK_FINISH=(35, 510)
cantattk=0
pactst=False
_firstclick=False
_ispact=False

class Bondling(threading.Thread):
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
            "IMAGE_BONDLING_PACT1": config['BONDLING']['IMAGE_BONDLING_PACT1'],
            "IMAGE_BONDLING_PACT2": config['BONDLING']['IMAGE_BONDLING_PACT2'],
            "IMAGE_BONDLING_PACT3": config['BONDLING']['IMAGE_BONDLING_PACT3'],
            "IMAGE_BONDLING_PACT4": config['BONDLING']['IMAGE_BONDLING_PACT4'],
        }

        gray_templates = {
            # BONDLING
            "IMAGE_BONDLING_BONDLING": config['BONDLING']['IMAGE_BONDLING_BONDLING'],
            "IMAGE_BONDLING_SUMMON": config['BONDLING']['IMAGE_BONDLING_SUMMON'],
            "IMAGE_BONDLING_PACTSETTINGS": config['BONDLING']['IMAGE_BONDLING_PACTSETTINGS'],
            "IMAGE_BONDLING_INFO": config['BONDLING']['IMAGE_BONDLING_INFO'],
            "IMAGE_BONDLING_EXPDETECT": config['BONDLING']['IMAGE_BONDLING_EXPDETECT'],
            "IMAGE_BONDLING_BRUSH": config['BONDLING']['IMAGE_BONDLING_BRUSH'],
            "IMAGE_BONDLING_CANCEL": config['BONDLING']['IMAGE_BONDLING_CANCEL'],

            # DEFAULT
            "IMAGE_FAILED": config['DEFAULT']['IMAGE_FAILED'],
            "IMAGE_ROOM_BACK": config['DEFAULT']['IMAGE_ROOM_BACK'],
            "IMAGE_FINISHED0": config['DEFAULT']['IMAGE_FINISHED0'],
            "IMAGE_FINISHED1": config['DEFAULT']['IMAGE_FINISHED1'],
            "IMAGE_FINISHED2": config['DEFAULT']['IMAGE_FINISHED2'],
            "IMAGE_EMPTY_SUSHI": config['DEFAULT']['IMAGE_EMPTY_SUSHI'],
            "IMAGE_EMPTY_SUSHI_CLOSE": config['DEFAULT']['IMAGE_EMPTY_SUSHI_CLOSE'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],

            # SOUL
            "IMAGE_SOUL_INVITE_CHECKBOX": config['SOUL']['IMAGE_SOUL_INVITE_CHECKBOX'],
            "IMAGE_SINGLE_SOUL_LOCK": config['SOUL']['IMAGE_SINGLE_SOUL_LOCK'],
            "IMAGE_SINGLE_SOUL_STAT": config['SOUL']['IMAGE_SINGLE_SOUL_STAT'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],

            # REALM
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],

            # Server (self.__sv)
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

    def gameModeBondling(self):
        global cantattk, pactst, _firstclick, count, _ispact
        CLICK_SOULMAX=(568, 387)
        START_SOUL_COORDINATE=(1075, 565)

        if self.__crystal_use != "false":
            self.__tomb = "false"
            self.__snowball = "false"
            self.__azure = "false"
            self.__kuro = "false"

        while True:  
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue
                
            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start
            time.sleep(1)

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_BONDLING'],part=1, pos1=(_displayChat+726, 540), pos2=(_displayChat+1025, 628))
            if position != False:
                logging.info("Enter Bondling Fairyland!")
                self.__gui.mouse_click_bg(position)
                time.sleep(5)
                continue

            # position = self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACT'], gray=1, threshold=0.70) or self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACT2'], gray=1, threshold=0.70)
            # if position != False and (self.__mode == 'Pact' or self.__mode == 'Both') and (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_EXPDETECT']) != False
            #     ):
            #     logging.info('Pact-forming Found!:%s'%position)
            #     self.__gui.mouse_click_bg(position)
            #     time.sleep(1)

            
            # กำหนด mapping ชื่อ - เงื่อนไขไว้ล่วงหน้า
            pact_targets = [
                {
                    "template": "IMAGE_BONDLING_PACT1",
                    "crystal_value": "1",
                    "mode_check": "tomb",
                    "log_name": "Tomb Guard!",
                    "sleep_time": 2
                },
                {
                    "template": "IMAGE_BONDLING_PACT2",
                    "crystal_value": "2",
                    "mode_check": "snowball",
                    "log_name": "Snowball!",
                    "sleep_time": 2
                },
                {
                    "template": "IMAGE_BONDLING_PACT3",
                    "crystal_value": "3",
                    "mode_check": "azure",
                    "log_name": "Azure Basan!",
                    "sleep_time": 2
                },
                {
                    "template": "IMAGE_BONDLING_PACT4",
                    "crystal_value": "4",
                    "mode_check": "kuro",
                    "log_name": "Kuro!",
                    "sleep_time": 3
                }
            ]

            for pact in pact_targets:
                position = self.__gui.find_game_img(
                    self.__gui.templates[pact["template"]],
                    gray=0,
                    threshold=0.975 ,part=1, pos1=(_displayChat+30, 389), pos2=(_displayChat+1022, 510)
                )

                # ตรงนี้: ดึงชื่อ attribute แบบรองรับ __ ได้
                attr_name = f"_{self.__class__.__name__}__{pact['mode_check']}"
                mode_value = getattr(self, attr_name, None)

                if (self.__bondlingmode in ('Pact', 'Both')) and ((self.__crystal_use == pact["crystal_value"]) or (mode_value == 'true')) and position:
                    logging.info(pact["log_name"])
                    self.__gui.mouse_click_bg(position)
                    _firstclick = False
                    time.sleep(pact["sleep_time"])

            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440))
            if (position != False) and (_firstclick == False):
                self.__gui.mouse_click_bg((_displayChat+50, 500))
                _firstclick = True
            
            
            if self.__bondlingmode == 'Pact' and self.__crystal_use != 'false':
                if (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACT%s'%self.__crystal_use],part=1, pos1=(_displayChat+30, 389), pos2=(_displayChat+1022, 510),threshold=0.96) == False) and (position != False):
                    logging.info("Summon Bondling!")
                    time.sleep(1)
                    self.__gui.mouse_click_bg(position)
                    time.sleep(2)
                    position = self.__gui.find_game_img(self.__gui.templates['IMAGE_ROOM_BACK'],part=1, pos1=(_displayChat+7, 4), pos2=(_displayChat+86, 67))
                    if position != False:
                        logging.info("Selecting Bondling...")
                        if self.__crystal_use == '1':
                            self.__gui.mouse_click_bg((_displayChat+896, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            logging.info("Tomb Guard selected!")
                            time.sleep(5)

                        if self.__crystal_use == '2':
                            self.__gui.mouse_click_bg((_displayChat+405, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            logging.info("Snowball selected!")
                            time.sleep(5)

                        if self.__crystal_use == '3':
                            self.__gui.mouse_click_bg((_displayChat+639, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            logging.info("Azure Basan selected!")
                            time.sleep(5)
                            
                        if self.__crystal_use == '4':
                            self.__gui.mouse_click_bg((_displayChat+190, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            logging.info("Kuro selected!")
                            time.sleep(5)

            
            #Pact Settings
            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACTSETTINGS'],part=1, pos1=(_displayChat+138, 538), pos2=(_displayChat+247, 631))
            if (self.__bondlingmode == 'Pact' or self.__bondlingmode == 'Both') and (position != False) and pactst == False:
                logging.info('Configuring Pact-forming')
                self.__gui.mouse_click_bg(position)
                time.sleep(1)
                position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_CANCEL'],part=1, pos1=(_displayChat+424, 467), pos2=(_displayChat+551, 534))
                if position2 != False:
                    logging.info('Test')
                    self.__gui.mouse_click_bg((position2[0],position2[1]-327))
                    time.sleep(1)
                    if self.__pactsettings == '1':
                        logging.info('Select a Basic Disc..')
                        self.__gui.mouse_click_bg((position2[0],position2[1]-245))
                        time.sleep(1)
                        self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                        if position2 != False:
                            self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                            time.sleep(1)
                    if self.__pactsettings == '2':
                        logging.info('Select a Great Disc..')
                        self.__gui.mouse_click_bg((position2[0]+125,position2[1]-245))
                        time.sleep(1)
                        self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                        if position2 != False:
                            self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                            time.sleep(1)
                    if self.__pactsettings == '3':
                        logging.info('Select a Ultra Disc..')
                        self.__gui.mouse_click_bg((position2[0]+249,position2[1]-245))
                        time.sleep(1)
                        self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                        if position2 != False:
                            self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                            time.sleep(1)
                pactst = True
            
            #lock line up
            position1=self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_SOUL_LOCK'],part=1, pos1=(_displayChat+712, 570), pos2=(_displayChat+782, 613))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440))
            if position1 != False and (position2 or position):
                logging.info("Successfully lock lineup...")
                self.__gui.mouse_click_bg(position1)
                continue
            
            if (self.__bondlingmode == 'Pact' or self.__bondlingmode == 'Both') and (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_INFO'],part=1, pos1=(_displayChat+31, 535), pos2=(_displayChat+132, 623)) != False
                ) and (position != False):
                logging.info('Pact-forming Start!')
                cantattk+=1
                _ispact=True
                self.__gui.mouse_click_bg((_displayChat + 1045, 545))
                time.sleep(1)

            if (self.__bondlingmode == 'Explore' or self.__bondlingmode == 'Both') and (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_EXPDETECT'],part=1, pos1=(_displayChat+525, 576), pos2=(_displayChat+616, 636)) != False
                ) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440)) != False):
                logging.info('Explore Start!')
                cantattk+=1
                self.__gui.mouse_click_bg((_displayChat + 1045, 545))
                time.sleep(3)

            if cantattk >= 10 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE'], part=1, pos1=(_displayChat+792, 143), pos2=(_displayChat+875, 200)) != False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+361, 337), pos2=(_displayChat+575, 420)) != False) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX'], part=1, pos1=(_displayChat+260, 280), pos2=(_displayChat+540, 360)) == False):
                logging.info("Unable to process, Exit!")
                self.game_utils.create_file(str(self.__total))
                subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                            creationflags=subprocess.CREATE_NO_WINDOW)
                return

            gameready=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
            if gameready != False:
                self.__gui.mouse_click_bg(gameready)
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue

            #Pact sucess
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_BRUSH'],part=1, pos1=(_displayChat+22, 67), pos2=(_displayChat+200, 300))
            if position != False and position2 == False:
                logging.info("Pact Formed!")
                cantattk = 0
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_EXPDETECT'],part=1, pos1=(_displayChat+525, 576), pos2=(_displayChat+616, 636)) != False:
                        break
                    self.__gui.mouse_click_bg((position[0], position[1]+120))
                break

            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                cantattk=0
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                        
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204)) == False:
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))

             #check finish
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477)) != False:
                logging.info("Battle End, Victory!")
                cantattk=0
                self.game_utils.reset_idle_count()
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI']) or self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACTSETTINGS'],part=1, pos1=(_displayChat+138, 538), pos2=(_displayChat+247, 631)) != False:
                        logging.info("Round End...")
                        if ((self.__bondlingmode == 'Both') or (self.__bondlingmode == 'Pact')):
                            count-=1
                            break
                        break

                    #soulmax
                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+361, 207), pos2=(_displayChat+778, 343))) != False:
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)
                        continue
                    self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                break

            #soulmax
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)
            
            else:
                continue
    


    def run(self):
        global count
        count=self.__beforetotal
        self.game_utils.create_file(data=str(count))
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeBondling()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.game_utils.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()
