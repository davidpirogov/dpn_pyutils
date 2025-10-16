# Crypto Module Documentation

## About

The `dpn_pyutils.crypto` module provides essential cryptographic and randomization utilities for Python applications. This module focuses on secure random number generation, random string creation, and URL-safe base64 encoding/decoding operations.

The module is designed for applications that need cryptographically secure random values and safe encoding mechanisms, making it suitable for session tokens, temporary passwords, secure identifiers, and data serialization tasks.

## Examples

### Random Number Generation

```python
from dpn_pyutils.crypto import get_random_number

# Generate a random number between 1 and 100 (inclusive)
random_value = get_random_number(1, 100)
print(f"Random number: {random_value}")

# Generate a random port number
port = get_random_number(1024, 65535)
print(f"Random port: {port}")
```

### Random String Generation

```python
from dpn_pyutils.crypto import get_random_string, ALPHA_NUM_CHARS

# Generate a random alphanumeric string (default length 10)
token = get_random_string()
print(f"Default token: {token}")

# Generate a longer random string
long_token = get_random_string(length=32)
print(f"Long token: {long_token}")

# Generate using only alphabetic characters
alpha_only = get_random_string(length=16, allowed_characters=ALPHA_CHARS)
print(f"Alpha token: {alpha_only}")

# Generate using only numeric characters
numeric_only = get_random_string(length=8, allowed_characters=NUM_CHARS)
print(f"Numeric token: {numeric_only}")
```

### Base64 Encoding and Decoding

```python
from dpn_pyutils.crypto import encode_base64, decode_base64

# Encode a string to base64
original_data = "Hello, World!"
encoded_data = encode_base64(original_data)
print(f"Original: {original_data}")
print(f"Encoded: {encoded_data}")

# Decode the base64 string back
decoded_data = decode_base64(encoded_data)
print(f"Decoded: {decoded_data}")

# Example with sensitive data
import json
sensitive_info = {"user_id": 12345, "session": "active"}
sensitive_json = json.dumps(sensitive_info)
encoded_sensitive = encode_base64(sensitive_json)
print(f"Encoded sensitive data: {encoded_sensitive}")
```

### Complete Workflow Example

```python
from dpn_pyutils.crypto import get_random_string, encode_base64, decode_base64

# Generate a secure session token
session_token = get_random_string(length=32)
print(f"Session token: {session_token}")

# Create session data
session_data = {
    "token": session_token,
    "user_id": 12345,
    "expires": "2024-12-31T23:59:59Z"
}

# Encode for storage/transmission
import json
encoded_session = encode_base64(json.dumps(session_data))
print(f"Encoded session: {encoded_session}")

# Decode when needed
retrieved_session = json.loads(decode_base64(encoded_session))
print(f"Retrieved session: {retrieved_session}")
```

## Architecture

### Design Philosophy

The crypto module follows these core principles:

1. **Security First**: Uses `secrets` module for cryptographically secure random generation
2. **Simplicity**: Provides straightforward APIs for common cryptographic tasks
3. **URL Safety**: Base64 encoding uses URL-safe character set for web compatibility
4. **UTF-8 Compatibility**: Proper handling of Unicode strings in encoding operations

### Key Components

#### Random Generation
- **`get_random_number(min, max)`**: Secure random integer generation using `secrets.SystemRandom()`
- **`get_random_string(length, allowed_characters)`**: Secure random string generation with customizable character sets

#### Encoding/Decoding
- **`encode_base64(plain_string)`**: URL-safe base64 encoding with UTF-8 support
- **`decode_base64(encoded_string)`**: URL-safe base64 decoding with UTF-8 support

### Character Set Constants

The module provides predefined character sets:
- **`ALPHA_CHARS`**: All alphabetic characters (a-z, A-Z)
- **`NUM_CHARS`**: All numeric characters (0-9)
- **`ALPHA_NUM_CHARS`**: Combined alphabetic and numeric characters

### Security Considerations

#### Cryptographic Security
- Uses `secrets` module instead of `random` for cryptographically secure operations
- Suitable for security-sensitive applications like tokens, passwords, and keys

#### Limitations
- **Token Uniqueness**: While cryptographically secure, true uniqueness requires application-level tracking
- **Length Considerations**: Longer tokens provide better security but may impact storage/transmission
- **Character Set Security**: Custom character sets should include sufficient entropy

### Performance Characteristics

- **Random Generation**: `secrets` module is optimized for security over performance
- **Base64 Operations**: Efficient encoding/decoding for typical string lengths
- **Memory Usage**: Minimal memory footprint for all operations

### Best Practices

1. **Token Length**: Use appropriate lengths (16+ characters for tokens, 32+ for sensitive data)
2. **Character Diversity**: Include multiple character types for better entropy
3. **Secure Storage**: Store encoded data securely, considering encryption for sensitive information
4. **Error Handling**: Always handle potential decoding errors in production code

### Integration Notes

- **Web Applications**: URL-safe base64 encoding is ideal for web tokens and API data
- **Database Storage**: Encoded data can be safely stored in text fields
- **API Communication**: Use for secure data transmission between services
