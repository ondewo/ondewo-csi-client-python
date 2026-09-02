# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Principles

Behavioral guidelines to reduce common mistakes. They bias toward caution over speed; for trivial tasks, use judgment.

### Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Surgical changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that _your_ changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### Goal-driven execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and
clarifying questions come before implementation rather than after mistakes.

## Logging

```python
from loguru import logger as log
```

- **Levels:** `log.trace()`, `log.debug()`, `log.info()`, `log.warning()`, `log.error()`, `log.exception()`. Choose by
  hotness/verbosity — `trace` for per-token / hot-path detail, `debug` for routine method entry/exit, `info` for notable
  lifecycle events, `warning` / `error` / `exception` for problems.
- **Interpolate with f-strings, not loguru's `{}` positional args.** Consistent with the Code Style rule, use
  `f"…{value}"`; only add the `f` prefix when the string actually interpolates (`"START: …"` with no params stays a
  plain string).
- **`START:` / `DONE:` bracketing.** Wrap a method (or other notable operation) with a `START:` line at entry and a
  `DONE:` line at exit, both naming `ClassName: method_name` (append `: param={value}` context where useful):

  ```python
  log.debug("START: IntentBertClassifier: predict")
  ...
  log.debug(f"DONE: IntentBertClassifier: predict. Elapsed time: {perf_counter() - start_time:.5f}")
  ```

- **Timing uses `perf_counter()`, rendered `:.5f`.** Measure elapsed time with `time.perf_counter()` captured as a start
  value and subtracted at the `DONE:` line; always format the elapsed value with the `:.5f` spec:

  ```python
  from time import perf_counter

  start_time: float = perf_counter()
  ...
  log.info(f"DONE: SESSION SERVICER: DetectIntent. Elapsed time: {perf_counter() - start_time:.5f}")
  ```

  Never measure a duration with `time.time()` — reserve `time.time()` for wall-clock timestamps (epoch seconds persisted
  to a DB / proto, unique-id or filename stamps). `perf_counter()` has an undefined epoch and must not be stored or
  compared across processes.

## Docstrings

Google-style, triple double-quotes:

```python
"""
Short imperative summary line.

Args:
    param_name (type):
        Description of the parameter.

Returns:
    type:
        Description of the return value.

Raises:
    ExceptionType:
        When this exception is raised.
"""
```

## Git Commits

- **Never include Claude as author or co-author** in commit messages, PR descriptions, or any other text. Do not add
  `Co-Authored-By: Claude…` trailers, "Generated with Claude Code" footers, or any similar attribution.
- The user's own git author identity (already configured in git) is the only identity that should appear on commits.
- This rule overrides the default Claude Code commit-template guidance.
- **Never prepend the JIRA ticket ID** (e.g. `[OND211-2386]`) to the commit subject yourself. The `giticket` pre-commit
  hook reads the ticket from the branch name (`(feature|bugfix|support|hotfix)/<TICKET>-…`) and prepends `[<ticket>]`
  (with a trailing space) automatically. Writing the prefix manually produces a duplicate like
  `[OND211-2386] [OND211-2386] feat: …`. Write the subject as plain Conventional Commits (`feat: …`, `fix(scope): …`,
  `docs(types): …`) and let the hook add the prefix on commit.

## General Principles

- Follow existing patterns before introducing new abstractions.
- Keep changes minimal and consistent with surrounding code.
- Validate inputs early with descriptive, context-rich error messages.
- Use context managers for files, sockets, and thread pools.
- Prefer region comments for grouping methods in files that already use them.
- End edited Markdown and YAML files with a trailing newline.

## GitHub Actions — the `tests` workflow is a REQUIRED gate

`.github/workflows/tests.yml` (job `unit-tests`) runs on **every push to every branch** and on every pull request. It
is a required gate, not advisory: a red run means the commit is broken and must be fixed, never merged around. Ask the
API for a specific commit's real verdict rather than guessing:

