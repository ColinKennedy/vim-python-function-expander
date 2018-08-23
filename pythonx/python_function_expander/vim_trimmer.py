#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT THIRD-PARTY LIBRARIES
import UltiSnips
import vim

# IMPORT LOCAL LIBRARIES
# TODO : Make local import
import trimmer


def _to_vim(cursor):
    return (cursor[0] + 1, cursor[1])


def _set_cursor(cursor):
    vim.current.window.cursor = _to_vim(cursor)


def _trim_unchanged_parameters_in_buffer(snippet):
    code = '\n'.join(snippet.buffer)
    (row, column) = snippet.cursor

    trimmed_code, call = trimmer.get_trimmed_keywords(code, row, column)

    if not call:
        return

    trimmed_lines = trimmed_code.splitlines()
    snippet.buffer[:] = trimmed_lines

    first_non_whitespace_character_column = \
        len(trimmed_lines[call.fromlineno - 1]) - \
        len(trimmed_lines[call.fromlineno - 1].lstrip())

    _set_cursor((call.fromlineno - 1, first_non_whitespace_character_column))


def trim_unchanged_parameters_in_buffer():
    # Note: I took this next section from <UltiSnips.snippet.definition._base.SnippetDefinition._eval_code>
    current = vim.current

    _locals = {
        'window': current.window,
        'buffer': current.buffer,
        'line': current.window.cursor[0] - 1,
        'column': current.window.cursor[1] - 1,
        'cursor': UltiSnips.snippet.definition._base._SnippetUtilCursor(current.window.cursor),
    }

    snip = UltiSnips.text_objects._python_code.SnippetUtilForAction(_locals)
    _trim_unchanged_parameters_in_buffer(snip)
