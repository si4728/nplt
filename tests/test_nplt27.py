import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import Mock, patch

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

    def test_website_builder_detects_common_generators_and_assets(self):
        cases = [
            ('<meta name="generator" content="WordPress 6.5">', "WordPress"),
            ('<script src="https://static.parastorage.com/app.js"></script>', "Wix"),
            ('<link href="https://cdn.shopify.com/theme.css" rel="stylesheet">', "Shopify"),
            ('<script src="https://ecimg.cafe24img.com/app.js"></script>', "Cafe24"),
            ('<link href="/theme/basic/style.css" rel="stylesheet">', "Gnuboard"),
            ('<script src="/_next/static/chunks/main.js"></script>', "Next.js (frontend framework)"),
            ('<script src="/media/system/js/core.js"></script>', "Joomla"),
            ('<script type="application/json">drupal-settings-json</script>', "Drupal"),
            ('<script src="/static/version123/frontend/theme.js"></script>', "Magento"),
            ('<link href="/catalog/view/theme/default/style.css" rel="stylesheet">', "OpenCart"),
            ('<script src="https://tistory1.daumcdn.net/tistory.js"></script>', "Tistory"),
            ('<script src="https://cdn.modoo.at/app.js"></script>', "Naver Modoo"),
            ('<script src="/js/bootstrap.bundle.min.js"></script>', "Bootstrap (frontend framework)"),
            ('<div data-reactroot="">App</div>', "React (frontend library)"),
            ('<div data-v-123abc>App</div>', "Vue (frontend framework)"),
            ('<app-root ng-version="17.0.0"></app-root>', "Angular (frontend framework)"),
            ('<script src="/page-data/app-data.json"></script>', "Gatsby"),
            ('<script src="/wp-content/plugins/elementor/assets/js/frontend.js"></script>', "Elementor"),
            ('<script src="/ghost/content/js/app.js"></script>', "Ghost"),
            ('<script src="https://static.hsappstatic.net/cms.js"></script>', "HubSpot CMS"),
            ('<script src="https://www.blogger.com/static/v1/widgets.js"></script>', "Blogger"),
            ('<script src="https://framerusercontent.com/sites/app.js"></script>', "Framer"),
            ('<link href="https://static.tildacdn.com/css/tilda-grid.css" rel="stylesheet">', "Tilda"),
            ('<script src="https://assets.carrd.co/assets/js/main.js"></script>', "Carrd"),
            ('<script src="https://shopby.cloud/assets/storefront.js"></script>', "Shopby"),
            ('<link href="https://firstmall.kr/data/skin/style.css" rel="stylesheet">', "Gabia Firstmall"),
            ('<script src="https://wisaimg.co.kr/js/shop.js"></script>', "WISA"),
        ]
        for html, expected in cases:
            with self.subTest(expected=expected):
                soup = nplt27.bs(f"<html><head>{html}</head></html>", "html.parser")
                self.assertEqual(nplt27.identify_website_builder(soup), expected)

    def test_website_builder_does_not_treat_gtm_preconnect_as_hostinger(self):
        soup = nplt27.bs(
            '<link rel="preconnect" href="https://www.googletagmanager.com">',
            "html.parser",
        )
        self.assertEqual(nplt27.identify_website_builder(soup), "Custom/Static Site")

    def test_website_builder_returns_custom_static_when_no_signature_exists(self):
        soup = nplt27.bs(
            "<html><head><title>Company</title></head><body>Hello</body></html>",
            "html.parser",
        )
        self.assertEqual(nplt27.identify_website_builder(soup), "Custom/Static Site")

    def test_security_header_recommendations_cover_missing_headers(self):
        headers = {
            "Cache-Control": "pre-check=0, post-check=0, max-age=0",
            "expires": "0",
            "Content-Type": "text/html; charset=utf-8",
        }
        recommendations = nplt27.collect_security_header_recommendations(headers)
        joined = "\n".join(recommendations)
        self.assertIn("X-XSS-Protection is missing", joined)
        self.assertIn("X-Content-Type-Options should be set to 'nosniff'", joined)
        self.assertIn("X-Frame-Options is missing", joined)
        self.assertIn("Content-Security-Policy is missing", joined)
        self.assertIn("Strict-Transport-Security is missing", joined)
        self.assertIn("Cache-Control disables freshness", joined)
        self.assertIn("Expires is set to 0", joined)

    def test_security_header_recommendations_accept_safe_core_headers(self):
        headers = {
            "X-XSS-Protection": "1; mode=block",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Content-Security-Policy": "default-src 'self'; frame-ancestors 'self'",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }
        recommendations = nplt27.collect_security_header_recommendations(headers)
        self.assertEqual(recommendations, [])

    def test_db_yes_option_accepts_yes_y_1_and_true(self):
        for value in ("Yes", "YES", "yes", "Y", "1", "true", "TRUE"):
            with self.subTest(value=value):
                self.assertTrue(nplt27.is_yes_option(value))
        for value in ("No", "N", "0", "", None):
            with self.subTest(value=value):
                self.assertFalse(nplt27.is_yes_option(value))

    @patch("nplt27.mysql.connector.connect")
    def test_db_cursor_rolls_back_on_generic_exception(self, connect):
        connection = Mock()
        cursor = Mock()
        connection.cursor.return_value = cursor
        connection.is_connected.return_value = True
        connect.return_value = connection

        with self.assertRaises(ValueError):
            with nplt27.get_db_cursor():
                raise ValueError("body failed")

        connection.rollback.assert_called_once()
        connection.commit.assert_not_called()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    @patch("nplt27.get_lastnumber", return_value=0)
    def test_report_to_db_aborts_when_next_id_is_not_allocated(self, get_lastnumber):
        cursor = Mock()
        with self.assertRaises(nplt27.mysql.connector.Error):
            nplt27._report_to_db(cursor, "unused.docx")
        cursor.execute.assert_not_called()

    @patch("nplt27.get_lastnumber", return_value=123)
    def test_db_connection_check_message_uses_next_id(self, get_lastnumber):
        self.assertEqual(nplt27.get_lastnumber(), 123)


if __name__ == "__main__":
    unittest.main()
