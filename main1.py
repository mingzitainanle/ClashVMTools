import datetime
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED, as_completed

import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


current_date = datetime.datetime.now().strftime("%Y-%m-%d")

if not os.path.exists("./logs"):
    os.makedirs("./logs")
log = Logger(f'./logs/{current_date}.log', level='debug')

def action(second):
    print(f"打印second，并停顿:{second}")
    time.sleep(second)
    return second


suc_action_lists = [('🇭🇰 香港03', 57392.954256331315), ('🇯🇵 日本02', 51128.067510990535),
                    ('🇭🇰 香港02', 42472.7044885931),
                    ('🇸🇬 新加坡03', 41927.685622940815), ('🇹🇼 台湾节点', 20005.87509251914),
                    ('🇸🇬 新加坡01', 13633.41451863364),
                    ('🇨🇳 台湾02', 4024.931049454175), ('🇯🇵 日本05', 3525.2819188185827),
                    ('🇭🇰 香港08', 3292.5442860161093),
                    ('🇰🇷 韩国05', 3217.756408815656), ('🇭🇰 香港10', 3214.781201972057),
                    ('🇺🇲 美国节点', 3214.074878562047),
                    ('🇭🇰 香港07', 3212.2522861575403), ('🇸🇬 新加坡02', 3211.407076574435),
                    ('🇭🇰 香港节点', 3209.6381167119994),
                    ('🇭🇰 香港04', 3207.9518494338017), ('🇺🇸 美国03', 3206.6580254227574),
                    ('🇭🇰 香港09', 3202.413136212306),
                    ('🇭🇰 香港01', 3198.6636976089153), ('🇨🇳 台湾06', 3190.4709274944175),
                    ('🇺🇸 美国01', 3181.980279573361),
                    ('🇰🇷 韩国03', 3180.2042558195035), ('🇯🇵 日本06', 3173.859741377603),
                    ('🇭🇰 香港06', 3148.8339372248965),
                    ('🇭🇰 香港05', 3147.916555169472), ('🇯🇵 日本节点', 3107.5493736919884),
                    ('🇯🇵 日本04', 3103.9302748607197),
                    ('🇺🇸 美国02', 3091.86018667347), ('🇰🇷 韩国06', 3089.9496560992943),
                    ('🇸🇬 新加坡04', 3073.568402875107),
                    ('🇯🇵 日本03', 3047.1462715132293), ('🇸🇬 新加坡06', 3045.727241879742),
                    ('🇨🇳 台湾05', 3005.340727764018),
                    ('🇨🇳 台湾03', 3000.476514228724), ('🇨🇳 台湾01', 2999.5963930259654),
                    ('🇨🇳 台湾04', 2999.5963930259654),
                    ('🇸🇬 新加坡05', 2707.304208569531), ('🇯🇵 日本01', 1185.2377625752822),
                    ('🇰🇷 韩国02', 1121.3598075476052),
                    ('🇰🇷 韩国04', 1107.2707005382538), ('🇰🇷 韩国节点', 913.4034601432675), ('DIRECT', 812.810939644231),
                    ('🇺🇸 美国04', 781.6376567391073), ('🇺🇸 美国06', 781.3440642858772),
                    ('🇰🇷 韩国01', 757.0414327612624),
                    ('🇸🇬 新加坡节点', 717.5205854798722)]


def calculation_speed(source: float) -> str:
    if not source:
        return "0 KB/S"
    if source <= 1024:
        return f"{source:.2f} KB/S"
    if source > 1024:
        return f"{source / 1024:.2f} MB/S"


for i in suc_action_lists:
    log.logger.info(f"======================{[i[0], calculation_speed(i[1])]}")


