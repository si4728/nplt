import unittest
from unittest.mock import patch

import nplt_whois


class NpltWhoisTests(unittest.TestCase):
    def test_normalize_domain_removes_scheme_path_port_and_common_subdomain(self):
        self.assertEqual(
            nplt_whois.normalize_domain(
                "https://www.onbranding.co.kr:443/contact/index.html"
            ),
            "onbranding.co.kr",
        )
        self.assertEqual(
            nplt_whois.normalize_domain("http://m.example.com/products"),
            "example.com",
        )

    def test_normalize_domain_preserves_kr_second_level_registration_domain(self):
        self.assertEqual(
            nplt_whois.normalize_domain("shop.branch.example.co.kr/path"),
            "example.co.kr",
        )

    def test_normalize_domain_accepts_whois_com_url(self):
        self.assertEqual(
            nplt_whois.normalize_domain("https://www.whois.com/whois/hd.com"),
            "hd.com",
        )

    @patch("nplt_whois.query_dns_nameservers", return_value=["ns1.example.com"])
    @patch(
        "nplt_whois.fetch_whois_com",
        return_value={"success": True, "domain": "example.co.kr"},
    )
    @patch(
        "nplt_whois.fetch_rdap",
        return_value={"success": False, "source": "rdap", "error": "not found"},
    )
    def test_get_domain_registration_info_uses_dns_fallback_for_missing_nameservers(
        self,
        fetch_rdap,
        fetch_whois_com,
        query_dns_nameservers,
    ):
        result = nplt_whois.get_domain_registration_info("www.example.co.kr")

        self.assertTrue(result["success"])
        self.assertEqual(result["domain"], "example.co.kr")
        self.assertEqual(result["name_servers"], ["ns1.example.com"])
        self.assertIn("dns", result["source_priority"])
        query_dns_nameservers.assert_called_once_with("example.co.kr", timeout=15)


if __name__ == "__main__":
    unittest.main()
