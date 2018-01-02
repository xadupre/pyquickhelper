"""
@file
@brief Publishing coverage

.. versionadded:: 1.3
"""
import os
import re
import sys
from collections import Counter
import shutil
from contextlib import redirect_stderr, redirect_stdout
from ..loghelper import SourceRepository, noLOG
from ..filehelper import explore_folder_iterfile


if sys.version_info[0] == 2:
    FileNotFoundError = Exception
    from StringIO import StringIO
else:
    from io import StringIO


def publish_coverage_on_codecov(path, token, commandline=True, fLOG=noLOG):
    """
    Publishes the coverage report on `codecov <https://codecov.io/>`_.
    See blog post :ref:`blogpost_coverage_codecov`.

    @param      path            path to source
    @param      token           token on codecov
    @param      commandline     see @see cl SourceRepository
    @param      fLOG            logging function
    @return                     out, err from function @see fn run_cmd
    """
    if os.path.isfile(path):
        report = path
    else:
        report = os.path.join(path, "_doc", "sphinxdoc",
                              "source", "coverage", "coverage_report.xml")

    report = os.path.normpath(report)
    if not os.path.exists(report):
        raise FileNotFoundError(report)

    proj = os.path.normpath(os.path.join(
        os.path.dirname(report), "..", "..", "..", ".."))

    src = SourceRepository(commandline=commandline)
    last = src.get_last_commit_hash(proj)
    cmd = ["--token={0}".format(token), "--file={0}".format(report),
           "--commit={0}".format(last), "--root={0} -X gcov".format(proj)]
    if token is not None:
        import codecov
        new_out = StringIO()
        new_err = StringIO()
        with redirect_stdout(new_out):
            with redirect_stderr(new_err):
                codecov.main(*cmd)
        out = new_out.getvalue()
        err = new_err.getvalue()
        if err:
            raise Exception(
                "unable to run:\nCMD:\n{0}\nOUT:\n{1}\n[pyqerror]\n{2}".format(cmd, out, err))
        return out, err
    else:
        return cmd


