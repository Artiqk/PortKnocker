# Port Checker

## Overview

**Port Checker** is a desktop application developed using Python and the PySide6 framework. This tool allows users to check if port forwarding is working by monitoring the status of specified TCP and UDP ports on a local machine. It is designed to be user-friendly, making it easy for both technical and non-technical users to verify their network configurations.

## Features

- Check the status (open/closed) of TCP and UDP ports.
- Support for multiple ports and protocols.
- A graphical user interface (GUI) built with PySide6.
- Dynamic update of port statuses in the UI.

## Requirements

To run the Port Checker, ensure you have the following installed:

- Python 3.6 or higher
- PySide6
- requests
- psutil

You can install the necessary packages using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Artiqk/PortChecker.git
cd PortChecker
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```
3. Run the application:

```bash
python port_checker.py
```

## Usage

1. **Adding Ports**: Enter a port number in the input field and select the protocol (TCP/UDP). Click the "Add Port" button or press Enter to add the port to the list.
2. **Checking Ports**: Select your local IP address and click on START to start checking the status of the added ports.
3. **Viewing Results**: The application will display the status of each port (open/closed) in the table.
4. **Removing Ports**: Click the trash can icon next to a port entry to remove it from the list.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push to the branch.
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or support, please open an issue in the GitHub repository or contact the author directly.
