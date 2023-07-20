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

# Configure DNF
echo "Configuring DNF..."
dnf config-manager --set-enabled crb
dnf install epel-release -y
dnf update -y
dnf install openssh-server zsh git vim curl wget htop net-tools iftop dnsutils nfs-utils tmux iscsi-initiator-utils -y

# Change Shell
echo "Changing shell to ZSH..."
usermod --shell /bin/zsh root

# Enable ISCSI
systemctl enable iscsid
systemctl start iscsid

# Configure Cockpit
echo "Configuring Cockpit..."
systemctl enable --now cockpit.socket
