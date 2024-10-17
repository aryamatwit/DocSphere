import socket
import sys
import threading
import json


HOST = ''
PORT = 9999

connected_clients = []
clients_lock = threading.Lock()
document = ""
version = 0

# Function to handle communication with a single client
def handle_client(client_socket, address):
    global document, version
    print(f'Connected with {address[0]}:{str(address[1])}')
    client_socket.sendall(f'Connected with {address[0]}:{str(address[1])}'.encode())

    # Add the new client to the list of connected clients
    with clients_lock:
        connected_clients.append(client_socket)

    send_document(client_socket)  # Send document to the new client

    while True:
        try:
            client_message = client_socket.recv(1024).decode()
            if not client_message:
                print(f"Client {address[0]} disconnected.")
                break  # Break on an empty message (connection closed)

            print(f"Client {address[0]}: {client_message}")

            if client_message.lower() == "end":
                print(f"Connection closed by client {address[0]}")
                break  # Close connection if the message is 'end'
            
            operation_data = json.loads(client_message)
            client_version = operation_data.get('version', 0)

            # Transform the operation if the client's version is outdated
            transformed_operation = transform_operation(operation_data, client_version)

            # Apply the operation to the shared document
            document = apply_operation(document, transformed_operation)

            # Increment the document version
            version += 1
            transformed_operation['version'] = version

            # Broadcast the transformed operation to all other clients
            broadcast_operation(transformed_operation, client_socket)

        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            break  # Exit on communication error

    with clients_lock:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
    client_socket.close()
    print(f"Connection with {address[0]} closed.")


# Function to send the current document to a new client
def send_document(client_socket):
    with clients_lock:
        client_socket.sendall(json.dumps({'document': document, 'version': version}).encode())

# Function to apply an operation to the shared document
def apply_operation(doc, operation):
    action = operation['action']
    position = operation['position']
    text = operation.get('text', '')

    if action == 'insert':
        doc = doc[:position] + text + doc[position:]
    elif action == 'delete':
        length = operation['length']
        doc = doc[:position] + doc[position+length:]

    return doc

# Function to transform an operation based on the current document version
def transform_operation(operation, client_version):
    global version
    # For simplicity, we assume that only insert and delete operations are transformed.
    # A more complex transformation would be needed for real applications.
    if client_version < version:
        # Example transformation logic (very simplistic):
        # This could be improved with more sophisticated rules.
        if operation['action'] == 'insert':
            operation['position'] = min(operation['position'], len(document))
        elif operation['action'] == 'delete':
            operation['position'] = min(operation['position'], len(document))
            operation['length'] = min(operation['length'], len(document) - operation['position'])

    return operation

def broadcast_operation(operation, sender_socket):
    with clients_lock:
        for client in connected_clients:
            if client != sender_socket:
                try:
                    client.sendall(json.dumps(operation).encode())
                except Exception:
                    print(f"Failed to send message to a client. Removing client.")
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