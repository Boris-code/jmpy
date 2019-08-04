# -*- coding: utf-8 -*-
'''
Created on 2018-07-18 18:24
---------
@summary: 加密python代码为pyd/so
---------
@author: Boris
'''
from distutils.core import setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import shutil
import getopt
import re
import sys
import os

CURRENT_PATH = os.path.abspath('.')

# 正则相关
_regexs = {}


def find_msg(text, regexs, allow_repeat=False, fetch_one=False, split=None):
    regexs = isinstance(regexs, str) and [regexs] or regexs

    infos = []
    for regex in regexs:
        if regex == '':
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
        infos = infos if infos else ('',)
        return infos if len(infos) > 1 else infos[0]
    else:
        infos = allow_repeat and infos or sorted(set(infos), key=infos.index)
        infos = split.join(infos) if split else infos
        return infos

# 文件相关


def get_abs_path(file_path, parent_path=CURRENT_PATH):
    return os.path.join(parent_path, file_path)


def walk_file(file_path):
    if os.path.isdir(file_path):
        for current_path, sub_folders, files_name in os.walk(file_path):
            # current_path 当前文件夹路径
            # sub_folders 当前路径下的子文件夹
            # files_name 当前路径下的文件

            for file in files_name:
                file_path = os.path.join(current_path, file)
                yield file_path

    else:
        yield file_path


def bak_files(files, bak_files=[]):
    bak_files.append('__init__.py')

    for file in files:
        if find_msg(file, regexs=bak_files):
            os.rename(file, file + '_bak')


def recover_files(files, bak_files=[]):
    bak_files.append('__init__.py')

    for file in files:
        if find_msg(file, regexs=bak_files):
            os.rename(file + '_bak', file)


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        pass


def copy_files(src_path, dst_path):
    if dst_path.endswith('.py'):
        directory = os.path.dirname(dst_path)
    else:
        directory = dst_path

    mkdir(directory)

    if os.path.isdir(src_path):
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path)
    else:
        shutil.copyfile(src_path, dst_path)


def get_py_files(files, ignore_files=[]):
    '''
    @summary:
    ---------
    @param files: 文件列表
    #param ignore_files: 忽略的文件，支持正则
    ---------
    @result:
    '''
    for file in files:
        if file.endswith('.py'):
            if find_msg(file, regexs=ignore_files):  # 该文件是忽略的文件
                pass
            else:
                yield file


def encrypt_pys(py_files, temp_file_path):

    for py_file in py_files:
        dir_name = os.path.dirname(py_file)
        file_name = os.path.basename(py_file)

        if file_name == '__init__.py':
            continue

        os.chdir(dir_name)

        print('正在加密 ', file_name)

        setup(
            ext_modules=cythonize([file_name]),
            script_args=["build_ext", '--inplace', "-t", temp_file_path],
        )

        print('-' * 40 + '\n')


def delete_files(files_path, temp_file_path):
    '''
    @summary: 删除文件
    ---------
    @param files_path: 文件路径 py 及 c 文件
    @param temp_file_path: 临时文件路径
    ---------
    @result:
    '''
    try:

        shutil.rmtree(temp_file_path)

        # 删除python文件及c文件
        for file in files_path:
            if file.endswith('__init__.py'):
                continue

            os.remove(file)  # py文件
            os.remove(file.replace('.py', '.c'))  # c文件

    except Exception as e:
        pass


def rename_excrypt_file(output_file_path):
    files = walk_file(output_file_path)
    for file in files:
        if '.cpython-' in file:
            new_filename = re.sub(r'cpython-.+\.', '', file)
            os.rename(file, new_filename)


def start_encrypt(input_file_path, output_file_path, ignore_files):
    temp_file_path = '.temp'

    input_file_path = get_abs_path(input_file_path)
    if not output_file_path:  # 无输出路径
        if os.path.isdir(input_file_path):  # 如果输入路径是文件夹 则输出路径为input_file_path/encrypted
            output_file_path = get_abs_path('encrypted', parent_path=input_file_path)
        else:
            output_file_path = get_abs_path(get_abs_path(os.path.basename(input_file_path), 'encrypted'), os.path.dirname(input_file_path))  # 如果输入是文件 则输出文件路径为当前文件目录下的build路径

    else:
        output_file_path = get_abs_path(output_file_path)
        if os.path.isfile(input_file_path) and not output_file_path.endswith('.py'):  # 如果输入路径为文件，且输出路径无文件名，则输出路径补充上文件名
            output_file_path = get_abs_path(os.path.basename(input_file_path), output_file_path)

    # if not output_file_path.endswith('.py'): # 以原工程文件夹命名 当不指定输入路径时，拷贝文件夹出现死循环
    #     output_file_path = get_abs_path(os.path.basename(input_file_path), output_file_path)

    if not output_file_path.endswith('.py'):  # 临时文件位置 输出路径为文件夹 则在输出路径文件夹下创建.temp
        temp_file_path = get_abs_path(temp_file_path, parent_path=output_file_path)
    else:  # 输入路径为文件 则在文件同级目录创建.temp
        temp_file_path = get_abs_path(temp_file_path, parent_path=os.path.dirname(output_file_path))

    # 拷贝原文件到目标文件
    copy_files(input_file_path, output_file_path)

    files = walk_file(output_file_path)
    py_files = get_py_files(files, ignore_files)
    py_files = list(py_files)  # 转为list，防止generator遍历一次就清空

    bak_files(py_files)  # 备份不需要加密的文件，__int__.py必须备份，改成__init__py_bak 否则影响加密
    encrypt_pys(py_files, temp_file_path)
    recover_files(py_files)

    delete_files(py_files, temp_file_path)
    rename_excrypt_file(output_file_path)

    print('加密完成 生成到 %s' % output_file_path)


def usage():
    '''
python 加密
参数说明：
    -i  | --input_file_path    待加密文件或文件夹路径，可是相对路径或绝对路径
    -o  | --output_file_path   加密后的文件或文件夹输出路径，默认在input_file_path下创建build文件夹，存放加密后的文件
    -I  | --ignore_files       不需要加密的文件，逗号分隔，如 main.py。 程序入口加密后无法启动程序
    '''

if __name__ == '__main__':
    options, args = getopt.getopt(sys.argv[1:], "h:i:o:ig", ["help", "input_file_path=", "output_file_path=", "ignore_files="])

    input_file_path = output_file_path = ignore_files = ''

    # print(input_file_path, output_file_path)

    for name, value in options:
        if name in ('-h', '--help'):
            print(usage.__doc__)
            sys.exit()

        elif name in ('-I', '--ignore_files'):
            ignore_files = value.split(',')

        elif name in ('-i', '--input_file_path'):
            input_file_path = value

        elif name in ('-o', '--output_file_path'):
            output_file_path = value

    if not input_file_path:
        print(usage.__doc__)
        sys.exit()

    # input_file_path = r'/Users/liubo/Workspaces/Python/encrypt-code/test.py'
    # output_file_path =r'/Users/liubo/Workspaces/Python/encrypt-code/hhh/'

    start_encrypt(input_file_path, output_file_path, ignore_files)
