#-*- coding: utf-8 -*-
"""
@brief      test log(time=33s)
"""

import sys
import os
import unittest


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src


from src.pyquickhelper.loghelper import fLOG
from src.pyquickhelper import get_fLOG


class TestGetfLOG(unittest.TestCase):

    def test_flog(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        f1 = get_fLOG(True)
        assert f1
        f2 = get_fLOG(False)
        assert f2
        assert f1 != f2

if __name__ == "__main__":
    unittest.main()
