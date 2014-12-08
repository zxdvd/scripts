from xmlrpc.client import ServerProxy

import click
from pymongo import MongoClient

prods = ['SUSE Linux Enterprise Server 12 (SLES 12)',
         'SUSE Linux Enterprise Server 11 SP3 (SLES 11 SP3)',
         'SUSE Linux Enterprise Desktop 12',
         'SUSE Linux Enterprise Desktop 11 SP3']

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
    client = MongoClient('mongodb://147.2.212.204:27017/')
    db = client.bz
    prod_col = db.prods

    for p in prods:
        bugs = proxy.Bug.search({'product': p})
        if 'bugs' in bugs:
            for item in bugs['bugs']:
                # change the key id to _id to adapte mongodb's objectID
                id = item.pop('id')
                item['_id'] = id
                #get the comments of this bug and add it to dick item
                #there are very few bugs may have some encoding problems
                #and the proxy.Bug.comments will get ExpatError
                try:
                    comments = proxy.Bug.comments({'ids': [id]})
                except:
                    comments = None
                    print(id)
                if comments:
                    if 'bugs' in comments and str(id) in comments['bugs']:
                        item.update(comments['bugs'][str(id)])
                prod_col.save(item)

    client.close()

if __name__ == '__main__':
    login()
