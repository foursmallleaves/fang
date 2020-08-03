# coding:utf-8
import sys
import json
import time
import asyncio
import datetime
import aiohttp
from aiohttp import web

"""
    s012 
    47.105.93.118(公)/172.31.125.143(私有)
"""

SOCKET_SERVICE_IP = "172.31.125.143"
SOCKET_SERVICE_PORT = 8899
TIMEOUT = 0.5

BASE_URL = "https://appsale.58.com/mobile/v5/sale/property/list?ajk_city_id=147&app=i-wb&udid2=439639427b274647bdc862d5d58470f467665632&v=13.2.3&page_size=41&source_id=2&city_id=147&uuid=439639427b274647bdc862d5d58470f467665632&entry=11&select_type=0&lng=119.792740&page=1&lat=34.045411&is_struct=1"

HEADER_GET_LIST_INFO = {
    "Accept": "*/*",
    "ua": "iPhone 6S_iOS 13.2.3",
    "User-Agent": "58tongcheng/9.3.2 (iPhone; iOS 13.2.3; Scale/2.00)",
    "nsign": "1000751ccdc730d5e8d51ff468acde406b32",
}


def except_info(e, params=None):
    """ 异常信息打印 """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_details = {
        'filename': exc_traceback.tb_frame.f_code.co_filename,
        'lineno': exc_traceback.tb_lineno,
        'name': exc_traceback.tb_frame.f_code.co_name,
        'type': exc_type.__name__
    }
    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # if traceback_details.get("type") != "TimeoutError":
    print("{0}-Throw Exception:{1}-Params:{2}-Errmsg:{3}".format(t, traceback_details, params, str(e)))


# 服务器返回数据
async def get_info(request):
    text = ""
    try:
        async with aiohttp.ClientSession(json_serialize=json.dumps, headers=HEADER_GET_LIST_INFO) as session:
            async with session.get(BASE_URL, timeout=TIMEOUT) as rs:
                text = await rs.text()
    except Exception as e:
        except_info(e)

    return web.Response(text=text)


async def init(loop_event):
    app = web.Application(loop=loop_event)
    app.router.add_route('GET', '/syn_data/', get_info)
    # 创建服务
    server = await loop_event.create_server(app.make_handler(), SOCKET_SERVICE_IP, SOCKET_SERVICE_PORT)  # 创建Http服务
    print('Server started at http://{}:{}...'.format(SOCKET_SERVICE_IP, SOCKET_SERVICE_PORT))
    return server


if __name__ == "__main__":

    service_loop = asyncio.get_event_loop()
    service_loop.run_until_complete(init(service_loop))
    service_loop.run_forever()

    pass

