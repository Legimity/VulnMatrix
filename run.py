import os
import sqlite3
import hashlib
import threading
import json
import re
import random


import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

# from docker_lib import Dockers_Start, Dockers_Stop, Dockers_Info
from docker_lib import Dockers_Start, Dockers_Stop, Dockers_Info,Docker_ComposeControl
from utils import Start_Get_Sysinfo
from log.logger import logger
from tornado.options import define, options
import dotenv
dotenv.load_dotenv()

PROJECT_PATH=os.getenv("PROJECT_PATH")
print(PROJECT_PATH)



# 尝试重构代码,从handlers中导入所有的handler，而不是全部写在同一个文件中
from handlers.LoginHandler import LoginHandler, LogoutHandler, HomeHandler, WelcomeHandler
from handlers.BaseHandler import BaseHandler, ErrorHandler,Reset_System_Handler,SettingHandler
from handlers.SocketHandler import SocketHandler
from handlers.PassHandler import Change_Pass_Handler
from handlers.ViewNetworkHandler import ViewNetworkHandler
from handlers.ToolManagerHandler import ToolManagerHandler
from handlers.TreminalWebSocketHandler import TreminalWebSocketHandler


try:
    from Queue import Queue
except ImportError as e:
    from queue import Queue
import os


que = Queue()
page_size = 30
Mem_Limit = '30M'
Sys_Pass = 'admin123'

# Tornado 框架中的 define 函数定义命令行选项 python run.py --port=8080
define("port", default = 8000, help = "run on the given port", type = int)
define("host", default = '0.0.0.0',help = "run on the given host", type = str)
define("sqlite_path", default = "./DB/test.db", help = "database path")


class Application(tornado.web.Application):
    '''
    标准的tornado初始化类。
    '''

    def __init__(self):
        '''
        初始化tornado
        '''

        # tornado的路由信息
        handlers = [
            (r"/", WelcomeHandler),
            (r"/home", HomeHandler),
            (r"/login", LoginHandler),

            (r"/logout", LogoutHandler),
            (r"/stop_all_containers", StopAllContainers),
            # TODO 网络拓扑的接口
            (r"/view", ViewNetworkHandler),
            # (r"/search_images", SearchImagesHandler),
            (r"/images_info", ImagesHandler),
            (r"/status_info", StatusHandler),
            (r"/websocket", SocketHandler),
            (r"/setting", SettingHandler),


            (r"/add_images", AddImagesHandler),
            (r"/start_containers", StartContainersHandler),
            (r"/stop_containers", StopContainersHandler),

            (r"/change_pass", Change_Pass_Handler),
            (r"/add_user", Add_User_Handler),

            # 测试上传文件接口
            # (r"/upload", UploadHandler),
            # 测试根据docker-compose启动靶场
            # (r"/start_envs", DockerComposeControlHandler),
            
            # 新建靶场环境,复制自AddImagesHandler
            (r"/add_envs", AddEnvsHandler),
            (r"/stop_envs", StopEnvsHandler),#TODO
            
           
            (r"/tool_manage", ToolManagerHandler),
            (r"/ws", TreminalWebSocketHandler),

            # 来自StartContainersHandler
            (r"/start_envs", StartEnvsHandler),

            # 增加展示所有已经启动的靶场,
            (r"/envs_info", EnvsHandler),
            
            
            

            (r".*", ErrorHandler),

            
        ]
        # 初始化tornado的设置
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = False,
            cookie_secret = "__TODO:_TORNADO_MY_OWN_RANDOM_VALUE_HERE__",
            login_url = "/login",
            debug = True,
        )

        logger.info('获取tronado基础配置')
        tornado.web.Application.__init__(self, handlers, **settings)
        logger.info('初始化tornado对象,初始化路由')
        self.db = sqlite3.connect(options.sqlite_path, check_same_thread = False)
        self.db.row_factory = self.__dict_factory
        # print("self.db.row_factory",self.db.row_factory)
        logger.info('链接数据库')
        threading.Thread(target = Start_Get_Sysinfo, args = (que,)).start()
        logger.info('开启后台监控进程')
        self.status = que.get()
        logger.info('获取系统信息！')

    def __dict_factory(self, cursor, row):
        '''
        设置sqlite3的查询结果是一个数组。
        :param cursor: sqlite游标
        :param row: 查询的sql语句
        :return: 返回查询的结果。
        '''
        dict_result= {}
        for index, colument in enumerate(cursor.description):
            dict_result[colument[0]] = row[index]
        return dict_result




