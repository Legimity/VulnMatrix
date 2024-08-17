#!/bin/bash
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
