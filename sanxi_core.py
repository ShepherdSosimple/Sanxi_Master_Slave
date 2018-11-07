"""
This module includes the core functions of SANXI robot
Class: Sanxi, whose base class is RS232 in communication.py module
Functions: search_origin()

Author: Mr SoSimple
"""


import time
import re

from communication import RS232


class Sanxi(RS232):
    __VE_MAX = 250000  # 最大速度
    __AC_MAX = 250000  # 最大加速度
    __DE_MAX = 250000  # 最大减速度

    def __init__(self):
        super(Sanxi, self).__init__()
        self.current_mode = 10
        self.all_return_code = ''  # Sanxi串口的所有返回數據
        self.new_return_code = ''  # Sanxi串口新添的返回数据
        self.return_coord_mode = 1  # 返回坐标值模式：1-cartesian space 0-joint space
        self.jn_value = []  # 伪实时关节空间坐标值
        self.xyz_value = []  # 伪实时笛卡尔空间坐标值
        # 正则表达式预编译
        # self.G_detect_pattern = re.compile(r'.*G.*')  # 检测 G字符 与下面表达式联合抽取返回的坐标值
        self.jn_pattern = re.compile('.*J1=(.*) J2=(.*) J3=(.*) J4=(.*) J5=(.*) J6=(.*)\r\s')
        self.xyz_pattern = re.compile('.*X=(.*) Y=(.*) Z=(.*) A=(.*) B=(.*) C=(.*) D=(.*)\r\s')

    def connect_sanxi(self, port_name):
        """
        连接三喜机器人
        :param port_name: string，串口名称 example：port_name='COM3'
        :return: Bool
        """
        self.set_port(port_name)
        self.set_baud_rate(115200)
        self.set_timeout(0.05)
        if self.connect() is True:
            self.change_to_mode14()  # 初始化为模式14
            self.set_return_data_mode()  # 初始化返回坐标模式为 cartesian space
            return True
        else:
            return False

    def query_current_mode(self):
        """
        向串口发送模式询问指令
        :return: int 0-询问失败 10-空闲模式 14-调试模式 15-复位模式 12-回零模式 11-文件模式
        """
        self.send_cmd('\x05', 0.001)
        if self.new_return_code == '\x10':
            # 空闲模式
            self.current_mode = 10
            return 10
        elif self.new_return_code == '\x14':
            # 调试模式
            self.current_mode = 14
            return 14
        elif self.new_return_code == '\x15':
            # 复位模式
            self.current_mode = 15
            return 15
        elif self.new_return_code == '\x12':
            # 回零模式
            self.current_mode = 12
            return 12
        elif self.new_return_code == '\x11':
            # 文件模式
            self.current_mode = 11
            return 11
        else:
            return 0

    def send_cmd(self, send_code, delay_time, has_return_code=True):
        """
        统一管理命令发送，延迟delay_time之后更新串口消息
        :param send_code: str  要发送的字符串
        :param delay_time: int 延迟接收串口返回的时间
        :param has_return_code: Bool 是否更新串口返回的数据，一般只在串口无返回消息时设为假
        :return:
        """
        self._send(send_code)
        time.sleep(delay_time)
        if has_return_code is True:
            self._update_return_code()

    def _update_return_code(self):
        """
        更新串口消息
        :return:
        """
        self.new_return_code = self._receive_all()
        self.all_return_code = self.all_return_code + self.new_return_code

    def set_return_data_mode(self, mode=1):
        """
        设置返回数据模式，直角坐标模式 或 关节坐标模式，默认前者
        :param mode: int 1-cartesian space 0-joint space
        :return: Bool
        """
        if mode == 1:
            if self.return_coord_mode == 0:
                self.jn_value.clear()
            self.send_cmd('G07 GCM=1\n', 0.003)
            self.return_coord_mode = 1
            return True
        elif mode == 0:
            if self.return_coord_mode == 1:
                self.xyz_value.clear()
            self.send_cmd('G07 GCM=0\n', 0.003)
            self.return_coord_mode = 0
            return True
        else:
            return False

    def query_coord(self):
        print('into query coord func!')
        self.freeze_motion()
        if self.current_mode != 14:
            self.change_to_mode14()
        self.send_cmd('\x30', 0.014)
        self._extract_output_info()
        if self.return_coord_mode == 1:
            return self.xyz_value
        elif self.return_coord_mode == 0:
            return self.jn_value
        else:
            return False

    def disconnect_sanxi(self):
        """
        停止运动，转为空闲模式，断开三喜机器人串口连接
        :return: Bool
        """
        self.stop_then_into_free_mode()
        self.new_return_code = ''
        self.all_return_code = ''
        if self.disconnect():
            return True
        else:
            return False

    def set_motion_para(self, vep, acp, dep):
        """
        设置运动参数
        :param vep: 速度百分比
        :param acp: 加速度百分比
        :param dep: 减速度百分比
        :return: None
        """
        if self.current_mode != 14:
            self.change_to_mode14()
        ve = vep * self.__VE_MAX / 100
        ac = acp * self.__AC_MAX / 100
        de = dep * self.__DE_MAX / 100
        self.send_cmd('G07 VE={}\n'.format(str(ve)), 0.004)
        self.send_cmd('G07 AC={}\n'.format(str(ac)), 0.004)
        self.send_cmd('G07 DE={}\n'.format(str(de)), 0.004)

    def _extract_output_info(self):
        """
        接收返回消息并抽取返回消息中的坐标信息
        :return: None
        """
        print('into extract func')
        print(self.new_return_code)
        jn_match = self.jn_pattern.match(str(self.new_return_code))  # 正则表达式匹配
        xyz_match = self.xyz_pattern.match(str(self.new_return_code))
        if jn_match:
            self.jn_value.clear()
            for i in range(1, 7):
                self.jn_value.append(float(jn_match.group(i)))
        if xyz_match:
            self.xyz_value.clear()
            for i in range(1, 8):
                self.xyz_value.append(float(xyz_match.group(i)))
            print('extracted xyz', self.xyz_value[0], self.xyz_value[1], '...')

    def change_to_mode14(self):
        self.freeze_motion()
        self.send_cmd('\x10', 0.002)
        self.send_cmd('\x14', 0.002)
        self.current_mode = 14

    def search_origin(self):
        """
        启动搜寻原点内置程序，原理：限位光电开关
        :return: None
        """
        self.freeze_motion()
        self.send_cmd('\x10', 0.002)
        self.send_cmd('\x12', 0.001)
        self.current_mode = 10

    def back2origin(self):
        """
        复位：回到原点
        :return: None
        """
        self.freeze_motion()
        self.send_cmd('\x10', 0.002)
        self.send_cmd('\x15', 0.002)
        self.current_mode = 15

    def rect_move(self, mode, **rect_dict):
        """
        直角坐标运动，点对点, 或直线
        :param mode: mode='p2p' OR mode='line'
        :param rect_dict: 字典——直角坐标目标值，{'X': float, ...}
        :return:
        """
        send_data = ''
        if mode == 'p2p':
            send_data += 'G20 '
        if mode == 'line':
            send_data += 'G21 '
        all_keys = ['X', 'Y', 'Z', 'A', 'B', 'C', 'D']
        for key in all_keys:
            if rect_dict[key] and (rect_dict[key] != ' '):
                send_data += '{0}={1} '.format(key, str(round(rect_dict[key], 2)))
        send_data += '\n'
        if self.current_mode != 14:
            self.change_to_mode14()
        self.send_cmd(send_data, 0.014)

    def multi_joints_motion(self, **j_dict):
        """
        关节运动，点对点
        :param j_dict: 字典——六轴目标值，{'J*': float, ...}
        :return:
        """
        send_data = 'G00 '
        for key in j_dict.keys():
            if key == 'J1':
                if j_dict[key] > 160:
                    j_dict[key] = 160
                    print('WARNING: Joint 1 is higher than the upper limit!')
                elif j_dict[key] < -160:
                    j_dict[key] = -160
                    print('WARNING: Joint 1 is lower than the lower limit!')
            elif key == 'J2':
                if j_dict[key] > 118:
                    j_dict[key] = 118
                    print('WARNING: Joint 2 is higher than the upper limit!')
                elif j_dict[key] < -130:
                    j_dict[key] = -130
                    print('WARNING: Joint 2 is lower than the lower limit!')
            elif key == 'J3':
                if j_dict[key] > 15:
                    j_dict[key] = 15
                    print('WARNING: Joint 3 is higher than the upper limit!')
                elif j_dict[key] < -180:
                    j_dict[key] = -180
                    print('WARNING: Joint 3 is lower than the lower limit!')
            elif key == 'J4':
                if j_dict[key] > 140:
                    j_dict[key] = 140
                    print('WARNING: Joint 4 is higher than the upper limit!')
                elif j_dict[key] < -140:
                    j_dict[key] = -140
                    print('WARNING: Joint 4 is lower than the lower limit!')
            elif key == 'J5':
                if j_dict[key] > 90:
                    j_dict[key] = 90
                    print('WARNING: Joint 5 is higher than the upper limit!')
                elif j_dict[key] < -130:
                    j_dict[key] = -130
                    print('WARNING: Joint 5 is lower than the lower limit!')
            send_data += '{0}={1} '.format(key, str(round(j_dict[key], 2)))
        send_data += '\n'
        if self.current_mode != 14:
            self.change_to_mode14()
        self.send_cmd(send_data, 0.014)

    def single_joint_motion_start(self, n, is_positive):
        """
        第n轴单轴运动
        :param n: 第n轴单动，eg 1   代表第一轴
        :param is_positive: True-顺时针或 向上, False-逆时针或向下
        :return:
        """
        if n in [2, 3, 5]:
            if is_positive:
                send_data = 'J{}+\n'.format(str(n))
            else:
                send_data = 'J{}-\n'.format(str(n))
        else:
            if is_positive:
                send_data = 'J{}-\n'.format(str(n))
            else:
                send_data = 'J{}+\n'.format(str(n))
        if self.current_mode != 14:
            self.change_to_mode14()
        self.send_cmd(send_data, 0.001, False)

    def single_joint_motion_stop(self, n):
        """
        第n轴停止单轴运动
        :param n: 第n轴停止单动，eg 1   代表第一轴
        :return:
        """
        send_data = 'J{}0\n'.format(str(n))
        self._send(send_data)
        time.sleep(0.002)
        self.send_cmd(send_data, 0.001, False)

    def freeze_motion(self):
        self.send_cmd('\x30', 0.014)

    def stop_then_into_free_mode(self):
        """
        终止运动，并退出当前模式，设置为空闲模式-0x10
        :return: None
        """
        self.freeze_motion()
        self.send_cmd('\x10', 0.002)
        self.current_mode = 10


if __name__ == '__main__':
    sanxi = Sanxi()
    sanxi.connect_sanxi('COM10')
