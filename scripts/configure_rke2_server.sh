#!/usr/bin/env bash

CONFIG_STRING="service-node-port-range: 30000-40000
cni: calico"

# Install Docker
echo "Installing Docker..."
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf install docker-ce docker-ce-cli containerd.io -y
dnf install python-pip -y
pip3 install docker-compose
systemctl start docker
systemctl enable docker

# Install RKE2
echo "Installing RKE2..."
curl -sfL https://rancher-mirror.rancher.cn/rke2/install.sh | INSTALL_RKE2_MIRROR=cn sh -

# Configure Rancher
echo "Configuring RKE2..."
echo "$CONFIG_STRING" > /etc/rancher/rke2/config.yaml

# Start RKE2 Server
echo "Starting RKE2 Server..."
systemctl enable rke2-server.service
systemctl start rke2-server.service

# Configure PATH
echo "Configure PATH..."v
echo "export PATH=$PATH:/var/lib/rancher/rke2/bin" >> /etc/profile

# Configure crictl
echo "Configure crictl..."
containerd config default > /etc/containerd/config.toml
CONFIG_CRICTL_STRING="runtime-endpoint: unix:///run/k3s/containerd/containerd.sock
image-endpoint: unix:///run/k3s/containerd/containerd.sock
timeout: 10
debug: false"
echo "$CONFIG_CRICTL_STRING" > /etc/crictl.yaml

