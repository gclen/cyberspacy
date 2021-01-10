from spacy.lang.xx import Language
import pytest

from cyberspacy.tokenizer import CommandLineTokenizer
from cyberspacy.tagger import CommandLineTagger
from cyberspacy.processor import WindowsCommandlineProcessor

@pytest.fixture(scope='function')
def nlp():
    return Language()

def test_tokenizer_integration(nlp):
    tokenizer = CommandLineTokenizer(nlp.vocab)
    nlp.tokenizer = tokenizer
    assert type(nlp.tokenizer).__name__ == 'CommandLineTokenizer'

def test_cmdline_integration(nlp):
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    assert nlp.pipe_names[-1] == 'cmdline_tagger'
    
def test_cmdline_tokenizer(nlp):
    tokenizer = CommandLineTokenizer(nlp.vocab)
    nlp.tokenizer = tokenizer
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    doc = nlp(r'"C:\Program Files\MyProgram.exe" /d C:\Users\Alice\file.txt --file C:\test.py')
    doc_cmd = nlp(r'"C:\Program Files\MyProgram.exe" /d "C:\Users\Alice\file.txt --file C:\test.py"')
    doc_cmd_c = nlp(r'C:\Windows\System32\cmd.exe /c C:\Users\Alice\file.txt --f C:\test.py')
    doc_cmd_k = nlp(r'C:\Windows\System32\cmd.exe /k C:\Users\Alice\file.txt --f C:\test.py')
    assert doc._.tokens == [r'"C:\Program Files\MyProgram.exe"', r'/d', r'C:\Users\Alice\file.txt', r'--file', r'C:\test.py']
    assert doc_cmd._.tokens == [r'"C:\Program Files\MyProgram.exe"', r'/d', r'"C:\Users\Alice\file.txt --file C:\test.py"']
    assert doc_cmd_c._.tokens == [r'C:\Windows\System32\cmd.exe', r'/c', r'"C:\Users\Alice\file.txt --f C:\test.py"']
    assert doc_cmd_k._.tokens == [r'C:\Windows\System32\cmd.exe', r'/k', r'"C:\Users\Alice\file.txt --f C:\test.py"']

def test_cmdline_path(nlp):
    nlp.tokenizer = CommandLineTokenizer(nlp.vocab)
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    doc = nlp(r'"C:\Program Files\MyProgram.exe" /d "C:\Users\Alice\file.txt --file C:\test.py"')
    assert doc._.has_path == True
    assert doc[0]._.is_path == True
    assert doc[2]._.is_path == False
    idx, path = doc._.path[0]
    assert idx == 0
    assert path.text == r'"C:\Program Files\MyProgram.exe"'
    assert path._.stem == r'"?pf64\myprogram.exe"'
    
def test_cmdline_arg(nlp):
    nlp.tokenizer = CommandLineTokenizer(nlp.vocab)
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    doc = nlp(r'"C:\Program Files\MyProgram.exe" /d C:\Users\Alice\file.txt --file C:\test.py')
    assert doc._.has_arg == True
    assert doc[1]._.is_arg == True
    assert doc[3]._.is_arg == True
    idx, arg = doc._.arg[0]
    assert idx == 1
    assert arg.text == "/d"
    assert arg._.stem == "/d"

def test_cmdline_cmd(nlp):
    nlp.tokenizer = CommandLineTokenizer(nlp.vocab)
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    doc = nlp(r'"C:\Program Files\MyProgram.exe" /d "C:\Users\Alice\appdata\local\temp\file.txt --file C:\test.py"')
    assert doc._.has_cmd == True
    assert doc[2]._.is_cmd == True
    idx, cmd = doc._.cmd[0]
    assert idx == 2
    assert cmd.text == r'"C:\Users\Alice\appdata\local\temp\file.txt --file C:\test.py"'
    assert cmd._.stem == r'"C:\Users\Alice\appdata\local\temp\file.txt --file C:\test.py"'
    
def test_cmdline_val(nlp):
    nlp.tokenizer = CommandLineTokenizer(nlp.vocab)
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    doc = nlp(r'"C:\Program Files\MyProgram.exe" /d "C:\Users\Alice\file.txt --file C:\test.py" -f C:\Users\Bob\file')
    assert doc._.has_val == True
    assert doc[2]._.is_val == True
    assert doc[4]._.is_val == True
    idx, val = doc._.val[1]
    assert idx == 4
    assert val.text == r'C:\Users\Bob\file'
    assert val._.stem == r'?usr\file'

def test_cmdline_sub_cmd(nlp):
    nlp.tokenizer = CommandLineTokenizer(nlp.vocab)
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    doc = nlp(r'"C:\Program Files\MyProgram.exe" /d "C:\Users\Alice\appdata\local\temp\file.txt --file C:\test.py"')
    assert type(doc[2]._.sub_cmd).__name__ == "Doc"
    assert [t for t in doc[2]._.sub_cmd._.tokens] == [r'C:\Users\Alice\appdata\local\temp\file.txt', r'--file', r'C:\test.py']
    assert doc[2]._.sub_cmd._.stems == [r'?usrtmp\file.txt', '--file', r'?c\test.py']
    assert doc[2]._.sub_cmd[0]._.is_path == True
    assert doc[2]._.sub_cmd[1]._.is_arg == True
    assert doc[2]._.sub_cmd[2]._.is_val == True
    
