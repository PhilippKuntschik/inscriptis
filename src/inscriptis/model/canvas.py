#!/usr/bin/env python
# encoding: utf-8

"""
Elements used for rendering (parts) of the canvas.

The :class:`Line` determines how a single line is rendered.
"""
from collections import namedtuple
from enum import Enum
from html import unescape

from inscriptis.html_properties import WhiteSpace
from inscriptis.model.css import HtmlElement

TextSnippet = namedtuple("TextSnippet", "text whitespace")


class Canvas:
    """
    The Canvas on which we write our HTML page.
    """

    __slots__ = ('blocks', 'current_block')

    def __init__(self):
        """
        Contains the completed blocks. Each block spawns at least a line
        """
        self.blocks = []
        self.current_block = []

    def write_block(self, tag: HtmlElement, text: str):
        self.flush_inline()
        self.current_block.append(TextSnippet(text, whitespace=WhiteSpace.pre))

    def write_inline(self, tag: HtmlElement, text: str):
        print("***", tag, text)
        self.current_block.append(TextSnippet(text, whitespace=tag.whitespace))

    @staticmethod
    def normalize(snippets: list[TextSnippet]):
        """Normalizes a list of TextSnippets to a single line

        Args:
            snippets: a list of TextSnippets

        Returns:
            the normalized string
        """
        result = []
        previous_isspace = False
        for snippet in snippets:
            # handling of pre formatted text
            if snippet.whitespace == WhiteSpace.pre:
                result.append(snippet.text)
                previous_isspace = None
                continue

            for ch in snippet.text:
                if not ch.isspace():
                    result.append(ch)
                    previous_isspace = False
                    continue

                if previous_isspace or not result:
                    continue
                else:
                    result.append(' ')
                    previous_isspace = True

        return ''.join(result)

    def flush_inline(self):
        if self.current_block:
            print(self.current_block)
            block = self.normalize(self.current_block)
            self.blocks.append(block)
            self.current_block = []

    def get_text(self):
        self.flush_inline()
        return unescape('\n'.join((block.rstrip() for block in self.blocks)))


class Line:
    """
    This class represents a line to render.

    Args:
        margin_before: number of empty lines before the given line.
        margin_after: number of empty lines before the given line.
        prefix: prefix add before the line's content.
        suffix: suffix to add after the line's content.
        list_bullet: a bullet to add before the line.
        padding: horizontal padding
        align: determines the alignment of the line (not used yet)
        width: total width of the line in characters (not used yet)
    """
    __slots__ = ('margin_before', 'margin_after', 'prefix', 'suffix',
                 'content', 'list_bullet', 'padding', 'align', 'width')

    def __init__(self):
        self.margin_before = 0
        self.margin_after = 0
        self.prefix = ""
        self.suffix = ""
        self.content = ""
        self.list_bullet = ""
        self.padding = 0

    def get_text(self):
        """
        Returns:
          str -- The text representation of the current line.
        """
        if '\0' not in self.content:
            # standard text without any `WhiteSpace.pre` formatted text.
            text = self.content.split()
        else:
            # content containing `WhiteSpace.pre` formatted text
            self.content = self.content.replace('\0\0', '')
            text = []
            # optional padding to add before every line
            base_padding = ' ' * self.padding

            for no, data in enumerate(self.content.split('\0')):
                # handle standard content
                if no % 2 == 0:
                    text.extend(data.split())
                # handle `WhiteSpace.pre` formatted content.
                else:
                    text.append(data.replace('\n', '\n' + base_padding))

        return ''.join(('\n' * self.margin_before,
                        ' ' * (self.padding - len(self.list_bullet)),
                        self.list_bullet,
                        self.prefix,
                        ' '.join(text),
                        self.suffix,
                        '\n' * self.margin_after))

    def __str__(self):
        return "<Line: '{0}'>".format(self.get_text())

    def __repr__(self):
        return str(self)
