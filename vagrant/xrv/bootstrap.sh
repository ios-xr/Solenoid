#!/usr/bin/env bash

### Configs ###

## Install Deploy Container ##

cd /misc/app_host/
sudo mv /home/vagrant/solenoid.tgz .
tar -zvxf solenoid.tgz > /dev/null
sudo -i virsh create /home/vagrant/demo.xml

## Apply a blind config ##

source /pkg/bin/ztp_helper.sh

xrapply /home/vagrant/router_config
if [ $? -ne 0 ]; then
   echo "xrapply failed to run"
fi
xrcmd "show config failed" > /home/vagrant/config_failed_check

config_file=/home/vagrant/router_config


cat /home/vagrant/config_failed_check
grep -q "ERROR" /home/vagrant/config_failed_check

if [ $? -ne 0 ]; then
    echo "Configuration was successful!"
    echo "Last applied configuration was:"
    xrcmd "show configuration commit changes last 1"
else
    echo "Configuration Failed. Check /home/vagrant/config_failed on the router for logs"
    xrcmd "show configuration failed" > /home/vagrant/config_failed
    exit 1
fi

sshpass -p "cisco" ssh -o StrictHostKeyChecking=no -T cisco@192.168.1.2 "bash -s" << EOF
touch /home/cisco/temp.txt
screen -S exabgp -dm bash -c '/opt/exabgp-3.4.16/sbin/exabgp router.ini'
cd Solenoid/website
screen -S website -dm bash -c 'python exabgp_website.py'
EOF
