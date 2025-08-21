# MCP Inspector — connect to your local & ngrok-exposed server

This guide shows how to run the **MCP Inspector**, connect it to the sample MCP server you’ll run locally (Streamable HTTP at `/mcp`), and then verify tools/resources/prompts. You’ll also see how to point the Inspector at the **public ngrok URL** when you expose your server.

> Scope: Inspector usage only. The SQLite Chinook server (read **and** write) and the Azure Agent steps live in sibling guides.

---

## What you’ll do

1. Start the MCP Inspector (no install; run via `npx`).
2. Connect to your **local** MCP server (e.g., `http://localhost:8787/mcp`).
3. Call tools, view resources, and try prompts from the Inspector UI.
4. Optionally connect to your **ngrok** URL (e.g., `https://<sub>.ngrok.app/mcp`) for remote testing.

---

## Prerequisites

- **Node.js** available on your machine (so `npx` works); see below. 
- Your **local MCP server** running (you’ll start it from `../server` in the next step of the demo).  
  - Default URL used throughout this demo: `http://localhost:8787/mcp`
- If you enable bearer auth on your server, have a token ready (e.g., from `LOCAL_MCP_TOKEN` in your `.env`).

> You do **not** need to install the Inspector globally.

### Get Node.js & `npx`

You need **Node.js LTS** (which includes `npm` and `npx`). Pick one path:

#### macOS (Homebrew)

~~~bash
brew install node
node -v && npm -v && npx --version
~~~

#### Windows (Winget, PowerShell)

~~~powershell
winget install OpenJS.NodeJS.LTS
node -v; npm -v; npx --version
~~~

(Alternative: `choco install nodejs-lts` if you use Chocolatey.)

#### Ubuntu/Debian (APT)

~~~bash
sudo apt-get update
sudo apt-get install -y nodejs npm
node -v && npm -v && npx --version
~~~

> Tip: If `node -v` prints an old version, consider using **nvm** to install the latest LTS.

#### Troubleshooting

- **`npx: command not found`** → Node.js/npm isn’t on `PATH` or too old. Reinstall Node.js LTS, then re-open your terminal.
- **Corporate machines** → If you can’t use package managers, install Node.js LTS from your IT software catalog or the standard installer for your OS; ensure `node`, `npm`, and `npx` are available in a new terminal.

Once `npx` works, continue with the Quickstart below. 

---

## Quickstart

From the repo root (or from this folder), no further install necessary:

~~~bash
# Launch the MCP Inspector UI
npx @modelcontextprotocol/inspector@latest
~~~

The CLI will print the local web address for the Inspector UI. Open it in your browser.

---

## Connect to your **local** MCP server

In the Inspector UI:

1. Choose **Transport**: `Streamable HTTP`.
2. **Server URL**: `http://localhost:8787/mcp`  
   (This matches the server in `../server`; the HTTP mount path is `/mcp`.)
3. If your server requires a token, add a header:  
   - **Header name**: `Authorization`  
   - **Header value**: `Bearer <YOUR_LOCAL_MCP_TOKEN>`
4. Click **Connect**.

### What you should see

- A server info panel (protocol version, capabilities).
- Tabs for **Tools**, **Resources**, and **Prompts**.
- For this demo’s SQLite server (added in the next step of the repo):
  - **Tools** (examples): `list_tables`, `run_sql`, `top_customers`
  - **Resources** (examples): `schema://current`
  - **Prompts** (example): `explain_query_purpose`

> If nothing appears, check the **URL**, **transport**, and **auth header**.

---

## Try some calls

Once connected:

- **Tools → `list_tables`** → **Run**  
  Expect a list like `Album`, `Artist`, `Customer`, `Invoice`, …
- **Tools → `top_customers`** → set `limit=5` → **Run**  
  Expect top 5 customers by total invoice amount.
- **Resources → `schema://current`** → **Open**  
  View the discovered schema for quick orientation.
- **Prompts → `explain_query_purpose`** → input a SQL string → **Run**  
  Get a natural-language explanation of the query.

> Write operations are demonstrated in the **server** guide (e.g., insert/update via `run_sql`), not from Inspector by default.

---

## Connect to your **ngrok** URL (optional now; used later with the Agent)

If you’ve run `ngrok http 8787`, take the **HTTPS** URL it prints (for example, `https://abcd-1234.ngrok.app`).

In the Inspector UI, create a new connection:

- **Transport**: `Streamable HTTP`
- **Server URL**: `https://<your-subdomain>.ngrok.app/mcp`
- Add `Authorization: Bearer <YOUR_LOCAL_MCP_TOKEN>` if the server enforces it.
- **Connect** and repeat the calls above.

> Keep the Inspector bound to **localhost**; do **not** tunnel the Inspector itself.

---

## Common issues

- **Wrong path / 404**  
  Ensure the server URL ends with `/mcp` (e.g., `http://localhost:8787/mcp`).
- **Auth errors (401/403)**  
  Add `Authorization: Bearer <token>` exactly. Verify the token value matches the server’s expected secret.
- **No tools/resources/prompts shown**  
  The server may have failed to initialize or the transport is wrong. Confirm the server’s logs and that you selected **Streamable HTTP**.
- **ngrok 502/connection failed**  
  Check that your local server is running on the port you exposed, and that you used the **HTTPS** ngrok URL.
  
---

## Clean up

- Close the Inspector UI tab and stop the CLI process in your terminal.

---

## Next steps

- **Server**: head to `../server/README.md` to run the SQLite Chinook MCP server (read **and** write).
- **Agent**: later, you’ll point an Azure AI Agent at your **ngrok** URL to use these tools programmatically.
