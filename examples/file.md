# File Module Documentation

## About

The `dpn_pyutils.file` module provides a comprehensive suite of file input/output utilities for Python applications. This module offers robust, safe, and feature-rich functions for reading and writing various file formats including JSON, CSV, TOML, and plain text files.

Built with safety and reliability in mind, the module includes advanced features such as atomic writes, format validation, comprehensive error handling, and support for complex data serialization scenarios. It integrates seamlessly with the custom exception classes for consistent error reporting.

## Examples

### JSON File Operations

```python
from dpn_pyutils.file import read_file_json, save_file_json, save_file_json_opts
from pathlib import Path
import json

# Read JSON file
config_path = Path("config.json")
try:
    config_data = read_file_json(config_path)
    print(f"Loaded config: {config_data}")
except FileNotFoundError:
    print("Config file not found")

# Save JSON file with default options
data = {
    "database": {"host": "localhost", "port": 5432},
    "api": {"timeout": 30, "retries": 3}
}
save_file_json(Path("app_config.json"), data)

# Save JSON with custom options (compact format)
save_file_json_opts(
    Path("compact_config.json"),
    data,
    overwrite=True,
    serializer_opts=0  # Minimal options for compact output
)
```

### Text File Operations

```python
from dpn_pyutils.file import read_file_text, save_file_text
from pathlib import Path

# Read text file
content = read_file_text(Path("README.txt"))
print(f"File content: {content}")

# Save text file
save_file_text(Path("output.txt"), "This is the file content")

# Save with overwrite protection
try:
    save_file_text(Path("output.txt"), "New content")  # Will fail without overwrite=True
except FileSaveError:
    print("File exists, use overwrite=True to replace")

# Force overwrite
save_file_text(Path("output.txt"), "New content", overwrite=True)
```

### CSV File Operations

```python
from dpn_pyutils.file import read_file_csv, save_file_csv
from pathlib import Path

# Read CSV file
data = read_file_csv(Path("data.csv"))
for row in data:
    print(f"Row: {row}")

# Read CSV with custom delimiter
tab_separated_data = read_file_csv(Path("data.tsv"), delimiter="\t")

# Save CSV file
csv_data = [
    ["Name", "Age", "City"],
    ["Alice", "25", "New York"],
    ["Bob", "30", "San Francisco"],
    ["Charlie", "35", "Chicago"]
]
save_file_csv(Path("people.csv"), csv_data)

# Save CSV with custom formatting
save_file_csv(
    Path("quoted_data.csv"),
    csv_data,
    delimiter=",",
    quote_char='"',
    escapechar="\\",
    overwrite=True
)
```

### TOML File Operations

```python
from dpn_pyutils.file import read_file_toml, save_file_text
from pathlib import Path

# Read TOML file
config = read_file_toml(Path("pyproject.toml"))
print(f"Project name: {config.get('project', {}).get('name')}")

# Save TOML file (TOML doesn't have a direct save function, use text)
import toml
toml_data = {
    "project": {"name": "my-project", "version": "1.0.0"},
    "dependencies": ["requests", "click"]
}
toml_string = toml.dumps(toml_data)
save_file_text(Path("pyproject.toml"), toml_string, overwrite=True)
```

### Advanced File Management

```python
from dpn_pyutils.file import (
    get_valid_file, append_value_to_filename,
    get_timestamp_formatted_file_dir, get_cachekey
)
from pathlib import Path
from datetime import datetime

# Generate unique filenames
base_dir = Path("./output")
unique_file = get_valid_file(base_dir, "report.json")
print(f"Unique file path: {unique_file}")

# Append values to filenames
modified_name = append_value_to_filename("report.json", "_2024")
print(f"Modified name: {modified_name}")

# Create timestamp-based directory structure
timestamp = datetime.now()
data_dir = get_timestamp_formatted_file_dir(
    Path("./data"),
    timestamp,
    resolution="DAY",
    create_dir=True
)
print(f"Timestamp directory: {data_dir}")

# Generate cache keys
cache_key = get_cachekey(3600, timestamp)  # 1-hour TTL
print(f"Cache key: {cache_key}")
```

### File Listing and Discovery

```python
from dpn_pyutils.file import get_file_list_from_dir
from pathlib import Path

# Get all JSON files recursively
json_files = get_file_list_from_dir(Path("./data"), "*.json")
print(f"Found {len(json_files)} JSON files")

# Get all Python files
python_files = get_file_list_from_dir(Path("."), "*.py")

# Get all files in a directory
all_files = get_file_list_from_dir(Path("./src"))
```

### Timestamp and Snapshot Utilities

```python
from dpn_pyutils.file import (
    extract_timestamp_from_snapshot_key,
    prepare_timestamp_datapath
)
from datetime import datetime

# Extract timestamp from snapshot key
snapshot_key = "trending-snapshot-2021-01-01-143546"
timestamp = extract_timestamp_from_snapshot_key(snapshot_key)
print(f"Extracted timestamp: {timestamp}")

# Prepare data path with timestamp
data_path = prepare_timestamp_datapath(
    Path("./data"),
    datetime.now(),
    data_dir_resolution="HOUR",
    data_file_timespan=3600,
    data_file_prefix="analytics_"
)
print(f"Data path: {data_path}")
```

