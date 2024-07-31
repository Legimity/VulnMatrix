from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.schema.runnable.passthrough import RunnableAssign
from langchain.schema.runnable import RunnableLambda

from langchain.pydantic_v1 import BaseModel
from langchain_community.vectorstores import FAISS
from faiss import  write_index, read_index
from operator import itemgetter

import os
import sys
import threading
from rich.console import Console
from rich.style import Style
from rich.theme import Theme
from rich.markdown import Markdown

from typing import List, Dict
from functools import partial
import uuid
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .config import (
        KnowledgeBase_conv,
        KnowledgeBase_shell,
        Report,
        PARASE_SHELL_PROMPT, PARASE_CONV_PROMPT, CMD_RECORD_PATH, GEN_REPORT_PROMPT
    )
except ImportError:
    from config import (
        KnowledgeBase_conv,
        KnowledgeBase_shell,
        Report,
        PARASE_SHELL_PROMPT, PARASE_CONV_PROMPT, CMD_RECORD_PATH, GEN_REPORT_PROMPT
    )

try:
    from Queue import Queue
except ImportError as e:
    from queue import Queue

from log.logger import logger


base_style = Style(color="#76B900", bold=True)
item_style = Style(color="blue", underline="", bold=True)

def PPrint(preface="State: ", mode = 0):
    """用于chain调试"""
    def print_and_return(x, preface=""):
        with open(CMD_RECORD_PATH, "a") as f:
            console = Console(file=f)
            # 打印项目标题
            #console.rule(f">{preface}", characters="-", style="blue underline", align='left')
            console.print(Markdown(preface))
            # 打印项目内容
            _pprint = partial(console.print, style=base_style)
            if mode == 1:
                try:
                    _pprint(x.messages[0].content, "\n")  # 输出提示词
                except:
                    f.write(x.messages[0].content + "\n")
            else:
                try:
                    _pprint(x, "\n")
                except:
                    f.write(x + "\n")
        return x

    if mode == 2:
        return RunnableLambda(partial(print_and_return, preface=preface)) | StrOutputParser()
    else:
        return RunnableLambda(partial(print_and_return, preface=preface))


def RExtract(pydantic_class, llm, prompt):
    '''构造信息提取的 chain
    [Args]
    pydantic_class : 知识库模版类
    llm            : 模型
    prompt         : 提示
    '''
    parser = PydanticOutputParser(pydantic_object=pydantic_class)
    instruct_merge = RunnableAssign({'format_instructions' : lambda x: parser.get_format_instructions()})
    def preparse(string):
        if '{' not in string: string = '{' + string
        if '}' not in string: string = string + '}'
        string = (string
            .replace("\\_", "_")
            .replace("\n", " ")
            .replace("\]", "]")
            .replace("\[", "[")
        )
        # print(string)  ## Good for diagnostics
        return string

    return instruct_merge | prompt \
        | PPrint("## 更新数据库所使用的prompt", mode=1) \
        | llm \
        | PPrint("## 模型的输出", mode=2) \
        | preparse | parser \
        | PPrint("## 知识库更新结果")
    # return instruct_merge | prompt | llm | preparse | parser


def get_key_fn(base: BaseModel) -> dict:
    '''TODO: 从知识库提取基本信息生成字典，供后续检索信息'''
    return {  ## More automatic options possible, but this is more explicit
        ...: ...,   # base.???
        ...: ...
    }


