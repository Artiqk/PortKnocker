import socket
import psutil
import threading
import logging
import resources.resources as resources
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QShortcut, QKeySequence
from app.window_ui import Ui_MainWindow
from app.port_utils import start_server, handle_port_status, trigger_firewall_prompt
from config.logging_config import setup_logging


class Worker(QtCore.QObject):
    finished = QtCore.Signal(dict)

    def __init__(self, ports_list, host):
        super().__init__()
        self.ports_list = ports_list
        self.host = host
        self.ports_status = {
            'open': { 'tcp': [], 'udp': [] },
            'closed': { 'tcp': [], 'udp': [] }
        }
        self._running = True


    def create_and_start_threads(self, protocol, ports):
        server_threads  = []
        request_threads = []

        try:
            for port in ports:
                server_thread = threading.Thread(target=start_server, args=(protocol, self.host, port))
                server_threads.append(server_thread)
                server_thread.start()

                request_thread = threading.Thread(target=handle_port_status, args=(protocol, port, self.ports_status))
                request_threads.append(request_thread)
                request_thread.start()
        except Exception as e:
            logging.error(f"Error starting server or request thread for {protocol.upper()} on port {port}: {e}")

        return server_threads, request_threads
    

    def join_threads(self, server_threads, request_threads):
        for thread in request_threads:
            thread.join()

        for thread in server_threads:
            thread.join()


    @QtCore.Slot()
    def run(self):
        logging.info("Worker started.")

        try:
            for protocol, ports in self.ports_list.items():
                if not self._running:
                    break
                
                server_threads, request_threads = self.create_and_start_threads(protocol, ports)

                if not self._running:
                    break

            self.join_threads(server_threads, request_threads)

        except Exception as e:
            logging.error(f"Error in Worker run method: {e}")

        logging.info("Worker finished.")
        self.finished.emit(self.ports_status)


    def stop(self):
        self._running = False



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ports_list = { 'tcp': [], 'udp': [] }

        self.thread = None
        self.worker = None

        self.setWindowIcon(QtGui.QIcon(":icon.ico"))
        self.setWindowTitle("Port Checker")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setupLocalIpComboBox()
        self.setupProtocolComboBox()

        self.ui.tableWidget.setColumnWidth(0, 30)
        
        self.ui.comboBox.activated.connect(self.keep_focus)
        self.ui.comboBox_2.activated.connect(self.keep_focus)

        self.ui.pushButton.clicked.connect(self.add_port)
        self.ui.lineEdit.returnPressed.connect(self.add_port)

        self.ui.pushButton_2.clicked.connect(self.start_port_checking)

        shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        shortcut_f5.activated.connect(self.start_port_checking)



    def setupLocalIpComboBox(self):
        local_ips = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                    local_ips.append(addr.address)
        self.ui.comboBox_2.addItems(local_ips)


    def setupProtocolComboBox(self):
        protocols = ["TCP", "UDP"]
        self.ui.comboBox.addItems(protocols)


    def keep_focus(self):
        self.ui.lineEdit.setFocus()


    def insert_port_row(self, protocol, port):
        row_position = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row_position)

        port_item = QtWidgets.QTableWidgetItem(str(port))
        port_item.setTextAlignment(QtCore.Qt.AlignCenter)

        protocol_item = QtWidgets.QTableWidgetItem(protocol)
        protocol_item.setTextAlignment(QtCore.Qt.AlignCenter)

        self.ui.tableWidget.setItem(row_position, 1, port_item)
        self.ui.tableWidget.setItem(row_position, 2, protocol_item)
        self.ui.tableWidget.setItem(row_position, 3, QtWidgets.QTableWidgetItem("Pending"))

        # TODO: Add button to remove all ports
        remove_button = QtWidgets.QPushButton("🗑️")
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: black; /* Default text color */
            }
            QPushButton:hover {
                background-color: red; /* Color on hover */
                color: white; /* Text color on hover */
            }
        """)
        remove_button.clicked.connect(lambda checked: self.remove_port(row_position))
        self.ui.tableWidget.setCellWidget(row_position, 0, remove_button)


    def populate_table(self):
        self.ui.tableWidget.setRowCount(0)

        for protocol, ports in self.ports_list.items():
            for port in ports:
                self.insert_port_row(protocol.upper(), port)


    def add_port(self):
        max_allowed_port = 128

        if self.thread and self.thread.isRunning():
            logging.warning("Attempted to add port while a thread is running.")
            return
        
        total_port = sum(len(self.ports_list[protocol]) for protocol in self.ports_list.keys())

        if total_port >= max_allowed_port:
            logging.warning(f"Maximum allowed port in the table reached ({max_allowed_port}).")
            return
        
        port = self.ui.lineEdit.text().strip()
        protocol = self.ui.comboBox.currentText().lower()

        if self.is_port_range_and_valid(port):
            port_range = port.split('-')
            start, end = int(port_range[0]), int(port_range[1])
            self.add_port_range(protocol, start, end)
        elif self.is_port_valid(protocol, port):
            self.add_port_to_table(protocol, port)

    
    def is_port_range_and_valid(self, port_input):
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
    

    def add_port_range(self, protocol, start, end, max_range=128):
        total_port = (end - start)
        try:
            if total_port > max_range:
                logging.warning(f"Too many ports selected ({total_port}). The maximum allowed is {max_range}.")
                return
            logging.info(f"Adding port range from {start} to {end}. Number of ports to add {end - start}.")
            for port_nb in range(start, end + 1):
                if self.is_port_valid(protocol, port_nb):
                    self.add_port_to_table(protocol, port_nb)
        except Exception as e:
            logging.error(f"Error adding port range: {e}")


    def is_port_valid(self, protocol, port):
        try:
            port = int(port)
            if protocol not in ['tcp', 'udp']:
                logging.error(f"Invalid protocol: {protocol}")
                return False
            if port < 1 or port > 65535:
                logging.error(f"Invalid port: {port}. Must be a number between 1 and 65535.")
                return False
            if port in self.ports_list[protocol]:
                logging.warning(f"Port {port} is already in the list for protocol {protocol.upper()}.")
                return False
        except ValueError:
            logging.error(f"Invalid port value: {port}. Must be an integer.")
            return False
        
        logging.info(f"Valid port: {port}")
        return True
    

    def add_port_to_table(self, protocol, port):
        try:
            port = int(port)
            self.ports_list[protocol].append(port)
            self.insert_port_row(protocol.upper(), port)
            self.ui.lineEdit.clear()
            logging.info(f"Added port {port} for protocol {protocol.upper()}.")
        except Exception as e:
            logging.error(f"Error adding port: {e}")
        finally:
            self.keep_focus()


    def remove_port(self, row):
        if self.thread and self.thread.isRunning():
            logging.warning("Attempted to remove port while a thread is running.")
            return
        
        protocol_item = self.ui.tableWidget.item(row, 2)
        port_item = self.ui.tableWidget.item(row, 1)

        if protocol_item and port_item:
            protocol = protocol_item.text().lower()
            port = int(port_item.text())
            ports = self.ports_list[protocol]

            try:
                ports.remove(port)
                self.populate_table()
                logging.info(f"Removed port {port} for protocol {protocol.upper()}.")
            except ValueError:
                logging.error(f"Port {port} not found in the list for protocol {protocol.upper()}")

        else:
            logging.error("Protocol or port item not found in the table.")
        
        self.keep_focus()


    def start_port_checking(self):
        if self.thread and self.thread.isRunning():
            logging.warning(f"Attempted to start port checking while a thread is running.")
            return

        for row in range(self.ui.tableWidget.rowCount()):
            self.ui.tableWidget.item(row, 3).setText("Checking...")
        
        host = self.ui.comboBox_2.currentText()

        try:
            self.worker = Worker(self.ports_list, host)
            self.worker.finished.connect(self.handle_results)

            self.thread = QtCore.QThread()
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.thread.start()
            logging.info("Started port checking process.")
        except Exception as e:
            logging.error(f"Error starting port checking: {e}")


    @QtCore.Slot()
    def handle_results(self, ports_status):
        try:
            for status, protocols in ports_status.items():
                for protocol, ports in protocols.items():
                    self.update_ports_status(protocol, ports, status)

            self.thread.quit()
            self.thread.wait()
            logging.info("Port checking process completed.")
        except Exception as e:
            logging.error(f"Error handling results: {e}")
        finally:
            self.keep_focus()

        
    def set_default_table_status(self):
        for row in range(self.ui.tableWidget.rowCount()):
            self.ui.tableWidget.item(row, 3).setText("Unknown")


    def update_ports_status(self, protocol, ports, status):
        for port in ports:
            self.update_port_row(protocol, port, status)

    
    def update_port_row(self, protocol, port, status):
        for row in range(self.ui.tableWidget.rowCount()):
            protocol_item = self.ui.tableWidget.item(row, 2)
            port_item = self.ui.tableWidget.item(row, 1)

            if protocol_item and port_item:
                if protocol_item.text().lower() == protocol and int(port_item.text()) == port:
                    # TODO: Add colors for status => green: open | red: closed
                    self.ui.tableWidget.item(row, 3).setText(status.capitalize())
                    break


if __name__ == "__main__":
    setup_logging()
    logging.info("Loading resources.")
    resources.qInitResources()

    try:
        trigger_firewall_prompt()

        app = QtWidgets.QApplication()
        app.setStyle("Fusion")

        window = MainWindow()
        window.show()
        window.ui.lineEdit.setFocus()
        
        app.exec()
    except Exception as e:
        logging.error(f"An error occurred during application startup: {e}")
    finally:
        logging.info("Cleaning up resources.")
        resources.qCleanupResources()