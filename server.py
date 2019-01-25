#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def sort_request(self):
        request_split = self.data.split(' ')
        method = request_split[0][2:]
        requested_file = request_split[1]
        self.requested_path=requested_file
    
        if method=="GET":
            return True
        else:
            return False

    def check_path(self):
        if '/../' in self.requested_path:
            return 0
        elif os.path.isfile('./www'+self.requested_path):
            self.requested_type=self.requested_path.split('.')[1]
            return 1
        
        elif os.path.isdir('./www'+self.requested_path[:-1]) and self.requested_path[-1:]=="/":
            return 2
        elif os.path.isdir('./www'+self.requested_path):
            return 3
        else:
            return 0

        return True
    def handle(self):
        self.data = str(self.request.recv(1024).strip())
        print ("Got a request of: %s\n" % self.data)
        if not self.sort_request():
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed",'utf-8'))
        requested_status=self.check_path()
        if requested_status==1:
            f=open('www'+self.requested_path)
            data=f.read()
            status="HTTP/1.1 200 OK\r\nContent-Type: text/{}\r\nContent-Length:{}\r\n\r\n".format(self.requested_type,str(len(data)))
            self.request.sendall(bytearray(status,'utf-8'))
            self.request.sendall(bytearray(data,'utf-8'))
            
            self.request.close()
        elif requested_status==2:
            f=open('www'+self.requested_path+'index.html')
            data=f.read()
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length:{} \r\n\r\n".format(str(len(data))),'utf-8'))
            self.request.sendall(bytearray(data,'utf-8'))
            self.request.close()
        elif requested_status==3:
            self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation:{}/\r\n\r\n".format(self.requested_path),'utf-8'))
            self.request.close()
        elif requested_status==0:
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found",'utf-8'))
            self.request.close()
            
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
