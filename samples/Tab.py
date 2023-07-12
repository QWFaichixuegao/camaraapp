# -*- coding: utf-8 -*-
import sys, nncam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QSignalBlocker, Qt,QRect,QIODevice
from PyQt5.QtGui import QPixmap, QImage,QFont
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QDesktopWidget, QCheckBox, QMessageBox, QMainWindow, QPushButton, QComboBox, QSlider, QGroupBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QMenu, QAction,QTextBrowser,QTabWidget,QTextEdit,QFrame
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from serial.tools import list_ports

class MainWindow(QMainWindow):
    evtCallback = pyqtSignal(int)

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

    def __init__(self):
        super().__init__()
        self.setMinimumSize(1024, 768)
        self.tabWidget = QTabWidget()
        self.tabWidget.setGeometry(QRect(-10, 10, 1024, 768))
        self.tab = QWidget()  #设置主界面
        self.tabWidget.addTab(self.tab, "Main")
        # self.w_main = QWidget(self.tab)
        # self.w_main.setGeometry(QRect(80, 30, 881, 651))
        grid_main = QGridLayout(self.tab)
        self.tab_2 = QWidget() #设置副界面
        widget = QWidget(self.tab_2)
        widget.setGeometry(QRect(50, 30, 900, 670))
        self.tabWidget.addTab(self.tab_2, "Sub")
        horizontalLayout = QHBoxLayout(widget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        #主界面所有
        self.hcam = None
        self.timer = QTimer(self)
        self.imgWidth = 0
        self.imgHeight = 0
        self.pData = None
        self.res = 0
        self.temp = nncam.NNCAM_TEMP_DEF
        self.tint = nncam.NNCAM_TINT_DEF
        self.count = 0
            #串口初始化
        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.receive_data)
        self.serial_port.errorOccurred.connect(self.handle_error)
            #分辨率
        gbox_res = QGroupBox("分辨率")
        self.cmb_res = QComboBox()
        self.cmb_res.setEnabled(False)
        vlyt_res = QVBoxLayout()
        vlyt_res.addWidget(self.cmb_res)
        gbox_res.setLayout(vlyt_res)
        self.cmb_res.currentIndexChanged.connect(self.onResolutionChanged)
            #曝光
        gbox_exp = QGroupBox("曝光")
        self.cbox_auto = QCheckBox()
        self.cbox_auto.setEnabled(False)
        lbl_auto = QLabel("自动曝光")
        hlyt_auto = QHBoxLayout()
        hlyt_auto.addWidget(self.cbox_auto)
        hlyt_auto.addWidget(lbl_auto)
        hlyt_auto.addStretch()
        lbl_time = QLabel("时间(us):")
        lbl_gain = QLabel("增益(%):")
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
        self.cbox_auto.stateChanged.connect(self.onAutoExpo)
        self.slider_expoTime.valueChanged.connect(self.onExpoTime)
        self.slider_expoGain.valueChanged.connect(self.onExpoGain)
            #白平衡
        gbox_wb = QGroupBox("白平衡")
        self.btn_autoWB = QPushButton("白平衡")
        self.btn_autoWB.setEnabled(False)
        self.btn_autoWB.clicked.connect(self.onAutoWB)
        lbl_temp = QLabel("色温:")
        lbl_tint = QLabel("色调:")
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
        self.slider_temp.valueChanged.connect(self.onWBTemp)
        self.slider_tint.valueChanged.connect(self.onWBTint)

        #相机按钮
        self.btn_open = QPushButton("打开相机")
        self.btn_open.clicked.connect(self.onBtnOpen)
        self.btn_snap = QPushButton("Snap")
        self.btn_snap.setEnabled(False)
        self.btn_snap.clicked.connect(self.onBtnSnap)

        # 串口连接按钮
        self.btn_connect = QPushButton("打开串口")
        self.btn_connect.clicked.connect(self.onBtnConnect)  # 连接按钮槽
        self.port_combo_box = QComboBox()
        self.refresh_port_list()
        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
            #左边布局
        vlyt_ctrl = QVBoxLayout()
        vlyt_ctrl.addWidget(gbox_res)
        vlyt_ctrl.addWidget(gbox_exp)
        vlyt_ctrl.addWidget(gbox_wb)
        vlyt_ctrl.addWidget(self.btn_open)
        vlyt_ctrl.addWidget(self.btn_snap)
        vlyt_ctrl.addWidget(self.port_combo_box)
        vlyt_ctrl.addWidget(self.btn_connect)
        vlyt_ctrl.addStretch()
        wg_ctrl = QWidget()
        wg_ctrl.setLayout(vlyt_ctrl)
            #右边布局
        self.lbl_frame = QLabel()
        self.lbl_video = QLabel()
        vlyt_show = QVBoxLayout()
        vlyt_show.addWidget(self.lbl_video, 1)
        vlyt_show.addWidget(self.lbl_frame)
        wg_show = QWidget()
        wg_show.setLayout(vlyt_show)
            # Main总体布局
        grid_main.setColumnStretch(0, 1)
        grid_main.setColumnStretch(1, 4)
        grid_main.addWidget(wg_ctrl)
        grid_main.addWidget(wg_show)
        # self.w_main.setLayout(grid_main)
        #副界面所有
            #添加采集和检测到布局（左边）
        MutiImg = QGroupBox("多光谱图像采集")
        self.caiji = QPushButton("开始采集")
        self.receive_text = QTextBrowser()
        vlyt_muti = QVBoxLayout()  # verticalLayout_7
        vlyt_muti.addWidget(self.caiji)
        vlyt_muti.addWidget(self.receive_text)
        MutiImg.setLayout(vlyt_muti)
        # self.caiji.clicked.connect(self.caiji_send)  # 添加采集按钮槽
        Detection = QGroupBox("损伤检测")
        self.jiance = QPushButton("开始检测")
        self.jiance_Browser = QTextBrowser()
        vlyt_jiance = QVBoxLayout()  # verticalLayout_8
        vlyt_jiance.addWidget(self.jiance)
        vlyt_jiance.addWidget(self.jiance_Browser)
        Detection.setLayout(vlyt_jiance)
        vlyt_detect = QVBoxLayout()  # Middle
        vlyt_detect.addWidget(MutiImg)
        vlyt_detect.addWidget(Detection)
            # 添加显示布局（右边）
        ReslutView = QGroupBox("结果显示")
        img = QLabel()
        img.setStyleSheet("background-color: rgb(222, 222, 222);")
        hlyt_img = QHBoxLayout()
        hlyt_img.setContentsMargins(20, -1, 20, -1)
        hlyt_img.addWidget(img)
        dt = QLabel()
        dt.setStyleSheet("background-color: rgb(255, 170, 0);")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        dt.setFont(font)
        dt.setStyleSheet("background-color: rgb(255, 170, 0);")
        dt.setFrameShape(QFrame.NoFrame)
        dt.setAlignment(Qt.AlignCenter)
        hlyt_dt = QHBoxLayout()
        hlyt_dt.setContentsMargins(100, -1, 100, 0)
        hlyt_dt.addWidget(dt)
        vlyt_view = QVBoxLayout()  # vlyt_detect
        vlyt_view.addLayout(hlyt_img)
        vlyt_view.addLayout(hlyt_dt)
        vlyt_view.setStretch(0, 6)
        vlyt_view.setStretch(1, 1)
        ReslutView.setLayout(vlyt_view)
            # SUB总体布局
        horizontalLayout.addLayout(vlyt_detect)
        horizontalLayout.addWidget(ReslutView)
        horizontalLayout.setStretch(0, 2)
        horizontalLayout.setStretch(1, 6)

        self.setCentralWidget(self.tabWidget)
        self.timer.timeout.connect(self.onTimer)
        self.evtCallback.connect(self.onevtCallback)

    def onTimer(self):
        if self.hcam:
            nFrame, nTime, nTotalFrame = self.hcam.get_FrameRate()
            self.lbl_frame.setText("{}, fps = {:.1f}".format(nTotalFrame, nFrame * 1000.0 / nTime))

    def closeCamera(self):
        if self.hcam:
            self.hcam.Close()
        self.hcam = None
        self.pData = None

        self.btn_open.setText("打开相机")
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

    def onResolutionChanged(self, index):
        if self.hcam: #step 1: stop camera
            self.hcam.Stop()

        self.res = index
        self.imgWidth = self.cur.model.res[index].width
        self.imgHeight = self.cur.model.res[index].height

        if self.hcam: #step 2: restart camera
            self.hcam.put_eSize(self.res)
            self.startCamera()

    def onAutoExpo(self, state):
        if self.hcam:
            self.hcam.put_AutoExpoEnable(1 if state else 0)
            self.slider_expoTime.setEnabled(not state)
            self.slider_expoGain.setEnabled(not state)

    def onExpoTime(self, value):
        if self.hcam:
            self.lbl_expoTime.setText(str(value))
            if not self.cbox_auto.isChecked():
                self.hcam.put_ExpoTime(value)

    def onExpoGain(self, value):
        if self.hcam:
            self.lbl_expoGain.setText(str(value))
            if not self.cbox_auto.isChecked():
                self.hcam.put_ExpoAGain(value)

    def onAutoWB(self):
        if self.hcam:
            self.hcam.AwbOnce()

    def wbCallback(nTemp, nTint, self):
        self.slider_temp.setValue(nTemp)
        self.slider_tint.setValue(nTint)

    def onWBTemp(self, value):
        if self.hcam:
            self.temp = value
            self.hcam.put_TempTint(self.temp, self.tint)
            self.lbl_temp.setText(str(value))

    def onWBTint(self, value):
        if self.hcam:
            self.tint = value
            self.hcam.put_TempTint(self.temp, self.tint)
            self.lbl_tint.setText(str(value))

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
            self.btn_open.setText("关闭相机")
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

    def onBtnSnap(self):
        if self.hcam:
            if 0 == self.cur.model.still:    # not support still image capture
                if self.pData is not None:
                    image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
                    self.count += 1
                    image.save("pyqt{}.jpg".format(self.count))
            else:
                menu = QMenu()
                for i in range(0, self.cur.model.still):
                    action = QAction("{}*{}".format(self.cur.model.res[i].width, self.cur.model.res[i].height), self)
                    action.setData(i)
                    menu.addAction(action)
                action = menu.exec(self.mapToGlobal(self.btn_snap.pos()))
                self.hcam.Snap(action.data())

    @staticmethod
    def eventCallBack(nEvent, self):
        '''callbacks come from nncam.dll/so internal threads, so we use qt signal to post this event to the UI thread'''
        self.evtCallback.emit(nEvent)

    def onevtCallback(self, nEvent):
        '''this run in the UI thread'''
        if self.hcam:
            if nncam.NNCAM_EVENT_IMAGE == nEvent:
                self.handleImageEvent()
            elif nncam.NNCAM_EVENT_EXPOSURE == nEvent:
                self.handleExpoEvent()
            elif nncam.NNCAM_EVENT_TEMPTINT == nEvent:
                self.handleTempTintEvent()
            elif nncam.NNCAM_EVENT_STILLIMAGE == nEvent:
                self.handleStillImageEvent()
            elif nncam.NNCAM_EVENT_ERROR == nEvent:
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Generic Error.")
            elif nncam.NNCAM_EVENT_STILLIMAGE == nEvent:
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
    # 串口
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
            self.btn_connect.setEnabled(False)

    def caiji_send(self):
        if self.serial_port.isOpen():
            data = str('#2').encode()
            self.serial_port.write(data)
            # self.receive_text.append("Sent: {}".format(data.decode()))
            print(data)
    def recvData(self):
        data = self.serial.readAll()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
