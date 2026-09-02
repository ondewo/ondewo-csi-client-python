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

## Jenkins — never trigger a multibranch scan or branch indexing

**NEVER trigger a Jenkins multibranch scan or branch indexing.** Do not call a multibranch/folder job's
`build`, `scan`, or reindex endpoints, click "Scan Repository Now" / "Build Now" on a folder, run
`p4 scan`, or use any API/CLI that reindexes branches or scans the repository. A scan/reindex runs across
**every** branch, consumes CI resources, and can kick off unintended builds and deploys.

If a branch is not building — it was not discovered, or its job is marked `buildable: false` / orphaned —
**report it and stop**. Let the user or a Jenkins admin adjust branch-discovery/config or rename the branch
to the convention. Never force a build by scanning or reindexing.
