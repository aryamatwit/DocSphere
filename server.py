import socket
import threading
import sys

HOST = ''
PORT = 9999

connected_clients = []
clients_lock = threading.Lock()
document = ""  # Shared document state
line_locks = {}  # Dictionary to track line locks {line_number: client_socket}

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
            # Receive the document data and line number from the client
            client_message = client_socket.recv(4096).decode('utf-8')
            if not client_message:
                print(f"Client {address[0]} disconnected.")
                break

            # Parse the received data
            line_number, new_content = client_message.split(":::", 1)
            line_number = int(line_number)

            # Check if the line is locked by this client or is not locked
            with clients_lock:
                if line_locks.get(line_number) in (None, client_socket):
                    line_locks[line_number] = client_socket  # Lock line for this client
                    update_document_line(line_number, new_content)  # Update the document
                    broadcast_document()  # Broadcast updated document to all clients
                else:
                    # If the line is locked by another client, send a "locked" message back
                    client_socket.sendall(f"LOCKED::{line_number}".encode())

        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            break

    # Remove the client and release any locks they held
    with clients_lock:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
        release_client_locks(client_socket)
    client_socket.close()
    print(f"Connection with {address[0]} closed.")

# Function to send the current document to a specific client
def send_document(client_socket):
    with clients_lock:
        client_socket.sendall(document.encode())

# Function to update a specific line in the shared document
def update_document_line(line_number, new_content):
    global document
    doc_lines = document.splitlines()
    if line_number < len(doc_lines):
        doc_lines[line_number] = new_content
    else:
        # Extend document if line_number is beyond current document length
        doc_lines += [""] * (line_number - len(doc_lines)) + [new_content]
    document = "\n".join(doc_lines)

# Function to release all locks held by a client
def release_client_locks(client_socket):
    global line_locks
    line_locks = {line: owner for line, owner in line_locks.items() if owner != client_socket}

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