class KnowbaseConversation:
    """基于知识库更新与 RAG 的对话模型"""
    _instance = None
    task_queue = Queue()   # 任务队列

    def __init__(self) -> None:

        # 语料来源
        self.urls =[
            "https://nmap.org/book/man-host-discovery.html",
            'https://nmap.org/book/man-briefoptions.html'
        ]

        # 相关 prmpt
        parase_shell_prompt = ChatPromptTemplate.from_template(PARASE_SHELL_PROMPT)
        parase_conv_prompt = ChatPromptTemplate.from_template(PARASE_CONV_PROMPT)
        gen_report_prompt = ChatPromptTemplate.from_template(GEN_REPORT_PROMPT)    # 根据知识库生成格式化报告

        # 模型
        instruct_llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1") | StrOutputParser()  # 用于知识库更新等
        chat_llm = ChatNVIDIA(model="meta/llama3-70b-instruct") | StrOutputParser()  # 用于对话
        embedding_model = NVIDIAEmbeddings(model_name="nvidia/nv-embedqa-e5-v5")   # 嵌入模型

        # 构造状态字典，并将信息纳入
        self.state = {
            'know_base' : KnowledgeBase_shell(IP=None,PORT = None,INFO = None,VALID=False),
            'command' : '',
            'result' : '',
            'input': ''
        }

        # 知识库更新器
        self.shell_info_update = RunnableAssign({'know_base' : RExtract(KnowledgeBase_shell, instruct_llm, parase_shell_prompt)}) # 基于工具使用更新
        self.conv_info_update = RunnableAssign({'know_base' : RExtract(KnowledgeBase_conv, instruct_llm, parase_conv_prompt)})  # 基于对话更新知识库

        # 对话 prompt
        external_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a chatbot for Penetration Testing, and you are helping users complete penetration testing."
                " Please chat with them! Stay concise and clear!"
                " This is for you only; Do not mention it!"
                " \nUsing that, we retrieved the following: {context}\n"
                "请用中文回答我，请用中文回答我，请用中文回答我"
            )),
            ("user", "{input}"),
        ])

        # 对话 chain
        self.chain = external_prompt | chat_llm

        # TODO: 报告生成 chain
        self.report_chain = RExtract(Report, instruct_llm, gen_report_prompt)

        # 加载语料库
        self.vector_store = FAISS.load_local(os.path.dirname(os.path.abspath(__file__)) + "/faiss_index/",embedding_model,allow_dangerous_deserialization=True)
        # self.vector_store = self.embeddings(embedding_model)   # 嵌入
        # print(type(self.vector_store))


    @classmethod
    def get_instance(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = KnowbaseConversation()
        return cls._instance


    def update_sh(self, message: List[str]) -> None:
        """
        根据 message 中用户命令和执行输出更新知识库
        :param message: List[str]
        """
        # 将新的信息纳入状态字典
        self.state['command'] = message[0]
        self.state['result'] = message[1]
        #self.state['know_base'] = KnowledgeBase(IP=None,PORT = None,INFO = None,VALID=False)
        try:
            self.state['know_base'] = self.state['know_base'].json()  # 转换成 json 格式
        except AttributeError:
            pass

        # 记录命令、输出、更新前的知识库状态
        with open(CMD_RECORD_PATH, "a") as f:
            console = Console(file=f)
            console.rule(f"SHELL I/O Updating {datetime.now()}")
            #f.write(f"command: {self.state['command']}\n")
            #f.write(f"result: {self.state['result']}\n")
            console.print(f"know_base: {self.state['know_base']}", style=base_style)
            console.print(f"state dict: {self.state}")

        try:
            self.state = self.shell_info_update.invoke(self.state)
        except Exception as e:
            logger.error(f"知识库更新失败<shell> {e}")


    def update_conv(self, message:str):
        """根据 message 中对话记录更新知识库
        :param message: List[str]
        """
        #self.state['history'] = "[User]" + usr_msg + "\n[Agent]" + age_msg + "\n"
        self.state['input'] = message

        # 记录用户信息、更新前的知识库状态
        with open(CMD_RECORD_PATH, "a") as f:
            console = Console(file=f)
            console.rule(f"Dialog Updating {datetime.now()}")
            #f.write(f"message: {self.state['input']}")
            console.print(f"state dict: {self.state}")
            console.print(f"know_base: {self.state['know_base']}", style=base_style)

        # 更新状态字典
        try:
            self.state = self.conv_info_update.invoke(self.state)
        except Exception as e:
            logger.error(f"知识库更新失败<对话> {e}")

    def loadeWeb2docs(self):
        """加载数据"""
        # 后面可以改成数据库存储
        docs = []
        for url in self.urls:
            web_loader = WebBaseLoader(url)
            docs.append(web_loader.load_and_split())
        return docs


    def spliter(self):
        """分词"""
        docs = self.loadeWeb2docs()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n","\n","."]
        )
        docs_chunks = [text_splitter.split_documents(doc) for doc in docs]
        return docs_chunks


    def embeddings(self, embedding_model):
        """词嵌入"""
        docs_chunks = self.spliter()
        vector_store = None  # 初始化为空或使用第一个文档的数据初始化
        for chunk in docs_chunks:
            if vector_store is None:
                vector_store = FAISS.from_documents(documents=chunk, embedding= embedding_model)
            else:
                vector_store.add_documents(documents=chunk, embedding= embedding_model)
        # self.KNOWLEDGDB = f"chat_sys/faiss_index/{str(uuid.uuid1())}.index"
        vector_store.save_local(os.path.dirname(os.path.abspath(__file__)) + "/faiss_index/")
        return vector_store


    def handle(self, message: str, history=None):
        """生成当前轮回复"""
        #get_key = RunnableLambda(get_key_fn)
        buffer = ""
        self.state['input'] = message
        self.state['context'] = self.vector_store.similarity_search(query=message,k=3)   # 相似性检索获取语料上下文
        init = True
        for token in self.chain.stream(self.state):
            # 初始状态下添加前导语
            if init:
                token = "[已为您更新知识库]\n\n" + token
                init = False
            buffer += token
            # print(token)
            yield token

    def generateReport(self):
        """生成报告"""
        # 报告保存路径
        from datetime import datetime
        current_time = datetime.now()
        report_path = f"./report_{current_time.strftime('%Y%m%d%H%M%S')}.html"

        # 提取知识库（ json 形式 ）
        try:
            know_base = self.state['know_base'].json()
        except:
            know_base = self.state['know_base']

        # 生成结构化信息
        report_json = self.report_chain.invoke({ 'know_base': know_base }).json()

        # 传入结构化信息并填充 html 报告模版
        from report import json2html
        report_html = json2html(report_json)

        # 保存报告
        with open(report_path, "w") as f:
            f.write(report_html)
        return report_path


