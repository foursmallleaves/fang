# coding:utf-8
import os
import sys
import json
import time
import datetime
import aiohttp
import asyncio
from db import DB

result = ""
old_result = {}

SOCKET_SERVICE_IP = ""
SOCKET_SERVICE_PORT = 8899
ADDRESS = (SOCKET_SERVICE_IP, SOCKET_SERVICE_PORT)


class Crawler(object):
    """ crawler """
    db = None
    TIMEOUT = 0.4
    TIMEOUT2 = 1
    MAX_LENGTH = 10000
    COMMONKEY = ""
    Subscribekey = ""
    GO_EASY_URL = "https://rest-hangzhou.goeasy.io/publish"

    AREA = ("瓦房店", "普兰店", "庄河", "长海县" "新城区", "老城区", "南城区", "中介勿扰")  #
    BASE_URL = "https://miniapp.58.com/sale/property/list?cid=613&from=58_ershoufang&app=a-wb&platform=windows&b=microsoft&s=win10&t=1591152453&cv=5.0&wcv=5.0&wv=7.0.9&sv=2.10.4&batteryLevel=0&muid=dec533856bf7ec8cf898e5f237dd9c49&weapp_version=1.0.0&user_id=&oid=oIArb4rMh6BXGZ7QidZbxvmttws4&udid=oIArb4rMh6BXGZ7QidZbxvmttws4&page={}&page_size=25&open_id=&union_id=&token=&source_id=2&entry=1003&city_id=147"
    # BASE_URL = "https://miniapp.58.com/sale/property/list?cid=613&from=58_ershoufang&app=a-wb&platform=windows&b=microsoft&s=win10&t=1596727658&cv=5.0&wcv=5.0&wv=7.0.9&sv=2.11.0&batteryLevel=0&muid=f90c23451e2fddd62c851ce997f78ec7&weapp_version=1.0.0&user_id=&oid=oIArb4rMh6BXGZ7QidZbxvmttws4&udid=oIArb4rMh6BXGZ7QidZbxvmttws4&page=2&page_size=25&open_id=&union_id=&token=&source_id=2&entry=1003&city_id=147"
    HEADER_GET_LIST_INFO = {
        "Host": "miniapp.58.com",
        "Connection": "keep-alive",
        "Cookie": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
        "X-Forwarded-For": "112.64.131.100",
        "X_AJK_APP": "a-weapp",
        "ak": "931d0f0a7f7bc73c7cee04b87a1f3cb83d175517",
        "content-type": "application/x-www-form-urlencoded",
        "ft": "ajk-weapp",
        "sig": "5a0213f974de4bb7495e8dc9fb0170eb",
        "Referer": "https://servicewechat.com/wxe5b752fbe3874df1/91/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br",
    }
    count = 0
    log_dir = "/mnt/"

    def __init__(self):
        self.db = DB()
        self.db.init_cache()
        self.db.cache.getset("PHONE", "0")

    def except_info(self, e, params=None):
        """ 异常信息打印 """
        msg = ""
        t = datetime.datetime.now()
        if params:
            msg = e
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {
                'filename': exc_traceback.tb_frame.f_code.co_filename,
                'lineno': exc_traceback.tb_lineno,
                'name': exc_traceback.tb_frame.f_code.co_name,
                'type': exc_type.__name__
            }
            msg = "{0}-Throw Exception:{1}-Params:{2}-Errmsg:{3}".format(t, traceback_details, params, str(e))
        if "TimeoutError" not in msg:
            with open("{}/{}.log".format(self.log_dir.replace("\\", "/"), t.strftime("%Y-%m-%d")), "a") as log:
                log.write("{}\n".format(msg))

    async def send(self, session2, msg):
        async with session2.post(
                self.GO_EASY_URL, timeout=self.TIMEOUT,
                data={"appkey": self.COMMONKEY, "channel": "fang", "content": msg}) as rs2:
            # print(await rs2.text())
            pass

    def record(self, t, p):
        with open("record.txt".format(t.strftime("%Y-%m-%d")), "a") as log:
            log.write("{}-{}\n".format(str(t), p))

    async def loop_list(self, uri, session=None, session2=None):
        try:
            async with session.get(uri, headers=self.HEADER_GET_LIST_INFO, timeout=self.TIMEOUT) as rs:
                html = await rs.text()
                if len(html) < 20000:
                    print(html)
                    self.except_info(html, 1)
                    return
                list_info = json.loads(html).get("data").get("list")
                print("list_info :", len(list_info))
                for info in list_info:
                    if not info.get("info"):
                        continue
                    _phone = info.get("info").get("broker").get("base").get("mobile")
                    # print("=====>>>", self.db.get_phone(_phone))
                    if self.db.get_phone(_phone):
                        # 区域过滤
                        title = "{}{}".format(info.get("info").get("property").get("base").get("title"),
                                              info.get("info").get("community").get("base").get("areaName"))
                        _filter = False
                        for add in self.AREA:  # ...
                            if add in title:
                                _filter = True
                                break
                        if _filter:
                            self.db.save(_phone)
                            continue
                        # 房源信息数据ID
                        # await self.send(session2, _phone)
                        # self.db.cache.set("PHONE", _phone)
                        
                        self.db.save(_phone)
                        # os.system("reboot")
        except Exception as e:
            self.except_info(e)

    async def run(self, page=1):
        uri = self.BASE_URL.format(page)
        # try:
        #     os.system("kill -9 $(pidof AliYunDunUpdate)")
        #     os.system("kill -9 $(pidof AliYunDun)")
        # except Exception as e:
        #     self.except_info(e)

        # h = datetime.datetime.now().hour
        # if h < 6:
        #     time.sleep(600)
        #     os.system("reboot")
        async with aiohttp.ClientSession() as session:
            while True:
                # tt = time.time()
                await self.loop_list(uri, session)
                # await self.loop_list(uri, session)
                # print("run time :", time.time() - tt, "----count-->", page)
                break

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()


if __name__ == "__main__":
    crawler = Crawler()
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(crawler.run(1)),
        # asyncio.ensure_future(crawler.run(1)),
        # asyncio.ensure_future(crawler.run(2)),
        # asyncio.ensure_future(crawler.run(3)),
        # asyncio.ensure_future(crawler.run(4)),
        # asyncio.ensure_future(crawler.run(5))
    ]

    loop.run_until_complete(asyncio.wait(tasks))

    loop.run_forever()
