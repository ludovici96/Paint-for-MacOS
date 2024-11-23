# This file manages the loading and access of icon assets used throughout the application.
# It implements a singleton pattern for efficient icon resource management.

import os
from kivy.core.image import Image as CoreImage

class IconManager:
    _instance = None
    _icons = {}
    _base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if IconManager._instance is not None:
            raise RuntimeError("Use get_instance() instead")
        self._load_icons()
    
    def _load_icons(self):
        """Load all icon files from the assets directory."""
        icon_files = {
            'pencil': 'pencil.png',
            'brush': 'brush.png',
            'eraser': 'eraser.png',
            'line': 'line.png',
            'rectangle': 'rectangle.png',
            'circle': 'circle.png',
            'fill': 'fill.png'
        }
        
        for icon_name, filename in icon_files.items():
            file_path = os.path.join(self._base_path, filename)
            try:
                # Load the image and store its texture
                image = CoreImage(file_path)
                self._icons[icon_name] = image.texture
            except Exception as e:
                print(f"Error loading icon {filename}: {e}")
    
    def get_icon(self, name):
        """Get the texture for the specified icon name."""
        if name not in self._icons:
            print(f"Warning: Icon '{name}' not found")
            return None
        return self._icons[name]
    
    def get_icon_path(self, name):
        """Get the full path for the specified icon name."""
        if name not in self._icons:
            print(f"Warning: Icon '{name}' not found")
            return None
        return os.path.join(self._base_path, f"{name}.png")