```bash
SHA=$(git rev-parse HEAD)
curl -s "https://api.github.com/repos/ondewo/ondewo-csi-client-python/actions/runs?head_sha=$SHA"
```

Read `.workflow_runs[].status` and `.conclusion`. Downloading a run's **logs** needs admin rights and answers
`403 Must have admin rights to Repository` for an ordinary token, so reproduce the failure locally instead.

### Reproducing it locally — in a FRESH venv, never your dev venv

This repo does not use `uv`; the workflow is plain `pip` on Python 3.12. Copy its commands exactly:

```bash
python3.12 -m venv /tmp/gha_venv
/tmp/gha_venv/bin/python -m pip install --upgrade pip
/tmp/gha_venv/bin/python -m pip install -e .
/tmp/gha_venv/bin/python -m pip install pytest pytest-cov pytest-asyncio
/tmp/gha_venv/bin/python -m pytest tests/unit -q \
  --cov=ondewo.csi.client.utils.keycloak \
  --cov=ondewo.csi.client.client_config \
  --cov=ondewo.csi.client.core.services_interface \
  --cov=ondewo.csi.client.core.async_services_interface \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-fail-under=100
```

- **The fresh venv is the load-bearing part.** The workflow installs `pip install -e .` (that is, `requirements.txt`)
  plus exactly `pytest pytest-cov pytest-asyncio`, and NEVER `requirements-dev.txt`. Your working venv does have the
  dev requirements, so it carries packages CI lacks and hides this entire failure class — the same way a non-frozen
  dependency install hides a stale lock file in the `uv`-based repos. Running the suite in your dev venv is not a
  reproduction of CI.
- **`python-dotenv` is the live instance of that trap.** It is listed in `requirements-dev.txt` only, never in
  `requirements.txt`, so it is absent in CI. All eight scripts under `examples/` pre-load `examples/environment.env`,
  and a module-scope `from dotenv import load_dotenv` therefore passes locally and dies in CI with
  `ModuleNotFoundError: No module named 'dotenv'`. That is what turned run #49 red, through the three tests in
  `tests/unit/examples/test_examples.py` that import `keycloak_auth_example`. The README promises an example runs
  "like any other python file" after installing the library, so the fix belongs in the example, not in CI: guard the
  import and fall back to the process environment, as `_load_example_environment` in
  `examples/keycloak_auth_example.py` now does. Do **not** promote `python-dotenv` to `requirements.txt` — that makes
  it a runtime dependency of every consumer for a convenience the shipped wheel does not even contain (`setup.py`
  packages `ondewo.*` only, so `examples/` is never distributed). The other seven examples still carry the unguarded
  import; no test imports them, so they do not break CI today.

### The coverage gate names its modules by hand, and the dotted form FAILS OPEN

`--cov-fail-under=100` reads as absolute but is scoped to the four dotted modules listed above, and the repo holds no
coverage configuration at all — no `.coveragerc`, no `pyproject.toml`, and `setup.cfg` carries only `[bdist_wheel]` —
so those CLI arguments are the entire configuration. Two consequences, both measured here rather than assumed:

- **A dotted `--cov=` module the suite never imports vanishes from the report instead of scoring 0%**, and the run
  stays green. Appending `--cov=ondewo.csi.client.async_client --cov=ondewo.csi.client.async_services_container`
  (neither is imported anywhere under `tests/unit`) still prints `Required test coverage of 100% reached. Total
  coverage: 100.00%` and exits 0. The only trace is a non-fatal `CoverageWarning: ... was never imported
  (module-not-imported)` on stderr. Naming a module in the gate is therefore NOT the same as gating it: after adding
  one, confirm its row really appears in the `term-missing` table.
