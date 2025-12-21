from Module.GameControl import *
from Module.ThreadGame import *
from Module.loadconfig import *
from Module.Utils import GameUtils
import time
import subprocess
import threading
import logging
from Module.loadconfig import config

_displayChat=0
_cAttackRealm=0
_scrollcount=0
_need1scrollup=False
SCROLL_DOWN=[(910, 520),(910, 265)]
CLICK_FINISH=(35, 510)
START_SOUL_COORDINATE = (1075, 565)

class GuildRealmRaid(threading.Thread):
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
            # DEFAULT
            "IMAGE_ROOM_BACK": config['DEFAULT']['IMAGE_ROOM_BACK'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],
            "IMAGE_FAILED": config['DEFAULT']['IMAGE_FAILED'],
            "IMAGE_FINISHED1": config['DEFAULT']['IMAGE_FINISHED1'],
            "IMAGE_FINISHED1S1": config['DEFAULT']['IMAGE_FINISHED1S1'],
            "IMAGE_FINISHED1S2": config['DEFAULT']['IMAGE_FINISHED1S2'],
            "IMAGE_FINISHED1S3": config['DEFAULT']['IMAGE_FINISHED1S3'],
            "IMAGE_FINISHED_CP": config['DEFAULT']['IMAGE_FINISHED_CP'],
            "IMAGE_FINISHED2": config['DEFAULT']['IMAGE_FINISHED2'],

            # Server-specific
            "IMAGE_REALM_RAID": config[self.__sv]['IMAGE_REALM_RAID'],
            "IMAGE_REALM_GUILD": config[self.__sv]['IMAGE_REALM_GUILD'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_REALM_ATK": config[self.__sv]['IMAGE_REALM_ATK'],

            # REALM
            "IMAGE_REALM_LOCK": config['REALM']['IMAGE_REALM_LOCK'],
            "IMAGE_REALM_GUILDPAGEEND": config['REALM']['IMAGE_REALM_GUILDPAGEEND'],
            "IMAGE_REALM_KO": config['REALM']['IMAGE_REALM_KO'],
            "IMAGE_REALM_CLOSE": config['REALM']['IMAGE_REALM_CLOSE'],
            "IMAGE_REALM_GUILDSCROLL": config['REALM']['IMAGE_REALM_GUILDSCROLL'],
            "IMAGE_REALM_SECTION2": config['REALM']['IMAGE_REALM_SECTION2'],
            "IMAGE_REALM_GRAIDCOUNT": config[self.__sv]['IMAGE_REALM_GRAIDCOUNT'],
            "IMAGE_REALM_GUILDPAGEEND_TOP": config['REALM']['IMAGE_REALM_GUILDPAGEEND_TOP'],
            "IMAGE_REALM_CANTATTK": config['REALM']['IMAGE_REALM_CANTATTK'],

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
        global _isPaused, _displayChat, _cAttackRealm, _scrollcount, _need1scrollup
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            if INBATTLE!= False and COOP_QUEST == False:
                time.sleep(1)
                continue

            REALM_GRAIDCOUNT=(self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GRAIDCOUNT'], part=1, pos1=(_displayChat+224, 495), pos2=(_displayChat+285, 540), threshold=0.95))
            if REALM_GRAIDCOUNT != False:
                logging.debug("Round: 0/6 | Sleep for Wait 5s")
                self.game_utils.reset_idle_count()
                time.sleep(5)
                continue
            
            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start

            #lock line up
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_LOCK'], part=1, pos1=(_displayChat+165, 530), pos2=(_displayChat+213, 570))
            if position != False:
                logging.info("Successfully lock lineup..")
                self.__gui.mouse_click_bg(position)
                self.game_utils.reset_idle_count()
                continue
            
            #KO or Page End
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND'], part=1, pos1=(_displayChat+637, 118), pos2=(_displayChat+675, 582))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_KO'], part=1, pos1=(_displayChat+275, 316), pos2=(_displayChat+331, 368))
            if (position and position2) or _scrollcount > 2:
                logging.info("Process Finish.. Exit!")
                self.game_utils.create_file(str(self.__total))
                subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                            creationflags=subprocess.CREATE_NO_WINDOW)
                return
                
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
            guildscroll=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDSCROLL'], part=1, pos1=(_displayChat+975, 105), pos2=(_displayChat+1045, 580))
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580))
            if (guildscroll != False) and (position == False):
                logging.info("Looking for enemy")
                page_end=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND'], part=1, pos1=(_displayChat+637, 118), pos2=(_displayChat+675, 582)) #รูปเขตที่ตีไปแล้ว
                if page_end:
                    logging.debug("scroll up")
                    _scrollcount += 1
                    logging.debug("_scrollcount:%s"%_scrollcount)
                    while True:
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                            detectAssistance.setDaemon(True)
                            detectAssistance.start
                        if _scrollcount > 2:
                            break
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580)):
                            break 
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND_TOP'], part=1, pos1=(_displayChat+970, 85), pos2=(_displayChat+1100, 180) ,threshold=0.96):
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
                            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                            detectAssistance.setDaemon(True)
                            detectAssistance.start
                        if _scrollcount > 2:
                            break
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580)):
                            break 
                        if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILDPAGEEND']):
                            break 
                        time.sleep(1)
                        self.__gui.mouse_drag_bg(SCROLL_DOWN[0],SCROLL_DOWN[1]) #down

            if (position and guildscroll) != False:
                self.__gui.mouse_click_bg(position)
                _cAttackRealm+=1
                _scrollcount=0
                _need1scrollup=True
                time.sleep(1)
                logging.info("Attack Realm!")
                atk=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK'], part=1, pos1=(_displayChat+525, 305), pos2=(_displayChat+947, 603))
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
                    position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANTATTK'], part=1, pos1=(_displayChat+250, 270), pos2=(_displayChat+890, 380))
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
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                logging.info("Battle End, Fail..")
                self.__gui.mouse_click_bg(position)
                time.sleep(1)
                _cAttackRealm=0
                self.game_utils.reset_idle_count()
                continue
                
           #check finish
            # if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (
            #     self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
            #     logging.info("Battle End, Victory!")
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1S2'], part=1, pos1=(_displayChat+30, 30), pos2=(_displayChat+95, 95))) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED_CP"], part=1, pos1=(_displayChat+360, 80), pos2=(_displayChat+500, 160)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S1"], part=1, pos1=(_displayChat+326, 119), pos2=(_displayChat+434, 215)) != False) or (
                self.__gui.find_game_img(self.__gui.templates["IMAGE_FINISHED1S3"], part=1, pos1=(_displayChat+50, 550), pos2=(_displayChat+450, 610)) != False) or (
                self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
                logging.info("Battle End, Victory!")
                #time.sleep(5)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2'], part=1, pos1=(_displayChat+540, 115), pos2=(_displayChat+970, 580)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))):
                        time.sleep(1)
                        _cAttackRealm=0
                        self.game_utils.reset_idle_count()
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
            
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_RAID'], part=1, pos1=(_displayChat+44, 547), pos2=(_displayChat+664, 632))
            if position != False:
                logging.info("Enter Realm Raid!")
                self.__gui.mouse_click_bg(position)
                time.sleep(2)
                continue

            #Click Guild Realm Page
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_GUILD'], part=1, pos1=(_displayChat+1000, 194), pos2=(_displayChat+1132, 446))
            if position != False:
                logging.info("Open Guild RealmRaid Page.")
                self.__gui.mouse_click_bg(position)
                _need1scrollup = False
                continue

    
    def run(self):
        count=self.__beforetotal
        self.game_utils.create_file(data=str(count))
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeGuildRealmRaid()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.game_utils.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()