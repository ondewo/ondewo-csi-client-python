# No bare `export`: the release credentials reach a process only through the environment of the
# steps that use them (see `release` and WITHOUT_CREDENTIALS), never pytest, pre-commit hooks or uv.
# ---------------- BEFORE RELEASE ----------------
# 1 - Update Version Number
# 2 - Update RELEASE.md
# 3 - make update_setup
# -------------- Release Process Steps (`make ondewo_release`) --------------
# 1 - spc: version not yet on origin or PyPI, RELEASE.md documents it (read-only)
# 2 - Load the credentials from devops-accounts and DELETE that clone before anything runs
# 3 - release_preflight: credentials valid, host tools present (read-only)
# 4 - Build, pre-commit, check_build and the full test suite
# 5 - Local commit, PyPI upload, wait until PyPI serves the version
# 6 - Push, release branch, release tag, GitHub release
# 7 - release_verify: tag on origin, non-empty GitHub release body, PyPI serves the version

########################################################
# 		Variables
########################################################

# MUST BE THE SAME AS API in Mayor and Minor Version Number
# example: API 2.9.0 --> Client 2.9.X
ONDEWO_CSI_VERSION=5.6.0
# The version as an anchored-regex fragment (dots escaped), for every heading / version match below. No line but the
# assignment above may carry an equals sign AFTER the version variable's name: older ondewo-csi-api release drivers
# rewrote every such line wholesale (tests/unit/test_release_runs_in_a_fresh_clone.py replays that rewrite).
RELEASE_VERSION_RE=$(subst .,\.,${ONDEWO_CSI_VERSION})
ONDEWO_CSI_API_GIT_BRANCH=tags/5.6.0
ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/5.15.3
PYPI_PACKAGE=ondewo-csi-client

# The credentials have NO defaults: GITHUB_GH_TOKEN (push access to this repository), PYPI_USERNAME and
# PYPI_PASSWORD come from the environment, normally loaded by `ondewo_release` from devops-accounts.
# A placeholder default would only move the failure from `release_preflight` to the middle of the release.

# Prefix of every release step that needs no credential: it runs with the credentials removed from its
# environment, so pytest, pre-commit hooks, uv and the proto-compiler containers never see them.
WITHOUT_CREDENTIALS=env -u GITHUB_GH_TOKEN -u GH_TOKEN -u PYPI_USERNAME -u PYPI_PASSWORD

# How long `verify_pypi` waits for PyPI to serve a freshly uploaded version. ondewo-csi-api's driver passes
# VERIFY_ATTEMPTS / VERIFY_INTERVAL_S.
RELEASE_VERIFY_ATTEMPTS?=$(if $(VERIFY_ATTEMPTS),$(VERIFY_ATTEMPTS),20)
RELEASE_VERIFY_INTERVAL_S?=$(if $(VERIFY_INTERVAL_S),$(VERIFY_INTERVAL_S),30)

# Shell prefix of every recipe line that hands a credential to a container. ondewo-csi-api's driver runs
# release_preflight and release_verify STANDALONE with only an absolute DEVOPS_ACCOUNT_DIR set: when a credential
# is not already in the environment, read all three from that clone into THIS line's shell environment (never an
# argv, never echoed). Inside `ondewo_release` they are already set, so nothing is read.
LOAD_CREDENTIALS=if [ -n "$${DEVOPS_ACCOUNT_DIR:-}" ] \
		&& { [ -z "$${GITHUB_GH_TOKEN:-}" ] || [ -z "$${PYPI_USERNAME:-}" ] || [ -z "$${PYPI_PASSWORD:-}" ]; }; then \
		test -d "$${DEVOPS_ACCOUNT_DIR}" || { echo "DEVOPS_ACCOUNT_DIR=$${DEVOPS_ACCOUNT_DIR} is not a directory"; exit 1; }; \
		set -a; \
		eval "$$(grep -h -E '^(GITHUB_GH_TOKEN|PYPI_USERNAME|PYPI_PASSWORD)=' \
			"$${DEVOPS_ACCOUNT_DIR}/account_github.env" "$${DEVOPS_ACCOUNT_DIR}/account_pypi.env")"; \
		set +a; \
	fi;

