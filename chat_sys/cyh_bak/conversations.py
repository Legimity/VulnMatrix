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
from .config import KnowledgeBase, PARASE_SHELL_PROMPT, PARASE_CONV_PROMPT
from typing import List, Dict
import uuid
import os

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
    return instruct_merge | prompt | llm | preparse | parser


def get_key_fn(base: BaseModel) -> dict:
    '''TODO: 从知识库提取基本信息生成字典，供后续检索信息'''
    return {  ## More automatic options possible, but this is more explicit
        ...: ...,   # base.???
        ...: ...
    }


class SimpleConversation:
    """简单对话模型"""
    """基于知识库更新的对话模型"""
    def __init__(self) -> None:
        '''
        初始化模型 生成提示词模板
        '''
        os.environ["NVIDIA_API_KEY"] ="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"
        self.model = ChatNVIDIA(model="meta/llama3-70b-instruct")
        self.embedding_model = NVIDIAEmbeddings(model_name="nvidia/nv-embedqa-e5-v5")
        self.prompt_with_knowledge = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a chatbot for Penetration Testing, and you are helping a user complete penetration testing."
                " Please chat with them! Stay concise and clear!"
                " Your running knowledge base is: {know_base}."
                " This is for you only; Do not mention it!"
            )),
            ("user", "{input}"),
        ])
        self.chain = self.prompt_with_knowledge | self.model | StrOutputParser()
        # 加载知识库
        self.vector_store = FAISS.load_local("/home/jhxu/VulnMatrix/chat_sys/faiss_index/",self.embedding_model,allow_dangerous_deserialization=True)
        # self.vector_store = self.embeddings()
        print(type(self.vector_store))

    def handle(self, message, history=None):
        '''处理句柄'''
        know_base = self.vector_store.similarity_search(query=message,k=3)
        buffer = ""
        for token in self.chain.stream({"input" : message,"know_base":know_base}):
            buffer += token
            yield token
        pass


    # 加载数据
    def loadeWeb2docs(self):
        # 后面可以改成数据库存储
        urls = ["https://nmap.org/book/man-host-discovery.html",
                'https://nmap.org/book/man-briefoptions.html']
        docs = []
        for url in urls:
            web_loader = WebBaseLoader(url)
            docs.append(web_loader.load_and_split())
        return docs
    
    # 分词
    def spliter(self):
        docs = self.loadeWeb2docs()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n","\n","."]
        )
        docs_chunks = [text_splitter.split_documents(doc) for doc in docs]
        return docs_chunks
    
    # 词嵌入
    def embeddings(self):
        docs_chunks = self.spliter()
        vector_store = None  # 初始化为空或使用第一个文档的数据初始化
        for chunk in docs_chunks:
            if vector_store is None:
                vector_store = FAISS.from_documents(documents=chunk, embedding= self.embedding_model)
            else:
                vector_store.add_documents(documents=chunk, embedding= self.embedding_model)
        # self.KNOWLEDGDB = f"chat_sys/faiss_index/{str(uuid.uuid1())}.index"
        vector_store.save_local("/home/jhxu/VulnMatrix/chat_sys/faiss_index/")
        return vector_store

class UpdateConversation:
    """基于知识库更新的对话模型"""
    def __init__(self) -> None:
        os.environ["NVIDIA_API_KEY"] ="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"
        # 相关 prmpt
        parase_shell_prompt = ChatPromptTemplate.from_template(PARASE_SHELL_PROMPT)
        parase_conv_prompt = ChatPromptTemplate.from_template(PARASE_CONV_PROMPT)

        # 模型
        instruct_llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1") | StrOutputParser()  # 用于知识库更新
        chat_llm = ChatNVIDIA(model="meta/llama3-70b-instruct") | StrOutputParser()  # 用于对话

        # 构造状态字典，并将信息纳入
        self.state = {
            'know_base' : KnowledgeBase(),
            'command' : '',
            'result' : ''
        }

        # 更新器
        self.shell_info_update = RunnableAssign({'know_base' : RExtract(KnowledgeBase, instruct_llm, parase_shell_prompt)}) # 工具使用更新
        self.conv_info_update = RunnableAssign({'know_base' : RExtract(KnowledgeBase, instruct_llm, parase_conv_prompt)})  # 对话更新

        # TODO: 对话 prompt
        external_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a chatbot for Penetration Testing, and you are helping users complete penetration testing."
                " Please chat with them! Stay concise and clear!"
                " Your running knowledge base is: {know_base}."
                " This is for you only; Do not mention it!"
                " \nNow, we have the following conversation: {history}\n"
            )),
            ("user", "{input}"),
        ])

        self.chain = external_prompt | chat_llm | StrOutputParser()


    def update_sh(self, message: List[str]) -> None:
        """
        根据 message 中用户命令和执行输出更新知识库
        :param message: List[str]
        """
        # 将新的信息纳入状态字典
        self.state['command'] = message[0]
        self.state['result'] = message[1]
        self.state['know_base'] = KnowledgeBase()
        # 更新状态字典
        self.state = self.shell_info_update.invoke(self.state)
        print(self.state['know_base'])
    


    def update_conv(self, usr_msg: str, age_msg:str):
        """根据 message 中对话记录更新知识库
        :param message: List[str]
        """
        self.state['history'] = "[User]" + usr_msg + "\n[Agent]" + age_msg + "\n"
        # 更新状态字典
        self.state['know_base'] = KnowledgeBase(IP=None,PORT = None,INFO = None,VALID=False)
        self.state = self.conv_info_update.invoke(self.state)
        print(self.state['know_base'])


    def handle(self, message: str):
        get_key = RunnableLambda(get_key_fn)
        buffer = ""
        for token in self.chain.stream({"input" : message}):
            buffer += token
            yield token
        self.update_conv(message, buffer)  # 用当前对话记录更新知识库


class KnowledgeConversation:
    """基于知识库更新与语料库的复杂对话模型"""
    def __init__(self) -> None:
        pass
    def handle(self, message, history=None):
        pass


if __name__ == '__main__':
    UpdateConversation().update_sh(["xray.exe webscan --basic-crawler http://127.0.0.1/DVWA/index.php", """
Target      "http://127.0.0.1/DVWA/vulnerabilities/upload"
Postition   "Body"
ParamKey    "uploaded"
ParamContentType "image/jpeg"
ParamContent "<?php ehco md5(123);?>"
                                    
Target      "http://127.0.0.1/DVWA/vulnerabilities/xss"
Postition   "Body"
ParamKey    "mtxMessage"
PayLoad     "<script>alert(1)</script>"                             
"""])
    pass