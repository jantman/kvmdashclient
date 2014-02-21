import pytest
from mock import MagicMock
from pretend import stub

import sys
import os
import simplejson as json

from libvirt import libvirtError, VIR_DOMAIN_RUNNING, VIR_DOMAIN_SHUTOFF

from kvmdashclient import kvmdash_client

"""
fixtures/:
 *.xml - domain XML exactly as returned by libvirt XMLDesc()
 *.parsed.json - JSON representation of the return value from kvmdash_client.parse_domain_xml() for the matching XML file

"""

def load_test_json(fname):
    """read in a test JSON file from fixtures/, and make it ASCII"""
    with open('kvmdashclient/tests/fixtures/%s' % fname, 'r') as fh:
        foo = json.load(fh, encoding='ascii')
    return foo

class TestIntegration():
    """
    high-level integration tests
    """

    # @TODO: this should be re-done...
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
                fname = self._name
                if str(self._name) == "3":
                    fname = 'baz.example.com'
                with open('kvmdashclient/tests/fixtures/%s.xml' % fname, 'r') as fh:
                    s = fh.read()
                return s

            def __init__(self, name):
                self._name = name
                if name == 'foo.example.com':
                    self._ID = 6
                    self._UUID = 'e7e6d19f-fcb8-6286-264c-26add934f909'
                    self._info = (VIR_DOMAIN_RUNNING, 8388608, 8388608, 1, 1)
                elif name == "bar.example.com":
                    self._ID = 5
                    self._UUID = '90492313-3b91-7a44-4241-6c0e4653fd5f'
                    self._info = (VIR_DOMAIN_RUNNING, 89388608, 89388608, 8, 1)
                elif name == 'baz.example.com':
                    self._ID = 4
                    self._UUID = '96ca7f69-2a51-f3d0-a2f7-248eeca371d0'
                    self._info = (VIR_DOMAIN_SHUTOFF, 8388608, 8388608, 1, 1)
                else:
                    self._ID = 0
                    self._UUID = ''
                    self._info = (VIR_DOMAIN_SHUTOFF, 2, 2, 1, 1)

        conn = MagicMock()
        #conn.listDomainsID.return_value = [3]
        conn.listDefinedDomains.return_value = ['foo.example.com', 'bar.example.com']
        conn.listAllDomains.side_effect = libvirtError("api pre 0.9.13")
        conn.lookupByID.side_effect = mock_domain
        conn.lookupByName.side_effect = mock_domain

        expected = []
        #for n in ['foo.example.com', 'bar.example.com', 'baz.example.com']:
        for n in ['foo.example.com', 'bar.example.com']:
            expected.append(load_test_json('%s.domain.json' % n))
        result = kvmdash_client.get_domains(conn)
        assert result == expected

    # @TODO: test all available domain XML fixtures
    def test_parse_domain_xml_bar(self):
        """
        test parsing domain xml
        """
        with open('kvmdashclient/tests/fixtures/bar.example.com.xml', 'r') as fh:
            x = fh.read()
        parsed = load_test_json('bar.example.com.parsed.json')
        res = kvmdash_client.parse_domain_xml(x)
        assert res == parsed

    def test_bool(self):
        assert kvmdash_client.bool("a") == True
        assert kvmdash_client.bool(2) == True
        assert kvmdash_client.bool({'foo': 'bar'}) == True
        assert kvmdash_client.bool(0) == False
        assert kvmdash_client.bool(False) == False
        assert kvmdash_client.bool(True) == True
