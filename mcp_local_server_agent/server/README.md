# SQLite Chinook MCP Server (Streamable HTTP)

A local **MCP server** that exposes **SQLite (Chinook)** data over **Streamable HTTP** at **`/mcp`**, designed to be:
- **Inspectable** via the MCP Inspector (tools, resources, prompts)
- **Usable by an Azure AI Agent** over a URL (e.g., via ngrok)
- **Safe for demos**: all **writes** go to a **working copy**, keeping the base dataset pristine

> Scope: Server only. See `../inspector/README.md` for Inspector usage and `../agent/README.md` for the Azure Agent flow.

---

## What the server exposes

**Transport**
- Streamable HTTP on `http://localhost:8787/mcp` (defaults shown; configurable via env)

**Tools (consolidated)**
- `list_tables()` — list tables and row counts  
- `get_table_info(table)` — columns, PKs, basic info  
- `run_sql(query, params?)` — **read-only**; rejects non-SELECT  
- `run_sql_write(query, params?)` — **write** path (INSERT/UPDATE/DELETE/REPLACE) with guardrails  
- `top_customers(limit)` — aggregate by invoice total  
- `insert_customer(first_name, last_name, email, city?, country?)` — create a customer  
- `update_customer_email(customer_id, new_email)` — update a customer’s email  
- `create_invoice(customer_id, items[])` — transactional insert of invoice + invoice_lines

**Resource**
- `schema://current` — introspected database schema (tables, columns, FKs)

**Prompt**
- `explain_query_purpose(sql)` — a terse natural-language explanation of a SQL statement

**Code organization**
```
server/
├─ app.py
├─ auth.py
├─ config.py
├─ errors.py
├─ logging.py
├─ db/
│  ├─ chinook.db          # base dataset (read-only source)
│  ├─ working/            # created at runtime for writes (safe copy)
│  └─ ...
└─ surface/
   ├─ tools.py            # all MCP tools (consolidated)
   ├─ schema.py           # MCP resource(s)
   └─ prompt.py           # MCP prompt(s)
```

---

## How writes are kept safe

- The **base dataset** (`server/db/chinook.db`) is **never modified**.
- On startup, the server creates a **working copy** at `server/db/working/chinook.work.sqlite` and directs **all writes** there.
- Stop/start to reset (the working copy is recreated from the base file).
- Optional config lets you persist the working copy across runs.

---

## Prerequisites

- **Python 3.11+** (recommended)
- Ability to create a virtual environment and install dependencies
- For inspection: **Node.js** (to run the MCP Inspector via `npx`) — see `../inspector/README.md`

---

## Configuration

Use a single repo-root `.env` for both **server** and **agent** settings (recommended). Start from the sample:

~~~bash
cp .env.sample .env
# Edit .env and set values as needed
~~~

Server-relevant variables:

| Variable | Default | Description |
|---|---:|---|
| `PORT` | `8787` | HTTP port the server listens on |
| `MCP_PATH` | `/mcp` | Mount path for the MCP endpoint |
| `DB_BASE_PATH` | `server/db/chinook.db` | Path to the pristine base DB (read-only) |
| `DB_WORKING_DIR` | `server/db/working` | Directory where the working copy is created |
| `PERSIST_WORKING_COPY` | `false` | If `true`, reuse the existing working copy across restarts |
| `LOCAL_MCP_TOKEN` | *(unset)* | If set, server requires `Authorization: Bearer <token>` |
| `LOG_LEVEL` | `info` | `debug`/`info`/`warning`/`error` |

> Recommendation: set `LOCAL_MCP_TOKEN` before exposing the server via ngrok.

---

## Install & run (server-only)

Install only the server’s dependencies:

~~~bash
# (optional) python -m venv .venv && source .venv/bin/activate
pip install -r server/requirements.txt

# run the server
python -m server.app
~~~

**Expected on first run**
- Creates `server/db/working/` (if missing)
- Copies `chinook.db` → `chinook.work.sqlite`
- Enables foreign keys, WAL mode, runs a quick integrity check
- Registers tools/resources/prompts
- Listens on `http://localhost:8787/mcp`

> If you prefer a single install for the whole repo, create a root `requirements.txt` with:  
> `-r server/requirements.txt` and `-r agent/requirements.txt`.

