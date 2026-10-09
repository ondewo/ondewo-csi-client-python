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
"""TLS and mutual TLS, end to end, through the SDK's own ``Client`` / ``AsyncClient`` and ``ClientConfig``.

Every handshake test builds the real client from a ``ClientConfig`` and sends one real
``CreateS2sPipeline`` to an in-process gRPC server holding a per-session PKI. The server has no
servicer, so ``UNIMPLEMENTED`` proves the TLS handshake completed and the call reached the server;
``UNAVAILABLE`` is the refusal of a handshake. ``CreateS2sPipeline`` is not idempotent, so the
SDK's retry policy never re-sends it and a refused handshake fails at once instead of retrying.

The channel itself is built by ``ondewo-client-utils`` (csi does not override channel creation);
these tests prove the csi config fields reach it unchanged and that the contract holds through
the SDK: both-or-neither client identity, insecure + identity refused, nothing secret rendered.
"""

import datetime
from concurrent import futures
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
)

import grpc
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import (
    ExtendedKeyUsageOID,
    NameOID,
)

from ondewo.csi.client.async_client import AsyncClient
from ondewo.csi.client.client import Client
from ondewo.csi.client.client_config import ClientConfig
from ondewo.csi.conversation_pb2 import S2sPipeline

SERVER_NAME: str = "localhost"
PASSWORD: str = "planted-ropc-password"


class Pki:
    """One throwaway CA with a server leaf (SAN ``localhost``) and a client leaf, all PEM bytes."""

    def __init__(self, name: str) -> None:
        self._ca_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.ca_cert: bytes = self._issue(f"{name}-ca", self._ca_key.public_key(), ca=True, issuer=None)
        ca: x509.Certificate = x509.load_pem_x509_certificate(self.ca_cert)
        server_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.server_key: bytes = _pem_key(server_key)
        self.server_cert: bytes = self._issue(
            f"{name}-server", server_key.public_key(), False, ca, ExtendedKeyUsageOID.SERVER_AUTH, SERVER_NAME
        )
        client_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.client_key: bytes = _pem_key(client_key)
        self.client_cert: bytes = self._issue(
            f"{name}-client", client_key.public_key(), False, ca, ExtendedKeyUsageOID.CLIENT_AUTH
        )

    def _issue(
        self,
        subject: str,
        public_key: ec.EllipticCurvePublicKey,
        ca: bool,
        issuer: Optional[x509.Certificate],
        usage: Optional[x509.ObjectIdentifier] = None,
        san: Optional[str] = None,
    ) -> bytes:
        now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        name: x509.Name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)])
        builder: x509.CertificateBuilder = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name if issuer is None else issuer.subject)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=30))
            .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        )
        if usage is not None:
            builder = builder.add_extension(x509.ExtendedKeyUsage([usage]), critical=False)
        if san is not None:
            builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(san)]), critical=False)
        return builder.sign(self._ca_key, hashes.SHA256()).public_bytes(serialization.Encoding.PEM)


