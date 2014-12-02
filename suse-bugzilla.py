
import configparser
import json
import os
from base64 import b64encode
from pprint import pprint
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

def parse_config():
    config = configparser.ConfigParser()
    config.read('bugzilla.ini')

def parser(data):
    dct = {}
    for lst in data:
            ver = lst.get('version')
            if lst.get('resolution') in ['DUPLICATE', 'INVALID']:
                continue
            if ver:
                d = dct.setdefault(ver, {'id':[]})         #nested dict
                count = d.setdefault('count', 0)
                d['count'] += 1
                d['id'].append(lst.get('id'))

    x_t, y = [], []
    for k in sorted(dct, key=lambda k: dct[k]['id'][0]):
        print(k)
        x_t.append(k[:8])
        y.append(dct[k]['count'])
    x = [i for i in range(len(x_t))]
    plt.xticks(x, x_t)
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

    if refresh or not os.path.isfile('bugs.json'):
        bugs = proxy.Bug.search({'product':'SUSE Linux Enterprise Desktop 12'})
        if 'bugs' in bugs:
            with open('bugs.json', 'w') as f:
                json.dump(bugs['bugs'], f,
                    default=lambda o: str(o) if isinstance(o, DateTime) else o)
                f.flush()

    with open('bugs.json', 'r') as f:
        data = json.load(f)
        parser(data)

    #parse_config()

if __name__ == '__main__':
    login()
