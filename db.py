# coding:utf8
import sys
import time
import redis
import sqlite3


class DB(object):

    con = None
    cur = None
    cache = None
    CACHE_LIMIT = 10000

    def __init__(self):
        if "win" in sys.platform:
            self.con = sqlite3.connect("fang.sqlite3")
        else:
            self.con = sqlite3.connect("/mnt/fang.sqlite3")
        self.cur = self.con.cursor()
        self.cache = redis.StrictRedis(host='localhost', port=6379, db=0)

        # self.init_cache()

    def query(self):
        self.cur.execute("select phone from fang order by time desc limit {}".format(self.CACHE_LIMIT))
        return self.cur.fetchall()

    def update(self, obj):
        self.cur.execute("insert into fang(phone, time) values ('{}', '{}')".format(obj, int(time.time())))
        self.con.commit()

    def init_cache(self):
        db_datas = self.query()
        for data in db_datas:
            self.cache.getset(data[0], 1)
        pass

    # conn = self.connection or pool.get_connection(command_name, **options)
    # try:
    #     print("AAAAA : ", args, command_name, options)
    #     conn.send_command(*args)
    #     return self.parse_response(conn, command_name, **options)
    def get_phone(self, phone):
        return self.cache.get(phone) is None

    def set_phone(self, phone):
        self.cache.set(phone, 1)

    def save(self, phone):
        self.set_phone(phone)
        self.update(phone)

