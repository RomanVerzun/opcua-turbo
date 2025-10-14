"""
Спільні константи, типи та утиліти для OPC UA модулів.
"""

from typing import TypeAlias
from asyncua.common.node import Node

# Константи
DEFAULT_MAX_DEPTH = 10
TARGET_OBJECT_NAME = "ePAC:Project"

# Типи
NodeType: TypeAlias = Node
PathType: TypeAlias = str

