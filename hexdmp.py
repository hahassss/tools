# -*- coding:utf-8 -*-
"""
思路：有无参数—C，在其基础上增加其他参数控制
使用的Linux上面Python版本为3.4，所以字符串使用的+
"""
import argparse
import os

END_BYTE = b''  # 文件结束符
MAX_READ_BYTES = 8 * 1024  # 一次读取的最大字节数


class PrintHex(object):
    def __init__(self, is_big=True):
        self.is_big = is_big  # 默认大端
        self.hex_length = 16  # 16进制长度
        self.ascii_max = 126  # 最大显示的ascii编码
        self.ascii_min = 32  # 最小显示的ascii编码
        self.__count_16_00 = 0  # 缓冲16个字节的计数器，实现多行全为相同时只输出一行
        self.__cache_list = list()  # 缓冲16个字节，实现多行全为相同时只输出一行

    def default_arg(self, generator, s=0):
        """默认偏移0，默认读所有，默认大端
        :param generator:
        :param s:
        :return:
        """
        cache_16_bytes = list()  # 缓冲16个字节
        i = 0
        for i, int_byte in enumerate(generator, start=1):
            cache_16_bytes.append(int_byte)
            if i % self.hex_length == 0:  # 满16位进行处理
                self.__count_16_00, cache_16_hex = self.check_data(cache_16_bytes, 'not -C')
                if self.__count_16_00 >= 2:  # 多行数据相同，不处理
                    cache_16_bytes = list()
                    continue

                cache_16_hex = self.default_hex_big(cache_16_hex)
                self.default_show_str(i + s, cache_16_hex, cache_16_bytes)
                cache_16_bytes = list()
        # 最后剩下的再处理
        self.__count_16_00, cache_16_hex = self.check_data(cache_16_bytes, 'not -C')
        cache_16_hex = self.default_hex_big(cache_16_hex)
        self.default_show_str(i + s, cache_16_hex, cache_16_bytes)

    @classmethod
    def default_hex_big(cls, bytes_list):
        """大端位置调换
        :return:
        """
        bytes_length = len(bytes_list)
        if bytes_length == 1:  # 一个字节，补00
            return ['00' + bytes_list[-1]]
        _cache_list = list()
        for i in range(1, bytes_length + 1):
            if i % 2 == 0:
                _cache_list.append(bytes_list[i - 1] + bytes_list[i - 2])
        if bytes_length % 2 != 0:  # 长度为奇数时，补00
            _cache_list.append('00' + bytes_list[-1])
        return _cache_list

    def default_show_str(self, s, cache_16_hex, cache_16_bytes):
        if self.__count_16_00 == 1 and len(self.__cache_list) != 0:  # 多行相同
            print('*')
            return None
        elif self.__count_16_00 == 0 and len(cache_16_bytes) == self.hex_length:  # 正常输出
            print('{:07x} {:48}'.format(s - self.hex_length, ' '.join(cache_16_hex)))
            return None
        if len(cache_16_bytes) == 0:  # 刚好结束
            print('{:07x}'.format(s))
        elif len(cache_16_bytes) < self.hex_length:
            s = s - len(cache_16_bytes)
            print('{:07x} {:48}'.format(s, ' '.join(cache_16_hex)))
            s = s + len(cache_16_bytes)
            print('{:07x}'.format(s))

    def upper_c_arg(self, generator, s=0):
        """参数—C，默认偏移0，默认读所有，默认大端
        :param generator:
        :param s:
        :return:
        """

        cache_16_bytes = list()  # 缓冲16个字
        i = 0
        for i, int_byte in enumerate(generator, start=1):
            cache_16_bytes.append(int_byte)
            if i % self.hex_length == 0:  # 满16位进行处理
                self.__count_16_00, cache_16_hex = self.check_data(cache_16_bytes)
                if self.__count_16_00 >= 2:  # 多行数据相同，不处理
                    cache_16_bytes = list()
                    continue
                cache_16_bytes = self.cache_16_bytes_join(cache_16_bytes)
                self.upper_c_show_str(i + s, cache_16_hex, cache_16_bytes)
                cache_16_bytes = list()
        # 最后剩下的再处理
        self.__count_16_00, cache_16_hex = self.check_data(cache_16_bytes)
        cache_16_bytes = self.cache_16_bytes_join(cache_16_bytes)
        self.upper_c_show_str(i + s, cache_16_hex, cache_16_bytes)

    def check_data(self, cache_16_bytes, args='-C'):
        """校验相邻的两行是否相同，相同不处理，不相同进行数据处理
        """
        if self.__cache_list == cache_16_bytes:
            return self.__count_16_00 + 1, cache_16_bytes
        _cache_list = list()
        self.__cache_list = cache_16_bytes[:]
        for i, int_byte in enumerate(cache_16_bytes):  # 转为16进制
            data = hex(int_byte)[2:]
            if len(data) == 1:  # 对16进制只有1位的进行补0
                data = '0' + data
            if i == 8 and args == '-C':  # -C的时候中间才多一个空格
                data = ' ' + data
            _cache_list.append(data)
        return 0, _cache_list

    def cache_16_bytes_join(self, cache_16_bytes):
        """将换行符进行转义
        """
        _cache_list = list()
        for int_byte in cache_16_bytes:
            if int_byte > self.ascii_max or int_byte < self.ascii_min:  # 不能显示的用.替换
                _cache_list.append('.')
            else:
                _cache_list.append(chr(int_byte))
        return _cache_list

    def upper_c_show_str(self, s, cache_16_hex, cache_16_bytes):
        if self.__count_16_00 == 1 and len(self.__cache_list) != 0:  # 多行相同
            print('*')
            return None
        elif self.__count_16_00 == 0 and len(cache_16_bytes) == self.hex_length:  # 正常输出
            print('{:08x}  {:48}  |{}|'.format(s - self.hex_length, ' '.join(cache_16_hex), ''.join(cache_16_bytes)))
            return None

        if len(cache_16_bytes) == 0:  # 刚好结束
            print('{:08x}'.format(s))
        elif len(cache_16_bytes) < self.hex_length:
            s = s - len(cache_16_bytes)
            print('{:08x}  {:48}  |{}|'.format(s, ' '.join(cache_16_hex), ''.join(cache_16_bytes)))
            s = s + len(cache_16_bytes)
            print('{:08x}'.format(s))