class StartEnvsHandler(BaseHandler):
    '''
    开启靶场环境。
    '''
    def docker_compose_up(self,docker_hub_path):
      # 启动靶场
      logger.info("Function docker_compose_up has been triggered!")
      docker_compose_path=os.path.join( docker_hub_path,'docker-compose.yml')
      # TODO：path不应该写死，应该根据id启动对应的靶场
      # docker_compose_path=os.path.join(os.path.dirname(__file__), "docker_hub","CFS-Docker","docker-compose.yml")
      # docker_compose_path=os.path.join(os.path.dirname(__file__), "files","docker-compose.yml")
      network_info=Docker_ComposeControl.run(docker_compose_path)
      # network_info：
      # INFO: {'network_names': ['network1', 'network2'], 
      # 'containers': ['app1', 'app2'], 
      # 'network_ids': ['4c40b4d34b48589d703403989fb6ca10982941281a51f5838e897da53565c022', '054ddc962657543d8afb0829c5e7530e894f638b7066847b187d660303519f74']}


    #  原来的tb_status的结构：
    #       0|id|INTEGER|0||1
    # 1|containers_id|CHAR(100)|0||0
    # 2|containers_user|CHAR(50)|1||0
    # 3|images_id|CHAR(100)|1||0
    # 4|containers_status|CHAR(50)|1||0
    # 5|containers_port|CHAR(50)|1||0
    # 6|containers_mapping_path|CHAR(50)|0||0
    # 7|start_time|DATETIMA|0|datetime('now', 'localtime')|0
    # TODO:这里应该写入数据库，记录网络的状态

    # 设计envs_status表
    # id
    # network_id 是一个列表
    # running or closed
    # docker-compose.yml的路径
    # 建表sql
    # CREATE TABLE envs_status (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     network_id TEXT NOT NULL,
    #     containers TEXT NOT NULL,
    #     status TEXT CHECK(status IN ('running', 'closed')) NOT NULL,
    #     docker_hub_path CHAR(50) NOT NULL

    # );

      self.db_update_insert('INSERT INTO envs_status (network_id, status,containers,docker_hub_path) VALUES (?, ?);', [json.dumps(network_info['network_ids']), 'running',json.dumps(network_info['containers']),docker_hub_path])


      return network_info

    @tornado.web.authenticated
    def get(self):
        docker_hub_path = self.get_argument("path", '').strip()
        
        print("@@@@docker_hub_path",docker_hub_path)
        network_info=self.docker_compose_up(docker_hub_path)
        logger.info(network_info)
        
        # 添加成功页面
        self.render('docker.html', status = 'start', port =None, error =  False)



class StopEnvsHandler(BaseHandler):
    '''
    关闭靶场环境。
    '''
    # TODO
    def docker_compose_down(self,docker_compose_path):
      # 启动靶场
      logger.info("Function docker_compose_up has been triggered!")
      network_info=Docker_ComposeControl.stop_and_remove_containers_and_networks(docker_compose_path)
      return network_info

    @tornado.web.authenticated
    def get(self):
        path = self.get_argument("path", '').strip()
        docker_hub_path=os.path.join(path,'docker-compose.yml')
        print("@@@@docker_hub_path",docker_hub_path)
        network_info=self.docker_compose_up(docker_hub_path)
        logger.info(network_info)
        
        # 添加成功页面
        self.render('docker.html', status = 'start', port =None, error =  False)





        # sql = 'SELECT * FROM tb_images WHERE images_id = ? ;'
        # result = self.db_select(sql, [images_id])
        # if not result :
        #     logger.error('用户%s提交的镜像id错误' % self.current_user.decode())
        #     self.render('docker.html', status = '', port = '', error = True)
        #     return

        # port, containers_id, tf = self.__start(result[0]['images_id'], result[0]['images_port'])

        # if not containers_id:
        #     logger.error('用户%s开启容器时错误，错误镜像id是%s' % (self.current_user.decode(), result[0]['images_id']))
        #     self.render('docker.html', status = '', port = '', error = True)
        #     return

        # if not tf :
        #     r = self.__insert_sql(containers_id, result[0]['images_id'], json.dumps(port))
        #     if r :
        #         logger.info('用户%s开启容器成功,容器id是%s,数据写入数据库成功！' % (self.current_user.decode(), containers_id))
        #     else:
        #         logger.error('用户%s开启容器成功,容器id是%s,数据写入数据库失败！' % (self.current_user.decode(), containers_id))
        #         con = Dockers_Info.Get_Containers_Message(containers_id)
        #         Dockers_Stop.Stop_Containers(con)
        #         self.render('docker.html', status = '', port = '', error = True)
        #         return

        # self.render('docker.html', status = 'start', port = self.__get_http(port), error = False)

    




