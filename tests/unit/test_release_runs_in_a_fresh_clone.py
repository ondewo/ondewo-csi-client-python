# Copyright 2021-2026 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
The ``release`` target works in the fresh clone ondewo-csi-api's ``release_client`` makes, and tests first.

The fresh clone has no ``.venv`` and the release host has no conda environment for this repository, so every
tool the release runs must come from ``uv sync`` of ``uv.lock``. And nothing may be committed, published, pushed or
tagged before the preflight and the unit suite passed - the order every ondewo-csi-client-<lang> repository shares,
so ondewo-csi-api's driver can treat all of them alike.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import (
    Dict,
    List,
)

import pytest

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
MAKEFILE: str = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")


def _recipe(target: str) -> List[str]:
    """
    Return the recipe lines of a make target.

    Args:
        target (str):
            The target name.

    Returns:
        List[str]:
            Its tab-indented recipe lines, stripped.
    """
    match = re.search(rf"^{re.escape(target)}:.*\n((?:\t.*\n)+)", MAKEFILE, flags=re.MULTILINE)
    assert match is not None, target
    return [line.strip() for line in match.group(1).splitlines()]


def test_the_release_needs_no_conda() -> None:
    """Verify no recipe activates a conda environment on the release path."""
    assert "activate ondewo-csi-client-python" not in "\n".join(_recipe("release"))


def test_pre_commit_runs_in_a_synced_project_environment() -> None:
    """Verify pre-commit runs through ``uv run --no-sync`` after ``install_dev_environment`` synced the .venv."""
    assert re.search(r"^precommit_hooks_run_all_files:\s*install_dev_environment\b", MAKEFILE, re.MULTILINE)
    assert _recipe("precommit_hooks_run_all_files") == ["uv run --no-sync pre-commit run --all-files"]
    assert _recipe("install_dev_environment") == ["uv sync --extra dev --frozen --python 3.12"]


# The release contract, in order. Each entry is a substring of exactly one recipe line of `release`.
RELEASE_ORDER: List[str] = [
    "make release_preflight",
    "make build",
    "make precommit_hooks_run_all_files",
    "make check_build",
    "make test",
    "git commit --no-verify",
    "make push_to_pypi_via_docker",
    "make verify_pypi",
    "git push",
    "make create_release_branch",
    "make create_release_tag",
    "make release_to_github_via_docker",
    "make release_verify",
]


def _line_of(recipe: List[str], step: str) -> int:
    """
    Return the index of the one recipe line that runs ``step``.

    Args:
        recipe (List[str]):
            The recipe lines.
        step (str):
            A substring naming the step.

    Returns:
        int:
            Its index.
    """
    matches: List[int] = [
        index for index, line in enumerate(recipe) if re.search(rf"(?<![\w-]){re.escape(step)}\b", line)
    ]
    assert len(matches) == 1, f"{step!r} runs on {len(matches)} lines of `release`: {recipe}"
    return matches[0]


def test_the_release_runs_its_steps_in_the_contract_order() -> None:
    """Verify preflight, build, tests, commit, PyPI, PyPI check, push, branch, tag, GitHub release, verify."""
    recipe: List[str] = _recipe("release")
    positions: List[int] = [_line_of(recipe, step) for step in RELEASE_ORDER]
    assert positions == sorted(positions), dict(zip(RELEASE_ORDER, positions))
    assert recipe[positions[0] - 1 : positions[0]] == ['@echo "Start Release"'], "the preflight must run first"
    assert "uv run --no-sync pytest tests/unit -q \\" in _recipe("test")


def test_a_release_with_nothing_to_commit_goes_on_and_a_failing_commit_stops_it() -> None:
    """
    Verify the commit is ``git diff --cached --quiet || git commit``, never ``-git commit``.

    A leading ``-`` makes make ignore EVERY failure of the line, so a commit refused for a real reason (no author
    identity, a broken index) went on to publish and tag a tree that was never committed.
    """
    recipe: List[str] = _recipe("release")
    commit: str = recipe[_line_of(recipe, "git commit --no-verify")]
    assert commit.startswith("git diff --cached --quiet || ")
    assert [line for line in recipe if line.startswith("-")] == []


def test_the_steps_that_need_no_credential_run_without_them() -> None:
    """Verify build, hooks, tests, commit, push, branch and tag run under ``WITHOUT_CREDENTIALS``."""
    recipe: List[str] = _recipe("release")
    for step in (
        "make build",
        "make precommit_hooks_run_all_files",
        "make check_build",
        "make test",
        "git commit --no-verify",
        "git push",
        "make create_release_branch",
        "make create_release_tag",
    ):
        assert "${WITHOUT_CREDENTIALS} " + step in recipe[_line_of(recipe, step)], step


