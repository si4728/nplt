import argparse
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from nplt_whois import get_domain_registration_info, normalize_domain


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": os.getenv("NPLT_DB_PASSWORD", "P@ssw0rd!@#$"),
    "database": "nplt",
}

DOMAIN_TABLE = "domain"
DOMAIN_KEY_COLUMN = "url_i"
WHOIS_UPDATE_COLUMNS = {
    "registrar",
    "creation_date",
    "expiration_date",
    "updated_date",
    "isp",
    "registrant",
    "domain_status",
    "name_servers",
    "whois_error",
    "lastdate",
}


def load_mysql_driver():
    try:
        import pymysql

        return "pymysql", pymysql
    except ImportError:
        pass

    try:
        import mysql.connector

        return "mysql.connector", mysql.connector
    except ImportError as exc:
        raise RuntimeError(
            "MySQL driver is not installed. Install one of these packages: "
            "pip install pymysql  or  pip install mysql-connector-python"
        ) from exc


def connect_mysql(args: argparse.Namespace):
    driver_name, driver = load_mysql_driver()

    if driver_name == "pymysql":
        return driver.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
            charset="utf8mb4",
            autocommit=False,
            cursorclass=driver.cursors.DictCursor,
        )

    return driver.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        autocommit=False,
    )


def cursor_dict(conn):
    try:
        return conn.cursor(dictionary=True)
    except TypeError:
        return conn.cursor()


