"""
@file
@brief Functions to run notebooks.

.. versionadded:: 1.4
    Split from *notebook_helper.py*.
"""
import sys
import time
import os
from datetime import datetime, timedelta

from ..loghelper.flog import noLOG
from ..filehelper import explore_folder
from .notebook_runner import NotebookRunner
from .notebook_exception import NotebookException
from .notebook_helper import writes


try:
    from nbformat.reader import reads
    from nbformat.reader import NotJSONError
except ImportError:
    from IPython.nbformat.reader import reads
    from IPython.nbformat.reader import NotJSONError

if sys.version_info[0] == 2:
    from codecs import open
    from StringIO import StringIO
    FileNotFoundError = Exception
    import urllib2 as urllib_request
else:
    from io import StringIO
    import urllib.request as urllib_request


def _cache_url_to_file(cache_urls, folder, fLOG=noLOG):
    """
    Downloads file corresponding to url stored in *cache_urls*.

    @param      cache_urls      list of urls
    @param      folder          where to store the cached files
    @param      fLOG            logging function
    @return                     dictionary { url: file }

    The function detects if the file was already downloaded.
    In that case, it does not do it a second time.

    .. versionadded:: 1.4
    """
    if cache_urls is None:
        return None
    if folder is None:
        raise FileNotFoundError("folder cannot be None")
    res = {}
    for url in cache_urls:
        local_file = "__cached__" + url.split("/")[-1]
        local_file = local_file.replace(":", "_").replace("%", "_")
        local_file = os.path.abspath(os.path.join(folder, local_file))
        if not os.path.exists(local_file):
            fLOG("download", url, "to", local_file)
            with open(local_file, "wb") as f:
                fu = urllib_request.urlopen(url)
                c = fu.read(2 ** 21)
                while len(c) > 0:
                    f.write(c)
                    f.flush()
                    c = fu.read(2 ** 21)
                fu.close()

        # to avoid having backslahes inside strings
        res[url] = "file:///" + local_file.replace("\\", "/")
    return res


def run_notebook(filename, profile_dir=None, working_dir=None, skip_exceptions=False,
                 outfilename=None, encoding="utf8", additional_path=None,
                 valid=None, clean_function=None, code_init=None,
                 fLOG=noLOG, kernel_name="python", log_level="30",
                 extended_args=None, cache_urls=None, replacements=None,
                 detailed_log=None):
    """
    Runs a notebook end to end,
    it is inspired from module `runipy <https://github.com/paulgb/runipy/>`_.

    @param      filename            notebook filename
    @param      profile_dir         profile directory
    @param      working_dir         working directory
    @param      skip_exceptions     skip exceptions
    @param      outfilename         if not None, saves the output in this notebook
    @param      encoding            encoding for the notebooks
    @param      additional_path     additional paths for import
    @param      valid               if not None, valid is a function which returns whether
                                    or not the cell should be executed or not, if the function
                                    returns None, the execution of the notebooks and skip the execution
                                    of the other cells
    @param      clean_function      function which cleans a cell's code before executing it (None for None)
    @param      code_init           code to run before the execution of the notebook as if it was a cell
    @param      fLOG                logging function
    @param      kernel_name         kernel name, it can be None
    @param      log_level           Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      extended_args       others arguments to pass to the command line ('--KernelManager.autorestar=True' for example),
                                    see :ref:`l-ipython_notebook_args` for a full list
    @param      cache_urls          list of urls to cache
    @param      replacements        list of additional replacements, list of tuple
    @param      detailed_log        a second function to log more information when executing the notebook,
                                    this should be a function with the same signature as ``print`` or None
    @return                         tuple (statistics, output)

    @warning The function calls `basicConfig <https://docs.python.org/3/library/logging.html#logging.basicConfig>`_.

    .. exref::
        :title: Run a notebook end to end

        ::

            from pyquickhelper.ipythonhelper import run_notebook
            run_notebook("source.ipynb", working_dir="temp",
                        outfilename="modified.ipynb",
                        additional_path = [ "c:/temp/mymodule/src" ] )

    The function adds the local variable ``theNotebook`` with
    the absolute file name of the notebook.

    The execution of a notebook might fail because it relies on remote data
    specified by url. The function downloads the data first and stores it in
    folder *working_dir* (must not be None). The url string is replaced by
    the absolute path to the file.

    .. versionchanged:: 1.3
        Parameters *log_level*, *extended_args*, *kernel_name* were added.

    .. versionchanged:: 1.4
        Parameter *cache_urls* was added.
        Function *valid* can return None and stops the execution of the notebook.

    .. versionchanged:: 1.5
        Parameter *detailed_log* was added.
    """
    cached_rep = _cache_url_to_file(cache_urls, working_dir, fLOG=fLOG)
    if replacements is None:
        replacements = cached_rep
    elif cached_rep is not None:
        cached_rep.update(replacements)
    else:
        cached_rep = replacements

    with open(filename, "r", encoding=encoding) as payload:
        try:
            nbc = payload.read()
        except UnicodeDecodeError as e:
            raise NotebookException(
                "(2) Unable to read file '{0}' encoding='{1}'.".format(filename, encoding)) from e
    try:
        nb = reads(nbc)
    except NotJSONError as e:
        raise NotebookException(
            "(1) Unable to read file '{0}' encoding='{1}'.".format(filename, encoding)) from e

    out = StringIO()

    def flogging(*l, **p):
        if len(l) > 0:
            out.write(" ".join(l))
        if len(p) > 0:
            out.write(str(p))
        out.write("\n")
        fLOG(*l, **p)

    nb_runner = NotebookRunner(nb, profile_dir, working_dir, fLOG=flogging, filename=filename,
                               theNotebook=os.path.abspath(filename),
                               code_init=code_init, log_level=log_level,
                               extended_args=extended_args, kernel_name=kernel_name,
                               replacements=cached_rep, kernel=True, detailed_log=detailed_log)
    stat = nb_runner.run_notebook(skip_exceptions=skip_exceptions, additional_path=additional_path,
                                  valid=valid, clean_function=clean_function)

    if outfilename is not None:
        with open(outfilename, 'w', encoding=encoding) as f:
            try:
                s = writes(nb_runner.nb)
            except NotebookException as e:
                raise NotebookException(
                    "issue with notebook: " + filename) from e
            if isinstance(s, bytes):
                s = s.decode('utf8')
            f.write(s)

    nb_runner.shutdown_kernel()
    return stat, out.getvalue()


