"""
@brief      test log(time=4s)
@author     Xavier Dupre
"""

import sys
import os
import unittest
import sphinx
import warnings
from docutils.parsers.rst import directives

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
from src.pyquickhelper import get_temp_folder
from src.pyquickhelper.helpgen.utils_sphinx_doc import private_migrating_doxygen_doc
from src.pyquickhelper.helpgen import BlogPost, BlogPostList, BlogPostDirective, BlogPostDirectiveAgg
from src.pyquickhelper.helpgen import rst2html
from src.pyquickhelper.helpgen import RunPythonDirective, runpython_node
from src.pyquickhelper.helpgen.sphinx_runpython_extension import visit_runpython_node, depart_runpython_node

if sys.version_info[0] == 2:
    from codecs import open


class TestRunPythonExtension(unittest.TestCase):

    def test_runpython(self):
        """
        this test also test the extension runpython
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.version_info[0] == 2:
            warnings.warn(
                "test_newdirective_with_rst2html not run on Python 2.7")
            return

        from docutils import nodes

        class runpythonthis_node(nodes.Structural, nodes.Element):
            pass

        class RunPythonThisDirective (RunPythonDirective):
            runpython_class = runpythonthis_node

        def visit_rp_node(self, node):
            self.body.append("<p><b>visit_rp_node</b></p>")

        def depart_rp_node(self, node):
            self.body.append("<p><b>depart_rp_node</b></p>")

        if "enable_disabled_documented_pieces_of_code" in sys.__dict__:
            raise Exception("this case shoud not be")

        content = """
                    test a directive
                    ================

                    .. runpythonthis::
                        :setsysvar:
                        :rst:
                        :showcode:

                        print(u"this code shoud appear" + u"___")
                        import sys
                        print(u"setsysvar: " + str(sys.__dict__.get('enable_disabled_documented_pieces_of_code', None)))
                    """.replace("                    ", "")
        if sys.version_info[0] >= 3:
            content = content.replace('u"', '"')

        tives = [("runpythonthis", RunPythonThisDirective, runpythonthis_node,
                  visit_rp_node, depart_rp_node)]

        html = rst2html(content, fLOG=fLOG,
                        writer="custom", keep_warnings=True,
                        directives=tives)

        t1 = "this code shoud appear___"
        if t1 not in html:
            raise Exception(html)
        t2 = "setsysvar: True"
        if t2 not in html:
            raise Exception(html)
        if "enable_disabled_documented_pieces_of_code" in sys.__dict__:
            raise Exception("this case shoud not be")


if __name__ == "__main__":
    unittest.main()
