import argparse
import socket

SERVER_HOST = '127.0.0.1' #Define socket host
BUFFER_SIZE = 1024 #Buffer size for the socket connection

class HTTPServer(object):

    def __init__(self):
        #Initialize the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def server(self):
        #Parse the command line arguments
        parser = argparse.ArgumentParser(description='Server Application')
        parser.add_argument('port_number', type=int, help='Port')
        args = parser.parse_args()

        SERVER_PORT = args.port_number #Get the Server Port from the command line argument

        self.sock.bind((SERVER_HOST, SERVER_PORT)) #Bind the host and port to the socket
        self.sock.listen(1) #Listen for connections
        print('Listening on port %s ...' % SERVER_PORT)

        while True:
            #Wait for client connections
            client_connection, client_address = self.sock.accept()
            print ('Got connection from', client_address)

            #Get the client request
            request = client_connection.recv(BUFFER_SIZE).decode()
            print('Request received: ' + request)

            #Parse the HTTP headers
            headers = request.split('\n')
            methodType = headers[0].split()[0]
            filename = headers[0].split()[1]

            #For GET method
            if methodType == 'GET':
                try:
                    #Set filename to index.html(default) for browser access without any path provided 
                    if filename == '/':
                        filename = 'index.html'
                    
                    #Get the content of the file
                    fin = open('./' + filename)
                    content = fin.read()
                    fin.close() #Close the file buffer after done accessing the file
                    response = 'HTTP/1.0 200 OK\n\n' + content
                except FileNotFoundError:
                    response = '404 NOT FOUND\n\nRequested File Not Found!'
                
                # Send HTTP response
                client_connection.sendall(response.encode())
                client_connection.close() #Close the socket connection
            #For PUT method
            elif methodType == 'PUT':
                #Create the file inside Received_Files folder
                fileToWrite = open('Received_Files/' + filename, 'wb')
                print ("Receiving...")

                #Get the file data from the client
                data = client_connection.recv(BUFFER_SIZE)
                while (data):
                    print ("Receiving...")
                    fileToWrite.write(data) #Save the data received from the client
                    data = client_connection.recv(BUFFER_SIZE)
                fileToWrite.close() #Close the file buffer after the file is saved on the disk
            
                print ("Done Receiving")
                
                #Send back the response to the client
                response = '200 OK File Created\n\n'
                client_connection.sendall(response.encode())
                client_connection.close() #Close the connection
            else:
                print('Only GET or PUT method is supported!')

# Main
HTTPServer().server()