from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CHECKER_VERSION = "canonical-public-package-checker-v0.4.2"
SPEC_SCHEMA_VERSION = "maxwell-demo-spec-v0.3.2"

REQUIRED_FILES = {
    ".github/workflows/ci.yml",
    "README.md",
    "REVIEWER_START_HERE.md",
    "DEMO_BUILD_BRIEF.md",
    "DEMO_SPEC.yml",
    "LICENSE",
    "LICENSE-NOTICE.md",
    "SECURITY.md",
    "NOTICE.md",
    "VERSION",
    "THREAT_MODEL.md",
    "Makefile",
    "pyproject.toml",
    "docs/CLAIMS_AND_LIMITATIONS.md",
    "docs/POLICY_REASON_CODES.md",
    "docs/ADVERSARIAL_REVIEW_NOTES.md",
    "docs/RED_TEAM_NOTES.md",
    "docs/ADVERSARIAL_TEST_REPORT.md",
    "docs/RED_TEAM_RULES_OF_ENGAGEMENT.md",
    "docs/ADVERSARIAL_HARNESS_REPORT.md",
    "examples/adversarial_inputs/README.md",
    "artifacts/README.md",
    "tools/create_clean_zip.py",
    "tools/public_package_check.py",
    "tools/public_release_boundary.json",
}

REQUIRED_DIRS = {
    ".github/workflows",
    "src",
    "policies",
    "examples",
    "examples/adversarial_inputs",
    "docs",
    "tests",
    "tests/adversarial",
    "tools",
    "artifacts",
}

REQUIRED_CI_COMMANDS = {
    "make demo",
    "make verify",
    "make test",
    "make adversarial",
    "make package-check",
}

REQUIRED_SPEC_KEYS = {
    "schema_version",
    "suite_index",
    "suite_name",
    "demo_name",
    "package_name",
    "version",
    "python_package",
    "threat_class",
    "headline",
    "cold_open",
    "core_invariant",
    "consequence_boundary",
    "primary_effect_artifact",
    "primary_no_effect_marker",
    "what_this_stresses",
    "audience",
    "standard_commands",
    "cases",
    "public_boundaries",
}

FORBIDDEN_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "env",
    ".env",
    ".env.local",
    ".DS_Store",
    "__MACOSX",
    "node_modules",
    "htmlcov",
    "dist",
    "build",
}
FORBIDDEN_FILE_NAMES = {".coverage", "coverage.xml"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".log"}

DEFAULT_DENYLIST_TERMS = {
    "MEVIDA",
    "Golden Tree",
    "Golden Tree internal",
    "MEVIDA kernel",
    "Golden Tree kernel",
    "production MEVIDA",
    "private evaluator chain",
    "private evaluator chains",
    "authority doctrine",
    "production trust root",
    "production trust roots",
    "non-public control grammar",
    "internal consequence doctrine",
    "MAXWELL_INTERNAL_ONLY",
    "DO_NOT_PUBLISH",
    "FOR INTERNAL USE ONLY",
}

DEFAULT_ALLOWED_PATHS = {
    "NOTICE.md",
    "DEMO_BUILD_BRIEF.md",
    "LICENSE",
    "LICENSE-NOTICE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "RELEASE_NOTES.md",
    "docs/PUBLIC_PREVIEW_BOUNDARIES.md",
    "docs/CLAIMS_AND_LIMITATIONS.md",
    "docs/ADVERSARIAL_REVIEW_GUIDE.md",
    "tools/public_package_check.py",
    "tools/public_release_boundary.json",
}

DEFAULT_INTENTIONAL_PRIVATE_KEYS = {
    "fixtures/manifest_demo_private_key.pem",
    "fixtures/oidc_demo_issuer_private_key.pem",
}

TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".lock",
    ".md",
    ".pem",
    ".pub",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {"Makefile", "LICENSE", "NOTICE", "VERSION"}
SELF_EXEMPT_FILES = {"tools/public_package_check.py"}

