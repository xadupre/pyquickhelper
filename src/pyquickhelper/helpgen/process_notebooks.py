# -*- coding: utf-8 -*-
"""
@file
@brief Contains the main function to generate the documentation
for a module designed the same way as this one, @see fn generate_help_sphinx.

"""

import os
import sys
import shutil

from ..loghelper.flog import run_cmd, fLOG
from .utils_sphinx_doc_helpers import HelpGenException, find_latex_path, find_pandoc_path
from ..filehelper.synchelper import has_been_updated
from .post_process import post_process_latex_output, post_process_latex_output_any, post_process_rst_output, post_process_html_output


template_examples = """

List of programs
++++++++++++++++

.. toctree::
   :maxdepth: 2

.. autosummary:: __init__.py
   :toctree: %s/
   :template: modules.rst

Another list
++++++++++++

"""


def process_notebooks(notebooks,
                      outfold,
                      build,
                      latex_path=None,
                      pandoc_path=None,
                      formats=["ipynb", "html", "python", "rst", "pdf"]
                      ):
    """
    Converts notebooks into html, rst, latex, pdf, python, docx using
    `nbconvert <http://ipython.org/ipython-doc/rel-1.0.0/interactive/nbconvert.html>`_.

    @param      notebooks   list of notebooks
    @param      outfold     folder which will contains the outputs
    @param      build       temporary folder which contains all produced files
    @param      pandoc_path path to pandoc
    @param      formats     list of formats to convert into (pdf format means latex then compilation)
    @param      latex_path  path to the latex compiler
    @return                 created files

    This function relies on `pandoc <http://johnmacfarlane.net/pandoc/index.html>`_.
    It also needs modules `pywin32 <http://sourceforge.net/projects/pywin32/>`_,
    `pygments <http://pygments.org/>`_.

    `pywin32 <http://sourceforge.net/projects/pywin32/>`_ might have some issues
    to find its DLL, look @see fn import_pywin32.

    The latex compilation uses `MiKTeX <http://miktex.org/>`_.
    The conversion into Word document directly uses pandoc.
    It still has an issue with table.

    Some latex templates (for nbconvert) uses ``[commandchars=\\\\\\{\\}]{\\|}`` which allows commands ``\\\\`` and it does not compile.
    The one used here is ``report``.
    Some others bugs can be found at: `schlichtanders/latex_test.html <https://gist.github.com/schlichtanders/e108ed0be80108178af2>`_.
    For example, you must not let spaces between symbol ``$`` and the
    formulas it indicates.

    If *pandoc_path* is None, uses @see fn find_pandoc_path to guess it.
    If *latex_path* is None, uses @see fn find_latex_path to guess it.

    @example(convert a notebook into multiple formats)
    @code
    process_notebooks("td1a_correction_session7.ipynb",
                      "dest_folder",
                      "dest_folder",
                      formats=["ipynb", "html", "python", "rst", "pdf", "docx"])
    @endcode
    @endexample

    .. versionchanged:: 0.9
        For HTML conversion, read the following blog about mathjax: `nbconvert: Math is not displayed in the html output <https://github.com/ipython/ipython/issues/6440>`_.
        Add defaults values for *pandoc_path*, *latex_path*.

    """
    if pandoc_path is None:
        pandoc_path = find_pandoc_path()

    if latex_path is None:
        latex_path = find_latex_path()

    if isinstance(notebooks, str):
        notebooks = [notebooks]

    if "PANDOCPY" in os.environ and sys.platform.startswith("win"):
        exe = os.environ["PANDOCPY"]
        exe = exe.rstrip("\\/")
        if exe.endswith("\\Scripts"):
            exe = exe[:len(exe) - len("Scripts") - 1]
        if not os.path.exists(exe):
            raise FileNotFoundError(exe)
        fLOG("** using PANDOCPY", exe)
    else:
        if sys.platform.startswith("win"):
            from .utils_pywin32 import import_pywin32
            import_pywin32()
        exe = os.path.split(sys.executable)[0]

    extensions = {"ipynb": ".ipynb",
                  "latex": ".tex",
                  "pdf": ".pdf",
                  "html": ".html",
                  "rst": ".rst",
                  "python": ".py",
                  "docx": ".docx",
                  "word": ".docx",
                  }

    if sys.platform.startswith("win"):
        user = os.environ["USERPROFILE"]
        path = pandoc_path.replace("%USERPROFILE%", user)
        p = os.environ["PATH"]
        if path not in p:
            p += ";%WINPYDIR%\DLLs;" + path
            os.environ["WINPYDIR"] = exe
            os.environ["PATH"] = p

        ipy = os.path.join(exe, "Scripts", "ipython3.exe")
        if not os.path.exists(ipy):
            # Anaconda is different
            ipy = os.path.join(exe, "Scripts", "ipython.exe")
            if not os.path.exists(ipy):
                raise FileNotFoundError(ipy)
    else:
        ipy = os.path.join(exe, "ipython")

    cmd = '{0} nbconvert --to {1} "{2}"{5} --output="{3}/{4}"'
    files = []

    for notebook in notebooks:
        nbout = os.path.split(notebook)[-1]
        if " " in nbout:
            raise HelpGenException(
                "spaces are not allowed in notebooks file names: {0}".format(notebook))
        nbout = os.path.splitext(nbout)[0]
        for format in formats:

            options = ""
            if format == "pdf":
                title = os.path.splitext(
                    os.path.split(notebook)[-1])[0].replace("_", " ")
                format = "latex"
                options = ' --post PDF --SphinxTransformer.author="" --SphinxTransformer.overridetitle="{0}"'.format(
                    title)
                compilation = True
                pandoco = None
            elif format in ["word", "docx"]:
                format = "html"
                pandoco = "docx"
                compilation = False
            else:
                compilation = False
                pandoco = None

            # output
            outputfile = os.path.join(build, nbout + extensions[format])
            fLOG("--- produce ", outputfile)

            # we chech it was not done before
            if os.path.exists(outputfile):
                dto = os.stat(outputfile).st_mtime
                dtnb = os.stat(notebook).st_mtime
                if dtnb < dto:
                    fLOG("-- skipping notebook", format,
                         notebook, "(", outputfile, ")")
                    files.append(outputfile)
                    if pandoco is None:
                        continue
                    else:
                        out2 = os.path.splitext(outputfile)[0] + "." + pandoco
                        if os.path.exists(out2):
                            continue

            templ = "full" if format != "latex" else "article"
            fLOG("### convert into ", format, " NB: ", notebook,
                 " ### ", os.path.exists(outputfile), ":", outputfile)

            if format == "html":
                fmttpl = " --template {0}".format(templ)
            else:
                fmttpl = ""

            c = cmd.format(ipy, format, notebook, build, nbout, fmttpl)

            c += options
            fLOG(c)

            #
            if format not in ["ipynb"]:
                # for latex file
                if format == "latex":
                    cwd = os.getcwd()
                    os.chdir(build)

                if not sys.platform.startswith("win"):
                    c = c.replace('"', '')
                # , shell = sys.platform.startswith("win"))
                out, err = run_cmd(
                    c, wait=True, do_not_log=True, log_error=False)

                if format == "latex":
                    os.chdir(cwd)

                if "raise ImportError" in err:
                    raise ImportError(err)
                if len(err) > 0:
                    if format == "latex":
                        # there might be some errors because the latex script needs to be post-processed
                        # sometimes (wrong characters such as " or formulas not
                        # captured as formulas)
                        pass
                    else:
                        err = err.lower()
                        if "error" in err or "critical" in err or "bad config" in err:
                            raise HelpGenException(err)

                # we should compile a second time
                # compilation = True  # already done above

            format = extensions[format].strip(".")

            # we add the file to the list of generated files
            files.append(outputfile)

            if "--post PDF" in c:
                files.append(os.path.join(build, nbout + ".pdf"))

            fLOG("******", format, compilation, outputfile)

            if compilation:
                # compilation latex
                if os.path.exists(latex_path):
                    if sys.platform.startswith("win"):
                        lat = os.path.join(latex_path, "pdflatex.exe")
                    else:
                        lat = "pdflatex"

                    tex = files[-1].replace(".pdf", ".tex")
                    post_process_latex_output_any(tex)
                    # -interaction=batchmode
                    c = '"{0}" "{1}" -output-directory="{2}"'.format(
                        lat, tex, os.path.split(tex)[0])
                    fLOG("   ** LATEX compilation (b)", c)
                    if not sys.platform.startswith("win"):
                        c = c.replace('"', '')
                    out, err = run_cmd(
                        c, wait=True, do_not_log=False, log_error=False, shell=sys.platform.startswith("win"))
                    if len(err) > 0:
                        raise HelpGenException(
                            "CMD:\n{0}\nERR:\n{1}".format(c, err))
                    f = os.path.join(build, nbout + ".pdf")
                    if not os.path.exists(f):
                        raise HelpGenException(
                            "missing file: {0}\nERR:\n{1}".format(f, err))
                    files.append(f)
                else:
                    fLOG("unable to find latex in", latex_path)

            elif pandoco is not None:
                # compilation pandoc
                fLOG("   ** pandoc compilation (b)", pandoco)
                outfilep = os.path.splitext(outputfile)[0] + "." + pandoco

                # for some files, the following error might appear:
                # Stack space overflow: current size 33692 bytes.
                # Use `+RTS -Ksize -RTS' to increase it.
                # it usually means there is something wrong (circular
                # reference, ...)
                if sys.platform.startswith("win"):
                    c = r'"{0}\pandoc.exe" -f html -t {1} "{2}" -o "{3}"'.format(
                        pandoc_path, pandoco, outputfile, outfilep)
                else:
                    c = r'pandoc -f html -t {1} "{2}" -o "{3}"'.format(
                        pandoc_path, pandoco, outputfile, outfilep)

                if not sys.platform.startswith("win"):
                    c = c.replace('"', '')
                out, err = run_cmd(
                    c, wait=True, do_not_log=False, log_error=False, shell=sys.platform.startswith("win"))
                if len(err) > 0:
                    raise HelpGenException(
                        "issue with cmd: %s\nERR:\n%s" % (c, err))

            if format == "html":
                # we add a link to the notebook
                if not os.path.exists(outputfile):
                    raise FileNotFoundError(outputfile + "\nCONTENT in " + os.path.dirname(outputfile) + ":\n" + "\n".join(
                        os.listdir(os.path.dirname(outputfile))) + "\nERR:\n" + err + "\nOUT:\n" + out + "\nCMD:\n" + c)
                files += add_link_to_notebook(outputfile, notebook,
                                              "pdf" in formats, False, "python" in formats)

            elif format == "ipynb":
                # we just copy the notebook
                files += add_link_to_notebook(outputfile, notebook,
                                              "ipynb" in formats, False, "python" in formats)

            elif format == "rst":
                # we add a link to the notebook
                files += add_link_to_notebook(
                    outputfile, notebook, "pdf" in formats, "html" in formats, "python" in formats)

            elif format in ("tex", "latex", "pdf"):
                files += add_link_to_notebook(outputfile,
                                              notebook, False, False, False)

            elif format == "py":
                pass

            elif format in ["docx", "word"]:
                pass

            else:
                raise HelpGenException("unexpected format " + format)

    copy = []
    for f in files:
        dest = os.path.join(outfold, os.path.split(f)[-1])
        if not f.endswith(".tex"):

            if sys.version_info >= (3, 4):
                try:
                    shutil.copy(f, outfold)
                    fLOG("copy ", f, " to ", outfold, "[", dest, "]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
            else:
                try:
                    shutil.copy(f, outfold)
                    fLOG("copy ", f, " to ", outfold, "[", dest, "]")
                except shutil.Error as e:
                    if "are the same file" in str(e):
                        fLOG("w,file ", dest, "already exists")
                    else:
                        raise e

            if not os.path.exists(dest):
                raise FileNotFoundError(dest)
        copy.append(dest)

    # image
    for image in os.listdir(build):
        if image.endswith(".png") or image.endswith(
                ".html") or image.endswith(".pdf"):
            image = os.path.join(build, image)
            dest = os.path.join(outfold, os.path.split(image)[-1])

            if sys.version_info >= (3, 4):
                try:
                    shutil.copy(image, outfold)
                    fLOG("copy ", image, " to ", outfold, "[", dest, "]")
                except shutil.SameFileError:
                    fLOG("w,file ", dest, "already exists")
                    pass
            else:
                try:
                    shutil.copy(image, outfold)
                    fLOG("copy ", image, " to ", outfold, "[", dest, "]")
                except shutil.Error as e:
                    if "are the same file" in str(e):
                        fLOG("w,file ", dest, "already exists")
                    else:
                        raise e

            if not os.path.exists(dest):
                raise FileNotFoundError(dest)
            copy.append(dest)

    return copy


def add_link_to_notebook(file, nb, pdf, html, python):
    """
    add a link to the notebook in HTML format and does a little bit of cleaning
    for various format

    @param      file        notebook.html
    @param      nb          notebook (.ipynb)
    @param      pdf         if True, add a link to the PDF, assuming it will exists at the same location
    @param      html        if True, add a link to the HTML conversion
    @param      python      if True, add a link to the Python conversion
    @return                 list of generated files

    The function does some cleaning too in the files.
    """
    ext = os.path.splitext(file)[-1]
    fLOG("    add_link_to_notebook", ext, " file ", file)

    fold, name = os.path.split(file)
    res = [os.path.join(fold, os.path.split(nb)[-1])]
    newr, reason = has_been_updated(nb, res[-1])
    if newr:
        shutil.copy(nb, fold)

    if ext == ".ipynb":
        return res
    elif ext == ".html":
        post_process_html_output(file, pdf, python)
        return res
    elif ext == ".tex":
        post_process_latex_output(file, True)
        return res
    elif ext == ".rst":
        post_process_rst_output(file, html, pdf, python)
        return res
    else:
        raise HelpGenException(
            "unable to add a link to this extension: " + ext)


def add_notebook_page(nbs, fileout):
    """
    creates a rst page with links to all notebooks

    @param      nbs             list of notebooks to consider
    @param      fileout         file to create
    @return                     created file name
    """
    rst = [_ for _ in nbs if _.endswith(".rst")]

    rows = ["", ".. _l-notebooks:", "", "", "Notebooks", "=========", ""]

    # exp = re.compile("[.][.] _([-a-zA-Z0-9_]+):")
    rst = sorted(rst)

    rows.append("")
    rows.append(".. toctree::")
    rows.append("")
    for file in rst:
        rows.append(
            "    notebooks/{0}".format(os.path.splitext(os.path.split(file)[-1])[0]))

    rows.append("")
    with open(fileout, "w", encoding="utf8") as f:
        f.write("\n".join(rows))
    return fileout
