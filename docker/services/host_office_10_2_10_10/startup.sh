#!/bin/bash
sysctl -w net.ipv4.ip_forward=1
for f in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > "$f"; done

tail -f /dev/null
