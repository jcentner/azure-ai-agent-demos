from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Sequence

from mcp.server.fastmcp import FastMCP

from ..db.client import Database, is_select, is_write, execute_read, execute_write


_email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def register(mcp: FastMCP, db: Database) -> None:
    # ---------- Tables ----------
    @mcp.tool()
    def list_tables() -> dict[str, Any]:
        """List tables and row counts."""
        with db.transaction() as con:
            names = [
                r[0]
                for r in con.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
                ).fetchall()
            ]
            out = []
            for nm in names:
                cnt = con.execute(f"SELECT COUNT(*) FROM '{nm}';").fetchone()[0]
                out.append({"name": nm, "row_count": int(cnt)})
            return {"tables": out}

    @mcp.tool()
    def get_table_info(table: str) -> dict[str, Any]:
        """Basic schema for a table."""
        with db.transaction() as con:
            cols = [
                {
                    "name": r["name"],
                    "type": r["type"],
                    "pk": bool(r["pk"]),
                    "not_null": bool(r["notnull"]),
                    "default": r["dflt_value"],
                }
                for r in con.execute(f"PRAGMA table_info('{table}');").fetchall()
            ]
            fks = [
                {"from": r["from"], "to_table": r["table"], "to_column": r["to"]}
                for r in con.execute(f"PRAGMA foreign_key_list('{table}');").fetchall()
            ]
            if not cols:
                raise ValueError(f"Table not found or has no columns: {table}")
            return {"name": table, "columns": cols, "foreign_keys": fks}

    # ---------- Raw SQL (read/write) ----------
    @mcp.tool()
    def run_sql(query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a single SELECT (read-only)."""
        if not is_select(query):
            raise ValueError("run_sql only accepts a single SELECT statement.")
        with db.transaction() as con:
            cols, rows = execute_read(con, query, params or {})
        return {"columns": cols, "rows": rows, "row_count": len(rows)}

    @mcp.tool()
    def run_sql_write(query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a single INSERT/UPDATE/DELETE/REPLACE (write)."""
        if not is_write(query):
            raise ValueError("run_sql_write only accepts a single INSERT/UPDATE/DELETE/REPLACE statement.")
        with db.transaction() as con:
            affected = execute_write(con, query, params or {})
        return {"affected_rows": affected}

    # ---------- Customers ----------
    @mcp.tool()
    def insert_customer(
        first_name: str,
        last_name: str,
        email: str,
        city: str | None = None,
        country: str | None = None,
    ) -> dict[str, int]:
        """Insert a new customer, return its id."""
        if not _email_re.match(email):
            raise ValueError("Invalid email format.")
        with db.transaction() as con:
            cur = con.execute(
                """
                INSERT INTO Customer (FirstName, LastName, Email, City, Country)
                VALUES (:fn, :ln, :em, :city, :country)
                """,
                {"fn": first_name, "ln": last_name, "em": email, "city": city, "country": country},
            )
            return {"customer_id": int(cur.lastrowid)}

    @mcp.tool()
    def update_customer_email(customer_id: int, new_email: str) -> dict[str, int]:
        """Update a customer's email."""
        if not _email_re.match(new_email):
            raise ValueError("Invalid email format.")
        with db.transaction() as con:
            cur = con.execute(
                "UPDATE Customer SET Email = :em WHERE CustomerId = :cid",
                {"em": new_email, "cid": customer_id},
            )
            return {"affected_rows": int(cur.rowcount or 0)}

    # ---------- Sales / Invoices ----------
    @mcp.tool()
    def top_customers(limit: int = 5):
        """Top N customers by total invoice amount."""
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        with db.transaction() as con:
            rows = con.execute(
                """
                SELECT c.CustomerId, c.FirstName, c.LastName, c.Email, IFNULL(SUM(i.Total), 0.0) AS TotalSpent
                FROM Customer c
                LEFT JOIN Invoice i ON i.CustomerId = c.CustomerId
                GROUP BY c.CustomerId
                ORDER BY TotalSpent DESC, c.CustomerId ASC
                LIMIT :lim
                """,
                {"lim": limit},
            ).fetchall()
            return [
                {
                    "customer_id": int(r["CustomerId"]),
                    "first_name": r["FirstName"],
                    "last_name": r["LastName"],
                    "email": r["Email"],
                    "total_spent": float(r["TotalSpent"]),
                }
                for r in rows
            ]

    @mcp.tool()
    def create_invoice(customer_id: int, items: Sequence[dict]) -> dict:
        """
        Create an invoice and invoice lines.
        Each item: { track_id: int, unit_price: float, quantity: int>0 }
        """
        if not items:
            raise ValueError("items must be a non-empty list")
        for it in items:
            if not all(k in it for k in ("track_id", "unit_price", "quantity")):
                raise ValueError("each item must include track_id, unit_price, quantity")
            if int(it["quantity"]) <= 0:
                raise ValueError("quantity must be > 0")

        with db.transaction() as con:
            total = sum(float(it["unit_price"]) * int(it["quantity"]) for it in items)
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cur = con.execute(
                """
                INSERT INTO Invoice (CustomerId, InvoiceDate, BillingAddress, BillingCity,
                                     BillingState, BillingCountry, BillingPostalCode, Total)
                VALUES (:cid, :dt, :addr, :city, :state, :country, :zip, :total)
                """,
                {
                    "cid": customer_id,
                    "dt": now,
                    "addr": "",
                    "city": "",
                    "state": None,
                    "country": "",
                    "zip": "",
                    "total": total,
                },
            )
            invoice_id = cur.lastrowid

            for it in items:
                con.execute(
                    """
                    INSERT INTO InvoiceLine (InvoiceId, TrackId, UnitPrice, Quantity)
                    VALUES (:iid, :tid, :price, :qty)
                    """,
                    {
                        "iid": invoice_id,
                        "tid": int(it["track_id"]),
                        "price": float(it["unit_price"]),
                        "qty": int(it["quantity"]),
                    },
                )

            return {"invoice_id": int(invoice_id), "total": float(total)}
