# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English
import pytest

from cyberspacy import IPDetector, URLDetector, EmailDetector

@pytest.fixture(scope='function')
def nlp():
    return English()

def test_ip_integration(nlp):
    detector = IPDetector(nlp, force_extension=True)
    nlp.add_pipe(detector, last=True)
    assert nlp.pipe_names[-1] == 'ip_detection'

def test_url_integration(nlp):
    detector = URLDetector(nlp, force_extension=True)
    nlp.add_pipe(detector, last=True)
    assert nlp.pipe_names[-1] == 'url_detection'

def test_email_integration(nlp):
    detector = EmailDetector(nlp, force_extension=True)
    nlp.add_pipe(detector, last=True)
    assert nlp.pipe_names[-1] == 'email_addr_detection'


def test_ip_detector(nlp):
    ip_detector = IPDetector(nlp, force_extension=True)
    nlp.add_pipe(ip_detector, first=True)
    doc = nlp(u'This is a sentence which contains 2.3.4.5 as an IP address')
    assert doc._.has_ipv4 == True
    assert doc[0]._.is_ipv4 == False
    assert doc[6]._.is_ipv4 == True
    assert len(doc._.ipv4) == 1
    idx, ipv4_token = doc._.ipv4[0]
    assert idx == 6
    assert ipv4_token.text == '2.3.4.5'

def test_url_detector(nlp):
    url_detector = URLDetector(nlp, force_extension=True)
    nlp.add_pipe(url_detector, first=True)
    doc = nlp(u'This is a sentence which contains https://example.com as a URL')
    assert doc._.has_url == True
    assert doc[0]._.is_url == False
    assert doc[6]._.is_url == True
    assert len(doc._.url) == 1
    idx, url_token = doc._.url[0]
    assert idx == 6
    assert url_token.text == 'https://example.com'

def test_email_detector(nlp):
    email_detector = EmailDetector(nlp, force_extension=True)
    nlp.add_pipe(email_detector, first=True)
    doc = nlp(u'This is a sentence which contains test@example.com as an email address')
    assert doc._.has_email_addr == True
    assert doc[0]._.is_email_addr == False
    assert doc[6]._.is_email_addr == True
    assert len(doc._.email_addr) == 1
    idx, url_token = doc._.email_addr[0]
    assert idx == 6
    assert url_token.text == 'test@example.com'    







