# 基础镜像
FROM tempestann/uos:v2.0

# 暴露端口
EXPOSE 80 22 6379

# 启动所有服务的脚本
COPY startup.sh /usr/local/bin/start_services.sh
RUN chmod +x /usr/local/bin/start_services.sh

# 入口点设置为启动所有服务的脚本
ENTRYPOINT ["/usr/local/bin/start_services.sh"]
