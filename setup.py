# -*- coding: utf-8 -*-
"""
Created on 2020/4/22 10:45 PM
---------
@summary:
---------
@author: Boris
@email: boris@bzkj.tech
"""

from os.path import dirname, join
from sys import version_info

import setuptools

if version_info < (3, 0, 0):
    raise SystemExit("Sorry! jmpy requires python 3.0.0 or later.")

with open(join(dirname(__file__), "VERSION"), "rb") as f:
    version = f.read().decode("ascii").strip()

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = setuptools.find_packages()

setuptools.setup(
    name="jmpy3",
    version=version,
    author="Boris",
    license="MIT",
    author_email="boris@bzkj.tech",
    description="python代码一键加密",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["Cython==0.29.20"],
    entry_points={"console_scripts": ["jmpy = jmpy.cmdline:execute"]},
    url="https://github.com/Boris-code/jmpy.git",
    packages=packages,
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
)
