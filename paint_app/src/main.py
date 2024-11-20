from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from paint_widget import PaintWidget
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

# Set window size
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

class PaintApp(App):
    def build(self):
        self.color_popup = None  # Store popup reference
        return Builder.load_file('paint_app/resources/paint.kv')
    
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
