# HTTP Module Documentation

## About

The `dpn_pyutils.http` module provides essential utilities for HTTP-related operations, with a primary focus on URL validation and parsing. This module offers a lightweight, reliable solution for applications that need to validate and work with web URLs.

The module is designed for scenarios where URL validation is critical, such as web scraping, API integrations, data processing pipelines, and any application that handles user-provided URLs or needs to ensure link validity.

## Examples

### Basic URL Validation

```python
from dpn_pyutils.http import is_url

# Validate various URL formats
test_urls = [
    "https://www.example.com",
    "http://localhost:8080",
    "https://api.github.com/users/octocat",
    "ftp://files.example.com/download.zip",
    "not-a-url",
    "www.example.com",  # Missing scheme
    "mailto:user@example.com",
    "file:///path/to/file.txt"
]

for url in test_urls:
    result = is_url(url)
    status = "✓ Valid" if result else "✗ Invalid"
    print(f"{status}: {url}")
```

### URL Validation in Data Processing

```python
from dpn_pyutils.http import is_url

def filter_valid_urls(url_list):
    """Filter a list of strings to return only valid URLs."""
    valid_urls = []
    for item in url_list:
        if is_url(item):
            valid_urls.append(item)
    return valid_urls

# Example usage
mixed_data = [
    "https://www.python.org",
    "not a url",
    "ftp://example.com/file.txt",
    "C:\\Windows\\System32",  # Invalid URL
    "https://github.com/user/repo"
]

valid_urls = filter_valid_urls(mixed_data)
print("Valid URLs found:")
for url in valid_urls:
    print(f"  - {url}")
```

### URL Validation with Error Handling

```python
from dpn_pyutils.http import is_url

def validate_url_safely(url_string):
    """Safely validate a URL with comprehensive error handling."""
    try:
        if not isinstance(url_string, str):
            return False, "Input must be a string"

        if not url_string.strip():
            return False, "URL cannot be empty"

        if is_url(url_string):
            return True, "Valid URL"
        else:
            return False, "Invalid URL format"

    except Exception as e:
        return False, f"Error during validation: {e}"

# Test various inputs
test_cases = [
    "https://example.com",
    "",
    None,
    "not-a-url",
    "ftp://test.com"
]

for case in test_cases:
    is_valid, message = validate_url_safely(case)
    print(f"Input: {repr(case)} -> {message}")
```

### URL Processing Pipeline

```python
from dpn_pyutils.http import is_url
from urllib.parse import urlparse

def process_potential_urls(data_list):
    """Process a list that might contain URLs and extract metadata."""
    results = []

    for item in data_list:
        if is_url(item):
            parsed = urlparse(item)
            results.append({
                'original': item,
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'is_valid': True
            })
        else:
            results.append({
                'original': item,
                'is_valid': False
            })

    return results

# Example with mixed data
mixed_data = [
    "https://www.google.com/search?q=python",
    "not a url",
    "http://localhost:3000/api",
    "invalid-url-format"
]

processed = process_potential_urls(mixed_data)
for result in processed:
    if result['is_valid']:
        print(f"URL: {result['original']}")
        print(f"  Domain: {result['netloc']}")
        print(f"  Path: {result['path']}")
    else:
        print(f"Invalid: {result['original']}")
    print()
```

### Integration with Web Requests

```python
import requests
from dpn_pyutils.http import is_url

def safe_http_get(url):
    """Safely make HTTP requests with URL validation."""
    if not is_url(url):
        raise ValueError(f"Invalid URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise RuntimeError(f"HTTP request failed for {url}: {e}")

# Usage
try:
    content = safe_http_get("https://httpbin.org/json")
    print(f"Successfully fetched {len(content)} characters")
except ValueError as e:
    print(f"URL validation error: {e}")
except RuntimeError as e:
    print(f"Request error: {e}")
```

## Architecture

### Design Philosophy

The HTTP module follows a minimalist yet robust approach:

1. **Single Responsibility**: Focuses solely on URL validation with high reliability
2. **Standards Compliance**: Uses Python's `urllib.parse` for standard URL parsing
3. **Error Safety**: Graceful handling of malformed input and edge cases
4. **Performance**: Lightweight validation suitable for high-throughput scenarios

