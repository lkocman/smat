#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Project Smat: System Modular Administration Tool
File name:    screen.py
Description:  This file contains curses frontend and the main smat class.

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

import os, sys, re, traceback, curses, math
import smerr,  obj_loader

#-------------------------------------------------------------------------------

def get_longest_value_from_dict(mydict):
    """get_longest_value_from_dict(mydict)"""
    l = 0
    for key in mydict.keys():
        cl = len(mydict[key])
        if cl > l:
            l = cl
    return l

#-------------------------------------------------------------------------------
class screen:
    """Base class of the entire project"""

    t_menu = 0
    t_selector = 1

    s_title = "title"
    s_parent = "parent"
    s_help = "help"
#-------------------------------------------------------------------------------

    def __init__(self, host_info, fpath):
        """screen(fpath)"""
        self.set_default_values(host_info, fpath)
        self.read_objects()

#---------------------------------------------------------------------------
    def get_obj_count(self):
        """get_obj_count() -- should be called after each read_objects()"""
        self.obj_count = len(self.objects) # curses purpose

#---------------------------------------------------------------------------
    def set_default_values(self,host_info,fpath):
        self.title = None
        self.title = None
        self.help = None
        self.parent = None
        self.type = None # This will be taken from the first object
        self.fpath = fpath
        self.type = None
        self.url = os.path.join(host_info.smat_home, fpath)
        self.objects = {}
        self.ghosts = {}
        self.unsorted_ids = []
        self.longest_label = 0 # experimental use

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
                    # WTH is going on here?
                    if obj.arg_priority != None and priorities[obj.cmd_priority].__contains__(obj.arg_priority):
                        raise sobj_exception(smerr.ERROR_11 % (obj.id,
                                                               "obj.arg_priority", `obj.arg_priority`))

                    priorities[obj.cmd_priority].append(obj.arg_priority)

                else:
                    priorities[obj.cmd_priority] = []

        return priorities
#---------------------------------------------------------------------------
    def substitute(self, arg_format):
        """subtitute(arg_format) - Function replaces all occurance of $[var_id]
        by self.objects[var_id].value"""

        VAR_START="$["; VAR_END="]"

        strt_pos = arg_format.find(VAR_START)

        if strt_pos <0:
            return arg_format

        static_prts = re.split("\$\[.*?\]", arg_format) # $[*] is cutted
        dynamic_ptrs = re.findall("\$\[.*?\]", arg_format) # $[*] is returned

        if not dynamic_ptrs:
            raise Exception(smerr.ERROR_18 %(self.fpath, VAR_START+VAR_END))

        index = 0

        for var_id in dynamic_ptrs:
            dynamic_ptrs[index]=self.objects[var_id[2:-1].strip()].value
            index+=1

        if strt_pos > 0: # It may happen that we'll have to add dyn. before static
            zipped=zip(static_prts, dynamic_ptrs)
        else:
            zipped=zip(dynamic_ptrs, static_prts)

        result = ""

        for tpl in zipped:
            result += "".join(tpl)

        return result

