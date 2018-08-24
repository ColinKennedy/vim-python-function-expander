#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module which trims text out of Vim's current buffer.'''

# IMPORT THIRD-PARTY LIBRARIES
import vim

# IMPORT LOCAL LIBRARIES
from . import trimmer


def _to_vim(cursor):
    '''tuple[int, int]: Change the given cursor to a Vim cursor, which is base-1.'''
    # Reference: https://github.com/reconquest/vim-pythonx
    #            I copied the code from this repository, to avoid the extra dependency
    #
    return (cursor[0] + 1, cursor[1])


def _set_cursor(cursor):
    '''Set the current cursor as the user's cursor in the current buffer.'''
    # Reference: https://github.com/reconquest/vim-pythonx
    #            I copied the code from this repository, to avoid the extra dependency
    #
    vim.current.window.cursor = _to_vim(cursor)


def trim_unchanged_arguments_in_buffer():
    '''Remove any unneeded arguments in the function call of the user's cursor.'''
    code = '\n'.join(vim.current.window.buffer)
    (row, column) = vim.current.window.cursor

    trimmed_code, call = trimmer.get_trimmed_keywords(code, row, column)

    if not call:
        return

    trimmed_lines = trimmed_code.splitlines()
    vim.current.window.buffer[:] = trimmed_lines

    first_non_whitespace_character_column = \
        len(trimmed_lines[call.fromlineno - 1]) - \
        len(trimmed_lines[call.fromlineno - 1].lstrip())

    _set_cursor((call.fromlineno - 1, first_non_whitespace_character_column))
