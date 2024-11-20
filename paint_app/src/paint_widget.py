from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Bezier
from kivy.properties import ColorProperty, NumericProperty, ObjectProperty
from collections import deque
from kivy.core.window import Window
from tools import ToolManager, Tool, BrushStyle, ShapeTool  # Add ShapeTool to imports

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
    current_color = ColorProperty([0, 0, 0, 1])  # Changed from [1, 1, 1, 1] to [0, 0, 0, 1] for black
    line_width = NumericProperty(2)
    tool_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_manager = ToolManager()
        self.undo_stack = deque(maxlen=50)  # Limit stack size to prevent memory issues
        self.redo_stack = deque(maxlen=50)
        self.points = []
        self.current_instructions = None
        self.current_tool = None  # Add this to maintain tool reference

    def set_color(self, color):
        self.current_color = color
        
    def set_line_width(self, width):
        self.line_width = width

    def set_tool(self, tool):
        # Confirm any active shape before switching tools
        self.confirm_current_shape()
        self.tool_manager.set_tool(tool)

    def confirm_current_shape(self):
        """Confirm the current shape and clean up"""
        if isinstance(self.current_tool, ShapeTool) and self.current_tool.shape:
            # Save the current shape to undo stack
            command = DrawCommand([self.current_tool.shape])
            self.undo_stack.append(command)
            self.redo_stack.clear()
            # Clean up
            self.current_tool.active = False
            self.current_tool.canvas.remove(self.current_tool.handles)
            self.current_tool = None

    def on_touch_down(self, touch):
        # If clicking in the toolbar area, confirm any active shape
        if touch.y > self.height - 56:  # Toolbar height is 56dp
            self.confirm_current_shape()
            return False

        if self.collide_point(*touch.pos):
            # First check if we have an active shape tool that's being edited
            if isinstance(self.current_tool, ShapeTool) and self.current_tool.shape:
                # Click outside shape area finalizes it
                if not self.current_tool.contains_point(touch.x, touch.y):
                    if self.current_tool.shape:
                        command = DrawCommand([self.current_tool.shape])
                        self.undo_stack.append(command)
                        self.redo_stack.clear()
                    self.current_tool = None
                    return True
                # Click inside continues editing
                instructions = self.current_tool.on_touch_down(touch.x, touch.y)
                self.current_instructions = instructions
                return True

            # Create new tool instance if no active tool
            self.current_tool = self.tool_manager.create_tool(self.canvas, self.current_color, self.line_width)
            touch.ud['tool'] = self.current_tool
            instructions = self.current_tool.on_touch_down(touch.x, touch.y)
            self.current_instructions = instructions

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            if 'tool' in touch.ud:
                touch.ud['tool'].on_touch_move(touch.x, touch.y)
            elif isinstance(self.current_tool, ShapeTool):
                self.current_tool.on_touch_move(touch.x, touch.y)

    def on_touch_up(self, touch):
        tool = touch.ud.get('tool') or self.current_tool
        if tool:
            final_instructions = tool.on_touch_up(touch.x, touch.y)
            if final_instructions:
                command = DrawCommand(final_instructions)
                self.undo_stack.append(command)
                self.redo_stack.clear()
                # Keep reference for shape tools that can be moved
                if isinstance(tool, ShapeTool):
                    self.current_tool = tool
                else:
                    self.current_tool = None
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
        # Confirm any active shape before undoing
        self.confirm_current_shape()
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo(self.canvas)
            self.redo_stack.append(command)

    def redo(self):
        # Confirm any active shape before redoing
        self.confirm_current_shape()
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.redo(self.canvas)
            self.undo_stack.append(command)
