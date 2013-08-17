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

from setuptools import setup

setup(
    name='qonda',
    version='0.1',
    description="A Model-View framework based on Qt Interview",
    author="Julio Cesar Gazquez",
    author_email='julio@mebamutual.com.ar',
    url='http://jotacege.com.ar/qonda',
<<<<<<< local
    packages=['qonda', 'qonda.mvc', 'qonda.widgets', 'qonda.sqla',
        'qonda.mainwindow'],
=======
    packages=['qonda', 'qonda.mvc', 'qonda.widgets', 'qonda.mainwindow', 'qonda.util', 'qonda.sqlalchemy'],
>>>>>>> other
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
    license='GPL'
        )
