"""
OPC UA Smart Reader & Writer Package

Модульний пакет для роботи з OPC UA серверами з автоматичним визначенням типів.
"""

# Re-exports для зворотної сумісності
from .common import TARGET_OBJECT_NAME, DEFAULT_MAX_DEPTH
from .cache import TypeCache
from .navigator import find_specific_object, get_child_objects, find_node_by_path
from .reader import OPCUAReader, find_and_read_variable, read_object_children
from .formatter import format_output, JSONFormatter, TreeFormatter
from .parser import format_value, parse_extension_object, parse_bitmask

__version__ = "2.0.0"
__all__ = [
    # Константи
    "TARGET_OBJECT_NAME",
    "DEFAULT_MAX_DEPTH",
    
    # Класи
    "TypeCache",
    "OPCUAReader",
    "JSONFormatter",
    "TreeFormatter",
    
    # Навігація
    "find_specific_object",
    "get_child_objects",
    "find_node_by_path",
    
    # Читання
    "find_and_read_variable",
    "read_object_children",
    
    # Форматування
    "format_output",
    "format_value",
    "parse_extension_object",
    "parse_bitmask",
]

