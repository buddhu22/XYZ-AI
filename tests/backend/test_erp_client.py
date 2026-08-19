"""
Test suite for ERP API Client (Phase 4 — Step 1)
"""

import pytest
import anyio
from app.services.erp_client import ERPClient, ERPClientError


@pytest.mark.anyio
async def test_erp_client_instantiation():
    client = ERPClient(base_url="http://127.0.0.1:8000")
    assert client.base_url == "http://127.0.0.1:8000"


@pytest.mark.anyio
async def test_erp_client_timeout_handling():
    # Test timeout handling with an unreachable host
    client = ERPClient(base_url="http://10.255.255.1:8000", timeout=0.2)
    with pytest.raises(ERPClientError) as exc_info:
        await client.get_student(1)
    assert exc_info.value.status_code in (503, 504)
