"""
IO for mass spectral libraries in JCAMP format
"""

 #############################################################################
 #                                                                           #
 #    PyMS software for processing of metabolomic mass-spectrometry data     #
 #    Copyright (C) 2005-8 Vladimir Likic                                    #
 #                                                                           #
 #    This program is free software; you can redistribute it and/or modify   #
 #    it under the terms of the GNU General Public License version 2 as      #
 #    published by the Free Software Foundation.                             #
 #                                                                           #
 #    This program is distributed in the hope that it will be useful,        #
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
 #    GNU General Public License for more details.                           #
 #                                                                           #
 #    You should have received a copy of the GNU General Public License      #
 #    along with this program; if not, write to the Free Software            #
 #    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.              #
 #                                                                           #
 #############################################################################

import numpy

from pyms.Utils.IO import file_lines
from pyms.Utils.Utils import is_str
from pyms.Utils.Error import error

__CASNAME_KEYWORD = "##CAS NAME"
__XYDATA_KEYWORD = "##XYDATA"

import Class

def load_jcamp(file_name):

    """
    @summary: Load all records as a list

    @param file_name: The input jcamp file
    @type file_name: StringType

    @return: A records list
    @rtype: ListType

    @author: Qiao Wang
    @author: Vladimir Likic
    """

    if not is_str(file_name):
        error("'file_name' not a string")

    print " -> Reading JCAMP library '%s'" % (file_name)
    lines_list = open(file_name,'r')
    records = []
    idx1 = 0
    idx2 = 0
    fields = ''
    name_value = ''
    xydata = []
    extra_name = 0
    extra_xydata = 0
    line_num = 0
    for line in lines_list:
        prefix = line.find('#')
        if prefix == 0:
            fields = line.split('=')
            if fields[0] == __CASNAME_KEYWORD:
                # empty name value detected, abort !
                if len(fields[1].strip()) == 0:
                    message = ' The current CAS NAME has no value.'
                    prompt_error(line_num, message)
                extra_xydata = 0
                extra_name = extra_name + 1
                if extra_name == 2:
                    # duplicate name detected, abort !
                    message = ' An extra CAS NAME founded in the same record.'
                    prompt_error(line_num, message)
                idx1 = idx1 + 1
                if idx1 == 1:
                    name_value = fields[1].strip()
                elif idx1 == 2:
                    if len(xydata) == 0:
                        # empty xydata detected, abort !
                        message = ' The empty XYDATA record founded.'
                        prompt_error(line_num, message)
                    r = Class.MSLibRecord(name_value, xydata)
                    records.append(r)
                    name_value = fields[1].strip()
                    xydata = []
                    idx1 = 1
                    idx2 = 0
            elif fields[0] == __XYDATA_KEYWORD:
                extra_name = 0
                extra_xydata = extra_xydata + 1
                if extra_xydata == 2:
                    # duplicate xydata detected, abort !
                    message = ' An extra XYDATA founded in the same record.'
                    prompt_error(line_num, message)
                idx2 = idx2 + 1
            else:
                extra_name = 0
                extra_xydata = 0
        else:
            if prefix == -1 and line != '\n' and line:
                data = line.split()
                if len(data) == 1 and data[0].isdigit():
                    message = ' The XYDATA is not in pair, wrong data format.'
                    prompt_error(line_num, message)
                elif data[0].isdigit() and data[1].isdigit():
                    data = map(int, data)
                    xydata.append(data)
        line_num = line_num + 1
    r = Class.MSLibRecord(name_value, xydata)
    records.append(r)
    lines_list.close()
    print "Total number of record is: ", len(records)
    print "Total numer of lines is: ", line_num
    return records

def prompt_error(line_num, message):

    """
    @summary: prompt the error

    @param line_num: Indicates which line throws the exception
    @type line_num: IntType
    @para message: The error message
    @type message: StringType

    @author: Qiao Wang
    @author: Vladimir Likic
    """
    error('Error (line ' + str(line_num) + '):' + message)
