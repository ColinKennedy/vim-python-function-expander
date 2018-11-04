#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module that trims arguments out of function calls.'''

# IMPORT THIRD-PARTY LIBRARIES
import jedi

# IMPORT LOCAL LIBRARIES
from . import call_visitor
from .. import config
from . import parser


class _CommonParameterExcluder(call_visitor.MultiLineCallVisitor):

    '''A class that can parse Python AST nodes into text.'''

    def __init__(self, excluded_keywords, indent='    '):
        '''Create the instance and store keywords to exclude.

        Args:
            excluded_keywords (set[tuple[str, str]]):
                All the keyword and value pairs which will, if found, will not
                be added to the returned text.
            indent (str):
                The text that will be used for indentation.

        '''
        super(_CommonParameterExcluder, self).__init__(indent)
        self.excluded_keywords = excluded_keywords

    def _is_allowed(self, node):
        '''bool: If the given node isn't listed as an excluded keyword.'''
        return (node.arg, node.value.as_string()) not in self.excluded_keywords

    def _get_args(self, node):
        '''list[str]: Add newline and extra space to each arg and kwarg.'''
        args = [arg.accept(self) for arg in node.args]

        keywords = []

        if node.keywords:
            keywords = [
                kwarg.accept(self) for kwarg in node.keywords if
                self._is_allowed(kwarg)]

        args.extend(keywords)
        return self._format_args(args)


class MultiLineParameterExcluder(_CommonParameterExcluder):

    '''A class that can parse Python AST nodes into a multi-line statement.'''

    pass


class SingleLineParameterExcluder(_CommonParameterExcluder):

    '''A class that can parse Python AST nodes into a single statement.'''

    def _format_args(self, args):
        '''str: Return the args as a comma-separate list.'''
        return ', '.join(args)


def adjust_cursor(code, row, column):
    '''Change the user's cursor to be inside of ()s of some callable object.

    Jedi is picky about where the cursor sits so, in case the user's cursor
    isn't quite where it needs to be, this function will fix it before the
    user's script is parsed.

    Args:
        code (str): The code to use as a reference for adjusting the cursor.
        row (int): A 1-based line number where the cursor sits.
        column (int): A 0-based position on `row` where the cursor sits.

    Returns:
        tuple[int, int]: The adjusted row and column.

    '''
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


def format_lines(code, node, visited_lines):
    '''Replace code with text that has been run through a visitor.

    Args:
        code (str): The original code to replace.
        node (`astroid.Node`): The callable object that will be replaced.
        visited_lines (iter[str]): The lines to replace `code` with.

    Returns:
        list[str]:
            The code, now with `visited_lines` in-place of the original text.

    '''
    lines = code.split('\n')
    indent = get_indent(lines[node.fromlineno - 1])
    output_lines = ['{indent}{text}'.format(indent=indent, text=text)
                    for text in visited_lines]

    start = node.fromlineno - 1
    end = parser.get_tolineno(node, lines)
    lines[start:end] = output_lines

    return lines


def get_indent(text):
    '''str: Find the existing indent from `text`.'''
    return text[:len(text) - len(text.lstrip())]


def get_trimmed_keywords(code, row, column, adjust=True):
    '''Delete the keyword(s) that are set to default value.

    Args:
        code (str): The Python text to trim.
        row (int): The 1-based index that represents the user's cursor, horizontally.
        column (int): The 0-based index that represents the user's cursor, vertically.

    Returns:
        tuple[str, `astroid.node` or NoneType]: The trimmed code.

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

    is_multiline = node.fromlineno != node.tolineno
    excluded_keywords = parser.get_unchanged_keywords(node, script)

    indent = config.get_indent_preference()

    if is_multiline:
        visitor = MultiLineParameterExcluder(excluded_keywords, indent=indent)
    else:
        visitor = SingleLineParameterExcluder(excluded_keywords, indent=indent)

    lines = format_lines(code, node, visitor(node).split('\n'))

    return ('\n'.join(lines), node)
