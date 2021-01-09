import re

from spacy.matcher import Matcher
from spacy.tokens import Doc, Span, Token
from spacy.symbols import ORTH, LEMMA
from spacy.lang.xx import Language

from .expressions import ipv4_expr, url_expr, email_expr
from .stemmer import get_domain, stem_ip_addr
from .stemmer import NormalizeWinPath


class CommandLineTagger(object):
    
    name='cmdline_tagger'

    def __init__(
        self, 
        nlp=None,
        pattern_id='CommandLine',
        force_extension=False,
        architecture='x86_64',
        attrs=('has_path', 'is_path', 'path',
               'stem', 'stems',
               'has_arg', 'is_arg','arg',
               'has_val', 'is_val','val',
               'has_cmd', 'is_cmd', 'cmd',
               'sub_cmd',
               'tokens',
               'normalize')
    ):
        
        self._has_path, self._is_path, self._path,\
        self._stem, self._stems,\
        self._has_arg, self._is_arg, self._arg,\
        self._has_val, self._is_val, self._val,\
        self._has_cmd, self._is_cmd, self._cmd,\
        self._sub_cmd,\
        self._tokens,\
        self._normalize = attrs
        
        if nlp is None:
            nlp = Language()
        self.nlp = nlp
        self.matcher = Matcher(nlp.vocab)
        self.normalizer = NormalizeWinPath(architecture)

        path_re = r"""(\\\?\?\\[^ ]+|\\\?\\[^ ]+)|("(([a-zA-Z]:)|([a-zA-Z]:\\Program Files \(x86\)))([^\"\s])+(\s((\S+\\)+\S*))*"|^[a-zA-Z]?:[^ ]+)"""
        arg_re = r"""(^(\/|-|--)\S*$)"""
        cmd_re = r"""(".*")"""
        val_re = r"""^[^(\/|-|\-\-| )]+"""

        path = [{"TEXT": {"REGEX": path_re}}]
        arg = [{"TEXT": {"REGEX": arg_re}}]
        cmd = [{"TEXT": {"REGEX": cmd_re}}]
        val = [{"TEXT": {"REGEX": val_re}}]
        
        self.matcher.add('path', None, path)
        self.matcher.add('arg', None, arg)
        self.matcher.add('cmd', None, cmd)
        self.matcher.add('val', None, val)

        Doc.set_extension(self._has_path, getter=self.has_path, force=True)
        Doc.set_extension(self._path, getter=self.iter_path, force=True)
        Span.set_extension(self._has_path, getter=self.has_path, force=True)
        Span.set_extension(self._path, getter=self.iter_path, force=True)
        Token.set_extension(self._is_path, default=False, force=True)
        
        Token.set_extension(self._stem, default=None, force=True)
        Doc.set_extension(self._stems, getter=self.iter_stems, force=True)
                     
        Doc.set_extension(self._has_arg, getter=self.has_arg, force=True)
        Doc.set_extension(self._arg, getter=self.iter_arg, force=True)
        Span.set_extension(self._has_arg, getter=self.has_arg, force=True)
        Span.set_extension(self._arg, getter=self.iter_arg, force=True)
        Token.set_extension(self._is_arg, default=False, force=True)
        
        Doc.set_extension(self._has_val, getter=self.has_val, force=True)
        Doc.set_extension(self._val, getter=self.iter_val, force=True)
        Span.set_extension(self._has_val, getter=self.has_val, force=True)
        Span.set_extension(self._val, getter=self.iter_val, force=True)
        Token.set_extension(self._is_val, default=False, force=True)

        Doc.set_extension(self._has_cmd, getter=self.has_cmd, force=True)
        Doc.set_extension(self._cmd, getter=self.iter_cmd, force=True)
        Span.set_extension(self._has_cmd, getter=self.has_cmd, force=True)
        Span.set_extension(self._cmd, getter=self.iter_cmd, force=True)
        Token.set_extension(self._is_cmd, default=False, force=True)
        Token.set_extension(self._sub_cmd, default=None, force=True)
        
        Doc.set_extension(self._tokens, getter=self.iter_tokens, force=True)
        
        Doc.set_extension(self._normalize, getter=self.normalize_cmd, force=True)
        
    def __call__(self, doc):
        matches = self.matcher(doc)
        spans = []
        
        for match_id, start, end in matches:
            span = doc[start : end]

            for token in span:
                if doc.vocab.strings[match_id] == 'path':
                    token._.set(self._is_path, True)
                    token._.set(self._stem, self.normalizer.normalize_path(token.text))
                
                elif doc.vocab.strings[match_id] == 'cmd':
                    if not token._.is_path:
                        token._.set(self._is_cmd, True)
                        token._.set(self._sub_cmd, self.nlp(token.text[1:-1]))
                 
                if doc.vocab.strings[match_id] == 'arg':
                    token._.set(self._is_arg, True)
                                                      
                elif doc.vocab.strings[match_id] == 'val' and start>0:
                    token._.set(self._is_val, True)
                
                if not token._.is_path:
                    token._.set(self._stem, token.text)
                                                   
            spans.append(span)
            
        return doc
    
    def has_path(self, tokens):
        return any(token._.get(self._is_path) for token in tokens)

    def iter_path(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_path)]
    
    def has_arg(self, tokens):
        return any(token._.get(self._is_arg) for token in tokens)

    def iter_arg(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_arg)]

    def has_val(self, tokens):
        return any(token._.get(self._is_val) for token in tokens)

    def iter_val(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_val)]

    def has_cmd(self, tokens):
        return any(token._.get(self._is_cmd) for token in tokens)

    def iter_cmd(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_cmd)]
    
    def iter_tokens(self, tokens):
        return [t.text for t in tokens]
    
    def iter_stems(self, tokens):
        return [t._.stem for t in tokens]
    
    def normalize_cmd(self, tokens):
        stemmed = []

        for t in tokens:
            if t._.is_cmd:
                sub_cmd = self.nlp(self._remove_quotes(t.text))
                normalized_sub = self._add_quotes(sub_cmd._.normalize)
                stemmed.append(normalized_sub)
            else:
                stemmed.append(t._.stem)

        return ' '.join(stemmed)

    @staticmethod
    def _remove_quotes(s):
        if (s[0] == s[-1]) and s.startswith(("'", '"')):
            return s[1:-1]

    @staticmethod
    def _add_quotes(s):
        return f'"{s}"'