#---------------------------------------------------------------------------

    def gen_cmd(self):
        """gen_cmd() -- This function generates set of command based on
screen.objects[]"""
        self.check_dependencies()

        cmd = command()
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

            if obj.value == None:
                continue

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
                        cmd_queue[obj.get_cmd_priority()] = \
                                 [[abs(obj.get_arg_priority()),\
                                   self.substitute(obj.get_arg_format())]]
                        continue
                    else:
                        cmd_queue[obj.get_cmd_priority()].append([abs(\
                            obj.get_arg_priority(),\
                            self.substitute(obj.get_arg_format()))])
                        continue

                if len(cmd[obj.get_cmd_priority()]) - 1 < obj.get_arg_priority(): # cmd[x][0]=cmd_string
                    cmd[obj.get_cmd_priority()].extend(
                        (obj.get_arg_priority() - (len(cmd[obj.get_cmd_priorty()]) -1)) * [ None ])
                    cmd[obj.get_cmd_priority()][obj.get_arg_priority() + 1] =\
                       self.substitute(obj.get_arg_format())
                    continue
                else:
                    cmd[obj.get_cmd_priority()].append(self.substitute(\
                        obj.get_arg_format()))
                    continue
            else:
                try:
                    i = 0
                    while True:
                        i = cmd[obj.get_cmd_priority()].index(None, i)

                        if not res_priority[obj.get_cmd_priority()].__contains__(i):
                            cmd[obj.get_cmd_priority()][i+1] = self.substitute(\
                                obj.get_arg_format())
                            res_priority[obj.get_cmd_priority()].append(i)
                            break
                        i=i+1

                except ValueError:
                    i = len(cmd[obj.get_cmd_priority()])
                    if not res_priority[obj.get_cmd_priority()].__contains__(i):
                        cmd[obj.get_cmd_priority()].append(self.substitute(\
                            obj.get_arg_format()))
                        res_priority[obj.get_cmd_priority()].append(i)


        for cmd_priority in cmd_queue:
            q_values = cmd_queue[cmd_priority]
            q_values.sort();q_values.reverse()

            for cmd_format in q_values:
                cmd[cmd_priority].append(cmd_format[1]) # 0 is id

            return cmd
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
                ids.append(o)

                # Blockers are indexed by what object is blocked "obj.blocking"
                if len(obj.blocking) > 0 :
                    for bl in obj.blocking:
                        if bl == obj.id:
                            raise dependency_exception(smerr.ERROR_6 +
                                                       smerr.ERROR_6_1 % (obj.id))

                        if self.is_mandatory_by_id(bl):
                            raise dependency_exception(smerr.ERROR_6 +
                                                       smerr.ERROR_6_2 % (bl))

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
                if ids.__contains__(block_key):
                    raise dependency_exception(smerr.ERROR_6)

        if len(dependencies) != 0:
            uniq_deps = self.__get_uniq(dependencies.values())
            for dep in uniq_deps:
                if not self.objects.has_key(dep):
                    raise dependency_exception(smerr.ERROR_8 % (dep, self.fpath))


#-------------------------------------------------------------------------------

    def add_object(self, sobj):
        """add_object(screen_obj)"""
        try:

            sobj.check()

            if self.type == screen.t_menu and sobj.type != screen_obj.t_link \
               or self.type == screen.t_selector \
               and sobj.type == screen_obj.t_link:
                print smerr.ERROR_17
                sys.exit(17)

            if self.objects.has_key(sobj.id):
                raise sobj_exception(smerr.ERROR_10 % (sobj.id))
            else:
                """
                Ghosts  objects needs to be
                """

                if sobj.type == screen_obj.t_ghost:
                    # TODO: needs to be processed
                    pass
                else:
                    #
                    # Experiments with setting up column for obj value (curses)
                    #
                    l = len(sobj.label)
                    if self.longest_label < l:
                        self.longest_label = l

                    del(l)

                    self.objects[sobj.id] = sobj
                    self.unsorted_ids.append(sobj.id)

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
        objr = obj_loader.obj_loader(screen_file, self.fpath)
        self.title, self.parent, self.help, self.type = objr.get_scr_info()

        # needs some extra steps that's why foreach
        for obj in objr.get_objects():
            self.add_object(obj)

        self.get_obj_count()

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
    s_value = "value"
    s_cmd = "cmd"
    s_cmd_false = "cmd_false"
    s_cmd_priority = "cmd_priority"
    s_cmd_priority_false = "cmd_priority_false"
    s_value_true = "value_true"
    s_value_false = "value_false"
    s_arg_format = "arg_format"
    s_arg_format_false = "arg_format_false"
    s_arg_priority = "arg_priority"
    s_arg_priority_false = "arg_priority_false"
    s_list_separator = "list_separator"
    s_blocking = "blocking"
    s_dependency = "dependency"
    s_mandatory = "mandatory"

    c_max_label_len = 40


#-------------------------------------------------------------------------------

    def __init__(self):
        """screen_obj(parent_screen)"""
        # Mandatory variables

        self.auto_id = None

        self.id = None
        self.type  = screen_obj.t_default
        self.mandatory = False
        self.value = None # Value is set via user input
        self.cmd = None # Static value
        self.label = None # not mandatory only for t_ghost
        self.cmd_false = None # Static value for false
        self.value_true = None # Static value for True, mandatory for bool
        self.value_false = None # Static value for False, mandatory for bool

        self.list_separator = None # Mandatory when id = t_list
        self.arg_format = None
        self.arg_format_false = None # Boolean false
        self.cmd_priority = None
        self.cmd_priority_false = None

        self.arg_priority = None
        self.arg_priority_false = None  # Boolean false

        self.dependency = [] # screen_obj.id
        self.blocking = [] # screen_obj.id
        self.predicate = [] # [{variable : value}, ...]

