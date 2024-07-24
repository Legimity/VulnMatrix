import tornado
import yaml

from handlers.BaseHandler import BaseHandler


class ViewNetworkHandler(BaseHandler):
    # def getNodeInfo(self, data):
    #     nodeInfo = []
    #     services = data['services']
    #     networks = data['networks']
    #     i = 1
    #
    #     # Add attacker node
    #     attacker_node = {
    #         'id': i,
    #         'name': 'attacker',
    #         'label': '攻击者网络',
    #         'type': 'attacker',
    #         'ip': '1.1.1.1',
    #         'medi': 'false',
    #         'port': '未知'
    #     }
    #     nodeInfo.append(attacker_node)
    #     i += 1
    #
    #     # Add router node
    #     router_node = {
    #         'id': i,
    #         'name': 'router',
    #         'label': 'Router',
    #         'type': 'router',
    #         'ip': '192.168.1.1',
    #         'medi': 'false',
    #         'port': '未知'
    #     }
    #     nodeInfo.append(router_node)
    #     i += 1
    #
    #     # Add switch node
    #     switch_node = {
    #         'id': i,
    #         'name': 'switch',
    #         'label': 'Switch',
    #         'type': 'switch',
    #         'ip': '192.168.1.2',
    #         'medi': 'false',
    #         'port': '未知'
    #     }
    #     nodeInfo.append(switch_node)
    #     i += 1
    #
    #     for key, value in services.items():
    #         node = {}
    #         node['id'] = i
    #         i += 1
    #         node['name'] = key
    #         node['label'] = 'Target'
    #         node['type'] = 'target'
    #         if 'ports' in value.keys():
    #             node['port'] = value['ports']
    #         else:
    #             node['port'] = value['expose']
    #         if len(value['networks']) == 1:
    #             # 转list要指定对值，否则默认转key
    #             li = list(value['networks'].values())
    #             node['ip'] = li[0]['ipv4_address']
    #             node['medi'] = 'false'
    #         else:
    #             li = list(value['networks'].values())
    #             node['net1'] = li[0]['ipv4_address']
    #             node['net2'] = li[1]['ipv4_address']
    #             node['medi'] = 'true'
    #
    #         nodeInfo.append(node)
    #     return nodeInfo

    def get(self, *args, **kwargs):
        # with open('./docker_hub/CFS-Docker/docker-compose.yml', 'r', encoding='utf-8') as f:
        #     yaml_data = yaml.safe_load(f)
        #
        # info = self.getNodeInfo(yaml_data)
        #
        # #self.render('test.html')
        # json_info = tornado.escape.json_encode(info)
        # #json_info=tornado.escape.json_encode(yaml_data)
        self.render('view2.html')
