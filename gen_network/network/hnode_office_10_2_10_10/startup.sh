#!/bin/bash

# 启动 Nginx
service nginx start

# 启动 php7.3-fpm
service service php7.3-fpm start

# 启动 redis
/usr/local/bin/redis-server /etc/redis/redis.conf

# 保持容器运行
tail -f /dev/null