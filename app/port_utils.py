import socket
import requests
import threading
import random
import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
from config.logging_config import setup_logging


PortsList = Dict[str, List[int]]
PortsStatus = Dict[str, Dict[str, List[int]]]

load_dotenv()

api_ip = os.getenv("API_IP")
api_path = os.getenv("API_PATH")


def start_tcp_server(host: str, port: int, timeout: float) -> None:
    """Start a TCP server and accept one connection."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            logging.info(f"Starting TCP server on {host}:{port}")
            server_socket.bind((host, port))
            server_socket.listen(1)
            server_socket.settimeout(timeout)
            try:
                conn, addr = server_socket.accept()
                logging.info(f"Connection accepted from {addr}")
                conn.close()
            except socket.timeout:
                logging.warning(f"TCP server on {host}:{port} timed out after {timeout} seconds")
    except socket.error as e:
        logging.error(f"Socket error in TCP server on {host}:{port}: {e}")
    except Exception as e:
        logging.critical(f"Unexpected error in TCP server on {host}:{port}: {e}")


def start_udp_server(host: str, port: int, timeout: float) -> None:
    """Start a UDP server and listen for one message."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            logging.info(f"Starting UDP server on {host}:{port}")
            udp_socket.bind((host, port))
            udp_socket.settimeout(timeout)
            try:
                data, addr = udp_socket.recvfrom(1024)
                logging.info(f"Received data from {addr}")
                udp_socket.sendto(b"Port test", addr)
            except socket.timeout:
                logging.warning(f"UDP server on {host}:{port} timed out after {timeout} seconds")
    except socket.error as e:
        logging.error(f"Socket error in UDP server on {host}:{port}: {e}")
    except Exception as e:
        logging.critical(f"Unexpected error in UDP server on {host}:{port}: {e}")


def start_server(protocol: str, host: str, port: int, timeout: float = 3):
    """Start a server based on the specified protocol (TCP or UDP)."""
    try:
        if protocol == 'tcp':
            start_tcp_server(host, port, timeout)
        elif protocol == 'udp':
            start_udp_server(host, port, timeout)
        else:
            logging.error(f"Unknown protocol: {protocol}")
    except Exception as e:
        logging.critical(f"Error in starting {protocol.upper()} server on {host}:{port}: {e}")


def handle_port_status(protocol: str, port: int, ports_status: PortsStatus) -> None:
    """Check and update the status of a given port for the specified protocol."""
    try:
        logging.info(f"Checking port {port} for protocol {protocol.upper()}")
        port_open = is_port_open(protocol, port)

        if port_open:
            logging.info(f"Port {port} ({protocol.upper()}) is open")
            ports_status['open'][protocol].append(port)
        else:
            logging.info(f"Port {port} ({protocol.upper()}) is closed")
            ports_status['closed'][protocol].append(port)
    except Exception as e:
        logging.error(f"Error handling port status for {protocol.upper()} on port {port}: {e}")


def is_port_open(protocol: str, port: int) -> bool:
    """Check if a specific port is open using the API."""
    api_url = f"http://{api_ip}/{api_path}/{protocol}/{port}"
    
    try:
        logging.info(f"Sending request to {api_url}")
        res = requests.get(api_url)

        if res.status_code == 200:
            logging.info(f"Port {port} ({protocol.upper()}) is open according to API response")
            return True
        elif res.status_code == 400:
            logging.warning(f"Bad request for port {port} ({protocol.upper()})")
            return False
        elif res.status_code == 404:
            logging.warning(f"Not found: port {port} ({protocol.upper()})")
            return False
        elif res.status_code == 408:
            logging.warning(f"Request timeout for port {port} ({protocol.upper()})")
            return False
        elif res.status_code == 500:
            logging.error(f"Server error (500) for port {port} ({protocol.upper()})")
            return False
        else:
            logging.warning(f"Unexpected status code {res.status_code} for port {port} ({protocol.upper()})")
            return False
        
    except requests.ConnectionError as e:
        logging.error(f"Connection error when checking port {port} ({protocol.upper()}): {e}")
        return False
    except Exception as e:
        logging.critical(f"Unexpected error when checking port {port} ({protocol.upper()}): {e}")
        return False

    
def trigger_firewall_prompt() -> None:
    """Trigger a prompt to open firewall ports for TCP and UDP servers."""
    try:
        port = get_random_port()
        logging.info(f"Randomly selected port: {port}")

        tcp_server_thread = threading.Thread(target=start_server, args=('tcp', '0.0.0.0', port, 3))
        udp_server_thread = threading.Thread(target=start_server, args=('udp', '0.0.0.0', port, 3))

        tcp_thread = threading.Thread(target=is_port_open, args=('tcp', port))
        udp_thread = threading.Thread(target=is_port_open, args=('udp', port))

        tcp_server_thread.start()
        udp_server_thread.start()

        tcp_thread.start()
        udp_thread.start()
    except Exception as e:
        logging.warning(f"Error triggering firewall prompt: {e}")


def get_random_port(max_attempts: int = 10) -> Optional[int]:
    """Get a random available port within a specified number of attempts."""
    attempts = 0
    while attempts < max_attempts:
        port = random.randint(49152, 65535)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('0.0.0.0', port))
            if result != 0:
                logging.info(f"Port {port} is available.")
                return port
            else:
                logging.warning(f"Port {port} is in use, trying another ({max_attempts - attempts} attempts left).")
        attempts += 1
    
    logging.error("Exceeded maximum attempts to find an available port.")
    raise RuntimeError("No available ports found after maximum attempts.")
