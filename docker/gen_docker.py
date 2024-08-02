import os

# Define routers, switches, and hosts configurations
routers = [
    {"name": "dmz_router", "nets": ["dmz"], "ip": "10.1.20.254"},
    {"name": "office_router", "nets": ["office"], "ip": "10.2.10.254"},
    {"name": "dev_router", "nets": ["dev"], "ip": "10.20.2.254"},
]

switches = [
    {"name": "dmz_switch", "net": "dmz", "ip": "10.1.20.3"},
    {"name": "office_switch", "net": "office", "ip": "10.2.10.3"},
    {"name": "dev_switch", "net": "dev", "ip": "10.20.2.3"},
]

hosts = {
    "dmz": [
        {"name": "website", "ip": "10.1.20.10"},
        {"name": "dmz_db", "ip": "10.1.20.11"},
        {"name": "mail_server", "ip": "10.1.20.12"},
    ],
    "office": [
        {"name": "office_pc1", "ip": "10.2.10.10"},
        {"name": "office_pc2", "ip": "10.2.10.11"},
    ],
    "dev": [
        {"name": "code_repo", "ip": "10.20.2.10"},
        {"name": "dev_db", "ip": "10.20.2.11"},
        {"name": "test_machine", "ip": "10.20.2.12"},
    ],
}

networks = {
    "public": "203.0.113.0/24",
    "dmz": "10.1.20.0/24",
    "office": "10.2.10.0/24",
    "dev": "10.20.2.0/24",
}

# Function to convert IP to a valid directory name
def ip_to_dirname(ip):
    return ip.replace('.', '_')

# Create necessary directories
def create_directories():
    if not os.path.exists('services'):
        os.mkdir('services')
    for router in routers:
        dirname = f'router_{router["nets"][0]}_{ip_to_dirname(router["ip"])}'
        if not os.path.exists(f'services/{dirname}'):
            os.makedirs(f'services/{dirname}')
    for switch in switches:
        dirname = f'switch_{switch["net"]}_{ip_to_dirname(switch["ip"])}'
        if not os.path.exists(f'services/{dirname}'):
            os.makedirs(f'services/{dirname}')
    for subnet in hosts:
        for host in hosts[subnet]:
            dirname = f'host_{subnet}_{ip_to_dirname(host["ip"])}'
            if not os.path.exists(f'services/{dirname}'):
                os.makedirs(f'services/{dirname}')

# Create Dockerfile
def create_dockerfile(service_type, network, ip):
    dirname = f'{service_type}_{network}_{ip_to_dirname(ip)}'
    dockerfile_content = """\
FROM alpine:latest
RUN apk update && apk add bash iproute2 iptables
COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh
ENTRYPOINT ["/usr/local/bin/startup.sh"]
"""
    with open(f'services/{dirname}/Dockerfile', 'w') as f:
        f.write(dockerfile_content)

# Create startup script
def create_startup_script(service_type, network, ip, commands=None):
    dirname = f'{service_type}_{network}_{ip_to_dirname(ip)}'
    iptables_rules = "\n".join(commands) if commands else ""
    startup_script_content = f"""\
#!/bin/bash
sysctl -w net.ipv4.ip_forward=1
for f in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > "$f"; done
{iptables_rules}
tail -f /dev/null
"""
    with open(f'services/{dirname}/startup.sh', 'w') as f:
        f.write(startup_script_content)

# Create docker-compose.yml file
def create_docker_compose():
    services = ""
    networks_str = ""

    for net_name, net_subnet in networks.items():
        networks_str += f"  {net_name}:\n    driver: bridge\n    ipam:\n      config:\n        - subnet: {net_subnet}\n"

    for switch in switches:
        dirname = f'switch_{switch["net"]}_{ip_to_dirname(switch["ip"])}'
        services += f"""
  {dirname}:
    build: ./services/{dirname}
    container_name: {dirname}
    networks:
      {switch['net']}:
        ipv4_address: {switch['ip']}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    for subnet, hosts_in_subnet in hosts.items():
        for host in hosts_in_subnet:
            dirname = f'host_{subnet}_{ip_to_dirname(host["ip"])}'
            services += f"""
  {dirname}:
    build: ./services/{dirname}
    container_name: {dirname}
    networks:
      {subnet}:
        ipv4_address: {host['ip']}
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    for router in routers:
        dirname = f'router_{router["nets"][0]}_{ip_to_dirname(router["ip"])}'
        services += f"""
  {dirname}:
    build: ./services/{dirname}
    container_name: {dirname}
    networks:
"""
        for net in router["nets"]:
            services += f"      {net}:\n"
        services += """
    privileged: true
    security_opt:
      - seccomp:unconfined
"""

    compose_content = f"""\
version: '3.8'
services:
{services}
networks:
{networks_str}
"""
    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)

# Create all files and directories
create_directories()
for switch in switches:
    create_dockerfile("switch", switch["net"], switch["ip"])
    create_startup_script("switch", switch["net"], switch["ip"])
for subnet in hosts:
    for host in hosts[subnet]:
        create_dockerfile("host", subnet, host["ip"])
        create_startup_script("host", subnet, host["ip"])
for router in routers:
    create_dockerfile("router", router["nets"][0], router["ip"])
    create_startup_script("router", router["nets"][0], router["ip"])
create_docker_compose()