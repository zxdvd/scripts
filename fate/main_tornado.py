import datetime

import tornado.ioloop
import tornado.web
from pymongo import MongoClient


prod_alias = {'22324': 'sles11sp4',
              '22325': 'sled11sp4'}
#let the value be a key of the dict
prod_alias.update({v:k for (k,v) in prod_alias.items()})

#the strings to control the terminal colors
term_color = {'blk': '\033[30m', 'green': '\033[32m', 'red': '\033[31m',
              'reset': '\033[0m'}

client = MongoClient('mongodb://147.2.212.204:27017/')
ft = client.fate.fates

class HelpHandler(tornado.web.RequestHandler):
    
    def get(self):
        help = '''Help:
        curl 147.2.212.204/fate/sled/btrfs : btrfs related features
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

class MainHandler(tornado.web.RequestHandler):
    '''All fates of a specific products, like sled11sp4.'''

    def get(self, prod):
            fates = ft.find({'productcontext.product.productid':
                prod_alias[prod]}, {'title': 1, 'productcontext': 1})
            for fate in fates:
                prods = fate['productcontext']
                prods = [prods] if not isinstance(prods, list) else prods
                for p in prods:
                    if p['product']['productid'] == prod_alias.get(prod):
                        status = tuple(p['status'])[0]
                        break
                if status in ['rejected', 'duplicate']:
                    continue
                out = {'_id': fate['_id'], 'title': fate['title'],
                        'status': status}
                out.update(term_color)
                self.write((u'{_id:6} {red}@{status: <15} {reset}|'
                ' {title}\n').format(**out))

if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', HelpHandler),
        (r'/([0-9]{6})/*', BugidHandler),
        (r'/([\w]+)', MainHandler),
        ], debug=True)
    app.listen(8001)
    tornado.ioloop.IOLoop.instance().start()