# The heading is the one ondewo-csi-api's release generator writes (`## Release ONDEWO CSI Python Client <v>`),
# ANCHORED at both ends with the dots escaped: unanchored, releasing 5.5.1 would also open the slice on a `5.5.10`
# heading. The slice ends on the ***** separator that delimits release entries. `\#` because a bare `#` starts a
# make comment. Keep the version reference and the `=` on SEPARATE lines: older generators rewrote, wholesale, any
# line that names ONDEWO_CSI_VERSION and also carries an equals sign.
CURRENT_RELEASE_NOTES=`cat RELEASE.md \
	| perl -ne 'print if /^\#+ Release ONDEWO CSI Python Client ${RELEASE_VERSION_RE}$$/../^\*{5}/'`

GH_REPO="https://github.com/ondewo/ondewo-csi-client-python"
GH_REPO_NAME=ondewo/ondewo-csi-client-python
DEVOPS_ACCOUNT_GIT=ondewo-devops-accounts
ONDEWO_CSI_API_DIR=ondewo-csi-api
ONDEWO_PROTO_COMPILER_DIR=ondewo-proto-compiler
GOOGLE_PROTOS_DIR=${ONDEWO_CSI_API_DIR}/google/
CSI_PROTOS_DIR=${ONDEWO_CSI_API_DIR}/ondewo/
OUTPUT_DIR=.
IMAGE_UTILS_NAME=ondewo-csi-client-utils-python:${ONDEWO_CSI_VERSION}
.DEFAULT_GOAL := help

########################################################
#       ONDEWO Standard Make Targets
########################################################

setup_developer_environment_locally: install_uv prepare_submodules install_dependencies_locally install_precommit_hooks ## Ready a fresh laptop: install uv, sync runtime+dev deps into .venv, install pre-commit hooks

install_uv: ## Install the uv package manager if it is not already available
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

install_precommit_hooks: ## Installs pre-commit hooks and sets them up for the ondewo-csi-client repo
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg

# The release runs in a FRESH clone (ondewo-csi-api's `release_client`), which has no .venv: sync it from uv.lock
# exactly as the CI workflow does, so the hooks and the tests run the locked tool versions on Python 3.12.
install_dev_environment: ## Creates/updates the project .venv from uv.lock (runtime + dev extra, Python 3.12)
	uv sync --extra dev --frozen --python 3.12

precommit_hooks_run_all_files: install_dev_environment ## Runs all pre-commit hooks on all files and not just the changed ones
	uv run --no-sync pre-commit run --all-files

# Exactly the CI workflow's checks. `release` runs this BEFORE it commits, branches, tags or publishes anything.
test: install_dev_environment ## Runs ruff, mypy and the unit suite with the coverage gate, as the CI workflow does
	uv run --no-sync ruff check .
	uv run --no-sync mypy ondewo
	uv run --no-sync pytest tests/unit -q \
		--cov=ondewo.csi.client \
		--cov-report=term-missing \
		--cov-fail-under=100

install_dependencies_locally: ## Install runtime + dev dependencies locally into the uv-managed .venv
	uv sync --extra dev

ruff: ## Lint with ruff (replaces flake8)
	uv run ruff check .

ruff_fix: ## Lint with ruff and auto-fix fixable issues
	uv run ruff check --fix .

ruff_format: ## Format the codebase with ruff (replaces black + autopep8)
	uv run ruff format .

mypy: ## Run mypy static code checking
	uv run mypy ondewo/ tests/

help: ## Print usage info about help targets
	# (first comment after target starting with double hashes ##)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

