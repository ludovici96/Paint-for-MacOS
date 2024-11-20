from enum import Enum, auto
from abc import ABC, abstractmethod
from kivy.graphics import Color, Line, Ellipse, Rectangle, InstructionGroup

class Tool(Enum):
    PENCIL = auto()
    BRUSH = auto()
    ERASER = auto()
    LINE = auto()
    RECTANGLE = auto()
    CIRCLE = auto()
    FILL = auto()

class BrushStyle(Enum):
    ROUND = auto()
    SQUARE = auto()

class AbstractTool(ABC):
    def __init__(self, canvas, color, line_width):
        self.canvas = canvas
        self.color = color
        self.line_width = line_width
        self.last_x = None
        self.last_y = None

    @abstractmethod
    def on_touch_down(self, x, y):
        pass

    @abstractmethod
    def on_touch_move(self, x, y):
        pass

    @abstractmethod
    def on_touch_up(self, x, y):
        pass

class PencilTool(AbstractTool):
    def on_touch_down(self, x, y):
        with self.canvas:
            Color(*self.color)
            self.line = Line(points=[x, y], width=self.line_width)
        return [self.line]

    def on_touch_move(self, x, y):
        self.line.points += [x, y]

    def on_touch_up(self, x, y):
        pass

class BrushTool(AbstractTool):
    def __init__(self, canvas, color, line_width, style=BrushStyle.ROUND):
        super().__init__(canvas, color, line_width)
        self.style = style
        self.stroke_points = []

    def on_touch_down(self, x, y):
        self.stroke_points = []
        self._add_brush_point(x, y)
        return self.stroke_points

    def on_touch_move(self, x, y):
        self._add_brush_point(x, y)

    def on_touch_up(self, x, y):
        pass

    def _add_brush_point(self, x, y):
        with self.canvas:
            Color(*self.color)
            size = self.line_width * 2
            if self.style == BrushStyle.ROUND:
                point = Ellipse(pos=(x - size/2, y - size/2), size=(size, size))
            else:  # SQUARE
                point = Rectangle(pos=(x - size/2, y - size/2), size=(size, size))
            self.stroke_points.append(point)

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
            Color(*self.color)
            self.preview = Line(rectangle=(x, y, 0, 0), width=self.line_width)
        return [self.preview]

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

        self.canvas.remove(self.preview)
        with self.canvas:
            Color(*self.color)
            self.shape = Line(
                rectangle=(
                    min(self.start_x, x),
                    min(self.start_y, y),
                    abs(x - self.start_x),
                    abs(y - self.start_y)
                ),
                width=self.line_width
            )
        return [self.shape]

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

class ToolManager:
    def __init__(self):
        self.current_tool = Tool.PENCIL
        self.brush_style = BrushStyle.ROUND
        
    def set_tool(self, tool):
        if isinstance(tool, Tool):
            self.current_tool = tool
        else:
            raise ValueError("Invalid tool selected")
    
    def get_current_tool(self):
        return self.current_tool

    def create_tool(self, canvas, color, line_width):
        if self.current_tool == Tool.PENCIL:
            return PencilTool(canvas, color, line_width)
        elif self.current_tool == Tool.BRUSH:
            return BrushTool(canvas, color, line_width, self.brush_style)
        elif self.current_tool == Tool.ERASER:
            return EraserTool(canvas, color, line_width)
        elif self.current_tool == Tool.LINE:
            return LineTool(canvas, color, line_width)
        elif self.current_tool == Tool.RECTANGLE:
            return RectangleTool(canvas, color, line_width)
        elif self.current_tool == Tool.CIRCLE:
            return CircleTool(canvas, color, line_width)
        else:
            raise ValueError("Tool not implemented")

    def set_brush_style(self, style):
        if isinstance(style, BrushStyle):
            self.brush_style = style