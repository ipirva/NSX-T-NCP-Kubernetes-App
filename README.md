# Overview

Use NSX-T container plug-in with Kubernetes to provide Networking and Security services. The main functionalities would be:

- Dynamic IP allocation
- Intra-cluster communication, on-demand provisioning of the routers and logical switches (segments)
- Network isolation at pod, node, and cluster levels
- k8s LoadBalancer and ClusterIP services
- k8s Ingress with NSX-T Layer 7 load balancer
- Automatic creation of SNAT rules for external connectivity
- Micro-segmentation, network and security policy at a granular level (Pod) with a zero-trust model

The NSX-T container plug-in provides on-demand provisioning of routers and logical switches (segments) for each Kubernetes namespace.
This examples uses a shared router (NSX-T T1 router) for all the namespaces and a dedicated segment per namespace. A dedicated router per namespace can as well be deployed.

## Environment

- Network and security - NSX-T platform v2.5
- Kubernetes CNI NSX plug-in (NCP) v2.5.1
- Kubernetes platform v1.16.4/v1.17.0
- Kubernetes master and workers on top of VM Ubuntu 18.04LTS
- docker-ce v19.03.5

Each Kubernetes VM node has 2 vNICs:

- "ens160" for the management (configured w/ an IP)
- "ens192" for the Kubernetes data plane (no IP configured)

NSX-T cluster configuration dumps are provided for before and after NCP installation.
Before the NCP installation, the NSX-T cluster was configured with (excerpt):

- ESXi transport node: to host the k8s master and workers
- Segment "MgmtSg" for the k8s nodes' management vNICs
- Segment "k8s-vifs-sg" for the pod transport data plane vNICs
- Tag the k8s node VMs pod transport data plane vNICs with: ncp/node_name = <node DNS name>, ncp/cluster = <Cluster name> i.e. k8s-cl1 for this example
- NSX-T TO router w/ BGP configured to announce LoadBalancer VIPs, SNAT range, Pod IP range when no SNAT is used
- IP pool "k8s-cl1-external-ippool": per k8s Namespace SNAT pool of IP addresses
- IP pool "k8s-cl1-lb-ippool": k8s service LoadBalancer VIP
- IP block "k8s-cl1-pod-network-ipblock": k8s Pod IP address space (SNATed)
- IP block "k8s-cl1-container-network-nosnat": k8s Pod IP address space (no SNAT)

## NSX Container Plug-in for Kubernetes (NCP) - Installation and Administration Guide

[Installation and Administration Guide link](https://docs.vmware.com/en/VMware-NSX-T-Data-Center/2.5/ncp-kubernetes/GUID-FB641321-319D-41DC-9D16-37D6BA0BC0DE.html)

## NSX Container Plugin 2.5.1 (NCP) Release Notes

19 December 2019, Build 15287458

[Release note link](https://docs.vmware.com/en/VMware-NSX-T-Data-Center/2.5/rn/NSX-Container-Plugin-251-Release-Notes.html)
