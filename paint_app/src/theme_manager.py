# This file manages the application's theme system, detecting and handling system dark/light
# mode changes for macOS integration.
from kivy.core.window import Window
from kivy.clock import Clock
import platform
import subprocess

class ThemeManager:
    @staticmethod
    def is_dark_theme():
        if platform.system() != 'Darwin':
            return False
            
        try:
            cmd = 'defaults read -g AppleInterfaceStyle'
            subprocess.check_output(cmd.split())
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def initialize():
        def check_theme(dt):
            Window.is_dark_theme = ThemeManager.is_dark_theme()
        
        # Check initially and every 5 seconds for theme changes
        Window.is_dark_theme = ThemeManager.is_dark_theme()
        Clock.schedule_interval(check_theme, 5)