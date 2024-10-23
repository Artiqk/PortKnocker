import psutil
import socket

def get_local_ips(exclude_list=['127.0.0.1']):
    local_ips = []
    for interface, addrs in psutil.net_if_addrs().items():
        local_ips.extend([addr.address for addr in addrs if addr.family == socket.AF_INET and addr.address not in exclude_list])
    return local_ips