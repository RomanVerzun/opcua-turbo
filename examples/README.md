# OPC UA Examples

Приклади використання бібліотеки OPC UA Smart Reader & Writer.

## Доступні приклади

### 1. simple_reader.py
Простий приклад читання даних з OPC UA сервера.

```bash
python examples/simple_reader.py
```

### 2. simple_writer.py
Простий приклад запису даних в OPC UA сервер.

```bash
python examples/simple_writer.py
```

### 3. combined_operations.py
Комплексний приклад з різними операціями:
- Читання конкретного вузла
- Запис значень
- Цикл читання-запис-читання
- Читання всіх вузлів

```bash
python examples/combined_operations.py
```

## Налаштування

Перед запуском прикладів змініть `SERVER_URL` в файлах на адресу вашого OPC UA сервера:

```python
SERVER_URL = "opc.tcp://your-server:4840"
```

## Вимоги

- Python 3.8+
- asyncua>=1.1.0
- Встановлений пакет opcua-turbo

## Встановлення

```bash
# З репозиторію
pip install -e .

# Або додайте src/ до PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```
