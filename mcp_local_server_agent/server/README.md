# SQLite Chinook MCP Server (Streamable HTTP)

A local **MCP server** that exposes **SQLite (Chinook)** data over **Streamable HTTP** at the path **`/mcp`**, designed to be:
- **Inspectable** via the MCP Inspector (tools, resources, prompts)
- **Usable by an Azure AI Agent** over a URL (e.g., via ngrok)
- **Safe for demos**: all **writes** go to a **working copy**, keeping the base dataset pristine

> Scope: This guide covers the server only (no code shown here). See `../inspector/README.md` for Inspector usage and `../agent/README.md` for the Azure Agent flow.

---

## What the server exposes

**Transport**
- Streamable HTTP on `http://localhost:8787/mcp` (defaults shown; configurable via env)

**Tools (planned)**
- `list_tables()` — list tables and row counts
- `get_table_info(table)` — columns, PKs, basic info
- `run_sql(query, params?)` — **read-only**; rejects non-SELECT
- `run_sql_write(query, params?)` — **write** path for INSERT/UPDATE/DELETE with guardrails
- `top_customers(limit)` — aggregate by invoice total
- `insert_customer(first_name, last_name, email, city?, country?)` — create a customer
- `update_customer_email(customer_id, new_email)` — update a customer’s email
- `create_invoice(customer_id, items[])` — transactional insert of invoice + invoice_lines

**Resources**
- `schema://current` — introspected database schema (tables, columns, FKs)

**Prompts**
- `explain_query_purpose(sql)` — returns a natural-language explanation of a SQL statement

---

## How writes are kept safe

- The **base dataset** (e.g., `server/db/chinook.sqlite`) is **never modified**.
- On startup, the server creates a **working copy** (e.g., `server/db/working/chinook.work.sqlite`) and directs **all writes** there.
- Stop/start to reset (the working copy is recreated from the base file).
- Optional config: keep/persist the working copy across runs.

---

## Prerequisites

- **Python 3.11+** (recommended)
- Ability to create a virtual environment and install dependencies
- For inspection: **Node.js** (to run the MCP Inspector via `npx`) — see `../inspector/README.md`

---

## Configure

Create your environment file at the repo root (or export shell vars directly):

~~~bash
cp .env.sample .env
# Edit .env and set values as needed
~~~

Server-relevant variables:

| Variable | Default | Description |
|---|---:|---|
| `PORT` | `8787` | HTTP port the server listens on |
| `MCP_PATH` | `/mcp` | Mount path for the MCP endpoint |
| `DB_BASE_PATH` | `server/db/chinook.sqlite` | Path to the pristine base DB (read-only) |
| `DB_WORKING_DIR` | `server/db/working` | Directory where the working copy is created |
| `PERSIST_WORKING_COPY` | `false` | If `true`, reuse the existing working copy across restarts |
| `LOCAL_MCP_TOKEN` | *(unset)* | If set, server requires `Authorization: Bearer <token>` |
| `LOG_LEVEL` | `info` | `debug`/`info`/`warning`/`error` |

> Recommendation: set `LOCAL_MCP_TOKEN` before exposing the server via ngrok.

---

## Start the server (local)

From the repo root:

~~~bash
# (once) create & activate venv, install server deps
# python -m venv .venv && source .venv/bin/activate
# pip install -r requirements.txt

# run the server (actual command provided in implementation step)
# example placeholder:
# python server/app.py
~~~

**Expected behavior on first run**
- Creates `server/db/working/` (if missing)
- Copies `chinook.sqlite` → `chinook.work.sqlite`
- Enables foreign keys, WAL mode, runs a quick integrity check
- Logs tools/resources/prompts registered
- Listens on `http://localhost:8787/mcp`

---

## Verify with MCP Inspector (local)

Follow `../inspector/README.md`, then connect the Inspector to:

- **Transport**: `Streamable HTTP`
- **Server URL**: `http://localhost:8787/mcp`
- If you set `LOCAL_MCP_TOKEN`, add header:  
  `Authorization: Bearer <YOUR_LOCAL_MCP_TOKEN>`

Try the following:

- **Tools → `list_tables`**  
  Expect a list of Chinook tables (Album, Artist, Customer, Invoice, …).
- **Resources → `schema://current`**  
  Browse schema metadata.
