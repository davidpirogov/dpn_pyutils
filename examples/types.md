# Types Module Documentation

## About

The `dpn_pyutils.types` module provides stateless utility functions for type checking and conversion operations. This module contains essential functions for validating and converting string inputs into appropriate Python types, making it ideal for input validation, configuration parsing, and data sanitization tasks.

The module focuses on robust type detection and conversion with comprehensive error handling, supporting numeric types (integers and floats), boolean representations, and intelligent type parsing. All functions are stateless and thread-safe, making them suitable for use in concurrent applications and functional programming patterns.

## Examples

### Type Checking Functions

```python
from dpn_pyutils.types import is_numeric, is_integer, is_boolean

# Check if strings represent numeric values
print(is_numeric("123"))        # True
print(is_numeric("123.45"))     # True
print(is_numeric("1.23e10"))    # True
print(is_numeric("abc"))        # False
print(is_numeric(""))           # False

# Check if strings represent integers
print(is_integer("123"))        # True
print(is_integer("123.0"))      # True
print(is_integer("123.45"))     # False
print(is_integer("1e2"))        # True (represents 100.0)

# Check if strings represent boolean values
print(is_boolean("true"))       # True
print(is_boolean("YES"))        # True
print(is_boolean("false"))      # True
print(is_boolean("No"))         # True
print(is_boolean("maybe"))      # False
print(is_boolean("2"))          # False
```

### Type Conversion with parse_type()

```python
from dpn_pyutils.types import parse_type

# Convert strings to appropriate types
print(parse_type("123"))        # 123 (int)
print(parse_type("123.45"))     # 123.45 (float)
print(parse_type("true"))       # True (bool)
print(parse_type("false"))      # False (bool)
print(parse_type(""))           # None
print(parse_type("hello"))      # 'hello' (str)

# Handle exponential notation
print(parse_type("1.23e2"))     # 123.0 (float)
print(parse_type("2e0"))        # 2.0 (float)

# Case-insensitive boolean parsing
print(parse_type("TRUE"))       # True
print(parse_type("False"))      # False
print(parse_type("YES"))        # True
print(parse_type("NO"))         # True
```

### Input Validation Workflow

```python
from dpn_pyutils.types import is_numeric, is_integer, is_boolean, parse_type

def validate_and_convert_input(user_input):
    """Example workflow for validating and converting user input."""

    # First, determine the input type
    if is_numeric(user_input):
        if is_integer(user_input):
            return int(user_input), "integer"
        else:
            return float(user_input), "float"
    elif is_boolean(user_input):
        return parse_type(user_input), "boolean"
    elif user_input == "":
        return None, "null"
    else:
        return user_input, "string"

# Example usage
test_inputs = ["123", "123.45", "true", "false", "", "hello", "YES", "no"]

for user_input in test_inputs:
    result, input_type = validate_and_convert_input(user_input)
    print(f"'{user_input}' -> {result} ({input_type})")
```

### Configuration Parsing Example

```python
from dpn_pyutils.types import parse_type

def parse_config_value(key, value_str):
    """Parse configuration values with intelligent type conversion."""

    # Use parse_type for intelligent conversion
    parsed_value = parse_type(value_str)

    # Validate based on expected types for common config keys
    if key in ["port", "timeout", "retries"]:
        if not isinstance(parsed_value, int) or parsed_value < 0:
            raise ValueError(f"{key} must be a non-negative integer")
    elif key in ["host", "name", "description"]:
        if parsed_value is None:
            raise ValueError(f"{key} cannot be empty")
    elif key in ["enabled", "debug", "verbose"]:
        if not isinstance(parsed_value, bool):
            raise ValueError(f"{key} must be a boolean")

    return parsed_value

# Example configuration parsing
config_strings = {
    "port": "8080",
    "timeout": "30",
    "host": "localhost",
    "debug": "true",
    "retries": "3",
    "name": "my-app",
    "enabled": "YES"
}

config = {}
for key, value_str in config_strings.items():
    config[key] = parse_config_value(key, value_str)

print("Parsed configuration:", config)
```

### Data Sanitization Pipeline

```python
from dpn_pyutils.types import parse_type, is_numeric, is_boolean

def sanitize_csv_data(csv_rows):
    """Sanitize and convert CSV data with mixed types."""

    sanitized_data = []

    for row in csv_rows:
        sanitized_row = {}
        for column, value in row.items():
            # Skip empty values
            if not value or value == "":
                sanitized_row[column] = None
                continue

            # Parse the value
            parsed_value = parse_type(value.strip())

            # Additional validation for specific columns
            if column in ["age", "count", "id"]:
                if not isinstance(parsed_value, int):
                    raise ValueError(f"{column} must be an integer, got {value}")
            elif column in ["price", "rate"]:
                if not isinstance(parsed_value, (int, float)):
                    raise ValueError(f"{column} must be numeric, got {value}")
            elif column in ["active", "enabled"]:
                if not isinstance(parsed_value, bool):
                    raise ValueError(f"{column} must be boolean, got {value}")

            sanitized_row[column] = parsed_value

        sanitized_data.append(sanitized_row)

    return sanitized_data

# Example CSV data sanitization
csv_data = [
    {"name": "Alice", "age": "25", "price": "99.99", "active": "true"},
    {"name": "Bob", "age": "30", "price": "149.50", "active": "false"},
    {"name": "Charlie", "age": "35", "price": "75.0", "active": "YES"}
]

sanitized = sanitize_csv_data(csv_data)
for row in sanitized:
    print(f"Sanitized: {row}")
```

