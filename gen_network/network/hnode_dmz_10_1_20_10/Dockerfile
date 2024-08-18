 # 基础镜像
FROM tempestann/uos:v1.1

# 复制启动脚本到容器内的 /usr/local/bin 目录
COPY startup.sh /usr/local/bin/start_services.sh

# 确保启动脚本具有执行权限
RUN chmod +x /usr/local/bin/start_services.sh

# 暴露端口
EXPOSE 8888 8080 8081 8082 8083

# 启动服务并保持容器运行
ENTRYPOINT ["/usr/local/bin/start_services.sh"]