### Core Implementation

#### URL Validation Logic
The `is_url()` function implements comprehensive URL validation:

```python
def is_url(url: str) -> bool:
    """Check if a given string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
```

#### Validation Criteria
A string is considered a valid URL if:
- **Scheme**: Has a valid URL scheme (http, https, ftp, file, etc.)
- **Network Location**: Contains a valid network location (domain/IP)
- **Parseable**: Can be successfully parsed by `urlparse`

### Supported URL Schemes

The module supports all standard URL schemes that `urllib.parse` can handle:

- **Web URLs**: `http://`, `https://`
- **File URLs**: `file://`
- **FTP URLs**: `ftp://`, `ftps://`
- **Email URLs**: `mailto:`
- **Custom Schemes**: Any valid scheme with proper formatting

### Performance Characteristics

- **Lightweight**: Minimal overhead for URL validation
- **Fast Parsing**: Uses optimized `urllib.parse` implementation
- **Memory Efficient**: No unnecessary object creation or storage
- **Scalable**: Suitable for processing large lists of URLs

### Error Handling Strategy

#### Input Validation
- **Type Checking**: Ensures input is a string
- **Empty String Handling**: Properly handles empty/whitespace-only strings
- **Exception Safety**: Catches and handles parsing exceptions gracefully

#### Edge Cases
- **Malformed URLs**: Returns `False` for unparseable strings
- **Relative URLs**: Correctly identifies missing scheme/netloc
- **Unicode URLs**: Supports international domain names

### Limitations and Considerations

- **Scheme Validation**: Validates format, not scheme existence or accessibility
- **Network Checking**: Does not verify if the URL actually exists or is reachable
- **Security**: Does not perform security validation (consider using `urllib.parse` for additional checks)
- **Performance**: For very large-scale URL processing, consider batch validation strategies

### Best Practices

1. **Input Sanitization**: Always validate user-provided URLs before processing
2. **Error Context**: Provide meaningful error messages when URL validation fails
3. **Scheme Filtering**: Filter URLs by scheme if your application only supports specific types
4. **Timeout Handling**: Implement appropriate timeouts when making requests to validated URLs

### Integration Patterns

#### Data Validation Pipeline
```python
from dpn_pyutils.http import is_url

class URLValidator:
    def __init__(self, allowed_schemes=None):
        self.allowed_schemes = set(allowed_schemes or ['http', 'https'])

    def validate(self, url):
        if not is_url(url):
            return False, "Invalid URL format"

        from urllib.parse import urlparse
        scheme = urlparse(url).scheme
        if scheme not in self.allowed_schemes:
            return False, f"Scheme '{scheme}' not allowed"

        return True, "Valid URL"
```

#### Batch Processing
```python
from dpn_pyutils.http import is_url

def batch_validate_urls(url_list, batch_size=100):
    """Validate URLs in batches for better performance."""
    results = []

    for i in range(0, len(url_list), batch_size):
        batch = url_list[i:i + batch_size]
        batch_results = [(url, is_url(url)) for url in batch]
        results.extend(batch_results)

    return results
```

### Security Considerations

While this module focuses on format validation, consider these security aspects:

- **URL Length Limits**: Implement reasonable length limits for user-provided URLs
- **Scheme Restrictions**: Restrict allowed schemes based on your application's needs
- **Input Encoding**: Be aware of URL encoding and potential bypasses
- **Additional Validation**: Consider using additional security libraries for comprehensive URL security

### Testing Examples

```python
import pytest
from dpn_pyutils.http import is_url

def test_valid_urls():
    assert is_url("https://example.com") == True
    assert is_url("http://localhost:8080") == True
    assert is_url("ftp://files.example.com") == True

def test_invalid_urls():
    assert is_url("not-a-url") == False
    assert is_url("www.example.com") == False  # Missing scheme
    assert is_url("") == False
    assert is_url(None) == False  # Will raise TypeError

def test_edge_cases():
    assert is_url("file:///path/to/file") == True
    assert is_url("mailto:user@example.com") == True
    assert is_url("https://пример.испытание") == True  # Unicode domains
