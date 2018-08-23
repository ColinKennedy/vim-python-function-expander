#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module that trims arguments out of function calls.'''

# IMPORT STANDARD LIBRARIES
import re

# IMPORT THIRD-PARTY LIBRARIES
import jedi

# IMPORT LOCAL LIBRARIES
from . import parser

import textwrap
_FUNCTION_TEMPLATE = textwrap.dedent(
    '''
    (.*)
    {keyword}\s*=\s*{value}\s*,
    (?:\s*\#[\w\ \t]+)?  # An optional in-line user comment, if it exists
    (\S*)
    (?:\n)?
    (?:\s\n+(\s*)|(\s*))
    '''
)
_FUNCTION_TEMPLATE = textwrap.dedent(
    '''
    (?:.*)
    {keyword}\s*=\s*{value}\s*,
    (?:\s*\#[\w\ \t]+)?  # An optional in-line user comment, if it exists
    (\S*)
    (?:\n)?
    (?:\s)
    '''
)
# _FUNCTION_TEMPLATE = textwrap.dedent(
#     '''
#     (?:\s*)
#     {keyword}\s*=\s*{value}\s*,
#     (?:\s*\#[\w\ \t]+)?  # An optional in-line user comment, if it exists
#     (\S*)
#     (\n)?
#     (?:\s)
#     '''
# )
# _FUNCTION_TEMPLATE = textwrap.dedent(
#     '''
#     (.*)
#     {keyword}\s*=\s*{value}\s*,
#     (?:\s*\#[\w\ \t]+)?  # An optional in-line user comment, if it exists
#     (?:\n([\ \t]*))?
#     '''
# )


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

    # def _get_code():
    #     return cropped_code

    # def replace(match):
    #     def get_indent(text):
    #         return text[:len(text) - len(text.lstrip())]

    #     def find_line_index(code, marker):
    #         lines = code.split('\n')
    #         count = 0

    #         for index, line in enumerate(lines):
    #             for char in line:
    #                 if count == marker:
    #                     return index
    #                 count += 1

    #         return -1

    #     code = _get_code()
    #     lines = code.split('\n')
    #     row = find_line_index(code, match.start())

    #     try:
    #         # print('asdfsd', lines)
    #         return get_indent(lines[row + 1])
    #     except IndexError:
    #         return ''

    #     return ''

    def replace(match):
        print('t', match.group())
        return ''

    for name, value in parser.get_unchanged_keywords(call, script):
        expression = _FUNCTION_TEMPLATE.format(
            keyword=name,
            value=value,
        )
        expression = re.compile(expression, re.VERBOSE | re.MULTILINE)

        cropped_code = expression.sub(r'\1', cropped_code)
        # cropped_code = expression.sub(replace, cropped_code)

    lines = code.split('\n')
    lines[call.fromlineno - 1:call.tolineno + 1] = cropped_code.split('\n')

    return ('\n'.join(lines), call)
