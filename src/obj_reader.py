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

# obj_loader.py - simple parser

import screen
import smerr
import host
import sys

class obj_loader:
    def __init__(self, lines,fpath):
        """obj_loader(self, lines, fpath)"""
        self.fpath = fpath
        self.lines = lines
        self.cur_line_n = 0
        self.objects=[]
        self.parse_lines()

#-------------------------------------------------------------------------------
    def parse_lines(self):
        in_section = False

        for line in self.lines:
            line = self.__cut_comments(line)

            if len(line) == 0:
                self.cur_line_n += 1
                continue

            if not in_section:
                in_section = self.section_start(line)
                if in_section == False:
                    print smerr.ERROR_14 % (self.fpath, self.cur_line_n,
                                            screen.screen_obj.sot_obj,
                                            screen.screen_obj.sot_info)
                    sys.exit(14)
                if in_section == screen.screen_obj.sot_obj:
                    self.objects.append(screen.screen_obj())

            else: # in_section != False
                if self.section_end(line):
                    in_section = False
                self.get_attr(line)


            # keep current line number for better debugging
            self.cur_line_n += 1

#-------------------------------------------------------------------------------
    def section_end(self,line):
        """section_end(self,line) -- function is expecting line containing '}'.
        Any extra character on the line will cause syntax error."""
        if line != "}": return False
        else: return True
#-------------------------------------------------------------------------------

    def section_start(self,line):
        """section_start(self,line) -- function expects that in_section in parse_lines
        is set to false.\n Line containing (scr_obj | scr_info)  + {  will be
        processed as section start. Returned value is False or section_name."""

        supported_sections = [screen.screen_obj.sot_info,
                              screen.screen_obj.sot_obj]

        sect = line.split()
        if len(sect) == 2:
            for ss in supported_sections:
                if sect[0] == ss and sect[1] == '{': return sect[0]

        return False

#-------------------------------------------------------------------------------
    def __cut_comments(self, line):
        """__cut_comments(self, line)\n
        This function cuts out everything behind '#' in given line.
        Function ignores '\#'. Return value is stripped."""

        try:
            i = 0
            while True:
                if line.__contains__(host.host.comment_char):
                    i = line.index(host.host.comment_char,i)
                    if i > 0 and line[i-1] == '\\':
                        i+=1
                        continue
                    else:
                        line=line[0:i]
                        break

                else: break

        except ValueError:
            return line.strip()

        return line.strip()
#-------------------------------------------------------------------------------
    def get_objects(self):
        return self.objects

