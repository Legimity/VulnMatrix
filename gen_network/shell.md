```bash
# Compose up
(VulnMatrix) Yuntsy:docker (main*) $ gen_network-compose up -d
WARN[0000] /Users/yuntsy/My/Projects/Blog/VulnMatrix/gen_network/gen_network-compose.yml: `version` is obsolete
[+] Building 2.5s (29/39)                                                                                  gen_network:desktop-linux
=> [switch_dmz_10_1_20_3 internal] load build definition from Dockerfile                                                  0.0s
=> => transferring dockerfile: 266B                                                                                       0.0s
=> [host_dmz_10_1_20_11 internal] load build definition from Dockerfile                                                   0.0s
=> => transferring dockerfile: 266B                                                                                       0.0s
=> [switch_office_10_2_10_3 internal] load metadata for gen_network.io/library/alpine:latest                                   2.3s
=> [host_dmz_10_1_20_10 internal] load build definition from Dockerfile                                                   0.0s
=> => transferring dockerfile: 266B                                                                                       0.0s
=> [switch_dev_10_20_2_3 internal] load build definition from Dockerfile                                                  0.0s
=> => transferring dockerfile: 266B                                                                                       0.0s
=> [switch_office_10_2_10_3 internal] load build definition from Dockerfile                                               0.0s
=> => transferring dockerfile: 266B                                                                                       0.0s
=> [host_dmz_10_1_20_12 internal] load build definition from Dockerfile                                                   0.0s
=> => transferring dockerfile: 266B                                                                                       0.0s
=> [switch_dev_10_20_2_3 internal] load .dockerignore                                                                     0.0s
=> => transferring context: 2B                                                                                            0.0s
=> [switch_dmz_10_1_20_3 internal] load .dockerignore                                                                     0.0s
=> => transferring context: 2B                                                                                            0.0s
=> [host_dmz_10_1_20_10 internal] load .dockerignore                                                                      0.0s
=> => transferring context: 2B                                                                                            0.0s
=> [host_dmz_10_1_20_11 internal] load .dockerignore                                                                      0.0s
=> => transferring context: 2B                                                                                            0.0s
=> [switch_office_10_2_10_3 internal] load .dockerignore                                                                  0.0s
=> => transferring context: 2B                                                                                            0.0s
=> [host_dmz_10_1_20_12 internal] load .dockerignore                                                                      0.0s
=> => transferring context: 2B                                                                                            0.0s
=> [switch_dev_10_20_2_3 1/4] FROM gen_network.io/library/alpine:latest@sha256:0a4eaa0eecf5f8c050e5bba433f58c052be7587ee8af3e  0.0s
=> [host_dmz_10_1_20_10 internal] load build context                                                                      0.0s
=> => transferring context: 208B                                                                                          0.0s
=> [switch_dmz_10_1_20_3 internal] load build context                                                                     0.0s
=> => transferring context: 208B                                                                                          0.0s
=> [switch_office_10_2_10_3 internal] load build context                                                                  0.0s
=> => transferring context: 208B                                                                                          0.0s
=> [host_dmz_10_1_20_12 internal] load build context                                                                      0.0s
=> => transferring context: 208B                                                                                          0.0s
=> [host_dmz_10_1_20_11 internal] load build context                                                                      0.0s
=> => transferring context: 208B                                                                                          0.0s
=> [switch_dev_10_20_2_3 internal] load build context                                                                     0.0s
=> => transferring context: 208B                                                                                          0.0s
=> CACHED [switch_dmz_10_1_20_3 2/4] RUN apk update && apk add bash iproute2 iptables                                     0.0s
=> CACHED [switch_dmz_10_1_20_3 3/4] COPY startup.sh /usr/local/bin/startup.sh                                            0.0s
=> CACHED [host_dmz_10_1_20_10 4/4] RUN chmod +x /usr/local/bin/startup.sh                                                0.0s
=> [switch_dmz_10_1_20_3] exporting to image                                                                              0.1s
=> => exporting layers                                                                                                    0.0s
=> => writing image sha256:2021bd9d45fde1defa052d40372827b52d2991f26857fe778825552ce8b80627                               0.0s
=> => naming to gen_network.io/library/gen_network-switch_dmz_10_1_20_3                                                             0.0s
=> [host_dmz_10_1_20_12] exporting to image                                                                               0.0s
=> => exporting layers                                                                                                    0.0s
=> => writing image sha256:e93f903c8c8c73b61e2f2f76b884b28a44ca0d5c6b22bad880d9bb325fbf6c07                               0.0s
=> => naming to gen_network.io/library/gen_network-host_dmz_10_1_20_12                                                              0.0s
=> [switch_dev_10_20_2_3] exporting to image                                                                              0.0s
=> => exporting layers                                                                                                    0.0s
=> => writing image sha256:5163fbf1c72924eaa7deeebc7ce2ade3670ac0a3a700b84c1a58dd31b6062414                               0.0s
=> => naming to gen_network.io/library/gen_network-switch_dev_10_20_2_3                                                             0.0s
=> [host_dmz_10_1_20_10] exporting to image                                                                               0.1s
=> => exporting layers                                                                                                    0.0s
=> => writing image sha256:f672706d8db7ab33b9f07b2fa3b6ab15dfb8c067bf352e1f745f2a720ee08da7                               0.0s
=> => naming to gen_network.io/library/gen_network-host_dmz_10_1_20_10                                                              0.0s
=> [host_dmz_10_1_20_11] exporting to image                                                                               0.0s
=> => exporting layers                                                                                                    0.0s
=> => writing image sha256:dae6964c5cb8930cd790d5875a8448f0f385892d2291c042063f464740762fdf                               0.0s
=> => naming to gen_network.io/library/gen_network-host_dmz_10_1_20_11                                                              0.0s
=> [switch_office_10_2_10_3] exporting to image                                                                           0.0s
=> => exporting layers                                                                                                    0.0s
=> => writing image sha256:e06152eb81fd94c04688ee838241f4fd85e9081ea00bfcef507dcdd83d3b3419                               0.0s
=> => naming to gen_network.io/library/gen_network-switch_office_10_2_10_3                                                          0.0s
[+] Running 4/0
✔ Network docker_dev                   Created                                                                            0.0s
✔ Network docker_dmz                   Created                                                                            0.0s
✔ Network docker_office                Created                                                                            0.0s
⠋ Container host_dev_10_20_2_11        Creating                                                                           0.0s
⠋ Container host_office_10_2_10_11     Creating                                                                           0.0s
⠋ Container router_dev_10_20_2_254     Creating                                                                           0.0s
⠋ Container switch_dev_10_20_2_3       Creating                                                                           0.0s
⠋ Container host_dmz_10_1_20_12        Creating                                                                           0.0s
⠋ Container switch_office_10_2_10_3    Creating                                                                           0.0s
⠋ Container router_dmz_10_1_20_254     Creating                                                                           0.0s
[+] Running 3/17t_dev_10_20_2_10        Creating                                                                           0.0s
✔ Network docker_dev                   Created                                                                            0.0s
✔ Network docker_dmz                   Created                                                                            0.0s
✔ Network docker_office                Created                                                                            0.0s
⠙ Container host_dev_10_20_2_11        Starting                                                                           0.1s
⠙ Container host_office_10_2_10_11     Starting                                                                           0.1s
⠙ Container router_dev_10_20_2_254     Starting                                                                           0.1s
⠙ Container switch_dev_10_20_2_3       Starting                                                                           0.1s
⠙ Container host_dmz_10_1_20_12        Starting                                                                           0.1s
⠙ Container switch_office_10_2_10_3    Starting                                                                           0.1s
⠙ Container router_dmz_10_1_20_254     Starting                                                                           0.1s
[+] Running 5/17t_dev_10_20_2_10        Starting                                                                           0.1s
✔ Network docker_dev                   Created                                                                            0.0s
✔ Network docker_dmz                   Created                                                                            0.0s
✔ Network docker_office                Created                                                                            0.0s
⠹ Container host_dev_10_20_2_11        Starting                                                                           0.2s
⠹ Container host_office_10_2_10_11     Starting                                                                           0.2s
⠹ Container router_dev_10_20_2_254     Starting                                                                           0.2s
⠹ Container switch_dev_10_20_2_3       Starting                                                                           0.2s
✔ Container host_dmz_10_1_20_12        Started                                                                            0.2s
✔ Container switch_office_10_2_10_3    Started                                                                            0.2s
⠹ Container router_dmz_10_1_20_254     Starting                                                                           0.2s
[+] Running 6/17t_dev_10_20_2_10        Starting                                                                           0.2s
✔ Network docker_dev                   Created                                                                            0.0s
✔ Network docker_dmz                   Created                                                                            0.0s
✔ Network docker_office                Created                                                                            0.0s
⠸ Container host_dev_10_20_2_11        Starting                                                                           0.3s
⠸ Container host_office_10_2_10_11     Starting                                                                           0.3s
⠸ Container router_dev_10_20_2_254     Starting                                                                           0.3s
⠸ Container switch_dev_10_20_2_3       Starting                                                                           0.3s
✔ Container host_dmz_10_1_20_12        Started                                                                            0.2s
✔ Container switch_office_10_2_10_3    Started                                                                            0.2s
⠸ Container router_dmz_10_1_20_254     Starting                                                                           0.3s
[+] Running 11/17_dev_10_20_2_10        Starting                                                                           0.3s
✔ Network docker_dev                   Created                                                                            0.0s
✔ Network docker_dmz                   Created                                                                            0.0s
✔ Network docker_office                Created                                                                            0.0s
⠼ Container host_dev_10_20_2_11        Starting                                                                           0.4s
✔ Container host_office_10_2_10_11     Started                                                                            0.4s
⠼ Container router_dev_10_20_2_254     Starting                                                                           0.4s
✔ Container switch_dev_10_20_2_3       Started                                                                            0.4s
✔ Container host_dmz_10_1_20_12        Started                                                                            0.2s
✔ Container switch_office_10_2_10_3    Started                                                                            0.2s
⠼ Container router_dmz_10_1_20_254     Starting                                                                           0.4s
[+] Running 17/17_dev_10_20_2_10        Starting                                                                           0.4s
✔ Network docker_dev                   Created                                                                            0.0s
✔ Network docker_dmz                   Created                                                                            0.0s
✔ Network docker_office                Created                                                                            0.0s
✔ Container host_dev_10_20_2_11        Started                                                                            0.5s
✔ Container host_office_10_2_10_11     Started                                                                            0.4s
✔ Container router_dev_10_20_2_254     Started                                                                            0.5s
✔ Container switch_dev_10_20_2_3       Started                                                                            0.4s
✔ Container host_dmz_10_1_20_12        Started                                                                            0.2s
✔ Container switch_office_10_2_10_3    Started                                                                            0.2s
✔ Container router_dmz_10_1_20_254     Started                                                                            0.5s
✔ Container host_dev_10_20_2_10        Started                                                                            0.5s
✔ Container host_dmz_10_1_20_11        Started                                                                            0.5s
✔ Container switch_dmz_10_1_20_3       Started                                                                            0.4s
✔ Container router_office_10_2_10_254  Started                                                                            0.5s
✔ Container host_dmz_10_1_20_10        Started                                                                            0.4s
✔ Container host_dev_10_20_2_12        Started                                                                            0.3s
✔ Container host_office_10_2_10_10     Started                                                                            0.4s

# 进入容器，ping其他主机，验证网络连通性
(VulnMatrix) Yuntsy:gen_network (main*) $ gen_network exec -it host_dmz_10_1_20_10 /bin/sh
# 显示当前目录
/ # pwd
/
# 查看当前目录下的文件
/ # ls
bin    dev    etc    home   lib    media  mnt    opt    proc   root   run    sbin   srv    sys    tmp    usr    var
# ping 同一个内网中的另一台主机  --> 应该成功，结果：成功
/ # ping 10.1.20.11
PING 10.1.20.11 (10.1.20.11): 56 data bytes
64 bytes from 10.1.20.11: seq=0 ttl=64 time=0.312 ms
64 bytes from 10.1.20.11: seq=1 ttl=64 time=0.154 ms
64 bytes from 10.1.20.11: seq=2 ttl=64 time=0.204 ms
64 bytes from 10.1.20.11: seq=3 ttl=64 time=0.229 ms
^C
--- 10.1.20.11 ping statistics ---
4 packets transmitted, 4 packets received, 0% packet loss
# ping 不同内网中的主机  --> 应该失败，结果：失败
/ # ping 10.2.10.10
PING 10.2.10.10 (10.2.10.10): 56 data bytes
^C
--- 10.2.10.10 ping statistics ---
7 packets transmitted, 0 packets received, 100% packet loss

```
