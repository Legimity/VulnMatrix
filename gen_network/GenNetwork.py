import os
import sys
from typing import List
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
print(os.path.dirname(os.path.abspath(__file__)) + '/../')

from gen_network.Contents import Contents
from gen_network.NetworkTopology import NetworkTopology, Router, Network, Host


def ipToDir(ip: str):
    return ip.replace('.', '_')


class GenNetwork:
    def __init__(self, networkTopology: NetworkTopology):
        self.networks: List[Network] = networkTopology.getNetworks
        self.routers: List[Router] = networkTopology.getRouters
        # self.switches: List[Switch] = networkTopology.getSwitches
        self.hosts: List[Host] = networkTopology.getHosts
        self.composeContents: str = ""

    def createDir(self):
        """
        创建网络拓扑的目录结构, Dockerfile文件, 启动脚本
        """
        if not os.path.exists('network'):
            os.mkdir('network')
        for router in self.routers:
            routerDirName = f'rnode_{router.getName}'
            routerPath = f'network/{routerDirName}'
            if not os.path.exists(routerPath):
                os.makedirs(routerPath)
                # print(f"Created directory: {output_path}")
                # logger.info(f"Created directory: {output_path}")
            with open(f'{routerPath}/Dockerfile', 'w') as f:
                f.write(Contents.BaseDockerfile)
            with open(f'{routerPath}/startup.sh', 'w') as f:
                f.write(Contents.BaseStartupScript)
        #
        # for switch in self.switches:
        #     switchDirName = f'switch_{switch.getNetwork}_{ipToDir(switch.getIp)}'
        #     if not os.path.exists(f'network/{switchDirName}'):
        #         os.makedirs(f'network/{switchDirName}')
        #     with open(f'network/{switchDirName}/Dockerfile', 'w') as f:
        #         f.write(Contents.BaseDockerfile)
        #     with open(f'network/{switchDirName}/startup.sh', 'w') as f:
        #         f.write(Contents.StartupScript)

        for host in self.hosts:
            # hostDirName = f'hnode_{host.getName}_{host.getNetwork}_{ipToDir(host.getIp)}'
            hostDirName = f'hnode_{host.getNetwork}_{ipToDir(host.getIp)}'
            if not os.path.exists(f'network/{hostDirName}'):
                os.makedirs(f'network/{hostDirName}')
            # dirName = f'network/{hostDirName}'
            if host.getType == '0':
                host.createDockerfile(Contents.BaseDockerfile)
                host.createStartupScript(Contents.BaseStartupScript)
            elif host.getType == '1':
                host.createDockerfile(Contents.VulDockerfile1)
                host.createStartupScript(Contents.StartupScript1)
            elif host.getType == '2':
                host.createDockerfile(Contents.VulDockerfile2)
                host.createStartupScript(Contents.StartupScript2)
            elif host.getType == '3':
                host.createDockerfile(Contents.VulDockerfile3)
                host.createStartupScript(Contents.StartupScript3)
            elif host.getType == '4':
                host.createDockerfile(Contents.VulDockerfile4)
                host.createStartupScript(Contents.StartupScript4)
            elif host.getType == '5':
                host.createDockerfile(Contents.VulDockerfile5)
                host.createStartupScript(Contents.StartupScript5)


    # TODO: ?
    # RUN apk install
    # def createDockerfile(self, path, addCommand: bool, commandLine: str):
    #     """
    #     创建Dockerfile文件
    #     @param path: Dockerfile文件路径
    #     @param addCommand: 是否添加新的命令
    #     @param commandLine: 要添加的命令
    #     """
    #     if addCommand:
    #         baseLines = Contents.BaseDockerfile.strip().split('\n')
    #         entrypointLine = baseLines[-1]
    #         contentBeforeEntrypoint = "\n".join(baseLines[:-1])
    #
    #         addContent = "\n".join(commandLine)
    #
    #
    #     # 生成最终内容，确保 ENTRYPOINT 在最后
    #     final_content = f"{content_before_entrypoint}\n{additional_content}\n{entrypoint_line}"
    #
    #     with open(path, 'w') as f:
    #         f.write()
    # def createStartupScript(self, path, commandLine: str):

    def createDockerCompose(self):
        """
        创建docker-compose.yml文件
        """
        networksContents: str = ""
        routersContents: str = ""
        # switchesContents: str = ""
        hostsContents: str = ""
        for network in self.networks:
            networkName = network.getName
            subnet = network.getNetwork
            networksContents += Contents.composeNetworks.format(networkName=networkName, subnet=subnet)
        # print(networksContents)

        contents = ""
        for router in self.routers:
            routerDirname = f'rnode_{router.getName}'
            for netGate in router.getNetGate:
                contents += f"{netGate.get('netName')}:\n            ipv4_address: {netGate.get('gateway')}\n\n        "
            routersContents += Contents.composeRouters.format(routerDirname=routerDirname, routerContents=contents)
            # print(routersContents)

        # for switch in self.switches:
        #     switchDirname = f'switch_{switch.getNetwork}_{ipToDir(switch.getIp)}'
        #     switchesContents += Contents.composeSwitches.format(switchDirname=switchDirname, network=switch.getNetwork,
        #                                                       ip=switch.getIp)
        #     # print(switchesContents)

        for host in self.hosts:
            hostDirname = f'hnode_{host.getNetwork}_{ipToDir(host.getIp)}'
            hostsContents += Contents.composeHosts.format(hostDirname=hostDirname, network=host.getNetwork,
                                                              ip=host.getIp)
            # print(hostsContents)

        # self.composeContents += Contents.composeServicesFlag + routersContents + switchesContents + hostsContents + Contents.composeNetworksFlag + networksContents
        self.composeContents += Contents.composeServicesFlag + routersContents + hostsContents + Contents.composeNetworksFlag + networksContents
        # print(self.composeContents)
        with open('docker-compose.yml', 'w') as f:
            f.write(self.composeContents)


def main():
    networkTopology = NetworkTopology()
    networkTopology.loadConfig('network_config.json')
    genNetwork = GenNetwork(networkTopology)
    genNetwork.createDir()
    genNetwork.createDockerCompose()


# if __name__ == '__main__':
    # main()
