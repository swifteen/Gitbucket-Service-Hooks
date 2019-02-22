#-*- coding:utf-8 -*-
import BaseHTTPServer
import SocketServer
import CGIHTTPServer 
import logging
import json
import urllib
import urlparse
from urlparse import unquote
import send_notify

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''处理请求并返回页面'''

    # 处理一个GET请求
    def do_POST(self):
#        CGIHTTPServer.CGIHTTPRequestHandler.do_POST(self)
        logging.debug('POST %s' % (self.path))
        print( "incomming http: ", self.path )

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        content_type = int(self.headers['Content-Type']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        js_str = ""
        if('application/json' != content_type)
        #将URL编码方式的字符转换为普通字符串
            js_str = urllib.unquote(post_data[8:])
        else
            js_str = post_data
        send_notify.sendNotify(js_str)
        #js = json.loads(js_str)
        #print json.dumps(js, indent=4,ensure_ascii=False)
        #print json.dumps(js_str, indent=4)
        self.send_response(200)

#        client.close()
#----------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8083)
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(serverAddress, RequestHandler)
    server.serve_forever()
