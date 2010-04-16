#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
CDDL HEADER START

The contents of this file are subject to the terms of the
Common Development and Distribution License (the "License").
You may not use this file except in compliance with the License.

You can obtain a copy of the license at src/SMAT.LICENSE
or http://www.opensolaris.org/os/licensing.
See the License for the specific language governing permissions
and limitations under the License.

When distributing Covered Code, include this CDDL HEADER in each
file and include the License file at src/SMAT.LICENSE.
If applicable, add the following below this CDDL HEADER, with the
fields enclosed by brackets "[]" replaced with your own identifying
information: Portions Copyright [yyyy] [name of copyright owner]

CDDL HEADER END

Copyright 2010 Lubos Kocman.  All rights reserved.
Use is subject to license terms.
"""

# host.py - Contains

import os, sys
import smerr

class host:
    SUPPORTED_OS = [ "SunOS" ] # Maybe OracleOS in future ;-)
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