#-------------------------------------------------------------------------------

    def get_value(self,split_list=True):
        """get_value()
        function will return non-none value of the given object. In case
        of boolean objects, value will be taken based on current obj.value.
        Lists will be joined into string concatenated by self.list_separator."""

        empty_string = ""
        value_true = "True"
        value_false = "False"

        try:
            if self.type == screen_obj.t_list: # A list type
                if self.value == None:
                    return empty_string

                if split_list:
                    return self.list_separator.join(self.value)
                else:
                    return self.value

            elif self.type == screen_obj.t_boolean: # Boolean type

                if self.value == True:
                    return value_true

                elif self.value == False:
                    return value_false

                else: return empty_string

            else:
                if self.value == None:
                    return empty_string
                else: return str(self.value)

        except (TypeError, AttributeError):
            print smerr.ERROR_9
            print "Current setup is:\n"
            print self.value, "With real type:", type(self.value).__name__,
            "and defined type id:", self.type
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
            if self.type == screen_obj.t_link:
                if self.value == None:
                    raise sobj_exception(smerr.ERROR_2 %
                                         (self.auto_id,screen_obj.s_value))
                else:
                    self.id = self.value

            if self.id == None:
                raise sobj_exception(smerr.ERROR_2 %
                                     (self.auto_id,screen_obj.s_id))

            elif self.type == None:
                raise sobj_exception(smerr.ERROR_2 %
                                     (self.auto_id,screen_obj.s_type))

            if self.type != screen_obj.t_ghost:
                if self.label == None:
                    raise sobj_exception(smerr.ERROR_2 % (self.auto_id, \
                                                          screen_obj.s_label))

            if self.type == screen_obj.t_list:
                if self.list_separator == None:
                    raise sobj_exception(smerr.ERROR_2 % (self.auto_id, \
                                                          screen_obj.s_list_separator))

            if self.type == screen_obj.t_boolean and \
               self.cmd_priority != None and \
               self.cmd_priority_false == None:
                self.cmd_priority_false = self.cmd_priority

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

class curses_screen:
    TITLE_LINE = 1
    HELP_LINE =  3
    CONTENT_LINE = 5

    VALUE_RES_COLS = 15

    # Keep in mind that no string L_* shouldn't exceed len of 20 chars
    # Recommended size is 16 chars to have some space arround
    L_GOTO   ="Esc+2=Goto"
    L_BACK   ="Esc+3=Back"
    L_REFR   ="Esc+4=Refresh"
    L_CMD    ="Esc+6=Command"
    L_QUIT   ="Esc+0=Quit"
    L_ENTER  ="Enter=Do"
    L_ENTER_2="Enter=Select"

    MENU_ITEM_SIZE=20

    items_t_menu = [L_GOTO, L_BACK, L_REFR, L_QUIT, L_ENTER_2]
    items_t_selector = [L_GOTO, L_BACK, L_REFR,L_CMD, L_QUIT, L_ENTER]

    m_default = 0
    m_input = 1
    m_command = 2

    type_sign = {
        screen_obj.t_boolean : " ?",
        screen_obj.t_text : "",
        screen_obj.t_list : " (,)",
        screen_obj.t_number: " #"
    }

    # get the longest type_sign

    max_ts_len = get_longest_value_from_dict(type_sign)
    max_value_len = 20 -  max_ts_len - 1

    LB = "["
    RB = "]"

    LOCAL_KEY_ENTER = 10
    LOCAL_KEY_BACKSPACE = 127

    CMDW_MARGIN = 2
