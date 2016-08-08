#!/usr/bin/env bash

curl -L https://github.com/Exa-Networks/exabgp/archive/3.4.16.tar.gz | sudo tar zx -C /opt/  > /dev/null

cp /vagrant/devbox/exabgp-router-conf.ini /usr/local/etc/exabgp-router-conf.ini
cp /vagrant/devbox/adv.py /usr/local/bin/adv.py
chmod 777 /usr/local/etc/exabgp-router-conf.ini /usr/local/bin/adv.py

screen -S exabgp -dm bash -c 'sudo env exabgp.tcp.bind="192.168.1.3" exabgp.tcp.port=179 /opt/exabgp-3.4.16/sbin/exabgp /usr/local/etc/exabgp-router-conf.ini'
