"""
This module includes the functions of sanxiUI.
Related modules: sanxi_core.py, Sanxi_CtrlUI.py
Author:Mr Sosimple
"""


import threading

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QCoreApplication

import sanxi_core
import Sanxi_CtrlUI


class SanxiWindow(sanxi_core.Sanxi, QtWidgets.QWidget, Sanxi_CtrlUI.Ui_Sanxi_form):
    def __init__(self):
        super(SanxiWindow, self).__init__()
        print(SanxiWindow.__mro__)
        self.setupUi(self)
        # communication/start up
        self.connect_pushButton.clicked.connect(self.connect_pushButton_clicked)
        self.searchorigin_pushButton.clicked.connect(self.searchorigin_pushButton_clicked)
        self.disconnct_pushButton.clicked.connect(self.disconnct_pushButton_clicked)
        # motion parameters
        self.motionparaOK_pushButton.clicked.connect(self.motionparaOK_pushButton_clicked)
        # core functions
        self.backtoorigin_pushButton.clicked.connect(self.backtoorigin_pushButton_clicked)
        self.stop_pushButton.clicked.connect(self.stop_pushButton_clicked)
        self.call_v51exe_pushButton.clicked.connect(self.call_v51exe_pushButton_clicked)
        self.quit_pushButton.clicked.connect(self.quit_pushButton_clicked)
        # fundamental functions
        self.p2p_pushButton.clicked.connect(self.p2p_pushButton_clicked)
        self.goline_pushButton.clicked.connect(self.goline_pushButton_clicked)
        self.goangle_pushButton.clicked.connect(self.goangle_pushButton_clicked)
        self.sendcode_pushButton.clicked.connect(self.sendcode_pushButton_clicked)
        # display board-timer
        # self.display_board_timer = threading.Timer(0.1, self.display_board)
        # self.display_board_timer.start()
        # display board-control button
        self.coordinate_display_mode_flag = 1  # 1为笛卡尔坐标  0位关节空间坐标
        self.rectmode_pushButton.clicked.connect(self.rectmode_pushButton_clicked)
        self.anglemode_pushButton.clicked.connect(self.anglemode_pushButton_clicked)
        # single joint jogging
        self.j1cw_pushButton.pressed.connect(self.j1cw_pushButton_pressed)
        self.j1cw_pushButton.clicked.connect(self.j1cw_pushButton_clicked)
        self.j1ccw_pushButton.pressed.connect(self.j1ccw_pushButton_pressed)
        self.j1ccw_pushButton.clicked.connect(self.j1ccw_pushButton_clicked)
        self.j2up_pushButton.pressed.connect(self.j2up_pushButton_pressed)
        self.j2up_pushButton.clicked.connect(self.j2up_pushButton_clicked)
        self.j2down_pushButton.pressed.connect(self.j2down_pushButton_pressed)
        self.j2down_pushButton.clicked.connect(self.j2down_pushButton_clicked)
        self.j3up_pushButton.pressed.connect(self.j3up_pushButton_pressed)
        self.j3up_pushButton.clicked.connect(self.j3up_pushButton_clicked)
        self.j3down_pushButton.pressed.connect(self.j3down_pushButton_pressed)
        self.j3down_pushButton.clicked.connect(self.j3down_pushButton_clicked)
        self.j4cw_pushButton.pressed.connect(self.j4cw_pushButton_pressed)
        self.j4cw_pushButton.clicked.connect(self.j4cw_pushButton_clicked)
        self.j4ccw_pushButton.pressed.connect(self.j4ccw_pushButton_pressed)
        self.j4ccw_pushButton.clicked.connect(self.j4ccw_pushButton_clicked)
        self.j5up_pushButton.pressed.connect(self.j5up_pushButton_pressed)
        self.j5up_pushButton.clicked.connect(self.j5up_pushButton_clicked)
        self.j5down_pushButton.pressed.connect(self.j5down_pushButton_pressed)
        self.j5down_pushButton.clicked.connect(self.j5down_pushButton_clicked)
        self.j6cw_pushButton.pressed.connect(self.j6cw_pushButton_pressed)
        self.j6cw_pushButton.clicked.connect(self.j6cw_pushButton_clicked)
        self.j6ccw_pushButton.pressed.connect(self.j6ccw_pushButton_pressed)
        self.j6ccw_pushButton.clicked.connect(self.j6ccw_pushButton_clicked)

    ##############################connection judgement then raise dialogs########################
    def not_connect_dialog(self):
        QMessageBox.Warning(self, 'Error', 'Please connect first!', QMessageBox.Yes)

    ##############################communication/start up##############################
    def connect_pushButton_clicked(self):
        port_number = self.port_spinBox.value()
        port_name = 'COM' + str(port_number)
        if self.connect_sanxi(port_name):
            self.motionparaOK_pushButton_clicked()
            self.set_return_data_mode(mode=1)
        else:
            QMessageBox.information(self, 'Warning', 'Connect Failed', QMessageBox.Yes)

    def searchorigin_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        self.search_origin()

    def disconnct_pushButton_clicked(self):
        self.disconnect_sanxi()

    ##############################motion parameters###########################
    def motionparaOK_pushButton_clicked(self):
        vep = self.ve_verticalSlider.value()
        acp = self.ac_verticalSlider.value()
        dep = self.de_verticalSlider.value()
        self.set_motion_para(vep, acp, dep)

    ##############################Core Functions##############################
    def backtoorigin_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        self.back2origin()

    def stop_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        self.freeze_motion()

    # 调用外部exe——三喜原厂软件
    def call_v51exe_pushButton_clicked(self):
        import os
        if self.is_connected():
            reply = QMessageBox.information(self, 'Warning',
                                            'Do you want to disconnect first?(Recommend Yes)',
                                            QMessageBox.Yes | QMessageBox.No)
            if reply:
                self.disconnect_sanxi()
        os.popen('V51.exe')

    # 退出
    def quit_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        else:
            self.stop_then_into_free_mode()
            self.disconnect_sanxi()
            self.display_board_timer.cancel()  # 退出系统前停止其他线程和定时器
            QCoreApplication.quit()

    ##############################Fundamental Functions##############################
    # 读直角坐标文本框值
    def read_rect_lineEdit(self):
        rect_dict = {'X': float(self.xread_lineEdit.text()),
                     'Y': float(self.yread_lineEdit.text()),
                     'Z': float(self.zread_lineEdit.text()),
                     'A': float(self.aread_lineEdit.text()),
                     'B': float(self.bread_lineEdit.text()),
                     'C': float(self.cread_lineEdit.text())}
        return rect_dict

    # 读关节坐标文本框值
    def read_angle_lineEdit(self):
        j_dict = {'J1': float(self.j1read_lineEdit.text()),
                  'J2': float(self.j2read_lineEdit.text()),
                  'J3': float(self.j3read_lineEdit.text()),
                  'J4': float(self.j4read_lineEdit.text()),
                  'J5': float(self.j5read_lineEdit.text()),
                  'J6': float(self.j6read_lineEdit.text())}
        return j_dict

    # 直角坐标点对点运动
    def p2p_pushButton_clicked(self):
        rect_dict = self.read_rect_lineEdit()
        rect_dict['D'] = 0
        self.rect_move(mode='p2p', **rect_dict)

    # 直角坐标直线运动
    def goline_pushButton_clicked(self):
        rect_dict = self.read_rect_lineEdit()
        rect_dict['D'] = '0'
        self.rect_move(mode='line', **rect_dict)

    # 按轴角度运动
    def goangle_pushButton_clicked(self):
        j_dict = self.read_angle_lineEdit()
        self.multi_joints_motion(**j_dict)

    # 发送命令
    def sendcode_pushButton_clicked(self):
        data_list = self.sendcode_textEdit.toPlainText().split(sep='\n')  # 拆分多行命令，间隔0.1秒发送
        if self.current_mode != 14:
            self.change_to_mode14()
        for send_data in data_list:
            if send_data:
                self.send_cmd(send_data + '\n', 0.014)

    #########################sigle jiont jogging#########################
    # 单轴点动：pressed为按下按钮操作，clicked为松开按钮操作
    def j1cw_pushButton_pressed(self):
        self.single_joint_motion_start(1, True)

    def j1cw_pushButton_clicked(self):
        self.single_joint_motion_stop(1)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j1ccw_pushButton_pressed(self):
        self.single_joint_motion_start(1, False)

    def j1ccw_pushButton_clicked(self):
        self.single_joint_motion_stop(1)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j2up_pushButton_pressed(self):
        self.single_joint_motion_start(2, True)

    def j2up_pushButton_clicked(self):
        self.single_joint_motion_stop(2)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j2down_pushButton_pressed(self):
        self.single_joint_motion_start(2, False)

    def j2down_pushButton_clicked(self):
        self.single_joint_motion_stop(2)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j3up_pushButton_pressed(self):
        self.single_joint_motion_start(3, True)

    def j3up_pushButton_clicked(self):
        self.single_joint_motion_stop(3)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j3down_pushButton_pressed(self):
        self.single_joint_motion_start(3, False)

    def j3down_pushButton_clicked(self):
        self.single_joint_motion_stop(3)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j4cw_pushButton_pressed(self):
        self.single_joint_motion_start(4, True)

    def j4cw_pushButton_clicked(self):
        self.single_joint_motion_stop(4)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j4ccw_pushButton_pressed(self):
        self.single_joint_motion_start(4, False)

    def j4ccw_pushButton_clicked(self):
        self.single_joint_motion_stop(4)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j5up_pushButton_pressed(self):
        self.single_joint_motion_start(5, True)

    def j5up_pushButton_clicked(self):
        self.single_joint_motion_stop(5)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j5down_pushButton_pressed(self):
        self.single_joint_motion_start(5, False)

    def j5down_pushButton_clicked(self):
        self.single_joint_motion_stop(5)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j6cw_pushButton_pressed(self):
        self.single_joint_motion_start(6, True)

    def j6cw_pushButton_clicked(self):
        self.single_joint_motion_stop(6)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    def j6ccw_pushButton_pressed(self):
        self.single_joint_motion_start(6, False)

    def j6ccw_pushButton_clicked(self):
        self.single_joint_motion_stop(6)
        if self.coordinate_display_mode_flag == 1:
            self.query_coord()

    #########################display board#########################
    def display_board(self):
        """
        显示接收代码，显示关节坐标值或直角坐标值
        :return:
        """
        # print(self.all_return_code)

        # if self.all_return_code:
        self.returncode_textBrowser.append(self.new_return_code)
        self.returncode_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.returncode_textBrowser.ensureCursorVisible()
        # refresh value
        if self.jn_value and (self.coordinate_display_mode_flag == 0):
            print(self.jn_value)
            self.j1show_lineEdit.setText(str(self.jn_value[0]))
            self.j2show_lineEdit.setText(str(self.jn_value[1]))
            self.j3show_lineEdit.setText(str(self.jn_value[2]))
            self.j4show_lineEdit.setText(str(self.jn_value[3]))
            self.j5show_lineEdit.setText(str(self.jn_value[4]))
            self.j6show_lineEdit.setText(str(self.jn_value[5]))
        if self.xyz_value and (self.coordinate_display_mode_flag == 1):
            print('in show_xyz', self.xyz_value[0], self.xyz_value[1], '...')
            self.xshow_lineEdit.setText(str(self.xyz_value[0]))
            self.yshow_lineEdit.setText(str(self.xyz_value[1]))
            self.zshow_lineEdit.setText(str(self.xyz_value[2]))
            self.ashow_lineEdit.setText(str(self.xyz_value[3]))
            self.bshow_lineEdit.setText(str(self.xyz_value[4]))
            self.cshow_lineEdit.setText(str(self.xyz_value[5]))
        self.display_board_timer = threading.Timer(0.1, self.display_board)
        self.display_board_timer.start()
        # print('leave display func')

    def rectmode_pushButton_clicked(self):
        """
        直角坐标显示模式
        :return:
        """
        self.set_return_data_mode(1)
        self.coordinate_display_mode_flag = 1
        self.j1show_lineEdit.clear()
        self.j2show_lineEdit.clear()
        self.j3show_lineEdit.clear()
        self.j4show_lineEdit.clear()
        self.j5show_lineEdit.clear()
        self.j6show_lineEdit.clear()

    def anglemode_pushButton_clicked(self):
        """
        关节坐标显示模式
        :return:
        """
        self.set_return_data_mode(0)
        self.coordinate_display_mode_flag = 0
        self.xshow_lineEdit.clear()
        self.yshow_lineEdit.clear()
        self.zshow_lineEdit.clear()
        self.ashow_lineEdit.clear()
        self.bshow_lineEdit.clear()
        self.cshow_lineEdit.clear()

    def closeEvent(self, QCloseEvent):
        if self.is_connected():
            self.disconnect_sanxi()
        self.display_board_timer.cancel()  # 退出系统前停止其他线程和定时器
        QCoreApplication.quit()