# This file handles the tool management system, including tool creation and switching
# between different drawing tools. It acts as a factory for creating specific tool instances.

from kivy.graphics import Color, Line, Rectangle
from modules.abstract_tool import Tool, BrushStyle, AbstractTool
from modules.shapetool import ShapeTool
from modules.bucketfill import FillTool
from modules.brushtool import BrushTool
from modules.penciltool import PencilTool
from modules.erasertool import EraserTool
from modules.circletool import CircleTool
from modules.rectangletool import RectangleTool
from modules.linetool import LineTool

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

    def create_tool(self, canvas, color, line_width, canvas_widget=None):
        if self.current_tool == Tool.PENCIL:
            return PencilTool(canvas, color, line_width)
        elif self.current_tool == Tool.BRUSH:
            return BrushTool(canvas, color, line_width)
        elif self.current_tool == Tool.ERASER:
            return EraserTool(canvas, color, line_width)
        elif self.current_tool == Tool.LINE:
            return LineTool(canvas, color, line_width)
        elif self.current_tool == Tool.RECTANGLE:
            return RectangleTool(canvas, color, line_width)
        elif self.current_tool == Tool.CIRCLE:
            return CircleTool(canvas, color, line_width)
        elif self.current_tool == Tool.FILL:
            tool = FillTool(canvas, color, line_width, canvas_widget=canvas_widget)
            tool.activate()  # Activate FillTool upon creation
            return tool
        else:
            raise ValueError("Tool not implemented")

    def set_brush_style(self, style):
        if isinstance(style, BrushStyle):
            self.brush_style = style