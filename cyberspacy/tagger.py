from spacy.matcher import Matcher
from spacy.tokens import Doc, Span, Token
from .stemmer import NormalizeWinPath
import re

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
        return ' '.join([t._.stem for t in tokens])