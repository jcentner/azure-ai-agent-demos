"""Structural and unit tests for mcp_mslearn_agent demo.

These tests validate code structure, imports, configuration, and MCPTool
handling WITHOUT making live Azure calls. Written from the spec (ADRs, README,
phase plan) before seeing the implementation.

Run: pytest mcp_mslearn_agent/tests/test_agent_config.py -v
"""

import ast
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEMO_DIR = pathlib.Path(__file__).resolve().parent.parent  # mcp_mslearn_agent/
REQUIRED_FILES = [
    "create_agent.py",
    "ask_agent.py",
    "README.md",
    "requirements.txt",
    ".env.sample",
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


# ===================================================================
# 1. Structural checks — files exist, .env.sample has required vars
# ===================================================================
class TestFileStructure:
    """ADR-004: flat demo directory layout."""

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_required_file_exists(self, filename: str) -> None:
        path = DEMO_DIR / filename
        assert path.exists(), f"Missing required file: {filename}"

    def test_env_sample_contains_required_vars(self) -> None:
        env_sample = (DEMO_DIR / ".env.sample").read_text()
        for var in REQUIRED_ENV_VARS:
            assert var in env_sample, (
                f".env.sample missing required variable: {var}"
            )

    def test_env_sample_has_agent_name_var(self) -> None:
        """AGENT_NAME should be present as an optional/default config."""
        env_sample = (DEMO_DIR / ".env.sample").read_text()
        assert "AGENT_NAME" in env_sample

    def test_env_sample_does_not_require_mcp_connection(self) -> None:
        """Public MCP server — no MCP_CONNECTION_NAME needed."""
        env_sample = (DEMO_DIR / ".env.sample").read_text()
        assert "MCP_CONNECTION_NAME" not in env_sample

    def test_requirements_has_v2_sdk(self) -> None:
        """ADR-003: GA V2 SDK — azure-ai-projects>=2.0.0."""
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "azure-ai-projects" in reqs
        assert ">=2.0.0" in reqs or ">2" in reqs, (
            "requirements.txt should pin azure-ai-projects to >=2.0.0 (GA v2)"
        )

    def test_requirements_has_azure_identity(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "azure-identity" in reqs

    def test_requirements_has_openai(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "openai" in reqs

    def test_requirements_has_python_dotenv(self) -> None:
        reqs = (DEMO_DIR / "requirements.txt").read_text()
        assert "python-dotenv" in reqs or "dotenv" in reqs


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
        """MCP-only demo — CodeInterpreterTool is enterprise-agent-specific."""
        assert "CodeInterpreterTool" not in _imported_names(tree)

    def test_references_require_approval_never(self, source: str) -> None:
        """Public read-only MCP server — auto-approve all calls."""
        assert "never" in source

    def test_does_not_reference_project_connection_id(self, source: str) -> None:
        """Public MCP server — no project connection needed."""
        assert "project_connection_id" not in source

    def test_references_agent_name_file(self, source: str) -> None:
        """ADR-001: agent name persisted to .agent_name file."""
        assert ".agent_name" in source

    def test_references_create_version(self, source: str) -> None:
        """ADR-003: V2 agent creation via project.agents.create_version."""
        assert "create_version" in source

    def test_references_mcp_tool(self, source: str) -> None:
        assert "MCPTool" in source

    def test_references_server_url(self, source: str) -> None:
        """Public MCP server uses server_url, not project_connection_id."""
        assert "server_url" in source


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

    def test_does_not_import_mcp_approval_response(self, tree: ast.Module) -> None:
        """No approval flow — require_approval='never' at creation time."""
        assert "McpApprovalResponse" not in _imported_names(tree)

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


# ===================================================================
# 5. Agent configuration objects — validate with real SDK classes
# ===================================================================
class TestAgentConfigurationObjects:
    """Instantiate the SDK config objects the demo spec requires."""

    def test_mcp_tool_with_require_approval_never(self) -> None:
        """Public read-only endpoint — require_approval='never'."""
        from azure.ai.projects.models import MCPTool

        tool = MCPTool(
            server_label="learn",
            server_url="https://learn.microsoft.com/api/mcp",
            require_approval="never",
        )
        assert tool.server_label == "learn"
        assert tool.require_approval == "never"

    def test_mcp_tool_does_not_need_project_connection_id(self) -> None:
        """Public endpoint — server_url only, no project_connection_id."""
        from azure.ai.projects.models import MCPTool

        tool = MCPTool(
            server_label="learn",
            server_url="https://learn.microsoft.com/api/mcp",
            require_approval="never",
        )
        # project_connection_id should be unset / None
        conn_id = getattr(tool, "project_connection_id", None)
        assert conn_id is None

    def test_prompt_agent_definition_accepts_mcp_tool(self) -> None:
        from azure.ai.projects.models import MCPTool, PromptAgentDefinition

        mcp = MCPTool(
            server_label="learn",
            server_url="https://learn.microsoft.com/api/mcp",
            require_approval="never",
        )
        definition = PromptAgentDefinition(
            model="gpt-4.1",
            instructions="You are a documentation assistant.",
            tools=[mcp],
        )
        assert definition.model == "gpt-4.1"
        assert len(definition.tools) == 1


# ===================================================================
# 6. Syntax validity — both scripts compile cleanly
# ===================================================================
class TestSyntaxValidity:
    """Ensure both scripts parse without syntax errors."""

    @pytest.mark.parametrize("script", ["create_agent.py", "ask_agent.py"])
    def test_script_compiles(self, script: str) -> None:
        source = (DEMO_DIR / script).read_text()
        compile(source, script, "exec")
