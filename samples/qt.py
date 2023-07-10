import sys, nncam
# import serial
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QSignalBlocker, QIODevice,Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QDesktopWidget, QCheckBox, QMessageBox, QMainWindow, QPushButton, QComboBox, QSlider, QGroupBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QMenu, QAction, QTextEdit
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from serial.tools import list_ports

class MainWindow(QMainWindow):#MainWindow继承QMainWindow

    #声明一个带int类型参数的信号
    evtCallback = pyqtSignal(int)

    #python使用函数"staticmethod()"或"@ staticmethod"指令的方法把普通的函数转换为静态方法。静态方法相当于全局函数
    @staticmethod
    def makeLayout(lbl_1, sli_1, val_1, lbl_2, sli_2, val_2):
        hlyt_1 = QHBoxLayout()
        hlyt_1.addWidget(lbl_1)
        hlyt_1.addStretch()
        hlyt_1.addWidget(val_1)
        hlyt_2 = QHBoxLayout()
        hlyt_2.addWidget(lbl_2)
        hlyt_2.addStretch()
        hlyt_2.addWidget(val_2)
        vlyt = QVBoxLayout()
        vlyt.addLayout(hlyt_1)
        vlyt.addWidget(sli_1)
        vlyt.addLayout(hlyt_2)
        vlyt.addWidget(sli_2)
        return vlyt

    #构造方法__init__用于创建实例对象时使用，每当创建一个类的实例对象时，Python 解释器都会自动调用它，用来初始化对象的某些属性
    def __init__(self):
        super().__init__()#MainWindow继承QMainWindow，因此此处__init__执行的是QMainWindow的
        self.setWindowTitle("apptest")
        self.setMinimumSize(1024, 568)
        self.hcam = None
        self.timer = QTimer(self)
        self.imgWidth = 0
        self.imgHeight = 0
        self.pData = None
        self.res = 0
        self.temp = nncam.NNCAM_TEMP_DEF
        self.tint = nncam.NNCAM_TINT_DEF
        self.count = 0

        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.receive_data)
        self.serial_port.errorOccurred.connect(self.handle_error)

        #分辨率ui
        gbox_res = QGroupBox("Resolution")
        self.cmb_res = QComboBox()
        self.cmb_res.setEnabled(False)
        vlyt_res = QVBoxLayout()
        vlyt_res.addWidget(self.cmb_res)
        gbox_res.setLayout(vlyt_res)
        self.cmb_res.currentIndexChanged.connect(self.onResolutionChanged)

        #曝光值ui
        ##水平布局
        gbox_exp = QGroupBox("Exposure")
        self.cbox_auto = QCheckBox()
        self.cbox_auto.setEnabled(False)
        lbl_auto = QLabel("Auto exposure")
        hlyt_auto = QHBoxLayout()
        hlyt_auto.addWidget(self.cbox_auto)
        hlyt_auto.addWidget(lbl_auto)
        hlyt_auto.addStretch()#布局充满的情况下添加伸缩量
        ##纵向布局
        lbl_time = QLabel("Time(us):")
        lbl_gain = QLabel("Gain(%):")
        self.lbl_expoTime = QLabel("0")
        self.lbl_expoGain = QLabel("0")
        self.slider_expoTime = QSlider(Qt.Horizontal)
        self.slider_expoGain = QSlider(Qt.Horizontal)
        self.slider_expoTime.setEnabled(False)
        self.slider_expoGain.setEnabled(False)
        vlyt_exp = QVBoxLayout()
        vlyt_exp.addLayout(hlyt_auto)
        vlyt_exp.addLayout(self.makeLayout(lbl_time, self.slider_expoTime, self.lbl_expoTime, lbl_gain, self.slider_expoGain, self.lbl_expoGain))
        gbox_exp.setLayout(vlyt_exp)
        self.cbox_auto.stateChanged.connect(self.onAutoExpo)#连接自动曝光槽
        self.slider_expoTime.valueChanged.connect(self.onExpoTime)#连接延迟值滑条槽
        self.slider_expoGain.valueChanged.connect(self.onExpoGain)#连接灰度值滑条槽

        #色温色调ui
        gbox_wb = QGroupBox("White balance")
        self.btn_autoWB = QPushButton("White balance")
        self.btn_autoWB.setEnabled(False)
        self.btn_autoWB.clicked.connect(self.onAutoWB)#连接自动白平衡槽
        lbl_temp = QLabel("Temperature:")
        lbl_tint = QLabel("Tint:")
        self.lbl_temp = QLabel(str(nncam.NNCAM_TEMP_DEF))
        self.lbl_tint = QLabel(str(nncam.NNCAM_TINT_DEF))
        self.slider_temp = QSlider(Qt.Horizontal)
        self.slider_tint = QSlider(Qt.Horizontal)
        self.slider_temp.setRange(nncam.NNCAM_TEMP_MIN, nncam.NNCAM_TEMP_MAX)
        self.slider_temp.setValue(nncam.NNCAM_TEMP_DEF)
        self.slider_tint.setRange(nncam.NNCAM_TINT_MIN, nncam.NNCAM_TINT_MAX)
        self.slider_tint.setValue(nncam.NNCAM_TINT_DEF)
        self.slider_temp.setEnabled(False)
        self.slider_tint.setEnabled(False)
        vlyt_wb = QVBoxLayout()
        vlyt_wb.addLayout(self.makeLayout(lbl_temp, self.slider_temp, self.lbl_temp, lbl_tint, self.slider_tint, self.lbl_tint))
        vlyt_wb.addWidget(self.btn_autoWB)
        gbox_wb.setLayout(vlyt_wb)
        self.slider_temp.valueChanged.connect(self.onWBTemp)#连接色温值滑条槽
        self.slider_tint.valueChanged.connect(self.onWBTint)#连接色调值滑条槽

        #连接相机按钮
        self.btn_open = QPushButton("Open")
        self.btn_open.clicked.connect(self.onBtnOpen)#连接按钮槽
        #拉取静态图片按钮
        self.btn_snap = QPushButton("Snap")
        self.btn_snap.setEnabled(False)
        self.btn_snap.clicked.connect(self.onBtnSnap)#连接按钮槽

        # 添加串口相关组件到布局
        # gbox_serial = QGroupBox("Serial Port")

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.onBtnConnect)

        self.port_combo_box = QComboBox(self)
        self.refresh_port_list()

        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)

        self.btn_660 = QPushButton("660")
        self.btn_730 = QPushButton("730")
        self.btn_800 = QPushButton("800")

        self.btn_850 = QPushButton("850")
        self.btn_940 = QPushButton("940")
        self.btn_1000 = QPushButton("1000")

        self.btn_xuanzhuan = QPushButton("turn")

        hlyt_serial0 = QHBoxLayout()#横
        hlyt_serial0.addWidget(self.port_combo_box)
        hlyt_serial0.addWidget(self.btn_connect)

        hlyt_serial1 = QHBoxLayout()#横
        hlyt_serial1.addWidget(self.btn_660)
        hlyt_serial1.addWidget(self.btn_730)
        hlyt_serial1.addWidget(self.btn_800)

        hlyt_serial2 = QHBoxLayout()#横
        hlyt_serial2.addWidget(self.btn_850)
        hlyt_serial2.addWidget(self.btn_940)
        hlyt_serial2.addWidget(self.btn_1000)

        vlyt_serial1 = QVBoxLayout()#纵
        vlyt_serial1.addWidget(self.receive_text)
        vlyt_serial1.addLayout(hlyt_serial0)
        vlyt_serial1.addLayout(hlyt_serial1)
        vlyt_serial1.addLayout(hlyt_serial2)
        vlyt_serial1.addWidget(self.btn_xuanzhuan)

        vlyt_serial1.addStretch()



        #驱动控制ui
        # vlyt_driver_ctrl = QVBoxLayout()
        # vlyt_driver_ctrl.addWidget(vlyt_serial1)
        wg_driver_ctrl = QWidget()
        wg_driver_ctrl.setLayout(vlyt_serial1)

        #将相机组件ui按顺序装入纵向布局
        vlyt_ctrl = QVBoxLayout()
        vlyt_ctrl.addWidget(gbox_res)
        vlyt_ctrl.addWidget(gbox_exp)
        vlyt_ctrl.addWidget(gbox_wb)
        vlyt_ctrl.addWidget(self.btn_open)
        vlyt_ctrl.addWidget(self.btn_snap)
        vlyt_ctrl.addStretch()
        wg_ctrl = QWidget()
        wg_ctrl.setLayout(vlyt_ctrl)

        #图像ui
        self.lbl_frame = QLabel()
        self.lbl_video = QLabel()
        vlyt_show = QVBoxLayout()
        vlyt_show.addWidget(self.lbl_video, 1)
        vlyt_show.addWidget(self.lbl_frame)
        wg_show = QWidget()
        wg_show.setLayout(vlyt_show)

        #栅格装载控制ui和图像ui
        grid_main = QGridLayout()
        grid_main.setColumnStretch(0, 2)
        grid_main.setColumnStretch(2, 3)
        grid_main.setColumnStretch(3, 5)
        grid_main.addWidget(wg_ctrl)
        grid_main.addWidget(wg_driver_ctrl)
        grid_main.addWidget(wg_show)

        w_main = QWidget()
        w_main.setLayout(grid_main)
        self.setCentralWidget(w_main)

        self.timer.timeout.connect(self.onTimer)#连接相机超时槽函数
        self.evtCallback.connect(self.onevtCallback)#连接相机内部信号所对应的相应槽

    def onTimer(self):#超时
        if self.hcam:
            nFrame, nTime, nTotalFrame = self.hcam.get_FrameRate()
            self.lbl_frame.setText("{}, fps = {:.1f}".format(nTotalFrame, nFrame * 1000.0 / nTime))

