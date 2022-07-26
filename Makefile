export

# PR BEFORE RELEASE
# 1 - Update Version Number
# 2 - Update RELEASE.md
# 3 - make update_setup
#
# Fully automated build and deploy process for ondewo-nlu-client-python
# Release Process Steps:
# 1 - Create Release Branch and push
# 2 - Create Release Tag and push
# 3 - GitHub Release
# 4 - PyPI Release

# MUST BE THE SAME AS API in Mayor and Minor Version Number
# example: API 2.9.0 --> Client 2.9.X
ONDEWO_CSI_VERSION=2.9.0

# Choose the submodule version to build ondewo-nlu-client-python
PYPI_USERNAME?=ENTER_HERE_YOUR_PYPI_USERNAME
PYPI_PASSWORD?=ENTER_HERE_YOUR_PYPI_PASSWORD

# You need to setup an access token at https://github.com/settings/tokens - permissions are important
GITHUB_GH_TOKEN?=ENTER_YOUR_TOKEN_HERE

CURRENT_RELEASE_NOTES=`cat RELEASE.md \
	| sed -n '/Release ONDEWO CSI Python Client ${ONDEWO_CSI_VERSION}/,/\*\*/p'`


# Choose repo to release to - Example: "https://github.com/ondewo/ondewo-nlu-client-python"
GH_REPO="https://github.com/ondewo/ondewo-csi-client-python"

ONDEWO_CSI_API_GIT_BRANCH=release/2.0.0
ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/2.0.0

# Submodule paths
ONDEWO_NLU_API_DIR=ondewo-nlu-api
ONDEWO_CSI_API_DIR=ondewo-csi-api
ONDEWO_PROTO_COMPILER_DIR=ondewo-proto-compiler
ONDEWO_S2T_API_DIR=ondewo-s2t-api
ONDEWO_T2S_API_DIR=ondewo-t2s-api
ONDEWO_SIP_API_DIR=ondewo-sip-api
ONDEWO_VTSI_API_DIR=ondewo-vtsi-api


# Specify protos directories
GOOGLE_API_DIR=${ONDEWO_NLU_API_DIR}/googleapis
NLU_PROTOS_DIR=${ONDEWO_NLU_API_DIR}/ondewo/
GOOGLE_PROTOS_DIR=${GOOGLE_API_DIR}/google/
S2T_PROTOS_DIR=${ONDEWO_S2T_API_DIR}/ondewo/
T2S_PROTOS_DIR=${ONDEWO_T2S_API_DIR}/ondewo/
SIP_PROTOS_DIR=${ONDEWO_SIP_API_DIR}/ondewo/
VTSI_PROTOS_DIR=${ONDEWO_VTSI_API_DIR}/ondewo/

# Utils release docker image environment variables
IMAGE_UTILS_NAME=ondewo-nlu-client-utils-python:${ONDEWO_NLU_VERSION}

.DEFAULT_GOAL := help

# First comment after target starting with double ## specifies usage
help:  ## Print usage info about help targets
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' Makefile | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

# BEFORE "release"
update_setup: ## Update NLU Version in setup.py
	@sed -i "s/version='[0-9]*.[0-9]*.[0-9]*'/version='${ONDEWO_NLU_VERSION}'/g" setup.py
	@sed -i "s/version=\"[0-9]*.[0-9]*.[0-9]*\"/version='${ONDEWO_NLU_VERSION}'/g" setup.py


release: create_release_branch create_release_tag build_and_release_to_github_via_docker build_and_push_to_pypi_via_docker ## Automate the entire release process
	@echo "Release Finished"

create_release_branch: ## Create Release Branch and push it to origin
	git checkout -b "release/${ONDEWO_NLU_VERSION}"
	git push -u origin "release/${ONDEWO_NLU_VERSION}"

create_release_tag: ## Create Release Tag and push it to origin
	git tag -a ${ONDEWO_NLU_VERSION} -m "release/${ONDEWO_NLU_VERSION}"
	git push origin ${ONDEWO_NLU_VERSION}

build_and_push_to_pypi_via_docker: push_to_pypi_via_docker_image  ## Release automation for building and pushing to pypi via a docker image

build_and_release_to_github_via_docker: build build_utils_docker_image release_to_github_via_docker_image  ## Release automation for building and releasing on GitHub via a docker image


