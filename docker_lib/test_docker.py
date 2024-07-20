import docker
client=docker.from_env()
images=client.images.list()
print(images)
# 返回一个包含所有镜像的列表