makefile_chapters: ## Shows all sections of Makefile
	@echo `cat Makefile| grep "########################################################" -A 1 | grep -v "########################################################"`

TEST:
	@echo "GH Token: \t $(if $(GITHUB_GH_TOKEN),<set>,<unset>)"
	@echo "PyPI User: \t $(if $(PYPI_USERNAME),<set>,<unset>)"
	@echo "PyPI Password: \t $(if $(PYPI_PASSWORD),<set>,<unset>)"
	@echo "\n${CURRENT_RELEASE_NOTES}"

check_build: ## Checks if all built proto-code is there
	@rm -rf build_check.txt
	@for proto in `find ondewo-csi-api/ondewo/csi -iname "*.proto*"`; \
	do \
		echo $${proto} | cut -d "/" -f 4 | cut -d "." -f 1 >> build_check.txt; \
	done
	@echo "`sort build_check.txt | uniq`" > build_check.txt
	@for file in `cat build_check.txt`;\
	do \
		find ondewo -iname "*pb*" | grep -q $${file}; \
		if test $$? != 0; then  echo "No Proto-Code for $${file}"; exit 1;fi \
	done
	@rm -rf build_check.txt

########################################################
#       Repo Specific Make Targets
########################################################
#		Build

update_setup: ## Update CSI Version in pyproject.toml
	@perl -i -pe 's/^version = "[0-9]+\.[0-9]+\.[0-9]+"/version = "${ONDEWO_CSI_VERSION}"/' pyproject.toml

build: clear_package_data prepare_submodules build_compiler generate_all_protos create_async_services update_setup ## Build source code

push_to_pypi_via_docker: build_utils_docker_image push_to_pypi_via_docker_image  ## Release automation for building and pushing to pypi via a docker image

release_to_github_via_docker: build_utils_docker_image release_to_github_via_docker_image  ## Release automation for building and releasing on GitHub via a docker image

clean_python_api:  ## Clear generated python files
	find ./ondewo -name \*pb2.py -type f -exec rm -f {} \;
	find ./ondewo -name \*pb2_grpc.py -type f -exec rm -f {} \;
	find ./ondewo -name \*.pyi -type f -exec rm -f {} \;
	rm -rf google

build_compiler:  ## Build proto compiler docker image
	make -C ondewo-proto-compiler/python build

build_utils_docker_image:  ## Build utils docker image
	docker build -f Dockerfile.utils -t ${IMAGE_UTILS_NAME} .

generate_all_protos: generate_csi_protos

generate_csi_protos:
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${CSI_PROTOS_DIR} \
		EXTRA_PROTO_DIR=${GOOGLE_PROTOS_DIR} \
		TARGET_DIR='ondewo/csi' \
		OUTPUT_DIR=${OUTPUT_DIR}
	-make precommit_hooks_run_all_files
	make precommit_hooks_run_all_files

HAND_WRITTEN_ASYNC_MARKER=ondewo:hand-written-async-service

