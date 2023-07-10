import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton
import serial

class SerialAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Assistant")
        self.setGeometry(100, 100, 400, 300)

        self.serial_port = serial.Serial()

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

    def send_data(self):
        data = self.text_edit.toPlainText()
        if self.serial_port.is_open:
            self.serial_port.write(data.encode())

    def open_port(self):
        if not self.serial_port.is_open:
            self.serial_port.port = "COM1"  # 根据实际情况修改串口号
            self.serial_port.baudrate = 9600  # 波特率，根据实际情况修改
            try:
                self.serial_port.open()
                self.text_edit.append("Port opened.")
            except serial.SerialException:
                self.text_edit.append("Failed to open port.")

    def close_port(self):
        if self.serial_port.is_open:
            self.serial_port.close()
            self.text_edit.append("Port closed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = SerialAssistant()
    assistant.show()
    sys.exit(app.exec_())
