import pytest
import sys
import os

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

        class libvirtError(Exception):
            message = "libvirtError message"
            def __init__(self, value):
                self.value = value
            def __str__(self):
                return repr(self.value)
        monkeypatch.setattr(kvmdash_client.libvirt, "libvirtError", libvirtError)
        def openReadOnly(foo):
            return "foo"
        monkeypatch.setattr(kvmdash_client.libvirt, "openReadOnly", openReadOnly)
        # need to finish this...
        #result = kvmdash_client.main()

    def test_parse_domain_xml_foo(self):
        """
        test parsing domain xml
        """
        with open('kvmdashclient/tests/fixtures/foo.example.com.xml', 'r') as fh:
            x = fh.read()
        res = kvmdash_client.parse_domain_xml(x)
        assert res == self.parsed_xml_foo
        assert self.parsed_xml_foo == kvmdash_client.parse_domain_lxml(x)

    def test_parse_domain_xml_bar(self):
        """
        test parsing domain xml
        """
        with open('kvmdashclient/tests/fixtures/bar.example.com.xml', 'r') as fh:
            x = fh.read()
        res = kvmdash_client.parse_domain_xml(x)
        assert res == self.parsed_xml_bar
        assert self.parsed_xml_bar == kvmdash_client.parse_domain_lxml(x)
