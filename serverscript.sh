#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

apt install git, blender, python3, python3-pip, nfs-kernel-server
pip install pyfiglet
systemctl restart nfs-kernel-server


git clone htttps://github.com/julianochsenreiter/BlendIt.git

mkdir /var/blendit
echo "/var/blendit *(rw,sync,no_root_squash)" >> /etc/exports
exportfs -a
