
import itertools
import os.path
from lxml import html
import requests

def getproduct(archs=['x86_64','i386'],medias=['DVD1'],flt=['sled']):
    """Will return a generator of reachable product."""
    base_url = 'http://147.2.207.1/dist/install/SLP/'
    page = requests.get(base_url)
    tree = html.fromstring(page.text)
    #use xpath to get all the dirs of the http server page
    sle = tree.xpath('//img[@alt="[DIR]"]/following-sibling::a[@href]')
    
    if not len(sle):
        print('Something get wrong, no products found!')
        raise
    
    #get all combination of product, arch and media, then filter the usable one
    urls = itertools.product([i.get('href') for i in sle], archs, medias)
    for url in urls:
        prod, arch, media = url
        if any(s in prod.lower() for s in flt):
            rel_url = os.path.join(prod, arch, media, 'boot', arch, 'loader/')
            url = base_url + rel_url
            r = requests.head(url)
            if r.status_code == requests.codes.ok:
                label = prod[:-1] + '-' + arch + '-' + media
                print(url)
                yield label, url

def topxe(urls):
    """Convert the slp output to a PXE menu. Generate a pxe.menu file in cwd."""
   
    with open('pxe.menu', 'w') as f:
        f.write('default menu.c32\n'
                'prompt 0\n'\
                'timeout 300\n'
                'ONTIMEOUT local\n')

        for label, url in urls:
            if 'SLP/' in url:
                rel_path = url.split('SLP/')[1]
                ploader = os.path.join('images', rel_path)
                repo = url.split('/boot/')[0]
                pxeitem = 'LABEL {0}\n' \
                          '    MENU LABEL {0}\n' \
                          '    KERNEL {1}linux\n' \
                          '    APPEND initrd={1}initrd install={2}\n'.format(
                                  label, ploader, repo)
                f.write(pxeitem) 

if __name__ == '__main__':
    urls = getproduct(flt=['desktop','server', 'sled', 'sles', 'opensuse'])
    if urls:
        topxe(urls)
