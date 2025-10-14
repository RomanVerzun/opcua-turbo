#!/usr/bin/env python3
"""
Основні тести для OPC UA Reader & Writer
"""

import asyncio
from opcua import OPCUAReader, TypeCache
from opcua_writer import write_values
from asyncua import Client

# Конфігурація
SERVER_URL = "opc.tcp://10.15.194.150:4840"
TEST_NODE = "cepn1"


# ============================================================================
# Тести читання
# ============================================================================

async def test_reader_connect():
    """Тест 1: Підключення до сервера"""
    reader = OPCUAReader(SERVER_URL)
    await reader.connect()
    assert reader.client is not None
    await reader.disconnect()


async def test_reader_context_manager():
    """Тест 2: Context manager"""
    async with OPCUAReader(SERVER_URL) as reader:
        assert reader.client is not None


async def test_read_single_node():
    """Тест 3: Читання одного вузла"""
    async with OPCUAReader(SERVER_URL) as reader:
        data = await reader.read_node(TEST_NODE)
        assert data is not None
        assert TEST_NODE in data
        assert isinstance(data[TEST_NODE], dict)


async def test_read_all_nodes():
    """Тест 4: Читання всіх вузлів"""
    async with OPCUAReader(SERVER_URL) as reader:
        data = await reader.read_all()
        assert data is not None
        assert len(data) > 0
        assert isinstance(data, dict)


async def test_cache_stats():
    """Тест 5: Статистика кешу"""
    async with OPCUAReader(SERVER_URL) as reader:
        await reader.read_node(TEST_NODE)
        stats = reader.get_cache_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "total" in stats


# ============================================================================
# Тести запису
# ============================================================================

async def test_write_single_value():
    """Тест 6: Запис одного значення"""
    data = {f"{TEST_NODE}.test": 1}
    
    async with Client(SERVER_URL) as client:
        results = await write_values(client, data)
        assert len(results) == 1
        assert results[f"{TEST_NODE}.test"] is True


async def test_write_multiple_values():
    """Тест 7: Запис кількох значень"""
    data = {
        f"{TEST_NODE}.test": 1,
        f"{TEST_NODE}.sensor1": 1,
    }
    
    async with Client(SERVER_URL) as client:
        results = await write_values(client, data)
        assert len(results) == 2
        assert sum(results.values()) >= 1  # Хоча б одне записалося


# ============================================================================
# Тести кешу
# ============================================================================

def test_type_cache():
    """Тест 8: TypeCache"""
    cache = TypeCache()
    
    # Тест set/get
    cache.set_definition("test_id", {"field": "value"})
    result = cache.get_definition("test_id")
    assert result == {"field": "value"}
    
    # Тест статистики
    stats = cache.get_stats()
    assert stats["total"] == 1


# ============================================================================
# Тести помилок
# ============================================================================

async def test_read_nonexistent_node():
    """Тест 9: Читання неіснуючого вузла"""
    async with OPCUAReader(SERVER_URL) as reader:
        data = await reader.read_node("nonexistent_node_12345")
        assert data is None


async def test_read_write_cycle():
    """Тест 10: Цикл читання-запис-читання"""
    # Читання початкового значення
    async with OPCUAReader(SERVER_URL) as reader:
        data_before = await reader.read_node(TEST_NODE)
        assert data_before is not None
    
    # Запис нового значення
    new_value = 1
    async with Client(SERVER_URL) as client:
        results = await write_values(client, {f"{TEST_NODE}.test": new_value})
        assert results[f"{TEST_NODE}.test"] is True
    
    # Читання після запису
    async with OPCUAReader(SERVER_URL) as reader:
        data_after = await reader.read_node(TEST_NODE)
        assert data_after is not None
        assert data_after[TEST_NODE]["test"] == new_value


# ============================================================================
# Запуск тестів
# ============================================================================

if __name__ == "__main__":
    print("🧪 Запуск тестів OPC UA\n")
    print("=" * 60)
    
    # Запуск без pytest (для швидкої перевірки)
    async def run_all_tests():
        tests = [
            ("Підключення", test_reader_connect),
            ("Context manager", test_reader_context_manager),
            ("Читання вузла", test_read_single_node),
            ("Читання всіх", test_read_all_nodes),
            ("Статистика кешу", test_cache_stats),
            ("Запис одного", test_write_single_value),
            ("Запис кількох", test_write_multiple_values),
            ("Неіснуючий вузол", test_read_nonexistent_node),
            ("Цикл read-write", test_read_write_cycle),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                print(f"✓ {name}")
                passed += 1
            except Exception as e:
                print(f"✗ {name}: {e}")
                failed += 1
        
        print("=" * 60)
        print(f"\n📊 Результати: {passed} пройдено, {failed} помилок")
        
        # TypeCache тест (синхронний)
        try:
            test_type_cache()
            print(f"✓ TypeCache")
            passed += 1
        except Exception as e:
            print(f"✗ TypeCache: {e}")
            failed += 1
        
        print(f"\n📊 Фінальний результат: {passed}/{passed + failed} тестів пройдено")
    
    asyncio.run(run_all_tests())

