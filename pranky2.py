import sys
import random
import math
import pygame
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QKeySequence, QImage
from PyQt5.QtWidgets import QShortcut
import win32api
import win32con

print("Starting prank_virus.py")
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
print(f"Screen resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

try:
    blood_path = resource_path("blood.png")
    print(f"Loading blood.png from: {blood_path}")
    BLOOD_IMAGE = pygame.image.load(blood_path)
    BLOOD_IMAGE = pygame.transform.scale(BLOOD_IMAGE, (100, 100))
except Exception as e:
    print(f"Error loading blood.png: {e}")
    BLOOD_IMAGE = None

blood_splatters = []
cursor_trail = []
error_popups = []
drips = []
static_glitches = []
blood_overlays = []

pygame.mixer.init()
try:
    sound_path = resource_path("robot_scream.wav")
    print(f"Loading robot_scream.wav from: {sound_path}")
    error_sound = pygame.mixer.Sound(sound_path)
    error_sound.play(loops=-1)
except Exception as e:
    print(f"Error loading robot_scream.wav: {e}")
    error_sound = None

class PrankWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Initializing PrankWindow")
        self.setWindowTitle("Prank Virus")
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.exit_timer = QTimer(self)
        self.exit_timer.timeout.connect(self.close)
        self.exit_timer.start(30000)
        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut.activated.connect(self.close)
        self.pygame_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.pygame_clock = pygame.time.Clock()
        self.glitch_timer = 0
        self.glitch_interval = 100
        self.shake_timer = 0
        self.shake_interval = 4000
        self.shake_offset = (0, 0)
        self.flash_timer = 0
        self.flash_interval = 2500
        self.flash_color = None
        self.popup_timer = 0
        self.popup_interval = 1000
        self.flicker_timer = 0
        self.flicker_interval = 400
        self.scramble_timer = 0
        self.scramble_interval = 1200
        self.drip_timer = 0
        self.drip_interval = 500
        self.pulse_timer = 0
        self.pulse_interval = 1000
        self.bsod_timer = 0
        self.bsod_interval = 8000
        self.show_bsod = False
        self.invert_timer = 0
        self.invert_interval = 6000
        self.invert = False
        self.cursor_timer = 0
        self.cursor_interval = 2000
        self.static_timer = 0
        self.static_interval = 1500
        self.overlay_timer = 0
        self.overlay_interval = 3000
        self.dim_timer = 0
        self.dim_interval = 5000
        self.dim_alpha = 0
        self.show_prank_message()

    def show_prank_message(self):
        print("Showing prank message")
        msg = QMessageBox(self)
        msg.setWindowTitle("Prank Alert")
        msg.setText("This is a harmless prank! Screen will turn red with gore, blood drips, glitches, BSOD, inversion, cursor jumps, and more. Press Ctrl+Q or wait 30 seconds to exit.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def paintEvent(self, event):
        print("Entering paintEvent")
        painter = QPainter(self)
        current_time = pygame.time.get_ticks()
        self.bsod_timer += self.pygame_clock.get_time()
        if self.bsod_timer > self.bsod_interval:
            self.bsod_timer = 0
            self.show_bsod = True
            QTimer.singleShot(1000, lambda: setattr(self, 'show_bsod', False))
        if self.show_bsod:
            painter.fillRect(self.rect(), QColor(0, 0, 255, 255))
            font = pygame.font.SysFont("arial", 24)
            text_surface = font.render("SYSTEM CRASH: 0xBLOOD", True, (255, 255, 255))
            self.pygame_surface.blit(text_surface, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            pygame_image = pygame.image.tostring(self.pygame_surface, "RGBA")
            qimage = QImage(pygame_image, SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_RGBA8888)
            painter.drawImage(0, 0, qimage)
            print("Drawing BSOD")
            return
        self.invert_timer += self.pygame_clock.get_time()
        if self.invert_timer > self.invert_interval:
            self.invert_timer = 0
            self.invert = True
            QTimer.singleShot(500, lambda: setattr(self, 'invert', False))
        if self.invert:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 200))
            for x in range(0, SCREEN_WIDTH, 10):
                for y in range(0, SCREEN_HEIGHT, 10):
                    pygame.draw.circle(self.pygame_surface, (255, 0, 0, 60), (x, y), 3)
            print("Drawing inversion")
        else:
            self.pulse_timer += self.pygame_clock.get_time()
            if self.pulse_timer > self.pulse_interval:
                self.pulse_timer = 0
            pulse_alpha = 50 + int(50 * math.sin(current_time / 500.0))
            if self.flash_color:
                painter.fillRect(self.rect(), QColor(*self.flash_color))
            else:
                painter.fillRect(self.rect(), QColor(255, 0, 0, pulse_alpha))
            print(f"Drawing red overlay with alpha: {pulse_alpha}")
        self.dim_timer += self.pygame_clock.get_time()
        if self.dim_timer > self.dim_interval:
            self.dim_timer = 0
            self.dim_alpha = 200
            QTimer.singleShot(300, lambda: setattr(self, 'dim_alpha', 0))
        if self.dim_alpha > 0:
            painter.fillRect(self.rect(), QColor(0, 0, 0, self.dim_alpha))
            print(f"Drawing dim effect with alpha: {self.dim_alpha}")
        self.shake_timer += self.pygame_clock.get_time()
        if self.shake_timer > self.shake_interval:
            self.shake_timer = 0
            self.shake_offset = (random.randint(-15, 15), random.randint(-15, 15))
            QTimer.singleShot(150, lambda: setattr(self, 'shake_offset', (0, 0)))
        self.setGeometry(self.shake_offset[0], self.shake_offset[1], SCREEN_WIDTH, SCREEN_HEIGHT)
        print(f"Screen shake offset: {self.shake_offset}")
        if self.flash_timer > self.flash_interval:
            self.flash_timer = 0
            colors = [(0, 255, 0, 120), (128, 0, 128, 120)]
            self.flash_color = random.choice(colors)
            QTimer.singleShot(250, lambda: setattr(self, 'flash_color', None))
        self.cursor_timer += self.pygame_clock.get_time()
        if self.cursor_timer > self.cursor_interval:
            self.cursor_timer = 0
            new_x = random.randint(0, SCREEN_WIDTH)
            new_y = random.randint(0, SCREEN_HEIGHT)
            win32api.SetCursorPos((new_x, new_y))
            print(f"Cursor jumped to: ({new_x}, {new_y})")
        self.pygame_surface.fill((0, 0, 0, 0))
        for splatter in blood_splatters[:]:
            x, y, size, start_time, alpha = splatter
            if current_time - start_time < 3000:
                if BLOOD_IMAGE:
                    scaled_image = pygame.transform.scale(BLOOD_IMAGE, (size, size))
                    self.pygame_surface.blit(scaled_image, (x - size // 2, y - size // 2))
                else:
                    pygame.draw.circle(self.pygame_surface, (255, 0, 0, alpha), (x, y), size // 2)
                print(f"Drawing blood splatter at: ({x}, {y})")
            else:
                blood_splatters.remove(splatter)
        self.drip_timer += self.pygame_clock.get_time()
        if self.drip_timer > self.drip_interval:
            self.drip_timer = 0
            x = random.randint(0, SCREEN_WIDTH)
            drips.append((x, 0, 0, current_time))
        for drip in drips[:]:
            x, y, length, start_time = drip
            if current_time - start_time < 5000:
                length += (current_time - start_time) // 50
                pygame.draw.line(self.pygame_surface, (255, 0, 0, 200), (x, y), (x, y + length), 5)
                print(f"Drawing drip at: ({x}, {y + length})")
            else:
                drips.remove(drip)
        self.glitch_timer += self.pygame_clock.get_time()
        if self.glitch_timer > self.glitch_interval:
            self.glitch_timer = 0
            for _ in range(7):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                w = random.randint(50, 250)
                h = random.randint(20, 120)
                blue_alpha = random.randint(50, 150)
                pygame.draw.rect(self.pygame_surface, (0, 0, 255, blue_alpha), (x, y, w, h))
                print(f"Drawing blue glitch at: ({x}, {y})")
        self.static_timer += self.pygame_clock.get_time()
        if self.static_timer > self.static_interval:
            self.static_timer = 0
            for _ in range(5):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                w = random.randint(100, 300)
                h = random.randint(50, 200)
                static_glitches.append((x, y, w, h, current_time))
        for glitch in static_glitches[:]:
            x, y, w, h, start_time = glitch
            if current_time - start_time < 500:
                for i in range(50):
                    rx = x + random.randint(0, w)
                    ry = y + random.randint(0, h)
                    pygame.draw.rect(self.pygame_surface, (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255), 150), (rx, ry, 5, 5))
                print(f"Drawing static glitch at: ({x}, {y})")
            else:
                static_glitches.remove(glitch)
        self.overlay_timer += self.pygame_clock.get_time()
        if self.overlay_timer > self.overlay_interval:
            self.overlay_timer = 0
            blood_overlays.append((current_time, random.randint(100, 200)))
        for overlay in blood_overlays[:]:
            start_time, alpha = overlay
            if current_time - start_time < 500:
                if BLOOD_IMAGE:
                    scaled_image = pygame.transform.scale(BLOOD_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.pygame_surface.blit(scaled_image, (0, 0))
                else:
                    pygame.draw.rect(self.pygame_surface, (255, 0, 0, alpha), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"Drawing blood overlay with alpha: {alpha}")
            else:
                blood_overlays.remove(overlay)
        for trail in cursor_trail[:]:
            x, y, start_time = trail
            if current_time - start_time < 600:
                pygame.draw.circle(self.pygame_surface, (255, 0, 0, 150), (x, y), 12)
                print(f"Drawing cursor trail at: ({x}, {y})")
            else:
                cursor_trail.remove(trail)
        if self.popup_timer > self.popup_interval:
            self.popup_timer = 0
            error_texts = ["YOU CAN'T ESCAPE!", "BLOOD OVERLOAD!", "SYSTEM INFECTED!", "DEATH IMMINENT!"]
            x = random.randint(100, SCREEN_WIDTH - 400)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            jitter_x = random.randint(-10, 10)
            jitter_y = random.randint(-10, 10)
            error_popups.append((x, y, random.choice(error_texts), current_time, jitter_x, jitter_y))
        for popup in error_popups[:]:
            x, y, text, start_time, jitter_x, jitter_y = popup
            if current_time - start_time < 3000:
                font = pygame.font.SysFont("impact", 36, bold=True)
                text_surface = font.render(text, True, (255, 0, 0))
                self.pygame_surface.blit(text_surface, (x + jitter_x, y + jitter_y))
                pygame.draw.rect(self.pygame_surface, (0, 0, 0, 200), (x - 10, y - 10, 400, 80), 5)
                print(f"Drawing popup: {text}")
            else:
                error_popups.remove(popup)
        self.flicker_timer += self.pygame_clock.get_time()
        if self.flicker_timer > self.flicker_interval:
            self.flicker_timer = 0
            for y in range(0, SCREEN_HEIGHT, 8):
                pygame.draw.line(self.pygame_surface, (255, 255, 255, 60), (0, y), (SCREEN_WIDTH, y))
            QTimer.singleShot(50, self.update)
            print("Drawing CRT flicker")
        self.scramble_timer += self.pygame_clock.get_time()
        if self.scramble_timer > self.scramble_interval:
            self.scramble_timer = 0
            scramble_text = ''.join(random.choice('BLOODGORE123456789!@#$%') for _ in range(25))
            font = pygame.font.SysFont("impact", 40, bold=True)
            text_surface = font.render(scramble_text, True, (255, 0, 0))
            x = random.randint(0, SCREEN_WIDTH - 250)
            y = random.randint(0, SCREEN_HEIGHT - 50)
            self.pygame_surface.blit(text_surface, (x + random.randint(-10, 10), y + random.randint(-10, 10)))
            print(f"Drawing scramble text: {scramble_text}")
        if error_sound:
            volume = 0.8 + 0.2 * math.sin(current_time / 2000.0)
            error_sound.set_volume(volume)
            print(f"Setting sound volume: {volume}")
        pygame_image = pygame.image.tostring(self.pygame_surface, "RGBA")
        qimage = QImage(pygame_image, SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_RGBA8888)
        painter.drawImage(0, 0, qimage)
        print("Drawing Pygame surface")
        self.pygame_clock.tick(60)

    def mousePressEvent(self, event):
        size = random.randint(50, 150)
        alpha = random.randint(150, 255)
        blood_splatters.append((event.x(), event.y(), size, pygame.time.get_ticks(), alpha))

    def mouseMoveEvent(self, event):
        cursor_trail.append((event.x(), event.y(), pygame.time.get_ticks()))

    def keyPressEvent(self, event):
        pass

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