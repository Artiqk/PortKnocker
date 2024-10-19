import socket
import psutil
import threading
import logging
from PySide6 import QtWidgets, QtCore, QtGui
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


    @QtCore.Slot()
    def run(self):
        logging.info("Worker started.")
        server_threads  = []
        request_threads = []

        try:
            for protocol, ports in self.ports_list.items():
                for port in ports:
                    if not self._running:
                        break
                    try:
                        server_thread = threading.Thread(target=start_server, args=(protocol, self.host, port))
                        server_threads.append(server_thread)
                        server_thread.start()

                        request_thread = threading.Thread(target=handle_port_status, args=(protocol, port, self.ports_status))
                        request_threads.append(request_thread)
                        request_thread.start()
                    except Exception as e:
                        logging.error(f"Error starting server or request thread for {protocol.upper()} on port {port}: {e}")

                if not self._running:
                    break

            for thread in request_threads:
                thread.join()

            for thread in server_threads:
                thread.join()

        except Exception as e:
            logging.error(f"Error in Worker run method: {e}")

        logging.info("Worker finished.")
        self.finished.emit(self.ports_status)


    def stop(self):
        self._running = False



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.ports_list = { 'tcp': [], 'udp': [] }

        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.thread = None
        self.worker = None

        self.setupLocalIpComboBox()
        self.setupProtocolComboBox()

        self.ui.comboBox.activated.connect(self.keep_focus)
        self.ui.comboBox_2.activated.connect(self.keep_focus)

        self.ui.pushButton.clicked.connect(self.add_port)
        self.ui.lineEdit.returnPressed.connect(self.add_port)
        self.ui.pushButton_2.clicked.connect(self.start_port_checking)

        self.ui.tableWidget.setColumnWidth(0, 30)


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
        if self.thread and self.thread.isRunning():
            logging.warning("Attempted to add port while a thread is running.")
            return
        
        port = self.ui.lineEdit.text().strip()
        protocol = self.ui.comboBox.currentText()

        try:
            if port.isdigit() and int(port) > 0 and int(port) < 65535:
                if int(port) not in self.ports_list[protocol.lower()]:
                    self.ports_list[protocol.lower()].append(int(port))
                    self.insert_port_row(protocol, port)
                    self.ui.lineEdit.clear()
                    logging.info(f"Added port {port} for protocol {protocol.upper()}.")
                else:
                    logging.warning(f"Port {port} is already in the list for protocol {protocol.upper()}.")
            else:
                logging.error(f"Invalid port number: {port}. Must be between 1 and 65535.")
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
            for row in range(self.ui.tableWidget.rowCount()):
                self.ui.tableWidget.item(row, 3).setText("Unknown")

            for status, protocols in ports_status.items():
                for protocol, ports in protocols.items():
                    for port in ports:
                        for row in range(self.ui.tableWidget.rowCount()):
                            protocol_item = self.ui.tableWidget.item(row, 2)
                            port_item = self.ui.tableWidget.item(row, 1)

                            if protocol_item and port_item:
                                if protocol_item.text().lower() == protocol and int(port_item.text()) == port:
                                    self.ui.tableWidget.item(row, 3).setText(status.capitalize())
                                    break

            self.thread.quit()
            self.thread.wait()
            logging.info("Port checking process completed.")
        except Exception as e:
            logging.error(f"Error handling results: {e}")
        finally:
            self.keep_focus()



if __name__ == "__main__":
    setup_logging()

    try:
        trigger_firewall_prompt()

        app = QtWidgets.QApplication()
        app.setStyle("Fusion")

        window = MainWindow()
        window.setWindowIcon(QtGui.QIcon("icon.ico"))
        window.show()
        window.ui.lineEdit.setFocus()
        
        app.exec()
    except Exception as e:
        logging.error(f"An error occurred during application startup: {e}")