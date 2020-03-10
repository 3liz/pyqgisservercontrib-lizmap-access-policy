SHELL:=bash
# 
#  Makefile for running server in docker containers
#
COMMITID=$(shell git rev-parse --short HEAD)

FLAVOR:=ltr

REGISTRY_URL ?= 3liz
REGISTRY_PREFIX=$(REGISTRY_URL)/

SERVER_HTTP_PORT:=127.0.0.1:8888

BECOME_USER:=$(shell id -u)

ifndef LOCAL_HOME
	LOCAL_HOME=$(shell pwd)
endif

SRCDIR=$(shell realpath ../..)

SCRIPTS=./tests/docker

local:
	rm -rf $$(pwd)/.local
	mkdir -p  $$(pwd)/.local  $(LOCAL_HOME)/.cache

WORKERS:=1

ifdef PYPISERVER
PYPISERVER_SCHEME ?= https
PIP_OPTIONS="--extra-index-url=$(PYPISERVER_SCHEME)://$(PYPISERVER) --trusted-host=$(PYPISERVER) --pre"
else
$(error PYPIPSERVER is not defined)
endif

QGIS_IMAGE=$(REGISTRY_PREFIX)qgis-platform:$(FLAVOR)

test: local
	docker run --rm --name qgis-wps-test-$(FLAVOR)-$(COMMITID) $(DOCKER_BUILD_ARGS) -w /src \
		-u $(BECOME_USER) \
		-v $(SRCDIR):/src \
		-v $(LOCAL_HOME)/.cache:/.cache \
		-v $$(pwd)/.local:/.local \
		-e PIP_CACHE_DIR=/.cache \
		-e PIP_OPTIONS=$(PIP_OPTIONS) \
		-e QGSWPS_LIZMAP_POLICY=/src/tests/policy.yml \
		-e PYTEST_ADDOPTS="$(PYTEST_ADDOPTS)" \
		-e QGSWPS_CACHE_ROOTDIR=/src/tests/data \
		-e QGSWPS_PROCESSING_PROVIDERS_MODULE_PATH=/src/tests/unittests \
		-e QGSWPS_SERVER_HTTP_PROXY=yes \
		-e QGIS_OPTIONS_PATH=/src/tests/qgis \
		--entrypoint $(SCRIPTS)/run-tests.sh \
		$(QGIS_IMAGE)

run: local
	docker run --rm --name qgis-wps-test-$(FLAVOR)-$(COMMITID) $(DOCKER_BUILD_ARGS) -w /src \
		-u $(BECOME_USER) \
		-v $(SRCDIR):/src \
		-v $(LOCAL_HOME)/.cache:/.cache \
		-v $$(pwd)/.local:/.local \
		-e PIP_CACHE_DIR=/.cache \
		-e PIP_OPTIONS=$(PIP_OPTIONS) \
		-e WORKERS=$(WORKERS) \
		-e QGSWPS_LIZMAP_POLICY=/src/tests/policy.yml \
		-e PYTEST_ADDOPTS="$(PYTEST_ADDOPTS)" \
		-e QGSWPS_CACHE_ROOTDIR=/src/tests/data \
		-e QGSWPS_PROCESSING_PROVIDERS_MODULE_PATH=/src/tests/unittests \
		-e QGSWPS_SERVER_HTTP_PROXY=yes \
		-e QGIS_OPTIONS_PATH=/src/tests/qgis \
		-e QGSWPS_LOGLEVEL=DEBUG \
		--entrypoint $(SCRIPTS)/run-server.sh \
		$(QGIS_IMAGE)


