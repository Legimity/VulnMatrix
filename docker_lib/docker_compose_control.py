#! coding=utf-8
# 初始化docker模块，直接提供三个控制借口，可以直接操作docker镜像和容器。
# import docker

# from log.logger import logger
# from docker_lib.docker_add import Dokcers_Add
# from docker_lib.docker_del import Dokcers_Del
# from docker_lib.docker_get import Dokcers_Get

# try:
#     client = docker.from_env()
#     client.images.list()
#     logger.info('连接到Docker进程。')
# except Exception as e :
#     logger.warning('连接本地Docker进程失败，可能是Docker进程未开启！')
#     exit()

# Dockers_Start = Dokcers_Add(client)
# Dockers_Stop = Dokcers_Del(client)
# Dockers_Info = Dokcers_Get(client)

#  my test code
# 
# 
# 
# 
import docker
import yaml
from docker.errors import ImageNotFound, NotFound, APIError
from dotenv import load_dotenv
# import os

# Load environment variables from .env file
load_dotenv()

def load_compose_file(file_path):
    with open(file_path, 'r') as file:
        compose_content = yaml.safe_load(file)
    return compose_content

def get_or_pull_image(client, image_name):
    try:
        client.images.get(image_name)
        print(f"Image {image_name} already exists locally.")
    except ImageNotFound:
        print(f"Image {image_name} not found locally. Pulling from Docker Hub...")
        client.images.pull(image_name)
        print(f"Image {image_name} pulled successfully.")

def disconnect_all_containers_from_network(client, network_name):
    try:
        network = client.networks.get(network_name)
        for container_id in network.attrs['Containers']:
            container = client.containers.get(container_id)
            network.disconnect(container, force=True)
            print(f"Disconnected container {container.name} from network {network.name}.")
    except NotFound:
        pass

def remove_existing_network(client, network_name):
    disconnect_all_containers_from_network(client, network_name)
    try:
        network = client.networks.get(network_name)
        print(f"Removing existing network {network_name} with ID {network.id}...")
        network.remove()
    except NotFound:
        pass
    except APIError as e:
        print(f"Error removing network {network_name}: {e}")

def create_networks(client, networks):
    created_networks = {}
    for network_name, network_details in networks.items():
        remove_existing_network(client, network_name)
        ipam_config = network_details.get('ipam', {}).get('config', [])
        ipam_pool = docker.types.IPAMConfig(pool_configs=[
            docker.types.IPAMPool(
                subnet=config.get('subnet'),
                iprange=config.get('ip_range')
            ) for config in ipam_config
        ])
        network = client.networks.create(
            network_name,
            driver=network_details.get('driver', 'bridge'),
            ipam=ipam_pool
        )
        created_networks[network_name] = network
        print(f"Network {network_name} created with ID {network.id}.")
    return created_networks

def convert_ports(ports):
    port_bindings = {}
    for port in ports:
        host_port, container_port = port.split(":")
        port_bindings[container_port + "/tcp"] = int(host_port)
    return port_bindings

def convert_expose_ports(expose):
    exposed_ports = {}
    for port in expose:
        exposed_ports[port + "/tcp"] = {}
    return exposed_ports

def remove_existing_endpoint(network, container_name):
    try:
        network.disconnect(container_name, force=True)
        print(f"Removed existing endpoint {container_name} from network {network.name}.")
    except NotFound:
        pass
    except APIError as e:
        print(f"Error removing endpoint {container_name} from network {network.name}: {e}")

def create_network_and_containers(compose_content):
    client = docker.from_env()

    networks = compose_content.get('networks', {})
    created_networks = create_networks(client, networks)

    services = compose_content.get('services', {})
    containers = []

    for service_name, service in services.items():
        image_name = service['image']
        container_name = service.get('container_name', service_name)
        get_or_pull_image(client, image_name)

        # Remove existing container if it exists
        try:
            existing_container = client.containers.get(container_name)
            print(f"Removing existing container {existing_container.name} with ID {existing_container.id}...")
            existing_container.stop()
            existing_container.remove()
        except NotFound:
            pass

        # Network aliases and connections
        network_aliases = service.get('networks', {})
        network_mode = None
        if network_aliases:
            network_mode = list(network_aliases.keys())[0]

        # Convert ports format
        ports = service.get('ports', [])
        port_bindings = convert_ports(ports)

        # Create and start container
        try:
            container = client.containers.run(
                image_name,
                name=container_name,
                detach=True,
                network_mode=network_mode,
                ports=port_bindings,
                environment=service.get('environment', {}),
                volumes=service.get('volumes', {}),
                restart_policy={"Name": service.get('restart', 'no')}
            )
            print(f"Container {container_name} started with ID {container.id}.")

            # Connect the container to additional networks if specified
            for net_name, net_details in network_aliases.items():
                if net_name in created_networks:
                    remove_existing_endpoint(created_networks[net_name], container_name)
                    created_networks[net_name].connect(container, ipv4_address=net_details.get('ipv4_address'), aliases=[service_name])
                    print(f"Container {container_name} connected to network {net_name} with IP {net_details.get('ipv4_address')}.")

            containers.append(container)
        except APIError as e:
            print(f"Error starting container {container_name}: {e}")

    return {
        "network_names": list(created_networks.keys()),
        "containers": [container.name for container in containers],
        "network_ids": [network.id for network in created_networks.values()]
    }

def stop_and_remove_containers_and_networks(network_ids):
    client = docker.from_env()
    try:
        for network_id in network_ids:
            network = client.networks.get(network_id)
            containers = network.attrs['Containers']

            for container_id in containers.keys():
                container = client.containers.get(container_id)
                print(f"Stopping container {container.name} with ID {container.id}...")
                container.stop()
                print(f"Removing container {container.name} with ID {container.id}...")
                container.remove()

            print(f"Removing network with ID {network_id}...")
            network.remove()
            print("Network removed successfully.")

    except NotFound:
        print(f"Network with ID {network_id} not found.")
    except APIError as e:
        print(f"Error: {e}")

def check_container_status(container_names):
    client = docker.from_env()
    for container_name in container_names:
        try:
            container = client.containers.get(container_name)
            print(f"Container {container.name} status: {container.status}")
        except NotFound:
            print(f"Container {container_name} not found.")

def main(file_path):
    compose_content = load_compose_file(file_path)
    network_info = create_network_and_containers(compose_content)
    print("-------------------------------")
    check_container_status(network_info['containers'])
    return network_info

if __name__ == "__main__":
    file_path = "docker-compose.yml"  # Replace with your actual docker-compose.yml file path
    network_info = main(file_path)
    print(f"Network Names: {', '.join(network_info['network_names'])}")
    print(f"Containers: {', '.join(network_info['containers'])}")
    print(f"Network IDs: {', '.join(network_info['network_ids'])}")

    # Uncomment the following line to stop and remove the networks and their containers
    # stop_and_remove_containers_and_networks(network_info['network_ids'])
