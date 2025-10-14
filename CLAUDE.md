# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OPC UA Smart Reader & Writer v2.0 - A modular Python package for working with OPC UA servers with automatic type detection. Optimized for speed (~0.3 seconds).

**Key Features:**
- Modular architecture with clean separation of concerns
- Automatic OPC UA type detection and formatting
- TypeCache for optimized repeated reads
- Support for complex data types (ExtensionObjects, arrays, bitmasks, enums)
- Both high-level API (OPCUAReader class) and low-level functions
- Backward compatibility with old API

## Development Commands

### Running Tests
```bash
# Run all tests (includes both async and sync tests)
python test_opcua.py

# For pytest (if installed)
pytest test_opcua.py -v
```

### Running Examples
```bash
# CLI reading (single node)
python opcua_reader.py opc.tcp://server:4840 --node cepn1

# CLI reading (all nodes, JSON format)
python opcua_reader.py opc.tcp://server:4840 --format json

# Combined reader + writer example
python main.py

# Test reading from specific server
python opcua_reader.py opc.tcp://10.15.194.150:4840 --node cepn1 --debug
```

### Python Environment
```bash
# Activate virtual environment (if exists)
source venv/bin/activate

# Install dependencies
pip install asyncua
```

## Architecture

### Module Structure

The codebase follows a **modular architecture** where each module has a single responsibility:

```
opcua/                     # Core package
├── common.py             # Constants (TARGET_OBJECT_NAME, DEFAULT_MAX_DEPTH)
├── cache.py              # TypeCache class - caches type metadata
├── navigator.py          # Tree navigation - finding objects/nodes
├── parser.py             # Value parsing - format_value, ExtensionObject handling
├── formatter.py          # Output formatting (JSON, Tree)
└── reader.py             # OPCUAReader class + read functions

opcua_reader.py           # CLI entry point for reading
opcua_writer.py           # Writer module with write_values()
test_opcua.py             # Test suite
main.py                   # Example combining reader + writer
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

### Reading Pattern (Recommended)
```python
async with OPCUAReader(url) as reader:
    data = await reader.read_node("cepn1")
```

### Writing Pattern
```python
async with Client(url) as client:
    results = await write_values(client, {
        "cepn1.sensor1": 1,
        "valve1.position": 50
    })
```

### Legacy API (Backward Compatibility)
```python
from opcua import find_specific_object, find_and_read_variable, TypeCache
cache = TypeCache()
async with Client(url) as client:
    root = client.nodes.objects
    epac = await find_specific_object(root, "ePAC:Project")
    data = await find_and_read_variable(epac, "cepn1", client, cache)
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
