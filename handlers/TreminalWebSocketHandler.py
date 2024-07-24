import os
import tornado.websocket  

# pty Linux终端版本
import pty
class TreminalWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
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
            container_name_or_id = "0ae88c1b358d"
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

    def handle_terminal_output(self, fd, events):
        if events & self.ioloop.READ:
            output = os.read(self.master_fd, 1024).decode()
            self.write_message(output)