"""Check the local workstation setup before running an L200 tools lab."""

import argparse
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
MINIMUM_PYTHON = (3, 11)

PACKAGES = {
    "azure-ai-projects": "2.3.0",
    "azure-identity": "1.25.3",
    "azure-search-documents": "12.0.0",
    "python-dotenv": "1.2.2",
    "requests": "2.34.2",
}

LAB_VARIABLES = {
    "1": ("PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME"),
    "2": ("PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME", "SEARCH_CONNECTION_NAME"),
    "3": (
        "PROJECT_ENDPOINT",
        "MODEL_DEPLOYMENT_NAME",
        "SEARCH_CONNECTION_NAME",
        "PROJECT_RESOURCE_ID",
        "AOAI_ENDPOINT",
    ),
}


def _read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _pass(message: str) -> None:
    print(f"[PASS] {message}")


def _fail(message: str) -> None:
    print(f"[FAIL] {message}")


def check_python() -> bool:
    current = sys.version_info[:2]
    if current < MINIMUM_PYTHON:
        _fail(
            f"Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} or later is required; "
            f"found {current[0]}.{current[1]}."
        )
        return False
    _pass(f"Python {sys.version.split()[0]}")
    return True


def check_virtual_environment() -> bool:
    if sys.prefix == sys.base_prefix:
        _fail("No virtual environment is active. Activate .venv and run this check again.")
        return False
    _pass(f"Virtual environment: {sys.prefix}")
    return True


def check_packages() -> bool:
    ok = True
    for package, expected in PACKAGES.items():
        try:
            installed = metadata.version(package)
        except metadata.PackageNotFoundError:
            _fail(f"{package} is not installed.")
            ok = False
            continue

        if installed != expected:
            _fail(f"{package} {installed} is installed; expected {expected}.")
            ok = False
        else:
            _pass(f"{package} {installed}")
    return ok


def check_azure_cli() -> bool:
    executable = shutil.which("az")
    if not executable:
        _fail("Azure CLI was not found on PATH.")
        return False

    result = subprocess.run(
        [executable, "account", "show", "--output", "none"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        _fail("Azure CLI is installed, but no active login was found. Run: az login")
        return False

    _pass("Azure CLI login")
    return True


def check_configuration(lab: str) -> bool:
    if not ENV_FILE.exists():
        _fail(f"{ENV_FILE} does not exist. Copy .env.sample to .env and fill in the values.")
        return False

    values = _read_env()
    required = LAB_VARIABLES[lab] if lab != "all" else tuple(
        dict.fromkeys(variable for variables in LAB_VARIABLES.values() for variable in variables)
    )
    missing = [variable for variable in required if not values.get(variable)]
    if missing:
        _fail(f"Missing values in .env: {', '.join(missing)}")
        return False

    endpoint = values.get("PROJECT_ENDPOINT", "")
    if not endpoint.startswith("https://") or "/api/projects/" not in endpoint:
        _fail("PROJECT_ENDPOINT does not match the Foundry project endpoint format.")
        return False

    _pass(f"Configuration for Lab {lab}" if lab != "all" else "Configuration for all labs")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lab",
        choices=("1", "2", "3", "all"),
        default="all",
        help="Check only the environment variables needed by one lab.",
    )
    args = parser.parse_args()

    checks = [
        check_python(),
        check_virtual_environment(),
        check_packages(),
        check_azure_cli(),
        check_configuration(args.lab),
    ]
    if all(checks):
        print("\nSetup is ready.")
        return 0

    print("\nSetup is not ready. Fix the failed items and run this command again.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
