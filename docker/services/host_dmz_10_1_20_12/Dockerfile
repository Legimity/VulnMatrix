FROM alpine:latest
RUN apk update && apk add bash iproute2 iptables
COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh
ENTRYPOINT ["/usr/local/bin/startup.sh"]