- **The filesystem-scanned form does not fail open.** `--cov=ondewo.csi.client` reports those same two modules at 0%,
  and the whole hand-written surface as 306 statements at 83%, against the gated subset's 204 statements at 100%. The
  gap is deliberate — `client.py`, `services_container.py`, both `conversations` services and the two async modules
  sit outside the gate by the workflow's own comment — but it means "100%" describes the Keycloak/D18 auth surface,
  not the package.

`flake8` and `mypy` are **not** part of this workflow; they run only through `.pre-commit-config.yaml` and the
`make flake8` / `make mypy` targets. A green Actions run says nothing about lint or types — run those yourself.

## What this package actually ships (and what it does not)

This client installs **`ondewo/csi` only**. It contains **no** `ondewo/nlu`, `ondewo/s2t` or
`ondewo/t2s` `*_pb2` modules — `pyproject.toml` declares `ondewo-nlu-client>=7.0.4,<7.1.0`,
`ondewo-s2t-client>=7.4.2,<7.5.0` and `ondewo-t2s-client>=6.6.3,<6.7.0`, and the csi protos
reference those packages' descriptors at import time. Verified against the installed
`.dist-info/RECORD`: this dist claims zero files under `ondewo/nlu/`.
`tests/unit/client/test_proto_descriptor_pool.py` holds that line at test time: it imports the csi,
nlu, s2t and t2s protos into one process and asserts all four register, which is the exact collision
a vendored copy would cause.

That matters when someone reasons about descriptor-pool collisions. The sibling client
`ondewo-vtsi-client-python` **does** vendor foreign protos (55 files under `ondewo/nlu`, plus
`ondewo/{s2t,t2s,sip,qa}`), so _it_ has to be regenerated in lockstep with the service clients. This
one does not — bump it only when the `ondewo/csi` surface itself changes. Do not "helpfully" add
vendored nlu protos here; it would create exactly the duplicate-file-in-pool crash the current
layout avoids.

Consumers pin this repo two different ways, and the difference decides whether a fix here reaches them:
`ondewo-csi` pins a **git rev** (`pyproject.toml`, currently `b033abec` — the commit immediately before the
`ClientConfig` redaction below), while `ondewo-vtsi` pins an **exact PyPI version**, currently
`ondewo-csi-client==5.4.3`. A rev pin picks up a branch commit; a version pin needs a release. Never rebase
or force-push a commit that a pin references.

**Whatever this file allows is what ondewo-vtsi can resolve, and that was papered over there.** This package
is the only edge in vtsi's whole locked graph that requires nlu-client, so the pin here propagates verbatim:
while this repo pinned `ondewo-nlu-client==7.0.3` **exactly**, vtsi could not lock against `7.0.4` at all
(`requirements are unsatisfiable`) and carries a `[tool.uv] override-dependencies = ["ondewo-nlu-client==7.0.4"]`
to cross it. **5.4.4 replaces that exact pin with `>=7.0.4,<7.1.0`**, which makes the override obsolete — once
5.4.4 is published, vtsi should bump its pin and drop it. Note what an override actually costs: it silences the
resolver, so a genuinely incompatible nlu-client would install without complaint and fail at import or at
descriptor registration.

The range narrows that propagation rather than ending it. A sibling **patch** release now reaches consumers with
no release here at all. A sibling **minor** — nlu `7.1.0`, s2t `7.5.0`, t2s `6.7.0` — still makes every consumer
unresolvable until this file moves, and that is deliberate: a minor is where a new proto generation would
plausibly land, so it should force a decision rather than resolve silently.

## Jenkins — never trigger a multibranch scan or branch indexing

**NEVER trigger a Jenkins multibranch scan or branch indexing.** Do not call a multibranch/folder job's
`build`, `scan`, or reindex endpoints, click "Scan Repository Now" / "Build Now" on a folder, run
`p4 scan`, or use any API/CLI that reindexes branches or scans the repository. A scan/reindex runs across
**every** branch, consumes CI resources, and can kick off unintended builds and deploys.

