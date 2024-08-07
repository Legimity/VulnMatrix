# 基础镜像
FROM xinzp/tzb_pc:v1.0

# 暴露端口
EXPOSE 81 6379

# 复制启动脚本到容器内的 /usr/local/bin 目录
COPY startup.sh /usr/local/bin/start_services.sh

# 确保启动脚本具有执行权限
RUN chmod +x /usr/local/bin/start_services.sh

# 入口点设置为启动所有服务的脚本
ENTRYPOINT ["/usr/local/bin/start_services.sh"]