
from base64 import b64encode
from pprint import pprint
from xmlrpc.client import SafeTransport, ServerProxy

import click

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

@click.command()
@click.option('--uri', default='https://apibugzilla.novell.com/xmlrpc.cgi',
              help='The uri of the xmlrpc api of bugzilla')
@click.option('-u', '--user', prompt='Please input the username of bugzilla',
              help='The username of bugzilla')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-v', '--verbose', is_flag=True)
def login(uri, user, password, verbose):
    trans = AuthTransport(user=user, password=password)
    proxy = ServerProxy(uri, transport=trans, verbose=verbose)
    pprint(proxy.Bug.comments({'ids':901273}))


if __name__ == '__main__':
    login()
