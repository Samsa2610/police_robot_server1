import tkinter as tk
from tkinter import Label
import sqlite3
import socket
import threading
import json
import cv2
import numpy as np
from PIL import Image, ImageTk
import base64

# Setup GUI window
root = tk.Tk()
root.title("Face Recognition System")
root.geometry("900x600")

# Colors
DEFAULT_COLOR = "gray"
RECOGNIZED_COLOR = "green"

# Connect to database and load suspect data
conn = sqlite3.connect('suspects.db')
c = conn.cursor()
c.execute("SELECT name, id_number, nationality, image FROM suspects")
suspects = []
suspect_images = {}

for row in c.fetchall():
    name, id_number, nationality, image_blob = row
    suspects.append((name, id_number, nationality))

    # Convert stored image blob to a displayable format
    if image_blob:
        nparr = np.frombuffer(image_blob, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.resize((100, 100))  # Resize for display
        suspect_images[f"{name} | ID: {id_number} | {nationality}"] = ImageTk.PhotoImage(image)

conn.close()

# Create icon widgets for each suspect
suspect_icons = {}
suspect_labels = {}
stored_image_labels = {}
captured_image_labels = {}
captured_image_refs = {}  # Store references to avoid Tkinter garbage collection

for idx, (name, id_number, nationality) in enumerate(suspects):
    frame = tk.Frame(root, bg=DEFAULT_COLOR, width=300, height=150, padx=10, pady=10)
    frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=10)

    label_text = f"{name}\nID: {id_number}\n{nationality}"
    label = tk.Label(frame, text=label_text, bg=DEFAULT_COLOR, fg="white")
    label.grid(row=0, column=0, columnspan=2)  # Center the text above images

    suspect_icons[f"{name} | ID: {id_number} | {nationality}"] = frame
    suspect_labels[f"{name} | ID: {id_number} | {nationality}"] = label

    # Display stored image on the left
    if f"{name} | ID: {id_number} | {nationality}" in suspect_images:
        stored_img_label = Label(frame, image=suspect_images[f"{name} | ID: {id_number} | {nationality}"])
        stored_img_label.grid(row=1, column=0, padx=5, pady=5)  # Left side
        stored_image_labels[f"{name} | ID: {id_number} | {nationality}"] = stored_img_label

    # Placeholder for captured image on the right
    captured_img_label = Label(frame, text="No Image", width=14, height=6, bg="black", fg="white")
    captured_img_label.grid(row=1, column=1, padx=5, pady=5)  # Right side
    captured_image_labels[f"{name} | ID: {id_number} | {nationality}"] = captured_img_label
    captured_image_refs[f"{name} | ID: {id_number} | {nationality}"] = None  # Initialize storage for images

# Function to update icons and display real-time images
def update_icons(recognized_names, captured_faces):
    for key in suspect_icons:
        if key in recognized_names:
            suspect_icons[key].config(bg=RECOGNIZED_COLOR)
            suspect_labels[key].config(bg=RECOGNIZED_COLOR)

            # Display the captured image beside the stored image
            if key in captured_faces:
                image_data = base64.b64decode(captured_faces[key])  # Decode base64
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                captured_img = Image.fromarray(img)
                captured_img = captured_img.resize((100, 100))
                captured_img = ImageTk.PhotoImage(captured_img)

                # Store reference and update image
                captured_image_refs[key] = captured_img  # Store reference
                captured_image_labels[key].config(image=captured_img, text="")  # Remove text
                captured_image_labels[key].image = captured_img  # Keep reference
        else:
            suspect_icons[key].config(bg=DEFAULT_COLOR)
            suspect_labels[key].config(bg=DEFAULT_COLOR)
            captured_image_labels[key].config(image="", text="No Image")  # Reset if not recognized

# Socket server to receive recognition data
def socket_server():
    HOST = '127.0.0.1'
    PORT = 65432
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print("GUI is waiting for face recognition system to connect...")

    while True:
        conn, addr = server_socket.accept()
        print("Connected to face recognition system.")

        try:
            while True:
                data = conn.recv(8192)  # Increase buffer size to handle large image data
                if not data:
                    break
                received_data = json.loads(data.decode('utf-8'))
                
                recognized_names = received_data.get("recognized_names", [])
                captured_faces = received_data.get("captured_images", {})

                update_icons(recognized_names, captured_faces)

        except (json.JSONDecodeError, ConnectionResetError, BrokenPipeError):
            print("Connection lost. Waiting for a new connection...")
            conn.close()

# Run socket server in a separate thread
threading.Thread(target=socket_server, daemon=True).start()

# Run the GUI
root.mainloop()





