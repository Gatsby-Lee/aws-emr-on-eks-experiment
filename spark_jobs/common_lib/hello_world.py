"""
@author: Gatsby Lee
@since: 2023-09-05
"""

import socket

def get_hostname() -> str:
    return socket.gethostname()
