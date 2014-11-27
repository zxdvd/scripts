# -*- coding: utf-8 -*-

import re, os.path
from subprocess import Popen, PIPE


def getslpsrv(cmd, filter_out=None):
    """Get a service list from a slp server.
    cmd is the command list to Popen, like ['slptool', 'findsrvs',...]
    filter_out is a list of filters ,like ['sled', 'sles']
    """

    output = []
    def str_filter():
        return list(filter(lambda s: s.lower() in str(line).lower(), filter_out))

    try:
        p = Popen(cmd, stdout=PIPE)
        for line in p.stdout.readlines():
            if (not filter_out) or str_filter():
                output.append(line)
    except Exception as e:
        print("Unexpected error: "+e.message)
    return sorted(output)

def toslpreg(slplist):
    """Convert the slp output to a PXE menu. Generate a pxe.menu file in cwd."""
    item = '{0}'\
           'tcp-port=81\n'\
           'type=server\n\n'
   
    with open('slp.reg', 'w') as f:
        for line in slplist:
            print(line)
            service = line.replace('2.207.1','2.212.204:81',1)
            service = service.replace('65535','en,65535')
            f.write(item.format(service)) 

if __name__ == "__main__":
    cmd = ["slptool", "unicastfindsrvs", "147.2.207.1", \
           "service:install.suse:http"]
    slplist = getslpsrv(cmd, ['sle-12','SLES-11-SP3','sle-11-sp3'])
    #for s in slplist: print(s)
    toslpreg(slplist)