# #设置串口
#     def init_port(self, port:QSerialPort):
#         port.setBaudRate(QSerialPort.BaudRate.Baud115200)
#         port.setDataBits(QSerialPort.DataBits.Data8)
#         port.setParity(QSerialPort.Parity.NoParity)
#         port.setStopBits(QSerialPort.StopBits.OneStop)
#         # port.readyRead.connect(recv_data)

#关闭像机
    def closeCamera(self):
        if self.hcam:
            self.hcam.Close()
        self.hcam = None
        self.pData = None

        self.btn_open.setText("Open")
        self.timer.stop()
        self.lbl_frame.clear()
        self.cbox_auto.setEnabled(False)
        self.slider_expoGain.setEnabled(False)
        self.slider_expoTime.setEnabled(False)
        self.btn_autoWB.setEnabled(False)
        self.slider_temp.setEnabled(False)
        self.slider_tint.setEnabled(False)
        self.btn_snap.setEnabled(False)
        self.cmb_res.setEnabled(False)
        self.cmb_res.clear()

    def closeEvent(self, event):
        self.closeCamera()
##

    def onResolutionChanged(self, index):#更改设备序号
        if self.hcam: #step 1: stop camera
            self.hcam.Stop()

        self.res = index
        self.imgWidth = self.cur.model.res[index].width
        self.imgHeight = self.cur.model.res[index].height

        if self.hcam: #step 2: restart camera
            self.hcam.put_eSize(self.res)
            self.startCamera()

