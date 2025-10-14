# OPC UA Smart Reader & Writer v2.0

Модульний пакет для роботи з OPC UA з автоматичним визначенням типів. Швидкість ~0.3 сек.

## ✨ Особливості

- ⚡ Блискавична швидкість (~0.3 сек)
- 🏗️ Модульна архітектура
- 🔍 Автоматичне визначення типів
- 📊 Підтримка всіх типів OPC UA
- 🔄 Зворотна сумісність

## 🚀 Швидкий старт

### Встановлення

```bash
source venv/bin/activate
```

### CLI (командний рядок)

```bash
# Читання одного вузла
python opcua_reader.py opc.tcp://server:4840 --node cepn1

# JSON формат
python opcua_reader.py opc.tcp://server:4840 --node valve1 --format json

# Всі вузли
python opcua_reader.py opc.tcp://server:4840

# Debug режим
python opcua_reader.py opc.tcp://server:4840 --node cepn1 --debug
```

## 📚 Приклади використання

### Читання даних

#### Приклад 1: Context Manager (рекомендований)

```python
import asyncio
from opcua import OPCUAReader

async def main():
    async with OPCUAReader("opc.tcp://server:4840") as reader:
        # Читання одного вузла
        data = await reader.read_node("cepn1")
        print(data)

asyncio.run(main())
```

#### Приклад 2: Ручне керування підключенням

```python
from opcua import OPCUAReader

async def main():
    reader = OPCUAReader("opc.tcp://server:4840")
    await reader.connect()
    
    data = await reader.read_node("valve1")
    print(data)
    
    await reader.disconnect()

asyncio.run(main())
```

#### Приклад 3: Читання всіх вузлів

```python
async with OPCUAReader("opc.tcp://server:4840") as reader:
    all_data = await reader.read_all()
    print(f"Знайдено {len(all_data)} об'єктів")
    for name, values in all_data.items():
        print(f"  • {name}: {len(values)} змінних")
```

#### Приклад 4: Статистика кешу

```python
async with OPCUAReader("opc.tcp://server:4840") as reader:
    await reader.read_node("cepn1")
    await reader.read_node("valve1")
    
    stats = reader.get_cache_stats()
    print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']}%")
```

### Запис даних

#### Приклад 1: Простий запис

```python
from asyncua import Client
from opcua_writer import write_values

async def main():
    data = {
        "cepn1.sensor1": 1,
        "cepn1.sensor2": 1,
    }
    
    async with Client("opc.tcp://server:4840") as client:
        results = await write_values(client, data)
        print(f"Записано: {sum(results.values())}/{len(results)}")

asyncio.run(main())
```

#### Приклад 2: Запис в кілька вузлів

```python
data = {
    "cepn1.test": 1,
    "cepn1.frequency": 1500,
    "valve1.position": 50,
    "valve2.position": 75,
}

async with Client("opc.tcp://server:4840") as client:
    results = await write_values(client, data)
    
    success = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]
    
    print(f"✓ Успішно: {len(success)}")
    print(f"✗ Помилки: {len(failed)}")
```

#### Приклад 3: Різні типи даних

```python
data = {
    "cepn1.test": 1,           # int
    "cepn1.run": True,         # bool
    "cepn1.frequency": 1500,   # int
}

async with Client("opc.tcp://server:4840") as client:
    results = await write_values(client, data)
    print(f"Записано: {sum(results.values())}/{len(results)}")
```

### Старий API (зворотна сумісність)

```python
from opcua import find_specific_object, find_and_read_variable, TypeCache
from asyncua import Client

async def main():
    cache = TypeCache()
    async with Client("opc.tcp://server:4840") as client:
        root = client.nodes.objects
        epac = await find_specific_object(root, "ePAC:Project")
        data = await find_and_read_variable(epac, "cepn1", client, cache)
        print(data)

asyncio.run(main())
```

## 🔧 API Документація

