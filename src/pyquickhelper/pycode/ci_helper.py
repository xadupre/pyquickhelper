"""
@file
@brief Helpers for CI

.. versionadded:: 1.3
"""


def is_travis_or_appveyor():
    """
    tells if is a travis environment or appveyor

    @return        travis, appveyor or None

    The function should rely more on environement variables
    ``CI``, ``TRAVIS``, ``APPVEYOR``.

    .. versionadded:: 1.3
    """
    import sys
    if "travis" in sys.executable:
        return "travis"
    import os
    if os.environ["USERNAME"] == "appveyor":
        return "appveyor"
    return None