## Architecture

### Design Philosophy

The file module is built around several core principles:

1. **Safety First**: Atomic writes, existence checks, and comprehensive error handling
2. **Format Support**: Native support for common file formats (JSON, CSV, TOML, text)
3. **Atomic Operations**: Safe file writes using temporary files and atomic moves
4. **Error Context**: Detailed error messages with file paths and operation context
5. **Performance**: Optimized for common use cases with efficient serialization

### Key Components

#### File Readers
- **`read_file_json()`**: JSON file parsing with custom object support
- **`read_file_text()`**: Plain text file reading
- **`read_file_toml()`**: TOML configuration file parsing
- **`read_file_csv()`**: CSV file parsing with delimiter/quote options

#### File Writers
- **`save_file_text()`**: Plain text file writing with overwrite protection
- **`save_file_csv()`**: CSV file writing with formatting options
- **`save_file_json()`**: JSON file writing with pretty-printing
- **`save_file_json_opts()`**: Advanced JSON writing with custom options

#### File Management
- **`get_valid_file()`**: Generate unique filenames to avoid conflicts
- **`append_value_to_filename()`**: Modify filenames with additional information
- **`get_timestamp_formatted_file_dir()`**: Create timestamp-based directory structures
- **`get_file_list_from_dir()`**: Recursive file discovery with pattern matching

#### Timestamp Utilities
- **`get_cachekey()`**: Generate time-based cache keys
- **`get_timestamp_format_by_ttl_seconds()`**: Calculate appropriate timestamp precision
- **`extract_timestamp_from_snapshot_key()`**: Parse timestamps from snapshot identifiers
- **`prepare_timestamp_datapath()`**: Create complete timestamp-based file paths

### Serialization Strategy

#### JSON Handling
- Uses `orjson` for high-performance JSON operations
- Supports custom object serialization via `json_serializer()`
- Handles datetime, date, and Decimal objects automatically
- Configurable formatting options for different use cases

#### CSV Processing
- Standard `csv` module integration with error handling
- Support for custom delimiters, quote characters, and escape sequences
- Proper handling of StringIO for memory-efficient processing

### Atomic Write Strategy

The module implements a robust atomic write pattern:

1. **Temporary File Creation**: Generate unique temporary filename
2. **Safe Writing**: Write data to temporary file first
3. **Atomic Move**: Use `Path.replace()` for atomic file replacement
4. **Cleanup**: Automatic cleanup of temporary files on errors

```python
# Internal atomic write process
random_file_name = get_random_string()
output_file_path = get_valid_file(json_file_path.parent, random_file_name)

try:
    with open(output_file_path, 'w') as f:
        f.write(data)
    output_file_path.replace(json_file_path)  # Atomic replacement
except Exception:
    if output_file_path.exists():
        output_file_path.unlink()  # Cleanup on error
    raise
```

### Error Handling Integration

All file operations integrate with the custom exception hierarchy:

- **`FileNotFoundError`**: When expected files don't exist
- **`FileOpenError`**: When file reading operations fail
- **`FileSaveError`**: When file writing operations fail

### Performance Considerations

#### Memory Efficiency
- **Streaming**: Large files are processed without loading entirely into memory
- **StringIO**: CSV operations use in-memory buffers for efficiency
- **OrJSON**: High-performance JSON parsing for large datasets

#### I/O Optimization
- **Binary Modes**: Uses appropriate file modes for different data types
- **Buffering**: Leverages Python's built-in buffering for efficient I/O
- **Batch Operations**: Supports processing multiple files efficiently

### Limitations and Considerations

- **File Size**: Very large files may require streaming or chunked processing
- **Encoding**: Assumes UTF-8 encoding for text operations
- **Permissions**: File operations require appropriate system permissions
- **Atomicity**: Atomic writes work within the same filesystem

### Best Practices

1. **Overwrite Protection**: Use `overwrite=True` explicitly when intended
2. **Error Handling**: Always handle file operation exceptions appropriately
3. **Path Validation**: Validate file paths before operations when possible
4. **Resource Management**: Files are automatically closed, but consider context managers for large operations
5. **Format Selection**: Choose appropriate formats based on data structure and use case

### Integration Examples

#### Configuration Management
```python
from dpn_pyutils.file import read_file_json, save_file_json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._config = None

    def load_config(self):
        try:
            self._config = read_file_json(self.config_path)
        except FileNotFoundError:
            self._config = {"version": "1.0", "settings": {}}
            save_file_json(self.config_path, self._config)

    def save_config(self):
        save_file_json(self.config_path, self._config, overwrite=True)
```

#### Data Export Pipeline
```python
from dpn_pyutils.file import save_file_csv, get_timestamp_formatted_file_dir
from datetime import datetime

def export_data_to_csv(data, export_name):
    timestamp = datetime.now()
    export_dir = get_timestamp_formatted_file_dir(
        Path("./exports"), timestamp, "DAY", create_dir=True
    )

    filename = f"{export_name}_{timestamp.strftime('%H%M%S')}.csv"
    filepath = export_dir / filename

    save_file_csv(filepath, data, overwrite=True)
    return filepath
