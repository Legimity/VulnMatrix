#!/bin/bash
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
tail -f /dev/null