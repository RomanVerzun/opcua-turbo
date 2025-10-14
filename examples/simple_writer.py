#!/usr/bin/env python3
"""
Простий приклад запису в OPC UA сервер
"""

import asyncio
from src.opcua import OPCUAWriter

SERVER_URL = "opc.tcp://10.15.194.150:4840"


async def main():
    """Простий приклад запису"""
    print("✍️  Простий приклад запису в OPC UA\n")

    # Дані для запису
    data = {
        "cepn1.test": 1,
        "cepn1.sensor1": 1,
    }

    # Використання context manager
    async with OPCUAWriter(SERVER_URL) as writer:
        results = await writer.write(data)

        # Виведення результатів
        print("Результати запису:")
        for path, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {path}")


if __name__ == "__main__":
    asyncio.run(main())
