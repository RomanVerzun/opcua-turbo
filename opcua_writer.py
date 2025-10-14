#!/usr/bin/env python3
"""
OPC UA Writer Module

Простий модуль для запису даних в OPC UA сервер.
Підтримує автоматичне визначення типів.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from asyncua import Client, ua
from asyncua.common.node import Node

# Використовуємо спільні модулі
from opcua.common import TARGET_OBJECT_NAME
from opcua.navigator import find_node_by_path as _find_node_by_path_internal
from opcua.navigator import find_object_by_name as _find_object_by_name_internal


# ============================================================================
# Константи
# ============================================================================

DEFAULT_TIMEOUT = 10.0


# ============================================================================
# Налаштування логування
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# Пошук вузлів (використовуємо функції з opcua.navigator)
# ============================================================================

async def find_node_by_path(
    client: Client,
    path: str,
    root_object_name: Optional[str] = None
) -> Optional[Node]:
    """
    Знайти вузол за шляхом (наприклад: 'cepn1.sensor1')
    
    Args:
        client: OPC UA клієнт
        path: Шлях до вузла (розділений крапками)
        root_object_name: Кореневий об'єкт (за замовчуванням TARGET_OBJECT_NAME)
    
    Returns:
        Node або None якщо не знайдено
    """
    return await _find_node_by_path_internal(client, path, root_object_name)


async def _find_object_by_name(client: Client, name: str) -> Optional[Node]:
    """Знайти об'єкт за іменем в Objects"""
    return await _find_object_by_name_internal(client, name)


# ============================================================================
# Конвертація типів
# ============================================================================

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


# ============================================================================
# Запис даних
# ============================================================================

async def _get_array_field_index(node: Node, field_name: str) -> Optional[int]:
    """
    Знайти індекс поля в масиві за його іменем
    
    Args:
        node: Батьківський вузол (масив)
        field_name: Ім'я поля
    
    Returns:
        Індекс поля в масиві або None
    """
    try:
        children = await node.get_children()
        for i, child in enumerate(children):
            display_name = await child.read_display_name()
            browse_name = await child.read_browse_name()
            
            if display_name.Text == field_name or browse_name.Name == field_name:
                return i
        
        return None
    except Exception as e:
        logger.debug(f"Помилка пошуку індексу поля '{field_name}': {e}")
        return None


async def write_values(
    client: Client,
    data: Dict[str, Any],
    root_object_name: Optional[str] = None,
    auto_convert: bool = True
) -> Dict[str, bool]:
    """
    Записати множину значень в OPC UA
    
    Args:
        client: OPC UA клієнт (вже підключений)
        data: Словник {шлях: значення}
        root_object_name: Кореневий об'єкт (за замовчуванням TARGET_OBJECT_NAME)
        auto_convert: Автоматично конвертувати типи (за замовчуванням True)
    
    Returns:
        Словник {шлях: успіх} з результатами запису
    
    Example:
        >>> data = {
        >>>     "cepn1.sensor1": True,
        >>>     "valve1.position": 50,
        >>>     "pump1.speed": 1500.5
        >>> }
        >>> async with Client("opc.tcp://localhost:4840") as client:
        >>>     results = await write_values(client, data)
    """
    results = {}
    
    # Групуємо записи по батьківському вузлу для оптимізації
    grouped_writes = {}
    
    for path, value in data.items():
        parts = path.split('.')
        if len(parts) >= 2:
            parent_path = '.'.join(parts[:-1])
            field_name = parts[-1]
            
            if parent_path not in grouped_writes:
                grouped_writes[parent_path] = {}
            grouped_writes[parent_path][field_name] = value
        else:
            # Простий шлях без крапки
            grouped_writes[path] = {None: value}
    
    # Обробляємо кожну групу
    for parent_path, fields in grouped_writes.items():
        try:
            # Знайти батьківський вузол
            parent_node = await find_node_by_path(client, parent_path, root_object_name)
            if parent_node is None:
                for field_name in fields.keys():
                    full_path = f"{parent_path}.{field_name}" if field_name else parent_path
                    logger.error(f"Вузол '{parent_path}' не знайдено")
                    results[full_path] = False
                continue
            
            # Перевірити чи це масив
            try:
                current_value = await parent_node.read_value()
                is_array = isinstance(current_value, (list, tuple))
            except:
                is_array = False
                current_value = None
            
            if is_array and len(fields) > 1 and current_value is not None:
                # Це масив і потрібно записати кілька полів - оптимізуємо
                new_array = list(current_value)
                
                for field_name, value in fields.items():
                    if field_name is None:
                        continue
                    
                    # Знайти індекс поля
                    index = await _get_array_field_index(parent_node, field_name)
                    if index is not None and index < len(new_array):
                        new_array[index] = int(value) if isinstance(value, bool) else value
                        full_path = f"{parent_path}.{field_name}"
                        results[full_path] = True
                    else:
                        full_path = f"{parent_path}.{field_name}"
                        logger.error(f"Поле '{field_name}' не знайдено в масиві")
                        results[full_path] = False
                
                # Записати весь масив одразу
                if auto_convert:
                    variant_type = await get_node_variant_type(parent_node, client)
                    variant = python_to_variant(new_array, prefer_type=variant_type)
                else:
                    variant = python_to_variant(new_array)
                
                dv = ua.DataValue(Value=variant)
                await parent_node.write_value(dv)
                logger.info(f"✓ Записано масив '{parent_path}': {len([r for r in results.values() if r])} полів")
            
            else:
                # Звичайний запис (не масив або одне поле)
                for field_name, value in fields.items():
                    full_path = f"{parent_path}.{field_name}" if field_name else parent_path
                    
                    try:
                        if field_name:
                            node = await find_node_by_path(client, full_path, root_object_name)
                        else:
                            node = parent_node
                        
                        if node is None:
                            logger.error(f"Вузол '{full_path}' не знайдено")
                            results[full_path] = False
                            continue
                        
                        if isinstance(value, dict):
                            logger.error(f"Запис словників не підтримується для '{full_path}'")
                            results[full_path] = False
                            continue
                        
                        if auto_convert:
                            variant_type = await get_node_variant_type(node, client)
                            variant = python_to_variant(value, prefer_type=variant_type)
                        else:
                            variant = python_to_variant(value)
                        
                        dv = ua.DataValue(Value=variant)
                        await node.write_value(dv)
                        
                        logger.info(f"✓ Записано '{full_path}' = {value}")
                        results[full_path] = True
                    
                    except Exception as e:
                        logger.error(f"✗ Помилка запису '{full_path}': {e}")
                        results[full_path] = False
        
        except Exception as e:
            for field_name in fields.keys():
                full_path = f"{parent_path}.{field_name}" if field_name else parent_path
                logger.error(f"✗ Помилка запису '{full_path}': {e}")
                results[full_path] = False
    
    return results


# ============================================================================
# Допоміжні функції
# ============================================================================

def setup_logging(level: int = logging.INFO):
    """
    Налаштувати логування для модуля
    
    Args:
        level: Рівень логування (logging.INFO, logging.DEBUG, etc.)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# ============================================================================
# Приклад використання
# ============================================================================

async def main():
    """Приклад використання модуля"""
    setup_logging(logging.INFO)
    
    url = "opc.tcp://localhost:4840"
    
    data = {
        "cepn1.test": 1,
        "cepn1.run": True,
        "cepn1.frequency": 1500,
    }
    
    async with Client(url) as client:
        results = await write_values(client, data)
        
        # Вивести результати
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        print(f"\n{'='*70}")
        print(f"Результат: {success_count}/{total_count} успішно записано")
        print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