If a branch is not building — it was not discovered, or its job is marked `buildable: false` / orphaned —
**report it and stop**. Let the user or a Jenkins admin adjust branch-discovery/config or rename the branch
to the convention. Never force a build by scanning or reindexing.

## Release gotchas (hard-won this session)

These bit us during the 6.14.0 release. Keep them in mind when releasing.

- **Trust the registry, not the log.** `make release_all_clients` wraps each client in `|| echo "Already released …"`, so a _failed_ release is reported as "done". After any release, verify the GitHub release **and** the published package (PyPI / npm) directly.
- **`npm install failed after 5 attempts` in a release log is usually a red herring** — that text is the echo _inside_ the docker `RUN for i in 1..5; do npm install …` retry loop, not a real failure (`npm install` succeeds → `#10 DONE`). Look further down for the real error (a TTY error, an eslint failure, a `setup.py` error).
- **Codegen must run TTY-free.** The `docker run` that invokes the proto-compiler must not pass `-it` — non-interactively it fails with `cannot attach stdin to a TTY-enabled container because stdin is not a terminal`. Fix the script (drop `-it`), or run the whole release under a pseudo-TTY: `script -qc 'make …' /dev/null`.
- **Release Makefiles can print secrets, and that is the PROJECT OWNER'S call, not yours.** Some
  `docker run … -e <TOKEN>=…` recipe lines lack a leading `@`, so `make` echoes the expanded token. In
  THIS repo that was fixed on master by "fix(release): stop make echoing PyPI and GitHub credentials".
  Where it still happens elsewhere, **do not rotate the credential and do not re-plumb the shared release
  recipe yourself** — those credentials live in `ondewo-devops-accounts` and are shared by every ondewo
  repository's release job, so rotating one breaks the next release of every other repo, and
  `run_release_with_devops` is shared verbatim across the SDKs so a local "improvement" desynchronises
  them. Report it once and leave it; the decision is recorded in ondewo-vtsi's CLAUDE.md §0.2. What still
  applies without exception: never write a credential into a file, a commit, a document or a log line
  yourself, and scrub any scratch file that captured one.
