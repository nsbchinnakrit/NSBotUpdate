import time
import pyautogui
from Module.GameControl import *
from Module.ThreadGame import *
from Module.loadconfig import *
from Module.Util import *
import threading, subprocess

_displayChat = 0
cantattk=0
_idlecount=0
CLICK_SOULMAX=(568, 387)
START_SOUL_COORDINATE = (1075, 565)

class Soul(threading.Thread):
    def __init__(self,Server, windowName, beforetotal, total, pid, bondlingmode, pactsettings, crystal_use, tomb, snowball, azure, kuro, markboss):
        # global svselect
        threading.Thread.__init__(self)
        self.__sv=Server
        self.__hwnd=windowName
        self.__beforetotal=beforetotal
        self.__total=total
        self.__pid=pid
        self.__bossmark=markboss
        self.__gui=GameControl(self.__hwnd,0)

        color_templates = {
            "IMAGE_SOUL_START_PATH": config[self.__sv]['IMAGE_SOUL_START_PATH'],
        }

        gray_templates = {
            # SOUL
            "IMAGE_SOUL_INVITE_PATH": config['SOUL']['IMAGE_SOUL_INVITE_PATH'],
            "IMAGE_SOUL_AUTOACCEPT_PATH": config['SOUL']['IMAGE_SOUL_AUTOACCEPT_PATH'],
            "IMAGE_SOUL_INVITE_CHECKBOX_PATH": config['SOUL']['IMAGE_SOUL_INVITE_CHECKBOX_PATH'],
            "IMAGE_SOUL_ROOM_DETECT_PATH": config['SOUL']['IMAGE_SOUL_ROOM_DETECT_PATH'],
            "IMAGE_SOUL_PETREWARD_PATH": config[self.__sv]['IMAGE_SOUL_PETREWARD_PATH'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],

            # REALM
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],

            # DEFAULT
            "IMAGE_FAILED_PATH": config['DEFAULT']['IMAGE_FAILED_PATH'],
            "IMAGE_EMPTY_SUSHI": config['DEFAULT']['IMAGE_EMPTY_SUSHI'],
            "IMAGE_EMPTY_SUSHI_CLOSE": config['DEFAULT']['IMAGE_EMPTY_SUSHI_CLOSE'],
            "IMAGE_MAIL": config['DEFAULT']['IMAGE_MAIL'],
            "IMAGE_BOSSHP": config['DEFAULT']['IMAGE_BOSSHP'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],
            "IMAGE_BOSSMARK": config[self.__sv]['IMAGE_BOSSMARK'],

            # FINISH
            "IMAGE_FINISHED0_PATH": config['DEFAULT']['IMAGE_FINISHED0_PATH'],
            "IMAGE_FINISHED1_PATH": config['DEFAULT']['IMAGE_FINISHED1_PATH'],
            "IMAGE_FINISHED1S2_PATH": config['DEFAULT']['IMAGE_FINISHED1S2_PATH'],
            "IMAGE_FINISHED2_PATH": config['DEFAULT']['IMAGE_FINISHED2_PATH'],

            # SERVER (shared)
            "IMAGE_READY_PATH": config[self.__sv]['IMAGE_READY_PATH'],
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
        global _displayChat, cantattk, _idlecount
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+459, 600), pos2=(_displayChat+544, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                _idlecount+=1
                continue

            detectAssistance = threading.Thread(target=self.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_START_PATH'],gray=0 , part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1136, 640))
            position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_PATH'], part=1, pos1=(528, 185), pos2=(631, 270))
            if (position) and (not position2):
                time.sleep(0.5)
                logging.info("Starting...")
                self.__gui.mouse_click_bg(position)
                cantattk+=1
                _idlecount=0
                # time.sleep(1)
                # return
            
            if cantattk >= 12 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE'], part=1, pos1=(_displayChat+792, 143), pos2=(_displayChat+875, 200)) != False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+361, 337), pos2=(_displayChat+575, 420)) != False) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX_PATH'], part=1, pos1=(_displayChat+260, 280), pos2=(_displayChat+424, 332)) == False):
                logging.info("Unable to process, Exit!")
                total = str(self.__total)
                self.create_file(data=total)
                args = ['taskkill', '/F', '/PID', str(self.__pid)]
                subprocess.Popen(args)
                sys.exit()

            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_AUTOACCEPT_PATH'], part=1, pos1=(_displayChat+184, 200), pos2=(_displayChat+250, 260))
            if position:
                logging.info("Accept Invited..")
                self.__gui.mouse_click_bg(position)
                time.sleep(1)
                # return

            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX_PATH'], part=1, pos1=(_displayChat+260, 280), pos2=(_displayChat+424, 332))
            if position:
                logging.info("Invited..")
                self.__gui.mouse_click_bg(position)
                time.sleep(0.5)
                self.__gui.mouse_click_bg((_displayChat + position[0] + 247, position[1] + 77))
                time.sleep(1)
                # return
            
            #=========================================get ready=================================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY_PATH'], part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1106, 607), threshold=0.8)
            if position != False:
                self.__gui.mouse_click_bg(position)
                time.sleep(2)
                continue

            if (
                # self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED0_PATH']) or 
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192)) or
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2_PATH'], part=1, pos1=(_displayChat+30, 30), pos2=(_displayChat+920, 550)) or
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))
            ):
                cantattk=0
                _idlecount=0
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_ROOM_DETECT_PATH'], part=1, pos1=(_displayChat+20, 455), pos2=(_displayChat+81, 535)) or
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX_PATH'], part=1, pos1=(_displayChat+260, 280), pos2=(_displayChat+424, 332)) or
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_START_PATH'],gray=0, part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1136, 640)) or
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_MAIL'], part=1, pos1=(_displayChat+996, 4), pos2=(_displayChat+1124, 63),threshold=0.96) or
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_AUTOACCEPT_PATH'], part=1, pos1=(_displayChat+184, 200), pos2=(_displayChat+250, 260)) or 
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450))
                    ):
                        break

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                        logging.info("Soul Max")
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)

                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_PETREWARD_PATH'], part=1, pos1=(_displayChat+103, 197), pos2=(_displayChat+304, 282)):
                        logging.info("Claim Pet Reward.")
                        self.__gui.mouse_click_bg((_displayChat + 950, 450))
                    self.__gui.mouse_click_bg(START_SOUL_COORDINATE)
                break

            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 20), pos2=(_displayChat+423, 204))
            if position:
                cantattk=0
                _idlecount=0
                logging.info("Failed...")
                self.__gui.mouse_click_bg(position)
            
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_PETREWARD_PATH'], part=1, pos1=(_displayChat+103, 197), pos2=(_displayChat+304, 282)):
                logging.info("Claim Pet Reward.")
                self.__gui.mouse_click_bg((_displayChat + 950, 450))
                time.sleep(1)
            
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                logging.info("Soul Max")
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)

            else:
                _idlecount+=1

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
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeSoul()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()