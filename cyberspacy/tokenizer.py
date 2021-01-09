import spacy
from spacy.tokens import Doc
import re

class CommandLineTokenizer(object):
    
    def __init__(self, vocab):
        self.vocab = vocab
        
    def cmdline_split(self, s):

        RE_CMD_LEX = r'''((?<!\S)"[^"]+|(?<!\S)'[^']+)|(?<=\S)("|')|(\\\\(?=\\*")|\\")|(&&?|\|\|?|\d?>|[<])|([^\s"&|<>]+)|(\s+)|(.)'''

        args = []
        accu = ''   # collects pieces of one arg
        q = 0
        
        cmd_ck =  r'''(.*cmd\.exe|.*cmd\.EXE)\s(\/c|\/k|\-c|\-k)\s(.*$)'''
        # cmd.exe [/c command] and [/k command]
        
        if re.match(cmd_ck, s):
            args = list(re.findall(cmd_ck, s)[0])
            if not re.match(r'^".*"$', args[-1]):
                args[-1] = f'"{args[-1]}"'
            return args
                  
        for rqs, lqs, esc, pipe, word, white, fail in re.findall(RE_CMD_LEX, s):
            if word:
                pass   # most frequent
            elif esc:
                word = esc[1]
            elif white or pipe:
                if q == 0:
                    if accu:
                        args.append(accu)
                    if pipe:
                        args.append(pipe)
                    accu = ''
                    continue
                else:
                    if white:
                        word=white
                    if pipe:
                        word=pipe
            elif fail:
                raise ValueError("invalid or incomplete shell string")
            elif rqs:
                q+=1
                if q > 1:
                    word = rqs
                else:
                    word = rqs
            elif lqs:
                q-=1
                if q == 0:
                    args.append(accu+lqs)
                    accu = ''
                else:
                    word=lqs
            else:
                word = rqs   # may be even empty; must be last

            accu += word

        if accu:
            args.append(accu)               
    
        return args
    
    def __call__(self, text):
        words = self.cmdline_split(text)
        spaces = [True] * len(words)                   
        return Doc(self.vocab, words=words, spaces=spaces)