#曝光
    def onAutoExpo(self, state):#自动曝光
        if self.hcam:
            self.hcam.put_AutoExpoEnable(1 if state else 0)
            self.slider_expoTime.setEnabled(not state)
            self.slider_expoGain.setEnabled(not state)

    def onExpoTime(self, value):#曝光时间
        if self.hcam:
            self.lbl_expoTime.setText(str(value))
            if not self.cbox_auto.isChecked():
                self.hcam.put_ExpoTime(value)

    def onExpoGain(self, value):#曝光灰度值
        if self.hcam:
            self.lbl_expoGain.setText(str(value))
            if not self.cbox_auto.isChecked():
                self.hcam.put_ExpoAGain(value)
##

#白平衡
    def onAutoWB(self):#自动白平衡
        if self.hcam:
            self.hcam.AwbOnce()

    def wbCallback(nTemp, nTint, self):
        self.slider_temp.setValue(nTemp)
        self.slider_tint.setValue(nTint)

    def onWBTemp(self, value):#调整色温
        if self.hcam:
            self.temp = value
            self.hcam.put_TempTint(self.temp, self.tint)
            self.lbl_temp.setText(str(value))

    def onWBTint(self, value):#调整色调
        if self.hcam:
            self.tint = value
            self.hcam.put_TempTint(self.temp, self.tint)
            self.lbl_tint.setText(str(value))
