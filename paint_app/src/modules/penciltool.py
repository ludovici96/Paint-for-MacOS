from kivy.graphics import Color, Line
from .abstract_tool import AbstractTool

class PencilTool(AbstractTool):
    def on_touch_down(self, x, y):
        with self.canvas:
            Color(*self.color)
            self.line = Line(points=[x, y], width=self.line_width)
        self.instructions = [self.line]  # Store instructions
        return None  # Don't return instructions yet

    def on_touch_move(self, x, y):
        self.line.points += [x, y]

    def on_touch_up(self, x, y):
        return self.instructions  # Return instructions for undo/redo