build: clear_package_data prepate_submodules build_compiler generate_all_protos update_setup ## Build source code

prepate_submodules: init_submodules checkout_defined_submodule_versions

init_submodules:
	git submodule update --init --recursive

install: init_submodules
	pip install -e .

checkout_defined_submodule_versions:
	@echo "START checking out submodules ..."
	git -C ${ONDEWO_CSI_API_DIR} fetch --all
	git -C ${ONDEWO_CSI_API_DIR} checkout ${ONDEWO_CSI_API_GIT_BRANCH}
	cd ${ONDEWO_CSI_API_DIR}
	make -C ${ONDEWO_CSI_API_DIR} build
	cd ..
	@echo "DONE checking out submodules"

build_compiler:
	make -C ondewo-proto-compiler/python build

clean_python_api:  ## Clear generated python files
	find ./ondewo -name \*pb2.py -type f -exec rm -f {} \;
	find ./ondewo -name \*pb2_grpc.py -type f -exec rm -f {} \;
	find ./ondewo -name \*.pyi -type f -exec rm -f {} \;
	rm -rf google

# {{{ PROTOS
generate_all_protos: generate_nlu_protos generate_s2t_protos generate_t2s_protos generate_sip_protos generate_vtsi_protos

generate_nlu_protos:
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${NLU_PROTOS_DIR} \
		EXTRA_PROTO_DIR=${GOOGLE_PROTOS_DIR} \
		TARGET_DIR='ondewo' \
		OUTPUT_DIR='.'

generate_s2t_protos:
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${S2T_PROTOS_DIR} \
		TARGET_DIR='ondewo' \
		OUTPUT_DIR='.'

generate_t2s_protos:
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${T2S_PROTOS_DIR} \
		TARGET_DIR='ondewo' \
		OUTPUT_DIR='.'

generate_sip_protos:
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${SIP_PROTOS_DIR} \
		TARGET_DIR='ondewo' \
		OUTPUT_DIR='.'

generate_vtsi_protos:
	make -f ondewo-proto-compiler/python/Makefile run \
		PROTO_DIR=${VTSI_PROTOS_DIR} \
		EXTRA_PROTO_DIR=${GOOGLE_PROTOS_DIR} \
		TARGET_DIR='ondewo' \
		OUTPUT_DIR='.'
# }}}

#VTSI proto Preparation{{{

copy_proto_files_all_submodules: copy_proto_files_for_google_api copy_proto_files_for_ondewo_nlu_api copy_proto_files_for_ondewo_s2t_api copy_proto_files_for_ondewo_t2s_api copy_proto_files_for_ondewo_sip_api

copy_proto_files_for_google_api:
	@echo "START copying googleapis protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/google/api
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/google/longrunning
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/google/rpc
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/google/type
	cp ${GOOGLE_PROTOS_DIR}/api/annotations.proto ${ONDEWO_VTSI_API_DIR}/google/api/
	cp ${GOOGLE_PROTOS_DIR}/api/http.proto ${ONDEWO_VTSI_API_DIR}/google/api/
	cp ${GOOGLE_PROTOS_DIR}/type/latlng.proto ${ONDEWO_VTSI_API_DIR}/google/type/
	cp ${GOOGLE_PROTOS_DIR}/rpc/status.proto ${ONDEWO_VTSI_API_DIR}/google/rpc/
	cp ${GOOGLE_PROTOS_DIR}/longrunning/operations.proto ${ONDEWO_VTSI_API_DIR}/google/longrunning/
	@echo "DONE copying googleapis protos from submodules to build folder."

copy_proto_files_for_ondewo_nlu_api:
	@echo "START copying ondewo-nlu protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/ondewo/nlu/
	cp ${NLU_PROTOS_DIR}/nlu/context.proto ${ONDEWO_VTSI_API_DIR}/ondewo/nlu/
	@echo "DONE copying ondewo-nlu protos from submodules to build folder."

copy_proto_files_for_ondewo_s2t_api:
	@echo "START copying ondewo-s2t protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/ondewo/s2t/
	cp ${S2T_PROTOS_DIR}/s2t/speech-to-text.proto ${ONDEWO_VTSI_API_DIR}/ondewo/s2t/
	@echo "DONE copying ondewo-s2t protos from submodules to build folder."

