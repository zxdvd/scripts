
import configparser
from xmlrpc.client import ServerProxy

import click
from pymongo import MongoClient

@click.command()
@click.option('--uri', default='https://apibugzilla.novell.com/xmlrpc.cgi',
              help='The uri of the xmlrpc api of bugzilla')
@click.option('-u', '--user', prompt='Please input the username of bugzilla',
              help='The username of bugzilla')
@click.option('-p', '--password', prompt=True, hide_input=True)
def login(uri, user, password):

    #if no https in url, add it; if no user and passwd in it, add it
    if not uri.startswith('https://'):
        uri = 'https://' + uri
    if not '@' in uri:
        uri = uri.replace('https://', 'https://%s:%s@' % (user, password), 1)

    proxy = ServerProxy(uri, use_datetime=True)

    config = configparser.ConfigParser()
    config.read('bugzilla.ini')

    bugs = proxy.Bug.search({'product':config.sections()})
    if 'bugs' in bugs:
        client = MongoClient('mongodb://147.2.212.204:27017/')
        db = client.bz
        prod_col = db.prods

        for item in bugs['bugs']: 
            item['_id'] = item.pop('id')
            prod_col.save(item)

        client.close()

if __name__ == '__main__':
    login()
