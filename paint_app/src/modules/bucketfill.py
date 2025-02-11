from kivy.graphics import Color, Fbo, ClearColor, ClearBuffers, Rectangle
from .abstract_tool import AbstractTool
import numpy as np
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
import scipy.ndimage  # Make sure to import scipy.ndimage

class FillTool(AbstractTool):
    name = 'bucket_fill'

    def __init__(self, canvas, color, line_width, tolerance=0, canvas_widget=None):
        super(FillTool, self).__init__(canvas, color, line_width)
        self.tolerance = tolerance          # Tolerance level
        self.active = False                 # Whether the tool is active
        self.image_data = None              # The image data as a numpy array
        self.texture = None                 # The texture used for drawing
        self.undo_stack = []                # Stack for undo functionality
        self.redo_stack = []                # Stack for redo functionality
        self.canvas_widget = canvas_widget  # Reference to the canvas widget

    def activate(self):
        self.active = True
        # Load the image data if not already loaded
        if self.image_data is None:
            self.capture_canvas()

    def deactivate(self):
        self.active = False

    def capture_canvas(self):
        # Capture the canvas as an image and store the pixel data
        img = self.canvas_widget.export_as_image()
        width, height = img.texture.size
        pixels = img.texture.pixels
        pixel_data = np.frombuffer(pixels, dtype=np.uint8)
        pixel_data = pixel_data.reshape(height, width, 4).copy()  # Make writable
        self.image_data = pixel_data
        self.texture = img.texture

    def on_touch_down(self, x, y):
        if not self.active:
            return super(FillTool, self).on_touch_down(x, y)
        
        # Check if touch is within the canvas bounds
        if not self.canvas_widget.collide_point(x, y):
            return False

        # Get the touch position relative to the canvas
        x -= self.canvas_widget.pos[0]
        y -= self.canvas_widget.pos[1]

        # Convert to integer coordinates
        x = int(x)
        y = int(y)

        # Adjust y coordinate because image origin is at top-left
        y = self.image_data.shape[0] - y - 1

        # Perform the fill operation
        self.fill(x, y)
        return True

    def on_touch_move(self, x, y):
        # FillTool does not handle touch move
        pass

    def on_touch_up(self, x, y):
        # FillTool does not handle touch up
        pass

    def fill(self, x, y):
        # Ensure image data is available
        if self.image_data is None:
            self.capture_canvas()

        pixel_data = self.image_data
        height, width, _ = pixel_data.shape

        # Check if (x, y) is within bounds
        if x < 0 or x >= width or y < 0 or y >= height:
            return

        # Get the target color at the clicked position
        target_color = pixel_data[y, x][:3]

        # Get the fill color from the tool's color property
        fill_color = np.array([int(c * 255) for c in self.color[:3]], dtype=np.uint8)

        # If the target color is the same as fill color, do nothing
        if np.array_equal(target_color, fill_color):
            return

        # Save the current image data for undo
        previous_image_data = pixel_data.copy()
        self.undo_stack.append(previous_image_data)
        # Clear the redo stack
        self.redo_stack.clear()

        # Perform the flood fill using optimized method
        self.flood_fill(pixel_data, x, y, target_color, fill_color, self.tolerance)

        # Update the texture with the modified image data
        new_pixels = pixel_data.tobytes()
        self.texture.blit_buffer(new_pixels, colorfmt='rgba', bufferfmt='ubyte')
        self.texture.flip_vertical()  # Ensure correct orientation after blit

        # Update the canvas with the new texture
        self.canvas_widget.canvas.clear()
        with self.canvas_widget.canvas:
            Rectangle(texture=self.texture, pos=self.canvas_widget.pos, size=self.canvas_widget.size)
        
        # Deactivate the FillTool after filling
        self.deactivate()

    def flood_fill(self, pixel_data, x, y, target_color, fill_color, tolerance):
        height, width, _ = pixel_data.shape
        # Create a boolean mask where pixels match the target color within the given tolerance
        mask = np.all(np.abs(pixel_data[:, :, :3].astype(int) - target_color.astype(int)) <= tolerance, axis=2)

        # Use scipy.ndimage.label to label connected regions in the mask
        structure = np.array([[0,1,0],[1,1,1],[0,1,0]], dtype=bool)  # 4-connectivity
        labeled, num_features = scipy.ndimage.label(mask, structure=structure)

        # Get the label of the region containing the starting point
        target_label = labeled[y, x]
        if target_label == 0:
            return  # The starting point is not in any connected region

        # Create a mask for the region to fill
        region_mask = (labeled == target_label)

        # Fill the region
        pixel_data[region_mask, :3] = fill_color

    def undo(self):
        if self.undo_stack:
            # Save current state for redo
            self.redo_stack.append(self.image_data.copy())
            # Restore previous state
            self.image_data = self.undo_stack.pop()
            # Update the texture
            new_pixels = self.image_data.tobytes()
            self.texture.blit_buffer(new_pixels, colorfmt='rgba', bufferfmt='ubyte')
            # Redraw the canvas
            with self.canvas_widget.canvas:
                self.canvas_widget.canvas.clear()
                Rectangle(texture=self.texture, pos=self.canvas_widget.pos, size=self.canvas_widget.size)

    def redo(self):
        if self.redo_stack:
            # Save current state for undo
            self.undo_stack.append(self.image_data.copy())
            # Restore next state
            self.image_data = self.redo_stack.pop()
            # Update the texture
            new_pixels = self.image_data.tobytes()
            self.texture.blit_buffer(new_pixels, colorfmt='rgba', bufferfmt='ubyte')
            # Redraw the canvas
            with self.canvas_widget.canvas:
                self.canvas_widget.canvas.clear()
                Rectangle(texture=self.texture, pos=self.canvas_widget.pos, size=self.canvas_widget.size)
