# Service Description

The app has NGINX frontend web servers deployed inside a Kubernetes namespace, "myapp".
The web servers are organised in 2 deployments with 2 NGINX instances each. Each deployment handles one web service, one web endpoint, /service1/,  respectively /service2/.

NSX Container Plugin is used for:

- Container network connectivity inside the cluster
- Distributed micro-segmentation (k8s network policy enforced in OVS)
- Ingress ressource / Ingress controller (NSX-T L7 load-balancer)
- SNAT for the traffic to outside the cluster (NSX-T T1 router)
- BGP to advertise relavant routes (NSX-T T0 router)

The following IP ressources are being configured inside NSX-T for this app:

- 10.1.0.0/16 -> an /24 will be allocated per Kubernetes namespace for Pods network connectivity
- 192.168.150.10 - 192.168.150.254 -> 1 IP per Kunernates namespace will be used to SNAT the traffic to outside the cluster
- 20.20.20.30 - 20.20.20.254 -> IP range to be used to allocate LB VIPs

```text
edgenode-01a> get logical-router
Logical Router
UUID                                   VRF    LR-ID  Name                              Type                        Ports
--- CUT FOR BREVITY --
36f4e18a-6961-4510-a0fc-d37f53751f51   2      2      SR-T0-GW                          SERVICE_ROUTER_TIER0        7
9e3c14da-5644-48d3-9296-6c8f555f38a4   3      1      DR-T0-GW                          DISTRIBUTED_ROUTER_TIER0    5
--- CUT FOR BREVITY --

edgenode-01a> vrf 2
edgenode-01a(tier0_sr)> get bgp neighbor summary
BFD States: NC - Not configured, AC - Activating,DC - Disconnected
            AD - Admin down, DW - Down, IN - Init,UP - Up
BGP summary information for VRF default for address-family: ipv4Unicast
Router ID: 192.168.240.11  Local AS: 100

Neighbor                            AS          State Up/DownTime  BFD InMsgs  OutMsgs InPfx  OutPfx
169.254.0.131                       100         Estab 2d12h22m     NC  217375  217377  33     33
192.168.240.1                       200         Estab 2d12h22m     UP  3675    3674    9      31
192.168.250.1                       200         Estab 2d12h22m     UP  3675    3674    10     31

BFD States: NC - Not configured, AC - Activating,DC - Disconnected
            AD - Admin down, DW - Down, IN - Init,UP - Up
BGP summary information for VRF default for address-family: ipv6Unicast
Router ID: 192.168.240.11  Local AS: 100
Neighbor                            AS          State Up/DownTime  BFD InMsgs  OutMsgs InPfx  OutPfx
169.254.0.131                       100         Estab 2d12h22m     NC  217375  217377  6      6
2240::1                             200         Estab 2d12h22m     NC  3629    3628    4      4
2250::1                             200         Estab 2d12h22m     NC  3629    3628    4      4

edgenode-01a(tier0_sr)> get bgp neighbor 192.168.240.1  advertised-routes

BGP table version is 106, local router ID is 192.168.240.11
Status flags: > - best, I - internal
Origin flags: i - IGP, e - EGP, ? - incomplete

   Network                             Next Hop                            Metric       LocPrf   Weight  Path
 --- CUT FOR BREVITY --
 > 10.1.1.0/24                         0.0.0.0                             0            100      32768            ?
 > 10.4.7.0/24                         0.0.0.0                             0            100      32768            ?
 > 20.20.20.30/32                      0.0.0.0                             0            100      32768            ?
 > 192.168.150.10/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.11/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.12/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.13/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.14/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.15/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.16/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.17/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.18/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.240.0/24                    0.0.0.0                             0            100      32768            ?
 > 192.168.250.0/24                    0.0.0.0
 --- CUT FOR BREVITY --

BGP table version is 106, local router ID is 192.168.240.11
Status flags: > - best, I - internal
Origin flags: i - IGP, e - EGP, ? - incomplete

   Network                             Next Hop                            Metric       LocPrf   Weight  Path
--- CUT FOR BREVITY --
 > 10.1.1.0/24                         0.0.0.0                             0            100      32768            ?
 > 10.4.7.0/24                         0.0.0.0                             0            100      32768            ?
 > 20.20.20.30/32                      0.0.0.0                             0            100      32768            ?
 > 192.168.150.10/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.11/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.12/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.13/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.14/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.15/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.16/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.17/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.150.18/32                   0.0.0.0                             0            100      32768            ?
 > 192.168.240.0/24                    0.0.0.0                             0            100      32768            ?
 > 192.168.250.0/24                    0.0.0.0                             0            100      32768            ?
 --- CUT FOR BREVITY --
```

The provisioned NSX-T LB VIP is configured with 1 VIP and it will receive the web requests to:

- http://mytest.fr/service1/, respectively to
- http://mytest.fr/service2/,

it will regex match the "HTTP Request URI", it will rewrite it to "/" and it will balance the web requests (round robin configured) to the containers forming the kubernetes service "service1", respectively "service2".

The kubernetes NetworkPolicy are configured Ingress on each container to allow only the TCP:8080 traffic coming from the NSX-T L7 LB VIP.
