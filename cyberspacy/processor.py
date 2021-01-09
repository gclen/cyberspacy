from spacy.lang.xx import Language

from .tokenizer import CommandLineTokenizer
from .tagger import CommandLineTagger

class WindowsCommandlineProcessor(object):
    
    def __init__(self):
        self.nlp = Language()
        self.nlp.tokenizer = CommandLineTokenizer(self.nlp.vocab)

        command_line = CommandLineTagger(self.nlp, architecture='x86_64')
        self.nlp.add_pipe(command_line, first=True)
    
    def normalize(self, cmd_line):
        """Fully normalize the command line by stemming all tokens"""
        return self.nlp(cmd_line)._.normalize

    def get_args(self, cmd_line):
        """Return arguments in the command line"""
        return [t.text for t in self.nlp(cmd_line) if t._.is_arg]
    
    def get_paths(self, cmd_line):
        """Return a list of all paths"""
        return [t.text for t in self.nlp(cmd_line) if t._.is_path]
    
    def get_normalized_paths(self, cmd_line):
        """Return a list of all paths after stemming"""
        return [t._.stem for t in self.nlp(cmd_line) if t._.is_path]

