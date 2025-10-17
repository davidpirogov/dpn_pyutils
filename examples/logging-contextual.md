# Contextual Logging with Contextvars

## Overview

The contextual logging system solves the problem of disjointed log output when worker threads call utility modules that don't have access to worker-specific loggers. Instead of passing logger parameters to every function, we use Python's `contextvars` to automatically propagate context information.

## The Problem

Before contextual logging, worker logs had context but utility module logs didn't:

```python
# Before - Disjointed logs
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.worker.thread Processing task
DEBUG [DataThread] app.lib.dataframes Getting data  # ❌ No context!
DEBUG [DataThread] app.lib.dataframes Read 4467 bytes  # ❌ No context!
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.worker.thread Task completed
```

## The Solution

With contextual logging, all logs within a worker context automatically include context:

```python
# After - Unified logs
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.worker.thread Processing task
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.lib.dataframes Getting data  # ✅ Has context!
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.lib.dataframes Read 4467 bytes  # ✅ Has context!
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.worker.thread Task completed
```

## Quick Start

### 1. In Worker Code (Set Context Once)

```python
# In thread.py or any worker code
from dpn_pyutils.logging import set_logging_context, clear_logging_context

async def _worker(self, worker_name: str) -> None:
    while not self.shutdown_event.is_set():
        task = await self.work_queue.get()

        # Set context at the START of task processing
        set_logging_context(worker_name, task.id)

        try:
            # Process the task - all code called here has context!
            result = await self.process_task(task)
        finally:
            # Clear context at the END
            clear_logging_context()
```

### 2. In Utility Modules (Use Contextual Logger)

```python
# In dataframes.py, coverage_analyzer.py, storage modules, etc.
from dpn_pyutils.logging import get_contextual_logger

# Change from:
# from dpn_pyutils.logging import get_logger
# log = get_logger(__name__)

# To:
log = get_contextual_logger(__name__)

# That's it! No other changes needed.
# The logger automatically includes context when available.

async def get_dataframe(storage: StorageBackend, file_path: Path) -> pd.DataFrame:
    # This log now includes worker context automatically!
    log.debug(f"Getting dataframe from {file_path}")

    data = await storage.read_file(file_path)
    log.debug(f"Read {len(data)} bytes")

    return pd.read_parquet(BytesIO(data))
```

## Core Concepts

### Context Variables

The system uses Python's `contextvars` module to store worker metadata:

- `worker_id`: Worker identifier (e.g., "Worker-0")
- `correlation_id`: Correlation ID (typically task ID UUID)

These variables are:

- **Thread-safe**: Isolated per thread
- **Async-safe**: Isolated per async task
- **Automatic**: No manual passing required

### Key Functions

- `set_logging_context(worker_id, correlation_id)`: Set context at task start
- `clear_logging_context()`: Clear context at task end
- `get_contextual_logger(module_name)`: Get logger with automatic context
- `get_logging_context()`: Retrieve current context values
- `has_logging_context()`: Check if context is set

## Usage Patterns

### Worker Thread Setup

```python
async def _read_worker(self, worker_name: str) -> None:
    while not self.shutdown_event.is_set():
        try:
            task = await asyncio.wait_for(self.read_queue.get(), timeout=1.0)

            # Set context at the start of task processing
            set_logging_context(worker_name, task.id)

            try:
                # All code within this block has access to context
                result = await self.workflow_manager.process_task(task)
            finally:
                # Always clear context when done
                clear_logging_context()

        except Exception as e:
            log.error(f"Error: {e}")
            clear_logging_context()  # Clear on error too
```

### Utility Module Usage

```python
# In any module (e.g., dataframes.py, coverage_analyzer.py, etc.)
from dpn_pyutils.logging import get_contextual_logger


async def get_dataframe(storage: StorageBackend, file_path: Path) -> pd.DataFrame:
    # This log will automatically include worker and correlation context
    # if called within a worker context, otherwise logs normally
    log.debug(f"Getting dataframe from {file_path}")

    data = await storage.read_file(file_path)
    log.debug(f"Read {len(data)} bytes from {file_path}")

    return pd.read_parquet(BytesIO(data))
```

## Configuration

### Formatter Setup

Configure your formatter to include worker context:

```python
from dpn_pyutils.logging import initialize_logging

logging_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "logging_project_name": "app",
    "formatters": {
        "default": {
            "()": "dpn_pyutils.logging.formatters.AppLogFormatter",
            "fmt": "%(levelprefix)-8s %(asctime)s.%(msecs)03d [%(threadName)s] %(worker_context)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
            "include_worker_context": True
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
        "propagate": False
    }
}

initialize_logging(logging_config)
```

