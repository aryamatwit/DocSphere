import socket
import threading
import sys
import os

HOST = ''
PORT = 9999

connected_clients = []
clients_lock = threading.Lock()
document = ""  # Shared document state
document_file = "shared_document.txt"

# Load the document from a file if it exists
def load_document():
    global document
    if os.path.exists(document_file):
        with open(document_file, "r") as file:
            document = file.read()

# Save the current document to a file
def save_document():
    with open(document_file, "w") as file:
        file.write(document)

# Function to handle communication with a single client
def handle_client(client_socket, address):
    global document
    print(f'Connected with {address[0]}:{str(address[1])}')
    
    # Add the new client to the list of connected clients
    with clients_lock:
        connected_clients.append(client_socket)

    # Immediately send the latest document to the new client
    send_document(client_socket)

    while True:
        try:
            # Receive the document data from the client (full or partial)
            client_message = client_socket.recv(4096).decode('utf-8')
            if not client_message:
                print(f"Client {address[0]} disconnected.")
                break

            print(f"Received updated document from client {address[0]}")

            # Update the shared document and save it to the file
            document = client_message
            save_document()

            # Broadcast the updated document to all clients
            broadcast_document()

        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            break

    # Remove the client from the connected clients list on disconnection
    with clients_lock:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
    client_socket.close()
    print(f"Connection with {address[0]} closed.")

# Function to send the current document to a specific client
def send_document(client_socket):
    with clients_lock:
        client_socket.sendall(document.encode())

# Function to broadcast the current document to all clients
def broadcast_document():
    with clients_lock:
        for client in connected_clients:
            try:
                client.sendall(document.encode())
            except Exception:
                print(f"Failed to send document to a client. Removing client.")
                client.close()
                connected_clients.remove(client)

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created!')

# Load the document when the server starts
load_document()

try:
    server_socket.bind((HOST, PORT))
    print('Socket bind complete.')
except socket.error as msg:
    print(f'Bind failed. Error: {msg}')
    sys.exit()

server_socket.listen(10)
print('Socket is now listening...')

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f'New connection established with {client_address[0]}:{client_address[1]}')

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

except KeyboardInterrupt:
    print("Server is shutting down...")

finally:
    server_socket.close()
    print("Socket closed.")