---

## Verify with MCP Inspector (local)

Follow `../inspector/README.md`, then connect the Inspector to:

- **Transport**: `Streamable HTTP`  
- **Server URL**: `http://localhost:8787/mcp`  
- If you set `LOCAL_MCP_TOKEN`, add header: `Authorization: Bearer <YOUR_LOCAL_MCP_TOKEN>`

Try the following:

- **Tools → `list_tables`**  
  Expect a list of Chinook tables (Album, Artist, Customer, Invoice, …).
- **Resource → `schema://current`**  
  Browse schema metadata.
- **Prompt → `explain_query_purpose`**  
  Paste a `SELECT` to see a short explanation.

---

## Try reads

Use **`run_sql`** (read-only). Sample queries:

~~~sql
SELECT Name, UnitPrice
FROM tracks
ORDER BY UnitPrice DESC, Name ASC
LIMIT 5;
~~~

~~~sql
SELECT c.CustomerId, c.FirstName, c.LastName, SUM(i.Total) AS TotalSpent
FROM customers c
LEFT JOIN invoices i ON i.CustomerId = c.CustomerId
GROUP BY c.CustomerId
ORDER BY TotalSpent DESC
LIMIT 5;
~~~

~~~sql
SELECT COUNT(*) AS n FROM invoices;
~~~

> If a non-SELECT is submitted to `run_sql`, the server will reject it.

---

## Try writes

Use **`run_sql_write`** (explicit write endpoint) or the dedicated helpers:

- **Insert customer** — `insert_customer(first_name, last_name, email, city?, country?)`  
  Returns `{ customer_id }`
- **Update email** — `update_customer_email(customer_id, new_email)`  
  Returns `{ affected_rows }`
- **Create invoice** — `create_invoice(customer_id, items[])`  
  Each item: `{ track_id, unit_price, quantity }`  
  Returns `{ invoice_id, total }`
- **Generic write** — `run_sql_write(query, params?)`  
  Accepts only `INSERT` / `UPDATE` / `DELETE` / `REPLACE` (rejects DDL & multi-statements)  
  Returns `{ affected_rows }`

Verify writes with a subsequent **`run_sql`** `SELECT`.

---

## Reset vs persist

- **Default**: stop the server → changes are discarded on next start (fresh working copy).
- To **persist** changes across runs, set `PERSIST_WORKING_COPY=true` in `.env`.
- To **manually reset**, delete the working DB file in `server/db/working/` and restart.

---

## Security notes

- If `LOCAL_MCP_TOKEN` is set, all requests must include:  
  `Authorization: Bearer <LOCAL_MCP_TOKEN>`
- Do **not** expose the MCP Inspector itself via ngrok.
- When using ngrok, expose the **server port only** (e.g., `8787`) and keep the Inspector local.

---

## Expose via ngrok (for Agent usage)

From a separate terminal:

~~~bash
ngrok http 8787
~~~

Copy the **HTTPS** forwarding URL (e.g., `https://<sub>.ngrok.app`) and use:

- **Server URL** for remote connections: `https://<sub>.ngrok.app/mcp`
- If you set a token, include: `Authorization: Bearer <YOUR_LOCAL_MCP_TOKEN>`

You’ll use this URL with your Azure AI Agent in `../agent/README.md`.

---

## Troubleshooting

- **401/403 (Unauthorized)**  
  Add/verify `Authorization: Bearer <token>`. Confirm the token matches `LOCAL_MCP_TOKEN`.
- **404 or empty discovery**  
  Ensure the URL includes **`/mcp`** and **Transport = Streamable HTTP** in Inspector.
- **DB is locked**  
  Close other processes; if needed, stop the server, delete the working copy, and restart.
- **Writes appear not to persist**  
  Default behavior discards changes on restart. Set `PERSIST_WORKING_COPY=true` to persist.
- **ngrok 502 or connection failed**  
  Verify the local server is running on `8787`, and that you’re connecting to the **HTTPS** ngrok URL with **`/mcp`**.

---

## Next steps

1. Confirm local connection with the Inspector.
2. (Optional) Expose the server via ngrok and re-verify.
3. Proceed to `../agent/README.md` to connect your Azure AI Agent to the ngrok URL.
