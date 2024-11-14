import socket
import threading
import sys
import json

HOST = ''
PORT = 9999

connected_clients = []
clients_lock = threading.Lock()
document = ""  # Shared document state
operation_counter = 0  # Global operation counter

# Function to handle communication with a single client
def handle_client(client_socket, address):
    global document
    global operation_counter
    print(f'Connected with {address[0]}:{str(address[1])}')
    
    # Add the new client to the list of connected clients
    with clients_lock:
        connected_clients.append(client_socket)
    
    # Send the latest document to the new client
    send_document(client_socket)
    
    while True:
        try:
            # Receive the operation data from the client
            message = client_socket.recv(4096).decode('utf-8')
            if not message:
                print(f"Client {address[0]} disconnected.")
                break

            operation = json.loads(message)
            print(f"Received operation from client {address[0]}: {operation}")

            # Apply the operation to the shared document
            with threading.Lock():
                apply_operation(operation)
                operation_counter += 1  # Increment the operation counter
                operation['operation_id'] = operation_counter  # Add operation ID

            # Broadcast the operation to all clients
            broadcast_operation(operation)

        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            break
        except json.JSONDecodeError:
            print(f"Received invalid JSON from client {address[0]}")
            continue

    # Remove the client from the connected clients list on disconnection
    with clients_lock:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
    client_socket.close()
    print(f"Connection with {address[0]} closed.")

# Function to send the current document to a specific client
def send_document(client_socket):
    with clients_lock:
        message = {
            'type': 'full_document',
            'content': document
        }
        client_socket.sendall(json.dumps(message).encode())

# Function to broadcast an operation to all clients
def broadcast_operation(operation):
    with clients_lock:
        clients_to_remove = []
        for client in connected_clients:
            try:
                client.sendall(json.dumps(operation).encode())
            except Exception:
                print(f"Failed to send operation to a client. Removing client.")
                client.close()
                clients_to_remove.append(client)
        for client in clients_to_remove:
            connected_clients.remove(client)

# Function to apply an operation to the shared document
def apply_operation(operation):
    global document
    op_type = operation.get('type')
    index = operation.get('index')
    text = operation.get('text', '')
    if op_type == 'insert':
        document = document[:index] + text + document[index:]
    elif op_type == 'delete':
        length = operation.get('length', 1)
        document = document[:index] + document[index+length:]
    else:
        print(f"Unknown operation type: {op_type}")

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
