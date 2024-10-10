import socket
import sys
import threading

HOST = ''
PORT = 9999

# Function to handle communication with a single client
def handle_client(client_socket, address):
    print(f'Connected with {address[0]}:{str(address[1])}')
    client_socket.sendall((f'Connected with {address[0]}:{str(address[1])}').encode())

    while True:
        try:
            # Receive message from client
            client_message = client_socket.recv(50).decode()
            print(f"Client {address[0]}: {client_message}")
            
            # If the client sends 'end', close the connection
            if client_message.lower() == "end":
                print(f"Connection closed by client {address[0]}")
                client_socket.close()
                break
            
            # Server message to send back to client
            server_message = input("You: ")
            if server_message.lower() == "end":
                client_socket.sendall("end".encode())
                print("Connection closed by server.")
                client_socket.close()
                break
            
            # Send the server's message to the client
            client_socket.sendall(server_message.encode())
        
        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            client_socket.close()
            break

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created!')
try:
    server_socket.bind((HOST, PORT))
    print('Socket bind complete.')
except socket.error as msg:
    print(f'Bind failed. Error code: {str(msg[0])} Message: {msg[1]}')
    sys.exit()
    
# Listen for incoming connections (maximum of 10)
server_socket.listen(10)

print('Socket is now listening...')
while True:
    try:
        # Accept new client connections
        client_socket, client_address = server_socket.accept()
        print(f'New connection established with {client_address[0]}:{client_address[1]}')
        
        # Create a new thread for each connected client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
    except socket.error as msg:
        print(f'Accept failed. Error code: {str(msg[0])} Message: {msg[1]}')
        break

server_socket.close()