from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler_app.utils import normalize_url


class UrlNormalizationTests(unittest.TestCase):
    def test_collapses_duplicate_slashes_in_absolute_paths(self):
        self.assertEqual(
            normalize_url("http://example.com//nested///page"),
            "http://example.com/nested/page",
        )

    def test_resolves_scheme_relative_links_against_base_url(self):
        self.assertEqual(
            normalize_url("//example.com/a", "http://base.test/root"),
            "http://example.com/a",
        )

    def test_preserves_trailing_slash_for_directory_paths(self):
        self.assertEqual(
            normalize_url("http://example.com/a/b/"),
            "http://example.com/a/b/",
        )

    def test_collapses_dot_segments_without_escaping_root(self):
        self.assertEqual(
            normalize_url("http://example.com/a/../../b"),
            "http://example.com/b",
        )


if __name__ == "__main__":
    unittest.main()
