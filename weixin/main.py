
import hashlib
import json

from lxml import etree
from tornado import ioloop, log, web

import wxapi

#pretty log for tornado server
log.enable_pretty_logging()

TOKEN = 'xudong_zxdvd'

class BaseHandler(web.RequestHandler):
    def check_sig(self):
        signature = self.get_argument('signature', None)
        timestamp = self.get_argument('timestamp', None)
        nonce = self.get_argument('nonce', None)
        echostr = self.get_argument('echostr', None)

        if timestamp and nonce and echostr:
            tmpList = sorted([timestamp, nonce, TOKEN])
            tmpStr = ''.join(tmpList).encode('utf-8')
            tmpStr = hashlib.sha1(tmpStr).hexdigest()

            if tmpStr == signature:
                return echostr
        return None

class MainHandler(BaseHandler):
    def get(self):
        check_sig = self.check_sig()
        if check_sig:
            self.write(check_sig)
        else:
            print('fail to verify signature!')

    def post(self):
        try:
            rcv_msg = etree.fromstring(self.request.body)
        except etree.XMLSyntaxError as e:
            print('invalid xml!', repr(e))
            self.finish()
        tmp_msg = {c.tag: c.text for c in rcv_msg}
        tmp_msg['ToUserName'] = tmp_msg.get('FromUserName', '')
        #a simple test, always reply a url
        tmp_msg['Content'] = 'http://www.bufeihua.cn/weixin/userinfo'
        outmsg = wxapi.reply(**tmp_msg)
        print(outmsg)
        self.write(outmsg)

class UserInfoHandler(BaseHandler):
    def get(self):
        self.redirect('/')

if __name__ == '__main__':
    settings = {'debug': True,
                'cookie_secret': 'weixinidf# D!C0kl \^%@'}

    app = web.Application([
        (r'/', MainHandler),
        (r'/userinfo', UserInfoHandler),
        ], **settings)
    app.listen(5010)
    ioloop.IOLoop.instance().start()
