import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog

HOST = '10.220.44.200'  
PORT = 9999

local_document = ""  # The local document content
locked_lines = set()  # Set of lines locked by other clients
update_delay = 500  # Delay in milliseconds

# Function to update the document received from the server
def update_document_from_server(text_widget, client_socket, line_numbers):
    global local_document
    while True:
        try:
            server_message = client_socket.recv(4096).decode('utf-8')
            if server_message.startswith("LINE_LOCK:"):
                process_line_lock(server_message, text_widget)
            else:
                merge_document(text_widget, server_message, line_numbers)
        except Exception as e:
            print(f"[ERROR] Lost connection to the server: {e}")
            break

# Process line lock/unlock messages from the server
def process_line_lock(message, text_widget):
    _, line, status = message.split(":")
    line = int(line)
    if status == "LOCKED":
        locked_lines.add(line)
        highlight_locked_line(text_widget, line, lock=True)
    elif status == "UNLOCKED":
        locked_lines.discard(line)
        highlight_locked_line(text_widget, line, lock=False)

# Highlight or unhighlight a line to indicate lock status
def highlight_locked_line(text_widget, line, lock=True):
    text_widget.tag_remove("locked_line", f"{line}.0", f"{line}.end")
    if lock:
        text_widget.tag_add("locked_line", f"{line}.0", f"{line}.end")
        text_widget.tag_configure("locked_line", background="lightgrey")

# Function to merge server updates with the local document
def merge_document(text_widget, server_update, line_numbers):
    global local_document
    cursor_position = text_widget.index(tk.INSERT)
    if server_update != local_document:
        local_document = server_update
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, local_document)
        update_line_numbers(text_widget, line_numbers)
        text_widget.mark_set(tk.INSERT, cursor_position)

# Function to send a lock or unlock request to the server
def request_line_lock(client_socket, line, lock):
    message = f"{'LOCK' if lock else 'UNLOCK'}:{line}"
    client_socket.sendall(message.encode())

# Function to detect keypresses and schedule updates
def on_key_release(event, client_socket, text_widget, line_numbers):
    line = int(text_widget.index("insert").split(".")[0])

    # Check if line is locked and prevent editing
    if line in locked_lines:
        return "break"  # Prevent editing on locked line

    # Request line lock if the line is not already locked
    if line not in locked_lines:
        request_line_lock(client_socket, line, True)

    # Detect line changes and unlock previous line
    if hasattr(on_key_release, "current_line") and on_key_release.current_line != line:
        request_line_lock(client_socket, on_key_release.current_line, False)

    on_key_release.current_line = line  # Update current line

    # Send document updates as usual
    if hasattr(on_key_release, "after_id"):
        text_widget.after_cancel(on_key_release.after_id)
    on_key_release.after_id = text_widget.after(update_delay, send_partial_update, client_socket, text_widget)

    update_line_numbers(text_widget, line_numbers)

# Function to send only the changed portion of the document to the server
def send_partial_update(client_socket, text_widget):
    global local_document
    current_content = text_widget.get(1.0, tk.END).strip()
    if current_content != local_document:
        client_socket.sendall(current_content.encode())
        local_document = current_content

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

# Start the client-side program
def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        root = tk.Tk()
        root.title("DevSphere")

        # Call on_closing() when the window is closed
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, client))
        
        # Create a frame for line numbers and text widget
        main_frame = tk.Frame(root)
        main_frame.pack(fill='both', expand=True)

        # Line numbers widget
        line_numbers = tk.Text(main_frame, width=4, padx=3, takefocus=0, border=0, background='lightgrey', state='disabled')
        line_numbers.pack(side='left', fill='y')

        # Text widget for document editing
        text_widget = tk.Text(main_frame, wrap='none', font=('Mono', 12), undo=True, border=0, foreground="#f8f8f2", background="#282a36")
        text_widget.pack(side='right', fill='both', expand=True)

        # Apply tag for locked line highlighting
        text_widget.tag_configure("locked_line", background="lightgrey")

        # Scrollbar
        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget['yscrollcommand'] = scrollbar.set

        # Bind key release events to update the line numbers and schedule document updates to the server
        text_widget.bind("<KeyRelease>", lambda event: on_key_release(event, client, text_widget, line_numbers))

        # Start a thread to receive the document from the server
        receive_thread = threading.Thread(target=update_document_from_server, args=(text_widget, client, line_numbers))
        receive_thread.daemon = True
        receive_thread.start()

        root.mainloop()

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

# Prompt the user to connect to the server
if input("Would you like to connect to the server (yes/no)? ").lower() == 'yes':
    start_client()
