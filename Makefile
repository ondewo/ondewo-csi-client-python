# Fully automated build and deploy process for ondewo-t2s-client-python
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

# Choose the submodule version to build ondewo-csi-client-python
ONDEWO_CSI_API_GIT_BRANCH=tags/1.6.0
ONDEWO_NLU_API_GIT_BRANCH=tags/2.8.3
ONDEWO_S2T_API_GIT_BRANCH=tags/3.2.0
ONDEWO_T2S_API_GIT_BRANCH=tags/4.1.0
ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/2.0.0
PYPI_USERNAME=ENTER_HERE_YOUR_PYPI_USERNAME
PYPI_PASSWORD=ENTER_HERE_YOUR_PYPI_PASSWORD

# Submodule paths
ONDEWO_CSI_APIS_DIR=ondewo-csi-api
ONDEWO_S2T_APIS_DIR=ondewo-s2t-api
ONDEWO_T2S_APIS_DIR=ondewo-t2s-api
ONDEWO_NLU_APIS_DIR=ondewo-nlu-api
ONDEWO_PROTO_COMPILER_DIR=ondewo-proto-compiler
GOOGLE_APIS_DIR=${ONDEWO_NLU_APIS_DIR}/googleapis

# Specify protos directories
ONDEWO_CSI_PROTOS_DIR=${ONDEWO_CSI_APIS_DIR}/ondewo
ONDEWO_S2T_PROTOS_DIR=${ONDEWO_S2T_APIS_DIR}/ondewo
ONDEWO_T2S_PROTOS_DIR=${ONDEWO_T2S_APIS_DIR}/ondewo
ONDEWO_NLU_PROTOS_DIR=${ONDEWO_NLU_APIS_DIR}/ondewo
GOOGLE_PROTOS_DIR=${GOOGLE_APIS_DIR}/google
OUTPUT_DIR=.
EXTRA_PROTOS_DIR=${ONDEWO_CSI_APIS_DIR}/google

# Pypi release docker image environment variables
IMAGE_PYPI_NAME=ondewo-csi-client-python:latest

.PHONY: help build install

.DEFAULT_GOAL := help

# First comment after target starting with double ## specifies usage
help:  ## Print usage info about help targets
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' Makefile | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'


build_and_push_to_pypi_via_docker: build build_pypi_docker_image push_to_pypi_via_docker_image  ## Release automation for building and pushing to pypi via a docker image

build: clear_package_data init_submodules checkout_defined_submodule_versions clean_protos_from_submodules copy_proto_files_all_submodules build_compiler generate_ondewo_protos  ## build source code

build_pypi_docker_image:   ## Build pypi docker image
	docker build -f Dockerfile.pypi -t ${IMAGE_PYPI_NAME} .

push_to_pypi_via_docker_image:  ## Push source code to pypi via docker
	[ -d $(OUTPUT_DIR) ] || mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v ${shell pwd}/dist:/home/ondewo/dist \
		-e PYPI_USERNAME=${PYPI_USERNAME} \
		-e PYPI_PASSWORD=${PYPI_PASSWORD} \
		${IMAGE_PYPI_NAME} make push_to_pypi
	rm -rf dist

install:  ## Install requirements
	pip install .
	pip install -r requirements.txt

init_submodules:  ## Initialize submodules
	@echo "START initializing submodules ..."
	git submodule update --init --recursive
	@echo "DONE initializing submodules"

checkout_defined_submodule_versions:  ## Update submodule versions
	@echo "START checking out submodules ..."
	git -C ${ONDEWO_CSI_APIS_DIR} fetch --all
	git -C ${ONDEWO_CSI_APIS_DIR} checkout ${ONDEWO_CSI_API_GIT_BRANCH}
	git -C ${ONDEWO_NLU_APIS_DIR} fetch --all
	git -C ${ONDEWO_NLU_APIS_DIR} checkout ${ONDEWO_NLU_API_GIT_BRANCH}
	git -C ${ONDEWO_S2T_APIS_DIR} fetch --all
	git -C ${ONDEWO_S2T_APIS_DIR} checkout ${ONDEWO_S2T_API_GIT_BRANCH}
	git -C ${ONDEWO_T2S_APIS_DIR} fetch --all
	git -C ${ONDEWO_T2S_APIS_DIR} checkout ${ONDEWO_T2S_API_GIT_BRANCH}
	git -C ${ONDEWO_PROTO_COMPILER_DIR} fetch --all
	git -C ${ONDEWO_PROTO_COMPILER_DIR} checkout ${ONDEWO_PROTO_COMPILER_GIT_BRANCH}
	@echo "DONE checking out submodules"

clean_protos_from_submodules:  ## delete submodule protos from main api directory
	@echo "START cleaning all protos from submodules from build folder ..."
	rm -rf  ${ONDEWO_CSI_APIS_DIR}/google
	rm -rf  ${ONDEWO_CSI_APIS_DIR}/ondewo/nlu
	rm -rf  ${ONDEWO_CSI_APIS_DIR}/ondewo/s2t
	rm -rf  ${ONDEWO_CSI_APIS_DIR}/ondewo/t2s
	@echo "DONE cleaning all protos from submodules from build folder."

