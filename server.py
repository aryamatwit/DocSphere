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
    client_socket.sendall(f'Connected with {address[0]}:{str(address[1])}'.encode())

    # Add the new client to the list of connected clients
    with clients_lock:
        connected_clients.append(client_socket)

    send_chat_history(client_socket)  # Send chat history to the new client

    while True:
        try:
            client_message = client_socket.recv(1024).decode()
            if not client_message:
                print(f"Client {address[0]} disconnected.")
                break  # Break on an empty message (connection closed)

            print(f"Message received from client {address[0]}: {client_message}")

            with clients_lock:
                chat_history.append(f"Client {address[0]}: {client_message}")

            broadcast_message(f"Client {address[0]}: {client_message}", client_socket)

        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            
            with clients_lock:
                if client_socket in connected_clients:
                    connected_clients.remove(client_socket)
                    print(f"Removing client {address[0]} from the list.")
                    client_socket.close()

   
# Function to send chat history to a new client
def send_chat_history(client_socket):
    if chat_history:
        try:
            client_socket.sendall("Chat History:\n".encode())
            for message in chat_history:
                client_socket.sendall(f"{message}\n".encode())
        except socket.error as msg:
            print(f"Error sending chat history: {msg}")

# Function to broadcast a message to all connected clients except the sender
def broadcast_message(message, sender_socket):
    with clients_lock:
        for client in connected_clients:
            if client != sender_socket:
                try:
                    client.sendall(message.encode())
                    print(f"Broadcasting message: {message}")
                except socket.error:
                    print(f"Failed to send message to a client. Removing client.")\
                    
                    #Safely remove the client from the list of connected clients and close the socket
                    with clients_lock:
                        connected_clients.remove(client)
                    
                    client.close()

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created!')

try:
    server_socket.bind((HOST, PORT))
    print('Socket bind complete.')
except socket.error as msg:
    print(f'Bind failed. Error: {msg}')
    sys.exit()

server_socket.listen(10)
print(f"Server is running on {HOST}:{PORT}...")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f'New connection established with {client_address[0]}:{client_address[1]}')

        with clients_lock:
            connected_clients.append(client_socket)

        # Start a new thread for each client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

except KeyboardInterrupt:
    print("Server is shutting down...")

finally:
    server_socket.close()
    print("Socket closed.")
