from kivy.graphics import Color, Line
from .shapetool import ShapeTool

class RectangleTool(ShapeTool):
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
                bounds = self.get_bounds()
                self.offset_x = x - bounds['x']
                self.offset_y = y - bounds['y']
            return [self.shape]

        self.start_x = x
        self.start_y = y
        with self.canvas:
            self.color_instruction = Color(*self.color)
            self.preview = Line(rectangle=(x, y, 0, 0), width=self.line_width)
        return [self.color_instruction, self.preview]  # Return both instructions

    def on_touch_move(self, x, y):
        if self.is_resizing and self.shape:
            self.resize_shape(x, y)
        elif self.is_moving and self.shape:
            new_x = x - self.offset_x
            new_y = y - self.offset_y
            bounds = self.get_bounds()
            self.move_shape(new_x - bounds['x'], new_y - bounds['y'])
        else:
            self.preview.rectangle = (
                min(self.start_x, x),
                min(self.start_y, y),
                abs(x - self.start_x),
                abs(y - self.start_y)
            )

    def on_touch_up(self, x, y):
        if self.is_moving or self.is_resizing:
            self.is_moving = False
            self.is_resizing = False
            self.resize_handle = None
            return None

        if hasattr(self, 'preview') and hasattr(self, 'color_instruction'):
            self.canvas.remove(self.preview)
            self.canvas.remove(self.color_instruction)
        
        with self.canvas:
            color_instruction = Color(*self.color)
            shape = Line(
                rectangle=(
                    min(self.start_x, x),
                    min(self.start_y, y),
                    abs(x - self.start_x),
                    abs(y - self.start_y)
                ),
                width=self.line_width
            )
            self.shape = shape
        return [color_instruction, shape]  # Return both instructions

    def get_bounds(self):
        if not self.shape:
            return None
        rect = self.shape.rectangle
        return {
            'x': rect[0],
            'y': rect[1],
            'width': rect[2],
            'height': rect[3]
        }

    def move_shape(self, dx, dy):
        rect = list(self.shape.rectangle)
        rect[0] += dx
        rect[1] += dy
        self.shape.rectangle = rect

    def resize_shape(self, x, y):
        if not self.resize_handle or not self.start_resize:
            return

        rect = list(self.shape.rectangle)
        original = self.start_resize['original_shape']
        
        # Always maintain the original anchor point opposite to the drag handle
        if self.resize_handle == 'br':  # Dragging bottom-right, anchor top-left
            rect[0] = original[0]  # Keep left edge fixed
            rect[1] = original[1]  # Keep top edge fixed
            rect[2] = max(0, x - rect[0])  # New width
            rect[3] = max(0, y - rect[1])  # New height
        elif self.resize_handle == 'bl':  # Dragging bottom-left, anchor top-right
            right_edge = original[0] + original[2]  # Keep right edge fixed
            rect[0] = min(x, right_edge)  # New left position
            rect[1] = original[1]  # Keep top edge fixed
            rect[2] = max(0, right_edge - rect[0])  # New width
            rect[3] = max(0, y - rect[1])  # New height
        elif self.resize_handle == 'tr':  # Dragging top-right, anchor bottom-left
            rect[0] = original[0]  # Keep left edge fixed
            bottom_edge = original[1]  # Keep bottom edge fixed
            rect[1] = min(y, bottom_edge + original[3])  # New top position
            rect[2] = max(0, x - rect[0])  # New width
            rect[3] = max(0, bottom_edge + original[3] - rect[1])  # New height
        elif self.resize_handle == 'tl':  # Dragging top-left, anchor bottom-right
            right_edge = original[0] + original[2]  # Keep right edge fixed
            bottom_edge = original[1]  # Keep bottom edge fixed
            rect[0] = min(x, right_edge)  # New left position
            rect[1] = min(y, bottom_edge + original[3])  # New top position
            rect[2] = max(0, right_edge - rect[0])  # New width
            rect[3] = max(0, bottom_edge + original[3] - rect[1])  # New height

        if rect[2] > 0 and rect[3] > 0:  # Prevent negative size
            self.shape.rectangle = rect
            self.draw_handles()

    def create_shape(self, x, y):
        return Line(
            rectangle=(
                min(self.start_x, x),
                min(self.start_y, y),
                abs(x - self.start_x),
                abs(y - self.start_y)
            ),
            width=self.line_width
        )
