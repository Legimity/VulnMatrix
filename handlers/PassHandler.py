import tornado.web
from log.logger import logger
import hashlib
from handlers.BaseHandler import BaseHandler

class Change_Pass_Handler(BaseHandler):

    '''
    修改密码
    '''

    @tornado.web.authenticated
    def get(self):
        self.render('change_pass.html', error = '')

    @tornado.web.authenticated
    def post(self):
        logger.info('提交数据进行修改密码')
        old_password = self.get_argument("old_password", '')
        new_password = self.get_argument("new_password", '')
        if not old_password.strip() or not new_password.strip():
            logger.info('密码不能为空')
            self.render('change_pass.html', error = 1)
            return

        md = hashlib.md5()
        md.update(old_password.encode('utf-8'))
        sql = 'SELECT password FROM tb_userinfo WHERE username = ? LIMIT 1;'
        result = self.db_select(sql, [self.current_user.decode()])

        if md.hexdigest() == result[0]['password']:
            md = hashlib.md5()
            md.update(new_password.encode('utf-8'))
            sql = 'UPDATE tb_userinfo SET password = ? WHERE username = ?'
            result = self.db_update_insert(sql, [md.hexdigest(), self.current_user.decode()])
            if not result:
                logger.warning('数据库更新失败，密码更改失败')
                self.render('change_pass.html', error = 2)
                return
        else :
            logger.info('原来密码错误')
            self.render('change_pass.html', error = 3)
            return
        logger.info('密码修改成功！')
        self.render('change_pass.html', error = 0)


