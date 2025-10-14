"""
OPC UA Smart Reader & Writer Package - COMPATIBILITY WRAPPER

DEPRECATED: This location is deprecated. Import from 'src.opcua' instead.
This file maintains backward compatibility during refactoring.

Модульний пакет для роботи з OPC UA серверами з автоматичним визначенням типів.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "Importing from 'opcua' is deprecated. Use 'from src.opcua import ...' instead. "
    "This compatibility wrapper will be removed in version 3.0.0",
    DeprecationWarning,
    stacklevel=2
)

# Import everything from the new location
from src.opcua import (
    # Version
    __version__,

    # Core
    TARGET_OBJECT_NAME,
    DEFAULT_MAX_DEPTH,
    NodeType,
    PathType,
    TypeCache,

    # Navigation
    find_specific_object,
    get_child_objects,
    find_node_by_path,
    find_object_by_name,

    # Client
    OPCUAReader,
    find_and_read_variable,
    read_object_children,
    OPCUAWriter,
    write_values,

    # Parsing
    format_output,
    JSONFormatter,
    TreeFormatter,
    format_value,
    parse_extension_object,
    parse_bitmask,
)

__all__ = [
    # Version
    "__version__",

    # Core
    "TARGET_OBJECT_NAME",
    "DEFAULT_MAX_DEPTH",
    "NodeType",
    "PathType",
    "TypeCache",

    # Navigation
    "find_specific_object",
    "get_child_objects",
    "find_node_by_path",
    "find_object_by_name",

    # Client
    "OPCUAReader",
    "find_and_read_variable",
    "read_object_children",
    "OPCUAWriter",
    "write_values",

    # Parsing
    "format_output",
    "JSONFormatter",
    "TreeFormatter",
    "format_value",
    "parse_extension_object",
    "parse_bitmask",
]

