# -*- coding: utf-8 -*-
#
# This file is part of the Qonda framework
# Qonda is (C)2012,2013 Julio César Gázquez
#
# Qonda is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Qonda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Qonda; If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from setuptools import setup

try:  # Python 3.x
    from setuptools.command.build_py import build_py_2to3 as build_py
except ImportError:  # Python 2.x
    from setuptools.command.build_py import build_py  # lint:ok
import sys
import subprocess


class build(build_py):

    def _compile_ui(self):
        print("Compiling Qt resource file")
        self.pyrcc4 = 'pyrcc4'

        if sys.version_info[0] == 2:
            option = '-py2'
        else:
            option = '-py3'

        try:
            subprocess.call([self.pyrcc4, option, 'icons/icons.qrc', '-o',
                             'icons/icons_rc.py'])
        except OSError:

            print("rcc command failed - make sure that pyrcc4 "
                  "or pyside-rcc4 is in your $PATH, or specify "
                  "a custom command with --rcc=command")

    def run(self):

        self._compile_ui()
        build_py.run(self)

cmdclass = {'build_py': build}

setup(
    name='qonda',
    version='0.6.4',
    description="A Model-View framework based on Qt Interview",
    author="Julio Cesar Gazquez",
    author_email='julio@mebamutual.com.ar',
    url='https://bitbucket.org/shulai/qonda',
    packages=['qonda', 'qonda.mvc', 'qonda.widgets',
        'qonda.util', 'qonda.sqlalchemy', 'qonda.icons'],
    package_dir={'qonda': '.'},
    use_2to3=True,
    long_description="""
    Qonda is a framework consisting in a set of classes to use Python models
    as Qt views.
    """,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later "
            "(GPLv2+)",
        "Environment :: X11 Applications :: Qt",
        "Environment :: X11 Applications :: KDE",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords='gui pyqt4',
    license='GPL',
    cmdclass=cmdclass
)
