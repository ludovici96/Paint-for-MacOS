from enum import Enum, auto
from abc import ABC, abstractmethod
from kivy.graphics import Color, Line, Ellipse, Rectangle

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
        else:
            raise ValueError("Tool not implemented")

    def set_brush_style(self, style):
        if isinstance(style, BrushStyle):
            self.brush_style = style