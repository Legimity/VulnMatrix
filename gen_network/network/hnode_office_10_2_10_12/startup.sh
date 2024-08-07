#!/bin/bash

# 启动 Apache
service apache2 start

# 启动 MySQL
service mysql start

# 启动 rsync
 rsync --daemon

# 保持容器运行
tail -f /dev/null
