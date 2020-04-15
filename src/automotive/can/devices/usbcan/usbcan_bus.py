# -*- coding:utf-8 -*-
# --------------------------------------------------------  
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------                 
# @Name:        usbcan_bus  
# @Purpose:     UsbCanBus
# @Author:      lizhe  
# @Created:     2019/12/2 12:57  
# --------------------------------------------------------
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from .usb_can import UsbCan
from automotive.can.interfaces import CanBus, CanBoxDevice, Message


class UsbCanBus(CanBus):
    """
    实现CANBus接口，能够多线程发送和接收can信号
    """

    def __init__(self, can_box_device: CanBoxDevice):
        super().__init__()
        # 线程池句柄
        self.__thread_pool = None
        # PCAN实例化
        self.__usbcan = UsbCan(can_box_device)
        # Default TimeStamp有效
        self.__time_flag = 1

    @staticmethod
    def __get_data(data, length: int) -> list:
        """
        转换pcan收的data为list

        :param data: 收到的data数据

        :param length:  长度

        :return: 8byte的列表
        """
        msg_data = []
        for i in range(length):
            msg_data.append(data[i])
        return msg_data

    @staticmethod
    def __get_reserved(reserved_value) -> list:
        """
        获取reversed参数

        :param reserved_value:  reversed的内容(can上收到的)

        :return: 解析后的列表
        """
        reserved_list = []
        for i in range(3):
            reserved_list.append(reserved_value[i])
        return reserved_list

    def __get_message(self, message) -> Message:
        """
        获取message对象

        :param message: message信息

        :return: PeakCanMessage对象
        """
        msg = Message()
        msg.msg_id = message.id
        msg.time_stamp = hex(message.time_stamp)
        msg.time_flag = message.time_flag
        msg.send_type = message.usb_can_send_type
        msg.remote_flag = message.remote_flag
        msg.external_flag = message.extern_flag
        msg.reserved = self.__get_reserved(message.reserved)
        msg.data_length = 8 if message.data_len > 8 else message.data_len
        msg.data = self.__get_data(message.data, msg.data_length)
        return msg

    def __receive(self):
        """
        CAN接收帧函数，在接收线程中执行
        """
        while self.__usbcan.is_open:
            try:
                ret, p_receive = self.__usbcan.receive()
                for i in range(ret):
                    receive_message = self.__get_message(p_receive[i])
                    logger.trace(f"msg id = {receive_message.msg_id}")
                    # 单帧数据
                    if receive_message.external_flag == 0:
                        # 获取数据并保存到self._receive_msg字典中
                        self._receive_messages[receive_message.msg_id] = receive_message
                        if len(self._stack) == self._max_stack:
                            self._stack.pop()
                        else:
                            logger.trace(f"stack size is {len(self._stack)}")
                            self._stack.append(receive_message)
                    # 扩展帧
                    else:
                        logger.debug("type is external frame, not implement")
            except RuntimeError:
                continue

    def __transmit(self, message: Message):
        """
        CAN发送帧函数，在线程中执行。

        :param message: Message对象
        """
        logger.trace(f"usb can status is {self.__usbcan.is_open}")
        msg_id = message.msg_id
        while self.__usbcan.is_open and not message.stop_flag:
            logger.trace(f"send msg {hex(msg_id)} and cycle time is {message.cycle_time}")
            self.__usbcan.transmit(message)

            # 循环发送的等待周期
            sleep(message.cycle_time / 1000.0)

    def __cycle_msg(self, message: Message):
        """
        发送周期性型号

        :param message: message的集合对象
        """
        msg_id = message.msg_id
        # 周期信号
        self._send_messages[msg_id] = message
        # 周期性发送
        logger.info(f"****** Transmit msg id {hex(msg_id)} Circle time is {message.cycle_time}ms ******")
        self.__thread_pool.submit(self.__transmit, message)

    def __event(self, message: Message):
        """
        发送事件信号

        :param message: message的集合对象
        """
        msg_id = message.msg_id
        # 事件信号
        for i in range(message.cycle_time_fast_times):
            logger.trace(f"****** Transmit msg id {hex(msg_id)} Once ******")
            self.__usbcan.transmit(message)
            sleep(message.cycle_time_fast / 1000.0)

    def open_can(self):
        """
        对CAN设备进行打开、初始化等操作，并同时开启设备的帧接收线程。
        """
        # 设置线程池，最大线程数为100
        self.__thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)
        # 打开设备，并初始化设备
        self.__usbcan.open_device()
        # 开启设备的接收线程
        # 把接收函数submit到线程池中
        self.__thread_pool.submit(self.__receive)

    def close_can(self):
        """
        关闭USB CAN设备。
        """
        self.__usbcan.close_device()

    def transmit(self, message: Message):
        """
        发送CAN帧函数。

        TODO: 延时没有实现

        :param message: message对象
        """
        msg_id = message.msg_id
        message.usb_can_send_type = 1
        if message.msg_send_type == self._cycle:
            # 周期信号
            self.__cycle_msg(message)
        elif message.msg_send_type == self._event:
            # 事件信号
            self.__event(message)
        else:
            # 周期信号
            if msg_id not in self._send_messages:
                self.__cycle_msg(message)
            # 暂停已发送的消息
            self._send_messages[msg_id].stop_flag = True
            self.__event(message)
            # 发送完成了周期性事件信号，恢复信号发送
            self._send_messages[msg_id].stop_flag = False
            self.__cycle_msg(message)

    def stop_transmit(self, msg_id: int = None):
        """
        停止某一帧CAN数据的发送。(当message_id为None时候停止所有发送的CAN数据)

        :param msg_id: 停止发送的Message的ID
        """
        logger.trace(f"send message list size is {len(self._send_messages)}")
        if msg_id:
            logger.trace(f"try to stop message {hex(msg_id)}")
            if msg_id in self._send_messages:
                logger.info(f"Message <{hex(msg_id)}> is stop to send.")
                self._send_messages[msg_id].stop_flag = True
            else:
                logger.error(f"Please check message id, Message <{hex(msg_id)}> is not contain.")
        else:
            logger.trace(f"try to stop all messages")
            for key, item in self._send_messages.items():
                logger.info(f"Message <{hex(key)}> is stop to send.")
                item.stop_flag = True

    def resume_transmit(self, msg_id: int = None):
        """
        恢复某一帧数据的发送函数。

        :param msg_id:停止发送的Message的ID
        """
        if msg_id:
            logger.trace(f"try to resume message {hex(msg_id)}")
            if msg_id in self._send_messages:
                logger.info(f"Message <{hex(msg_id)}> is resume to send.")
                pcan_message = self._send_messages[msg_id]
                pcan_message.stop_flag = False
                self.transmit(pcan_message)
            else:
                logger.error(f"Please check message id, Message <{hex(msg_id)}> is not contain.")
        else:
            logger.trace(f"try to resume all messages")
            for key, item in self._send_messages.items():
                logger.info(f"Message <{hex(key)}> is resume to send.")
                item.stop_flag = False
                self.transmit(item)

    def receive(self, msg_id: int) -> Message:
        """
        接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据。

        :param msg_id: 接收所需Message的ID

        :return: Message对象
        """
        if msg_id in self._receive_messages:
            return self._receive_messages[msg_id]
        else:
            raise RuntimeError(f"message_id {msg_id} not receive")

    def is_open(self) -> bool:
        """
        CAN设备是否被打开

        :return:
            True 打开

            False 关闭
        """
        return self.__usbcan.is_open

    def get_stack(self) -> list:
        """
         获取CAN的stack
        """
        return self._stack

    def clear_stack_data(self):
        """
        清除栈数据
        """
        self._stack.clear()

    def set_stack_size(self, size: int):
        """
        设置栈大小

        :param size: 用于定义最大的保存数据数量
        """
        self._max_stack = size