### Format String Options

The formatter supports three context-related format fields:

- `%(worker_context)s`: Combined context string (e.g., `[worker:Worker-1][corr:abc-123]`)
- `%(worker_id)s`: Individual worker ID field
- `%(correlation_id)s`: Individual correlation ID field

#### Using Combined Context String

```python
"fmt": "%(levelname)s - %(worker_context)s - %(message)s"
# Output: INFO - [worker:Worker-1][corr:abc-123] - Processing task
```

#### Using Individual Fields

```python
"fmt": "%(levelname)s - %(worker_id)s - %(correlation_id)s - %(message)s"
# Output: INFO - Worker-1 - abc-123 - Processing task
```

#### Custom Format Examples

```python
# Minimal format with just correlation ID
"fmt": "%(levelname)s - %(correlation_id)s - %(message)s"
# Output: INFO - abc-123 - Processing task

# Structured format with individual fields
"fmt": "%(asctime)s [%(worker_id)s] %(correlation_id)s %(message)s"
# Output: 2023-12-01 12:00:00 [Worker-1] abc-123 Processing task

# JSON-like format
"fmt": "%(levelname)s worker=%(worker_id)s task=%(correlation_id)s msg=%(message)s"
# Output: INFO worker=Worker-1 task=abc-123 msg=Processing task
```

**Note**: When using individual fields (`%(worker_id)s`, `%(correlation_id)s`), the values will be `None` when no context is set, which will display as "None" in the log output.

### Using Different Logger Types

- **`get_worker_logger(module, worker_id, correlation_id)`**: Explicit parameters, always includes context
- **`get_contextual_logger(module)`**: Contextvars-based, includes context only when set

## Benefits

### 1. No Parameter Passing

- Utility functions don't need logger parameters
- Cleaner function signatures
- Easier to maintain and refactor

### 2. Thread-Safe and Async-Safe

- `contextvars` are isolated per async task
- No risk of context leaking between concurrent tasks
- Works correctly with asyncio, threading, and concurrent.futures

### 3. Graceful Degradation

- If no context is set, `get_contextual_logger()` returns a standard logger
- Existing code works without modification
- Modules can be used both inside and outside worker contexts

### 4. Unified Log Output

All logs now include consistent context:

```text
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.worker.thread Processing task
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.lib.dataframes Getting dataframe
DEBUG [DataThread] [worker:Worker-0][corr:57b844e5] app.lib.dataframes Read 4467 bytes
```

## Migration Guide

### For Existing Modules

1. **Replace logger import:**

    ```python
    # Old
    from dpn_pyutils.logging import get_logger
    log = get_logger(__name__)

    # New
    from dpn_pyutils.logging import get_contextual_logger
    log = get_contextual_logger(__name__)
    ```

2. **No other changes needed** - The logger interface remains the same

### For New Worker Methods

1. **Set context at task start:**

    ```python
    set_logging_context(worker_name, task.id)
    ```

2. **Clear context in finally block:**
    ```python
    try:
        # Process task
        pass
    finally:
        clear_logging_context()
    ```

## Best Practices

### 1. Always Use Finally Blocks

```python
try:
    set_logging_context(worker_name, task_id)
    # Process task
finally:
    clear_logging_context()  # Ensures cleanup even on exception
```

### 2. Clear Context on Errors

```python
except Exception as e:
    log.error(f"Error: {e}")
    clear_logging_context()  # Don't let context leak to next task
```

### 3. Check Context When Needed

```python
from dpn_pyutils.logging import has_logging_context

if has_logging_context():
    # We're in a worker context
    log.debug("Processing in worker context")
else:
    # We're in a non-worker context (e.g., startup, testing)
    log.debug("Processing outside worker context")
```

### 4. Module-Level Logger Declaration

Declare loggers at module level for best performance:

```python
from dpn_pyutils.logging import get_contextual_logger

# Module-level declaration - context is evaluated at log time
log = get_contextual_logger(__name__)

def my_function():
    # Use module-level logger - context is automatically included when available
    log.debug("Processing")
```

## Testing

### Unit Tests

```python
from dpn_pyutils.logging import (
    set_logging_context,
    clear_logging_context,
    get_logging_context,
    get_contextual_logger,
)

def test_contextual_logging():
    # Initially no context
    assert get_logging_context() == (None, None)

    # Set context
    set_logging_context("TestWorker", "test-123")
    worker_id, corr_id = get_logging_context()
    assert worker_id == "TestWorker"
    assert corr_id == "test-123"

    # Get contextual logger
    log = get_contextual_logger(__name__)
    # Verify it's a LoggerAdapter with context
    assert hasattr(log, 'extra')

    # Clear context
    clear_logging_context()
    assert get_logging_context() == (None, None)
```

