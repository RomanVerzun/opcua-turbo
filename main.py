#!/usr/bin/env python3
"""
Приклад використання OPC UA Reader та Writer.

Демонструє:
1. Читання конкретного вузла через subprocess
2. Запис значень через opcua_writer
"""

import asyncio
import subprocess
import json
from opcua_writer import Client, write_values, setup_logging
import logging

setup_logging(logging.INFO)

# URL OPC UA сервера
SERVER_URL = "opc.tcp://localhost:4840"


async def read_node_example():
    """Приклад читання конкретного вузла."""
    print("=" * 70)
    print("ПРИКЛАД 1: Читання конкретного вузла (valve1)")
    print("=" * 70)
    
    # Виклик opcua_reader.py для читання конкретного вузла
    result = subprocess.run(
        ["python", "opcua_reader.py", SERVER_URL, "--node", "valve1", "--format", "json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f"\nЧас читання: {data['timestamp']}")
        print(f"Дані: {json.dumps(data['data'], indent=2, ensure_ascii=False)}")
    else:
        print(f"Помилка читання: {result.stderr}")


async def write_values_example():
    """Приклад запису значень."""
    print("\n" + "=" * 70)
    print("ПРИКЛАД 2: Запис значень")
    print("=" * 70)
    
    async with Client(SERVER_URL) as client:
        data = {
            "cepn1.sensor1": 1,
            "cepn1.sensor2": 1,
            "cepn1.sensor3": 1,
            "cepn1.sensor4": 1,
        }
        
        print(f"\nЗаписуємо: {data}")
        results = await write_values(client, data)
        
        success = sum(results.values())
        total = len(results)
        print(f"\nРезультат: {success}/{total} успішно записано")
        
        # Показати детальні результати
        for path, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {path}")


async def main():
    """Головна функція з прикладами."""
    print("\n🚀 OPC UA Reader & Writer - Приклади використання\n")
    
    # Приклад 1: Читання
    await read_node_example()
    
    # Приклад 2: Запис
    await write_values_example()
    
    print("\n✓ Всі приклади виконано")


if __name__ == "__main__":
    asyncio.run(main())