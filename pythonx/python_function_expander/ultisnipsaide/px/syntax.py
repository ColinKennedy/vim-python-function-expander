#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT THIRD-PARTY LIBRARIES
import vim

# IMPORT LOCAL LIBRARIES
from . import cursor


def is_string(cursor):
    return 'String' in get_names(cursor)


# lookbehind=True will match previous character as well due weird syntax
# identification in vim, when last character in comment is not identified
# as comment.
def is_comment(cursor, lookbehind=True):
    comment = 'Comment' in get_names(cursor)

    if lookbehind:
        if cursor[1] != 0 and is_comment((cursor[0], cursor[1]-1), False):
            return True

    return comment


def get_names(position):
    try:
        syntax_stack = vim.eval('synstack({}, {})'.format(
            *cursor.to_vim_lang(position)
        ))
    except:
        return []

    names = []
    for syn_id in syntax_stack:
        names.append(
            vim.eval('synIDattr(synIDtrans({}), "name")'.format(syn_id))
        )

    return names

