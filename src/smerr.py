#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Project Smat: System Modular Administration Tool
File name:    smerr.py
Description:  This file contains misc. error messages.

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

ERROR_1='Error 1: Unable to get valid smat home. Neither $SMAT_HOME or %s exists. Exiting.\n'
ERROR_2='Error 2: Object auto id <%d>: value for attribute <%s> is not set. Exiting.\n'
ERROR_3='Error 3: Can\'t find $DISPLAY. Will now exit.\n'
ERROR_5='Error 5: Unexpected error during creating dependency list.\n'
ERROR_6='Error 6: Dependency/Blocking problem.\n'
ERROR_6_1='Object <%s> can\'t block itself.\n'
ERROR_6_2='Mandatory object <%s> can\'t be set as blocking.\n'
ERROR_7='Error 7: Fast path <%s> does not exist. Exiting.\n'
ERROR_8='Error 8: Object id <%s> does not exist within fpath <%s>. Exiting.\n'
ERROR_9='Error 9: Internal type error in screen_obj.get_value(). Exiting\n'
ERROR_10='Error 10: Object with given ID <%s> already exists. Exiting.\n'
ERROR_11='Error 11: Object with given ID <%s> has duplicate attribute <%s> value: <%d>. Exiting.\n'
ERROR_12='Error 12: Failed to determinate cmd_priority for object with given id <%s>. Exiting.\n'
ERROR_13='Error 13: No objects are matching hosted environment\n'
ERROR_14='SyntaxError 14: Fpath %s line %d:\n Expected format is "(%s | %s) {".\n'
ERROR_15='SyntaxError 15: Fpath %s line %d:\n Expected format is "<value> = <attribute>".\n'
ERROR_16='SyntaxError 16: Fpath %s line %d:\n Unsupported attribute "%s".\n'
ERROR_17='Error 17: Objects of type link can\'t be mixed with other types.\n'