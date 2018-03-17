"""
@brief      test log(time=12s)
@author     Xavier Dupre
"""
import os
import sys
import unittest
import shutil


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

from src.pyquickhelper.pycode import get_temp_folder, ExtTestCase
from src.pyquickhelper.loghelper.flog import fLOG
from src.pyquickhelper.filehelper.synchelper import synchronize_folder
import src.pyquickhelper.helpgen.utils_sphinx_doc as utils_sphinx_doc


class TestSphinxDocFull (ExtTestCase):

    def test_full_documentation(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        temp = get_temp_folder(__file__, "temp_doc")

        if sys.version_info[0] == 2:
            return

        file = os.path.join(temp, "..", "..", "..")
        fLOG(os.path.normpath(os.path.abspath(file)))
        self.assertExists(os.path.exists(file))

        sysp = os.path.normpath(os.path.join(
            file, "_doc", "sphinxdoc", "source"))
        self.assertExists(os.path.exists(sysp))
        fLOG('sysp=', sysp)
        sys.path.insert(0, sysp)
        del sys.path[0]

        synchronize_folder(sysp, temp,
                           filter=lambda c: "__pycache__" not in c and "pyquickhelper" not in c)
        shutil.copy(os.path.join(file, "README.rst"), temp)

        # copy the files
        project_var_name = "pyquickhelper"
        issues = []
        store_obj = {}

        utils_sphinx_doc.prepare_file_for_sphinx_help_generation(
            store_obj, file, temp, silent=True,
            subfolders=[("src/" + project_var_name, project_var_name), ],
            rootrep=("ut_helpgen.temp_doc.%s." % (project_var_name,), ""),
            optional_dirs=[], mapped_function=[(".*[.]tohelp$", None)],
            issues=issues, module_name=project_var_name)

        fLOG("end of prepare_file_for_sphinx_help_generation")

        files = [
            #os.path.join(temp, "index_ext-tohelp.rst"),
            os.path.join(temp, "index_function.rst"),
            os.path.join(temp, "glossary.rst"),
            os.path.join(temp, "index_class.rst"),
            os.path.join(temp, "index_module.rst"),
            os.path.join(temp, "index_property.rst"),
            os.path.join(temp, "index_method.rst"),
            os.path.join(temp, "all_report.rst"),
        ]
        for f in files:
            if not os.path.exists(f):
                raise FileNotFoundError(f + "\nabspath: " + os.path.abspath(f))
            if "report" in f:
                with open(f, "r", encoding="utf8") as ff:
                    content = ff.read()
                self.assertIn(".py", content)

        if os.path.exists(os.path.join(temp, "all_FAQ.rst")):
            with open(os.path.join(temp, "all_FAQ.rst"), "r") as f:
                contentf = f.read()
            self.assertIn("How to activate the logs?", contentf)
            self.assertNotIn("_le-", contentf)
            self.assertNotIn("_lf-", contentf)
            self.assertNotIn("__!LI!NE!__", contentf)

        with open(files[0], "r", encoding="utf8") as f:
            f.read()

        for f in ["fix_incomplete_references"]:
            func = [
                _ for _ in issues if _[0] == f and "utils_sphinx_doc.py" not in _[1]]
            if len(func) > 0:
                fLOG(func)
                mes = "\n".join([_[1] for _ in func])
                stk = []
                for k, v in store_obj.items():
                    if isinstance(v, list):
                        for o in v:
                            stk.append("storedl %s=%s " % (k, o.rst_link()))
                    else:
                        stk.append("stored  %s=%s " % (k, v.rst_link()))
                mes += "\nstored:\n" + "\n".join(sorted(stk))
                raise Exception(
                    "issues detected for function " +
                    f +
                    "\n" +
                    mes)

        exclude = os.path.join(
            temp,
            "pyquickhelper",
            "helpgen",
            "utils_sphinx_doc.py")
        with open(exclude, "r") as f:
            content = f.read()
        self.assertNotIn("### # -- HELP END EXCLUDE --", content)
        self.assertNotIn(
            "### class useless_class_UnicodeStringIOThreadSafe(str):", content)


if __name__ == "__main__":
    unittest.main()