create_async_services: ## Create async services for all synchronous services
	# The rewrite below turns every `self.stub.Rpc(...)` into `await self.stub.Rpc(...)`, which is
	# correct for a unary RPC and WRONG for a streaming one (grpc.aio returns an async ITERATOR that
	# must not be awaited). An async_*.py carrying ${HAND_WRITTEN_ASYNC_MARKER} is maintained by hand
	# and is left alone.
	@find ondewo -type d -name "services" ! -path "*/.*/*" | while read -r dir; do \
	    for file in "$$dir"/*.py; do \
	        filename=$$(basename -- "$$file"); \
	        case "$$filename" in \
	            "__init__.py"|async_*) continue ;; \
	        esac; \
	        if [ -f "$$dir/async_$$filename" ] && grep -q "${HAND_WRITTEN_ASYNC_MARKER}" "$$dir/async_$$filename"; then \
	            echo "create_async_services: keeping hand-written $$dir/async_$$filename"; \
	            continue; \
	        fi; \
	        cp "$$file" "$$dir/async_$$filename"; \
	    done; \
	    for file in "$$dir"/async_*.py; do \
	        if grep -q "${HAND_WRITTEN_ASYNC_MARKER}" "$$file"; then continue; fi; \
	        perl -i -pe 'unless(/def stub/){ s/^([[:space:]]*)def /$$1async def /g; s/self\.stub/await self.stub/g; s/\(BaseServicesInterface\)/(AsyncBaseServicesInterface)/g; s/base_services_interface/async_base_services_interface/g; s/import BaseServicesInterface/import AsyncBaseServicesInterface/g; s/core\.services_interface/core.async_services_interface/g; s/import ServicesInterface/import AsyncServicesInterface/g; s/\((?<!Async)ServicesInterface\)/(AsyncServicesInterface)/g; }' \
	            "$$file"; \
	    done; \
	done
	-make precommit_hooks_run_all_files
	make precommit_hooks_run_all_files

########################################################
#		Release

# The ORDER is the release contract shared by every ondewo-csi-client-<lang> repository, and
# tests/unit/test_release_runs_in_a_fresh_clone.py pins it: nothing is committed, published, pushed or tagged
# before the preflight and the full test suite passed, and PyPI (the one step that cannot be undone) is
# published and verified BEFORE anything reaches origin. Plain `make`, not `$(MAKE)`, so `make -n release`
# prints the steps instead of running the sub-makes.
release: ## Automate the entire release process (see README "Automatic Release Process")
	@echo "Start Release"
	make release_preflight
	${WITHOUT_CREDENTIALS} make build
	${WITHOUT_CREDENTIALS} make precommit_hooks_run_all_files
	git status
	${WITHOUT_CREDENTIALS} make check_build
	${WITHOUT_CREDENTIALS} make test
	git add ondewo
	git add Makefile
	git add RELEASE.md
	git add pyproject.toml uv.lock
	git add ${ONDEWO_PROTO_COMPILER_DIR}
	git add ${ONDEWO_CSI_API_DIR}
	git status
	git diff --cached --quiet || ${WITHOUT_CREDENTIALS} git commit --no-verify -m "PREPARING FOR RELEASE ${ONDEWO_CSI_VERSION}"
	make push_to_pypi_via_docker
	make verify_pypi
	${WITHOUT_CREDENTIALS} git push
	${WITHOUT_CREDENTIALS} make create_release_branch
	${WITHOUT_CREDENTIALS} make create_release_tag
	make release_to_github_via_docker
	make release_verify
	@echo "Release Finished"

# Read-only: nothing is committed, pushed, tagged or uploaded. It builds the local utils image, because gh and
# twine run in it. `spc` repeats here so a direct `make release` is guarded as well as `make ondewo_release`.
release_preflight: check_host_tools spc build_utils_docker_image check_github_credentials check_pypi_credentials ## Read-only: fails before the release builds, commits or pushes anything
	@echo "release_preflight: OK for ${PYPI_PACKAGE} ${ONDEWO_CSI_VERSION}"

# The host needs only these. gh and twine run in the pinned utils image (Dockerfile.utils); uv runs the
# build, the pre-commit hooks and the tests from uv.lock.
check_host_tools: ## Fails unless the tools the release runs on the host are installed
	@for tool in docker git make perl curl uv; do \
		command -v $$tool >/dev/null 2>&1 || { echo "release_preflight: '$$tool' is not installed on this host"; exit 1; }; \
	done
	@docker info >/dev/null 2>&1 || { echo "release_preflight: the docker daemon is not reachable"; exit 1; }

# Proves the token is valid AND may push here; `gh` reads it from GH_TOKEN, so nothing is stored in
# ~/.config/gh and the value is never on an argv.
check_github_credentials: ## Fails unless GITHUB_GH_TOKEN has push permission on this repository
	@$(LOAD_CREDENTIALS) \
	test -n "$${GITHUB_GH_TOKEN:-}" || { echo "release_preflight: GITHUB_GH_TOKEN is not set"; exit 1; }; \
	push=$$(GH_TOKEN="$${GITHUB_GH_TOKEN}" docker run --rm -e GH_TOKEN ${IMAGE_UTILS_NAME} \
		gh api repos/${GH_REPO_NAME} --jq .permissions.push); \
	test "$$push" = true || { echo "release_preflight: GITHUB_GH_TOKEN cannot push to ${GH_REPO_NAME} (permissions.push='$$push')"; exit 1; }
	@echo "release_preflight: GITHUB_GH_TOKEN may push to ${GH_REPO_NAME}"

# PyPI offers no read-only "whoami". The cheapest REAL probe is an upload PyPI is guaranteed to refuse to
# publish: the newest file ALREADY on PyPI, downloaded from PyPI a second earlier and sent again. PyPI checks the
# credential and the upload permission on this project FIRST and answers 403 when either fails; only then does it
# see the file exists and answer 400 "File already exists" (or 200 for a byte-identical file). So a pass proves
# the credential authenticates AND may upload to ${PYPI_PACKAGE}, and nothing new can be published.
# NOT `twine upload --skip-existing`: twine then asks the index whether the file exists and skips WITHOUT
# contacting the upload endpoint, so a bogus token passes.
check_pypi_credentials: ## Fails unless PYPI_USERNAME/PYPI_PASSWORD may upload to the PyPI project
	@$(LOAD_CREDENTIALS) \
	{ test -n "$${PYPI_USERNAME:-}" && test -n "$${PYPI_PASSWORD:-}"; } \
		|| { echo "release_preflight: PYPI_USERNAME / PYPI_PASSWORD are not set"; exit 1; }; \
	docker run --rm -e PYPI_USERNAME -e PYPI_PASSWORD -e COLUMNS=1000 ${IMAGE_UTILS_NAME} make probe_pypi_upload_permission \
		|| { echo "release_preflight: PyPI refused PYPI_USERNAME / PYPI_PASSWORD for ${PYPI_PACKAGE}"; exit 1; }
	@echo "release_preflight: PyPI accepts the credentials for ${PYPI_PACKAGE}"

# Runs INSIDE the utils image (see check_pypi_credentials). COLUMNS keeps twine's message on one line.
probe_pypi_upload_permission:
	@url=$$(curl -fsS https://pypi.org/pypi/${PYPI_PACKAGE}/json \
		| python3 -c 'import json, sys; print(next(u["url"] for u in json.load(sys.stdin)["urls"] if u["packagetype"] == "sdist"))') \
		&& mkdir -p /tmp/pypi-probe \
		&& curl -fsSL -o "/tmp/pypi-probe/$${url##*/}" "$$url" \
		&& { out=$$(TWINE_USERNAME="$${PYPI_USERNAME}" TWINE_PASSWORD="$${PYPI_PASSWORD}" \
			twine upload --non-interactive --disable-progress-bar -r pypi /tmp/pypi-probe/* 2>&1); status=$$?; \
			printf '%s\n' "$$out"; \
			test $$status -eq 0 || printf '%s' "$$out" | grep -q 'File already exists'; }

