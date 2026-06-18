import re
import json
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any, Dict, List, Optional


def normalize_domain(domain: str) -> str:
    """
    https://www.whois.com/whois/hd.com 또는 hd.com 입력 모두 처리
    """
    domain = domain.strip().lower()

    domain = re.sub(r"^https?://", "", domain)
    domain = domain.replace("www.whois.com/whois/", "")
    domain = domain.split("/")[0]
    domain = domain.strip()

    return domain


def pick_event(events: List[Dict[str, Any]], keywords: List[str]) -> Optional[str]:
    """
    RDAP events에서 registration, expiration, last changed 등 날짜 추출
    """
    for event in events:
        action = str(event.get("eventAction", "")).lower()
        if any(k.lower() in action for k in keywords):
            return event.get("eventDate")
    return None


def extract_rdap_entity(entities: List[Dict[str, Any]], role_keyword: str) -> Dict[str, Any]:
    """
    RDAP entity에서 registrant, administrative, technical 등 역할별 정보 추출
    개인정보보호로 비공개인 경우가 많음
    """
    role_keyword = role_keyword.lower()

    for entity in entities:
        roles = [str(r).lower() for r in entity.get("roles", [])]
        if role_keyword not in roles:
            continue

        result = {
            "name": None,
            "organization": None,
            "email": None,
            "phone": None,
            "country": None,
            "raw_roles": entity.get("roles", []),
        }

        vcard = entity.get("vcardArray", [])
        if len(vcard) >= 2:
            for item in vcard[1]:
                if not isinstance(item, list) or len(item) < 4:
                    continue

                key = item[0]
                value = item[3]

                if key == "fn":
                    result["name"] = value
                elif key == "org":
                    if isinstance(value, list):
                        result["organization"] = " ".join(value)
                    else:
                        result["organization"] = value
                elif key == "email":
                    result["email"] = value
                elif key == "tel":
                    result["phone"] = value
                elif key == "adr":
                    if isinstance(value, list) and len(value) > 6:
                        result["country"] = value[6]

        return result

    return {
        "name": None,
        "organization": None,
        "email": None,
        "phone": None,
        "country": None,
        "raw_roles": [],
    }


def fetch_rdap(domain: str, timeout: int = 15) -> Dict[str, Any]:
    """
    RDAP API 기반 도메인 등록정보 조회
    """
    url = f"https://rdap.org/domain/{domain}"

    headers = {
        "User-Agent": "Mozilla/5.0 domain-rdap-parser/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        return {
            "success": False,
            "source": "rdap",
            "error": f"RDAP request failed: {exc}",
            "raw": None,
        }

    if response.status_code != 200:
        return {
            "success": False,
            "source": "rdap",
            "error": f"RDAP request failed: HTTP {response.status_code}",
            "raw": None,
        }

    try:
        data = response.json()
    except ValueError as exc:
        return {
            "success": False,
            "source": "rdap",
            "error": f"RDAP response is not valid JSON: {exc}",
            "raw": None,
        }

    events = data.get("events", [])
    entities = data.get("entities", [])

    registrant = extract_rdap_entity(entities, "registrant")
    admin = extract_rdap_entity(entities, "administrative")
    tech = extract_rdap_entity(entities, "technical")

    nameservers = []
    for ns in data.get("nameservers", []):
        ns_name = ns.get("ldhName") or ns.get("unicodeName")
        if ns_name:
            nameservers.append(ns_name)

    registrar = None
    registrar_entity = extract_rdap_entity(entities, "registrar")
    if registrar_entity.get("organization"):
        registrar = registrar_entity.get("organization")
    elif registrar_entity.get("name"):
        registrar = registrar_entity.get("name")

    return {
        "success": True,
        "source": "rdap",
        "domain": data.get("ldhName") or domain,
        "registrar": registrar,
        "creation_date": pick_event(events, ["registration"]),
        "updated_date": pick_event(events, ["last changed", "last update", "changed"]),
        "expiration_date": pick_event(events, ["expiration", "expiry"]),
        "status": data.get("status", []),
        "name_servers": nameservers,
        "registrant": registrant,
        "admin_contact": admin,
        "tech_contact": tech,
        "raw": data,
    }


