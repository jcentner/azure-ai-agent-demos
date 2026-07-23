"""Phase 3 - Build v2 (Web Search + Code Interpreter) but do NOT promote it.

Creating a new version does not change default_version. This sets up the break:
the consumer endpoint still serves v1, so agents still see only Web Search, while
the version-specific developer endpoint serves the full v2 tool set.

Toolbox rule: at most ONE unnamed tool per toolbox. v1's Web Search was unnamed, so
here Code Interpreter must be named or the create call fails with:
    invalid_payload "Multiple tools without identifiers found".
"""

from azure.ai.projects.models import (
    AutoCodeInterpreterToolParam,
    CodeInterpreterToolboxTool,
    WebSearchToolboxTool,
)

from common import TOOLBOX_NAME, developer_endpoint, project, tools_list


def main():
    version = project.toolboxes.create_version(
        name=TOOLBOX_NAME,
        description="Lab 1 v2: web search + code interpreter",
        tools=[
            WebSearchToolboxTool(description="Search the public web for current information."),
            CodeInterpreterToolboxTool(
                name="code_interpreter",
                description="Run Python to do calculations and data work.",
                container=AutoCodeInterpreterToolParam(),
            ),
        ],
    )
    print(f"Created version {version.version}: {[(t.type, getattr(t, 'name', None)) for t in version.tools]}")

    toolbox = project.toolboxes.get(TOOLBOX_NAME)
    print(f"default_version = {toolbox.default_version}  (still points at v1 - not promoted)")

    print(f"developer (v{version.version}) tools/list: {tools_list(developer_endpoint(version.version))}")


if __name__ == "__main__":
    main()
