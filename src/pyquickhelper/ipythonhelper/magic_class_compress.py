#-*- coding: utf-8 -*-
"""
@file
@brief Magic command to handle files

.. versionadded:: 1.3
    Magic commands coming from pyensae
"""
import os
from IPython.core.magic import magics_class, line_magic

from .magic_class import MagicClassWithHelpers
from .magic_parser import MagicCommandParser
from ..filehelper import zip_files, gzip_files, zip7_files


@magics_class
class MagicCompress(MagicClassWithHelpers):

    """
    Defines magic commands to compress files.

    .. versionadded:: 1.3
        Magic commands coming from pyensae
    """

    @staticmethod
    def compress_parser():
        """
        defines the way to parse the magic command ``%compress``
        """
        parser = MagicCommandParser(prog="compress",
                                    description='display the content of a repository (GIT or SVN)')
        parser.add_argument(
            'dest',
            type=str,
            help='destination, the extension defines the compression format, zip, gzip 7z')
        parser.add_argument(
            'files',
            type=str,
            nargs="?",
            help='files to compress or a python list')
        return parser

    @line_magic
    def compress(self, line):
        """
        define ``%compress``

        @NB(compress)

        It compress a list of files,
        it returns the number of compressed files::

            from pyquickhelper import zip_files, gzip_files, zip7_files
            if format == "zip":
                zip_files(dest, files)
            elif format == "gzip":
                gzip_files(dest, files)
            elif format == "7z":
                zip7_files(dest, files)
            else:
                raise ValueError("unexpected format: " + format)

        @endNB
        """
        parser = self.get_parser(MagicCompress.compress_parser, "compress")
        args = self.get_args(line, parser)

        if args is not None:
            dest = args.dest
            files = args.files
            format = os.path.splitext(dest)[-1].strip(".").lower()

            if format == "zip":
                return zip_files(dest, files)
            elif format == "gzip":
                return gzip_files(dest, files)
            elif format == "7z":
                return zip7_files(dest, files)
            else:
                raise ValueError(
                    "unexpected format: {0} from file {1}".format(format, dest))


def register_file_magics(ip=None):
    """
    register magics function, can be called from a notebook

    @param      ip      from ``get_ipython()``
    """
    if ip is None:
        from IPython import get_ipython
        ip = get_ipython()
    ip.register_magics(MagicCompress)