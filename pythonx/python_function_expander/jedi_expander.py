#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A module that generates UltiSnips arguments for callable objects on-the-fly.'''

# IMPORT THIRD-PARTY LIBRARIES
from UltiSnips import snippet_manager
import jedi_vim
import jedi
import vim


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


def needs_update(line, column):
    '''bool: Check if the source-code line is ready to be expanded.'''
    if len(line) < column:
        return False

    try:
        previous_character = line[column - 1]
    except IndexError:
        return False

    try:
        next_character = line[column]
    except IndexError:
        return False

    return previous_character == '(' and next_character == ')'


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


def get_parameter_details(parameter, lines, name):
    '''Get the UltiSnips representation of a parameter.

    Note:
        if the user has `let g:expander_use_local_variables = '0'` then `name`
        will be returned as the default value.

    Args:
        parameter (:class:`jedi.api.classes.Definition`):
            The parameter whose name and default value will be parsed.
        lines (list[str]):
            The source code whose last line contains the line that we want to
            generate the snippet for as well as all lines before it.
        name (str):
            The fallback value which will be used if no default value was found
            or if the user specifies to not use local variables.

    Returns:
        tuple[str, str]:
            The UltiSnips-style string and the string's default value, if
            the parameter was an optional parameter.

    '''
    def is_optional(description):
        '''bool: Check if the given description is from an optional parameter.'''
        return '=' in description

    if not is_optional(parameter.description):
        return ('${{{tabstop}:{name}}}', '')

    argument = '{name}=${{{tabstop}:{default}}}'

    if vim.eval("get(g:, 'expander_use_local_variables', '1')") == '0':
        return (argument, _get_default(parameter.description))

    default = get_default(
        lines,
        name=name,
        fallback=_get_default(parameter.description),
    )
    return (argument, default)


def get_parameter_snippet(parameters, lines=None):
    '''Create a snippet for a Python callable object.

    Args:
        parameters (list[:class:`jedi.api.classes.Definition`]):
            The parameters which will be converted into an UltiSnips snippet.
        lines (list[str]):
            The source code whose last line contains the line that we want to
            generate the snippet for as well as all lines before it.

    Returns:
        str: The generated snippet.

    '''
    if not lines:
        lines = []

    arguments = []
    tabstop = 1  # UltiSnips tabstops start at 1 (0 is a reserved tabstop)

    for parameter in parameters:
        name = get_description_name(parameter.description)
        argument, default = get_parameter_details(parameter, lines, name)
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


def get_balanced_parenthesis():
    '''Recommend the character(s) needed to append to the current line.

    jedi-vim cannot find signatures for a callable object if the line has
    unbalanced parenthesis. So if the user is on a line that looks like "foo("
    then it needs to be changed to "foo()" to be parseable.

    Returns:
        str: The characters to balance a string.

    '''
    (row, _) = vim.current.window.cursor
    current_line = vim.current.buffer[row - 1]

    if current_line.strip()[-1] != ')':
        return ')'
    return ''


# Note: This is a copy/paste of jedi_vim.clear_call_signatures. The only
#       difference is that we modify the buffer using snip.buffer and snip.cursor,
#       instead of vim.current.buffer and vim.cursor. This is important because
#       UltiSnips requires us to make modifications to the current buffer through
#       `snip`, otherwise it will error
#
# @jedi_vim.catch_and_print_exceptions
def clear_call_signatures(snip):
    '''Clear the current buffer of any Jedi-completion menus.'''
    import re

    # Check if using command line call signatures
    if int(jedi_vim.vim_eval("g:jedi#show_call_signatures")) == 2:
        jedi_vim.vim_command('echo ""')
        return
    cursor = snip.cursor
    e = jedi_vim.vim_eval('g:jedi#call_signature_escape')
    # We need two turns here to search and replace certain lines:
    # 1. Search for a line with a call signature and save the appended
    #    characters
    # 2. Actually replace the line and redo the status quo.
    py_regex = r'%sjedi=([0-9]+), (.*?)%s.*?%sjedi%s'.replace(
        '%s', re.escape(e))
    for i, line in enumerate(snip.buffer):
        match = re.search(py_regex, line)
        if match is not None:
            # Some signs were added to minimize syntax changes due to call
            # signatures. We have to remove them again. The number of them is
            # specified in `match.group(1)`.
            after = line[match.end() + int(match.group(1)):]
            line = line[:match.start()] + match.group(2) + after
            snip.buffer[i] = line
    snip.cursor = cursor


def expand_signatures(snip, force=False):
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

    Args:
        cursor (:class:`UltiSnips.text_objects._python_code.SnippetUtilForAction`):
            A controller which can get/set the user's position in the current buffer.
        force (:obj:`bool`, optional):
            If True, the signature will expand. If False, then the current line
            will be "checked" to see if it needs expansion. Default is False.

    '''
    if vim.eval('g:jedi#show_call_signatures') == '1':
        # Jedi literally places text into a line in the current buffer to show
        # the user any completion options when the mode is set to 1.
        # If this completion-text is visible in Vim once `expand_signatures`
        # is called then it would cause `call_signatures` to fail to return []
        # and then our function will do nothing.
        #
        # To avoid that, we call `clear_call_signatures`, beforehand.
        # Also notice that `jedi_vim.show_call_signatures` does this, too!
        #
        clear_call_signatures(snip)

    script = jedi_vim.get_script()
    signatures = script.call_signatures()

    if not signatures:
        return

    (row, column) = vim.current.window.cursor
    current_row_index = row - 1
    code = script._code_lines
    lines = code[:current_row_index + 1]

    if not lines:
        return

    lines[-1] = lines[-1].rstrip()

    if force or needs_update(lines[-1], column):
        snippet = get_parameter_snippet(
            signatures[0].params,
            lines=lines,
        )
        snippet_manager.UltiSnips_Manager.expand_anon(snippet)

        if snip:
            # Make sure the user's cursor doesn't move, even after expanding the snippet
            snip.cursor.preserve()
