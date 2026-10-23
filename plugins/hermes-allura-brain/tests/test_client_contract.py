"""Client contract regressions across MCP SDK versions."""

import asyncio
import importlib.util
from pathlib import Path
import types
import unittest
from unittest.mock import patch


def load_client():
    path = Path(__file__).resolve().parents[1] / "client.py"
    spec = importlib.util.spec_from_file_location("client_contract", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClientContractTests(unittest.TestCase):
    @staticmethod
    def _stuck(cancelled):
        async def stuck():
            try:
                await asyncio.sleep(0.08)
            finally:
                cancelled.append(True)

        return stuck

    def test_sync_operation_deadline_cancels_pending_request(self):
        module = load_client()
        cancelled = []

        with self.assertRaises(TimeoutError):
            module.AlluraBrainClient._run_sync(self._stuck(cancelled), 0.01)
        self.assertEqual(cancelled, [True])

    def test_sync_operation_deadline_inside_event_loop_cancels_pending_request(self):
        module = load_client()
        cancelled = []

        async def invoke():
            with self.assertRaises(TimeoutError):
                module.AlluraBrainClient._run_sync(self._stuck(cancelled), 0.01)

        asyncio.run(invoke())
        self.assertEqual(cancelled, [True])

    def test_modern_structured_result_without_text(self):
        module = load_client()
        client = module.AlluraBrainClient("https://example.invalid/mcp")

        async def response(operation):
            return types.SimpleNamespace(
                content=[],
                is_error=False,
                structured_content={"results": [{"id": "receipt"}]},
            )

        with patch.object(client, "_with_session", response):
            self.assertEqual(
                client.call_tool("memory_search", {}),
                {"results": [{"id": "receipt"}]},
            )

    def test_legacy_structured_result_fallback(self):
        module = load_client()
        client = module.AlluraBrainClient("https://example.invalid/mcp")

        async def response(operation):
            return types.SimpleNamespace(
                content=[],
                isError=False,
                structuredContent={"results": [{"id": "legacy"}]},
            )

        with patch.object(client, "_with_session", response):
            self.assertEqual(
                client.call_tool("memory_search", {}),
                {"results": [{"id": "legacy"}]},
            )


if __name__ == "__main__":
    unittest.main()
