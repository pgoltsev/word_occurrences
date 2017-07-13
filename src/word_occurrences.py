#!/usr/bin/env python3

import argparse
import re
import sys
from operator import itemgetter
from typing import Mapping, Iterable, Counter, Callable, Tuple, Any

WordCountMapping = Mapping[str, int]

__author__ = 'pgoltsev'
__version__ = '1.0.0'


def print_statistic(iterable: Iterable,
                    formatter: Callable[[Any], str]) -> None:
    """
    Print mapping statistics to the standard output.

    :param iterable: Iterable object to print.
    :param formatter: Formatter to which an every item of iterable object is
    passed. It should return a formatted string.
    """
    for item in iterable:
        sys.stdout.write('%s\n' % formatter(item))


def format_with_colon(item: Tuple) -> str:
    """
    Concatenate key and value with colon.

    :param item: A tuple of two elements.
    :return: String with values of the tuple with a colon between them.
    """
    return f'{item[0]}: {item[1]}'


def sort_by_occurrences(mapping: WordCountMapping) -> Iterable[
    Tuple[str, int]
]:
    """
    Sort mapping by keys in alphabetical order and if they are equal by values
    in descending order.

    :param mapping: Mapping.
    :return: Iterable object with sorted sequence of tuples. Every tuple has
    two elements: a key and a value.
    """
    items = mapping.items()
    items_sorted_by_keys = sorted(items, key=itemgetter(0))
    items_sorted = sorted(items_sorted_by_keys,
                          key=itemgetter(1),
                          reverse=True)
    return items_sorted


def count_word_occurrences(
        text: str,
        split_func: Callable[[str], Iterable[str]],
        accumulator: Counter = None
) -> Counter:
    """
    Count word occurrences in a text.

    :param text: Input text
    :param split_func: Function for splitting the text into words.
    :param accumulator: Accumulate result here. May be used for reducing
    memory usage. If not defined it will be created.
    :return: Counter object which key is a word and a value is
    occurrences of this word in the given text.
    """
    if accumulator is None:
        accumulator = Counter()

    for word in split_func(text):
        if word:
            accumulator[word] += 1
    return accumulator


word_regex = re.compile(r'\b([\w\'-]+)\b')
"""
Regular expression of a word. It takes into account an apostrophe.
"""


def split_text_to_words(text: str) -> Iterable[str]:
    """
    Split text into words.

    :param text: Text to split.
    :return: Iterable object with words.
    """
    for word in word_regex.finditer(text):
        yield word[0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Script counts word occurrences inside of the 
given text file."""
    )
    parser.add_argument(
        'file',
        help='path to a text file',
        type=argparse.FileType('r')
    )
    args = parser.parse_args()

    word_occurrences = Counter()
    for line in args.file:
        count_word_occurrences(line,
                               split_func=split_text_to_words,
                               accumulator=word_occurrences)

    sorted_word_occurrences = sort_by_occurrences(word_occurrences)
    print_statistic(sorted_word_occurrences,
                    formatter=format_with_colon)
