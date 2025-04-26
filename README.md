# Port Knocker

## Overview

**Port Knocker** is a desktop application developed using Python and the PySide6 framework. This tool allows users to check if port forwarding is working by monitoring the status of specified TCP and UDP ports on a local machine. It is designed to be user-friendly, making it easy for both technical and non-technical users to verify their network configurations.

## Features

- Check the status (open/closed) of TCP and UDP ports.
- Support for multiple ports and protocols.
- A graphical user interface (GUI) built with PySide6.
- Dynamic update of port statuses in the UI.

## Requirements

To run the Port Knocker, ensure you have the following installed:

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
git clone https://github.com/Artiqk/PortKnocker.git
cd PortKnocker
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```
3. Run the application:

```bash
python main.py
```

## Note for Debian-based systems

If you encounter an error related to the Qt "xcb" platform plugin, make sure to install the required package:

```
sudo apt install libxcb-cursor0
```

This is needed for Qt applications starting from version 6.5.0.

## Disclaimer

This project depends on an external API, with the API path and IP stored in a ```.env``` file that is **not included** in this repository for **security reasons**. As a result, the code cannot be executed independently after cloning.

If you require access to the API, please note that it is not publicly available here. However, those with the necessary tools and expertise may be able to find the information required to replicate the functionality.

## Usage

### Main Features

- **Add Ports**: Enter the port number and select the protocol (TCP/UDP) to add a port to the list. Then click on "Add Port" button on press **Enter**.
- **Start Port Checking**: Click the "Start" button or press **F5** to begin checking the status of the ports in the list.
- **Remove Ports**: Select a port from the table and click the 🗑️ button to delete it from the list.
- **View Results**: The application will display the results of the port checks in the table.

### Keyboard Shortcuts

- **Return** Add port to the list.
- **F5**: Start checking the ports.

### Running on Privileged Ports (Below 1024)

If you're checking ports under 1024 (like 22 or 80), Linux will block you unless you run the app with elevated privileges.  
Use this command to give it permission without full root:

```bash
sudo setcap 'cap_net_bind_service=+ep' /path/to/binary
```
Replace /path/to/binary with the binary you're using. Or just run the thing with `sudo` like a true daredevil.

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