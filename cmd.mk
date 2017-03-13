.DEFAULT_GOAL := help


.PHONY: pypi
pypi:
	@# Upload test pypi

	twine upload dist/*.whl -r pypi


.PHONY: venv
venv:
	@# Build wheel package

	virtualenv -p python2.7 .venv27
	/usr/local/bin/python3.6 -m venv .venv36
	.venv36/bin/pip install wheel


.PHONY: wheel
wheel:
	@# Build wheel package

	rm -rf dist
	.venv27/bin/python setup.py bdist_wheel
	.venv36/bin/python setup.py bdist_wheel


.PHONY: testpypi
testpypi: wheel
	@# Register to test pypi

	twine upload dist/*.whl -r testpypi


.PHONY: clean
clean:
	@# clean build directory

	rm -rf build dist


.PHONY: help
help:
	@# Display usage

	unmake $(MAKEFILE_LIST)
