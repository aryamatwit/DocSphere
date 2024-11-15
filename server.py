import socket
import threading
import sys
import json

HOST = ''
PORT = 9999

connected_clients = []
clients_lock = threading.Lock()
document = ""  # Shared document state
chat_history = []  # List to store chat history

# Function to handle communication with a single client
def handle_client(client_socket, address):
    global document, chat_history
    print(f'Connected with {address[0]}:{str(address[1])}')

    # Initialize buffer for this client
    buffer = ''

    # Receive username
    try:
        data = client_socket.recv(4096).decode('utf-8')
        if not data:
            print(f"Client {address[0]} disconnected before sending username.")
            client_socket.close()
            return
        buffer += data
        if '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            message = json.loads(line)
            if message['type'] == 'USERNAME':
                username = message['username']
                print(f"Username received from {address[0]}: {username}")
            else:
                print(f"Expected USERNAME message from {address[0]}")
                client_socket.close()
                return
        else:
            # Wait for the rest of the message
            for message in receive_messages(client_socket):
                if message['type'] == 'USERNAME':
                    username = message['username']
                    print(f"Username received from {address[0]}: {username}")
                    break
                else:
                    print(f"Expected USERNAME message from {address[0]}")
                    client_socket.close()
                    return
            else:
                # Connection closed
                print(f"Client {address[0]} disconnected before sending username.")
                client_socket.close()
                return
    except Exception as e:
        print(f"Error receiving username from {address[0]}: {e}")
        client_socket.close()
        return

    # Add the new client to the list of connected clients
    with clients_lock:
        connected_clients.append({'socket': client_socket, 'username': username})

    # Send the latest document and chat history to the new client
    send_document(client_socket)
    send_chat_history(client_socket)
    # Send the updated user list to all clients
    broadcast_user_list()

    # Now handle messages from client
    for message in receive_messages(client_socket):
        if message['type'] == 'OPERATION':
            # Update the shared document
            apply_operation_to_document(message)
            # Broadcast the operation to other clients
            broadcast_operation(message, client_socket)
        elif message['type'] == 'CHAT':
            chat_message = message['content']
            print(f"Received chat message from {username}: {chat_message}")
            # Save chat message to history
            with threading.Lock():
                chat_history.append({'username': username, 'content': chat_message})
            broadcast_chat(username, chat_message)
        else:
            print(f"Unknown message type from {address[0]}: {message['type']}")

    # Remove the client from the connected clients list on disconnection
    with clients_lock:
        for client in connected_clients:
            if client['socket'] == client_socket:
                connected_clients.remove(client)
                break
    client_socket.close()
    print(f"Connection with {address[0]} closed.")

    # Broadcast the updated user list
    broadcast_user_list()

# Function to receive messages from the client
def receive_messages(sock):
    buffer = ''
    while True:
        try:
            data = sock.recv(4096).decode('utf-8')
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                message = json.loads(line)
                yield message
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Function to send the current document to a specific client
def send_document(client_socket):
    with clients_lock:
        message = json.dumps({'type': 'DOCUMENT', 'content': document}) + '\n'
        client_socket.sendall(message.encode('utf-8'))

# Function to send the chat history to a specific client
def send_chat_history(client_socket):
    with clients_lock:
        message = json.dumps({'type': 'CHAT_HISTORY', 'history': chat_history}) + '\n'
        client_socket.sendall(message.encode('utf-8'))

# Function to broadcast the user list to all clients
def broadcast_user_list():
    with clients_lock:
        usernames = [client['username'] for client in connected_clients]
        message = json.dumps({'type': 'USERLIST', 'users': usernames}) + '\n'
        for client in connected_clients.copy():
            try:
                client['socket'].sendall(message.encode('utf-8'))
            except Exception:
                print(f"Failed to send user list to {client['username']}. Removing client.")
                client['socket'].close()
                connected_clients.remove(client)

# Function to broadcast chat messages to all clients
def broadcast_chat(username, chat_message):
    with clients_lock:
        message = json.dumps({'type': 'CHAT', 'username': username, 'content': chat_message}) + '\n'
        for client in connected_clients.copy():
            try:
                client['socket'].sendall(message.encode('utf-8'))
            except Exception:
                print(f"Failed to send chat message to {client['username']}. Removing client.")
                client['socket'].close()
                connected_clients.remove(client)

# Function to apply operation to the shared document
def apply_operation_to_document(message):
    global document
    operation = message['operation']
    if operation == 'insert':
        index = message['index']
        text = message['text']
        # Convert index to integer offset
        offset = text_index_to_offset(index)
        with threading.Lock():
            document = document[:offset] + text + document[offset:]
    elif operation == 'delete':
        index_start = message['index_start']
        index_end = message['index_end']
        offset_start = text_index_to_offset(index_start)
        offset_end = text_index_to_offset(index_end)
        with threading.Lock():
            document = document[:offset_start] + document[offset_end:]

# Function to convert Tkinter text index to offset
def text_index_to_offset(index):
    # Index is in the form 'line.column'
    line, column = map(int, index.split('.'))
    lines = document.split('\n')
    offset = sum(len(lines[i]) + 1 for i in range(line - 1)) + column
    return offset

# Function to broadcast operation to all clients except the source
def broadcast_operation(message, source_socket):
    with clients_lock:
        for client in connected_clients.copy():
            if client['socket'] != source_socket:
                try:
                    msg = json.dumps(message) + '\n'
                    client['socket'].sendall(msg.encode('utf-8'))
                except Exception:
                    print(f"Failed to send operation to {client['username']}. Removing client.")
                    client['socket'].close()
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
