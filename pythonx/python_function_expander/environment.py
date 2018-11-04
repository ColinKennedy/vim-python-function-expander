#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT THIRD-PARTY LIBRARIES
import vim

# IMPORT LOCAL LIBRARIES
from . import config


def init():
    '''Get the user's preferred indentation, if they have it defined.'''
    try:
        indent = vim.eval('g:vim_python_style_swapper_indent')
    except Exception:
        pass
    else:
        config.register_indent_preference(indent)
        return

    if vim.eval('&expandtab'):
        default_indent = '    '
    else:
        default_indent = '\t'

    config.register_indent_preference(default_indent)
