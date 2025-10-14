#!/usr/bin/env python3
"""
OPC UA Writer Module - COMPATIBILITY WRAPPER

DEPRECATED: This file is deprecated. Import from 'src.opcua.client.writer' instead.
This file maintains backward compatibility during refactoring.

Простий модуль для запису даних в OPC UA сервер.
Підтримує автоматичне визначення типів.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "Importing from 'opcua_writer' is deprecated. Use 'from src.opcua.client.writer import ...' instead. "
    "This compatibility wrapper will be removed in version 3.0.0",
    DeprecationWarning,
    stacklevel=2
)

# Import everything from the new location
from src.opcua.client.writer import write_values, OPCUAWriter
from src.opcua.core.type_conversion import python_to_variant, get_node_variant_type
from src.opcua.navigation.navigator import find_node_by_path, find_object_by_name
from src.opcua.core.common import TARGET_OBJECT_NAME

__all__ = [
    "write_values",
    "OPCUAWriter",
    "python_to_variant",
    "get_node_variant_type",
    "find_node_by_path",
    "find_object_by_name",
    "TARGET_OBJECT_NAME",
]
