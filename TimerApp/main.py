import sys
import sqlite3
import simpleaudio as sa
from pathlib import Path
from PyQt6.QtWidgets import (QApplication,
                             QMainWindow,
                             QDialog,
                             QFileDialog,
                             QLabel,
                             QPushButton,
                             QCheckBox,
                             QDoubleSpinBox,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QSizePolicy,
                             QWidget)
from PyQt6.QtCore import QTimer, Qt
from multislider import MultiSlider

# Specifying base directory, path to database and path to sounds directory.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "timer_app.db"
SOUNDS_PATH = BASE_DIR / "sounds"

def initialize_db():
    """Initialize database. Create (if non-existent) tables: settings, profiles.
    """
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    timer_duration REAL,
                    reset_timer_on_save BOOLEAN,
                    enable_sound BOOLEAN,
                    final_sound_filename TEXT,
                    intermediate_sound_filename TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    settings_id INTEGER,
                    FOREIGN KEY (settings_id) REFERENCES settings (id)
        )              
    """)
    con.commit()
    con.close()

def get_default_settings():
    """Get default settings in dictonary format identical to what's used throughout the program.
    
    Returns: settings (dict)"""
    settings = {
        "timer_duration" : 10.0,
        "reset_timer_on_save" : False,
        "enable_sound" : True,
        "final_sound_filename" : str(SOUNDS_PATH / "bell.wav"),
        "intermediate_sound_filename" : str(SOUNDS_PATH / "beep.wav")
    }
    return settings

class SettingsWindow(QDialog):
    """QDialog window that contains various settings of TimerApp.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.settings = self.parent().settings
        self.initUI()
        self.set_layouts()
        self.configure_widgets()

    def initUI(self):
        """ Initialize UI of SettingsWindow.
        """
        self.setWindowTitle('Settings | Timer Application')
        # Create control widgets and corresponding labels
        self.duration_label = QLabel('&Timer duration', self)
        self.duration_spinbox = QDoubleSpinBox(self)
        self.intermediate_multislider_label = QLabel('Add and remove bells', self)
        self.intermediate_multislider = MultiSlider()
        self.toggle_reset_on_save_label = QLabel('&Reset running timer on save', self)
        self.toggle_reset_on_save_checkbox = QCheckBox(self)
        self.toggle_sound_label = QLabel('&Play sound', self)
        self.toggle_sound_checkbox = QCheckBox(self)
        self.final_sound_label = QLabel('&Final sound', self)
        self.intermediate_sound_label = QLabel('&Intermediate sound', self)
        self.final_sound_button = QPushButton('Select file', self)
        self.intermediate_sound_button = QPushButton('Select file', self)
        self.reset_button = QPushButton('&Reset settings', self)
        self.save_settings_button = QPushButton('&Save settings', self)
        # Set buddies for labels and controls widgets
        self.toggle_reset_on_save_label.setBuddy(self.toggle_reset_on_save_checkbox)
        self.toggle_sound_label.setBuddy(self.toggle_sound_checkbox)
        self.duration_label.setBuddy(self.duration_spinbox)
        self.final_sound_label.setBuddy(self.final_sound_button)
        self.intermediate_sound_label.setBuddy(self.intermediate_sound_button)
        # Set stylesheet for window
        self.setStyleSheet("""
            QDialog {
                background-color: violet;
                color: white;       
            }
            QLabel {
                font-size: 11pt;
            }
            QPushButton {
                font-size: 11pt;
            }
        """)

    def set_layouts(self):
        """Add widgets to layouts.
        """
        # top group of widgets 
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(self.duration_label)
        duration_layout.addStretch()
        duration_layout.addWidget(self.duration_spinbox)
        reset_on_save_layout = QHBoxLayout()
        reset_on_save_layout.addWidget(self.toggle_reset_on_save_label)
        reset_on_save_layout.addStretch()
        reset_on_save_layout.addWidget(self.toggle_reset_on_save_checkbox)
        multislider_layout = QHBoxLayout()
        multislider_layout.addWidget(self.intermediate_multislider_label)
        multislider_layout.addStretch()
        multislider_layout.addWidget(self.intermediate_multislider)
        # add top group of layouts to top layout
        timer_configuration_layout = QVBoxLayout()
        timer_configuration_layout.addLayout(duration_layout)
        timer_configuration_layout.addLayout(reset_on_save_layout)
        timer_configuration_layout.addLayout(multislider_layout)
        # middle group of widgets
        play_sound_layout = QHBoxLayout()
        play_sound_layout.addWidget(self.toggle_sound_label)
        play_sound_layout.addStretch()
        play_sound_layout.addWidget(self.toggle_sound_checkbox)
        final_file_layout = QHBoxLayout()
        final_file_layout.addWidget(self.final_sound_label)
        final_file_layout.addStretch()
        final_file_layout.addWidget(self.final_sound_button)
        intermediate_file_layout = QHBoxLayout()
        intermediate_file_layout.addWidget(self.intermediate_sound_label)
        intermediate_file_layout.addStretch()
        intermediate_file_layout.addWidget(self.intermediate_sound_button)
        # add middle group of widgets to middle layout
        sound_layout = QVBoxLayout()
        sound_layout.addLayout(play_sound_layout)
        sound_layout.addLayout(final_file_layout)
        sound_layout.addLayout(intermediate_file_layout)
        # bottom layout
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addWidget(self.reset_button)
        bottom_buttons_layout.addStretch()
        bottom_buttons_layout.addWidget(self.save_settings_button)
        # combine all groups of layouts into main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(timer_configuration_layout)
        main_layout.addStretch()
        main_layout.addLayout(sound_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_buttons_layout)
        self.setLayout(main_layout)

    def configure_widgets(self):
        """Set defaults and connect with slots widgets that control settings.
        """
        # Configure timer duration spinbox
        self.duration_spinbox.setMinimum(0)
        self.duration_spinbox.setMaximum(1e5)
        self.duration_spinbox.setDecimals(0)
        self.duration_spinbox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.duration_spinbox.valueChanged.connect(self.set_duration)
        # Configure multislider
        self.intermediate_multislider.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        # Configure toggle reset on save checkbox
        self.toggle_reset_on_save_checkbox.stateChanged.connect(self.set_reset_on_save)
        # Configure toggle sound checkbox
        self.toggle_sound_checkbox.stateChanged.connect(self.set_sound_enabled)
        # Connect select final sound file button
        self.final_sound_button.pressed.connect(self.final_open_file_dialog)
        # Connect select intermediate sound file button
        self.intermediate_sound_button.pressed.connect(self.intermediate_open_file_dialog)
        # Connect reset settings button
        self.reset_button.pressed.connect(self.reset_settings)
        # Connect save settings button
        self.save_settings_button.pressed.connect(self.pass_settings_and_exit)
        # Set widgets according to settings
        self.load_from_settings()

    def load_from_settings(self):
        """Set widgets' values and states to what's specified in settings.
        """
        self.duration_spinbox.setValue(self.settings["timer_duration"])
        self.toggle_reset_on_save_checkbox.setChecked(self.settings["reset_timer_on_save"])
        self.toggle_sound_checkbox.setChecked(self.settings["enable_sound"])
  
    def set_duration(self, value):
        """Set duration in settings dictionary.

        Args:
            value (float): value of doubleSpinbox.
        """
        self.settings["timer_duration"] = round(value, 2)

    def set_reset_on_save(self):
        """Set behaviour of timer on saving the settings.
        """
        self.settings["reset_timer_on_save"] = self.toggle_reset_on_save_checkbox.isChecked()

    def set_sound_enabled(self):
        """Set enable sounds.
        """
        self.settings["enable_sound"] = self.toggle_sound_checkbox.isChecked()

    def final_open_file_dialog(self):
        """Open file dialog to pick a .wav file for final sound signal.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Final sound for Timer | Timer Application", "", "WAV files (*.wav)")
        if file_name:
            print(f"Selected Final soundfile: {file_name}")
            self.settings["final_sound_filename"] = file_name

    def intermediate_open_file_dialog(self):
        """Open file dialog to pick a .wav file for intermediate sound signal.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Intermediate sound for Timer | Timer Application", "", "WAV files (*.wav)")
        if file_name:
            print(f"Selected Intermediate soundfile: {file_name}")
            self.settings["intermediate_sound_filename"] = file_name

    def reset_settings(self):
        """Reset settings to what is return in get_default_settings(), then update widgets.
        """
        self.settings = get_default_settings()
        self.load_from_settings()

    def pass_settings_and_exit(self):
        """Pass settings from settings window to main window. Then close the settings window.
        This method is created following the logic that all settings are passed in main window at the same time.
        I don't know if this is a proper way.
        """
        self.parent().save_settings(self.settings)
        self.close()

