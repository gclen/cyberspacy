from spacy.lang.xx import Language

from .tokenizer import CommandLineTokenizer
from .tagger import CommandLineTagger

class WindowsCommandlineProcessor(object):
    
    def __init__(self):
        self.nlp = Language()
        self.nlp.tokenizer = CommandLineTokenizer(self.nlp.vocab)

        self.tagger = CommandLineTagger(self.nlp, architecture='x86_64')
        self.nlp.add_pipe(self.tagger, first=True)
    
    def normalize(self, cmd_line):
        """Fully normalize the command line by stemming all tokens"""
        return self.nlp(cmd_line)._.normalize

    def get_args(self, cmd_line, include_nested_commands=True):
        """Return arguments in the command line"""     
        cl_args = []
        
        for t in self.nlp(cmd_line):
            if t._.is_arg:
                cl_args.append(t.text)
            elif include_nested_commands and t._.is_cmd:
                sub_cmd = self.nlp(self.tagger._remove_quotes(t.text))
                sub_args = [st.text for st in sub_cmd if st._.is_arg]
                cl_args.extend(sub_args)
        
        return cl_args
    
    def get_paths(self, cmd_line, include_nested_commands=True):
        """Return a list of all paths"""
        paths = []
        
        for t in self.nlp(cmd_line):
            if t._.is_path:
                paths.append(t.text)
            elif include_nested_commands and t._.is_cmd:
                sub_cmd = self.nlp(self.tagger._remove_quotes(t.text))
                sub_paths = [st.text for st in sub_cmd if st._.is_path]
                paths.extend(sub_paths)
        return paths
    
    def get_normalized_paths(self, cmd_line, include_nested_commands=True):
        """Return a list of all paths after stemming"""
        paths = []
        
        for t in self.nlp(cmd_line):
            if t._.is_path:
                paths.append(t._.stem)
            elif include_nested_commands and t._.is_cmd:
                sub_cmd = self.nlp(self.tagger._remove_quotes(t.text))
                sub_paths = [st._.stem for st in sub_cmd if st._.is_path]
                paths.extend(sub_paths)
        
        return paths

