# Release History

*****************

## Release ONDEWO CSI Python Client 5.4.2

### Bug Fixes

* **5.4.1 made `ondewo-nlu-client==7.0.3` unresolvable for every downstream project.** This package
  ships `ondewo/csi` only and consumes the `ondewo/nlu` protos from the nlu-client wheel, so it pins
  that wheel **exactly** — and an exact pin propagates. 5.4.1 shipped pinning `ondewo-nlu-client==7.0.2`
  on the same day nlu-client 7.0.3 was released, so any project depending on both got
  `requirements are unsatisfiable` from its resolver rather than a usable resolution. The pin is now
  `ondewo-nlu-client==7.0.3`. 7.0.3 is the same nlu-api 7.0.0 generation as 7.0.2 — no `_pb2.py` or
  `_pb2_grpc.py` differs between the two wheels — so the vendored proto alignment the exact pin exists
  to protect is unchanged. No code in this package changed.

*****************

## Release ONDEWO CSI Python Client 5.4.1

### Bug Fixes

* [[OND211-2418]](https://ondewo.atlassian.net/browse/OND211-2418) **A client could silently authenticate as a different user.** `get_keycloak_token_provider` keyed its shared-provider registry on `id(config)` — the memory address of the `ClientConfig`. The service interfaces keep only the grpc channel, so the config passed to the usual `Client(config=ClientConfig(...))` becomes unreachable the moment the client is built; CPython then reuses that address for the next `ClientConfig`, and the `WeakValueDictionary` handed the new client the previous user's still-alive token provider. The second client authenticated as the first user — including when its own credentials were wrong or belonged to nobody at all. Any process that builds more than one client with different identities was affected, and the failure is silent: calls succeed, they are simply made as the wrong principal. The registry is now keyed by a SHA-256 of the credential set (`keycloak_url`, `realm`, `client_id`, username, `password`, `token_expiration_in_s`, `keycloak_verify_ssl`), so two configs share a provider exactly when a shared provider would behave identically for both, and never otherwise. The digest is hashed rather than stored as a plain tuple so the password does not end up in a module-level dict or in that frame's locals, where a traceback renderer printing locals would expose it. This is the same fix released as `ondewo-nlu-client` 7.0.2.
* [[OND211-2418]](https://ondewo.atlassian.net/browse/OND211-2418) **`ClientConfig` printed its credentials in clear text.** `@dataclass` generates a `__repr__` that renders every field, so `log.debug(f"...{config}")` — or any traceback carrying locals — wrote the Keycloak `password` and the gRPC certificate to the logs. That is not hypothetical: a repository-wide sweep in ondewo-vtsi found this class among its leaking dataclasses, and the real staging password was observed on a developer console this way. `repr()` and `str()` now render `password` and `grpc_cert` as `***REDACTED***`. An unset or empty secret still renders as `None` / `''` rather than as the marker: `***REDACTED***` reads as "this is set and sensitive", which is actively misleading when the real fault is that nobody set it — usually the very thing being debugged.
* **Behaviour change** for anyone who parsed the repr: read the attribute (`config.password`, `config.grpc_cert`) instead. Only the rendered text changed — the fields themselves, equality and `dataclasses.asdict()` are untouched.

### Improvements

* The `commit-msg` hooks now run in the right order: `conventional-pre-commit` validates the subject the author typed **before** `giticket` prepends `[<TICKET>]`. With `giticket` first the validator was handed the prefix the other hook had just added and rejected it, so no conforming commit message existed at all — which is why this repo's recent history is full of subjects committed with `--no-verify`.

*****************

## Release ONDEWO CSI Python Client 5.4.0

### Improvements

* Tracking API Version [5.4.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/5.4.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 5.2.0

### Improvements

* Tracking API Version [5.2.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/5.2.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 5.1.0

### Improvements

* Tracking API Version [5.1.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/5.1.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 5.0.0

### Improvements

* Tracking API Version [5.0.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/5.0.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 4.0.1

### Improvements

* Added functionality to pass grpc options to grpc clients based on [ONDEWO CLIENT UTILS PYTHON 2.0.0](https://github.com/ondewo/ondewo-client-utils-python/releases/tag/2.0.0)

*****************

## Release ONDEWO CSI Python Client 4.0.0

### Improvements

* Tracking API Version [4.0.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/4.0.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 3.2.0

### Improvements

* Tracking API Version [3.2.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/3.2.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 3.1.1

### Bug Fixes

* Spelling mistakes fixed synthesize_response
* Examples updated for ondewo-csi-api version 3.1.0

*****************

## Release ONDEWO CSI Python Client 3.1.0

### Improvements

* Tracking API
  Version [3.1.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/3.1.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 3.0.1

### Improvements

* Moved library dependencies to SoundFile, pyaudio, pysoundio to requirements-dev.txt

*****************

## Release ONDEWO CSI Python Client 3.0.0

### Improvements

* Tracking API
  Version [3.0.0](https://github.com/ondewo/ondewo-csi-api/releases/tag/3.0.0) ( [Documentation](https://ondewo.github.io/ondewo-csi-api/) )

*****************

## Release ONDEWO CSI Python Client 2.11.1

### New Features

* Upgraded pyaudio>=0.2.12, pysoundio>=2.0.0 and grpc.*>=1.47.0

*****************

## Release ONDEWO CSI Python Client 2.11.0

### New Features

* Upgraded to CSI API Version 2.3.1

*****************

## Release ONDEWO CSI Python Client 2.10.0

### New Features

* Upgraded to CSI API Version 2.3.0

*****************

## Release ONDEWO CSI Python Client 2.9.0

### Improvements

* [[OND211-2039]](https://ondewo.atlassian.net/browse/OND211-2039) - Added pre-commit hooks and adjusted files to them
* Upgraded to CSI API Version 2.0.0

### New Features

* [[OND211-2039]](https://ondewo.atlassian.net/browse/OND211-2039) - Release Automation

*****************

## Release ONDEWO CSI Python Client 2.8.0

### New Features

* Grpc library upgrades
* Ondewo client updates
* Automate proto generation and pypi package creation

*****************

## Release ONDEWO CSI Python Client 2.7.0

### New Features

* Upgrade toondewo-s2t-client 3.1.0
* Added stop_all_control_messages option

*****************

## Release ONDEWO CSI Python Client 2.6.0

### New Features

* Upgrade to ondewo-nlu-client 2.4.2
* Upgrade toondewo-s2t-client 3.0.0
* Upgrade toondewo-t2s-client 3.0.1
* Upgrade toondewo-sip-client 3.2.0

*****************

## Release ONDEWO CSI Python Client 2.5.1

### New Features

* Upgrade to ondewo-nlu-client 2.4.1

*****************

## Release ONDEWO CSI Python Client 2.5.0

### New Features

* Upgrade to ondewo-csi-api 1.4.0 with extended sip control messages

*****************

## Release ONDEWO CSI Python Client 2.4.1

### New Features

* Upgrade to Ondewo Logging 3.1.0

*****************

## Release ONDEWO CSI Python Client 2.4.0

### New Features

* Sip control messages addition and update sip client to 3.2.0

*****************

## Release ONDEWO CSI Python Client 2.2.0

### New Features

* Control messages integration

*****************

## Release ONDEWO CSI Python Client 2.0.0

### New Features

* New client adaptation to new s2t,t2s, and nlu

*****************

## Release ONDEWO CSI Python Client 1.0.0

### New Features

* Updated ondewo-logging version to 2.0.3
* Updated ondewo-s2t-client version to 1.5.0
* Updated ondewo-nlu-client version to 2.0.0
* Add endpoint for control stream

## Release ONDEWO CSI Python Client 0.2.3

### New Features

* Updated ondewo-sip-client version to 2.2.1

## Release ONDEWO CSI Python Client 0.2.2

### New Features

* [OND233-201] add endpoint for checking health of upstream S2T, NLU and T2S servers
* [OND233-213] add possibility to trigger a specific intent in NLU system in the beginning of the conversation
* [OND233-216] add hangup functionality

*****************

## Release ONDEWO CSI Python Client 0.2.1

### New Features

* Double check licenses

*****************

## Release ONDEWO CSI Python Client 0.2.0

### New Features

* New client!

*****************
