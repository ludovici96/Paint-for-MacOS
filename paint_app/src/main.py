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
from kivy.uix.button import Button

# Set window size
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

class MenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.2, 0.2, 0.2, 1)
        self.color = (0.9, 0.9, 0.9, 1)
        self.size_hint = (None, None)
        self.height = '30dp'
        self.width = '100dp'

class MenuBar(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.size_hint_y = None
        self.height = '30dp'
        self.create_menus()

    def create_menus(self):
        # File Menu
        file_button = MenuButton(text='File')
        file_dropdown = DropDown()
        file_items = [
            ('New', lambda x: print('New - Not implemented')),
            ('Open...', lambda x: print('Open - Not implemented')),
            ('Save', lambda x: print('Save - Not implemented')),
            ('Export...', lambda x: print('Export - Not implemented')),
        ]
        self.create_dropdown_items(file_dropdown, file_items)
        file_button.bind(on_release=file_dropdown.open)
        self.add_widget(file_button)

        # Edit Menu
        edit_button = MenuButton(text='Edit')
        edit_dropdown = DropDown()
        edit_items = [
            ('Undo', lambda x: self.app.root.ids.paint_widget.undo()),
            ('Redo', lambda x: self.app.root.ids.paint_widget.redo()),
            ('Clear All', lambda x: self.app.root.ids.paint_widget.canvas.clear()),
        ]
        self.create_dropdown_items(edit_dropdown, edit_items)
        edit_button.bind(on_release=edit_dropdown.open)
        self.add_widget(edit_button)

        # Tools Menu
        tools_button = MenuButton(text='Tools')
        tools_dropdown = DropDown()
        tools_items = [
            ('Pencil', lambda x: self.app.select_tool('PENCIL')),
            ('Brush', lambda x: self.app.select_tool('BRUSH')),
            ('Eraser', lambda x: self.app.select_tool('ERASER')),
            ('Line', lambda x: self.app.select_tool('LINE')),
            ('Rectangle', lambda x: self.app.select_tool('RECTANGLE')),
            ('Circle', lambda x: self.app.select_tool('CIRCLE')),
        ]
        self.create_dropdown_items(tools_dropdown, tools_items)
        tools_button.bind(on_release=tools_dropdown.open)
        self.add_widget(tools_button)

        # View Menu
        view_button = MenuButton(text='View')
        view_dropdown = DropDown()
        
        # Color Picker item
        color_picker_btn = Button(
            text='Color Picker',
            size_hint_y=None,
            height='35dp',
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1),
            color=(0.9, 0.9, 0.9, 1)
        )
        color_picker_btn.bind(on_release=lambda x: self.app.show_color_picker())
        color_picker_btn.bind(on_release=view_dropdown.dismiss)
        view_dropdown.add_widget(color_picker_btn)

        # Brush Style submenu
        brush_style_btn = Button(
            text='Brush Style ►',
            size_hint_y=None,
            height='35dp',
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1),
            color=(0.9, 0.9, 0.9, 1)
        )
        brush_submenu = self.create_brush_style_submenu()
        brush_style_btn.bind(on_release=brush_submenu.open)
        view_dropdown.add_widget(brush_style_btn)

        view_button.bind(on_release=view_dropdown.open)
        self.add_widget(view_button)

    def create_dropdown_items(self, dropdown, items):
        for text, callback in items:
            btn = Button(
                text=text, 
                size_hint_y=None, 
                height='35dp',
                background_normal='',
                background_color=(0.25, 0.25, 0.25, 1),
                color=(0.9, 0.9, 0.9, 1)
            )
            btn.bind(on_release=callback)
            btn.bind(on_release=dropdown.dismiss)
            dropdown.add_widget(btn)

    def create_brush_style_submenu(self):
        submenu = DropDown()
        
        round_btn = Button(
            text='Round',
            size_hint_y=None,
            height='35dp',
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1),
            color=(0.9, 0.9, 0.9, 1)
        )
        round_btn.bind(
            on_release=lambda x: self.app.root.ids.paint_widget.tool_manager.set_brush_style(self.app.brush_styles.ROUND)
        )
        round_btn.bind(on_release=submenu.dismiss)
        submenu.add_widget(round_btn)

        square_btn = Button(
            text='Square',
            size_hint_y=None,
            height='35dp',
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1),
            color=(0.9, 0.9, 0.9, 1)
        )
        square_btn.bind(
            on_release=lambda x: self.app.root.ids.paint_widget.tool_manager.set_brush_style(self.app.brush_styles.SQUARE)
        )
        square_btn.bind(on_release=submenu.dismiss)
        submenu.add_widget(square_btn)

        return submenu

class PaintApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brush_styles = BrushStyle

    def build(self):
        self.color_popup = None  # Store popup reference
        # Bind keyboard
        Window.bind(on_keyboard=self._on_keyboard)
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to the .kv file
        kv_path = os.path.join(os.path.dirname(current_dir), 'resources', 'paint.kv')
        root = Builder.load_file(kv_path)
        # Add menu bar to the root widget
        root.ids.toolbar.add_widget(MenuBar(self), 0)
        return root
    
    def select_tool(self, tool_name):
        try:
            tool = Tool[tool_name]
            self.root.ids.paint_widget.set_tool(tool)
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
        
        # Add confirm button
        confirm_button = Button(
            text='Select Color',
            size_hint_y=None,
            height='48dp'
        )
        content.add_widget(confirm_button)
        
        # Create and store popup reference
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

if __name__ == '__main__':
    PaintApp().run()
