from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.properties import ColorProperty, NumericProperty

class PaintWidget(Widget):
    current_color = ColorProperty([0, 0, 0, 1])  # Changed to ColorProperty
    line_width = NumericProperty(2)  # Changed to NumericProperty

    def set_color(self, color):
        self.current_color = color
        
    def set_line_width(self, width):
        self.line_width = width

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            with self.canvas:
                Color(*self.current_color)
                touch.ud['line'] = Line(points=[touch.x, touch.y], width=self.line_width)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]
