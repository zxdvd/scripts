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

#the strings to control the terminal colors
term_color = {'blk': '\033[30m', 'green': '\033[32m', 'red': '\033[31m',
              'reset': '\033[0m'}

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

        result['text'] = bug.get('text', '')
        result['count'] = bug.get('count', '')

        if 'comments' in cols and bug.get('comments'):
            result['comments'] = []
            for comment in bugs_parser(bug.get('comments'), ()):
                result['comments'].append(comment)
        yield result

class HelpHandler(tornado.web.RequestHandler):
    
    def get(self):
        help = '''Help:
        curl 147.2.212.204/N : recent N days' bugs
        curl 147.2.212.204/sles(or sled, sled12)/N : N days' bugs
        curl 147.2.212.204/xdzhang@suse.com : bug reported by xdzhang
        curl 147.2.212.204/btrfs : btrfs related bugs
        curl 147.2.212.204/BUG_ID : details about a specific bug
        '''
        self.write(help+'\n')

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
            color = True
            for c in result['comments']:
                c.update(term_color)
                c['clr'] = c['green'] if color else c['red']
                out += (u'{clr}comment{count} @{creator}\n').format(**c)
                out += (u'{text}{reset}\n').format(**c)
                color = not color
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
                i.update(term_color)
                output = u'{id:6} {green}{prod: <9}{reset}| {summ}'.format(**i)
                self.write(output+'\n')
        else:
            bugs = prods.find({'$text': {'$search': word}})
            results = bugs_parser(bugs, ())
            for i in results:
                i.update(term_color)
                out = (u'{id:6} {red}@{creator: <13} {green}{prod: <9}{reset}|'
                ' {summ}').format(**i)
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
            i.update(term_color)
            out = (u'{id:6} {red}@{creator: <13} {green}{prod: <9}{reset}|'
            ' {summ}').format(**i)
            self.write(out+'\n')

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', HelpHandler),
        (r'/?([\d\w]*)?/([0-9]{1,2})', NDaybugHandler),
        (r'/([0-9]{6})/*', BugidHandler),
        (r'/([@\.\w]+)', SearchHandler),
        ], debug=True)
    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
