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
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.core.text import LabelBase
from kivy.animation import Animation

# Initialize font before creating any widgets
FontManager.initialize()

# Set window size
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

# Register Helvetica font
def register_fonts():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(os.path.dirname(current_dir), 'resources', 'helvetica.ttf')
    LabelBase.register(name='Helvetica', fn_regular=font_path)

class HoverButton(Button):
    default_bg = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        Window.bind(mouse_pos=self.on_mouse_pos)
        
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            # Mouse is over the button
            if not hasattr(self, '_hover_anim'):
                hover_color = [min(1.0, c * 1.2) for c in self.default_bg]
                self._hover_anim = Animation(background_color=hover_color, duration=0.2)
                self._hover_anim.start(self)
        else:
            # Mouse is not over the button
            if hasattr(self, '_hover_anim'):
                self._hover_anim.stop(self)
                Animation(background_color=self.default_bg, duration=0.2).start(self)
                del self._hover_anim

class SaveDialog(ModalView):
    _kv_loaded = False  # Class variable to track if KV file has been loaded
    on_save = ObjectProperty(None)
    on_dont_save = ObjectProperty(None)
    on_cancel = ObjectProperty(None)
    warning_icon = StringProperty('')
    
    def __init__(self, **kwargs):
        # Set initial opacity to 0 for fade-in
        kwargs['opacity'] = 0
        # Load KV file only once for the class
        if not SaveDialog._kv_loaded:
            Builder.load_file(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'resources', 'save_dialog.kv'
            ))
            SaveDialog._kv_loaded = True
            
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = ('400dp', '130dp')
        self.background_color = (0.95, 0.95, 0.95, 0.98) if not Window.is_dark_theme else (0.2, 0.2, 0.2, 0.98)
        self.warning_icon = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'assets', 'images', 'warning.png'
        )
        
        # Add fade-in animation when dialog opens
        self.bind(on_pre_open=self._start_open_animation)
        
    def _start_open_animation(self, *args):
        # Create and start fade-in animation
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self)
        
    def dismiss(self, *args, **kwargs):
        # Create fade-out animation
        def after_fade(dialog):
            super(SaveDialog, dialog).dismiss()
            
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=lambda *x: after_fade(self))
        anim.start(self)

class PaintApp(App):
    def __init__(self, **kwargs):
        register_fonts()
        super().__init__(**kwargs)
        self.brush_styles = BrushStyle
        ThemeManager.initialize()
        # Remove duplicate font initialization since it's done before class
        self.theme_is_dark = Window.is_dark_theme
        self.icon_manager = IconManager.get_instance()
        # Initialize color_popup here instead of in build
        self.color_popup = None

    def build(self):
        # Bind keyboard before loading UI
        Window.bind(on_keyboard=self._on_keyboard)
        
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to the .kv file
        kv_path = os.path.join(os.path.dirname(current_dir), 'resources', 'paint.kv')
        
        try:
            # Load the kv file with error handling
            root = Builder.load_file(kv_path)
            if not root:
                raise Exception("Failed to load KV file")
                
            # Add the menu bar
            menu_bar = MenuBar(self)
            root.ids.toolbar.add_widget(menu_bar, 0)
            return root
            
        except Exception as e:
            print(f"Error loading application: {e}")
            return None

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
        
        # Command + N (new canvas)
        if codepoint == 'n' and modifier == ['meta']:
            self.new_canvas()
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

    def create_unsaved_changes_dialog(self, on_save, on_dont_save, on_cancel):
        """Create and return a styled save changes dialog"""
        dialog = SaveDialog()
        # Bind the callbacks
        dialog.on_save = on_save
        dialog.on_dont_save = on_dont_save
        dialog.on_cancel = lambda: self.handle_dialog_action(dialog, on_cancel)
        return dialog
    
    def handle_dialog_action(self, modal, callback):
        """Handle dialog button actions"""
        modal.dismiss()
        if callback:
            callback()
    
    def new_canvas(self, *args):
        """Handle new canvas creation with save check"""
        paint_widget = self.root.ids.paint_widget
        
        def create_new():
            paint_widget.clear_canvas()
        
        def save_then_new():
            # TODO: Implement save functionality
            print("Save functionality not implemented yet")
            create_new()
            
        def do_nothing():
            pass
        
        if paint_widget.has_unsaved_changes():
            dialog = self.create_unsaved_changes_dialog(
                on_save=lambda: self.handle_dialog_action(dialog, save_then_new),
                on_dont_save=lambda: self.handle_dialog_action(dialog, create_new),
                on_cancel=do_nothing
            )
            dialog.open()
        else:
            create_new()
    
    def get_application_path(self):
        """Return the path to the application root directory"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        PaintApp().run()
    except Exception as e:
        print(f"Application failed to start: {e}")
