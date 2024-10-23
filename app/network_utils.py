import psutil
import socket
from typing import List

def get_local_ips(exclude_list: List[str] = ['127.0.0.1']) -> List[str]:
    """Retrieve a list of local IP addresses, excluding those in the exclude list."""
    local_ips = []
    for interface, addrs in psutil.net_if_addrs().items():
        local_ips.extend([addr.address for addr in addrs if addr.family == socket.AF_INET and addr.address not in exclude_list])
    return local_ips