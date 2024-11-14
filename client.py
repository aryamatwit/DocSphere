import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import json
import time

HOST = '10.27.3.110'  # Replace with your server's IP address
PORT = 9999

client_id = str(time.time())  # Unique client identifier
operation_counter = 0  # Local operation counter

# Function to update the document received from the server
def update_document_from_server(text_widget, client_socket, line_numbers):
    while True:
        try:
            server_message = client_socket.recv(4096).decode('utf-8')
            if server_message:
                operation = json.loads(server_message)
                if operation['type'] == 'full_document':
                    # Initialize the document
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(tk.END, operation['content'])
                else:
                    apply_operation_locally(text_widget, operation)
                    update_line_numbers(text_widget, line_numbers)
        except Exception as e:
            print(f"[ERROR] Lost connection to the server: {e}")
            break

# Function to apply an operation locally
def apply_operation_locally(text_widget, operation):
    op_type = operation.get('type')
    index = operation.get('index')
    text = operation.get('text', '')
    start_index = f"1.0 + {index} chars"
    if op_type == 'insert':
        text_widget.insert(start_index, text)
    elif op_type == 'delete':
        length = operation.get('length', 1)
        end_index = f"1.0 + {index + length} chars"
        text_widget.delete(start_index, end_index)
    else:
        print(f"Unknown operation type: {op_type}")

# Function to send an operation to the server
def send_operation(client_socket, operation):
    try:
        client_socket.sendall(json.dumps(operation).encode())
    except Exception as e:
        print(f"[ERROR] Failed to send operation: {e}")

# Function to handle text changes
def on_text_change(event):
    global operation_counter
    index = event.widget.index(tk.INSERT)
    char_index = get_char_index(event.widget, index)
    if event.keysym == 'BackSpace':
        # Deleting character before the cursor
        operation = {
            'type': 'delete',
            'index': char_index,
            'length': 1,
            'client_id': client_id,
            'timestamp': time.time()
        }
    elif event.char and len(event.char) == 1:
        # Inserting character at the cursor position -1
        operation = {
            'type': 'insert',
            'index': char_index - 1,
            'text': event.char,
            'client_id': client_id,
            'timestamp': time.time()
        }
    else:
        return  # Ignore other keys

    operation_counter += 1
    operation['operation_id'] = operation_counter
    send_operation(client_socket, operation)

# Function to get character index from Tkinter index
def get_char_index(text_widget, index):
    return int(text_widget.count("1.0", index, "chars")[0])

# Function to update line numbers
def update_line_numbers(text_widget, line_numbers):
    line_numbers_text = "\n".join(str(i + 1) for i in range(int(text_widget.index('end-1c').split('.')[0])))
    line_numbers.config(state='normal')
    line_numbers.delete(1.0, tk.END)
    line_numbers.insert(tk.END, line_numbers_text)
    line_numbers.config(state='disabled')

# Function to handle closing the window and disconnecting from the server
def on_closing(root, client_socket):
    client_socket.close()  # Close the client socket
    root.destroy()  # Close the GUI window

# Function to save the current document to a local file
def save_document(text_widget):
    # Open a file dialog to select the file location
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        try:
            with open(file_path, "w") as file:
                # Write the current document content to the file
                file.write(text_widget.get(1.0, tk.END).strip())
            print(f"Document saved successfully to {file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save the document: {e}")

# Start the client-side program
def start_client():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        root = tk.Tk()
        root.title("DevSphere")

        # Call on_closing() when the window is closed
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, client_socket))

        # Create a menu bar
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # Add a "File" menu with a "Save" option
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save", command=lambda: save_document(text_widget))
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create a frame for line numbers and text widget
        main_frame = tk.Frame(root)
        main_frame.pack(fill='both', expand=True)

        # Line numbers widget
        line_numbers = tk.Text(main_frame, width=4, padx=3, takefocus=0, border=0, background='lightgrey', state='disabled')
        line_numbers.pack(side='left', fill='y')

        # Text widget for document editing
        text_widget = tk.Text(main_frame, wrap='none', font=('Mono', 12), undo=True, border=0, foreground="#f8f8f2", background="#282a36")
        text_widget.pack(side='right', fill='both', expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget['yscrollcommand'] = scrollbar.set

        # Bind key release events to handle text changes
        text_widget.bind("<KeyRelease>", on_text_change)

        # Start a thread to receive operations from the server
        receive_thread = threading.Thread(target=update_document_from_server, args=(text_widget, client_socket, line_numbers))
        receive_thread.daemon = True
        receive_thread.start()

        root.mainloop()

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

# Prompt the user to connect to the server
if __name__ == "__main__":
    start_client()
