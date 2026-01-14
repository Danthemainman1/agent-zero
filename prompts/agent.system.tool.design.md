## Tool: "design_tool" - Interactive Design & Visual Editing

Use this tool for design tasks, image manipulation, mockup generation, and visual asset management.

### Actions:

#### analyze - Analyze image contents
```json
{
    "thoughts": ["Analyzing the uploaded image..."],
    "tool_name": "design_tool",
    "tool_args": {
        "action": "analyze",
        "image_path": "path/to/image.png"
    }
}
```

#### annotate - Add annotations to images
```json
{
    "thoughts": ["Adding markup to highlight key areas..."],
    "tool_name": "design_tool",
    "tool_args": {
        "action": "annotate",
        "image_path": "screenshot.png",
        "annotations": [
            {"type": "rectangle", "x1": 10, "y1": 10, "x2": 100, "y2": 50, "color": "red"},
            {"type": "text", "x": 10, "y": 60, "text": "Click here", "color": "blue"}
        ],
        "output_path": "annotated_screenshot.png"
    }
}
```

#### generate_mockup - Create UI mockups
```json
{
    "thoughts": ["Generating a mobile app mockup..."],
    "tool_name": "design_tool",
    "tool_args": {
        "action": "generate_mockup",
        "description": "A fitness tracking app with workout cards and progress charts",
        "style": "modern",
        "width": 375,
        "height": 812
    }
}
```

#### create_wireframe - Create wireframes
```json
{
    "thoughts": ["Creating wireframes for the app screens..."],
    "tool_name": "design_tool",
    "tool_args": {
        "action": "create_wireframe",
        "description": "E-commerce app with product browsing",
        "screens": ["Home", "Product List", "Product Detail", "Cart", "Checkout"]
    }
}
```

#### export_assets - Export design assets
```json
{
    "thoughts": ["Exporting app icons in all required sizes..."],
    "tool_name": "design_tool",
    "tool_args": {
        "action": "export_assets",
        "source_path": "app_icon.png",
        "output_dir": "assets/icons",
        "formats": ["png"]
    }
}
```

#### color_palette - Generate color palettes
```json
{
    "thoughts": ["Creating a color scheme for the app..."],
    "tool_name": "design_tool",
    "tool_args": {
        "action": "color_palette",
        "base_color": "#6366F1",
        "harmony": "complementary"
    }
}
```

### Color Harmony Types:
- `complementary` - Opposite colors
- `analogous` - Adjacent colors
- `triadic` - Three evenly spaced colors
- `split-complementary` - Base + adjacent to complement
- `monochromatic` - Single hue variations

### Best Practices:
1. Start with wireframes to plan layout
2. Generate mockups for visual design
3. Use color_palette for consistent theming
4. Export assets in all required sizes
5. Use browser_agent for interactive design tool access
