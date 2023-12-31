# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Recent\shumeipaiDriverBoard\cameraAPP\save\untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


from PyQt5 import QtCore, QtGui, QtWidgets

import sys, nncam
# import serial
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QSignalBlocker, QIODevice,Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QDesktopWidget, QCheckBox, QMessageBox, QMainWindow, QPushButton, QComboBox, QSlider, QGroupBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QMenu, QAction, QTextEdit
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from serial.tools import list_ports

class Ui_Form(object):
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

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(817, 543)
        # self.setWindowTitle("apptest")
        # self.setMinimumSize(1024, 568)
        self.hcam = None
        self.timer = QTimer(Form)
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
        self.cmb_res = QComboBox()
        self.cmb_res.setEnabled(False)
        self.cmb_res.currentIndexChanged.connect(self.onResolutionChanged)

        #曝光值ui
        self.cbox_auto = QCheckBox()
        self.cbox_auto.setEnabled(False)
        self.cbox_auto.stateChanged.connect(self.onAutoExpo)#连接自动曝光槽
        lbl_auto = QLabel("Auto exposure")
        hlyt_auto = QHBoxLayout()
        hlyt_auto.addWidget(self.cbox_auto)
        hlyt_auto.addWidget(lbl_auto)
        hlyt_auto.addStretch()#布局充满的情况下添加伸缩量

        #色温色调ui
        self.btn_autoWB = QPushButton("White balance")
        self.btn_autoWB.setEnabled(False)
        self.btn_autoWB.clicked.connect(self.onAutoWB)#连接自动白平衡槽

        #连接相机按钮
        self.btn_open = QPushButton("Open")
        self.btn_open.clicked.connect(self.onBtnOpen)#连接按钮槽
        #拉取静态图片按钮
        self.btn_snap = QPushButton("Snap")
        self.btn_snap.setEnabled(False)
        self.btn_snap.clicked.connect(self.onBtnSnap)#连接按钮槽

        # 添加串口相关组件到布局
        self.btn_connect = QPushButton("connect")
        self.btn_connect.clicked.connect(self.onBtnConnect)
        self.port_combo_box = QComboBox()
        self.refresh_port_list()
        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)


        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.xiangji_left = QtWidgets.QVBoxLayout()
        self.xiangji_left.setObjectName("xiangji_left")
#*******************************************************************************************************
        self.xiangji_left.addWidget(self.cmb_res)#布局添加分辨率改变
        self.xiangji_left.addLayout(hlyt_auto)#布局添加自动曝光
        self.xiangji_left.addWidget(self.btn_autoWB)#布局添加自动白平衡
        self.xiangji_left.addWidget(self.btn_open)#布局添加打开相机按钮
        self.xiangji_left.addWidget(self.btn_snap)#布局添加打开相机按钮
        self.xiangji_left.addWidget(self.port_combo_box)#布局添加端口选择按钮
        self.xiangji_left.addWidget(self.btn_connect)#布局添加串口连接按钮

        self.horizontalLayout_3.addLayout(self.xiangji_left)
        self.Middle = QtWidgets.QVBoxLayout()
        self.Middle.setObjectName("Middle")
        self.MutiImg = QtWidgets.QGroupBox(Form)
        self.MutiImg.setObjectName("MutiImg")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.MutiImg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.caiji = QtWidgets.QPushButton(self.MutiImg)
        self.caiji.setObjectName("caiji")
        self.caiji.clicked.connect(self.caiji_send)#添加采集按钮槽
        self.verticalLayout.addWidget(self.caiji)
        self.receive_text = QtWidgets.QTextBrowser(self.MutiImg)#更改接收框名字
        self.receive_text.setObjectName("receive_text")
        self.verticalLayout.addWidget(self.receive_text)
        self.Middle.addWidget(self.MutiImg)
        self.Detection = QtWidgets.QGroupBox(Form)
        self.Detection.setObjectName("Detection")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.Detection)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.jiance = QtWidgets.QPushButton(self.Detection)
        self.jiance.setObjectName("jiance")
        self.verticalLayout_2.addWidget(self.jiance)
        self.jiance_Browser = QtWidgets.QTextBrowser(self.Detection)
        self.jiance_Browser.setObjectName("jiance_Browser")
        self.verticalLayout_2.addWidget(self.jiance_Browser)
        self.Middle.addWidget(self.Detection)
        self.horizontalLayout_3.addLayout(self.Middle)
        self.ReslutView_right = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ReslutView_right.sizePolicy().hasHeightForWidth())
        self.ReslutView_right.setSizePolicy(sizePolicy)
        self.ReslutView_right.setObjectName("ReslutView_right")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.ReslutView_right)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tuxiang = QtWidgets.QLabel(self.ReslutView_right)
        self.tuxiang.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tuxiang.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tuxiang.setText("")
        self.tuxiang.setObjectName("tuxiang")
        self.horizontalLayout_4.addWidget(self.tuxiang)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.qingkuang = QtWidgets.QLabel(self.ReslutView_right)
        self.qingkuang.setAlignment(QtCore.Qt.AlignCenter)
        self.qingkuang.setObjectName("qingkuang")
        self.horizontalLayout.addWidget(self.qingkuang)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(100, -1, 100, 10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.jieguo = QtWidgets.QLabel(self.ReslutView_right)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.jieguo.setFont(font)
        self.jieguo.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.jieguo.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.jieguo.setAlignment(QtCore.Qt.AlignCenter)
        self.jieguo.setObjectName("jieguo")
        self.horizontalLayout_2.addWidget(self.jieguo)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.setStretch(0, 6)
        self.verticalLayout_3.setStretch(2, 1)
        self.horizontalLayout_3.addWidget(self.ReslutView_right)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 2)
        self.horizontalLayout_3.setStretch(2, 6)

        self.retranslateUi(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        # self.btn_connect.setText(_translate("Form", "连接COM口"))
        self.MutiImg.setTitle(_translate("Form", "多光谱图像采集"))
        self.caiji.setText(_translate("Form", "开始采集"))
        self.Detection.setTitle(_translate("Form", "隐性损伤检测"))
        self.jiance.setText(_translate("Form", "开始检测"))
        self.ReslutView_right.setTitle(_translate("Form", "结果显示"))
        self.qingkuang.setText(_translate("Form", "损伤情况："))
        self.jieguo.setText(_translate("Form", "碰伤果"))



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

#白平衡
    def onAutoWB(self):#自动白平衡
        if self.hcam:
            self.hcam.AwbOnce()


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

    def caiji_send(self):
        if self.serial_port.isOpen():
            data = str('#2').encode()
            self.serial_port.write(data)
            # self.receive_text.append("Sent: {}".format(data.decode()))
            print(data)

    def recvData(self):
        data = self.serial.readAll()
##

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
