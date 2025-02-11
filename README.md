# Paint for macOS

An open-source, Microsoft Paint-like application built with Python and Kivy, specifically designed for macOS.

## Features

- **Free-hand Drawing**: Draw freely with adjustable brush sizes and smoothing options.
- **Multiple Tools**:
  - Pencil and Brush with different styles.
  - Eraser to correct mistakes.
  - Line, Rectangle, and Circle tools with resize and move capabilities.
  - Fill Tool (Paint Bucket) for filling areas with color.
- **Shape Manipulation**: Shape tools with handles for easy manipulation.
- **Color Selection**:
  - Basic color palette.
  - Custom color picker for selecting any color.
- **Brush Styles**: Different brush styles including round and square brushes.
- **Undo/Redo Functionality**: Support for undo and redo actions using Command+Z and Command+Shift+Z.
- **Modern Interface**: A macOS-style interface with dark theme support.
- **Menu System**: Dropdown menus for easy navigation.
- **Canvas Operations**:
  - Clear canvas functionality.
  - New canvas creation with unsaved changes warning.
- **File Operations**:
  - Save functionality supporting multiple formats: PNG, JPEG, BMP, TIFF, and PDF.
  - Open existing images to edit.
  - Export functionality.
- **Keyboard Shortcuts**: Quick access to tools and functions through keyboard shortcuts.
- **MacOS-style Dialogs**: Native macOS save dialogs with icons and animations.

## Requirements

- **macOS**: Version 10.14 or higher.
- **Python**: Version 3.7 or higher.
- **Kivy**: Version 2.2.0 or higher.
- **NumPy**: Version 2.0.2 or higher.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ludovici96/Paint-for-MacOS.git
   ```

2. **Navigate to the project directory**:
  ```bash
  cd paint-for-macos
  ```

3. **Create a virtual environment (optional but recommended)**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

4. **Install the required packages**:
  ```bash
  pip install -r requirements.txt
  ```

5. **To run the program**:
  ```bash
  python3 src/main.py
  ```

**Future Plans:**

* **Layers Support**
  - Implementing layers for complex editing
  - Layer opacity control
  - Layer blending modes
  - Layer reordering

* **Selection Tool** 
  - Adding the ability to select and manipulate parts of the canvas
  - Rectangle selection
  - Lasso selection
  - Magic wand tool
  
* **Text Tool**
  - Enabling the insertion and styling of text
  - Font selection
  - Text formatting options
  - Text layer editing

* **Zoom Functionality**
  - Allowing users to zoom in and out for detailed work
  - Zoom slider control
  - Zoom to fit
  - Pan tool for navigation

* **Canvas Resize Option**
  - Providing options to resize the canvas
  - Maintain aspect ratio option
  - Custom dimensions input
  - Scale content options

* **Image Filters and Effects**
  - Introducing basic filters and effects to enhance images
  - Brightness/Contrast adjustments
  - Color balance
  - Blur/Sharpen effects
  - Basic artistic filters
