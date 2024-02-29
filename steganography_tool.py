import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os

# Define colors and styles
bg_color = "#343a40"
text_color = "#f8f9fa"
button_color = "#007bff"
error_color = "red"
success_color = "Green"
font = "Helvetica 10"

def embed_message_into_image(image_path, message, output_path):
    try:
        image = Image.open(image_path)
        encoded_image = _encode_message_in_image(image, message)
        encoded_image.save(output_path)
        messagebox.showinfo("Success", f"Message successfully hidden in image and saved as {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def _encode_message_in_image(image, message):
    width, height = image.size
    binary_message = ''.join(format(ord(char), '08b') for char in message) + '11111111'  # EOF marker
    max_length = width * height
    if len(binary_message) > max_length:
        raise ValueError(f"Message too long. Maximum length for this image is {max_length // 8} characters.")

    index = 0
    for row in range(height):
        for col in range(width):
            pixel = image.getpixel((col, row))
            new_pixel = list(pixel)
            new_pixel[0] = pixel[0] & ~1 | int(binary_message[index])
            image.putpixel((col, row), tuple(new_pixel))
            index += 1
            if index == len(binary_message):
                return image
    return image

def extract_message_from_image(image_path):
    try:
        image = Image.open(image_path)
        message = _decode_message_from_image(image)
        message_text.delete("1.0", "end")
        message_text.insert("1.0", message)
        messagebox.showinfo("Success", "Message successfully extracted from image.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def _decode_message_from_image(image):
    width, height = image.size
    binary_message = ""
    for row in range(height):
        for col in range(width):
            pixel = image.getpixel((col, row))
            binary_message += str(pixel[0] & 1)

    binary_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    message = ""
    for byte in binary_message:
        if byte == '11111111':  # EOF marker
            break
        message += chr(int(byte, 2))
    return message

def open_image():
    global image_path
    image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if image_path:
        image = Image.open(image_path)
        image.thumbnail((250, 250))
        image_tk = ImageTk.PhotoImage(image)
        image_label.configure(image=image_tk)
        image_label.image = image_tk
        _update_message_max_length()

def _update_message_max_length():
    if image_path:
        image = Image.open(image_path)
        width, height = image.size
        max_length_label.config(text=f"Max Message Length: {width * height // 8} characters")

def hide_message():
    message = message_text.get("1.0", "end-1c")
    if not image_path:
        messagebox.showerror("Error", "Please select an image first.")
        return
    if not message:
        messagebox.showerror("Error", "Please enter a message to hide.")
        return
    output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])
    if output_path:
        embed_message_into_image(image_path, message, output_path)

def extract_message():
    if not image_path:
        messagebox.showerror("Error", "Please select an image first.")
        return
    extract_message_from_image(image_path)

# GUI setup
window = tk.Tk()
window.title("Advanced Steganography Tool")
window.configure(bg=bg_color)

# Styling for tkinter widgets
style = ttk.Style()
style.configure("TButton", font=font, padding=6)
style.configure("TLabel", background=bg_color, foreground=text_color, font=font)
style.map("TButton", foreground=[('pressed', text_color), ('active', text_color)],
          background=[('pressed', '!disabled', button_color), ('active', button_color)])

image_label = tk.Label(window, bg=bg_color)
image_label.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)

message_text = tk.Text(window, height=10, bg=text_color, fg=bg_color, font=font)
message_text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

max_length_label = ttk.Label(window, text="Max Message Length: N/A")
max_length_label.grid(row=2, column=0, columnspan=2, sticky="nsew")

open_image_button = ttk.Button(window, text="Open Image", command=open_image)
open_image_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

hide_message_button = ttk.Button(window, text="Hide Message", command=hide_message)
hide_message_button.grid(row=3, column=1, padx=10, pady=10)

extract_message_button = ttk.Button(window, text="Extract Message", command=extract_message)
extract_message_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

window.mainloop()
