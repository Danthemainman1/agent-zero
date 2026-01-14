"""
Mobile Application Development Tool.
Supports React Native, Expo, and Flutter frameworks.
"""

import os
import json
from python.helpers.tool import Tool, Response
from python.helpers import files


class MobileDevTool(Tool):
    """
    End-to-end mobile application development tool.
    Creates, scaffolds, and manages mobile app projects.
    """

    FRAMEWORKS = {
        "react-native": {
            "name": "React Native",
            "init_cmd": "npx react-native init {app_name}",
            "run_ios": "npx react-native run-ios",
            "run_android": "npx react-native run-android",
            "extension": ".tsx"
        },
        "expo": {
            "name": "Expo (React Native)",
            "init_cmd": "npx create-expo-app {app_name} --template blank-typescript",
            "run": "npx expo start",
            "extension": ".tsx"
        },
        "flutter": {
            "name": "Flutter",
            "init_cmd": "flutter create {app_name}",
            "run": "flutter run",
            "extension": ".dart"
        }
    }

    async def execute(self,
                     action: str = "",
                     framework: str = "expo",
                     app_name: str = "",
                     **kwargs) -> Response:
        """
        Execute mobile development actions.
        
        Actions:
        - create: Create a new mobile app project
        - add_screen: Add a new screen/page
        - add_component: Add a reusable component
        - generate_ui: Generate UI from description
        - build: Build the app for production
        - info: Get framework information
        """
        
        if not action:
            return Response(
                message="Error: No action specified. Available actions: create, add_screen, add_component, generate_ui, build, info",
                break_loop=False
            )

        framework = framework.lower()
        if framework not in self.FRAMEWORKS:
            return Response(
                message=f"Error: Unknown framework '{framework}'. Supported: {', '.join(self.FRAMEWORKS.keys())}",
                break_loop=False
            )

        if action == "create":
            return await self._create_app(framework, app_name, **kwargs)
        elif action == "add_screen":
            return await self._add_screen(framework, app_name, **kwargs)
        elif action == "add_component":
            return await self._add_component(framework, app_name, **kwargs)
        elif action == "generate_ui":
            return await self._generate_ui(framework, **kwargs)
        elif action == "build":
            return await self._build_app(framework, app_name, **kwargs)
        elif action == "info":
            return await self._get_info(framework)
        else:
            return Response(
                message=f"Error: Unknown action '{action}'",
                break_loop=False
            )

    async def _create_app(self, framework: str, app_name: str, features: str = "", **kwargs) -> Response:
        """Create a new mobile app project."""
        if not app_name:
            return Response(
                message="Error: app_name is required for create action",
                break_loop=False
            )

        # Sanitize app name
        app_name = app_name.replace(" ", "_").replace("-", "_")
        fw = self.FRAMEWORKS[framework]

        # Generate init command
        init_cmd = fw["init_cmd"].format(app_name=app_name)

        # Build response with instructions and starter code
        response = f"""## Mobile App Creation: {app_name}

### Framework: {fw['name']}

### Step 1: Create Project
Run this command to create your project:
```bash
{init_cmd}
cd {app_name}
```

### Step 2: Project Structure Created
"""

        if framework in ["react-native", "expo"]:
            response += self._get_rn_structure(app_name, features)
        elif framework == "flutter":
            response += self._get_flutter_structure(app_name, features)

        response += f"""

### Step 3: Run the App
```bash
{"npx expo start" if framework == "expo" else fw.get('run', fw.get('run_android', 'npm start'))}
```

### Next Steps:
1. Use `mobile_dev` with action="add_screen" to add new screens
2. Use `mobile_dev` with action="add_component" to add reusable components
3. Use `mobile_dev` with action="generate_ui" to generate UI from descriptions
"""

        return Response(message=response, break_loop=False)

    def _get_rn_structure(self, app_name: str, features: str) -> str:
        """Get React Native/Expo project structure."""
        return f"""
```
{app_name}/
├── App.tsx                 # Main app component
├── src/
│   ├── screens/           # Screen components
│   │   └── HomeScreen.tsx
│   ├── components/        # Reusable components
│   │   └── Button.tsx
│   ├── navigation/        # Navigation setup
│   │   └── AppNavigator.tsx
│   ├── hooks/             # Custom hooks
│   ├── services/          # API services
│   ├── utils/             # Utility functions
│   └── types/             # TypeScript types
├── assets/                # Images, fonts, etc.
├── package.json
└── tsconfig.json
```

### Starter App.tsx:
```tsx
import React from 'react';
import {{ SafeAreaView, StyleSheet, Text, View, StatusBar }} from 'react-native';

export default function App() {{
  return (
    <SafeAreaView style={{styles.container}}>
      <StatusBar barStyle="dark-content" />
      <View style={{styles.content}}>
        <Text style={{styles.title}}>Welcome to {app_name}</Text>
        <Text style={{styles.subtitle}}>Your mobile app is ready!</Text>
      </View>
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#ffffff',
  }},
  content: {{
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  }},
  title: {{
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1a1a2e',
    marginBottom: 10,
  }},
  subtitle: {{
    fontSize: 16,
    color: '#666',
  }},
}});
```
"""

    def _get_flutter_structure(self, app_name: str, features: str) -> str:
        """Get Flutter project structure."""
        return f"""
```
{app_name}/
├── lib/
│   ├── main.dart          # App entry point
│   ├── screens/           # Screen widgets
│   │   └── home_screen.dart
│   ├── widgets/           # Reusable widgets
│   │   └── custom_button.dart
│   ├── models/            # Data models
│   ├── services/          # API services
│   └── utils/             # Utility functions
├── assets/                # Images, fonts, etc.
├── test/                  # Unit tests
└── pubspec.yaml          # Dependencies
```

### Starter main.dart:
```dart
import 'package:flutter/material.dart';

void main() {{
  runApp(const MyApp());
}}

class MyApp extends StatelessWidget {{
  const MyApp({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{app_name}',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }}
}}

class HomeScreen extends StatelessWidget {{
  const HomeScreen({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{app_name}'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Welcome to {app_name}',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text('Your mobile app is ready!'),
          ],
        ),
      ),
    );
  }}
}}
```
"""

    async def _add_screen(self, framework: str, app_name: str, 
                          screen_name: str = "", description: str = "", **kwargs) -> Response:
        """Add a new screen to the app."""
        if not screen_name:
            return Response(
                message="Error: screen_name is required for add_screen action",
                break_loop=False
            )

        screen_name = screen_name.replace(" ", "")
        
        if framework in ["react-native", "expo"]:
            code = self._generate_rn_screen(screen_name, description)
            file_path = f"src/screens/{screen_name}Screen.tsx"
        else:
            code = self._generate_flutter_screen(screen_name, description)
            file_path = f"lib/screens/{screen_name.lower()}_screen.dart"

        return Response(
            message=f"""## New Screen: {screen_name}

### File: `{file_path}`

{code}

### Usage:
Import and add this screen to your navigation.
""",
            break_loop=False
        )

    def _generate_rn_screen(self, name: str, description: str) -> str:
        """Generate React Native screen code."""
        return f"""```tsx
import React from 'react';
import {{ View, Text, StyleSheet, ScrollView }} from 'react-native';

interface {name}ScreenProps {{
  // Add props here
}}

export const {name}Screen: React.FC<{name}ScreenProps> = () => {{
  return (
    <ScrollView style={{styles.container}}>
      <View style={{styles.content}}>
        <Text style={{styles.title}}>{name}</Text>
        {f'<Text style={{styles.description}}>{description}</Text>' if description else ''}
      </View>
    </ScrollView>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#fff',
  }},
  content: {{
    padding: 20,
  }},
  title: {{
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  }},
  description: {{
    fontSize: 16,
    color: '#666',
  }},
}});

export default {name}Screen;
```"""

    def _generate_flutter_screen(self, name: str, description: str) -> str:
        """Generate Flutter screen code."""
        class_name = name[0].upper() + name[1:]
        return f"""```dart
import 'package:flutter/material.dart';

class {class_name}Screen extends StatelessWidget {{
  const {class_name}Screen({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{name}'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '{name}',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            {f"const SizedBox(height: 10),\\n            const Text('{description}')," if description else ""}
          ],
        ),
      ),
    );
  }}
}}
```"""

    async def _add_component(self, framework: str, app_name: str,
                             component_name: str = "", component_type: str = "basic", **kwargs) -> Response:
        """Add a reusable component."""
        if not component_name:
            return Response(
                message="Error: component_name is required for add_component action",
                break_loop=False
            )

        component_name = component_name.replace(" ", "")

        if framework in ["react-native", "expo"]:
            code = self._generate_rn_component(component_name, component_type)
            file_path = f"src/components/{component_name}.tsx"
        else:
            code = self._generate_flutter_component(component_name, component_type)
            file_path = f"lib/widgets/{component_name.lower()}.dart"

        return Response(
            message=f"""## New Component: {component_name}

### File: `{file_path}`

{code}
""",
            break_loop=False
        )

    def _generate_rn_component(self, name: str, comp_type: str) -> str:
        """Generate React Native component."""
        return f"""```tsx
import React from 'react';
import {{ View, Text, TouchableOpacity, StyleSheet, ViewStyle }} from 'react-native';

interface {name}Props {{
  title?: string;
  onPress?: () => void;
  style?: ViewStyle;
  children?: React.ReactNode;
}}

export const {name}: React.FC<{name}Props> = ({{
  title,
  onPress,
  style,
  children,
}}) => {{
  const Container = onPress ? TouchableOpacity : View;
  
  return (
    <Container style={{[styles.container, style]}} onPress={{onPress}}>
      {{title && <Text style={{styles.title}}>{{title}}</Text>}}
      {{children}}
    </Container>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    padding: 16,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
  }},
  title: {{
    fontSize: 16,
    fontWeight: '600',
  }},
}});

export default {name};
```"""

    def _generate_flutter_component(self, name: str, comp_type: str) -> str:
        """Generate Flutter widget."""
        class_name = name[0].upper() + name[1:]
        return f"""```dart
import 'package:flutter/material.dart';

class {class_name} extends StatelessWidget {{
  final String? title;
  final VoidCallback? onPressed;
  final Widget? child;

  const {class_name}({{
    super.key,
    this.title,
    this.onPressed,
    this.child,
  }});

  @override
  Widget build(BuildContext context) {{
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != null)
              Text(
                title!,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            if (child != null) child!,
          ],
        ),
      ),
    );
  }}
}}
```"""

    async def _generate_ui(self, framework: str, description: str = "", **kwargs) -> Response:
        """Generate UI code from description."""
        if not description:
            return Response(
                message="Error: description is required for generate_ui action",
                break_loop=False
            )

        response = f"""## UI Generation

Based on your description: "{description}"

I'll generate the UI code. For more complex UIs, consider using the orchestrate tool to parallelize component generation.

### Note:
For best results, break down complex UIs into:
1. Individual screens
2. Reusable components
3. Navigation structure

Use `add_screen` and `add_component` actions to build each piece.
"""
        return Response(message=response, break_loop=False)

    async def _build_app(self, framework: str, app_name: str, platform: str = "all", **kwargs) -> Response:
        """Build the app for production."""
        fw = self.FRAMEWORKS[framework]

        if framework in ["react-native", "expo"]:
            build_cmds = """
### iOS Build:
```bash
# For Expo
npx expo build:ios
# Or for bare React Native
cd ios && pod install && cd ..
npx react-native run-ios --configuration Release
```

### Android Build:
```bash
# For Expo
npx expo build:android
# Or for bare React Native
cd android && ./gradlew assembleRelease
```
"""
        else:
            build_cmds = """
### iOS Build:
```bash
flutter build ios --release
```

### Android Build:
```bash
flutter build apk --release
# Or for app bundle
flutter build appbundle --release
```
"""

        return Response(
            message=f"""## Build Instructions for {fw['name']}

{build_cmds}

### Pre-build Checklist:
- [ ] Update version numbers
- [ ] Configure app icons
- [ ] Set up signing certificates
- [ ] Review permissions
- [ ] Test on physical devices
""",
            break_loop=False
        )

    async def _get_info(self, framework: str) -> Response:
        """Get framework information."""
        fw = self.FRAMEWORKS[framework]
        
        return Response(
            message=f"""## Framework: {fw['name']}

### Initialization:
```bash
{fw['init_cmd'].format(app_name='MyApp')}
```

### File Extension: `{fw['extension']}`

### Available Actions:
- `create` - Create new project
- `add_screen` - Add a screen/page
- `add_component` - Add reusable component
- `generate_ui` - Generate UI from description
- `build` - Build for production

### Documentation:
- React Native: https://reactnative.dev
- Expo: https://docs.expo.dev
- Flutter: https://flutter.dev/docs
""",
            break_loop=False
        )

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://phone_android {self.agent.agent_name}: Mobile Development",
            content="",
            kvps=self.args
        )
