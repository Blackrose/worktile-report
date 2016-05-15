import tornado.ioloop
import tornado.web
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class GetReport(tornado.web.RequestHandler):
    def get(self):
        self.render("do.html")

if __name__ == "__main__":
    application = tornado.web.Application([
        ("/", MainHandler),
        ("/do", GetReport),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates")
    )

    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
