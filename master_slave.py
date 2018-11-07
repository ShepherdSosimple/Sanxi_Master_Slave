"""
This module includes the core functions of Geomagic touch haptic device.
Class:
Methods:
"""


from collections import deque
import threading
from ctypes import *

from geomagic_touch_core import GeoTouchLower
from sanxi_core import Sanxi


class GeoCtrlSanXi(Sanxi):
    def __init__(self):
        super(GeoCtrlSanXi, self).__init__()
        self.scaling_factor_position = 1
        self.scaling_factor_angle = 1
        self.touch_position_queue = deque(maxlen=2)
        self.touch_gimbal_angles_queue = deque(maxlen=2)
        # threading Timer
        self.ctrl_timer = None

    def start_ctrl(self):
        geo_touch.touch_handle = geo_touch.hd_init_device('Default Device')
        if geo_touch.touch_handle < 0:
            return False
        else:
            geo_touch.hd_schedule_synchronous(scheduler_call_back_func1)
            geo_touch.hd_start_scheduler()
            # threading Timer
            self.ctrl_timer = threading.Timer(0.08, self.touch_ctrl_sanxi_loop)
            self.ctrl_timer.start()
            return True

    def stop_ctrl(self):
        if geo_touch.touch_handle < 0:
            return False
        else:
            geo_touch.hd_stop_scheduler()
            self.ctrl_timer.cancel()

    def touch_ctrl_sanxi_loop(self):
        if geo_touch.touch_button_state == 0:
            # 空闲时清空差值列表
            self.touch_position_queue.clear()
            self.touch_gimbal_angles_queue.clear()
        elif geo_touch.touch_button_state == 1:
            self.adjust_orientation2()
        elif geo_touch.touch_button_state == 2:
            self.adjust_position()
        self.ctrl_timer = threading.Timer(0.08, self.touch_ctrl_sanxi_loop)
        self.ctrl_timer.start()

    def adjust_position(self):
        self.touch_position_queue.append(geo_touch.touch_current_position)
        if len(self.touch_position_queue) == 2:
            touch_delta_position = \
                [self.touch_position_queue[1][i] - self.touch_position_queue[0][i] for i in range(0, 3)]
            print('delta position is  ', touch_delta_position[0], touch_delta_position[1], touch_delta_position[2])
            if self.return_coord_mode != 1:
                self.set_return_data_mode(1)
            self.query_coord()
            sanxi_current_position = self.xyz_value
            print('Sanxi current position = ', self.xyz_value)
            if len(sanxi_current_position):
                sanxi_target_position_dict = \
                    {'X': sanxi_current_position[0] + touch_delta_position[2] * self.scaling_factor_position,
                     'Y': sanxi_current_position[1] + touch_delta_position[0] * self.scaling_factor_position,
                     'Z': sanxi_current_position[2] + touch_delta_position[1] * self.scaling_factor_position,
                     'A': sanxi_current_position[3],
                     'B': sanxi_current_position[4],
                     'C': sanxi_current_position[5],
                     'D': sanxi_current_position[6]}
                print('target-position is', sanxi_target_position_dict)
                self.rect_move(mode='line', **sanxi_target_position_dict)
                print('\n', '\n')

    def adjust_orientation2(self):
        self.touch_gimbal_angles_queue.append(geo_touch.touch_current_gimbal_angles)
        if len(self.touch_gimbal_angles_queue) == 2:
            touch_delta_gimbal_angles = \
                [self.touch_gimbal_angles_queue[1][i] - self.touch_gimbal_angles_queue[0][i] for i in range(0, 3)]
            if self.return_coord_mode != 0:
                self.set_return_data_mode(0)
            self.query_coord()
            sanxi_current_angle = self.jn_value
            if len(sanxi_current_angle):
                target_j4 = sanxi_current_angle[3] - touch_delta_gimbal_angles[0] * self.scaling_factor_angle
                target_j5 = sanxi_current_angle[4] + touch_delta_gimbal_angles[1] * self.scaling_factor_angle
                sanxi_target_angle_dict = {'J4': target_j4, 'J5': target_j5}
                self.multi_joints_motion(**sanxi_target_angle_dict)

    def adjust_orientation3(self):
        pass


@CFUNCTYPE(c_uint)
def scheduler_call_back_func1():
    """

    :return: None
    """
    geo_touch.touch_handle = geo_touch.hd_get_current_device()
    geo_touch.hd_begin_frame(geo_touch.touch_handle)
    geo_touch.touch_current_position = geo_touch.hd_get_current_position()
    geo_touch.touch_current_gimbal_angles = geo_touch.hd_get_current_gimbal_angles()
    geo_touch.touch_button_state = geo_touch.hd_get_current_buttons()
    geo_touch.hd_end_frame(geo_touch.touch_handle)
    return 1


geo_touch = GeoTouchLower()

if __name__ == '__main__':
    geo_ctrl_sanxi = GeoCtrlSanXi()
    geo_ctrl_sanxi.connect_sanxi(port_name='COM10')
    geo_ctrl_sanxi.set_motion_para(5, 30, 10)
    geo_ctrl_sanxi.start_ctrl()
