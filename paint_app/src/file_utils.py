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

SUPPORTED_EXPORT_FORMATS = {
    'PNG': {'extension': '.png', 'description': 'PNG Image'},
    'JPEG': {'extension': '.jpg', 'description': 'JPEG Image'},
    'BMP': {'extension': '.bmp', 'description': 'BMP Image'},
    'TIFF': {'extension': '.tiff', 'description': 'TIFF Image'},
    'PDF': {'extension': '.pdf', 'description': 'PDF Document'}
}

class ExportSettings:
    def __init__(self, format='PNG', dpi=300, quality=90, transparency=True):
        self.format = format
        self.dpi = dpi
        self.quality = quality
        self.transparency = transparency

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
    def export_canvas(paint_widget, filepath, settings):
        """Export canvas with specified settings"""
        try:
            # Get the image from the paint widget
            img = paint_widget.export_as_image()
            data = BytesIO()
            img.save(data, fmt='png')
            data.seek(0)
            
            # Open with PIL for advanced export options
            image = Image.open(data)
            
            # Prepare output filename with correct extension
            base_filename, _ = os.path.splitext(filepath)
            output_path = base_filename + SUPPORTED_EXPORT_FORMATS[settings.format]['extension']
            
            # Handle format-specific settings
            if settings.format == 'PNG':
                if not settings.transparency and image.mode == 'RGBA':
                    # Convert RGBA to RGB with white background
                    bg = Image.new('RGB', image.size, (255, 255, 255))
                    bg.paste(image, mask=image.split()[3])
                    image = bg
                image.save(output_path, 'PNG', 
                         dpi=(settings.dpi, settings.dpi),
                         optimize=True)
                
            elif settings.format == 'JPEG':
                # JPEG doesn't support transparency, always convert to RGB
                if image.mode == 'RGBA':
                    bg = Image.new('RGB', image.size, (255, 255, 255))
                    bg.paste(image, mask=image.split()[3])
                    image = bg
                image.save(output_path, 'JPEG', 
                         quality=settings.quality, 
                         dpi=(settings.dpi, settings.dpi),
                         optimize=True)
                
            elif settings.format == 'TIFF':
                image.save(output_path, 'TIFF', 
                         resolution=settings.dpi,
                         quality=settings.quality)
                
            elif settings.format == 'PDF':
                # Convert to RGB for PDF
                if image.mode == 'RGBA':
                    bg = Image.new('RGB', image.size, (255, 255, 255))
                    bg.paste(image, mask=image.split()[3])
                    image = bg
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                    
                # Calculate PDF dimensions (assuming 72 DPI is base PDF unit)
                width_in_inches = image.width / settings.dpi
                height_in_inches = image.height / settings.dpi
                width_in_points = width_in_inches * 72
                height_in_points = height_in_inches * 72
                
                # Save as PDF with correct dimensions
                image.save(output_path, 'PDF', 
                         resolution=settings.dpi,
                         width=width_in_points,
                         height=height_in_points)
                
            elif settings.format == 'BMP':
                # BMP doesn't support transparency
                if image.mode == 'RGBA':
                    bg = Image.new('RGB', image.size, (255, 255, 255))
                    bg.paste(image, mask=image.split()[3])
                    image = bg
                image.save(output_path, 'BMP')
            
            print(f"Successfully exported to {output_path}")
            print(f"Format: {settings.format}, DPI: {settings.dpi}, Quality: {settings.quality}")
            return True
            
        except Exception as e:
            print(f"Error exporting image: {e}")
            import traceback
            traceback.print_exc()
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