class ImagesHandler(BaseHandler):

    '''
    显示所有的镜像，也可以搜索。
    '''
    @tornado.web.authenticated
    def get(self):
        page = int(self.get_argument("page", 1))
        sql = 'SELECT * FROM tb_images LIMIT ?,?;'
        images_result = self.db_select(sql, [(page - 1) * page_size, page_size])

        images_count = self.db_select('SELECT id FROM tb_images')

        # sql = 'SELECT images_id FROM tb_status WHERE containers_user = ? AND containers_status = "runing";'
        # statrt_result = self.db_select(sql, [self.current_user.decode()])

        result = []

        for x in images_result:
            x['json_images_port'] = json.loads(x['images_port'])
            result.append(x)


        logger.info('获取用户%s可以使用的镜像！' % self.current_user.decode())
        self.render('images.html', cursor = result, count = len(images_count) - len(statrt_result) if (len(images_count) - len(statrt_result)) > 0 else 0)


class EnvsHandler(BaseHandler):

    '''
    显示所有的镜像，也可以搜索。
    '''
    @tornado.web.authenticated
    def get(self):
        # logger.warning("EnvsHandler get")

        # page = int(self.get_argument("page", 1))
        # sql = 'SELECT * FROM tb_envs LIMIT ?,?;'
        # images_result = self.db_select(sql, [(page - 1) * page_size, page_size])

        # images_count = self.db_select('SELECT id FROM tb_images')

        # sql = 'SELECT images_id FROM tb_status WHERE containers_user = ? AND containers_status = "runing";'
        # statrt_result = self.db_select(sql, [self.current_user.decode()])

        # result = []

        # for x in images_result:
        #     if {'images_id': x['images_id']} not in statrt_result:
        #         x['json_images_port'] = json.loads(x['images_port'])
        #         result.append(x)


        # logger.info('获取用户%s可以使用的镜像！' % self.current_user.decode())
        # self.render('envs.html', cursor = result, count = len(images_count) - len(statrt_result) if (len(images_count) - len(statrt_result)) > 0 else 0)
        page = int(self.get_argument("page", 1))
        sql = 'SELECT * FROM tb_envs LIMIT ?,?;'
        envs_result = self.db_select(sql, [(page - 1) * page_size, page_size])
        print("envs_result",envs_result)
        

        result=[]


        self.render('envs.html', cursor = envs_result, count = len(envs_result))
        

# class SearchImagesHandler(BaseHandler):
#     '''
#     搜索镜像
#     '''
#
#     @tornado.web.authenticated
#     def get(self):
#         page = int(self.get_argument("page", 1))
#         q = self.get_argument('q', '')
#         if not q :
#             self.redirect('/images_info')
#             return
#         sql = 'SELECT * FROM tb_images WHERE name LIKE upper(?) OR tags LIKE upper(?) OR info LIKE upper(?) OR author LIKE upper(?) OR types LIKE upper(?) ;'
#         images_count = self.db_select(sql, ['%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%'])
#
#
#         sql = 'SELECT * FROM tb_images WHERE name LIKE upper(?) OR tags LIKE upper(?) OR info LIKE upper(?) OR author LIKE upper(?) OR types LIKE upper(?) LIMIT ?,?;'
#         images_result = self.db_select(sql, ['%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%',  (page - 1) * page_size, page_size])
#
#         sql = 'SELECT images_id FROM tb_status WHERE containers_user = ? AND containers_status = "runing";'
#         statrt_result = self.db_select(sql, [self.current_user.decode()])
#
#         result = []
#         for x in images_result:
#             if {'images_id': x['images_id']} not in statrt_result:
#                 x['json_images_port'] = json.loads(x['images_port'])
#                 result.append(x)
#
#         result_count = []
#
#         for x in images_count:
#             if {'images_id': x['images_id']} not in statrt_result:
#                 result_count.append(x)
#
#         logger.info('获取用户%s搜索的可以使用的镜像！' % self.current_user.decode())
#         self.render('images.html', cursor = result, count = len(result_count))


# 展示已经开启的所有的靶场，复制自上面的SearchImagesHandler
class ShowRangesHandler(BaseHandler):
    '''
    查看所有可用的靶场
    '''

    @tornado.web.authenticated
    def get(self):
        page = int(self.get_argument("page", 1))
        q = self.get_argument('q', '')
        # if not q :
        #     self.redirect('/images_info')
        #     return
        sql = 'SELECT * FROM tb_images WHERE name LIKE upper(?) OR tags LIKE upper(?) OR info LIKE upper(?) OR author LIKE upper(?) OR types LIKE upper(?) ;'
        images_count = self.db_select(sql, ['%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%'])


        sql = 'SELECT * FROM tb_images WHERE name LIKE upper(?) OR tags LIKE upper(?) OR info LIKE upper(?) OR author LIKE upper(?) OR types LIKE upper(?) LIMIT ?,?;'
        images_result = self.db_select(sql, ['%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%', '%' + q + '%',  (page - 1) * page_size, page_size])

        # sql = 'SELECT images_id FROM tb_status WHERE containers_user = ? AND containers_status = "runing";'
        # statrt_result = self.db_select(sql, [self.current_user.decode()])

        result = []
        for x in images_result:
            x['json_images_port'] = json.loads(x['images_port'])
            result.append(x)



        logger.info('获取用户%s搜索的可以使用的镜像！' % self.current_user.decode())
        # self.render('upload.html', cursor = result, count = len(result_count))
        self.render('envs.html', cursor = result, count = len(images_count))