#-------------------------------------------------------------------------------
    def __init__(self, host_info, fpath):
        """curses_screen(host_info,fpath)"""
        self.host_info = host_info
        self.scr_inf = screen(host_info, fpath)
        self.ncols = 0.0
        self.nlines = 0.0
        self.cline = 0 # Current active line in content
        self.pline = 0 # previous line
        self.stdscr = None
        self.i_t_menu_len = 0
        self.i_t_selector_len = 0
        self.bounds = (0 ,0) # (y_min, y_max)
        self.get_mn_items_len()
        self.stdscr = None
        self.content_pad = None
        self.bounds_changed = False
        self.cmd_window = None

        self.mode = curses_screen.m_default

        self.previous_scr_type = None # to minimalize redrawing

        try:
            self.start_text_interface()
            self.process_user_input()

        except SystemExit:
            pass

        except:
            self.clear_all_screen()
            print traceback.print_exc()
            sys.exit(18)


        self.exit_text_interface()

#-------------------------------------------------------------------------------
    def draw_cmd_pad(self, cmd):
        "draw_cmd_pad(cmd) -- Creates a pad that contains passed string."
        
        x_margin = 1
        y_margin = 1
        
        head_line = 0

        mrg = curses_screen.CMDW_MARGIN
        # I have to use windows.subpad in order to display border correctly
        if self.cmd_window == None:

            self.cmd_window = curses.newwin(self.nlines - 2*mrg, self.ncols -
                                            2*mrg, mrg, mrg)
            self.cmd_window.box()
            
            self.cmd_window.refresh()
            # Don't forget about border, it takes one col/row on each side
            
            mrg += 1
            
            s_cmd = str(cmd) # transform given dict into a string
            
            self.cmd_pad = curses.newpad(s_cmd.count("\n") + 1,
                                         self.ncols - (2*mrg))
            
            self.cmd_pad.addstr(y_margin,x_margin,s_cmd)
            
            self.cmd_pad.refresh(head_line, 1, mrg, mrg, self.nlines - (2*mrg),
                                 self.ncols - (2*mrg))

        while True:
            key=self.stdscr.getch()
            break

        self.draw_all_screen() # Really necessary

#-------------------------------------------------------------------------------

    def dismiss_user_action(self):
        """dismiss_user_action(self)
        function should be called before usage of goto() or reset() """
        self.cline = self.pline = 0
        self.bounds = (0,0)
        self.clear_screen(False) # By setting up False, nothing will be redrawed

#-------------------------------------------------------------------------------
    def process_user_input(self):
        key = None
        key_steps = 0

        key=self.stdscr.getch()

        while True:
            if key == 27: # ESCAPE
                if self.mode != curses_screen.m_command:
                    self.mode = curses_screen.m_command
                else:
                    self.mode = curses_screen.m_default

                key=self.stdscr.getch()
                continue

            if self.mode == curses_screen.m_command:
                if key == ord('0'):
                    self.exit_text_interface() # Esc+0

                elif key == ord('3'): # Esc+3
                    self.goto(self.scr_inf.parent)

                elif key == ord('6'): # Esc+6 -- main purpose
                    self.draw_cmd_pad(self.scr_inf.gen_cmd())
                # Leave command mode
                self.mode = curses_screen.m_default
            else:
                if key == curses.KEY_DOWN or key == ord('j'):
                    if not self.cline >= self.scr_inf.obj_count -1:
                        self.pline = self.cline
                        self.cline = self.cline + 1

                elif key == curses.KEY_UP or key == ord('k'): # vim-like behavior
                    if not self.cline == 0:
                        self.pline = self.cline
                        self.cline = self.cline - 1

                elif key == curses.KEY_ENTER or key == 10: # 343 WTF?
                    if self.scr_inf.type == screen.t_menu:
                        self.goto(self.get_current_object().value)
                    else: # Enter edit mode
                        self.edit_cobj_value()

            self.update_content()
            key=self.stdscr.getch()



#-------------------------------------------------------------------------------
    def get_current_object(self):
        return self.scr_inf.objects[self.scr_inf.unsorted_ids[self.cline]]
#-------------------------------------------------------------------------------
    def get_previous_object(self):
        return self.scr_inf.objects[self.scr_inf.unsorted_ids[self.pline]]