class IPTagger(object):
    """spaCy v2.0 pipeline component for adding IP meta data to `Doc` objects.
    
        USAGE:
        >>> import spacy
        >>> from spacy.lang.en import English
        >>> from cyberspacy import IPTagger
        >>> nlp = English()
        >>> ip_Tagger = IPTagger(nlp)
        >>> nlp.add_pipe(ip_Tagger, first=True)
        >>> doc = nlp(u'This is a sentence which contains 2.3.4.5 as an IP address')
        >>> assert doc._.has_ipv4 == True
        >>> assert doc[0]._.is_ipv4 == False
        >>> assert doc[6]._.is_ipv4 == True
        >>> assert len(doc._.ipv4) == 1
        >>> idx, ipv4_token = doc._.ipv4[0]
        >>> assert idx == 6
        >>> assert ipv4_token.text == '2.3.4.5'
    """
    name='ip_tagger'

    def __init__(self, nlp, pattern_id='IPTagger', attrs=('has_ipv4', 'is_ipv4', 'ipv4'), force_extension=False,
                 subnets_to_keep=4):
        """Initialise the pipeline component.

        nlp (Language): The shared nlp object. Used to initialise the matcher
            with the shared `Vocab`, and create `Doc` match patterns.
        pattern_id (unicode): ID of match pattern, defaults to 'IPTagger'. Can be
            changed to avoid ID clashes.
        attrs (tuple): Attributes to set on the ._ property. Defaults to
            ('has_ipv4', 'is_ipv4', 'ipv4').
        force_extension (bool): Force creation of extension objects.
        subnets_to_keep (int): Number of subnets to include in lemmatization.
        RETURNS (callable): A spaCy pipeline component.
        """
        self._has_ipv4, self._is_ipv4, self._ipv4 = attrs
        self.matcher = Matcher(nlp.vocab)
        
        if (subnets_to_keep < 1) or (subnets_to_keep > 4):
            raise ValueError('Subnets_to_keep must be in the range 1-4')
        self.subnets_to_keep = subnets_to_keep

        # Add IPv4 rule to matcher
        self._ipv4_re = re.compile(ipv4_expr, re.VERBOSE | re.I | re.UNICODE)
        ipv4_mask = lambda text: bool(self._ipv4_re.match(text))
        ipv4_flag = nlp.vocab.add_flag(ipv4_mask)
        self.matcher.add('IPV4', None, [{ipv4_flag: True}])
        
        # Add attributes
        # Need to force since extensions are global by default
        Doc.set_extension(self._has_ipv4, getter=self.has_ipv4, force=force_extension)
        Doc.set_extension(self._ipv4, getter=self.iter_ipv4, force=force_extension)
        Span.set_extension(self._has_ipv4, getter=self.has_ipv4, force=force_extension)
        Span.set_extension(self._ipv4, getter=self.iter_ipv4, force=force_extension)
        Token.set_extension(self._is_ipv4, default=False, force=force_extension)

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
                token.lemma_ = stem_ip_addr(token.text, self.subnets_to_keep)
            spans.append(span)

        return doc

    def has_ipv4(self, tokens):
        return any(token._.get(self._is_ipv4) for token in tokens)

    def iter_ipv4(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_ipv4)]        


