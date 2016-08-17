#!/usr/bin/env bash

### Configs ###

#curl -L 'https://cisco.box.com/shared/static/9no4xqjtm8q05ofmsa5dhe52hv3tmof7.tgz' -o 'solenoid.tgz'

## Install Deploy Container ##

cd /misc/app_host/
sudo mkdir solenoid
sudo mv /home/vagrant/solenoid.tgz .
tar -zvxf solenoid.tgz -C solenoid/ > /dev/null
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

sleep 2m

sshpass -p "ubuntu" ssh -p 58822 -o StrictHostKeyChecking=no  -T ubuntu@11.1.1.10 "bash -s" << EOF
screen -S exabgp -dm bash -c 'cd Solenoid ; source venv/bin/activate; cd .. ; exabgp router.ini'
screen -S website -dm bash -c 'cd Solenoid ; source venv/bin/activate; cd website; python exabgp_website.py'
EOF