def coverage_combine(data_files, output_path, source, process=None, absolute_path=True):
    """
    Merges multiples reports.

    @param      data_files      report files (``.coverage``)
    @param      output_path     output path
    @param      source          source directory
    @param      process         function which processes the coverage report
    @param      absolute_path   relocate sources with absolute paths
    @return                     coverage report

    The function *process* should have the signature:

    ::

        def process(content):
            # ...
            return content
    """
    def raise_exc(exc, content, ex, ex2, outfile, destcov, source, dests, inter, cov):

        from coverage.data import CoverageData

        def shorten(t):
            if len(t) > 2000:
                return t[:2000] + "\n..."
            else:
                return t
        if len(content) > 2000:
            content = content[:2000] + '\n...'
        ex = "\n-\n".join(shorten(_) for _ in ex)
        ex2 = "\n-\n".join(shorten(_) for _ in ex2)
        rows = ["destcov='{0}'".format(destcov),
                "outfile='{0}'".format(outfile),
                "source='{0}'".format(source),
                "cov.source={0}".format(cov.source),
                "dests='{0}'".format(';'.join(dests)),
                "inter={0}".format(inter)]
        if cov is not None and cov.data is not None and cov.data._lines is not None:
            rows.append("----- LINES")
            end = min(5, len(cov.data._lines))
            for k, v in list(sorted(cov.data._lines.items()))[:end]:
                rows.append('   {0}:{1}'.format(k, v))
            rows.append("----- RUNS")
            end = min(5, len(cov.data._runs))
            for k in cov.data._runs[:end]:
                rows.append('   {0}'.format(k))
            rows.append("----- END")
        for d in dests:
            dd = CoverageData()
            dd.read_file(d + "~")
            rows.append("------- LINES - '{0}'".format(d))
            end = min(5, len(dd._lines))
            for k, v in list(sorted(dd._lines.items()))[:end]:
                rows.append('   {0}:{1}'.format(k, v))
            rows.append("------- RUNS - '{0}'".format(d))
            end = min(5, len(dd._runs))
            for k in dd._runs[:end]:
                rows.append('   {0}'.format(k))
            rows.append("------- END")

        raise RuntimeError(
            "{5}. In '{0}'.\n{1}\n{2}\n---AFTER---\n{3}\n---BEGIN---\n{4}".format(output_path, "\n".join(rows), content, ex, ex2, exc, cov)) from exc

    # We copy the origin coverage if the report is produced
    # in a folder part of the merge.
    destcov = os.path.join(output_path, '.coverage')
    if os.path.exists(destcov):
        destcov2 = destcov + '_old'
        shutil.copy(destcov, destcov2)
        os.remove(destcov)

    # Starts merging coverage.
    from coverage import Coverage
    cov = Coverage(data_file=destcov, source=[source])
    # Module coverage may modify the folder,
    # we take the one it considers.
    # On Windows, it has to have the right case.
    # If not, coverage reports an empty coverage and
    # raises an exception.
    cov._init()
    cov.get_data()
    if cov.source is None or len(cov.source) == 0:
        raise_exc(FileNotFoundError("Probably unable to find '{0}'".format(source)),
                  "", [], [], "", destcov, source, [], [], cov)
    source = cov.source[0]

    inter = []
    reg = re.compile(',\\"(.*?[.]py)\\"')

    def copy_replace(source, dest, root_source):
        with open(source, "r") as f:
            content = f.read()
        if process is not None:
            content = process(content)
        cf = reg.findall(content)
        co = Counter([_.split('src')[0] for _ in cf])
        mx = max((v, k) for k, v in co.items())
        root = mx[1].rstrip('\\/')
        if absolute_path:
            if '\\\\' in root:
                s2 = root_source.replace('\\', '\\\\').replace('/', '\\\\')
                s2 += "\\\\"
                root += "\\\\"
            elif '\\' in root:
                s2 = root_source
                s2 += "\\\\"
                root += "\\"
            else:
                s2 = root_source
                s2 += "/"
                root += "/"
        else:
            s2 = ""
            if '\\\\' in root:
                root += "\\\\"
            elif '\\' in root:
                root += "\\"
            else:
                root += "/"
        inter.append((root, root_source, s2))
        content = content.replace(root, s2)
        with open(dest, "w") as f:
            f.write(content)

    # We modify the root in every coverage file.
    dests = [os.path.join(output_path, '.coverage{0}'.format(
        i)) for i in range(len(data_files))]
    for fi, de in zip(data_files, dests):
        copy_replace(fi, de, source)
        shutil.copy(de, de + "~")

    # Keeping information (for exception).
    ex = []
    for d in dests:
        with open(d, "r") as f:
            ex.append(f.read())
    ex2 = []
    for d in data_files:
        with open(d, "r") as f:
            ex2.append(f.read())

    # We replace destcov by destcov2 if found in dests.
    if destcov in dests:
        ind = dests.index(destcov)
        dests[ind] = destcov2

    # Let's combine.
    cov.combine(dests)

    from coverage.misc import NoSource
    try:
        cov.html_report(directory=output_path)
    except NoSource as e:
        raise_exc(e, "", ex, ex2, "", destcov, source, dests, inter, cov)

    outfile = os.path.join(output_path, "coverage_report.xml")
    cov.xml_report(outfile=outfile)
    cov.save()

    # Verifications
    with open(outfile, "r", encoding="utf-8") as f:
        content = f.read()

    if 'line hits="1"' not in content:
        raise_exc(Exception("Coverage is empty"), content, ex,
                  ex2, outfile, destcov, source, dests, inter, cov)

    return cov


def find_coverage_report(folder, exclude=None, filter_out='.*conda.*'):
    """
    Finds all coverage reports in one subfolder.

    @param      folder      which folder to look at
    @param      exclude     list of subfolder not to look at
    @param      filter_out  filter out from the name
    @return                 list of files ``.coverage``

    The structure is supposed to:

    ::

        folder
          +- hash1
          |    +- date1
          |    |    +- .coverage - not selected
          |    +- date2
          |         +- .coverage - selected
          +- hash2
               +- date
                    +- .coverage - selected
    """
    regexp = re.compile('data_file=([0-9a-zA-Z_]+)')
    regcov = re.compile(
        '<h1>Coveragereport:<spanclass=.?pc_cov.?>([0-9]+)%</span>')
    regout = re.compile(filter_out) if filter_out else None
    covs = {}
    subfold = os.listdir(folder)
    for sub in subfold:
        if exclude is not None and sub in exclude:
            continue
        full = os.path.join(folder, sub)
        keep = []
        nn = None
        cov = None
        for it in explore_folder_iterfile(full):
            name = os.path.split(it)[-1]
            dt = os.stat(full).st_mtime
            if name == 'index.html':
                with open(it, 'r') as f:
                    htd = f.read().replace('\n', '').replace('\r', '').replace(' ', '')
                cont = regcov.findall(htd)
                if len(cont) > 0:
                    cov = cont[0]
            if name == 'covlog.txt':
                with open(it, 'r') as f:
                    logd = f.read()
                cont = regexp.findall(logd)
                if len(cont) > 0:
                    nn = cont[0]
            if name == '.coverage':
                keep.append((dt, it))
        if len(keep) == 0:
            continue
        mx = max(keep)
        if regout is not None and regout.search(nn):
            continue
        covs[sub] = (mx[-1], nn, cov)
    return covs
