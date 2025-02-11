# This file provides the base implementation for all shape-based tools (line, rectangle, circle).
# It includes shared functionality for shape manipulation, resizing, and movement.
from abc import abstractmethod
from kivy.graphics import Color, Line, Rectangle, InstructionGroup
from .abstract_tool import AbstractTool

class ShapeTool(AbstractTool):
    """Base class for moveable and resizable shapes"""
    def __init__(self, canvas, color, line_width):
        super().__init__(canvas, color, line_width)
        self.is_moving = False
        self.is_resizing = False
        self.shape = None
        self.offset_x = 0
        self.offset_y = 0
        self.resize_handle = None  # 'tl', 'tr', 'bl', 'br' for corners
        self.handle_size = 20  # Increased from 16 to 20
        self.hit_area = 40  # Increased from 30 to 40 for easier selection
        self.handles = InstructionGroup()  # Group for handle visuals
        self.active = False  # Add this to track if shape is being edited
        self.outline_width = 2  # Width for outlines

    def contains_point(self, x, y):
        if not self.shape:
            return False
        bounds = self.get_bounds()
        # Check resize handles first
        handle = self.get_resize_handle(x, y)
        if handle:
            self.resize_handle = handle
            return True
        # Then check main shape
        return (bounds['x'] <= x <= bounds['x'] + bounds['width'] and 
                bounds['y'] <= y <= bounds['y'] + bounds['height'])

    def get_resize_handle(self, x, y):
        if not self.shape:
            return None
        bounds = self.get_bounds()
        # Use larger hit area for detection
        half_hit = self.hit_area / 2
        
        # Top-left
        if abs(x - bounds['x']) < half_hit and abs(y - (bounds['y'] + bounds['height'])) < half_hit:
            return 'tl'
        # Top-right
        if abs(x - (bounds['x'] + bounds['width'])) < half_hit and abs(y - (bounds['y'] + bounds['height'])) < half_hit:
            return 'tr'
        # Bottom-left
        if abs(x - bounds['x']) < half_hit and abs(y - bounds['y']) < half_hit:
            return 'bl'
        # Bottom-right
        if abs(x - (bounds['x'] + bounds['width'])) < half_hit and abs(y - bounds['y']) < half_hit:
            return 'br'
        return None

    def draw_handles(self):
        """Draw visible resize handles at corners"""
        if not self.shape or not self.active:  # Only draw handles when shape is active
            self.canvas.remove(self.handles)
            return
        
        bounds = self.get_bounds()
        self.canvas.remove(self.handles)
        self.handles = InstructionGroup()
        
        # Draw dashed selection outline
        self.handles.add(Color(0.2, 0.6, 1, 1))  # Light blue color for selection
        if isinstance(self, LineTool):
            self.handles.add(Line(points=self.shape.points, width=1.5, dash_length=5, dash_offset=2))
        elif isinstance(self, RectangleTool):
            rect = self.shape.rectangle
            self.handles.add(Line(rectangle=rect, width=1.5, dash_length=5, dash_offset=2))
        elif isinstance(self, CircleTool):
            circle = self.shape.circle
            self.handles.add(Line(circle=circle, width=1.5, dash_length=5, dash_offset=2))

        # Draw resize handles
        positions = [
            (bounds['x'], bounds['y']),  # Bottom-left
            (bounds['x'] + bounds['width'], bounds['y']),  # Bottom-right
            (bounds['x'], bounds['y'] + bounds['height']),  # Top-left
            (bounds['x'] + bounds['width'], bounds['y'] + bounds['height'])  # Top-right
        ]
        
        for x, y in positions:
            # Black outer border
            self.handles.add(Color(0, 0, 0, 1))
            self.handles.add(Rectangle(
                pos=(x - self.handle_size/2 - 1, y - self.handle_size/2 - 1),
                size=(self.handle_size + 2, self.handle_size + 2)
            ))
            # White fill
            self.handles.add(Color(1, 1, 1, 1))
            self.handles.add(Rectangle(
                pos=(x - self.handle_size/2, y - self.handle_size/2),
                size=(self.handle_size, self.handle_size)
            ))
            # Inner blue border
            self.handles.add(Color(0.2, 0.6, 1, 1))
            self.handles.add(Line(
                rectangle=(x - self.handle_size/2, y - self.handle_size/2,
                          self.handle_size, self.handle_size),
                width=self.outline_width
            ))
        
        self.canvas.add(self.handles)

    def on_touch_down(self, x, y):
        if self.shape and self.contains_point(x, y):
            self.active = True  # Set shape as active when selected
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
            self.draw_handles()  # Redraw handles when selected
            return [self.shape]
        
        # If clicking outside any shape, deactivate current shape
        self.active = False
        self.canvas.remove(self.handles)  # Remove handle visuals
        
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
            self.move_shape(x - self.offset_x - self.get_bounds()['x'],
                          y - self.offset_y - self.get_bounds()['y'])
        else:
            self.preview_line.points = [self.start_x, self.start_y, x, y]

    def on_touch_up(self, x, y):
        if self.is_moving or self.is_resizing:
            self.is_moving = False
            self.is_resizing = False
            self.resize_handle = None
            if not self.active:
                self.canvas.remove(self.handles)
            else:
                self.draw_handles()  # Redraw handles if still active
            return None
        
        # New shape creation
        if hasattr(self, 'preview_line'):
            self.canvas.remove(self.preview_line)
            with self.canvas:
                Color(*self.color)
                self.shape = self.create_shape(x, y)  # Implement in subclasses
            self.active = True  # New shape starts as active
            self.draw_handles()
            return [self.shape]
        return None

    def get_shape_data(self):
        """Store original shape data for resize operations"""
        if isinstance(self, LineTool):
            return list(self.shape.points)
        elif isinstance(self, RectangleTool):
            return list(self.shape.rectangle)
        elif isinstance(self, CircleTool):
            return list(self.shape.circle)
        return None

    @abstractmethod
    def resize_shape(self, x, y):
        pass

    @abstractmethod
    def create_shape(self, x, y):
        """Create the final shape - implement in subclasses"""
        pass