import socket
import sys
import threading

HOST = ''
PORT = 9999

connected_clients = []
clients_lock = threading.Lock()
chat_history = []  

# Function to handle communication with a single client
def handle_client(client_socket, address):
    print(f'Connected with {address[0]}:{str(address[1])}')
    client_socket.sendall((f'Connected with {address[0]}:{str(address[1])}').encode())

    client_socket.sendall((f'Connected with {address[0]}:{str(address[1])}').encode())

    # Add the new client to the list of connected clients
    with clients_lock:
        connected_clients.append(client_socket)

    while True:
        try:
            # Receive message from client
            client_message = client_socket.recv(1024).decode()
            if client_message:
                print(f"Client {address[0]}: {client_message}")

                # If the client sends 'end', close the connection and remove from the list
                if client_message.lower() == "end":
                    print(f"Connection closed by client {address[0]}")
                    with clients_lock:
                        connected_clients.remove(client_socket)
                    client_socket.close()
                    break

                with clients_lock:
                    chat_history.append(f"Client {address[0]}: {client_message}")

                # Broadcast the received message to all connected clients
                broadcast_message(f"Client {address[0]}: {client_message}", client_socket)
            else:
                # Remove the client if no message is received (connection closed)
                with clients_lock:
                    connected_clients.remove(client_socket)
                client_socket.close()
                break
        
        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            with clients_lock:
                connected_clients.remove(client_socket)
            client_socket.close()
            break

def send_chat_history(client_socket):
    if chat_history:
        client_socket.send("Chat History:\n".encode('utf-8'))
        for message in chat_history:
            client_socket.send(f"{message}\n".encode('utf-8'))


# Function to broadcast a message to all connected clients except the sender
def broadcast_message(message, sender_socket):
    with clients_lock:
        for client in connected_clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    # If sending fails, remove the client from the list
                    connected_clients.remove(client)
                    client.close()

def start_server():
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
            connected_clients.append(client_socket)
            print(f'New connection established with {client_address[0]}:{client_address[1]}')
            
            # Create a new thread for each connected client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
            send_chat_history(client_socket)
            
        except socket.error as msg:
            print(f'Accept failed. Error code: {str(msg[0])} Message: {msg[1]}')
            server_socket.close()
            break

if input("Would you like to start the server (yes/no)? ").lower() == 'yes':
    start_server()
else:
    print("Server shutdown.")
    sys.exit()
            