#-------------------------------------------------------------------------------
    def edit_cobj_value(self):
        cobj = self.get_current_object()

        if cobj.value == None:
            cobj.value = ""

        while True:
            key = self.stdscr.getch()

            if key == curses_screen.LOCAL_KEY_ENTER or\
               key == curses.KEY_ENTER:
                break

            elif key == curses_screen.LOCAL_KEY_BACKSPACE\
                 or key == curses.KEY_BACKSPACE:
                cobj.value = cobj.value[:-1]
            else:
                if cobj.type == screen_obj.t_number:
                    if not (key > 47 and key < 58):
                        continue
                elif cobj.type == screen_obj.t_boolean:
                    pass

                try:
                    cobj.value += chr(key)
                except ValueError:
                    pass

            self.update_content(split_list=False)

        if len(cobj.value.strip()) == 0:
            cobj.value = None

#-------------------------------------------------------------------------------
    def move_cursor(self):
        cursor_line = curses_screen.CONTENT_LINE  + self.cline - self.bounds[0]
        self.stdscr.move(cursor_line ,0)
#-------------------------------------------------------------------------------
    def goto(self, fpath="mmenu"):
        if fpath != None:
            self.dismiss_user_action()
            self.scr_inf = screen(self.host_info, fpath)
            self.draw_all_screen()
        else: # User probably hit back when in mmenu
            self.exit_text_interface()
#-------------------------------------------------------------------------------
    def get_mn_items_len(self):
        self.i_t_menu_len = len(curses_screen.items_t_menu) * \
            curses_screen.MENU_ITEM_SIZE
        self.i_t_selector_len = len(curses_screen.items_t_selector) * \
            curses_screen.MENU_ITEM_SIZE
#-------------------------------------------------------------------------------
    def check_screen_size(self):
        """Function will return false in the size of screen is not big enough."""
        return True

#-------------------------------------------------------------------------------
    def draw_all_screen(self):
        self.get_yx() # Trying to handle possible resizing of screen

        self.stdscr.erase()
        self.draw_title()
        self.draw_help()
        self.draw_menu(force=True)
        self.stdscr.refresh()
        self.draw_content()

#-------------------------------------------------------------------------------
    def draw_screen(self):
        """draw_screen(self) -- draws everything except of content pad"""
        self.draw_title()
        self.draw_help()
        self.draw_menu(force=True)
        self.stdscr.refresh()
#-------------------------------------------------------------------------------

    def check_bounds(self):
        if self.bounds == (0,0): # (y_min, y_max)
            self.bounds = (0, self.avail_lines)
            self.bounds_changed = True
            return

        if self.cline > self.bounds[1] or self.cline < self.bounds[0]:
            if self.cline > self.bounds[1]: # scrolling down
                if self.bounds[1] + 1 < self.scr_inf.obj_count:
                    self.bounds = (self.bounds[0] + 1, self.bounds[1] + 1)
                    self.bounds_changed = True
                else:
                    self.bounds = (self.bounds[0] + 1, self.scr_inf.obj_count)
                    self.bounds_changed = True

            else: # scrolling up
                self.bounds = (self.cline, self.cline + self.avail_lines)
                self.bounds_changed = True
                return
        self.bounds_changed = False

#-------------------------------------------------------------------------------

    def get_yx(self):
        self.nlines, self.ncols = self.stdscr.getmaxyx()

        if self.ncols < 80:
            self.__value_col = 50
        else:
            self.__value_col = self.ncols - 20

#-------------------------------------------------------------------------------

    def add_cnt_item(self, obj, line, mode, split_list=True, col=0):
        """add_cnt_item(text, line, mode, col=0)"""
        self.content_pad.addstr(line, col, " " + obj.label, mode)


        if self.scr_inf.type == screen.t_selector:

            col = self.__value_col

            l = len(obj.get_value()[-self.max_value_len:])

            self.content_pad.addstr(line, col, curses_screen.LB +
                obj.get_value(split_list)[-curses_screen.max_value_len:]\
                + curses_screen.RB, mode)

            # Rest of the function  is making sure that space behind RB is clean

            s_col = self.ncols - len(curses_screen.type_sign[obj.type]) -1
            rev_col = col+l+2
            self.content_pad.addstr(line,rev_col,(s_col - rev_col) * " ", \
                                    curses.A_NORMAL)


            # Print type sign of expected user input
            self.content_pad.addstr(line, s_col, \
                curses_screen.type_sign[obj.type], mode)

