#!/bin/bash

# 启动 Redis
redis-server /tmp/redis-2.8.17/redis.conf &

# 启动 SSH
/usr/local/sbin/sshd -f /usr/local/etc/sshd_config &

# 启动 Nginx
/usr/local/nginx/sbin/nginx &

# 防止容器退出
tail -f /dev/null
