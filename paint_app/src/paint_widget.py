from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Bezier, Rectangle  # Add Rectangle to imports
from kivy.properties import ColorProperty, NumericProperty, ObjectProperty
from collections import deque
from kivy.core.window import Window
from tools import ToolManager, Tool, BrushStyle, ShapeTool
from modules.bucketfill import FillTool  # Add this import
from kivy.core.image import Image as CoreImage  # Ensure CoreImage is imported
from kivy.graphics.texture import Texture  # Add this import
from PIL import Image  # Add this import
import io  # Add this import

class DrawCommand:
    def __init__(self, canvas_instructions):
        # Store instructions as a list even if a single instruction is passed
        self.instructions = canvas_instructions if isinstance(canvas_instructions, list) else [canvas_instructions]

    def undo(self, canvas):
        # Remove instructions in reverse order to handle Color instructions properly
        for instr in reversed(self.instructions):
            try:
                canvas.remove(instr)
            except ValueError:
                # Skip if instruction is already removed
                pass

    def redo(self, canvas):
        # Add instructions in original order
        for instr in self.instructions:
            canvas.add(instr)

class ImageLoadCommand:
    """Command for loading images with undo/redo support"""
    def __init__(self, widget, old_instructions, new_instructions, old_size, new_size, texture=None):
        print(f"Creating ImageLoadCommand:")
        print(f"- Old size: {old_size}")
        print(f"- New size: {new_size}")
        print(f"- Old instructions count: {len(old_instructions) if old_instructions else 0}")
        print(f"- New instructions count: {len(new_instructions) if new_instructions else 0}")
        
        self.widget = widget
        # Create deep copies of instructions
        self.old_instructions = old_instructions[:]  # Use slice to create a copy
        self.new_instructions = []
        # Create new instructions with new Color and Rectangle objects
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=widget.pos, size=new_size)
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, pos=widget.pos, size=new_size)
            self.new_instructions = widget.canvas.children[:]
        
        self.old_size = tuple(old_size)
        self.new_size = tuple(new_size)
        self.texture = texture

    def undo(self, canvas):
        print(f"Undoing image load:")
        print(f"- Restoring size: {self.old_size}")
        print(f"- Restoring {len(self.old_instructions)} instructions")
        
        # Clear and restore old state
        canvas.clear()
        self.widget.size = self.old_size
        for instr in self.old_instructions:
            try:
                canvas.add(instr)
            except Exception as e:
                print(f"Error restoring instruction: {e}")

    def redo(self, canvas):
        print(f"Redoing image load:")
        print(f"- Setting size: {self.new_size}")
        print(f"- Has texture: {self.texture is not None}")
        
        # Clear and restore new state
        canvas.clear()
        self.widget.size = self.new_size
        for instr in self.new_instructions:
            try:
                canvas.add(instr)
            except Exception as e:
                print(f"Error restoring instruction: {e}")

