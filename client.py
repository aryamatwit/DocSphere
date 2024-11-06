import socket
import threading
import tkinter as tk

HOST = '10.220.44.200'  
PORT = 9999

local_document = ""  # The local document content
update_delay = 100  # Delay in milliseconds
lock_granted = False

# Function to update the document received from the server
def update_document_from_server(text_widget, client_socket):
    global local_document
    while True:
        try:
            server_message = client_socket.recv(4096).decode('utf-8')
            if server_message:
                if server_message == "LOCK_GRANTED":
                    global lock_granted
                    lock_granted = True
                elif server_message == "LOCK_DENIED":
                    lock_granted = False
                else:
                    merge_document(text_widget, server_message)

        except Exception as e:
            print(f"[ERROR] Lost connection to the server: {e}")
            break

# Function to merge server updates with the local document
def merge_document(text_widget, server_update):
    global local_document
    cursor_position = text_widget.index(tk.INSERT)

    if server_update != local_document:
        local_document = server_update
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, local_document)

        text_widget.mark_set(tk.INSERT, cursor_position)

# Function to send only the changed portion of the document to the server
def send_partial_update(client_socket, text_widget):
    global local_document, lock_granted
    current_content = text_widget.get(1.0, tk.END).strip()
    
    if current_content != local_document and lock_granted:
        client_socket.sendall(current_content.encode())
        local_document = current_content

# Function to request a lock from the server
def request_lock(client_socket, start, end):
    client_socket.sendall(f"LOCK_REQUEST {start} {end}".encode())

# Function to detect keypresses, request lock, and schedule updates to the server
def on_key_release(event, client_socket, text_widget):
    if not lock_granted:
        # Request lock for the section the user is editing
        cursor_position = int(text_widget.index(tk.INSERT).split('.')[0])
        request_lock(client_socket, cursor_position, cursor_position + 1)

    if lock_granted:
        if hasattr(on_key_release, "after_id"):
            text_widget.after_cancel(on_key_release.after_id)
        on_key_release.after_id = text_widget.after(update_delay, send_partial_update, client_socket, text_widget)

# Start the client-side program
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        root = tk.Tk()
        root.title("Collaborative Document Editor")
        text_widget = tk.Text(root, wrap='word', font=('Arial', 12))
        text_widget.pack(expand=True, fill='both')

        # Bind key release events to schedule document updates to the server
        text_widget.bind("<KeyRelease>", lambda event: on_key_release(event, client, text_widget))

        # Start a thread to receive the document from the server
        receive_thread = threading.Thread(target=update_document_from_server, args=(text_widget, client))
        receive_thread.start()

        root.mainloop()

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()
