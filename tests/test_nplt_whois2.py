import unittest

import nplt_whois2


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.responses.pop(0))


class WhoisTests(unittest.TestCase):
    def test_normalize_domain_removes_scheme_www_and_path(self):
        self.assertEqual(
            nplt_whois2.normalize_domain(
                "https://www.onbranding.co.kr/contact/index.html"
            ),
            "onbranding.co.kr",
        )

    def test_parse_kisa_response_normalizes_fields(self):
        payload = {
            "response": {
                "result": {"result_code": "10000", "result_msg": "OK"},
                "whois": {
                    "domain_name": "onbranding.co.kr",
                    "registered_date": "2018.07.27",
                    "expiration_date": "2030.07.27",
                    "agency": "Example Registrar",
                    "name_server": ["NS2.EXAMPLE.COM.", "ns1.example.com."],
                },
            }
        }
        result = nplt_whois2.parse_kisa_response(
            payload, "onbranding.co.kr"
        )
        self.assertEqual(result["Domain_Name"], "onbranding.co.kr")
        self.assertEqual(result["Creation_Date"], "2018-07-27")
        self.assertEqual(result["Expiration_Date"], "2030-07-27")
        self.assertEqual(
            result["Name_Server"],
            ["ns1.example.com", "ns2.example.com"],
        )
        self.assertEqual(result["Lookup_Source"], "KISA WHOIS OpenAPI")

    def test_missing_api_key_uses_dns_fallback(self):
        dns_payload = {
            "Answer": [
                {"name": "onbranding.co.kr.", "type": 2, "data": "ns2.cafe24.com."},
                {"name": "onbranding.co.kr.", "type": 2, "data": "ns1.cafe24.com."},
            ]
        }
        session = FakeSession([dns_payload])
        result = nplt_whois2.nplt_whois(
            "www.onbranding.co.kr", api_key="", session=session
        )
        self.assertEqual(result["Domain_Name"], "onbranding.co.kr")
        self.assertEqual(result["Lookup_Source"], "DNS fallback")
        self.assertIn("not configured", result["Lookup_Error"])
        self.assertEqual(
            result["Name_Server"],
            ["ns1.cafe24.com", "ns2.cafe24.com"],
        )

    def test_kisa_error_raises_value_error(self):
        payload = {
            "whois": {
                "error": {
                    "error_code": "020",
                    "error_msg": "API key required",
                }
            }
        }
        with self.assertRaisesRegex(ValueError, "API key required"):
            nplt_whois2.parse_kisa_response(payload, "example.co.kr")


if __name__ == "__main__":
    unittest.main()