- **The release does NOT auto-pull the latest `ondewo-proto-compiler` tag — it checks out the PINNED one,
  and the pin can silently disagree with the committed gitlink.** `checkout_defined_submodule_versions`
  runs `git -C ondewo-proto-compiler checkout ${ONDEWO_PROTO_COMPILER_GIT_BRANCH}`, so the Makefile
  variable is authoritative for what gets built while the gitlink is authoritative for what git records.
  When they disagree the build DOWNGRADES the submodule and the release commit records that downgrade,
  with nothing failing anywhere. Measured 2026-09-02: the Makefile read `tags/5.12.0` while the gitlink
  had already moved to `205429a5` = `tags/5.13.0` (commit "Update proto compiler dependency to version
  5.13.0"), so every build since had been quietly reverting it. **Before any release, assert the two
  agree:**

  ```bash
  git -C ondewo-proto-compiler rev-parse "$(grep -oE '^ONDEWO_PROTO_COMPILER_GIT_BRANCH=.*' Makefile \
    | cut -d= -f2)^{commit}"          # what make will check out
  git ls-files -s ondewo-proto-compiler | awk '{print $2}'   # what git records
  ```

  The same trap exists in `ondewo-sip-client-python`, where it was found first. A Python client can take a
  compiler bump cheaply: `git diff --name-only tags/<old> tags/<new> -- python/` was **empty** for
  5.12.0 -> 5.14.0, because 5.13.0 and 5.14.0 are Angular/TypeScript presence work. Measure that diff
  rather than assuming a bump is inert, and rather than assuming it is risky.
- **npm package names are inconsistent** — e.g. the JS client publishes as `@ondewo/ondewo-nlu-client-js` (double `ondewo`), not `@ondewo/nlu-client-js`. Check `src/package.json`'s `name` before querying npm.
- **PyPI build needs setuptools.** The release image (`Dockerfile.utils`) is `python:3.12-slim`, which bundles no `setuptools`, so `python setup.py sdist bdist_wheel` dies with `ModuleNotFoundError: No module named 'setuptools'`. `Dockerfile.utils` must `pip install … setuptools wheel`.

## Python tooling — uv + ruff + mypy + pyproject.toml (this session's refactor)

This repo was migrated off `setup.py` / `.flake8` / `mypy.ini` to a single **pyproject.toml** with **uv**, **ruff**, and **mypy**. Going forward:

- **Build backend stays setuptools** (for PyPI compatibility). Build with `python -m build --no-isolation` or `uv build` — NOT `python setup.py sdist bdist_wheel` (setup.py is deleted). `Dockerfile.utils` installs `twine setuptools wheel build`.
- **Dependencies via uv + a committed `uv.lock`.** CI runs `uv sync --extra dev --frozen`. To add/change a dep: edit `[project.dependencies]`/`[project.optional-dependencies].dev` in pyproject.toml then `uv lock`.
- **Lint is ruff** (`[tool.ruff]`, line-length 120, generated `*_pb2*` excluded) — `uv run ruff check .`. flake8 is gone.
- **mypy config lives in `[tool.mypy]`.** Do **NOT** re-create `mypy.ini` — it silently _shadows_ the pyproject config. Generated `*_pb2*` modules get `ignore_errors` overrides.
- **Do NOT re-add `setup.py`** — with setuptools>=61 it conflicts with `[project]` on duplicated metadata.
- **PEP 625**: the sdist is now underscore-normalised (`ondewo_<name>-<v>.tar.gz`); anything that greps the tarball name by hand must use underscores.
- The version-bump release target edits the version in **pyproject.toml** (not setup.py); the release stages `pyproject.toml uv.lock`.
- **CI installs `portaudio19-dev`** — `pyaudio`/`pysoundio` (pulled transitively via the s2t/t2s clients in the dev extra) build from source and need PortAudio headers.

## uv migration — completed conversion (this session)

The repo is now fully on **uv** (not just pyproject.toml):

- `make setup_developer_environment_locally` bootstraps uv (installs it if missing), runs `uv sync --extra dev` (creates `.venv` + installs all runtime+dev deps + pre-commit), then `uv run pre-commit install`. **No conda** — the old `create_conda_env`/`setup_conda_env` scaffolding was removed.
- Every Makefile target uses uv: `uv sync --extra dev` (deps), `uv run pytest`/`ruff`/`mypy` (tools), `uv build` (wheel). No `pip install`, no `python -m build`, no `python setup.py`.
- New targets: `make ruff` / `make ruff_fix` / `make ruff_format` / `make mypy`. The `flake8` target is **removed**.
- Removed for good: `requirements.txt`, `requirements-dev.txt`, `setup.cfg` — deps + tool config live in `pyproject.toml`. Do **not** re-add them.
- `Dockerfile.utils` installs uv (`COPY --from=ghcr.io/astral-sh/uv`) and builds with uv; it no longer `COPY`s `requirements.txt`.
- **`[tool.mypy] python_version` must be `3.12`** wherever numpy 2.x is on the mypy path — its PEP-695 `type X = …` stubs fail to parse on < 3.12.
- The release `git commit` uses **`--no-verify`** so pre-commit hooks never gate an automated release.
- **Validated by a real PyPI publish** — `ondewo-t2s-client 6.5.0` was built with `uv build` and uploaded via twine end-to-end; the uv release pipeline works.

## `ClientConfig` must not print its secrets

`@dataclass` generates a `__repr__` that prints **every** field, so `log.debug(f"…{config}")` — or any
traceback carrying locals — wrote the ROPC `password` and the PEM `grpc_cert` to the log in clear text.
Downstream consumers really do log config objects: a repository-wide sweep in ondewo-vtsi found this class
among the leakers, alongside thirteen of its own dataclasses. All five ONDEWO Python clients had the same
defect and all five now carry the same fix.

`ondewo/csi/client/client_config.py` names the secrets once and renders around them:

```python
SECRET_FIELD_NAMES: ClassVar[FrozenSet[str]] = frozenset({"password", "grpc_cert"})
```

Four properties are load-bearing:

- **An empty secret renders as `''`, never as `***REDACTED***`.** The marker reads as "this is set and
  sensitive", which is actively misleading when the real fault is that nobody set it — usually the very
  thing being debugged. The `__repr__` therefore redacts only a _truthy_ value.
- **A new secret field must join `SECRET_FIELD_NAMES` in the same commit.** That frozenset is the entire
  policy; nothing infers sensitivity from a field name.
- **Redaction covers `repr()` / `str()` only.** Measured on the sibling class: `to_json()`, `to_dict()` and
  `dataclasses.asdict()` still return the plaintext password, and `to_json()` renders the certificate as a
  byte array. That is deliberate, because `@dataclass_json` has to round-trip through `from_json` — so
  never log a serialized config, and do not "fix" it by redacting there.
- **The guard is behavioural.** `tests/unit/client/test_client_config_redacts_secrets.py` builds a
  `ClientConfig` with distinctive planted values and reads its `repr`. It does not grep for `__repr__`,
  because a grep passes just as well for a `__repr__` that prints the secret anyway. It also asserts each
  secret is really **on the object** (`config.password == PASSWORD`) before asserting it is absent from the
  repr — reading only the repr would pass vacuously against unfixed code. The certificate is compared
  against `GRPC_CERT.encode()`, since `BaseClientConfig.__post_init__` encodes it to `bytes`; comparing to
  the `str` would fail while the redaction it guards worked perfectly.

Run it with `uv run pytest tests/unit/client/test_client_config_redacts_secrets.py -q` — 5 tests.

**The fix shipped in 5.4.1** — `git tag --contains ed7f90c` lists `5.4.1`, `5.4.2`, `5.4.3`, and ondewo-vtsi
now pins `ondewo-csi-client==5.4.3`, so that consumer has it. Only the published `5.4.0` artifact still
carries the leak. ondewo-csi's git-rev pin (`b033abec`, the commit immediately before the redaction) does
**not** have it and will pick it up as soon as that rev is moved past it. This paragraph was wrong for two
releases while it read "the fix is unreleased": a version string cannot tell you what a tree contains, so
re-run `git tag --contains <commit>` before repeating a claim like this.

## Tests: the coverage gate covers the whole hand-written surface

`uv run pytest tests/unit -q` — 97 tests, no network, no channel, no Keycloak call. CI (and any local
check worth trusting) runs the gate the way `.github/workflows/tests.yml` does:

```bash
uv run --frozen pytest tests/unit -q --cov=ondewo.csi.client --cov-report=term-missing --cov-fail-under=100
```

**`--cov=ondewo.csi.client` is the whole policy, and it is deliberately a package, not a list of modules.**
The gate used to name four modules (`utils.keycloak`, `client_config`, `core.services_interface`,
`core.async_services_interface`) and reported a triumphant 100% while `async_client.py` sat at **0%** and
every one of the eighteen `Conversations` RPC wrappers was never executed — real coverage was 84%. A
hand-written module that nobody adds to the list is invisible to a gate built from a list. Naming the
package means a new module is covered the day it lands. This costs nothing in generated-code noise: the
`*_pb2*` stubs live in `ondewo/csi/`, one level **above** `ondewo/csi/client/`, so they are outside the
measured package automatically.

What the suite pins down, so a new test lands in the right file:

- `test_client_config.py` / `test_client_config_redacts_secrets.py` — config validation and the
  secret-redaction behaviour described above.
- `test_keycloak.py` — the token provider, its refresh loop and the credential-keyed registry.
- `test_conversations_metadata.py` — depth: a Keycloak bearer token really reaches an outgoing call.
- `test_conversations_rpcs.py` — breadth: every RPC wrapper, sync and async, forwards the right request to
  the right stub endpoint **with `metadata=`**, and returns the stub's own object (identity, not equality —
  a wrapper returning a fresh empty message would compare equal and pass a weaker assertion). Streaming RPCs
  additionally assert the iterator comes back **unconsumed**: `s2s_stream` is fed by a live generator, so a
  wrapper that materialized it would block until the caller stopped speaking.
