# Changelog

All notable changes to OPC UA Smart Reader & Writer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2025-10-15

### Added

#### Architecture
- **Modern src/ layout**: Reorganized codebase into `src/opcua/` package structure
- **Layered architecture** with clear separation of concerns:
  - `core/` - Common utilities, cache, type conversion
  - `client/` - OPCUAReader and OPCUAWriter classes
  - `navigation/` - Tree navigation functions
  - `parsing/` - Value parsing and output formatting

#### New Features
- **OPCUAWriter class** with context manager support (mirrors OPCUAReader API)
  ```python
  async with OPCUAWriter(url) as writer:
      await writer.write({"cepn1.sensor1": 1})
  ```
- **Comprehensive test suite** with pytest support
  - Run with: `pytest tests/ -v`
  - Standalone mode: `python tests/test_opcua.py`
  - Coverage support: `pytest --cov=src/opcua tests/`

#### Examples
- Added `examples/` directory with three complete examples:
  - `simple_reader.py` - Basic reading with context manager
  - `simple_writer.py` - Basic writing with context manager
  - `combined_operations.py` - Full read-write-read cycle with stats

#### Documentation
- `docs/API.md` - Complete API reference with all classes and functions
- `docs/ARCHITECTURE.md` - In-depth architecture documentation with:
  - Layer breakdown and responsibilities
  - Data flow diagrams
  - Design patterns used
  - Performance optimizations explained
  - Extension points for customization
- Updated `README.md` with v2.1 examples and migration guide
- Updated `USAGE.md` with new import patterns
- Updated `CLAUDE.md` with v2.1 architecture details

#### Backward Compatibility
- **Full backward compatibility** with v2.0 through compatibility wrappers
- Legacy imports still work with deprecation warnings:
  ```python
  from opcua import OPCUAReader  # Works, but shows warning
  from opcua_writer import write_values  # Works, but shows warning
  ```
- Wrappers redirect to new `src.opcua` package

### Changed

#### Reorganization
- Moved all core code into `src/opcua/` package
- Split monolithic modules into focused submodules:
  - `opcua/reader.py` → `src/opcua/client/reader.py` + extracted helper functions
  - `opcua/writer.py` → `src/opcua/client/writer.py`
  - `opcua/cache.py` → `src/opcua/core/cache.py`
  - `opcua/navigator.py` → `src/opcua/navigation/navigator.py`
  - `opcua/parser.py` → `src/opcua/parsing/parser.py`
  - `opcua/formatter.py` → `src/opcua/parsing/formatter.py`
  - `opcua/common.py` → `src/opcua/core/common.py`
  - New: `src/opcua/core/type_conversion.py` (extracted from writer.py)

#### Improved Organization
- Created `tests/` directory for all test files
  - `test_opcua.py` moved from root to `tests/`
  - Added `conftest.py` for pytest fixtures
- Created `examples/` directory for usage examples
  - Replaced `main.py` with three focused examples
- Created `docs/` directory for documentation
  - Separated API docs from README
  - Added architecture documentation

#### Import Paths (Recommended)
- **New (v2.1)**: `from src.opcua import OPCUAReader, OPCUAWriter`
- **Old (v2.0)**: `from opcua import OPCUAReader` (still works, deprecated)

### Fixed
- Improved error messages in navigation functions
- Better handling of missing nodes
- Consistent async/await patterns throughout

### Performance
- No performance changes (maintains ~0.3 second read time)
- All optimizations from v2.0 preserved:
  - Parallel node reads with asyncio.gather
  - TypeCache with LRU eviction
  - Array write optimization

### Deprecated
- `opcua/` package as import source (use `src.opcua` instead)
- `opcua_writer.py` module (use `from src.opcua import write_values` or `OPCUAWriter`)
- These will be removed in v3.0

---

## [2.0.0] - 2024-XX-XX

### Added
- **OPCUAReader class** with context manager support
- **TypeCache** with LRU eviction strategy (max 1000 entries)
- **Automatic type detection** for all OPC UA types:
  - ExtensionObjects with field name resolution
  - Arrays and multidimensional arrays
  - Bitmasks with flag unpacking
  - Enumerations
  - DateTime, ByteString, etc.
- **write_values()** function for writing to OPC UA servers
  - Dot-notation paths: `"cepn1.sensor1"`
  - Automatic type conversion
  - Array optimization (batch writes)
- **CLI interface** via `opcua_reader.py`
  - Read single node: `--node cepn1`
  - Read all nodes (no flag)
  - Output formats: `--format tree|json`
  - Debug mode: `--debug`
- **Output formatters**:
  - TreeFormatter (default) - Unicode tree view
  - JSONFormatter - Indented JSON

### Performance
- **~0.3 second read time** achieved through:
  - Parallel node reads with asyncio.gather
  - TypeCache reduces server roundtrips by ~80%
  - Breadth-first search finds nodes faster
  - Array write optimization (N writes → 1 write)

### Architecture
- Modular design with separation of concerns:
  - `opcua/common.py` - Constants
  - `opcua/cache.py` - TypeCache
  - `opcua/navigator.py` - Tree navigation
  - `opcua/parser.py` - Value parsing
  - `opcua/formatter.py` - Output formatting
  - `opcua/reader.py` - OPCUAReader class
  - `opcua_writer.py` - Write functions

---

## [1.0.0] - 2024-XX-XX (Pre-history)

Initial version with basic read functionality (not documented in detail).

---

## Migration Guides

### Migrating from v2.0 to v2.1

**No breaking changes!** Your existing code continues to work.

#### Option 1: Keep using old imports (will show warnings)
```python
from opcua import OPCUAReader  # DeprecationWarning
from opcua_writer import write_values  # DeprecationWarning
```

#### Option 2: Update to new imports (recommended)
```python
# Old
from opcua import OPCUAReader, TypeCache
from opcua_writer import write_values

# New
from src.opcua import OPCUAReader, OPCUAWriter, TypeCache, write_values
```

#### New Features Available in v2.1

**Use OPCUAWriter class** (cleaner than raw write_values):
```python
# Old way
from opcua_writer import write_values
from asyncua import Client

async with Client(url) as client:
    results = await write_values(client, {"cepn1.test": 1})

# New way
from src.opcua import OPCUAWriter

async with OPCUAWriter(url) as writer:
    results = await writer.write({"cepn1.test": 1})
```

**Run tests**:
```bash
# Old
python test_opcua.py

# New (both work)
python tests/test_opcua.py
pytest tests/ -v
```

**Run examples**:
```bash
# Old
python main.py

# New
python examples/simple_reader.py
python examples/simple_writer.py
python examples/combined_operations.py
```

### Preparing for v3.0

v3.0 will remove compatibility wrappers. To prepare:

1. Update imports from `opcua` to `src.opcua`
2. Update imports from `opcua_writer` to `src.opcua`
3. Consider switching to `OPCUAWriter` class instead of `write_values()` function
4. Run tests to verify everything still works
5. Address any DeprecationWarnings

---

## Version History Summary

| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| 2.1.0   | 2025-10-15  | src/ layout, OPCUAWriter class, comprehensive docs |
| 2.0.0   | 2024-XX-XX  | OPCUAReader class, TypeCache, ~0.3s performance |
| 1.0.0   | 2024-XX-XX  | Initial release |

---

**Links:**
- [Repository](https://github.com/yourusername/opcua-turbo) (if applicable)
- [Documentation](./README.md)
- [API Reference](./docs/API.md)
- [Architecture Guide](./docs/ARCHITECTURE.md)
