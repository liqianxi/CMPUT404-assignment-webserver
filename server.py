#  coding: utf-8 
import socketserver
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
#
# Copyright 2021 Qianxi Li
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# stolen from Emalsha https://emalsha.wordpress.com/author/emalsha/
# From emalsha.wordpress.com
# https://emalsha.wordpress.com/2016/11/24/how-create-http-server-using-python-socket-part-ii/


import re
import os
import requests


not_found_html = '''
<!DOCTYPE html>
    <html>
        <body>
            <h2>Error 404: File not found</h2>
        </body>
    </html>'''

method_not_allowed ='''
<!DOCTYPE html>
    <html>
        <body>
            <h2>405 Method Not Allowed</h2>
        </body>
    </html>'''

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()

        # get the first line of the request
        header_firstline = self.data.decode().split("\n")[0]

        # get the request file path
        file_requested_path = header_firstline.split(" ")[1]

        # get the method it use
        method = header_firstline.split(" ")[0]

        encode_type = "utf-8"
        response_header = ""
        response = ""
        file_name = ""
        root_folder = (os.sep 
                       + "www" 
                       + os.sep)
        folder_path = os.path.dirname(os.path.abspath(__file__))
        full_file_path = ""
        html_file_name = "index.html"
        methods_not_handle = ["POST", 
                              "PUT", 
                              "DELETE"]

        if method == "GET":
            # now start to check which file has been requested.
            condition = (file_requested_path.startswith(os.sep) and not 
                         file_requested_path.endswith(os.sep) and 
                         os.path.isdir(folder_path 
                                       + root_folder 
                                       + file_requested_path[1:]))

            if (file_requested_path == os.sep or
               (file_requested_path.startswith(os.sep) and
                file_requested_path.endswith(os.sep))):
                # handle case like: http://127.0.0.1:8080/deep/
                # valid directory path, use index.html inside instead
                # set the open file's path
                full_file_path = (folder_path 
                                  + root_folder 
                                  + file_requested_path[1:] 
                                  + html_file_name)
                file_name = html_file_name

                # set the header's first line to 200 OK
                response_header = "HTTP/1.1 200 OK\n"
                
            elif condition:
                # handle case like: http://127.0.0.1:8080/deep
                # redirect link using 301
                # set the open file's path
                response_header = "HTTP/1.1 301 Moved Permanently\n"

                # redirect to show this file
                full_file_path = (folder_path 
                                  + root_folder 
                                  + file_requested_path[1:]
                                  + os.sep 
                                  + html_file_name)

                # set redirect address                  
                response_header += ("Location: http://127.0.0.1:8080/"
                                    + file_requested_path[1:] 
                                    + os.sep 
                                    + "\n")

                file_name = html_file_name
                
            else:
                # handle case like: http://127.0.0.1:8080/deep/index.html
                # set the open file's path
                full_file_path = (folder_path 
                                  + root_folder 
                                  + file_requested_path)
                file_name = [i for i in file_requested_path.split(os.sep) \
                             if i][-1]

                # here we can set the header
                response_header = "HTTP/1.1 200 OK\n"

            try:
                # try to open the file on that path, read it, then close it.
                request_file = open(full_file_path, 'rb')
                response = request_file.read()
                request_file.close()
                
                # now check file_type
                if re.search(".html\Z", file_name):
                    # case when the file is html
                    mime = "text/html"

                elif(re.search(".css\Z", file_name)):
                    # case when the file is css
                    mime = "text/css"
              
                response_header += "Content-Type: {}".format(mime) + "\n\n"

            except Exception as e:
                response_header = "HTTP/1.1 404 Not Found\n"
                response_header += "Content-Type: text/html\n"
                response = not_found_html.encode(encode_type)
    
        elif method in methods_not_handle:
            response_header = "HTTP/1.1 405 Method Not Allowed\n"
            response_header += "Content-Type: text/html\n"
            response = method_not_allowed.encode(encode_type)
        
        # concat the header and the body to get the full response
        full_response = response_header.encode(encode_type) + response

        # send out the response to the client
        self.request.sendall(full_response)

        # for indentification purpose
        self.request.sendall("Qianxi's server 1 ".encode(encode_type))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
