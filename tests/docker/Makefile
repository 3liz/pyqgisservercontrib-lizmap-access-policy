SHELL:=bash
# 
#  Makefile for running server in docker containers
#
COMMITID=$(shell git rev-parse --short HEAD)

FLAVOR:=ltr

ifdef REGISTRY_URL
	REGISTRY_PREFIX=$(REGISTRY_URL)/
endif

SERVER_HTTP_PORT:=127.0.0.1:8888

BECOME_USER:=$(shell id -u)

ifndef LOCAL_HOME
	LOCAL_HOME=$(shell pwd)
endif

SRCDIR=$(shell realpath ../..)

SCRIPTS=./tests/docker

local:
	rm -rf $$(pwd)/.local
	mkdir -p  $(LOCAL_HOME)/.cache

WORKERS:=1

QGIS_WPSIMAGE=$(REGISTRY_PREFIX)qgis-wps:$(FLAVOR)

test: local
	docker run --rm --name qgis-wps-test-$(FLAVOR)-$(COMMITID) -w /src \
		-v $(SRCDIR):/src \
		-v $(LOCAL_HOME)/.cache:/.cache \
		-e BECOME_USER=$(BECOME_USER) \
		-e PIP_CACHE_DIR=/.cache \
		-e QGSRV_LIZMAP_POLICY=/src/tests/policy.yml \
		-e PYTEST_ADDOPTS="$(PYTEST_ADDOPTS)" \
		-e QYWPS_CACHE_ROOTDIR=/src/tests/data \
		-e QYWPS_PROCESSING_PROVIDERS_MODULE_PATH=/src/tests/unittests \
		-e QYWPS_SERVER_HTTP_PROXY=yes \
		-e QGIS_OPTIONS_PATH=/src/tests/qgis \
		--entrypoint $(SCRIPTS)/run-tests.sh \
		$(QGIS_WPSIMAGE)

run: local
	docker run --rm --name qgis-wps-test-$(FLAVOR)-$(COMMITID) -w /src \
		-v $(SRCDIR):/src \
		-v $(LOCAL_HOME)/.cache:/.cache \
		-e BECOME_USER=$(BECOME_USER) \
		-e PIP_CACHE_DIR=/.cache \
		-e WORKERS=$(WORKERS) \
		-e QGSRV_LIZMAP_POLICY=/src/tests/policy.yml \
		-e PYTEST_ADDOPTS="$(PYTEST_ADDOPTS)" \
		-e QYWPS_CACHE_ROOTDIR=/src/tests/data \
		-e QYWPS_PROCESSING_PROVIDERS_MODULE_PATH=/src/tests/unittests \
		-e QYWPS_SERVER_HTTP_PROXY=yes \
		-e QGIS_OPTIONS_PATH=/src/tests/qgis \
		-e QYWPS_LOGLEVEL=DEBUG \
		--entrypoint $(SCRIPTS)/run-server.sh \
		$(QGIS_WPSIMAGE)


