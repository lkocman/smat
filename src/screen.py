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

# screen.py - contains screen class

import os, sys
import smerr
import obj_reader

class screen:
    """Base class of the entire project"""

    t_menu = 0
    t_selector = 1

#-------------------------------------------------------------------------------

    def __init__(self, host_info, fpath):
        """screen(fpath)"""
        self.title = None
        self.help = None
        self.parent = None

        self.fpath = fpath
        self.type = None
        self.url = os.path.join(host_info.smat_home, fpath)
        self.objects = {}
        self.obj_count = 0

#---------------------------------------------------------------------------

    def get_priority_by_cmd(self, myobj):
        """searches for the highest cmd_priority containing the same command.
        Function returns None in the case of no-match."""
        ret_prior = None
        if myobj.cmd_priority != None:
            return myobj.cmd_priority

        else:
            for obj_key in self.objects:

                if self.objects[obj_key].cmd == myobj.cmd  \
                and self.objects[obj_key].cmd_priority > ret_prior:
                    ret_prior = self.objects[obj_key].cmd_priority

        if ret_prior == None:
            raise exception(smerr.ERROR_12 % (myobj.id))

        return ret_prior


#---------------------------------------------------------------------------
    def get_reserved_priority(self):
        """get_reserved_priority(): returns a dict. containing reserved
        priorities"""
        priorities = {}

        for obj_key in self.objects:
            obj = self.objects[obj_key]
            if obj.cmd_priority == None:
                obj.cmd_priority = self.get_priority_by_cmd(obj)

            if obj.cmd_priority != None:
                if priorities.has_key(obj.cmd_priority):
                    if priorities[obj.cmd_priority].__contains__(obj.arg_priority):
                        raise sobj_exception(smerr.ERROR_11 % (obj.id,
                        "obj.arg_priority", obj.arg_priority))

                    priorities[obj.cmd_priority].append(obj.arg_priority)

                else:
                    priorities[obj.cmd_priority] = []

        return priorities
#---------------------------------------------------------------------------

    def gen_cmd(self):
        """gen_cmd() -- This function generates set of command based on
screen.objects[]"""
        cmd = {}
        cmd_queue = {}
        """
        Structure of cmd {}
        {cmd_priority :
            [ cmd, arg_format1, arg_format2, .. ]
        """

        res_priority = self.get_reserved_priority()  # Contains indexes of reserved priorities

        """ format of res_priority -- {0: [1, 2], 1: [], 2: []}
             obj_cmd_priority.n: [cmd_arg_priority.n]

        This step is used only to make arg indexing easier. Each non-reserved index can
        be used by objects with non-specified arg_priority. Each command has reserved
        cmd_priority see: priority_by_cmd() which is called from get_reserved_priority().
        """

        # I should get myself to rework this shit in the future
        # But it should work like it is ...

        for obj_key in self.objects:
            obj = self.objects[obj_key]

            if obj.type == screen_obj.t_boolean:
                if obj.value == True and obj.cmd == None:
                    continue
                elif obj.value == False and obj.cmd_false == None:
                    continue
                elif obj.value == None:
                    continue

            if not cmd.has_key(obj.get_cmd_priority()):
                cmd[obj.get_cmd_priority()] = [obj.get_cmd()]

            if obj.get_arg_priority() != None:

                if obj.get_arg_priority() < 0: # -1 -2 ...
                    if not cmd_queue.has_key(obj.get_cmd_priority()):
                        cmd_queue[obj.get_cmd_priority()] = [[abs(obj.get_arg_priority()),
                                           obj.get_arg_format()]]
                        continue
                    else:
                        cmd_queue[obj.get_cmd_priority()].append([abs(obj.get_arg_priority()),obj.get_arg_format()])
                        continue

                if len(cmd[obj.get_cmd_priority()]) - 1 < obj.get_arg_priority(): # cmd[x][0]=cmd_string
                    cmd[obj.get_cmd_priority()].extend(
                        (obj.get_arg_priority() - (len(cmd[obj.get_cmd_priorty()]) -1)) * [ None ])
                    cmd[obj.get_cmd_priority()][obj.get_arg_priority() + 1] = obj.get_arg_format()
                    continue
                else:
                    cmd[obj.get_cmd_priority()].append(obj.get_arg_format())
                    continue
            else:
                try:
                    i = 0
                    while True:
                        i = cmd[obj.get_cmd_priority()].index(None, i)

                        if not res_priority[obj.get_cmd_priority()].__contains__(i):
                            cmd[obj.get_cmd_priority()][i+1] = obj.get_arg_format()
                            res_priority[obj.get_cmd_priority()].append(i)
                            break
                        i=i+1

                except ValueError:
                # TODO continue here
                    i = len(cmd[obj.get_cmd_priority()])
                    if not res_priority[obj.get_cmd_priority()].__contains__(i):
                        cmd[obj.get_cmd_priority()].append(obj.get_arg_format())
                        res_priority[obj.get_cmd_priority()].append(i)


        for cmd_priority in cmd_queue:
            q_values = cmd_queue[cmd_priority]
            q_values.sort();q_values.reverse()

            for cmd_format in q_values:
                print "appending", cmd_format
                cmd[cmd_priority].append(cmd_format[1]) # 0 is id


        print "`DEBUG: Generated command will be: \n", cmd

