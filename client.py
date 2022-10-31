import argparse
import socket
import sys

BUFFER_SIZE = 1024 #Buffer size for the socket connection

class HTTPClient(object):

    def __init__(self):
        #Initialize the  socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     
    def connectServer(self):
        #Parse the command line arguments
        parser = argparse.ArgumentParser(description='Client Application')
        parser.add_argument('host', help='Server Name')
        parser.add_argument('port_number', type=int, help='Port')
        parser.add_argument('method', help='Method(GET/PUT)')
        parser.add_argument('filename', help='Filename')
        args = parser.parse_args()

        SERVER_HOST = args.host #Get the Server Host from the command line argument
        SERVER_PORT = args.port_number #Get the Server Port from the command line argument
        REQ_METHOD = args.method #Get the request method from the command line argument
        FILENAME = args.filename #Get the filename from the command line argument

        try:
            #Connect to the server
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            print("Connected to the server successfully...!")
            self.request(REQ_METHOD, FILENAME) #Parse received request and handle request accordingly
        except socket.error:
            #If for some reason unable to connect to the server 
            print("Error: Can not connect to the provided server, make sure the server is running!")
            sys.exit()

    def request(self, REQ_METHOD, FILENAME):
        #For GET method
        if REQ_METHOD == 'GET':
            requestBody = bytes('{} {} HTTP/1.0\r\n'.format(REQ_METHOD, FILENAME), encoding='utf8')
            self.sock.sendall(requestBody) #Send the request to the server with the given filename

            #Wait for the response from the server
            print("Waiting for the server response...")
            while True:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    break
                print(data.decode()) #Print the received data on the console
        #For PUT method
        elif REQ_METHOD == 'PUT':
            requestBody = bytes('{} {} HTTP/1.0\r\n'.format(REQ_METHOD, FILENAME), encoding='utf8')
            self.sock.sendall(requestBody) #Send the request with the given filename to the server
            
            #Read the file and send it to the server
            file = open(FILENAME, 'rb')
            print('Uploading ' + FILENAME)
            data = file.read(BUFFER_SIZE)
            while (data):
                print('Uploading...')
                self.sock.sendall(data)
                data = file.read(BUFFER_SIZE)
            file.close() #Close the file buffer after file is uploaded
            print("Done Uploading")
            
            self.sock.shutdown(socket.SHUT_WR) #Shutdown the socket connection after upload
            
            #Wait for the response from the server
            while True:
                serverResponse = self.sock.recv(BUFFER_SIZE)
                if not serverResponse:
                    break
                print(serverResponse.decode()) #Print the server response on the console
            
            #Close the socket after done receiving the response
            self.sock.close()
        else:
            print('Only GET or PUT method is supported!')

# Main
HTTPClient().connectServer()
