#!/usr/bin/python2.6
# -*- coding: ascii -*-

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

# ips.py -- a small connector to pkg

#
# Standard Python libraries for ips are not used because of one simple reason.
# IPS is under heavy development, and who guarantees that code will be compatible.
# If pkg class is not available, simple bridge for pkginfo(1) is used.
#

import os

class ips:

#-------------------------------------------------------------------------------

	def is_installed(fmri):
		try:
			import pkg

		except ImportError:
			return svr4.is_installed(fmri)

#-------------------------------------------------------------------------------

class svr4:
	""" Fall back to svr4 in the case that pkg(5) is not in use """
	ERROR_3 = "Error 3: pkginfo(1) failed"
	PKG_CLIENT = "/usr/bin/pkginfo"
	CLIENT_ARGS = "-q"


#-------------------------------------------------------------------------------

	def is_installed(fmri):
		"""is_installed(fmri). Uses pkginfo(1) to revrieve information"""

		try:
			ret = os.system(PKG_CLIENT + " " + CLIENT_ARGS + " " + fmri)
		except:
			print svr4.ERROR_3
			sys.exit(3)
		if ret == 0:
			return True
		else:
			return False

#-------------------------------------------------------------------------------