#-------------------------------------------------------------------------------
    def draw_content(self):
        """draw_content() function will draw each non-ghost object on screen"""
        if self.content_pad == None:
            self.content_pad = curses.newpad(len(self.scr_inf.objects), \
                                             self.ncols)
        i_line = 0

        self.check_bounds()

        for obj_key in self.scr_inf.unsorted_ids:
            if self.scr_inf.objects[obj_key].type == screen_obj.t_ghost:
                pass
            mode = curses.A_NORMAL
            if i_line == self.cline:
                mode = curses.A_REVERSE
            self.add_cnt_item(self.scr_inf.objects[obj_key], i_line, mode)
            i_line += 1

        border_line = self.avail_lines + self.CONTENT_LINE
        self.move_cursor()

        self.move_cursor()
        self.content_pad.refresh(self.bounds[0],0,curses_screen.CONTENT_LINE,0,\
                                 border_line ,self.ncols)

#-------------------------------------------------------------------------------
    def cleanup_cnt_bg(self, draw_screen=True):
        """Function will erase whole stdscr and redraw everything except of
           pad. setting draw_screen to false will not redraw anything."""
        self.stdscr.erase()

        if draw_screen:
            self.draw_screen()
#-------------------------------------------------------------------------------
    def update_content(self, split_list=True):
        self.check_bounds()
        if self.bounds_changed:
            self.cleanup_cnt_bg()

        self.add_cnt_item(self.get_previous_object(), self.pline, curses.A_NORMAL)

        self.add_cnt_item(self.get_current_object(), self.cline, curses.A_REVERSE, split_list)

        border_line = self.avail_lines + self.CONTENT_LINE
        self.move_cursor()
        self.content_pad.noutrefresh(self.bounds[0],0,curses_screen.CONTENT_LINE,0,\
                                     border_line ,self.ncols)
#-------------------------------------------------------------------------------

    def draw_title(self):
        start_col = (self.ncols - len(self.scr_inf.title)) // 2
        self.stdscr.addstr(curses_screen.TITLE_LINE, start_col, \
                           self.scr_inf.title)

#-------------------------------------------------------------------------------

    def draw_help(self):
        self.stdscr.addstr(curses_screen.HELP_LINE, 0, self.scr_inf.help)

#-------------------------------------------------------------------------------

    def draw_menu(self, force=False):
        menu = None
        menu_len = 0

        if self.previous_scr_type == self.scr_inf.type and not force:
            return
        else:
            self.previous_scr_type = self.scr_inf.type

        if self.scr_inf.type == screen.t_selector:
            menu = curses_screen.items_t_selector
            menu_len = self.i_t_selector_len
        else:
            menu = curses_screen.items_t_menu
            menu_len = self.i_t_menu_len

        menu_lines = int(math.ceil(float(menu_len) / float(self.ncols)))

        # avail lines are used for drawing content
        self.avail_lines = self.nlines - curses_screen.CONTENT_LINE - \
            menu_lines - 2

        s_line = self.nlines - menu_lines
        n_items_line = self.ncols / curses_screen.MENU_ITEM_SIZE

        c = 0 # currently used cols (20 chars per menu item)

        for i in menu:
            if not (c / curses_screen.MENU_ITEM_SIZE)  < n_items_line:
                c = 0;s_line += 1

            self.stdscr.addstr(s_line, c,i)
            c+= curses_screen.MENU_ITEM_SIZE

#-------------------------------------------------------------------------------

    def start_text_interface(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        self.draw_all_screen()

#-------------------------------------------------------------------------------

    def clear_screen(self, draw_content=True):
        del(self.content_pad)
        self.content_pad = None
        self.cleanup_cnt_bg(draw_content)

#-------------------------------------------------------------------------------
    def clear_all_screen(self):
        """clear_all_screen()"""
        self.stdscr.clear()
        self.stdscr.refresh()
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        print curses.tigetstr('sgr0')

#-------------------------------------------------------------------------------

    def exit_text_interface(self):
        self.clear_all_screen()
        sys.exit(0)

#-------------------------------------------------------------------------------

class command(dict):
#-------------------------------------------------------------------------------
    def __str__(self):
        s_cmd = ""
        
        for cmd_key in self.keys():
            s_cmd += " ".join(self.get(cmd_key)) + "\n"
            
        return s_cmd[:-1] # get rid of last newline
        