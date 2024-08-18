import dataclasses


@dataclasses.dataclass
class Contents:
    BaseDockerfile: str = """\
FROM alpine:latest
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
RUN apk update && apk add bash iproute2 iptables
COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh
ENTRYPOINT ["/usr/local/bin/startup.sh"]
"""

    BaseStartupScript1: str = """#!/bin/bash
for f in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > "$f"; done
tail -f /dev/null
"""

    BaseStartupScript2: str = """#!/bin/bash
# 禁用反向路径过滤
for f in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > "$f"; done
# 获取主机的IP地址
HOST_IP=$(hostname -i)
# 将IP地址的最后一位替换为254
GATEWAY_IP=$(echo $HOST_IP | sed 's/\.[0-9]*$/.254/')
# 设置默认路由
ip route del default
ip route add default via $GATEWAY_IP

tail -f /dev/null
"""

    VulDockerfile1: str = """ # 基础镜像
FROM tempestann/uos:v1.1

# 复制启动脚本到容器内的 /usr/local/bin 目录
COPY startup.sh /usr/local/bin/start_services.sh

# 确保启动脚本具有执行权限
RUN chmod +x /usr/local/bin/start_services.sh

# 暴露端口
EXPOSE 8888 8080 8081 8082 8083

# 启动服务并保持容器运行
ENTRYPOINT ["/usr/local/bin/start_services.sh"]
"""

    StartupScript1: str = """#!/bin/bash
# 获取主机的IP地址
HOST_IP=$(hostname -i)
# 将IP地址的最后一位替换为254
GATEWAY_IP=$(echo $HOST_IP | sed 's/\.[0-9]*$/.254/')
# 设置默认路由
ip route del default
ip route add default via $GATEWAY_IP
# 启动 Apache
service apache2 start

# 启动 MySQL
service mysql start

# 启动 Tomcat
/opt/tomcat8/bin/startup.sh

# 启动 SSHD
/usr/local/sbin/sshd

# 保持容器运行
tail -f /dev/null
"""

    VulDockerfile2: str = """# 基础镜像
FROM tempestann/uos:v2.0

# 暴露端口
EXPOSE 80 22 6379

# 启动所有服务的脚本
COPY startup.sh /usr/local/bin/start_services.sh
RUN chmod +x /usr/local/bin/start_services.sh

# 入口点设置为启动所有服务的脚本
ENTRYPOINT ["/usr/local/bin/start_services.sh"]
"""

    StartupScript2: str = """#!/bin/bash
# 获取主机的IP地址
HOST_IP=$(hostname -i)
# 将IP地址的最后一位替换为254
GATEWAY_IP=$(echo $HOST_IP | sed 's/\.[0-9]*$/.254/')
# 设置默认路由
ip route del default
ip route add default via $GATEWAY_IP
# 启动 Redis
redis-server /tmp/redis-2.8.17/redis.conf &

# 启动 SSH
/usr/local/sbin/sshd -f /usr/local/etc/sshd_config &

# 启动 Nginx
/usr/local/nginx/sbin/nginx &

# 防止容器退出
tail -f /dev/null
"""

    VulDockerfile3: str = """# 基础镜像
FROM xinzp/tzb_pc:v1.0

# 暴露端口
EXPOSE 81 6379

# 复制启动脚本到容器内的 /usr/local/bin 目录
COPY startup.sh /usr/local/bin/start_services.sh

# 确保启动脚本具有执行权限
RUN chmod +x /usr/local/bin/start_services.sh

# 入口点设置为启动所有服务的脚本
ENTRYPOINT ["/usr/local/bin/start_services.sh"]"""

    StartupScript3: str = """#!/bin/bash
# 获取主机的IP地址
HOST_IP=$(hostname -i)
# 将IP地址的最后一位替换为254
GATEWAY_IP=$(echo $HOST_IP | sed 's/\.[0-9]*$/.254/')
# 设置默认路由
ip route del default
ip route add default via $GATEWAY_IP
# 启动 Nginx
service nginx start

# 启动 php7.3-fpm
service service php7.3-fpm start

# 启动 redis
/usr/local/bin/redis-server /etc/redis/redis.conf

# 保持容器运行
tail -f /dev/null"""

    VulDockerfile4: str = """# 基础镜像
FROM xinzp/tiaozhanbei:v1.2
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list 
RUN apt-get install -y iproute2 iptables

# 暴露端口
EXPOSE 80 81 873

# 复制启动脚本到容器内的 /usr/local/bin 目录
COPY startup.sh /usr/local/bin/start_services.sh

# 确保启动脚本具有执行权限
RUN chmod +x /usr/local/bin/start_services.sh

# 入口点设置为启动所有服务的脚本
ENTRYPOINT ["/usr/local/bin/start_services.sh"]"""

    StartupScript4: str = """#!/bin/bash
# 获取主机的IP地址
HOST_IP=$(hostname -i)
# 将IP地址的最后一位替换为254
GATEWAY_IP=$(echo $HOST_IP | sed 's/\.[0-9]*$/.254/')
# 设置默认路由
ip route del default
ip route add default via $GATEWAY_IP
# 启动 Apache
service apache2 start

# 启动 MySQL
service mysql start

# 启动 rsync
rsync --daemon

# 保持容器运行
tail -f /dev/null
"""

    VulDockerfile5: str = """FROM jezet/drl_web:v3

COPY ./startup.sh /usr/local/bin/startup.sh

RUN chmod +x /usr/local/bin/startup.sh

EXPOSE 8086
EXPOSE 8080
EXPOSE 6379

CMD ["/bin/bash", "-c", "/usr/local/bin/startup.sh && /bin/bash"]

"""

    StartupScript5: str = """# 获取主机的IP地址
HOST_IP=$(hostname -i)
# 将IP地址的最后一位替换为254
GATEWAY_IP=$(echo $HOST_IP | sed 's/\.[0-9]*$/.254/')
# 设置默认路由
ip route del default
ip route add default via $GATEWAY_IP
sudo supervisord -c /etc/supervisord.conf
sudo supervisorctl start httpd
sudo /usr/sbin/php-fpm -y /etc/php-fpm.d/www.conf
/redis-4.0.8/src/redis-server --daemonize yes
# 从本地主机连接Redis并禁用受保护模式
redis-cli <<EOF
CONFIG SET protected-mode no
CONFIG REWRITE
EOF

echo "Protected mode disabled."
cd /opt/spring-cli/spring-cli-standalone-0.10.0-SNAPSHOT-linux-x86_64/login-app/
./mvnw spring-boot:run &
sudo mysqld_safe

tail -f /dev/null
"""

    composeNetworks: str = """  {networkName}:\n    driver: bridge\n    ipam:\n      config:\n        - subnet: {subnet}\n"""

    composeRouters: str = """
  {routerDirname}:
    build: ./network/{routerDirname}
    sysctls:
      - net.ipv4.ip_forward=1
    container_name: {routerDirname}
    networks:
        {routerContents}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    composeSwitches: str = """
  {switchDirname}:
    build: ./network/{switchDirname}
    container_name: {switchDirname}
    networks:
      {network}:
        ipv4_address: {ip}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    composeHosts: str = """
  {hostDirname}:
    build: ./network/{hostDirname}
    container_name: {hostDirname}
    networks:
      {network}:
        ipv4_address: {ip}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    composeServicesFlag: str = """version: '3.8'\nservices:\n"""

    composeNetworksFlag: str = """\nnetworks:\n"""
