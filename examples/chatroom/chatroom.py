from os import path as op

import tornado.web
import tornadio
import tornadio.router
import tornadio.server

ROOT = op.normpath(op.dirname(__file__))

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render("index.html")

class ChatConnection(tornadio.SocketConnection):
    # Class level variable
    participants = set()

    def on_open(self, *args, **kwargs):
        self.participants.add(self)
        self.send("Welcome!")

    def on_message(self, message):
        print 'Msg %s' % message
        for p in self.participants:
            p.send(message)

    def on_close(self):
        print 'Close'
        self.participants.remove(self)
        for p in self.participants:
            p.send("A user has left.")

#use the routes classmethod to build the correct resource
ChatRouter = tornadio.get_router(ChatConnection, "socket.io/*")

#configure the Tornado application
application = tornado.web.Application(
    [(r"/", IndexHandler), ChatRouter.route()],
    enabled_protocols = ['websocket',
                         'flashsocket',
                         'xhr-multipart',
                         'xhr-polling'],
    flash_policy_port = 843,
    flash_policy_file = op.join(ROOT, 'flashpolicy.xml'),
    socket_io_port = 8888
)

if __name__ == "__main__":
    tornadio.server.SocketServer(application)

