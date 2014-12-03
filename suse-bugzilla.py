
import configparser
import json
import os
from base64 import b64encode
from collections import OrderedDict
from xmlrpc.client import SafeTransport, ServerProxy, DateTime

import click
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import numpy as np

class AuthTransport(SafeTransport):
    '''Inherited the Transport class, add an authentication header'''

    def __init__(self, *args, **kwargs):
        '''Get the username and password and made it a BASE64 encoded header'''

        user = kwargs.pop('user', None)
        password = kwargs.pop('password', None)
        auth_str = bytes(user+':'+password, 'utf-8')
        auth_str = b64encode(auth_str).decode('ascii')
        self._auth_header = 'Basic %s' % auth_str

        super(AuthTransport, self).__init__(*args, **kwargs)

    def send_headers(self, connection, headers):
        '''Override this function in the parent to add the auth_header'''

        headers.append(('Authorization', self._auth_header))
        for key, val in headers:
            connection.putheader(key, val)


def parser(data, config):
    dct = {}
    for section in config.sections():
        sec_dct = {}
        for item in config[section]:
            sec_dct.setdefault(item,
                    {'time':config[section][item], 'new':0, 'fix':0})
        sec_dct = OrderedDict(sorted(sec_dct.items(),
            key=lambda x:x[1]['time']))
        dct.update({section: sec_dct})
    print(dct)

    for lst in data:
            if lst.get('resolution') in ['DUPLICATE', 'INVALID']:
                continue
            prod = lst.get('product')
            if prod:
                prod_dct = dct.get(prod)
                ctime = str(lst.get('creation_time'))
                ctime = '-'.join([ctime[:4], ctime[4:6], ctime[6:8]])

                for (k, v) in prod_dct.items():
                    if v['time'] > ctime:
                        prod_dct[k]['new'] += 1
                        break

                if lst.get('resolution') in ['FIXED', 'WORKSFORME', 'WONTFIX']:
                    mtime = str(lst.get('last_change_time'))
                    #convert the 20130529 style time to 2013-05-29
                    mtime = '-'.join([mtime[:4], mtime[4:6], mtime[6:8]])
                    for (k,v) in prod_dct.items():
                        if v['time'] > mtime:
                            prod_dct[k]['fix'] += 1
                            break

    xaxis = ''
    for (k, v) in dct.items():
        print(k, v)
        xaxis = k if len(v) > len(dct.get(xaxis, '')) else xaxis
    x_tick = [k for k in dct[xaxis].keys()]
    print(x_tick)
    x = [i for i in range(len(x_tick))]
    plt.xticks(x, x_tick)

    for (k, v) in dct.items():
        y = []
        for k1 in x_tick:
            tmp_d = v.get(k1, None)
            if tmp_d and tmp_d['fix']:
                y.append(tmp_d['new']/tmp_d['fix'])
            else:
                y.append(None)
        plt.plot(x, y)
    plt.show()


@click.command()
@click.option('--uri', default='https://apibugzilla.novell.com/xmlrpc.cgi',
              help='The uri of the xmlrpc api of bugzilla')
@click.option('-u', '--user', prompt='Please input the username of bugzilla',
              help='The username of bugzilla')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-r', '--refresh', is_flag=True,
              help='Refresh the server to get the latest information')
@click.option('-v', '--verbose', is_flag=True)
def login(uri, user, password, refresh, verbose):

    trans = AuthTransport(user=user, password=password)
    proxy = ServerProxy(uri, transport=trans, verbose=verbose)

    config = configparser.ConfigParser()
    config.read('bugzilla.ini')

    if refresh or not os.path.isfile('bugs.json'):
        bugs = proxy.Bug.search({'product':config.sections()})
        if 'bugs' in bugs:
            with open('bugs.json', 'w') as f:
                json.dump(bugs['bugs'], f,
                    default=lambda o: str(o) if isinstance(o, DateTime) else o)
                f.flush()

    with open('bugs.json', 'r') as f:
        data = json.load(f)
        parser(data, config)

if __name__ == '__main__':
    login()
