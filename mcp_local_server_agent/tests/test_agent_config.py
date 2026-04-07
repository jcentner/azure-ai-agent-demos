"""Structural and unit tests for mcp_local_server_agent demo.

These tests validate code structure, imports, configuration, server logic,
and MCP approval handling WITHOUT making live Azure or server calls.
Written from the spec before seeing the implementation.

Run: pytest mcp_local_server_agent/tests/test_agent_config.py -v
"""

import ast
import pathlib
import sys

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEMO_DIR = pathlib.Path(__file__).resolve().parent.parent  # mcp_local_server_agent/
REQUIRED_FILES = [
    "create_agent.py",
    "ask_agent.py",
    "README.md",
    "requirements.txt",
    ".env.sample",
]
REQUIRED_SERVER_FILES = [
    "server/__init__.py",
    "server/app.py",
    "server/config.py",
    "server/auth.py",
    "server/db/__init__.py",
    "server/db/client.py",
    "server/db/init.py",
    "server/db/chinook.db",
    "server/surface/__init__.py",
    "server/surface/tools.py",
    "server/surface/schema.py",
    "server/surface/prompt.py",
]
REQUIRED_ENV_VARS = [
    "PROJECT_ENDPOINT",
    "MODEL_DEPLOYMENT_NAME",
]