class TimerApp(QMainWindow):
    """Main window for app based on QMainWindow.
    """
    def __init__(self):
        super().__init__()
        self.settings = get_default_settings()
        self.settings_window = None
        initialize_db()
        self.load_settings_from_db()
        self.initUI()
        self.configure_widgets()
        self.load_sounds()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

       
    def initUI(self):
        """ Initialize UI of main window.
        """
        self.setWindowTitle('Timer Application')
        # Create timer label and pushbuttons
        self.timer_label = QLabel('TimerApp', self)
        self.settings_button = QPushButton('&Settings', self)
        self.start_button = QPushButton('Start', self)
        self.reset_button = QPushButton('&Reset', self)
        # Create and configure layouts
        layoutMain = QVBoxLayout()
        layoutMain.addWidget(self.timer_label)
        layoutButtons = QHBoxLayout()
        layoutButtons.addWidget(self.settings_button)
        layoutButtons.addWidget(self.start_button)
        layoutButtons.addWidget(self.reset_button)
        layoutMain.addLayout(layoutButtons)
        # Add the container widget as central widget to set main layout
        container = QWidget()
        container.setLayout(layoutMain)
        self.setCentralWidget(container)

    def configure_widgets(self):
        # Configure timer label
        self.timer_label.setText(self.get_time((self.settings["timer_duration"])))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        # Connect buttons to slots
        self.settings_button.clicked.connect(self.open_settings)
        self.start_button.clicked.connect(self.start_timer)
        self.start_button.setShortcut('Space')
        self.reset_button.clicked.connect(self.reset_timer)

    def save_settings_to_db(self, db_path=DB_PATH):
        """Save settings to database.
        
        Args:
            db_path (str or pathlib.Path): path to database file.
        """
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO settings (timer_duration,
                                  reset_timer_on_save,
                                  enable_sound,
                                  final_sound_filename,
                                  intermediate_sound_filename)
            VALUES (?, ?, ?, ?, ?)
        """, (self.settings["timer_duration"],
              self.settings["reset_timer_on_save"],
              self.settings["enable_sound"],
              self.settings["final_sound_filename"],
              self.settings["intermediate_sound_filename"]))
        print("Executed save settings query.")
        con.commit()
        print("Commited save settings to DB.")
        cursor.execute("""

        """)
        con.close()

    def load_settings_from_db(self, db_path=DB_PATH):
        """Load settings from database or set to defaults if no user settings loaded.
        
        Args:
            db_path (str or pathlib.Path): path to database file.
        """
        print("Trying to load settings...")
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        # Get the latest settings configuration
        cursor.execute("""
            SELECT *
              FROM settings
             ORDER BY id DESC
             LIMIT 1
            """)
        print("Executed load settings query.")
        row = cursor.fetchone()
        con.close()
        default_settings = get_default_settings()
        # If got settings then save it into class member, else stay with defaults
        if row:
            print(f"Found user settings.")
            self.settings = {
                "timer_duration" : row[1],
                "reset_timer_on_save" : bool(row[2]),
                "enable_sound" : bool(row[3]),
                "final_sound_filename" : row[4],
                "intermediate_sound_filename" : row[5]
            }
        else:
            print(f"User settings not found, using defaults.")
            self.settings = default_settings
        # Merge with default settings (loaded settings will overwrite defaults, if present)
        self.settings = {**default_settings, **self.settings}
        print(f"Loaded settings: {self.settings}")

    def load_sounds(self):
        """Load sounds from paths specified in settings.

        Args:
            final: sound which is played then timer ends;
            intermediate: sound which is played for intermediate bells.
        """
      
        try:
            self.wave_final = sa.WaveObject.from_wave_file(self.settings["final_sound_filename"])
            self.wave_intermediate = sa.WaveObject.from_wave_file(self.settings["intermediate_sound_filename"])
        except Exception as e:
            print(f'Error while loading sounds: {e}')
        print("Loaded sounds.")

    def start_timer(self):
        """Reset timer to its full duration and start timer.
        """
        self.time_left = self.settings["timer_duration"] # Reset time
        self.timer.start(10)  # Timer will tick every 1/100th of second

    def update_timer(self):
        """Manage timer by subtracting timer timeout interval from time_left at every timeout.
        If no time left, stop timer, update UI [and play sound].
        """
        # Continuously update timer until time_left > 0
        if self.time_left > 0:
            # Subtract timer step from time_left (at the moment it is 1/100th of second hardcoded)
            self.time_left -= 0.01
            self.time_left = round(self.time_left, 2)
            time_str = self.get_time(self.time_left)
            self.timer_label.setText(time_str)
        else:
            self.timer.stop()
            self.time_left = self.settings["timer_duration"]
            self.timer_label.setText('Time\'s up!')
            if self.settings["enable_sound"] == True:
                play_final = self.wave_final.play()

    def reconfigure_timer(self, duration):
        self.time_left = self.settings["timer_duration"]
        time_str = self.get_time(self.settings["timer_duration"])
        self.timer_label.setText(time_str)

    def reset_timer(self):
        """Stop timer and set timer label text to original duration.
        """
        print("Reset timer.")
        self.timer.stop()
        time_str = self.get_time(self.settings["timer_duration"])
        self.timer_label.setText(time_str)

    def get_time(self, raw_time):
        """Convert time from seconds to HH:MM:SS.SS format.
        
        Args:
            raw_time (int): time in seconds.
        Returns:
            time_str (str): formatted time string.
        """
        seconds = raw_time
        minutes = int(raw_time // 60)
        if seconds >= 3600:
            hours = int(raw_time) // 3600
            minutes = int(raw_time // 60 - hours * 60)
            seconds = raw_time - hours * 3600 - minutes * 60
            time_str = f"{hours}:{minutes:02d}:{seconds:05.2f}"
        elif seconds >= 60:
            minutes = int(raw_time // 60)
            seconds = raw_time - minutes * 60
            time_str = f"{minutes:02d}:{seconds:05.2f}"
        else:
            time_str = f"{raw_time:05.2f}"
        return time_str

    
    def open_settings(self):
        print("Opened settings.")
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.settings = self.settings
            self.settings_window.load_from_settings()
        self.settings_window.exec()

    def save_settings(self, settings):
        """Save all settings passed from settings window in main window.
        
        Args:
            settings (dict): settings dictionary   {"timer_duration": int,
                                                    "reset_on_save: bool,
                                                    "enable_sound": bool,
                                                    "final_sound_filename": str,
                                                    "intermediate_sound_filename": str}
        """
        self.settings = settings
        self.load_sounds()
        if settings["reset_timer_on_save"] == True:
            self.reset_timer()
        self.save_settings_to_db()

if __name__ == '__main__':
    print("TimerApp by D. Sergeev.")
    app = QApplication(sys.argv)
    window = TimerApp()
    window.show()
    with open(BASE_DIR / "styles.css", "r") as f: 
        window.setStyleSheet(f.read())
    sys.exit(app.exec())