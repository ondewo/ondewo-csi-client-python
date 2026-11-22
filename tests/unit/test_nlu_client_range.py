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
"""The declared ``ondewo-nlu-client`` range admits the 7.7 line and stops before the next minor.

This package is the only edge in ondewo-vtsi's locked graph that requires nlu-client, so its range decides what
every consumer can resolve: ondewo-csi, ondewo-sip and ondewo-vtsi move to nlu-client 7.6.0 (the warm-transfer intro
RPCs) and then to 7.7.0 (the typed session-step interruption and the aligned heard-text precisions), and a cap
below it makes all three unresolvable. A sibling MINOR still has to force a decision here.
"""

import tomllib
from pathlib import Path
from typing import List

import pytest
from packaging.requirements import Requirement

REPO_ROOT: Path = Path(__file__).resolve().parents[2]


def _nlu_client_requirement() -> Requirement:
    """
    Read the one ``ondewo-nlu-client`` requirement of ``[project.dependencies]``.

    Returns:
        Requirement:
            The parsed requirement.
    """
    dependencies: List[str] = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "dependencies"
    ]
    requirements: List[Requirement] = [
        Requirement(line) for line in dependencies if Requirement(line).name == "ondewo-nlu-client"
    ]
    assert len(requirements) == 1, f"expected one ondewo-nlu-client requirement, found {requirements}"
    return requirements[0]


@pytest.mark.parametrize("version", ["7.4.0", "7.5.0", "7.5.9", "7.6.0", "7.6.3", "7.7.0", "7.7.4"])
def test_the_range_admits(version: str) -> None:
    """The 7.4 to 7.7 lines all serve the generated code, which imports only nlu-api 7.4.0 messages."""
    assert _nlu_client_requirement().specifier.contains(version)


@pytest.mark.parametrize("version", ["7.3.9", "7.8.0", "8.0.0"])
def test_the_range_refuses(version: str) -> None:
    """Below the 7.4 floor, and from the next minor on, the range refuses."""
    assert not _nlu_client_requirement().specifier.contains(version)


def _t2s_client_requirement() -> Requirement:
    """
    Read the one ``ondewo-t2s-client`` requirement of ``[project.dependencies]``.

    Returns:
        Requirement:
            The parsed requirement.
    """
    dependencies: List[str] = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "dependencies"
    ]
    requirements: List[Requirement] = [
        Requirement(line) for line in dependencies if Requirement(line).name == "ondewo-t2s-client"
    ]
    assert len(requirements) == 1, f"expected one ondewo-t2s-client requirement, found {requirements}"
    return requirements[0]


@pytest.mark.parametrize("version", ["6.7.0", "6.7.2", "6.8.0", "6.8.3"])
def test_the_t2s_range_admits(version: str) -> None:
    """The 6.7 and 6.8 lines (6.8.0 adds response-only text spans and word timings) both serve the generated code."""
    assert _t2s_client_requirement().specifier.contains(version)


@pytest.mark.parametrize("version", ["6.6.9", "6.9.0"])
def test_the_t2s_range_refuses(version: str) -> None:
    """Below the 6.7 floor, and from the next minor on, the range refuses."""
    assert not _t2s_client_requirement().specifier.contains(version)
