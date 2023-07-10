import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QTimer
import serial
from serial.tools import list_ports


class SerialAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Assistant")
        self.setGeometry(100, 100, 400, 300)

        self.serial_port = serial.Serial()
        self.timer = QTimer()
        self.timer.timeout.connect(self.receive_data)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 10, 380, 200)

        send_button = QPushButton("Send", self)
        send_button.setGeometry(10, 220, 180, 30)
        send_button.clicked.connect(self.send_data)

        open_button = QPushButton("Open Port", self)
        open_button.setGeometry(200, 220, 90, 30)
        open_button.clicked.connect(self.open_port)

        close_button = QPushButton("Close Port", self)
        close_button.setGeometry(300, 220, 90, 30)
        close_button.clicked.connect(self.close_port)

        self.port_combo_box = QComboBox(self)
        self.port_combo_box.setGeometry(10, 260, 180, 30)
        self.refresh_port_list()

    def send_data(self):
        data = self.text_edit.toPlainText()
        if self.serial_port.is_open:
            self.serial_port.write(data.encode())
            print(data.encode())

    def open_port(self):
        if not self.serial_port.is_open:
            port_name = self.port_combo_box.currentText()
            self.serial_port.port = port_name
            self.serial_port.baudrate = 115200  # 波特率，根据实际情况修改
            try:
                self.serial_port.open()
                self.text_edit.append(f"Port opened: {port_name}")
                self.timer.start(100)  # 每100毫秒接收一次数据
            except serial.SerialException:
                self.text_edit.append("Failed to open port.")

    def close_port(self):
        if self.serial_port.is_open:
            self.serial_port.close()
            self.timer.stop()
            self.text_edit.append("Port closed.")

    def receive_data(self):
        if self.serial_port.is_open:
            try:
                while self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    received_data = data.decode().strip()
                    self.text_edit.append(f"Received: {received_data}")
            except serial.SerialException:
                self.text_edit.append("Error occurred while receiving data.")

    def refresh_port_list(self):
        self.port_combo_box.clear()
        ports = list_ports.comports()
        for port in ports:
            self.port_combo_box.addItem(port.device)

    def closeEvent(self, event):
        if self.serial_port.is_open:
            self.serial_port.close()
            self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = SerialAssistant()
    assistant.show()
    sys.exit(app.exec_())
