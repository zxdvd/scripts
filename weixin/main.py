
import hashlib
import json

from tornado import ioloop, log, web

#pretty log for tornado server
log.enable_pretty_logging()

TOKEN = 'xudong_zxdvd'

class VerifySigHandler(web.RequestHandler):
    def get(self):
        signature = self.get_argument('signature', None)
        timestamp = self.get_argument('timestamp', None)
        nonce = self.get_argument('nonce', None)
        echostr = self.get_argument('echostr', None)

        if timestamp and nonce and echostr:
            tmpList = sorted([timestamp, nonce, TOKEN])
            tmpStr = ''.join(tmpList).encode('utf-8')
            tmpStr = hashlib.sha1(tmpStr).hexdigest()

            if tmpStr == signature:
                self.write(echostr)
            else:
                self.write(json.dumps({'result':-1, 'msg':'verify failed!'}))


if __name__ == '__main__':
    settings = {'debug': True,
                'cookie_secret': 'weixinidf# D!C0kl \^%@',
                'xsrf_cookies': True}

    app = web.Application([
        (r'/', VerifySigHandler),
        ], **settings)
    app.listen(5010)
    ioloop.IOLoop.instance().start()