def execute_notebook_list(folder, notebooks, clean_function=None, valid=None, fLOG=noLOG,
                          additional_path=None, deepfLOG=noLOG, kernel_name="python",
                          log_level="30", extended_args=None, cache_urls=None,
                          replacements=None, detailed_log=None):
    """
    Executes a list of notebooks.

    @param      folder              folder (where to execute the notebook, current folder for the notebook)
    @param      notebooks           list of notebooks to execute (or a list of tuple(notebook, code which initializes the notebook))
    @param      clean_function      function which transform the code before running it
    @param      valid               if not None, valid is a function which returns whether
                                    or not the cell should be executed or not, if the function
                                    returns None, the execution of the notebooks and skip the execution
                                    of the other cells
    @param      fLOG                logging function
    @param      deepfLOG            logging function used to run the notebook
    @param      additional_path     path to add to *sys.path* before running the notebook
    @param      kernel_name         kernel name, it can be None
    @param      log_level           Choices: (0, 10, 20, 30=default, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    @param      extended_args       others arguments to pass to the command line ('--KernelManager.autorestar=True' for example),
                                    see :ref:`l-ipython_notebook_args` for a full list
    @param      cache_urls          list of urls to cache
    @param      replacements        additional replacements
    @param      detailed_log        detailed log
    @return                         dictionary of dictionaries ``{ notebook_name: {  } }``

    If *isSuccess* is False, *statistics* contains the execution time, *output* is the exception
    raised during the execution.

    The signature of function ``valid_cell`` is::

        def valid_cell(cell):
            return True or False or None to stop execution of the notebook before this cell

    The signature of function ``clean_function`` is::

        def clean_function(cell):
            return new_cell_content

    The execution of a notebook might fail because it relies on remote data
    specified by url. The function downloads the data first and stores it in
    folder *working_dir* (must not be None). The url string is replaced by
    the absolute path to the file.

    .. versionadded:: 1.1

    .. versionchanged:: 1.3
        Parameters *log_level*, *extended_args*, *kernel_name* were added.

    .. versionchanged:: 1.4
        Parameter *cache_urls* was added.
        Function *valid* can return None.

    .. versionchanged:: 1.5
        Parameter *detailed_log* was added.
        Changes the results into a list of dictionaries
    """
    if additional_path is None:
        additional_path = []

    # we cache urls before running through the list of notebooks
    _cache_url_to_file(cache_urls, folder, fLOG=fLOG)

    results = {}
    for i, note in enumerate(notebooks):
        if isinstance(note, tuple):
            note, code_init = note
        else:
            code_init = None
        if filter(i, note):
            fLOG("******", i, os.path.split(note)[-1])
            outfile = os.path.join(folder, "out_" + os.path.split(note)[-1])
            cl = time.clock()
            try:
                stat, out = run_notebook(note, working_dir=folder, outfilename=outfile,
                                         additional_path=additional_path, valid=valid,
                                         clean_function=clean_function, fLOG=deepfLOG,
                                         code_init=code_init, kernel_name=kernel_name,
                                         log_level=log_level, extended_args=extended_args,
                                         cache_urls=cache_urls, replacements=replacements,
                                         detailed_log=detailed_log)
                if not os.path.exists(outfile):
                    raise FileNotFoundError(outfile)
                etime = time.clock() - cl
                results[note] = dict(success=True, output=out, name=note, etime=etime,
                                     date=datetime.now())
                results[note].update(stat)
            except Exception as e:
                etime = time.clock() - cl
                results[note] = dict(success=False, etime=etime, error=e, name=note,
                                     date=datetime.now())
    return results


