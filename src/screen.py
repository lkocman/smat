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

# screen.py - contains screen class

import os, sys

class screen:
	"""Base class of the entire project"""

	t_menu = 0
	t_selector = 1

	ERROR_5 = "Error 5: Unexpected error during creating dependency list."
	ERROR_6 = "Error 6: Dependency/Blocking problem."
	ERROR_6_1 = " Object <%s> can't block itself."
	ERROR_6_2 = " Mandatory object <%s> can't be set as blocking."
	ERROR_6_2 = " y object <%s> can't be set as blocking."
	ERROR_7 = "Error 7: Fast path <%s> does not exist. Exiting"
#-------------------------------------------------------------------------------

	def __init__(self, host_info, fpath):
		"""screen(fpath)"""
		self.title = None
		self.fpath = fpath
		self.parent = None
		self.type = None
		self.url = os.path.join(host_info.smat_home, fpath)
		self.pkg_dep = []
		self.objects = {}
		self.obj_count = 0

#---------------------------------------------------------------------------

	def check_objects(self):
		"""This method checkes for following issues
		1. Any object can't be both blocking and mandatory
		"""
		pass

#---------------------------------------------------------------------------

	def is_mandatory_by_id(self,id):
		"""Function returns if object with specified id is mandatory"""
		return self.objects[obj.id].mandatory
				
#---------------------------------------------------------------------------

	def check_dependencies(self):
		"""check_dependencies(). This method browses creates list of dependencies
		and returns list of missing screen_obj.id's"""
		ids = [] # All obj id's that user selected to process 
		blocking = {}
		dependencies = {}

		for o in self.objects:
			obj = self.objects[o]	
			# Only if user specified value, or ghost objects
			if obj.value != None or obj.type == screen_obj.t_ghost:
				ids.append(obj.id)

				# Blockers are indexed by what object is blocked "obj.blocking"
				if len(obj.blocking) > 0 :
					for bl in obj.blocking:
						if bl == obj.id:
							raise dependency_exception(screen.ERROR_6 + screen.ERROR_6_1 % (obj.id))

						if is_mandatory_by_id(bl):
							raise dependency_exception(screen.ERROR_6 + screen.ERROR_6_2 % (bl))

						if not blocking.has_key(bl):
							blocking[bl] = [obj.id]

						else:
							blocking[bl].append(obj.id)

				# Dependencies are indexed by what has dependency "obj.id"
				# Each object has to have unique id, so no index check is req.
				if len(obj.dependency) > 0:
					dependencies[obj.id] = obj.dependency

		# Possible TODO: in case of any dependency/blocking problems
		# I recommend to print a tree of dependencies/blockers for given
		# case


		ids.sort()

		print "# total deps/blocks --------------------------------"
		print "Dependencies"
		print dependencies	
		print "Blocking"
		print blocking
		print "active IDs"
		print ids

		# Following code needs to be optimalized

		if len(blocking) != 0:
			for block_key in blocking:
				print block_key
				if ids.__contains__(block_key):
					raise dependency_exception(screen.ERROR_6)





#-------------------------------------------------------------------------------

	def start_text_interface(self):
		"""This method is launching curses based interface. """
		self.read_objects()
		self.check_dependencies() # This will invoked by user in future

#-------------------------------------------------------------------------------

	def start_gtk_interface(self):
		"""This method is launching gtk intefrace for smat. """
		self.start_gtk_interface() # TODO: gtk interface is planned

#-------------------------------------------------------------------------------

	def add_object(self, sobj):
		"""add_object(screen_obj)"""
		try:
			sobj.autoid=self.obj_count
			self.obj_count = self.obj_count + 1
			sobj.check()
			self.objects[sobj.id] = sobj

		except sobj_exception as se:
			print se
			sys.exit(1)