##

#打开像机 onBtnOpen -> openCamera -> startCamera(sdk)
    def startCamera(self):
        self.pData = bytes(nncam.TDIBWIDTHBYTES(self.imgWidth * 24) * self.imgHeight)
        uimin, uimax, uidef = self.hcam.get_ExpTimeRange()
        self.slider_expoTime.setRange(uimin, uimax)
        self.slider_expoTime.setValue(uidef)
        usmin, usmax, usdef = self.hcam.get_ExpoAGainRange()
        self.slider_expoGain.setRange(usmin, usmax)
        self.slider_expoGain.setValue(usdef)
        self.handleExpoEvent()
        if self.cur.model.flag & nncam.NNCAM_FLAG_MONO == 0:
            self.handleTempTintEvent()
        try:
            self.hcam.StartPullModeWithCallback(self.eventCallBack, self)
        except nncam.HRESULTException:
            self.closeCamera()
            QMessageBox.warning(self, "Warning", "Failed to start camera.")
        else:
            self.cmb_res.setEnabled(True)
            self.cbox_auto.setEnabled(True)
            self.btn_autoWB.setEnabled(True)
            self.slider_temp.setEnabled(self.cur.model.flag & nncam.NNCAM_FLAG_MONO == 0)
            self.slider_tint.setEnabled(self.cur.model.flag & nncam.NNCAM_FLAG_MONO == 0)
            self.btn_open.setText("Close")
            self.btn_snap.setEnabled(True)
            bAuto = self.hcam.get_AutoExpoEnable()
            self.cbox_auto.setChecked(1 == bAuto)
            self.timer.start(1000)

    def openCamera(self):
        self.hcam = nncam.Nncam.Open(self.cur.id)
        if self.hcam:
            self.res = self.hcam.get_eSize()
            self.imgWidth = self.cur.model.res[self.res].width
            self.imgHeight = self.cur.model.res[self.res].height
            with QSignalBlocker(self.cmb_res):
                self.cmb_res.clear()
                for i in range(0, self.cur.model.preview):
                    self.cmb_res.addItem("{}*{}".format(self.cur.model.res[i].width, self.cur.model.res[i].height))
                self.cmb_res.setCurrentIndex(self.res)
                self.cmb_res.setEnabled(True)
            self.hcam.put_Option(nncam.NNCAM_OPTION_BYTEORDER, 0) #Qimage use RGB byte order
            self.hcam.put_AutoExpoEnable(1)
            self.startCamera()

    def onBtnOpen(self):
        if self.hcam:
            self.closeCamera()
        else:
            arr = nncam.Nncam.EnumV2()
            if 0 == len(arr):
                QMessageBox.warning(self, "Warning", "No camera found.")
            elif 1 == len(arr):
                self.cur = arr[0]
                self.openCamera()
            else:
                menu = QMenu()
                for i in range(0, len(arr)):
                    action = QAction(arr[i].displayname, self)
                    action.setData(i)
                    menu.addAction(action)
                action = menu.exec(self.mapToGlobal(self.btn_open.pos()))
                if action:
                    self.cur = arr[action.data()]
                    self.openCamera()
##

#拉模式静态抓拍
    def onBtnSnap(self):
        if self.hcam:
            if 0 == self.cur.model.still:    # not support still image capture
                if self.pData is not None:
                    image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
                    self.count += 1
                    image.save("pyqt{}.jpg".format(self.count))#更改保存的图片名
            else:
                menu = QMenu()
                for i in range(0, self.cur.model.still):
                    action = QAction("{}*{}".format(self.cur.model.res[i].width, self.cur.model.res[i].height), self)
                    action.setData(i)
                    menu.addAction(action)
                action = menu.exec(self.mapToGlobal(self.btn_snap.pos()))
                self.hcam.Snap(action.data())

    @staticmethod
##

