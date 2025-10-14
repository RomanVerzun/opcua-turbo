"""
OPC UA Reader - клас для читання даних з OPC UA сервера.
"""

import asyncio
from typing import Any, Dict, Optional
from asyncua import Client, ua
from asyncua.common.node import Node

from .common import TARGET_OBJECT_NAME
from .cache import TypeCache
from .navigator import find_specific_object, get_child_objects
from .parser import format_value


async def read_object_children(
    node: Node,
    client: Client,
    type_cache: TypeCache
) -> Dict[str, Any]:
    """
    Читає значення всіх дочірніх змінних об'єкта з автоматичним визначенням типів.
    Використовує паралельне читання для швидкості.
    
    Args:
        node: Батьківський об'єкт
        client: OPC UA клієнт
        type_cache: Кеш типів даних
        
    Returns:
        Словник {ім'я_змінної: значення}
    """
    values = {}
    
    try:
        children = await node.get_children()
        
        async def read_single_child(child):
            try:
                child_name = await child.read_display_name()
                child_class = await child.read_node_class()
                
                if child_class == ua.NodeClass.Variable:
                    value = await child.read_value()
                    formatted_value = await format_value(child, value, client, type_cache)
                    return (child_name.Text, formatted_value)
            except Exception:
                pass
            return None
        
        results = await asyncio.gather(*[read_single_child(child) for child in children], return_exceptions=True)
        
        for result in results:
            if result and not isinstance(result, Exception) and isinstance(result, tuple):
                name, value = result
                values[name] = value
                
    except Exception:
        pass
    
    return values


async def find_and_read_variable(
    parent_node: Node,
    variable_name: str,
    client: Client,
    type_cache: TypeCache
) -> Optional[Dict[str, Any]]:
    """
    Знаходить конкретну змінну серед дочірніх елементів та читає її значення.
    
    Args:
        parent_node: Батьківський вузол
        variable_name: Ім'я змінної для пошуку
        client: OPC UA клієнт
        type_cache: Кеш типів даних
        
    Returns:
        Словник з значенням змінної або None якщо не знайдено
    """
    try:
        children = await parent_node.get_children()
        for child in children:
            try:
                child_name = await child.read_display_name()
                
                if child_name.Text == variable_name:
                    child_class = await child.read_node_class()
                    
                    if child_class == ua.NodeClass.Variable:
                        value = await child.read_value()
                        formatted_value = await format_value(child, value, client, type_cache)
                        return {variable_name: formatted_value}
                    elif child_class == ua.NodeClass.Object:
                        children_values = await read_object_children(child, client, type_cache)
                        return {variable_name: children_values}
            except Exception:
                pass
    except Exception:
        pass
    
    return None


class OPCUAReader:
    """
    Клас для читання даних з OPC UA сервера.
    
    Приклад використання:
        reader = OPCUAReader("opc.tcp://localhost:4840")
        await reader.connect()
        data = await reader.read_node("cepn1")
        await reader.disconnect()
        
    Або з context manager:
        async with OPCUAReader("opc.tcp://localhost:4840") as reader:
            data = await reader.read_node("cepn1")
    """
    
    def __init__(self, url: str, target_object: str = TARGET_OBJECT_NAME):
        """
        Ініціалізація reader.
        
        Args:
            url: URL OPC UA сервера
            target_object: Ім'я цільового об'єкта
        """
        self.url = url
        self.target_object = target_object
        self.cache = TypeCache()
        self.client: Optional[Client] = None
        self._epac_node: Optional[Node] = None
    
    async def connect(self) -> None:
        """Підключення до OPC UA сервера."""
        self.client = Client(url=self.url)
        await self.client.connect()
        
        # Знаходимо цільовий об'єкт
        root = self.client.nodes.objects
        self._epac_node = await find_specific_object(root, self.target_object)
        
        if self._epac_node is None:
            raise RuntimeError(f"Об'єкт '{self.target_object}' не знайдено")
    
    async def disconnect(self) -> None:
        """Відключення від сервера."""
        if self.client:
            await self.client.disconnect()
            self.client = None
            self._epac_node = None
    
    async def read_node(self, node_name: str) -> Optional[Dict[str, Any]]:
        """
        Читає конкретний вузол.
        
        Args:
            node_name: Ім'я вузла
            
        Returns:
            Словник з даними або None
        """
        if not self.client or not self._epac_node:
            raise RuntimeError("Не підключено до сервера. Викличте connect() спочатку")
        
        return await find_and_read_variable(self._epac_node, node_name, self.client, self.cache)
    
    async def read_all(self) -> Dict[str, Any]:
        """
        Читає всі вузли з цільового об'єкта.
        
        Returns:
            Словник з усіма даними
        """
        if not self.client or not self._epac_node:
            raise RuntimeError("Не підключено до сервера. Викличте connect() спочатку")
        
        all_data = {}
        
        # Читаємо значення з цільового об'єкта
        epac_values = await read_object_children(self._epac_node, self.client, self.cache)
        if epac_values:
            all_data[self.target_object] = epac_values
        
        # Читаємо дочірні об'єкти
        parent_objects = await get_child_objects(self._epac_node, level=0, max_level=5)
        
        async def read_child_object(obj_node, obj_name):
            assert self.client is not None
            values = await read_object_children(obj_node, self.client, self.cache)
            return (obj_name, values) if values else None
        
        tasks = [read_child_object(obj_node, obj_name) for obj_node, obj_name in parent_objects]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result and not isinstance(result, Exception) and isinstance(result, tuple):
                name, values = result
                all_data[name] = values
        
        return all_data
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Отримати статистику кешу."""
        return self.cache.get_stats()

