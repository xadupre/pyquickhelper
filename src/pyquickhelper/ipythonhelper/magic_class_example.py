# -*- coding: utf-8 -*-
"""
@file
@brief Example of a class which defines magic commands.

.. versionadded:: 1.3
    Magic commands coming from pyensae
"""
from __future__ import print_function

from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from ..helpgen import docstring2html
from IPython.core.magic import magics_class, line_magic


@magics_class
class MagicClassExample(MagicClassWithHelpers):

    """
    .. faqref::
        :title: Define a magic command

        This class is an example of how a magic commands can be defined
        with parameters as if it was a regular command in a terminal.
        The class @see cl MagicClassExample defines magic
        command ``htmlhelp`` and the associated parser.
        Function @see fn load_ipython_extension
        register the magic command through ``%load_ext pyquickhelper``.
        The magic command can be unit tested with::

            mg = MagicClassExample()
            mg.add_context(context={"MagicClassExample": MagicClassExample})
            cmd = "MagicClassExample -f text"
            res = mg.htmlhelp(cmd)
            assert "NB(example of a magic command)"

    .. versionadded:: 1.3
        Magic commands coming from pyensae
    """

    @staticmethod
    def htmlhelp_parser():
        """
        defines the way to parse the magic command ``%htmlhelp``

        .. versionadded:: 1.3
        """
        parser = MagicCommandParser(prog="htmlhelp",
                                    description='display help for an object in HTML format')
        parser.add_argument(
            'obj',
            type=str,
            help='a python object')
        parser.add_argument(
            '-f',
            '--format',
            type=str,
            default="html",
            help='format',
            choices=['text', 'html', 'rst', 'rawhtml'])
        parser.add_argument(
            '-np',
            '--no-print',
            action='store_true',
            help='by default, the magic command outputs everything on the standard output, '
                 'if specified, it returns a string')
        return parser

    @line_magic
    def htmlhelp(self, line):
        """
        Define ``%htmlhelp``, it displays the help for an object in HTML.

        .. nbref::
            :title: %htmlhelp

            Magic command ``htmlhelp`` convert docstring (RST)
            into HTML format for a better display in a notebook.
            It is equivalent to the code:

            ::

                from pyquickhelper.helpgen import docstring2html
                obj = <function or object>
                docstring2html(obj, format="html")

            See function @see fn docstring2html.
        """
        parser = self.get_parser(MagicClassExample.htmlhelp_parser, "htmlhelp")
        args = self.get_args(line, parser)

        if args is not None:
            obj = args.obj
            format = args.format
            nop = args.no_print
            if nop or format == "html":
                return docstring2html(obj, format=format)
            else:
                print(docstring2html(obj, format=format))


def register_file_magics(ip=None):
    """
    register magics function, can be called from a notebook

    @param      ip      from ``get_ipython()``
    """
    if ip is None:
        from IPython import get_ipython
        ip = get_ipython()
    ip.register_magics(MagicClassExample)
