import sys
from PyQt5.QtCore import QIODevice, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit, QPushButton, QComboBox
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from serial.tools import list_ports

class SerialPortWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Port Communication")
        self.setGeometry(100, 100, 400, 300)

        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.receive_data)
        self.serial_port.errorOccurred.connect(self.handle_error)

        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget(self)
        layout = QVBoxLayout(main_widget)

        # 创建标签和文本框用于显示收发的数据
        self.receive_label = QLabel("Received Data:")
        layout.addWidget(self.receive_label)

        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        layout.addWidget(self.receive_text)

        self.send_label = QLabel("Send Data:")
        layout.addWidget(self.send_label)

        self.send_text = QTextEdit()
        layout.addWidget(self.send_text)

        # 创建按钮用于打开和关闭串口以及发送数据
        self.open_button = QPushButton("Open Port")
        self.open_button.clicked.connect(self.open_serial_port)
        layout.addWidget(self.open_button)

        self.close_button = QPushButton("Close Port")
        self.close_button.clicked.connect(self.close_serial_port)
        layout.addWidget(self.close_button)

        self.send_button = QPushButton("Send Data")
        self.send_button.clicked.connect(self.send_data)
        layout.addWidget(self.send_button)

        self.port_combo_box = QComboBox(self)
        # self.port_combo_box.setGeometry(10, 260, 180, 30)
        layout.addWidget(self.port_combo_box)
        self.refresh_port_list()


        self.setCentralWidget(main_widget)

    def open_serial_port(self):
        port_name = self.port_combo_box.currentText()
        baud_rate = QSerialPort.BaudRate.Baud115200  # 修改波特率，例如 QSerialPort.Baud115200

        if self.serial_port.isOpen():
            self.serial_port.close()

        self.serial_port.setPortName(port_name)
        self.serial_port.setBaudRate(baud_rate)

        if self.serial_port.open(QIODevice.ReadWrite):
            self.receive_text.append("Serial port {} is open.".format(port_name))
        else:
            self.receive_text.append("Error opening serial port: {}".format(self.serial_port.errorString()))

    def close_serial_port(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.receive_text.append("Serial port is closed.")

    def send_data(self):
        if self.serial_port.isOpen():
            data = self.send_text.toPlainText().encode()
            self.serial_port.write(data)
            # self.receive_text.append("Sent: {}".format(data.decode()))
            print(data)

    def receive_data(self):
        data = self.serial_port.readAll().data().decode().strip()
        if data:
            print(data)
            self.receive_text.append("Received: {}".format(data))


    def handle_error(self, error):
        if error == QSerialPort.NoError:
            return

        error_message = self.serial_port.errorString()
        self.receive_text.append("Serial port error: {}".format(error_message))

    def refresh_port_list(self):
        self.port_combo_box.clear()
        ports = list_ports.comports()
        for port in ports:
            self.port_combo_box.addItem(port.device)

    def closeEvent(self, event):
        self.close_serial_port()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialPortWindow()
    window.show()
    sys.exit(app.exec_())
