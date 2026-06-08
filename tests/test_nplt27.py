import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

import nplt27


class Nplt27ImprovementTests(unittest.TestCase):
    def test_import_has_no_console_output(self):
        workspace = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-c", "import nplt27"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_skip_ext_list_has_no_duplicates(self):
        counts = Counter(nplt27.skip_ext_list)
        duplicates = [item for item, count in counts.items() if count > 1]
        self.assertEqual(duplicates, [])

    def test_check_string2_delegates_to_check_string_behavior(self):
        values = ["alpha", "beta"]
        self.assertTrue(nplt27.check_string2("xxalphayy", values))
        self.assertFalse(nplt27.check_string2("gamma", values))
        self.assertEqual(
            nplt27.check_string2("xxalphayy", values),
            nplt27.check_string("xxalphayy", values),
        )

    def test_domain_host_normalization_is_shared(self):
        self.assertEqual(
            nplt27.normalize_domain_host("HTTPS://WWW.Example.COM:443/path"),
            "www.example.com",
        )
        self.assertEqual(
            nplt27.normalize_domain_host(
                "HTTPS://M.Example.COM:443/path",
                strip_common_subdomain=True,
            ),
            "example.com",
        )
        self.assertEqual(nplt27.normalize_host("www.example.com:443"), "example.com")
        self.assertEqual(nplt27.normalize_sns_host("m.facebook.com"), "facebook.com")

    def test_nplt27_cli_help_runs(self):
        workspace = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "nplt27.py", "-h"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("website address", result.stdout)


if __name__ == "__main__":
    unittest.main()
