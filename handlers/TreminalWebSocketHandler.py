import os
import re
import tornado.websocket
import string
from log.logger import logger

# pty Linux终端版本
import pty
import threading
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chat_sys.conversations import KnowbaseConversation
_task_queue = KnowbaseConversation.task_queue

class TreminalWebSocketHandler(tornado.websocket.WebSocketHandler):
    # 命令提示符编码（正则)
    SHELL = b'\x1b[?2004h\x1b]0;root@'
    # 命令行键入回车换行
    ENTER = b'\r\n\x1b[?2004l\r'

    def open(self):
        self.record = [b'', b'']
        self.mode = 0

        self.master_fd, slave_fd = pty.openpty()
        self.pid = os.fork()
        if self.pid == 0:  # 子进程
            os.setsid()
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(slave_fd)
            os.close(self.master_fd)
            # 指定Docker容器名称或ID
            container_name_or_id = "d5c989e2fa80"
            # 使用docker exec命令进入容器的bash
            os.execv('/usr/bin/docker', ['docker', 'exec', '-it', container_name_or_id, '/bin/bash'])
        else:  # 父进程
            os.close(slave_fd)
            self.ioloop = tornado.ioloop.IOLoop.current()
            self.fd_handler = self.ioloop.add_handler(self.master_fd, self.handle_terminal_output, self.ioloop.READ)

    def on_message(self, message):
        os.write(self.master_fd, message.encode())

    def on_close(self):
        self.ioloop.remove_handler(self.master_fd)
        os.kill(self.pid, 9)

    def _update_kb_stub(self):
        """基于shel进行知识库更新"""
        # —————————— 指令过滤 ————————————
        if ": command not found" in self.record[1].strip():   # 无效指令识别
            return
        if self.record[0].strip() == "" or self.record[1].strip() == "":   # 空指令识别
            return
        if self.record[0].strip() in ["python", "python3"]:  # 启动 python
            return
        with open('./conf/irr_cmd.txt', 'r') as file:   # 无关指令识别
            for cmd in file:
                if cmd.rstrip('\n') in self.record[0].strip().split(" "):
                    return
        # ——————————————————————————————

        MAX_TOKEN = 2048
        ## 更新知识库
        if len(self.record[1]) > MAX_TOKEN:    # 命令的输出结果太长要进行切分
            # 创建拆分器
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=MAX_TOKEN,           # 每个 chunk 最多 MAX_TOKEN 个字符
                chunk_overlap=20,               # chunk 与 chunk 之间重叠的字符有 20 个
                length_function=len,
                is_separator_regex=False,
            )
            # 按照分块更新数据库
            chunks = text_splitter.split_text(self.record[1])
            for chunk in chunks:
                record = [self.record[0], chunk]
                _task_queue.put(threading.Thread(target=KnowbaseConversation.get_instance().update_sh, args=(record,)))   # 添加到线程队列
        else:
            _task_queue.put(threading.Thread(target=KnowbaseConversation.get_instance().update_sh, args=(self.record,)))   # 添加到线程队列

    def _handle(self, msg):
        """提取终端用户输入与结果输出"""
        def remove_color_codes(s):
            """过滤掉颜色控制字符"""
            pattern = r'\x1b\[([0-9]{0,2};)*[0-9]{0,2}m'  # 正则表达式匹配颜色控制字符
            return re.sub(pattern, '', s)

        def parase_control_codes(s):
            """过滤掉控制字符"""
            size = len(s)
            i = 0
            res = ""
            while i < size:
                # 可打印字符
                if s[i] in string.printable:   # 可打印字符
                    res += s[i]
                    i+=1
                    continue
                # 非可打印字符
                for bac in [b"\x08\x1b[K", b"\x08 \x08", b"\x08"]:  # 退格符号
                    if s[i:].encode().startswith(bac):
                        i += (len(bac)-1)
                        res = res[:-1]
                        break
                i += 1
            return res

        def get_shell_prompt(msg):
            """匹配并提取提示符字符串"""
            shell_pat = [    # 正则
                r'(\x1b\[\?2004h\x1b\]0;root@)([0-9a-f]+)',
                r'(: )((/[\w\-.]+(?:/[\w\-.]+)*/?)|(/))',
                r'(\)-\[\x1b\[0;1m)((/[\w\-.]+(?:/[\w\-.]+)*/?)|(/))',
            ]
            l = [
                b'',
                b'\x07\x1b[;94m\xe2\x94\x8c\xe2\x94\x80\xe2\x94\x80(\x1b[1;31mroot\xe3\x89\xbfd5c989e2fa80\x1b[;94m',
                b'\x1b[;94m]\r\r\n\x1b[;94m\xe2\x94\x94\xe2\x94\x80\x1b[1;31m#\x1b[0m ',
            ]
            result = b''
            for pat,s in zip(shell_pat,l):
                try:
                    result += "".join(re.findall(pat, msg.decode())[0][:2]).encode() + s
                except:
                    pass
            return result

        if TreminalWebSocketHandler.SHELL.decode() in msg.decode() or b'\x07\x1b[;94m\xe2\x94\x8c\xe2\x94\x80\xe2\x94\x80(\x1b[1;31mroot\xe3\x89\xbfd5c989e2fa80\x1b[;94m'.decode() in msg.decode():
            sp = get_shell_prompt(msg)
            tmp = msg.split(sp)
            self.record[1] += tmp[0].split(TreminalWebSocketHandler.ENTER)[-1]

            # 处理
            self.record[0] = parase_control_codes(self.record[0].decode())   # 命令处理
            self.record[1] = remove_color_codes(self.record[1][:-4].decode())  # 去掉输出结果最后的 '\r\n\r\n'

            # 日志
            logger.info(f"got cmd executed record: ['{self.record[0]}', {self.record[1] if len(self.record[1]) < 70 else self.record[1][:30]+' ... '+self.record[1][-30:]}]")

            # 知识库更新
            self._update_kb_stub()

            self.record = [b'', tmp[-1]]
            self.mode = 0
            return

        if TreminalWebSocketHandler.ENTER in msg:
            tmp = msg.split(TreminalWebSocketHandler.ENTER)
            self.record[0] += tmp[0]
            self.record[1] += tmp[1]
            self.mode = 1
            return

        self.record[self.mode] += msg

    def handle_terminal_output(self, fd, events):
        if events & self.ioloop.READ:
            output = os.read(self.master_fd, 1024).decode()
            #print("output: ", output.encode())
            self._handle(output.encode())
            self.write_message(output)