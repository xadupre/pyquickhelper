# -*- coding: utf-8 -*-
"""
@file
@brief Helpers to process blog post inclueded in the documentation.
"""

import os
from docutils import io as docio
from docutils.core import publish_programmatically
from docutils.parsers.rst import directives

from .sphinx_blog_extension import BlogPostInfoDirective


class BlogPostPareError(Exception):

    """
    exceptions when a error comes after a blogpost was parsed
    """
    pass


class BlogPost:

    """
    defines a blog post,
    """

    def __init__(self, filename, encoding="utf8"):
        """
        create an instance of a blog post from a file or a string

        @param      filename        filename or string
        @param      encoding        encoding

        The constructor creates the following members:

        * title
        * date
        * keywords
        * categories
        * _filename
        * _raw
        * rst_obj: the object generated by docutils (@see cl BlogPostInfoDirective)
        * pub: Publisher

        """
        if os.path.exists(filename):
            with open(filename, "r", encoding=encoding) as f:
                content = f.read()
            self._filename = filename
        else:
            content = filename
            self._filename = None

        self._raw = content

        overrides = {}
        overrides['input_encoding'] = encoding
        overrides["out_blogpostlist"] = []

        directives.register_directive("blogpost", BlogPostInfoDirective)

        output, pub = publish_programmatically(
            source_class=docio.StringInput,
            source=content,
            source_path=None,
            destination_class=docio.StringOutput,
            destination=None,
            destination_path=None,
            reader=None,
            reader_name='standalone',
            parser=None,
            parser_name='restructuredtext',
            writer=None,
            writer_name='null',
            settings=None,
            settings_spec=None,
            settings_overrides=overrides,
            config_section=None,
            enable_exit_status=None)

        #document = pub.writer.document
        objects = pub.settings.out_blogpostlist

        if len(objects) != 1:
            raise BlogPostPareError("no blog post in\n" + filename)

        post = objects[0]
        for k in post.options:
            setattr(self, k, post.options[k])
        self.rst_obj = post
        self.pub = pub

    @property
    def FileName(self):
        """
        return the filename
        """
        return self._filename

    @property
    def Title(self):
        """
        return the title
        """
        return self.title

    @property
    def Date(self):
        """
        return the date
        """
        return self.date

    @property
    def Keywords(self):
        """
        return the keywords
        """
        return self.keywords

    @property
    def Categories(self):
        """
        return the categories
        """
        return self.categories
