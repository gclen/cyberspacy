# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English
import pytest

from cyberspacy import IPTagger, URLTagger, EmailTagger

@pytest.fixture(scope='function')
def nlp():
    return English()

def test_ip_integration(nlp):
    Tagger = IPTagger(nlp, force_extension=True)
    nlp.add_pipe(Tagger, last=True)
    assert nlp.pipe_names[-1] == 'ip_tagger'

def test_url_integration(nlp):
    Tagger = URLTagger(nlp, force_extension=True)
    nlp.add_pipe(Tagger, last=True)
    assert nlp.pipe_names[-1] == 'url_tagger'

def test_email_integration(nlp):
    Tagger = EmailTagger(nlp, force_extension=True)
    nlp.add_pipe(Tagger, last=True)
    assert nlp.pipe_names[-1] == 'email_addr_tagger'


def test_ip_Tagger(nlp):
    ip_Tagger = IPTagger(nlp, force_extension=True)
    nlp.add_pipe(ip_Tagger, first=True)
    doc = nlp(u'This is a sentence which contains 2.3.4.5 as an IP address')
    assert doc._.has_ipv4 == True
    assert doc[0]._.is_ipv4 == False
    assert doc[6]._.is_ipv4 == True
    assert len(doc._.ipv4) == 1
    idx, ipv4_token = doc._.ipv4[0]
    assert idx == 6
    assert ipv4_token.text == '2.3.4.5'

def test_url_Tagger(nlp):
    url_Tagger = URLTagger(nlp, force_extension=True)
    nlp.add_pipe(url_Tagger, first=True)
    doc = nlp(u'This is a sentence which contains https://example.com as a URL')
    assert doc._.has_url == True
    assert doc[0]._.is_url == False
    assert doc[6]._.is_url == True
    assert len(doc._.url) == 1
    idx, url_token = doc._.url[0]
    assert idx == 6
    assert url_token.text == 'https://example.com'
    assert url_token.lemma_ == 'example.com'

def test_email_Tagger(nlp):
    email_Tagger = EmailTagger(nlp, force_extension=True)
    nlp.add_pipe(email_Tagger, first=True)
    doc = nlp(u'This is a sentence which contains test@example.com as an email address')
    assert doc._.has_email_addr == True
    assert doc[0]._.is_email_addr == False
    assert doc[6]._.is_email_addr == True
    assert len(doc._.email_addr) == 1
    idx, url_token = doc._.email_addr[0]
    assert idx == 6
    assert url_token.text == 'test@example.com'    

def test_ip_stemming(nlp):
    ip_Tagger = IPTagger(nlp, force_extension=True, subnets_to_keep=3)
    nlp.add_pipe(ip_Tagger, first=True)
    doc = nlp(u'This is a sentence which contains 2.3.4.5 as an IP address')
    idx, ipv4_token = doc._.ipv4[0]
    assert ipv4_token.lemma_ == '2.3.4'

def test_subnet_range(nlp):
    with pytest.raises(ValueError):
        ip_Tagger = IPTagger(nlp, force_extension=True, subnets_to_keep=0)

    with pytest.raises(ValueError):
        ip_Tagger = IPTagger(nlp, force_extension=True, subnets_to_keep=5)

