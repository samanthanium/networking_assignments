#!/usr/bin/python3

from socket import *
from collections import namedtuple
from ClientSocket import TCP_IPv4_ClientSocket
from concurrent.futures import ThreadPoolExecutor
import sys

class TCP_IPv4_ServerSocket:
    """ 
    Server socket instance which keeps track of client instances 
    
    Attributes
    ---------
    sock = socket(..., ...)
        holds a socket instance
    port_number = int
        an integer specifying the port number to listen to. Default is 8080
        for development purposes.
    max_queues = int
        an integer specifying how many connection requests the server socket
        may queue up to
    client_sockets = Set
        keeps track of ongoing client socket connections

    Methods
    -------
    listen()
        Binds socket instance to the port and starts listening as a server 

    loop()
        Continuously accepts connections from clients and creates separate
        thread instances for each of the client sockets

    close()
        Shuts down server socket
    """
    
    def __init__(self, port_number=8080, max_queues=5):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.port = port_number
        self.max_queues = max_queues
        self.executor = ThreadPoolExecutor(max_workers=max_queues)

    def listen(self):
        try:
            self.sock.bind(('', self.port))
            self.sock.listen(self.max_queues)

        except Exception as e:
            print(f'{self.__class__.__name__}: {str(e)}')
            self.close()

        finally:
            return
    def handle_client(self, sock, addr):
        c_sock = TCP_IPv4_ClientSocket(sock, addr)

        # Client socket will automatically close after request is handled
        req = c_sock.receive(1024)
        if req != 1:
            c_sock.handle(req)

    def loop(self):
        # Establishes client connections
        try:
            while True:
                print(f'{self.__class__.__name__}:Listening at port {self.port}...')

                # Wait for incoming client connection
                c_sock, addr = self.sock.accept()
                print(f'{c_sock.__class__.__name__}: Connected at port {addr}')

                # Create one-time client socket instance for handling requests
                self.executor.submit(self.handle_client, c_sock, addr)
                #client = threading.Thread(target=self.handle_client, args=(c_sock, addr), daemon=True)
                #client.start()

        except Exception as e:
            print(f'{self.__class__.__name__}: {str(e)}')

        finally:
            self.close()
            return

    def close(self):
        print(f'{self.__class__.__name__}: Shutting down server socket')
        self.executor.shutdown(wait=False) # behaves like threading.Thread(daemon=True)
        self.sock.close()

# Main execution
if __name__ == '__main__':

    # Create instance of the main server socket
    serverSocket = TCP_IPv4_ServerSocket()

    serverSocket.listen()
    serverSocket.loop()

    # After server exits
    sys.exit()
