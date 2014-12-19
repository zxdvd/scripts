import os
from pprint import pprint

import click
import requests
import xmltodict

keeper = 'https://keeper.suse.com/sxkeeper/feature?query='
@click.command()
@click.option('-u', '--user', prompt='Please input the username of fate',
              help='The username of fate')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-r', '--refresh', is_flag=True,
              help='Refresh the server to get the latest information')
@click.option('-q', '--query', help="Query string: "
              "like /feature[@k:id='316228']")
def login(user, password, refresh, query):

    # if refresh option is set or no fate.txt file, get data from server
    if refresh or not os.path.isfile('fate.txt'):
        #if user input a digital ID, let assume it's a fate ID
        query = "/feature[@k:id='%s']" % query if query.isdigit() else query
        if not query.startswith('/feature'):
            print('The query string must start with /feature')
            raise
        url = keeper + query
        r = requests.get(url, auth=(user, password))
        if r.status_code == requests.codes.ok:
            with open('fate.txt', 'w') as f:
                f.write(r.text)
                f.flush()
        else:
            print('Wrong query or network error!')
            raise

    with open('fate.txt', 'r') as f:
        try:
            f_dct = xmltodict.parse(f.read())
            features = f_dct.get('k:collection').get('k:object')
            #if only one feature, it'll return a dict, convert it to list
            if isinstance(features, dict):
                features = list(features)
        except AttributeError:
            print('Wrong key in xml')
            raise
        for ft in features:
            pprint(ft.get('feature'))

if __name__ == '__main__':
    login()
