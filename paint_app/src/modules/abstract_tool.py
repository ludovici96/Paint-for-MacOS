# This file defines the base abstractions for all drawing tools and tool-related enums.
# It provides the interface that all concrete tools must implement.
from abc import ABC, abstractmethod
from enum import Enum, auto

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