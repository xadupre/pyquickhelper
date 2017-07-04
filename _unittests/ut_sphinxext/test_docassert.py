"""
@brief      test log(time=8s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import warnings
import logging

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


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

from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.sphinxext.sphinx_docassert_extension import import_object
from src.pyquickhelper.helpgen import rst2html
from sphinx.util.logging import getLogger


class TestDocAssert(unittest.TestCase):

    def test_import_object(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exdocassert.onefunction", "function")
        self.assertTrue(obj is not None)
        self.assertTrue(obj(4, 5), 9)
        sys.path.pop()

    def test_docassert_html(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        logger1 = getLogger("MockSphinxApp")
        logger2 = getLogger("docassert")

        log_capture_string = StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger1.logger.addHandler(ch)
        logger2.logger.addHandler(ch)

        this = os.path.abspath(os.path.dirname(__file__))
        data = os.path.join(this, "datadoc")
        sys.path.append(data)
        obj, name = import_object("exdocassert.onefunction", "function")
        docstring = obj.__doc__
        with warnings.catch_warnings(record=True) as ws:
            html = rst2html(docstring)
            if "if a and b have different" not in html:
                raise Exception(html)

        newstring = ".. autofunction:: exdocassert.onefunction"
        with warnings.catch_warnings(record=True) as ws:
            html = rst2html(newstring)
            for i, w in enumerate(ws):
                fLOG(i, ":", w)
            if "if a and b have different" not in html:
                html = rst2html(newstring, fLOG=fLOG)
                fLOG("number of warnings", len(ws))
                for i, w in enumerate(ws):
                    fLOG(i, ":", str(w).replace("\\n", "\n"))
                raise Exception(html)

        from docutils.parsers.rst.directives import _directives
        self.assertTrue("autofunction" in _directives)

        sys.path.pop()

        lines = log_capture_string.getvalue().split("\n")
        if len(lines) > 0:
            for line in lines:
                if "'onefunction' has no parameter 'TypeError'" in line:
                    raise Exception(
                        "This warning should not happen.\n{0}".format("\n".join(lines)))
        self.assertTrue("<strong>a</strong>" in html)


if __name__ == "__main__":
    unittest.main()