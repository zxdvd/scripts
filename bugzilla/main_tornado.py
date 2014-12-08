import datetime

import tornado.ioloop
import tornado.web
from pymongo import MongoClient


prod_alias = {'SUSE Linux Enterprise Server': 'sles',
              'SUSE Linux Enterprise Desktop': 'sled',
              'SUSE Linux Enterprise Server 12 (SLES 12)': 'sles12',
              'SUSE Linux Enterprise Server 11 SP3 (SLES 11 SP3)': 'sles11sp3',
              'SUSE Linux Enterprise Desktop 12': 'sled12',
              'SUSE Linux Enterprise Desktop 11 SP3': 'sled11sp3'}
#let the value be a key of the dict
prod_alias.update({v:k for (k,v) in prod_alias.items()})

client = MongoClient('mongodb://147.2.212.204:27017/')
prods = client.bz.prods

def bugs_parser(bugs,cols):

    for bug in bugs:
        result = {}
        result['id'] = bug.get('_id')
        result['summ'] = bug.get('summary')
        tmp = bug.get('product')
        result['prod'] = prod_alias.get(tmp, 'others')
        tmp = bug.get('creator')
        result['creator'] = tmp.split('@', 1)[0] if tmp else None

        result['text'] = bug.get('text')
        result['count'] = bug.get('count')

        if 'comments' in cols and bug.get('comments'):
            result['comments'] = []
            for comment in bugs_parser(bug.get('comments'), ()):
                result['comments'].append(comment)
        yield result

class BugidHandler(tornado.web.RequestHandler):
    
    def get(self, id):
        bug = prods.find_one({'_id': int(id)})
        result = bugs_parser([bug], ('comments'))
        result = next(result)
        out = (u'https://bugzilla.suse.com/show_bug.cgi?id={id}\n'
                'creator: {creator}\n'
                'product: {prod}\n'
                'summary: {summ}\n').format(**result)
        if result.get('comments', None):
            out += u'comments:\n'
            for c in result['comments']:
                out += (u'\e[0;31m==comment{count} @{creator}==\e[0;30m\n').format(**c)
                out += (u'{text}\n').format(**c)
        self.write(out)

class SearchHandler(tornado.web.RequestHandler):
    '''If @ in the string, assume it as a user's email and return all bugs
    created by him. Otherwise, take it as a ordinary string and return all bugs
    contained this string.'''

    def get(self, word):
        if '@' in word:
            bugs = prods.find({'creator': word})
            results = bugs_parser(bugs, ())
            for i in results:
                output = u'{id:6} {prod: <9}| {summ}'.format(**i)
                self.write(output+'\n')
        else:
            bugs = prods.find({'$text': {'$search': word}})
            results = bugs_parser(bugs, ())
            for i in results:
                out = u'{id:6} @{creator: <13} {prod: <9}| {summ}'.format(**i)
                self.write(out+'\n')

class NDaybugHandler(tornado.web.RequestHandler):
    '''/n (n=1~99): all bugs of recent n days'''
    '''/sles(sled, sles11sp3)/n: all sles bugs of recent n days'''

    def get(self, prod, n):
        query = {}
        if prod and prod in prod_alias:
            if prod.isalpha():
                query['classification'] = prod_alias[prod]
            else:
                query['product'] = prod_alias[prod]
        if n:
            delta = datetime.timedelta(days=int(n))
            t = datetime.datetime.utcnow() - delta
            query['creation_time'] = {'$gt': t}
        print(query)
        bugs = prods.find(query)
        results = bugs_parser(bugs, ())
        for i in results:
            out = u'{id:6} @{creator: <13} {prod: <9}| {summ}'.format(**i)
            self.write(out+'\n')

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', tornado.web.RedirectHandler, {'url': '/1'}),
        (r'/?([\d\w]*)?/([0-9]{1,2})', NDaybugHandler),
        (r'/([0-9]{6})/*', BugidHandler),
        (r'/([@\.\w]+)', SearchHandler),
        ], debug=True)
    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
