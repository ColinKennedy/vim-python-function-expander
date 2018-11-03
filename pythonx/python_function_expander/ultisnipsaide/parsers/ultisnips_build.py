#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The module responsible for making auto_docstring work with UltiSnips.

UltiSnips have a method called `snip.expand_anon` which, if given a string,
gets expanded as if it were a predefined UltiSnips snippet.

But in order for this to work, the string must have "tabstops" defined for
UltiSnips to know how use the string.

auto_docstring has its own string format and so this module converts from
auto_docstring's format to something UltiSnips can read.

'''

# IMPORT THIRD-PARTY LIBRARIES
import pyparsing
import six


class RecursiveParser(object):

    '''A class that converts auto_docstring strings to UltiSnips snippets.

    Attributes:
        conversion_text (str):
            The auto_docstring-specific marker that indicates
            where to put an UltiSnips tabstop.

    '''

    conversion_text = '!f'

    def __init__(self):
        '''Create the object and do nothing else.'''
        super(RecursiveParser, self).__init__()

    @classmethod
    def _is_convertible(cls, item):
        '''Check if the given `item` is an auto_docstring marker.

        Args:
            item (str): The text to check.

        Returns:
            bool: If the given item is a marker.

        '''
        return item.endswith(cls.conversion_text)

    @classmethod
    def _is_list_convertible(cls, items):
        '''Check if the given index-able object is an auto_docstring marker.

        This happens when there is a nested marker - aka a marker in a marker.

        Args:
            items (list[str]): The list that represents an auto_docstring marker.

        Returns:
            bool: If `items` is a marker.

        '''
        try:
            return cls._is_convertible(items[-1])
        except IndexError:
            return False

    @classmethod
    def _convert(cls, text, force=False):
        '''Remove the auto_docstring marker, "!f" from the given text, if needed.

        Args:
            text (str): The text to convert.
            force (bool, optional):
                If True, then the last two characters of `text` will be removed.
                If False, the characters will be removed only if `text`
                is convertible.
                Default is False.

        Returns:
            text: The output text, with no marker.

        '''
        ends_with_conversion = cls._is_convertible(text)
        if not force and not ends_with_conversion:
            return text

        if ends_with_conversion:
            text = text[:-2]  # Strip off the '!f'

        return text

    @staticmethod
    def _wrap(items):
        '''Add {}s around the given items, if needed.

        UltiSnips has a very specific logic about which tabstops need {}s
        around them. Rather than force this class to depend on UltiSnip's
        functions, we will replicate the logic, here.

        Basically, if items is a list with only one item and that item is a
        number, then it doesn't need to use {}s. Example: "$3". But if items
        is a list that contains multiple items or items that aren't digits,
        it needs {}s. Example: "{3:default_text}".

        Returns:
            str: The joined and wrapped `items`.

        '''
        # This try/except is a very unique syntax to UltiSnips. Basically, if a
        # tabstop in UltiSnips contains text, it looks like this "${3:foo}" where
        # "foo" is default text. If the tabstop is just a number though, you can
        # write it as either "${3}" or just "$3". This try/except will check
        # if we actually need {}s. The prefix "$" will be added, later.
        #
        try:
            is_single_list = _is_itertype(items) and len(items) == 1
            if is_single_list and items[0].isdigit():
                return items[0]
        except AttributeError:
            pass

        if isinstance(items, six.string_types) and items.isdigit():
            return items

        return '{{{}}}'.format(''.join(items))

    @staticmethod
    def _tag(text):
        '''str: Add "$" to the beginning of the given text.'''
        return '$' + text

    def expand(self, items):
        '''Recursively convert `items` into an UltiSnips-snippet string.

        Args:
            items (list[str] or str): The information to convert.

        Returns:
            str: The UltiSnips-snippet string.

        '''
        if not _is_itertype(items):
            return items

        is_convertible = self._is_list_convertible(items)

        for index, item in enumerate(items):
            expanded_item = self.expand(item)
            items[index] = expanded_item

        # Re-add the "{}"s that pyparsing removed
        items = self._convert(''.join(items), force=True)
        output = self._wrap(items)

        # Is this is going to be used as an UltiSnips snippet, add the $
        if is_convertible:
            output = self._tag(output)

        return output

    @classmethod
    def _parse(cls, text, function):
        '''Prep `text` into a list of strs and then pass it to `function`.

        The given text should contain one or more {}s in it,
        like "foo {bar} buzz", and this function will convert it
        to ['foo', ['bar'], 'buzz'] and then pass that to `function`.

        Args:
            text (str):
                The text to convert into a list (of lists) of strs.
            function (callable[list[str or list[str]]]):
                The function that takes the parsed `text` as input.

        Returns:
            str: The output of function.

        '''
        # 1. We wrap the entire text in {}s, to make it a nested expression
        text = cls._wrap(text)

        pyparsing.ParserElement.setDefaultWhitespaceChars('\n\t')
        _content = pyparsing.CharsNotIn(['{', '}'])
        _curlys = pyparsing.nestedExpr('{', '}', content=_content)

        # 2. Since we made the expression nested a little while ago, lets unpack it
        #    by getting the 0th index
        #
        parsed_text = _curlys.parseString(text).asList()[0]
        result = function(parsed_text)

        # 3. The {}s that we added with `_wrap` need to be removed.
        #    So we just remove the first and last characters, [1:-1]
        #    from the final result
        #
        return result[1:-1]

    def parse(self, text):
        '''Convert the given `text` into an UltiSnips-compatible string.

        Note:
            This method is recursive. Markers-within-markers will be parsed
            as separate UltiSnips tabstops.

        Args:
            text (str): The input to convert.

        Returns:
            str: A valid UltiSnips string.

        '''
        return self._parse(text, self.expand)


def _is_string_instance(obj):
    '''bool: If the object is a string instance.'''
    return isinstance(obj, six.string_types)


def _is_itertype(obj, allow_outliers=False, outlier_check=_is_string_instance):
    '''Check if the obj is iterable. Returns False if string by default.

    Args:
        obj (any): The object to check for iterable methods
        allow_outliers (:obj:`bool`, optional):
            If True, returns True if obj is string
        outlier_check (:obj:`function`, optional): A function to use to check
            for 'bad itertypes'. This function does nothing if allow_outliers
            is True. If nothing is provided, strings are checked and rejected.

    Returns:
        bool: If the input obj is a proper iterable type.

    '''
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        if not allow_outliers and outlier_check(obj):
            return False
    return True
