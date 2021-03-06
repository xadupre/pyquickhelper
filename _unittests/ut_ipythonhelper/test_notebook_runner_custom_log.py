"""
@brief      test log(time=6s)
"""

import sys
import os
import unittest

from pyquickhelper.ipythonhelper import run_notebook
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.loghelper import fLOG, CustomLog
from pyquickhelper.pycode import is_travis_or_appveyor


class TestNotebookRunnerCustomLog (unittest.TestCase):

    def test_notebook_runner_custom_log(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(self.test_notebook_runner_custom_log)
        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        assert os.path.exists(nbfile)
        addpath = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))
        assert os.path.exists(addpath)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        assert not os.path.exists(outfile)

        custom = CustomLog(temp)
        stat, out = run_notebook(nbfile, working_dir=temp, outfilename=outfile,
                                 additional_path=[addpath],
                                 detailed_log=custom)
        fLOG(stat)
        fLOG(out)
        assert os.path.exists(outfile)
        assert "No module named 'pyquickhelper'" not in out
        assert "datetime.datetime(2015, 3, 2" in out
        out = os.path.join(temp, "log_custom_000.txt")
        if not os.path.exists(out):
            raise FileNotFoundError(out)


if __name__ == "__main__":
    unittest.main()
