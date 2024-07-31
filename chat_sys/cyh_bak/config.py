from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Union, Optional, List

# TODO: shell知识库更新 prompt
PARASE_SHELL_PROMPT = """
The user is using some command line tools to perform penetration testing.
Now the user executes a command and obtains the output corresponding to this command, and you are extracting useful information from it to record the process of its penetration testing for the user.
the command and the corresponding output results are as follows:

- command: `{command}`
- result:
```
{result}
```

The corresponding descriptions of command and result are as follows:
- `command`:
    - command指的是在命令行中执行的操作,比如`nmap -sV`
    - ls、cd、pwd、whoami这些常见的command不算渗透测试命令
    - 你不应该把command和result放在一起做为一个字符串,而是分开处理
- `result`:
    - 结果指的是命令执行后的输出,比如`nmap`扫描的结果
    - 如果结果中包含了`IP`、`端口`、`服务`、`vuln`、`exploit`、`payload`、`shell`、`PORT`等关键词,那么这个结果就是有效的渗透测试结果
    - 你需要思考`command`是不是渗透测试命令并且result的结果与渗透测试不相干,如果不相干请在VALID字段中填写`False`
    - 一个Reuslt中可能存在多个有效的信息,请你分点陈述,比如一个Result中可能存在多个IP地址和对应的端口和漏洞,你需要分开记录

Your output is an update to the original knowledge base to track the progress of users in conducting penetration tests.
old knowledge base is as follows:
```
{know_base}
```

{format_instructions}

Please output the json according to the commands executed by the user and the corresponding output results.
Follow the format instructions above to update
Follow the format precisely, including quotations and commas!! Follow the format precisely, including quotations and commas!!
Do not hallucinate any details, and make sure the knowledge base is not redundant.!! Do not hallucinate any details, and make sure the knowledge base is not redundant!!
Please do not add items to the schema yourself.
You can only add records or update the `INFO` content of records, you cannot delete records of the old knowledge base
You can only add records or update the `INFO` content of records, you cannot delete records of the old knowledge base
You can only add records or update the `INFO` content of records, you cannot delete records of the old knowledge base
"""

# TODO: 对话知识库更新 prompt
PARASE_CONV_PROMPT = "You are chatting with a user. The user just responded ('input'). Please update the knowledge base."\
    " Record your response in the 'response' tag to continue the conversation."\
    " Do not hallucinate any details, and make sure the knowledge base is not redundant."\
    " Update the entries frequently to adapt to the conversation flow."\
    "\n{format_instructions}"\
    "\n\nOLD KNOWLEDGE BASE: {know_base}"\
    "\n\nUSED COMMAND: {command}"\
    "\n\nGOT OUTPUT: {result}"



class KnowledgeBase(BaseModel):
    """Update based on old knowledge base according to command and result information."""
    # @pydantic.dataclasses.dataclass(config=Config)
    class InerRecord(BaseModel):
        """Penetration testing process record"""
        IP : object = Field(None, description="The target IP address of the record. If `command` and `result` are empty, please enter empty string (""). ")
        PORT: object = Field(None, description="The open port of the target IP address of the record. If `command` and `result` are empty, please enter empty string (""). ")
        INFO: object = Field(None, description="The valid output information of the executed command (information related to penetration testing) to this item. You need to pay special attention to keywords such as VULN, EXPLOIT, PAYLOAD, SHELL, PORT, etc.")

    RECORDS : List[InerRecord] = Field(
        [], description="The list of records which include the penetration testing process. A record in the list corresponds to an ip:port and records the process of penetration testing on this ip:port. "\
        "If the command currently executed by the user scans a new port or IP (As long as there is one difference between the two), you should append a new record which follows the schema of `InerRecord` rather than override an existing record "\
        "You can only add records or update the content of records' `INFO`, you cannot delete records of the old knowledge base",
    )

