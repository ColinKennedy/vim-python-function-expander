#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module which keeps caches from expanding accidentally.'''


class Expansion(object):

    '''A cache which will determine if we need to create anonymous snippets.'''

    def __init__(self, code):
        '''Store the source-code of a script for comparisons.

        Args:
            code (list[str]): The source-code to cache. It is used to check
                              future expansions so we don't continually keep
                              trying to expand the same code over and over.

        '''
        super(Expansion, self).__init__()
        self.code = code

    def needs_expanding(self, line):
        '''bool: Check if the source-code line is ready to be expanded.'''
        return line[-2:] == '()'

    def needs_update(self, code):
        '''Check if there were any changes in the code.

        Args:
            code (list[str]): The source-code to check.

        Returns:
            bool: If the current callable object's parameters need to be expanded.

        '''
        return code != self.code and self.needs_expanding(code[-1])


CACHE = None


def needs_update(code):
    '''Check if the given row has been expanded already.

    Args:
        code (list[str]): The source-code to check.

    Returns:
        bool: If the current callable object's parameters need to be expanded.

    '''
    global CACHE

    if not CACHE:
        CACHE = Expansion(code)
        output = CACHE.needs_expanding(code[-1])
        return output

    if CACHE.needs_update(code):
        CACHE.code = code
        return True

    return False
