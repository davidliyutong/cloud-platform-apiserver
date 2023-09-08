#!/bin/bash

HELP_MSG="Usage: ./setup.sh [-t|--target-machine] [-s|--server-node] [-u|user][ARGUMENTS]"

# 默认值
TARGET_MACHINE=""
SERVER_NODE=""
USER="root"

# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case "$1" in
    -t | --target-machine)
        TARGET_MACHINE="$2"
        shift
        ;;
    -s | --server-node)
        SERVER_NODE="$2"
        shift
        ;;
    -u | --user)
        USER="$2"
        shift
        ;;
    -h | --help)
        echo $HELP_MSG
        exit 1
        ;;
    *)
        echo "无效的选项: $1" >&2
        exit 1
        ;;
    esac
    shift
done

# 检查必要参数
if [[ -z "$TARGET_MACHINE" ]]; then
    echo "必须指定目标机器"
    exit 1
fi

if [[ -z "$SERVER_NODE" ]]; then
    echo "必须指定服务器节点"
    exit 1
fi

echo "目标机器: $TARGET_MACHINE"
echo "服务器节点: $SERVER_NODE"

set -e
# generate payload
echo "生成payload"
if [[ -f root-deployment.tar.gz ]]; then
    echo "root-deployment.tar.gz已存在，跳过生成"
else
    if [[ -d .temporary_root ]]; then
        rm -rf .temporary_root
    fi
    mkdir -p .temporary_root
    cp scripts/configure_rke2_agent.sh scripts/install_base_server.sh scripts/prepare_disk.sh .temporary_root/
    wget https://rancher-mirror.rancher.cn/rke2/install.sh -O .temporary_root/install_rke2.sh
    cp -a ~/.ssh .temporary_root/
    if [[ -f .temporary_root/.ssh/known_hosts ]]; then
        rm ./temporary_root/.ssh/known_hosts
    fi
    tar -czf root-deployment.tar.gz -C .temporary_root .
    rm -rf .temporary_root
fi

# copy payload
echo "复制payload到目标机器"
scp root-deployment.tar.gz $USER@$TARGET_MACHINE:/tmp
ssh $USER@$TARGET_MACHINE "sudo tar -xzf /tmp/root-deployment.tar.gz --no-same-owner -C /root"

# run the basic setup
echo "运行基本设置: install_base_server.sh"
ssh $USER@$TARGET_MACHINE "sudo bash /root/install_base_server.sh"

# install the rke2
echo "安装rke2: install_rke2.sh"
ssh $USER@$TARGET_MACHINE "export INSTALL_RKE2_MIRROR=cn;export INSTALL_RKE2_TYPE=agent; sudo -E bash /root/install_rke2.sh"

# trust host
#echo "信任主机: "
#ssh $USER@$TARGET_MACHINE "sudo ssh root@$SERVER_NODE sleep 1;"

# join the cluster
echo "加入集群: configure_rke2_agent.sh"
ssh $USER@$TARGET_MACHINE "sudo bash /root/configure_rke2_agent.sh $SERVER_NODE"
