#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Any generic function that is used across multiple modules.'''


def get_default(text):
    '''Get the default value of some parameter.

    Args:
        text (str): The name and default value of a parameter.
                    This comes in the form "foo=bar" and "bar" is the default.

    Returns:
        str: The found default.

    '''
    try:
        index = text.index('=')
    except ValueError:
        return ''

    default = text[index + 1:]

    if default == '...':  # `typeshed` frequently shows just a ... for default values.
        return ''

    return default
