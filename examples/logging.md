# Logging Package Documentation

## About

The `dpn_pyutils.logging` package provides a comprehensive, enterprise-grade logging system built on Python's standard `logging` module. This package offers enhanced functionality including custom log levels, structured configuration, project-aware logger namespacing, and robust initialization patterns.

The logging system is designed for applications that require sophisticated logging capabilities, such as microservices, distributed systems, worker processes, and applications with complex logging requirements. It provides both simple setup for basic use cases and advanced configuration for enterprise deployments.

## Examples

### Basic Logger Setup

```python
from dpn_pyutils.logging import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Basic logging
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

### Custom Log Levels (TRACE)

```python
from dpn_pyutils.logging import get_logger

logger = get_logger(__name__)

# Use the custom TRACE level (more detailed than DEBUG)
logger.trace("This is a trace message - very detailed debugging info")
logger.debug("This is a debug message")
logger.info("This is an info message")
```

### Project-Aware Logging

```python
from dpn_pyutils.logging import initialize_logging, get_logger

# Initialize logging with project name
logging_config = {
    "logging_project_name": "my-awesome-app",
    "version": 1,
    "formatters": {
        "detailed": {
            "()": "logging.Formatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

initialize_logging(logging_config)

# Loggers will now be namespaced under the project
logger = get_logger("database")  # Becomes: my-awesome-app.database
logger.info("Database connection established")

api_logger = get_logger("api.endpoints")  # Becomes: my-awesome-app.api.endpoints
api_logger.info("API request received")
```

### Worker Logger with Context

```python
from dpn_pyutils.logging import get_worker_logger

# Create a worker logger with automatic context injection
worker_log = get_worker_logger("data_processor", worker_id=1, correlation_id="abc-123")

# All log messages will automatically include worker context
worker_log.info("Starting data processing task")
# Output: INFO - data_processor - Starting data processing task [worker:1][corr:abc-123]

worker_log.error("Failed to process data")
# Output: ERROR - data_processor - Failed to process data [worker:1][corr:abc-123]
```

### Contextual Logging with Contextvars

For applications with worker threads or async tasks, use `get_contextual_logger` to automatically propagate context:

```python
from dpn_pyutils.logging import set_logging_context, clear_logging_context, get_contextual_logger

# In worker code - set context once
async def process_task(task_id):
    set_logging_context(worker_id="Worker-1", correlation_id=task_id)
    try:
        await handle_task()
    finally:
        clear_logging_context()

# In any utility module - context automatically included
log = get_contextual_logger(__name__)
async def handle_task():
    log.debug("Processing")  # Includes [worker:Worker-1][corr:task_id]
```

For comprehensive documentation on contextual logging, see [Contextual Logging Guide](./logging-contextual.md).

### Worker Context Configuration

```python
from dpn_pyutils.logging import initialize_logging, get_logger
import logging

# Configuration with worker context support
logging_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "logging_project_name": "app",
    "formatters": {
        "default": {
            "()": "dpn_pyutils.logging.AppLogFormatter",
            "fmt": "%(levelprefix)-8s %(asctime)s.%(msecs)03d [%(threadName)s] %(worker_context)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
            "include_worker_context": True
        },
        "file": {
            "()": "dpn_pyutils.logging.AppLogFormatter",
            "fmt": "%(levelprefix)-8s %(asctime)s.%(msecs)03d [%(threadName)s] %(worker_context)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": False,
            "include_worker_context": True
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "level": "DEBUG",
            "formatter": "file",
            "class": "dpn_pyutils.logging.TimedFileHandler",
            "filename": "/app/output.log",
            "mode": "a",
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
        "propagate": False
    }
}

initialize_logging(logging_config)

# Worker context filter for adding context to log records
class WorkerContextFilter(logging.Filter):
    def __init__(self, worker_id=None, correlation_id=None):
        self.worker_id = worker_id
        self.correlation_id = correlation_id

    def filter(self, record):
        if self.worker_id:
            record.worker_id = self.worker_id
        if self.correlation_id:
            record.correlation_id = self.correlation_id
        return True

# Usage example
logger = get_logger(__name__)
worker_filter = WorkerContextFilter(worker_id="worker-001", correlation_id="req-123")
logger.addFilter(worker_filter)

logger.info("Processing request with worker context")
# Output: INFO     2023-12-01 12:00:00,000 [MainThread] app [worker:worker-001][corr:req-123] Processing request with worker context
```

### Configuration File-Based Setup

```python
from dpn_pyutils.logging import initialize_logging_from_file

# Initialize logging from a JSON configuration file
try:
    initialize_logging_from_file("logging_config.json")
    print("Logging initialized from config file")
except FileNotFoundError as e:
    print(f"Config file not found: {e}")
```

### Safe Logging Initialization

```python
from dpn_pyutils.logging import initialize_logging_safe, get_logger

# Safe initialization - never raises exceptions
logging_config = {
    "version": 1,
    "formatters": {
        "basic": {
            "()": "logging.Formatter",
            "fmt": "%(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "basic"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

initialize_logging_safe(logging_config)

# Now you can safely get loggers
logger = get_logger(__name__)
logger.info("Logging is working safely!")
```

### Advanced Configuration with File Handlers

```python
from dpn_pyutils.logging import initialize_logging

# Complex logging configuration with file rotation
config = {
    "logging_project_name": "web-scraper",
    "version": 1,
    "formatters": {
        "detailed": {
            "()": "logging.Formatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "level": "DEBUG",
            "filename": "logs/scraper.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "scraper.core": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console", "file"]
    }
}

initialize_logging(config)
```

### Exception Handling with Enhanced Logging

```python
import logging
from dpn_pyutils.logging import initialize_logging_from_file, get_logger

# Initialize with better exceptions for debugging
initialize_logging_from_file("logging_config.json")

logger = get_logger(__name__)

def risky_operation():
    try:
        # Some risky operation
        result = 1 / 0  # This will raise ZeroDivisionError
    except Exception as e:
        logger.exception("An error occurred during risky operation")
        # This will log the full traceback with context
        raise

# Usage
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

## Architecture

### Design Philosophy

The logging package is built around several core principles:

1. **Enhanced Standard Library**: Extends Python's `logging` module rather than replacing it
2. **Project Awareness**: Automatic namespacing of loggers under project names
3. **Safety First**: Robust initialization with fallback mechanisms
4. **Context Injection**: Automatic inclusion of worker and correlation IDs
5. **Configuration Flexibility**: Support for both programmatic and file-based configuration

### Core Components

#### Logger Classes
- **`PyUtilsLogger`**: Enhanced logger class with custom TRACE level
- **Standard `logging.Logger`**: Full compatibility with Python's logging system

#### Initialization Functions
- **`initialize_logging()`**: Core logging initialization with full configuration
- **`initialize_logging_from_file()`**: File-based configuration with validation
- **`initialize_logging_safe()`**: Exception-safe initialization with fallbacks

#### Logger Factories
- **`get_logger()`**: Project-aware logger creation
- **`get_logger_fqn()`**: Fully-qualified name logger creation
- **`get_worker_logger()`**: Context-aware logger with worker/correlation IDs

### Custom Log Levels

#### TRACE Level
- **Level**: `logging.DEBUG - 5` (5)
- **Purpose**: Ultra-detailed debugging information
- **Usage**: Internal state, variable values, detailed flow tracing

```python
# The TRACE level is between NOTSET (0) and DEBUG (10)
# NOTSET (0) - TRACE (5) - DEBUG (10) - INFO (20) - WARNING (30) - ERROR (40) - CRITICAL (50)
```

### Project Namespacing

#### Automatic Namespacing
When a project name is configured, all loggers are automatically namespaced:

```python
# Without project name: "database", "api", "utils"
# With project name "myapp": "myapp.database", "myapp.api", "myapp.utils"
```

#### Benefits
- **Hierarchical Organization**: Clear module relationships
- **Filtering**: Easy filtering by project or module
- **Multi-tenancy**: Support for multiple applications in same process

### Configuration Schema

#### Supported Configuration
The logging system supports the full Python `logging.config` dictionary schema plus:

```python
{
    "logging_project_name": "my-project",  # Optional project namespace
    "version": 1,
    "formatters": {...},
    "handlers": {...},
    "loggers": {...},
    "root": {...}
}
```

#### Validation
- **Schema Validation**: Uses Pydantic models for configuration validation
- **File Validation**: Validates configuration files before applying
- **Error Reporting**: Clear error messages for configuration issues

### State Management

#### Initialization State
- **`is_initialized()`**: Check if logging has been initialized
- **`set_initialized()`**: Mark logging as initialized
- **`reset_state()`**: Reset logging state (for testing)

#### Project Name Management
- **`get_project_name()`**: Retrieve current project name
- **`set_project_name()`**: Set project name for namespacing

### Integration Features

#### Better Exceptions Integration
- **Enhanced Tracebacks**: Integration with `better_exceptions` for improved error display
- **Warning Capture**: Automatic capture of Python warnings into logging
- **Context Preservation**: Maintains logging context across exceptions

#### File Handler Utilities
- **Directory Creation**: Automatic creation of log directories
- **Path Validation**: Validation of log file paths before configuration
- **Atomic Configuration**: Safe application of logging configuration

### Performance Characteristics

#### Initialization Performance
- **Lazy Loading**: Loggers created only when first requested
- **Configuration Caching**: Configuration applied once and cached
- **Minimal Overhead**: Negligible performance impact on logger creation

#### Runtime Performance
- **Efficient Formatting**: Optimized log message formatting
- **Context Injection**: Minimal overhead for context inclusion
- **Async Safety**: Thread-safe logger operations

### Error Handling Strategy

#### Initialization Errors
1. **Validation Errors**: Clear messages for configuration issues
2. **File Errors**: Helpful messages for missing or invalid config files
3. **Fallback Mechanism**: Automatic fallback to basic console logging

#### Runtime Errors
1. **Exception Safety**: Logging operations never raise exceptions
2. **Context Preservation**: Maintains logging context during errors
3. **Graceful Degradation**: Continues operation even with logging issues

### Best Practices

#### Logger Naming
```python
# ✅ Good: Use module names for clear hierarchy
logger = get_logger(__name__)  # e.g., "myapp.database.connection"

# ✅ Good: Use descriptive component names
api_logger = get_logger("api.endpoints")
db_logger = get_logger("database.pool")

# ❌ Avoid: Generic names
generic_logger = get_logger("logger")  # Too vague
```

#### Configuration Management
```python
# ✅ Good: Environment-specific configuration
if environment == "production":
    config_file = "logging_prod.json"
else:
    config_file = "logging_dev.json"

initialize_logging_from_file(config_file)

# ✅ Good: Safe initialization in entry points
def main():
    initialize_logging_safe(basic_config)
    # Application code here
```

#### Context Usage
```python
# ✅ Good: Use worker loggers for tracked operations
def process_task(task_id, worker_id):
    logger = get_worker_logger("task_processor", worker_id, task_id)
    logger.info("Starting task processing")
    # ... processing ...
    logger.info("Task completed")
```

### Advanced Examples

#### Structured Logging

```python
import json
import logging
from dpn_pyutils.logging import get_logger

class StructuredLogger:
    def __init__(self, name):
        self.logger = get_logger(name)

    def log_structured(self, level, message, **kwargs):
        # Create structured log entry
        log_entry = {
            "message": message,
            "level": level,
            **kwargs
        }

        self.logger.log(level, json.dumps(log_entry))

# Usage
structured_logger = StructuredLogger("api")
structured_logger.log_structured(
    logging.INFO,
    "User login",
    user_id="12345",
    ip_address="192.168.1.1",
    success=True
)
```

#### Logging in Distributed Systems

```python
from dpn_pyutils.logging import get_worker_logger, initialize_logging

# Initialize with project name for microservice
initialize_logging({
    "logging_project_name": "user-service",
    "version": 1,
    # ... other config
})

def handle_request(request_id, user_id):
    # Worker logger with request context
    logger = get_worker_logger(
        "user_service.handlers",
        worker_id="worker-001",
        correlation_id=request_id
    )

    logger.info("Processing user request", extra={"user_id": user_id})

    try:
        # Process request
        result = process_user_data(user_id)
        logger.info("Request processed successfully", extra={"result": result})
        return result
    except Exception as e:
        logger.error("Request processing failed", extra={"error": str(e)})
        raise
```

#### Testing with Logging

```python
import logging
from unittest.mock import patch
from dpn_pyutils.logging import get_logger

def test_with_mocked_logging():
    logger = get_logger("test_module")

    with patch.object(logger, 'info') as mock_info:
        # Test code that logs
        some_function()

        # Verify logging calls
        mock_info.assert_called_with("Expected log message")

def test_logging_configuration():
    """Test that logging is properly configured."""
    from dpn_pyutils.logging import is_logging_initialized

    assert is_logging_initialized() == True

    logger = get_logger("test")
    assert logger is not None
    assert hasattr(logger, 'trace')  # Custom TRACE method
```

This comprehensive logging package provides enterprise-grade logging capabilities while maintaining simplicity and compatibility with Python's standard logging ecosystem.
