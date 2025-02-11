# This file defines the toolbar UI components including menu buttons, dropdowns, and tool buttons.
# It handles the menu system and tool selection interface.
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from font_manager import FontManager
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

class ToolButton(ButtonBehavior, Image):
    tool = StringProperty('')
    tooltip = StringProperty('')
    active = BooleanProperty(False)  # Changed to BooleanProperty
    
    def on_release(self):
        if self.parent:
            # Deactivate all other tool buttons
            for child in self.parent.children:
                if isinstance(child, ToolButton) and child != self:
                    child.active = False
            # Activate this button
            self.active = True
            # Get the app instance correctly
            app = App.get_running_app()
            app.select_tool(self.tool)

class MenuButton(Button):
    dropdown = ObjectProperty(None, allownone=True)
    _current_dropdown = None  # Class variable to track active dropdown
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.98, 0.98, 0.98, 1) if not Window.is_dark_theme else (0.2, 0.2, 0.2, 1)
        self.color = (0.1, 0.1, 0.1, 1) if not Window.is_dark_theme else (0.9, 0.9, 0.9, 1)
        self.size_hint = (None, None)
        self.height = '22dp'
        self.width = '80dp'
        self.font_name = FontManager.get_system_font()
        self.font_size = '13sp'

    def on_release(self):
        if self.dropdown:
            # If there's already a dropdown showing, dismiss it first
            if MenuButton._current_dropdown and MenuButton._current_dropdown != self.dropdown:
                MenuButton._current_dropdown.dismiss()
            if not self.dropdown.parent:
                self.dropdown.open(self)
                MenuButton._current_dropdown = self.dropdown

