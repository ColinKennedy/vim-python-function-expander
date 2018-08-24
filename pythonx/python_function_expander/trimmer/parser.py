#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A series of helpers that are used to parse Python callable objects.'''

# IMPORT THIRD-PARTY LIBRARIES
import functools
import astroid
import re

# IMPORT LOCAL LIBRARIES
from .. import common


class CallVisitor(object):

    '''A node vistor that finds all calls for a given node.'''

    def __init__(self):
        '''Create the instance and make a container for <astroid.Call> nodes.'''
        super(CallVisitor, self).__init__()
        self.expressions = []

    def visit(self, node):
        '''Visit the given Node's children.

        Args:
            (<astroid.Node>): The node to visit.

        '''
        for child in node.get_children():
            try:
                child.accept(self)
            except AttributeError:
                self.visit(child)

    def visit_call(self, node):
        '''Add the found <astroid.Call> node to the current instance.'''
        self.expressions.append(node)
        self.visit(node)


def _get_tolineno(node, lines):
    '''Find the 'tolineno' of an astroid node.

    I'm not sure if this is a bug but astroid doesn't properly give the line numbers
    of the call.

    Example:
        >>> 1. foo(
        >>> 2.    bar,
        >>> 3.    fizz,
        >>> 4.    thing=None
        >>> 5. )

    If you were to ask me "what lines does `foo` take up?" I would say line 1-5.
    But astroid doesn't count the line where the ending ")" is positioned.
    If asked the same question, astroid would say it's lines 1-4.

    This function exists to correct that mistake.

    Args:
        node (<astroid.Call>): A called object to parse.
        lines (list[str]): The lines of source code that `node` is a part of.

    Returns:
        int: The found ending line number. If the line number could not be parsed,
             this function returns back -1, instead.

    '''
    _LINE_ENDING = re.compile('\)(?:\s*#[\w\s]+)?$')
    # tolineno is 1-based so subtract 1
    zeroed_lineno = node.tolineno - 1

    if _LINE_ENDING.search(lines[zeroed_lineno]):
        return node.tolineno

    for index, line in enumerate(lines[zeroed_lineno + 1:]):
        index += 1  # Make the line 1-based

        if _LINE_ENDING.search(line):
            return node.tolineno + index

    # This shouldn't ever happen because the cases above should catch it
    return -1


def get_call(code, row):
    '''Find the node in some code that is closest to the given row.

    Args:
        code (str): The Python code to parse.
        row (int): The 0-based row where the Call objects is expected to be.

    Returns:
        <astroid.Call> or NoneType: The found node, if any.

    '''
    node = astroid.parse(code)
    visitor = CallVisitor()
    visitor.visit(node)

    lines = code.split('\n')

    get_real_tolineno = functools.partial(_get_tolineno, lines=lines)

    for node in visitor.expressions:
        if isinstance(node, astroid.Call):
            tolineno = get_real_tolineno(node)
            is_row_on_single_line_call = (node.fromlineno == tolineno and row == node.fromlineno)
            is_row_within_multi_line_call = (node.fromlineno != tolineno and row >= node.fromlineno and row <= tolineno)

            if is_row_on_single_line_call or is_row_within_multi_line_call:
                return node


def get_parameter_info(script):
    '''Find the parameter definition for a function call and its default values.

    Note:
        This function does NOT give the default value that the user wrote
        for the function call. It's the default value that was used for the
        object's definition. To get the actual default value info, use <get_parameter_values>.

    Args:
        (<jedi.Script>): The script whose row/column is positioned directly
                         over the call that must be parsed for parameter data.

    Returns:
        dict[str, str]: The keywords and their defined default values.

    '''
    # TODO : This needs to be chosen somehow
    try:
        signature = script.call_signatures()[0]
    except IndexError:
        return dict()

    info = dict()
    for parameter in signature.params:
        default = common.get_default(parameter.description)

        if default:
            info[str(parameter.name)] = default

    return info


def get_parameter_values(node):
    '''Find the parameter definition for a function call and its default values.

    Note:
        This function gives the value that the user wrote for the function call.
        To get the default value for that callable object's definition,
        use <get_parameter_info>.

    Args:
        node (<astroid.Call>): The callable object to parse.

    Returns:
        dict[str, str]: The keywords and the user's defined value.

    '''
    items = dict()
    keywords = node.keywords or []

    for child in keywords:
        items[child.arg] = child.value.as_string()

    return items


def get_unchanged_keywords(node, script):
    '''Check some code and determine which call keywords are set to their defaults.

    Args:
        node (<astroid.Call>):
            The callable object to parse.
        script (<jedi.Script>):
            The script whose row/column is positioned directly over the call
            that must be parsed for parameter data.

    Raises:
        RuntimeError:
            If astroid and Jedi created different keyword results.
            This should never happen but, if it did, it'll create many errors
            so this function bails out early.

    Returns:
        list[tuple[str, str]]: The keywords and their defined default values.

    '''
    parameters = get_parameter_info(script)
    values = get_parameter_values(node)

    if not parameters or not values:
        return dict()

    unchanged = []

    if set(parameters.keys()) != set(values.keys()):
        raise RuntimeError('Parsing node failed. Cannot continue')

    for keyword, default in parameters.items():
        value = values[keyword]
        if default == value:
            unchanged.append((keyword, value))

    return unchanged