def _get_dump_default_path(dump):
    """
    Proposes a default location to dump results about notebooks execution.

    @param      dump        location of the dump or module.
    @return                 location of the dump

    The result might be equal to the input if *dump* is already path.
    """
    if hasattr(dump, '__file__') and hasattr(dump, '__name__'):
        # Default value. We check it is none travis or appveyor.
        from ..pycode import is_travis_or_appveyor
        if is_travis_or_appveyor():
            dump = None
        if dump is not None:
            # We guess the package name.
            name = dump.__name__.split('.')[-1]
            loc = os.path.dirname(dump.__file__)
            # We choose a path for the dumps in a way
            fold = os.path.join(loc, "..", "..", "..", "_notebook_dumps")
            if not os.path.exists(fold):
                os.mkdir(fold)
            dump = os.path.join(fold, "notebook.{0}.txt".format(name))
            return dump
    return dump


def execute_notebook_list_finalize_ut(res, dump=None, fLOG=noLOG):
    """
    Checks the list of results and raises an exception if one failed.
    This is meant to be used in unit tests.

    @param      res     output of @see fn execute_notebook_list
    @param      dump    if not None, dump the results of the execution in a flat file
    @param      fLOG    logging function

    The dump relies on :epkg:`pandas` and append the results a previous dump.
    If *dump* is a module, the function stores the output of the execution in a default
    location only if the process does not run on :epkg:`travis` or :epkg:`appveyor`.
    The default location is something like:

    .. runpython::

        from pyquickhelper.ipythonhelper.run_notebook import _get_dump_default_path
        import pyquickhelper
        print(_get_dump_default_path(pyquickhelper))


    .. versionadded:: 1.5
    """
    if len(res) == 0:
        raise Exception("No notebook was run.")

    def fail_note(v):
        return "error" in v
    fails = [(os.path.split(k)[-1], v)
             for k, v in sorted(res.items()) if fail_note(v)]
    for f in fails:
        fLOG(f)
    for k, v in sorted(res.items()):
        name = os.path.split(k)[-1]
        fLOG(name, v.get("success", None), v.get("etime", None))
    if len(fails) > 0:
        raise fails[0][1]["error"]

    dump = _get_dump_default_path(dump)
    if dump is not None:
        import pandas
        if os.path.exists(dump):
            df = pandas.read_csv(dump, sep="\t", encoding="utf-8")
        else:
            df = None

        new_df = pandas.DataFrame(data=list(res.values()))

        # We replace every EOL.
        def eol_replace(t):
            return t.replace("\r", "").replace("\n", "\\n")

        subdf = new_df.select_dtypes(include=['object']).applymap(eol_replace)
        for c in subdf.columns:
            new_df[c] = subdf[c]

        if df is None:
            df = new_df
        else:
            df = pandas.concat([df, new_df]).copy()

        df.to_csv(dump, sep="\t", encoding="utf-8", index=False)


