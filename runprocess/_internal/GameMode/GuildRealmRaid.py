from Module.GameControl import *
from Module.ThreadGame import *
from Module.Util import *
from Module.loadconfig import load_config
import time
import subprocess

_displayChat=0
_cAttackRealm=0
_idlecount=0
_scrollcount=0
_need1scrollup=False
SCROLL_DOWN=[(910, 520),(910, 265)]
CLICK_FINISH=(35, 510)
START_SOUL_COORDINATE = (1075, 565)

class GuildRealmRaid(threading.Thread):
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
        }

        gray_templates = {
            # DEFAULT
            "IMAGE_ROOM_BACK": config['DEFAULT']['IMAGE_ROOM_BACK'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],
            "IMAGE_FAILED_PATH": config['DEFAULT']['IMAGE_FAILED_PATH'],
            "IMAGE_FINISHED1_PATH": config['DEFAULT']['IMAGE_FINISHED1_PATH'],
            "IMAGE_FINISHED1S3_PATH": config['DEFAULT']['IMAGE_FINISHED1S3_PATH'],
            "IMAGE_FINISHED2_PATH": config['DEFAULT']['IMAGE_FINISHED2_PATH'],

            # Server-specific
            "IMAGE_REALM_RAID_PATH": config[self.__sv]['IMAGE_REALM_RAID_PATH'],
            "IMAGE_REALM_GUILD_PATH": config[self.__sv]['IMAGE_REALM_GUILD_PATH'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_REALM_ATK_PATH": config[self.__sv]['IMAGE_REALM_ATK_PATH'],

            # REALM
            "IMAGE_REALM_LOCK_PATH": config['REALM']['IMAGE_REALM_LOCK_PATH'],
            "IMAGE_REALM_GUILDPAGEEND_PATH": config['REALM']['IMAGE_REALM_GUILDPAGEEND_PATH'],
            "IMAGE_REALM_KO_PATH": config['REALM']['IMAGE_REALM_KO_PATH'],
            "IMAGE_REALM_CLOSE": config['REALM']['IMAGE_REALM_CLOSE'],
            "IMAGE_REALM_GUILDSCROLL_PATH": config['REALM']['IMAGE_REALM_GUILDSCROLL_PATH'],
            "IMAGE_REALM_SECTION2_PATH": config['REALM']['IMAGE_REALM_SECTION2_PATH'],
            "IMAGE_REALM_GRAIDCOUNT": config[self.__sv]['IMAGE_REALM_GRAIDCOUNT'],
            "IMAGE_REALM_GUILDPAGEEND_TOP_PATH": config['REALM']['IMAGE_REALM_GUILDPAGEEND_TOP_PATH'],
            "IMAGE_REALM_CANTATTK_PATH": config['REALM']['IMAGE_REALM_CANTATTK_PATH'],

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

    def gameModeGuildRealmRaid(self):
        global _isPaused, _displayChat, _cAttackRealm, _idlecount, _scrollcount, _need1scrollup
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                _idlecount+=1
                continue

            REALM_GRAIDCOUNT=(self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GRAIDCOUNT'], part=1, pos1=(_displayChat+224, 495), pos2=(_displayChat+285, 540), threshold=0.95))
            if REALM_GRAIDCOUNT != False:
                logging.debug("Round: 0/6 | Sleep for Wait 5s")
                time.sleep(5)
                _idlecount+=5
                continue
            
            detectAssistance = threading.Thread(target=self.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            #lock line up
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_LOCK_PATH'], part=1, pos1=(_displayChat+165, 530), pos2=(_displayChat+213, 570))
            if position != False:
                logging.info("Successfully lock lineup..")
                self.__gui.mouse_click_bg(position)
                continue
            
            #KO or Page End
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND_PATH'], part=1, pos1=(_displayChat+637, 118), pos2=(_displayChat+675, 582))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_KO_PATH'], part=1, pos1=(_displayChat+275, 316), pos2=(_displayChat+331, 368))
            if (position !=False and position2 !=False) or _scrollcount > 2:
                logging.info("Process Finish.. Exit!")
                total = str(self.__total)
                self.create_file(data=total)
                args = ['taskkill', '/F', '/PID', str(self.__pid)]
                subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW)
                sys.exit()
                
            #If Can't Attack Enemy 
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            if (_cAttackRealm >= 5) and (position != False):
                time.sleep(1)
                logging.info("Reopen Guild Realm Raid")
                _cAttackRealm = 0
                self.__gui.mouse_click_bg(position)
                self.__gui.mouse_click_bg(position)
                time.sleep(1)
                if position != False:
                    self.__gui.mouse_click_bg(position)
                    continue
            
            #Drag mouse down if enemy not found
            guildscroll=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDSCROLL_PATH'], part=1, pos1=(_displayChat+975, 105), pos2=(_displayChat+1045, 580))
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2_PATH'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580))
            if (guildscroll != False) and (position == False):
                logging.debug("Looking for enemy")
                page_end=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND_PATH'], part=1, pos1=(_displayChat+637, 118), pos2=(_displayChat+675, 582)) #รูปเขตที่ตีไปแล้ว
                if page_end:
                    logging.debug("scroll up")
                    _scrollcount += 1
                    logging.debug("_scrollcount:%s"%_scrollcount)
                    while True:
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                            detectAssistance = threading.Thread(target=self.detectAssistance())
                            detectAssistance.setDaemon(True)
                            detectAssistance.start
                        if _scrollcount > 2:
                            break
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2_PATH'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580)):
                            break 
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND_TOP_PATH'], part=1, pos1=(_displayChat+970, 85), pos2=(_displayChat+1100, 180) ,threshold=0.96):
                            break
                        self.__gui.mouse_drag_bg(SCROLL_DOWN[1],SCROLL_DOWN[0]) #up
                        time.sleep(1)
                          
                else:
                    logging.debug("scroll down")
                    if _need1scrollup == True:
                        self.__gui.mouse_drag_bg(SCROLL_DOWN[1],SCROLL_DOWN[0]) #scroll up 1 time for check on top 
                        _need1scrollup = False
                        continue
                    time.sleep(1)
                    _scrollcount += 1
                    logging.debug("_scrollcount:%s"%_scrollcount)
                    while True:
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                            detectAssistance = threading.Thread(target=self.detectAssistance())
                            detectAssistance.setDaemon(True)
                            detectAssistance.start
                        if _scrollcount > 2:
                            break
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2_PATH'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580)):
                            break 
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND_PATH']):
                            break 
                        time.sleep(1)
                        self.__gui.mouse_drag_bg(SCROLL_DOWN[0],SCROLL_DOWN[1]) #down

            if (position and guildscroll) != False:
                self.__gui.mouse_click_bg(position)
                _cAttackRealm+=1
                _idlecount=0
                _scrollcount=0
                _need1scrollup=True
                time.sleep(0.5)
                logging.info("Attack Realm!")
                atk=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK_PATH'], part=1, pos1=(_displayChat+525, 305), pos2=(_displayChat+947, 603))
                position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
                if atk != False and position2 != False:
                    logging.debug("Click Attack by atk image")
                    self.__gui.mouse_click_bg(atk)
                    time.sleep(1)
                    continue
                elif atk == False and position2 != False:
                    logging.debug("Click Attack by SECTION2 image")
                    self.__gui.mouse_click_bg((_displayChat+position[0]-24,position[1]+148))    
                    # self.__gui.mouse_click_bg((_displayChat+position[0]-24,position[1]+190))    
                    #If Can't Attack Enemy 
                    position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
                    position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANTATTK_PATH'], part=1, pos1=(_displayChat+250, 270), pos2=(_displayChat+890, 380))
                    if position2 != False:
                        time.sleep(1)
                        logging.info("Reopen Guild RealmRaid Page.")
                        self.__gui.mouse_click_bg(position)
                        self.__gui.mouse_click_bg(position)
                        time.sleep(1)
                        if position != False:
                            self.__gui.mouse_click_bg(position)
                            continue
                    else:
                        self.__gui.mouse_click_bg((35, 51))
                        continue 

            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                time.sleep(1)
                _cAttackRealm=0
                _idlecount=0
                continue
                
           #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
                logging.info("Battle End, Victory!")
                #time.sleep(5)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2_PATH'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))):
                        time.sleep(1)
                        _cAttackRealm=0
                        _idlecount=0
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH[0], CLICK_FINISH[1]))
                    time.sleep(0.05)
                break

            
            #Room Back
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_ROOM_BACK'], part=1, pos1=(_displayChat+17, 18), pos2=(_displayChat+58, 54))
            if position != False:
                logging.info("In Room Detected, Exit Room..")
                self.__gui.mouse_click_bg(position)
                continue
            
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_RAID_PATH'], part=1, pos1=(_displayChat+44, 547), pos2=(_displayChat+664, 632))
            if position != False:
                logging.info("Enter Realm Raid!")
                self.__gui.mouse_click_bg(position)
                time.sleep(2)
                continue

            #Click Guild Realm Page
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILD_PATH'], part=1, pos1=(_displayChat+1000, 194), pos2=(_displayChat+1132, 446))
            if position != False:
                logging.info("Open Guild RealmRaid Page.")
                self.__gui.mouse_click_bg(position)
                _need1scrollup = False
                continue

            else:
                _idlecount+=1
            time.sleep(1)

    
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
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeGuildRealmRaid()
            # self.test()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()