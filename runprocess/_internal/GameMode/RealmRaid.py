from Module.GameControl import *
from Module.ThreadGame import *
from Module.Util import *
from Module.loadconfig import *
import time
import subprocess

_localVariable=threading.local()
_displayChat=0
_cAttackRealm=0
_is3Realm=False
_idlecount=0
CLICK_FINISH2=(35, 510)
START_SOUL_COORDINATE = (1075, 565)

class RealmRaid(threading.Thread):
    def __init__(self,Server, windowName, beforetotal, total, pid, bondlingmode, pactsettings, crystal_use, tomb, snowball, azure, kuro, markboss):
        # global self.__sv
        threading.Thread.__init__(self)
        self.__sv=Server
        self.__hwnd=windowName
        self.__beforetotal=beforetotal
        self.__total=total
        self.__pid=pid
        self.__mode=bondlingmode
        self.__gui=GameControl(self.__hwnd,0)

        color_templates = {
        }

        gray_templates = {
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
            "IMAGE_REALM_CANTATTK_PATH": config['REALM']['IMAGE_REALM_CANTATTK_PATH'],
            "IMAGE_REALM_JADE_PATH": config['REALM']['IMAGE_REALM_JADE_PATH'],

            # Server-specific (self.__sv)
            "IMAGE_REALM_CANCEL_BATTLE": config[self.__sv]['IMAGE_REALM_CANCEL_BATTLE'],
            "IMAGE_REALM_RAID_PATH": config[self.__sv]['IMAGE_REALM_RAID_PATH'],
            "IMAGE_REALM_ATK_PATH": config[self.__sv]['IMAGE_REALM_ATK_PATH'],
            "IMAGE_REALM_REFRESH_PATH": config[self.__sv]['IMAGE_REALM_REFRESH_PATH'],
            "IMAGE_COOP2_SEAL": config[self.__sv]['IMAGE_COOP2_SEAL'],
            "IMAGE_CHATDETECT": config[self.__sv]['IMAGE_CHATDETECT'],
            "IMAGE_CHATSTICKER": config[self.__sv]['IMAGE_CHATSTICKER'],
            "IMAGE_REALM_CANCEL": config[self.__sv]['IMAGE_REALM_CANCEL'],
            "IMAGE_READY_PATH": config[self.__sv]['IMAGE_READY_PATH'],
            "IMAGE_REALM_COOLDOWN": config[self.__sv]['IMAGE_REALM_COOLDOWN'],

            # GB & CN (ใช้ชื่อ key เดิมได้เพราะ path ไม่ชนกัน)
            "IMAGE_REALM_EMPTY_TICKET": config[self.__sv]['IMAGE_REALM_EMPTY_TICKET'],

            # DEFAULT
            "IMAGE_BACK": config['DEFAULT']['IMAGE_BACK'],
            "IMAGE_BACK2": config['DEFAULT']['IMAGE_BACK2'],
            "IMAGE_INBATTLE": config[self.__sv]['IMAGE_INBATTLE'],
            "IMAGE_FAILED_PATH": config['DEFAULT']['IMAGE_FAILED_PATH'],
            "IMAGE_FINISHED1_PATH": config['DEFAULT']['IMAGE_FINISHED1_PATH'],
            "IMAGE_FINISHED1S3_PATH": config['DEFAULT']['IMAGE_FINISHED1S3_PATH'],
            "IMAGE_FINISHED2_PATH": config['DEFAULT']['IMAGE_FINISHED2_PATH'],

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
        global _cAttackRealm, _displayChat, _is3Realm, _idlecount
        while True:
            INBATTLE=self.__gui.find_game_img(self.__gui.templates['IMAGE_INBATTLE'],part=1, pos1=(_displayChat+196, 600), pos2=(_displayChat+277, 640))
            COOP_QUEST = self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175))
            IMAGE_REALM_COOLDOWN = self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_COOLDOWN'], part=1, pos1=(_displayChat+840, 490), pos2=(_displayChat+1025, 570), threshold=0.95)
            if (INBATTLE != False and COOP_QUEST == False) or (IMAGE_REALM_COOLDOWN != False and (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAID_PATH'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_3RAIDFROG_PATH'], part=1, pos1=(_displayChat+325, 490), pos2=(_displayChat+451, 571)))):
                time.sleep(1)
                _idlecount+=1
                continue
                
            detectAssistance = threading.Thread(target=self.detectAssistance())
            detectAssistance.setDaemon(True)
            detectAssistance.start
            #If Found Daruma
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_FN3R_PATH'], part=1, pos1=(_displayChat+451, 413), pos2=(_displayChat+675, 545))
            position2=self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135))
            if (position and position2) and (self.__mode != 'AllRaid'):
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
                # pyautogui.alert(text='REALM RAID DONE', title='FINISH', button='OK')
                total = str(self.__total)
                self.create_file(data=total)
                args = ['taskkill', '/F', '/PID', str(self.__pid)]
                subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW)
                sys.exit()

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
            
            if _is3Realm == False and (self.__mode != 'AllRaid'):
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
            if ((_is3Realm != False) and position4 != False and (self.__mode != 'AllRaid')) or (
            (self.__mode == 'AllRaid') and (position4 != False) and (positionatk == False)):
                logging.debug('This should refresh')
                self.__gui.mouse_click_bg(position4)
                time.sleep(1)
                #This to Click OK button
                if self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CANCEL'], part=1, pos1=(_displayChat+363, 340), pos2=(_displayChat+555, 430)) != False:
                    self.__gui.mouse_click_bg((position4[0]-253,position4[1]-145))
                    logging.debug('set 3Realm raid state = False')
                    _is3Realm = False
                    _idlecount=0
                    time.sleep(1)
            
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

            #Fail
            position=self.__gui.find_game_img(self.__gui.templates['IMAGE_FAILED_PATH'], part=1, pos1=(_displayChat+368, 153), pos2=(_displayChat+423, 204))
            if position != False:
                logging.info("Battle End, Fail..")
                _cAttackRealm=0
                _idlecount=0
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_JADE_PATH'])) != False:
                        _cAttackRealm=0
                        _idlecount=0
                        break
                    self.__gui.mouse_click_bg((_displayChat+CLICK_FINISH2[0], CLICK_FINISH2[1]))

            #check finish
            if (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED1_PATH'], part=1, pos1=(_displayChat+395, 137), pos2=(_displayChat+459, 192))) or (self.__gui.find_game_img(self.__gui.templates['IMAGE_FINISHED2_PATH'], part=1, pos1=(_displayChat+513, 444), pos2=(_displayChat+559, 477))):
                logging.info("Battle End, Victory!")
                #time.sleep(5)
                while True:
                    if self.__gui.find_game_img(self.__gui.templates['IMAGE_COOP2_SEAL'], part=1, pos1=(_displayChat+455, 135), pos2=(_displayChat+495, 175)) or (_displayChat == 0 and self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATDETECT'])) or self.__gui.find_game_img(self.__gui.templates['IMAGE_CHATSTICKER'], part=1, pos1=(_displayChat+560, 300), pos2=(_displayChat+607, 397)):
                        detectAssistance = threading.Thread(target=self.detectAssistance())
                        detectAssistance.setDaemon(True)
                        detectAssistance.start

                    if (self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_CLOSE'], part=1, pos1=(_displayChat+1054, 101), pos2=(_displayChat+1087, 135)) or self.__gui.find_game_img(self.__gui.templates['IMAGE_REALM_JADE_PATH'])) != False:
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
        while self.__total-count>0:
            seconds=0
            while seconds:
                time.sleep(1)
                seconds-=1
            logging.info("\n\n==================Starting a new round==================")
            self.gameModeRealmRaid()
            count+=1
            message="completed %s, remaining %s round"%(str(count),str(self.__total-count))
            self.create_file(data=str(count))
            logging.info(message)


if __name__ == '__main__':
    load_config()