"""
@brief      test log(time=2s)
@author     Xavier Dupre
"""

import sys
import os
import unittest

from pyquickhelper.loghelper import fLOG
from pyquickhelper.filehelper.ftp_mock import MockTransferFTP
from pyquickhelper.filehelper import TransferAPIFtp


class TestTransferFTP(unittest.TestCase):

    def test_transfer_ftp(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        mock = MockTransferFTP(fLOG=fLOG)
        assert mock._ftp
        r = mock.ls(".")
        self.assertEqual(r, [{'name': 'setup.py'}])
        this = os.path.abspath(__file__)
        name = os.path.split(this)[-1]
        t = mock.transfer(this, '.', name=name)
        fLOG(t)
        dest = os.path.join(os.path.split(__file__)[0], "out_ftp_retr.py.temp")
        t = mock.retrieve('.', name=name, file=dest)
        fLOG(t)
        assert os.path.exists(dest)

    def test_transfer_ftp_api(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        mock = TransferAPIFtp(None, None, None, fLOG=fLOG)
        t = mock.transfer('setup.py', data=b'# ee')
        fLOG(t)
        data = mock.retrieve('setup.py')
        fLOG(t)
        self.assertEqual(data, b'# ee')


if __name__ == "__main__":
    unittest.main()