if __name__ == '__main__':
    records = [
        #['',''],
        #['ls', 'bin   dev  home  media  opt   root  sbin  sys  usr\r\nboot  etc  lib   mnt    proc  run   srv   tmp  var'],
        ["xray.exe webscan --basic-crawler http://127.0.0.1/DVWA/index.php", """
Target      "http://127.0.0.1/DVWA/vulnerabilities/upload"
Postition   "Body"
ParamKey    "uploaded"
ParamContentType "image/jpeg"
ParamContent "<?php ehco md5(123);?>"
                                    
Target      "http://127.0.0.1/DVWA/vulnerabilities/xss"
Postition   "Body"
ParamKey    "mtxMessage"
PayLoad     "<script>alert(1)</script>"
"""],
        ['pwd', '/'],
        ['cd bin', ''],
        ['python3 vulmap.py -u http://127.0.0.1:8161/', """[*] ---------------- Running Vulmap ----------------
[14:30:11] [INFO] Start scanning target: http://127.0.0.1:8161/
[14:30:15] [INFO] Unable to identify target, Run all pocs                
[14:30:16] [?] The target maybe Apache AcitveMQ: CVE-2015-5254 [maybe] [version: 5.11.1] [version check]  
[14:30:16] [ERROR] /Users/yqc/Documents/Project/GAME/挑战杯/Vul-scan-gpt/webScan/lib/vulmap/module/output.py 26
[14:30:16] [+] The target is Apache AcitveMQ: CVE-2016-3088 [upload: http://127.0.0.1:8161/api/9206343fde9b.jsp ] [admin:admin]
[14:30:16] [ERROR] /Users/yqc/Documents/Project/GAME/挑战杯/Vul-scan-gpt/webScan/lib/vulmap/module/output.py 26
[14:30:32] [INFO] Scan completed and ended """]
    ]
    # records = [
    #     ['pwd', '/'],
    #     ['cd bin', ''],
    # ]

    conv = KnowbaseConversation()

    for record in records:
        conv.update_sh(record)
    pass