import json
from jinja2 import Environment, FileSystemLoader


def json2html(info):
    """TODO:"""
    # 加载模板
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('./template/pentest_report.html')

    # 解析json数据
    data = json.loads(info)

    # 渲染模板
    output = template.render(data)

    return output