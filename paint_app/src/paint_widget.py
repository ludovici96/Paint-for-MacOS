from kivy.uix.widget import Widget
from kivy.graphics import Color, Line

class PaintWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_color = (0, 0, 0, 1)  # Default black
        self.line_width = 2

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            with self.canvas:
                Color(*self.current_color)
                touch.ud['line'] = Line(points=[touch.x, touch.y], width=self.line_width)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]
