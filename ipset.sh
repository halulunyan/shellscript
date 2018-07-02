#!/bin/sh
LIST="./host.list"
NIC0="eth0"
NIC1="eth1"
 
SCRIPT_DIR=`dirname $0`
cd $SCRIPT_DIR
 
MYSERIAL_CD=`dmidecode | grep UUID | awk 'BEGIN { FS=": "; } { print $2; }' | sed -e "s/-//g"`
 
IFCFGNIC0="ifcfg-${NIC0}"
IFCFGNIC1="ifcfg-${NIC1}"
 
if [ -z `cat $LIST | grep $MYSERIAL_CD` ]; then
    echo "It did not exist in [$ LIST] within [$ MYSERIAL_CD]"
    echo ""
    exit 1
fi
 
#Host Name
HOSTNAME=`cat $LIST | grep $MYSERIAL_CD | awk 'BEGIN {FS=","} { print $1 }'`
 
#Default Gateway
GATEWAY=`cat $LIST | grep $MYSERIAL_CD | awk 'BEGIN {FS=","} { print $3 }' | awk 'BEGIN {FS="/"} {print $1}'`
 
#NIC0
NIC0_IPADDR=`cat $LIST | grep $MYSERIAL_CD | awk 'BEGIN {FS=","} { print $4 }' | awk 'BEGIN {FS="/"} {print $1}'`
NIC0_PREFIX=`cat $LIST | grep $MYSERIAL_CD | awk 'BEGIN {FS=","} { print $4 }' | awk 'BEGIN {FS="/"} {print $2}'`
NIC0_HWADDR=`ifconfig $NIC0 | grep HWaddr | awk '{print $5}'`
 
#NIC1
NIC1_IPADDR=`cat $LIST | grep $MYSERIAL_CD | awk 'BEGIN {FS=","} { print $5 }' | awk 'BEGIN {FS="/"} {print $1}'`
NIC1_PREFIX=`cat $LIST | grep $MYSERIAL_CD | awk 'BEGIN {FS=","} { print $5 }' | awk 'BEGIN {FS="/"} {print $2}'`
NIC1_HWADDR=`ifconfig $NIC1 | grep HWaddr | awk '{print $5}'`
 
#create ifcfg-*
cd /etc/sysconfig/network-scripts
 
#ifcfg-NIC0
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
 
#ifcfg-NIC1
echo "DEVICE=$NIC1" > $IFCFGNIC1
echo "TYPE=Ethernet" >> $IFCFGNIC1
echo "ONBOOT=yes" >> $IFCFGNIC1
echo "NM_CONTROLLED=yes" >> $IFCFGNIC1
echo "BOOTPROTO=none" >> $IFCFGNIC1
echo "IPADDR=$NIC1_IPADDR" >> $IFCFGNIC1
echo "PREFIX=$NIC1_PREFIX" >> $IFCFGNIC1
echo "DEFROUTE=yes" >> $IFCFGNIC1
echo "IPV4_FAILURE_FATAL=yes" >> $IFCFGNIC1
echo "IPV6INIT=no" >> $IFCFGNIC1
echo "NAME=\"System $NIC1\"" >> $IFCFGNIC1
echo "HWADDR=$NIC1_HWADDR" >> $IFCFGNIC1
 
#Network Restart
/etc/init.d/network restart
 
cd /etc/sysconfig
echo "NETWORKING=yes" > network
echo "HOSTNAME=$HOSTNAME" >> network
echo "GATEWAY=$GATEWAY" >> network