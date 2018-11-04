#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module that trims arguments out of function calls.'''

# IMPORT THIRD-PARTY LIBRARIES
import astroid
import jedi

# IMPORT LOCAL LIBRARIES
from . import parser


def adjust_cursor(code, row, column):
    # TODO : Audit if I can replace "split('\n')" with "splitlines()"
    lines = code.split('\n')

    # fromlineo is 1-based so convert it to 0-based by subtracting 1
    row -= 1

    call_line = lines[row]
    try:
        column = max((call_line.index('(') + 1, column))
    except ValueError:
        # If this happens, it's because the user wrote some really weird syntax, like:
        #
        # >>> foo\
        # >>> (bar)
        #
        pass

    # Set row back to 1-based
    row += 1
    return (row, column)


def get_trimmed_keywords(code, row, column, adjust=True):
    '''Delete the keyword(s) that are set to default value.

    Args:
        code (str): The Python text to trim.
        row (int): The 1-based index that represents the user's cursor, horizontally.
        column (int): The 0-based index that represents the user's cursor, vertically.

    Returns:
        tuple[str, <astroid.node> or NoneType]: The trimmed code.

    '''
    node = parser.get_nearest_call(code, row)

    if not node:
        return (code, None)

    if adjust:
        row, column = adjust_cursor(code, row, column)

    # TODO : In the future, remove the `environment` keyword so that Jedi can
    #        run using Python 3.
    #
    script = jedi.Script(code, row, column, environment=jedi.get_system_environment('2'))

    if not script:
        return (code, None)

    cropped_code = '\n'.join(code.splitlines()[node.fromlineno - 1:node.tolineno + 1])

    call = node
    if isinstance(call.parent, astroid.Assign):
        call = call.parent

    is_multiline = node.fromlineno != node.tolineno

    if is_multiline:
        visitor = MultiLineParameterExcluder()
    else:
        visitor = SingleLineParameterExcluder()

    unchanged_keywords = parser.get_unchanged_keywords(node, script)

    cropped_code = visitor.as_string()
    lines = code.split('\n')
    lines[node.fromlineno - 1:node.tolineno + 1] = cropped_code.split('\n')

    return ('\n'.join(lines), node)
