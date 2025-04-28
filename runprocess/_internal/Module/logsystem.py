import logging, time, os

class MyLog():
    plogger = logging.getLogger('Passenger')
    dlogger = logging.getLogger('Driver')
    mlogger = logging.getLogger()

    @staticmethod
    def init(loglv='DEBUG'):
        setloglv = None
        
        if loglv == 'DEBUG':
            setloglv = logging.DEBUG
        else:
            setloglv = logging.INFO
            
        if loglv != 'OFF':
            if not os.path.exists('logs'):
                os.makedirs('logs')

            log_filename = f'./logs/log.txt'
            if not os.path.exists(log_filename):
                with open(log_filename, "w") as file:
                    file.close

            try:
                os.rename(log_filename, log_filename)
            except IOError:
                instance_num = 0
                log_filename = f'./logs/log_inst{instance_num}.txt'
                try:
                    os.rename(log_filename, log_filename)
                except IOError:
                    instance_num += 1
                    log_filename = f'./logs/log_inst{instance_num}.txt'
            
            logging.basicConfig(level=setloglv,
                                format='%(asctime)s %(levelname)-3s [%(module)-0s | %(lineno)d]: %(message)s',
                                datefmt='[%H:%M:%S]',
                                filename=log_filename,
                                filemode='w')

            #################################################################################################
            console = logging.StreamHandler()
            console.setLevel(setloglv)
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)-3s [%(module)-0s | %(lineno)d]: %(message)s',
                datefmt='[%H:%M:%S]',)
            console.setFormatter(formatter)
            MyLog.mlogger.addHandler(console)
            logger = logging.getLogger('MyLogger')
            logger.addHandler(console)
            #################################################################################################
