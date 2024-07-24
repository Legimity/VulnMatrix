import tornado.web
from log.logger import logger
class BaseHandler(tornado.web.RequestHandler):

    @property
    def status(self):
        '''
        获取系统信息
        :return: 返回一个字典
        '''
        return self.application.status

    def db_select(self, sql, variable = []):
        '''
        统一数据库查询方法
        :param sql: 查询的sql语句
        :param variable: 查询语句的参数
        :return: 返回一个字典，包含所有的查询结果
        '''
        try:
            cursors = self.application.db.cursor()
            cursors.execute(sql, variable)
        except Exception as e:
            logger.error('查询数据库出错！SQL语句为：%s,错误原因为：%s' % (sql, e))
            return []

        return cursors.fetchall()

    def db_update_insert(self, sql, variable = []):
        '''
        统一数据库插入更新删除方法
        :param sql: sql语句
        :param variable: sql语句的参数
        :return: 返回True或False
        '''
        try:
            self.application.db.execute(sql, variable)
            self.application.db.commit()
        except Exception as e:
            logger.error('数据库插入更改数据出错！SQL语句为：%s,错误原因为：%s' % (sql, e))
            return False

        return True

    def get_current_user(self):
        '''
        设置安全登陆的cookie
        :return:
        '''
        return self.get_secure_cookie("cookie_user")

    def write_error(self, status_code, **kwargs):
        '''
        统一网站错误信息为500，友好显示界面
        :param status_code:
        :param kwargs:
        :return:
        '''
        self.render('500.html')


class ErrorHandler(BaseHandler):
    '''
    设置404错误页面
    '''
    def get(self):
        self.render('404.html')


class Reset_System_Handler(BaseHandler):
    '''
    系统重置页面
    '''

    @tornado.web.authenticated
    def get(self):
        self.render('setting.html')

    @tornado.web.authenticated
    def post(self):
        password = self.get_argument('password', '')
        pass
    
class SettingHandler(BaseHandler):
    '''
    设置页面
    '''

    @tornado.web.authenticated
    def get(self):
        self.render('change_pass.html', error='')



class HomeHandler(BaseHandler):
    '''
    主页，搜索。
    '''
    @tornado.web.authenticated
    def get(self):
        self.render('search.html')
