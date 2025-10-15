# OPC UA Smart Reader & Writer - API Documentation

## Table of Contents

1. [Client Classes](#client-classes)
   - [OPCUAReader](#opcuareader)
   - [OPCUAWriter](#opcuawriter)
2. [Core Functions](#core-functions)
   - [write_values](#write_values)
   - [find_and_read_variable](#find_and_read_variable)
   - [read_object_children](#read_object_children)
3. [Navigation Functions](#navigation-functions)
4. [Parsing & Formatting](#parsing--formatting)
5. [Type Cache](#type-cache)
6. [Type System](#type-system)

---

## Client Classes

### OPCUAReader

Client class for reading data from OPC UA servers.

#### Constructor

```python
OPCUAReader(
    url: str,
    target_object: str = "ePAC:Project",
    timeout: float = 30.0
)
```

**Parameters:**
- `url` (str): OPC UA server URL (must start with "opc.tcp://")
- `target_object` (str): Target root object name. Default: "ePAC:Project"
- `timeout` (float): Connection and operation timeout in seconds. Default: 30.0

**Raises:**
- `ValueError`: If URL is invalid or doesn't start with "opc.tcp://"

#### Methods

##### connect()

```python
async def connect() -> None
```

Connect to the OPC UA server.

**Raises:**
- `RuntimeError`: If connection times out

**Example:**
```python
reader = OPCUAReader("opc.tcp://server:4840")
await reader.connect()
```

##### disconnect()

```python
async def disconnect() -> None
```

Disconnect from the OPC UA server.

##### read_node()

```python
async def read_node(node_name: str, max_depth: int = DEFAULT_MAX_DEPTH) -> Optional[Dict[str, Any]]
```

Read a specific node and all its children.

**Parameters:**
- `node_name` (str): Name of the node to read
- `max_depth` (int): Maximum recursion depth. Default: 10

**Returns:**
- `Dict[str, Any]`: Dictionary with node data, or `None` if not found

**Example:**
```python
data = await reader.read_node("cepn1")
# Returns: {"cepn1": {"field1": value1, "field2": value2, ...}}
```

##### read_all()

```python
async def read_all(max_depth: int = DEFAULT_MAX_DEPTH) -> Dict[str, Dict[str, Any]]
```

Read all available nodes.

**Parameters:**
- `max_depth` (int): Maximum recursion depth. Default: 10

**Returns:**
- `Dict[str, Dict[str, Any]]`: Dictionary with all nodes data

**Example:**
```python
all_data = await reader.read_all()
# Returns: {"node1": {...}, "node2": {...}, ...}
```

##### get_cache_stats()

```python
def get_cache_stats() -> Dict[str, Any]
```

Get type cache statistics.

**Returns:**
- Dictionary with keys: `hits`, `misses`, `total`, `hit_rate`, `datatype_definitions`, `field_names`

**Example:**
```python
stats = reader.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']}%")
```

#### Context Manager Support

```python
async with OPCUAReader(url) as reader:
    data = await reader.read_node("cepn1")
```

Automatically handles connection and disconnection.

---

### OPCUAWriter

Client class for writing data to OPC UA servers.

#### Constructor

```python
OPCUAWriter(
    url: str,
    target_object: str = "ePAC:Project",
    timeout: float = 30.0
)
```

**Parameters:**
- `url` (str): OPC UA server URL (must start with "opc.tcp://")
- `target_object` (str): Target root object name. Default: "ePAC:Project"
- `timeout` (float): Connection and operation timeout in seconds. Default: 30.0

**Raises:**
- `ValueError`: If URL is invalid or doesn't start with "opc.tcp://"

#### Methods

##### connect()

```python
async def connect() -> None
```

Connect to the OPC UA server.

**Raises:**
- `RuntimeError`: If connection times out

##### disconnect()

```python
async def disconnect() -> None
```

Disconnect from the OPC UA server.

##### write()

```python
async def write(
    data: Dict[str, Any],
    auto_convert: bool = True
) -> Dict[str, bool]
```

Write values to the OPC UA server.

**Parameters:**
- `data` (Dict[str, Any]): Dictionary mapping paths to values
  - Path format: `"node.field"` or `"node.subnode.field"`
- `auto_convert` (bool): Automatically convert types to match server. Default: True

**Returns:**
- `Dict[str, bool]`: Dictionary mapping paths to success status

**Example:**
```python
results = await writer.write({
    "cepn1.sensor1": 1,
    "cepn1.test": True,
    "valve1.position": 50.5
})
# Returns: {"cepn1.sensor1": True, "cepn1.test": True, "valve1.position": True}
```

#### Context Manager Support

```python
async with OPCUAWriter(url) as writer:
    results = await writer.write({"cepn1.test": 1})
```

---

## Core Functions

### write_values()

Low-level function for writing multiple values.

```python
async def write_values(
    client: Client,
    data: Dict[str, Any],
    root_object_name: Optional[str] = None,
    auto_convert: bool = True
) -> Dict[str, bool]
```

**Parameters:**
- `client` (Client): Connected asyncua Client instance
- `data` (Dict[str, Any]): Dictionary mapping paths to values
- `root_object_name` (Optional[str]): Root object name. Default: TARGET_OBJECT_NAME
- `auto_convert` (bool): Automatically convert types. Default: True

**Returns:**
- `Dict[str, bool]`: Dictionary mapping paths to success status

**Features:**
- Automatic type conversion based on server data types
- Optimized array writing (batch updates)
- Path validation and error handling

**Example:**
```python
from asyncua import Client
from src.opcua import write_values

async with Client("opc.tcp://server:4840") as client:
    results = await write_values(client, {
        "cepn1.test": 1,
        "cepn1.sensor1": True
    })
```

### find_and_read_variable()

Read a specific variable from OPC UA tree.

```python
async def find_and_read_variable(
    node: Node,
    variable_name: str,
    client: Client,
    cache: TypeCache,
    max_depth: int = DEFAULT_MAX_DEPTH,
    current_depth: int = 0
) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `node` (Node): Starting node for search
- `variable_name` (str): Variable name to find
- `client` (Client): OPC UA client
- `cache` (TypeCache): Type cache instance
- `max_depth` (int): Maximum recursion depth
- `current_depth` (int): Current recursion depth (internal)

**Returns:**
- `Optional[Dict[str, Any]]`: Variable data or None

### read_object_children()

Read all children of an object node.

```python
async def read_object_children(
    node: Node,
    client: Client,
    cache: TypeCache,
    max_depth: int = DEFAULT_MAX_DEPTH,
    current_depth: int = 0
) -> Dict[str, Any]
```

**Parameters:**
- `node` (Node): Object node to read children from
- `client` (Client): OPC UA client
- `cache` (TypeCache): Type cache instance
- `max_depth` (int): Maximum recursion depth
- `current_depth` (int): Current recursion depth (internal)

**Returns:**
- `Dict[str, Any]`: Dictionary with all children data

---

## Navigation Functions

### find_specific_object()

```python
async def find_specific_object(
    start_node: Node,
    target_name: str
) -> Optional[Node]
```

Find a specific object by name in the OPC UA tree.

### get_child_objects()

```python
async def get_child_objects(
    node: Node,
    level: int = 0,
    max_level: int = DEFAULT_MAX_DEPTH
) -> List[Node]
```

Get all child objects recursively up to max_level.

### find_node_by_path()

```python
async def find_node_by_path(
    client: Client,
    path: str,
    root_object_name: Optional[str] = None
) -> Optional[Node]
```

Find a node by dot-separated path (e.g., "cepn1.sensor1").

### find_object_by_name()

```python
async def find_object_by_name(
    client: Client,
    name: str
) -> Optional[Node]
```

Find an object by name in the Objects folder.

---

## Parsing & Formatting

### format_output()

```python
def format_output(
    data: Dict[str, Any],
    format_type: str = "tree",
    timestamp: Optional[str] = None
) -> str
```

Format OPC UA data for display.

**Parameters:**
- `data` (Dict[str, Any]): Data to format
- `format_type` (str): "tree" or "json". Default: "tree"
- `timestamp` (Optional[str]): Timestamp string

**Returns:**
- Formatted string

### format_value()

```python
def format_value(value: Any) -> Any
```

Format a single value (handles special types like DateTime, ExtensionObject, etc.).

### parse_extension_object()

```python
async def parse_extension_object(
    ext_obj: Any,
    client: Client,
    cache: TypeCache
) -> Dict[str, Any]
```

Parse OPC UA ExtensionObject to dictionary.

### parse_bitmask()

```python
def parse_bitmask(value: int, field_names: List[str]) -> Dict[str, bool]
```

Parse bitmask value to dictionary of boolean flags.

---

## Type Cache

### TypeCache

LRU cache for OPC UA type definitions.

```python
class TypeCache:
    def __init__(self, max_size: int = 1000)
```

#### Methods

##### set_definition()

```python
def set_definition(type_id: str, definition: Any) -> None
```

Store type definition.

##### get_definition()

```python
def get_definition(type_id: str) -> Optional[Any]
```

Retrieve type definition.

##### set_field_names()

```python
def set_field_names(type_id: str, field_names: List[str]) -> None
```

Store field names for a type.

##### get_field_names()

```python
def get_field_names(type_id: str) -> Optional[List[str]]
```

Retrieve field names.

##### get_stats()

```python
def get_stats() -> Dict[str, Any]
```

Get cache statistics (hits, misses, total, sizes).

---

## Type System

### python_to_variant()

```python
def python_to_variant(
    value: Any,
    prefer_type: Optional[ua.VariantType] = None
) -> ua.Variant
```

Convert Python value to OPC UA Variant.

**Automatic type detection:**
- `bool` → `ua.VariantType.Boolean`
- `int` → `ua.VariantType.Int32`
- `float` → `ua.VariantType.Double`
- `str` → `ua.VariantType.String`
- `list/tuple` → Array variants

### get_node_variant_type()

```python
async def get_node_variant_type(
    node: Node,
    client: Client
) -> ua.VariantType
```

Get the correct VariantType for a node from the server.

**Supported types:**
- Boolean, SByte, Byte
- Int16, UInt16, Int32, UInt32, Int64, UInt64
- Float, Double
- String, DateTime, ByteString

---

## Constants

```python
TARGET_OBJECT_NAME = "ePAC:Project"  # Default root object
DEFAULT_MAX_DEPTH = 10               # Default recursion depth
```

## Type Aliases

```python
NodeType = Literal["Variable", "Object", "Method"]
PathType = Union[str, List[str]]
```
