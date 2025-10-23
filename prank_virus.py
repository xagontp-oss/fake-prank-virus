import sys
import random
import math
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QKeySequence, QImage
from PyQt5.QtWidgets import QShortcut

# Initialize Pygame
pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# Load blood splatter image (or use circle as fallback)
try:
    BLOOD_IMAGE = pygame.image.load("blood.png")
    BLOOD_IMAGE = pygame.transform.scale(BLOOD_IMAGE, (100, 100))
except FileNotFoundError:
    print("Warning: blood.png not found. Using red circle.")
    BLOOD_IMAGE = None

# Lists for effects
blood_splatters = []  # (x, y, size, start_time, alpha)
cursor_trail = []     # (x, y, start_time)
error_popups = []     # (x, y, text, start_time, jitter_x, jitter_y)
drips = []            # (x, y, length, start_time)

class PrankWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prank Virus")
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Exit timer (30 seconds)
        self.exit_timer = QTimer(self)
        self.exit_timer.timeout.connect(self.close)
        self.exit_timer.start(30000)

        # Exit shortcut (Ctrl+Q)
        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut.activated.connect(self.close)

        # Pygame surface
        self.pygame_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.pygame_clock = pygame.time.Clock()

        # Effect timers
        self.glitch_timer = 0
        self.glitch_interval = 100   # Blue glitch frequency
        self.shake_timer = 0
        self.shake_interval = 4000   # Screen shake every 4 seconds
        self.shake_offset = (0, 0)
        self.flash_timer = 0
        self.flash_interval = 2500   # Color flash every 2.5 seconds
        self.flash_color = None
        self.popup_timer = 0
        self.popup_interval = 1500   # Error popup every 1.5 seconds
        self.flicker_timer = 0
        self.flicker_interval = 400  # CRT flicker every 400ms
        self.scramble_timer = 0
        self.scramble_interval = 1200  # Text scramble every 1.2 seconds
        self.drip_timer = 0
        self.drip_interval = 500     # New drip every 500ms
        self.pulse_timer = 0
        self.pulse_interval = 1000   # Red overlay pulse every 1 second
        self.bsod_timer = 0
        self.bsod_interval = 8000    # BSOD every 8 seconds
        self.show_bsod = False
        self.invert_timer = 0
        self.invert_interval = 6000  # Invert every 6 seconds
        self.invert = False

        # Sound effect
        pygame.mixer.init()
        try:
            self.error_sound = pygame.mixer.Sound("robot_scream.wav")
        except FileNotFoundError:
            self.error_sound = None
        self.sound_timer = 0
        self.sound_interval = 3000   # Sound every 3 seconds

        # Show prank message
        self.show_prank_message()

    def show_prank_message(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Windows Security")
        msg.setText("Our Windows Security Team- System Breached (Error - 922")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def paintEvent(self, event):
        painter = QPainter(self)
        current_time = pygame.time.get_ticks()

        # BSOD effect
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
            return

        # Screen inversion effect
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
        else:
            # Pulsating red overlay
            self.pulse_timer += self.pygame_clock.get_time()
            if self.pulse_timer > self.pulse_interval:
                self.pulse_timer = 0
            pulse_alpha = 50 + int(50 * math.sin(current_time / 500.0))  # 50-100 alpha
            if self.flash_color:
                painter.fillRect(self.rect(), QColor(*self.flash_color))
            else:
                painter.fillRect(self.rect(), QColor(255, 0, 0, pulse_alpha))

        # Apply screen shake
        if self.shake_timer > self.shake_interval:
            self.shake_timer = 0
            self.shake_offset = (random.randint(-15, 15), random.randint(-15, 15))
            QTimer.singleShot(150, lambda: setattr(self, 'shake_offset', (0, 0)))
        self.setGeometry(self.shake_offset[0], self.shake_offset[1], SCREEN_WIDTH, SCREEN_HEIGHT)

        # Apply color flash
        if self.flash_timer > self.flash_interval:
            self.flash_timer = 0
            colors = [(0, 255, 0, 120), (128, 0, 128, 120)]  # Green, Purple
            self.flash_color = random.choice(colors)
            QTimer.singleShot(250, lambda: setattr(self, 'flash_color', None))

        # Update Pygame surface
        self.pygame_surface.fill((0, 0, 0, 0))

        # Draw blood splatters
        for splatter in blood_splatters[:]:
            x, y, size, start_time, alpha = splatter
            if current_time - start_time < 3000:
                if BLOOD_IMAGE:
                    scaled_image = pygame.transform.scale(BLOOD_IMAGE, (size, size))
                    self.pygame_surface.blit(scaled_image, (x - size // 2, y - size // 2))
                else:
                    pygame.draw.circle(self.pygame_surface, (255, 0, 0, alpha), (x, y), size // 2)
            else:
                blood_splatters.remove(splatter)

        # Draw dripping blood
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
                drips[drips.index(drip)] = (x, y, length, start_time)
            else:
                drips.remove(drip)

        # Draw blue glitch rectangles
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

        # Draw red cursor trail
        for trail in cursor_trail[:]:
            x, y, start_time = trail
            if current_time - start_time < 600:
                pygame.draw.circle(self.pygame_surface, (255, 0, 0, 150), (x, y), 12)
            else:
                cursor_trail.remove(trail)

        # Draw gory error popups
        if self.popup_timer > self.popup_interval:
            self.popup_timer = 0
            error_texts = ["BLOOD SYSTEM FAILURE!", "GORE DETECTED!", "VIRAL INFECTION!", "CRITICAL HEMORRHAGE!"]
            x = random.randint(100, SCREEN_WIDTH - 300)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            jitter_x = random.randint(-5, 5)
            jitter_y = random.randint(-5, 5)
            error_popups.append((x, y, random.choice(error_texts), current_time, jitter_x, jitter_y))
        for popup in error_popups[:]:
            x, y, text, start_time, jitter_x, jitter_y = popup
            if current_time - start_time < 3000:
                font = pygame.font.SysFont("arial", 28, bold=True)
                text_surface = font.render(text, True, (255, 0, 0))
                self.pygame_surface.blit(text_surface, (x + jitter_x, y + jitter_y))
                pygame.draw.rect(self.pygame_surface, (0, 0, 0, 200), (x - 10, y - 10, 300, 60), 3)
            else:
                error_popups.remove(popup)

        # Draw CRT flicker
        self.flicker_timer += self.pygame_clock.get_time()
        if self.flicker_timer > self.flicker_interval:
            self.flicker_timer = 0
            for y in range(0, SCREEN_HEIGHT, 8):
                pygame.draw.line(self.pygame_surface, (255, 255, 255, 60), (0, y), (SCREEN_WIDTH, y))
            QTimer.singleShot(50, self.update)

        # Draw gory text scramble
        self.scramble_timer += self.pygame_clock.get_time()
        if self.scramble_timer > self.scramble_interval:
            self.scramble_timer = 0
            scramble_text = ''.join(random.choice('BLOODGORE123456789!@#$%') for _ in range(25))
            font = pygame.font.SysFont("arial", 32, bold=True)
            text_surface = font.render(scramble_text, True, (255, 0, 0))
            x = random.randint(0, SCREEN_WIDTH - 250)
            y = random.randint(0, SCREEN_HEIGHT - 50)
            self.pygame_surface.blit(text_surface, (x + random.randint(-5, 5), y + random.randint(-5, 5)))

        # Play sound
        self.sound_timer += self.pygame_clock.get_time()
        if self.sound_timer > self.sound_interval and self.error_sound:
            self.sound_timer = 0
            self.error_sound.play()

        # Convert Pygame surface to QImage
        pygame_image = pygame.image.tostring(self.pygame_surface, "RGBA")
        qimage = QImage(pygame_image, SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_RGBA8888)
        painter.drawImage(0, 0, qimage)

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
    app = QApplication(sys.argv)
    window = PrankWindow()
    window.showFullScreen()
    app.exec_()
    pygame.quit()

if __name__ == "__main__":
    main()