## Architecture

### Design Philosophy

The types module follows these core principles:

1. **Robustness**: Comprehensive error handling for edge cases and invalid inputs
2. **Performance**: Efficient type checking without unnecessary conversions
3. **Consistency**: Predictable behavior across all type checking functions
4. **Statelessness**: All functions are pure and thread-safe
5. **Extensibility**: Easy to add new type validations or conversion patterns

### Key Components

#### Type Checking Functions
- **`is_numeric(n)`**: Validates numeric string representations including integers, floats, and exponential notation
- **`is_integer(n)`**: Determines if a numeric string represents a whole number
- **`is_boolean(n)`**: Validates boolean string representations with case-insensitive matching

#### Type Conversion Functions
- **`parse_type(n)`**: Intelligent type conversion with priority-based parsing (int → float → bool → None → str)

#### Constants
- **`TRUE_BOOLS`**: List of string representations that evaluate to True
- **`FALSE_BOOLS`**: List of string representations that evaluate to False

### Type Detection Strategy

The module implements a hierarchical type detection approach:

1. **Numeric Detection**: First checks if input can be parsed as a number
2. **Integer Validation**: If numeric, determines if it's a whole number
3. **Boolean Recognition**: Checks against predefined boolean string patterns
4. **Empty Handling**: Special case for empty strings returning None
5. **String Fallback**: Returns original string if no other type matches

### Error Handling Strategy

#### Exception Management
- Uses try/catch blocks for controlled error handling
- Returns False for type checking functions on invalid input
- Returns original string for parse_type on unrecognized formats

#### Edge Case Handling
- Empty strings return False for type checks, None for parse_type
- Exponential notation properly handled for both integers and floats
- Case-insensitive boolean string matching

### Performance Characteristics

#### Efficiency Optimizations
- **Early Returns**: Functions return False immediately on invalid input
- **Minimal Conversions**: Type checking avoids unnecessary parsing operations
- **Constant Lookups**: Boolean validation uses set membership for O(1) lookups

#### Computational Complexity
- **Type Checking**: O(1) for boolean checks, O(n) for numeric parsing where n is string length
- **Type Conversion**: O(n) where n is string length due to parsing operations
- **Memory Usage**: Minimal memory footprint with no persistent state

### Security Considerations

#### Input Validation
- **Safe Parsing**: All parsing operations are wrapped in try/catch blocks
- **No Code Injection**: String inputs are never executed, only parsed
- **Type Safety**: Functions return predictable types preventing injection attacks

#### Best Practices
1. **Input Sanitization**: Always validate user input before processing
2. **Type Coercion**: Use parse_type for intelligent type conversion from strings
3. **Error Handling**: Handle conversion failures gracefully in application code
4. **Data Validation**: Combine type checking with business logic validation

### Limitations and Considerations

- **Locale Dependency**: Numeric parsing follows Python's locale settings
- **Precision Limits**: Very large numbers may lose precision in float conversion
- **Boolean Ambiguity**: Only predefined boolean strings are recognized
- **Unicode Support**: Assumes UTF-8 compatible string inputs

### Best Practices

1. **Validation Order**: Use specific type checks before general parsing
2. **Error Handling**: Always handle potential conversion failures
3. **Type Coercion**: Be explicit about when type conversion is desired
4. **Input Sanitization**: Use for user input validation and CSV data processing
5. **Configuration Parsing**: Ideal for converting string configuration values

### Integration Examples

#### API Request Processing
```python
from dpn_pyutils.types import parse_type, is_numeric, is_boolean

def process_api_request(request_data):
    """Process and validate API request parameters."""

    processed = {}

    for key, value in request_data.items():
        if key in ["limit", "offset"]:
            if is_numeric(str(value)):
                processed[key] = int(float(str(value)))  # Ensure integer
            else:
                raise ValueError(f"{key} must be numeric")
        elif key in ["active", "enabled"]:
            if is_boolean(str(value)):
                processed[key] = parse_type(str(value))
            else:
                raise ValueError(f"{key} must be boolean")
        else:
            processed[key] = str(value)

    return processed
```

#### Form Data Processing
```python
from dpn_pyutils.types import parse_type

def process_form_data(form_fields):
    """Process HTML form data with type conversion."""

    processed_data = {}

    for field_name, field_value in form_fields.items():
        # Convert to appropriate type based on field name patterns
        if 'count' in field_name or 'id' in field_name or 'age' in field_name:
            processed_data[field_name] = parse_type(field_value)
            if not isinstance(processed_data[field_name], int):
                raise ValueError(f"{field_name} must be an integer")
        elif 'price' in field_name or 'rate' in field_name:
            processed_data[field_name] = parse_type(field_value)
            if not isinstance(processed_data[field_name], (int, float)):
                raise ValueError(f"{field_name} must be numeric")
        else:
            processed_data[field_name] = field_value.strip() or None

    return processed_data