#---------------------------------------------------------------------------

    def is_mandatory_by_id(self,id):
        """Function returns if object with specified id is mandatory"""

        try:
            return self.objects[id].mandatory
        except KeyError:
            raise dependency_exception(smerr.ERROR_8 % (id, self.fpath))


#---------------------------------------------------------------------------
    def __get_uniq(self,alist):
        """This function should make unique list from [[a,b,c],[a,d],...]"""
        to_return = [None]
        for lst in alist:
            for item in lst:
                if to_return.__contains__(item):
                    break
                else:
                    to_return.append(item)

        return to_return[1:]
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
                            raise dependency_exception(smerr.ERROR_6 + smerr.ERROR_6_1 % (obj.id))

                        if self.is_mandatory_by_id(bl):
                            raise dependency_exception(smerr.ERROR_6 + smerr.ERROR_6_2 % (bl))

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


        if len(blocking) != 0:
            for block_key in blocking:
                print block_key
                if ids.__contains__(block_key):
                    raise dependency_exception(smerr.ERROR_6)

        if len(dependencies) != 0:
            uniq_deps = self.__get_uniq(dependencies.values())
            for dep in uniq_deps:
                if not self.objects.has_key(dep):
                    raise dependency_exception(smerr.ERROR_8 % (dep, self.fpath))


#-------------------------------------------------------------------------------

    def start_text_interface(self):
        """This method is launching curses based interface. """
        self.read_objects()
        self.check_dependencies() # This will invoked by user in future

#-------------------------------------------------------------------------------

    def start_gtk_interface(self):
        """This method is launching gtk intefrace for smat. """
        self.start_text_interface()

#-------------------------------------------------------------------------------

    def add_object(self, sobj):
        """add_object(screen_obj)"""
        try:
            sobj.check()

            if self.objects.has_key(sobj.id):
                raise sobj_exception(smerr.ERROR_10 % (sobj.id))
            else:
                    self.objects[sobj.id] = sobj

        except sobj_exception, se:
            print se
            sys.exit(1)

#-------------------------------------------------------------------------------

    def read_objects(self):

        screen_file = None
        try:
            file = open(self.url)
            screen_file = file.readlines()
            file.close()

        except IOError:
            print smerr.ERROR_7 % ( self.fpath)
            sys.exit(7)
        try:
            for obj in obj_reader.obj_loader(screen_file, self.fpath):
                self.add_object(obj)

            self.gen_cmd()

        except TypeError:
            print smerr.ERROR_13
            #raise sobj_exception(smerr.ERROR_13)


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

    # Screen objects types
    sot_obj = "scr_obj"
    sot_info = "scr_info"

    # String contstants
    s_id = "id"
    s_type = "type"
    s_label = "label"
    s_command = "cmd"
    s_value = "value"
    s_value_true = "value_true"
    s_value_false = "value_false"
    s_list_separator = "list_separator"



