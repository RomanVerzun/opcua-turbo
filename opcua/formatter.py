"""
Форматування виводу даних OPC UA (JSON та Tree).
"""

import json
from typing import Any, Dict
from datetime import datetime


def _convert_to_serializable(obj: Any) -> Any:
    """
    Конвертує об'єкт у JSON-сумісний формат.
    
    Args:
        obj: Об'єкт для конвертації
        
    Returns:
        JSON-сумісний об'єкт
    """
    if isinstance(obj, dict):
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj)


class JSONFormatter:
    """Форматування виводу в JSON."""
    
    @staticmethod
    def format(data: Dict[str, Any], timestamp: str) -> str:
        """
        Форматує дані у JSON.
        
        Args:
            data: Дані для форматування
            timestamp: Мітка часу
            
        Returns:
            JSON рядок
        """
        output = {
            "timestamp": timestamp,
            "data": _convert_to_serializable(data)
        }
        return json.dumps(output, ensure_ascii=False, indent=2)


class TreeFormatter:
    """Форматування виводу у вигляді дерева."""
    
    @staticmethod
    def format(data: Dict[str, Any], timestamp: str) -> str:
        """
        Форматує дані у вигляді дерева.
        
        Args:
            data: Дані для форматування
            timestamp: Мітка часу
            
        Returns:
            Текстове представлення дерева
        """
        lines = [f"\n[{timestamp}]", "-" * 70, ""]
        
        for obj_name, variables in data.items():
            lines.append(f"📦 {obj_name}:")
            for var_name, value in variables.items():
                if isinstance(value, dict):
                    lines.append(f"   ├─ {var_name}:")
                    for field_name, field_value in value.items():
                        lines.append(f"      │  {field_name}: {field_value}")
                else:
                    lines.append(f"   ├─ {var_name}: {value}")
            lines.append("")
        
        return "\n".join(lines)


def format_output(data: Dict[str, Any], output_format: str = "tree", timestamp: str = None) -> str:
    """
    Універсальна функція форматування виводу.
    
    Args:
        data: Дані для форматування
        output_format: Формат виводу ("json" або "tree")
        timestamp: Мітка часу (якщо None - генерується автоматично)
        
    Returns:
        Відформатований рядок
    """
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    if output_format == "json":
        return JSONFormatter.format(data, timestamp)
    else:
        return TreeFormatter.format(data, timestamp)

