"""
    Test profiles
"""
from pyqgiswps.tests import HTTPTestCase
from pyqgiswps.executors.processingexecutor import ProcessingExecutor
from pyqgiswps.executors.processfactory import get_process_factory


class Tests(HTTPTestCase):

    def get_processes(self):
        return get_process_factory()._create_qgis_processes()

    def test_execute_return_403(self):
        """ Test map profile 
        """
        uri = ('?service=WPS&request=Execute&Identifier=pyqgiswps_test:testcopylayer&Version=1.0.0&MAP=france_parts'
                   '&DATAINPUTS=INPUT=france_parts%3BOUTPUT=france_parts_2')
        rv = self.client.get(uri, headers={ 'X-Lizmap-User-Groups': 'operator,admin' })
        assert rv.status_code == 403

    def test_getcapabilities_1(self):
        """ Test access policy
        """
        uri = ('?service=WPS&request=GetCapabilities')
        rv = self.client.get(uri, headers={ 'X-Lizmap-User-Groups': 'operator,admin' })
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
        rv = self.client.get(uri, headers={ 'X-Lizmap-User-Groups': 'operator,admin' })
        assert rv.status_code == 200

        exposed = rv.xpath_text('/wps:Capabilities'
                                  '/wps:ProcessOfferings'
                                  '/wps:Process'
                                  '/ows:Identifier')
        # Check that there is only one exposed pyqgiswps_test
        idents = [x for x in exposed.split() if x.startswith('pyqgiswps_test:')]
        assert idents == ['pyqgiswps_test:testsimplevalue']


    def test_getcapabilities_3(self):
        """ Test access policy
        """
        uri = ('?service=WPS&request=GetCapabilities&MAP=france_parts')
        rv = self.client.get(uri, headers={ 'X-Lizmap-User': 'john' })
        assert rv.status_code == 200

        exposed = rv.xpath_text('/wps:Capabilities'
                                  '/wps:ProcessOfferings'
                                  '/wps:Process'
                                  '/ows:Identifier')
        # Check that there is only one exposed pyqgiswps_test
        idents = [x for x in exposed.split() if x.startswith('pyqgiswps_test:')]
        assert idents == ['pyqgiswps_test:testcopylayer']
 

    def test_execute_return_ok(self):
        """ Test map profile 
        """
        uri = ('?service=WPS&request=Execute&Identifier=pyqgiswps_test:testcopylayer&Version=1.0.0&MAP=france_parts'
                   '&DATAINPUTS=INPUT=france_parts%3BOUTPUT=france_parts_2')
        rv = self.client.get(uri, headers={ 'X-Lizmap-User': 'john' })
        assert rv.status_code == 200


    def test_subfolder_map(self):
        """ Test access policy
        """
        uri = ('?service=WPS&request=GetCapabilities&MAP=others/france_parts')
        rv = self.client.get(uri, headers={ 'X-Lizmap-User': 'jack' })
        assert rv.status_code == 200

        exposed = rv.xpath_text('/wps:Capabilities'
                                  '/wps:ProcessOfferings'
                                  '/wps:Process'
                                  '/ows:Identifier')
        # Check that there is only one exposed pyqgiswps_test
        idents = [x for x in exposed.split() if x.startswith('pyqgiswps_test:')]
        assert idents == ['pyqgiswps_test:testcopylayer']


    def test_encoded_url(self):
        """ Test access policy
        """
        uri = ('?service=WPS&request=GetCapabilities&MAP=others%2Ffrance_parts')
        rv = self.client.get(uri, headers={ 'X-Lizmap-User': 'jack' })
        assert rv.status_code == 200

        exposed = rv.xpath_text('/wps:Capabilities'
                                  '/wps:ProcessOfferings'
                                  '/wps:Process'
                                  '/ows:Identifier')
        # Check that there is only one exposed pyqgiswps_test
        idents = [x for x in exposed.split() if x.startswith('pyqgiswps_test:')]
        assert idents == ['pyqgiswps_test:testcopylayer']