# This is the main canvas widget where drawing occurs. It handles touch/mouse input,
# manages the undo/redo system, and coordinates with the active drawing tools.
class PaintWidget(Widget):
    current_color = ColorProperty([0, 0, 0, 1])  # Changed from [1, 1, 1, 1] to [0, 0, 0, 1] for black
    line_width = NumericProperty(2)
    tool_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tool_manager = ToolManager()
        self.undo_stack = deque(maxlen=50)  # Limit stack size to prevent memory issues
        self.redo_stack = deque(maxlen=50)
        self.points = []  # Initialize points list
        self.current_instructions = None
        self.current_tool = None  # Add this to maintain tool reference

    def set_color(self, color):
        self.current_color = color
        
    def set_line_width(self, width):
        self.line_width = width

    def set_tool(self, tool):
        # Confirm any active shape before switching tools
        self.confirm_current_shape()
        # Deactivate the current tool if it has a deactivate method
        if self.current_tool and hasattr(self.current_tool, 'deactivate'):
            self.current_tool.deactivate()
        self.tool_manager.set_tool(tool)

    def confirm_current_shape(self):
        """Confirm the current shape and clean up"""
        if isinstance(self.current_tool, ShapeTool) and self.current_tool.shape:
            try:
                # Save the current shape to undo stack
                command = DrawCommand([self.current_tool.shape])
                self.undo_stack.append(command)
                self.redo_stack.clear()
                # Clean up
                self.current_tool.active = False
                if self.current_tool.handles in self.canvas.children:
                    self.canvas.remove(self.current_tool.handles)
                self.current_tool = None
            except Exception as e:
                print(f"Error confirming shape: {e}")
                # Ensure cleanup even if there's an error
                self.current_tool = None

    def on_touch_down(self, touch):
        # If clicking in the menu bar area, confirm any active shape first
        if touch.y > self.height - 0:  # Only menu bar height
            self.confirm_current_shape()  # Always confirm shape when clicking menu
            return False

        if self.collide_point(*touch.pos):
            # First check if we have an active shape tool that's being edited
            if isinstance(self.current_tool, ShapeTool) and self.current_tool.shape:
                # Click outside shape area finalizes it
                if not self.current_tool.contains_point(touch.x, touch.y):
                    self.confirm_current_shape()
                    return True
                # Click inside continues editing
                instructions = self.current_tool.on_touch_down(touch.x, touch.y)
                self.current_instructions = instructions
                return True

            # Create new tool instance if no active tool
            self.current_tool = self.tool_manager.create_tool(
                self.canvas, 
                self.current_color, 
                self.line_width,
                canvas_widget=self  # Pass the PaintWidget instance
            )
            
            # Activate the tool if it's FillTool
            if isinstance(self.current_tool, FillTool):
                self.current_tool.activate()

            touch.ud['tool'] = self.current_tool
            self.points = [touch.x, touch.y]  # Initialize points on touch down
            instructions = self.current_tool.on_touch_down(touch.x, touch.y)
            self.current_instructions = instructions
        else:
            # If clicking outside the widget entirely, confirm any active shape
            self.confirm_current_shape()

    def on_touch_move(self, touch):
        # Prevent drawing in the menu bar area only
        if touch.y > self.height - 0:  # Only menu bar height
            return False

        if self.collide_point(*touch.pos):
            if 'tool' in touch.ud:
                touch.ud['tool'].on_touch_move(touch.x, touch.y)
                self.points.extend([touch.x, touch.y])  # Collect points during touch move
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
        
        if len(self.points) < 4:
            return self.points
        
        smooth_points = []
        smooth_points.extend(self.points[:2])  # Add first point
        
        # Create smooth curve through points
        for i in range(2, len(self.points) - 2, 2):
            x0, y0 = self.points[i - 2], self.points[i - 1]  # Previous point
            x1, y1 = self.points[i], self.points[i + 1]      # Current point
            x2, y2 = self.points[i + 2], self.points[i + 3]  # Next point
            
            # Calculate control points for Bézier curve
            cp1x = x0 + (x1 - x0) * 0.5
            cp1y = y0 + (y1 - y0) * 0.5
            cp2x = x1 + (x2 - x1) * 0.5
            cp2y = y1 + (y2 - y1) * 0.5
            
            # Add points for smooth curve
            smooth_points.extend([cp1x, cp1y, x1, y1, cp2x, cp2y])
        
        smooth_points.extend(self.points[-2:])  # Add last point
        self.points = []  # Clear points after processing
        return smooth_points

    def undo(self):
        print("\nExecuting undo:")
        print(f"- Undo stack size: {len(self.undo_stack)}")
        print(f"- Redo stack size: {len(self.redo_stack)}")
        
        self.confirm_current_shape()
        if self.undo_stack:
            command = self.undo_stack.pop()
            print(f"- Command type: {type(command).__name__}")
            command.undo(self.canvas)
            self.redo_stack.append(command)
            print("Undo completed")
        else:
            print("No actions to undo")

    def redo(self):
        print("\nExecuting redo:")
        print(f"- Undo stack size: {len(self.undo_stack)}")
        print(f"- Redo stack size: {len(self.redo_stack)}")
        
        self.confirm_current_shape()
        if self.redo_stack:
            command = self.redo_stack.pop()
            print(f"- Command type: {type(command).__name__}")
            command.redo(self.canvas)
            self.undo_stack.append(command)
            print("Redo completed")
        else:
            print("No actions to redo")

    def has_unsaved_changes(self):
        """Check if there are any unsaved changes"""
        return len(self.undo_stack) > 0
    
    def clear_canvas(self):
        """Clear the canvas and reset drawing history"""
        # First store the background color and rectangle
        with self.canvas:
            bg_color = Color(1, 1, 1, 1)  # White background
            bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        # Clear everything
        self.canvas.clear()
        
        # Restore the background
        with self.canvas:
            self.canvas.add(bg_color)
            self.canvas.add(bg_rect)
        
        # Reset all state
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.points = []
        self.current_instructions = None
        
        # Properly cleanup any active tool
        if self.current_tool and hasattr(self.current_tool, 'deactivate'):
            self.current_tool.deactivate()
        self.current_tool = None
        
        # Reset to default state
        self.current_color = [0, 0, 0, 1]
        self.line_width = 2

    def export_as_image(self):
        """Capture the current canvas state as an image"""
        # Use the parent class method to get the image
        return super().export_as_image()
    
    def clear_unsaved_changes(self):
        """Clear the unsaved changes flag after successful save"""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def load_image(self, filepath):
        """Load an image from a file and display it on the canvas."""
        try:
            print(f"\nLoading image: {filepath}")
            
            # Store current canvas state
            old_size = list(self.size)
            old_instructions = self.canvas.children[:]
            print(f"Current canvas state:")
            print(f"- Size: {old_size}")
            print(f"- Instructions count: {len(old_instructions)}")
            
            # Load and process image
            with open(filepath, 'rb') as f:
                data = f.read()
            pil_image = Image.open(io.BytesIO(data)).convert('RGBA')
            image_data = pil_image.tobytes()
            
            # Create texture
            texture = Texture.create(size=pil_image.size, colorfmt='rgba', bufferfmt='ubyte')
            texture.blit_buffer(image_data, colorfmt='rgba', bufferfmt='ubyte')
            
            print(f"Image processed:")
            print(f"- Image size: {pil_image.size}")
            print(f"- Texture created: {texture.size}")
            
            # Update widget size to match image
            self.size = pil_image.size
            
            # Clear canvas and draw new image
            self.canvas.clear()
            with self.canvas:
                # Draw white background
                Color(1, 1, 1, 1)
                Rectangle(pos=self.pos, size=self.size)
                # Draw the image
                Color(1, 1, 1, 1)  # Reset color to white
                Rectangle(texture=texture, pos=self.pos, size=self.size)
            
            # Create and add command to undo stack
            command = ImageLoadCommand(
                self,
                old_instructions,
                self.canvas.children[:],  # Current instructions after loading
                old_size,
                pil_image.size,
                texture
            )
            
            print(f"Adding command to undo stack")
            print(f"- Undo stack size before: {len(self.undo_stack)}")
            self.undo_stack.append(command)
            self.redo_stack.clear()
            print(f"- Undo stack size after: {len(self.undo_stack)}")
            
            return True
            
        except Exception as e:
            print(f"Error in load_image: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def clear_undo_history(self):
        """Clear the undo and redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()