# ===================================================================
# Helpers
# ===================================================================
def _imported_names(tree: ast.Module) -> set[str]:
    """Collect all imported names (or their aliases) from an AST."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.name if alias.asname is None else alias.asname)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name if alias.asname is None else alias.asname)
    return names


# Ensure the demo dir is on sys.path so server imports work
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))


# ===================================================================
# 1. Structural checks — files exist, .env.sample, requirements.txt
# ===================================================================
class TestFileStructure:
    """Required files exist including server/ subdirectory tree."""

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_required_file_exists(self, filename: str) -> None:
        path = DEMO_DIR / filename
        assert path.exists(), f"Missing required file: {filename}"

    @pytest.mark.parametrize("filename", REQUIRED_SERVER_FILES)
    def test_required_server_file_exists(self, filename: str) -> None:
        path = DEMO_DIR / filename
        assert path.exists(), f"Missing required server file: {filename}"

    def test_chinook_db_is_non_empty(self) -> None:
        db = DEMO_DIR / "server" / "db" / "chinook.db"
        assert db.stat().st_size > 0, "chinook.db should be a non-empty SQLite file"

    def test_env_sample_contains_required_vars(self) -> None:
        env_sample = (DEMO_DIR / ".env.sample").read_text()
        for var in REQUIRED_ENV_VARS:
            assert var in env_sample, (
                f".env.sample missing required variable: {var}"
            )

    def test_env_sample_has_agent_name_var(self) -> None:
        env_sample = (DEMO_DIR / ".env.sample").read_text()
        assert "AGENT_NAME" in env_sample

    def test_env_sample_has_mcp_connection_name_optional(self) -> None:
        """MCP_CONNECTION_NAME should be present but optional (commented out)."""
        env_sample = (DEMO_DIR / ".env.sample").read_text()
        assert "MCP_CONNECTION_NAME" in env_sample

    def test_requirements_has_v2_sdk(self) -> None:
        """ADR-003: GA V2 SDK — azure-ai-projects>=2.0.0."""
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "azure-ai-projects" in reqs
        assert ">=2.0.0" in reqs or ">2" in reqs

    def test_requirements_has_azure_identity(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "azure-identity" in reqs

    def test_requirements_has_openai(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "openai" in reqs

    def test_requirements_has_python_dotenv(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "python-dotenv" in reqs or "dotenv" in reqs

    def test_requirements_has_mcp_cli(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "mcp[cli]" in reqs or "mcp" in reqs

    def test_requirements_has_starlette(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "starlette" in reqs

    def test_requirements_has_uvicorn(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "uvicorn" in reqs


# ===================================================================
# 2. Import resolution — all SDK symbols importable
# ===================================================================
class TestImportsResolve:
    """Verify the SDK packages install the symbols the demo depends on."""

    def test_ai_project_client_importable(self) -> None:
        from azure.ai.projects import AIProjectClient  # noqa: F401

    def test_default_azure_credential_importable(self) -> None:
        from azure.identity import DefaultAzureCredential  # noqa: F401

    def test_prompt_agent_definition_importable(self) -> None:
        from azure.ai.projects.models import PromptAgentDefinition  # noqa: F401

    def test_mcp_tool_importable(self) -> None:
        from azure.ai.projects.models import MCPTool  # noqa: F401

    def test_mcp_approval_response_importable(self) -> None:
        from openai.types.responses.response_input_param import (
            McpApprovalResponse,
        )  # noqa: F401

    def test_openai_client_importable(self) -> None:
        import openai  # noqa: F401

    def test_dotenv_importable(self) -> None:
        import dotenv  # noqa: F401


# ===================================================================
# 3. create_agent.py — AST-level validation
# ===================================================================
class TestCreateAgentStructure:
    """Validate create_agent.py structure via AST parsing (no execution)."""

    @pytest.fixture()
    def source(self) -> str:
        return (DEMO_DIR / "create_agent.py").read_text()

    @pytest.fixture()
    def tree(self, source: str) -> ast.Module:
        return ast.parse(source, filename="create_agent.py")

    def test_imports_ai_project_client(self, tree: ast.Module) -> None:
        assert "AIProjectClient" in _imported_names(tree)

    def test_imports_default_azure_credential(self, tree: ast.Module) -> None:
        assert "DefaultAzureCredential" in _imported_names(tree)

    def test_imports_prompt_agent_definition(self, tree: ast.Module) -> None:
        assert "PromptAgentDefinition" in _imported_names(tree)

    def test_imports_mcp_tool(self, tree: ast.Module) -> None:
        assert "MCPTool" in _imported_names(tree)

    def test_does_not_import_code_interpreter_tool(self, tree: ast.Module) -> None:
        """MCP-only demo — no CodeInterpreterTool."""
        assert "CodeInterpreterTool" not in _imported_names(tree)

    def test_references_require_approval_always(self, source: str) -> None:
        """Server does writes — require_approval='always'."""
        assert "always" in source

    def test_references_project_connection_id(self, source: str) -> None:
        """Optional auth via project connection — code references it even if conditional."""
        assert "project_connection_id" in source

    def test_references_agent_name_file(self, source: str) -> None:
        """ADR-001: agent name persisted to .agent_name file."""
        assert ".agent_name" in source

    def test_references_create_version(self, source: str) -> None:
        """ADR-003: V2 agent creation via project.agents.create_version."""
        assert "create_version" in source

    def test_references_mcp_tool(self, source: str) -> None:
        assert "MCPTool" in source


# ===================================================================
# 4. ask_agent.py — AST-level validation
# ===================================================================
class TestAskAgentStructure:
    """Validate ask_agent.py structure via AST parsing (no execution)."""

    @pytest.fixture()
    def source(self) -> str:
        return (DEMO_DIR / "ask_agent.py").read_text()

    @pytest.fixture()
    def tree(self, source: str) -> ast.Module:
        return ast.parse(source, filename="ask_agent.py")

    def test_imports_ai_project_client(self, tree: ast.Module) -> None:
        assert "AIProjectClient" in _imported_names(tree)

    def test_imports_mcp_approval_response(self, tree: ast.Module) -> None:
        """Approval flow required — server does writes."""
        assert "McpApprovalResponse" in _imported_names(tree)

    def test_references_agent_reference_extra_body(self, source: str) -> None:
        """ADR-003: agent_reference in extra_body for Responses API."""
        assert "agent_reference" in source

    def test_references_previous_response_id(self, source: str) -> None:
        """Conversation continuity via response chaining."""
        assert "previous_response_id" in source

    def test_references_stream(self, source: str) -> None:
        assert "stream" in source

    def test_references_agent_name_file(self, source: str) -> None:
        """ADR-001: reads agent name from .agent_name file."""
        assert ".agent_name" in source

    def test_references_responses_create(self, source: str) -> None:
        """ADR-003: uses openai.responses.create for conversation."""
        assert "responses.create" in source

    def test_references_get_mcp_approval_requests(self, source: str) -> None:
        """Has the MCP approval helper function."""
        assert "get_mcp_approval_requests" in source


# ===================================================================
# 5. Server code — unit tests (no live calls)
# ===================================================================
class TestServerCode:
    """Test actual server module logic without starting a server."""

    # --- db/client.py: is_select ---

    def test_is_select_simple(self) -> None:
        from server.db.client import is_select

        assert is_select("SELECT * FROM albums") is True

    def test_is_select_case_insensitive(self) -> None:
        from server.db.client import is_select

        assert is_select("select name from artists") is True

    def test_is_select_with_leading_whitespace(self) -> None:
        from server.db.client import is_select

        assert is_select("  SELECT 1") is True

    def test_is_select_rejects_insert(self) -> None:
        from server.db.client import is_select

        assert is_select("INSERT INTO albums VALUES (1, 'x', 1)") is False

    def test_is_select_rejects_multi_statement(self) -> None:
        from server.db.client import is_select

        assert is_select("SELECT 1; DROP TABLE albums") is False

    def test_is_select_empty_string(self) -> None:
        from server.db.client import is_select

        assert is_select("") is False

    def test_is_select_none(self) -> None:
        from server.db.client import is_select

        assert is_select(None) is False

    # --- db/client.py: is_write ---

    def test_is_write_insert(self) -> None:
        from server.db.client import is_write

        assert is_write("INSERT INTO albums VALUES (999, 'Test', 1)") is True

    def test_is_write_update(self) -> None:
        from server.db.client import is_write

        assert is_write("UPDATE albums SET title='X' WHERE albumid=1") is True

    def test_is_write_delete(self) -> None:
        from server.db.client import is_write

        assert is_write("DELETE FROM albums WHERE albumid=999") is True

    def test_is_write_rejects_select(self) -> None:
        from server.db.client import is_write

        assert is_write("SELECT * FROM albums") is False

    def test_is_write_rejects_multi_statement(self) -> None:
        from server.db.client import is_write

        assert is_write("INSERT INTO albums VALUES (1, 'x', 1); DROP TABLE albums") is False

    def test_is_write_case_insensitive(self) -> None:
        from server.db.client import is_write

        assert is_write("  UPDATE albums SET title='Y'") is True

    # --- db/client.py: Database dataclass ---

    def test_database_dataclass_instantiates(self) -> None:
        from server.db.client import Database

        db = Database(path=pathlib.Path("/tmp/test.db"))
        assert db.path == pathlib.Path("/tmp/test.db")

    # --- surface/prompt.py: _render_explanation ---

    def test_render_explanation_select(self) -> None:
        from server.surface.prompt import _render_explanation

        result = _render_explanation("SELECT * FROM albums")
        assert "SELECT" in result
        assert "read" in result.lower() or "without modifying" in result.lower()

    def test_render_explanation_insert(self) -> None:
        from server.surface.prompt import _render_explanation

        result = _render_explanation("INSERT INTO albums VALUES (1, 'x', 1)")
        assert "WRITE" in result or "modif" in result.lower()

    def test_render_explanation_empty(self) -> None:
        from server.surface.prompt import _render_explanation

        result = _render_explanation("")
        assert "Empty" in result

    def test_render_explanation_none(self) -> None:
        from server.surface.prompt import _render_explanation

        result = _render_explanation(None)
        assert "Empty" in result

    # --- auth.py: extract_bearer_token ---

    def test_extract_bearer_token_valid(self) -> None:
        from server.auth import extract_bearer_token

        assert extract_bearer_token("Bearer abc123") == "abc123"

    def test_extract_bearer_token_empty_string(self) -> None:
        from server.auth import extract_bearer_token

        assert extract_bearer_token("") is None

    def test_extract_bearer_token_none(self) -> None:
        from server.auth import extract_bearer_token

        assert extract_bearer_token(None) is None

    def test_extract_bearer_token_wrong_scheme(self) -> None:
        from server.auth import extract_bearer_token

        assert extract_bearer_token("Basic abc123") is None

    def test_extract_bearer_token_bearer_no_space(self) -> None:
        from server.auth import extract_bearer_token

        assert extract_bearer_token("Bearerabc") is None

    # --- config.py: Config dataclass ---

    def test_config_dataclass_instantiates(self) -> None:
        from server.config import Config

        cfg = Config(
            PORT=8787,
            MCP_PATH="/mcp",
            DB_BASE_PATH=DEMO_DIR / "server" / "db" / "chinook.db",
            DB_WORKING_DIR=DEMO_DIR / "server" / "db" / "working",
            PERSIST_WORKING_COPY=False,
            LOCAL_MCP_TOKEN=None,
            LOG_LEVEL="info",
        )
        assert cfg.PORT == 8787
        assert cfg.MCP_PATH == "/mcp"
        assert cfg.LOCAL_MCP_TOKEN is None

    def test_config_validate_rejects_bad_mcp_path(self) -> None:
        from server.config import Config

        cfg = Config(
            PORT=8787,
            MCP_PATH="no-slash",
            DB_BASE_PATH=DEMO_DIR / "server" / "db" / "chinook.db",
            DB_WORKING_DIR=DEMO_DIR / "server" / "db" / "working",
            PERSIST_WORKING_COPY=False,
            LOCAL_MCP_TOKEN=None,
            LOG_LEVEL="info",
        )
        with pytest.raises(ValueError, match="MCP_PATH"):
            cfg.validate()


# ===================================================================
# 6. Agent configuration objects — validate with real SDK classes
# ===================================================================
class TestAgentConfigurationObjects:
    """Instantiate the SDK config objects the demo spec requires."""

    def test_mcp_tool_with_require_approval_always(self) -> None:
        """Chinook server does writes — require_approval='always'."""
        from azure.ai.projects.models import MCPTool

        tool = MCPTool(
            server_label="chinook",
            server_url="https://example.ngrok.app/mcp",
            require_approval="always",
        )
        assert tool.server_label == "chinook"
        assert tool.require_approval == "always"

    def test_mcp_tool_accepts_optional_project_connection_id(self) -> None:
        """Optional auth via project connection."""
        from azure.ai.projects.models import MCPTool

        tool = MCPTool(
            server_label="chinook",
            server_url="https://example.ngrok.app/mcp",
            require_approval="always",
            project_connection_id="test-connection",
        )
        assert tool.project_connection_id == "test-connection"

    def test_mcp_tool_without_project_connection_id(self) -> None:
        """No auth — project_connection_id not set."""
        from azure.ai.projects.models import MCPTool

        tool = MCPTool(
            server_label="chinook",
            server_url="https://example.ngrok.app/mcp",
            require_approval="always",
        )
        conn_id = getattr(tool, "project_connection_id", None)
        assert conn_id is None

    def test_prompt_agent_definition_accepts_mcp_only_tools(self) -> None:
        """MCP-only demo — no CodeInterpreterTool in tool list."""
        from azure.ai.projects.models import MCPTool, PromptAgentDefinition

        mcp = MCPTool(
            server_label="chinook",
            server_url="https://example.ngrok.app/mcp",
            require_approval="always",
        )
        definition = PromptAgentDefinition(
            model="gpt-4.1",
            instructions="You are a database assistant.",
            tools=[mcp],
        )
        assert definition.model == "gpt-4.1"
        assert len(definition.tools) == 1


# ===================================================================
# 7. Syntax validity — both scripts compile cleanly
# ===================================================================
class TestSyntaxValidity:
    """Ensure both agent scripts parse without syntax errors."""

    @pytest.mark.parametrize("script", ["create_agent.py", "ask_agent.py"])
    def test_script_compiles(self, script: str) -> None:
        source = (DEMO_DIR / script).read_text()
        compile(source, script, "exec")
