import os
from datetime import date, datetime
from urllib.parse import urlparse

import requests


DEFAULT_KISA_API_URL = "https://whois.kr/openapi/whois.jsp"
DNS_API_URL = "https://dns.google/resolve"
REQUEST_TIMEOUT = (10, 30)


def normalize_domain(value):
    value = (value or "").strip().lower()
    if "://" in value:
        value = urlparse(value).hostname or ""
    else:
        value = value.split("/", 1)[0].split(":", 1)[0]
    return value[4:] if value.startswith("www.") else value


def _first_value(data, keys):
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in keys and value not in (None, "", [], {}):
                return value
        for value in data.values():
            found = _first_value(value, keys)
            if found not in (None, "", [], {}):
                return found
    elif isinstance(data, list):
        for value in data:
            found = _first_value(value, keys)
            if found not in (None, "", [], {}):
                return found
    return None


def _as_text(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value).strip() if value is not None else ""


def _parse_date(value):
    text = _as_text(value)
    if not text:
        return ""
    normalized = text[:10].replace(".", "-").replace("/", "-")
    try:
        return datetime.strptime(normalized, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return normalized


def _normalize_nameservers(value):
    if not value:
        return []
    if isinstance(value, str):
        values = value.replace(",", " ").split()
    elif isinstance(value, dict):
        values = list(value.values())
    else:
        values = value
    return sorted(
        {
            str(item).strip().lower().rstrip(".")
            for item in values
            if str(item).strip()
        }
    )


def _days_until(expiration_date):
    if not expiration_date:
        return None
    try:
        return (date.fromisoformat(expiration_date) - date.today()).days
    except ValueError:
        return None


def parse_kisa_response(payload, domain):
    error_code = _first_value(payload, {"error_code", "result_code"})
    error_message = _first_value(payload, {"error_msg", "result_msg"})
    if error_code and str(error_code) not in {"0", "00", "10000"}:
        raise ValueError(_as_text(error_message) or f"KISA error {error_code}")

    expiration_date = _parse_date(
        _first_value(
            payload,
            {
                "expiration_date",
                "expiry_date",
                "expiredate",
                "expirationdate",
            },
        )
    )
    nameservers = _normalize_nameservers(
        _first_value(
            payload,
            {
                "name_server",
                "nameserver",
                "nameservers",
                "hostname",
                "host_name",
            },
        )
    )
    result = {
        "Domain_Name": _as_text(
            _first_value(payload, {"domain_name", "domain", "name"})
        )
        or domain,
        "Registrar": _as_text(
            _first_value(
                payload,
                {"registrar", "registrant", "registrant_name", "registrantname"},
            )
        ),
        "Agency": _as_text(
            _first_value(payload, {"agency", "registrar_name", "registrarname"})
        ),
        "Creation_Date": _parse_date(
            _first_value(
                payload,
                {"creation_date", "created_date", "registered_date", "regdate"},
            )
        ),
        "Expiration_Date": expiration_date,
        "Updated_Date": _parse_date(
            _first_value(
                payload,
                {"updated_date", "last_updated_date", "lastupdateddate"},
            )
        ),
        "Name_Server": nameservers,
        "NoDRfexpire": _days_until(expiration_date),
        "Lookup_Source": "KISA WHOIS OpenAPI",
    }
    return {key: value for key, value in result.items() if value not in ("", [])}


def query_kisa(domain, api_key=None, session=None):
    api_key = api_key or os.getenv("NPLT_WHOIS_API_KEY", "")
    if not api_key:
        raise ValueError("WHOIS API key is not configured")

    api_url = os.getenv("NPLT_WHOIS_API_URL", DEFAULT_KISA_API_URL)
    client = session or requests.Session()
    response = client.get(
        api_url,
        params={"query": domain, "key": api_key, "answer": "json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return parse_kisa_response(response.json(), domain)


def query_dns_nameservers(domain, session=None):
    client = session or requests.Session()
    response = client.get(
        DNS_API_URL,
        params={"name": domain, "type": "NS"},
        headers={"Accept": "application/dns-json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    nameservers = sorted(
        {
            answer.get("data", "").strip().lower().rstrip(".")
            for answer in payload.get("Answer", [])
            if answer.get("type") == 2 and answer.get("data")
        }
    )
    return nameservers


def nplt_whois(url, api_key=None, session=None):
    domain = normalize_domain(url)
    if not domain:
        return {
            "Lookup_Source": "none",
            "Lookup_Error": "Invalid domain",
        }

    try:
        return query_kisa(domain, api_key=api_key, session=session)
    except (requests.RequestException, ValueError, TypeError) as error:
        result = {
            "Domain_Name": domain,
            "Lookup_Source": "DNS fallback",
            "Lookup_Error": str(error),
        }
        try:
            nameservers = query_dns_nameservers(domain, session=session)
            if nameservers:
                result["Name_Server"] = nameservers
        except (requests.RequestException, ValueError, TypeError) as dns_error:
            result["Lookup_Error"] = f"{error}; DNS lookup failed: {dns_error}"
        return result
