#!/bin/bash
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
