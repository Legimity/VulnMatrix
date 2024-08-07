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
