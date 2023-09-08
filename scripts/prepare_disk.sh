#!/bin/bash

DEVICE=$1
echo ">>>>>> DEVICE = $DEVICE"

set -e
echo ">>>>>> Wait for 10 seconds"
sleep 10;

echo ">>>>>> formatting"
mkfs.ext4 /dev/$DEVICE

sleep 10;

DEVICE_UUID=$(lsblk -o NAME,UUID | grep $DEVICE | awk '{print $2}')
echo ">>>>>> DEVICE_UUID = $DEVICE_UUID"

echo ">>>>>> creating mount point"
mkdir /mnt/$DEVICE

echo ">>>>>> editing /etc/fstab"
echo "UUID=$DEVICE_UUID /mnt/$DEVICE                       ext4     defaults        0 0" >> /etc/fstab

systemctl daemon-reload
mount -a