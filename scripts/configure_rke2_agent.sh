#!/usr/bin/env bash

# Install RKE2
echo "Installing RKE2..."
curl -sfL https://rancher-mirror.rancher.cn/rke2/install.sh | INSTALL_RKE2_MIRROR=cn INSTALL_RKE2_TYPE="agent" sh -


SERVER_HOSTNAME=$1

if [ -z "$SERVER_HOSTNAME" ]; then
    echo "Usage: $0 <server_hostname>"
    exit 1
fi

set -e

TOKEN=$(ssh $SERVER_HOSTNAME "cat /var/lib/rancher/rke2/server/node-token")

if USE_EXTERNAL_CONTAINERD; then
  CONFIG_STRING="server: https://"$SERVER_HOSTNAME":9345
token: $TOKEN
kubelet-arg: \"--max-pods=200\"
container-runtime-endpoint: unix:///run/containerd/containerd.sock"
else
    CONFIG_STRING="server: https://"$SERVER_HOSTNAME":9345
token: $TOKEN
kubelet-arg: \"--max-pods=200\""
fi

# Configure Rancher
echo "Configuring RKE2..."
echo "$CONFIG_STRING" > /etc/rancher/rke2/config.yaml

# Prepare images
if USE_EXTERNAL_CONTAINERD; then
  ctr -n k8s.io image pull docker.io/rancher/pause:3.6
  ctr -n k8s.io image tag docker.io/rancher/pause:3.6 registry.k8s.io/pause:3.6
fi


## Start RKE2 Agent
echo "Starting RKE2 Agent..."
systemctl enable rke2-agent.service
systemctl start rke2-agent.service
