
import os

from tornado import ioloop, log, web

#pretty log for tornado server
log.enable_pretty_logging()

class BaseHandler(web.RequestHandler):
    pass

class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')

class UploadHandler(BaseHandler):
    def post(self):
        allfiles = []
        nickname = self.get_body_argument('nickname')
        for f in self.request.files['img']:
            content_type = f.get('content_type', '')
            if content_type.startswith('image/'):
                filename = nickname + '-' + f['filename']
                with open('images/' + filename, 'wb') as fh:
                    fh.write(f['body'])
                    allfiles.append(filename)
        self.redirect('/list')

class ListHandler(BaseHandler):
    """list all uploaded files"""
    def get(self):
        files = os.listdir('images/')
        self.render('list.html', allfiles=files)

if __name__ == '__main__':

    TORNADO_SETTINGS = {'debug': True,
                    'cookie_secret': 'idf# &sh&RzWXD! \\^%12@@',
                    #'xsrf_cookies': True,
                    'template_path': 'templates'}

    app = web.Application([
        (r'/', IndexHandler),
        (r'/upload', UploadHandler),
        (r'/list', ListHandler),
        (r'/static/(.*)', web.StaticFileHandler, {'path': './static'}),
        ], **TORNADO_SETTINGS)
    app.listen(5050)
    ioloop.IOLoop.instance().start()