class StatusHandler(BaseHandler):
    '''
    显示获取的系统信息和开启的容器信息。
    '''

    @tornado.web.authenticated
    def get(self):
        sql = 'SELECT * FROM tb_status WHERE containers_user = ? AND containers_status = "runing";'
        status_result = self.db_select(sql, [self.current_user.decode()])
        images_result = self.db_select('SELECT * FROM tb_images;')

        for _ in status_result:
            sql = 'SELECT * FROM tb_images WHERE images_id = ?'
            _['images_info'] = self.db_select(sql, [_['images_id']])[0]
            _['json_containers_port'] = json.loads(_['containers_port'])


        logger.info('获取用户%s已开启的镜像名字和端口' % self.current_user.decode())
        self.render('status.html', sysinfo = self.status, cursor = status_result, start_counts = len(status_result), images_counts = len(images_result))





class StopAllContainers(BaseHandler):
    '''
    关闭当前用户的所有容器
    '''

    @tornado.web.authenticated
    def get(self):

        logger.info('用户%s退出登陆并尝试关闭所有的容器！' % self.current_user.decode())
        sql = 'SELECT containers_id FROM tb_status WHERE containers_user = ? and containers_status = ?;'
        containers_list = self.db_select(sql, [self.current_user.decode(), 'runing'])

        for x in containers_list:
            con = Dockers_Info.Get_Containers_Message(x['containers_id'])
            if not con:
                continue
            Dockers_Stop.Stop_Containers(con)


        sql = 'UPDATE tb_status SET containers_status = ? WHERE containers_user = ? AND containers_status = ?;'
        self.db_update_insert(sql, ['closed', self.current_user.decode(), 'runing'])
        logger.info('关闭用户%s所有的容器，并更新数据库状态！' % self.current_user.decode())
        self.redirect("/logout")

