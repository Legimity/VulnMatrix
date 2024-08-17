#!/bin/bash
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
