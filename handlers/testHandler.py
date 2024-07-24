# class DockerComposeControlHandler(tornado.web.RequestHandler):
#     def post(self):
#         data = tornado.escape.json_decode(self.request.body)
#         if data.get('action') == 'trigger':
#             network_info=self.docker_compose_up()
#             logger.info(network_info)
#             self.write("DockerComposeControlHandler triggered successfully.")
#         else:
#             self.write("Invalid action.")

#     def docker_compose_up(self):
#         # 启动靶场
#         logger.info("Function docker_compose_up has been triggered!")

#         # TODO：path不应该写死，应该根据id启动对应的靶场
#         docker_compose_path=os.path.join(os.path.dirname(__file__), "docker_hub","CFS-Docker","docker-compose.yml")
#         # docker_compose_path=os.path.join(os.path.dirname(__file__), "files","docker-compose.yml")
#         network_info=Docker_ComposeControl.run(docker_compose_path)
#         return network_info