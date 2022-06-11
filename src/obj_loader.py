#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Project Smat: System Modular Administration Tool
File name:    obj_loader.py
Description:  Simple parser for screen files.

Copyright (c) since 2009 Lubos Kocman <lkocman@luboskocman.com>. All rights reserved.

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
        self.ghosts=[]
        self.__title = None
        self.__help = None
        self.__parent = None
        self.__type = None

        self.parse_lines()


#-------------------------------------------------------------------------------
    def parse_lines(self):
        in_section = False
        next_auto_id = 0
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
                    self.objects[len(self.objects) -1 ].auto_id = next_auto_id
                    next_auto_id+=1

            else: # in_section != False
                if self.section_end(line):
                    in_section = False
                    continue

                self.get_attr(line, in_section)


            # keep current line number for better debugging
            self.cur_line_n += 1

#-------------------------------------------------------------------------------
    def get_scr_info(self):
        """get_scr_info(self) -- returns tuple of (title,parent,help,type)."""
        if self.__type == None and len(self.objects) > 0:
            if self.objects[0].type == screen.screen_obj.t_link:
                self.__type = screen.screen.t_menu
            else:
                self.__type = screen.screen.t_selector

        return (self.__title, self.__parent, self.__help, self.__type)
#-------------------------------------------------------------------------------
    def __get_list(self, value):
        return value.split()
#-------------------------------------------------------------------------------
    def get_attr(self, line, in_section):
        attr,value = self.vattr_split(line)
        if in_section == screen.screen_obj.sot_info: # scr_info
            if attr == screen.screen.s_title:
                self.__title = value

            elif attr == screen.screen.s_parent:
                self.__parent = value

            elif attr == screen.screen.s_help:
                self.__help = value

            else: # unknown attribute
                print smerr.ERROR_16 % (self.fpath,self.cur_line_n,attr)
                sys.exit(16)

        elif in_section == screen.screen_obj.sot_obj: # scr_obj
            if attr == screen.screen_obj.s_id: # id
                self.objects[len(self.objects) -1].id = value

            elif attr == screen.screen_obj.s_type: # type
                t = None

                if value == "link":
                    t = screen.screen_obj.t_link
                elif value == "number":
                    t = screen.screen_obj.t_number
                elif value == "boolean":
                    t = screen.screen_obj.t_boolean
                elif value == "list":
                    t = screen.screen_obj.t_list
                elif value == "ghost":
                    t = screen.screen_obj.t_ghost
                else:
                    t = screen.screen_obj.t_text

                self.objects[len(self.objects) -1].type = t

            elif attr == screen.screen_obj.s_mandatory:
                m = False
                if value == "true":
                    m = True

                self.objects[len(self.objects) -1].mandatory = m

            elif attr == screen.screen_obj.s_label: # label
                self.objects[len(self.objects) -1].label = \
                    value[:screen.screen_obj.c_max_label_len]

            elif attr == screen.screen_obj.s_cmd: # cmd
                self.objects[len(self.objects) -1].cmd = value

            elif attr == screen.screen_obj.s_cmd_false: # cmd_false
                self.objects[len(self.objects) -1].cmd_false = value

            elif attr == screen.screen_obj.s_cmd_priority: # cmd_priority
                self.objects[len(self.objects) -1].cmd_priority = int(value)

            elif attr == screen.screen_obj.s_cmd_priority_false: # cmd_priority_false
                self.objects[len(self.objects) -1].cmd_priority_false = int(value)

            elif attr == screen.screen_obj.s_arg_priority: # arg_priority
                self.objects[len(self.objects) -1].arg_priority = int(value)

            elif attr == screen.screen_obj.s_arg_priority_false:
                self.objects[len(self.objects) -1].arg_priority_false = int(value)

            elif attr == screen.screen_obj.s_value: # value
                self.objects[len(self.objects) -1].value = value

            elif attr == screen.screen_obj.s_value_true: # value_true
                self.objects[len(self.objects) -1].value_true = value

            elif attr == screen.screen_obj.s_value_false: # value_false
                self.objects[len(self.objects) -1].value_false = value

            elif attr == screen.screen_obj.s_list_separator: # list_separator
                self.objects[len(self.objects) -1].list_separator = value

            elif attr == screen.screen_obj.s_arg_format: # arg_format
                self.objects[len(self.objects) -1].arg_format = value

            elif attr == screen.screen_obj.s_arg_format_false: # arg_format_false
                self.objects[len(self.objects) -1].arg_format_false = value

            elif attr == screen.screen_obj.s_cmd_priority: # cmd_priority
                self.objects[len(self.objects) -1].cmd_priority = int(value)

            elif attr == screen.screen_obj.s_cmd_priority_false: # cmd_priority_false
                self.objects[len(self.objects) -1].cmd_priority_false = int(value)

            elif attr == screen.screen_obj.s_dependency: # dependency
                self.objects[len(self.objects) -1].dependency = self.__get_list(value)

            elif attr == screen.screen_obj.s_blocking:
                self.objects[len(self.objects) -1].blocking = self.__get_list(value)
            else:
                print smerr.ERROR_16 % (self.fpath,self.cur_line_n,attr)
                sys.exit(16)

#-------------------------------------------------------------------------------
    def vattr_split(self, line):
        """vattr_split(self,line) -- Generally transform string in format:
        "<attribute> = <value>=opt" into a tuple (attribute, value).\n
        line="".strip()"""

        # TODO: handler for ",' can be added

        try:
            i = line.index("=")
            attr = line[0:i].strip()
            value = line[i+1:].strip()

            if len(attr.split()) != 1:
                raise ValueError()

            return (attr,value)

        except ValueError:
            print smerr.ERROR_15 % (self.fpath,self.cur_line_n)
            sys.exit(15)


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

