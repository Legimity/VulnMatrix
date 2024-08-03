import os
from typing import List

from docker.NetworkTopology import NetworkTopology, Router, Network, Switch, Host


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
