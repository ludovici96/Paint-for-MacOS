from kivy.graphics import Color, Line
from .shapetool import ShapeTool

class LineTool(ShapeTool):
    def on_touch_down(self, x, y):
        if self.shape and self.contains_point(x, y):
            if self.resize_handle:
                self.is_resizing = True
                bounds = self.get_bounds()
                self.start_resize = {
                    'x': x, 'y': y,
                    'bounds': bounds.copy()
                }
            else:
                self.is_moving = True
                self.offset_x = x - self.start_x
                self.offset_y = y - self.start_y
            return [self.shape]
        
        self.start_x = x
        self.start_y = y
        with self.canvas:
            Color(*self.color)
            self.preview_line = Line(points=[x, y, x, y], width=self.line_width)
        return [self.preview_line]

    def on_touch_move(self, x, y):
        if self.is_resizing and self.shape:
            self.resize_shape(x, y)
        elif self.is_moving and self.shape:
            dx = x - self.offset_x - self.start_x
            dy = y - self.offset_y - self.start_y
            self.move_shape(dx, dy)
        else:
            self.preview_line.points = [self.start_x, self.start_y, x, y]

    def on_touch_up(self, x, y):
        if self.is_moving or self.is_resizing:
            self.is_moving = False
            self.is_resizing = False
            self.resize_handle = None
            return None

        self.canvas.remove(self.preview_line)
        with self.canvas:
            Color(*self.color)
            self.shape = Line(
                points=[self.start_x, self.start_y, x, y],
                width=self.line_width
            )
        return [self.shape]

    def get_bounds(self):
        if not self.shape:
            return None
        points = self.shape.points
        x1, y1, x2, y2 = points[0], points[1], points[2], points[3]
        return {
            'x': min(x1, x2),
            'y': min(y1, y2),
            'width': abs(x2 - x1),
            'height': abs(y2 - y1)
        }

    def move_shape(self, dx, dy):
        points = self.shape.points
        self.shape.points = [
            points[0] + dx, points[1] + dy,
            points[2] + dx, points[3] + dy
        ]
        self.start_x += dx
        self.start_y += dy

    def resize_shape(self, x, y):
        if not self.resize_handle or not self.start_resize:
            return

        points = list(self.shape.points)
        
        # Move only the end being dragged, keeping the opposite end fixed
        if self.resize_handle in ['tl', 'bl']:  # Moving start point
            points[0] = x
            points[1] = y
        else:  # Moving end point
            points[2] = x
            points[3] = y

        self.shape.points = points
        self.draw_handles()

    def create_shape(self, x, y):
        return Line(
            points=[self.start_x, self.start_y, x, y],
            width=self.line_width
        )
