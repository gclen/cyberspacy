import re
from urllib.parse import urlparse

def stem_ip_addr(ip_addr, subnets_to_keep):
    """Return the first N subnets of the IP address"""    
    split = ip_addr.split('.')
    return '.'.join(split[:subnets_to_keep])

def get_domain(token):
    """Extract the domain from a URL by removing the path"""
    parsed = urlparse(token)

    if parsed.netloc:
        return parsed.netloc
    else:
        # Return everything up until the first /
        slash_idx = parsed.path.find('/')
        if slash_idx == -1:
            return parsed.path
        else:
            return parsed.path[:slash_idx]
 
class NormalizeWinPath(object):
 
    settings = {
        'guid': '[{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?',
        'systemdrive': r'(\\\?\?\\|\\\?\\)?c:\\',
        'systemroot': r'(\\\?\?\\|\\\?\\)?c:\\windows\\',
        'usrTempPath': 'users\\\\[^\\\\]+\\\\appdata\\\\local\\\\temp\\\\',
        'usrPath': 'users\\\\[^\\\\]+\\\\'
    }
    
    system_specific_settings = {
        'x86_64': {
            'ProgFiles86': r'program files \(x86\)',
            'ProgFiles64': r'program files',
            'Sys86': 'syswow64',
            'Sys64': 'system32'
        },
        'x86': {
            'ProgFiles86': r'program files',
            'Sys86': 'system32'
        }
    }
    
    rules = []
    
    def __init__(self, architecture='x86_64'):
        self.settings['architecture']= architecture
        self.generate_rules()
    
    def normalize_path(self, path):
        for rule in self.rules:
            path = re.sub(f"{rule['regex']}", rule['replacement'], path.lower())
        return path
  
    def generate_rules(self):
        if self.settings['architecture'] == 'x86_64':
            self.settings.update(self.system_specific_settings['x86_64'])
        elif self.settings['architecture'] == 'x86':
            self.settings.update(self.system_specific_settings['x86'])       
        else:
            raise ValueError('the architecture of the host is x86 or x86_64')
        
        self.rules.append(
            {
                'regex': f"{self.settings['systemroot']}{self.settings['Sys86']}",
                'replacement': '?sys32'
            }
        )
        
        if self.settings['architecture'] == 'x86_64':
            self.rules.append(
                {
                    'regex': f"{self.settings['systemroot']}{self.settings['Sys64']}",
                    'replacement': '?sys64'
                }
            )
        self.rules.append(
            {
                'regex': f"{self.settings['systemdrive']}{self.settings['ProgFiles86']}",
                'replacement': '?pf86'
            }
        )
        if self.settings['architecture'] == 'x86_64':
            self.rules.append(
                {
                    'regex': f"{self.settings['systemdrive']}{self.settings['ProgFiles64']}",
                    'replacement': '?pf64'
                }
            )
        self.rules.append(
            {
                'regex': f"{self.settings['systemdrive']}{self.settings['usrTempPath']}",
                'replacement': '?usrtmp\\\\'
            }
        )
        self.rules.append(
            {
                'regex': f"{self.settings['systemdrive']}{self.settings['usrPath']}",
                'replacement': '?usr\\\\'
            }
        )
        self.rules.append(
            {
                'regex': f"{self.settings['systemroot']}",
                'replacement': '?win\\\\'
            }
        )
        self.rules.append(
            {
                'regex': f"{self.settings['systemdrive']}",
                'replacement': '?c\\\\'
            }
        )
        self.rules.append(
            {
                'regex': f"{self.settings['guid']}",
                'replacement': '{guid}'
            }
        )

