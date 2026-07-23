"""Phase 1 - Build the toolbox (v1 = Web Search).

Creates the toolbox with a single tool. The first version of a new toolbox is
automatically promoted to default_version, so the consumer endpoint serves it
right away.
"""

from azure.ai.projects.models import WebSearchToolboxTool

from common import TOOLBOX_NAME, project


def main():
    version = project.toolboxes.create_version(
        name=TOOLBOX_NAME,
        description="Lab 1 v1: web search only",
        tools=[WebSearchToolboxTool(description="Search the public web for current information.")],
    )
    print(f"Created {version.name} version {version.version}: {[t.type for t in version.tools]}")

    toolbox = project.toolboxes.get(TOOLBOX_NAME)
    print(f"default_version = {toolbox.default_version}  (first version auto-promoted)")


if __name__ == "__main__":
    main()
