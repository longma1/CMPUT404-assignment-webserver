#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Long Ma
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


class MyWebServer(socketserver.BaseRequestHandler):
    def sort_request(self):
        #extracts requested file and method of the http request
        request_split = self.data.split(' ')
        #gets the method and file of the request
        method = request_split[0][2:]
        requested_file = request_split[1]
        self.requested_path=requested_file


        #returns True if it can be handled by our server, false if it can't
        if method=="GET":
            return True
        else:
            return False

    def check_path(self):
        #Checks the path requested and if the file exists or not and returns
        #different numbers depending on what file is requested
        
        #cannot go up in directory
        if '/../' in self.requested_path:
            return 0
        elif os.path.isfile('./www'+self.requested_path):
            #if the file exist return 1
            self.requested_type=self.requested_path.split('.')[1]
            return 1
        
        elif os.path.isdir('./www'+self.requested_path[:-1]) and self.requested_path[-1:]=="/":
            #if requesting a directory return 2
            return 2
        elif os.path.isdir('./www'+self.requested_path):
            #if moved then return 3
            return 3
        else:
            #if the requested path does nto exist return 0
            return 0

        return True
    def handle(self):
        self.data = str(self.request.recv(1024).strip())
        print ("Got a request of: %s\n" % self.data)
        if not self.sort_request():
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed",'utf-8'))
        requested_status=self.check_path()
        if requested_status==1:
            #handles a requested file
            
            f=open('www'+self.requested_path)
            data=f.read()
            #returns a 200 ok
            status="HTTP/1.1 200 OK\r\nContent-Type: text/{}\r\nContent-Length:{}\r\n\r\n".format(self.requested_type,str(len(data)))
            self.request.sendall(bytearray(status,'utf-8'))
            #sends the file requested
            self.request.sendall(bytearray(data,'utf-8'))
            
            self.request.close()

            
        elif requested_status==2:
            #if requested a directory
            
            f=open('www'+self.requested_path+'index.html')
            data=f.read()
            #returns a 200 ok
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length:{} \r\n\r\n".format(str(len(data))),'utf-8'))
            self.request.sendall(bytearray(data,'utf-8'))
            #return the index page
            self.request.close()

            
        elif requested_status==3:
            #if requesting a directory without / at the end
            #returns a 301
            self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation:{}/\r\n\r\n".format(self.requested_path),'utf-8'))
            self.request.close()

            
        elif requested_status==0:
            #if the requested file/directory does not exist, return a 404
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
