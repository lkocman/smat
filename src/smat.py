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

# smat.py - base smat class

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
        print """Usage:
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
