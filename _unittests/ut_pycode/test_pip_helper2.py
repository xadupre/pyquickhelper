"""
@brief      test tree node (time=2s)
"""

import sys
import os
import unittest
import pandas

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
from src.pyquickhelper.pycode.pip_helper import get_package_info
from src.pyquickhelper.pycode import ExtTestCase
from src.pyquickhelper.pycode.pip_helper import fix_pip_902


class TestPipHelper2(ExtTestCase):

    def test_pip_show(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        fix_pip_902()
        info = get_package_info("pandas")
        # if "license" not in info:
        #    raise Exception(str(info))
        if "version" not in info:
            raise Exception(str(info))

        if sys.version_info[0] >= 3:
            info = get_package_info("sphinx")
            if "version" not in info:
                raise Exception(str(info))

    def test_pip_show_all(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        info = get_package_info(start=0, end=2)
        df = pandas.DataFrame(info)
        self.assertNotEmpty(info)
        self.assertIsInstance(info[0], dict)

        if __name__ == "__mahin__":
            info = get_package_info()
            df = pandas.DataFrame(info)
            df.to_excel("out_packages.xlsx")


if __name__ == "__main__":
    unittest.main()