def parse_whois_com_html(html: str) -> Dict[str, Any]:
    """
    whois.com/whois/{domain} 페이지 HTML에서 텍스트 기반 파싱
    whois.com은 페이지 구조가 바뀌거나 차단될 수 있으므로 보조 용도 권장
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")

    # 공백 정리
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    joined = "\n".join(lines)

    def find_value(patterns: List[str]) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, joined, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def find_all_values(patterns: List[str]) -> List[str]:
        values = []
        for pattern in patterns:
            for match in re.finditer(pattern, joined, re.IGNORECASE):
                value = match.group(1).strip()
                if value not in values:
                    values.append(value)
        return values

    return {
        "source": "whois.com",
        "domain": find_value([
            r"Domain Name:\s*([^\n]+)",
            r"Domain:\s*([^\n]+)",
        ]),
        "registrar": find_value([
            r"Registrar:\s*([^\n]+)",
            r"Sponsoring Registrar:\s*([^\n]+)",
        ]),
        "creation_date": find_value([
            r"Creation Date:\s*([^\n]+)",
            r"Created Date:\s*([^\n]+)",
            r"Registered On:\s*([^\n]+)",
            r"Domain Registration Date:\s*([^\n]+)",
        ]),
        "updated_date": find_value([
            r"Updated Date:\s*([^\n]+)",
            r"Last Updated On:\s*([^\n]+)",
            r"Domain Last Updated Date:\s*([^\n]+)",
        ]),
        "expiration_date": find_value([
            r"Registry Expiry Date:\s*([^\n]+)",
            r"Registrar Registration Expiration Date:\s*([^\n]+)",
            r"Expiration Date:\s*([^\n]+)",
            r"Expires On:\s*([^\n]+)",
        ]),
        "registrant_name": find_value([
            r"Registrant Name:\s*([^\n]+)",
        ]),
        "registrant_organization": find_value([
            r"Registrant Organization:\s*([^\n]+)",
            r"Registrant Org:\s*([^\n]+)",
        ]),
        "registrant_country": find_value([
            r"Registrant Country:\s*([^\n]+)",
        ]),
        "admin_name": find_value([
            r"Admin Name:\s*([^\n]+)",
            r"Administrative Contact Name:\s*([^\n]+)",
        ]),
        "admin_organization": find_value([
            r"Admin Organization:\s*([^\n]+)",
        ]),
        "admin_email": find_value([
            r"Admin Email:\s*([^\n]+)",
        ]),
        "tech_name": find_value([
            r"Tech Name:\s*([^\n]+)",
            r"Technical Contact Name:\s*([^\n]+)",
        ]),
        "tech_email": find_value([
            r"Tech Email:\s*([^\n]+)",
        ]),
        "name_servers": find_all_values([
            r"Name Server:\s*([^\n]+)",
            r"Nameserver:\s*([^\n]+)",
        ]),
        "status": find_all_values([
            r"Domain Status:\s*([^\n]+)",
            r"Status:\s*([^\n]+)",
        ]),
    }


def fetch_whois_com(domain: str, timeout: int = 15) -> Dict[str, Any]:
    """
    whois.com HTML 페이지에서 보조 파싱
    """
    url = f"https://www.whois.com/whois/{domain}"

    headers = {
        "User-Agent": "Mozilla/5.0 domain-whois-parser/1.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers, timeout=timeout)

    if response.status_code != 200:
        return {
            "success": False,
            "source": "whois.com",
            "error": f"whois.com request failed: HTTP {response.status_code}",
        }

    parsed = parse_whois_com_html(response.text)
    parsed["success"] = True
    parsed["url"] = url

    return parsed


def merge_domain_info(rdap_info: Dict[str, Any], whois_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    RDAP 결과를 우선 사용하고, 부족한 항목은 whois.com 결과로 보완
    """
    if not whois_info:
        whois_info = {}

    result = {
        "domain": rdap_info.get("domain") or whois_info.get("domain"),
        "registrar": rdap_info.get("registrar") or whois_info.get("registrar"),
        "creation_date": rdap_info.get("creation_date") or whois_info.get("creation_date"),
        "updated_date": rdap_info.get("updated_date") or whois_info.get("updated_date"),
        "expiration_date": rdap_info.get("expiration_date") or whois_info.get("expiration_date"),
        "status": rdap_info.get("status") or whois_info.get("status"),
        "name_servers": rdap_info.get("name_servers") or whois_info.get("name_servers"),

        "registrant": rdap_info.get("registrant") or {
            "name": whois_info.get("registrant_name"),
            "organization": whois_info.get("registrant_organization"),
            "country": whois_info.get("registrant_country"),
        },

        "admin_contact": rdap_info.get("admin_contact") or {
            "name": whois_info.get("admin_name"),
            "organization": whois_info.get("admin_organization"),
            "email": whois_info.get("admin_email"),
        },

        "tech_contact": rdap_info.get("tech_contact") or {
            "name": whois_info.get("tech_name"),
            "email": whois_info.get("tech_email"),
        },

        "source_priority": ["rdap", "whois.com"],
        "collected_at": datetime.now().isoformat(timespec="seconds"),
    }

    return result


