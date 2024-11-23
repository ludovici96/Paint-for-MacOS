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
from kivy.uix.filechooser import FileChooserListView
from file_utils import FileManager, SUPPORTED_FORMATS
from kivy.uix.progressbar import ProgressBar
import threading
import os
from kivy.clock import Clock  # Add this import at the top
from Foundation import NSURL
from AppKit import NSSavePanel, NSView, NSMakeRect, NSTextField, NSPopUpButton, NSColor, NSModalResponseOK
from Foundation import NSOpenPanel  # Ensure NSOpenPanel is imported
from file_utils import SUPPORTED_EXPORT_FORMATS, ExportSettings
from AppKit import NSMenuItem, NSPopUpButton, NSSlider, NSButton, NSOnState, NSOffState
from Foundation import NSObject
import objc

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

# Define the SliderHandler class
class SliderHandler(NSObject):
    def init(self):
        self = objc.super(SliderHandler, self).init()
        if self is None: return None
        self.dpi_value = None
        self.quality_value = None
        return self

    def setupWithDpiValue_qualityValue_(self, dpi_value, quality_value):
        """Objective-C method for setting up values"""
        self.dpi_value = dpi_value
        self.quality_value = quality_value
        return self

    def sliderChanged_(self, sender):
        """Objective-C method to handle slider changes"""
        try:
            tag = sender.tag()
            value = str(int(sender.intValue()))
            if tag == 1:  # DPI slider
                self.dpi_value.setStringValue_(value)
            elif tag == 2:  # Quality slider
                self.quality_value.setStringValue_(value)
        except Exception as e:
            print(f"Error in slider change: {e}")

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
        self.slider_handler = SliderHandler.alloc().init()  # Retain handler instance

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
        
        # Command + S (save)
        if codepoint == 's' and modifier == ['meta']:
            self.save_canvas()
            return True

        # Command + O (open)
        if codepoint == 'o' and modifier == ['meta']:
            self.open_image()
            return True
        
        return False

    def get_icon_path(self, name):
        return self.icon_manager.get_icon_path(name)
    
    def save_canvas(self, callback=None, *args):
        """Handle save operation using native macOS save dialog with format selection"""
        try:
            # Create save panel
            save_panel = NSSavePanel.alloc().init()
            save_panel.setTitle_("Save Image")
            save_panel.setNameFieldStringValue_("Untitled")  # Remove .png extension
            save_panel.setAllowedFileTypes_(["png", "jpg", "jpeg"])  # Allowed formats
            save_panel.setAllowsOtherFileTypes_(False)  # Restrict to allowed types
            save_panel.setExtensionHidden_(True)  # Show the file extension field

            # Create accessory view with format selection
            accessory_view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 200, 50))

            # Create label for the format selection
            format_label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 15, 60, 25))
            format_label.setStringValue_("Format:")
            format_label.setEditable_(False)
            format_label.setBezeled_(False)
            format_label.setDrawsBackground_(False)
            format_label.setBordered_(False)
            format_label.setBackgroundColor_(NSColor.clearColor())

            # Create pop-up button for format selection
            format_pop_up = NSPopUpButton.alloc().initWithFrame_(NSMakeRect(65, 15, 120, 25))
            format_pop_up.addItemsWithTitles_(["PNG", "JPEG"])
            format_pop_up.selectItemWithTitle_("PNG")  # Set default selection

            # Add label and pop-up button to the accessory view
            accessory_view.addSubview_(format_label)
            accessory_view.addSubview_(format_pop_up)

            # Set accessory view to the save panel
            save_panel.setAccessoryView_(accessory_view)

            # Set initial directory to Pictures folder
            initial_path = os.path.expanduser("~/Pictures")
            url = NSURL.fileURLWithPath_(initial_path)
            save_panel.setDirectoryURL_(url)

            # Run the save panel modal
            response = save_panel.runModal()

            if response == NSModalResponseOK:
                filename = save_panel.URL().path()

                # Get selected format from the pop-up button
                selected_format = format_pop_up.titleOfSelectedItem()

                # Set the appropriate extension
                if selected_format == "PNG":
                    extension = ".png"
                elif selected_format == "JPEG":
                    extension = ".jpg"

                # Replace existing extension with the selected one
                filename, ext = os.path.splitext(filename)
                filename += extension

                # Show progress dialog
                progress = ModalView(size_hint=(0.4, 0.2))
                progress_bar = ProgressBar(max=100, value=0)
                progress.add_widget(progress_bar)
                progress.open()

                # Save the file on the main thread
                def save_on_main_thread(dt):
                    try:
                        file_format = selected_format
                        progress_bar.value = 50

                        # Save the file
                        success = FileManager.save_canvas_as_image(
                            self.root.ids.paint_widget,
                            filename,
                            file_format=file_format
                        )
                        progress_bar.value = 100
                        self._finish_save(progress, success, filename)
                        if success and callback:
                            callback()
                        elif not success:
                            self.show_error("Failed to save file")
                    except Exception as e:
                        self._handle_save_error(progress, str(e))

                # Schedule the save operation on the main thread
                Clock.schedule_once(save_on_main_thread, 0)

            else:
                # User canceled the save dialog
                if callback:
                    callback()

        except Exception as e:
            self.show_error(f"Error in save dialog: {str(e)}")
            if callback:
                callback()

    def _finish_save(self, progress, success, filename):
        """Handle completion of save operation"""
        progress.dismiss()
        if success:
            self.root.ids.paint_widget.clear_unsaved_changes()
            self.title = f"Paint - {os.path.basename(filename)}"
        else:
            self.show_error("Failed to save file")

    def _handle_save_error(self, progress, error_message):
        """Handle save operation error"""
        progress.dismiss()
        self.show_error(f"Error while saving: {error_message}")

    def show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        button = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(button)
        
        popup = Popup(title='Error', content=content,
                     size_hint=(0.4, 0.3))
        button.bind(on_release=popup.dismiss)
        popup.open()

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
            self.save_canvas(callback=create_new)
            
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

    def open_image(self, *args):
        """Handle opening an image and loading it onto the canvas."""
        try:
            # Create open panel
            open_panel = NSOpenPanel.alloc().init()
            open_panel.setTitle_("Open Image")
            open_panel.setAllowedFileTypes_(["png", "jpg", "jpeg", "bmp"])
            open_panel.setAllowsMultipleSelection_(False)
            # Remember last directory
            initial_dir = FileManager.get_last_directory()
            open_panel.setDirectoryURL_(NSURL.fileURLWithPath_(initial_dir))

            # Run the open panel modal
            response = open_panel.runModal()

            if response == NSModalResponseOK:
                filename = open_panel.URLs()[0].path()
                print(f"Selected file: {filename}")  # Add this line for debugging
                # Update last directory
                FileManager.set_last_directory(os.path.dirname(filename))
                # Load the image onto the canvas
                success = self.root.ids.paint_widget.load_image(filename)
                if success:
                    # Clear undo/redo stacks
                    self.root.ids.paint_widget.clear_undo_history()
                    # Update window title
                    self.title = f"Paint - {os.path.basename(filename)}"
                else:
                    self.show_error("Failed to open image.")
        except Exception as e:
            self.show_error(f"Error opening image: {str(e)}")

    def export_image(self, *args):
        """Handle image export with advanced options"""
        try:
            # Create save panel
            save_panel = NSSavePanel.alloc().init()
            save_panel.setTitle_("Export Image")
            save_panel.setNameFieldStringValue_("Untitled")
            
            # Create accessory view with more vertical space for controls
            accessory_view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 150))
            
            # Format selection (near top)
            format_label = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 120, 60, 25))
            format_label.setStringValue_("Format:")
            format_label.setEditable_(False)
            format_label.setBezeled_(False)
            format_label.setDrawsBackground_(False)
            
            format_popup = NSPopUpButton.alloc().initWithFrame_(NSMakeRect(80, 120, 200, 25))
            formats = list(SUPPORTED_EXPORT_FORMATS.keys())
            format_popup.addItemsWithTitles_(formats)
            
            # DPI selection with value display
            dpi_label = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 90, 60, 25))
            dpi_label.setStringValue_("DPI:")
            dpi_label.setEditable_(False)
            dpi_label.setBezeled_(False)
            dpi_label.setDrawsBackground_(False)
            
            dpi_value = NSTextField.alloc().initWithFrame_(NSMakeRect(250, 90, 40, 25))
            dpi_value.setStringValue_("300")
            dpi_value.setEditable_(False)
            dpi_value.setBezeled_(False)
            dpi_value.setDrawsBackground_(False)
            
            dpi_slider = NSSlider.alloc().initWithFrame_(NSMakeRect(80, 90, 160, 25))
            dpi_slider.setMinValue_(72)
            dpi_slider.setMaxValue_(600)
            dpi_slider.setIntValue_(300)
            
            # Quality selection with value display
            quality_label = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 60, 60, 25))
            quality_label.setStringValue_("Quality:")
            quality_label.setEditable_(False)
            quality_label.setBezeled_(False)
            quality_label.setDrawsBackground_(False)
            
            quality_value = NSTextField.alloc().initWithFrame_(NSMakeRect(250, 60, 40, 25))
            quality_value.setStringValue_("90")
            quality_value.setEditable_(False)
            quality_value.setBezeled_(False)
            quality_value.setDrawsBackground_(False)
            
            quality_slider = NSSlider.alloc().initWithFrame_(NSMakeRect(80, 60, 160, 25))
            quality_slider.setMinValue_(1)
            quality_slider.setMaxValue_(100)
            quality_slider.setIntValue_(90)
            
            # Transparency checkbox
            transparency_check = NSButton.alloc().initWithFrame_(NSMakeRect(10, 30, 200, 25))
            transparency_check.setTitle_("Preserve Transparency")
            transparency_check.setButtonType_(1)
            transparency_check.setState_(NSOnState)
            
            # Assign dpi_value and quality_value to handler
            self.slider_handler.setupWithDpiValue_qualityValue_(dpi_value, quality_value)
            
            # Tag the sliders to identify them
            dpi_slider.setTag_(1)
            quality_slider.setTag_(2)
            
            # Set up the action for both sliders
            action = objc.selector(self.slider_handler.sliderChanged_,
                                 signature=b'v@:@')
            
            dpi_slider.setTarget_(self.slider_handler)
            dpi_slider.setAction_(action)
            
            quality_slider.setTarget_(self.slider_handler)
            quality_slider.setAction_(action)
            
            # Store handler reference to prevent garbage collection
            self._current_handler = self.slider_handler
            
            # Add all controls to accessory view
            for control in [format_label, format_popup, 
                            dpi_label, dpi_slider, dpi_value,
                            quality_label, quality_slider, quality_value,
                            transparency_check]:
                accessory_view.addSubview_(control)
            
            save_panel.setAccessoryView_(accessory_view)
            
            # Set initial directory and allowed types
            initial_path = FileManager.get_last_directory()
            url = NSURL.fileURLWithPath_(initial_path)
            save_panel.setDirectoryURL_(url)
            save_panel.setAllowedFileTypes_([SUPPORTED_EXPORT_FORMATS[f]['extension'][1:] for f in formats])
            
            # Run panel
            response = save_panel.runModal()
            
            if response == NSModalResponseOK:
                filename = save_panel.URL().path()
                FileManager.set_last_directory(os.path.dirname(filename))
                
                # Create settings object with current values
                settings = ExportSettings(
                    format=format_popup.titleOfSelectedItem(),
                    dpi=int(dpi_slider.doubleValue()),
                    quality=int(quality_slider.doubleValue()),
                    transparency=(transparency_check.state() == NSOnState)
                )
                
                # Show progress dialog
                progress = ModalView(size_hint=(0.4, 0.2))
                progress_bar = ProgressBar(max=100, value=0)
                progress.add_widget(progress_bar)
                progress.open()
                
                def export_on_main_thread(dt):
                    try:
                        progress_bar.value = 50
                        success = FileManager.export_canvas(
                            self.root.ids.paint_widget,
                            filename,
                            settings
                        )
                        progress_bar.value = 100
                        progress.dismiss()
                        
                        if success:
                            self.title = f"Paint - {os.path.basename(filename)} (Exported)"
                        else:
                            self.show_error("Failed to export file")
                            
                    except Exception as e:
                        progress.dismiss()
                        self.show_error(f"Error during export: {str(e)}")
                
                Clock.schedule_once(export_on_main_thread, 0)
                
        except Exception as e:
            self.show_error(f"Error in export dialog: {str(e)}")

if __name__ == '__main__':
    try:
        PaintApp().run()
    except Exception as e:
        print(f"Application failed to start: {e}")