#-------------------------------------------------------------------------------

    def __init__(self, parent_screen):
        """screen_obj(parent_screen)"""
        # Mandatory variables

        self.auto_id = parent_screen.obj_count # Set mandatory autoid
        parent_screen.obj_count += 1 # Inc. number of initialized objects

        self.id = None
        self.type  = screen_obj.t_default
        self.mandatory = False
        self.value = None # Value is set via user input
        self.cmd = None # Static value
        self.label = None # not mandatory only for t_ghost
        # Mandatory for boolean type
        self.cmd_false = None # Static value for false
        self.value_true = None # Static value for True, mandatory for bool
        self.value_false = None # Static value for False, mandatory for bool

        self.list_separator = None # Mandatory when id = t_list
        # Non-mandatory variables
        self.arg_format = None
        self.cmd_priority = None
        self.cmd_priority_false = None
        self.arg_format_false = None # Boolean false

        self.arg_priority = None
        self.arg_priority_false = None  # Boolean false

        self.dependency = [] # screen_obj.id
        self.blocking = [] # screen_obj.id
        self.predicate = [] # [{variable : value}, ...]

#-------------------------------------------------------------------------------

    def get_value(self):
        try:
            if self.type == screen_obj.t_list: # A list type
                return str(self.list_separator.join(self.value))

            elif self.type == screen_obj.t_boolean: # Boolean type
                if self.value == True:
                    return str(self.value_true)
                elif self.value == False:
                    return str(self.value_false)
                else:
                    return None
            else:
                return str(self.value)

        except (TypeError, AttributeError):
            print smerr.ERROR_9
            print "Current setup is:\n"
            print self.value, "With real type:", type(self.value).__name__, "and defined type id:", self.type
            sys.exit(9)

#-------------------------------------------------------------------------------
    def get_arg_format(self):
        """get_arg_format(self)"""
        if self.type == screen_obj.t_boolean:
            if self.value == True:
                return self.arg_format
            elif self.value == False:
                return self.arg_format_false
            else:
                return self.value # None in this case
        else:
            return self.arg_format
#-------------------------------------------------------------------------------
    def get_arg_priority(self):
        """get_arg_priority(self)"""
        if self.type == screen_obj.t_boolean:
            if self.value == True:
                return self.arg_priority
            elif self.value == False:
                return self.arg_priority_false
            else:
                return self.value # None in this case
        else:
            return self.arg_priority
#-------------------------------------------------------------------------------
    def get_cmd_priority(self):
        """get_cmd_priority(self)"""
        if self.type == screen_obj.t_boolean:
            if self.value == True:
                return self.cmd_priority
            elif self.value == False:
                return self.cmd_priority_false
        else:
            return self.cmd_priority
#-------------------------------------------------------------------------------
    def get_cmd(self):
        """get_cmd(self)"""
        if self.type == screen_obj.t_boolean:
            if self.value == True:
                return self.cmd
            elif self.value == False:
                return self.cmd_false
            else:
                return self.value # None
        else:
            return self.cmd
#-------------------------------------------------------------------------------

    def check(self):
        """check(). A set of test to check if object contains
necessary data."""
        try:
            if self.id == None:
                raise sobj_exception(smerr.ERROR_2 % self.auto_id,
                                     self.id, screen_obj.s_id)
            elif self.type == None:
                raise sobj_exception(smerr.ERROR_2 % self.auto_id,
                                     selfid, screen_obj.s_type)

            # Extended check

            if self.type > screen_obj.t_ghost:
                if self.label == None:
                    raise sobj_exception(smerr.ERROR_2 % (self.auto_id,
                                     self.id, screen_obj.s_label))

            if self.type == screen_obj.t_list:
                if self.list_separator == None:
                    raise sobj_exception(smerr.ERROR_2 % (self.auto_id,
                                     self.id, screen_obj.s_list_separator))

            if self.type == screen_obj.t_boolean and \
               self.cmd_priority != None and \
               self.cmd_priority_false == None:
                self.cmd_priority_false = self.cmd_priority

#            if self.type == screen_obj.t_boolean:
#                if self.value_false == None or self.value_true == None:
#                    raise sobj_exception(smerr.ERROR_2 % (self.auto_id,
#                                                               screen_obj.s_value_false + " or " +
#                                                               screen_obj.s_value_true))

#-------------------------------------------------------------------------------


        except sobj_exception, se:
            print se # This should be viewed later in the text/gtk interface
            sys.exit(2)

#-------------------------------------------------------------------------------

class sobj_exception(Exception):
#-------------------------------------------------------------------------------

    def __init__(self, msg="sobj_exception: generic"):
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
