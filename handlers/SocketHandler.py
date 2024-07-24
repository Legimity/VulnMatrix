import tornado.websocket
import threading
from log.logger import logger
import asyncio
import json
try:
    from Queue import Queue
except ImportError as e:
    from queue import Queue
import os

que = Queue()
class SocketHandler(tornado.websocket.WebSocketHandler):
    '''
    一个websocket连接，从后台获取系统信息，并且返回到前端。
    '''
    waiters = set()

    def __init__(self, application, request):
        super(SocketHandler, self).__init__(application, request)
        logger.info('开始获取系统信息，并使用websocket发送给每个客户端！')
        threading.Thread(target = self.__send_messages, args = (que,)).start()

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def check_origin(self, origin):
        # set open must with Browser
        return True

    def open(self):
        username = self.get_secure_cookie('cookie_user')
        if not username:
            return
        logger.info('开启websocket链接')
        SocketHandler.waiters.add(self)

    def on_close(self):
        logger.info('关闭websocket链接')
        SocketHandler.waiters.remove(self)

    def on_message(self, message):
        logger.info('和客户端连接成功！')

    @classmethod
    def __send_messages(cls, que):
        asyncio.set_event_loop(asyncio.new_event_loop())
        while 1:
            status = json.dumps(que.get())
            for waiters in cls.waiters:
                try:
                    waiters.write_message(status)
                    logger.info('向客户端发送系统信息成功！')
                except Exception as e:
                    continue
            que.queue.clear()