def get_domain_registration_info(
    domain_or_url: str,
    use_whois_com_fallback: bool = True,
    include_raw: bool = False,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    도메인 등록정보를 JSON 형태의 dict로 반환한다.

    반환 항목:
    - domain
    - registrar
    - creation_date
    - updated_date
    - expiration_date
    - registrant
    - admin_contact
    - tech_contact
    - name_servers
    - status

    사용 예:
        info = get_domain_registration_info("https://www.whois.com/whois/hd.com")
        print(json.dumps(info, ensure_ascii=False, indent=2))
    """
    domain = normalize_domain(domain_or_url)

    rdap_info = fetch_rdap(domain, timeout=timeout)

    whois_info = None
    if use_whois_com_fallback:
        try:
            whois_info = fetch_whois_com(domain, timeout=timeout)
        except Exception as exc:
            whois_info = {
                "success": False,
                "source": "whois.com",
                "error": str(exc),
            }

    if rdap_info.get("success"):
        result = merge_domain_info(rdap_info, whois_info)
        result["success"] = True
    elif whois_info and whois_info.get("success"):
        result = {
            "success": True,
            "domain": whois_info.get("domain") or domain,
            "registrar": whois_info.get("registrar"),
            "creation_date": whois_info.get("creation_date"),
            "updated_date": whois_info.get("updated_date"),
            "expiration_date": whois_info.get("expiration_date"),
            "status": whois_info.get("status"),
            "name_servers": whois_info.get("name_servers"),
            "registrant": {
                "name": whois_info.get("registrant_name"),
                "organization": whois_info.get("registrant_organization"),
                "country": whois_info.get("registrant_country"),
            },
            "admin_contact": {
                "name": whois_info.get("admin_name"),
                "organization": whois_info.get("admin_organization"),
                "email": whois_info.get("admin_email"),
            },
            "tech_contact": {
                "name": whois_info.get("tech_name"),
                "email": whois_info.get("tech_email"),
            },
            "source_priority": ["whois.com"],
            "collected_at": datetime.now().isoformat(timespec="seconds"),
        }
    else:
        result = {
            "success": False,
            "domain": domain,
            "error": {
                "rdap": rdap_info.get("error"),
                "whois_com": whois_info.get("error") if whois_info else None,
            },
            "collected_at": datetime.now().isoformat(timespec="seconds"),
        }

    if include_raw:
        result["raw"] = {
            "rdap": rdap_info,
            "whois_com": whois_info,
        }

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch domain registration information using RDAP and whois.com fallback."
    )
    parser.add_argument(
        "domain",
        help="Domain or whois.com URL to look up, e.g. hd.com or https://www.whois.com/whois/hd.com",
    )
    parser.add_argument(
        "--no-whois-com-fallback",
        action="store_true",
        help="Skip the whois.com HTML fallback lookup.",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include raw RDAP and whois.com responses in the output.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Request timeout in seconds. Default: 15",
    )
    args = parser.parse_args()

    info = get_domain_registration_info(
        args.domain,
        use_whois_com_fallback=not args.no_whois_com_fallback,
        include_raw=args.include_raw,
        timeout=args.timeout,
    )
    print(json.dumps(info, ensure_ascii=False, indent=2))
