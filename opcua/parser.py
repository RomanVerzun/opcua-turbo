"""
Парсинг та форматування значень OPC UA різних типів.
"""

from typing import Any, Dict, List, Optional, Tuple
from asyncua import Client, ua
from asyncua.common.node import Node

from .cache import TypeCache


async def get_variable_metadata(node: Node) -> Tuple[Optional[Any], Optional[int], Optional[List[int]]]:
    """
    Отримує метадані змінної: тип даних, ранг, розміри масиву.
    
    Args:
        node: Вузол змінної OPC UA
        
    Returns:
        Кортеж (data_type, value_rank, array_dimensions)
    """
    try:
        data_type = await node.read_data_type()
        value_rank = await node.read_value_rank()
        
        try:
            array_dimensions = await node.read_array_dimensions()
        except Exception:
            array_dimensions = None
            
        return data_type, value_rank, array_dimensions
    except Exception:
        return None, None, None


async def get_datatype_node(client: Client, datatype_id) -> Optional[Node]:
    """
    Отримує вузол типу даних за його NodeId.
    
    Args:
        client: OPC UA клієнт
        datatype_id: NodeId типу даних
        
    Returns:
        Вузол типу даних або None
    """
    try:
        return client.get_node(datatype_id)
    except Exception:
        return None


async def get_structure_fields(
    client: Client,
    datatype_node: Node,
    type_cache: TypeCache
) -> Optional[List[str]]:
    """
    Отримує поля структури через browse дочірніх вузлів.
    
    Args:
        client: OPC UA клієнт
        datatype_node: Вузол типу даних
        type_cache: Кеш типів
        
    Returns:
        Список імен полів або None
    """
    try:
        cached = type_cache.get_field_names(datatype_node.nodeid)
        if cached is not None:
            return cached
        
        children = await datatype_node.get_children()
        field_names = []
        
        for child in children:
            try:
                child_name = await child.read_display_name()
                field_names.append(child_name.Text)
            except Exception:
                pass
        
        if field_names:
            type_cache.set_field_names(datatype_node.nodeid, field_names)
            return field_names
            
    except Exception:
        pass
    
    return None


async def parse_extension_object(value: Any, field_names: Optional[List[str]] = None) -> Any:
    """
    Розпаковує ExtensionObject у словник з іменованими полями.
    
    Args:
        value: ExtensionObject для розпакування
        field_names: Список імен полів (якщо відомі)
        
    Returns:
        Словник з полями або оригінальне значення
    """
    try:
        if hasattr(value, '__dict__'):
            result = {}
            obj_dict = value.__dict__
            
            if field_names:
                for i, field_name in enumerate(field_names):
                    field_value = obj_dict.get(field_name)
                    if field_value is None and i < len(obj_dict):
                        field_value = list(obj_dict.values())[i]
                    result[field_name] = field_value
            else:
                result = obj_dict
                
            return result
        
        return value
        
    except Exception:
        return value


async def get_enum_strings(node: Node) -> Optional[List[str]]:
    """
    Отримує EnumStrings або EnumValues для змінної.
    
    Args:
        node: Вузол змінної
        
    Returns:
        Список рядків або None
    """
    try:
        children = await node.get_children()
        
        for child in children:
            try:
                child_name = await child.read_display_name()
                
                if child_name.Text in ['EnumStrings', 'EnumValues']:
                    enum_value = await child.read_value()
                    
                    if hasattr(enum_value, '__iter__'):
                        result = []
                        for item in enum_value:
                            if hasattr(item, 'Text'):
                                result.append(item.Text)
                            else:
                                result.append(str(item))
                        return result
                    
            except:
                pass
                
    except Exception:
        pass
    
    return None


async def parse_bitmask(value: int, bit_names: List[str]) -> Dict[str, int]:
    """
    Розпаковує бітову маску у словник з іменами бітів.
    
    Args:
        value: Числове значення (бітова маска)
        bit_names: Список імен для кожного біта
        
    Returns:
        Словник {ім'я_біта: значення}
    """
    if not isinstance(value, int):
        return value
    
    result = {}
    
    for i, bit_name in enumerate(bit_names):
        bit_value = (value >> i) & 1
        result[bit_name] = bit_value
    
    return result


async def get_variable_field_names(node: Node, type_cache: TypeCache, debug: bool = False) -> Optional[List[str]]:
    """
    Отримує імена полів змінної через browse її дочірніх вузлів.
    
    Args:
        node: Вузол змінної
        type_cache: Кеш типів
        debug: Виводити debug інформацію
        
    Returns:
        Список імен полів або None
    """
    try:
        node_id_str = str(node.nodeid)
        
        cached = type_cache.get_field_names(node_id_str)
        if cached is not None:
            return cached
        
        children = await node.get_children()
        field_names = []
        
        if debug:
            node_name = await node.read_display_name()
            print(f"\n[DEBUG] Змінна: {node_name.Text}")
            print(f"[DEBUG] Знайдено дочірніх вузлів: {len(children)}")
        
        for child in children:
            try:
                child_name = await child.read_display_name()
                child_class = await child.read_node_class()
                
                if debug:
                    print(f"[DEBUG]   - {child_name.Text} [{child_class.name}]")
                
                if child_class == ua.NodeClass.Variable:
                    field_names.append(child_name.Text)
            except Exception as e:
                if debug:
                    print(f"[DEBUG]   - Помилка читання дочірнього вузла: {e}")
        
        if debug:
            print(f"[DEBUG] Знайдено імен полів: {field_names}")
        
        if field_names:
            type_cache.set_field_names(node_id_str, field_names)
            return field_names
            
    except Exception as e:
        if debug:
            print(f"[DEBUG] Помилка get_variable_field_names: {e}")
    
    return None


async def format_value(node: Node, value: Any, client: Client, type_cache: TypeCache) -> Any:
    """
    Універсальна функція форматування значення на основі метаданих OPC UA.
    
    Args:
        node: Вузол змінної
        value: Значення для форматування
        client: OPC UA клієнт
        type_cache: Кеш типів даних
        
    Returns:
        Відформатоване значення
    """
    try:
        data_type, value_rank, array_dimensions = await get_variable_metadata(node)
        
        if data_type is None:
            return value
        
        enum_strings = await get_enum_strings(node)
        
        if enum_strings and isinstance(value, int) and not isinstance(value, bool):
            return await parse_bitmask(value, enum_strings)
        
        if isinstance(value, (list, tuple)):
            if len(value) > 0:
                field_names = await get_variable_field_names(node, type_cache, debug=False)
                
                if not field_names:
                    datatype_node = await get_datatype_node(client, data_type)
                    if datatype_node:
                        field_names = await get_structure_fields(client, datatype_node, type_cache)
                
                if field_names:
                    result = {}
                    for i, val in enumerate(value):
                        if i < len(field_names):
                            result[field_names[i]] = val
                        else:
                            result[f"[{i}]"] = val
                    return result
                
                if hasattr(value[0], '__dict__'):
                    return [await parse_extension_object(item, field_names) for item in value]
                
                return {f"[{i}]": v for i, v in enumerate(value)}
            return value
        
        if hasattr(value, '__dict__'):
            datatype_node = await get_datatype_node(client, data_type)
            if datatype_node:
                field_names = await get_structure_fields(client, datatype_node, type_cache)
                return await parse_extension_object(value, field_names)
        
        return value
        
    except Exception:
        return value