copy_proto_files_for_ondewo_t2s_api:
	@echo "START copying ondewo-t2s protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/ondewo/t2s/
	cp ${T2S_PROTOS_DIR}/t2s/text-to-speech.proto ${ONDEWO_VTSI_API_DIR}/ondewo/t2s/
	@echo "DONE copying ondewo-t2s protos from submodules to build folder."

copy_proto_files_for_ondewo_sip_api:
	@echo "START copying ondewo-sip protos from submodules to build folder ..."
	-mkdir -p ${ONDEWO_VTSI_API_DIR}/ondewo/sip/
	cp ${SIP_PROTOS_DIR}/sip/sip.proto ${ONDEWO_VTSI_API_DIR}/ondewo/sip/
	@echo "DONE copying ondewo-sip protos from submodules to build folder."
#}}}

build_utils_docker_image:  ## Build utils docker image
	docker build -f Dockerfile.utils -t ${IMAGE_UTILS_NAME} .

push_to_pypi_via_docker_image:  ## Push source code to pypi via docker
	[ -d $(OUTPUT_DIR) ] || mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v ${shell pwd}/dist:/home/ondewo/dist \
		-e PYPI_USERNAME=${PYPI_USERNAME} \
		-e PYPI_PASSWORD=${PYPI_PASSWORD} \
		${IMAGE_UTILS_NAME} make push_to_pypi
	rm -rf dist

push_to_pypi: build_package upload_package clear_package_data
	@echo 'YAY - Pushed to pypi : )'

push_to_gh: login_to_gh build_gh_release
	@echo 'Released to Github'

release_to_github_via_docker_image:  ## Release to Github via docker
	docker run --rm \
		-e GITHUB_GH_TOKEN=${GITHUB_GH_TOKEN} \
		${IMAGE_UTILS_NAME} make push_to_gh

build_package:
	python setup.py sdist bdist_wheel
	chmod a+rw dist -R

upload_package:
	twine upload --verbose -r pypi dist/* -u${PYPI_USERNAME} -p${PYPI_PASSWORD}

clear_package_data:
	rm -rf build dist/* ondewo_vtsi_client.egg-info

ondewo_release: spc clone_devops_accounts run_release_with_devops ## Release with credentials from devops-accounts repo
	@rm -rf ${DEVOPS_ACCOUNT_GIT}

clone_devops_accounts: ## Clones devops-accounts repo
	if [ -d $(DEVOPS_ACCOUNT_GIT) ]; then rm -Rf $(DEVOPS_ACCOUNT_GIT); fi
	git clone git@bitbucket.org:ondewo/${DEVOPS_ACCOUNT_GIT}.git

DEVOPS_ACCOUNT_GIT="ondewo-devops-accounts"
DEVOPS_ACCOUNT_DIR="./${DEVOPS_ACCOUNT_GIT}"

TEST:
	@echo ${GITHUB_GH_TOKEN}
	@echo ${PYPI_USERNAME}
	@echo ${PYPI_PASSWORD}
	@echo ${CURRENT_RELEASE_NOTES}

run_release_with_devops:
	$(eval info:= $(shell cat ${DEVOPS_ACCOUNT_DIR}/account_github.env | grep GITHUB_GH & cat ${DEVOPS_ACCOUNT_DIR}/account_pypi.env | grep PYPI_USERNAME & cat ${DEVOPS_ACCOUNT_DIR}/account_pypi.env | grep PYPI_PASSWORD))
	make release $(info)

spc: ## Checks if the Release Branch, Tag and Pypi version already exist
	$(eval filtered_branches:= $(shell git branch --all | grep "release/${ONDEWO_NLU_VERSION}"))
	$(eval filtered_tags:= $(shell git tag --list | grep "${ONDEWO_NLU_VERSION}"))
	$(eval setuppy_version:= $(shell cat setup.py | grep "version"))
	@if test "$(filtered_branches)" != ""; then echo "-- Test 1: Branch exists!!" & exit 1; else echo "-- Test 1: Branch is fine";fi
	@if test "$(filtered_tags)" != ""; then echo "-- Test 2: Tag exists!!" & exit 1; else echo "-- Test 2: Tag is fine";fi
	@if test "$(setuppy_version)" != "version='${ONDEWO_NLU_VERSION}',"; then echo "-- Test 3: Setup.py not updated!!" & exit 1; else echo "-- Test 3: Setup.py is fine";fi
