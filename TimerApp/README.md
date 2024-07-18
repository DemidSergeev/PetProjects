# TimerApp

TimerApp is a Python application built using PyQt6 and SQLite, designed to provide a customizable timer experience with sound notifications.

## Features

- **Customizable Timer Settings**: Adjust timer duration, enable sound notifications, and select sound files for intermediate and final alerts.
- **Persistent Settings**: Save and load timer settings from an SQLite database.
- **Simple and Flexible**: Intuitive UI with settings dialog for easy configuration.
- **Sound Notifications**: Play selected WAV files upon timer completion and for intermediate notifications.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DemidSergeev/PetProjects/new/master/TimerApp.git
   cd TimerApp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python timer_app.py
   ```

## Usage

- **Setting Configuration**: Click on the "Settings" button to configure timer duration, sound preferences, and sound files.
- **Starting the Timer**: Press the "Start" button or use the spacebar shortcut to begin the timer countdown.
- **Resetting the Timer**: Use the "Reset" button to stop and reset the timer to its original duration.
