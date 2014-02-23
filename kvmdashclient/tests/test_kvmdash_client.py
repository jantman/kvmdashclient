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
 *.parsed.json - JSON representation of the return value of kvmdash_client.parse_domain_xml() for the matching XML file
 *.domain.json - JSON representation of the dict representing the given domain in kvmdash_client.get_domains() return list

"""
FIXTURE_DIR = 'kvmdashclient/tests/fixtures'

def load_fixture_json_domain(dom_name):
    """read in a test domain JSON file from fixtures/, and make it ASCII"""
    with open('%s/%s.domain.json' % (FIXTURE_DIR, dom_name), 'r') as fh:
        foo = json.load(fh, encoding='ascii')
    return foo

def load_fixture_json_parsed(dom_name):
    """read in a test parsed XML JSON file from fixtures/, and make it ASCII"""
    with open('%s/%s.parsed.json' % (FIXTURE_DIR, dom_name), 'r') as fh:
        foo = json.load(fh, encoding='ascii')
    return foo

def load_fixture_xml(dom_name):
    """read in a test XML file from fixtures/, and make it ASCII"""
    with open('%s/%s.xml' % (FIXTURE_DIR, dom_name), 'r') as fh:
        foo = fh.read()
    return foo

class mock_virDomain():
    """ class to represent a libvirt.virDomain instance"""

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
        with open('%s/%s.xml' % (FIXTURE_DIR, fname), 'r') as fh:
            s = fh.read()
        return s

    def __init__(self, name, dom_id=0, UUID='', info=(VIR_DOMAIN_SHUTOFF, 2, 2, 1, 1)):
        self._name = name
        self._ID = dom_id
        self._UUID = UUID
        self._info = info

class TestIntegration():
    """
    high-level integration tests
    """

    def test_get_domains_pre_0_9_13(self):
        """ test getting domains (kvmdash_client.get_domains()) on pre 0.9.13 libvirt """

        conn = MagicMock()
        conn.listDomainsID.return_value = [5, 6]
        conn.listDefinedDomains.return_value = ['baz.example.com']
        conn.listAllDomains.side_effect = libvirtError("api pre 0.9.13")

        def mocked_lookupByID(d_id):
            """ return the correct object for a lookupByID() call """
            if d_id == 6:
                return mock_virDomain(name='foo.example.com',
                                      dom_id=6,
                                      UUID='e7e6d19f-fcb8-6286-264c-26add934f909',
                                      info=(VIR_DOMAIN_RUNNING, 8388608, 8388608, 1, 1)
                                      )
            elif d_id == 5:
                return mock_virDomain(name='bar.example.com',
                                      dom_id=5,
                                      UUID='90492313-3b91-7a44-4241-6c0e4653fd5f',
                                      info=(VIR_DOMAIN_RUNNING, 89388608, 89388608, 8, 1)
                                      )

            else:
                raise libvirtError('virDomainLookupByID() failed')

        def mocked_lookupByName(name):
            """ return the correct object for a lookupByName() call """
            if name == 'foo.example.com':
                return mock_virDomain(name=name,
                                      dom_id=6,
                                      UUID='e7e6d19f-fcb8-6286-264c-26add934f909',
                                      info=(VIR_DOMAIN_RUNNING, 8388608, 8388608, 1, 1)
                                      )
            elif name == "bar.example.com":
                return mock_virDomain(name=name,
                                      dom_id=5,
                                      UUID='90492313-3b91-7a44-4241-6c0e4653fd5f',
                                      info=(VIR_DOMAIN_RUNNING, 89388608, 89388608, 8, 1)
                                      )
            elif name == "baz.example.com":
                return mock_virDomain(name='baz.example.com',
                                      dom_id=-1, # stopped, so ID is -1
                                      UUID='96ca7f69-2a51-f3d0-a2f7-248eeca371d0',
                                      info=(VIR_DOMAIN_SHUTOFF, 8388608, 8388608, 1, 1)
                                      )
            else:
                raise libvirtError('virDomainLookupByName() failed')

        conn.lookupByID.side_effect = mocked_lookupByID
        conn.lookupByName.side_effect = mocked_lookupByName

        expected = []
        for n in ['foo.example.com', 'bar.example.com', 'baz.example.com']:
            expected.append(load_fixture_json_domain(n))
        result = kvmdash_client.get_domains(conn)
        assert conn.listAllDomains.call_count == 1
        """
        # DEBUG - I wish pytest did deep pretty printing of diffs...
        for i in xrange(0, len(result)):
            print("###################### %s ######################" % i)
            print result[i]
            print expected[i]
            for k in result[i]:
                print("## %s:" % k)
                print(result[i][k])
                print(expected[i][k])
        """
        assert result.sort() == expected.sort()

    def test_get_domains_post_0_9_13(self):
        """ test getting domains (kvmdash_client.get_domains()) on post-0.9.13 libvirt """

        # we call conn.listAllDomains(16383), which
        # returns a list of libvirt.virDomain instances

        domain_objs = [ mock_virDomain(name='foo.example.com',
                                       dom_id=6,
                                       UUID='e7e6d19f-fcb8-6286-264c-26add934f909',
                                       info=(VIR_DOMAIN_RUNNING, 8388608, 8388608, 1, 1)
                                   ),
                        mock_virDomain(name='bar.example.com',
                                       dom_id=5,
                                       UUID='90492313-3b91-7a44-4241-6c0e4653fd5f',
                                       info=(VIR_DOMAIN_RUNNING, 89388608, 89388608, 8, 1)
                                   ),
                        mock_virDomain(name='baz.example.com',
                                       dom_id=-1, # stopped, so ID is -1
                                       UUID='96ca7f69-2a51-f3d0-a2f7-248eeca371d0',
                                       info=(VIR_DOMAIN_SHUTOFF, 8388608, 8388608, 1, 1)
                                   ),
                        ]

        conn = MagicMock()
        conn.listAllDomains.return_value = domain_objs

        expected = []
        for n in ['foo.example.com', 'bar.example.com', 'baz.example.com']:
            expected.append(load_fixture_json_domain(n))
        result = kvmdash_client.get_domains(conn)
        assert conn.listAllDomains.call_count == 1
        assert result.sort() == expected.sort()

    @pytest.mark.parametrize("dom_name", [
        'foo.example.com',
        'bar.example.com',
        'baz.example.com'
    ])
    def test_parse_domain_xml(self, dom_name):
        """
        test parsing domain xml
        """
        x = load_fixture_xml(dom_name)
        parsed = load_fixture_json_parsed(dom_name)
        res = kvmdash_client.parse_domain_xml(x)
        assert res == parsed

    def test_get_host_info(self, monkeypatch):
        """ test kvmdash_client.get_host_info() """
        conn = MagicMock()
        conn.getHostname.return_value = 'my.host.name'
        # http://libvirt.org/html/libvirt-libvirt.html#virNodeInfo
        conn.getInfo.return_value = ('', 100, '', '', '', '', '', '')
        conn.getMaxVcpus.return_value = 24

        expected = {}
        expected['maxvcpus'] = 24
        expected['memory_bytes'] = 104857600
        expected['hostname'] = 'my.host.name'

        res = kvmdash_client.get_host_info(conn)
        assert conn.getHostname.call_count == 1
        assert conn.getInfo.call_count == 1
        assert conn.getMaxVcpus.call_count == 1
        assert res == expected