check_release_notes: ## Fails unless RELEASE.md documents ONDEWO_CSI_VERSION exactly once, with a non-empty body
	@test "$$(grep -cE '^#+ Release ONDEWO CSI Python Client ${RELEASE_VERSION_RE}$$' RELEASE.md)" = 1 \
		|| { echo "RELEASE.md must carry exactly one '## Release ONDEWO CSI Python Client ${ONDEWO_CSI_VERSION}' heading"; exit 1; }
	@test -n "$$(printf '%s\n' "${CURRENT_RELEASE_NOTES}" | perl -ne 'print unless /^#+ Release / || /^\*{5}/' | tr -d '[:space:]')" \
		|| { echo "RELEASE.md has no release notes under its ${ONDEWO_CSI_VERSION} heading"; exit 1; }
	@echo "RELEASE.md documents ${ONDEWO_CSI_VERSION}"

# Read-only, after publishing; ondewo-csi-api's driver runs it to decide whether a client is released.
release_verify: verify_tag verify_github_release verify_pypi ## Read-only: fails unless the tag, the GitHub release notes and the PyPI version all exist
	@echo "release_verify: ${PYPI_PACKAGE} ${ONDEWO_CSI_VERSION} is released"

verify_tag:
	@git ls-remote --exit-code origin "refs/tags/${ONDEWO_CSI_VERSION}" >/dev/null \
		|| { echo "release_verify: tag ${ONDEWO_CSI_VERSION} is not on origin"; exit 1; }

