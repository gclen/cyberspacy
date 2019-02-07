# coding: utf8
from __future__ import unicode_literals

import re

from spacy.tokens import Doc, Span, Token
from spacy.matcher import Matcher

from .about import __version__
from .expressions import ipv4_expr


class Cyber(object):
    """spaCy v2.0 pipeline component for adding meta data about IPs, domains and
     email addresses to `Doc` objects.
    """
    name='cyberspacy'

    def __init__(self, nlp, pattern_id='CYBER', attrs=('has_ipv4', 'is_ipv4', 'ipv4')):
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

