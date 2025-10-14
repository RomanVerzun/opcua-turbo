"""
Pytest fixtures and configuration for OPC UA tests
"""

import pytest
import asyncio
from src.opcua import OPCUAReader, OPCUAWriter

# Конфігурація для pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def server_url():
    """OPC UA server URL fixture"""
    return "opc.tcp://10.15.194.150:4840"


@pytest.fixture(scope="session")
def test_node():
    """Test node name fixture"""
    return "cepn1"


@pytest.fixture
async def opcua_reader(server_url):
    """OPC UA Reader fixture with auto cleanup"""
    reader = OPCUAReader(server_url)
    await reader.connect()
    yield reader
    await reader.disconnect()


@pytest.fixture
async def opcua_writer(server_url):
    """OPC UA Writer fixture with auto cleanup"""
    writer = OPCUAWriter(server_url)
    await writer.connect()
    yield writer
    await writer.disconnect()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