class MenuBar(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.size_hint_y = None
        self.height = '22dp'
        self.background_color = (0.98, 0.98, 0.98, 1) if not Window.is_dark_theme else (0.2, 0.2, 0.2, 1)
        self.active_tool = None
        # Initialize dropdowns as None
        self.file_dropdown = None
        self.edit_dropdown = None
        self.tools_dropdown = None
        self.view_dropdown = None
        # Bind window focus to dismiss all dropdowns
        Window.bind(on_cursor_leave=self.dismiss_all_dropdowns,
                   on_motion=self.check_mouse_pos)
        self.create_menus()

    def check_mouse_pos(self, instance, etype, me):
        """Dismiss dropdowns if mouse moves outside menu area"""
        if me.pos[1] < self.y or me.pos[1] > (self.y + self.height):
            self.dismiss_all_dropdowns()

    def dismiss_all_dropdowns(self, *args):
        """Dismiss all dropdowns"""
        if hasattr(MenuButton, '_current_dropdown') and MenuButton._current_dropdown:
            MenuButton._current_dropdown.dismiss()
            MenuButton._current_dropdown = None

    def create_menus(self):
        self.add_file_menu()
        self.add_edit_menu()
        self.add_tools_menu()
        self.add_view_menu()

    def add_file_menu(self):
        file_button = MenuButton(text='File')
        self.file_dropdown = self.create_styled_dropdown()
        file_button.dropdown = self.file_dropdown
        file_items = [
            ('New Canvas', lambda x: self.app.new_canvas()),
            ('Open...', lambda x: self.app.open_image()),
            ('Save', lambda x: self.app.save_canvas()),
            #('Save As...', 'cmd+shift+S', lambda x: self.app.save_canvas()),
            ('Export...', lambda x: self.app.export_image()),
        ]
        self.create_dropdown_items(self.file_dropdown, file_items)
        file_button.bind(on_release=self.file_dropdown.open)
        self.add_widget(file_button)

    def add_edit_menu(self):
        edit_button = MenuButton(text='Edit')
        self.edit_dropdown = self.create_styled_dropdown()
        edit_button.dropdown = self.edit_dropdown  # Store dropdown reference
        edit_items = [
            ('Undo', lambda x: self.app.root.ids.paint_widget.undo()),
            ('Redo', lambda x: self.app.root.ids.paint_widget.redo()),
            ('Cut', 'cmd+X', lambda x: print('Cut - Not implemented')),
            ('Copy', 'cmd+C', lambda x: print('Copy - Not implemented')),
            ('Paste', 'cmd+V', lambda x: print('Paste - Not implemented')),
            ('Clear All', lambda x: self.app.root.ids.paint_widget.canvas.clear()),
        ]
        self.create_dropdown_items(self.edit_dropdown, edit_items)
        edit_button.bind(on_release=self.edit_dropdown.open)
        self.add_widget(edit_button)

    def add_tools_menu(self):
        tools_button = MenuButton(text='Tools')
        self.tools_dropdown = self.create_styled_dropdown()
        tools_button.dropdown = self.tools_dropdown  # Store dropdown reference

        tool_names = ['PENCIL', 'BRUSH', 'ERASER', 'LINE', 'RECTANGLE', 'CIRCLE', 'FILL']
        for tool_name in tool_names:
            btn = Button(
                text=tool_name.title(),
                size_hint_y=None,
                height='35dp',
                background_normal='',
                background_color=(0.98, 0.98, 0.98, 1) if not Window.is_dark_theme else (0.25, 0.25, 0.25, 1),
                color=(0.1, 0.1, 0.1, 1) if not Window.is_dark_theme else (0.9, 0.9, 0.9, 1),
                font_name=FontManager.get_system_font(),
                font_size='13sp'
            )
            
            def create_tool_callback(tool):
                def callback(instance):
                    self.app.select_tool(tool)
                    # Update quick access toolbar button states
                    quick_toolbar = self.app.root.ids.quick_toolbar
                    for child in quick_toolbar.children:
                        if isinstance(child, ToolButton):
                            child.active = (child.tool == tool)
                    self.tools_dropdown.dismiss()
                return callback
            
            btn.bind(on_release=create_tool_callback(tool_name))
            self.tools_dropdown.add_widget(btn)

        tools_button.bind(on_release=self.tools_dropdown.open)
        self.add_widget(tools_button)

    def add_view_menu(self):
        view_button = MenuButton(text='View')
        self.view_dropdown = self.create_styled_dropdown()
        view_button.dropdown = self.view_dropdown  # Store dropdown reference
        view_items = [
            ('Show Grid', 'meta+G', lambda x: print('Show Grid - Not implemented')),
            ('Zoom In', 'meta+plus', lambda x: print('Zoom In - Not implemented')),
            ('Zoom Out', 'meta+minus', lambda x: print('Zoom Out - Not implemented')),
            ('Actual Size', 'meta+0', lambda x: print('Actual Size - Not implemented')),
            ('Color Picker', 'meta+K', self.app.show_color_picker),
        ]
        self.create_dropdown_items(self.view_dropdown, view_items)
        brush_style_btn = self.create_brush_style_button()
        self.view_dropdown.add_widget(brush_style_btn)
        view_button.bind(on_release=self.view_dropdown.open)
        self.add_widget(view_button)

    # ... keeping all the helper methods from the original MenuBar class ...
    def create_dropdown_items(self, dropdown, items):
        for item in items:
            # Handle both (text, callback) and (text, shortcut, callback) formats
            if len(item) == 2:
                text, callback = item
                shortcut = None
            else:
                text, shortcut, callback = item

            btn = Button(
                text=f'{text}\t{shortcut}' if shortcut else text,
                size_hint_y=None,
                height='35dp',
                background_normal='',
                background_color=(0.98, 0.98, 0.98, 1) if not Window.is_dark_theme else (0.25, 0.25, 0.25, 1),
                color=(0.1, 0.1, 0.1, 1) if not Window.is_dark_theme else (0.9, 0.9, 0.9, 1),
                font_name=FontManager.get_system_font(),  # Use system font
                font_size='13sp'
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

    def create_styled_dropdown(self):
        """Creates a styled dropdown menu with macOS appearance"""
        dropdown = DropDown()
        dropdown.bar_width = 1
        dropdown.spacing = 0
        dropdown.container.padding = [0, 1, 0, 1]
        dropdown.container.spacing = 0
        
        # Add background color to dropdown
        with dropdown.container.canvas.before:
            if not Window.is_dark_theme:
                dropdown.container.canvas.before.add(Color(0.98, 0.98, 0.98, 1))
            else:
                dropdown.container.canvas.before.add(Color(0.2, 0.2, 0.2, 1))
            self.rect = Rectangle(size=dropdown.container.size, pos=dropdown.container.pos)
            dropdown.container.canvas.before.add(self.rect)
            
        # Update background size when dropdown size changes
        def update_rect(instance, value):
            self.rect.size = instance.size
            self.rect.pos = instance.pos
            
        dropdown.container.bind(size=update_rect, pos=update_rect)
        return dropdown

    def create_brush_style_button(self):
        return Button(
            text='Brush Style ►',
            size_hint_y=None,
            height='35dp',
            background_normal='',
            background_color=(0.25, 0.25, 0.25, 1),
            color=(0.9, 0.9, 0.9, 1)
        )
