
import argparse
import random
import sqlite3
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Tuple


VENDORS = ["Cisco", "Juniper", "Versa"]
VENDOR_KEYWORD = {"Cisco": "interface", "Juniper": "set", "Versa": "system"}


def rand_suffix(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


def make_ipv4(valid: bool = True) -> str:
    if not valid:
        # deliberately invalid
        return random.choice(["999.1.1.1", "abc.def.1.1", "10.10.10", "256.0.0.1"])

    a = random.choice([10, 172, 192])
    if a == 10:
        return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    if a == 172:
        return f"172.{random.randint(16,31)}.{random.randint(0,255)}.{random.randint(1,254)}"
    return f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"


def make_config(vendor: str, include_required: bool = True) -> str:
    # Build some plausible config text. If include_required=False, omit vendor keyword.
    base = [
        "hostname MOCK-DEVICE",
        "logging buffered 10000",
        "ntp server 1.1.1.1",
    ]

    required = VENDOR_KEYWORD[vendor].lower()

    if include_required:
        if vendor == "Cisco":
            base += [
                "interface GigabitEthernet0/0",
                " ip address 10.0.0.1 255.255.255.0",
                " no shutdown",
            ]
        elif vendor == "Juniper":
            base += [
                "set system host-name MOCK-DEVICE",
                "set interfaces ge-0/0/0 unit 0 family inet address 10.0.0.1/24",
            ]
        else:  # Versa
            base += [
                "system",
                " system hostname MOCK-DEVICE",
                " system ntp server 1.1.1.1",
            ]
    else:
        # Omit required keyword carefully
        base += [
            "routing-options static route 0.0.0.0/0 next-hop 10.0.0.254",
            "snmp community public",
        ]
        base = [ln for ln in base if required not in ln.lower()]

    return "\n".join(base)


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            vendor TEXT NOT NULL,
            ip TEXT NOT NULL,
            config TEXT NOT NULL,
            last_validation_status TEXT,
            last_validation_at TEXT
        )
        """
    )
    conn.commit()


def reset_table(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM devices;")
    conn.commit()


def chunked(lst: List[str], n: int) -> List[List[str]]:
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def worker_insert(db_path: str, device_ids: List[str], invalid_ratio: float, unvalidated_ratio: float) -> Tuple[int, int]:
    """
    Returns: (inserted_count, skipped_count)
    """
    inserted = 0
    skipped = 0

    conn = sqlite3.connect(db_path, timeout=30)
    try:
        ensure_schema(conn)

        rows = []
        now = datetime.now(timezone.utc)

        for device_id in device_ids:
            vendor = random.choice(VENDORS)

            # Some are "bad" (invalid IP or missing keyword) to create failed-like data variety
            is_invalid = random.random() < invalid_ratio
            ip_valid = not (is_invalid and random.random() < 0.5)
            include_kw = not (is_invalid and not ip_valid)  # mix cases; still can omit keyword sometimes

            ip = make_ipv4(valid=ip_valid)
            config = make_config(vendor, include_required=include_kw)

            # Some devices have never been validated yet (None status/timestamp)
            is_unvalidated = random.random() < unvalidated_ratio
            if is_unvalidated:
                last_status = None
                last_at = None
            else:
                # Make random past timestamps
                last_at_dt = now - timedelta(minutes=random.randint(1, 60 * 24 * 14))  # up to ~2 weeks ago
                last_at = last_at_dt.isoformat()

                # Assign status; if the record is "invalid", bias toward FAILED
                if is_invalid:
                    last_status = "FAILED"
                else:
                    last_status = random.choices(["PASSED", "FAILED"], weights=[0.8, 0.2], k=1)[0]

            rows.append((device_id, vendor, ip, config, last_status, last_at))

        # Fast batched insert, ignore duplicates
        conn.executemany(
            """
            INSERT OR IGNORE INTO devices
            (device_id, vendor, ip, config, last_validation_status, last_validation_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()

        # sqlite3 doesn't directly tell "ignored" count, so estimate:
        # total attempted minus changes
        # changes() = rows inserted/updated since last statement
        # For executemany, total_changes is safest:
        inserted = conn.total_changes
        skipped = max(0, len(rows) - inserted)

        return inserted, skipped
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="./devices.db", help="Path to SQLite DB file (default: ./devices.db)")
    parser.add_argument("--count", type=int, default=200, help="Number of devices to insert")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads")
    parser.add_argument("--prefix", default="R", help="Device ID prefix (default: R)")
    parser.add_argument("--reset", action="store_true", help="Delete existing rows before inserting")
    parser.add_argument("--invalid-ratio", type=float, default=0.25, help="Fraction of devices that look 'invalid' (default 0.25)")
    parser.add_argument("--unvalidated-ratio", type=float, default=0.15, help="Fraction of devices with NULL validation fields (default 0.15)")
    args = parser.parse_args()

    db_path = str(Path(args.db).resolve())

    # Ensure DB exists and schema is present + optional reset
    conn = sqlite3.connect(db_path, timeout=30)
    try:
        ensure_schema(conn)
        if args.reset:
            reset_table(conn)
    finally:
        conn.close()

    # Build device_ids
    device_ids = [f"{args.prefix}{i:04d}" for i in range(1, args.count + 1)]

    # Split into chunks per thread
    per_thread = max(1, len(device_ids) // args.threads)
    batches = chunked(device_ids, per_thread)

    inserted_total = 0
    skipped_total = 0

    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = [
            ex.submit(worker_insert, db_path, batch, args.invalid_ratio, args.unvalidated_ratio)
            for batch in batches
        ]
        for f in as_completed(futures):
            inserted, skipped = f.result()
            inserted_total += inserted
            skipped_total += skipped

    print(f"DB: {db_path}")
    print(f"Attempted: {args.count}")
    print(f"Inserted:  {inserted_total}")
    print(f"Skipped:   {skipped_total}  (likely duplicates)")
    print("Done.")


if __name__ == "__main__":
    main()