def quote_identifier(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def get_table_columns(conn, table_name: str) -> List[str]:
    with cursor_dict(conn) as cur:
        cur.execute(f"SHOW COLUMNS FROM {quote_identifier(table_name)}")
        rows = cur.fetchall()
    return [row["Field"] for row in rows]


def fetch_domain_urls(
    conn,
    table_name: str,
    key_column: str,
    limit: Optional[int],
    where: Optional[str],
) -> List[str]:
    sql = (
        f"SELECT {quote_identifier(key_column)} "
        f"FROM {quote_identifier(table_name)} "
        f"WHERE {quote_identifier(key_column)} IS NOT NULL "
        f"AND {quote_identifier(key_column)} <> ''"
    )

    if where:
        sql += f" AND ({where})"

    sql += f" ORDER BY {quote_identifier(key_column)}"

    if limit:
        sql += " LIMIT %s"
        params: Sequence[Any] = (limit,)
    else:
        params = ()

    with cursor_dict(conn) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [str(row[key_column]).strip() for row in rows if row.get(key_column)]


def first_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", []):
            return value
    return None


def join_list(value: Any) -> Optional[str]:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    if value in (None, ""):
        return None
    return str(value)


def truncate(value: Any, max_length: int = 100) -> Optional[str]:
    if value in (None, ""):
        return None
    text = str(value)
    if len(text) <= max_length:
        return text
    return text[:max_length]


def format_whois_error(info: Dict[str, Any]) -> Optional[str]:
    error = info.get("error")
    if isinstance(error, dict):
        parts = []
        for key, value in error.items():
            if value:
                parts.append(f"{key}: {value}")
        return "; ".join(parts) if parts else None
    return error


def print_lookup_result(url: str, info: Dict[str, Any]) -> None:
    registrant = info.get("registrant") or {}

    print("lookup result:")
    print(f"  url_i: {url}")
    print(f"  success: {info.get('success')}")
    print(f"  domain: {info.get('domain')}")
    print(f"  registrar: {info.get('registrar')}")
    print(f"  registrant: {first_value(registrant.get('organization'), registrant.get('name'))}")
    print(f"  creation_date: {info.get('creation_date')}")
    print(f"  expiration_date: {info.get('expiration_date')}")
    print(f"  updated_date: {info.get('updated_date')}")
    print(f"  status: {join_list(info.get('status'))}")
    print(f"  name_servers: {join_list(info.get('name_servers'))}")
    print(f"  error: {format_whois_error(info)}")


def flatten_whois_info(info: Dict[str, Any]) -> Dict[str, Any]:
    registrant = info.get("registrant") or {}

    return {
        "registrar": truncate(info.get("registrar"), 250),
        "isp": truncate(info.get("registrar"), 100),
        "creation_date": truncate(info.get("creation_date"), 100),
        "updated_date": truncate(info.get("updated_date"), 100),
        "expiration_date": truncate(info.get("expiration_date"), 100),
        "registrant": truncate(
            first_value(registrant.get("organization"), registrant.get("name")),
            100,
        ),
        "domain_status": truncate(join_list(info.get("status")), 100),
        "name_servers": truncate(join_list(info.get("name_servers")), 100),
        "whois_error": truncate(format_whois_error(info), 100),
        "lastdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def build_update_values(columns: Iterable[str], info: Dict[str, Any]) -> Dict[str, Any]:
    flattened = flatten_whois_info(info)
    return {
        column: flattened[column]
        for column in columns
        if column in WHOIS_UPDATE_COLUMNS
        and column in flattened
        and column != DOMAIN_KEY_COLUMN
    }


def update_domain_row(
    conn,
    table_name: str,
    key_column: str,
    key_value: str,
    values: Dict[str, Any],
) -> int:
    if not values:
        return 0

    assignments = ", ".join(f"{quote_identifier(column)} = %s" for column in values)
    sql = (
        f"UPDATE {quote_identifier(table_name)} "
        f"SET {assignments} "
        f"WHERE {quote_identifier(key_column)} = %s"
    )
    params: Tuple[Any, ...] = tuple(values.values()) + (key_value,)

    with cursor_dict(conn) as cur:
        cur.execute(sql, params)
        return cur.rowcount


def sync_domain_whois(args: argparse.Namespace) -> None:
    conn = connect_mysql(args)

    try:
        columns = get_table_columns(conn, args.table)
        if args.key_column not in columns:
            raise RuntimeError(
                f"{args.table} table does not have key column: {args.key_column}"
            )

        urls = fetch_domain_urls(
            conn,
            table_name=args.table,
            key_column=args.key_column,
            limit=args.limit,
            where=args.where,
        )

        print(f"target rows: {len(urls)}")

        total_updated = 0
        for index, url in enumerate(urls, start=1):
            domain = normalize_domain(url)
            print(f"[{index}/{len(urls)}] lookup {url} -> {domain}")

            info = get_domain_registration_info(
                domain,
                use_whois_com_fallback=not args.no_whois_com_fallback,
                include_raw=args.include_raw,
                timeout=args.timeout,
            )

            values = build_update_values(columns, info)

            if args.print_json:
                print(json.dumps(info, ensure_ascii=False, indent=2))
            elif args.print_result:
                print_lookup_result(url, info)

            if args.dry_run:
                print(f"dry-run update columns: {', '.join(values) or '(none)'}")
            else:
                updated = update_domain_row(
                    conn,
                    table_name=args.table,
                    key_column=args.key_column,
                    key_value=url,
                    values=values,
                )
                conn.commit()
                total_updated += updated
                print(f"updated rows: {updated}")

            if args.sleep > 0:
                time.sleep(args.sleep)

        print(f"done. total updated rows: {total_updated}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read domain.url_i values from MySQL/MariaDB nplt DB, "
            "call nplt_whois.py lookup function, and update available WHOIS columns."
        )
    )
    parser.add_argument("--host", default=DB_CONFIG["host"])
    parser.add_argument("--port", type=int, default=DB_CONFIG["port"])
    parser.add_argument("--user", default=DB_CONFIG["user"])
    parser.add_argument(
        "--password",
        default=DB_CONFIG["password"],
        help="DB password. If omitted, NPLT_DB_PASSWORD environment variable is used.",
    )
    parser.add_argument("--database", default=DB_CONFIG["database"])
    parser.add_argument("--table", default=DOMAIN_TABLE)
    parser.add_argument("--key-column", default=DOMAIN_KEY_COLUMN)
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--where",
        help="Extra SQL condition appended to the WHERE clause. Example: \"whois_updated_at IS NULL\"",
    )
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--include-raw", action="store_true")
    parser.add_argument("--no-whois-com-fallback", action="store_true")
    parser.add_argument(
        "--print-result",
        action="store_true",
        help="Print a readable summary of each WHOIS lookup result.",
    )
    parser.add_argument("--print-json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    sync_domain_whois(parse_args())
