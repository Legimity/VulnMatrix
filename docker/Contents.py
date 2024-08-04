import dataclasses


@dataclasses.dataclass
class Contents:
    BaseDockerfile: str = """\
FROM alpine:latest
RUN apk update && apk add bash iproute2 iptables
COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh
ENTRYPOINT ["/usr/local/bin/startup.sh"]
"""

    StartupScript: str = f"""\
#!/bin/bash
sysctl -w net.ipv4.ip_forward=1
for f in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > "$f"; done
tail -f /dev/null
"""

    composeNetworks: str = """  {networkName}:\n    driver: bridge\n    ipam:\n      config:\n        - subnet: {subnet}\n"""

    composeRouters: str = """
  {routerDirname}:
    build: ./network/{routerDirname}
    container_name: {routerDirname}
    networks:
        {routerContents}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    composeSwitches: str = """
  {switchDirname}:
    build: ./network/{switchDirname}
    container_name: {switchDirname}
    networks:
      {network}:
        ipv4_address: {ip}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    composeHosts: str = """
  {hostDirname}:
    build: ./network/{hostDirname}
    container_name: {hostDirname}
    networks:
      {network}:
        ipv4_address: {ip}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    composeServicesFlag: str = """version: '3.8'\nservices:\n"""

    composeNetworksFlag: str = """\nnetworks:\n"""
