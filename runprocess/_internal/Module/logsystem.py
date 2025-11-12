import logging
import os
import sys
import time


class MyLog:
    """Utility logger with file‑rotation and concise console output."""
    plogger = logging.getLogger('Passenger')
    dlogger = logging.getLogger('Driver')
    mlogger = logging.getLogger()          # root

    @staticmethod
    def init(loglv: str = 'DEBUG'):
        # ---- early exit ----
        if loglv.upper() == 'OFF':
            return

        setloglv = logging.DEBUG if loglv.upper() == 'DEBUG' else logging.INFO

        # ---- log directory ----
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        # ---- keep at most 10 files ----
        # log_files = sorted(
        #     (f for f in os.listdir(log_dir) if f.startswith('log_') and f.endswith('.txt')),
        #     key=lambda f: os.path.getctime(os.path.join(log_dir, f))
        # )
        # if len(log_files) >= 10:
        #     os.remove(os.path.join(log_dir, log_files[0]))
        try:
            log_files = sorted(
                (f for f in os.listdir(log_dir) if f.startswith('log_') and f.endswith('.txt')),
                key=lambda f: os.path.getctime(os.path.join(log_dir, f))
            )
            
            if len(log_files) >= 10:
                file_to_remove = os.path.join(log_dir, log_files[0])
                
                #
                # !!! นี่คือส่วนที่แก้ไข !!!
                #
                try:
                    # พยายามลบไฟล์ที่เก่าที่สุด
                    os.remove(file_to_remove)
                    
                except (PermissionError, OSError) as e:
                    # ถ้าลบไม่ได้ (เพราะไฟล์ถูกใช้งานอยู่)
                    # ให้ print แจ้งเตือนไปยัง stderr แล้วทำงานต่อ
                    # (การลบไฟล์เก่าไม่สำเร็จ ไม่ควรทำให้โปรแกรมหลักหยุดทำงาน)
                    print(f"MyLog Init Warning: Failed to remove old log file '{log_files[0]}'. File may be in use ({e}).", file=sys.stderr)
                    
        except Exception as e:
            # ดักจับ Error อื่นๆ ที่อาจเกิดจากการ list/sort ไฟล์ (เช่น ไม่มีสิทธิ์อ่านโฟลเดอร์)
            print(f"MyLog Init Warning: Failed to process old log files directory. ({e})", file=sys.stderr)

        # ---- choose filename: log_YYYYMMDD_HHmmss[_instX].txt ----
        stamp = time.strftime('%Y%m%d_%H%M%S')
        index = 0
        while True:
            suffix = "" if index == 0 else f"_inst{index}"
            log_filename = os.path.join(log_dir, f"log_{stamp}{suffix}.txt")
            try:
                with open(log_filename, 'x'):
                    pass
                break
            except FileExistsError:
                index += 1

        # ---- formatters ----
        file_fmt = logging.Formatter(
            '%(asctime)s %(levelname)-3s [%(module)s | %(lineno)d]: %(message)s',
            datefmt='[%H:%M:%S]'
        )

        class AbbrevFormatter(logging.Formatter):
            def format(self, record):
                abbrev = ''.join(ch for ch in record.module if ch.isupper())
                record.abbrev_module = abbrev or record.module[:2].upper()
                return super().format(record)

        console_fmt = AbbrevFormatter(
            # '%(asctime)s %(levelname)-3s [%(abbrev_module)s]: %(message)s',
            '%(asctime)s %(levelname)-3s : %(message)s',
            datefmt='[%H:%M:%S]'
        )

        # ---- root logger ----
        root = MyLog.mlogger
        root.setLevel(setloglv)
        root.handlers.clear()  # fresh start every init

        # file handler
        fh = logging.FileHandler(log_filename, mode='w')
        fh.setLevel(setloglv)
        fh.setFormatter(file_fmt)
        root.addHandler(fh)

        # stdout handler (DEBUG/INFO)
        out_hdl = logging.StreamHandler(sys.stdout)
        out_hdl.setLevel(setloglv)
        out_hdl.addFilter(lambda r: r.levelno < logging.WARNING)
        out_hdl.setFormatter(console_fmt)
        root.addHandler(out_hdl)

        # stderr handler (WARNING+)
        err_hdl = logging.StreamHandler(sys.stderr)
        err_hdl.setLevel(logging.WARNING)
        err_hdl.setFormatter(console_fmt)
        root.addHandler(err_hdl)

        root.propagate = False