class AddImagesHandler(BaseHandler):
    '''
    添加一个镜像
    '''

    @tornado.web.authenticated
    def get(self):
        self.redirect('/images_info')

    @tornado.web.authenticated
    def post(self):
        file = self.request.files.get('jsonfile', '')
        name = self.get_argument("name", '')
        tags = self.get_argument("tags", '')
        types = self.get_argument("type", '')
        info = self.get_argument("info", '')
        isupload = self.get_argument("isupload", '')
        flag = self.get_argument("flag", '')
        author = self.get_argument("author", '')
        risk = self.get_argument("risk", '')
        hub = self.get_argument("hub", '')
        port = self.get_argument("port", '')
        sys_pass_json = self.get_argument('syspassjson', '').strip()
        sys_pass_file = self.get_argument('syspassfile', '').strip()

        if Sys_Pass != sys_pass_json and Sys_Pass != sys_pass_file :
            logger.info('输入的系统密码错误！')
            return

        if file:
            logger.info('尝试直接上传json文件来批量添加镜像！')
            data = file[0]['body']

            try:
                logger.info('尝试使用json格式化上传的数据！')
                data = json.loads(data)
                for _ in data:

                    port = self.__re_port(_['port'])
                    risk = self.__re_risk(_['risk'])

                    if _['name']: name = _['name']

                    images_name, images_tag = self.__re_hub(_['hub'])
                    if not images_name : continue

                    if _['flag'] and _['types'] == 'ctf':
                        datas = [name, _['info'], _['isupload'], _['types'], _['tags'], risk, _['author'], port, _['flag'], 'start']
                    elif _['types'] == 'debug':
                        datas = [name, _['info'], _['isupload'], _['types'], _['tags'], risk, _['author'], port, 'flag{}', 'start']
                    else:
                        continue

                    t = True
                    for _ in datas:
                        if not _.strip():
                            logger.error('发送的数据错误，数据中有空参数！')
                            t = False
                            break
                    if not t: continue

                    threading.Thread(target = self.__thread_addimages,args = (datas, images_name, images_tag, self.db_update_insert)).start()

            except Exception as  e:
                logger.error('尝试处理上传json数据是出错！')
                return


        elif flag and types == 'ctf' :
            port = self.__re_port(port)
            risk = self.__re_risk(risk)

            if name: name = name

            images_name, images_tag = self.__re_hub(hub)
            if not images_name :
                logger.error('发送的数据错误，不能够获取到正确的镜像名!')
                return

            data = [name, info, isupload, types, tags, risk, author, port, flag, 'start']

            for _ in data:
                if not _.strip():
                    logger.error('发送的数据错误，数据中有空参数！')
                    return

            threading.Thread(target = self.__thread_addimages, args=(data, images_name, images_tag, self.db_update_insert)).start()


        elif types == 'debug':
            port = self.__re_port(port)
            risk = self.__re_risk(risk)

            if name : name = name

            images_name, images_tag = self.__re_hub(hub)
            if not images_name:
                logger.error('发送的数据错误，不能够获取到正确的镜像名!')
                return

            data = [name, info, isupload, types.lower(), tags, risk, author, port, 'flag{}', 'start']
            for _ in data:
                if not _.strip():
                    logger.error('发送的数据错误，数据中有空参数！')
                    return

            threading.Thread(target = self.__thread_addimages, args = (data, images_name, images_tag, self.db_update_insert)).start()

        else:
            logger.error('发送的数据错误，不能够识别环境的类型！')
            return

        self.finish('success')


    def __thread_addimages(self, data, images_name, images_tag, db_update_insert):

        logger.info('开启一个线程去创建images镜像，镜像地址为：%s:%s' % (images_name, images_tag))
        images = Dockers_Start.Add_Images(images_name, images_tag)
        if not images:
            return False

        images_name = images.tags[0]
        images_id = images.id

        data.append(images_name)
        data.append(images_id)

        sql = 'DELETE FROM tb_images WHERE images_name = ? ;'

        if db_update_insert(sql, [images_name,]):
            logger.info('成功创建一个images镜像并删除数据库中旧的数据！')
        else:
            logger.error('成功创建一个images镜像,但是在删除数据库中旧的数据时出错。')

        sql = 'INSERT INTO tb_images (name, info, isupload, types, tags, difficulty, author, images_port, flag, images_start_mode, images_name, images_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'

        if db_update_insert(sql, data):
            logger.info('成功把images镜像信息写入数据库，镜像名字为：%s' % images_name)
        else:
            logger.error('把images镜像信息写入数据库时出错，镜像名字为：%s' % images_name)



    def __re_port(self, strings):

        result = []
        logger.info('处理传入的环境端口信息！')

        string = re.split(r',|;', strings.lower())


        if not string:
            logger.error('传入的环境端口信息有误！错误端口信息为：%s' % strings)
            return ''

        res = r'(\d{1,5})/(tcp|udp)'

        print(string)
        for _ in string:
            if _ == '':
                continue
            r = re.search(res, _)

            if not r :
                logger.error('传入的环境端口信息有误！错误端口信息为：%s' % _)
                return ''

            port = r.group(1)
            protocol = r.group(2)
            result.append({'port': port, 'protocol': protocol})

        logger.info('成功处理传入的环境端口信息，获取到端口信息为：%s' % json.dumps(result))
        return json.dumps(result)

    def __re_risk(self, string):

        if not string.strip():
            return ''

        string = string.strip().lower()
        logger.info('处理传入的环境难度等级信息！')

        lists = ['simple', 'medium', 'advanced']

        if string not in lists:
            logger.error('传入的环境难度等级信息有误！')
            return ''

        logger.info('成功处理传入的环境难度等级信息，获取到难度等级为：%s' % string)
        return string


    def __re_hub(self, hub):

        result = hub.strip().split(':')
        if len(result) > 1 :
            images_name = result[0]
            images_tag = result[1]
        else:
            images_name = hub.strip()
            images_tag = 'latest'
        if images_name :
            logger.info('成功获取到镜像名称为：%s:%s' % (images_name, images_tag))
        return images_name, images_tag



