# CLI Module Documentation

## About

The `dpn_pyutils.cli` module provides comprehensive color formatting utilities for command-line interface (CLI) output. Built on top of the `colorama` library, this module offers a clean and consistent API for adding colors, backgrounds, and text formatting to terminal output.

This module is particularly useful for creating visually appealing and well-organized CLI applications, scripts, and tools where color-coded output enhances user experience and readability.

## Examples

### Basic Color Text Formatting

```python
from dpn_pyutils.cli import color_t

# Format text with a specific color
red_text = color_t("Error: Something went wrong!", Fore.RED)
green_text = color_t("Success: Operation completed!", Fore.GREEN)
blue_text = color_t("Info: Processing data...", Fore.BLUE)

print(red_text)
print(green_text)
print(blue_text)
```

### Variable Display with Colors

```python
from dpn_pyutils.cli import color_var_fore

# Display variables with colored values
status = color_var_fore("Status", "Active", Fore.GREEN)
level = color_var_fore("Log Level", "DEBUG", Fore.YELLOW)
count = color_var_fore("Records", "1,234", Fore.CYAN)

print(status)
print(level)
print(count)
```

### Complex Variable Formatting

```python
from dpn_pyutils.cli import color_var

# Full control over label and value colors
error_msg = color_var("Error", Fore.RED, "Connection Failed", Back.WHITE)
warning_msg = color_var("Warning", Fore.YELLOW, "Low Disk Space", Back.RESET)

print(error_msg)
print(warning_msg)
```

### Advanced Formatting with Backgrounds

```python
from dpn_pyutils.cli import color_var_fore_back

# Format with both foreground and background colors
header = color_var_fore_back(
    "CRITICAL", Fore.WHITE, Back.RED,
    "System Alert", Fore.YELLOW, Back.RESET
)

print(header)
```

### Direct String Formatting

```python
from dpn_pyutils.cli import color_format_string

# Direct string formatting with colors
formatted = color_format_string("IMPORTANT MESSAGE", Fore.RED, Back.YELLOW)
print(formatted)
```

## Architecture

### Design Philosophy

The CLI module follows a layered approach to color formatting:

1. **Low-level formatting** (`color_format_string`): Handles basic text formatting with foreground and background colors
2. **Variable formatting** (`color_var`, `color_var_fore`, `color_var_fore_back`): Provides structured formatting for key-value pairs
3. **Convenience functions** (`color_t`): Offers simple text coloring for quick usage

### Key Design Decisions

- **Colorama Integration**: Leverages the robust `colorama` library for cross-platform color support
- **Consistent API**: All functions follow similar parameter patterns for predictability
- **Flexible Color Input**: Accepts both `colorama` color constants and string color names
- **Automatic Resets**: Ensures color states don't bleed between different formatted sections

### Color Constants

The module uses `colorama` color constants:
- `Fore`: Foreground colors (text color)
- `Back`: Background colors
- `Style`: Text styles (though not directly exposed in this module)

### Limitations and Considerations

- **Terminal Dependency**: Colors only work in terminals that support ANSI color codes
- **Color Blindness**: Consider accessibility when choosing color schemes
- **Cross-platform**: While `colorama` handles Windows compatibility, some advanced features may vary
- **Performance**: For high-frequency output, consider caching formatted strings

### Best Practices

1. **Consistent Color Usage**: Use the same colors for similar types of messages across your application
2. **Color Pairing**: Ensure sufficient contrast between foreground and background colors
3. **Fallback Planning**: Consider how your CLI output will look without colors
4. **Semantic Colors**: Use red for errors, green for success, yellow for warnings, blue for information
