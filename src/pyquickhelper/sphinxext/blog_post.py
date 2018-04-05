# -*- coding: utf-8 -*-
"""
@file
@brief Helpers to process blog post included in the documentation.
"""

import os
import sys
from docutils import io as docio
from docutils.core import publish_programmatically


if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO
else:
    from io import StringIO


class BlogPostParseError(Exception):

    """
    exceptions when a error comes after a blogpost was parsed
    """
    pass


class BlogPost:

    """
    defines a blog post,
    """

    def __init__(self, filename, encoding='utf-8-sig', raise_exception=False, extensions=None):
        """
        create an instance of a blog post from a file or a string

        @param      filename            filename or string
        @param      encoding            encoding
        @param      raise_exception     to raise an exception when the blog cannot be parsed
        @param      extensions          list of extension to use to parse the content of the blog,
                                        if None, it will consider a default list
                                        (see @see cl BlogPost and @see fn get_default_extensions)

        The constructor creates the following members:

        * title
        * date
        * keywords
        * categories
        * _filename
        * _raw
        * rst_obj: the object generated by docutils (@see cl BlogPostDirective)
        * pub: Publisher

        .. versionchanged:: 1.3
            Parameter *raise_exception* was added to catch the standard error.
            The constructor aims at getting the text of a blog post, not
            interpreting it. The code used to throw warnings or errors due to
            unreferenced nodes.

        .. versionchanged:: 1.5
            Parameter *extensions* was added.
        """
        if os.path.exists(filename):
            with open(filename, "r", encoding=encoding) as f:
                try:
                    content = f.read()
                except UnicodeDecodeError as e:
                    raise Exception(
                        'unable to read filename (encoding issue):\n  File "{0}", line 1'.format(filename)) from e
            self._filename = filename
        else:
            content = filename
            self._filename = None

        self._raw = content

        overrides = {}
        overrides["out_blogpostlist"] = []
        overrides["blog_background"] = True
        overrides["blog_background_page"] = False
        overrides["sharepost"] = None

        overrides.update({  # 'warning_stream': StringIO(),
            'out_blogpostlist': [],
            'out_runpythonlist': [],
            'master_doc': 'stringblog'
        })

        if "extensions" not in overrides:
            if extensions is None:
                # To avoid circular references.
                from . import get_default_extensions
                extensions = get_default_extensions()
            overrides["extensions"] = extensions

        from ..helpgen.sphinxm_mock_app import MockSphinxApp
        app = MockSphinxApp.create(confoverrides=overrides)
        env = app[0].env
        config = env.config

        if 'blog_background' not in config:
            raise AttributeError("Unable to find 'blog_background' in config:\n{0}".format(
                "\n".join(sorted(config.values))))
        if 'blog_background_page' not in config:
            raise AttributeError("Unable to find 'blog_background_page' in config:\n{0}".format(
                "\n".join(sorted(config.values))))

        env.temp_data["docname"] = "stringblog"
        overrides["env"] = env

        config.add('doctitle_xform', True, False, bool)
        config.add('initial_header_level', 2, False, int)
        config.add('input_encoding', encoding, False, str)

        errst = sys.stderr
        keeperr = StringIO()
        sys.stderr = keeperr

        output, pub = publish_programmatically(source_class=docio.StringInput, source=content,
                                               source_path=None, destination_class=docio.StringOutput, destination=None,
                                               destination_path=None, reader=None, reader_name='standalone', parser=None,
                                               parser_name='restructuredtext', writer=None, writer_name='null', settings=None,
                                               settings_spec=None, settings_overrides=overrides, config_section=None,
                                               enable_exit_status=None)

        sys.stderr = errst

        all_err = keeperr.getvalue()
        if len(all_err) > 0:
            if raise_exception:
                raise BlogPostParseError("unable to parse a blogpost:\n[sphinxerror]\n{0}\nFILE\n{1}\nCONTENT\n{2}".format(
                    all_err, self._filename, content))
            else:
                # we assume we just need the content, raising a warnings
                # might make some process fail later
                # warnings.warn("Raw rst was caught but unable to fully parse a blogpost:\n[sphinxerror]\n{0}\nFILE\n{1}\nCONTENT\n{2}".format(
                #     all_err, self._filename, content))
                pass

        # document = pub.writer.document
        objects = pub.settings.out_blogpostlist

        if len(objects) != 1:
            raise BlogPostParseError(
                'no blog post (#={1}) in\n  File "{0}", line 1'.format(filename, len(objects)))

        post = objects[0]
        for k in post.options:
            setattr(self, k, post.options[k])
        self.rst_obj = post
        self.pub = pub
        self._content = post.content

    def __cmp__(self, other):
        """
        This method avoids to get the following error
        ``TypeError: unorderable types: BlogPost() < BlogPost()``.

        @param      other       other @see cl BlogPost
        @return                 -1, 0, or 1
        """
        if self.Date < other.Date:
            return -1
        elif self.Date > other.Date:
            return 1
        else:
            if self.Tag < other.Tag:
                return -1
            elif self.Tag > other.Tag:
                return 1
            else:
                raise Exception(
                    "same tag for two BlogPost: {0}".format(self.Tag))

    def __lt__(self, other):
        """
        Tells if this blog should be placed before *other*.
        """
        if self.Date < other.Date:
            return True
        elif self.Date > other.Date:
            return False
        else:
            if self.Tag < other.Tag:
                return True
            else:
                return False

    @property
    def Fields(self):
        """
        Returns the fields as a dictionary.
        """
        res = dict(title=self.title,
                   date=self.date,
                   keywords=self.Keywords,
                   categories=self.Categories)
        if self.BlogBackground is not None:
            res["blog_ground"] = self.BlogBackground
        if self.Author is not None:
            res["author"] = self.Author
        return res

    @property
    def Tag(self):
        """
        Produces a tag for the blog post.
        """
        return BlogPost.build_tag(self.Date, self.Title)

    @staticmethod
    def build_tag(date, title):
        """
        Builds the tag for a post.

        @param      date        date
        @param      title       title
        @return                 tag or label
        """
        return "post-" + date + "-" + \
               "".join([c for c in title.lower() if "a" <= c <= "z"])

    @property
    def FileName(self):
        """
        Returns the filename.
        """
        return self._filename

    @property
    def Title(self):
        """
        Returns the title.
        """
        return self.title

    @property
    def BlogBackground(self):
        """
        Return the blog background or None if not defined.
        """
        return self.blog_ground if hasattr(self, "blog_ground") else None

    @property
    def Author(self):
        """
        Return the author or None if not defined.
        """
        return self.author if hasattr(self, "author") else None

    @property
    def Date(self):
        """
        Returns the date.
        """
        return self.date

    @property
    def Year(self):
        """
        Return the year, we assume self.date is a string ``YYYY-MM-DD``.
        """
        return self.date[:4]

    @property
    def Keywords(self):
        """
        Returns the keywords.
        """
        return [_.strip() for _ in self.keywords.split(",")]

    @property
    def Categories(self):
        """
        Returns the categories.
        """
        return [_.strip() for _ in self.categories.split(",")]

    @property
    def Content(self):
        """
        Returns the content of the blogpost.
        """
        return self._content

    def post_as_rst(self, language, directive="blogpostagg", cut=True):
        """
        Reproduces the text of the blog post,
        updates the image links.

        @param      language    language
        @param      directive   to specify a different behavior based on
        @param      cut         truncate the post after the first paragraph
        @return                 blog post as RST

        .. versionadded:: 1.7
            Parameter *cut* was added.
        """
        rows = []
        rows.append(".. %s::" % directive)
        for f, v in self.Fields.items():
            if isinstance(v, str):
                rows.append("    :%s: %s" % (f, v))
            else:
                rows.append("    :%s: %s" % (f, ",".join(v)))
        if self._filename is not None:
            spl = self._filename.replace("\\", "/").split("/")
            name = "/".join(spl[-2:])
            rows.append("    :rawfile: %s" % name)
        rows.append("")

        def can_cut(i, r, rows_stack):
            rs = r.lstrip()
            indent = len(r) - len(rs)
            if len(rows_stack) == 0:
                if len(rs) > 0:
                    rows_stack.append(r)
            else:
                indent2 = len(rows_stack[0]) - len(rows_stack[0].lstrip())
                last = rows_stack[-1]
                if len(last) > 0:
                    last = last[-1]
                if indent == indent2 and len(rs) == 0 and \
                        last in {'.', ';', ',', ':', '!', '?'}:
                    return True
                rows_stack.append(r)
            return False

        rows_stack = []
        if directive == "blogpostagg":
            for i, r in enumerate(self.Content):
                rows.append("    " + self._update_link(r))
                if cut and can_cut(i, r, rows_stack):
                    rows.append("")
                    rows.append("    ...")
                    break
        else:
            for i, r in enumerate(self.Content):
                rows.append("    " + r)
                if cut and can_cut(i, r, rows_stack):
                    rows.append("")
                    rows.append("    ...")
                    break

        rows.append("")
        rows.append("")

        return "\n".join(rows)

    image_tag = ".. image:: "

    def _update_link(self, row):
        """
        changes a link to an image if the page contains one into
        *year/img.png*

        @param      row     row
        @return             new row
        """
        r = row.strip("\r\t ")
        if r.startswith(BlogPost.image_tag):
            i = len(BlogPost.image_tag)
            r2 = row[i:]
            if "/" in r2:
                return row
            row = "{0}{1}/{2}".format(row[:i], self.Year, r2)
            return row
        else:
            return row
