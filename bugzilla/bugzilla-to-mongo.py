import datetime
from xmlrpc.client import ServerProxy

import click
from pymongo import MongoClient

prods = ['SUSE Linux Enterprise Server 12 (SLES 12)',
         'SUSE Linux Enterprise Server 11 SP3 (SLES 11 SP3)',
         'SUSE Linux Enterprise Server 11 SP4 (SLES 11 SP4)',
         'SUSE Linux Enterprise Desktop 12',
         'SUSE Linux Enterprise Desktop 11 SP3',
         'SUSE Linux Enterprise Desktop 11 SP4 (SLED 11 SP4)']

@click.command()
@click.option('--uri', default='https://apibugzilla.novell.com/xmlrpc.cgi',
              help='The uri of the xmlrpc api of bugzilla')
@click.option('-u', '--user', prompt='Please input the username of bugzilla',
              help='The username of bugzilla')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-d', '--days', default=1, help='Recent N days\' bugs')
def login(uri, user, password, days):

    #if no https in url, add it; if no user and passwd in it, add it
    if not uri.startswith('https://'):
        uri = 'https://' + uri
    if not '@' in uri:
        uri = uri.replace('https://', 'https://%s:%s@' % (user, password), 1)

    proxy = ServerProxy(uri, use_datetime=True)
    client = MongoClient('mongodb://147.2.212.204:27017/')
    db = client.bz
    prod_col = db.prods

    delta = datetime.timedelta(days=days)
    t = datetime.datetime.utcnow() - delta
    for p in prods:
        bugs = proxy.Bug.search({'product': p, 'last_change_time': t})
        if 'bugs' in bugs:
            while bugs['bugs']:
                item = bugs['bugs'].pop(0)
                # change the key id to _id to adapte mongodb's objectID
                bugid = item.pop('id')
                print(bugid)
                item['_id'] = bugid
                #get the comments of this bug and add it to dick item
                #there are very few bugs may have some encoding problems
                #and the proxy.Bug.comments will get ExpatError
                try:
                    comments = proxy.Bug.comments({'ids': [bugid]})
                except:
                    comments = None
                    print(str(bugid), 'failed to get comments')
                if comments:
                    if 'bugs' in comments and str(bugid) in comments['bugs']:
                        item.update(comments['bugs'][str(bugid)])
                prod_col.replace_one({'_id':bugid}, item, upsert=True)
                item.clear()

    client.close()

if __name__ == '__main__':
    login()