class AddEnvsHandler(BaseHandler):
    '''
    添加一个镜像
    '''

    # @tornado.web.authenticated
    def get(self):
        self.redirect('/envs_info')

    # @tornado.web.authenticated
    def post(self):
        file = self.request.files.get('jsonfile', '')
        name = self.get_argument("name", '')
        tags = self.get_argument("tags", '')
        # types = self.get_argument("type", '')
        info = self.get_argument("info", '')
        # isupload = self.get_argument("isupload", '')
        # flag = self.get_argument("flag", '')
        # author = self.get_argument("author", '')
        # risk = self.get_argument("risk", '')
        # hub = self.get_argument("hub", '')
        # port = self.get_argument("port", '')
        # sys_pass_json = self.get_argument('syspassjson', '').strip()
        sys_pass_file = self.get_argument('syspassfile', '').strip()
        
        # logger.warning("@@@@env info",info)
        # logger.warning("@@@@env name",name)
        # print("@@@@env info",info,"@@@@env name",name)
        # print("sys_pass_file",sys_pass_file)
        # print("file[0]",file[0])#这里可以获取到docker-compose文件的内容
        # file[0] {'filename': 'docker-compose.yml', 'body'DROP TABLE IF EXISTS tb_images;: b'version: \'3.8\'\r\n\r\nnetworks:\r\n  network1:\r\n    driver: bridge\r\n    ipam:\r\n      config:\r\n        - subnet: 172.25.0.0/16\r\n  network2:\r\n    driver: bridge\r\n    ipam:\r\n      config:\r\n        - subnet: 172.26.0.0/16\r\n\r\nservices:\r\n  app1:\r\n    image: nginx:latest\r\n    ports:\r\n      - "8080:80"\r\n    networks:\r\n      network1:\r\n        aliases:\r\n          - app1\r\n        ipv4_address: 172.25.0.10\r\n      network2:\r\n        aliases:\r\n          - app1-net2\r\n        ipv4_address: 172.26.0.10\r\n    environment:\r\n      - NGINX_HOST=app1\r\n      - NGINX_PORT=80\r\n    volumes:\r\n      - app1-data:/usr/share/nginx/html\r\n\r\n  app2:\r\n    image: redis:latest\r\n    ports:\r\n      - "6379:6379"\r\n    networks:\r\n      network2:\r\n        aliases:\r\n          - app2\r\n        ipv4_address: 172.26.0.11\r\n    environment:\r\n      - REDIS_PASSWORD=secret\r\n    volumes:\r\n      - app2-data:/data\r\n\r\nvolumes:\r\n  app1-data:\r\n  app2-data:\r\n', 'content_type': 'application/octet-stream'}

        if name:
          docker_hub_path = os.path.join(PROJECT_PATH,'docker_hub', name)
          os.makedirs(docker_hub_path, exist_ok=True)
          file_path = os.path.join(docker_hub_path, 'docker-compose.yml')
          with open(file_path, 'w') as f:
            f.write(file[0]['body'].decode('utf-8'))

        # Todo：写入tb_envs数据库操作
        #         CREATE TABLE tb_envs (
        #     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     name char(50) NOT NULL,
        #     tags TEXT,
        #     info  char(50) ,
        #     docker_hub_path  char(50) 
        # );
        sql='INSERT INTO tb_envs (name,tags, info, docker_hub_path) VALUES (?, ?, ?, ?);'
        self.db_update_insert(sql,[name,tags, info, docker_hub_path])

        # if Sys_Pass != sys_pass_json and Sys_Pass != sys_pass_file :
        #     logger.info('输入的系统密码错误！')
        #     return

        # if file:
        #     logger.info('尝试直接上传json文件来批量添加镜像！')
        #     data = file[0]['body']

        #     try:
        #         logger.info('尝试使用json格式化上传的数据！')
        #         data = json.loads(data)
        #         for _ in data:

        #             port = self.__re_port(_['port'])
        #             risk = self.__re_risk(_['risk'])

        #             if _['name']: name = _['name']

        #             images_name, images_tag = self.__re_hub(_['hub'])
        #             if not images_name : continue

        #             if _['flag'] and _['types'] == 'ctf':
        #                 datas = [name, _['info'], _['isupload'], _['types'], _['tags'], risk, _['author'], port, _['flag'], 'start']
        #             elif _['types'] == 'debug':
        #                 datas = [name, _['info'], _['isupload'], _['types'], _['tags'], risk, _['author'], port, 'flag{}', 'start']
        #             else:
        #                 continue

        #             t = True
        #             for _ in datas:
        #                 if not _.strip():
        #                     logger.error('发送的数据错误，数据中有空参数！')
        #                     t = False
        #                     break
        #             if not t: continue

        #             threading.Thread(target = self.__thread_addimages,args = (datas, images_name, images_tag, self.db_update_insert)).start()

        #     except Exception as  e:
        #         logger.error('尝试处理上传json数据是出错！')
        #         return


        # elif flag and types == 'ctf' :
        #     port = self.__re_port(port)
        #     risk = self.__re_risk(risk)

        #     if name: name = name

        #     images_name, images_tag = self.__re_hub(hub)
        #     if not images_name :
        #         logger.error('发送的数据错误，不能够获取到正确的镜像名!')
        #         return

        #     data = [name, info, isupload, types, tags, risk, author, port, flag, 'start']

        #     for _ in data:
        #         if not _.strip():
        #             logger.error('发送的数据错误，数据中有空参数！')
        #             return

        #     threading.Thread(target = self.__thread_addimages, args=(data, images_name, images_tag, self.db_update_insert)).start()


        # elif types == 'debug':
        #     port = self.__re_port(port)
        #     risk = self.__re_risk(risk)

        #     if name : name = name

        #     images_name, images_tag = self.__re_hub(hub)
        #     if not images_name:
        #         logger.error('发送的数据错误，不能够获取到正确的镜像名!')
        #         return

        #     data = [name, info, isupload, types.lower(), tags, risk, author, port, 'flag{}', 'start']
        #     for _ in data:
        #         if not _.strip():
        #             logger.error('发送的数据错误，数据中有空参数！')
        #             return

        #     threading.Thread(target = self.__thread_addimages, args = (data, images_name, images_tag, self.db_update_insert)).start()

        # else:
        #     logger.error('发送的数据错误，不能够识别环境的类型！')
        #     return

        self.finish('success')


    # def __thread_addimages(self, data, images_name, images_tag, db_update_insert):

    #     logger.info('开启一个线程去创建images镜像，镜像地址为：%s:%s' % (images_name, images_tag))
    #     images = Dockers_Start.Add_Images(images_name, images_tag)
    #     if not images:
    #         return False

    #     images_name = images.tags[0]
    #     images_id = images.id

    #     data.append(images_name)
    #     data.append(images_id)

    #     sql = 'DELETE FROM tb_images WHERE images_name = ? ;'

    #     if db_update_insert(sql, [images_name,]):
    #         logger.info('成功创建一个images镜像并删除数据库中旧的数据！')
    #     else:
    #         logger.error('成功创建一个images镜像,但是在删除数据库中旧的数据时出错。')

    #     sql = 'INSERT INTO tb_images (name, info, isupload, types, tags, difficulty, author, images_port, flag, images_start_mode, images_name, images_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'

    #     if db_update_insert(sql, data):
    #         logger.info('成功把images镜像信息写入数据库，镜像名字为：%s' % images_name)
    #     else:
    #         logger.error('把images镜像信息写入数据库时出错，镜像名字为：%s' % images_name)



    # def __re_port(self, strings):

    #     result = []
    #     logger.info('处理传入的环境端口信息！')

    #     string = re.split(r',|;', strings.lower())


    #     if not string:
    #         logger.error('传入的环境端口信息有误！错误端口信息为：%s' % strings)
    #         return ''

    #     res = r'(\d{1,5})/(tcp|udp)'

    #     print(string)
    #     for _ in string:
    #         if _ == '':
    #             continue
    #         r = re.search(res, _)

    #         if not r :
    #             logger.error('传入的环境端口信息有误！错误端口信息为：%s' % _)
    #             return ''

    #         port = r.group(1)
    #         protocol = r.group(2)
    #         result.append({'port': port, 'protocol': protocol})

    #     logger.info('成功处理传入的环境端口信息，获取到端口信息为：%s' % json.dumps(result))
    #     return json.dumps(result)

    # def __re_risk(self, string):

    #     if not string.strip():
    #         return ''

    #     string = string.strip().lower()
    #     logger.info('处理传入的环境难度等级信息！')

    #     lists = ['simple', 'medium', 'advanced']

    #     if string not in lists:
    #         logger.error('传入的环境难度等级信息有误！')
    #         return ''

    #     logger.info('成功处理传入的环境难度等级信息，获取到难度等级为：%s' % string)
    #     return string


    # def __re_hub(self, hub):

    #     result = hub.strip().split(':')
    #     if len(result) > 1 :
    #         images_name = result[0]
    #         images_tag = result[1]
    #     else:
    #         images_name = hub.strip()
    #         images_tag = 'latest'
    #     if images_name :
    #         logger.info('成功获取到镜像名称为：%s:%s' % (images_name, images_tag))
    #     return images_name, images_tag