def test_the_preflight_checks_credentials_versions_notes_and_tools_without_side_effects() -> None:
    """Verify ``release_preflight`` runs every read-only check, and ``spc`` asks origin and PyPI with anchored refs."""
    preflight = re.search(r"^release_preflight:([^#\n]*)", MAKEFILE, flags=re.MULTILINE)
    assert preflight is not None
    for check in ("check_host_tools", "spc", "check_github_credentials", "check_pypi_credentials"):
        assert re.search(rf"\b{check}\b", preflight.group(1)), check
    assert re.search(r"^spc:\s*check_release_notes\b", MAKEFILE, flags=re.MULTILINE)
    spc: str = "\n".join(_recipe("spc"))
    assert 'git ls-remote --exit-code origin "refs/heads/release/${ONDEWO_CSI_VERSION}"' in spc
    assert 'git ls-remote --exit-code origin "refs/tags/${ONDEWO_CSI_VERSION}"' in spc
    assert "https://pypi.org/pypi/${PYPI_PACKAGE}/${ONDEWO_CSI_VERSION}/json" in spc
    assert "& exit" not in MAKEFILE.replace("&& exit", "")
    assert "gh api repos/${GH_REPO_NAME} --jq .permissions.push" in "\n".join(_recipe("check_github_credentials"))


def test_release_verify_checks_the_tag_the_notes_and_pypi() -> None:
    """Verify ``release_verify`` needs the tag on origin, a non-empty GitHub release body and PyPI serving it."""
    verify = re.search(r"^release_verify:([^#\n]*)", MAKEFILE, flags=re.MULTILINE)
    assert verify is not None
    assert verify.group(1).split() == ["verify_tag", "verify_github_release", "verify_pypi"]
    assert "--json body --jq .body" in "\n".join(_recipe("verify_github_release"))
    assert "seq 1 ${RELEASE_VERIFY_ATTEMPTS}" in "\n".join(_recipe("verify_pypi"))


def test_ondewo_release_deletes_the_devops_clone_before_it_releases() -> None:
    """
    Verify ``ondewo_release`` deletes the devops-accounts clone BEFORE ``make release``, and on failure too.

    The clone holds every credential. Deleted only after a successful release, it survived every failed one in
    the release host's working tree - and in the ``docker build .`` context of the utils image.
    """
    assert re.search(r"^ondewo_release:\s*spc\b", MAKEFILE, flags=re.MULTILINE)
    recipe: str = "\n".join(_recipe("ondewo_release"))
    assert recipe.index('trap \'if [ -n "$$owned" ]; then rm -rf "$$owned"; fi\' EXIT') < recipe.index("git clone")
    assert 'owned="$$(mktemp -d)"' in recipe
    assert '[ -n "$${DEVOPS_ACCOUNT_DIR:-}" ] && [ -d "$${DEVOPS_ACCOUNT_DIR}" ]' in recipe
    loaded: int = recipe.index("set +a")
    deleted: int = recipe.index('rm -rf "$$owned"; owned=""', loaded)
    released: int = recipe.index("make release")
    assert loaded < deleted < released
    assert recipe.rstrip().endswith("make release")
    assert "$(MAKE)" not in recipe, "`make -n ondewo_release` must print, not clone the credentials"
    assert not re.search(r"^DEVOPS_ACCOUNT_DIR\s*[?:]?=", MAKEFILE, flags=re.MULTILINE), "the driver's value must win"


def test_standalone_preflight_and_verify_load_their_credentials_from_devops_account_dir() -> None:
    """
    Verify every recipe line that hands a credential to a container first runs ``$(LOAD_CREDENTIALS)``.

    ondewo-csi-api's driver runs ``release_preflight`` and ``release_verify`` on their own, with only an absolute
    ``DEVOPS_ACCOUNT_DIR`` set and no token in the environment; without the load, gh ran unauthenticated and
    ``release_verify`` reported a live GitHub release as missing.
    """
    load = re.search(r"^LOAD_CREDENTIALS=((?:.*\\\n)*.*)", MAKEFILE, flags=re.MULTILINE)
    assert load is not None
    assert '[ -n "$${DEVOPS_ACCOUNT_DIR:-}" ]' in load.group(1)
    assert "grep -h -E '^(GITHUB_GH_TOKEN|PYPI_USERNAME|PYPI_PASSWORD)='" in load.group(1)
    for target in ("check_github_credentials", "check_pypi_credentials", "verify_github_release"):
        recipe: List[str] = _recipe(target)
        container_lines: List[int] = [index for index, line in enumerate(recipe) if "docker run" in line]
        assert container_lines, target
        first: int = next(index for index, line in enumerate(recipe) if line.startswith("@"))
        assert recipe[first] == "@$(LOAD_CREDENTIALS) \\", target
        # One shell: every line from the load to the container is a continuation of it.
        assert all(line.endswith("\\") for line in recipe[first : container_lines[-1]]), target
    assert re.search(r"^RELEASE_VERIFY_ATTEMPTS\?=\$\(if \$\(VERIFY_ATTEMPTS\)", MAKEFILE, flags=re.MULTILINE)


