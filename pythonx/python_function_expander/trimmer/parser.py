#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import re

# IMPORT THIRD-PARTY LIBRARIES
import astroid

# IMPORT LOCAL LIBRARIES
# TODO : Make relative
# from . import common
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


def get_call(code, row):
    '''Find the node in some code that is closest to the given row.

    Args:
        code (str): The Python code to parse.
        row (int): The row where the Call objects is expected to be.

    Returns:
        <astroid.Call> or NoneType: The found node, if any.

    '''
    node = astroid.parse(code)
    visitor = CallVisitor()
    visitor.visit(node)

    for node in visitor.expressions:
        if isinstance(node, astroid.Call):
            is_row_on_single_line_call = (node.fromlineno == node.tolineno and row == node.fromlineno)
            is_row_within_multi_line_call = (node.fromlineno != node.tolineno and row >= node.fromlineno and row <= node.tolineno)

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
        list[tuple[str, str]]: The keyword name and its default value.

    '''
    # TODO : Update docstring Returns
    # TODO : This needs to be chosen somehow
    signature = script.call_signatures()[0]

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
        list[tuple[str, str]]: The keywords and their defined default values.

    '''
    # TODO : Update docstring Returns
    items = dict()
    keywords = node.keywords or []

    for child in keywords:
        items[child.arg] = child.value.as_string()

    return items


def get_unchanged_keywords(node, script):
    '''Check some code and determine which call keywords are set to their defaults.

    Args:
        node (<astroid.Call>): The callable object to parse.
        (<jedi.Script>): The script whose row/column is positioned directly
                         over the call that must be parsed for parameter data.

    Returns:
        list[tuple[str, str]]: The keywords and their defined default values.

    '''
    parameters = get_parameter_info(script)
    values = get_parameter_values(node)

    unchanged = []

    if set(parameters.keys()) != set(values.keys()):
        raise RuntimeError('Parsing node failed. Cannot continue')

    for keyword in parameters.keys():
        value = values[keyword]
        if parameters[keyword] == value:
            unchanged.append((keyword, value))

    return unchanged
