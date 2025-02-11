
from kivy.graphics import Color, Line
from .abstract_tool import AbstractTool

class EraserTool(AbstractTool):
    def on_touch_down(self, x, y):
        with self.canvas:
            Color(1, 1, 1, 1)  # White
            self.line = Line(points=[x, y], width=self.line_width * 2)
        return [self.line]

    def on_touch_move(self, x, y):
        self.line.points += [x, y]

    def on_touch_up(self, x, y):
        pass