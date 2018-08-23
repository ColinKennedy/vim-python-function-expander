#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module that trims arguments out of function calls.'''

# IMPORT STANDARD LIBRARIES
import re

# IMPORT THIRD-PARTY LIBRARIES
import jedi

# IMPORT LOCAL LIBRARIES
from . import parser


_FUNCTION_TEMPLATE = r'(.*){keyword}\s*=\s*{value}\s*,(?:\s*#[\w\ \t]+)?(\S*)(?:\n)?(\s*)'


def get_trimmed_keywords(code, row, column):
    '''Delete the keyword(s) that are set to default value.

    Args:
        code (str): The Python text to trim.
        row (int): The 1-based index that represents the user's cursor, horizontally.
        column (int): The 0-based index that represents the user's cursor, vertically.

    Returns:
        tuple[str, <astroid.Call> or NoneType]: The trimmed code.

    '''
    call = parser.get_call(code, row)

    if not call:
        return (code, None)

    # TODO : In the future, remove the `environment` keyword so that Jedi can
    #        run using Python 3.
    #
    script = jedi.Script(code, row, column, environment=jedi.get_system_environment('2'))

    if not script:
        return (code, None)

    cropped_code = '\n'.join(code.splitlines()[call.fromlineno - 1:call.tolineno + 1])

    for name, value in parser.get_unchanged_keywords(call, script):

        expression = _FUNCTION_TEMPLATE.format(
            keyword=name,
            value=value,
        )

        cropped_code = re.sub(
            expression,
            r'\1\2',
            cropped_code,
            re.VERBOSE,
        )

    lines = code.splitlines()
    lines[call.fromlineno - 1:call.tolineno + 1] = cropped_code.splitlines()

    return ('\n'.join(lines), call)


# TODO : Remove test code
def test():
    '''Test to make sure that the trimmer function works.'''
    import textwrap
    code = textwrap.dedent(
        '''\
        import os

        def foo(bar, fizz, thing=None, another=8):
            pass

        foo(
            bar,
            fizz,
            thing=None,
            another=9,
        )

        os.path.join('asdf', 'asdf')
        '''
    )

    #code = textwrap.dedent(
    #    """\
    #    #!/usr/bin/env python
    #    # -*- coding: utf-8 -*-

    #    # IMPORT STANDARD LIBRARIES
    #    import shotgun_api3 as shotgun


    #    def main():
    #        '''Run the main execution of the current script.'''
    #        sg = shotgun.Shotgun()

    #        sg.find_one(
    #            entity_type,
    #            filters,
    #            fields='asdfsd',
    #            order=None,
    #            filter_operator=None,
    #            retired_only=False,
    #            include_archived_projects=True,
    #            additional_filter_presets=None,
    #        )


    #    if __name__ == '__main__':
    #        main()
    #    """
    #)

    lines = code.splitlines()
    for row in range(len(lines)):
        for column in range(len(lines[row])):
            # print('try', row, column)
            try:
                output, call = get_trimmed_keywords(code, row, column)
            except Exception:
                continue

            if call:
                print('found')
            if output != code:
                print('FOUND', row, column)
                print(output)


if __name__ == '__main__':
    test()
