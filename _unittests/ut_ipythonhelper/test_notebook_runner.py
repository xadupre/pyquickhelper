"""
@brief      test log(time=6s)
"""

import sys
import os
import unittest

from pyquickhelper.ipythonhelper import run_notebook, NotebookError
from pyquickhelper.pycode import get_temp_folder
from pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


class TestNotebookRunner(ExtTestCase):

    @unittest.skipIf(sys.version_info[0] == 2, reason="notebook is written in python 3")
    def test_notebook_runner(self):
        temp = get_temp_folder(__file__, "temp_notebook")
        nbfile = os.path.join(temp, "..", "data", "simple_example.ipynb")
        self.assertExists(nbfile)
        addpath = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))
        self.assertExists(addpath)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        self.assertNotExists(outfile)

        stat, out = run_notebook(nbfile, working_dir=temp, outfilename=outfile,
                                 additional_path=[addpath])
        self.assertExists(outfile)
        self.assertNotIn("No module named 'pyquickhelper'", out)
        self.assertIn("datetime.datetime(2015, 3, 2", out)
        self.assertIsInstance(stat, dict)

    @unittest.skipIf(sys.version_info[0] == 2, reason="notebook is written in python 3")
    def test_notebook_runner_exc(self):
        temp = get_temp_folder(__file__, "temp_notebook")
        nbfile = os.path.join(temp, "..", "data", "simple_example_exc.ipynb")
        self.assertExists(nbfile)
        addpath = os.path.normpath(os.path.join(temp, "..", "..", "..", "src"))
        self.assertExists(addpath)

        outfile = os.path.join(temp, "out_notebook.ipynb")
        self.assertNotExists(outfile)

        try:
            run_notebook(nbfile, working_dir=temp, outfilename=outfile,
                         additional_path=[addpath])
        except NotebookError as e:
            self.assertIn("name 'str2datetimes' is not defined", str(e))


if __name__ == "__main__":
    unittest.main()
