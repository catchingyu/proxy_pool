# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyRefreshSchedule.py  
   Description :  代理定时刷新
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4: 代理定时刷新
                   2017/03/06: 使用LogHandler添加日志
                   2017/04/26: raw_proxy_queue验证通过但useful_proxy_queue中已经存在的代理不在放入
-------------------------------------------------
"""

import sys
import time
import logging
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

__author__ = 'JHao'

logging.basicConfig()


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('refresh_schedule')

    def validProxy(self):
        """
        验证raw_proxy_queue中的代理, 将可用的代理放入useful_proxy_queue
        :return:
        """
        print "validProxy"
        self.db.changeTable(self.raw_proxy_queue)
        raw_proxy = self.db.pop()
        self.log.info('%s start validProxy_a' % time.ctime())
        exist_proxy = self.db.getAll()
        while raw_proxy:
            if validUsefulProxy(raw_proxy) and (raw_proxy not in exist_proxy):
                self.db.changeTable(self.useful_proxy_queue)
                self.db.put(raw_proxy)
                self.log.info('validProxy_a: %s validation pass' % raw_proxy)
            else:
                self.log.debug('validProxy_a: %s validation fail' % raw_proxy)
            self.db.changeTable(self.raw_proxy_queue)
            raw_proxy = self.db.pop()
        self.log.info('%s validProxy_a complete' % time.ctime())


def refreshPool():
    pp = ProxyRefreshSchedule()
    pp.validProxy()


def main(process_num=30):
    p = ProxyRefreshSchedule()

    # 获取新代理
    p.refresh()

    # 检验新代理
    pl = []
    for num in range(process_num):
        proc = Thread(target=refreshPool, args=())
        pl.append(proc)

    for num in range(process_num):
        pl[num].start()

    for num in range(process_num):
        pl[num].join()


def run():
    # main()
    print "Sched Begin"
    sched = BlockingScheduler()
#    sched.add_job(main, 'interval', minutes=10)
    sched.add_job(main, 'interval', seconds=60)
    sched.start()


if __name__ == '__main__':
    run()
