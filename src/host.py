#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Project Smat: System Modular Administration Tool
File name:    host.py
Description:  This class contain general information about hosted environment.

Copyright (c) since 2009 Lubos Kocman <lkocman@redhat.com>. All rights reserved.

"""

"""
This file is part of Smat.

Smat is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Smat is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Smat.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, sys
import smerr

class host:
    smat_home_var = "SMAT_HOME"
    smat_def_path = "/usr/share/smat/fpaths"
    comment_char = "#"
#---------------------------------------------------------------------------

    def __init__(self):
        self.get_smat_home()
        self.get_utsname()
        self.has_display()

#---------------------------------------------------------------------------
    def has_display(self):
        if os.getenv("DISPLAY") != None:
            self.display = True
        else:
            self.display = False
#---------------------------------------------------------------------------

    def get_utsname(self):
        "get_utsname()"
        utsname = os.uname()
        self.os_name = utsname[0] # uname -s
        self.os_release = utsname[2] # uname -r
        self.os_version = utsname[3] # uname -v
        self.platform = utsname[4] # uname -i
        del(utsname)

#---------------------------------------------------------------------------

    def get_smat_home(self):
        self.smat_home = os.getenv(host.smat_home_var, default = None)

        if self.smat_home == None:
            if os.path.exists(host.smat_def_path):
                self.smat_home = host.__smat_def_path
            else:
                raise sm_host_exception(smerr.ERROR_1 %(host.smat_def_path))

#---------------------------------------------------------------------------

class sm_host_exception(Exception):

#---------------------------------------------------------------------------

    def __init__(self, msg):
        self.value = msg

#---------------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)

#---------------------------------------------------------------------------

host_info = host()
