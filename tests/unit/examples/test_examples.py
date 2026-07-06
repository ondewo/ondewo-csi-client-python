# Copyright 2021-2025 ONDEWO GmbH
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
"""Hermetic tests that prove the ``examples/`` scripts work without a live gRPC server.

The gRPC transport is fully mocked: no channel is opened and no Keycloak/network call is
made. The tests assert that ``keycloak_auth_example`` constructs the client with the
current Keycloak bearer-auth config, builds the right request, and handles the response,
and that every example file still compiles.
"""
import glob
import importlib.util
import py_compile
from pathlib import Path
from types import ModuleType
from typing import List
from unittest.mock import MagicMock

import pytest

from ondewo.csi.conversation_pb2 import (
    ListS2sPipelinesRequest,
    ListS2sPipelinesResponse,
    S2sPipeline,
)

# Repo root is four levels up from this file: tests/unit/examples/test_examples.py.
EXAMPLES_DIR: Path = Path(__file__).resolve().parents[3] / "examples"

# Bound once so a refactor that changes only an input or only an expectation cannot silently
# make a test tautological.
USERNAME: str = "tech-user@example.com"
PASSWORD: str = "s3cr3t"
PIPELINE_ID_1: str = "pipeline-one"
PIPELINE_ID_2: str = "pipeline-two"


def _load_example(name: str) -> ModuleType:
    """
    Load an ``examples/<name>.py`` script as an isolated module.

    The examples directory is not an importable package, so the script is loaded straight
    from its file path. Loading only runs the module-level imports (each example guards its
    side effects behind ``if __name__ == "__main__"``).

    Args:
        name (str):
            The example filename without the ``.py`` suffix.

    Returns:
        ModuleType:
            The freshly executed example module.
    """
    path: Path = EXAMPLES_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    loader = spec.loader
    assert loader is not None
    module: ModuleType = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_all_examples_compile() -> None:
    """Every script under ``examples/`` compiles (syntax + bytecode), no imports executed."""
    example_files: List[str] = sorted(glob.glob(str(EXAMPLES_DIR / "*.py")))
    assert example_files, f"no example scripts found under {EXAMPLES_DIR}"
    for path in example_files:
        py_compile.compile(path, doraise=True)


def test_build_config_uses_keycloak_bearer_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    """``build_config`` yields a complete Keycloak (bearer) config with no legacy fields.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to set the credential environment variables the example reads.
    """
    monkeypatch.setenv("KEYCLOAK_USER_NAME", USERNAME)
    monkeypatch.setenv("KEYCLOAK_PASSWORD", PASSWORD)

    module: ModuleType = _load_example("keycloak_auth_example")
    config = module.build_config()

    assert config.keycloak_configured is True
    assert config.resolved_username == USERNAME
    # The removed cai-token / HTTP-Basic field must not be part of the current config.
    assert not hasattr(config, "http_token")


def test_list_pipeline_ids_builds_request_and_returns_ids() -> None:
    """``list_pipeline_ids`` sends a ``ListS2sPipelinesRequest`` and returns the response ids."""
    module: ModuleType = _load_example("keycloak_auth_example")

    client: MagicMock = MagicMock()
    client.services.conversations.list_s2s_pipelines.return_value = ListS2sPipelinesResponse(
        pipelines=[S2sPipeline(id=PIPELINE_ID_1), S2sPipeline(id=PIPELINE_ID_2)],
    )

    ids: List[str] = module.list_pipeline_ids(client)

    assert ids == [PIPELINE_ID_1, PIPELINE_ID_2]
    client.services.conversations.list_s2s_pipelines.assert_called_once()
    sent_request = client.services.conversations.list_s2s_pipelines.call_args.args[0]
    assert isinstance(sent_request, ListS2sPipelinesRequest)


def test_main_constructs_client_and_prints_pipeline_ids(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``main`` builds an insecure client and prints each pipeline id from the response.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Fixture used to set the password env var and swap ``Client`` for a mock.
        capsys (pytest.CaptureFixture[str]):
            Fixture capturing the example's stdout.
    """
    monkeypatch.setenv("KEYCLOAK_PASSWORD", PASSWORD)

    module: ModuleType = _load_example("keycloak_auth_example")

    fake_client: MagicMock = MagicMock()
    fake_client.services.conversations.list_s2s_pipelines.return_value = ListS2sPipelinesResponse(
        pipelines=[S2sPipeline(id=PIPELINE_ID_1)],
    )
    client_factory: MagicMock = MagicMock(return_value=fake_client)
    monkeypatch.setattr(module, "Client", client_factory)

    module.main()

    printed: str = capsys.readouterr().out
    assert PIPELINE_ID_1 in printed
    client_factory.assert_called_once()
    # No grpc_cert is configured, so the example must build an insecure channel.
    assert client_factory.call_args.kwargs["use_secure_channel"] is False
