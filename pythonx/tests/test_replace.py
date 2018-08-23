#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT STANDARD LIBRARIES
import textwrap
import unittest

# IMPORT 'LOCAL' LIBRARIES
from python_function_expander.trimmer import trimmer


class RegexTrim(unittest.TestCase):
    @staticmethod
    def _acquire_cursor(text):
        lines = text.split('\n')

        for row, line in enumerate(lines):
            try:
                index = line.index('|')
            except ValueError:
                continue

            if line[index + 2] == '|':
                lines[row] = line.replace('|', '')
                return ('\n'.join(lines), (row + 1, index))

        raise ValueError('No cursor was found.')

    def _compare(self, expected, code):
        (code, (row, column)) = self._acquire_cursor(code)
        output, call = trimmer.get_trimmed_keywords(code, row, column)

        # raise ValueError(expected)
        # raise ValueError(code)
        raise ValueError(output)

        for index, (char1, char2) in enumerate(zip(expected, output)):
            if char1 != char2:
                raise ValueError(index, char1, char2, output[:index + 1], expected[:index + 1])

        # raise ValueError(output)
        self.assertEqual(expected, output)

    def test_single_line(self):
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            foo(bar, |f|izz, thing=None, another=9)

            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            foo(bar, fizz, another=9)

            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_multiline_001(self):
        '''Test to make sure that the a basic trimmer function works.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            foo(
                b|a|r,
                fizz,
                thing=None,
                another=9,
            )

            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            foo(
                bar,
                fizz,
                another=9,
            )

            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_multiline_002(self):
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            foo(
                bar,
                    fizz,
                    another=8,
                        |t|hing='thasdf'
            )

            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            foo(
                bar,
                    fizz,
                        thing='tt',
            )

            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    # def test_fringe_001(self):
    #     '''Replace text even when the cursor is outside of the function.'''

    # def test_fringe_002(self):
    #     '''Replace text even when the cursor is outside of the function.'''

    # def test_fringe_003(self):
    #     '''Replace text even when the cursor is on the edge of a line.'''

    # def test_fringe_004(self):
    #     '''Replace text even when the cursor is in whitespace.'''
