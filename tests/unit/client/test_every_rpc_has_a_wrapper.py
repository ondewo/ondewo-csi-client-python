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
Every RPC of every ``ondewo.csi`` service is reachable through BOTH the sync and the async client.

The expectations are DERIVED from the generated descriptors (``DESCRIPTOR.services_by_name`` of every
``ondewo/csi/*_pb2.py``), not listed here, so the next API release that adds an RPC fails this module until both
wrappers exist, and one that adds a service fails it until both wrapper classes exist - without anybody having to
remember to extend a list. The wrapper of ``Rpc`` is ``snake_case(Rpc)`` on the class named after the service in
``ondewo.csi.client.services.<snake_case(Service)>`` and its ``async_`` twin, and it must call ``self.stub.Rpc``. An
async wrapper of a STREAMING RPC must not be a coroutine function: grpc.aio returns an async iterator for it, and
``await``-ing that fails at runtime, which ``make build``'s generated async copies get wrong.
"""

import importlib
import inspect
import pkgutil
import re
from types import ModuleType
from typing import (
    Any,
    List,
    Tuple,
)

import pytest

import ondewo.csi


def wrapper_name(name: str) -> str:
    """
    Convert a proto service or RPC name to the wrapper naming convention.

    Args:
        name (str):
            A CamelCase proto name, e.g. ``CreateS2sPipeline`` or ``Conversations``.

    Returns:
        str:
            ``create_s2s_pipeline`` / ``conversations``.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _csi_pb2_modules() -> List[ModuleType]:
    """
    Import every generated ``ondewo.csi.*_pb2`` module.

    Returns:
        List[ModuleType]:
            The modules, sorted by name.
    """
    names: List[str] = sorted(
        info.name for info in pkgutil.iter_modules(ondewo.csi.__path__) if info.name.endswith("_pb2")
    )
    assert names, "no generated ondewo.csi *_pb2 module found - this test would inspect nothing"
    return [importlib.import_module(f"ondewo.csi.{name}") for name in names]


SERVICES: List[Tuple[str, Any]] = [
    (name, service) for module in _csi_pb2_modules() for name, service in module.DESCRIPTOR.services_by_name.items()
]
CASES: List[Any] = [
    pytest.param((name, method), id=f"{name}.{method.name}") for name, service in SERVICES for method in service.methods
]


def _wrapper_class(service_name: str, asynchronous: bool) -> Any:
    """
    Return the hand-written wrapper class of a service.

    Args:
        service_name (str):
            The proto service name, e.g. ``Conversations``.
        asynchronous (bool):
            Whether to return the ``async_`` twin.

    Returns:
        Any:
            The class.
    """
    prefix: str = "async_" if asynchronous else ""
    module: ModuleType = importlib.import_module(f"ondewo.csi.client.services.{prefix}{wrapper_name(service_name)}")
    wrapper: Any = getattr(module, service_name, None)
    assert wrapper is not None, f"{module.__name__} defines no class {service_name}"
    return wrapper


def test_the_descriptors_carry_the_services_this_test_derives_from() -> None:
    """Guard against a vacuous pass: the derived case list is not empty and names the known service and RPCs."""
    names: List[str] = [name for name, _ in SERVICES]
    assert "Conversations" in names
    rpcs: List[str] = [method.name for _, service in SERVICES for method in service.methods]
    for must_contain in ("S2sStream", "GetControlStream", "SetControlStatus", "SetCallMediaControl"):
        assert must_contain in rpcs
    assert len(CASES) > len(SERVICES)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("case", CASES)
def test_every_rpc_has_a_wrapper_that_calls_its_stub(case: Tuple[str, Any], asynchronous: bool) -> None:
    """
    The service's wrapper class has ``wrapper_name(Rpc)``, which calls ``self.stub.<Rpc>``.

    Args:
        case (Tuple[str, Any]):
            The service name and the RPC's method descriptor.
        asynchronous (bool):
            Whether the async twin is checked.
    """
    service_name, method = case
    wrapper: Any = _wrapper_class(service_name, asynchronous)
    function: Any = getattr(wrapper, wrapper_name(method.name), None)
    assert function is not None, f"{wrapper.__module__}.{service_name} has no {wrapper_name(method.name)}()"
    assert f"self.stub.{method.name}(" in inspect.getsource(function)
    streaming: bool = method.server_streaming or method.client_streaming
    if not asynchronous:
        assert not inspect.iscoroutinefunction(function)
    else:
        assert inspect.iscoroutinefunction(function) is not streaming, (
            f"async {service_name}.{wrapper_name(method.name)} must "
            + ("return the stream, not await it" if streaming else "be a coroutine function")
        )
