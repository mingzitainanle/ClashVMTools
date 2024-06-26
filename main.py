import argparse
import datetime
import logging
import os
import sys
import time
from logging import handlers

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from func_timeout import func_set_timeout

from concurrent.futures import ThreadPoolExecutor

from clash import api, test
from configruation import get_config


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

speed_dict = {}
handoff = ""
suc_action_lists = []


# noinspection PyBroadException
def get_user_config():
    try:
        clash_config_path = os.path.join(os.path.expanduser('~'), ".config", "clash", "config.yaml")
        with open(clash_config_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except:
        return None


# noinspection HttpUrlsUsage
def init_config():
    parser = argparse.ArgumentParser(description='clash tools')
    parser.add_argument('--base_url', help='clash api 地址')
    parser.add_argument('--secret', help='clash api 认证')
    parser.add_argument('--proxy_url', help='clash 代理地址')
    parser.add_argument('--group_name', help='clash 代理分组名称')
    parser.add_argument('--timeout', help='节点测试超时时间')
    parser.add_argument('--max_size', help='节点测试下载文件大小')
    parser.add_argument('--scheduler_time', help='定时任务间隔时间')
    get_config().set_args(parser.parse_args())
    if get_config().base_url and get_config().secret and get_config().proxy_url:
        return
    get_config().set_args_of_env()
    if get_config().base_url and get_config().secret and get_config().proxy_url:
        return
    clash_config = get_user_config()
    if clash_config is not None:
        get_config().base_url = f"http://{clash_config['external-controller']}"
        get_config().secret = clash_config['secret']
        get_config().proxy_url = f"http://127.0.0.1:{clash_config['mixed-port']}"
    if get_config().group_name is None:
        get_config().group_name = "🚀 手动切换"


# noinspection PyBroadException,PyPackageRequirements
def run():
    proxies_names = api.get_proxies_names(get_config().group_name)
    if len(proxies_names) <= 0:
        log.logger.error(f"获取 [{get_config().group_name}] 下的节点信息失败，退出检查")
        return
    if get_config().proxy_url is None:
        get_config().proxy_url = api.get_proxy_url()
    log.logger.info("开始检查代理是否有效")

    # 通过submit提交执行的函数到线程池中
    log.logger.info(f"======================启动线程池")
    with ThreadPoolExecutor(max_workers=5) as pool:
        [pool.submit(thread_fun, i) for i in proxies_names]

    for i in sorted(speed_dict.items(), key=lambda x: x[1], reverse=True):
        log.logger.info(f"======================{[i[0], calculation_speed(i[1])]}")

    # 线程池关闭
    pool.shutdown()

    if not handoff:
        speed_tuple_list = sorted(speed_dict.items(), key=lambda x: x[1], reverse=True)
        if len(speed_tuple_list) <= 0:
            return
        proxies_name, max_value = speed_tuple_list[0]
        api.switch_proxy(get_config().group_name, proxies_name)
        log.logger.warning(
            f"未能找到符合要求的节点，已切换为速度最快的节点: [{proxies_name}]，速度: [{calculation_speed(max_value)}]")

        # ssrToolsApi.update_download_stats(proxies_name)


def calculation_speed(source: float) -> str:
    if not source:
        return "0 KB/S"
    if source <= 1024:
        return f"{source:.2f} KB/S"
    if source > 1024:
        return f"{source / 1024:.2f} MB/S"


def init_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(run, "interval", minutes=get_config().timeout, coalesce=True, max_instances=1)
    scheduler.start()
    log.logger.info(f"添加定时任务成功，每{get_config().scheduler_time}分钟检查一次")


def thread_fun(proxies_name):
    log.logger.info(f"线程池启动，节点名: [{proxies_name}]")

    @func_set_timeout(get_config().timeout * 3)
    def exec_test():
        return test.test_download()

    global handoff, suc_action_lists
    try:
        start_time = time.time()
        result = exec_test()
        end_time = time.time()
        execution_time = end_time - start_time
        speed_dict[proxies_name] = (get_config().max_size / 1024) / execution_time
        if result:
            result = test.test_google()
        handoff = False
    except:
        result = False
        handoff = False
        execution_time = sys.maxsize
    if not result or execution_time > get_config().timeout:
        api.switch_proxy(get_config().group_name, proxies_name)
        log.logger.warning(
            f"当前代理测试失败，测试时长：{execution_time}秒, 切换代理[{get_config().group_name} -> {proxies_name}]")
    else:
        handoff = True
        log.logger.info(
            f"当前代理代理测试成功，节点：{proxies_name},速度: [{calculation_speed(speed_dict[proxies_name])}]")
        va = [proxies_name, speed_dict[proxies_name]]
        suc_action_lists.append(va)



# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    init_config()
    init_scheduler()
    run()

