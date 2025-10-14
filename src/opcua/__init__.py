"""
OPC UA Smart Reader & Writer Package

Модульний пакет для роботи з OPC UA серверами з автоматичним визначенням типів.
"""

# Core
from .core.common import TARGET_OBJECT_NAME, DEFAULT_MAX_DEPTH, NodeType, PathType
from .core.cache import TypeCache

# Navigation
from .navigation.navigator import (
    find_specific_object,
    get_child_objects,
    find_node_by_path,
    find_object_by_name,
)

# Client
from .client.reader import OPCUAReader, find_and_read_variable, read_object_children
from .client.writer import OPCUAWriter, write_values

# Parsing
from .parsing.formatter import format_output, JSONFormatter, TreeFormatter
from .parsing.parser import (
    format_value,
    parse_extension_object,
    parse_bitmask,
)

__version__ = "2.1.0"
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
