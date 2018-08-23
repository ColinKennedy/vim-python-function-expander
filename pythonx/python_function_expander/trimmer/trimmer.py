#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module that trims arguments out of function calls.'''

# IMPORT STANDARD LIBRARIES
import re

# IMPORT THIRD-PARTY LIBRARIES
import jedi

# IMPORT LOCAL LIBRARIES
from . import parser


_FUNCTION_TEMPLATE = r'(.*){keyword}\s*=\s*{value}\s*,(?:\s*#[\w\ \t]+)?(\S*)(?:\n)?(\s*)'


def get_trimmed_keywords(code, row, column):
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

    # TODO : In the future, remove the `environment` keyword so that Jedi can
    #        run using Python 3.
    #
    script = jedi.Script(code, row, column, environment=jedi.get_system_environment('2'))

    if not script:
        return (code, None)

    cropped_code = '\n'.join(code.splitlines()[call.fromlineno - 1:call.tolineno + 1])

    for name, value in parser.get_unchanged_keywords(call, script):
        expression = _FUNCTION_TEMPLATE.format(
            keyword=name,
            value=value,
        )

        cropped_code = re.sub(
            expression,
            r'\1\2',
            cropped_code,
            re.VERBOSE,
        )

    lines = code.split('\n')
    lines[call.fromlineno - 1:call.tolineno + 1] = cropped_code.split('\n')

    return ('\n'.join(lines), call)
