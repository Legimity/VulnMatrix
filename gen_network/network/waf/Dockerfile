FROM intel/tadk-waf
RUN apt update && apt install -y iproute2 iptables

COPY nginx.conf /usr/local/nginx/conf/nginx.conf

