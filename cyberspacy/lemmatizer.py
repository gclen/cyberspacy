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