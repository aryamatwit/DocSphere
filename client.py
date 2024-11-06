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
            # Receive the document update from the server
            server_message = client_socket.recv(4096).decode('utf-8')
            if server_message:
                # Merge the server update into the local document
                merge_document(text_widget, server_message)

        except Exception as e:

            print(f"[ERROR] Lost connection to the server: {e}")
            break

# Function to merge server updates with the local document
def merge_document(text_widget, server_update):
    global local_document
    # Save the current cursor position
    cursor_position = text_widget.index(tk.INSERT)

    # Update the local document and text widget with the server update
    if server_update != local_document:
        local_document = server_update
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, local_document)

        # Restore the cursor position
        text_widget.mark_set(tk.INSERT, cursor_position)

# Function to send only the changed portion of the document to the server
def send_partial_update(client_socket, text_widget):
    global local_document
    current_content = text_widget.get(1.0, tk.END).strip()
    
    # Calculate the difference and send only the changes
    if current_content != local_document:
        client_socket.sendall(current_content.encode())
        local_document = current_content

# Function to detect keypresses and schedule updates to the server
def on_key_release(event, client_socket, text_widget):
    # Cancel any scheduled update
    if hasattr(on_key_release, "after_id"):
        text_widget.after_cancel(on_key_release.after_id)

    # Schedule a new update
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

# Prompt the user to connect to the server
if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()
