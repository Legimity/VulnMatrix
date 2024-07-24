from handlers.BaseHandler import BaseHandler
import tornado.web
import hashlib
from log.logger import logger

class LoginHandler(BaseHandler):
    '''
    设置登陆方法
    '''

    def get(self):
        self.render('login.html', error = False)

    def post(self):
        username = self.get_argument("username", '')
        password = self.get_argument("password", '')
        md = hashlib.md5()
        md.update(password.encode('utf-8'))

        sql = 'SELECT password FROM tb_userinfo WHERE username = ? LIMIT 1'
        pass_result = self.db_select(sql, [username])
        if not pass_result:
            logger.error('用户%s登陆失败！用户名错误！' % username)
            self.render('login.html', error = True)
            return

        if md.hexdigest() == pass_result[0]['password']:

            self.set_secure_cookie("cookie_user", username, expires_days = None)
            logger.info('用户%s登陆成功！' % username)

        else:
            logger.error('用户%s登陆失败！密码错误！' % username)
            self.render('login.html', error = True)
            return

        self.redirect("/")


class LogoutHandler(BaseHandler):
    '''
    设置注销方法
    '''

    @tornado.web.authenticated
    def get(self):
        sql = 'SELECT containers_id FROM tb_status WHERE containers_user = ? and containers_status = ?;'
        containers_list = self.db_select(sql, [self.current_user.decode(), 'runing'])

        if containers_list:
            logger.error('用户%s没有关闭所有的容器，无法退出登陆！' % self.current_user.decode())
            self.render('logout.html')
            return

        logger.info('用户%s退出登录！' % self.current_user.decode())
        self.clear_cookie("cookie_user")
        self.redirect("/")


class HomeHandler(BaseHandler):
    '''
    主页，搜索。
    '''
    @tornado.web.authenticated
    def get(self):
        self.render('search.html')
