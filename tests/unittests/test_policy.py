"""
    Test profiles
"""
from pyqgiswps.app import WPSProcess, Service
from pyqgiswps.tests import HTTPTestCase
from pyqgiswps.executors.processingexecutor import ProcessingExecutor

class Tests(HTTPTestCase):

    def test_execute_return_403(self):
        """ Test map profile 
        """
        uri = ('?service=WPS&request=Execute&Identifier=pyqgiswps_test:testcopylayer&Version=1.0.0&MAP=france_parts'
                   '&DATAINPUTS=INPUT=france_parts%3BOUTPUT=france_parts_2')
        client = self.client_for(Service(executor=ProcessingExecutor()))
        rv = client.get(uri, headers={ 'X-Lizmap-User-Groups': 'operator,admin' })
        assert rv.status_code == 403

    def test_getcapabilities_1(self):
        """ Test access policy
        """
        uri = ('?service=WPS&request=GetCapabilities')
        client = self.client_for(Service(executor=ProcessingExecutor()))
        rv = client.get(uri, headers={ 'X-Lizmap-User-Groups': 'operator,admin' })
        assert rv.status_code == 200

        exposed = rv.xpath_text('/wps:Capabilities'
                                  '/wps:ProcessOfferings'
                                  '/wps:Process'
                                  '/ows:Identifier')
        # Test that only  scripts are exposed
        assert exposed == 'script:testalgfactory'
 
    def test_getcapabilities_2(self):
        """ Test access policy
        """
        uri = ('?service=WPS&request=GetCapabilities&MAP=france_parts')
        client = self.client_for(Service(executor=ProcessingExecutor()))
        rv = client.get(uri, headers={ 'X-Lizmap-User-Groups': 'operator,admin' })
        assert rv.status_code == 200

        exposed = rv.xpath_text('/wps:Capabilities'
                                  '/wps:ProcessOfferings'
                                  '/wps:Process'
                                  '/ows:Identifier')
        # Check that there is only one exposed pyqgiswps_test
        idents = [x for x in exposed.split() if x.startswith('pyqgiswps_test:')]
        assert idents == ['pyqgiswps_test:testsimplevalue']
       
