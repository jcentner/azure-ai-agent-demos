"""Phase 0 (optional) - Reset. Delete the lab toolbox so 01_build_v1 starts clean.

Run this before re-running the lab. create_version on an existing toolbox appends a
new version instead of starting over.
"""

from common import TOOLBOX_NAME, project


def main():
    try:
        project.toolboxes.delete(TOOLBOX_NAME)
        print(f"deleted toolbox {TOOLBOX_NAME}")
    except Exception as exc:  # toolbox may not exist yet
        print(f"nothing to delete ({str(exc)[:80]})")


if __name__ == "__main__":
    main()
