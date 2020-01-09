# Install Kubernetes Cluster

High-level installation guidance for 1 Kubernetes master and 2 Kubernetes workers.
For this example, the Kubernetes nodes are Ubuntu 18.04LTS VMs.

## Master & WORKER Bootstrap

### MASTER & WORKER

```bash
apt-get install -qy curl socat conntrack python
swapoff -a
modprobe br_netfilter
```

```bash
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
```

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable"
```

```bash
apt-get update && apt-get install docker-ce docker-ce-cli containerd.io

apt-get install -y kubeadm=1.16.4-00 && apt-get install -y kubelet=1.16.4-00 && apt-get install -y kubectl=1.16.4-00
apt-mark hold kubeadm kubelet kubectl

bash -c 'cat > /etc/docker/daemon.json <<EOF
{
    "exec-opts": ["native.cgroupdriver=systemd"],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m"
    },
    "storage-driver": "overlay2"
}
EOF'

systemctl daemon-reload && systemctl enable docker && systemctl restart docker
```

### MASTER

```bash
hostnamectl set-hostname master1

iptables -F && iptables -t nat -F && iptables -t mangle -F && iptables -X

kubeadm config images pull && kubeadm init
```

kubeadm will give the token to be used on workers to join them to the cluster.

For the user you want to be able to use kebectl:

`mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config &&sudo chown $(id -u):$(id -g) \$HOME/.kube/config`

### WORKER

`hostnamectl set-hostname worker1`

In my case the Kubernetes API server endpoint is 10.10.10.11 and the below is the command of kubeadm init output on the master:

`kubeadm join 10.10.10.11:6443 --token myznmr.yi86vd58scomt0wc --discovery-token-ca-cert-hash sha256:32d17024fbbbff51716efcc3ce862b7a8425e36449feeddb93d7f98479f90465`

## Install NCP

High-level NSX Container Plugin (NCP) installation guidance. Follow install document and the release notes for further details.

NCP v2.5.1 is being used.
Download the NSX-T NCP package from my.vmware.com portal (nsx-container-2.5.1.15287458.zip):
Products > All Products & Programs > All Products > Network & Security > VMware NSX-T Data Center > Drivers&Tools > NSX Container Plugin

NCP will deploy the following components in the Kubernetes namespace nsx-system:

- nsx-ncp: a Deployment w/ 1 replica by default
- nsx-node-agent: a DaemonSet where each Pod runs two containers. One container runs the NSX node agent, whose main responsibility is to manage container network interfaces. It interacts with the CNI plugin and the Kubernetes API server. The other container runs NSX kube-proxy, whose only responsibility is to implement Kubernetes service abstraction by translating cluster IPs into pod IPs. It implements the same functionality as the upstream kube-proxy.
- nsx-ncp-bootstrap: a DaemonSet which provides OVS and CNI lifecycles, the installation and checks on each node.

### Master

`unzip nsx-container-2.5.1.15287458.zip`

The archive contains:

- all the NCP control-plane and bootstrap components (NCP docker image), i.e. docker image nsx-ncp-ubuntu-2.5.1.15287458.tar
- the cluster configuration YAML, i.e. ncp-ubuntu.yaml

`docker load -i ~/nsx-ncp-ubuntu-2.5.1.15287458.tar && docker tag registry.local/2.5.1.15287458/nsx-ncp-ubuntu nsx-ncp-ubuntu`

#### Edit ncp-ubuntu.yaml

A few options are changed on ncp-ubuntu.yaml. The default and changed files are available on Git for your comparaison.

#### Apply YML

`kubectl apply -f ~/nsx-container-2.5.1.15287458/Kubernetes/ncp-ubuntu.yaml`

### Worker

Copy the docker NCP image to each worker and load it.

`docker load -i ~/nsx-ncp-ubuntu-2.5.1.15287458.tar && docker tag registry.local/2.5.1.15287458/nsx-ncp-ubuntu nsx-ncp-ubuntu`

## Useful Troubleshooting Commands

kubectl get nodes

kubectl get pods -o wide --all-namespaces

kubectl logs -n nsx-system $(kubectl get pods -n nsx-system -l component=nsx-ncp --no-headers -o custom-columns=":metadata.name")

kubectl get events --all-namespaces

kubectl get deployments -n nsx-system

kubectl get daemonset -n nsx-system

kubectl get configmap -n nsx-system

Other useful ressources: [Administering NSX Container Plug-in](https://docs.vmware.com/en/VMware-NSX-T-Data-Center/2.5/ncp-kubernetes/GUID-7D35C9FD-813B-43C0-ADA8-C5C82596E1C9.html)
The previous ressource is particularly useful for the NSX CLI commands available on the key NCP components: NCP Container, NSX Node Agent and NSX Kube Proxy
