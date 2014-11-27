#! /bin/sh

if [ -z "$1" ]; then
    printf "%20s  |  %-20s  |  %-20s\n" "ID" "NAME" "IP"
    
else
    IP=$(docker inspect --format "{{.NetworkSettings.IPAddress}}" "$1")
    if [ -z "$IP" ]; then
        exit 1
    else
        echo $IP
    fi
fi
