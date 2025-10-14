#!/usr/bin/env python3
"""
Простий приклад читання з OPC UA сервера
"""

import asyncio
from src.opcua import OPCUAReader, format_output

SERVER_URL = "opc.tcp://10.15.194.150:4840"


async def main():
    """Простий приклад читання"""
    print("📖 Простий приклад читання з OPC UA\n")

    # Використання context manager для автоматичного підключення/відключення
    async with OPCUAReader(SERVER_URL) as reader:
        # Читання конкретного вузла
        data = await reader.read_node("cepn1")

        if data:
            print("Дані отримано:")
            print(format_output(data, format_type="json"))
        else:
            print("Дані не знайдено")


if __name__ == "__main__":
    asyncio.run(main())
