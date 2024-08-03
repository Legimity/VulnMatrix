import os
from typing import List

from docker.NetworkTopology import NetworkTopology, Router, Network, Switch, Host

# TODO：按照gen_docker.py的逻辑，实现GenNetwork类，实现自动生成网络拓扑
class GenNetwork:
    def __init__(self, networkTopology: NetworkTopology):
        self.networks:List[Network] = networkTopology.getNetworks
        self.routers:List[Router] = networkTopology.getRouters
        self.switches:List[Switch] = networkTopology.getSwitches
        self.hosts:List[Host] = networkTopology.getHosts


    def createDir(self):
        if not os.path.exists('network'):
            os.mkdir('network')

        for router in self.routers:
