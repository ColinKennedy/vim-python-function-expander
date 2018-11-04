#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT THIRD-PARTY LIBRARIES
try:
    from astroid import as_string
except ImportError:
    import sys
    import os

    _ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(os.path.join(_ROOT, 'vendors'))

    from astroid import as_string


class MultiLineCallVisitor(as_string.AsStringVisitor):

    '''A visitor that re-prints `astroid.Call` nodes in a multi-line style.

    Attributes:
        _single_line_exceptions (tuple[str]):
            Any functions, by-name, which should not allowed to be made multi-line.

    '''

    _single_line_exceptions = ('super', )

    def _format_args(self, args):
        '''Change the given arguments into "multi-line" style arguments.

        Args:
            args (list[str]):
                The list of args/kwargs to change.

        Returns:
            list[str]: The multi-line representation of `args`.

        '''
        if not args:
            return ''

        # `args` has a chance of being a tuple. We need indexing so convert it to a list
        args = list(args)

        # Add proper indentation to every arg
        args[0] = '\n{indent}'.format(indent=self.indent) + args[0]
        args = [args[0]] + ['{indent}{name}'.format(indent=self.indent, name=name) for name in args[1:]]

        # Add commas to every arg, including the last arg
        args[-1] += ',\n'
        args = ',\n'.join(args)

        return args

    def _get_args(self, node):
        '''list[str]: Add newline and extra space to each arg and kwarg.'''
        args = [arg.accept(self) for arg in node.args]

        keywords = []

        if node.keywords:
            keywords = [kwarg.accept(self) for kwarg in node.keywords]

        args.extend(keywords)
        return self._format_args(args)

    def visit_call(self, node):
        '''Expand an `astroid.Call` object into a valid Python string.

        Args:
            node (`astroid.Call`): The node to create a string representation for.

        Returns:
            str: The printable representation of the given `node`.

        '''
        expression = node.func.accept(self)

        try:
            if node.func.name in self._single_line_exceptions:
                return node.as_string()
        except AttributeError:
            # This only happens if node is a `astroid.Attribute`
            # An attribute will never be in the list of function exceptions so
            # just ignore it.
            #
            pass

        args = self._get_args(node)

        return '{expression}({args})'.format(expression=expression, args=args)
