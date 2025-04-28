from Module.GameControl import *
from Module.ThreadGame import *
from Module.Util import *
from Module.loadconfig import *
import time, subprocess

_localVariable=threading.local()
_displayChat=0
cantattk=0
pactst=False
_idlecount=0
_firstclick=False
_ispact=False

class Bondling(threading.Thread):
    def __init__(self,Server, windowName, beforetotal, total, pid, bondlingmode, pactsettings, crystal_use, tomb, snowball, azure, kuro, markboss):
        # global self.__sv
        threading.Thread.__init__(self)
        self.__sv=Server
        # self.__sv=self.__server
        self.__hwnd=windowName
        self.__beforetotal=beforetotal
        self.__total=total
        self.__pid=pid
        self.__mode=bondlingmode
        self.__pact=pactsettings
        self.__crystal=crystal_use
        self.__tomb=tomb
        self.__snowball=snowball
        self.__azure=azure
        self.__kuro=kuro
        self.__gui=GameControl(self.__hwnd,0)

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
            "IMAGE_FAILED_PATH": config['DEFAULT']['IMAGE_FAILED_PATH'],
            "IMAGE_ROOM_BACK": config['DEFAULT']['IMAGE_ROOM_BACK'],
            "IMAGE_FINISHED0_PATH": config['DEFAULT']['IMAGE_FINISHED0_PATH'],
            "IMAGE_FINISHED1_PATH": config['DEFAULT']['IMAGE_FINISHED1_PATH'],
            "IMAGE_FINISHED2_PATH": config['DEFAULT']['IMAGE_FINISHED2_PATH'],
            "IMAGE_EMPTY_SUSHI": config['DEFAULT']['IMAGE_EMPTY_SUSHI'],
            "IMAGE_EMPTY_SUSHI_CLOSE": config['DEFAULT']['IMAGE_EMPTY_SUSHI_CLOSE'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],

            # SOUL
            "IMAGE_SOUL_INVITE_CHECKBOX_PATH": config['SOUL']['IMAGE_SOUL_INVITE_CHECKBOX_PATH'],
            "IMAGE_SINGLE_SOUL_LOCK_PATH": config['SOUL']['IMAGE_SINGLE_SOUL_LOCK_PATH'],
            "IMAGE_SINGLE_SOUL_STAT_PATH": config['SOUL']['IMAGE_SINGLE_SOUL_STAT_PATH'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],

            # REALM
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],

            # Server (self.__sv)
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

    def gameModeBondling(self):
        global cantattk, pactst, _idlecount, _firstclick, count, _ispact
        CLICK_SOULMAX=(568, 387)
        START_SOUL_COORDINATE=(1075, 565)
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
            time.sleep(1)

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_BONDLING'],part=1, pos1=(_displayChat+726, 540), pos2=(_displayChat+1025, 628))
            if position != False:
                logging.info("Enter Bondling Fairyland")
                self.__gui.mouse_click_bg(position)
                _idlecount=0
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
                    threshold=0.95 ,part=1, pos1=(_displayChat+30, 389), pos2=(_displayChat+1022, 510)
                )

                # ตรงนี้: ดึงชื่อ attribute แบบรองรับ __ ได้
                attr_name = f"_{self.__class__.__name__}__{pact['mode_check']}"
                mode_value = getattr(self, attr_name, None)

                if (self.__mode in ('Pact', 'Both')) and ((self.__crystal == pact["crystal_value"]) or (mode_value == 'true')) and position:
                    logging.info(pact["log_name"])
                    self.__gui.mouse_click_bg(position)
                    _idlecount = 0
                    logging.debug("_firstclick = False")
                    _firstclick = False
                    time.sleep(pact["sleep_time"])

            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440))
            if (position != False) and (_firstclick == False):
                self.__gui.mouse_click_bg((_displayChat+50, 500))
                _firstclick = True
            
            
            if self.__mode == 'Pact' and self.__crystal != 'false':
                if (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACT%s'%self.__crystal],part=1, pos1=(_displayChat+30, 389), pos2=(_displayChat+1022, 510)) == False) and (position != False):
                    logging.info("Summon Bondling!")
                    time.sleep(1)
                    self.__gui.mouse_click_bg(position)
                    _idlecount=0
                    time.sleep(2)
                    position = self.__gui.find_game_img(self.__gui.templates['IMAGE_ROOM_BACK'],part=1, pos1=(_displayChat+7, 4), pos2=(_displayChat+86, 67))
                    if position != False:
                        logging.info("Select Bondling!")
                        if self.__crystal == '1':
                            logging.info("Tomb Guard Select!")
                            self.__gui.mouse_click_bg((_displayChat+896, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            time.sleep(5)

                        if self.__crystal == '2':
                            logging.info("Snowball Select!")
                            self.__gui.mouse_click_bg((_displayChat+405, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            time.sleep(5)

                        if self.__crystal == '3':
                            logging.info("Azure Basan Select!")
                            self.__gui.mouse_click_bg((_displayChat+639, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            time.sleep(5)
                            
                        if self.__crystal == '4':
                            logging.info("Kuro Select!")
                            self.__gui.mouse_click_bg((_displayChat+190, 383))
                            time.sleep(1)
                            self.__gui.mouse_click_bg((_displayChat+591, 569))
                            time.sleep(5)

            
            #Pact Settings
            position = self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACTSETTINGS'],part=1, pos1=(_displayChat+138, 538), pos2=(_displayChat+247, 631))
            if (self.__mode == 'Pact' or self.__mode == 'Both') and (position != False) and pactst == False:
                logging.info('Pact Settings')
                self.__gui.mouse_click_bg(position)
                _idlecount=0
                time.sleep(1)
                position2 = self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_CANCEL'],part=1, pos1=(_displayChat+424, 467), pos2=(_displayChat+551, 534))
                if position2 != False:
                    logging.info('Test')
                    self.__gui.mouse_click_bg((position2[0],position2[1]-327))
                    time.sleep(1)
                    if self.__pact == '1':
                        logging.info('select Basic Disc')
                        self.__gui.mouse_click_bg((position2[0],position2[1]-245))
                        time.sleep(1)
                        self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                        if position2 != False:
                            self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                            time.sleep(1)
                    if self.__pact == '2':
                        logging.info('select Great Disc')
                        self.__gui.mouse_click_bg((position2[0]+125,position2[1]-245))
                        time.sleep(1)
                        self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                        if position2 != False:
                            self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                            time.sleep(1)
                    if self.__pact == '3':
                        logging.info('select Ultra Disc')
                        self.__gui.mouse_click_bg((position2[0]+249,position2[1]-245))
                        time.sleep(1)
                        self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                        if position2 != False:
                            self.__gui.mouse_click_bg((position2[0]+180,position2[1]))
                            time.sleep(1)
                pactst = True
            
            #lock line up
            position1=self.__gui.find_game_img(self.__gui.templates['IMAGE_SINGLE_SOUL_LOCK_PATH'],part=1, pos1=(_displayChat+712, 570), pos2=(_displayChat+782, 613))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440))
            if position1 != False and (position2 or position):
                logging.info("Successfully lock lineup...")
                self.__gui.mouse_click_bg(position1)
                _idlecount=0
                continue
            
            if (self.__mode == 'Pact' or self.__mode == 'Both') and (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_INFO'],part=1, pos1=(_displayChat+31, 535), pos2=(_displayChat+132, 623)) != False
                ) and (position != False):
                logging.info('Pact-forming Start')
                cantattk+=1
                _idlecount=0
                _ispact=True
                self.__gui.mouse_click_bg((_displayChat + 1045, 545))
                time.sleep(1)

            if (self.__mode == 'Explore' or self.__mode == 'Both') and (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_EXPDETECT'],part=1, pos1=(_displayChat+525, 576), pos2=(_displayChat+616, 636)) != False
                ) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440)) != False):
                logging.info('Explore Start')
                cantattk+=1
                _idlecount=0
                self.__gui.mouse_click_bg((_displayChat + 1045, 545))
                time.sleep(3)

            if cantattk >= 12 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI']) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE']) == False) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL']) != False) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_CHECKBOX_PATH'], threshold=0.98) == False):
                logging.info("Unable to process, Exit!")
                total = str(self.__total)
                self.create_file(data=total)
                args = ['taskkill', '/F', '/PID', str(self.__pid)]
                subprocess.Popen(args)
                sys.exit()

            gameready=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY_PATH'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
            if gameready != False:
                self.__gui.mouse_click_bg(gameready)
                _idlecount=0
                time.sleep(1)
                continue

            #Pact sucess
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_BRUSH'],part=1, pos1=(_displayChat+22, 67), pos2=(_displayChat+200, 300))
            if position != False and position2 == False:
                logging.info("#Pact sucess")
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_EXPDETECT'],part=1, pos1=(_displayChat+525, 576), pos2=(_displayChat+616, 636)) != False:
                        logging.info("Pact Round End...")
                        # count+=1
                        _idlecount=0
                        break
                    self.__gui.mouse_click_bg((position[0], position[1]+120))
                break

            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                cantattk=0
                _idlecount=0
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                        
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204)) == False:
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))

             #check finish
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477)) != False:
                logging.info("Battle End!")
                cantattk=0
                _idlecount=0
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_SUMMON'],part=1, pos1=(_displayChat+1018, 378), pos2=(_displayChat+1089, 440)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI']) or self.__gui.find_game_img(self.__gui.templates['IMAGE_BONDLING_PACTSETTINGS'],part=1, pos1=(_displayChat+138, 538), pos2=(_displayChat+247, 631)))) != False:
                        logging.info("Round End...")
                        if ((self.__mode == 'Both') or (self.__mode == 'Pact')):
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
                _idlecount=0
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
        global count
        count=self.__beforetotal
        self.create_file(data=str(count))
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeBondling()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()