### OPCUAReader

**Конструктор:**
```python
reader = OPCUAReader(url: str, target_object: str = "ePAC:Project")
```

**Методи:**
- `await connect()` - підключення до сервера
- `await disconnect()` - відключення від сервера
- `await read_node(node_name: str)` - читання конкретного вузла
- `await read_all()` - читання всіх вузлів
- `get_cache_stats()` - статистика кешу

**Context Manager:**
```python
async with OPCUAReader(url) as reader:
    # автоматичне підключення/відключення
    data = await reader.read_node("cepn1")
```

### write_values()

```python
await write_values(
    client: Client,
    data: Dict[str, Any],
    root_object_name: Optional[str] = None,
    auto_convert: bool = True
) -> Dict[str, bool]
```

**Параметри:**
- `client` - OPC UA клієнт (вже підключений)
- `data` - словник `{шлях: значення}`
- `root_object_name` - кореневий об'єкт (за замовчуванням "ePAC:Project")
- `auto_convert` - автоматична конвертація типів

**Повертає:** словник `{шлях: успіх}`

### Функції модулів

**opcua.navigator:**
- `find_specific_object(node, name)` - пошук об'єкта
- `get_child_objects(node, level, max_level)` - дочірні об'єкти
- `find_node_by_path(client, path)` - пошук за шляхом

**opcua.formatter:**
- `format_output(data, format, timestamp)` - форматування виводу
- `JSONFormatter.format(data, timestamp)` - JSON формат
- `TreeFormatter.format(data, timestamp)` - Tree формат

**opcua.cache:**
- `TypeCache()` - кеш типів даних
- `cache.get_stats()` - статистика кешування

## 📦 Структура проекту

```
opcua/                  # Модульний пакет
├── __init__.py         # Re-exports
├── common.py           # Константи
├── cache.py            # TypeCache
├── navigator.py        # Навігація
├── parser.py           # Парсинг
├── formatter.py        # Форматування
└── reader.py           # OPCUAReader

opcua_reader.py         # CLI
opcua_writer.py         # Writer
reader_example.py       # Приклади читання
writer_example.py       # Приклади запису
main.py                 # Reader + Writer
```

## ⚙️ Параметри CLI

```bash
python opcua_reader.py <url> [опції]

Опції:
  --node <name>         Конкретний вузол для читання
  --format {tree,json}  Формат виводу (за замовчуванням: tree)
  --debug               Режим відладки зі статистикою
```

## 🐛 Усунення проблем

**Об'єкт не знайдено**
```
⚠ Об'єкт 'ePAC:Project' не знайдено
```
→ Перевірте назву об'єкта через UaExpert

**Помилка підключення**
```
✗ Помилка: Connection refused
```
→ Перевірте URL сервера, чи запущений сервер, firewall

**Import error**
```
ModuleNotFoundError: No module named 'opcua'
```
→ Перевірте що директорія `opcua/` існує та містить `__init__.py`

## 📦 Залежності

- Python >= 3.8
- asyncua >= 1.1.0

Встановлення:
```bash
pip install asyncua
```

## 🎯 Приклади виводу

### Tree формат
```
[2025-10-14 18:49:02.824]
----------------------------------------------------------------------

📦 valve1:
   ├─ value_timeout: 0
   ├─ motor_closed: 0
   ├─ position: 50
```

### JSON формат
```json
{
  "timestamp": "2025-10-14 18:49:02.824",
  "data": {
    "valve1": {
      "value_timeout": 0,
      "motor_closed": 0,
      "position": 50
    }
  }
}
```

## 🚀 Запуск прикладів

```bash
# Приклади читання
python reader_example.py

# Приклади запису
python writer_example.py

# Reader + Writer разом
python main.py
```

---

**Версія**: 2.0.0  
**Швидкість**: ~0.3 сек  
**Архітектура**: Модульна  
**Python**: >= 3.8
