"""
Кешування метаданих типів OPC UA для оптимізації.
"""

from typing import Any, Dict, List, Optional


class TypeCache:
    """
    Кеш для зберігання інформації про типи даних OPC UA.
    Зменшує кількість запитів до сервера при повторному читанні.
    """
    
    def __init__(self):
        self._datatype_definitions: Dict[str, Any] = {}
        self._field_names: Dict[str, List[str]] = {}
        self._hits = 0
        self._misses = 0
    
    def get_definition(self, datatype_id) -> Optional[Any]:
        """Отримати опис типу з кешу."""
        result = self._datatype_definitions.get(str(datatype_id))
        if result is not None:
            self._hits += 1
        else:
            self._misses += 1
        return result
    
    def set_definition(self, datatype_id, definition: Any) -> None:
        """Зберегти опис типу в кеш."""
        self._datatype_definitions[str(datatype_id)] = definition
    
    def get_field_names(self, datatype_id) -> Optional[List[str]]:
        """Отримати імена полів структури з кешу."""
        result = self._field_names.get(str(datatype_id))
        if result is not None:
            self._hits += 1
        else:
            self._misses += 1
        return result
    
    def set_field_names(self, datatype_id, names: List[str]) -> None:
        """Зберегти імена полів в кеш."""
        self._field_names[str(datatype_id)] = names
    
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

