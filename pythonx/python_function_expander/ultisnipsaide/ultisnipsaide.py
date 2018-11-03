#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT THIRD-PARTY LIBRARIES
from .px import cursor
from .px import syntax


def is_comment():
    return syntax.is_comment(cursor.get())


def is_string():
    names = ['String', 'Constant']
    syntax_names = syntax.get_names(cursor.get())
    for name in names:
        if name in syntax_names:
            return True

    return False
