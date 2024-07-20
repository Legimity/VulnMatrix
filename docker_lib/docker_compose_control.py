import docker
import yaml
from docker.errors import ImageNotFound, NotFound, APIError
from dotenv import load_dotenv
import logging
import os
# Load environment variables from .env file
load_dotenv()
# from . import logger

class DockerComposeControl:
    # def __init__(self):
    #     self.client = docker.from_env()
    #     self.logger = logging.getLogger(__name__)
    #     logging.basicConfig(level=logging.INFO)
    def __init__(self, client):
        super(DockerComposeControl, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.client = client


    def load_compose_file(self, file_path):
        with open(file_path, 'r') as file:
            compose_content = yaml.safe_load(file)
        return compose_content

    def get_or_pull_image(self, image_name):
        try:
            self.client.images.get(image_name)
            self.logger.info(f"Image {image_name} already exists locally.")
        except ImageNotFound:
            self.logger.info(f"Image {image_name} not found locally. Pulling from Docker Hub...")
            self.client.images.pull(image_name)
            self.logger.info(f"Image {image_name} pulled successfully.")

    def disconnect_all_containers_from_network(self, network_name):
        try:
            network = self.client.networks.get(network_name)
            for container_id in network.attrs['Containers']:
                container = self.client.containers.get(container_id)
                network.disconnect(container, force=True)
                self.logger.info(f"Disconnected container {container.name} from network {network.name}.")
        except NotFound:
            pass

    def remove_existing_network(self, network_name):
        self.disconnect_all_containers_from_network(network_name)
        try:
            network = self.client.networks.get(network_name)
            self.logger.info(f"Removing existing network {network_name} with ID {network.id}...")
            network.remove()
        except NotFound:
            pass
        except APIError as e:
            self.logger.error(f"Error removing network {network_name}: {e}")
    

    def create_networks(self, networks):
        created_networks = {}
        for network_name, network_details in networks.items():
            self.remove_existing_network(network_name)
            ipam_config = network_details.get('ipam', {}).get('config', [])
            ipam_pool = docker.types.IPAMConfig(pool_configs=[
                docker.types.IPAMPool(
                    subnet=config.get('subnet'),
                    iprange=config.get('ip_range')
                ) for config in ipam_config
            ])
            network = self.client.networks.create(
                network_name,
                driver=network_details.get('driver', 'bridge'),
                ipam=ipam_pool
            )
            created_networks[network_name] = network
            self.logger.info(f"Network {network_name} created with ID {network.id}.")
        return created_networks

    def convert_ports(self, ports):
        port_bindings = {}
        for port in ports:
            host_port, container_port = port.split(":")
            port_bindings[container_port + "/tcp"] = int(host_port)
        return port_bindings
    

    def resolve_volumes(self, volumes):
        resolved_volumes = {}
        for volume in volumes:
            host_path, container_path = volume.split(":")
            resolved_host_path = os.path.expandvars(host_path)
            resolved_volumes[resolved_host_path] = {'bind': container_path, 'mode': 'rw'}
        return resolved_volumes
    

    def remove_existing_endpoint(self, network, container_name):
        try:
            network.disconnect(container_name, force=True)
            self.logger.info(f"Removed existing endpoint {container_name} from network {network.name}.")
        except NotFound:
            pass
        except APIError as e:
            self.logger.error(f"Error removing endpoint {container_name} from network {network.name}: {e}")

    def create_network_and_containers(self, compose_content):
        networks = compose_content.get('networks', {})
        created_networks = self.create_networks(networks)

        services = compose_content.get('services', {})
        containers = []

        for service_name, service in services.items():
            image_name = service['image']
            container_name = service.get('container_name', service_name)
            self.get_or_pull_image(image_name)

            # Remove existing container if it exists
            try:
                existing_container = self.client.containers.get(container_name)
                self.logger.info(f"Removing existing container {existing_container.name} with ID {existing_container.id}...")
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
            port_bindings = self.convert_ports(ports)

             # Resolve volumes
            volumes = service.get('volumes', [])
            resolved_volumes = self.resolve_volumes(volumes)

            # Create and start container
            try:
                container = self.client.containers.run(
                    image_name,
                    name=container_name,
                    detach=True,
                    network_mode=network_mode,
                    ports=port_bindings,
                    environment=service.get('environment', {}),
                    # volumes=service.get('volumes', {}),
                    volumes=resolved_volumes,
                    restart_policy={"Name": service.get('restart', 'no')}
                )
                self.logger.info(f"Container {container_name} started with ID {container.id}.")

                # Connect the container to additional networks if specified
                for net_name, net_details in network_aliases.items():
                    if net_name in created_networks:
                        self.remove_existing_endpoint(created_networks[net_name], container_name)
                        created_networks[net_name].connect(container, ipv4_address=net_details.get('ipv4_address'), aliases=[service_name])
                        self.logger.info(f"Container {container_name} connected to network {net_name} with IP {net_details.get('ipv4_address')}.")

                containers.append(container)
            except APIError as e:
                self.logger.error(f"Error starting container {container_name}: {e}")

        return {
            "network_names": list(created_networks.keys()),
            "containers": [container.name for container in containers],
            "network_ids": [network.id for network in created_networks.values()]
    }

    def stop_and_remove_containers_and_networks(self, network_ids):
        try:
            for network_id in network_ids:
                network = self.client.networks.get(network_id)
                containers = network.attrs['Containers']

                for container_id in containers.keys():
                    container = self.client.containers.get(container_id)
                    self.logger.info(f"Stopping container {container.name} with ID {container.id}...")
                    container.stop()
                    self.logger.info(f"Removing container {container.name} with ID {container.id}...")
                    container.remove()

                self.logger.info(f"Removing network with ID {network_id}...")
                network.remove()
                self.logger.info("Network removed successfully.")
        except NotFound:
            self.logger.error(f"Network with ID {network_id} not found.")
        except APIError as e:
            self.logger.error(f"Error: {e}")

    def check_container_status(self, container_names):
        for container_name in container_names:
            try:
                container = self.client.containers.get(container_name)
                self.logger.info(f"Container {container.name} status: {container.status}")
            except NotFound:
                self.logger.error(f"Container {container_name} not found.")

    def run(self, file_path):
        compose_content = self.load_compose_file(file_path)
        network_info = self.create_network_and_containers(compose_content)
        self.logger.info("-------------------------------")
        self.check_container_status(network_info['containers'])
        return network_info

if __name__ == "__main__":
    file_path = "docker-compose.yml" 
    dcc = DockerComposeControl()
    network_info = dcc.run(file_path)
    print(f"Network Names: {', '.join(network_info['network_names'])}")
    print(f"Containers: {', '.join(network_info['containers'])}")
    print(f"Network IDs: {', '.join(network_info['network_ids'])}")

    # Uncomment the following line to stop and remove the networks and their containers
    # dcc.stop_and_remove_containers_and_networks(network_info['network_ids'])
