from kivy.graphics import Color, Line
from .shapetool import ShapeTool

class CircleTool(ShapeTool):
    def on_touch_down(self, x, y):
        if self.shape and self.contains_point(x, y):
            if self.resize_handle:
                self.is_resizing = True
                bounds = self.get_bounds()
                self.start_resize = {
                    'x': x, 'y': y,
                    'bounds': bounds.copy(),
                    'original_shape': self.get_shape_data()
                }
            else:
                self.is_moving = True
                self.offset_x = x - self.center_x
                self.offset_y = y - self.center_y
            return [self.shape]

        self.center_x = x
        self.center_y = y
        with self.canvas:
            Color(*self.color)
            self.preview = Line(circle=(x, y, 0), width=self.line_width)
        return [self.preview]

    def on_touch_move(self, x, y):
        if self.is_resizing and self.shape:
            self.resize_shape(x, y)
        elif self.is_moving and self.shape:
            dx = x - self.offset_x - self.center_x
            dy = y - self.offset_y - self.center_y
            self.move_shape(dx, dy)
        else:
            radius = ((x - self.center_x) ** 2 + (y - self.center_y) ** 2) ** 0.5
            self.preview.circle = (self.center_x, self.center_y, radius)

    def on_touch_up(self, x, y):
        if self.is_moving or self.is_resizing:
            self.is_moving = False
            self.is_resizing = False
            self.resize_handle = None
            return None

        self.canvas.remove(self.preview)
        radius = ((x - self.center_x) ** 2 + (y - self.center_y) ** 2) ** 0.5
        with self.canvas:
            Color(*self.color)
            self.shape = Line(
                circle=(self.center_x, self.center_y, radius),
                width=self.line_width
            )
        return [self.shape]

    def get_bounds(self):
        if not self.shape:
            return None
        circle = self.shape.circle
        return {
            'x': circle[0] - circle[2],
            'y': circle[1] - circle[2],
            'width': circle[2] * 2,
            'height': circle[2] * 2
        }

    def move_shape(self, dx, dy):
        circle = list(self.shape.circle)
        circle[0] += dx
        circle[1] += dy
        self.shape.circle = circle
        self.center_x += dx
        self.center_y += dy

    def resize_shape(self, x, y):
        if not self.resize_handle or not self.start_resize:
            return
            
        original = self.start_resize['original_shape']
        original_center = (original[0], original[1])
        original_radius = original[2]
        
        # Calculate new radius based on the distance from the anchor point
        if self.resize_handle == 'br':  # Anchor top-left
            anchor_x = original_center[0] - original_radius
            anchor_y = original_center[1] + original_radius
            self.center_x = (x + anchor_x) / 2
            self.center_y = (y + anchor_y) / 2
        elif self.resize_handle == 'bl':  # Anchor top-right
            anchor_x = original_center[0] + original_radius
            anchor_y = original_center[1] + original_radius
            self.center_x = (x + anchor_x) / 2
            self.center_y = (y + anchor_y) / 2
        elif self.resize_handle == 'tr':  # Anchor bottom-left
            anchor_x = original_center[0] - original_radius
            anchor_y = original_center[1] - original_radius
            self.center_x = (x + anchor_x) / 2
            self.center_y = (y + anchor_y) / 2
        elif self.resize_handle == 'tl':  # Anchor bottom-right
            anchor_x = original_center[0] + original_radius
            anchor_y = original_center[1] - original_radius
            self.center_x = (x + anchor_x) / 2
            self.center_y = (y + anchor_y) / 2
        
        # Calculate new radius based on the distance to the anchor point
        radius = max(1, ((x - anchor_x) ** 2 + (y - anchor_y) ** 2) ** 0.5 / 2)
        self.shape.circle = (self.center_x, self.center_y, radius)
        self.draw_handles()

    def create_shape(self, x, y):
        radius = ((x - self.center_x) ** 2 + (y - self.center_y) ** 2) ** 0.5
        return Line(
            circle=(self.center_x, self.center_y, radius),
            width=self.line_width
        )
