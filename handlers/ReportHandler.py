import os
import json
import tornado.web

from concurrent.futures import ThreadPoolExecutor
_ReportGenerator = ThreadPoolExecutor(max_workers=4)

class ReportHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            # 异步生成报告
            report_path = yield _ReportGenerator.submit(self.generate_report_stub)
            # 如果报告生成成功，返回下载链接
            if report_path:
                self.write(json.dumps({"success": True, "download_url": "/download_report?path=" + report_path}))
            else:
                self.write(json.dumps({"success": False, "error": "报告生成失败"}))
        except Exception as e:
            # 捕获生成报告过程中的异常并反馈给前端
            self.write(json.dumps({"success": False, "error": str(e)}))

    def generate_report_stub(self):
        """生成报告"""

        # 模拟生成报告过程
        import time
        time.sleep(10)  # 生成报告可能需要一些时间
        return "report.html"

        # 真正的生成报告的过程（待测试）
        # try:
        #     return _conversation.generateReport()
        # except Exception as e:
        #     return None

class DownloadHandler(tornado.web.RequestHandler):
    def get(self):
        report_path = self.get_argument("path")
        if os.path.exists(report_path):
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + os.path.basename(report_path))
            with open(report_path, 'rb') as f:
                while chunk := f.read(4096):
                    self.write(chunk)
            self.finish()
        else:
            self.set_status(404)
            self.write("报告不存在")