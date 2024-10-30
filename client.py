import socket
import threading
import tkinter as tk

HOST = '10.220.44.200'  
PORT = 9999

local_document = ""  # The local document content
update_delay = 500  # Delay in milliseconds

# Function to update the document received from the server
def update_document_from_server(text_widget, client_socket):
    global local_document
    while True:
        try:
            # Receive the full document from the server
            server_message = client_socket.recv(4096).decode('utf-8')
            if server_message and server_message != local_document:
                local_document = server_message
                
                # Update the text widget with the new document from the server
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, local_document)

        except Exception as e:
            print(f"[ERROR] Lost connection to the server: {e}")
            break

# Function to send the current document to the server
def send_document_to_server(client_socket, text_widget):
    global local_document
    current_content = text_widget.get(1.0, tk.END).strip()  # Strip trailing newline
    if current_content != local_document:
        local_document = current_content  # Update local_document
        client_socket.sendall(local_document.encode())  # Send the entire document

# Function to detect any keypress in the text widget and send updates to the server after a delay
def on_key_release(event, client_socket, text_widget):
    # Cancel previous scheduled update if it exists
    if hasattr(on_key_release, "after_id"):
        text_widget.after_cancel(on_key_release.after_id)

    # Schedule a new update
    on_key_release.after_id = text_widget.after(update_delay, send_document_to_server, client_socket, text_widget)

# Start the client-side program
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        root = tk.Tk()
        root.title("Collaborative Document Editor")

        text_widget = tk.Text(root, wrap='word', font=('Arial', 12))
        text_widget.pack(expand=True, fill='both')

        # Bind key release events to send document updates to the server
        text_widget.bind("<KeyRelease>", lambda event: on_key_release(event, client, text_widget))

        # Start a thread to receive the document from the server
        receive_thread = threading.Thread(target=update_document_from_server, args=(text_widget, client))
        receive_thread.start()

        root.mainloop()

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

# Prompt the user to connect to the server
if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()
