import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.cli import load_local_env


class CliTests(unittest.TestCase):
    def test_load_local_env_reads_known_values_without_overwriting_environment(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text(
                "DMXAPI_API_KEY=from-file\nMODEL_A=ds4.1\nIGNORED=value\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"DMXAPI_API_KEY": "already-set"}, clear=False):
                os.environ.pop("MODEL_A", None)
                load_local_env(env_file)
                self.assertEqual(os.environ["DMXAPI_API_KEY"], "already-set")
                self.assertEqual(os.environ["MODEL_A"], "ds4.1")
                os.environ.pop("MODEL_A", None)


if __name__ == "__main__":
    unittest.main()