def notebook_coverage(module_or_path, dump=None, too_old=30):
    """
    Extracts a list of notebooks and merges with a list of runs dumped by
    function @see fn execute_notebook_list_finalize_ut.

    @param      module_or_path      a module or a path
    @param      dump                dump (or None to get the location by default)
    @param      too_old             drop executions older than *too_old* days from now
    @return                         dataframe

    If *module_or_path* is a module, the function will get a list notebooks
    assuming it follows the same design as :epkg:`pyquickhelper`.

    .. versionadded:: 1.5
    """
    if dump is None:
        dump = _get_dump_default_path(module_or_path)
    else:
        dump = _get_dump_default_path(dump)

    # Create the list of existing notebooks.
    if isinstance(module_or_path, list):
        nbs = [_[1] if isinstance(_, tuple) else _ for _ in module_or_path]
    elif hasattr(module_or_path, '__file__') and hasattr(module_or_path, '__name__'):
        fold = os.path.dirname(module_or_path.__file__)
        _doc = os.path.join(fold, "..", "..", "_doc")
        if not os.path.exists(_doc):
            raise FileNotFoundError(
                "Unable to find path '{0}' for module '{1}'".format(_doc, module_or_path))
        nbpath = os.path.join(_doc, "notebooks")
        if not os.path.exists(nbpath):
            raise FileNotFoundError(
                "Unable to find path '{0}' for module '{1}'".format(nbpath, module_or_path))
        nbs = explore_folder(nbpath, ".*[.]ipynb$")[1]
    else:
        nbpath = module_or_path
        nbs = explore_folder(nbpath, ".*[.]ipynb$")[1]

    import pandas
    dfnb = pandas.DataFrame(data=dict(notebooks=nbs))
    dfnb["notebooks"] = dfnb["notebooks"].apply(lambda x: os.path.normpath(x))
    dfnb = dfnb[~dfnb.notebooks.str.contains(".ipynb_checkpoints")].copy()
    dfnb["key"] = dfnb["notebooks"].apply(lambda x: "/".join(os.path.normpath(
        x).replace("\\", "/").split("/")[-3:]) if isinstance(x, str) else x)
    dfnb["key"] = dfnb["key"].apply(
        lambda x: x.lower() if isinstance(x, str) else x)

    # Loads the dump.
    dfall = pandas.read_csv(dump, sep="\t", encoding="utf-8")

    # We drop too old execution.
    old = datetime.now() - timedelta(too_old)
    old = "%04d-%02d-%02d" % (old.year, old.month, old.day)
    dfall = dfall[dfall.date > old].copy()

    # We add a key to merge.
    dfall["name"] = dfall["name"].apply(lambda x: os.path.normpath(x))
    dfall["key"] = dfall["name"].apply(lambda x: "/".join(os.path.normpath(
        x).replace("\\", "/").split("/")[-3:]) if isinstance(x, str) else x)
    dfall["key"] = dfall["key"].apply(
        lambda x: x.lower() if isinstance(x, str) else x)

    # We keep the last execution.
    gr = dfall.sort_values("date", ascending=False).groupby(
        "key", as_index=False).first().reset_index(drop=True).copy()
    gr = gr.drop("name", axis=1)

    # Folders might be different so we merge on the last part of the path.
    merged = dfnb.merge(gr, left_on="key", right_on="key", how="outer")
    merged = merged[merged.notebooks.notnull()]
    merged = merged.sort_values("key").reset_index(drop=True).copy()

    if "last_name" not in merged.columns:
        merged["last_name"] = merged["key"].apply(
            lambda x: os.path.split(x)[-1])

    # We check there is no duplicates in merged.
    for c in ["key", "last_name"]:
        names = [_ for _ in merged[c] if isinstance(_, str)]
        if len(names) > len(set(names)):
            raise ValueError("Unexpected duplicated names in column '{1}'\n{0}".format(
                "\n".join(sorted(names)), c))

    return merged


def badge_notebook_coverage(df, image_name):
    """
    Builds a badge reporting on the notebook coverage.
    It gives the proportion of run cells.

    @param      df          output of @see fn notebook_coverage
    @param      image_name  image to produce

    The function relies on module :epkg:`Pillow`.
    """
    cell = df["nbcell"].sum()
    run = df["nbrun"].sum()
    valid = df["nbvalid"].sum()
    cov = run * 100.0 / cell if cell > 0 else 1.0
    val = valid * 100.0 / cell if cell > 0 else 1.0
    from PIL import Image, ImageFont, ImageDraw
    img = Image.new(mode='P', size=(70, 20), color=100)
    im = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    try:
        cov = int(cov)
        cov = min(cov, 100)
    except ValueError:
        cov = "?"
    try:
        val = int(val)
        val = min(val, 100)
    except ValueError:
        val = "?"
    if cov != val:
        im.text((3, 4), "NB:{0}%-{1}%".format(cov, val),
                (255, 255, 255), font=font)
    else:
        im.text((3, 4), "NB: {0}%".format(cov), (255, 255, 255), font=font)
    img.save(image_name)


def get_additional_paths(modules):
    """
    Returns a list of paths to add before running the notebooks
    for a given a list of modules.

    @return             list of paths
    """
    addpath = [os.path.dirname(mod.__file__) for mod in modules]
    addpath = [os.path.normpath(os.path.join(_, "..")) for _ in addpath]
    return addpath
