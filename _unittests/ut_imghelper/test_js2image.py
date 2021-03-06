"""
@brief      test log(time=15s)

skip this test for regular run
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.pycode import ExtTestCase, get_temp_folder, skipif_appveyor, skipif_circleci, skipif_azure
from pyquickhelper.imghelper.js_helper import run_js_fct, install_node_js_modules
from pyquickhelper.imghelper.js_helper import nodejs_version, require, run_js_with_nodejs


class TestJs2Image(ExtTestCase):

    def test_js2fct(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        script = 'function add(a, b) {return a + b}'
        fct = run_js_fct(script)
        c = fct(3, 4)
        self.assertEqual(c, 7)

    @skipif_appveyor("No node.js.")
    @skipif_circleci("No node.js.")
    def test_nodejs(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        out = run_js_with_nodejs("console.log('jsnodejs');", fLOG=fLOG)
        self.assertEqual([out], ["jsnodejs\n"])

    @skipif_appveyor("No node.js.")
    @skipif_circleci("No node.js.")
    @skipif_azure("No node.js.")
    def test_js2fctdom(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        vers = nodejs_version()
        self.assertGreater(len(vers), 2)
        self.assertIn('.', vers)
        fLOG(vers)

        temp = get_temp_folder(__file__, 'temp_jsfctdom', clean=False)

        install_node_js_modules(temp, fLOG=fLOG)
        mod = require("underscore", cache_folder=temp, fLOG=fLOG)
        self.assertTrue(mod is not None)
        m = mod.max([0, 5, 4])
        self.assertEqual(m, 5)


if __name__ == "__main__":
    unittest.main()
