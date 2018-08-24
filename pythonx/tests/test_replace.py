#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A series of tests to make sure unused args are deleted correctly.'''

# IMPORT STANDARD LIBRARIES
import textwrap
import unittest

# IMPORT 'LOCAL' LIBRARIES
from python_function_expander.trimmer import trimmer


class RegexTrim(unittest.TestCase):

    '''A TestCase that checks to make sure unused args are deleted correctly.'''

    @staticmethod
    def _acquire_cursor(text):
        '''Get the cursor in some text and remove the cursor marker.

        Args:
            text (str): The code to find a cursor for.

        Returns:
            tuple[str, tuple[int, int]]:
                The modified code, followed by the row and column that the cursor
                was found in.

        '''
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
        '''Check that the given code works the way we expect.

        Args:
            expected (str): What (ideally) should be the output of `code` after
                            unused arguments have beem trimmed.
            code (str): The code to process.

        '''
        (code, (row, column)) = self._acquire_cursor(code)
        output, call = trimmer.get_trimmed_keywords(code, row, column)

        # raise ValueError(expected)
        # raise ValueError(code)
        # raise ValueError(output)

        for index, (char1, char2) in enumerate(zip(expected, output)):
            if char1 != char2:
                raise ValueError(index, char1, char2, output[:index + 1], expected[:index + 1])

        # raise ValueError(output)
        self.assertEqual(expected, output)

    def test_single_line_001(self):
        '''Remove unused arguments even if the cursor isn't directly on one.'''
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

    def test_single_line_002(self):
        '''Remove unused arguments even if the cursor isn't directly on one.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            stuff('asfd')
            foo(bar, |f|izz, thing=None, another=9)
            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            stuff('asfd')
            foo(bar, fizz, another=9)
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_single_line_003(self):
        '''Remove unused arguments even when the cursor is on the start of the function.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            stuff('asfd')
            foo|(|bar, fizz, thing=None, another=9)
            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            stuff('asfd')
            foo(bar, fizz, another=9)
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_single_line_004(self):
        '''Remove unused arguments even when the cursor is not in the function.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            stuff('asfd')
            f|o|o(bar, fizz, thing=None, another=9)
            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            stuff('asfd')
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
        '''Remove unused arguments and preserve the user's whitespace.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            foo(
                bar,
                    fizz,
                    another=8,
                        |t|hing='tt'
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
                        thing='tt'
            )

            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_multiline_003(self):
        '''Test to make sure that the a basic trimmer function works.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
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

            variant = 'asdf'
            foo(
                bar,
                fizz,
                another=9,
            )
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_fringe_001(self):
        '''Replace text even when the cursor is outside of the function.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
                thing=None,
                another=9,
            |)|
            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
                another=9,
            )
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_fringe_002(self):
        '''Replace text even when the cursor is outside of the function.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo|(|
                bar,
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

            variant = 'asdf'
            foo(
                bar,
                fizz,
                another=9,
            )
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_fringe_003(self):
        '''Replace text even when the cursor is on the edge of a line.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
                thing=None|,|
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

            variant = 'asdf'
            foo(
                bar,
                fizz,
                another=9,
            )
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_fringe_004(self):
        '''Replace text even when the cursor is in whitespace.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
            | |    thing=None,
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

            variant = 'asdf'
            foo(
                bar,
                fizz,
                another=9,
            )
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)

    def test_no_match_001(self):
        '''Don't remove arguments if there are none to remove.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
                thing=None,
                another=9,
            )
            os|.|path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
                thing=None,
                another=9,
            )
            os.path.join('asdf', 'asdf')'''
        )

        self._compare(expected, code)

    def test_no_match_002(self):
        '''Don't remove arguments if there are none to remove.'''
        code = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
                thing=None,
                another=9,
            )
            |a|
            os.path.join('asdf', 'asdf')
            '''
        )

        expected = textwrap.dedent(
            '''\
            import os

            def foo(bar, fizz, thing=None, another=8):
                pass

            variant = 'asdf'
            foo(
                bar,
                fizz,
                thing=None,
                another=9,
            )
            a
            os.path.join('asdf', 'asdf')
            '''
        )

        self._compare(expected, code)
