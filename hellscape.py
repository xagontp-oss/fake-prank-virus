import sys
import random
import math
import pygame
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QKeySequence, QImage
from PyQt5.QtWidgets import QShortcut

print("Starting hellscape.py")

# Resource path for PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    path = os.path.join(base_path, relative_path)
    print(f"Resolved path for {relative_path}: {path}")
    return path

# Initialize Pygame
try:
    pygame.init()
    print("Pygame initialized successfully")
except Exception as e:
    print(f"Pygame initialization failed: {e}")
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
print(f"Screen resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Load assets
try:
    blood_path = resource_path("blood.png")
    print(f"Loading blood.png from: {blood_path}")
    BLOOD_IMAGE = pygame.image.load(blood_path)
    BLOOD_IMAGE = pygame.transform.scale(BLOOD_IMAGE, (100, 100))
    print("blood.png loaded successfully")
except Exception as e:
    print(f"Error loading blood.png: {e}")
    BLOOD_IMAGE = None

try:
    sound_path = resource_path("robot_scream.wav")
    print(f"Loading robot_scream.wav from: {sound_path}")
    pygame.mixer.init()
    error_sound = pygame.mixer.Sound(sound_path)
    error_sound.play(loops=-1)
    print("robot_scream.wav loaded and playing")
except Exception as e:
    print(f"Error loading robot_scream.wav: {e}")
    error_sound = None

# Generate additional sounds
try:
    # Generate simple waveforms for beep, whisper, heartbeat
    import numpy as np
    sample_rate = 44100
    duration = 0.1  # Short sounds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Beep: High-frequency sine wave
    beep_wave = (np.sin(2 * np.pi * 1000 * t) * 32767 / 2).astype(np.int16)
    beep_sound = pygame.mixer.Sound(beep_wave)
    # Whisper: Low-frequency noise
    whisper_wave = (np.random.uniform(-0.2, 0.2, len(t)) * 32767 / 4).astype(np.int16)
    whisper_sound = pygame.mixer.Sound(whisper_wave)
    # Heartbeat: Low-frequency sine wave
    heartbeat_wave = (np.sin(2 * np.pi * 100 * t) * 32767 / 4).astype(np.int16)
    heartbeat_sound = pygame.mixer.Sound(heartbeat_wave)
    print("Additional sounds generated")
except Exception as e:
    print(f"Error generating sounds: {e}")
    beep_sound = whisper_sound = heartbeat_sound = None

# Lists for effects
blood_splatters = []    # (x, y, size, start_time, alpha, color)
cursor_trail = []       # (x, y, start_time, color)
error_popups = []       # (x, y, text, start_time, jitter_x, jitter_y)
drips = []              # (x, y, length, start_time, color)
static_glitches = []    # (x, y, w, h, start_time)
blood_overlays = []     # (start_time, alpha, color)
tentacles = []          # (x, y, angle, length, start_time)
eyeballs = []           # (x, y, size, start_time, blink_state, dx, dy)
gears = []              # (x, y, size, angle, start_time)
code_rain = []          # (x, y, text, start_time)
corrupted_files = []    # (x, y, text, start_time)
hearts = []             # (x, y, size, start_time)
cracks = []             # (x, y, length, angle, start_time)
warnings = []           # (x, y, size, start_time)
ghost_cursors = []      # (x, y, start_time, dx, dy)
worms = []              # (x, y, angle, length, start_time)
lightning = []          # (x1, y1, x2, y2, start_time)
scan_bars = []          # (x, y, width, progress, start_time)
melts = []              # (x, y, length, start_time, color)

class PrankWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Initializing PrankWindow")
        self.setWindowTitle("Neon Cyber Hellscape")
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.exit_timer = QTimer(self)
        self.exit_timer.timeout.connect(self.close)
        self.exit_timer.start(60000)  # 60 seconds
        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut.activated.connect(self.close)
        try:
            self.pygame_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            print("Pygame surface created")
        except Exception as e:
            print(f"Error creating Pygame surface: {e}")
        self.pygame_clock = pygame.time.Clock()
        self.glitch_timer = 0
        self.glitch_interval = 50
        self.shake_timer = 0
        self.shake_interval = 1500
        self.shake_offset = (0, 0)
        self.flash_timer = 0
        self.flash_interval = 1000
        self.flash_color = None
        self.popup_timer = 0
        self.popup_interval = 500
        self.invert_timer = 0
        self.invert_interval = 3000
        self.invert = False
        self.static_timer = 0
        self.static_interval = 800
        self.overlay_timer = 0
        self.overlay_interval = 1500
        self.drip_timer = 0
        self.drip_interval = 300
        self.tentacle_timer = 0
        self.tentacle_interval = 1200
        self.eyeball_timer = 0
        self.eyeball_interval = 1800
        self.gear_timer = 0
        self.gear_interval = 2000
        self.code_timer = 0
        self.code_interval = 600
        self.file_timer = 0
        self.file_interval = 1000
        self.heart_timer = 0
        self.heart_interval = 2500
        self.crack_timer = 0
        self.crack_interval = 1500
        self.warning_timer = 0
        self.warning_interval = 1400
        self.ghost_timer = 0
        self.ghost_interval = 1200
        self.worm_timer = 0
        self.worm_interval = 1600
        self.lightning_timer = 0
        self.lightning_interval = 2000
        self.scan_timer = 0
        self.scan_interval = 2500
        self.melt_timer = 0
        self.melt_interval = 1800
        self.beep_timer = 0
        self.beep_interval = 2500
        self.whisper_timer = 0
        self.whisper_interval = 3500
        self.heartbeat_timer = 0
        self.heartbeat_interval = 4000
        self.show_prank_message()

    def show_prank_message(self):
        print("Showing prank message")
        msg = QMessageBox(self)
        msg.setWindowTitle("Neon Cyber Hellscape Prank")
        msg.setText("WARNING: This is a harmless prank! Brace for EXTREME neon gore, blood, tentacles, eyeballs, worms, and screams. Press Ctrl+Q or wait 60 seconds to exit.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def paintEvent(self, event):
        print("Entering paintEvent")
        painter = QPainter(self)
        current_time = pygame.time.get_ticks()
        self.invert_timer += self.pygame_clock.get_time()
        if self.invert_timer > self.invert_interval:
            self.invert_timer = 0
            self.invert = True
            QTimer.singleShot(600, lambda: setattr(self, 'invert', False))
        if self.invert:
            painter.fillRect(self.rect(), QColor(255, 255, 0, 220))
            for x in range(0, SCREEN_WIDTH, 20):
                for y in range(0, SCREEN_HEIGHT, 20):
                    pygame.draw.circle(self.pygame_surface, (random.randint(0, 255), 0, random.randint(0, 255), 100), (x, y), 7)
            print("Drawing neon inversion grid")
        else:
            self.flash_timer += self.pygame_clock.get_time()
            if self.flash_timer > self.flash_interval:
                self.flash_timer = 0
                colors = [(255, 0, 0, 180), (0, 255, 0, 180), (255, 0, 255, 180), (255, 255, 0, 180)]
                self.flash_color = random.choice(colors)
                QTimer.singleShot(300, lambda: setattr(self, 'flash_color', None))
                print(f"Flashing color: {self.flash_color}")
            if self.flash_color:
                painter.fillRect(self.rect(), QColor(*self.flash_color))
            else:
                pulse_alpha = 70 + int(70 * math.sin(current_time / 300.0))
                painter.fillRect(self.rect(), QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), pulse_alpha))
                print(f"Drawing neon pulse with alpha: {pulse_alpha}")
        self.shake_timer += self.pygame_clock.get_time()
        if self.shake_timer > self.shake_interval:
            self.shake_timer = 0
            self.shake_offset = (random.randint(-20, 20), random.randint(-20, 20))
            QTimer.singleShot(200, lambda: setattr(self, 'shake_offset', (0, 0)))
        self.setGeometry(self.shake_offset[0], self.shake_offset[1], SCREEN_WIDTH, SCREEN_HEIGHT)
        print(f"Screen shake offset: {self.shake_offset}")
        self.pygame_surface.fill((0, 0, 0, 0))
        self.overlay_timer += self.pygame_clock.get_time()
        if self.overlay_timer > self.overlay_interval:
            self.overlay_timer = 0
            color = random.choice([(255, 0, 0), (0, 255, 0), (255, 0, 255), (255, 255, 0)])
            blood_overlays.append((current_time, random.randint(140, 240), color))
        for overlay in blood_overlays[:]:
            start_time, alpha, color = overlay
            if current_time - start_time < 600:
                if BLOOD_IMAGE:
                    scaled_image = pygame.transform.scale(BLOOD_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.pygame_surface.blit(scaled_image, (0, 0))
                else:
                    pygame.draw.rect(self.pygame_surface, color + (alpha,), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"Drawing neon blood overlay with alpha: {alpha}")
            else:
                blood_overlays.remove(overlay)
        for splatter in blood_splatters[:]:
            x, y, size, start_time, alpha, color = splatter
            if current_time - start_time < 5000:
                if BLOOD_IMAGE:
                    scaled_image = pygame.transform.scale(BLOOD_IMAGE, (size, size))
                    self.pygame_surface.blit(scaled_image, (x - size // 2, y - size // 2))
                else:
                    pygame.draw.circle(self.pygame_surface, color + (alpha,), (x, y), size // 2)
                for _ in range(15):
                    px = x + random.randint(-size // 2, size // 2)
                    py = y + random.randint(-size // 2, size // 2)
                    pygame.draw.circle(self.pygame_surface, (255, 255, 0, 150), (px, py), 5)
                print(f"Drawing gore splatter with sparks at: ({x}, {y})")
            else:
                blood_splatters.remove(splatter)
        self.drip_timer += self.pygame_clock.get_time()
        if self.drip_timer > self.drip_interval:
            self.drip_timer = 0
            x = random.randint(0, SCREEN_WIDTH)
            color = random.choice([(255, 0, 0), (0, 255, 0), (255, 0, 255), (255, 255, 0)])
            drips.append((x, 0, 0, current_time, color))
        for drip in drips[:]:
            x, y, length, start_time, color = drip
            if current_time - start_time < 6000:
                length += (current_time - start_time) // 30
                pygame.draw.line(self.pygame_surface, color + (220,), (x, y), (x, y + length), 8)
                pygame.draw.circle(self.pygame_surface, color + (220,), (x, y + length), 12)
                print(f"Drawing neon drip puddle at: ({x}, {y + length})")
            else:
                drips.remove(drip)
        self.static_timer += self.pygame_clock.get_time()
        if self.static_timer > self.static_interval:
            self.static_timer = 0
            for _ in range(10):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                w = random.randint(150, 500)
                h = random.randint(100, 300)
                static_glitches.append((x, y, w, h, current_time))
        for glitch in static_glitches[:]:
            x, y, w, h, start_time = glitch
            if current_time - start_time < 800:
                for i in range(100):
                    rx = x + random.randint(0, w)
                    ry = y + random.randint(0, h)
                    pygame.draw.rect(self.pygame_surface, (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255), 200), (rx, ry, 8, 8))
                print(f"Drawing glitch storm at: ({x}, {y})")
            else:
                static_glitches.remove(glitch)
        self.popup_timer += self.pygame_clock.get_time()
        if self.popup_timer > self.popup_interval:
            self.popup_timer = 0
            error_texts = ["GORE CONSUMES ALL!", "EYES BLEED FOREVER!", "BLOOD CODE INFECTS!", "NEON HELL AWAKENS!", "YOUR SOUL DRIPS!"]
            x = random.randint(100, SCREEN_WIDTH - 600)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            jitter_x = random.randint(-20, 20)
            jitter_y = random.randint(-20, 20)
            error_popups.append((x, y, random.choice(error_texts), current_time, jitter_x, jitter_y))
        for popup in error_popups[:]:
            x, y, text, start_time, jitter_x, jitter_y = popup
            if current_time - start_time < 4000:
                font = pygame.font.SysFont("impact", 60, bold=True)
                text_surface = font.render(text, True, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                self.pygame_surface.blit(text_surface, (x + jitter_x, y + jitter_y))
                pygame.draw.rect(self.pygame_surface, (0, 0, 0, 230), (x - 20, y - 20, 600, 120), 10)
                print(f"Drawing haunted popup: {text}")
            else:
                error_popups.remove(popup)
        self.tentacle_timer += self.pygame_clock.get_time()
        if self.tentacle_timer > self.tentacle_interval:
            self.tentacle_timer = 0
            x = random.choice([0, SCREEN_WIDTH])
            y = random.randint(0, SCREEN_HEIGHT)
            angle = random.randint(0, 360)
            tentacles.append((x, y, angle, 0, current_time))
        for tentacle in tentacles[:]:
            x, y, angle, length, start_time = tentacle
            if current_time - start_time < 6000:
                length += (current_time - start_time) // 40
                for i in range(0, int(length), 20):
                    tx = x + i * math.cos(math.radians(angle + math.sin(current_time / 500.0) * 20))
                    ty = y + i * math.sin(math.radians(angle + math.sin(current_time / 500.0) * 20))
                    pygame.draw.circle(self.pygame_surface, (0, 255, 0, 220), (tx, ty), 12)
                print(f"Drawing writhing tentacle from: ({x}, {y})")
            else:
                tentacles.remove(tentacle)
        self.eyeball_timer += self.pygame_clock.get_time()
        if self.eyeball_timer > self.eyeball_interval:
            self.eyeball_timer = 0
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            size = random.randint(60, 120)
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            eyeballs.append((x, y, size, current_time, True, dx, dy))
        for eyeball in eyeballs[:]:
            x, y, size, start_time, blink_state, dx, dy = eyeball
            if current_time - start_time < 7000:
                x += dx
                y += dy
                if x < 50 or x > SCREEN_WIDTH - 50:
                    dx = -dx
                if y < 50 or y > SCREEN_HEIGHT - 50:
                    dy = -dy
                if (current_time - start_time) % 800 < 400:
                    blink_state = True
                else:
                    blink_state = False
                pygame.draw.circle(self.pygame_surface, (255, 255, 255, 255), (x, y), size // 2)
                if blink_state:
                    pygame.draw.circle(self.pygame_surface, (255, 0, 0, 255), (x, y), size // 4)
                    pygame.draw.circle(self.pygame_surface, (0, 0, 0, 255), (x, y), size // 8)
                    pygame.draw.line(self.pygame_surface, (255, 0, 0, 200), (x, y), (x, y + size), 5)
                print(f"Drawing eyeball at: ({x}, {y}), blink: {blink_state}")
            else:
                eyeballs.remove(eyeball)
        self.gear_timer += self.pygame_clock.get_time()
        if self.gear_timer > self.gear_interval:
            self.gear_timer = 0
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            size = random.randint(50, 150)
            gears.append((x, y, size, 0, current_time))
        for gear in gears[:]:
            x, y, size, angle, start_time = gear
            if current_time - start_time < 6000:
                angle += (current_time - start_time) / 100.0
                for i in range(8):
                    tooth_angle = angle + i * 45
                    tx = x + (size // 2) * math.cos(math.radians(tooth_angle))
                    ty = y + (size // 2) * math.sin(math.radians(tooth_angle))
                    pygame.draw.circle(self.pygame_surface, (255, 255, 0, 200), (tx, ty), 10)
                pygame.draw.circle(self.pygame_surface, (255, 0, 255, 200), (x, y), size // 2)
                print(f"Drawing gore gear at: ({x}, {y})")
            else:
                gears.remove(gear)
        self.code_timer += self.pygame_clock.get_time()
        if self.code_timer > self.code_interval:
            self.code_timer = 0
            x = random.randint(0, SCREEN_WIDTH - 50)
            y = 0
            text = ''.join(random.choice('01BLOODGOREHELLSCAPE') for _ in range(20))
            code_rain.append((x, y, text, current_time))
        for code in code_rain[:]:
            x, y, text, start_time = code
            if y < SCREEN_HEIGHT:
                y += (current_time - start_time) // 10
                font = pygame.font.SysFont("couriernew", 20)
                text_surface = font.render(text, True, (255, 0, 0, 200))
                self.pygame_surface.blit(text_surface, (x, y))
                print(f"Drawing blood code rain at: ({x}, {y})")
            else:
                code_rain.remove(code)
        self.file_timer += self.pygame_clock.get_time()
        if self.file_timer > self.file_interval:
            self.file_timer = 0
            x = random.randint(0, SCREEN_WIDTH - 200)
            y = random.randint(0, SCREEN_HEIGHT - 50)
            text = f"CORRUPTED: gore{random.randint(1, 999)}.dll"
            corrupted_files.append((x, y, text, current_time))
        for file in corrupted_files[:]:
            x, y, text, start_time = file
            if current_time - start_time < 4000:
                font = pygame.font.SysFont("arial", 24)
                text_surface = font.render(text, True, (255, 0, 0, 200))
                self.pygame_surface.blit(text_surface, (x, y))
                print(f"Drawing corrupted file: {text}")
            else:
                corrupted_files.remove(file)
        self.heart_timer += self.pygame_clock.get_time()
        if self.heart_timer > self.heart_interval:
            self.heart_timer = 0
            x = SCREEN_WIDTH // 2
            y = SCREEN_HEIGHT // 2
            size = random.randint(100, 200)
            hearts.append((x, y, size, current_time))
        for heart in hearts[:]:
            x, y, size, start_time = heart
            if current_time - start_time < 5000:
                scale = 1 + 0.2 * math.sin(current_time / 200.0)
                pygame.draw.circle(self.pygame_surface, (255, 0, 0, 200), (x, y), int(size * scale) // 2)
                for i in range(4):
                    vx = x + random.randint(-100, 100)
                    vy = y + random.randint(-100, 100)
                    pygame.draw.line(self.pygame_surface, (255, 0, 0, 150), (x, y), (vx, vy), 5)
                print(f"Drawing pulsating heart at: ({x}, {y})")
            else:
                hearts.remove(heart)
        self.crack_timer += self.pygame_clock.get_time()
        if self.crack_timer > self.crack_interval:
            self.crack_timer = 0
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            length = random.randint(50, 200)
            angle = random.randint(0, 360)
            cracks.append((x, y, length, angle, current_time))
        for crack in cracks[:]:
            x, y, length, angle, start_time = crack
            if current_time - start_time < 4000:
                end_x = x + length * math.cos(math.radians(angle))
                end_y = y + length * math.sin(math.radians(angle))
                pygame.draw.line(self.pygame_surface, (255, 255, 0, 200), (x, y), (end_x, end_y), 6)
                print(f"Drawing neon crack at: ({x}, {y})")
            else:
                cracks.remove(crack)
        self.warning_timer += self.pygame_clock.get_time()
        if self.warning_timer > self.warning_interval:
            self.warning_timer = 0
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            size = random.randint(80, 160)
            warnings.append((x, y, size, current_time))
        for warning in warnings[:]:
            x, y, size, start_time = warning
            if current_time - start_time < 3000:
                points = [(x, y - size // 2), (x - size // 2, y + size // 2), (x + size // 2, y + size // 2)]
                pygame.draw.polygon(self.pygame_surface, (255, 0, 0, 200), points)
                font = pygame.font.SysFont("arial", 24)
                text_surface = font.render("GORE WARNING!", True, (255, 255, 0))
                self.pygame_surface.blit(text_surface, (x - 60, y - 20))
                print(f"Drawing warning triangle at: ({x}, {y})")
            else:
                warnings.remove(warning)
        self.ghost_timer += self.pygame_clock.get_time()
        if self.ghost_timer > self.ghost_interval:
            self.ghost_timer = 0
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            ghost_cursors.append((x, y, current_time, dx, dy))
        for ghost in ghost_cursors[:]:
            x, y, start_time, dx, dy = ghost
            if current_time - start_time < 5000:
                x += dx
                y += dy
                if x < 0 or x > SCREEN_WIDTH:
                    dx = -dx
                if y < 0 or y > SCREEN_HEIGHT:
                    dy = -dy
                pygame.draw.circle(self.pygame_surface, (0, 255, 255, 150), (x, y), 15)
                print(f"Drawing ghost cursor at: ({x}, {y})")
            else:
                ghost_cursors.remove(ghost)
        self.worm_timer += self.pygame_clock.get_time()
        if self.worm_timer > self.worm_interval:
            self.worm_timer = 0
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            angle = random.randint(0, 360)
            worms.append((x, y, angle, 0, current_time))
        for worm in worms[:]:
            x, y, angle, length, start_time = worm
            if current_time - start_time < 6000:
                length += (current_time - start_time) // 50
                for i in range(0, int(length), 10):
                    wx = x + i * math.cos(math.radians(angle + math.sin(current_time / 300.0) * 30))
                    wy = y + i * math.sin(math.radians(angle + math.sin(current_time / 300.0) * 30))
                    pygame.draw.circle(self.pygame_surface, (255, 0, 255, 200), (wx, wy), 8)
                print(f"Drawing gore worm at: ({x}, {y})")
            else:
                worms.remove(worm)
        self.lightning_timer += self.pygame_clock.get_time()
        if self.lightning_timer > self.lightning_interval:
            self.lightning_timer = 0
            x1 = random.randint(0, SCREEN_WIDTH)
            y1 = random.randint(0, SCREEN_HEIGHT // 2)
            x2 = x1 + random.randint(-200, 200)
            y2 = y1 + random.randint(100, 400)
            lightning.append((x1, y1, x2, y2, current_time))
        for bolt in lightning[:]:
            x1, y1, x2, y2, start_time = bolt
            if current_time - start_time < 300:
                pygame.draw.line(self.pygame_surface, (255, 255, 0, 255), (x1, y1), (x2, y2), 10)
                for i in range(5):
                    mx = (x1 + x2) / 2 + random.randint(-50, 50)
                    my = (y1 + y2) / 2 + random.randint(-50, 50)
                    pygame.draw.line(self.pygame_surface, (255, 255, 0, 200), (x1, y1), (mx, my), 5)
                    pygame.draw.line(self.pygame_surface, (255, 255, 0, 200), (mx, my), (x2, y2), 5)
                print(f"Drawing lightning bolt from: ({x1}, {y1}) to ({x2}, {y2})")
            else:
                lightning.remove(bolt)
        self.scan_timer += self.pygame_clock.get_time()
        if self.scan_timer > self.scan_interval:
            self.scan_timer = 0
            x = random.randint(100, SCREEN_WIDTH - 300)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            width = random.randint(200, 400)
            scan_bars.append((x, y, width, 0, current_time))
        for bar in scan_bars[:]:
            x, y, width, progress, start_time = bar
            if current_time - start_time < 4000:
                progress = min((current_time - start_time) / 40, width)
                pygame.draw.rect(self.pygame_surface, (0, 255, 0, 150), (x, y, progress, 20))
                font = pygame.font.SysFont("arial", 16)
                text_surface = font.render("GORE SCANNING...", True, (255, 255, 0))
                self.pygame_surface.blit(text_surface, (x, y - 20))
                print(f"Drawing scan bar at: ({x}, {y})")
            else:
                scan_bars.remove(bar)
        self.melt_timer += self.pygame_clock.get_time()
        if self.melt_timer > self.melt_interval:
            self.melt_timer = 0
            x = random.randint(0, SCREEN_WIDTH)
            color = random.choice([(255, 0, 0), (0, 255, 0), (255, 0, 255), (255, 255, 0)])
            melts.append((x, 0, 0, current_time, color))
        for melt in melts[:]:
            x, y, length, start_time, color = melt
            if current_time - start_time < 6000:
                length += (current_time - start_time) // 20
                for i in range(0, int(length), 10):
                    mx = x + random.randint(-15, 15)
                    my = y + i
                    pygame.draw.circle(self.pygame_surface, color + (200,), (mx, my), 10)
                print(f"Drawing melting ooze at: ({x}, {y + length})")
            else:
                melts.remove(melt)
        self.beep_timer += self.pygame_clock.get_time()
        if self.beep_timer > self.beep_interval:
            self.beep_timer = 0
            if beep_sound:
                beep_sound.play()
                print("Playing glitch beep")
        self.whisper_timer += self.pygame_clock.get_time()
        if self.whisper_timer > self.whisper_interval:
            self.whisper_timer = 0
            if whisper_sound:
                whisper_sound.play()
                print("Playing whisper sound")
        self.heartbeat_timer += self.pygame_clock.get_time()
        if self.heartbeat_timer > self.heartbeat_interval:
            self.heartbeat_timer = 0
            if heartbeat_sound:
                heartbeat_sound.play()
                print("Playing heartbeat sound")
        if error_sound:
            volume = 0.6 + 0.4 * math.sin(current_time / 1200.0)
            error_sound.set_volume(volume)
            print(f"Setting scream volume: {volume}")
        try:
            pygame_image = pygame.image.tostring(self.pygame_surface, "RGBA")
            qimage = QImage(pygame_image, SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_RGBA8888)
            painter.drawImage(0, 0, qimage)
            print("Drawing Pygame surface")
        except Exception as e:
            print(f"Error drawing Pygame surface: {e}")
        self.pygame_clock.tick(60)

    def mousePressEvent(self, event):
        size = random.randint(80, 200)
        alpha = random.randint(180, 255)
        color = random.choice([(255, 0, 0), (0, 255, 0), (255, 0, 255), (255, 255, 0)])
        blood_splatters.append((event.x(), event.y(), size, pygame.time.get_ticks(), alpha, color))
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        angle = random.randint(0, 360)
        worms.append((x, y, angle, 0, pygame.time.get_ticks()))
        for _ in range(10):
            px = event.x() + random.randint(-50, 50)
            py = event.y() + random.randint(-50, 50)
            blood_splatters.append((px, py, size // 2, pygame.time.get_ticks(), alpha, color))
        print(f"Mouse click spawned splatters and worm at: ({event.x()}, {event.y()})")

    def mouseMoveEvent(self, event):
        color = random.choice([(255, 0, 0), (0, 255, 0), (255, 0, 255), (255, 255, 0)])
        cursor_trail.append((event.x(), event.y(), pygame.time.get_ticks(), color))
        print(f"Mouse moved, trail at: ({event.x()}, {event.y()})")

def main():
    print("Entering main function")
    app = QApplication(sys.argv)
    window = PrankWindow()
    window.showFullScreen()
    app.exec_()
    pygame.quit()
    print("Exiting application")

if __name__ == "__main__":
    main()