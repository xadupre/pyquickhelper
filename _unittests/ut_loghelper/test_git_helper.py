"""
@brief      test log(time=42s)
"""

import sys
import os
import unittest

if "temp_" in os.path.abspath(__file__):
    raise ImportError(
        "this file should not be imported in that location: " +
        os.path.abspath(__file__))

from pyquickhelper.loghelper import fLOG, removedirs
from pyquickhelper.filehelper import change_file_status
from pyquickhelper.loghelper.repositories.pygit_helper import clone, rebase
from pyquickhelper.loghelper.repositories.pygit_helper import get_file_last_modification
from pyquickhelper.pycode import is_travis_or_appveyor, ExtTestCase


class TestGitHelper(ExtTestCase):

    def test_clone_repo(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fold = os.path.abspath(os.path.split(__file__)[0])
        temp = os.path.join(fold, "temp_clone_repo")
        if os.path.exists(temp):
            removedirs(temp, use_command_line=True)
        if not os.path.exists(temp):
            os.mkdir(temp)

        if is_travis_or_appveyor() in ("travis", "appveyor"):
            return

        to = os.path.join(temp, "pq")
        out, err = clone(to, "github.com", "sdpython", "pyquickhelper")
        fLOG("OUT:", out)
        fLOG("ERR:", err)
        self.assertTrue("Cloning into" in err)
        self.assertTrue(os.path.exists(
            os.path.join(
                to,
                "src",
                "pyquickhelper",
                "__init__.py")))

        out, err = rebase(to, "github.com", "sdpython", "pyquickhelper")
        fLOG("OUT:", out)
        fLOG("ERR:", err)

        r = change_file_status(temp)
        self.assertTrue(len(r) > 0)

    def test_git_last_modifications(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(__file__).replace(".pyc", ".py")
        last = get_file_last_modification(this)
        self.assertTrue("2019" in last or '2020' in last)


if __name__ == "__main__":
    unittest.main()