copy_proto_files_all_submodules: copy_proto_files_for_google_api copy_proto_files_for_ondewo_nlu_api copy_proto_files_for_ondewo_s2t_api copy_proto_files_for_ondewo_t2s_api  ## copy submodule proto files to main api directory

copy_proto_files_for_google_api:
	@echo "START copying googleapis protos from submodules to build folder ..."
	#-mkdir -p ${ONDEWO_CSI_APIS_DIR}/google
	-mkdir -p ${ONDEWO_CSI_APIS_DIR}/google/api
	-mkdir -p ${ONDEWO_CSI_APIS_DIR}/google/type
	-mkdir -p ${ONDEWO_CSI_APIS_DIR}/google/rpc
	#cp -r ${GOOGLE_PROTOS_DIR} ${ONDEWO_CSI_APIS_DIR}
	cp ${GOOGLE_PROTOS_DIR}/api/annotations.proto ${ONDEWO_CSI_APIS_DIR}/google/api/
	cp ${GOOGLE_PROTOS_DIR}/api/http.proto ${ONDEWO_CSI_APIS_DIR}/google/api/
	cp ${GOOGLE_PROTOS_DIR}/type/latlng.proto ${ONDEWO_CSI_APIS_DIR}/google/type/
	cp ${GOOGLE_PROTOS_DIR}/rpc/status.proto ${ONDEWO_CSI_APIS_DIR}/google/rpc/
	@echo "DONE copying googleapis protos from submodules to build folder."

copy_proto_files_for_ondewo_nlu_api:
	@echo "START copying ondewo-nlu protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_CSI_PROTOS_DIR}/nlu/
	#cp -r ${ONDEWO_NLU_PROTOS_DIR}/nlu/ ${ONDEWO_CSI_PROTOS_DIR}
	cp  ${ONDEWO_NLU_PROTOS_DIR}/nlu/common.proto ${ONDEWO_CSI_PROTOS_DIR}/nlu
	cp  ${ONDEWO_NLU_PROTOS_DIR}/nlu/context.proto ${ONDEWO_CSI_PROTOS_DIR}/nlu
	cp  ${ONDEWO_NLU_PROTOS_DIR}/nlu/entity_type.proto ${ONDEWO_CSI_PROTOS_DIR}/nlu
	cp  ${ONDEWO_NLU_PROTOS_DIR}/nlu/intent.proto ${ONDEWO_CSI_PROTOS_DIR}/nlu
	cp  ${ONDEWO_NLU_PROTOS_DIR}/nlu/operations.proto ${ONDEWO_CSI_PROTOS_DIR}/nlu
	cp  ${ONDEWO_NLU_PROTOS_DIR}/nlu/operation_metadata.proto ${ONDEWO_CSI_PROTOS_DIR}/nlu
	cp  ${ONDEWO_NLU_PROTOS_DIR}/nlu/session.proto ${ONDEWO_CSI_PROTOS_DIR}/nlu
	@echo "DONE copying ondewo-nlu protos from submodules to build folder."

copy_proto_files_for_ondewo_s2t_api:
	@echo "START copying ondewo-s2t protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_CSI_PROTOS_DIR}/s2t/
	#cp -r ${ONDEWO_S2T_PROTOS_DIR}/s2t/ ${ONDEWO_CSI_PROTOS_DIR}
	cp  ${ONDEWO_S2T_PROTOS_DIR}/s2t/speech-to-text.proto ${ONDEWO_CSI_PROTOS_DIR}/s2t
	@echo "DONE copying ondewo-s2t protos from submodules to build folder."

copy_proto_files_for_ondewo_t2s_api:
	@echo "START copying ondewo-t2s protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_CSI_PROTOS_DIR}/t2s/
	#cp -r ${ONDEWO_T2S_PROTOS_DIR}/t2s/ ${ONDEWO_CSI_PROTOS_DIR}
	cp ${ONDEWO_T2S_PROTOS_DIR}/t2s/text-to-speech.proto ${ONDEWO_CSI_PROTOS_DIR}/t2s
	@echo "DONE copying ondewo-t2s protos from submodules to build folder."

build_compiler:  ## Build proto compiler docker image
	make -C ondewo-proto-compiler/python build

generate_ondewo_protos:  ## Generate python code from proto files
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${ONDEWO_CSI_PROTOS_DIR} \
		EXTRA_PROTO_DIR=${EXTRA_PROTOS_DIR} \
		TARGET_DIR='ondewo' \
		OUTPUT_DIR=${OUTPUT_DIR}

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
	chmod a+rw dist -R

upload_package:
	twine upload --verbose -r pypi dist/* -u${PYPI_USERNAME} -p${PYPI_PASSWORD}

clear_package_data:  ## Clear package generation residuals
	rm -rf build dist
