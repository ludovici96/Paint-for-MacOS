import os
from pathlib import Path
from kivy.core.image import Image as CoreImage
from PIL import Image
from io import BytesIO

DEFAULT_SAVE_DIR = os.path.expanduser("~/Pictures")
SUPPORTED_FORMATS = {
    'PNG Files': ['*.png'],
    'JPEG Files': ['*.jpg', '*.jpeg'],
    'BMP Files': ['*.bmp'],  # Added BMP support
}

class FileManager:
    _last_directory = DEFAULT_SAVE_DIR

    @classmethod
    def get_last_directory(cls):
        if not os.path.exists(cls._last_directory):
            cls._last_directory = DEFAULT_SAVE_DIR
        return cls._last_directory

    @classmethod
    def set_last_directory(cls, directory):
        if os.path.exists(directory):
            cls._last_directory = directory

    @classmethod
    def get_save_directory(cls):
        if not os.path.exists(cls._last_directory):
            cls._last_directory = DEFAULT_SAVE_DIR
        return cls._last_directory

    @classmethod
    def set_save_directory(cls, directory):
        if os.path.exists(directory):
            cls._last_directory = directory

    @staticmethod
    def save_canvas_as_image(paint_widget, filepath, file_format='PNG', jpeg_quality=90):
        try:
            print(f"Attempting to save image to: {filepath}")
            
            # Get the image from the paint widget
            img = paint_widget.export_as_image()
            data = BytesIO()
            img.save(data, fmt='png')
            data.seek(0)
            
            # Open the image with PIL
            image = Image.open(data)
            
            # Save the image in the desired format
            if file_format.upper() == 'PNG':
                image.save(filepath, 'PNG')
            else:
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3])  # Remove transparency
                    image = background
                image.save(filepath, 'JPEG', quality=jpeg_quality)
            print("Save successful")
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    @staticmethod
    def estimate_file_size(canvas, format='PNG'):
        """Estimate file size before saving"""
        buffer = BytesIO()
        texture = canvas.export_as_image().texture
        
        # Convert to PIL Image (similar to save process)
        pixels = texture.pixels
        size = (texture.width, texture.height)
        mode = 'RGBA' if texture.colorfmt == 'rgba' else 'RGB'
        image = Image.frombytes(mode, size, pixels)
        
        # Save to buffer to estimate size
        if format.upper() == 'PNG':
            image.save(buffer, format='PNG')
        else:
            if image.mode == 'RGBA':
                background = Image.new('RGB', size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            image.save(buffer, format='JPEG', quality=90)
            
        return len(buffer.getvalue()) / 1024  # Size in KB