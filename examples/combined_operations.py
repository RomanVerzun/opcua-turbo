#!/usr/bin/env python3
"""
Приклад використання OPC UA Reader та Writer.

Демонструє:
1. Читання конкретного вузла
2. Запис значень через OPCUAWriter
3. Комбіновані операції читання та запису
"""

import asyncio
import logging
from src.opcua import OPCUAReader, OPCUAWriter, format_output

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# URL OPC UA сервера
SERVER_URL = "opc.tcp://10.15.194.150:4840"


async def read_node_example():
    """Приклад читання конкретного вузла."""
    print("=" * 70)
    print("ПРИКЛАД 1: Читання конкретного вузла (cepn1)")
    print("=" * 70)

    async with OPCUAReader(SERVER_URL) as reader:
        # Читання конкретного вузла
        data = await reader.read_node("cepn1")

        if data:
            print(f"\nДані вузла 'cepn1':")
            print(format_output(data, format_type="tree"))
        else:
            print("Вузол не знайдено")


async def write_values_example():
    """Приклад запису значень."""
    print("\n" + "=" * 70)
    print("ПРИКЛАД 2: Запис значень")
    print("=" * 70)

    async with OPCUAWriter(SERVER_URL) as writer:
        data = {
            "cepn1.sensor1": 1,
            "cepn1.sensor2": 1,
            "cepn1.sensor3": 1,
            "cepn1.sensor4": 1,
        }

        print(f"\nЗаписуємо: {data}")
        results = await writer.write(data)

        success = sum(results.values())
        total = len(results)
        print(f"\nРезультат: {success}/{total} успішно записано")

        # Показати детальні результати
        for path, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {path}")


async def read_write_cycle_example():
    """Приклад циклу: читання -> запис -> читання."""
    print("\n" + "=" * 70)
    print("ПРИКЛАД 3: Цикл читання-запис-читання")
    print("=" * 70)

    # 1. Читання початкового значення
    print("\n1. Читання початкового значення...")
    async with OPCUAReader(SERVER_URL) as reader:
        data_before = await reader.read_node("cepn1")
        if data_before and "cepn1" in data_before:
            test_value_before = data_before["cepn1"].get("test", "N/A")
            print(f"   Поточне значення 'cepn1.test': {test_value_before}")

    # 2. Запис нового значення
    print("\n2. Запис нового значення...")
    new_value = 42
    async with OPCUAWriter(SERVER_URL) as writer:
        results = await writer.write({"cepn1.test": new_value})
        if results.get("cepn1.test"):
            print(f"   ✓ Записано нове значення: {new_value}")
        else:
            print(f"   ✗ Помилка запису")

    # 3. Читання після запису
    print("\n3. Читання після запису...")
    async with OPCUAReader(SERVER_URL) as reader:
        data_after = await reader.read_node("cepn1")
        if data_after and "cepn1" in data_after:
            test_value_after = data_after["cepn1"].get("test", "N/A")
            print(f"   Нове значення 'cepn1.test': {test_value_after}")


async def read_all_example():
    """Приклад читання всіх доступних вузлів."""
    print("\n" + "=" * 70)
    print("ПРИКЛАД 4: Читання всіх вузлів")
    print("=" * 70)

    async with OPCUAReader(SERVER_URL) as reader:
        # Читання всіх вузлів
        all_data = await reader.read_all()

        print(f"\nЗнайдено вузлів: {len(all_data)}")
        print("\nСписок вузлів:")
        for node_name in all_data.keys():
            print(f"  - {node_name}")

        # Показати статистику кешу
        cache_stats = reader.get_cache_stats()
        print(f"\nСтатистика кешу:")
        print(f"  Hits: {cache_stats['hits']}")
        print(f"  Misses: {cache_stats['misses']}")
        print(f"  Total: {cache_stats['total']}")


async def main():
    """Головна функція з прикладами."""
    print("\n🚀 OPC UA Reader & Writer - Приклади використання\n")

    try:
        # Приклад 1: Читання вузла
        await read_node_example()

        # Приклад 2: Запис значень
        await write_values_example()

        # Приклад 3: Цикл читання-запис-читання
        await read_write_cycle_example()

        # Приклад 4: Читання всіх вузлів
        await read_all_example()

        print("\n✓ Всі приклади виконано успішно")

    except Exception as e:
        print(f"\n✗ Помилка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