class URLTagger(object):
    """spaCy v2.0 pipeline component for adding URL meta data to `Doc` objects.
    
        USAGE:
        >>> import spacy
        >>> from spacy.lang.en import English
        >>> from cyberspacy import URLTagger
        >>> nlp = English()
        >>> url_Tagger = URLTagger(nlp)
        >>> nlp.add_pipe(url_Tagger, first=True)
        >>> doc = nlp(u'This is a sentence which contains https://example.com as a URL')
        >>> assert doc._.has_url == True
        >>> assert doc[0]._.is_url == False
        >>> assert doc[6]._.is_url == True
        >>> assert len(doc._.url) == 1
        >>> idx, url_token = doc._.url[0]
        >>> assert idx == 6
        >>> assert url_token.text == 'https://example.com'
    """
    name='url_tagger'

    def __init__(self, nlp, pattern_id='URLTagger', attrs=('has_url', 'is_url', 'url'), force_extension=False):
        """Initialise the pipeline component.

        nlp (Language): The shared nlp object. Used to initialise the matcher
            with the shared `Vocab`, and create `Doc` match patterns.
        pattern_id (unicode): ID of match pattern, defaults to 'URLTagger'. Can be
            changed to avoid ID clashes.
        attrs (tuple): Attributes to set on the ._ property. Defaults to
            ('has_url', 'is_url', 'url').
        force_extension (bool): Force creation of extension objects.
        RETURNS (callable): A spaCy pipeline component.
        """
        self._has_url, self._is_url, self._url = attrs
        self.matcher = Matcher(nlp.vocab)

        # Add  URL rule to matcher
        self._url_re = re.compile(url_expr, re.VERBOSE | re.I | re.UNICODE)
        url_mask = lambda text: bool(self._url_re.match(text))
        url_flag = nlp.vocab.add_flag(url_mask)
        self.matcher.add('url', None, [{url_flag: True}])
        
        # Add attributes
        Doc.set_extension(self._has_url, getter=self.has_url, force=force_extension)
        Doc.set_extension(self._url, getter=self.iter_url, force=force_extension)
        Span.set_extension(self._has_url, getter=self.has_url, force=force_extension)
        Span.set_extension(self._url, getter=self.iter_url, force=force_extension)
        Token.set_extension(self._is_url, default=False, force=force_extension)

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
                token.lemma_ = get_domain(token.text)
            spans.append(span)

        return doc

    def has_url(self, tokens):
        return any(token._.get(self._is_url) for token in tokens)

    def iter_url(self, tokens):
        return [(i, t) for i, t in enumerate(tokens) if t._.get(self._is_url)]     

class EmailTagger(object):
    """spaCy v2.0 pipeline component for adding email address meta data to `Doc` objects.
    
        USAGE:
        >>> import spacy
        >>> from spacy.lang.en import English
        >>> from cyberspacy import EmailTagger
        >>> nlp = English()
        >>> email_Tagger = EmailTagger(nlp)
        >>> nlp.add_pipe(email_Tagger, first=True)
        >>> doc = nlp(u'This is a sentence which contains test@example.com as an email address')
        >>> assert doc._.has_email_addr == True
        >>> assert doc[0]._.is_email_addr == False
        >>> assert doc[6]._.is_email_addr == True
        >>> assert len(doc._.email_addr) == 1
        >>> idx, url_token = doc._.email_addr[0]
        >>> assert idx == 6
        >>> assert url_token.text == 'test@example.com'
    """
    name='email_addr_tagger'

    def __init__(self, nlp, pattern_id='EmailAddrTagger', attrs=('has_email_addr', 'is_email_addr', 'email_addr'), force_extension=False):
        """Initialise the pipeline component.

        nlp (Language): The shared nlp object. Used to initialise the matcher
            with the shared `Vocab`, and create `Doc` match patterns.
        pattern_id (unicode): ID of match pattern, defaults to 'EmailAddrTagger'. Can be
            changed to avoid ID clashes.
        attrs (tuple): Attributes to set on the ._ property. Defaults to
            ('has_email_addr', 'is_email_addr', 'email_addr').
        force_extension (bool): Force creation of extension objects.
        RETURNS (callable): A spaCy pipeline component.
        """
        self._has_email_addr, self._is_email_addr, self._email_addr = attrs
        self.matcher = Matcher(nlp.vocab)

        # Add email address rule to matcher
        self._email_addr_re = re.compile(email_expr, re.VERBOSE | re.I | re.UNICODE)
        email_addr_mask = lambda text: bool(self._email_addr_re.match(text))
        email_addr_flag = nlp.vocab.add_flag(email_addr_mask)
        self.matcher.add('email_addr', None, [{email_addr_flag: True}])
        
        # Add attributes
        Doc.set_extension(self._has_email_addr, getter=self.has_email_addr, force=force_extension)
        Doc.set_extension(self._email_addr, getter=self.iter_email_addr, force=force_extension)
        Span.set_extension(self._has_email_addr, getter=self.has_email_addr, force=force_extension)
        Span.set_extension(self._email_addr, getter=self.iter_email_addr, force=force_extension)
        Token.set_extension(self._is_email_addr, default=False, force=force_extension)

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

