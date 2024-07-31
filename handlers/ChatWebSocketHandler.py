import json
import threading
import tornado.web

from log.logger import logger
from chat_sys.conversations import KnowbaseConversation

_task_queue = KnowbaseConversation.get_instance().task_queue

class ChatWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        logger.info("WebSocket opened")

    def on_message(self, message):
        data = json.loads(message)
        user_message = data.get('message')
        buffer = ""

        _task_queue.join()   # 等待队列中所有任务完成才能处理用户输入的新消息

        # 创建知识库更新的线程
        _task_queue.put(threading.Thread(target=KnowbaseConversation.get_instance().update_conv, args=(user_message,)))   # 创建一个线程对象，用当前对话记录更新知识库，并添加到线程队列

        # 对回复进行回传
        for reply in KnowbaseConversation.get_instance().handle(user_message):
            buffer += reply
            self.write_message(reply)

    def on_close(self):
        logger.info("WebSocket closed")