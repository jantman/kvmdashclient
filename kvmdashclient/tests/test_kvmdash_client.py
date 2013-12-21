from kvmdashclient import kvmdash_client
import pytest

class TestIntegration():


    def test_everything(self, monkeypatch):
        """
        As a precaution before doing any major work,
        a high-level integration test
        """
        monkeypatch.setattr(sys, "argv", ["myhostname"])
        
