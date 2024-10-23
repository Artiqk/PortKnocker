import logging
from app.port_utils import PortsList

def is_port_range_and_valid(port_input: str) -> bool:
    """Check if the given port input is a port range and a valid one in the format 'start-end'."""
    if '-' in port_input:
        port_range = port_input.split('-')

        if len(port_range) != 2:
            logging.warning("Invalid port range format. Please use the format 'start-end', e.g., 22-80.")
            return False
        
        try:
            start = int(port_range[0])
            end = int(port_range[1])
            if start < 1 or end > 65535 or start >= end:
                logging.error(f"Invalid port range: {start}-{end}. Ports must be between 1-65535, and start must be less than end.")
                return False
        except ValueError:
            logging.error(f"Invalid port range values: {port_range[0]} - {port_range[1]}. Both values must be integers.")
            return False
        
        logging.info(f"Valid port range: {start}-{end}")
        return True
    
    return False


def is_port_valid(protocol: str, port: str, ports_list: PortsList) -> bool:
    """Validate if the specified port is valid for the given protocol and not already in the ports list."""
    try:
        port = int(port)
        if protocol not in ['tcp', 'udp']:
            logging.error(f"Invalid protocol: {protocol}")
            return False
        if port < 1 or port > 65535:
            logging.error(f"Invalid port: {port}. Must be a number between 1 and 65535.")
            return False
        if port in ports_list[protocol]:
            logging.warning(f"Port {port} is already in the list for protocol {protocol.upper()}.")
            return False
    except ValueError:
        logging.error(f"Invalid port value: {port}. Must be an integer.")
        return False
    
    logging.info(f"Valid port: {port}")
    return True