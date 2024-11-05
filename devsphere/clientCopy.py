import socket
import threading
import vscode  # For interacting with the VS Code editor

HOST = '10.220.44.200'  
PORT = 9999

local_document = ""  # Cache for local document content
update_delay = 500  # Delay in milliseconds for updates

# Function to update the document with server data
def update_document_from_server(client_socket, vscode_editor):
    global local_document
    while True:
        try:
            # Receive update from the server
            server_message = client_socket.recv(4096).decode('utf-8')
            if server_message:
                # If the received document is different, update the local VS Code editor
                if server_message != local_document:
                    local_document = server_message
                    vscode_editor.set_text(local_document)  # Update the open document in VS Code
        except Exception as e:
            print(f"[ERROR] Lost connection to server: {e}")
            break

# Function to send document updates to the server if there are changes
def send_partial_update(client_socket, vscode_editor):
    global local_document
    current_content = vscode_editor.get_text().strip()
    
    # If content has changed, send the updated content to the server
    if current_content != local_document:
        client_socket.sendall(current_content.encode())
        local_document = current_content

# Main function to start the client and manage document sync
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        # Initialize VS Code editor
        with vscode.Editor() as vscode_editor:
            # Start a thread to handle incoming server updates
            receive_thread = threading.Thread(target=update_document_from_server, args=(client, vscode_editor))
            receive_thread.start()

            # Monitor for document changes and send updates to the server
            while True:
                send_partial_update(client, vscode_editor)

    except socket.error as err:
        print(f"Failed to connect to server: {err}")

# Prompt to start the client
if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()
