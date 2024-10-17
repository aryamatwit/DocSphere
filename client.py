import socket
import threading
import json

# Define the server's IP address and port number
HOST = '10.220.44.200'  # local host
PORT = 9999

# Local document state
local_document = ""
version = 0  # Client's version of the document

# Function to handle communication with the server
def receive_msg(client_socket):
    global local_document, version
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
                operation = json.loads(msg)
                print(f"\nReceived operation: {operation}")

                # Apply the operation to the local document
                local_document = apply_operation(local_document, operation)

                # Update the local document version
                version = operation['version']
                
                # Display the updated document
                print(f"Updated document: {local_document}")
            else:
                break
        except Exception as e:
            print(f"[ERROR] Lost connection to the server: {e}")
            break

# Function to apply an operation to the local document
def apply_operation(doc, operation):
    action = operation['action']
    position = operation['position']
    text = operation.get('text', '')

    if action == 'insert':
        doc = doc[:position] + text + doc[position:]
    elif action == 'delete':
        length = operation['length']
        doc = doc[:position] + doc[position + length:]

    return doc

# Function to send an operation to the server
def send_operation(client_socket, action, position, text=None, length=None):
    global version
    operation = {
        'action': action,
        'position': position,
        'version': version  # Send the version of the document the client is aware of
    }
    if text:
        operation['text'] = text
    if length:
        operation['length'] = length

    client_socket.send(json.dumps(operation).encode('utf-8'))

# Start the client-side program
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        welcome_msg = client.recv(1024).decode('utf-8')
        print(welcome_msg)

        receive_thread = threading.Thread(target=receive_msg, args=(client,))
        receive_thread.start()

        while True:
            action = input("Enter action (insert/delete): ").strip()
            position = int(input("Enter position: "))

            if action == 'insert':
                text = input("Enter text to insert: ")
                send_operation(client, action, position, text=text)

            elif action == 'delete':
                length = int(input("Enter length of text to delete: "))
                send_operation(client, action, position, length=length)

            elif action.lower() == 'exit':
                print("\nDisconnecting from the server... Goodbye!")
                client.close()
                break

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

# Prompt the user to connect to the server
if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()