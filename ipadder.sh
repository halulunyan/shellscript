#!/bin/sh
LIST="`/host.list"
NIC0="eth0"
 
IFCFG-NIC0="ifcfg-${NIC0}"
   
if [ $# -ne 1 ]; then
    echo "Please input 'setip.sh HOSTNAME'"
    echo ""
    exit 1
fi
  
if [ -z `cat $LIST | grep $1` ]; then
    echo "It did not exist in [$ LIST] within [$ 1]"
    echo ""
    exit 1
fi
  
#Host Name
HOSTNAME=`cat $LIST | grep $1 | awk 'BEGIN {FS=","} { print $1 }'`
  
#Default Gateway
GATEWAY=`cat $LIST | grep $1 | awk 'BEGIN {FS=","} { print $2 }' | awk 'BEGIN {FS="/"} {print $1}'`
  
#NIC0
NIC0_IPADDR=`cat $LIST | grep $1 | awk 'BEGIN {FS=","} { print $3 }' | awk 'BEGIN {FS="/"} {print $1}'`
NIC0_PREFIX=`cat $LIST | grep $1 | awk 'BEGIN {FS=","} { print $3 }' | awk 'BEGIN {FS="/"} {print $2}'`
NIC0_HWADDR=`ifconfig $NIC0 | grep HWaddr | awk '{print $5}'`
  
  
#create ifcfg-*
cd /etc/sysconfig/network-scripts
  
#ifcfg-NIC0
IFCFGNIC0="ifcfg-$NIC0"
echo "DEVICE=$NIC0" > $IFCFGNIC0
echo "TYPE=Ethernet" >> $IFCFGNIC0
echo "ONBOOT=yes" >> $IFCFGNIC0
echo "NM_CONTROLLED=yes" >> $IFCFGNIC0
echo "BOOTPROTO=none" >> $IFCFGNIC0
echo "IPADDR=$NIC0_IPADDR" >> $IFCFGNIC0
echo "PREFIX=$NIC0_PREFIX" >> $IFCFGNIC0
echo "GATEWAY=$GATEWAY" >> $IFCFGNIC0
echo "DEFROUTE=yes" >> $IFCFGNIC0
echo "IPV4_FAILURE_FATAL=yes" >> $IFCFGNIC0
echo "IPV6INIT=no" >> $IFCFGNIC0
echo "NAME=\"System $NIC0\"" >> $IFCFGNIC0
echo "HWADDR=$NIC0_HWADDR" >> $IFCFGNIC0
  
  
#Network Restart
/etc/init.d/network restart
  
  
cd /etc/sysconfig
echo "NETWORKING=yes" > network
echo "HOSTNAME=$HOSTNAME" >> network
echo "GATEWAY=$GATEWAY" >> network