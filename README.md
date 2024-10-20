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
python -m app.port_checker
```

## Usage

### Main Features

- **Add Ports**: Enter the port number and select the protocol (TCP/UDP) to add a port to the list. Then click on "Add Port" button on press **Enter**.
- **Start Port Checking**: Click the "Start" button or press **F5** to begin checking the status of the ports in the list.
- **Remove Ports**: Select a port from the table and click the 🗑️ button to delete it from the list.
- **View Results**: The application will display the results of the port checks in the table.

### Keyboard Shortcuts

- **Return** Add port to the list.
- **F5**: Start checking the ports.

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

## Credits

- **Developer**: Artiqk - Created and maintained this application.
- **Icon**: Designed by Arthur Minthe