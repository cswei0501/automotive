# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2020, China TSP, All rights reserved
# --------------------------------------------------------
# @Name:        CRT
# @Purpose:     串口操作
# @Author:      liluo
# @Created:     2019-05-09
# --------------------------------------------------------
import serial
import serial.tools.list_ports as list_ports
import chardet
from time import sleep
from loguru import logger


class SerialPort(object):
    """
    串口类，用于基础的串口操作
    """

    def __init__(self):
        self._serial = None

    def check_status(func):
        """
        检查设备是否已经连接
        :param func: 装饰器函数
        """

        def wrapper(self, *args, **kwargs):
            if not (self._serial and self._serial.isOpen):
                raise RuntimeError("please connect serial first")
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def __detect_codec(string: bytes):
        """
        检测编码类型并返回

        :param string:输入的未解码的字符串

        :return  返回编码类型
        """
        encode = chardet.detect(string)
        logger.debug(f"codec is {encode['encoding']}")
        return encode['encoding']

    def __get_line(self, line: bytes, type_: bool = None) -> str:
        """
        获取一行数据

        :param line: 一行的数据

        :param type_: 类型

        :return 行数据
        """
        if type_ is None:
            return line.decode(self.__detect_codec(line))
        else:
            return line if type_ else line.decode("utf-8")

    def connect(self, port: str, baud_rate: int, byte_size: int = serial.EIGHTBITS, parity: str = serial.PARITY_NONE,
                stop_bits: int = serial.STOPBITS_ONE, xon_xoff: bool = False, rts_cts: bool = False,
                dsr_dtr: bool = False, timeout: float = 0.5, write_timeout: float = 3):
        """
        创建新的串口会话窗口、

        :param port: 串口端口：COM1， 必填

        :param baud_rate: 波特率必填
            (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,9600, 19200, 38400, 57600, 115200, 230400,
            460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000)

        :param byte_size:
            #数据位： (FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS)， 默认=EIGHTBITS

        :param parity:
            #奇偶校验位： (PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE)，默认=PARITY_NONE

        :param stop_bits:
            #停止位： one of (STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO)，默认=STOPBITS_ONE

        :param xon_xoff: #XONXOFF

        :param rts_cts: #RTSCTS

        :param dsr_dtr: #DTRDSR

        :param timeout: # 读取数据超时设置，必须设置，否则会block forever， 默认=0.5

        :param write_timeout: # 写入数据超时设置
        """
        if self.check_port(port):
            self._serial = serial.Serial(port=port, baudrate=baud_rate, bytesize=byte_size, parity=parity,
                                         stopbits=stop_bits, timeout=timeout, xonxoff=xon_xoff, rtscts=rts_cts,
                                         write_timeout=write_timeout, dsrdtr=dsr_dtr)
        else:
            raise RuntimeError(f"connect failed")
        sleep(1)

    def disconnect(self):
        """
        关闭串口
        """
        if self._serial:
            self._serial.close()
            self._serial = None

    @staticmethod
    def check_port(port: str) -> bool:
        """
        检测已连接的串口端口

        :param port: 用于连接串口的端口，检测该端口是否可用

        :return:
            True: 已连接

            False: 未连接
        """
        ports = {}
        for port_obj in list_ports.comports():
            ports[port_obj.device] = port_obj.description
        if port.upper() in ports.keys():
            return True
        logger.warning(f"un support COM port: {port}, should be one of :{ports}")
        return False

    @check_status
    def send(self, cmd: (bytes, str), type_: bool = True, end: str = '\r'):
        """
        发送命令到串口

        :param cmd: 发送的串口命令

        :param type_: 编码方式

            True: bytes模式

            False: string模式

        :param end:是否增加结束符，默认为为\r
        """
        cmd = cmd + end if end else cmd
        if type_:
            if not isinstance(cmd, bytes):
                cmd = cmd.encode("utf-8")
        self._serial.write(cmd)

    @check_status
    def send_break(self):
        """
        发送终止命令，停止打印
        """
        self._serial.sendBreak(duration=0.25)

    @check_status
    def read_bytes(self, byte_number: int = None, type_: bool = None) -> bytes:
        """
        读取串口输出，按byte读取

        :param byte_number: 读取的字节数，不写则默认1

        :param type_:

            True:不进行解码操作，直接返回

            False:以utf-8的方式进行解码并返回

            None: 自动检测编码格式，并自动解码后返回

        :return: 读取到的串口输出bytes
        """
        byte_ = self._serial.read(byte_number) if byte_number is not None else self._serial.read()
        if type_ is None:
            return byte_.decode(self.__detect_codec(byte_))
        else:
            return byte_.decode('utf-8') if type_ else byte_

    @check_status
    def read_line(self, type_: bool = None) -> str:
        """
        读取串口输出，按行读取，调用一次读取一行

        :param type_:

            True:不进行解码操作，直接返回

            False:以utf-8的方式进行解码并返回

            None: 自动检测编码格式，并自动解码后返回

        :return: 读取到的串口输出string
        """
        line = self._serial.readline()
        return self.__get_line(line, type_)

    @check_status
    def read_lines(self, type_: bool = None) -> list:
        """
        读取串口输出，读取所有行，返回列表

        :param type_:

            True:不进行解码操作，直接返回

            False:以utf-8的方式进行解码并返回

            None: 自动检测编码格式，并自动解码后返回

        :return: 读取到的串口输出list
        """
        lines = self._serial.readlines()
        result = []
        for line in lines:
            result.append(self.__get_line(line, type_))
        return result

    @check_status
    def read_all(self, type_: bool = None) -> str:
        """
        读取串口输出，一次性把所有输出读取

        :param type_:

            True:不进行解码操作，直接返回

            False:以utf-8的方式进行解码并返回

            None: 自动检测编码格式，并自动解码后返回

        :return: 读取到的串口输出string
        """
        all_lines = self._serial.readall()
        return self.__get_line(all_lines, type_)

    @check_status
    def in_waiting(self) -> int:
        """
        获取接收缓存区数据大小

        :return: 接收缓存区数据字节数:int
        """
        return self._serial.in_waiting

    @check_status
    def out_waiting(self) -> int:
        """
        获取写命令缓存区数据大小

        :return: 写命令缓存区数据字节数:int
        """
        return self._serial.out_waiting

    @check_status
    def flush(self):
        """
        清空所有缓存
        """
        self._serial.flush()

    @check_status
    def flush_input(self):
        """
        清空输入缓存
        """
        self._serial.flushInput()

    @check_status
    def flush_output(self):
        """
        清空输出缓存
        """
        self._serial.flushOutput()

    @check_status
    def reset_input_buffer(self):
        """
        清除串口输入缓存
        """
        self._serial.reset_input_buffer()

    @check_status
    def reset_output_buffer(self):
        """
        清除串口输出缓存
        """
        self._serial.reset_output_buffer()

    @check_status
    def set_buffer(self, rx_size: int = 4096, tx_size: int = 4096):
        """
        设置串口缓存大小，默认4096

        :param rx_size: 接收缓存区大小设置

        :param tx_size: 发送缓存区大小设置
        """
        self._serial.set_buffer_size(rx_size, tx_size)
