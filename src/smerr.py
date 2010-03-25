#!/usr/bin/python2.6
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

# smerr.py - Contains error messages from smat

ERROR_1='Error 1: Unable to get valid smat home. Neither $SMAT_HOME or %s exists. Exiting.\n'
ERROR_2='Error 2: Object auto id <%d> id <%s>: value for attribute <%s> is not set. Exiting.\n'
ERROR_3='Can\'t find $DISPLAY. Will now exit.\n'
ERROR_5='Error 5: Unexpected error during creating dependency list.\n'
ERROR_6='Error 6: Dependency/Blocking problem.\n'
ERROR_6_1='Object <%s> can\'t block itself.\n'
ERROR_6_2='Mandatory object <%s> can\'t be set as blocking.\n'
ERROR_7='Error 7: Fast path <%s> does not exist. Exiting.\n'
ERROR_8='Error 8: Object id <%s> does not exist within fpath <%s>. Exiting.\n'
ERROR_9='Error 9: Internal type error in screen_obj.get_value(). Exiting\n'
ERROR_10='Error 10: Object with given ID <%s> already exists. Exiting.\n'
ERROR_11='Error 11: Object with given ID <%s> has duplicate attribute <%s> value: <%d>. Exiting.\n'
