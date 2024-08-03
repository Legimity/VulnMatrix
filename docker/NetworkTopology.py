import json
from typing import List, Dict


class Router:
    """
    Router类，用于存储路由器的名称，网关信息
    """

    def __init__(self, name: str, netGate: List[Dict[str, str]]):
        """
        @name: name
        @netGate: [{'netName': 'name', 'network': 'net1', 'gateway': ''}, {'netName': 'name', 'network': 'net2', 'gateway': ''}]
            network是接入的网络，netName是接入的网络名，gateway是网关地址 --> 在仿真出来的网络中认为是路由器在这个网络中的ip）

        在yml文件中对应：
        networks:
            000_svc: # 网络名
                ipv4_address: 192.168.160.254 # ip
            net_152_net0:
                ipv4_address: 10.152.0.253
        """
        self._name = name
        self._netGate = netGate

    @property
    def getName(self) -> str:
        return self._name

    @property
    def getNetGate(self) -> List[Dict[str, str]]:
        return self._netGate

    def netNameToIp(self, netName: str) -> str:
        for net in self._netGate:
            if net.get('netName') == netName:
                return net.get('network')


class Switch:
    """
    Switch类，子交换机
    用于存储子交换机的名称，交换机接入的网络，交换机在这个网络中的ip地址
    """

    def __init__(self, name: str, net: str, ip: str):
        """
        @name: 交换机名
        @net: 接入的网络
        @ip: 在这个网络中的ip
        """
        self._name = name
        self._net = net
        self._ip = ip

    @property
    def getName(self) -> str:
        return self._name

    @property
    def getNetwork(self) -> str:
        return self._net

    @property
    def getIp(self) -> str:
        return self._ip


class Network:
    """
    Network类，用于存储网络的名称，网络的网段
    """

    def __init__(self, nameNet: List[Dict[str, str]]):
        """
        @nameNet: 网络名: 网络地址
        """
        self._nameNet = nameNet

    def getNetwork(self, name) -> str:
        for net in self._nameNet:
            if net.get('name') == name:
                return net.get('network')

    @property
    def getNameNet(self):
        return self._nameNet


class Host:
    """
    Host类，用于存储主机的名称，主机接入的网络，主机在这个网络中的ip地址
    """

    def __init__(self, name: str, net: str, ip: str):
        """
        @name: 主机名
        @net: 接入的网络
        @ip: 在这个网络中的ip
        """
        self._name = name
        self._net = net
        self._ip = ip

    @property
    def getName(self) -> str:
        return self._name

    @property
    def getNetwork(self) -> str:
        return self._net

    @property
    def getIp(self) -> str:
        return self._ip


class NetworkTopology:

    def __init__(self):
        self._routers: List[Router] = []
        self._switches: List[Switch] = []
        self._networks: List[Network] = []
        self._hosts: List[Host] = []

        self._routersRaw = []
        self._switchesRaw = []
        self._hostsRaw = {}
        self._networksRaw = {}

    def loadConfig(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            self._routersRaw = data.get('routers', [])
            self._switchesRaw = data.get('switches', [])
            self._hostsRaw = data.get('hosts', {})
            self._networksRaw = data.get('networks', {})

    @property
    def getRouters(self) -> List[Router]:
        for router_data in self._routersRaw:
            name = router_data.get('name', '')
            netGateList = []
            for net in router_data.get('network', []):
                network = self.getNetworkFromName(net)
                netGate = {'netName': net.get('name'), 'network': network, 'gateway': net.get('gateway')}
                netGateList.append(netGate)
            router = Router(name, netGateList)
            self._routers.append(router)
        return self._routers

    @property
    def getSwitches(self) -> List[Switch]:
        for switch_data in self._switchesRaw:
            name = switch_data.get('name', '')
            network = switch_data.get('network', '')
            ip = switch_data.get('ip', '')
            switch = Switch(name, network, ip)
            self._switches.append(switch)

            # try:
            #     network = self.getNetworkFromName(network)
            #     ip = switch_data.get('ip', '')
            #     switch = Switch(name, network, ip)
            #     self._switches.append(switch)
            # except Exception as e:
            #     print('没有找到对应的网络')

        return self._switches

    @property
    def getHosts(self) -> List[Host]:
        for subnet, hosts in self._hostsRaw.items():
            network = subnet
            for host_data in hosts:
                name = host_data.get('name', '')
                ip = host_data.get('ip', '')
                host = Host(name, network, ip)
                self._hosts.append(host)
                # try:
                #     network = self.getNetworkFromName(network)
                #     ip = host_data.get('ip', '')
                #     host = Host(name, network, ip)
                #     self._hosts.append(host)
                # except Exception as e:
                #     print('没有找到对应的网络')

        return self._hosts

    @property
    def getNetworks(self) -> List[Network]:
        nameNetList = []
        for network_data in self._networksRaw:
            name = network_data.get('name', '')
            network = network_data.get('network', '')
            nameNet = {'name': name, 'network': network}
            nameNetList.append(nameNet)
        network = Network(nameNetList)
        self._networks.append(network)
        return self._networks

    def getNetworkFromName(self, name: str) -> str:
        for net in self._networksRaw:
            if net.get('name') == name:
                return net.get('network')


# networkTopology = NetworkTopology()
# networkTopology.loadConfig('network_config.json')
#
# routers: List[Router] = networkTopology.getRouters
# # for router1 in routers:
# #     print(router1.getName)
# #     print(router1.getNetGate)
# switches: List[Switch] = networkTopology.getSwitches
# # for switch1 in switches:
# #     print(switch1.getName + '接入网络: ' + switch1.getNetwork + ', IP地址: ' + switch1.getIp)
# networks: List[Network] = networkTopology.getNetworks
# # for network1 in networks:
# #     print(network1.getNameNet)
# hosts: List[Host] = networkTopology.getHosts
# # for host in hosts:
# #     print(host.getName + '接入网络: ' + host.getNetwork + ', IP地址: ' + host.getIp)
