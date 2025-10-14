"""
OPC UA Writer - клас для запису даних в OPC UA сервер.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from asyncua import Client, ua
from asyncua.common.node import Node

from ..core.common import TARGET_OBJECT_NAME
from ..core.type_conversion import python_to_variant, get_node_variant_type
from ..navigation.navigator import find_node_by_path, find_object_by_name

logger = logging.getLogger(__name__)


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
        # Валідація шляху
        if not path or not isinstance(path, str):
            logger.error(f"Невалідний шлях: {path}")
            results[str(path)] = False
            continue

        parts = path.split('.')
        parts = [p for p in parts if p]  # Видалити порожні рядки

        if not parts:
            logger.error(f"Порожній шлях після обробки: {path}")
            results[path] = False
            continue

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
                    full_path = f"{parent_path}.{field_name}"

                    if index is None:
                        logger.error(f"Поле '{field_name}' не знайдено в масиві")
                        results[full_path] = False
                    elif index >= len(new_array):
                        logger.error(f"Індекс {index} поза межами масиву розміру {len(new_array)}")
                        results[full_path] = False
                    else:
                        # Правильна конвертація типу
                        if auto_convert:
                            try:
                                child_node = await parent_node.get_children()
                                if index < len(child_node):
                                    variant_type = await get_node_variant_type(child_node[index], client)
                                    if variant_type == ua.VariantType.Boolean:
                                        new_array[index] = bool(value)
                                    else:
                                        new_array[index] = value
                                else:
                                    new_array[index] = value
                            except Exception:
                                new_array[index] = value
                        else:
                            new_array[index] = value
                        results[full_path] = True

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


class OPCUAWriter:
    """
    Клас для запису даних в OPC UA сервер.

    Приклад використання:
        writer = OPCUAWriter("opc.tcp://localhost:4840")
        await writer.connect()
        results = await writer.write({"cepn1.sensor1": 1})
        await writer.disconnect()

    Або з context manager:
        async with OPCUAWriter("opc.tcp://localhost:4840") as writer:
            results = await writer.write({"cepn1.sensor1": 1})
    """

    def __init__(self, url: str, target_object: str = TARGET_OBJECT_NAME, timeout: float = 30.0):
        """
        Ініціалізація writer.

        Args:
            url: URL OPC UA сервера
            target_object: Ім'я цільового об'єкта
            timeout: Таймаут підключення та операцій (в секундах)

        Raises:
            ValueError: Якщо URL має невірний формат
        """
        # Валідація URL
        if not url or not isinstance(url, str):
            raise ValueError(f"Невалідний URL: {url}")
        if not url.startswith("opc.tcp://"):
            raise ValueError(f"URL має починатися з 'opc.tcp://': {url}")

        self.url = url
        self.target_object = target_object
        self.timeout = timeout
        self.client: Optional[Client] = None

    async def connect(self) -> None:
        """Підключення до OPC UA сервера з таймаутом."""
        self.client = Client(url=self.url)
        try:
            await asyncio.wait_for(self.client.connect(), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise RuntimeError(f"Таймаут підключення до {self.url} ({self.timeout}s)")

    async def disconnect(self) -> None:
        """Відключення від сервера."""
        if self.client:
            await self.client.disconnect()
            self.client = None

    async def write(self, data: Dict[str, Any], auto_convert: bool = True) -> Dict[str, bool]:
        """
        Записати значення в OPC UA сервер.

        Args:
            data: Словник {шлях: значення}
            auto_convert: Автоматично конвертувати типи

        Returns:
            Словник {шлях: успіх} з результатами запису
        """
        if not self.client:
            raise RuntimeError("Не підключено до сервера. Викличте connect() спочатку")

        return await write_values(self.client, data, self.target_object, auto_convert)

    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        try:
            await self.disconnect()
        except Exception:
            pass  # Ensure disconnect is attempted even if it fails
        return False  # Don't suppress exceptions