verify_github_release: build_utils_docker_image
	@$(LOAD_CREDENTIALS) \
	test -n "$${GITHUB_GH_TOKEN:-}" || { echo "release_verify: GITHUB_GH_TOKEN is not set"; exit 1; }; \
	body=$$(GH_TOKEN="$${GITHUB_GH_TOKEN}" docker run --rm -e GH_TOKEN ${IMAGE_UTILS_NAME} \
		gh release view "${ONDEWO_CSI_VERSION}" --repo ${GH_REPO_NAME} --json body --jq .body) \
		|| { echo "release_verify: gh cannot read the GitHub release ${ONDEWO_CSI_VERSION} (invalid GITHUB_GH_TOKEN, or no such release)"; exit 1; }; \
	test -n "$$(printf '%s' "$$body" | tr -d '[:space:]')" \
		|| { echo "release_verify: the GitHub release ${ONDEWO_CSI_VERSION} is missing or has an empty body"; exit 1; }

# The PyPI JSON API lags an upload by seconds to minutes; poll instead of failing on the first miss.
verify_pypi: ## Polls the PyPI JSON API until it serves ONDEWO_CSI_VERSION with at least one file
	@for attempt in $$(seq 1 ${RELEASE_VERIFY_ATTEMPTS}); do \
		served=$$(curl -fsS "https://pypi.org/pypi/${PYPI_PACKAGE}/${ONDEWO_CSI_VERSION}/json" 2>/dev/null \
			| perl -MJSON::PP -0777 -ne 'my $$d = decode_json($$_); print $$d->{info}{version} if @{$$d->{urls}}'); \
		if [ "$$served" = "${ONDEWO_CSI_VERSION}" ]; then echo "PyPI serves ${PYPI_PACKAGE} ${ONDEWO_CSI_VERSION}"; exit 0; fi; \
		echo "PyPI does not serve ${PYPI_PACKAGE} ${ONDEWO_CSI_VERSION} yet (attempt $$attempt/${RELEASE_VERIFY_ATTEMPTS})"; \
		sleep ${RELEASE_VERIFY_INTERVAL_S}; \
	done; \
	echo "release_verify: PyPI does not serve ${PYPI_PACKAGE} ${ONDEWO_CSI_VERSION}"; exit 1

create_release_branch: ## Create Release Branch and push it to origin
	git checkout -b "release/${ONDEWO_CSI_VERSION}"
	git push -u origin "release/${ONDEWO_CSI_VERSION}"

create_release_tag: ## Create Release Tag and push it to origin
	git tag -a ${ONDEWO_CSI_VERSION} -m "release/${ONDEWO_CSI_VERSION}"
	git push origin ${ONDEWO_CSI_VERSION}

# `--verify-tag` refuses to create a tag gh would otherwise invent; check_release_notes refuses an empty body
# (`gh release create -n ""` succeeds and publishes a release without notes).
build_gh_release: check_release_notes ## Generate Github Release with CLI (reads GH_TOKEN)
	gh release create --repo $(GH_REPO) "$(ONDEWO_CSI_VERSION)" --verify-tag -n "$(CURRENT_RELEASE_NOTES)" -t "Release ${ONDEWO_CSI_VERSION}"

