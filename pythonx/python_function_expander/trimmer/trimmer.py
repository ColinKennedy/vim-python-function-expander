#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module that trims arguments out of function calls.'''

# IMPORT STANDARD LIBRARIES
import textwrap
import re

# IMPORT THIRD-PARTY LIBRARIES
import jedi

# IMPORT LOCAL LIBRARIES
from . import parser


# TODO : Combine the common parts of these two templates
_SINGLE_LINE_TEMPLATE = textwrap.dedent(
    '''
    (?:[\ \t]*)
    {keyword}\s*=\s*{value}\s*,([\ \t]*)?
    (?:\#[\w\ \t]+)?  # An optional in-line user comment, if it exists
    (\S*)
    (?:\n)?
    '''
)
_FUNCTION_TEMPLATE = textwrap.dedent(
    '''
    (?:[\ \t]*)
    {keyword}\s*=\s*{value}\s*,([\ \t]*)?
    (?:\#[\w\ \t]+)?  # An optional in-line user comment, if it exists
    (\S*)
    (?:\n)?
    (\s)
    '''
)


def adjust_cursor(code, row, column):
    # TODO : Audit if I can replace "split('\n')" with "splitlines()"
    lines = code.split('\n')

    # fromlineo is 1-based so convert it to 0-based by subtracting 1
    row -= 1

    call_line = lines[row]
    try:
        column = max((call_line.index('(') + 1, column))
    except ValueError:
        # TODO : Make a unittest for this case
        # If this happens, it's because the user wrote some really weird syntax, like:
        # >>> foo\
        # >>> (bar)
        # TODO : finish this usage case
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
        tuple[str, <astroid.Call> or NoneType]: The trimmed code.

    '''
    call = parser.get_call(code, row)

    if not call:
        return (code, None)

    # TODO : Once unittesting is complete, move this logic into vim_trimmer.py instead!!!!
    if adjust:
        row, column = adjust_cursor(code, row, column)

    # TODO : In the future, remove the `environment` keyword so that Jedi can
    #        run using Python 3.
    #
    script = jedi.Script(code, row, column, environment=jedi.get_system_environment('2'))

    if not script:
        return (code, None)

    cropped_code = '\n'.join(code.splitlines()[call.fromlineno - 1:call.tolineno + 1])

    for name, value in parser.get_unchanged_keywords(call, script):
        # Our regex from above consumes
        is_multiline = call.fromlineno != call.tolineno
        if is_multiline:
            expression = _FUNCTION_TEMPLATE.format(
                keyword=re.escape(name),
                value=re.escape(value),
            )
        else:
            expression = _SINGLE_LINE_TEMPLATE.format(
                keyword=re.escape(name),
                value=re.escape(value),
            )

        expression = re.compile(expression, re.VERBOSE | re.MULTILINE)
        cropped_code = expression.sub(r'\1\2', cropped_code)

    lines = code.split('\n')
    lines[call.fromlineno - 1:call.tolineno + 1] = cropped_code.split('\n')

    return ('\n'.join(lines), call)
