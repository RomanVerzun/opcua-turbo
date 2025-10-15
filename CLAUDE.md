# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OPC UA Smart Reader & Writer v2.1 - A modular Python package for working with OPC UA servers with automatic type detection. Optimized for speed (~0.3 seconds).

**Key Features:**
- Modern src/ layout architecture with clean layering
- Automatic OPC UA type detection and formatting
- TypeCache with LRU eviction for optimized repeated reads
- Support for complex data types (ExtensionObjects, arrays, bitmasks, enums)
- Both OPCUAReader and OPCUAWriter classes with context manager support
- Full backward compatibility with v2.0 through compatibility wrappers
- Comprehensive test suite with pytest
- Rich examples demonstrating all features

## Development Commands

### Running Tests
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run all tests with pytest
pytest tests/ -v

# Run specific test
pytest tests/test_opcua.py::test_reader_connect

# Run with coverage
pytest --cov=src/opcua tests/

# Run tests without pytest (standalone)
python tests/test_opcua.py
```

### Running Examples
```bash
# Simple reader example
python examples/simple_reader.py

# Simple writer example
python examples/simple_writer.py

# Combined operations (comprehensive example)
python examples/combined_operations.py

# Old CLI interface (deprecated but still works)
python opcua_reader.py opc.tcp://server:4840 --node cepn1
```

### Python Environment
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install in editable mode
pip install -e .
```

## Architecture

### Module Structure

The codebase follows a **modern src/ layout** with layered architecture:

```
src/opcua/                     # Main package (v2.1)
├── __init__.py               # Public API exports
├── core/                     # Core functionality
│   ├── common.py            # Constants, type aliases
│   ├── cache.py             # TypeCache with LRU
│   └── type_conversion.py   # Python ↔ OPC UA type conversion
├── client/                   # OPC UA clients
│   ├── reader.py            # OPCUAReader class
│   └── writer.py            # OPCUAWriter class + write_values()
├── navigation/               # Tree navigation
│   └── navigator.py         # find_node_by_path, find_specific_object, etc.
└── parsing/                  # Value parsing & formatting
    ├── parser.py            # format_value, parse_extension_object
    └── formatter.py         # JSONFormatter, TreeFormatter

opcua/                        # Legacy package (compatibility wrapper)
opcua_writer.py              # Legacy module (compatibility wrapper)
tests/                       # Test suite
├── conftest.py              # pytest fixtures
└── test_opcua.py           # Main tests
examples/                    # Usage examples
├── simple_reader.py
├── simple_writer.py
└── combined_operations.py
```

### Key Architectural Patterns

**1. Context Manager Pattern (Reader)**
- `OPCUAReader` implements async context manager (`__aenter__`/`__aexit__`)
- Automatically handles connect/disconnect lifecycle
- Preferred usage pattern in examples

**2. Parallel Processing**
- Navigator uses `asyncio.gather()` for parallel node traversal
- Reader uses parallel reads for multiple nodes
- Critical for achieving ~0.3 second performance

**3. Type Caching**
- `TypeCache` stores field names and type definitions
- Reduces server roundtrips on repeated reads
- Tracks hit/miss statistics via `get_stats()`

**4. Path-Based Navigation**
- Writer uses dot-notation paths: `"cepn1.sensor1"`
- `find_node_by_path()` traverses from root object through hierarchy
- Supports both BrowseName and DisplayName matching

**5. Automatic Type Detection**
- `format_value()` in parser.py handles all type conversions
- Detects arrays, ExtensionObjects, bitmasks, enums
- Uses metadata (data_type, value_rank, array_dimensions)

### Data Flow

**Reading Flow:**
1. `OPCUAReader.connect()` → finds target object (default: "ePAC:Project")
2. `read_node(name)` → calls `find_and_read_variable()`
3. `read_object_children()` → parallel reads of all child variables
4. `format_value()` → automatic type detection and formatting
5. Returns nested dict structure

**Writing Flow:**
1. `write_values(client, data)` → groups writes by parent node
2. For each path: `find_node_by_path()` → traverses tree
3. Array optimization: reads current array, modifies fields, writes once
4. Type conversion: `get_node_variant_type()` + `python_to_variant()`
5. Returns dict of success/failure per path

## Important Implementation Details

### Target Object
- Default root object: `"ePAC:Project"` (configurable via TARGET_OBJECT_NAME)
- All navigation starts from this object under Objects node
- Can be overridden in OPCUAReader constructor or write_values()

### Array Handling in Writer
- Detects if parent node is array by reading current value
- Optimizes multi-field array writes: single write operation for all fields
- Uses `_get_array_field_index()` to map field names to array indices
- Falls back to individual writes for non-arrays

### Type Cache Strategy
- Caches at two levels: datatype definitions and field names
- Key types cached: node_id → field_names mapping
- Cache persists for lifetime of OPCUAReader instance
- Statistics available via `get_cache_stats()`

### Error Handling Philosophy
- Silent failures in navigation (returns None)
- Exceptions caught at high level (reader methods, write_values)
- Writer returns success/failure dict per path
- Debug mode available in CLI (`--debug` flag)

### ExtensionObject Parsing
- Uses `__dict__` inspection for custom OPC UA types
- Maps indices to field names when available
- Falls back to generic structure if field names unknown
- Supports nested ExtensionObjects

## Common Patterns

### Reading Pattern (Recommended - v2.1)
```python
from src.opcua import OPCUAReader

async with OPCUAReader(url) as reader:
    data = await reader.read_node("cepn1")
```

### Writing Pattern (Recommended - v2.1)
```python
from src.opcua import OPCUAWriter

async with OPCUAWriter(url) as writer:
    results = await writer.write({
        "cepn1.sensor1": 1,
        "valve1.position": 50
    })
```

### Alternative Writing Pattern (low-level)
```python
from src.opcua import write_values
from asyncua import Client

async with Client(url) as client:
    results = await write_values(client, {
        "cepn1.sensor1": 1,
        "valve1.position": 50
    })
```

### Legacy API (Backward Compatibility - deprecated)
```python
# This still works but shows deprecation warnings
from opcua import OPCUAReader, TypeCache
from opcua_writer import write_values

# Internally redirects to src.opcua
async with OPCUAReader(url) as reader:
    data = await reader.read_node("cepn1")
```

## Testing Notes

- Tests use live OPC UA server at `opc.tcp://10.15.194.150:4840`
- Test node: `"cepn1"` with fields like `test`, `sensor1`, `frequency`
- Tests cover: connection, context manager, read/write cycles, cache stats
- Can run without pytest (has built-in test runner in `__main__`)

## Performance Considerations

- **Parallel reads**: Key to ~0.3s performance - uses asyncio.gather extensively
- **Type caching**: Reduces metadata lookups on repeated operations
- **Breadth-first search**: Navigator checks current level before recursing
- **Array optimization**: Writer coalesces multiple array field writes into one operation

## Notes for AI Assistants

- This is an **industrial automation** tool (OPC UA is IEC 62541 standard)
- Default server in examples may not be accessible - update SERVER_URL as needed
- The codebase is in **Ukrainian** (comments, docstrings, error messages)
- When adding features, maintain the modular structure - don't mix concerns
- Always use parallel operations (asyncio.gather) for multiple node operations
- Test with actual OPC UA server - consider using open source servers like FreeOpcUa