########################################################
#		Submodules

prepare_submodules: init_submodules checkout_defined_submodule_versions

init_submodules:  ## Initialize submodules
	@echo "START initializing submodules ..."
	git submodule update --init --recursive
	@echo "DONE initializing submodules"

install: init_submodules
	uv sync

checkout_defined_submodule_versions:  ## Update submodule versions
	@echo "START checking out submodules ..."
	git -C ${ONDEWO_CSI_API_DIR} fetch --all
	git -C ${ONDEWO_CSI_API_DIR} checkout ${ONDEWO_CSI_API_GIT_BRANCH}
	make -C ${ONDEWO_CSI_API_DIR} build
	git -C ${ONDEWO_PROTO_COMPILER_DIR} fetch --all
	git -C ${ONDEWO_PROTO_COMPILER_DIR} checkout ${ONDEWO_PROTO_COMPILER_GIT_BRANCH}
	@echo "DONE checking out submodules"

########################################################
#		PYPI

build_package: ## Builds PYPI Package
	uv build
	chmod -R a+rw dist

# twine reads TWINE_USERNAME / TWINE_PASSWORD from the environment; `-u` / `-p` would put the
# credentials on its argv, which /proc/<pid>/cmdline shows to every user on the host.
upload_package: ## Uploads PYPI Package
	@TWINE_USERNAME="$${PYPI_USERNAME}" TWINE_PASSWORD="$${PYPI_PASSWORD}" twine upload --verbose -r pypi dist/*

clear_package_data: ## Clears PYPI Package
	echo "Waiting 5s so directory for removal is not busy anymore"
	sleep 5s
	-rm -rf build dist/* ondewo_csi_client.egg-info

push_to_pypi_via_docker_image:  ## Push source code to pypi via docker
	[ -d $(OUTPUT_DIR) ] || mkdir -p $(OUTPUT_DIR)
	@docker run --rm \
		-v ${shell pwd}/dist:/home/ondewo/dist \
		-e PYPI_USERNAME \
		-e PYPI_PASSWORD \
		${IMAGE_UTILS_NAME} make push_to_pypi
	rm -rf dist

push_to_pypi: build_package upload_package clear_package_data ## Builds -> Uploads -> Clears PYPI Package
	@echo 'YAY - Pushed to pypi : )'

show_pypi: build_package ## Shows PYPI Package with Dockerimage
	tar xvfz dist/ondewo_csi_client-${ONDEWO_CSI_VERSION}.tar.gz
	tree ondewo_csi_client-${ONDEWO_CSI_VERSION}
	cat ondewo_csi_client-${ONDEWO_CSI_VERSION}/ondewo_csi_client.egg-info/requires.txt

show_pypi_via_docker_image: build_utils_docker_image ## Push source code to pypi via docker
	[ -d $(OUTPUT_DIR) ] || mkdir -p $(OUTPUT_DIR)
	@docker run --rm \
		-v ${shell pwd}/dist:/home/ondewo/dist \
		${IMAGE_UTILS_NAME} make show_pypi
	rm -rf dist

########################################################
#		GITHUB

push_to_gh: build_gh_release ## Creates the GitHub release (gh reads GH_TOKEN; nothing is stored in ~/.config/gh)
	@echo 'Released to Github'

# "$${GITHUB_GH_TOKEN}" is expanded by the shell from the environment and handed to gh as GH_TOKEN by name.
# $(GITHUB_GH_TOKEN) would be expanded by make INTO the recipe line, i.e. onto the argv of `/bin/sh -c`.
release_to_github_via_docker_image:  ## Release to Github via docker
	@GH_TOKEN="$${GITHUB_GH_TOKEN}" docker run --rm \
		-e GH_TOKEN \
		${IMAGE_UTILS_NAME} make push_to_gh

########################################################
#		DEVOPS-ACCOUNTS

# The credentials are loaded into the ENVIRONMENT of `make release` (`make release NAME=<value>` would put every
# value on make's argv, which /proc/<pid>/cmdline shows to every user on the host), and the devops-accounts clone
# is DELETED before `make release` starts - also when the clone, the load or the release fails (trap). The clone
# lives in a mktemp directory, never in this repository, so no `docker build .` context or mount can contain it.
# DEVOPS_ACCOUNT_DIR: an existing clone to use instead (ondewo-csi-api's driver clones once for all clients and
# deletes it itself). Plain `make release`, not `$(MAKE)`, so `make -n ondewo_release` clones nothing.
ondewo_release: spc ## Release with credentials from devops-accounts repo (DEVOPS_ACCOUNT_DIR reuses a clone)
	@rm -rf ./${DEVOPS_ACCOUNT_GIT}
	@set -e; \
	owned=""; \
	trap 'if [ -n "$$owned" ]; then rm -rf "$$owned"; fi' EXIT; \
	trap 'exit 130' INT TERM; \
	if [ -n "$${DEVOPS_ACCOUNT_DIR:-}" ] && [ -d "$${DEVOPS_ACCOUNT_DIR}" ]; then \
		accounts="$${DEVOPS_ACCOUNT_DIR}"; \
	else \
		owned="$$(mktemp -d)"; \
		accounts="$$owned/${DEVOPS_ACCOUNT_GIT}"; \
		git clone -q --depth 1 git@bitbucket.org:ondewo/${DEVOPS_ACCOUNT_GIT}.git "$$accounts"; \
	fi; \
	set -a; \
	eval "$$(grep -h -E '^(GITHUB_GH_TOKEN|PYPI_USERNAME|PYPI_PASSWORD)=' \
		"$$accounts/account_github.env" "$$accounts/account_pypi.env")"; \
	set +a; \
	if [ -n "$$owned" ]; then rm -rf "$$owned"; owned=""; fi; \
	make release

# Read-only and credential-free, so `ondewo_release` runs it before it loads any credential.
spc: check_release_notes ## Checks that release/<version>, tag <version> and the PyPI version do not exist yet
	@git ls-remote --exit-code origin "refs/heads/release/${ONDEWO_CSI_VERSION}" >/dev/null; \
	status=$$?; \
	case $$status in \
		2) echo "-- Test 1: Branch is fine";; \
		0) echo "-- Test 1: branch release/${ONDEWO_CSI_VERSION} already exists on origin"; exit 1;; \
		*) echo "-- Test 1: cannot list the branches of origin (git ls-remote exit $$status)"; exit 1;; \
	esac
	@git ls-remote --exit-code origin "refs/tags/${ONDEWO_CSI_VERSION}" >/dev/null; \
	status=$$?; \
	case $$status in \
		2) echo "-- Test 2: Tag is fine";; \
		0) echo "-- Test 2: tag ${ONDEWO_CSI_VERSION} already exists on origin"; exit 1;; \
		*) echo "-- Test 2: cannot list the tags of origin (git ls-remote exit $$status)"; exit 1;; \
	esac
	@code=$$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/${PYPI_PACKAGE}/${ONDEWO_CSI_VERSION}/json"); \
	case $$code in \
		404) echo "-- Test 3: PyPI version is fine";; \
		200) echo "-- Test 3: ${PYPI_PACKAGE} ${ONDEWO_CSI_VERSION} is already on PyPI"; exit 1;; \
		*) echo "-- Test 3: cannot ask PyPI for ${PYPI_PACKAGE} ${ONDEWO_CSI_VERSION} (HTTP $$code)"; exit 1;; \
	esac

########################################################
#       Test
########################################################

test_unit: ## Run unit tests
	uv run pytest tests/unit -v