SECRET_PREFILTERS = [
    ("AWS access key id", "AKIA", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("AWS secret access key", "aws_secret_access_key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{30,}")),
    ("Google API key", "AIza", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("GitHub token", "gh", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("GitHub fine-grained token", "github_pat_", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{80,}\b")),
    ("Slack token", "xox", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "credential assignment",
        "",  # no prefilter because either ':' or '=' can be used
        re.compile(
            r"(?i)\b(api[_-]?key|secret|password|passwd|access[_-]?token|refresh[_-]?token|client[_-]?secret)\b"
            r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=\-]{20,}"
        ),
    ),
]
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_config(root: Path) -> dict:
    path = root / "tools" / "public_release_boundary.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("tools/public_release_boundary.json must contain a JSON object")
    return data


def set_from_config(config: dict, key: str, default: set[str]) -> set[str]:
    value = config.get(key)
    if value is None:
        return set(default)
    if not isinstance(value, list):
        return set(default)
    return {str(item).strip() for item in value if str(item).strip()}


def is_textual(path: Path) -> bool:
    return path.name in TEXT_NAMES or path.suffix.lower() in TEXT_SUFFIXES


def line_no(text: str, needle: str) -> int:
    idx = text.lower().find(needle.lower())
    if idx < 0:
        return 1
    return text.count("\n", 0, idx) + 1


def generated_artifact_outside_samples(rel: Path) -> bool:
    parts = rel.parts
    if len(parts) < 2 or parts[0] != "artifacts":
        return False
    if len(parts) >= 3 and parts[1] == "sample_outputs":
        return False
    if parts == ("artifacts", "README.md"):
        return False
    return True


def simple_glob_match(path: str, pattern: str) -> bool:
    if pattern == path:
        return True
    if "*" not in pattern:
        return False
    regex = "^" + re.escape(pattern).replace("\\*", ".*") + "$"
    return re.match(regex, path) is not None


def yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    if not match:
        return None
    value = match.group(1).strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value.strip()


def validate_demo_spec(root: Path, failures: list[str]) -> None:
    spec_path = root / "DEMO_SPEC.yml"
    if not spec_path.exists():
        failures.append("Missing DEMO_SPEC.yml")
        return
    text = read_text(spec_path)
    present = set(re.findall(r"(?m)^([A-Za-z_][A-Za-z0-9_]*):", text))
    missing = sorted(REQUIRED_SPEC_KEYS - present)
    if missing:
        failures.append(f"DEMO_SPEC.yml missing required v0.3.2 keys: {', '.join(missing)}")
        return

    schema_version = yaml_scalar(text, "schema_version")
    if schema_version != SPEC_SCHEMA_VERSION:
        failures.append(f"DEMO_SPEC.yml schema_version must be {SPEC_SCHEMA_VERSION!r}; found {schema_version!r}")

    suite_index = yaml_scalar(text, "suite_index") or ""
    if not re.fullmatch(r"(?:0[1-9]|10)", suite_index):
        failures.append(f"DEMO_SPEC.yml suite_index must be a zero-padded string 01-10; found {suite_index!r}")

    suite_name = yaml_scalar(text, "suite_name")
    if suite_name != "Maxwell Consequence Boundary Demo Suite":
        failures.append("DEMO_SPEC.yml suite_name must be 'Maxwell Consequence Boundary Demo Suite'")

    for key in [
        "demo_name",
        "package_name",
        "version",
        "python_package",
        "threat_class",
        "headline",
        "cold_open",
        "core_invariant",
        "consequence_boundary",
        "primary_effect_artifact",
        "primary_no_effect_marker",
        "what_this_stresses",
    ]:
        value = yaml_scalar(text, key)
        if not value or value.lower().startswith(("todo", "tbd", "placeholder")):
            failures.append(f"DEMO_SPEC.yml field {key!r} must be populated with non-placeholder text")

    effect = yaml_scalar(text, "primary_effect_artifact") or ""
    if effect and not (effect.endswith(".json") or effect.startswith("absence of")):
        failures.append("DEMO_SPEC.yml primary_effect_artifact should name a JSON effect artifact")

    case_count = len(re.findall(r"(?m)^\s*-\s+id:\s*", text))
    if case_count < 5:
        failures.append(f"DEMO_SPEC.yml should list at least five threat cases; found {case_count}")

    readme_path = root / "README.md"
    if readme_path.exists() and suite_index:
        readme = read_text(readme_path)
        required_fragments = [
            f"Demo {suite_index} of 10",
            "Threat class:",
            "Money-shot command",
            "Shared suite invariant",
            "Threat matrix",
        ]
        for fragment in required_fragments:
            if fragment not in readme:
                failures.append(f"README.md missing narrative/spec fragment: {fragment}")
        for link in ["https://www.maxwellevidence.com/", "https://www.youtube.com/@MaxwellEvidence"]:
            if link not in readme:
                failures.append(f"README.md missing public Maxwell Evidence link: {link}")

    if suite_index == "02":
        flagship_required = [
            "docs/MUTATION_AND_FUZZING.md",
            "tools/gate_mutation_smoke.py",
            "tests/fuzz/test_fail_closed_input_space.py",
        ]
        for rel in flagship_required:
            if not (root / rel).exists():
                failures.append(f"Flagship Demo 02 missing v0.3.4 mutation/fuzz asset: {rel}")

        makefile_path = root / "Makefile"
        if makefile_path.exists():
            make_text = read_text(makefile_path)
            for target in ["fuzz-quick", "mutation-smoke"]:
                if target not in make_text:
                    failures.append(f"Flagship Demo 02 Makefile missing v0.3.4 target: {target}")

        workflow_dir = root / ".github" / "workflows"
        workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml")) if workflow_dir.exists() else []
        workflow_text = "\n".join(read_text(p) for p in workflow_files)
        for command in ["make fuzz-quick", "make mutation-smoke"]:
            if command not in workflow_text:
                failures.append(f"Flagship Demo 02 CI workflow does not invoke v0.3.4 command: {command}")


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0] if argv else ".").resolve()
    failures: list[str] = []

    if not root.is_dir():
        print(f"Package hygiene check failed ({CHECKER_VERSION}):")
        print(f"- Root is not a directory: {root}")
        return 2

    try:
        config = load_config(root)
    except Exception as exc:
        print(f"Package hygiene check failed ({CHECKER_VERSION}):")
        print(f"- Invalid tools/public_release_boundary.json: {exc}")
        return 1

    denylist = set_from_config(config, "denylist_terms", DEFAULT_DENYLIST_TERMS)
    allowed_paths = set_from_config(config, "allowed_paths", DEFAULT_ALLOWED_PATHS)
    allowed_globs = set_from_config(config, "allowed_globs", set())
    intentional_private_keys = set_from_config(config, "intentional_public_private_keys", DEFAULT_INTENTIONAL_PRIVATE_KEYS)

    if len(denylist) < 8:
        failures.append("Public-boundary denylist is missing or too small; expected explicit internal-token guardrails")
    if "tools/public_release_boundary.json" not in allowed_paths:
        failures.append("tools/public_release_boundary.json must be allowlisted because it contains the denylist itself")

    for rel in sorted(REQUIRED_FILES):
        if not (root / rel).exists():
            failures.append(f"Missing required public package file: {rel}")
    for rel in sorted(REQUIRED_DIRS):
        if not (root / rel).exists():
            failures.append(f"Missing required public package directory: {rel}")

    validate_demo_spec(root, failures)

    makefile = root / "Makefile"
    if makefile.exists():
        make_text = read_text(makefile)
        if "package-check" not in make_text or "tools/public_package_check.py" not in make_text:
            failures.append("Makefile package-check target must call tools/public_package_check.py")
        if "adversarial:" not in make_text or "tests/adversarial" not in make_text:
            failures.append("Makefile must expose an adversarial target that runs tests/adversarial")
        if "adversarial:" not in make_text:
            failures.append("Makefile must include an adversarial target for the public adversarial corpus")

    workflow_dir = root / ".github" / "workflows"
    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml")) if workflow_dir.exists() else []
    if not workflow_files:
        failures.append("No GitHub Actions workflow YAML files found under .github/workflows")
    else:
        workflow_text = "\n".join(read_text(p) for p in workflow_files)
        for command in sorted(REQUIRED_CI_COMMANDS):
            if command not in workflow_text:
                failures.append(f"CI workflow does not invoke required command: {command}")

    found_intentional_private_keys: set[str] = set()
    denylist_lower = [(term, term.lower()) for term in sorted(denylist, key=str.lower)]

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        rel_text = rel.as_posix()
        if ".git" in rel.parts:
            continue
        if any(part in FORBIDDEN_NAMES for part in rel.parts):
            failures.append(f"Forbidden public-package file or directory: {rel_text}")
            continue
        if path.is_dir():
            if path.name.endswith(".egg-info"):
                failures.append(f"Forbidden package build metadata directory: {rel_text}")
            continue
        if path.name in FORBIDDEN_FILE_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"Forbidden generated/local-only file: {rel_text}")
            continue
        if generated_artifact_outside_samples(rel):
            failures.append(f"Generated run/replay artifact should not be packaged outside artifacts/sample_outputs: {rel_text}")
            continue
        if not is_textual(path):
            continue
        text = read_text(path)
        text_lower = text.lower()

        if rel_text not in SELF_EXEMPT_FILES:
            if "private key" in text_lower and PRIVATE_KEY_RE.search(text):
                if rel_text in intentional_private_keys:
                    found_intentional_private_keys.add(rel_text)
                else:
                    failures.append(f"Suspicious private key PEM content in: {rel_text}")

            for label, prefilter, pattern in SECRET_PREFILTERS:
                if prefilter and prefilter.lower() not in text_lower:
                    continue
                if pattern.search(text):
                    failures.append(f"Suspicious {label} content in: {rel_text}")

        if rel_text not in allowed_paths and not any(simple_glob_match(rel_text, pat) for pat in allowed_globs):
            for term, term_lower in denylist_lower:
                if term_lower in text_lower:
                    failures.append(
                        f"Public-boundary denylist term {term!r} appears outside approved boundary files: "
                        f"{rel_text}:{line_no(text, term)}"
                    )

    if found_intentional_private_keys:
        fixture_readme = root / "fixtures" / "README.md"
        if not fixture_readme.exists():
            failures.append("Missing fixtures/README.md for public demo fixture keys")
        else:
            warning = read_text(fixture_readme).lower()
            for phrase in ("intentionally public demo material", "not production"):
                if phrase not in warning:
                    failures.append(f"fixtures/README.md must state fixture keys are {phrase!r}")

    if failures:
        print(f"Package hygiene check failed ({CHECKER_VERSION}):")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Package hygiene check passed ({CHECKER_VERSION}).")
    print("Checks: required files/directories, CI commands, Makefile gate, DEMO_SPEC v0.3.2 schema, README narrative fragments, THREAT_MODEL and adversarial-corpus assets, Demo 02 mutation/fuzz assets where applicable, v0.4.0 adversarial harness report, v0.4.2 public links, junk/cache artifacts, secrets, demo private-key boundaries, generated artifacts, public-boundary denylist, red-team notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
