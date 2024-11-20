from kivy.app import App
from kivy.config import Config

# Set window size
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

class PaintApp(App):
    def build(self):
        return super().build()

if __name__ == '__main__':
    PaintApp().run()
