import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox
import os

# Define the server's IP address and port number
HOST = '10.220.44.200'  # Use '127.0.0.1' for localhost testing
PORT = 9999

local_document = ""
version = 0  # Client's version of the document
filename = "document.txt"  # File to save the document

# Function to load document from a file
def load_document_from_file():
    global local_document
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            local_document = file.read()
    else:
        local_document = ""

# Function to save the current document to a file
def save_document_to_file():
    global local_document
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(local_document)

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

# Function to handle receiving messages from the server
def receive_msg(client_socket, text_widget):
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

                # Update the text widget (GUI)
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, local_document)

                # Save updated document to file
                save_document_to_file()
            else:
                break
        except Exception as e:
            print(f"[ERROR] Lost connection to the server: {e}")
            break

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

# Function to send insert operation
def insert_text(event, client_socket, text_widget):
    cursor_position = text_widget.index(tk.INSERT)  # Get current cursor position
    position = int(cursor_position.split('.')[1])  # Extract position as an integer
    text = event.char  # Get the character inserted
    if text.isprintable():  # Only send printable characters
        send_operation(client_socket, 'insert', position, text=text)

# Function to send delete operation
def delete_text(event, client_socket, text_widget):
    cursor_position = text_widget.index(tk.INSERT)  # Get current cursor position
    position = int(cursor_position.split('.')[1])  # Extract position as an integer
    send_operation(client_socket, 'delete', position, length=1)

# Start the client-side program
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        welcome_msg = client.recv(1024).decode('utf-8')
        print(welcome_msg)

        # Load document from file
        load_document_from_file()

        # Setup the tkinter window
        root = tk.Tk()
        root.title("Collaborative Document Editor")

        text_widget = tk.Text(root, wrap='word')
        text_widget.pack(expand=True, fill='both')

        # Load the document into the text widget
        text_widget.insert(tk.END, local_document)

        # Start a thread to receive messages from the server
        receive_thread = threading.Thread(target=receive_msg, args=(client, text_widget))
        receive_thread.start()

        # Bind key events to capture cursor-based insertions
        text_widget.bind("<KeyPress>", lambda event: insert_text(event, client, text_widget))
        text_widget.bind("<BackSpace>", lambda event: delete_text(event, client, text_widget))

        # Close the connection gracefully when the window is closed
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                client.close()
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

# Prompt the user to connect to the server
if __name__ == "__main__":
    start_client()
