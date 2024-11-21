from kivy.graphics import Color, Ellipse, Rectangle
from .abstract_tool import AbstractTool, BrushStyle

class BrushTool(AbstractTool):
    def __init__(self, canvas, color, line_width, style=BrushStyle.ROUND):
        super().__init__(canvas, color, line_width)
        self.style = style
        self.instructions = []  # Initialize instructions list

    def on_touch_down(self, x, y):
        self.instructions = []  # Reset instructions for new stroke
        with self.canvas:
            Color(*self.color)
            self._add_brush_point(x, y)
        return None  # Don't return instructions yet

    def on_touch_move(self, x, y):
        with self.canvas:
            Color(*self.color)
            self._add_brush_point(x, y)

    def on_touch_up(self, x, y):
        return self.instructions  # Return all instructions for undo/redo

    def _add_brush_point(self, x, y):
        size = self.line_width * 2
        with self.canvas:
            Color(*self.color)
            if self.style == BrushStyle.ROUND:
                point = Ellipse(pos=(x - size/2, y - size/2), size=(size, size))
            else:  # SQUARE
                point = Rectangle(pos=(x - size/2, y - size/2), size=(size, size))
            self.instructions.append(point)
