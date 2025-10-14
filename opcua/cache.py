"""
Кешування метаданих типів OPC UA для оптимізації.
"""

from typing import Any, Dict, List, Optional
from collections import OrderedDict


class TypeCache:
    """
    Кеш для зберігання інформації про типи даних OPC UA.
    Зменшує кількість запитів до сервера при повторному читанні.
    Використовує LRU (Least Recently Used) стратегію з обмеженням розміру.
    """

    def __init__(self, max_size: int = 1000):
        """
        Ініціалізація кешу.

        Args:
            max_size: Максимальна кількість записів в кеші (за замовчуванням 1000)
        """
        self._datatype_definitions: OrderedDict[str, Any] = OrderedDict()
        self._field_names: OrderedDict[str, List[str]] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def _evict_if_needed(self, cache: OrderedDict) -> None:
        """Видалити найстаріший елемент якщо кеш переповнений."""
        if len(cache) >= self._max_size:
            cache.popitem(last=False)  # Видалити найстаріший (FIFO)

    def get_definition(self, datatype_id) -> Optional[Any]:
        """Отримати опис типу з кешу."""
        key = str(datatype_id)
        result = self._datatype_definitions.get(key)
        if result is not None:
            self._hits += 1
            # Переміщуємо в кінець (LRU)
            self._datatype_definitions.move_to_end(key)
        else:
            self._misses += 1
        return result

    def set_definition(self, datatype_id, definition: Any) -> None:
        """Зберегти опис типу в кеш."""
        key = str(datatype_id)
        self._evict_if_needed(self._datatype_definitions)
        self._datatype_definitions[key] = definition
        self._datatype_definitions.move_to_end(key)

    def get_field_names(self, datatype_id) -> Optional[List[str]]:
        """Отримати імена полів структури з кешу."""
        key = str(datatype_id)
        result = self._field_names.get(key)
        if result is not None:
            self._hits += 1
            # Переміщуємо в кінець (LRU)
            self._field_names.move_to_end(key)
        else:
            self._misses += 1
        return result

    def set_field_names(self, datatype_id, names: List[str]) -> None:
        """Зберегти імена полів в кеш."""
        key = str(datatype_id)
        self._evict_if_needed(self._field_names)
        self._field_names[key] = names
        self._field_names.move_to_end(key)
    
    def clear(self) -> None:
        """Очистити весь кеш."""
        self._datatype_definitions.clear()
        self._field_names.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Отримати статистику використання кешу."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": round(hit_rate, 2),
            "definitions_cached": len(self._datatype_definitions),
            "field_names_cached": len(self._field_names)
        }

