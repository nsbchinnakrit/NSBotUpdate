from Module.GameControl import *
from Module.ThreadGame import *
from Module.Util import *
from Module.loadconfig import *
from Module.logsystem import MyLog
import time, subprocess
import logging

_localVariable=threading.local()
_displayChat=0
cantattk=0
_idlecount=0

class Event(threading.Thread):
    def __init__(self,Server, windowName, beforetotal, total, pid, bondlingmode, pactsettings, crystal_use, tomb, snowball, azure, kuro, markboss):
        # global Server
        threading.Thread.__init__(self)
        self.__sv=Server
        self.__hwnd=windowName
        self.__beforetotal=beforetotal
        self.__total=total
        self.__pid=pid
        self.__bossmark=markboss
        self.__gui=GameControl(self.__hwnd, self.load_templates, 0)

        color_templates = {
        }

        gray_templates = {
            "IMAGE_EVENT_LOCK": config['EVENT']['IMAGE_EVENT_LOCK'],
            "IMAGE_EVENT_LOCKED": config['EVENT']['IMAGE_EVENT_LOCKED'],
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],
            "IMAGE_READY_PATH": config[self.__sv]['IMAGE_READY_PATH'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],
            "IMAGE_BOSSMARK": config[self.__sv]['IMAGE_BOSSMARK'],
            "IMAGE_BOSSHP": config['DEFAULT']['IMAGE_BOSSHP'],
            "IMAGE_FAILED_PATH": config['DEFAULT']['IMAGE_FAILED_PATH'],
            "IMAGE_FINISHED1_PATH": config['DEFAULT']['IMAGE_FINISHED1_PATH'],
            "IMAGE_FINISHED1S1_PATH": config['DEFAULT']['IMAGE_FINISHED1S1_PATH'],
            "IMAGE_FINISHED2_PATH": config['DEFAULT']['IMAGE_FINISHED2_PATH'],
            "IMAGE_BACK2": config['DEFAULT']['IMAGE_BACK2'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],

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
        global _displayChat, cantattk, _idlecount
        CLICK_SOULMAX=(568, 387)
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                _idlecount+=1
                continue

            detectAssistance = threading.Thread(target=self.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start
            
            # position = (self.__gui.find_game_img(
            #     config['EVENT']['IMAGE_EVENT_TARGET'], threshold=0.87) or self.__gui.find_game_img(self.__gui.templates['IMAGE_EVENT_TARGET'], threshold=0.80))
            # position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_EVENT_ATT'])
            # if position != False and position2 == False:
            #     self.__gui.mouse_click_bg(position)
            #     _idlecount=0
            #     time.sleep(10)
                
            # position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_EVENT_ATT'])
            # if position2 != False:
            #     self.__gui.mouse_click_bg(position2)
            #     _idlecount=0

            position = self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCK"], part=1, pos1=(_displayChat+704, 568), pos2=(_displayChat+769, 613))
            if position != False:
                self.__gui.mouse_click_bg(position)
                _idlecount=0
                time.sleep(1)
                continue

            position = self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCKED"], part=1, pos1=(_displayChat+704, 568), pos2=(_displayChat+769, 613), threshold=0.84)
            if position != False:
                logging.info('Start')
                self.__gui.mouse_click_bg((position[0]+276, position[1]+0))
                _idlecount=0
                time.sleep(1)
                continue

            # position = (self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_SOUL_STAT_PATH'], threshold=0.96) or self.__gui.find_game_img(self.__gui.templates['IMAGE_EVENT_START'], threshold= 0.9) or self.__gui.find_game_img(self.__gui.templates['IMAGE_EVENT_START2'], threshold= 0.9))
            # if position != False:
            #     time.sleep(0.5)
            #     logging.info('Start')
            #     cantattk+=1
            #     self.__gui.mouse_click_bg(position)
            #     _idlecount=0
            #     time.sleep(1)
            #     continue

            if cantattk >= 5 or (self.__gui.find_game_img(self.__gui.templates["IMAGE_REALM_CANCEL"], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+575, 420)) != False):
                logging.info("Unable to process, Exit!")
                total = str(self.__total)
                self.create_file(data=total)
                args = ['taskkill', '/F', '/PID', str(self.__pid)]
                subprocess.Popen(args)
                sys.exit()

            #=========================================get ready=================================================
            # position=self.__gui.find_game_img(self.__gui.templates["IMAGE_READY_PATH"],threshold=0.8)
            # if position != False:
            #     self.__gui.mouse_click_bg(position)
            #     time.sleep(2)
            #     continue
            
            position=self.__gui.find_game_img(self.__gui.templates["IMAGE_FAILED_PATH"], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                cantattk=0
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                _idlecount=0
                continue
                
            #check finish
            # if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH']) != False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S1_PATH']) != False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH']) != False):
            if (self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1_PATH"], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192)) != False) or (self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S1_PATH"], part=1, pos1=(_displayChat+326, 119), pos2=(_displayChat+434, 215)) != False) or (self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED2_PATH"], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477)) != False):
                logging.info("Battle End, Victory!")
                cantattk=0
                _idlecount=0
                while True:
                    # if self.__gui.find_game_img(config[self.__sv]['IMAGE_COOP2_SEAL']) or (_displayChat == 0 and self.__gui.find_game_img(config[self.__sv]['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(config[self.__sv]['IMAGE_CHATSTICKER']):
                    if self.__gui.find_game_img(self.__gui.templates["IMAGE_COOP2_SEAL"], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates["IMAGE_CHATDETECT"])) or self.__gui.find_game_img(self.__gui.templates["IMAGE_CHATSTICKER"], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    # if (self.__gui.find_game_img(self.__gui.templates['IMAGE_EVENT_LOCKED'],threshold=0.84)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_EVENT_LOCK'],threshold=0.84):
                    if (self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCKED"], part=1, pos1=(_displayChat+704, 568), pos2=(_displayChat+769, 613), threshold=0.84)) or self.__gui.find_game_img(self.__gui.templates["IMAGE_EVENT_LOCK"], part=1, pos1=(_displayChat+704, 568), pos2=(_displayChat+769, 613), threshold=0.84):
                        break

                    #soulmax
                    # if (self.__gui.find_game_img(config[self.__sv]['IMAGE_SOULMAX'])) != False:
                    if (self.__gui.find_game_img(self.__gui.templates["IMAGE_SOULMAX"], part=1, pos1=(_displayChat+361, 207), pos2=(_displayChat+778, 343))) != False:
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)
                        continue
                    self.__gui.mouse_click_bg((_displayChat+35, 540))
                break

            #soulmax
            # if self.__gui.find_game_img(config[self.__sv]['IMAGE_SOULMAX']) != False:
            if self.__gui.find_game_img(self.__gui.templates["IMAGE_SOULMAX"], part=1, pos1=(_displayChat+361, 207), pos2=(_displayChat+778, 343)) != False:
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                _idlecount=0
                time.sleep(1)
            
            else:
                _idlecount+=1
            
            time.sleep(0.2)
    
    def detectAssistance(self):
        global _displayChat, _idlecount
        position1 = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
        # position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397))
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
        _localVariable.detectCount=10
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeEvent()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()
