from Module.GameControl import *
from Module.ThreadGame import *
from Module.Util import *
from Module.loadconfig import *
import time
import pyautogui, subprocess

_localVariable=threading.local()
_displayChat=0
_isLeader=False
_cAutoRotation=False
_isboss=False
cantattk=0
waittime=0
_idlecount=0

class Explore(threading.Thread):
    def __init__(self,Server, windowName, beforetotal, total, pid, bondlingmode, pactsettings, crystal_use, tomb, snowball, azure, kuro, markboss):
        # global self.__sv
        threading.Thread.__init__(self)
        self.__sv=Server
        self.__hwnd=windowName
        self.__beforetotal=beforetotal
        self.__total=total
        self.__pid=pid
        self.__gui=GameControl(self.__hwnd,0)

        color_templates = {
            "IMAGE_STORY_LEAD_PATH": config[self.__sv]['IMAGE_STORY_LEAD_PATH'],
        }

        gray_templates = {
            # EXPLORE
            "IMAGE_STORY_ACCEPT_PATH": config['EXPLORE']['IMAGE_STORY_ACCEPT_PATH'],
            "IMAGE_STORY_BOX_PATH": config['EXPLORE']['IMAGE_STORY_BOX_PATH'],
            "IMAGE_STORY_FIGHT_PATH": config['EXPLORE']['IMAGE_STORY_FIGHT_PATH'],
            "IMAGE_STORY_FIGHT_BOSS_PATH": config['EXPLORE']['IMAGE_STORY_FIGHT_BOSS_PATH'],
            "IMAGE_STORY_CHERRY_CAKE_PATH": config['EXPLORE']['IMAGE_STORY_CHERRY_CAKE_PATH'],
            "IMAGE_STORY_LIST_CHAPTER_PATH": config['EXPLORE']['IMAGE_STORY_LIST_CHAPTER_PATH'],
            "IMAGE_STORY_GET_REWARD_PATH": config['EXPLORE']['IMAGE_STORY_GET_REWARD_PATH'],

            # SOUL
            "IMAGE_SOUL_INVITE_PATH": config['SOUL']['IMAGE_SOUL_INVITE_PATH'],
            "IMAGE_SOUL_ROOM_DETECT_PATH": config['SOUL']['IMAGE_SOUL_ROOM_DETECT_PATH'],

            # DEFAULT
            "IMAGE_FINISHED2_PATH": config['DEFAULT']['IMAGE_FINISHED2_PATH'],
            "IMAGE_FINISHED1_PATH": config['DEFAULT']['IMAGE_FINISHED1_PATH'],
            "IMAGE_FINISHED1S2_PATH": config['DEFAULT']['IMAGE_FINISHED1S2_PATH'],
            "IMAGE_FAILED_PATH": config['DEFAULT']['IMAGE_FAILED_PATH'],
            "IMAGE_EMPTY_SUSHI": config['DEFAULT']['IMAGE_EMPTY_SUSHI'],
            "IMAGE_EMPTY_SUSHI_CLOSE": config['DEFAULT']['IMAGE_EMPTY_SUSHI_CLOSE'],
            "IMAGE_BUFF": config['DEFAULT']['IMAGE_BUFF'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],

            # self.__sv-specific (server-dependent)
            "IMAGE_SOUL_INVITE_DIALOG_PATH": config[self.__sv]['IMAGE_SOUL_INVITE_DIALOG_PATH'],
            "IMAGE_SOUL_START_PATH": config[self.__sv]['IMAGE_SOUL_START_PATH'],
            "IMAGE_STORY_AUTOFOOD_PATH": config[self.__sv]['IMAGE_STORY_AUTOFOOD_PATH'],
            "IMAGE_READY_PATH": config[self.__sv]['IMAGE_READY_PATH'],
            "IMAGE_SOULMAX": config[self.__sv]['IMAGE_SOULMAX'],
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


    def gameModeExplore(self):
        global _isLeader, _cAutoRotation, cantattk, waittime, _idlecount, _isboss
        CLICK_SOULMAX=(568, 387)
        CLICK_FINISH2=(35, 510)
        SLIDE_STORY_COORDINATE=[(_displayChat+200,200),(_displayChat+1000,200)]
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

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_ACCEPT_PATH'],part=1, pos1=(_displayChat+82, 187), pos2=(_displayChat+171, 263))
            if position != False:
                logging.info("Accept Invite.")
                self.__gui.mouse_click_bg(position)  
                _idlecount=0
                time.sleep(1)
                continue

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_BOX_PATH'],part=1, pos1=(_displayChat+8, 119), pos2=(_displayChat+896, 501))
            if position != False:
                logging.info("Box Found. (Func.2)")
                self.__gui.mouse_click_bg(position)
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477)) != False:
                self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
            
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_PATH'], part=1, pos1=(528, 185), pos2=(631, 270)) != False:
                waittime+=1
                if waittime>=12:
                    self.__gui.mouse_click_bg((_displayChat+960, 225))
                    time.sleep(2)
                    self.__gui.mouse_click_bg((_displayChat+444, 514))
                    waittime=0
            
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_DIALOG_PATH'], part=1, pos1=(381, 242), pos2=(754, 323))
            if position != False:
                logging.info("Invited..")
                time.sleep(1)
                self.__gui.mouse_click_bg((_displayChat+position[0]+170,position[1]+100))
            
            if cantattk >= 12 or (self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False and self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI_CLOSE'], part=1, pos1=(_displayChat+792, 143), pos2=(_displayChat+875, 200)) == False):
                logging.info("Unable to process, Exit!")
                total = str(self.__total)
                self.create_file(data=total)
                args = ['taskkill', '/F', '/PID', str(self.__pid)]
                subprocess.Popen(args)
                sys.exit()
                    
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_START_PATH'], part=1, pos1=(_displayChat+951, 454), pos2=(_displayChat+1136, 640))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_INVITE_PATH'], part=1, pos1=(903, 185), pos2=(1034, 270))
            if position != False and position2 == False:
                logging.info("Start... ")
                self.__gui.mouse_click_bg(position)
                waittime=0
                _idlecount=0
                time.sleep(1)

            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_AUTOFOOD_PATH'],part=1, pos1=(_displayChat+90, 575), pos2=(_displayChat+265, 625))
            if position != False:
                logging.info("Click Auto Rotation")
                self.__gui.mouse_click_bg((_displayChat+117, 599))
                _cAutoRotation+=1
                if _cAutoRotation >= 5:
                    logging.info("Exit!")
                    pyautogui.alert(text='auto rotation food runs out, stop working..', title='Exit!', button='OK')
                    args = ['taskkill', '/F', '/PID', str(self.__pid)]
                    subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW)
                    sys.exit()
                time.sleep(1)
                continue

            #-=======================================================================================================
            if _isLeader == False:
                position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LEAD_PATH'], part=1, pos1=(75, 245), pos2=(170, 300), gray=0, threshold=0.90)
                if position != False:
                    logging.info("Leader Detected in display..")
                    _isLeader=True
                else:
                    _isLeader=False
            
                #===============================================slide windows if not found monster
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_PATH'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49))
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_BOSS_PATH'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            if _isLeader != False and (position == False or position3 == False) and position2 != False:
                time.sleep(1)
                if position == False and position2 != False and position3 == False:
                    self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[1],SLIDE_STORY_COORDINATE[0])
                    _localVariable.detectCount -= 1
                    time.sleep(1)
                    if _localVariable.detectCount < 1:
                        # self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[1],SLIDE_STORY_COORDINATE[0])
                        self.__gui.mouse_drag_bg(SLIDE_STORY_COORDINATE[0],SLIDE_STORY_COORDINATE[1])
                        _localVariable.detectCount=30
                        time.sleep(1)
            
            # position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_BOSS_PATH'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            if (_isLeader and position3) != False:
                logging.info("BOSS was detected: ")
                self.__gui.mouse_click_bg(position3)
                _isboss=True
                cantattk+=1
                _idlecount=0
                time.sleep(1)
                continue

            # position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_FIGHT_PATH'],part=1, pos1=(_displayChat+1, 200), pos2=(_displayChat+1136, 500))
            if (_isLeader and position) != False:
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
                _idlecount=0
                time.sleep(2)
                continue

            #=========================================Finish=================================================
            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 20), pos2=(_displayChat+423, 204))
            if position != False:
                cantattk=0
                _idlecount=0
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                continue

            # position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))
            # if position != False:
            #     cantattk=0
            #     _idlecount=0
            #     self.__gui.mouse_click_bg(position)
            #     continue

            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192)) or 
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2_PATH'], part=1, pos1=(_displayChat+25, 26), pos2=(_displayChat+120, 605)) != False) and (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER_PATH'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180)) or 
                self.__gui.find_game_img(self.__gui.templates['IMAGE_SOUL_ROOM_DETECT_PATH'], part=1, pos1=(_displayChat+20, 455), pos2=(_displayChat+81, 535)) == False):
                logging.info("Battle End, Victory!")
                cantattk=0
                _idlecount=0
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start
                    if (_isboss != True) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False or 
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_ACCEPT_PATH'],part=1, pos1=(_displayChat+82, 187), pos2=(_displayChat+171, 263)) != False or 
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_LIST_CHAPTER_PATH'],part=1, pos1=(_displayChat+955, 79), pos2=(_displayChat+1080, 180)) != False or 
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_BUFF']) != False or 
                        self.__gui.find_game_img(self.__gui.templates['IMAGE_EMPTY_SUSHI'], part=1, pos1=(_displayChat+486, 390), pos2=(_displayChat+650, 450)) != False):
                        time.sleep(1)
                        break
                    if (_isboss) and (self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_CHERRY_CAKE_PATH'],part=1, pos1=(_displayChat+584, 5), pos2=(_displayChat+649, 49)) != False):
                        _isboss=False
                        continue
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                        logging.info("Soul Max")
                        self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                        time.sleep(1)
                        continue
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                    time.sleep(0.01)
                break

            #==========================================Reward settlement=============================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_STORY_GET_REWARD_PATH'],part=1, pos1=(_displayChat+190, 310), pos2=(_displayChat+921, 561))
            if position != False:
                logging.info("Get treasure.... ")
                self.__gui.send_esc_down()
                time.sleep(2)
                _idlecount=0
                self.__gui.mouse_click_bg((_displayChat+655, 383))

            #soulmax
            if self.__gui.find_game_img(self.__gui.templates['IMAGE_SOULMAX'], part=1, pos1=(_displayChat+320, 213), pos2=(_displayChat+811, 431)) != False:
                logging.info("Soul Max")
                self.__gui.mouse_click_bg((_displayChat+CLICK_SOULMAX[0], CLICK_SOULMAX[1]))
                time.sleep(1)
                continue

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
            self.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()
