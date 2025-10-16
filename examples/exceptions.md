# Exceptions Module Documentation

## About

The `dpn_pyutils.exceptions` module provides a comprehensive set of custom exception classes specifically designed for file operation error handling. This module extends Python's built-in exception hierarchy to offer more granular and informative error handling for file-related operations.

The exception classes are organized hierarchically, with `FileOperationError` as the base class, allowing for both specific error handling and general file operation error catching. Each exception includes contextual information about the file path and operation that caused the error.

## Examples

### Basic Exception Handling

```python
from dpn_pyutils.exceptions import FileOperationError, FileNotFoundError
from pathlib import Path

def safe_file_reader(file_path: Path) -> str:
    """Example function that uses custom exceptions for file operations."""
    try:
        if not file_path.exists():
            raise FileNotFoundError(file_path, f"File {file_path} not found")

        # Simulate file reading operation
        with open(file_path, 'r') as f:
            return f.read()

    except FileOperationError as e:
        print(f"File operation failed: {e}")
        print(f"File path: {e.file_path}")
        return None

# Usage
file_path = Path("nonexistent.txt")
content = safe_file_reader(file_path)
```

### Handling Specific File Operation Errors

```python
from dpn_pyutils.exceptions import (
    FileOperationError,
    FileSaveError,
    FileOpenError,
    FileNotFoundError
)
from pathlib import Path

def comprehensive_file_handler(file_path: Path, data: str) -> bool:
    """Example showing different exception handling strategies."""

    try:
        # Check if file exists before operations
        if not file_path.exists():
            raise FileNotFoundError(file_path, "Cannot operate on non-existent file")

        # Simulate file opening
        try:
            with open(file_path, 'r') as f:
                current_content = f.read()
        except PermissionError:
            raise FileOpenError(file_path, "Permission denied accessing file")

        # Simulate file saving
        try:
            with open(file_path, 'w') as f:
                f.write(data)
        except PermissionError:
            raise FileSaveError(file_path, "Permission denied saving file")

        return True

    except FileNotFoundError as e:
        print(f"File not found: {e.file_path}")
        return False
    except FileOpenError as e:
        print(f"Failed to open file: {e}")
        return False
    except FileSaveError as e:
        print(f"Failed to save file: {e}")
        return False
    except FileOperationError as e:
        print(f"General file operation error: {e}")
        return False

# Usage examples
result1 = comprehensive_file_handler(Path("test.txt"), "new content")
result2 = comprehensive_file_handler(Path("readonly.txt"), "content")  # Permission denied
```

### Exception Inheritance and Polymorphism

```python
from dpn_pyutils.exceptions import FileOperationError, FileSaveError
from pathlib import Path

def process_file_operation(operation_func):
    """Example showing polymorphic exception handling."""
    try:
        return operation_func()
    except FileSaveError as e:
        print(f"Save operation failed for {e.file_path}: {e}")
        return False
    except FileOperationError as e:
        print(f"General file operation failed for {e.file_path}: {e}")
        return False

# Different operations that can raise different exceptions
def save_operation():
    raise FileSaveError(Path("test.txt"), "Disk full")

def open_operation():
    raise FileOperationError(Path("test.txt"), "Unknown file error")

# Both operations can be handled by the same exception handler
process_file_operation(save_operation)
process_file_operation(open_operation)
```

### Exception Information Access

```python
from dpn_pyutils.exceptions import FileOperationError
from pathlib import Path

try:
    raise FileOperationError(Path("/restricted/file.txt"), "Access denied")
except FileOperationError as e:
    print(f"Error message: {e}")
    print(f"File path: {e.file_path}")
    print(f"Absolute path: {e.file_path.absolute()}")
    print(f"Parent directory: {e.file_path.parent}")
    print(f"File exists: {e.file_path.exists()}")
```

## Architecture

### Exception Hierarchy

The exceptions module implements a clean inheritance hierarchy:

```
Exception (Python built-in)
└── FileOperationError (base class)
    ├── FileSaveError
    ├── FileOpenError
    └── FileNotFoundError
```

### Design Philosophy

1. **Contextual Information**: Every exception includes the file path and descriptive message
2. **Inheritance**: Allows for both specific and general error handling
3. **Consistency**: Uniform constructor signature across all exception types
4. **Path Integration**: Uses `pathlib.Path` objects for robust path handling

### Key Design Decisions

#### Base Class Design
- **`FileOperationError`**: Serves as the foundation for all file-related errors
- **Path Storage**: Maintains the file path that caused the error for debugging
- **Message Context**: Provides clear, actionable error messages

#### Specific Exception Types
- **`FileSaveError`**: Raised when file writing/saving operations fail
- **`FileOpenError`**: Raised when file reading/opening operations fail
- **`FileNotFoundError`**: Raised when expected files don't exist (custom version of built-in)

### Constructor Pattern

All exceptions follow a consistent constructor pattern:

```python
def __init__(self, file_path: Path, message: str):
    self.file_path = file_path
    super().__init__(message)
```

### Integration with Standard Exceptions

The module's `FileNotFoundError` coexists with Python's built-in `FileNotFoundError` by being used in specific contexts where additional path information is beneficial.

### Error Handling Strategies

#### Specific Exception Handling
```python
try:
    risky_file_operation()
except FileSaveError:
    # Handle save-specific errors
except FileOpenError:
    # Handle open-specific errors
```

#### General Exception Handling
```python
try:
    risky_file_operation()
except FileOperationError:
    # Handle any file operation error
```

### Limitations and Considerations

- **Path Dependency**: All exceptions require a valid `Path` object
- **Context Limitation**: Exceptions only capture the immediate file path, not full operation context
- **Inheritance Clarity**: While inheritance provides flexibility, it requires understanding of the hierarchy

### Best Practices

1. **Specific First**: Catch specific exceptions before general ones
2. **Path Validation**: Always validate paths before operations when possible
3. **Informative Messages**: Provide clear, actionable error messages
4. **Logging Integration**: Use file path information for comprehensive logging
5. **Recovery Strategies**: Design exceptions to support graceful error recovery

### Testing Considerations

When testing code that uses these exceptions:

```python
import pytest
from dpn_pyutils.exceptions import FileNotFoundError
from pathlib import Path

def test_file_not_found_error():
    with pytest.raises(FileNotFoundError) as exc_info:
        raise FileNotFoundError(Path("missing.txt"), "File not found")

    assert exc_info.value.file_path == Path("missing.txt")
    assert "File not found" in str(exc_info.value)
