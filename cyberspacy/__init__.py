# coding: utf8
from __future__ import unicode_literals

import re

from spacy.tokens import Doc, Span, Token
from spacy.matcher import Matcher

from .about import __version__
from .expressions import ipv4_expr, url_expr, email_expr


class IPDetector(object):
    """spaCy v2.0 pipeline component for adding IP meta data to `Doc` objects."""
    name='ip_detection'

    def __init__(self, nlp, pattern_id='IPDetector', attrs=('has_ipv4', 'is_ipv4', 'ipv4')):
        self._has_ipv4, self._is_ipv4, self._ipv4 = attrs
        self.matcher = Matcher(nlp.vocab)

        # Add IPv4 rule to matcher
        self._ipv4_re = re.compile(ipv4_expr, re.VERBOSE | re.I | re.UNICODE)
        ipv4_mask = lambda text: bool(self._ipv4_re.match(text))
        ipv4_flag = nlp.vocab.add_flag(ipv4_mask)
        self.matcher.add('IPV4', None, [{ipv4_flag: True}])
        
        # Add attributes
        Doc.set_extension(self._has_ipv4, getter=self.has_ipv4)
        Doc.set_extension(self._ipv4, getter=self.iter_ipv4)
        Span.set_extension(self._has_ipv4, getter=self.has_ipv4)
        Span.set_extension(self._ipv4, getter=self.iter_ipv4)
        Token.set_extension(self._is_ipv4, default=False)

    def __call__(self, doc):
        """Apply the pipeline component to a `Doc` object.

        doc (Doc): The `Doc` returned by the previous pipeline component.
        RETURNS (Doc): The modified `Doc` object.
        """
        matches = self.matcher(doc)
        spans = []  # keep spans here to merge them later
        for match_id, start, end in matches:
            span = doc[start : end]
            for token in span:
                token._.set(self._is_ipv4, True)
            spans.append(span)

        return doc

    def has_ipv4(self, tokens):
        return any(token._.get(self._is_ipv4) for token in tokens)

    def iter_ipv4(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_ipv4)]        


class URLDetector(object):
    """spaCy v2.0 pipeline component for adding URL meta data to `Doc` objects."""
    name='url_detection'

    def __init__(self, nlp, pattern_id='URLDetector', attrs=('has_url', 'is_url', 'url')):
        self._has_url, self._is_url, self._url = attrs
        self.matcher = Matcher(nlp.vocab)

        # Add  URL rule to matcher
        self._url_re = re.compile(url_expr, re.VERBOSE | re.I | re.UNICODE)
        url_mask = lambda text: bool(self._url_re.match(text))
        url_flag = nlp.vocab.add_flag(url_mask)
        self.matcher.add('url', None, [{url_flag: True}])
        
        # Add attributes
        Doc.set_extension(self._has_url, getter=self.has_url)
        Doc.set_extension(self._url, getter=self.iter_url)
        Span.set_extension(self._has_url, getter=self.has_url)
        Span.set_extension(self._url, getter=self.iter_url)
        Token.set_extension(self._is_url, default=False)

    def __call__(self, doc):
        """Apply the pipeline component to a `Doc` object.

        doc (Doc): The `Doc` returned by the previous pipeline component.
        RETURNS (Doc): The modified `Doc` object.
        """
        matches = self.matcher(doc)
        spans = []  # keep spans here to merge them later
        for match_id, start, end in matches:
            span = doc[start : end]
            for token in span:
                token._.set(self._is_url, True)
            spans.append(span)

        return doc

    def has_url(self, tokens):
        return any(token._.get(self._is_url) for token in tokens)

    def iter_url(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_url)]     

class EmailDetector(object):
    """spaCy v2.0 pipeline component for adding email address meta data to `Doc` objects."""
    name='email_addr_detection'

    def __init__(self, nlp, pattern_id='EmailAddrDetector', attrs=('has_email_addr', 'is_email_addr', 'email_addr')):
        self._has_email_addr, self._is_email_addr, self._email_addr = attrs
        self.matcher = Matcher(nlp.vocab)

        # Add email address rule to matcher
        self._email_addr_re = re.compile(email_expr, re.VERBOSE | re.I | re.UNICODE)
        email_addr_mask = lambda text: bool(self._email_addr_re.match(text))
        email_addr_flag = nlp.vocab.add_flag(email_addr_mask)
        self.matcher.add('email_addr', None, [{email_addr_flag: True}])
        
        # Add attributes
        Doc.set_extension(self._has_email_addr, getter=self.has_email_addr)
        Doc.set_extension(self._email_addr, getter=self.iter_email_addr)
        Span.set_extension(self._has_email_addr, getter=self.has_email_addr)
        Span.set_extension(self._email_addr, getter=self.iter_email_addr)
        Token.set_extension(self._is_email_addr, default=False)

    def __call__(self, doc):
        """Apply the pipeline component to a `Doc` object.

        doc (Doc): The `Doc` returned by the previous pipeline component.
        RETURNS (Doc): The modified `Doc` object.
        """
        matches = self.matcher(doc)
        spans = []  # keep spans here to merge them later
        for match_id, start, end in matches:
            span = doc[start : end]
            for token in span:
                token._.set(self._is_email_addr, True)
            spans.append(span)

        return doc

    def has_email_addr(self, tokens):
        return any(token._.get(self._is_email_addr) for token in tokens)

    def iter_email_addr(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_email_addr)]     


