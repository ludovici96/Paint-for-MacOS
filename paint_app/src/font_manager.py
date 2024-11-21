import platform
from kivy.core.text import LabelBase
import os

class FontManager:
    @staticmethod
    def initialize():
        # Get the path to the resources directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resources_dir = os.path.join(current_dir, 'resources')
        
        # Register Helvetica font from resources
        helvetica_path = os.path.join(resources_dir, 'helvetica.ttf')
        if os.path.exists(helvetica_path):
            LabelBase.register(
                'Helvetica',
                helvetica_path
            )
            return True
                
        return False

    @staticmethod
    def get_system_font():
        if platform.system() == 'Darwin':
            return 'Helvetica' if FontManager.initialize() else 'Roboto'
        return 'Roboto'