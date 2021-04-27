
install:
	pip install .
	pip install -r requirements.txt

# GENERATE PYTHON FILES FROM PROTOS
ONDEWO_PROTOS_DIR=ondewo-csi-api/ondewo/csi
ONDEWO_APIS_DIR=ondewo-csi-api
PROTO_OUTPUT_FOLDER= .

generate_ondewo_protos:
	for f in $$(find ${ONDEWO_PROTOS_DIR} -name '*.proto'); do \
		python -m grpc_tools.protoc -I ${ONDEWO_APIS_DIR} --python_out=${PROTO_OUTPUT_FOLDER} --mypy_out=${PROTO_OUTPUT_FOLDER} --grpc_python_out=${PROTO_OUTPUT_FOLDER} $$f; \
	done

push_to_pypi: build_package upload_package clear_package_data
	echo 'pushed to pypi :)'

build_package:
	python setup.py sdist bdist_wheel

upload_package:
	twine upload -r pypi dist/*

clear_package_data:
	rm -rf build dist ondewo_logging.egg-info