- `test_clients.py` — `Client` / `AsyncClient` wiring, gRPC option forwarding, and that a secure channel
  without a certificate fails loudly _without_ the `ValueError` printing the password.
- `test_proto_descriptor_pool.py` — the csi/nlu/s2t/t2s coexistence guarantee.

Async tests are marked `@pytest.mark.asyncio` explicitly (pytest-asyncio runs in its default strict mode;
there is no `asyncio_mode` setting in `pyproject.toml`). Construct clients with `use_secure_channel=False`:
`grpc.insecure_channel` connects lazily, so no test touches the network.

## Bumping the ondewo client dependencies — measure, don't assume

The three sibling clients are each pinned to a **single minor** (`ondewo-nlu-client>=7.0.4,<7.1.0`,
`ondewo-s2t-client>=7.4.2,<7.5.0`, `ondewo-t2s-client>=6.6.3,<6.7.0`), so widening a bound is a decision, not
a chore. Before moving one, prove the new wheel is the same api generation instead of trusting the version
number:

```bash
# unzip both wheels, then:
diff -rq x-<old>/ondewo x-<new>/ondewo    # must be empty
```

A patch bump that is byte-identical under `ondewo/` (7.0.2 → 7.0.3 → 7.0.4 all were — the only difference
in the whole distribution was the `Version:` line and the `.dist-info` directory name) is safe: the proto
alignment the pin exists to protect is unchanged. If the trees differ at all, that justification is void.
This is also why the upper bound stops at the minor: every patch bump measured so far has been provably inert
under `ondewo/`, and no minor bump has been.

