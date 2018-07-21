#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module that generates UltiSnips arguments for callable objects on-the-fly.'''

# IMPORT THIRD-PARTY LIBRARIES
from UltiSnips import snippet_manager
import jedi_vim
import jedi
import vim

# IMPORT LOCAL LIBRARIES
import cache


def _get_default(text):
    '''Get the default value of some parameter.

    Args:
        text (str): The name and default value of a parameter.
                    This comes in the form "foo=bar" and "bar" is the default.

    Returns:
        str: The found default.

    '''
    index = text.index('=')
    return text[index + 1:]


def join_columnwise(arguments):
    '''Combine the given arguments vertically.

    Args:
        arguments (list[str]):
            The arguments to join. These could contain a name or name + default.

    Returns:
        str: The joined text.

    '''
    # TODO : Maybe take this indent from a global variable or something?
    indent = '    '
    arguments = ['\n{indent}{argument},'.format(indent=indent, argument=argument)
                 for argument in arguments]
    return ''.join(arguments)


def get_description_name(text):
    '''Get the name of a parameter from its description.

    Args:
        text (str): The text to check. Usually it looks like "param foo=bar"
                    Where "foo" is the name that we want to return.

    Returns:
        str: The found name.

    '''
    try:
        index = text.index('=')
        text = text[:index]
    except ValueError:
        pass

    return text.replace('param ', '')


def get_default(lines, name, fallback=''):
    '''Recommend a good default name for some variable based on what is in-scope.

    Args:
        lines (list[str]):
            The lines of code to check for variables within.
        name (str):
            The name of the variable which will be checked if it's in-scope.
        fallback (str, optional):
            If `name` is not in-scope, this value is returned instead. Default: "".

    Returns:
        str: The recommended default name.

    '''
    def _get_indent(text):
        '''int: The leading indentation of some string.'''
        return len(text) - len(text.lstrip())

    indent = _get_indent(lines[-1])

    # We need to insert our fake line ONE line above the last line
    fake_line = '{indent}{name}\n'.format(indent=(' ' * indent), name=name)
    fake_lines = lines[:-1] + [fake_line] + [lines[-1]]
    row = len(fake_lines) - 1  # This is the row of our 'fake_line'
    column = len(fake_line) - 1
    code = ''.join(fake_lines)

    new_script = jedi.Script(code, row, column)
    for completion in new_script.completions():
        if completion.name == name:
            return name

    return fallback


def get_parameter_snippet(parameters, lines=None):
    '''Create a snippet for a Python callable object.

    Args:
        parameters (list[]):
            The parameters which will be converted into an UltiSnips snippet.
        lines (list[str]):
            The source code whose last line contains the line that we want to
            generate the snippet for as well as all lines before it.

    Returns:
        str: The generated snippet.

    '''
    def is_optional(description):
        '''bool: Check if the given description is from an optional parameter.'''
        return '=' in description

    if not lines:
        lines = []

    arguments = []
    tabstop = 1  # UltiSnips tabstops start at 1 (0 is a reserved tabstop)

    for parameter in parameters:
        name = get_description_name(parameter.description)
        default = ''

        if not is_optional(parameter.description):
            argument = '${{{tabstop}:{name}}}'
        else:
            argument = '{name}=${{{tabstop}:{default}}}'
            default = get_default(
                lines,
                name,
                fallback=_get_default(parameter.description),
            )

        arguments.append(argument.format(tabstop=tabstop, name=name, default=default))
        tabstop += 1

    length = sum([len(argument_) for argument_ in arguments])
    column = len(lines[-1].rstrip())
    if length + column < 79:
        return ', '.join(arguments)

    # Add one more tabstop at the end, just to make it easier to navigate
    # through the function
    #
    return join_columnwise(arguments) + '${{{tabstop}}}\n'.format(tabstop=tabstop)


def log(func):
    '''Log a function if it fails to execute.'''
    import traceback

    def function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            with open('/tmp/foo', 'w') as file_:
                file_.write(traceback.format_exc())

    return function


def expand_signatures(snip):
    '''Create an anonymous snippet at the current cursor location.

    It works like this - type code like you normally do and, when Jedi generates
    object argument auto-completion, also create and expand an UltiSnips snippet
    with the same information.

    Your text:
        >>> import textwrap
        >>> textwrap.fill()

    And then after:
        >>> import textwrap
        >>> textwrap.fill(text, width=70, **kwargs)

    And tabstops are generated for each argument, automatically. Sweet, right?

    There's one more feature which you can call a convenience.
    If you have a variable in-scope that matches the name of a parameter in
    the auto-completion results, it's used instead. So in the previous example...

    Your text:
        >>> import textwrap
        >>> width = 100
        >>> textwrap.fill()

    And then after:
        >>> import textwrap
        >>> width = 100
        >>> textwrap.fill(text, width=width, **kwargs)

    `width` was applied because you defined it earlier. Of course, this works
    with classes, nested functions, etc because it uses Jedi as the back-end.

    '''
    if int(jedi_vim.vim_eval("has('conceal') && g:jedi#show_call_signatures")) == 0:
        return

    script = jedi_vim.get_script()
    signatures = script.call_signatures()

    if not signatures:
        return

    (row, _) = vim.current.window.cursor
    current_row_index = row - 1
    code = script._code_lines
    lines = code[:current_row_index + 1]

    if not lines:
        return

    lines[-1] = lines[-1].rstrip()

    if cache.needs_update(lines):
        snippet = get_parameter_snippet(
            signatures[0].params,
            lines=lines,
        )
        snippet_manager.UltiSnips_Manager.expand_anon(snippet)

    snip.cursor.preserve()
