#!/usr/bin/env python3
"""
OPC UA Smart Reader CLI - Command Line Interface для читання даних з OPC UA.

Використовує модульний пакет opcua для роботи з сервером.
"""

import sys
import asyncio
import argparse
import json
from datetime import datetime
from typing import Optional

from opcua import OPCUAReader, TARGET_OBJECT_NAME, format_output
from opcua.navigator import find_specific_object
from opcua.reader import find_and_read_variable, read_object_children
from opcua.cache import TypeCache


async def main(url: str, output_format: str = "tree", debug: bool = False, target_node: Optional[str] = None):
    """
    Головна функція CLI.
    
    Args:
        url: URL OPC UA сервера
        output_format: Формат виводу ("json" або "tree")
        debug: Режим відладки
        target_node: Конкретний вузол для читання
    """
    if output_format == "tree":
        print("✓ OPC UA Smart Reader v2.0\n")
        print(f"{'='*70}")
        print(f"Підключення до: {url}")
        print(f"{'='*70}\n")
    
    try:
        async with OPCUAReader(url) as reader:
            if output_format == "tree":
                print("✓ Підключено до сервера\n")
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # Читання даних
            if target_node:
                if output_format == "tree":
                    print(f"🎯 Читання вузла: {target_node}\n")
                
                data = await reader.read_node(target_node)
                
                if not data:
                    if output_format == "tree":
                        print(f"⚠ Вузол '{target_node}' не знайдено\n")
                    else:
                        print(json.dumps({"error": f"Node '{target_node}' not found"}, ensure_ascii=False))
                    return
            else:
                data = await reader.read_all()
            
            # Вивід результатів
            output = format_output(data, output_format, timestamp)
            print(output)
            
            # Статистика кешу в debug режимі
            if debug and output_format == "tree":
                stats = reader.get_cache_stats()
                print(f"\n📊 Статистика кешу:")
                print(f"   Hits: {stats['hits']}, Misses: {stats['misses']}")
                print(f"   Hit rate: {stats['hit_rate']}%")
            
            if output_format == "tree":
                print("\n✓ Відключено від сервера")
                
    except RuntimeError as e:
        if output_format == "tree":
            print(f"⚠ {e}\n")
        else:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
        
    except Exception as e:
        if output_format == "tree":
            print(f"\n✗ Помилка: {e}")
            print(f"Тип: {type(e).__name__}")
        else:
            print(json.dumps({"error": str(e), "type": type(e).__name__}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OPC UA Smart Reader - швидке читання даних з OPC UA сервера",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади:
  # Читання всіх вузлів
  python opcua_reader.py opc.tcp://localhost:4840
  
  # Читання конкретного вузла
  python opcua_reader.py opc.tcp://localhost:4840 --node cepn1
  
  # JSON формат
  python opcua_reader.py opc.tcp://localhost:4840 --node valve1 --format json
        """
    )
    
    parser.add_argument(
        'url',
        help='URL OPC UA сервера (opc.tcp://server:port)'
    )
    
    parser.add_argument(
        '--node',
        type=str,
        default=None,
        help='Конкретний вузол для читання'
    )
    
    parser.add_argument(
        '--format',
        choices=['tree', 'json'],
        default='tree',
        help='Формат виводу (за замовчуванням: tree)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Режим відладки з статистикою'
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.url, output_format=args.format, debug=args.debug, target_node=args.node))
    except KeyboardInterrupt:
        if args.format == "tree":
            print("\n\n✓ Завершено користувачем")
        sys.exit(0)

