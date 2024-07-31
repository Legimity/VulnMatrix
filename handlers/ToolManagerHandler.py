import os
import json
import threading
import tornado.web
from handlers.BaseHandler import BaseHandler

from log.logger import logger
from chat_sys.conversations import KnowbaseConversation
from utils.regProduct import generate_reg_file

def monitor(task_queue):
    """监控任务队列， 检查是否有任务需要执行"""
    while True:
        # 阻塞等待队列中的任务
        task = task_queue.get()
        if task is None:
            continue
        logger.info(f"Executing task: {task}")
        task.start()    # 启动线程
        task.join()     # 等待线程结束
        task_queue.task_done()  # 任务完成，从队列中移除
        logger.info(f"Task {task} completed. {task_queue.qsize()} tasks left.")


class ToolManagerHandler(BaseHandler):
    '''
    工具管理界面 快捷使用攻击进行渗透测试
    '''
    @tornado.web.authenticated
    def get(self):
        # 渲染页面
        self.check_and_create_table('tb_local_tool', 'CREATE TABLE tb_local_tool (id INTEGER PRIMARY KEY AUTOINCREMENT, tool_name VARCHAR(255), tool_path VARCHAR(255));')
        local_tools = self.db_select('SELECT * FROM tb_local_tool;')

        tool = dict()
        tool.setdefault('local', {})
        tool.setdefault('remote', {})
        #print(local_tools)
        for local_tool in local_tools:
            tool['local'][local_tool['tool_name']] = local_tool['tool_path']
        tool['remote'] = {"metasploit":"/bin",
                      "bee":"/tmp",
                      "sqlmap":"/tmp",
                      "nmap":"/tmp",
                      "Nikto":"/bin",
                      }
        if self.get_argument('type', '') != 'query':
            global _conversation, _monitor_thread
            # 创建对话模型
            _conversation = KnowbaseConversation.get_instance()
            # 创建并启动监控线程
            _monitor_thread = threading.Thread(target=monitor, args=(_conversation.task_queue,))
            _monitor_thread.daemon = True  # 设置为守护线程，这样主线程退出时监控线程也会退出
            _monitor_thread.start()

            logger.info('初始化 AI 成功')
            self.render('tool_manage.html')
            #self.finish()
        else:
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(tool))


    @tornado.web.authenticated
    def put(self):
        # 检查是否存在本地工具表，如果不存在则创建
        self.check_and_create_table('tb_local_tool', 'CREATE TABLE tb_local_tool (id INTEGER PRIMARY KEY AUTOINCREMENT, tool_name VARCHAR(255), tool_path VARCHAR(255));')
        # 检查是否存在远程工具表，如果不存在则创建
        self.check_and_create_table('tb_remote_tool', 'CREATE TABLE tb_remote_tool (id INTEGER PRIMARY KEY AUTOINCREMENT, tool_name VARCHAR(255), tool_path VARCHAR(255));')
        data = self.request.body.decode('utf-8')
        try:
            data = json.loads(data)
        except Exception as e:
            logger.error('获取数据失败！')
            self.write('error')
        exeName = data.get('exeName', '')
        exePath = data.get('exePath', '')
        procotalName,file_path = generate_reg_file(exePath)
        self.db_update_insert('INSERT INTO tb_local_tool (tool_name, tool_path) VALUES (?, ?);', [exeName, procotalName])
        # 文件传输
        file_name = os.path.basename(file_path)
        # 设置HTTP头部，告诉浏览器这是一个文件下载响应
        self.set_header('Content-Type', 'application/json')
        try:
            with open(file_path, 'rb') as f:
                data = f.read()  # 读取文件块
                self.write(json.dumps({"status": "success","filename" : exeName +".reg","content": data.decode('utf-8')}))
        except Exception as e:
            self.write(json.dumps({"status": "error", "message": str(e)}))
        self.finish()