def test_cmdline_stemming(nlp):
    nlp.tokenizer = CommandLineTokenizer(nlp.vocab)
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    guid = nlp(r'\?\Volume{26a21bda-a627-11d7-9931-806e6f6e6963}')
    systemdrive = nlp(r'\??\C:\test \?\C:\test  C:\test')
    systemroot = nlp(r'''C:\Windows\test''')
    usrTempPath = nlp(r'C:\Users\Alice\appdata\local\temp\test')
    usrPath = nlp(r'''C:\Users\Alice\test''')
    ProgFiles86 = nlp(r'''"C:\Program Files\test"''')
    ProgFiles64 = nlp(r'"C:\Program Files (x86)\test"')
    Sys86 = nlp(r'C:\Windows\Syswow64')
    Sys64 = nlp(r'C:\Windows\System32')
    assert guid._.stems == [r'\?\volume{guid}']
    assert systemdrive._.stems == [r'?c\test', r'?c\test', r'?c\test']
    assert systemroot._.stems == [r'?win\test']
    assert usrTempPath._.stems == [r'?usrtmp\test']
    assert usrPath._.stems == [r'?usr\test']
    assert ProgFiles86._.stems == [r'"?pf64\test"']
    assert ProgFiles64._.stems == [r'"?pf86\test"']
    assert Sys86._.stems == [r'?sys32']
    assert Sys64._.stems == [r'?sys64']
    
def test_cmd_normalization(nlp):
    nlp.tokenizer = CommandLineTokenizer(nlp.vocab)
    cmdline_tagger = CommandLineTagger(nlp)
    nlp.add_pipe(cmdline_tagger, last=True)
    doc = nlp(r'"C:\Program Files\MyProgram.exe" /d "C:\Users\Alice\appdata\local\temp\file.txt --file C:\test.py"')
    doc2 = nlp(r'"C:\Program Files\MyProgram.exe" /d C:\Users\Alice\appdata\local\temp\file.txt --file C:\test.py')
    doc3 = nlp(r'C:\Windows\System32\cmd.exe /c C:\Users\Alice\appdata\local\temp\file.txt --file C:\test.py')
    assert doc._.normalize == r'"?pf64\myprogram.exe" /d "?usrtmp\file.txt --file ?c\test.py"'
    assert doc[2]._.sub_cmd._.normalize == r'?usrtmp\file.txt --file ?c\test.py'
    assert doc2._.normalize == r'"?pf64\myprogram.exe" /d ?usrtmp\file.txt --file ?c\test.py'
    assert doc3._.normalize == r'?sys64\cmd.exe /c "?usrtmp\file.txt --file ?c\test.py"'
    assert doc3[2]._.sub_cmd._.normalize == r'?usrtmp\file.txt --file ?c\test.py'

def test_windows_commandline_processor(nlp):
    processor = WindowsCommandlineProcessor()
    cmd_line = r'"C:\Program Files\MyProgram.exe" /d C:\Users\Alice\file.txt --file C:\test.py'
    assert processor.get_args(cmd_line) == ["/d", "--file"]
    assert processor.get_paths(cmd_line) == ['"C:\\Program Files\\MyProgram.exe"', 'C:\\Users\\Alice\\file.txt', 'C:\\test.py']
    assert processor.get_normalized_paths(cmd_line) == ['"?pf64\\myprogram.exe"', '?usr\\file.txt', '?c\\test.py']
    assert processor.normalize(cmd_line) == '"?pf64\\myprogram.exe" /d ?usr\\file.txt --file ?c\\test.py'

def test_windows_commandline_processor_subcmds(nlp):
    processor = WindowsCommandlineProcessor()
    cmd_line = r'"C:\Program Files\MyProgram.exe" /d "C:\Users\Alice\appdata\local\temp\test.exe --file C:\test.py"'
    assert processor.normalize(cmd_line) == r'"?pf64\myprogram.exe" /d "?usrtmp\test.exe --file ?c\test.py"'
    assert processor.get_args(cmd_line, include_nested_commands=True) == ['/d', '--file']
    assert processor.get_args(cmd_line, include_nested_commands=False) == ['/d']
    assert processor.get_paths(cmd_line, include_nested_commands=True) == ['"C:\\Program Files\\MyProgram.exe"', 'C:\\Users\\Alice\\appdata\\local\\temp\\test.exe', 'C:\\test.py']
    assert processor.get_paths(cmd_line, include_nested_commands=False) == ['"C:\\Program Files\\MyProgram.exe"']
    assert processor.get_normalized_paths(cmd_line, include_nested_commands=True) == ['"?pf64\\myprogram.exe"', '?usrtmp\\test.exe', '?c\\test.py']
    assert processor.get_normalized_paths(cmd_line, include_nested_commands=False) == ['"?pf64\\myprogram.exe"']    

