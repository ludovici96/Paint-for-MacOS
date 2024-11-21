from kivy.graphics import Color
from .abstract_tool import AbstractTool

class FillTool(AbstractTool):
    def __init__(self, canvas, color, line_width):
        super().__init__(canvas, color, line_width)
        self.tolerance = 32  # Default tolerance value (0-255)

    def on_touch_down(self, x, y):
        with self.canvas:
            Color(*self.color)
            # Store the initial point for flood fill
            self.start_point = (int(x), int(y))
            # We'll implement the actual fill algorithm later
            return None  # Return None for now

    def on_touch_move(self, x, y):
        # Fill tool doesn't need to respond to movement
        pass

    def on_touch_up(self, x, y):
        # Implement the flood fill algorithm here
        # For now, just return empty list
        return []

    def set_tolerance(self, tolerance):
        """Set the color tolerance for the fill operation (0-255)"""
        self.tolerance = max(0, min(255, tolerance))
