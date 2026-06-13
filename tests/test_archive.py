from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.archive import save_digest


class ArchiveTests(unittest.TestCase):
    def test_save_digest_writes_markdown_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = save_digest("hello slack", Path(temp_dir))

            self.assertEqual(path.suffix, ".md")
            self.assertEqual(path.read_text(encoding="utf-8"), "hello slack\n")


if __name__ == "__main__":
    unittest.main()
