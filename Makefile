# Fully automated build and deploy process for ondewo-csi-client-python
#
# Release Process Steps:
# 1 - Create Release Branch and push
# 2 - Create Release Tag and push
# 3 - GitHub Release
# 4 - PyPI Release

include ./envs/versions.env
export
export GH_TOKEN=

CURRENT_RELEASE_NOTES=`cat RELEASE.md \
	| sed -n '/Release ONDEWO CSI Python Client ${ONDEWO_CSI_VERSION}/,/\*\*/p'`

# Github repo to release to:
GH_REPO="https://github.com/ondewo/ondewo-csi-client-python"

# Utils release docker image environment variables
IMAGE_UTILS_NAME=ondewo-csi-client-utils-python:${ONDEWO_CSI_VERSION}

# BEFORE "release"
update_setup: ## Update CSI Version in setup.py
	@sed -i "s/version='[0-9]*.[0-9]*.[0-9]*'/version='${ONDEWO_CSI_VERSION}'/g" setup.py

release: ## Automate the entire release process
	@echo "Release Automation started"
	create_release_branch
	create_release_tag
	build_and_release_to_github_via_docker
	build_and_push_to_pypi_via_docker
	@echo "Release Finished"

create_release_branch: ## Create Release Branch and push it to origin
	git checkout -b "release/${ONDEWO_CSI_VERSION}"
	git push -u origin "release/${ONDEWO_CSI_VERSION}"

create_release_tag: ## Create Release Tag and push it to origin
	git tag -a ${ONDEWO_CSI_VERSION} -m "release/${ONDEWO_CSI_VERSION}"
	git push origin ${ONDEWO_CSI_VERSION}

build_and_push_to_pypi_via_docker: build build_utils_docker_image push_to_pypi_via_docker_image  ## Release automation for building and pushing to pypi via a docker image

build_and_release_to_github_via_docker: build build_utils_docker_image release_to_github_via_docker_image  ## Release automation for building and releasing on GitHub via a docker image

login_to_gh: ## Login to Github CLI with Access Token
	echo $(GITHUB_GH_TOKEN) | gh auth login -p ssh --with-token

build_gh_release: ## Generate Github Release with CLI
	gh release create --repo $(GH_REPO) "$(ONDEWO_CSI_VERSION)" -n "$(CURRENT_RELEASE_NOTES)" -t "Release ${ONDEWO_CSI_VERSION}"

build: clear_package_data generate_ondewo_protos  ## Build source code

install:
	pip install .
	pip install -r requirements.txt

# GENERATE PYTHON FILES FROM PROTOS
ONDEWO_API_DIR=ondewo-csi-api
PROTO_OUTPUT_FOLDER= .

generate_ondewo_protos:
	for f in $$(find ${ONDEWO_API_DIR}/ondewo/csi -name '*.proto'); do \
		python -m grpc_tools.protoc -I ${ONDEWO_API_DIR} -I ${ONDEWO_API_DIR}/googleapis --python_out=${PROTO_OUTPUT_FOLDER} --mypy_out=${PROTO_OUTPUT_FOLDER} --grpc_python_out=${PROTO_OUTPUT_FOLDER} $$f; \
	done

build_utils_docker_image:  ## Build utils docker image
	docker build -f Dockerfile.utils -t ${IMAGE_UTILS_NAME} .

OUTPUT_DIR=.
push_to_pypi_via_docker_image:  ## Push source code to pypi via docker
	[ -d $(OUTPUT_DIR) ] || mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v ${shell pwd}/dist:/home/ondewo/dist \
		-e PYPI_USERNAME=${PYPI_USERNAME} \
		-e PYPI_PASSWORD=${PYPI_PASSWORD} \
		${IMAGE_UTILS_NAME} make push_to_pypi
	rm -rf dist

push_to_pypi: build_package upload_package clear_package_data
	echo 'YAY - pushed to pypi :)'

push_to_gh: login_to_gh build_gh_release
	@echo 'Released to Github'

release_to_github_via_docker_image:  ## Release to Github via docker
	docker run --rm \
		${IMAGE_UTILS_NAME} make push_to_gh

build_package:
	python setup.py sdist bdist_wheel

upload_package:
	twine upload -r pypi dist/*

clear_package_data:
	rm -rf build dist ondewo_logging.egg-info
