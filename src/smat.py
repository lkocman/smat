#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Project Smat: System Modular Administration Tool
File name:    smat.py
Description:  The main purpose of this file is to autopick which frontend will be
              used (text or e.g. gtk).

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

import sys, os
import smerr
from host import host_info
from screen import *

class smat:
    m_text = 0
    m_auto = 1
    m_gtk = 2

    VERSION = 0.2
    DEF_FPATH = "mmenu"

#-------------------------------------------------------------------------------

    def __init__(self, mode=m_text):
        """__init__(smat.m_text | smat.m_auto | smat.m_gtk)"""
        if (len(sys.argv) > 2):
            self.print_usage()
        elif (len(sys.argv) == 1):
#            self.cur_scr = screen(host_info, smat.DEF_FPATH)
            self.cur_scr = curses_screen(host_info, smat.DEF_FPATH)
        else:
            if sys.argv[1] == "help":
                self.print_usage()
            elif sys.argv[1] == "version":
                print smat.VERSION
            elif sys.argv[1] == "list":
                self.list_fpaths()
            else:
                self.cur_scr = curses_screen(host_info, sys.argv[1])

        self.mode = mode
        self.start_interface()

#-------------------------------------------------------------------------------

    def start_interface(self):
        """"start_interface() launches curses or gtk gui"""
        if self.mode == smat.m_text:
            self.cur_scr.start_text_interface()

        elif self.mode == smat.m_auto or self.mode == smat.m_gtk:

            if  host_info.display:
                self.cur_scr.start_text_interface()

            elif self.mode == smat.m_gtk:
                print smerror.ERROR_3
                sys.exit(8)

            else: # mode=smat.m_auto
                self.cur_scr.start_text_interface()

#-------------------------------------------------------------------------------

    def print_usage(self):
        print """This is program is a Free Software.
Author does not take any responsibility for it.\n\nUsage:
	%s [ subcommand ] [fpath]

	Subcommands:
	version - Prints smat version.
	help    - Prints this helpful message.
	list    - Lists all supported fpaths.


""" % (sys.argv[0])
        sys.exit(0)

#-------------------------------------------------------------------------------

    def list_fpaths(self):
        fpaths=os.listdir(host_info.smat_home)
        fpaths.sort()

        for fpath in fpaths:
            print fpath

        sys.exit(0)

#-------------------------------------------------------------------------------
