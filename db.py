"""Database layer: creates a sample SQLite database, reads its schema, runs queries safely."""
import os
import random
import sqlite3
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales.db")

FIRST_NAMES = ["Aarav", "Ananya", "Vikram", "Priya", "Rahul", "Sneha", "Kiran", "Divya",
               "Arjun", "Meena", "Suresh", "Lakshmi", "Rohit", "Pooja", "Sanjay", "Nikhil"]
LAST_NAMES = ["Reddy", "Sharma", "Rao", "Naidu", "Patel", "Kumar", "Singh", "Iyer", "Gupta", "Das"]
CITIES = ["Hyderabad", "Vijayawada", "Bengaluru", "Chennai", "Mumbai", "Delhi", "Pune", "Kolkata"]
PRODUCTS = [
    ("Laptop", "Electronics", 55000), ("Smartphone", "Electronics", 22000),
    ("Headphones", "Electronics", 2500), ("Smartwatch", "Electronics", 6000),
    ("Tablet", "Electronics", 18000), ("Office Chair", "Furniture", 7500),
    ("Study Desk", "Furniture", 9000), ("Bookshelf", "Furniture", 5500),
    ("Sofa", "Furniture", 28000), ("Running Shoes", "Fashion", 3200),
    ("T-Shirt", "Fashion", 700), ("Jeans", "Fashion", 1800),
    ("Jacket", "Fashion", 3500), ("Backpack", "Fashion", 1500),
    ("Notebook Pack", "Stationery", 250), ("Pen Set", "Stationery", 180),
    ("Desk Lamp", "Home", 1200), ("Water Bottle", "Home", 450),
    ("Mixer Grinder", "Home", 3800), ("Air Fryer", "Home", 6500),
]
STATUSES = ["Delivered", "Delivered", "Delivered", "Shipped", "Cancelled", "Returned"]


def init_db(force: bool = False) -> None:
    """Create the sample database (only if it does not exist yet)."""
    if os.path.exists(DB_PATH) and not force:
        return
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    random.seed(42)  # same data every time
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            signup_date TEXT NOT NULL
        );
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        );
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        CREATE TABLE order_items (
            item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        """
    )

    start, end = date(2025, 1, 1), date(2026, 10, 31)
    span = (end - start).days

    for cid in range(1, 61):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        signup = start + timedelta(days=random.randint(0, 300))
        cur.execute("INSERT INTO customers VALUES (?,?,?,?)",
                    (cid, name, random.choice(CITIES), signup.isoformat()))

    for pid, (pname, cat, price) in enumerate(PRODUCTS, start=1):
        cur.execute("INSERT INTO products VALUES (?,?,?,?)", (pid, pname, cat, price))

    item_id = 1
    for oid in range(1, 401):
        odate = start + timedelta(days=random.randint(0, span))
        cur.execute("INSERT INTO orders VALUES (?,?,?,?)",
                    (oid, random.randint(1, 60), odate.isoformat(), random.choice(STATUSES)))
        for _ in range(random.randint(1, 3)):
            cur.execute("INSERT INTO order_items VALUES (?,?,?,?)",
                        (item_id, oid, random.randint(1, len(PRODUCTS)), random.randint(1, 4)))
            item_id += 1

    con.commit()
    con.close()


def get_schema() -> str:
    """Return the database schema as text. This text goes into the LLM prompt."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    lines = []
    for t in tables:
        cols = cur.execute(f"PRAGMA table_info({t})").fetchall()
        col_text = []
        for _, cname, ctype, _, _, pk in cols:
            extra = " PRIMARY KEY" if pk else ""
            hint = ""
            if ctype.upper() == "TEXT":
                vals = [r[0] for r in cur.execute(
                    f"SELECT DISTINCT {cname} FROM {t} LIMIT 11")]
                if 0 < len(vals) <= 8:  # short list of values helps the LLM
                    hint = f"  -- values: {', '.join(map(str, vals))}"
            col_text.append(f"    {cname} {ctype}{extra}{hint}")
        lines.append(f"TABLE {t} (\n" + "\n".join(col_text) + "\n)")
        for fk in cur.execute(f"PRAGMA foreign_key_list({t})").fetchall():
            lines.append(f"-- {t}.{fk[3]} -> {fk[2]}.{fk[4]}")
    con.close()
    lines.append("-- Dates are stored as TEXT in YYYY-MM-DD format.")
    return "\n".join(lines)


def run_query(sql: str, limit: int = 500):
    """Run a query on a READ-ONLY connection. Returns (columns, rows)."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        cur = con.cursor()
        cur.execute(sql)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = [list(r) for r in cur.fetchmany(limit)]
        return columns, rows
    finally:
        con.close()


if __name__ == "__main__":
    init_db(force=True)
    print("Database created:", DB_PATH)
    print(get_schema())
