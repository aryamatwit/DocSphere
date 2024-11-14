import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import json

HOST = '10.220.43.80'
PORT = 9999

local_document = ""  # The local document content
update_delay = 10  # Delay in milliseconds

# Function to update the document received from the server
def update_document_from_server(text_widget, client_socket, user_list_widget, chat_display_widget):
    for message in receive_messages(client_socket):
        if message['type'] == 'DOCUMENT':
            merge_document(text_widget, message['content'])
        elif message['type'] == 'USERLIST':
            update_user_list(user_list_widget, message['users'])
        elif message['type'] == 'CHAT':
            update_chat_display(chat_display_widget, message['username'], message['content'])

# Function to receive messages from the server
def receive_messages(sock):
    buffer = ''
    while True:
        try:
            data = sock.recv(4096).decode('utf-8')
            if not data:
                # Connection closed
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                message = json.loads(line)
                yield message
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

# Function to send the updated document to the server
def send_partial_update(client_socket, text_widget):
    global local_document
    current_content = text_widget.get(1.0, tk.END).strip()
    if current_content != local_document:
        msg = json.dumps({'type': 'DOCUMENT', 'content': current_content}) + '\n'
        client_socket.sendall(msg.encode('utf-8'))
        local_document = current_content

# Function to detect keypresses and schedule updates to the server
def on_key_release(event, client_socket, text_widget):
    if hasattr(on_key_release, "after_id"):
        text_widget.after_cancel(on_key_release.after_id)
    on_key_release.after_id = text_widget.after(update_delay, send_partial_update, client_socket, text_widget)

# Function to handle closing the window and disconnecting from the server
def on_closing(root, client_socket):
    client_socket.close()  # Close the client socket
    root.destroy()  # Close the GUI window

# Function to save the current document to a local file
def save_document(text_widget):
    # Open a file dialog to select the file location
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        try:
            with open(file_path, "w") as file:
                # Write the current document content to the file
                file.write(text_widget.get(1.0, tk.END).strip())
            print(f"Document saved successfully to {file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save the document: {e}")

# Function to update the user list in the GUI
def update_user_list(user_list_widget, users):
    user_list_widget.config(state='normal')
    user_list_widget.delete(1.0, tk.END)
    user_list_widget.insert(tk.END, "Connected Users: " + ", ".join(users))
    user_list_widget.config(state='disabled')

# Function to update the chat display
def update_chat_display(chat_display_widget, username, message):
    chat_display_widget.config(state='normal')
    chat_display_widget.insert(tk.END, f"{username}: {message}\n")
    chat_display_widget.see(tk.END)
    chat_display_widget.config(state='disabled')

# Function to send a chat message
def send_chat_message(event=None):
    message = chat_entry.get().strip()
    if message:
        msg = json.dumps({'type': 'CHAT', 'content': message}) + '\n'
        client.sendall(msg.encode('utf-8'))
        chat_entry.delete(0, tk.END)

# Start the client-side program
def start_client(username):
    global client, chat_entry
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        # Send the username to the server
        msg = json.dumps({'type': 'USERNAME', 'username': username}) + '\n'
        client.sendall(msg.encode('utf-8'))

        root = tk.Tk()
        root.title("Collaborative Document Editor")
        root.configure(bg='gray')

        # Make the window full screen
        root.state('zoomed')

        # Call on_closing() when the window is closed
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, client))

        # Create a menu bar
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # Add a "File" menu with a "Save" option
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save", command=lambda: save_document(text_widget))
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create a frame for the user list at the top
        user_list_widget = tk.Text(root, height=1, wrap='none', font=('Arial', 10),
                                   state='disabled', borderwidth=0, bg='gray', fg='white')
        user_list_widget.pack(side='top', fill='x')

        # Create the main frame
        main_frame = tk.Frame(root, bg='gray')
        main_frame.pack(fill='both', expand=True)

        # Create a canvas to hold the A4 size page
        canvas = tk.Canvas(main_frame, bg='gray')
        canvas.pack(side='left', fill='both', expand=True)

        # Add vertical scrollbar to the canvas
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='left', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to represent the A4 page with margins
        page_width = 794  # A4 width in pixels at 96 DPI
        page_height = 1123  # A4 height in pixels at 96 DPI
        margin = 50  # Margin size in pixels

        # Center the page in the canvas
        def center_page(event=None):
            canvas_width = canvas.winfo_width()
            x = (canvas_width - page_width) // 2
            if x < 0:
                x = 0
            canvas.coords(page_window, x, 0)

        page_frame = tk.Frame(canvas, width=page_width, height=page_height, bg='white')
        page_window = canvas.create_window(0, 0, window=page_frame, anchor='nw')

        # Bind the canvas size change to center the page
        canvas.bind('<Configure>', center_page)

        # Add the text widget inside the page frame with margins
        text_widget = tk.Text(page_frame, wrap='word', font=('Arial', 12), undo=True,
                              bg='white', borderwidth=0)
        text_widget.place(x=margin, y=margin, width=page_width - 2 * margin, height=page_height - 2 * margin)

        # Update scroll region
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))

        page_frame.bind('<Configure>', update_scroll_region)

        # Create the chat panel on the right
        chat_frame = tk.Frame(main_frame, bg='lightgray', bd=1, relief='sunken')
        chat_frame.pack(side='right', fill='y')

        # Create a button to minimize/maximize the chat panel
        def toggle_chat():
            if chat_frame.winfo_viewable():
                chat_frame.pack_forget()
                toggle_button.config(text='Show Chat')
            else:
                chat_frame.pack(side='right', fill='y')
                toggle_button.config(text='Hide Chat')

        toggle_button = tk.Button(root, text='Hide Chat', command=toggle_chat)
        toggle_button.place(relx=1.0, rely=0.0, anchor='ne')

        # Chat display widget
        chat_display_widget = tk.Text(chat_frame, wrap='word', state='disabled', width=30, bg='white')
        chat_display_widget.pack(side='top', fill='both', expand=True)

        # Chat entry widget
        chat_entry = tk.Entry(chat_frame)
        chat_entry.pack(side='bottom', fill='x')
        chat_entry.bind('<Return>', send_chat_message)

        # Bind key release events to schedule document updates to the server
        text_widget.bind("<KeyRelease>", lambda event: on_key_release(event, client, text_widget))

        # Start a thread to receive messages from the server
        receive_thread = threading.Thread(target=update_document_from_server,
                                          args=(text_widget, client, user_list_widget, chat_display_widget))
        receive_thread.daemon = True
        receive_thread.start()

        root.mainloop()

    except socket.error as err:
        print(f"Failed to connect to the server: {err}")

# Prompt the user to connect to the server with a username
username = input("Enter your username: ").strip()
if username:
    start_client(username)
