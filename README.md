# OPC UA Smart Reader & Writer v2.1

Модульний пакет для роботи з OPC UA з автоматичним визначенням типів. Швидкість ~0.3 сек.

## ✨ Особливості

- ⚡ Блискавична швидкість (~0.3 сек)
- 🏗️ Модульна архітектура з src/ layout
- 🔍 Автоматичне визначення типів
- 📊 Підтримка всіх типів OPC UA
- 🔄 Зворотна сумісність через compatibility wrappers
- ✍️ Підтримка як читання, так і запису
- 🧪 Повне покриття тестами

## 🚀 Швидкий старт

### Встановлення

```bash
# Встановлення з репозиторію
pip install -e .

# Або активація віртуального середовища
source .venv/bin/activate
```

## 📚 Приклади використання

### Читання даних

#### Приклад 1: Context Manager (рекомендований)

```python
import asyncio
from src.opcua import OPCUAReader

async def main():
    async with OPCUAReader("opc.tcp://server:4840") as reader:
        # Читання одного вузла
        data = await reader.read_node("cepn1")
        print(data)

asyncio.run(main())
```

#### Приклад 2: Ручне керування підключенням

```python
from src.opcua import OPCUAReader

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
from src.opcua import OPCUAReader, format_output

async with OPCUAReader("opc.tcp://server:4840") as reader:
    all_data = await reader.read_all()

    # JSON формат
    print(format_output(all_data, format_type="json"))

    # Tree формат (за замовчуванням)
    print(format_output(all_data, format_type="tree"))
```

### Запис даних

#### Приклад 1: Використання OPCUAWriter класу (рекомендований)

```python
from src.opcua import OPCUAWriter

async def main():
    data = {
        "cepn1.sensor1": 1,
        "cepn1.sensor2": 1,
        "cepn1.test": True,
    }

    async with OPCUAWriter("opc.tcp://server:4840") as writer:
        results = await writer.write(data)
        print(f"Записано: {sum(results.values())}/{len(results)}")

asyncio.run(main())
```

#### Приклад 2: Використання функції write_values

```python
from src.opcua import write_values
from asyncua import Client

async def main():
    data = {
        "cepn1.test": 1,
        "cepn1.frequency": 1500,
        "valve1.position": 50,
    }

    async with Client("opc.tcp://server:4840") as client:
        results = await write_values(client, data)

        for path, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {path}")

asyncio.run(main())
```

#### Приклад 3: Цикл читання-запис-читання

```python
from src.opcua import OPCUAReader, OPCUAWriter

async def main():
    # Читання поточного значення
    async with OPCUAReader("opc.tcp://server:4840") as reader:
        data_before = await reader.read_node("cepn1")
        print(f"Перед: {data_before}")

    # Запис нового значення
    async with OPCUAWriter("opc.tcp://server:4840") as writer:
        await writer.write({"cepn1.test": 42})

    # Перевірка запису
    async with OPCUAReader("opc.tcp://server:4840") as reader:
        data_after = await reader.read_node("cepn1")
        print(f"Після: {data_after}")

asyncio.run(main())
```

### Зворотна сумісність (deprecated)

Старий API все ще працює через compatibility wrappers:

```python
# Старий імпорт (з deprecation warning)
from opcua import OPCUAReader, TypeCache
from opcua_writer import write_values

# Новий імпорт (рекомендований)
from src.opcua import OPCUAReader, OPCUAWriter, TypeCache, write_values
```

## 🔧 API Документація

### OPCUAReader

**Конструктор:**
```python
reader = OPCUAReader(
    url: str,
    target_object: str = "ePAC:Project",
    timeout: float = 30.0
)
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

### OPCUAWriter

**Конструктор:**
```python
writer = OPCUAWriter(
    url: str,
    target_object: str = "ePAC:Project",
    timeout: float = 30.0
)
```

**Методи:**
- `await connect()` - підключення до сервера
- `await disconnect()` - відключення від сервера
- `await write(data: Dict[str, Any], auto_convert: bool = True)` - запис значень

**Context Manager:**
```python
async with OPCUAWriter(url) as writer:
    # автоматичне підключення/відключення
    results = await writer.write({"cepn1.test": 1})
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