class StartContainersHandler(BaseHandler):
    '''
    开启容器。
    '''

    @tornado.web.authenticated
    def get(self):
        images_id = self.get_argument("images_id", '').strip()

        sql = 'SELECT * FROM tb_images WHERE images_id = ? ;'
        result = self.db_select(sql, [images_id])
        if not result :
            logger.error('用户%s提交的镜像id错误' % self.current_user.decode())
            self.render('docker.html', status = '', port = '', error = True)
            return

        port, containers_id, tf = self.__start(result[0]['images_id'], result[0]['images_port'])

        if not containers_id:
            logger.error('用户%s开启容器时错误，错误镜像id是%s' % (self.current_user.decode(), result[0]['images_id']))
            self.render('docker.html', status = '', port = '', error = True)
            return

        if not tf :
            r = self.__insert_sql(containers_id, result[0]['images_id'], json.dumps(port))
            if r :
                logger.info('用户%s开启容器成功,容器id是%s,数据写入数据库成功！' % (self.current_user.decode(), containers_id))
            else:
                logger.error('用户%s开启容器成功,容器id是%s,数据写入数据库失败！' % (self.current_user.decode(), containers_id))
                con = Dockers_Info.Get_Containers_Message(containers_id)
                Dockers_Stop.Stop_Containers(con)
                self.render('docker.html', status = '', port = '', error = True)
                return

        self.render('docker.html', status = 'start', port = self.__get_http(port), error = False)

    def __get_port(self):
        logger.info('获取系统已经开启的端口，并返回一个随机端口')
        cmd = "netstat -ntl | grep -v Active | grep -v Proto | awk '{print $4}' | awk -F: '{print $NF}'"
        ports = os.popen(cmd).read().split('\n')
        port = random.randint(1024, 65535)
        if str(port) not in ports:
            return port
        else:
            self.__get_port()

    def __start(self, images_id, port_containers):
        # sql = 'SELECT * FROM tb_status WHERE images_id = ? AND containers_user = ? AND containers_status = "runing" LIMIT 1;'
        # result = self.db_select(sql, [images_id, self.current_user.decode()])
        # if result :
        #     port = json.loads(result[0]['containers_port'])
        #
        #     return port, result[0]['containers_id'], True

        port = {}

        json_port = json.loads(port_containers)


        for _ in json_port:
            port_containers = '%s/%s' % (_['port'], _['protocol'])

            port_host = self.__get_port()

            port[port_containers] = '%s/%s' % (port_host, _['protocol'])

        containers_id = Dockers_Start.Start_Containers(images_id, port, Mem_Limit = Mem_Limit)
        return port, containers_id, False

    def __insert_sql(self, containers_id, images_id, port_containers):
        sql = "INSERT INTO tb_status (containers_id, containers_user, images_id, containers_status, containers_port, containers_mapping_path) VALUES (?, ?, ?, 'runing', ?, '');"
        result = self.db_update_insert(sql, [containers_id, self.current_user.decode(), images_id, port_containers])

        if not result :
            return False

        return True


    def __get_http(self, port):

        res = r'(\d+)/(tcp|udp)'

        try:
            if port['80/tcp']:
                return re.search(res, port['80/tcp']).group(1)
            elif port['8080/tcp']:
                return re.search(res, port['8080/tcp']).group(1)

        except Exception as e:
            return False

