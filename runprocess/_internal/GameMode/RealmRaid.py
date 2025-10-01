from Module.GameControl import *
from Module.ThreadGame import *
from Module.loadconfig import *
from Module.Utils import GameUtils
import time
import subprocess
import threading
import logging
from Module.loadconfig import config

_localVariable=threading.local()
_displayChat=0
_cAttackRealm=0
_is3Realm=False
CLICK_FINISH2=(35, 510)
START_SOUL_COORDINATE = (1075, 565)

class RealmRaid(threading.Thread):
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
            "IMAGE_REALM_CANTATTK": config['REALM']['IMAGE_REALM_CANTATTK'],
            "IMAGE_REALM_JADE": config['REALM']['IMAGE_REALM_JADE'],

            # Server-specific (self.__sv)
            "IMAGE_REALM_CANCEL_BATTLE": config[self.__sv]['IMAGE_REALM_CANCEL_BATTLE'],
            "IMAGE_REALM_RAID": config[self.__sv]['IMAGE_REALM_RAID'],
            "IMAGE_REALM_ATK": config[self.__sv]['IMAGE_REALM_ATK'],
            "IMAGE_REALM_REFRESH": config[self.__sv]['IMAGE_REALM_REFRESH'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],
            "IMAGE_READY": config[self.__sv]['IMAGE_READY'],
            "IMAGE_REALM_COOLDOWN": config[self.__sv]['IMAGE_REALM_COOLDOWN'],

            # GB & CN (ใช้ชื่อ key เดิมได้เพราะ path ไม่ชนกัน)
            "IMAGE_REALM_EMPTY_TICKET": config[self.__sv]['IMAGE_REALM_EMPTY_TICKET'],

            # DEFAULT
            "IMAGE_BACK": config['DEFAULT']['IMAGE_BACK'],
            "IMAGE_BACK2": config['DEFAULT']['IMAGE_BACK2'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],
            "IMAGE_FAILED": config['DEFAULT']['IMAGE_FAILED'],
            "IMAGE_FINISHED1": config['DEFAULT']['IMAGE_FINISHED1'],
            "IMAGE_FINISHED1S3": config['DEFAULT']['IMAGE_FINISHED1S3'],
            "IMAGE_FINISHED2": config['DEFAULT']['IMAGE_FINISHED2'],

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

    def gameModeRealmRaid(self):
        global _cAttackRealm, _displayChat, _is3Realm
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            IMAGE_REALM_COOLDOWN = self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_COOLDOWN'], part=1, pos1=(_displayChat+840, 490), pos2=(_displayChat+1025, 570), threshold=0.95)
            if (INBATTLE != False and COOP_QUEST == False) or (IMAGE_REALM_COOLDOWN != False and (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAID'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAIDFROG'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)))):
                self.game_utils.reset_idle_count()
                time.sleep(1)
                continue
                
            detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start
            #If Found Daruma
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_FN3R'], part=1, pos1=(_displayChat+451, 413), pos2=(_displayChat+675, 545))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            if (position and position2) and (self.__bondlingmode != 'AllRaid'):
                logging.info('3 Realm Raid Reward')
                time.sleep(2)
                self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                time.sleep(2)
                _is3Realm = True

            #not enough ticket
            # if self.__gameMode == 6:
            position = (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET'], part=1, pos1=(1005, 10), pos2=(1105, 45), threshold=0.97) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_EMPTY_TICKET'], part=1, pos1=(1530, 10), pos2=(1630, 45), threshold=0.97))
            if  position or (_cAttackRealm >= 5):
                logging.info("Process Finish.. Exit!")
                self.game_utils.create_file(str(self.__total))
                subprocess.run(['taskkill','/F','/PID', str(self.__pid)],
                            creationflags=subprocess.CREATE_NO_WINDOW)
                return

            #Click icon realm
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_RAID'], part=1, pos1=(_displayChat+44, 547), pos2=(_displayChat+664, 632))
            if position != False:
                logging.info("Enter Realm Raid!")
                self.__gui.mouse_click_bg(position)
                time.sleep(3)
                continue
            
            #lock line up
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_LOCK'], part=1, pos1=(_displayChat+713, 512), pos2=(_displayChat+775, 556))
            if position != False:
                logging.info("Successfully lock lineup...")
                self.__gui.mouse_click_bg(position)
                continue
            
            if _is3Realm == False and (self.__bondlingmode != 'AllRaid'):
                position=(self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAID'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAIDFROG'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)))
                if position == False:
                    # logging.info('Not Found 3Realm raid icon')
                    # _is3Realm = False
                    pass
                else:
                    logging.debug('set 3Realm raid state = True')
                    _is3Realm = True

            #Click Realm
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTIONFROG'], part=1, pos1=(_displayChat+117, 115), pos2=(_displayChat+1020, 490), threshold=0.91)
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_SECTION2'], part=1, pos1=(_displayChat+117, 115), pos2=(_displayChat+1020, 490))
            positionatk=(position or position2)
            position3=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_ATK'], part=1, pos1=(_displayChat+242, 296), pos2=(_displayChat+993, 621))
            position4=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_REFRESH'], part=1, pos1=(_displayChat+840, 490), pos2=(_displayChat+1025, 570), threshold=0.96)
            position5=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            #This to Refresh#=========================================================================================================
            if ((_is3Realm != False) and position4 != False and (self.__bondlingmode != 'AllRaid')) or (
            (self.__bondlingmode == 'AllRaid') and (position4 != False) and (positionatk == False)):
                logging.info('Refresh Realm Raid Page!')
                self.__gui.mouse_click_bg(position4)
                time.sleep(1)
                #This to Click OK button
                if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+555, 430)) != False:
                    self.__gui.mouse_click_bg((position4[0]-253,position4[1]-145))
                    logging.debug('set 3Realm raid state = False')
                    _is3Realm = False
                    self.game_utils.reset_idle_count()
                    time.sleep(1)
            
            #This Click Enemy#=========================================================================================================
            if _is3Realm == False and position5 != False:
                time.sleep(1)
                if _is3Realm == False and position5 != False:
                    if positionatk != False and _is3Realm == False:
                        logging.info("Attack Realm!")
                        self.__gui.mouse_click_bg(positionatk)
                        time.sleep(2)
                        _cAttackRealm+=1
                        self.game_utils.reset_idle_count()
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
                    self.game_utils.reset_idle_count()
                    time.sleep(1)
            
            #=========================================get ready=================================================
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_READY'], part=1, pos1=(_displayChat+981, 477), pos2=(_displayChat+1103, 567))
            if position != False:
                # logging.info("Starting battle.... ")
                self.__gui.mouse_click_bg(position)
                time.sleep(2)
                continue

            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                logging.info("Battle End, Fail..")
                _cAttackRealm=0
                self.game_utils.reset_idle_count()
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_JADE'])) != False:
                        _cAttackRealm=0
                        self.game_utils.reset_idle_count()
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))

            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
                logging.info("Battle End, Victory!")
                #time.sleep(5)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.game_utils.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_JADE'])) != False:
                        _cAttackRealm=0
                        self.game_utils.reset_idle_count()
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))
                break

            else:
                time.sleep(1)
    
    def run(self):
        count=self.__beforetotal
        self.game_utils.create_file(data=str(count))
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeRealmRaid()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.game_utils.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()