import sys
from playsound import playsound
from PyQt6.QtWidgets import (QApplication,
                             QMainWindow,
                             QDialog,
                             QLabel,
                             QPushButton,
                             QCheckBox,
                             QDoubleSpinBox,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QWidget)
from PyQt6.QtCore import QTimer, Qt

class SettingsWindow(QDialog):
    def __init__(self, parent, duration):
        super().__init__(parent)
        self.initUI()
        self.duration_spinbox.setValue(duration)
        self.duration_spinbox.setMinimum(0)
        self.duration_spinbox.setMaximum(1e10)
        self.duration_spinbox.setMinimumWidth(80)
        self.duration_spinbox.valueChanged.connect(parent.save_settings)
    
    def initUI(self):
        self.setWindowTitle('Settings | Timer Application')
        layout = QGridLayout()
        self.duration_label = QLabel("Timer duration", self)
        self.duration_spinbox = QDoubleSpinBox(self)
        self.sound_checkbox = QCheckBox(self)
        self.sound_label = QLabel("&Play sound", self)
        self.sound_label.setBuddy(self.sound_checkbox)
        layout.addWidget(self.duration_spinbox, 0, 1)
        layout.addWidget(self.duration_label, 0, 0)
        layout.addWidget(self.sound_label, 1, 0)
        layout.addWidget(self.sound_checkbox, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: violet;
                color: white;       
            }
        """)

class TimerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def initUI(self):
        self.setWindowTitle('Timer Application')
        self.settings_window = None
        self.duration = 10.0
        self.label = QLabel(str(self.duration), self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.settings_button = QPushButton('Settings', self)
        self.settings_button.clicked.connect(self.open_settings)
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_timer)
        self.reset_button = QPushButton('Reset', self)
        self.reset_button.clicked.connect(self.reset_timer)

        layoutMain = QVBoxLayout()
        layoutMain.addWidget(self.label)
        layoutButtons = QHBoxLayout()
        layoutButtons.addWidget(self.settings_button)
        layoutButtons.addWidget(self.start_button)
        layoutButtons.addWidget(self.reset_button)
        layoutMain.addLayout(layoutButtons)

        container = QWidget()
        container.setLayout(layoutMain)

        self.setCentralWidget(container)


    def open_settings(self):
        print("Opened settings.")
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self, self.duration)
        self.settings_window.exec()

    def save_settings(self, value):
        self.duration = value
        time = self.get_time(self.duration)
        self.label.setText(time)

    def reset_timer(self):
        print("Reset timer")
        self.timer.stop()
        time = self.get_time(self.duration)
        self.label.setText(time)

    def get_time(self, raw_time):
        seconds = raw_time
        minutes = int(raw_time // 60)
        if seconds >= 3600:
            hours = int(raw_time) // 3600
            minutes = int(raw_time // 60 - hours * 60)
            seconds = raw_time - hours * 3600 - minutes * 60
            time = f"{hours}:{minutes:02d}:{seconds:05.2f}"
        elif seconds >= 60:
            minutes = int(raw_time // 60)
            seconds = raw_time - minutes * 60
            time = f"{minutes:02d}:{seconds:05.2f}"
        else:
            time = f"{raw_time:05.2f}"
        return time

    def start_timer(self):
        self.time_left = self.duration # Reset time
        self.timer.start(10)  # Timer will tick every 1/100th of second

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 0.01
            self.time_left = round(self.time_left, 2)
            time = self.get_time(self.time_left)
            self.label.setText(time)
        else:
            self.timer.stop()
            self.label.setText('Time\'s up!')
            playsound("/home/demid/Documents/PetProjects/TimerApp/sound.mp3")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimerApp()
    window.show()
    with open("/home/demid/Documents/PetProjects/TimerApp/styles.css", "r") as f: 
        window.setStyleSheet(f.read())
    sys.exit(app.exec())