### Integration Tests

Test that context propagates through the call stack:

```python
async def test_context_propagation():
    set_logging_context("Worker-1", "task-xyz")

    # Call a function that uses get_contextual_logger
    result = await get_dataframe(storage, path)

    # Verify logs include context (check log output)
    # ...

    clear_logging_context()
```

## Troubleshooting

### Context Not Appearing in Logs

1. **Check formatter configuration** - Ensure your log formatter includes `worker_id` and `correlation_id` fields
2. **Verify context is set** - Use `get_logging_context()` to check
3. **Check module uses get_contextual_logger** - Not `get_logger`

### Context Leaking Between Tasks

1. **Ensure clear_logging_context is called** - Use finally blocks
2. **Check for missing exception handling** - Clear context in except blocks too
3. **Verify async task isolation** - Context should not leak in properly configured async code

### Performance Issues

1. **Declare loggers at module level** - Don't create new loggers in hot paths
2. **Avoid excessive logging** - Use appropriate log levels
3. **Profile if needed** - Context variable access is very fast, but check if logging itself is the issue

## Advanced Topics

### Context Manager Pattern

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def logging_context(worker_id: str, correlation_id: str):
    """Context manager for automatic context lifecycle."""
    set_logging_context(worker_id, correlation_id)
    try:
        yield
    finally:
        clear_logging_context()

# Usage
async def process_task(task):
    async with logging_context("Worker-1", task.id):
        # All code here has context
        await do_work(task)
```

### Additional Context Fields

The system can be extended to support additional context fields:

```python
# Future enhancement example
def set_extended_logging_context(worker_id: str, correlation_id: str, user_id: str = None, request_id: str = None):
    """Extended context with additional fields."""
    set_logging_context(worker_id, correlation_id)
    # Additional context variables could be added here
```

### Distributed Tracing Integration

Context can be integrated with distributed tracing systems:

```python
def set_tracing_context(worker_id: str, correlation_id: str, trace_id: str = None):
    """Set logging context with distributed tracing support."""
    set_logging_context(worker_id, correlation_id)
    if trace_id:
        # Set trace context for distributed tracing
        pass
```

## Technical Details

### Lazy Context Evaluation

The `ContextualLoggerAdapter` solves the module-level instantiation problem by evaluating contextvars at log time, not at logger creation time:

```python
class ContextualLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        """Process the log record to inject context at log time."""
        # Get current context at log time
        worker_id, correlation_id = get_logging_context()

        # Add context to the extra dict
        extra = kwargs.get('extra', {})
        extra['worker_id'] = worker_id
        extra['correlation_id'] = correlation_id
        kwargs['extra'] = extra

        return msg, kwargs
```

This allows:

- **Module-level instantiation**: `log = get_contextual_logger(__name__)` at module top
- **Runtime context evaluation**: Context is checked when `log.debug()` is called
- **No performance penalty**: Contextvars access is extremely fast
- **Custom format support**: Works with both `%(worker_context)s` and individual `%(worker_id)s`/`%(correlation_id)s` fields

The `ContextualLoggerAdapter` overrides the `_log` method to inject context directly into the log record's `extra` dict, making the context fields available to any formatter that references them.

### Context Variable Isolation

Context variables provide automatic isolation:

```python
# Task 1 (running concurrently)
set_logging_context("Worker-1", "uuid-1")
log.debug("Task 1")  # Shows [worker:Worker-1][corr:uuid-1]

# Task 2 (running concurrently)
set_logging_context("Worker-2", "uuid-2")
log.debug("Task 2")  # Shows [worker:Worker-2][corr:uuid-2]

# No interference between concurrent tasks!
```

### Performance Considerations

- Context variable access is extremely fast (similar to thread-local storage)
- No overhead when context is not set
- No locks or synchronization needed
- Minimal memory footprint

### Compatibility

- **Python Version**: Requires Python 3.7+ (contextvars introduced in 3.7)
- **Async**: Full support for asyncio
- **Threading**: Works correctly with threading.Thread
- **Concurrent Futures**: Works with ThreadPoolExecutor and ProcessPoolExecutor

## Conclusion

The contextual logging implementation provides a clean, Pythonic solution for propagating worker metadata throughout the application. By leveraging `contextvars`, we achieve:

- **Cleaner code** - No logger parameter passing
- **Better logs** - Unified context across all modules
- **Type safety** - Thread-safe and async-safe by design
- **Performance** - Minimal overhead
- **Maintainability** - Easy to extend and debug

This approach follows Python 3.12+ best practices and provides a solid foundation for scalable, production-ready logging.
