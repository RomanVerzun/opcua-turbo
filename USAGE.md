# 📖 Як користуватися OPC UA Reader & Writer v2.1

Простий посібник для швидкого старту.

---

## 🔧 Підготовка

```bash
cd /home/trainer/Documents/opcua-turbo
source .venv/bin/activate
```

---

## 📖 Читання даних

### Через командний рядок

```bash
# Прочитати один вузол
python opcua_reader.py opc.tcp://10.15.194.150:4840 --node cepn1

# Прочитати всі вузли
python opcua_reader.py opc.tcp://10.15.194.150:4840

# Отримати JSON
python opcua_reader.py opc.tcp://10.15.194.150:4840 --node valve1 --format json
```

### Через Python код

**Простий спосіб (рекомендований v2.1):**

```python
import asyncio
from src.opcua import OPCUAReader

async def read_data():
    # Підключитися та прочитати
    async with OPCUAReader("opc.tcp://10.15.194.150:4840") as reader:
        data = await reader.read_node("cepn1")
        print(data)

# Запустити
asyncio.run(read_data())
```

**Старий API (deprecated, але працює):**

```python
# Працює через compatibility wrapper
from opcua import OPCUAReader
# Видасть DeprecationWarning, використовуйте src.opcua замість opcua
```

**Що отримаєте:**

```python
{
  "cepn1": {
    "test": 1,
    "frequency": 1500,
    "sensor1": 1,
    "sensor2": 0
  }
}
```

---

## ✍️ Запис даних

### Через Python код

**Спосіб 1: Використання OPCUAWriter класу (рекомендований v2.1):**

```python
import asyncio
from src.opcua import OPCUAWriter

async def write_data():
    # Дані для запису (шлях.змінна: значення)
    data = {
        "cepn1.sensor1": 1,
        "cepn1.sensor2": 0,
    }

    # Підключитися та записати
    async with OPCUAWriter("opc.tcp://10.15.194.150:4840") as writer:
        results = await writer.write(data)
        print(f"Записано: {sum(results.values())}/{len(results)}")

# Запустити
asyncio.run(write_data())
```

**Спосіб 2: Низькорівневий (через функцію write_values):**

```python
import asyncio
from asyncua import Client
from src.opcua import write_values

async def write_data():
    data = {
        "cepn1.sensor1": 1,
        "cepn1.sensor2": 0,
    }

    async with Client("opc.tcp://10.15.194.150:4840") as client:
        results = await write_values(client, data)
        print(f"Записано: {sum(results.values())}/{len(results)}")

asyncio.run(write_data())
```

**Старий API (deprecated):**

```python
# Працює через compatibility wrapper
from opcua_writer import write_values
# Видасть DeprecationWarning
```

**Кілька вузлів одночасно:**

```python
from src.opcua import OPCUAWriter

data = {
    "cepn1.test": 1,
    "cepn1.frequency": 1500,
    "valve1.position": 50,
    "valve2.position": 75,
}

async with OPCUAWriter("opc.tcp://10.15.194.150:4840") as writer:
    results = await writer.write(data)
    print(f"✓ Успішно: {sum(results.values())}")
```

---

## 🔄 Читання + Запис разом

```python
import asyncio
from src.opcua import OPCUAReader, OPCUAWriter

async def main():
    # 1. Прочитати поточні значення
    async with OPCUAReader("opc.tcp://10.15.194.150:4840") as reader:
        data = await reader.read_node("cepn1")
        print(f"Поточні значення: {data}")

    # 2. Записати нові значення
    new_data = {
        "cepn1.sensor1": 1,
        "cepn1.test": 0,
    }

    async with OPCUAWriter("opc.tcp://10.15.194.150:4840") as writer:
        results = await writer.write(new_data)
        print(f"Записано: {sum(results.values())}/{len(results)}")

    # 3. Перевірити зміни
    async with OPCUAReader("opc.tcp://10.15.194.150:4840") as reader:
        data = await reader.read_node("cepn1")
        print(f"Нові значення: {data}")

asyncio.run(main())
```

---

## 📝 Формат шляху для запису

```python
# Формат: "об'єкт.змінна"
"cepn1.sensor1"      # змінна sensor1 в об'єкті cepn1
"valve1.position"    # змінна position в об'єкті valve1

# Можна записувати кілька одночасно
data = {
    "cepn1.sensor1": 1,
    "cepn1.sensor2": 0,
    "valve1.position": 50,
}
```

---

## ⚡ Швидкі команди

```bash
# Активувати середовище
source .venv/bin/activate

# Прочитати cepn1
python opcua_reader.py opc.tcp://10.15.194.150:4840 --node cepn1

# Прочитати valve1 в JSON
python opcua_reader.py opc.tcp://10.15.194.150:4840 --node valve1 --format json

# Запустити приклади
python examples/simple_reader.py
python examples/simple_writer.py
python examples/combined_operations.py
```

---

## 🎯 Типові задачі

### Задача 1: Дізнатися поточне значення сенсора

```bash
python opcua_reader.py opc.tcp://localhost:4840 --node cepn1
```

Або в коді:

```python
from src.opcua import OPCUAReader

async with OPCUAReader("opc.tcp://10.15.194.150:4840") as reader:
    data = await reader.read_node("cepn1")
    sensor_value = data["cepn1"]["sensor1"]
    print(f"Sensor1 = {sensor_value}")
```

### Задача 2: Встановити значення

```python
from src.opcua import OPCUAWriter

data = {"cepn1.sensor1": 1}

async with OPCUAWriter("opc.tcp://10.15.194.150:4840") as writer:
    await writer.write(data)
```

### Задача 3: Прочитати всі доступні вузли

```bash
python opcua_reader.py opc.tcp://10.15.194.150:4840
```

### Задача 4: Змінити кілька параметрів

```python
from src.opcua import OPCUAWriter

data = {
    "cepn1.test": 1,
    "cepn1.frequency": 1500,
    "cepn1.run": True,
}

async with OPCUAWriter("opc.tcp://10.15.194.150:4840") as writer:
    results = await writer.write(data)
```

---

## 🐛 Що робити якщо не працює?

**Помилка: "Connection refused"**
```
→ Перевірте чи запущений OPC UA сервер
→ Перевірте IP адресу та порт
```

**Помилка: "Node not found"**
```
→ Перевірте назву вузла (регістр важливий!)
→ Подивіться доступні вузли: python opcua_reader.py <url>
```

**Помилка: "ModuleNotFoundError"**
```
→ Активуйте .venv: source .venv/bin/activate
→ Встановіть залежності: pip install -r requirements.txt
```

---

## 📚 Додаткова інформація

Детальна документація: [README.md](README.md)

Швидкість читання: **~0.3 секунди** ⚡

---

**Версія**: 2.1 | **Python**: >= 3.8 | **Архітектура**: Модульна src/ layout

