#!/usr/bin/python3

from socket import *
from collections import namedtuple

class TCP_IPv4_ClientSocket:
    """
    A client socket instance for a single HTTP request
    Socket closes after the transaction is complete

    """


    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        # request
        self.req = None
        self._reqTuple = namedtuple('Request', ['method', 'url', 'ver', 'body'])
        # response
        self.res = b''

    def join_res(self, header, body):
        self.res = (header + '\r\n' + body + '\r\n').encode()

    def receive(self, byte_size):
        """ Receives request from client side and returns the parsed request """

        try:
            raw_msg = self.sock.recv(byte_size).decode()
            return self.parse(raw_msg)

        except Exception as e:
            print(f'{self.addr}: {str(e)}')
            header='HTTP/1.1 500 INTERNAL SERVER ERROR'
            self.join_res(header=header, body='')
            print(f'{self.addr}: {header}')
            self.sock.send(self.res)
            self.close()

    def parse(self, raw_msg):
        """ Parses request into a named tuple and returns it """
        try:
            split_msg = raw_msg.split('\r\n')

            # Parse the request line
            # TODO: this is just a simple parse for demo purposes. Make it more robust!
            request_line = split_msg[0].split()
            method = request_line[0]
            url = request_line[1]
            version = request_line[2]

            # TODO: Parse the header lines

            #Parse the entity body
            body = split_msg[-1]

            self.req = self._reqTuple(method=method, url=url, ver=version, body=body)
            return self.req

        except Exception as e:
            print(f'{self.addr}: {str(e)}')
            header='HTTP/1.1 400 BAD REQUEST'
            self.join_res(header=header, body='')
            print(f'{self.addr}: {header}')
            self.sock.send(self.res)
            self.close()
            return 1

    def handle(self, req):
        """ A one for all HTTP GET/POST handler function """
        try:
            if req.method == 'GET':
                header = 'HTTP/1.1 200 OK'

                # Retrieve file from fs
                with open('pages/'+req.url[1:], 'r') as f:
                    req_body = f.read()
                    self.join_res(header=header, body=req_body)

                print(f'{self.addr}: {header}')
                self.sock.send(self.res)

            else:
                header='HTTP/1.1 404 NOT FOUND'
                self.join_res(header=header, body='')
                print(f'{self.addr}: {header}')
                self.sock.send(self.res)

        except IOError as e:
            header='HTTP/1.1 404 NOT FOUND'
            self.join_res(header=header, body='')
            print(f'{self.addr}: {header}')
            self.sock.send(self.res)

        except Exception as e:
            header='HTTP/1.1 500 INTERNAL SERVER ERROR'
            self.join_res(header=header, body='')
            print(f'{self.addr}: {header}')
            self.sock.send(self.res)

        finally:
            self.close()

    def close(self):
        print(f'{self.addr}: Closing socket\n')
        self.sock.close()
