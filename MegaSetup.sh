#!/bin/sh
basedir="/tmp/"
zabbixdir="/etc/zabbix/"
unzip ${basedir}MegaRAID-Monitoring.zip
rpm -ivh ${basedir}MegaRAID-Monitoring/linux/MegaCli-8.07.14-1.noarch.rpm
cp -r ${basedir}MegaRAID-Monitoring/linux/scripts /etc/zabbix/scripts
cp -r ${basedir}MegaRAID-Monitoring/linux/conf/userparameter_MegaRAID.conf /etc/zabbix/zabbix_agentd.d/
chmod +x ${zabbixdir}scripts/*.sh
chown -R zabbix:zabbix ${zabbixdir}scripts/
sed -i 's#Defaults    requiretty#\#Defaults    requiretty#' /etc/sudoers
pkill zabbix
/usr/sbin/zabbix_agentd
