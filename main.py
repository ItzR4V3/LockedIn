import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QAction,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QDialog,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter
from pynput import keyboard as pynput_key
from pynput.keyboard import Listener as KeyboardListener, KeyCode
from pynput.mouse import Listener
import keyboard
import win32gui
import win32con
import win32api
import ctypes
import time
user32 = ctypes.windll.user32
VK_MENU = 0x12  #alt
VK_TAB = 0x09  #tab 
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
alt_pressed = False

class PinDialog(QDialog):
    def __init__(self, correct_pin, parent=None):
        super(PinDialog, self).__init__(parent)
        self.correct_pin = correct_pin
        self.setWindowTitle("Enter PIN")
        self.setModal(True)

        self.layout = QVBoxLayout()
        self.label = QLabel("Enter the PIN to exit:")
        self.layout.addWidget(self.label)

        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.pin_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_pin)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def check_pin(self):
        if self.pin_input.text() == self.correct_pin:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Incorrect PIN. Try again.")

class KioskBrowser(QMainWindow):
    def __init__(self, screen):
        super(KioskBrowser, self).__init__()
        self.check_keys_timer = QTimer()
        self.check_keys_timer.timeout.connect(self.check_for_alt_tab)
        self.check_keys_timer.start(100)

        keyboard.block_key('Win')
        keyboard.block_key("Alt")
        keyboard.block_key('Ctrl')

        # Set the window for fullscreen on this specific screen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(screen.geometry())
        self.setWindowTitle("LockedIn")

        # Browser setup
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.youtube.com/"))

        self.url_bar = QLineEdit()
        self.url_bar.setText("https://www.youtube.com/")
        self.url_bar.setReadOnly(True)

        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        refresh_btn = QAction("Refresh", self)
        refresh_btn.triggered.connect(self.browser.reload)
        nav_bar.addAction(refresh_btn)

        nav_bar.addWidget(self.url_bar)

        close_button = QPushButton("Close LockedIn")
        close_button.clicked.connect(self.close_kiosk)
        nav_bar.addWidget(close_button)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.browser.urlChanged.connect(self.update_url_bar)

        # Show fullscreen on the current monitor
        self.showFullScreen()

        # Set up key listener and track typed characters
        self.key_listener = pynput_key.Listener(on_press=self.check_for_alt_tab)
        self.key_listener.start()
        self.key_sequence = ""
        
        # Initialize lock mode screen
        self.locked_mode = False
        self.lock_screen = QWidget(self)
        self.lock_screen.setStyleSheet("background-color: red;")
        self.lock_screen.setGeometry(self.rect())
        self.lock_screen.hide()

        self.key_listener = pynput_key.Listener(on_press=self.on_key_press)
        self.key_listener.start()

        # Get screen width and height for centering
        screen_width = screen.geometry().width()
        screen_height = screen.geometry().height()

        # Add text to the locked screen (Locked Mode)
        self.lock_text = QLabel("LOCKED MODE", self.lock_screen)
        self.lock_text.setStyleSheet("color: white; font-size: 60px; font-family: Calibri; font-weight: bold;")
        self.lock_text.adjustSize()
        text_width = self.lock_text.width()
        text_height = self.lock_text.height()
        self.lock_text.move((screen_width - text_width) // 2, (screen_height - text_height) // 3)

        # Lock screen buttons (Bigger and positioned left/right)
        self.unlock_button = QPushButton("Unlock", self.lock_screen)
        self.unlock_button.setStyleSheet("background-color: white; font-size: 20px; padding: 15px 30px; color: black; border-radius: 10px; border: 2px solid black;")
        self.unlock_button.clicked.connect(self.unlock_app)
        button_width = self.unlock_button.width()
        button_height = self.unlock_button.height()
        self.unlock_button.move((screen_width // 2) - (button_width + 100), (screen_height // 2) + 50)

        self.close_button = QPushButton("Close", self.lock_screen)
        self.close_button.setStyleSheet("background-color: white; font-size: 20px; padding: 15px 30px; color: black; border-radius: 10px; border: 2px solid black;")
        self.close_button.clicked.connect(self.close_app)
        self.close_button.move((screen_width // 2) + 100, (screen_height // 2) + 50)

    def on_key_press(self, key):
        try:
            self.key_sequence += key.char
            if self.key_sequence.endswith("kuru"):
                self.enter_locked_mode()
                self.key_sequence = ""
        except AttributeError:
            pass
    def check_for_alt_tab(self):
        # Check if both Alt and Tab are pressed
        if user32.GetAsyncKeyState(VK_MENU) & 0x8000 and user32.GetAsyncKeyState(VK_TAB) & 0x8000:
            self.enter_locked_mode()  # Call your method to trigger locked mode

    def update_url_bar(self, q):
        self.url_bar.setText(q.toString())

    def enter_locked_mode(self):
        if not self.locked_mode:
            self.locked_mode = True
            self.lock_screen.showFullScreen()

    def keyPressEvent(self, event):
        # Block specific keys in the GUI itself
        if event.key() in [Qt.Key_Escape, Qt.Key_F11, Qt.Key_F4, Qt.Key_Alt, Qt.Key_Control]:
            event.ignore()

    def close_kiosk(self):
        dialog = PinDialog(correct_pin="1234", parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.close()
        else:
            print("PIN Dialog was cancelled or incorrect")

    def unlock_app(self):
        dialog = PinDialog(correct_pin="1234", parent=self)  # Set desired PIN here
        if dialog.exec_() == QDialog.Accepted:
            self.lock_screen.hide()
            self.locked_mode = False

    def close_app(self):
        dialog = PinDialog(correct_pin="1234", parent=self)  # Set desired PIN here
        if dialog.exec_() == QDialog.Accepted:
            self.close()

class BlackoutWindow(QMainWindow):
    def __init__(self, screen_geometry):
        super(BlackoutWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setGeometry(screen_geometry)
        self.setStyleSheet("background-color: black;")
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0))  # Black background
        painter.drawRect(self.rect())

if __name__ == "__main__":
    app = QApplication(sys.argv)

    screens = app.screens()

    # Create blackout window for the secondary screen(s)
    windows = []
    for screen in screens:
        if screen == screens[0]:
            # Primary screen - Show the Kiosk Browser
            window = KioskBrowser(screen)
        else:
            # For secondary screens, show a blank screen (blackout window)
            window = BlackoutWindow(screen.geometry())
        windows.append(window)

    sys.exit(app.exec_())