Check the sibling wheels too — `ondewo-s2t-client` and `ondewo-t2s-client` must ship only `ondewo/s2t` and
`ondewo/t2s`. The day one of them starts vendoring `ondewo/nlu`, this package gets the duplicate-file
descriptor-pool crash, and the version bump will look like the innocent party.

Then: `uv lock --upgrade-package ondewo-nlu-client --upgrade-package ...` (never a bare `uv lock --upgrade`,
which churns the entire graph), `uv sync --extra dev --frozen`, and run the gate above.

## The two commit-msg hooks must run in this order

`.pre-commit-config.yaml` lists `conventional-pre-commit` **before** `giticket`, and the order is the whole
point. pre-commit runs hooks in file order, and `giticket` rewrites the subject to
`[OND211-2418] <subject>`, which is not a valid Conventional Commit. With `giticket` first the validator is
handed the prefix the other hook just added and rejects it, so **no conforming commit message exists at
all** — one hook failing on the other hook's output. The only escapes were `--no-verify` (which also skips
ruff, ruff-format, mypy and uv-lock) or renaming the branch away from its ticket, and this repo's history
shows the result: subjects that are not Conventional Commits at all.

This repo had the wrong order until the redaction commit fixed it. So: type the plain subject
(`fix(client-config): …`), let the validator see exactly that, and let `giticket` decorate it afterwards.
Never write the `[TICKET]` prefix yourself — that yields `[OND211-2418] [OND211-2418] …`.

One cosmetic leftover: an orphaned `# Enforce Conventional Commits on the commit message.` comment sits at
the end of the file, where the hook used to be. It documents nothing now.
