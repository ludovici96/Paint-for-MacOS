from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Bezier
from kivy.properties import ColorProperty, NumericProperty
from collections import deque
from kivy.core.window import Window

class DrawCommand:
    def __init__(self, canvas_instructions):
        self.instructions = canvas_instructions

    def undo(self, canvas):
        for instr in self.instructions:
            canvas.remove(instr)

    def redo(self, canvas):
        for instr in self.instructions:
            canvas.add(instr)

class PaintWidget(Widget):
    current_color = ColorProperty([1, 1, 1, 1])  # Changed from [0, 0, 0, 1] to [1, 1, 1, 1] for white
    line_width = NumericProperty(2)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.undo_stack = deque(maxlen=50)  # Limit stack size to prevent memory issues
        self.redo_stack = deque(maxlen=50)
        self.points = []
        self.current_instructions = None

    def set_color(self, color):
        self.current_color = color
        
    def set_line_width(self, width):
        self.line_width = width

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.points = [touch.x, touch.y]
            with self.canvas:
                Color(*self.current_color)
                touch.ud['current_color'] = Color(*self.current_color)
                touch.ud['line'] = Line(points=self.points, width=self.line_width)
            self.current_instructions = [touch.ud['current_color'], touch.ud['line']]

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and 'line' in touch.ud:
            self.points.extend([touch.x, touch.y])
            # Apply smoothing when we have enough points
            if len(self.points) > 4:
                # Create smooth curve using the last 4 points
                touch.ud['line'].points = self.smooth_points(self.points)

    def on_touch_up(self, touch):
        if 'line' in touch.ud:
            if self.current_instructions:
                command = DrawCommand(self.current_instructions)
                self.undo_stack.append(command)
                self.redo_stack.clear()  # Clear redo stack when new action is performed
                self.current_instructions = None

    def smooth_points(self, points):
        # If we have few points, return them as is
        if len(points) < 4:
            return points
        
        smooth_points = []
        smooth_points.extend(points[:2])  # Add first point
        
        # Create smooth curve through points
        for i in range(2, len(points) - 2, 2):
            x0, y0 = points[i - 2], points[i - 1]  # Previous point
            x1, y1 = points[i], points[i + 1]      # Current point
            x2, y2 = points[i + 2], points[i + 3]  # Next point
            
            # Calculate control points for Bézier curve
            cp1x = x0 + (x1 - x0) * 0.5
            cp1y = y0 + (y1 - y0) * 0.5
            cp2x = x1 + (x2 - x1) * 0.5
            cp2y = y1 + (y2 - y1) * 0.5
            
            # Add points for smooth curve
            smooth_points.extend([cp1x, cp1y, x1, y1, cp2x, cp2y])
        
        smooth_points.extend(points[-2:])  # Add last point
        return smooth_points

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo(self.canvas)
            self.redo_stack.append(command)

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.redo(self.canvas)
            self.undo_stack.append(command)
