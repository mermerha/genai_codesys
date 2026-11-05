import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.model_client import chat_completion


class _FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self._body


class ModelClientTests(unittest.TestCase):
    def test_reads_chat_content_and_never_places_key_in_body(self):
        payload = {
            "model": "model-returned-by-api",
            "choices": [{"message": {"content": "model output"}}],
            "usage": {"total_tokens": 12},
        }

        def fake_urlopen(request, timeout):
            self.assertEqual(timeout, 30.0)
            self.assertNotIn(b"secret-for-test", request.data)
            self.assertEqual(request.get_header("Authorization"), "Bearer secret-for-test")
            return _FakeResponse(payload)

        with patch("plc_agent.model_client.urlopen", side_effect=fake_urlopen):
            result = chat_completion(
                model="requested-model",
                messages=[{"role": "user", "content": "hello"}],
                api_key="secret-for-test",
                timeout_seconds=30.0,
            )

        self.assertEqual(result.content, "model output")
        self.assertEqual(result.model, "model-returned-by-api")
        self.assertEqual(result.usage["total_tokens"], 12)


if __name__ == "__main__":
    unittest.main()
