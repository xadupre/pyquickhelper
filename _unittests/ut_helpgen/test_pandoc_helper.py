"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import get_temp_folder, is_travis_or_appveyor, ExtTestCase
from pyquickhelper.helpgen import latex2rst


class TestPandocHelper(ExtTestCase):

    def test_latex2rst(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        if is_travis_or_appveyor() in ('travis', 'appveyor'):
            # It requires pandoc.
            return
        temp = get_temp_folder(__file__, "temp_latex2rst")
        data = os.path.join(temp, "..", "data", "chap9_thread.tex")
        output = os.path.join(temp, "chap9_thread.rst")
        temp_file = os.path.join(temp, "chap_utf8.tex")
        latex2rst(data, output, encoding="latin-1",
                  fLOG=fLOG, temp_file=temp_file)
        self.assertExists(output)


if __name__ == "__main__":
    unittest.main()
