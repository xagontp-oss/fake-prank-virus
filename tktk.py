import tkinter as tk
import random
import threading
import time

# ==== EDIT THESE ====
NUM_POPUPS = 100            # Number of popups
DELAY = 0.000000000000000000000000000000001                # Delay between popups (seconds)
MESSAGES = ["SHOWTIME;)"]
COLORS = ["red", "green", "blue", "yellow", "orange", "pink", "purple"]
# =====================

def show_popup():
    popup = tk.Tk()
    popup.overrideredirect(True)  # No title bar
    popup.config(bg=random.choice(COLORS))

    # Get screen size and set popup to 74% of it
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    width = int(screen_width * 0.74)
    height = int(screen_height * 0.74)

    # Random position (so it still fits)
    x = random.randint(0, screen_width - width)
    y = random.randint(0, screen_height - height)
    popup.geometry(f"{width}x{height}+{x}+{y}")

    # Message label
    label = tk.Label(popup, text=random.choice(MESSAGES), bg=popup["bg"], fg="white", font=("Arial", 24))
    label.pack(expand=True, fill="both")

    # Close after 300 seconds
    popup.after(300000, popup.destroy)
    popup.mainloop()

# Create and start popups with a delay between each
threads = []
for _ in range(NUM_POPUPS):
    t = threading.Thread(target=show_popup)
    t.start()
    threads.append(t)
    time.sleep(DELAY)  # Delay before spawning the next popup

for t in threads:
    t.join()
