import os
import sys
import logging
import pytest

from pathlib import Path

from pyqgiswps.tests import TestRuntime

def pytest_addoption(parser):
    parser.addoption("--server-debug", action='store_true', help="set debug mode")

server_debug = False

def pytest_configure(config):
    global server_debug
    server_debug = config.getoption('server_debug')


@pytest.fixture(scope='session')
def outputdir(request):
    outdir=request.config.rootdir.join('__outputdir__')
    os.makedirs(outdir.strpath, exist_ok=True)
    return outdir


@pytest.fixture(scope='session')
def data(request):
    return request.config.rootdir.join('data')


def pytest_sessionstart(session):

    if not server_debug:
        logging.basicConfig(  stream=sys.stderr, level=logging.ERROR )
        logging.disable(logging.ERROR)
    else:
        logging.basicConfig(  stream=sys.stderr, level=logging.DEBUG )

    rt = TestRuntime.instance()
    rt.start()


def pytest_sessionfinish(session, exitstatus):
    """
    """
    rt = TestRuntime.instance()
    rt.stop()



