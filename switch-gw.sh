#! /bin/bash
set -e              #exit when error occurs

function usage {
    echo "Usage: switch-gw.sh interface [num]"
    echo ""
    echo "The first arg is the interface/device you want switch to."
    echo "The [num] is the forth part of the gateway ip address. Default is 254."
    echo "If your gateway is 192.168.1.1, you must set the [num] as 1."
    exit 1
}

function getgw {
    local device=$(ip route | head -1 | grep -oE 'dev [^ ]+' | awk '{print $2}')
    echo $device
}

function listdevice {
    local all=$(ip link | grep '^[1-9]' | awk -F: '{print $2}')
    echo $all
}

function getip {
    if [[ $# -eq 1 ]] ; then
        #the /inet / can filter lines; the sub() is sued to remove the /24 subfix
        local ip=$(ip ad show dev $1 | awk '/inet / {sub(/\/.*$/,"",$2); print $2}')
        echo $ip
    fi
}

[[ $# -eq 0 ]] && usage

dev=$1
# The second arg is the last part of the gateway addr, if not set, set it to 254 
forth_part_of_gw=${2:-254}
alldevice=$(listdevice)
#=~ test if a string is in a list; and use ! to negative it
#so would quit if a wrong interface is giving
if [[ ! $alldevice =~ $dev ]] ; then
    echo "Wrong device. Please give a device from [$alldevice]!"
    exit 1;
fi

ip=$(getip $dev)
gw=$(echo $ip | sed -e "s/[0-9]*$/$forth_part_of_gw/g")
echo "Will set default gateway to $gw"
#now delete the default route and add a new gateway
if ip route | grep 'default' ; then
    ip route del default || { echo "failed to delete default route"; exit 1; }
fi
ip route add default via $gw dev $dev && echo "Successfully changed" || echo "failed to add route"
