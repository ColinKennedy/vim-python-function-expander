#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A simple module to store the user's style preferences.'''


INDENT_PREFERENCE = {'indent': '    '}


def get_indent_preference():
    '''str: How the user prefers their indentation. Default: "    ".'''
    return INDENT_PREFERENCE['indent']


def register_indent_preference(text):
    '''Set indentation that will be used for multi-line function calls.'''
    INDENT_PREFERENCE['indent'] = text
