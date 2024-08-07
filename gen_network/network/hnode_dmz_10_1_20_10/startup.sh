#!/bin/bash

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
