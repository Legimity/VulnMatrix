import os
import sys

def generate_reg_file(path):
    # 确保路径以 .exe 结尾
    if not path.lower().endswith('.exe'):
        print("Provided path does not point to an .exe file.")
        return
    # 从完整路径中提取文件名
    filename = os.path.basename(path)
    # 创建自定义协议名称
    protocol_name = f"CallBSEXE{filename}".split('.')[0]
    protocol_name = protocol_name.split(" ")[0]
    path = path.replace("\\", "\\\\")

    # 构建注册表文件内容
    reg_content = f"""Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\\{protocol_name}]
@="URL: {protocol_name} Protocol Handler"
"URL Protocol"=""

;E:\\localExe\\gy_print.exe 为本地EXE路径
[HKEY_CLASSES_ROOT\\{protocol_name}\\DefaultIcon]
@="{path}"

[HKEY_CLASSES_ROOT\\{protocol_name}\\Shell]

[HKEY_CLASSES_ROOT\\{protocol_name}\\Shell\\Open]

[HKEY_CLASSES_ROOT\\{protocol_name}\\Shell\\Open\\Command]
@="\\"{path}\\" %1"
"""
    # 写入到注册表文件
    with open(f"tmp/{protocol_name}.reg", "w",encoding="utf-8") as reg_file:
        reg_file.write(reg_content)
    return protocol_name,f"tmp/{protocol_name}.reg"

# if __name__ == "__main__":
#     generate_reg_file(r"C:\tool\010Editor\010 Editor 12.0.1.exe")