## 📦 Структура проекту

```
opcua-turbo/
├── src/opcua/              # Головний пакет (нова структура)
│   ├── __init__.py         # Public API
│   ├── core/               # Основна функціональність
│   │   ├── common.py       # Константи та типи
│   │   ├── cache.py        # TypeCache з LRU
│   │   └── type_conversion.py  # Конвертація типів
│   ├── client/             # OPC UA клієнти
│   │   ├── reader.py       # OPCUAReader
│   │   └── writer.py       # OPCUAWriter
│   ├── navigation/         # Навігація по дереву
│   │   └── navigator.py    # Пошук вузлів
│   └── parsing/            # Парсинг та форматування
│       ├── parser.py       # Парсинг значень
│       └── formatter.py    # JSON/Tree форматування
├── opcua/                  # Старий пакет (compatibility wrapper)
├── tests/                  # Тести pytest
│   ├── conftest.py         # Fixtures
│   └── test_opcua.py       # Основні тести
├── examples/               # Приклади використання
│   ├── simple_reader.py    # Простий Reader
│   ├── simple_writer.py    # Простий Writer
│   └── combined_operations.py  # Комплексні операції
├── docs/                   # Документація
├── README.md               # Цей файл
├── USAGE.md                # Детальні інструкції
└── requirements.txt        # Залежності
```

## 🧪 Тестування

### Запуск тестів з pytest

```bash
# Всі тести
pytest tests/

# Конкретний тест
pytest tests/test_opcua.py::test_reader_connect

# З verbose виводом
pytest -v tests/

# З покриттям
pytest --cov=src/opcua tests/
```

### Запуск тестів без pytest

```bash
python tests/test_opcua.py
```

## 📖 Приклади

Дивіться директорію `examples/` для детальних прикладів:

```bash
# Простий Reader
python examples/simple_reader.py

# Простий Writer
python examples/simple_writer.py

# Комплексні операції
python examples/combined_operations.py
```

## 🐛 Усунення проблем

**Об'єкт не знайдено**
```
⚠ Об'єкт 'ePAC:Project' не знайдено
```
→ Перевірте назву об'єкта через UaExpert або вкажіть інший target_object

**Помилка підключення**
```
✗ Помилка: Connection refused
```
→ Перевірте URL сервера, чи запущений сервер, firewall

**Import error (ModuleNotFoundError)**
```
ModuleNotFoundError: No module named 'asyncua'
```
→ Активуйте віртуальне середовище: `source .venv/bin/activate`

**Deprecation warnings**
```
DeprecationWarning: Importing from 'opcua' is deprecated
```
→ Оновіть імпорти на `from src.opcua import ...`

## 📦 Залежності

- Python >= 3.8
- asyncua >= 1.1.0
- pytest >= 7.0.0 (для тестування)
- pytest-asyncio >= 0.21.0 (для тестування)

Встановлення:
```bash
pip install -r requirements.txt
```

## 🔄 Міграція з v2.0 на v2.1

Старий код продовжує працювати через compatibility wrappers:

```python
# v2.0 (все ще працює, але deprecated)
from opcua import OPCUAReader
from opcua_writer import write_values

# v2.1 (рекомендований)
from src.opcua import OPCUAReader, OPCUAWriter, write_values
```

Зміни:
- Додано `OPCUAWriter` клас (аналогічний до `OPCUAReader`)
- Перенесено код в `src/opcua/` структуру
- Старі імпорти працюють через wrapper з deprecation warning
- Compatibility wrappers будуть видалені в v3.0

---

**Версія**: 2.1.0
**Швидкість**: ~0.3 сек
**Архітектура**: Модульна src/ layout
**Python**: >= 3.8
