# -*- coding: utf-8 -*-
"""
@file
@brief Implements command line ``python -m pyquickhelper <command> <args>``.

.. versionadded:: 1.8
"""
import sys


def main(args, fLOG=print):
    """
    Implements ``python -m pyquickhelper <command> <args>``.

    @param      args        command line arguments
    @param      fLOG        logging function
    """
    try:
        from .cli.pyq_sync_cli import pyq_sync
        from .cli.encryption_file_cli import encrypt_file, decrypt_file
        from .cli.encryption_cli import encrypt, decrypt
        from .pandashelper import df2rst
        from .pycode import clean_files, run_test_function
        from .cli import cli_main_helper
        from .helpgen.process_notebooks import process_notebooks
        from .filehelper import create_visual_diff_through_html_files
        from .filehelper import explore_folder
        from .cli.simplified_fct import sphinx_rst
        from .ipythonhelper import run_notebook
        from .imghelper.img_helper import zoom_img
        from .imghelper.img_export import images2pdf
        from .script_exec import repeat_script
    except ImportError:  # pragma: no cover
        from pyquickhelper.cli.pyq_sync_cli import pyq_sync
        from pyquickhelper.cli.encryption_file_cli import encrypt_file, decrypt_file
        from pyquickhelper.cli.encryption_cli import encrypt, decrypt
        from pyquickhelper.pandashelper import df2rst
        from pyquickhelper.pycode import clean_files, run_test_function
        from pyquickhelper.cli import cli_main_helper
        from pyquickhelper.helpgen.process_notebooks import process_notebooks
        from pyquickhelper.filehelper import create_visual_diff_through_html_files
        from pyquickhelper.filehelper import explore_folder
        from pyquickhelper.cli.simplified_fct import sphinx_rst
        from pyquickhelper.ipythonhelper import run_notebook
        from pyquickhelper.imghelper.img_helper import zoom_img
        from pyquickhelper.imghelper.img_export import images2pdf
        from pyquickhelper.cli.script_exec import repeat_script

    fcts = dict(synchronize_folder=pyq_sync, encrypt_file=encrypt_file,
                decrypt_file=decrypt_file, encrypt=encrypt,
                decrypt=decrypt, df2rst=df2rst, clean_files=clean_files,
                process_notebooks=process_notebooks,
                visual_diff=create_visual_diff_through_html_files,
                ls=explore_folder, run_test_function=run_test_function,
                sphinx_rst=sphinx_rst, run_notebook=run_notebook,
                zoom_img=zoom_img, images2pdf=images2pdf,
                repeat_script=repeat_script)
    return cli_main_helper(fcts, args=args, fLOG=fLOG)


if __name__ == "__main__":
    main(sys.argv[1:])