#startCamera时传递该函数 nncam.dll/so中的响应会调用qt.py中的eventCallBack函数发出信号
    def eventCallBack(nEvent, self):
        '''callbacks come from nncam.dll/so internal threads, so we use qt signal to post this event to the UI thread'''
        self.evtCallback.emit(nEvent)

    def onevtCallback(self, nEvent):
        '''this run in the UI thread'''
        if self.hcam:
            if nncam.NNCAM_EVENT_IMAGE == nEvent:#视频图像数据到达(视频). 使用Nncam_PullImageXXXX“拉”图像数据
                self.handleImageEvent()
            elif nncam.NNCAM_EVENT_EXPOSURE == nEvent:#曝光时间发生改变
                self.handleExpoEvent()
            elif nncam.NNCAM_EVENT_TEMPTINT == nEvent:#白平衡参数发生改变,Temp/Tint模式
                self.handleTempTintEvent()
            elif nncam.NNCAM_EVENT_STILLIMAGE == nEvent:#静态图片数据到达(Nncam_Snap或Nncam_SnapN引发). 使用Nncam_PullImageXXXX“拉”图像数据
                self.handleStillImageEvent()
            elif nncam.NNCAM_EVENT_ERROR == nEvent:#一般性错误, 数据采集不能继续
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Generic Error.")
            elif nncam.NNCAM_EVENT_STILLIMAGE == nEvent:#
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Camera disconnect.")

    def handleImageEvent(self):
        try:
            self.hcam.PullImageV3(self.pData, 0, 24, 0, None)
        except nncam.HRESULTException:
            pass
        else:
            image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
            newimage = image.scaled(self.lbl_video.width(), self.lbl_video.height(), Qt.KeepAspectRatio, Qt.FastTransformation)
            self.lbl_video.setPixmap(QPixmap.fromImage(newimage))

    def handleExpoEvent(self):
        time = self.hcam.get_ExpoTime()
        gain = self.hcam.get_ExpoAGain()
        with QSignalBlocker(self.slider_expoTime):
            self.slider_expoTime.setValue(time)
        with QSignalBlocker(self.slider_expoGain):
            self.slider_expoGain.setValue(gain)
        self.lbl_expoTime.setText(str(time))
        self.lbl_expoGain.setText(str(gain))

    def handleTempTintEvent(self):
        nTemp, nTint = self.hcam.get_TempTint()
        with QSignalBlocker(self.slider_temp):
            self.slider_temp.setValue(nTemp)
        with QSignalBlocker(self.slider_tint):
            self.slider_tint.setValue(nTint)
        self.lbl_temp.setText(str(nTemp))
        self.lbl_tint.setText(str(nTint))

    def handleStillImageEvent(self):
        info = nncam.NncamFrameInfoV3()
        try:
            self.hcam.PullImageV3(None, 1, 24, 0, info) # peek
        except nncam.HRESULTException:
            pass
        else:
            if info.width > 0 and info.height > 0:
                buf = bytes(nncam.TDIBWIDTHBYTES(info.width * 24) * info.height)
                try:
                    self.hcam.PullImageV3(buf, 1, 24, 0, info)
                except nncam.HRESULTException:
                    pass
                else:
                    image = QImage(buf, info.width, info.height, QImage.Format_RGB888)
                    self.count += 1
                    image.save("pyqt{}.jpg".format(self.count))
##

#串口
    def refresh_port_list(self):
        self.port_combo_box.clear()
        ports = list_ports.comports()
        for port in ports:
            self.port_combo_box.addItem(port.device)

    def handle_error(self, error):
        if error == QSerialPort.NoError:
            return

    def receive_data(self):
        data = self.serial_port.readAll().data().decode().strip()
        if data:
            print(data)
            self.receive_text.append("Received: {}".format(data))

    def onBtnConnect(self):
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


        # if self.serial.isOpen():
        #     self.serial.close()
        #     self.btn_connect.setText("Connect")
        # else:
        #     port = self.cmb_port.currentText()
        #     self.serial.setPortName(port)
        #     if self.serial.open(QSerialPort.ReadWrite):
        #         self.serial.setBaudRate(QSerialPort.Baud115200)
        #         self.serial.readyRead.connect(self.recvData)
        #         self.btn_connect.setText("Disconnect")
        #     else:
        #         QMessageBox.warning(self, "Warning", "Failed to connect to serial port.")

    def recvData(self):
        data = self.serial.readAll()
##

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
