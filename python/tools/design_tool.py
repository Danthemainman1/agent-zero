"""
Interactive Design and Image Manipulation Tool.
Provides visual editing capabilities with coordinate-based operations.
"""

import os
import base64
import json
from pathlib import Path
from python.helpers.tool import Tool, Response
from python.helpers import files


class DesignTool(Tool):
    """
    Interactive design and image manipulation tool.
    Supports analysis, editing, annotation, and generation of visual content.
    """

    async def execute(self,
                     action: str = "",
                     image_path: str = "",
                     **kwargs) -> Response:
        """
        Execute design operations.
        
        Actions:
        - analyze: Analyze an image and describe its contents
        - annotate: Add annotations/markup to an image
        - generate_mockup: Generate UI mockup from description
        - create_wireframe: Create wireframe from description
        - export_assets: Export design assets
        - color_palette: Extract or generate color palettes
        """
        
        if not action:
            return Response(
                message="Error: No action specified. Available: analyze, annotate, generate_mockup, create_wireframe, export_assets, color_palette",
                break_loop=False
            )

        if action == "analyze":
            return await self._analyze_image(image_path, **kwargs)
        elif action == "annotate":
            return await self._annotate_image(image_path, **kwargs)
        elif action == "generate_mockup":
            return await self._generate_mockup(**kwargs)
        elif action == "create_wireframe":
            return await self._create_wireframe(**kwargs)
        elif action == "export_assets":
            return await self._export_assets(**kwargs)
        elif action == "color_palette":
            return await self._color_palette(**kwargs)
        else:
            return Response(
                message=f"Error: Unknown action '{action}'",
                break_loop=False
            )

    async def _analyze_image(self, image_path: str, **kwargs) -> Response:
        """Analyze an image and describe its contents."""
        if not image_path:
            return Response(
                message="Error: image_path is required for analyze action",
                break_loop=False
            )

        # Check if the image exists
        abs_path = files.get_abs_path(image_path)
        if not os.path.exists(abs_path):
            return Response(
                message=f"Error: Image not found at {image_path}",
                break_loop=False
            )

        response = f"""## Image Analysis: {os.path.basename(image_path)}

### File Info:
- **Path:** {image_path}
- **Size:** {os.path.getsize(abs_path)} bytes

### Analysis:
To perform detailed visual analysis, use the vision capabilities by:
1. Loading this image as an attachment in your message
2. Using the browser_agent to view and analyze web content
3. Using code_execution_tool with PIL/Pillow for programmatic analysis

### Quick Analysis Script:
```python
from PIL import Image
import os

img = Image.open("{abs_path}")
print(f"Format: {{img.format}}")
print(f"Size: {{img.size}}")
print(f"Mode: {{img.mode}}")

# Get dominant colors
if img.mode != 'RGB':
    img = img.convert('RGB')
colors = img.getcolors(maxcolors=100000)
if colors:
    sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:5]
    print("Top colors:", sorted_colors)
```

Use code_execution_tool with runtime="python" to run this analysis.
"""
        return Response(message=response, break_loop=False)

    async def _annotate_image(self, image_path: str, 
                              annotations: list = None,
                              output_path: str = "", **kwargs) -> Response:
        """Add annotations to an image."""
        if not image_path:
            return Response(
                message="Error: image_path is required for annotate action",
                break_loop=False
            )

        annotations = annotations or []
        output_path = output_path or image_path.replace(".", "_annotated.")

        response = f"""## Image Annotation

### Source: {image_path}
### Output: {output_path}

### Annotation Script:
```python
from PIL import Image, ImageDraw, ImageFont

# Load image
img = Image.open("{image_path}")
draw = ImageDraw.Draw(img)

# Annotations to apply:
annotations = {json.dumps(annotations, indent=2)}

for ann in annotations:
    ann_type = ann.get('type', 'text')
    
    if ann_type == 'text':
        x, y = ann.get('x', 0), ann.get('y', 0)
        text = ann.get('text', '')
        color = ann.get('color', 'red')
        draw.text((x, y), text, fill=color)
    
    elif ann_type == 'rectangle':
        x1, y1 = ann.get('x1', 0), ann.get('y1', 0)
        x2, y2 = ann.get('x2', 100), ann.get('y2', 100)
        color = ann.get('color', 'red')
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
    
    elif ann_type == 'circle':
        cx, cy = ann.get('cx', 50), ann.get('cy', 50)
        r = ann.get('r', 25)
        color = ann.get('color', 'red')
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=2)
    
    elif ann_type == 'arrow':
        x1, y1 = ann.get('x1', 0), ann.get('y1', 0)
        x2, y2 = ann.get('x2', 100), ann.get('y2', 100)
        color = ann.get('color', 'red')
        draw.line([x1, y1, x2, y2], fill=color, width=2)

# Save annotated image
img.save("{output_path}")
print(f"Annotated image saved to {output_path}")
```

### Annotation Format:
```json
[
    {{"type": "text", "x": 10, "y": 10, "text": "Label", "color": "red"}},
    {{"type": "rectangle", "x1": 50, "y1": 50, "x2": 150, "y2": 100, "color": "blue"}},
    {{"type": "circle", "cx": 200, "cy": 200, "r": 30, "color": "green"}},
    {{"type": "arrow", "x1": 0, "y1": 0, "x2": 100, "y2": 100, "color": "yellow"}}
]
```

Use code_execution_tool with runtime="python" to apply annotations.
"""
        return Response(message=response, break_loop=False)

    async def _generate_mockup(self, description: str = "", 
                               style: str = "modern",
                               width: int = 375,
                               height: int = 812, **kwargs) -> Response:
        """Generate a UI mockup from description."""
        if not description:
            return Response(
                message="Error: description is required for generate_mockup action",
                break_loop=False
            )

        response = f"""## UI Mockup Generation

### Description: {description}
### Style: {style}
### Dimensions: {width}x{height}

### HTML/CSS Mockup:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mockup - {description[:30]}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .device-frame {{
            width: {width}px;
            height: {height}px;
            background: white;
            border-radius: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
            position: relative;
        }}
        
        .status-bar {{
            height: 44px;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14px;
        }}
        
        .content {{
            padding: 20px;
            height: calc(100% - 44px);
            overflow-y: auto;
        }}
        
        .header {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }}
        
        .button {{
            background: #007AFF;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="device-frame">
        <div class="status-bar">9:41</div>
        <div class="content">
            <h1 class="header">Mockup Preview</h1>
            <p style="color: #666; margin-bottom: 20px;">{description}</p>
            
            <div class="card">
                <h3 style="margin-bottom: 8px;">Feature 1</h3>
                <p style="color: #666; font-size: 14px;">Description of the first feature</p>
            </div>
            
            <div class="card">
                <h3 style="margin-bottom: 8px;">Feature 2</h3>
                <p style="color: #666; font-size: 14px;">Description of the second feature</p>
            </div>
            
            <button class="button">Get Started</button>
        </div>
    </div>
</body>
</html>
```

### To Preview:
1. Save this HTML to a file
2. Open in browser
3. Take a screenshot for the final mockup

### For Higher Fidelity:
- Use Figma, Sketch, or Adobe XD
- Use browser_agent to interact with design tools
- Use the orchestrate tool to generate multiple variants in parallel
"""
        return Response(message=response, break_loop=False)

    async def _create_wireframe(self, description: str = "",
                                screens: list = None, **kwargs) -> Response:
        """Create wireframe from description."""
        if not description:
            return Response(
                message="Error: description is required for create_wireframe action",
                break_loop=False
            )

        screens = screens or ["Home", "Detail", "Profile"]

        response = f"""## Wireframe Generation

### Description: {description}
### Screens: {', '.join(screens)}

### ASCII Wireframes:

"""
        for screen in screens:
            response += f"""
#### {screen} Screen:
```
┌─────────────────────────────┐
│  ← {screen:^21} ⋮  │ Header
├─────────────────────────────┤
│                             │
│  ┌───────────────────────┐  │
│  │     Hero Section      │  │
│  │                       │  │
│  └───────────────────────┘  │
│                             │
│  ┌──────┐ ┌──────┐ ┌──────┐ │
│  │ Card │ │ Card │ │ Card │ │ Content
│  └──────┘ └──────┘ └──────┘ │
│                             │
│  ┌───────────────────────┐  │
│  │    Content Block      │  │
│  │    ───────────────    │  │
│  │    ───────────────    │  │
│  └───────────────────────┘  │
│                             │
├─────────────────────────────┤
│   🏠    🔍    ➕    👤    ⚙️   │ Tab Bar
└─────────────────────────────┘
```
"""

        response += """
### Convert to High-Fidelity:
1. Use `generate_mockup` to create styled versions
2. Use design tools (Figma, Sketch) for final designs
3. Use `mobile_dev` to implement the screens

### Export Options:
- Save ASCII to markdown for documentation
- Use HTML/CSS mockup for interactive preview
- Export to design tool format
"""
        return Response(message=response, break_loop=False)

    async def _export_assets(self, source_path: str = "",
                             output_dir: str = "assets",
                             formats: list = None, **kwargs) -> Response:
        """Export design assets in multiple formats and sizes."""
        formats = formats or ["png", "svg"]

        response = f"""## Asset Export

### Source: {source_path or 'Not specified'}
### Output Directory: {output_dir}
### Formats: {', '.join(formats)}

### Export Script:
```python
from PIL import Image
import os

def export_assets(source_path, output_dir, sizes):
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(source_path)
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    
    # Standard mobile asset sizes
    sizes = {{
        '1x': 1.0,
        '2x': 2.0,
        '3x': 3.0,
    }}
    
    for suffix, scale in sizes.items():
        new_size = (int(img.width * scale), int(img.height * scale))
        resized = img.resize(new_size, Image.LANCZOS)
        output_path = os.path.join(output_dir, f"{{base_name}}@{{suffix}}.png")
        resized.save(output_path)
        print(f"Exported: {{output_path}}")

# For iOS:
# icon-20@2x.png (40x40)
# icon-20@3x.png (60x60)
# icon-29@2x.png (58x58)
# etc.

# For Android:
# mdpi: 1x
# hdpi: 1.5x
# xhdpi: 2x
# xxhdpi: 3x
# xxxhdpi: 4x
```

### Standard Icon Sizes:

#### iOS App Icons:
| Size | Usage |
|------|-------|
| 20pt | Notification |
| 29pt | Settings |
| 40pt | Spotlight |
| 60pt | App Icon |
| 76pt | iPad App |
| 83.5pt | iPad Pro |
| 1024pt | App Store |

#### Android Icons:
| Density | Scale | 48dp → |
|---------|-------|--------|
| mdpi | 1x | 48px |
| hdpi | 1.5x | 72px |
| xhdpi | 2x | 96px |
| xxhdpi | 3x | 144px |
| xxxhdpi | 4x | 192px |
"""
        return Response(message=response, break_loop=False)

    async def _color_palette(self, action_type: str = "generate",
                             colors: list = None,
                             base_color: str = "",
                             harmony: str = "complementary", **kwargs) -> Response:
        """Generate or extract color palettes."""
        
        if action_type == "extract" and colors:
            response = f"""## Extracted Color Palette

### Colors:
{chr(10).join(f'- `{c}`' for c in colors)}
"""
        else:
            # Generate color palette based on harmony type
            harmonies = {
                "complementary": "Colors opposite on the color wheel",
                "analogous": "Colors adjacent on the color wheel",
                "triadic": "Three colors evenly spaced (120°)",
                "split-complementary": "Base + two adjacent to complement",
                "tetradic": "Four colors forming a rectangle",
                "monochromatic": "Variations of a single hue"
            }

            response = f"""## Color Palette Generator

### Harmony Type: {harmony}
{harmonies.get(harmony, '')}

### Base Color: {base_color or '#007AFF'}

### Generated Palette:
```css
:root {{
    /* Primary */
    --color-primary: {base_color or '#007AFF'};
    --color-primary-light: #4DA3FF;
    --color-primary-dark: #0055CC;
    
    /* Secondary (Complementary) */
    --color-secondary: #FF9500;
    --color-secondary-light: #FFAA33;
    --color-secondary-dark: #CC7700;
    
    /* Neutral */
    --color-background: #FFFFFF;
    --color-surface: #F5F5F7;
    --color-text: #1D1D1F;
    --color-text-secondary: #86868B;
    
    /* Semantic */
    --color-success: #34C759;
    --color-warning: #FF9500;
    --color-error: #FF3B30;
    --color-info: #5856D6;
}}
```

### Color Accessibility:
- Ensure contrast ratio ≥ 4.5:1 for normal text
- Ensure contrast ratio ≥ 3:1 for large text
- Test with color blindness simulators

### Usage in React Native:
```typescript
export const colors = {{
    primary: '{base_color or '#007AFF'}',
    secondary: '#FF9500',
    background: '#FFFFFF',
    surface: '#F5F5F7',
    text: '#1D1D1F',
    textSecondary: '#86868B',
}};
```
"""
        return Response(message=response, break_loop=False)

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://palette {self.agent.agent_name}: Design Tool",
            content="",
            kvps=self.args
        )