def test_the_legacy_driver_rewrite_touches_only_the_three_pins() -> None:
    """
    Verify the version rewrites of older ondewo-csi-api release drivers change nothing but the three pins.

    Those drivers ran ``s/ONDEWO_CSI_VERSION.*=.*/.../``, ``s/ONDEWO_PROTO_COMPILER_GIT_BRANCH.*=.*/.../`` and
    ``s/CSI_API_GIT_BRANCH.*=.*/.../`` over this Makefile, unanchored: any OTHER line naming the variable and
    carrying an ``=`` after it (``... >/dev/null; status=$$?``, a ``VERSION_RE=`` helper) was replaced wholesale.
    """
    rewrites = [
        (re.compile(r"ONDEWO_CSI_VERSION.*=.*"), "ONDEWO_CSI_VERSION=9.9.9"),
        (re.compile(r"ONDEWO_PROTO_COMPILER_GIT_BRANCH.*=.*"), "ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/9.9.9"),
        (re.compile(r"CSI_API_GIT_BRANCH.*=.*"), "CSI_API_GIT_BRANCH=tags/9.9.9"),
    ]
    changed: List[str] = []
    for line in MAKEFILE.splitlines():
        rewritten: str = line
        for pattern, replacement in rewrites:
            rewritten = pattern.sub(replacement, rewritten)
        if rewritten != line:
            changed.append(rewritten)
    assert changed == [
        "ONDEWO_CSI_VERSION=9.9.9",
        "ONDEWO_CSI_API_GIT_BRANCH=tags/9.9.9",
        "ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/9.9.9",
    ]


def _make_dry_run(tmp_path: Path, *arguments: str) -> subprocess.CompletedProcess:
    """
    Run ``make -n`` in this repository with a ``git`` on ``PATH`` that records every call and fails.

    Args:
        tmp_path (Path):
            A private directory for the fake ``git`` and its call log.
        *arguments (str):
            The make goal and variables.

    Returns:
        subprocess.CompletedProcess:
            The finished ``make -n`` run; ``(tmp_path / "git.calls")`` exists only if ``git`` was called.
    """
    fake_bin: Path = tmp_path / "bin"
    fake_bin.mkdir()
    fake_git: Path = fake_bin / "git"
    fake_git.write_text(f'#!/bin/sh\necho "$*" >> "{tmp_path}/git.calls"\nexit 1\n', encoding="utf-8")
    fake_git.chmod(0o755)
    environment: Dict[str, str] = {
        name: value
        for name, value in os.environ.items()
        if name not in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "VERIFY_ATTEMPTS", "VERIFY_INTERVAL_S")
    }
    environment["PATH"] = f"{fake_bin}{os.pathsep}{environment.get('PATH', '')}"
    return subprocess.run(
        ["make", "--no-print-directory", "-n", *arguments],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
def test_a_dry_run_of_ondewo_release_clones_and_reads_nothing(tmp_path: Path) -> None:
    """
    Verify ``make -n ondewo_release`` only PRINTS: no ``git`` runs, so nothing is cloned, and no credential is read.

    A ``$(MAKE)`` (or ``$(shell git ...)``) in the recipe would make ``make -n`` execute it, i.e. clone
    ondewo-devops-accounts and start a real release from a dry run.
    """
    completed = _make_dry_run(tmp_path, "ondewo_release", "DEVOPS_ACCOUNT_DIR=/nonexistent/ondewo-devops-accounts")
    assert completed.returncode == 0, completed.stderr
    assert not (tmp_path / "git.calls").exists(), (tmp_path / "git.calls").read_text(encoding="utf-8")
    assert "git clone -q --depth 1 git@bitbucket.org:ondewo/ondewo-devops-accounts.git" in completed.stdout
    assert completed.stdout.rstrip().endswith("make release")


@pytest.mark.skipif(shutil.which("make") is None, reason="make is not installed")
def test_the_driver_wide_verify_overrides_reach_the_pypi_polling(tmp_path: Path) -> None:
    """Verify ``VERIFY_ATTEMPTS`` / ``VERIFY_INTERVAL_S`` (passed by ondewo-csi-api's driver) set the poll loop."""
    completed = _make_dry_run(tmp_path, "verify_pypi", "VERIFY_ATTEMPTS=3", "VERIFY_INTERVAL_S=7")
    assert completed.returncode == 0, completed.stderr
    assert "$(seq 1 3)" in completed.stdout
    assert "sleep 7;" in completed.stdout
    (tmp_path / "defaults").mkdir()
    defaults = _make_dry_run(tmp_path / "defaults", "verify_pypi")
    assert "$(seq 1 20)" in defaults.stdout
    assert "sleep 30;" in defaults.stdout
