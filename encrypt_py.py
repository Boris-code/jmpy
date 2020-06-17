# -*- coding: utf-8 -*-
"""
Created on 2018-07-18 18:24
---------
@summary: 加密python代码为pyd/so
---------
@author: Boris
"""
import getopt
import os
import re
import shutil
import sys
import tempfile
from distutils.core import setup
from typing import Union, List

from Cython.Build import cythonize


class TemporaryDirectory(object):
    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


_regexs = {}


def find_msg(text, regexs, allow_repeat=False, fetch_one=False, split=None):
    regexs = isinstance(regexs, str) and [regexs] or regexs

    infos = []
    for regex in regexs:
        if regex == "":
            continue

        if regex not in _regexs.keys():
            _regexs[regex] = re.compile(regex, re.S)

        if fetch_one:
            infos = _regexs[regex].search(text)
            if infos:
                infos = infos.groups()
            else:
                continue
        else:
            infos = _regexs[regex].findall(str(text))

        if len(infos) > 0:
            break

    if fetch_one:
        infos = infos if infos else ("",)
        return infos if len(infos) > 1 else infos[0]
    else:
        infos = allow_repeat and infos or sorted(set(infos), key=infos.index)
        infos = split.join(infos) if split else infos
        return infos


def walk_file(file_path):
    if os.path.isdir(file_path):
        for current_path, sub_folders, files_name in os.walk(file_path):
            for file in files_name:
                file_path = os.path.join(current_path, file)
                yield file_path

    else:
        yield file_path


def copy_files(src_path, dst_path):
    if os.path.isdir(src_path):
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)

        def callable(src, names: list):
            if find_msg(src, dst_path):
                return names
            return ["dist", ".git", "venv", ".idea"]

        shutil.copytree(src_path, dst_path, ignore=callable)
    else:
        shutil.copyfile(src_path, os.path.join(dst_path, os.path.basename(src_path)))


def get_py_files(files, ignore_files: Union[List, str, None] = None):
    """
    @summary:
    ---------
    @param files: 文件列表
    #param ignore_files: 忽略的文件，支持正则
    ---------
    @result:
    """
    for file in files:
        if file.endswith(".py"):
            if ignore_files and find_msg(file, regexs=ignore_files):  # 该文件是忽略的文件
                pass
            else:
                yield file


def filter_cannot_encrypted_py(files):
    """
    过滤掉不能加密的文件，如 __init__.py __main__.py 以及包含 if __name__ == "__main__": 的文件
    Args:
        files:

    Returns:

    """
    _files = []
    for file in files:
        if find_msg(file, regexs=["__init__.py", "__main__.py"]):
            continue

        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            if find_msg(content, regexs=['if __name__ == "__main__":']):
                continue

        _files.append(file)

    return _files


def encrypt_py(py_files: list):

    with TemporaryDirectory() as td:
        for py_file in py_files:
            dir_name = os.path.dirname(py_file)
            file_name = os.path.basename(py_file)

            os.chdir(dir_name)

            print("正在加密 ", file_name)

            setup(
                ext_modules=cythonize([file_name]),
                script_args=["build_ext", "--inplace", "-t", td],
            )

            print("-" * 40 + "\n")


def delete_files(files_path):
    """
    @summary: 删除文件
    ---------
    @param files_path: 文件路径 py 及 c 文件
    ---------
    @result:
    """
    try:
        # 删除python文件及c文件
        for file in files_path:
            os.remove(file)  # py文件
            os.remove(file.replace(".py", ".c"))  # c文件

    except Exception as e:
        pass


def rename_excrypted_file(output_file_path):
    files = walk_file(output_file_path)
    for file in files:
        if ".cpython-" in file:
            new_filename = re.sub(r"cpython-.+\.", "", file)
            os.rename(file, new_filename)


def start_encrypt(
    input_file_path,
    output_file_path: str = None,
    ignore_files: Union[List, str, None] = None,
):
    if output_file_path and not os.path.isdir(output_file_path):
        raise ValueError("output_file_path need a dir path")

    input_file_path = os.path.abspath(input_file_path)
    if not output_file_path:  # 无输出路径
        if os.path.isdir(
            input_file_path
        ):  # 如果输入路径是文件夹 则输出路径为input_file_path/dist/project_name
            output_file_path = os.path.join(
                input_file_path, "dist", os.path.basename(input_file_path)
            )
        else:
            output_file_path = os.path.join(os.path.dirname(input_file_path), "dist")
    else:
        output_file_path = os.path.abspath(input_file_path)

    # 拷贝原文件到目标文件
    copy_files(input_file_path, output_file_path)

    files = walk_file(output_file_path)
    py_files = get_py_files(files, ignore_files)

    # 过滤掉不需要加密的文件，__int__.py 及 包含 if __name__ == "__main__": 的文件不加密
    need_encrypted_py = filter_cannot_encrypted_py(py_files)

    encrypt_py(need_encrypted_py)

    delete_files(need_encrypted_py)
    rename_excrypted_file(output_file_path)

    print("加密完成 生成到 %s" % output_file_path)


def usage():
    """
python 加密
参数说明：
    -i  | --input_file_path    待加密文件或文件夹路径，可是相对路径或绝对路径
    -o  | --output_file_path   加密后的文件或文件夹输出路径，默认在input_file_path下创建dist文件夹，存放加密后的文件
    -I  | --ignore_files       不需要加密的文件，逗号分隔，如 main.py。 程序入口加密后无法启动程序
    """


if __name__ == "__main__":
    options, args = getopt.getopt(
        sys.argv[1:],
        "h:i:o:ig",
        ["help", "input_file_path=", "output_file_path=", "ignore_files="],
    )

    input_file_path = output_file_path = ignore_files = ""

    # print(input_file_path, output_file_path)

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
