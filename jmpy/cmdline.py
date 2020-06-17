# -*- coding: utf-8 -*-
"""
Created on 2020/6/17 6:55 下午
---------
@summary:
---------
@author: Boris
"""
import getopt
import sys

from jmpy.encrypt_py import start_encrypt


def usage():
    """
python 加密
参数说明：
    -i  | --input_file_path    待加密文件或文件夹路径，可是相对路径或绝对路径
    -o  | --output_file_path   加密后的文件输出路径，默认在input_file_path下创建dist文件夹，存放加密后的文件
    -I  | --ignore_files       不需要加密的文件，逗号分隔
    """


def execute():
    options, args = getopt.getopt(
        sys.argv[1:],
        "h:i:o:ig",
        ["help", "input_file_path=", "output_file_path=", "ignore_files="],
    )

    input_file_path = output_file_path = ignore_files = ""

    for name, value in options:
        if name in ("-h", "--help"):
            print(usage.__doc__)
            sys.exit()

        elif name in ("-I", "--ignore_files"):
            ignore_files = value.split(",")

        elif name in ("-i", "--input_file_path"):
            input_file_path = value

        elif name in ("-o", "--output_file_path"):
            output_file_path = value

    if not input_file_path:
        print(usage.__doc__)
        sys.exit()

    start_encrypt(input_file_path, output_file_path, ignore_files)
