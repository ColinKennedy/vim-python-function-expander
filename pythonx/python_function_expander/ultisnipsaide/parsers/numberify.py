#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The module responsible for making a string into an auto_docstring string.

Basically, a string that looks like this, "foo {bar} {!f} thing {here!f}."
would need to be converted to "foo {bar} {1!f} thing {2:here!f}."

{!f} is used as a marker to indicate areas that auto_docstring
should be interested in. This information gets used by other text tools,
like UltiSnips, to generate the final docstring.

'''

# IMPORT STANDARD LIBRARIES
import uuid
import re

# IMPORT LOCAL LIBRARIES
from . import ultisnips_build


class RecursiveNumberifyParser(ultisnips_build.RecursiveParser):

    '''The class that converts a Python string to an auto_docstring string.'''

    _conversion_compiled = re.compile(r'(?P<number>\d*)(?P<text>.*)(?P<conversion>!\w)$')

    def __init__(self):
        '''Create this instance and keep a reference to all used numbers.'''
        super(RecursiveNumberifyParser, self).__init__()
        self._used_names = dict()
        self._used_numbers = set()

    @classmethod
    def _get_conversion_info(cls, text):
        '''Get the group information of the given `text`, if there is any.

        Args:
            text (str): The text to parse, using regex.

        Returns:
            dict[str, str]: The found information from `text`.
                "number" (str): The number assigned to `text`, if any.
                "text" (str): The body of the string, if any.
                "conversion" (str): The conversion marker of text, if any.
                                    If there is one, it is usually "!f".

        '''
        info = cls._conversion_compiled.match(text)
        try:
            return info.groupdict()
        except AttributeError:
            return dict()

    @staticmethod
    def _wrap(items):
        '''Add {}s around the given items.

        Args:
            items (list[str]): The items to join and wrap.

        Returns:
            str: The output text.

        '''
        text = ''.join(items)
        return '{{{}}}'.format(text)

    def _convert(self, text, force=False):
        '''Add a number indicator to the given `text`, if needed.

        Args:
            text (str): The text to convert.
            force (bool, optional): Unused in this method. Default is False.

        Returns:
            str: The converted text.

        '''
        info = self._get_conversion_info(text)
        if not info:
            # If info is empty, we can safely return the original text
            return text

        conversion = info.get('conversion', '')

        latest_number = self._register_and_get_next_number(
            text=info.get('text', ''),
            stored_number=info.get('number', 0),
        )

        return '{latest_number}{text}{conversion}'.format(
            latest_number=latest_number,
            text=info.get('text', ''),
            conversion=conversion)

    @staticmethod
    def _tag(text):
        '''str: Do not tag the given text.'''
        return text

    def _register_and_get_next_number(self, text='', stored_number=0):
        '''Find the next number that this instance should use for formatting.

        If `text` is not empty, check if the name was already used.
        If the used name is in our cached used names and the number along with
        that used name is the same the number that we have stored for this text
        then do not modify `text`'s number and just return it.

        Otherwise though, we need a new number.

        Args:
            text (`str`, optional):
                The text to use to query the next number.
            stored_number (`int`, optional):
                The suggested number to use for text, if any.
                Default: 0.

        Returns:
            int: The next number to use.

        '''
        self._used_names.setdefault(text, dict())

        try:
            latest_number = max(self._used_numbers) + 1
        except ValueError:
            latest_number = 1

        if not text:
            self._used_names[text][stored_number] = latest_number
            self._used_numbers.add(latest_number)
            return latest_number

        try:
            return self._used_names[text][stored_number]
        except KeyError:
            self._used_names[text][stored_number] = latest_number
            self._used_numbers.add(latest_number)
            return latest_number

    def parse(self, text):
        '''Clear the stored names and numbers and then parse the given `text`.

        Args:
            text (str):
                The text to add numbers and markers to and to convert to
                an auto_docstring-compatible string.

        Returns:
            str: The parsed text.

        '''
        self.clear()
        return super(RecursiveNumberifyParser, self).parse(text=text)

    @classmethod
    def add_conversion(cls, text):
        '''Do the main work of the class by adding numbers and markers to `text`.

        Args:
            text (str): The text to "numberify".

        Returns:
            str: The converted text.

        '''
        # expected - text that doesn't already have !f on it
        def _add_conversion(items):
            if not ultisnips_build._is_itertype(items):
                return items

            try:
                is_convertible = cls._is_list_convertible(items)
            except AttributeError:
                # If this happens, it's because items is a nested list
                # Since lists are recursively processed by _add_conversion, it's
                # OK to just set this value to False. Other recursion levels
                # will sort it out
                #
                is_convertible = False

            for index, item in enumerate(items):
                items[index] = _add_conversion(item)

            if not is_convertible:
                items.insert(0, ':')
                items.insert(0, str(_get_unique_number()))
                items.append(cls.conversion_text)

            # Re-add the "{}"s that pyparsing removed
            output = cls._wrap(items)
            return output

        output = cls._parse(text, function=_add_conversion)

        # Remove the trailing !f that gets added
        output = output[:-2]
        return output

    def clear(self):
        '''Remove all known names and numbers from this instance.'''
        self._used_names = self._used_names.__class__()
        self._used_numbers = self._used_numbers.__class__()


def _get_unique_number():
    '''int: Get a unique (non-repeated) number value.'''
    return uuid.uuid4().int