class StopContainersHandler(BaseHandler):
    '''
    关闭容器
    '''

    @tornado.web.authenticated
    def get(self):
        containers_id = self.get_argument("containers_id", '').strip()
        if not containers_id:
            logger.error('用户%s提交的容器id错误' % self.current_user.decode())
            self.render('docker.html', status = '', port = '', error = True)
            return
        logger.info('用户%s提交的容器id是%s。' % (self.current_user.decode(),containers_id))
        con = Dockers_Info.Get_Containers_Message(containers_id)
        if not con:
            logger.error('用户%s提交的容器id错误' % self.current_user.decode())
            self.render('docker.html', status = '', port = '', error = True)
            return
        logger.info('获取到用户%s提交的容器信息。' % self.current_user.decode())
        if not Dockers_Stop.Stop_Containers(con):
            logger.error('获取用户%s提交的容器信息，但是在关闭的时候出错。' % self.current_user.decode())
            self.render('docker.html', status = '', port = '', error = True)
            return
        logger.info('成功关闭用户%s提交的容器。' % self.current_user.decode())
        sql = "UPDATE tb_status SET containers_status = 'closed' WHERE containers_id = ? ;"
        result = self.db_update_insert(sql, [containers_id])
        if not result:
            logger.error('成功关闭用户%s提交的容器，但是在写入数据库时出错。' % self.current_user.decode())
            self.render('docker.html', status = '', port = '', error = True)
            return
        logger.info('成功关闭用户%s提交的容器，并成功写入数据库。' % self.current_user.decode())
        self.render('docker.html', status='close', port='', error = False)


class Add_User_Handler(BaseHandler):
    '''
    系统重置页面
    '''

    @tornado.web.authenticated
    def get(self):
        sys_pass = self.get_argument('sys_pass', '').strip()
        username = self.get_argument('username', '').strip()
        password = self.get_argument('password', '').strip()
        email = self.get_argument('email', '').strip()

        if Sys_Pass != sys_pass :
            self.render('setting.html', error = '加入用户失败！系统密码不正确！')
            return
        if not username or not password or not email:
            self.render('setting.html', error='用户数据不能为空！')
            return

        md = hashlib.md5()
        md.update(password.encode('utf-8'))
        password = md.hexdigest()

        sql = 'INSERT INTO tb_userinfo (username, password, email) VALUES (?, ?, ?);'
        res = self.db_update_insert(sql, [username, password, email])
        if not res :
            self.render('setting.html', error = '加入用户失败！请检查输入的数据！')
            return

        self.render('setting.html', error = '加入用户成功！')





def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
