# This is the main application file that initializes the Paint application.
# It sets up the window, manages global state, and coordinates between different components.
import os
import sys
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from paint_widget import PaintWidget
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from tools import Tool
from tools import BrushStyle
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle
from theme_manager import ThemeManager
from font_manager import FontManager
from toolbar import MenuBar, ToolButton  # Update this line to import ToolButton
from icon_manager import IconManager

# Initialize font before creating any widgets
FontManager.initialize()

# Set window size
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

class PaintApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brush_styles = BrushStyle
        ThemeManager.initialize()
        FontManager.initialize()  # Initialize font manager
        self.theme_is_dark = Window.is_dark_theme  # Store theme state
        self.icon_manager = IconManager.get_instance()

    @property
    def is_dark_theme(self):
        return Window.is_dark_theme

    def build(self):
        self.color_popup = None  # Store popup reference
        # Bind keyboard
        Window.bind(on_keyboard=self._on_keyboard)  # Use keyword argument
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to the .kv file
        kv_path = os.path.join(os.path.dirname(current_dir), 'resources', 'paint.kv')
        root = Builder.load_file(kv_path)
        # Add the modular menu bar
        root.ids.toolbar.add_widget(MenuBar(self), 0)  # Use the imported MenuBar
        return root
    
    def select_tool(self, tool_name):
        try:
            tool = Tool[tool_name]
            self.root.ids.paint_widget.set_tool(tool)
            
            # Deactivate all tool buttons in quick_toolbar
            for child in self.root.ids.quick_toolbar.walk(restrict=True):
                if isinstance(child, ToolButton):
                    child.active = (child.tool == tool_name)
                    
        except KeyError:
            print(f"Invalid tool: {tool_name}")

    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        paint_widget = self.root.ids.paint_widget
        
        # Command + Z (undo)
        if codepoint == 'z' and modifier == ['meta']:
            paint_widget.undo()
            return True
            
        # Command + Shift + Z (redo)
        if codepoint == 'z' and set(modifier) == {'meta', 'shift'}:
            paint_widget.redo()
            return True
        
        return False

    def show_color_picker(self):
        content = BoxLayout(orientation='vertical')
        color_picker = ColorPicker()
        content.add_widget(color_picker)
        
        # Set initial color to current color
        color_picker.color = self.root.ids.paint_widget.current_color

        confirm_button = Button(
            text='Select Color',
            size_hint_y=None,
            height='48dp'
        )
        content.add_widget(confirm_button)
        
        self.color_popup = Popup(
            title='Choose Color',
            content=content,
            size_hint=(0.8, 0.9)
        )
        
        def on_color_select(instance):
            self.root.ids.paint_widget.set_color(color_picker.color)
            self.color_popup.dismiss()
            
        confirm_button.bind(on_release=on_color_select)
        self.color_popup.open()

    def get_icon_path(self, name):
        return self.icon_manager.get_icon_path(name)
        
    def on_start(self):
        # Ensure icons are loaded when the app starts
        self.icon_manager = IconManager.get_instance()


if __name__ == '__main__':
    PaintApp().run()
