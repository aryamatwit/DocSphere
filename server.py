import socket
import threading
import sys

HOST = ''
PORT = 9999

connected_clients = []
clients_lock = threading.Lock()
document = ""  # Shared document state
line_locks = {}  # Dictionary to track which lines are locked by which clients

# Function to handle communication with a single client
def handle_client(client_socket, address):
    global document
    print(f'Connected with {address[0]}:{str(address[1])}')

    with clients_lock:
        connected_clients.append(client_socket)

    send_document(client_socket)

    while True:
        try:
            client_message = client_socket.recv(4096).decode('utf-8')
            if not client_message:
                print(f"Client {address[0]} disconnected.")
                break

            # Process messages based on type
            if client_message.startswith("LOCK:"):
                line = int(client_message.split(":")[1])
                lock_line(client_socket, line)
            elif client_message.startswith("UNLOCK:"):
                line = int(client_message.split(":")[1])
                unlock_line(client_socket, line)
            else:
                # Update document and broadcast changes
                document = client_message
                broadcast_document()

        except socket.error as msg:
            print(f"Communication error with client {address[0]}: {str(msg)}")
            break

    with clients_lock:
        connected_clients.remove(client_socket)
    client_socket.close()
    print(f"Connection with {address[0]} closed.")

# Lock a line for a specific client
def lock_line(client_socket, line):
    with clients_lock:
        if line not in line_locks:
            line_locks[line] = client_socket
            broadcast_line_lock(line, True)

# Unlock a line, making it available for other clients
def unlock_line(client_socket, line):
    with clients_lock:
        if line in line_locks and line_locks[line] == client_socket:
            del line_locks[line]
            broadcast_line_lock(line, False)

# Broadcast the current document to all clients
def broadcast_document():
    with clients_lock:
        for client in connected_clients:
            try:
                client.sendall(document.encode())
            except Exception:
                client.close()
                connected_clients.remove(client)

# Broadcast line lock/unlock status to all clients
def broadcast_line_lock(line, is_locked):
    with clients_lock:
        lock_message = f"LINE_LOCK:{line}:{'LOCKED' if is_locked else 'UNLOCKED'}"
        for client in connected_clients:
            try:
                client.sendall(lock_message.encode())
            except Exception:
                client.close()
                connected_clients.remove(client)

# Send the current document to a specific client
def send_document(client_socket):
    with clients_lock:
        client_socket.sendall(document.encode())

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
