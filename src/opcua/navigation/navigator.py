"""
Навігація по дереву OPC UA - пошук об'єктів та вузлів.
"""

import asyncio
import logging
from typing import Any, List, Optional, Tuple
from asyncua import Client, ua
from asyncua.common.node import Node

from ..core.common import DEFAULT_MAX_DEPTH, TARGET_OBJECT_NAME

logger = logging.getLogger(__name__)


async def find_specific_object(
    node: Node,
    target_name: str,
    level: int = 0,
    max_level: int = DEFAULT_MAX_DEPTH,
    visited: Optional[set] = None
) -> Optional[Node]:
    """
    Швидко шукає об'єкт за іменем в дереві OPC UA.
    Оптимізовано: спочатку шукає на поточному рівні, потім рекурсивно.

    Args:
        node: Кореневий вузол для обходу
        target_name: Ім'я шуканого об'єкта
        level: Поточний рівень вкладеності
        max_level: Максимальна глибина обходу
        visited: Набір відвіданих вузлів (для запобігання циклам)

    Returns:
        Вузол знайденого об'єкта або None
    """
    if visited is None:
        visited = set()

    if level > max_level:
        return None

    try:
        # Перевірка на цикли
        node_id = str(node.nodeid)
        if node_id in visited:
            return None
        visited.add(node_id)

        # Спочатку перевіряємо поточний вузол
        display_name = await node.read_display_name()
        node_class = await node.read_node_class()

        if node_class == ua.NodeClass.Object and display_name.Text == target_name:
            return node

        # Отримуємо всіх дітей одразу
        children = await node.get_children()

        # Спочатку шукаємо на поточному рівні (швидше для типових випадків)
        async def check_child(child):
            try:
                child_id = str(child.nodeid)
                if child_id in visited:
                    return None
                child_name = await child.read_display_name()
                child_class = await child.read_node_class()
                if child_class == ua.NodeClass.Object and child_name.Text == target_name:
                    return child
            except Exception as e:
                logger.debug(f"Помилка перевірки дочірнього вузла: {e}")
            return None

        # Паралельно перевіряємо всіх дітей на поточному рівні
        results = await asyncio.gather(*[check_child(child) for child in children], return_exceptions=True)
        for result in results:
            if result and not isinstance(result, Exception):
                return result

        # Якщо не знайдено, рекурсивно шукаємо глибше
        for child in children:
            result = await find_specific_object(child, target_name, level + 1, max_level, visited)
            if result is not None:
                return result

    except Exception:
        pass

    return None


async def get_child_objects(
    node: Node,
    level: int = 0,
    max_level: int = 5,
    max_concurrent: int = 20
) -> List[Tuple[Node, str]]:
    """
    Отримує всі дочірні об'єкти вказаного вузла рекурсивно.
    Оптимізовано: паралельна обробка дочірніх вузлів з обмеженням конкурентності.

    Args:
        node: Батьківський вузол
        level: Поточний рівень вкладеності
        max_level: Максимальна глибина обходу
        max_concurrent: Максимальна кількість одночасних запитів

    Returns:
        Список кортежів (node, display_name) для всіх дочірніх об'єктів
    """
    if level > max_level:
        return []

    child_objects = []

    try:
        children = await node.get_children()

        # Створюємо семафор для обмеження конкурентності
        semaphore = asyncio.Semaphore(max_concurrent)

        # Паралельно обробляємо всіх дітей з обмеженням
        async def process_child(child):
            async with semaphore:
                try:
                    child_name = await child.read_display_name()
                    child_class = await child.read_node_class()

                    if child_class == ua.NodeClass.Object:
                        # Рекурсивно отримуємо вкладені об'єкти
                        nested = await get_child_objects(child, level + 1, max_level, max_concurrent)
                        return [(child, child_name.Text)] + nested
                except Exception as e:
                    logger.debug(f"Помилка обробки дочірнього об'єкта: {e}")
                return []

        # Паралельно обробляємо всіх дітей
        results = await asyncio.gather(*[process_child(child) for child in children], return_exceptions=True)
        
        # Збираємо результати
        for result in results:
            if result and not isinstance(result, Exception) and isinstance(result, list):
                child_objects.extend(result)
            
    except Exception:
        pass
    
    return child_objects


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
    try:
        if root_object_name is None:
            root_object_name = TARGET_OBJECT_NAME

        parts = path.split('.')

        # Завжди починаємо з кореневого об'єкта
        current_node = await find_object_by_name(client, root_object_name)
        if current_node is None:
            logger.error(f"Кореневий об'єкт '{root_object_name}' не знайдено")
            return None

        # Проходимо по шляху
        for part in parts:
            children = await current_node.get_children()
            found = False
            
            for child in children:
                browse_name = await child.read_browse_name()
                display_name = await child.read_display_name()
                
                if browse_name.Name == part or display_name.Text == part:
                    current_node = child
                    found = True
                    break
            
            if not found:
                logger.error(f"Вузол '{part}' не знайдено в шляху '{path}'")
                return None
        
        return current_node
    
    except Exception as e:
        logger.error(f"Помилка пошуку вузла '{path}': {e}")
        return None


async def find_object_by_name(client: Client, name: str) -> Optional[Node]:
    """
    Знайти об'єкт за іменем в Objects.
    
    Args:
        client: OPC UA клієнт
        name: Ім'я об'єкта
        
    Returns:
        Node або None якщо не знайдено
    """
    try:
        objects_node = client.get_objects_node()
        children = await objects_node.get_children()
        
        for child in children:
            display_name = await child.read_display_name()
            if display_name.Text == name:
                return child
        
        return None
    except Exception as e:
        logger.error(f"Помилка пошуку об'єкта '{name}': {e}")
        return None

