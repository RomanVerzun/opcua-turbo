"""
Type conversion utilities for OPC UA values.
"""

import logging
from typing import Any, Optional
from asyncua import Client, ua
from asyncua.common.node import Node

logger = logging.getLogger(__name__)


def python_to_variant(value: Any, prefer_type: Optional[ua.VariantType] = None) -> ua.Variant:
    """
    Конвертувати Python значення в OPC UA Variant

    Args:
        value: Python значення
        prefer_type: Бажаний тип Variant (якщо None - автоматичне визначення)

    Returns:
        ua.Variant з визначеним типом
    """
    if value is None:
        return ua.Variant(None, ua.VariantType.Null)

    # Якщо вказано бажаний тип - використовуємо його
    if prefer_type is not None and prefer_type != ua.VariantType.Variant:
        return ua.Variant(value, prefer_type)

    elif isinstance(value, bool):
        return ua.Variant(value, ua.VariantType.Boolean)

    elif isinstance(value, int):
        return ua.Variant(value, ua.VariantType.Int32)

    elif isinstance(value, float):
        return ua.Variant(value, ua.VariantType.Double)

    elif isinstance(value, str):
        return ua.Variant(value, ua.VariantType.String)

    elif isinstance(value, (list, tuple)):
        if not value:
            return ua.Variant([], ua.VariantType.Null)

        first_type = type(value[0])
        if first_type == bool:
            return ua.Variant(list(value), ua.VariantType.Boolean)
        elif first_type == int:
            return ua.Variant(list(value), ua.VariantType.Int32)
        elif first_type == float:
            return ua.Variant(list(value), ua.VariantType.Double)
        elif first_type == str:
            return ua.Variant(list(value), ua.VariantType.String)
        else:
            return ua.Variant(list(value), ua.VariantType.Variant)

    else:
        return ua.Variant(str(value), ua.VariantType.String)


async def get_node_variant_type(node: Node, client: Client) -> ua.VariantType:
    """
    Отримати тип Variant для вузла з сервера

    Args:
        node: OPC UA вузол
        client: OPC UA клієнт

    Returns:
        ua.VariantType
    """
    try:
        data_type_node_id = await node.read_data_type()
        data_type_node = client.get_node(data_type_node_id)
        browse_name = await data_type_node.read_browse_name()
        data_type_name = browse_name.Name

        type_mapping = {
            'Boolean': ua.VariantType.Boolean,
            'SByte': ua.VariantType.SByte,
            'Byte': ua.VariantType.Byte,
            'Int16': ua.VariantType.Int16,
            'UInt16': ua.VariantType.UInt16,
            'Int32': ua.VariantType.Int32,
            'UInt32': ua.VariantType.UInt32,
            'Int64': ua.VariantType.Int64,
            'UInt64': ua.VariantType.UInt64,
            'Float': ua.VariantType.Float,
            'Double': ua.VariantType.Double,
            'String': ua.VariantType.String,
            'DateTime': ua.VariantType.DateTime,
            'ByteString': ua.VariantType.ByteString,
        }

        return type_mapping.get(data_type_name, ua.VariantType.Variant)

    except Exception as e:
        logger.debug(f"Не вдалось отримати тип вузла: {e}")
        return ua.VariantType.Variant
