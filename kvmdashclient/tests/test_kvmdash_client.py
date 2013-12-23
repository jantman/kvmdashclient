import pytest
import sys
import os

from libvirt import libvirtError

from kvmdashclient import kvmdash_client


class TestIntegration():
    """
    high-level integration tests
    """

    parsed_xml_foo = {'bridges': [{'mac': '00:16:3e:75:ba:ae', 'model': None}],
                      'disk_files': ['/var/lib/libvirt/images/foo.example.com-disk0'],
                      'memory_bytes': 8589934592,
                      'type': 'kvm',
                      'vcpus': 1}

    parsed_xml_bar = {'bridges': [{'mac': '52:54:00:e6:6b:60', 'model': 'virtio'}],
                      'disk_files': ['/var/lib/libvirt/images/bar.example.com-disk0'],
                      'memory_bytes': 91533934592,
                      'type': 'kvm',
                      'vcpus': 8}

    def test_everything_foo(self, monkeypatch):
        """
        As a precaution before doing any major work,
        a high-level integration test
        """
        monkeypatch.setattr(sys, "argv", ["kvmdash_client.py", "foo.example.com"])

        #monkeypatch.setattr(kvmdash_client.libvirt, "libvirtError", libvirtError)
        #def openReadOnly(foo):
        #    return "foo"
        #monkeypatch.setattr(kvmdash_client.libvirt, "openReadOnly", openReadOnly)
        # need to finish this...
        #result = kvmdash_client.main()
        assert True == True

    def test_get_domains_pre_0_9_13(self, monkeypatch):
        class mock_domain():
            def name(self):
                return self._name

            def __init__(self, name):
                self._name = name

        class mock_conn():

            def listAllDomains(self, x):
                raise libvirtError("api pre 0.9.13")

            def listDefinedDomains(self):
                return ['foo.example.com', 'bar.example.com']

            def listDomainsID(self):
                return [3]

            def lookupByID(self, ID):
                return mock_domain("baz.example.com")

            def lookupByName(self, name):
                return mock_domain(name)

        #monkeypatch.setattr(kvmdash_client.libvirt, "listAllDomains", test_listAllDoamins)
        #monkeypatch.setattr(kvmdash_client.get_domains, "listAllDomains", test_listAllDoamins)
        conn = mock_conn()
        foo = kvmdash_client.get_domains(conn)
        assert foo == None

    def test_parse_domain_xml_foo(self):
        """
        test parsing domain xml
        """
        with open('kvmdashclient/tests/fixtures/foo.example.com.xml', 'r') as fh:
            x = fh.read()
        res = kvmdash_client.parse_domain_xml(x)
        assert res == self.parsed_xml_foo

    def test_parse_domain_xml_bar(self):
        """
        test parsing domain xml
        """
        with open('kvmdashclient/tests/fixtures/bar.example.com.xml', 'r') as fh:
            x = fh.read()
        res = kvmdash_client.parse_domain_xml(x)
        assert res == self.parsed_xml_bar

    def test_bool(self):
        assert kvmdash_client.bool("a") == True
        assert kvmdash_client.bool(2) == True
        assert kvmdash_client.bool({'foo': 'bar'}) == True
        assert kvmdash_client.bool(0) == False
        assert kvmdash_client.bool(False) == False
        assert kvmdash_client.bool(True) == True