#-------------------------------------------------------------------------------

	def read_objects(self):

		try:
			open(self.url)
		except IOError:
			print screen.ERROR_7 % ( self.fpath)
			sys.exit(7)


		#TESTING
		testobj = screen_obj()

		testobj.id = "id1"
		testobj.type = screen_obj.t_text
		testobj.mandatory = True
		testobj.label = "Test id 1"

		testobj2 = screen_obj()
		testobj2.id = "id2"
		testobj2.type = screen_obj.t_text
		testobj2.label = "Test id 2"
		testobj2.dependency = [ "id1" ]
		testobj2.value = "test string"

		testobj3 = screen_obj()
		testobj3.id = "id3"
		testobj3.type = screen_obj.t_list
		testobj3.list_separator = ","
		testobj3.label = "Test id 3"
		testobj3.blocking = [ "id1" ]
		
		testobj4 = screen_obj()
		testobj4.id = "id4"
		testobj4.type = screen_obj.t_text
		testobj4.label = "Test id 4"
		testobj4.dependency = [ "id2" ]
		testobj4.value = "test string"

		self.add_object(testobj)
		self.add_object(testobj2)
		self.add_object(testobj3)
		self.add_object(testobj4)
		

		self.check_objects()
	#END OF TESTING

#-------------------------------------------------------------------------------

"""
Screen object has following variables

self.id  type: string, example: user_name
self.parent type: string, example mmenu or none
self.type type: t_sobj
"""

class screen_obj:
	t_text = 5
	t_number = 4
	t_boolean = 3
	t_list = 2
	t_ghost = 1
	t_link = 0

	t_default = t_text # Default type set to text

	# String contstants
	s_id = "id"
	s_type = "type"
	s_label = "label"
	s_command = "command"
	s_list_separator = "list_separator"

	ERROR_2 = "Error 2: Object autoid %d: value for attrbute %s is not set. Exiting."

#-------------------------------------------------------------------------------

	def __init__(self):
		"""screen_obj()"""
		# Mandatory variables
		self.auto_id = 0 # Assigned by screen.add_obj()
		self.id = None
		self.type  = screen_obj.t_default
		self.mandatory = False
		# Non-mandatory variables
		self.value = None # Value is set via user input
		self.list_separator = None # Mandatory when id = t_list
		self.dependency = [] # screen_obj.id
		self.blocking = [] # screen_obj.id
		self.command = None # absolute path
		self.label = None # Mandatory in case that type != t_ghost
		self.command_false = None # Used only in boolean type
		self.predicate = [] # [{variable : value}, ...]

#-------------------------------------------------------------------------------

	def check(self):
		"""check(). A set of test to check if object contains
necessary data."""
		try:
			if self.id == None:
				raise sobj_exception(screen_obj.ERROR_2 % self.auto_id,
			                     screen_obj.s_id)
			elif self.type == None:
				raise sobj_exception(screen_obj.ERROR_2 % self.auto_id,
			                     screen_obj.s_type)

			# Extended check

			if self.type > screen_obj.t_ghost:
				if self.label == None:
					raise sobj_exception(screen_obj.ERROR_2 % (self.auto_id,
					                     screen_obj.s_label))

			if self.type == screen_obj.t_list:
				if self.list_separator == None:
					raise sobj_exception(screen_obj.ERROR_2 % (self.auto_id,
					                     screen_obj.s_list_separator))

#-------------------------------------------------------------------------------


		except sobj_exception as se:
			if self.__fatal__:
				print se
				sys.exit(2)
			else:
				print se # This should be viewed later in the text/gtk interface

#-------------------------------------------------------------------------------

class sobj_exception(Exception):
#-------------------------------------------------------------------------------

	def __init__(self, msg):
		self.value = msg

#-------------------------------------------------------------------------------

	def __str__(self):
		return self.value

#-------------------------------------------------------------------------------


class dependency_exception(Exception):
#-------------------------------------------------------------------------------

	def __init__(self, msg, fatal=False):
		self.value = msg
		self.__fatal__ = fatal

#-------------------------------------------------------------------------------

	def __str__(self):
		return self.value

#-------------------------------------------------------------------------------
