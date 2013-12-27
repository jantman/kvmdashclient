import pytest
import sys
import os

from libvirt import libvirtError, VIR_DOMAIN_RUNNING, VIR_DOMAIN_SHUTOFF

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

            def ID(self):
                return self._ID

            def UUIDString(self):
                return self._UUID

            def info(self):
                return self._info

            def XMLDesc(self, foo):
                s = ""
                with open('kvmdashclient/tests/fixtures/%s.xml' % self._name, 'r') as fh:
                    s = fh.read()
                return s

            def __init__(self, name):
                self._name = name
                if self.name == 'foo.example.com':
                    self._ID = 6
                    self._UUID = 'e7e6d19f-fcb8-6286-264c-26add934f909'
                    self._info = (VIR_DOMAIN_RUNNING, 8388608, 8388608, 1, 1)
                elif self.name == "bar.example.com":
                    self._ID = 5
                    self._UUID = '90492313-3b91-7a44-4241-6c0e4653fd5f'
                    self._info = (VIR_DOMAIN_RUNNING, 89388608, 89388608, 8, 1)
                elif self.name == 'baz.example.com':
                    self._ID = 4
                    self._UUID = '96ca7f69-2a51-f3d0-a2f7-248eeca371d0'
                    self._info = (VIR_DOMAIN_SHUTOFF, 8388608, 8388608, 1, 1)
                else:
                    self._ID = 0
                    self._UUID = ''
                    self._info = (VIR_DOMAIN_SHUTOFF, 2, 2, 1, 1)

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
