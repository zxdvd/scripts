# -*- coding: utf-8 -*-

import re, os.path
from subprocess import Popen, PIPE


def getslpsrv(cmd, filter_out):
    """Get a service list from a slp server.
    cmd is the command list to Popen, like ['slptool', 'findsrvs',...]
    filter_out is a list of filters ,like ['sled', 'sles']
    """

    output = []
    def str_filter():
        return list(filter(lambda s: s in str(line).lower(), filter_out))

    try:
        p = Popen(cmd, stdout=PIPE)
        for line in p.stdout.readlines():
            if str_filter():
                output.append(line)
    except Exception as e:
        print("Unexpected error: "+e.message)
    return sorted(output)

def topxe(slplist):
    """Convert the slp output to a PXE menu. Generate a pxe.menu file in cwd."""
   
    pattern = re.compile(r'install.suse:((\w+?):.*?dist.install/SLP/((SLE.+?)/(i386|x86_64).*?)),') 
    with open('pxe.menu', 'w') as f:
        f.write('default menu.c32\n'
                'prompt 0\n'\
                'timeout 300\n'
                'ONTIMEOUT local\n')

        for line in slplist:
            m = pattern.search(str(line))
            if m:
                print(m.group(1,2,3,4))
                install_url, install_method, path, product, arch = m.group(1,2,3,4,5)
                #print(product, arch)
                loader_path = os.path.join('images', path, 'boot', arch, 'loader/')
                kernel_path = os.path.join(loader_path, 'linux')
                initrd_path = os.path.join(loader_path, 'initrd')
                #print(kernel_path, initrd_path)
                pxeitem = 'LABEL {0}-{1}\n' \
                          '    MENU LABEL {0}-{1}\n' \
                          '    KERNEL {2}\n' \
                          '    APPEND initrd={3} install={4}\n'.format(product, arch,\
                                        kernel_path, initrd_path, install_url)
                f.write(pxeitem) 

if __name__ == "__main__":
    cmd = ["slptool", "unicastfindsrvs", "147.2.207.1", \
           "service:install.suse:ftp"]
    slplist = getslpsrv(cmd, ['desktop','server', 'sled', 'sles', 'opensuse'])
    print(slplist)
    topxe(slplist)
