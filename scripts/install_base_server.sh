#!/usr/bin/env bash

# Check if SELinux is enabled
if [ $(getenforce) = "Enforcing" ]; then
    echo "SELinux is enabled. Disabling it now..."

    # Disable SELinux
    setenforce 0

    # Make sure the change is persistent
    sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

    echo "SELinux has been disabled."
else
    echo "SELinux is already disabled."
fi

# Configure io watcher
echo fs.inotify.max_user_instances=8192| tee -a /etc/sysctl.conf && sysctl -p

# Configure DNF
echo "Configuring DNF..."
dnf config-manager --set-enabled crb
dnf install epel-release -y
dnf update -y
dnf install openssh-server zsh git vim curl wget htop net-tools iftop dnsutils nfs-utils tmux iscsi-initiator-utils -y

# Install Docker Runtime
if USE_EXTERNAL_CONTAINERD; then
    echo "Using external containerd"
    dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    dnf install containerd.io -y
    systemctl start containerd
    systemctl enable containerd
    # Configure Containerd
    containerd config default > /etc/containerd/config.toml
else
    echo "Using internal containerd"
fi

# Change Shell
echo "Changing shell to ZSH..."
usermod --shell /bin/zsh root

# Enable ISCSI
systemctl enable iscsid
systemctl start iscsid
