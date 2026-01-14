## Tool: "mobile_dev" - Mobile Application Development

Use this tool to create and develop mobile applications for iOS and Android.

### Supported Frameworks:
- **expo** (default) - Easiest React Native development
- **react-native** - Full React Native with native modules
- **flutter** - Google's cross-platform framework

### Actions:

#### create - Create a new mobile app
```json
{
    "thoughts": ["Creating a new mobile app project..."],
    "tool_name": "mobile_dev",
    "tool_args": {
        "action": "create",
        "framework": "expo",
        "app_name": "MyAwesomeApp",
        "features": "authentication, navigation, dark mode"
    }
}
```

#### add_screen - Add a new screen/page
```json
{
    "thoughts": ["Adding a new screen to the app..."],
    "tool_name": "mobile_dev",
    "tool_args": {
        "action": "add_screen",
        "framework": "expo",
        "app_name": "MyApp",
        "screen_name": "Profile",
        "description": "User profile with avatar and settings"
    }
}
```

#### add_component - Add a reusable component
```json
{
    "thoughts": ["Creating a reusable button component..."],
    "tool_name": "mobile_dev",
    "tool_args": {
        "action": "add_component",
        "framework": "expo",
        "app_name": "MyApp",
        "component_name": "PrimaryButton",
        "component_type": "button"
    }
}
```

#### build - Build for production
```json
{
    "thoughts": ["Building the app for release..."],
    "tool_name": "mobile_dev",
    "tool_args": {
        "action": "build",
        "framework": "expo",
        "app_name": "MyApp",
        "platform": "all"
    }
}
```

#### info - Get framework information
```json
{
    "thoughts": ["Getting information about Flutter..."],
    "tool_name": "mobile_dev",
    "tool_args": {
        "action": "info",
        "framework": "flutter"
    }
}
```

### Best Practices:
1. Start with `create` to scaffold the project
2. Use `add_screen` for each major view
3. Use `add_component` for reusable UI elements
4. Use code_execution_tool to run the generated commands
5. Use `build` when ready for production
