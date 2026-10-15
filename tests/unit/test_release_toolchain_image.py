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
The release toolchain image (``Dockerfile.utils``) runs the same pinned tools on every release.

uv builds the package, twine uploads it and gh creates and reads the GitHub release, all inside this image, so a
floating tag (``uv:latest``, an unpinned ``pip install twine``, gh from the moving apt repository) would let two
releases of the same commit build or upload differently, with nothing in the log to say so.
"""

import re
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
DOCKERFILE: str = (REPO_ROOT / "Dockerfile.utils").read_text(encoding="utf-8")


def test_every_base_image_is_pinned_to_a_version_and_a_digest() -> None:
    """Verify every ``FROM`` / ``COPY --from`` image carries an exact version and a sha256 digest."""
    images = re.findall(r"^(?:FROM|COPY --from=)\s*(\S+)", DOCKERFILE, flags=re.MULTILINE)
    assert images
    for image in images:
        assert re.search(r":[0-9]+\.[0-9]+\.[0-9]+[^@]*@sha256:[0-9a-f]{64}$", image), image


def test_twine_and_gh_are_pinned() -> None:
    """Verify twine and gh are installed at an exact version, gh checked against its published sha256."""
    assert re.search(r"^ARG TWINE_VERSION=[0-9]+\.[0-9]+\.[0-9]+$", DOCKERFILE, flags=re.MULTILINE)
    assert '"twine==${TWINE_VERSION}"' in DOCKERFILE
    assert re.search(r"^ARG GH_VERSION=[0-9]+\.[0-9]+\.[0-9]+$", DOCKERFILE, flags=re.MULTILINE)
    assert re.search(r"^ARG GH_SHA256=[0-9a-f]{64}$", DOCKERFILE, flags=re.MULTILINE)
    assert "sha256sum -c -" in DOCKERFILE
    assert "apt install -y gh" not in DOCKERFILE


def test_the_examples_keep_their_directory_and_cmd_is_exec_form() -> None:
    """Verify ``COPY examples examples`` (``COPY examples .`` flattened it) and the JSON form ``CMD``."""
    assert re.search(r"^COPY examples examples$", DOCKERFILE, flags=re.MULTILINE)
    assert re.search(r"^CMD \[.*\]$", DOCKERFILE, flags=re.MULTILINE)
