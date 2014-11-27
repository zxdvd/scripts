#! /bin/bash

# This script will find all ISOs of a folder then mount these ISOs to 
# /tmp/mount/1,2,3,4...
# And it will start python server (python2.7 -m SimpleHTTPServer) at all these
# mounted directories. The server port is increased from 8101
# So you get online repos of these ISOs via http://localhost:810X

function usage {
    echo "Usage: mount-iso [OPTIONS] PATH"
    echo -e  "\tmount all isos to /tmp/mount/NUM and setup python http server"
    echo
    echo "Options:"
    echo -e "  -u|--umount|--unmount\t kill all servers and umount all"
    echo -e "  -p|--print\t print the iso and mounted dir and http server port"
    echo
    exit $1
}

function unmount {
    #first kill all python server (ports from 8100)
    pkill -f "SimpleHTTPServer.*81" && echo "python server killed"
    mounted=$(mount | grep '/tmp/mount/' | awk '{print $3}')
   for file in $mounted
   do
        umount $file && echo "$file umounted" || echo "fail to umount $file"
   done

   exit 0
}

printall=1
while [ $# -gt 0 ] ; do
    case "$1" in 
    -h|--help)  usage 0 ;;
    -u|--umount|unmount)  unmount; exit 0;;
    -p|--print) printall=1; shift ;;
    --) shift; break    ;;
    -*) echo "Wrong option!" ; usage 1;;
    *) break ;;
    esac
done

[ $1 ] && dir=$1 || dir=/dev/null
a=1
port=8100
for isofile in $(find $dir -type f -iname '*.iso')
do
    ## mkdir and then mount the iso files
    [ -d /tmp/mount/$a ] || mkdir  -p /tmp/mount/$a
    mount $isofile  /tmp/mount/$a
    if [ $? -eq 0 ] ; then
        ((port++))
        cd /tmp/mount/$a && python2.7 -m SimpleHTTPServer $port &
    fi
    ((a++))
    [ $a -gt 20 ] && echo "Too much isos!" && exit 1
done

if [ $printall -eq 1 ] ; then
   printf "%-70s | %-15s | %-10s\n" "ISO-NAME" "MOUNTED-DIR" "SEVER-PORT"
   mount |  awk '/tmp.mount/ {print $1" "$3}'| while read line
   do
       iso=$(echo $line | cut -d' ' -f1)
       iso=$(basename $iso .iso)
       dir=$(echo $line |cut -d' ' -f2)
       pid=$(lsof $dir 2>/dev/null | awk '/python/ {print $2}')
       port=$(cat /proc/$pid/cmdline)
       port=${port: -4}
       printf "%-70s | %-15s | %-10s\n" $iso $dir $port
   done
   exit 0
fi

case $# in
0)
usage 1; shift ;;
esac

exit 0