def _pem_key(key: ec.EllipticCurvePrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def _crlf(pem: bytes) -> bytes:
    return pem.replace(b"\n", b"\r\n")


@pytest.fixture(scope="module")
def pki() -> Pki:
    return Pki("deployment")


@pytest.fixture(scope="module")
def foreign() -> Pki:
    return Pki("foreign")


@pytest.fixture
def server() -> Iterator[Callable[[Pki, bool], int]]:
    """Start a servicer-less TLS server on an ephemeral port; ``(pki, require_client_auth) -> port``."""
    servers: List[grpc.Server] = []

    def start(pki: Pki, require_client_auth: bool) -> int:
        grpc_server: grpc.Server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        credentials: grpc.ServerCredentials = grpc.ssl_server_credentials(
            [(pki.server_key, pki.server_cert)],
            root_certificates=pki.ca_cert if require_client_auth else None,
            require_client_auth=require_client_auth,
        )
        port: int = grpc_server.add_secure_port(f"{SERVER_NAME}:0", credentials)
        grpc_server.start()
        servers.append(grpc_server)
        return port

    yield start
    for grpc_server in servers:
        grpc_server.stop(grace=None)


def _config(port: int, trust: Pki, identity: Optional[Pki] = None, crlf: bool = False) -> ClientConfig:
    """A csi ``ClientConfig`` trusting ``trust``'s CA and presenting ``identity``'s client leaf when given."""
    wrap: Callable[[bytes], bytes] = _crlf if crlf else (lambda pem: pem)
    return ClientConfig(
        host=SERVER_NAME,
        port=str(port),
        grpc_cert=wrap(trust.ca_cert).decode(),
        grpc_client_cert=None if identity is None else wrap(identity.client_cert).decode(),
        grpc_client_key=None if identity is None else wrap(identity.client_key).decode(),
    )


def _call(config: ClientConfig) -> grpc.StatusCode:
    """Send one RPC through the sync ``Client`` and return the status the server (or handshake) gave."""
    client: Client = Client(config=config, use_secure_channel=True)
    try:
        with pytest.raises(grpc.RpcError) as failure:
            client.services.conversations.create_s2s_pipeline(S2sPipeline(id="tls-probe"))
        code: grpc.StatusCode = failure.value.code()  # type: ignore[attr-defined]
        return code
    finally:
        client.disconnect()


async def _async_call(config: ClientConfig) -> grpc.StatusCode:
    """Send one RPC through the ``AsyncClient`` and return the status the server (or handshake) gave."""
    client: AsyncClient = AsyncClient(config=config, use_secure_channel=True)
    try:
        with pytest.raises(grpc.aio.AioRpcError) as failure:
            await client.services.conversations.create_s2s_pipeline(S2sPipeline(id="tls-probe"))
        return failure.value.code()
    finally:
        await client.disconnect()


REACHED: grpc.StatusCode = grpc.StatusCode.UNIMPLEMENTED
REFUSED: grpc.StatusCode = grpc.StatusCode.UNAVAILABLE


class TestSyncClientHandshakes:
    def test_plain_tls_reaches_the_server(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        assert _call(_config(server(pki, False), pki)) is REACHED

    def test_mutual_tls_reaches_a_server_requiring_client_certificates(
        self, server: Callable[[Pki, bool], int], pki: Pki
    ) -> None:
        assert _call(_config(server(pki, True), pki, identity=pki)) is REACHED

    def test_no_client_identity_is_refused_by_a_client_auth_server(
        self, server: Callable[[Pki, bool], int], pki: Pki
    ) -> None:
        assert _call(_config(server(pki, True), pki)) is REFUSED

    def test_a_client_identity_from_an_unrelated_ca_is_refused(
        self, server: Callable[[Pki, bool], int], pki: Pki, foreign: Pki
    ) -> None:
        assert _call(_config(server(pki, True), pki, identity=foreign)) is REFUSED

    def test_a_server_from_an_untrusted_ca_is_refused(
        self, server: Callable[[Pki, bool], int], pki: Pki, foreign: Pki
    ) -> None:
        assert _call(_config(server(pki, False), foreign)) is REFUSED

    def test_crlf_pems_complete_the_mutual_tls_handshake(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        assert _call(_config(server(pki, True), pki, identity=pki, crlf=True)) is REACHED

    def test_empty_strings_on_both_identity_fields_mean_plain_tls(
        self, server: Callable[[Pki, bool], int], pki: Pki
    ) -> None:
        config: ClientConfig = ClientConfig(
            host=SERVER_NAME,
            port=str(server(pki, False)),
            grpc_cert=pki.ca_cert.decode(),
            grpc_client_cert="",
            grpc_client_key="",
        )
        assert _call(config) is REACHED


class TestAsyncClientHandshakes:
    @pytest.mark.asyncio
    async def test_plain_tls_reaches_the_server(self, server: Callable[[Pki, bool], int], pki: Pki) -> None:
        assert await _async_call(_config(server(pki, False), pki)) is REACHED

    @pytest.mark.asyncio
    async def test_mutual_tls_reaches_a_server_requiring_client_certificates(
        self, server: Callable[[Pki, bool], int], pki: Pki
    ) -> None:
        assert await _async_call(_config(server(pki, True), pki, identity=pki)) is REACHED

    @pytest.mark.asyncio
    async def test_no_client_identity_is_refused_by_a_client_auth_server(
        self, server: Callable[[Pki, bool], int], pki: Pki
    ) -> None:
        assert await _async_call(_config(server(pki, True), pki)) is REFUSED

    @pytest.mark.asyncio
    async def test_a_client_identity_from_an_unrelated_ca_is_refused(
        self, server: Callable[[Pki, bool], int], pki: Pki, foreign: Pki
    ) -> None:
        assert await _async_call(_config(server(pki, True), pki, identity=foreign)) is REFUSED


class TestConfigContract:
    @pytest.mark.parametrize("half", ["grpc_client_cert", "grpc_client_key"])
    def test_half_a_client_identity_is_refused_by_the_config(self, pki: Pki, half: str) -> None:
        """grpc core would abort() the process on half a pair; the config refuses it before any channel."""
        identity: Dict[str, Any] = {half: (pki.client_cert if half == "grpc_client_cert" else pki.client_key).decode()}
        with pytest.raises(ValueError, match="set both to use mutual TLS, or neither") as refusal:
            ClientConfig(host=SERVER_NAME, port="1", grpc_cert=pki.ca_cert.decode(), **identity)
        assert "BEGIN" not in str(refusal.value)

    @pytest.mark.parametrize("client_class", [Client, AsyncClient])
    def test_an_insecure_channel_with_a_client_identity_is_refused(self, pki: Pki, client_class: type) -> None:
        with pytest.raises(ValueError, match="use a secure channel") as refusal:
            client_class(config=_config(1, pki, identity=pki), use_secure_channel=False)
        assert "BEGIN" not in str(refusal.value)

    def test_repr_and_str_never_render_the_private_key_or_password(self, pki: Pki) -> None:
        config: ClientConfig = ClientConfig(
            host=SERVER_NAME,
            port="1",
            grpc_cert=pki.ca_cert.decode(),
            grpc_client_cert=pki.client_cert.decode(),
            grpc_client_key=pki.client_key.decode(),
            keycloak_url="https://keycloak.invalid/auth",
            realm="realm",
            client_id="client",
            username="user",
            password=PASSWORD,
        )
        # The secrets are really on the object, so their absence below is not vacuous.
        assert config.grpc_client_key == pki.client_key
        assert config.password == PASSWORD
        for rendered in (repr(config), str(config)):
            assert PASSWORD not in rendered
            assert "PRIVATE KEY" not in rendered
            assert pki.client_key.decode() not in rendered
