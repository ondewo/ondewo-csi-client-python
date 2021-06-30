
install:
	pip install .
	pip install -r requirements.txt

# GENERATE PYTHON FILES FROM PROTOS
ONDEWO_API_DIR=ondewo-csi-api
PROTO_OUTPUT_FOLDER= .

generate_ondewo_protos:
	for f in $$(find -L ${ONDEWO_API_DIR}/ondewo -name '*.proto'); do \
		python -m grpc_tools.protoc -I ${ONDEWO_API_DIR} -I ${ONDEWO_API_DIR}/googleapis --python_out=${PROTO_OUTPUT_FOLDER} --mypy_out=${PROTO_OUTPUT_FOLDER} --grpc_python_out=${PROTO_OUTPUT_FOLDER} $$f; \
	done

push_to_pypi: build_package upload_package clear_package_data
	echo 'pushed to pypi :)'

build_package:
	python setup.py sdist bdist_wheel

upload_package:
	twine upload -r pypi dist/*

clear_package_data:
	rm -rf build dist ondewo_logging.egg-info
