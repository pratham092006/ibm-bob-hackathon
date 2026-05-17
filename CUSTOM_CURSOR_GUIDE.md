# Custom SVG Cursor Implementation Guide

## Overview

The Axon application now uses a custom SVG-based pointing hand cursor for the AI overlay. This provides a more professional and recognizable cursor that clearly indicates AI actions.

## Implementation Details

### Files Modified

1. **`ui/reticle.py`**
   - Added SVG rendering support using `QSvgRenderer`
   - Modified `_draw_hand_cursor()` to render the SVG instead of drawing polygons
   - Added fallback to simple circle if SVG fails to load
   - SVG is loaded from `pointinghand.svg` in the project root

2. **`requirements.txt`**
   - Added `PyQt6-SVG>=6.6.0` dependency for SVG rendering support

### SVG File

- **Location**: `ibm-bob-hackathon/axon/pointinghand.svg`
- **Size**: 32x32 pixels (viewBox)
- **Format**: Standard SVG with white fill and black stroke
- **Hotspot**: Positioned at the tip of the pointing finger (approximately 16, 8)

## How It Works

1. **Initialization**: When the `Reticle` class is instantiated, it loads the SVG file using `QSvgRenderer`
2. **Rendering**: The `_draw_hand_cursor()` method renders the SVG at the cursor position
3. **Positioning**: The cursor is offset so the finger tip appears at the target coordinates
4. **Fallback**: If SVG loading fails, a simple circle is drawn instead

## Installation

To use the custom cursor, ensure PyQt6-SVG is installed:

```bash
pip install PyQt6-SVG>=6.6.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Testing

A test script is provided to verify the cursor implementation:

```bash
cd ibm-bob-hackathon/axon
python test_svg_cursor.py
```

The test will:
- Create an overlay with the SVG cursor
- Position it at screen center
- Show a control window with instructions
- Allow you to verify the cursor follows your mouse with an offset

## Customization

### Changing the Cursor Size

Edit `ui/reticle.py`, line ~60:

```python
cursor_size = 32  # Change this value to scale the cursor
```

### Changing the Hotspot

Edit `ui/reticle.py`, lines ~63-64:

```python
offset_x = 16  # Horizontal offset from cursor position
offset_y = 8   # Vertical offset from cursor position
```

### Using a Different SVG

1. Replace `pointinghand.svg` with your custom SVG file
2. Ensure the SVG has a clear viewBox definition
3. Adjust the hotspot offsets if needed

## Troubleshooting

### Cursor Shows as Circle Instead of Hand

**Cause**: SVG file not loaded correctly

**Solutions**:
1. Verify `pointinghand.svg` exists in the correct location
2. Check console for error messages about SVG loading
3. Ensure PyQt6-SVG is installed: `pip install PyQt6-SVG`
4. Verify the SVG file is valid (open in browser or SVG editor)

### Cursor Position is Off

**Cause**: Hotspot offsets need adjustment

**Solution**: Adjust `offset_x` and `offset_y` values in `ui/reticle.py`

### SVG Appears Distorted

**Cause**: Aspect ratio or size issues

**Solution**: 
1. Check the SVG viewBox matches the actual content
2. Adjust `cursor_size` to match your SVG dimensions
3. Ensure the SVG uses proper coordinate system

## Integration with Main Application

The custom cursor is automatically used when running the main Axon application:

```bash
python main.py
```

The cursor will:
- Appear when a task is started
- Follow the mouse with an offset
- Display coordinates near the cursor
- Change appearance based on action state (clicking, moving, etc.)

## Technical Notes

- **Performance**: SVG rendering is efficient and doesn't impact performance
- **Transparency**: The cursor supports transparency from the SVG
- **Antialiasing**: Enabled for smooth rendering
- **Thread Safety**: All rendering happens on the Qt main thread

## Future Enhancements

Possible improvements:
- Add cursor state variations (different SVGs for clicking, moving, etc.)
- Implement cursor animation (e.g., finger tap on click)
- Add color customization options
- Support for multiple cursor themes