def arg():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-C", "--C", action="store_true")
    parser.add_argument("-s", "--s", default='0')
    parser.add_argument("-n", "--n", default='-1')
    parser.add_argument("root", type=str, help="input file path")
    args = parser.parse_args()
    try:
        args.s = int(args.s)
        args.n = int(args.n)
        assert args.n >= 0
        assert args.s >= 0
    except Exception as e:
        _ = e
        print('input error')
        return None
    return args


def read_byte(root, n, s):
    try:
        with open(root, 'rb') as f:
            f.seek(s)
            count = 0  # 字节计数器
            while True:
                data_byte = f.read(MAX_READ_BYTES)
                if data_byte == END_BYTE:
                    return None

                for int_byte in data_byte:
                    count = count + 1
                    yield int_byte
                    if n == count or n == 0:  # 文件读取到第n个字节退出
                        return None

    except Exception as e:
        print(e)
        return None


def change_s(root, s):
    """修正s，有些文件读不出大小就为0，就打开读第一个字节来判断到底有没有数据
    :param root:
    :param s:
    :return:
    """
    size = os.path.getsize(root)
    if size == 0:
        try:
            with open(root, 'rb') as f:
                if f.read(1) != END_BYTE:
                    return s
        except Exception as e:
            _ = e

    if s > size:
        return size
    return s


def main():
    args = arg()
    if args is None or args.n == 0:
        return None
    s = change_s(args.root, args.s)
    generator = read_byte(args.root, args.n, s)
    if generator is None:
        return None
    p_hex = PrintHex()
    if args.C is True:
        p_hex.upper_c_arg(generator, s)
    else:
        p_hex.default_arg(generator, s)


if __name__ == '__main__':
    main()
