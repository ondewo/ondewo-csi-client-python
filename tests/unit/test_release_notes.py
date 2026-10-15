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
The GitHub release body is sliced out of RELEASE.md by the Makefile's ``CURRENT_RELEASE_NOTES``.

The slice starts at the heading ``^#+ Release ONDEWO CSI Python Client <version>$`` (anchored, dots escaped) and
ends at the next ``*****`` line. A heading spelled any other way gives an empty slice, and
``gh release create -n ""`` then publishes a release without notes and without an error
(ondewo-vtsi-client-python 4.0.0 to 8.7.0 shipped like that).
"""

import re
import shutil
import subprocess
from pathlib import Path
from typing import List

import pytest

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
RELEASE_NOTES: str = (REPO_ROOT / "RELEASE.md").read_text(encoding="utf-8")
MAKEFILE: str = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
HEADING_PREFIX: str = "## Release ONDEWO CSI Python Client "


def _release_notes_slice(version: str) -> List[str]:
    """Reproduce the Makefile's perl range ``/^#+ Release ONDEWO CSI Python Client <v>$/../^\\*{5}/``."""
    lines: List[str] = RELEASE_NOTES.splitlines()
    heading: re.Pattern = re.compile(rf"^#+ Release ONDEWO CSI Python Client {re.escape(version)}$")
    start: int = next(i for i, line in enumerate(lines) if heading.match(line))
    # Like perl's range operator, an unterminated last section runs to the end of the file.
    end: int = next((i for i in range(start + 1, len(lines)) if re.match(r"^\*{5}", lines[i])), len(lines))
    return lines[start : end + 1]


def test_the_makefile_slices_the_heading_this_test_checks() -> None:
    """The perl range in the Makefile still matches the heading spelling pinned here."""
    assert "/^\\#+ Release ONDEWO CSI Python Client ${RELEASE_VERSION_RE}$$/../^\\*{5}/" in MAKEFILE
    assert "RELEASE_VERSION_RE=$(subst .,\\.,${ONDEWO_CSI_VERSION})" in MAKEFILE


def test_every_release_heading_uses_the_spelling_the_makefile_slices() -> None:
    """No ``## Release ONDEWO`` heading may use another spelling."""
    headings: List[str] = [line for line in RELEASE_NOTES.splitlines() if line.startswith("## Release ONDEWO")]
    assert headings
    assert [heading for heading in headings if not heading.startswith(HEADING_PREFIX)] == []


def test_every_release_section_ends_before_the_next_heading() -> None:
    """Each slice holds exactly one release: a missing ``*****`` separator would pull in the next section."""
    versions: List[str] = [
        line[len(HEADING_PREFIX) :].strip() for line in RELEASE_NOTES.splitlines() if line.startswith(HEADING_PREFIX)
    ]
    assert versions
    assert [v for v in versions if sum(line.startswith(HEADING_PREFIX) for line in _release_notes_slice(v)) != 1] == []


def test_the_current_version_has_non_empty_release_notes() -> None:
    """The version the Makefile releases has a section with content between its heading and the separator."""
    version_match = re.search(r"^ONDEWO_CSI_VERSION=(\S+)$", MAKEFILE, re.MULTILINE)
    assert version_match is not None
    body: List[str] = [line for line in _release_notes_slice(version_match.group(1))[1:-1] if line.strip()]
    assert len(body) > 1


@pytest.mark.skipif(shutil.which("perl") is None, reason="perl is not installed")
def test_the_slice_of_5_5_1_does_not_open_on_a_5_5_10_heading(tmp_path: Path) -> None:
    """
    The opening pattern is anchored: releasing 5.5.1 must not slice the notes of 5.5.10 (or of ``5x5x1``).

    Unanchored, the FIRST heading containing the version string opened the slice, so a RELEASE.md listing 5.5.10
    above 5.5.1 would have published 5.5.10's notes as the 5.5.1 release body.
    """
    match = re.search(r"perl -ne 'print if /(?P<start>[^/]+)/\.\./(?P<end>[^/]+)/'", MAKEFILE)
    assert match is not None
    start: str = match.group("start").replace("${RELEASE_VERSION_RE}", "5\\.5\\.1").replace("$$", "$")
    start = start.replace("\\#", "#")
    notes: Path = tmp_path / "RELEASE.md"
    notes.write_text(
        "# Release History\n\n*****************\n\n"
        "## Release ONDEWO CSI Python Client 5.5.10\n\n* ten\n\n*****************\n\n"
        "## Release ONDEWO CSI Python Client 5x5x1\n\n* wrong dots\n\n*****************\n\n"
        "## Release ONDEWO CSI Python Client 5.5.1\n\n* one\n\n*****************\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        ["perl", "-ne", f"print if /{start}/../{match.group('end')}/", str(notes)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.splitlines() == [
        "## Release ONDEWO CSI Python Client 5.5.1",
        "",
        "* one",
        "",
        "*****************",
    ]