- **Prompts → `explain_query_purpose`**  
  Paste a `SELECT` to see a short explanation.

---

## Try reads

Use **`run_sql`** (read-only). Examples you can paste into the Inspector:

- Top 5 tracks by unit price:

~~~sql
SELECT Name, UnitPrice
FROM tracks
ORDER BY UnitPrice DESC, Name ASC
LIMIT 5;
~~~

- Customer + total invoice:

~~~sql
SELECT c.CustomerId, c.FirstName, c.LastName, SUM(i.Total) AS TotalSpent
FROM customers c
LEFT JOIN invoices i ON i.CustomerId = c.CustomerId
GROUP BY c.CustomerId
ORDER BY TotalSpent DESC
LIMIT 5;
~~~

- Table row count (parameterize with `params` if needed):

~~~sql
SELECT COUNT(*) AS n FROM invoices;
~~~

> If a non-SELECT is submitted to `run_sql`, the server will reject it.

---

## Try writes

Use **`run_sql_write`** (explicit write endpoint) or the dedicated helpers:

- **Insert customer** (using the **`insert_customer`** tool):
  - Inputs: `first_name`, `last_name`, `email`, optional `city`, `country`
  - Output: `{ customer_id }`

- **Update email** (using **`update_customer_email`**):
  - Inputs: `customer_id`, `new_email`
  - Output: `{ affected_rows }`

- **Create invoice** (using **`create_invoice`**):
  - Inputs: `customer_id`, `items[]` where each item is `{ track_id, unit_price, quantity }`
  - Output: `{ invoice_id, total }`

- **Generic write** (using **`run_sql_write`**):
  - Accepts only `INSERT` / `UPDATE` / `DELETE`
  - Limits & validation applied (e.g., reject DDL unless explicitly allowed by config)
  - Output: `{ affected_rows }`

Verify writes with a subsequent **`run_sql`** `SELECT`.

---

## Reset vs persist

- **Default behavior**: stop the server → changes are discarded at next start (fresh working copy).
- To **persist** changes across runs, set:
  - `PERSIST_WORKING_COPY=true` in `.env`
- To **manually reset**, delete the working DB file inside `server/db/working/` and restart.

---

## Security notes

- If `LOCAL_MCP_TOKEN` is set, all requests must include:
  - Header: `Authorization: Bearer <LOCAL_MCP_TOKEN>`
- Do **not** expose the MCP Inspector itself via ngrok.
- When using ngrok, expose the **server port only** (e.g., 8787) and keep the Inspector local.

---

## Expose via ngrok (for Agent usage)

From a separate terminal:

~~~bash
# Expose the server’s local port (8787)
ngrok http 8787
~~~

Copy the **HTTPS** forwarding URL (e.g., `https://<sub>.ngrok.app`) and use:

- **Server URL** for remote connections: `https://<sub>.ngrok.app/mcp`
- If you set a token, include: `Authorization: Bearer <LOCAL_MCP_TOKEN>`

You’ll use this URL with your Azure AI Agent in `../agent/README.md`.

---

## Troubleshooting

- **401/403 (Unauthorized)**  
  Add/verify `Authorization: Bearer <token>`. Confirm the token value matches `LOCAL_MCP_TOKEN`.

- **404 or empty discovery**  
  Ensure the URL includes the **`/mcp`** path and **Transport = Streamable HTTP** in Inspector.

- **DB is locked**  
  Close other processes accessing the working DB; if needed, stop the server, delete the working copy, and restart.

- **Writes appear not to persist**  
  By default they won’t after restart. Set `PERSIST_WORKING_COPY=true` to reuse the working DB.

- **ngrok 502 or connection failed**  
  Verify the local server is running on `8787`, and that you’re connecting to the **HTTPS** ngrok URL with the **`/mcp`** path.

---

## Extensibility

- Add domain-focused tool modules (e.g., `albums.py`, `reports.py`).
- Add more resources (e.g., `schema://tables/<name>`).
- Add prompts for common explanations (e.g., “summarize invoice history for a customer”).

---

## Next steps

1. Confirm you can connect locally with the Inspector.
2. (Optional) Expose the server via ngrok and re-verify.
3. Proceed to `../agent/README.md` to connect your Azure AI Agent to the ngrok URL.
